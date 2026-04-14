#!/usr/bin/env python3
"""
Medical RAG — Nightly Maintenance
Runs at 00:30 UTC via systemd timer medical-rag-maintenance.timer.
Guarantee: never crashes, always writes report, always pushes to git.
Usage: python3 scripts/nightly_maintenance.py
"""

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

import psutil

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE            = Path(__file__).parent.parent
BACKUP_DIR      = BASE / "backups"
BACKUP_QDRANT   = BACKUP_DIR / "qdrant"
BACKUP_META     = BACKUP_DIR / "metadata"
REPORT_PATH     = BASE / "SYSTEM_DOCS" / "MAINTENANCE_REPORT.md"
CONTEXT_PATH    = BASE / "SYSTEM_DOCS" / "CONTEXT.md"

# ── Config ──────────────────────────────────────────────────────────────────────
QDRANT_BASE       = "http://localhost:6333"
OLLAMA_BASE       = "http://localhost:11434"
MAX_SNAPSHOTS     = 7        # per collection, local backup copies
MAX_META_BACKUPS  = 30       # daily metadata JSON backups
MAX_PROC_LOG_DAYS = 30       # processing logs older than this are deleted
MAX_SNAP_SIZE_MB  = 500      # skip local download if snapshot exceeds this

# ─────────────────────────────────────────────────────────────────────────────
# HTTP helpers
# ─────────────────────────────────────────────────────────────────────────────

def _http(method: str, url: str,
          data: bytes | None = None,
          timeout: int = 15) -> tuple[int, Any]:
    """Generic HTTP call. Returns (status_code, parsed_body_or_raw_string)."""
    try:
        headers = {"User-Agent": "medical-rag-maintenance/1.0"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(body)
            except json.JSONDecodeError:
                return resp.status, body
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read().decode("utf-8", errors="replace")
        except Exception:
            return e.code, None
    except Exception as exc:
        return 0, str(exc)


def http_get(url: str, timeout: int = 15) -> tuple[int, Any]:
    return _http("GET", url, timeout=timeout)

def http_post(url: str, data: dict | None = None, timeout: int = 30) -> tuple[int, Any]:
    body = json.dumps(data).encode() if data is not None else b""
    return _http("POST", url, data=body, timeout=timeout)

def http_delete(url: str, timeout: int = 15) -> tuple[int, Any]:
    return _http("DELETE", url, timeout=timeout)


# ─────────────────────────────────────────────────────────────────────────────
# MaintenanceRunner
# ─────────────────────────────────────────────────────────────────────────────

class MaintenanceRunner:

    def run(self) -> int:
        """Orchestrate all maintenance phases.
        Returns 0=OK, 1=WARNING, 2=ERROR."""
        self.started_at   = datetime.now()
        self._overall_label = "UNKNOWN"   # set by _write_report
        t0 = time.monotonic()

        print(f"\nMedical RAG — Nachtelijk onderhoud")
        print(f"Gestart: {self.started_at.strftime('%d-%m-%Y %H:%M:%S')}")
        print("─" * 56)

        self.disk_before = psutil.disk_usage("/")

        # Run the five measurement phases first so the report can be complete
        phases = [
            ("pre_check",    "Pre-checks",          self._phase_pre_check),
            ("qdrant",       "Qdrant maintenance",  self._phase_qdrant),
            ("consistency",  "Data consistentie",   self._phase_consistency),
            ("software",     "Software check",      self._phase_software),
            ("cleanup",      "Opruimen",            self._phase_cleanup),
        ]
        results: dict[str, dict] = {}
        for key, label, fn in phases:
            results[key] = self._run_phase(label, fn)

        self.disk_after = psutil.disk_usage("/")
        total = time.monotonic() - t0
        overall = self._overall_status(results)

        # Write report + update CONTEXT.md before the backup git commit
        try:
            self._write_report(results, total, overall)
        except Exception:
            print(f"  ⚠ Rapport schrijven mislukt:\n{traceback.format_exc()}")

        try:
            self._update_context(results, total, overall)
        except Exception:
            print(f"  ⚠ CONTEXT.md bijwerken mislukt:\n{traceback.format_exc()}")

        # Backup + final git push (always last)
        results["backup"] = self._run_phase("Backup & git push", self._phase_backup)
        total = time.monotonic() - t0
        overall = self._overall_status(results)

        print()
        print("─" * 56)
        icon = {"OK": "✅", "WARNING": "⚠️", "ERROR": "❌"}.get(overall, "?")
        print(f"  {icon} Uitslag   : {overall}")
        print(f"  Duur       : {total:.1f}s")
        print(f"  Rapport    : {REPORT_PATH.relative_to(BASE)}")
        print("─" * 56)

        return 0 if overall == "OK" else (1 if overall == "WARNING" else 2)

    # ── phase runner wrapper ─────────────────────────────────────────────────

    def _run_phase(self, label: str, fn) -> dict:
        t = time.monotonic()
        try:
            status, details = fn()
        except Exception:
            status  = "ERROR"
            details = {"findings": [f"Onverwachte fout:\n{traceback.format_exc()}"]}
        elapsed = time.monotonic() - t
        icon = {"OK": "✅", "WARNING": "⚠️", "ERROR": "❌"}.get(status, "?")
        first = (details.get("findings") or [""])[0]
        summary = first[:60] + "…" if len(first) > 60 else first
        print(f"  {icon} {label:<24} ({elapsed:.1f}s)  {summary}")
        return {"label": label, "status": status, "details": details, "elapsed": elapsed}

    def _overall_status(self, results: dict) -> str:
        statuses = [r["status"] for r in results.values()]
        if "ERROR"   in statuses: return "ERROR"
        if "WARNING" in statuses: return "WARNING"
        return "OK"

    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 1 — PRE-CHECKS
    # ─────────────────────────────────────────────────────────────────────────

    def _phase_pre_check(self) -> tuple[str, dict]:
        findings = []
        status   = "OK"

        # Disk
        disk    = psutil.disk_usage("/")
        free_gb = disk.free / 1e9
        if free_gb < 5:
            findings.append(f"KRITIEK: schijf slechts {free_gb:.1f} GB vrij")
            status = "ERROR"
        elif free_gb < 20:
            findings.append(f"WAARSCHUWING: schijf {free_gb:.1f} GB vrij (< 20 GB drempel)")
            status = "WARNING"
        else:
            findings.append(f"Schijf: {free_gb:.1f} GB vrij, {disk.percent:.0f}% gebruikt")

        # RAM
        mem      = psutil.virtual_memory()
        avail_gb = mem.available / 1e9
        if avail_gb < 2:
            findings.append(f"WAARSCHUWING: RAM slechts {avail_gb:.1f} GB beschikbaar")
            if status == "OK": status = "WARNING"
        else:
            findings.append(f"RAM: {avail_gb:.1f} GB beschikbaar, {mem.percent:.0f}% gebruikt")

        # Qdrant
        code, _ = http_get(f"{QDRANT_BASE}/healthz", timeout=5)
        if code == 200:
            findings.append("Qdrant: ✓ online")
        else:
            findings.append(f"Qdrant: OFFLINE (HTTP {code})")
            status = "ERROR"

        # Ollama
        code, data = http_get(f"{OLLAMA_BASE}/api/tags", timeout=5)
        if code == 200:
            models = [m["name"] for m in (data or {}).get("models", [])]
            findings.append(
                f"Ollama: ✓ online ({', '.join(models) if models else 'geen modellen'})"
            )
        else:
            findings.append(f"Ollama: OFFLINE (HTTP {code})")
            if status == "OK": status = "WARNING"

        # Docker
        r = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}: {{.Status}}"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0:
            containers = [l for l in r.stdout.strip().splitlines() if l]
            findings.append(f"Docker: {len(containers)} container(s) actief")
            findings.extend(f"  • {c}" for c in containers)
        else:
            findings.append("Docker: fout bij ophalen containers")
            if status == "OK": status = "WARNING"

        return status, {"findings": findings}

    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 2 — QDRANT MAINTENANCE
    # ─────────────────────────────────────────────────────────────────────────

    def _phase_qdrant(self) -> tuple[str, dict]:
        findings     = []
        status       = "OK"
        vector_counts: dict[str, int] = {}

        code, data = http_get(f"{QDRANT_BASE}/collections", timeout=10)
        if code != 200:
            return "ERROR", {
                "findings": [f"Qdrant niet bereikbaar: HTTP {code}"],
                "vector_counts": {},
            }

        collections = [c["name"] for c in data["result"]["collections"]]
        if not collections:
            findings.append("Geen collecties aangemaakt — niets te onderhouden")
            return "OK", {"findings": findings, "vector_counts": {}}

        BACKUP_QDRANT.mkdir(parents=True, exist_ok=True)

        for col in collections:
            # Vector count + optimizer status
            code2, cdata = http_get(f"{QDRANT_BASE}/collections/{col}", timeout=10)
            if code2 == 200 and isinstance(cdata, dict):
                res  = cdata.get("result", {})
                vc   = res.get("vectors_count", 0)
                opt  = res.get("optimizer_status", {})
                opt_s = opt.get("status", "?") if isinstance(opt, dict) else str(opt)
                vector_counts[col] = vc
                findings.append(f"{col}: {vc:,} vectoren, optimizer: {opt_s}")

            # Create snapshot
            code3, snap = http_post(
                f"{QDRANT_BASE}/collections/{col}/snapshots", timeout=60
            )
            if code3 in (200, 201) and isinstance(snap, dict):
                snap_name = (snap.get("result") or {}).get("name", "")
                if snap_name:
                    findings.append(f"{col}: snapshot aangemaakt: {snap_name}")
                    # Download locally
                    snap_url   = f"{QDRANT_BASE}/collections/{col}/snapshots/{snap_name}"
                    local_path = BACKUP_QDRANT / f"{col}_{snap_name}"
                    try:
                        req = urllib.request.Request(
                            snap_url,
                            headers={"User-Agent": "medical-rag-maintenance/1.0"},
                        )
                        with urllib.request.urlopen(req, timeout=180) as resp:
                            snap_bytes = resp.read()
                        size_mb = len(snap_bytes) / 1e6
                        if size_mb < MAX_SNAP_SIZE_MB:
                            local_path.write_bytes(snap_bytes)
                            findings.append(f"  → opgeslagen ({size_mb:.1f} MB)")
                        else:
                            findings.append(
                                f"  → te groot ({size_mb:.0f} MB > {MAX_SNAP_SIZE_MB} MB), "
                                "lokale kopie overgeslagen"
                            )
                    except Exception as exc:
                        findings.append(f"  → download mislukt: {exc}")
                        if status == "OK": status = "WARNING"
            else:
                findings.append(f"{col}: snapshot aanmaken mislukt (HTTP {code3})")
                if status == "OK": status = "WARNING"

            # Prune local backup copies — keep newest MAX_SNAPSHOTS
            local_snaps = sorted(
                BACKUP_QDRANT.glob(f"{col}_*"),
                key=lambda p: p.stat().st_mtime,
            )
            if len(local_snaps) > MAX_SNAPSHOTS:
                n_rm = len(local_snaps) - MAX_SNAPSHOTS
                for old in local_snaps[:n_rm]:
                    old.unlink()
                findings.append(f"{col}: {n_rm} lokale snapshot(s) opgeruimd")

            # Prune Qdrant-internal snapshots via API
            code4, slist = http_get(
                f"{QDRANT_BASE}/collections/{col}/snapshots", timeout=10
            )
            if code4 == 200 and isinstance(slist, dict):
                snaps = slist.get("result") or []
                if len(snaps) > MAX_SNAPSHOTS:
                    snaps_sorted = sorted(snaps, key=lambda s: s.get("name", ""))
                    n_old = len(snaps) - MAX_SNAPSHOTS
                    for old_s in snaps_sorted[:n_old]:
                        http_delete(
                            f"{QDRANT_BASE}/collections/{col}/snapshots/{old_s['name']}",
                            timeout=30,
                        )
                    findings.append(
                        f"{col}: {n_old} interne Qdrant-snapshots verwijderd"
                    )

        return status, {"findings": findings, "vector_counts": vector_counts}

    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 3 — DATA CONSISTENCY
    # ─────────────────────────────────────────────────────────────────────────

    def _phase_consistency(self) -> tuple[str, dict]:
        findings       = []
        status         = "OK"
        inconsistencies: list[str] = []

        meta_path = BASE / "data" / "books_metadata.json"
        if not meta_path.exists():
            return "OK", {
                "findings": ["books_metadata.json niet gevonden — niets te controleren"],
                "inconsistencies": [],
            }

        with open(meta_path) as f:
            metadata: dict = json.load(f)

        n_ingested = sum(1 for m in metadata.values() if m.get("ingested"))
        findings.append(
            f"{len(metadata)} boeken in metadata, {n_ingested} ingested"
        )

        # Qdrant collections for cross-reference
        code, cdata = http_get(f"{QDRANT_BASE}/collections", timeout=10)
        qdrant_cols = (
            [c["name"] for c in cdata["result"]["collections"]]
            if code == 200 else []
        )

        for slug, meta in metadata.items():
            if not meta.get("ingested"):
                continue
            src = meta.get("source_file", "")

            # File existence
            if src and not (BASE / "books" / src).exists():
                inconsistencies.append(f"BESTAND ONTBREEKT: {src} (slug: {slug})")
                if status == "OK": status = "WARNING"

            # Qdrant vector presence
            if src and qdrant_cols:
                col = meta.get("collection", "medical_literature")
                if col in qdrant_cols:
                    code2, res = http_post(
                        f"{QDRANT_BASE}/collections/{col}/points/scroll",
                        data={
                            "filter": {
                                "must": [{
                                    "key": "source_file",
                                    "match": {"value": src},
                                }]
                            },
                            "limit": 1,
                            "with_payload": False,
                        },
                        timeout=15,
                    )
                    if code2 == 200:
                        pts = (res or {}).get("result", {}).get("points", [])
                        if not pts:
                            inconsistencies.append(
                                f"GEEN VECTOREN: {src} ontbreekt in Qdrant-collectie {col}"
                            )
                            if status == "OK": status = "WARNING"

        # Orphan images
        imgs_dir = BASE / "data" / "extracted_images"
        if imgs_dir.exists():
            img_files = list(imgs_dir.glob("*.png"))
            orphans = []
            for img in img_files:
                m = re.match(r"^(.+?)_p\d+_fig\d+$", img.stem)
                if m and m.group(1) not in metadata:
                    orphans.append(img.name)
            if orphans:
                findings.append(
                    f"{len(img_files)} afbeeldingen: {len(orphans)} wees-bestand(en)"
                )
                findings.extend(f"  • {o}" for o in orphans[:5])
                if len(orphans) > 5:
                    findings.append(f"  … +{len(orphans)-5} meer")
                if status == "OK": status = "WARNING"
            else:
                findings.append(
                    f"{len(img_files)} afbeeldingen gecontroleerd — geen wees-bestanden"
                )

        # image_memory.json broken references
        mem_path = BASE / "data" / "image_memory.json"
        if mem_path.exists():
            with open(mem_path) as f:
                img_memory: dict = json.load(f)
            broken = [
                f"{tissue}: {Path(p).name}"
                for tissue, paths in img_memory.items()
                if isinstance(paths, list)
                for p in paths
                if not Path(p).exists()
            ]
            if broken:
                findings.append(
                    f"image_memory.json: {len(broken)} kapotte verwijzing(en)"
                )
                findings.extend(f"  • {b}" for b in broken[:3])
                if len(broken) > 3:
                    findings.append(f"  … +{len(broken)-3} meer")
                if status == "OK": status = "WARNING"
            else:
                total_refs = sum(
                    len(v) for v in img_memory.values() if isinstance(v, list)
                )
                findings.append(
                    f"image_memory.json: {total_refs} verwijzing(en) — allemaal geldig"
                )

        if inconsistencies:
            findings.append(f"⚠ {len(inconsistencies)} inconsistentie(s) gevonden:")
            findings.extend(f"  • {i}" for i in inconsistencies)
        else:
            findings.append("Consistentie: geen problemen gevonden")

        return status, {"findings": findings, "inconsistencies": inconsistencies}

    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 4 — SOFTWARE UPDATE CHECK (report only, never installs)
    # ─────────────────────────────────────────────────────────────────────────

    def _phase_software(self) -> tuple[str, dict]:
        findings = []
        status   = "OK"

        # pip outdated
        r = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
            capture_output=True, text=True, timeout=120,
        )
        if r.returncode == 0:
            try:
                outdated = json.loads(r.stdout or "[]")
            except json.JSONDecodeError:
                outdated = []
            if outdated:
                findings.append(f"{len(outdated)} pip-pakket(ten) verouderd:")
                for pkg in outdated:
                    findings.append(
                        f"  • {pkg['name']}  {pkg['version']} → {pkg['latest_version']}"
                    )
                status = "WARNING"
            else:
                findings.append("Alle pip-pakketten up-to-date")
        else:
            findings.append("pip list --outdated: niet beschikbaar of mislukt")

        # Docker image info
        r2 = subprocess.run(
            ["docker", "images",
             "--format", "{{.Repository}}:{{.Tag}}\t{{.CreatedSince}}\t{{.Size}}"],
            capture_output=True, text=True, timeout=10,
        )
        if r2.returncode == 0 and r2.stdout.strip():
            findings.append("Docker images:")
            findings.extend(f"  • {l}" for l in r2.stdout.strip().splitlines())

        # GitHub latest releases
        for svc, repo in [("Qdrant", "qdrant/qdrant"), ("Ollama", "ollama/ollama")]:
            try:
                code, data = http_get(
                    f"https://api.github.com/repos/{repo}/releases/latest",
                    timeout=10,
                )
                if code == 200 and isinstance(data, dict):
                    tag = data.get("tag_name", "?")
                    pub = (data.get("published_at") or "")[:10]
                    findings.append(f"{svc} nieuwste release: {tag} ({pub})")
                elif code == 403:
                    findings.append(f"{svc}: GitHub API rate-limit bereikt")
                else:
                    findings.append(f"{svc}: GitHub niet bereikbaar (HTTP {code})")
            except Exception as exc:
                findings.append(f"{svc}: GitHub check mislukt: {exc}")

        return status, {"findings": findings}

    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 5 — CLEANUP
    # ─────────────────────────────────────────────────────────────────────────

    def _phase_cleanup(self) -> tuple[str, dict]:
        findings    = []
        status      = "OK"
        bytes_freed = 0

        cutoff_1d  = time.time() - 86_400
        cutoff_7d  = time.time() - 7  * 86_400
        cutoff_30d = time.time() - MAX_PROC_LOG_DAYS * 86_400

        # Stale /tmp files (pdf, epub, log) older than 1 day
        removed_tmp = 0
        for pattern in ("/tmp/*.pdf", "/tmp/*.epub", "/tmp/*.log"):
            for p in glob.glob(pattern):
                try:
                    st = os.stat(p)
                    if st.st_mtime < cutoff_1d:
                        bytes_freed += st.st_size
                        os.unlink(p)
                        removed_tmp += 1
                except OSError:
                    pass
        if removed_tmp:
            findings.append(f"/tmp: {removed_tmp} verouderd(e) bestand(en) verwijderd")
        else:
            findings.append("/tmp: geen verouderde bestanden")

        # Rotate /tmp/web.log → keep last 1 000 lines
        weblog = Path("/tmp/web.log")
        if weblog.exists():
            try:
                lines = weblog.read_text(errors="replace").splitlines()
                if len(lines) > 1_000:
                    old_size = weblog.stat().st_size
                    weblog.write_text("\n".join(lines[-1_000:]) + "\n")
                    saved = old_size - weblog.stat().st_size
                    bytes_freed += max(saved, 0)
                    findings.append(
                        f"web.log geroteerd: {len(lines):,} → 1 000 regels"
                    )
                else:
                    findings.append(
                        f"web.log: {len(lines)} regels — geen rotatie nodig"
                    )
            except Exception as exc:
                findings.append(f"web.log rotatie mislukt: {exc}")

        # Processing logs older than MAX_PROC_LOG_DAYS days
        proc_dir    = BASE / "data" / "processing_logs"
        removed_proc = 0
        if proc_dir.exists():
            for f in proc_dir.glob("*.json"):
                try:
                    if f.stat().st_mtime < cutoff_30d:
                        bytes_freed += f.stat().st_size
                        f.unlink()
                        removed_proc += 1
                except OSError:
                    pass
        if removed_proc:
            findings.append(
                f"processing_logs: {removed_proc} logbestand(en) "
                f"(> {MAX_PROC_LOG_DAYS} dgn) verwijderd"
            )

        # Qdrant backup snapshots older than 7 days
        removed_snaps = 0
        if BACKUP_QDRANT.exists():
            for f in BACKUP_QDRANT.glob("*"):
                try:
                    if f.stat().st_mtime < cutoff_7d:
                        bytes_freed += f.stat().st_size
                        f.unlink()
                        removed_snaps += 1
                except OSError:
                    pass
        if removed_snaps:
            findings.append(
                f"backups/qdrant: {removed_snaps} snapshot(s) (> 7 dgn) verwijderd"
            )

        # Summary
        if bytes_freed > 0:
            if bytes_freed >= 1e9:
                freed_str = f"{bytes_freed/1e9:.2f} GB"
            elif bytes_freed >= 1e6:
                freed_str = f"{bytes_freed/1e6:.1f} MB"
            else:
                freed_str = f"{bytes_freed/1024:.0f} KB"
            findings.append(f"Totaal vrijgemaakt: {freed_str}")
        else:
            findings.append("Totaal vrijgemaakt: 0 (niets te verwijderen)")

        return status, {"findings": findings, "bytes_freed": bytes_freed}

    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 6 — BACKUP + GIT
    # ─────────────────────────────────────────────────────────────────────────

    def _phase_backup(self) -> tuple[str, dict]:
        findings = []
        status   = "OK"
        today    = datetime.now().strftime("%Y-%m-%d")

        BACKUP_META.mkdir(parents=True, exist_ok=True)

        # JSON metadata backups
        for src_rel, prefix in [
            ("data/books_metadata.json",  "books_metadata"),
            ("data/image_memory.json",    "image_memory"),
        ]:
            src = BASE / src_rel
            if src.exists():
                dest = BACKUP_META / f"{prefix}_{today}.json"
                try:
                    shutil.copy2(src, dest)
                    findings.append(f"Backup: {src.name} → {dest.name}")
                except Exception as exc:
                    findings.append(f"Backup {src.name} mislukt: {exc}")
                    if status == "OK": status = "WARNING"

        # Prune old metadata backups
        for prefix in ["books_metadata", "image_memory"]:
            existing = sorted(
                BACKUP_META.glob(f"{prefix}_*.json"), key=lambda p: p.name
            )
            if len(existing) > MAX_META_BACKUPS:
                n_rm = len(existing) - MAX_META_BACKUPS
                for old in existing[:n_rm]:
                    old.unlink()
                findings.append(
                    f"{prefix}: {n_rm} oude backup(s) verwijderd "
                    f"(max {MAX_META_BACKUPS} bewaard)"
                )

        # Weekly git tag on Sundays
        if datetime.now().weekday() == 6:  # Sunday = 6
            tag = f"weekly-{today}"
            r = subprocess.run(
                ["git", "tag", "-a", tag, "-m", f"Weekly stable point {today}"],
                cwd=BASE, capture_output=True, text=True,
            )
            if r.returncode == 0:
                subprocess.run(
                    ["git", "push", "origin", tag],
                    cwd=BASE, capture_output=True, timeout=30,
                )
                findings.append(f"Git tag aangemaakt en gepusht: {tag}")
            else:
                # tag may already exist from a previous run today
                findings.append(
                    f"Git tag overgeslagen: {r.stderr.strip()[:80]}"
                )

        # Git add + commit + push
        subprocess.run(
            ["git", "add",
             "SYSTEM_DOCS/MAINTENANCE_REPORT.md",
             "SYSTEM_DOCS/CONTEXT.md",
             "PROJECT_STATE.md"],
            cwd=BASE, capture_output=True, text=True,
        )
        commit_msg = (
            f"maintenance: nightly {today} — {self._overall_label}"
        )
        r_commit = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=BASE, capture_output=True, text=True,
        )
        out = r_commit.stdout + r_commit.stderr
        if "nothing to commit" in out:
            findings.append("Git commit: geen wijzigingen")
        elif r_commit.returncode == 0:
            findings.append("Git commit: geslaagd")
        else:
            findings.append(f"Git commit mislukt: {out.strip()[:120]}")
            if status == "OK": status = "WARNING"

        r_push = subprocess.run(
            ["git", "push"], cwd=BASE, capture_output=True, text=True, timeout=30,
        )
        if r_push.returncode == 0:
            findings.append("Git push: geslaagd")
        else:
            err = r_push.stderr.strip()[:120]
            findings.append(f"Git push mislukt: {err}")
            if status == "OK": status = "WARNING"

        return status, {"findings": findings}

    # ─────────────────────────────────────────────────────────────────────────
    # REPORT WRITER
    # ─────────────────────────────────────────────────────────────────────────

    def _write_report(self, results: dict, total: float, overall: str):
        now  = self.started_at.strftime("%d-%m-%Y %H:%M:%S")
        icon = {"OK": "✅", "WARNING": "⚠️", "ERROR": "❌"}.get(overall, "?")
        pi   = {"OK": "✅", "WARNING": "⚠️", "ERROR": "❌"}

        db   = self.disk_before
        da   = self.disk_after
        freed_bytes = max(0, da.free - db.free)
        freed_str   = (
            f"{freed_bytes/1e6:.1f} MB" if freed_bytes > 0 else "—"
        )

        lines = [
            "# Maintenance Report — Medical RAG",
            "",
            f"**Datum:** {now}  ",
            f"**Duur:** {total:.1f}s  ",
            f"**Uitslag:** {icon} {overall}  ",
            "",
            "---",
            "",
            "## Samenvatting",
            "",
            "| Fase | Status | Duur | Bevinding |",
            "|---|---|---|---|",
        ]
        for r in results.values():
            first = (r["details"].get("findings") or ["—"])[0]
            first = (first[:68] + "…") if len(first) > 68 else first
            lines.append(
                f"| {r['label']} | {pi[r['status']]} {r['status']} "
                f"| {r['elapsed']:.1f}s | {first} |"
            )

        lines += [
            "",
            f"**Schijf voor:** {db.free/1e9:.1f} GB vrij  ",
            f"**Schijf na:** {da.free/1e9:.1f} GB vrij  ",
            f"**Vrijgemaakt:** {freed_str}  ",
            "",
            "---",
            "",
        ]

        # Detailed findings per phase
        for r in results.values():
            lines.append(f"## {pi[r['status']]} {r['label']}")
            lines.append("")
            for finding in r["details"].get("findings", []):
                prefix = "" if finding.startswith("  ") else "- "
                lines.append(f"{prefix}{finding}")
            lines.append("")

        # Qdrant vector count table
        vc = results.get("qdrant", {}).get("details", {}).get("vector_counts", {})
        if vc:
            lines += [
                "---", "",
                "## Qdrant vectortelling", "",
                "| Collectie | Vectoren |",
                "|---|---|",
            ]
            for col, count in vc.items():
                lines.append(f"| `{col}` | {count:,} |")
            lines.append("")

        # Data inconsistencies
        incons = (
            results.get("consistency", {}).get("details", {}).get("inconsistencies", [])
        )
        if incons:
            lines += [
                "---", "",
                "## ⚠ Data-inconsistenties", "",
            ]
            lines.extend(f"- {i}" for i in incons)
            lines.append("")

        # Recommendations
        lines += ["---", "", "## Aanbevelingen", ""]
        recs = []
        sw_findings = results.get("software", {}).get("details", {}).get("findings", [])
        if any("→" in f for f in sw_findings):
            recs.append(
                "**Pip-pakketten:** Update selectief met "
                "`pip install <pakket> --break-system-packages`. "
                "Nooit `pip install --upgrade-all` — kan LlamaIndex/Docling breken."
            )
        if any("OFFLINE" in f
               for r in results.values()
               for f in r["details"].get("findings", [])):
            recs.append(
                "**Service offline:** Controleer met `docker ps` en "
                "`systemctl status medical-rag-web`."
            )
        if incons:
            recs.append(
                "**Inconsistenties:** Draai `ingest_books.py` opnieuw voor de "
                "genoemde bestanden, of verwijder de vermeldingen uit "
                "`data/books_metadata.json`."
            )
        if not recs:
            recs.append("Systeem is gezond — geen actie vereist.")

        lines.extend(f"- {rec}" for rec in recs)
        lines += [
            "",
            "---",
            "",
            f"*Gegenereerd door `scripts/nightly_maintenance.py` op {now}*",
        ]

        REPORT_PATH.write_text("\n".join(lines))
        self._overall_label = overall   # used by backup phase for commit message

    # ─────────────────────────────────────────────────────────────────────────
    # CONTEXT.md — ## Maintenance status section
    # ─────────────────────────────────────────────────────────────────────────

    def _update_context(self, results: dict, total: float, overall: str):
        now  = self.started_at.strftime("%d-%m-%Y %H:%M")
        icon = {"OK": "✅", "WARNING": "⚠️", "ERROR": "❌"}.get(overall, "?")

        n_ok   = sum(1 for r in results.values() if r["status"] == "OK")
        n_warn = sum(1 for r in results.values() if r["status"] == "WARNING")
        n_err  = sum(1 for r in results.values() if r["status"] == "ERROR")

        if overall == "OK":
            summary = f"Alle {n_ok} fasen geslaagd"
        elif overall == "WARNING":
            summary = f"{n_warn} waarschuwing(en), {n_ok} OK"
        else:
            summary = f"{n_err} fout(en), {n_warn} waarschuwing(en)"

        section = (
            "## Maintenance status\n\n"
            f"**Laatste run:** {now} ({total:.1f}s)  \n"
            f"**Uitslag:** {icon} {overall} — {summary}  \n"
            "\n"
        )

        ctx = CONTEXT_PATH.read_text()
        pattern = re.compile(
            r"## Maintenance status\n.*?(?=\n---|\n## |\Z)", re.DOTALL
        )
        if pattern.search(ctx):
            ctx = pattern.sub(section.rstrip() + "\n", ctx)
        else:
            # Insert before ## Test status if present, else ## Git / state tracking
            for anchor in ("## Test status", "## Git / state tracking"):
                if anchor in ctx:
                    idx = ctx.index(anchor)
                    ctx = ctx[:idx] + section + "\n---\n\n" + ctx[idx:]
                    break
            else:
                ctx = ctx.rstrip() + "\n\n---\n\n" + section

        CONTEXT_PATH.write_text(ctx)


# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    return MaintenanceRunner().run()


if __name__ == "__main__":
    sys.exit(main())
