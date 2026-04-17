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
from datetime import datetime, time as dtime
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

def http_put(url: str, data: dict | None = None, timeout: int = 30) -> tuple[int, Any]:
    body = json.dumps(data).encode() if data is not None else b""
    return _http("PUT", url, data=body, timeout=timeout)

def http_delete(url: str, timeout: int = 15) -> tuple[int, Any]:
    return _http("DELETE", url, timeout=timeout)


# ─────────────────────────────────────────────────────────────────────────────
# Nightly helpers
# ─────────────────────────────────────────────────────────────────────────────

WEB_BASE = "http://localhost:8000"


def _in_window(start_hm: str, end_hm: str) -> bool:
    """Return True if current local time is within [start_hm, end_hm) (HH:MM).
    Handles midnight crossing (e.g. '23:00'–'03:00')."""
    try:
        sh, sm = (int(x) for x in start_hm.split(":"))
        eh, em = (int(x) for x in end_hm.split(":"))
        from zoneinfo import ZoneInfo
        now    = datetime.now(ZoneInfo("Europe/Amsterdam"))
        t_now   = dtime(now.hour, now.minute)
        t_start = dtime(sh, sm)
        t_end   = dtime(eh, em)
    except (ValueError, AttributeError):
        return True  # malformed → don't restrict
    if t_start <= t_end:
        return t_start <= t_now < t_end
    # midnight crossing
    return t_now >= t_start or t_now < t_end


def _pause_queues() -> None:
    """Pause book-ingest and transcription queues via the web API."""
    for path in ("/library/pause", "/videos/pause"):
        try:
            http_post(f"{WEB_BASE}{path}")
        except Exception:
            pass


def _resume_queues() -> None:
    """Resume book-ingest and transcription queues."""
    for path in ("/library/resume", "/videos/resume"):
        try:
            http_post(f"{WEB_BASE}{path}")
        except Exception:
            pass


def _count_skipped_chunks() -> int:
    """Count total skipped chunks across all books (from state.json)."""
    total = 0
    cache = BASE / "data" / "ingest_cache"
    if not cache.exists():
        return 0
    for sp in cache.glob("*/state.json"):
        try:
            state = json.loads(sp.read_text())
            skipped = (state.get("phases", {}).get("audit", {})
                       .get("chunks_skipped", 0)) or 0
            total += int(skipped)
        except Exception:
            pass
    return total


def _count_books_needing_extraction() -> int:
    """Count books with qdrant=done but no images_metadata.json yet."""
    total = 0
    cache = BASE / "data" / "ingest_cache"
    images_out = BASE / "data" / "extracted_images"
    if not cache.exists():
        return 0
    for state_file in cache.glob("*/state.json"):
        try:
            state = json.loads(state_file.read_text())
            phases = state.get("phases", {})
            if (phases.get("qdrant") or {}).get("status") != "done":
                continue
            bh = state.get("book_hash", state_file.parent.name)
            meta = images_out / bh / "images_metadata.json"
            if not meta.exists():
                total += 1
        except Exception:
            pass
    return total


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

        # Pause ingestion queues for the duration of the maintenance run
        _pause_queues()

        # ── Compute smart time-window allocation ─────────────────────────
        allocation: dict = {"retroaudit_seconds": None, "image_extract_seconds": None}
        try:
            sys.path.insert(0, str(BASE / "scripts"))
            from nightly_stats import allocate_window as _alloc_win
            from claude_audit import load_settings as _ls_alloc, \
                is_enabled as _claude_enabled_alloc
            _cfg_alloc  = _ls_alloc().get("nightly", {})
            _start_hm   = _cfg_alloc.get("start_time", "00:00")
            _end_hm     = _cfg_alloc.get("end_time",   "07:00")
            _sh, _sm    = map(int, _start_hm.split(":"))
            _eh, _em    = map(int, _end_hm.split(":"))
            _window_sec = max(0, (_eh * 60 + _em) - (_sh * 60 + _sm)) * 60
            _raw_alloc  = _alloc_win(
                window_seconds    = _window_sec,
                n_chunks_skipped  = _count_skipped_chunks(),
                n_images_pending  = _count_books_needing_extraction(),
                claude_api_enabled= _claude_enabled_alloc(),
            )
            allocation = {
                "retroaudit_seconds":    _raw_alloc.get("retroaudit_seconds"),
                "image_extract_seconds": _raw_alloc.get("image_seconds"),
            }
            print(f"  Tijdverdeling: {_raw_alloc.get('note','')}")
            print(f"  Retroaudit budget: {allocation['retroaudit_seconds']}s  "
                  f"Image extractie budget: {allocation['image_extract_seconds']}s")
        except Exception as _alloc_err:
            print(f"  ⚠ Tijdverdeling berekening mislukt: {_alloc_err} — geen limiet")
        # ─────────────────────────────────────────────────────────────────

        results: dict[str, dict] = {}
        try:
            phases = [
                ("pre_check",      "Pre-checks",           self._phase_pre_check),
                ("qdrant",         "Qdrant maintenance",   self._phase_qdrant),
                ("consistency",    "Data consistentie",    self._phase_consistency),
                ("retro_audit",    "Retroaudit chunks",
                 lambda: self._phase_retro_audit(
                     time_budget_seconds=allocation["retroaudit_seconds"])),
                ("image_extract",   "Afbeelding extractie",
                 lambda: self._phase_image_extract(
                     time_budget_seconds=allocation["image_extract_seconds"])),
                ("state_integrity","State integriteit",    self._phase_state_integrity),
                ("software",       "Software check",       self._phase_software),
                ("cleanup",        "Opruimen",             self._phase_cleanup),
            ]
            for key, label, fn in phases:
                results[key] = self._run_phase(label, fn)
        finally:
            # Always resume queues, even if a phase throws
            _resume_queues()

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

        # ── Qdrant ↔ disk consistency: transcripts ───────────────────────────
        trans_dir = BASE / "data" / "transcripts"
        trans_findings, trans_incons = self._check_transcript_consistency(qdrant_cols)
        findings.extend(trans_findings)
        inconsistencies.extend(trans_incons)
        if trans_incons:
            if status == "OK": status = "WARNING"

        # ── Qdrant ↔ disk consistency: books ─────────────────────────────────
        book_findings, book_incons = self._check_book_consistency(qdrant_cols)
        findings.extend(book_findings)
        inconsistencies.extend(book_incons)
        if book_incons:
            if status == "OK": status = "WARNING"

        # ── Write consistency log ─────────────────────────────────────────────
        self._write_consistency_log(trans_incons + book_incons, status)

        return status, {"findings": findings, "inconsistencies": inconsistencies}

    def _check_transcript_consistency(
        self, qdrant_cols: list[str]
    ) -> tuple[list[str], list[str]]:
        """
        For each JSON transcript in data/transcripts/, verify it has vectors
        in video_transcripts.  Re-ingest if missing.
        """
        findings: list[str] = []
        incons:   list[str] = []
        trans_dir = BASE / "data" / "transcripts"

        if not trans_dir.exists():
            return ["Transcripts: map niet gevonden"], []

        json_files = list(trans_dir.glob("*.json"))
        if not json_files:
            return ["Transcripts: geen JSON bestanden gevonden"], []

        if "video_transcripts" not in qdrant_cols:
            return [f"Transcripts: {len(json_files)} bestanden, collectie bestaat niet"], []

        missing = []
        for jf in json_files:
            code, res = http_post(
                f"{QDRANT_BASE}/collections/video_transcripts/points/scroll",
                data={
                    "filter": {"must": [{"key": "source_file", "match": {"value": jf.name}}]},
                    "limit": 1,
                    "with_payload": False,
                },
                timeout=10,
            )
            if code == 200:
                pts = (res or {}).get("result", {}).get("points", [])
                if not pts:
                    missing.append(jf)
            else:
                findings.append(f"Transcripts: Qdrant query mislukt voor {jf.name} (HTTP {code})")

        findings.append(
            f"Transcripts: {len(json_files)} bestanden, "
            f"{len(json_files) - len(missing)} in Qdrant, "
            f"{len(missing)} ontbreken"
        )

        if not missing:
            return findings, []

        # Determine video_type from videos/ directory structure
        video_dirs: dict[str, str] = {}
        for vtype in ("qat", "nrt", "pemf", "rlt"):
            vdir = BASE / "videos" / vtype
            if vdir.exists():
                for vf in vdir.glob("*"):
                    video_dirs[vf.stem] = vtype

        re_ingested = 0
        for jf in missing:
            stem   = jf.stem
            vtype  = video_dirs.get(stem, "qat")  # default qat if unknown
            incons.append(f"TRANSCRIPT ONTBREEKT IN QDRANT: {jf.name} (type: {vtype})")
            # Re-ingest
            r = subprocess.run(
                [sys.executable, str(BASE / "scripts" / "ingest_transcript.py"),
                 "--file", str(jf), "--video-type", vtype],
                capture_output=True, text=True, timeout=120,
            )
            if r.returncode == 0:
                findings.append(f"  → her-ingestered: {jf.name}")
                re_ingested += 1
            else:
                findings.append(f"  → her-ingest mislukt: {jf.name}: {r.stderr.strip()[:80]}")

        if re_ingested:
            findings.append(f"Transcripts: {re_ingested} bestand(en) her-ingestered")

        return findings, incons

    def _check_book_consistency(
        self, qdrant_cols: list[str]
    ) -> tuple[list[str], list[str]]:
        """
        For each approved book audit in data/book_quality/, verify it has
        vectors in the appropriate collection.  Re-queue if missing.
        """
        findings: list[str] = []
        incons:   list[str] = []
        quality_dir = BASE / "data" / "book_quality"
        queue_file  = Path("/tmp/book_ingest_queue.json")

        if not quality_dir.exists():
            return ["Boeken: book_quality map niet gevonden"], []

        audit_files = list(quality_dir.glob("*_audit.json"))
        if not audit_files:
            return ["Boeken: geen audit-bestanden gevonden"], []

        re_queued = 0
        checked   = 0

        for af in audit_files:
            try:
                audit = json.loads(af.read_text())
            except Exception:
                continue
            if audit.get("status") != "approved":
                continue

            book_file  = audit.get("book", "")
            collection = audit.get("collection", "medical_library")
            checked   += 1

            if collection not in qdrant_cols:
                continue

            code, res = http_post(
                f"{QDRANT_BASE}/collections/{collection}/points/scroll",
                data={
                    "filter": {"must": [{"key": "source_file", "match": {"value": book_file}}]},
                    "limit": 1,
                    "with_payload": False,
                },
                timeout=10,
            )
            if code != 200:
                continue
            pts = (res or {}).get("result", {}).get("points", [])
            if pts:
                continue

            # No vectors — find book file and re-queue
            incons.append(f"BOEK ONTBREEKT IN QDRANT: {book_file} (collectie: {collection})")

            # Locate the physical file
            book_path: Path | None = None
            for sub in ("medical_literature", "nrt", "qat", "device", "acupuncture", "anatomy", "medical"):
                candidate = BASE / "books" / sub / book_file
                if candidate.exists():
                    book_path = candidate
                    break

            if book_path is None:
                findings.append(f"  → bestand niet gevonden op disk: {book_file}")
                continue

            # Add to queue
            try:
                q: list[dict] = []
                if queue_file.exists():
                    q = json.loads(queue_file.read_text())
                # Only add if not already queued
                already = any(item.get("filename") == book_file for item in q)
                if not already:
                    q.append({"filename": book_file, "collection": collection,
                              "filepath": str(book_path)})
                    queue_file.write_text(json.dumps(q, indent=2))
                    findings.append(f"  → terug in wachtrij gezet: {book_file}")
                    re_queued += 1
                else:
                    findings.append(f"  → al in wachtrij: {book_file}")
            except Exception as exc:
                findings.append(f"  → wachtrij-update mislukt: {exc}")

        findings.insert(0,
            f"Boeken: {checked} goedgekeurde audit(s) gecontroleerd, "
            f"{len(incons)} ontbreken in Qdrant, {re_queued} her-in-wachtrij gezet"
        )
        return findings, incons

    def _write_consistency_log(self, incons: list[str], status: str) -> None:
        """Write a timestamped summary to /var/log/nightly_consistency.log."""
        log_path = Path("/var/log/nightly_consistency.log")
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [f"=== {ts} — {status} ==="]
        if incons:
            lines.extend(f"  {i}" for i in incons)
        else:
            lines.append("  Geen inconsistenties gevonden")
        lines.append("")
        try:
            with open(log_path, "a") as f:
                f.write("\n".join(lines) + "\n")
        except Exception as e:
            print(f"  ⚠ consistency log schrijven mislukt: {e}")

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
    # PHASE 4b — RETROACTIVE AUDIT
    # ─────────────────────────────────────────────────────────────────────────

    def _phase_retro_audit(self,
                           time_budget_seconds: float | None = None,
                           ) -> tuple[str, dict]:
        """Retry tagging for chunks skipped by Ollama. Claude API primary, Ollama fallback."""
        findings   = []
        status     = "OK"
        COLLECTION = "medical_library"
        t_phase_start = time.monotonic()

        import sys as _sys
        _sys.path.insert(0, str(BASE / "scripts"))

        # Budget = 0 means skipped this run (e.g. Claude on-demand mode)
        if time_budget_seconds is not None and time_budget_seconds <= 0:
            findings.append(
                "Claude API actief — retroaudit wordt op aanvraag uitgevoerd via UI"
            )
            return "OK", {"findings": findings}

        # Determine engine and chunk limit
        try:
            from claude_audit import is_enabled as _claude_enabled, audit_chunks_parallel
            use_claude = _claude_enabled()
        except ImportError:
            use_claude = False

        try:
            from claude_audit import load_settings as _ls_ca
            _cfg_nm = _ls_ca().get("nightly", {})
        except Exception:
            _cfg_nm = {}
        win_start = _cfg_nm.get("start_time", "00:00")
        win_end   = _cfg_nm.get("end_time",   "07:00")

        if not _in_window(win_start, win_end):
            findings.append(
                f"Buiten tijdvenster ({win_start}–{win_end}) — retroaudit overgeslagen"
            )
            return "OK", {"findings": findings}

        # Chunk limit: time-budget driven if available, else fallback defaults
        if time_budget_seconds:
            try:
                from nightly_stats import load_stats as _load_ns
                _ns = _load_ns()
                _spc = _ns["retroaudit"]["avg_sec_per_chunk"]
                MAX_CHUNKS = max(1, int(time_budget_seconds / _spc))
                findings.append(
                    f"Tijdsbudget: {time_budget_seconds}s  "
                    f"({_spc:.1f}s/chunk → max {MAX_CHUNKS} chunks)"
                )
            except Exception:
                MAX_CHUNKS = 10_000 if use_claude else 200
        elif use_claude:
            MAX_CHUNKS = 10_000
        else:
            MAX_CHUNKS = 200

        if use_claude:
            findings.append(f"Engine: Claude API · venster {win_start}–{win_end}")
        else:
            findings.append(f"Engine: Ollama · venster {win_start}–{win_end}")

        # 1. Check Qdrant availability first
        code, _ = http_get(f"{QDRANT_BASE}/healthz", timeout=5)
        if code != 200:
            findings.append("Qdrant offline — retroaudit overgeslagen")
            return "WARNING", {"findings": findings}

        # 2. Scroll for all skipped chunks
        code, data = http_post(
            f"{QDRANT_BASE}/collections/{COLLECTION}/points/scroll",
            data={
                "filter": {
                    "should": [
                        {"key": "audit_status", "match": {"value": "skipped_ollama_timeout"}},
                        {"key": "audit_status", "match": {"value": "skipped_claude_error"}},
                    ]
                },
                "limit":        MAX_CHUNKS,
                "with_payload": True,
                "with_vectors": False,
            },
            timeout=30,
        )

        if code != 200:
            findings.append(f"Qdrant scroll mislukt (HTTP {code}) — retroaudit overgeslagen")
            return "WARNING", {"findings": findings}

        points_raw = (data.get("result") or {}).get("points", [])
        if not points_raw:
            findings.append("Geen overgeslagen chunks gevonden — niets te doen")
            return "OK", {"findings": findings}

        findings.append(f"{len(points_raw)} overgeslagen chunk(s) gevonden voor retroaudit")

        # Build (point_id, chunk_dict) pairs
        id_chunk_pairs: list[tuple] = []
        for pt in points_raw:
            pid     = pt.get("id")
            payload = pt.get("payload") or {}
            if pid is not None:
                id_chunk_pairs.append((pid, payload))

        chunks_only = [pair[1] for pair in id_chunk_pairs]

        # 3a. Claude path
        if use_claude:
            # Clear audit_status before sending to Claude
            for c in chunks_only:
                c.pop("audit_status", None)

            tagged_list = audit_chunks_parallel(chunks_only)
            scored        = 0
            still_pending = 0

            for (pid, _), chunk in zip(id_chunk_pairs, tagged_list):
                if (chunk.get("audit_status") or "").startswith("skipped"):
                    still_pending += 1
                    continue
                update_payload = {
                    "kai_k":          chunk.get("kai_k", 3),
                    "kai_a":          chunk.get("kai_a", 3),
                    "kai_i":          chunk.get("kai_i", 3),
                    "tags":           chunk.get("tags", []),
                    "summary":        chunk.get("summary", ""),
                    "audit_status":   "tagged_claude",
                    "audit_engine":   "claude_api",
                }
                http_put(
                    f"{QDRANT_BASE}/collections/{COLLECTION}/points/payload",
                    data={"payload": update_payload, "points": [pid]},
                    timeout=10,
                )
                scored += 1

        # 3b. Ollama path
        else:
            try:
                from audit_book import tag_chunks_with_ollama
            except ImportError as exc:
                findings.append(f"Import audit_book mislukt: {exc} — retroaudit overgeslagen")
                return "WARNING", {"findings": findings}

            for _, chunk in id_chunk_pairs:
                chunk.pop("audit_status", None)

            tag_chunks_with_ollama(chunks_only)
            scored        = 0
            still_pending = 0

            for pid, chunk in id_chunk_pairs:
                if chunk.get("audit_status") == "skipped_ollama_timeout":
                    still_pending += 1
                    continue
                update_payload = {
                    "usability_tags":     chunk.get("usability_tags", []),
                    "protocol_relevance": chunk.get("protocol_relevance", 0.0),
                    "has_point_codes":    chunk.get("has_point_codes", False),
                    "has_figure_refs":    chunk.get("has_figure_refs", False),
                    "primary_use":        chunk.get("primary_use", ""),
                    "audit_status":       "tagged",
                }
                http_put(
                    f"{QDRANT_BASE}/collections/{COLLECTION}/points/payload",
                    data={"payload": update_payload, "points": [pid]},
                    timeout=10,
                )
                scored += 1

        elapsed_phase = time.monotonic() - t_phase_start
        findings.append(
            f"Retroaudit: {len(id_chunk_pairs)} geprobeerd, "
            f"{scored} gescoord, {still_pending} nog uitstaand"
        )
        if scored == 0 and still_pending > 0:
            status = "WARNING"

        # Record timing stats for future allocation
        try:
            from nightly_stats import record_retroaudit as _rec_ra
            _rec_ra(scored, elapsed_phase)
        except Exception:
            pass

        return status, {"findings": findings}

    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 4b — IMAGE EXTRACTION
    # ─────────────────────────────────────────────────────────────────────────

    def _phase_image_extract(self,
                             time_budget_seconds: float | None = None,
                             ) -> tuple[str, dict]:
        """
        For each book with qdrant=done and pdf_cropped/epub image_source but no
        images_metadata.json yet, run extract_figures_from_pdf / extract_images_from_epub.
        """
        findings = []
        status   = "OK"
        CACHE_DIR  = BASE / "data" / "ingest_cache"
        IMAGES_OUT = BASE / "data" / "extracted_images"
        t_start = time.monotonic()

        if not CACHE_DIR.exists():
            findings.append("ingest_cache map niet gevonden — overgeslagen")
            return "OK", {"findings": findings}

        sys.path.insert(0, str(BASE / "scripts"))
        try:
            from image_extractor import extract_figures_from_pdf, extract_images_from_epub
        except ImportError as exc:
            findings.append(f"Import image_extractor mislukt: {exc} — overgeslagen")
            return "WARNING", {"findings": findings}

        # Load book_classifications.json for image_source per book
        kai_cache: dict = {}
        try:
            cfg_path = BASE / "config" / "book_classifications.json"
            kai_cache = json.loads(cfg_path.read_text()).get("classifications", {})
        except Exception:
            pass

        def _get_image_source(filepath: str) -> str:
            """Determine image_source from book_classifications or filename extension."""
            for entry in kai_cache.values():
                for pat in entry.get("filename_patterns", []):
                    if pat.lower() in Path(filepath).name.lower():
                        src = entry.get("image_source", "")
                        if src:
                            return src
            ext = Path(filepath).suffix.lower()
            return "epub" if ext == ".epub" else "pdf_cropped" if ext == ".pdf" else "none"

        if time_budget_seconds is not None:
            findings.append(f"Tijdsbudget afbeelding extractie: {time_budget_seconds}s")

        extracted_books = 0
        total_figures   = 0

        for state_file in CACHE_DIR.glob("*/state.json"):
            if time_budget_seconds is not None:
                elapsed = time.monotonic() - t_start
                if elapsed >= time_budget_seconds:
                    findings.append(
                        f"Tijdsbudget bereikt ({elapsed:.0f}s / "
                        f"{time_budget_seconds}s) — gestopt"
                    )
                    break

            try:
                state = json.loads(state_file.read_text())
            except Exception:
                continue

            phases = state.get("phases", {})
            if (phases.get("qdrant") or {}).get("status") != "done":
                continue

            book_hash = state.get("book_hash", state_file.parent.name)
            meta_path = IMAGES_OUT / book_hash / "images_metadata.json"
            if meta_path.exists():
                continue  # already extracted

            filepath = state.get("filepath", "")
            if not filepath:
                continue

            book_path = Path(filepath)
            if not book_path.exists():
                findings.append(f"{book_path.name}: bestand niet gevonden — overgeslagen")
                continue

            image_source = _get_image_source(filepath)
            if image_source == "none":
                continue

            book_name = state.get("filename", book_path.name)
            try:
                if image_source == "pdf_cropped":
                    imgs = extract_figures_from_pdf(book_path, book_hash, IMAGES_OUT)
                else:
                    imgs = extract_images_from_epub(book_path, book_hash, IMAGES_OUT)
                n = len(imgs)
                findings.append(f"{book_name}: {n} afbeeldingen geëxtraheerd")
                total_figures   += n
                extracted_books += 1
            except Exception as exc:
                findings.append(f"{book_name}: extractie mislukt: {exc}")
                if status == "OK":
                    status = "WARNING"

        elapsed_total = time.monotonic() - t_start

        if extracted_books == 0:
            findings.append("Geen boeken gevonden voor afbeelding extractie")
        else:
            findings.append(
                f"Totaal: {extracted_books} boek(en), "
                f"{total_figures} afbeeldingen in {elapsed_total:.0f}s"
            )

        try:
            from nightly_stats import record_image_screening as _rec_im
            _rec_im(total_figures, elapsed_total)
        except Exception:
            pass

        return status, {"findings": findings}

    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 4c — STATE MACHINE INTEGRITY
    # ─────────────────────────────────────────────────────────────────────────

    def _phase_state_integrity(self) -> tuple[str, dict]:
        """
        Compare Qdrant chunk counts vs state.json for each completed book.
        Flag books where qdrant phase shows done but no vectors found.
        """
        findings = []
        status   = "OK"
        CACHE_DIR = BASE / "data" / "ingest_cache"
        COLLECTION = "medical_library"

        if not CACHE_DIR.exists():
            findings.append("ingest_cache map niet gevonden — overgeslagen")
            return "OK", {"findings": findings}

        # Check Qdrant availability
        code, _ = http_get(f"{QDRANT_BASE}/healthz", timeout=5)
        if code != 200:
            findings.append("Qdrant offline — state integriteit overgeslagen")
            return "WARNING", {"findings": findings}

        checked = ok_count = mismatch_count = 0

        for state_file in CACHE_DIR.glob("*/state.json"):
            try:
                state = json.loads(state_file.read_text())
            except Exception:
                continue

            phases = state.get("phases", {})
            qdrant_done = (phases.get("qdrant") or {}).get("status") == "done"
            if not qdrant_done:
                continue

            book_filename = state.get("filename", "")
            expected_chunks = (phases.get("qdrant") or {}).get("chunks_upserted", 0)
            checked += 1

            code2, res = http_post(
                f"{QDRANT_BASE}/collections/{COLLECTION}/points/count",
                data={
                    "filter": {
                        "must": [{
                            "key": "source_file",
                            "match": {"value": book_filename},
                        }]
                    },
                    "exact": True,
                },
                timeout=15,
            )
            if code2 != 200:
                findings.append(f"Qdrant query mislukt voor {book_filename} (HTTP {code2})")
                continue

            actual = (res or {}).get("result", {}).get("count", 0)

            if actual == 0 and expected_chunks > 0:
                findings.append(
                    f"MISMATCH: {book_filename} — verwacht {expected_chunks} chunks, "
                    f"Qdrant heeft 0"
                )
                mismatch_count += 1
                if status == "OK": status = "WARNING"
            elif actual > 0:
                ok_count += 1
            else:
                findings.append(f"{book_filename}: 0 chunks — qdrant was leeg bij embed?")

        findings.insert(0,
            f"State integriteit: {checked} voltooide boeken gecontroleerd, "
            f"{ok_count} OK, {mismatch_count} mismatches"
        )
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

        # Ingest cache phase files older than 30 days
        # Keep: state.json + phase4_done.marker  (needed for re-ingest detection)
        # Delete: phase1_chunks.json, phase2_audited.json, phase3_vectors.npy
        CACHE_DIR = BASE / "data" / "ingest_cache"
        CACHE_PHASE_FILES = {"phase1_chunks.json", "phase2_audited.json", "phase3_vectors.npy"}
        removed_cache = 0
        if CACHE_DIR.exists():
            for state_file in CACHE_DIR.glob("*/state.json"):
                book_dir = state_file.parent
                try:
                    state = json.loads(state_file.read_text())
                    phases = state.get("phases", {})
                    qdrant_done = (phases.get("qdrant") or {}).get("status") == "done"
                    if not qdrant_done:
                        continue  # never clean up incomplete ingests
                    completed_at = (phases.get("qdrant") or {}).get("completed_at", "")
                    if completed_at:
                        try:
                            ts = datetime.fromisoformat(completed_at)
                            age_days = (datetime.now() - ts.replace(tzinfo=None)).days
                            if age_days < MAX_PROC_LOG_DAYS:
                                continue
                        except Exception:
                            pass
                    # Remove bulky phase files
                    for fname in CACHE_PHASE_FILES:
                        fp = book_dir / fname
                        if fp.exists():
                            try:
                                bytes_freed += fp.stat().st_size
                                fp.unlink()
                                removed_cache += 1
                            except OSError:
                                pass
                except Exception:
                    continue
        if removed_cache:
            findings.append(
                f"ingest_cache: {removed_cache} fase-bestand(en) "
                f"(> {MAX_PROC_LOG_DAYS} dgn oud) verwijderd"
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
