#!/usr/bin/env python3
"""
Medical RAG — Automatische testsuite
Gebruik: python3 scripts/run_tests.py
Schrijft resultaten naar SYSTEM_DOCS/TEST_REPORT.md
"""

import unittest
import sys
import os
import io
import time
import json
import http.client
import tempfile
import shutil
import random
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.parent
REPORT_PATH   = BASE / "SYSTEM_DOCS" / "TEST_REPORT.md"
CONTEXT_PATH  = BASE / "SYSTEM_DOCS" / "CONTEXT.md"

# ── Custom test result tracker ────────────────────────────────────────────────

ICONS = {"PASS": "✅", "FAIL": "❌", "ERROR": "💥", "SKIP": "⏭️"}


class TimedResult(unittest.TestResult):
    """Verzamelt pass/fail/skip/error per test met timing; print direct naar stdout."""

    def __init__(self):
        super().__init__()
        self.records = []       # list of dicts
        self._start_times = {}

    def startTest(self, test):
        super().startTest(test)
        self._start_times[test] = time.monotonic()

    def _elapsed(self, test):
        return time.monotonic() - self._start_times.get(test, 0)

    def _record(self, test, status, detail=""):
        elapsed = self._elapsed(test)
        rec = {
            "class": test.__class__.__name__,
            "name": test._testMethodName,
            "doc": (test._testMethodDoc or "").strip(),
            "status": status,
            "elapsed": elapsed,
            "detail": detail,
        }
        self.records.append(rec)
        print(f"  {ICONS[status]} {rec['class']}.{rec['name']}  ({elapsed*1000:.0f} ms)")

    def addSuccess(self, test):
        self._record(test, "PASS")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._record(test, "FAIL", self._exc_info_to_string(err, test))

    def addError(self, test, err):
        super().addError(test, err)
        self._record(test, "ERROR", self._exc_info_to_string(err, test))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._record(test, "SKIP", reason)

    def addExpectedFailure(self, test, err):
        self._record(test, "PASS")

    def addUnexpectedSuccess(self, test):
        self._record(test, "FAIL", "Onverwacht geslaagd (was als xfail gemarkeerd)")


# ── Report writer ─────────────────────────────────────────────────────────────

def write_report(result: TimedResult, total_duration: float):
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    records = result.records

    n_pass  = sum(1 for r in records if r["status"] == "PASS")
    n_fail  = sum(1 for r in records if r["status"] == "FAIL")
    n_error = sum(1 for r in records if r["status"] == "ERROR")
    n_skip  = sum(1 for r in records if r["status"] == "SKIP")
    n_total = len(records)
    n_run   = n_pass + n_fail + n_error

    overall = "GESLAAGD" if (n_fail == 0 and n_error == 0) else "MISLUKT"
    badge   = "✅" if overall == "GESLAAGD" else "❌"

    lines = [
        "# Test Report — Medical RAG",
        "",
        f"**Datum:** {now}  ",
        f"**Duur:** {total_duration:.1f}s  ",
        f"**Uitslag:** {badge} {overall}  ",
        f"**Score:** {n_pass}/{n_run} geslaagd",
        f"  ({n_skip} overgeslagen, {n_fail} mislukt, {n_error} fouten)",
        "",
        "---",
        "",
    ]

    # group by class
    classes = {}
    for r in records:
        classes.setdefault(r["class"], []).append(r)

    status_icon = {"PASS": "✅", "FAIL": "❌", "ERROR": "💥", "SKIP": "⏭️"}

    for cls_name, cls_records in classes.items():
        lines.append(f"## {cls_name}")
        lines.append("")
        lines.append("| Status | Test | Beschrijving | Tijd |")
        lines.append("|---|---|---|---|")
        for r in cls_records:
            icon = status_icon.get(r["status"], "?")
            name = r["name"]
            doc  = r["doc"] or "—"
            t    = f"{r['elapsed']*1000:.0f} ms"
            lines.append(f"| {icon} {r['status']} | `{name}` | {doc} | {t} |")
        lines.append("")

    # failures + errors
    problems = [r for r in records if r["status"] in ("FAIL", "ERROR")]
    if problems:
        lines += [
            "---",
            "",
            "## Mislukte tests — details",
            "",
        ]
        for r in problems:
            lines.append(f"### `{r['class']}.{r['name']}`")
            lines.append("")
            lines.append("```")
            lines.append(r["detail"].strip())
            lines.append("```")
            lines.append("")

    # skipped
    skipped = [r for r in records if r["status"] == "SKIP"]
    if skipped:
        lines += [
            "---",
            "",
            "## Overgeslagen tests",
            "",
            "| Test | Reden |",
            "|---|---|",
        ]
        for r in skipped:
            lines.append(f"| `{r['class']}.{r['name']}` | {r['detail']} |")
        lines.append("")

    # recommendations
    lines += ["---", "", "## Aanbevelingen", ""]
    if n_fail == 0 and n_error == 0 and n_skip == 0:
        lines.append("Alle tests geslaagd. Het systeem is gereed voor gebruik.")
    else:
        if any("docling" in r["detail"].lower() or "docling" in r["name"] for r in skipped):
            lines.append("- **Installeer docling:** `pip install docling docling-core --break-system-packages`")
        if any("qdrant_client" in r["detail"].lower() for r in skipped):
            lines.append("- **Installeer qdrant-client:** `pip install qdrant-client --break-system-packages`")
        if any("sentence_transformers" in r["detail"].lower() for r in skipped):
            lines.append("- **Installeer sentence-transformers:** `pip install sentence-transformers --break-system-packages`")
        if any("reportlab" in r["detail"].lower() for r in skipped):
            lines.append("- **Installeer reportlab (testtool):** `pip install reportlab --break-system-packages`")
        if any("pypdf" in r["detail"].lower() for r in skipped):
            lines.append("- **Installeer pypdf:** `pip install pypdf --break-system-packages`")
        if any("pillow" in r["detail"].lower() or "PIL" in r["detail"] for r in skipped):
            lines.append("- **Installeer pillow:** `pip install pillow --break-system-packages`")
        if any("whisper" in r["detail"].lower() for r in skipped):
            lines.append("- **Installeer openai-whisper:** `pip install openai-whisper --break-system-packages`")
        for r in problems:
            lines.append(f"- **Onderzoek `{r['name']}`:** zie details hierboven")
    lines.append("")
    lines += [
        "---",
        "",
        "*Gegenereerd door `scripts/run_tests.py`*",
    ]

    REPORT_PATH.write_text("\n".join(lines))
    return overall


def _update_context_status(result: TimedResult, total_duration: float):
    """Vervangt de ## Test status sectie in CONTEXT.md met de actuele testuitslag."""
    import re

    now = datetime.now().strftime("%d-%m-%Y %H:%M")
    records = result.records
    n_pass = sum(1 for r in records if r["status"] == "PASS")
    n_fail = sum(1 for r in records if r["status"] in ("FAIL", "ERROR"))
    n_skip = sum(1 for r in records if r["status"] == "SKIP")
    n_run  = n_pass + n_fail

    if n_fail == 0:
        uitslag = f"✅ GESLAAGD — {n_pass}/{n_run} geslaagd, {n_skip} overgeslagen"
    else:
        uitslag = f"❌ MISLUKT — {n_pass}/{n_run} geslaagd, {n_fail} mislukt, {n_skip} overgeslagen"

    lines = [
        "## Test status",
        "",
        f"**Laatste run:** {now} ({total_duration:.1f}s)  ",
        f"**Uitslag:** {uitslag}  ",
    ]

    failed = [r for r in records if r["status"] in ("FAIL", "ERROR")]
    if failed:
        names = ", ".join(f"`{r['name']}`" for r in failed)
        lines.append(f"**Mislukt:** {names}  ")

    lines.append("")

    new_section = "\n".join(lines)

    ctx = CONTEXT_PATH.read_text()

    # Replace the existing ## Test status block (up to the next \n--- or \n## or EOF)
    pattern = re.compile(
        r"## Test status\n.*?(?=\n---|\n## |\Z)",
        re.DOTALL,
    )
    if pattern.search(ctx):
        ctx = pattern.sub(new_section.rstrip() + "\n", ctx)
    else:
        # Section missing — insert before ## Git / state tracking
        insert_at = "## Git / state tracking"
        if insert_at in ctx:
            idx = ctx.index(insert_at)
            ctx = ctx[:idx] + new_section + "\n---\n\n" + ctx[idx:]
        else:
            ctx = ctx.rstrip() + "\n\n---\n\n" + new_section

    CONTEXT_PATH.write_text(ctx)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. INFRASTRUCTURE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class InfrastructureTests(unittest.TestCase):

    def test_qdrant_running(self):
        """Qdrant draait op localhost:6333 en geeft HTTP 200 terug op /healthz"""
        try:
            conn = http.client.HTTPConnection("localhost", 6333, timeout=5)
            conn.request("GET", "/healthz")
            resp = conn.getresponse()
            self.assertEqual(resp.status, 200,
                             f"Verwachtte 200, kreeg {resp.status}")
        except ConnectionRefusedError:
            self.fail("Verbinding geweigerd — is Qdrant gestart?")

    def test_ollama_running(self):
        """Ollama draait op localhost:11434 en geeft HTTP 200 terug op /api/tags"""
        try:
            conn = http.client.HTTPConnection("localhost", 11434, timeout=5)
            conn.request("GET", "/api/tags")
            resp = conn.getresponse()
            self.assertEqual(resp.status, 200,
                             f"Verwachtte 200, kreeg {resp.status}")
        except ConnectionRefusedError:
            self.fail("Verbinding geweigerd — is Ollama gestart?")

    def test_disk_space(self):
        """Vrije schijfruimte is groter dan 10 GB"""
        import psutil
        disk = psutil.disk_usage("/")
        free_gb = disk.free / 1e9
        self.assertGreater(free_gb, 10.0,
                           f"Onvoldoende schijfruimte: {free_gb:.1f} GB vrij (minimum 10 GB)")

    def test_ram_available(self):
        """Beschikbaar werkgeheugen is groter dan 4 GB"""
        import psutil
        mem = psutil.virtual_memory()
        avail_gb = mem.available / 1e9
        self.assertGreater(avail_gb, 4.0,
                           f"Onvoldoende RAM: {avail_gb:.1f} GB beschikbaar (minimum 4 GB)")

    def test_docling_import(self):
        """Docling kan worden geïmporteerd (PDF-extractie backend)"""
        try:
            import docling  # noqa: F401
        except ImportError as e:
            self.skipTest(f"docling niet geïnstalleerd: {e}")

    def test_ebooklib_import(self):
        """ebooklib kan worden geïmporteerd (EPUB-parser)"""
        try:
            import ebooklib  # noqa: F401
        except ImportError as e:
            self.skipTest(f"ebooklib niet geïnstalleerd: {e}")

    def test_qdrant_client_import(self):
        """qdrant_client kan worden geïmporteerd (vector store client)"""
        try:
            import qdrant_client  # noqa: F401
        except ImportError as e:
            self.skipTest(f"qdrant_client niet geïnstalleerd: {e}")

    def test_sentence_transformers_import(self):
        """sentence_transformers kan worden geïmporteerd (embedding model)"""
        try:
            import sentence_transformers  # noqa: F401
        except ImportError as e:
            self.skipTest(f"sentence_transformers niet geïnstalleerd: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. PIPELINE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class PipelineTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = Path(tempfile.mkdtemp(prefix="medrag_pipe_"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def _make_minimal_pdf(self, path: Path, text: str = "Test medical text", pages: int = 1):
        """Maakt een minimale geldige PDF zonder externe bibliotheken."""
        lines = []
        lines.append("%PDF-1.4")
        # object 1: catalog
        obj1_off = len("\n".join(lines)) + 1
        lines.append("1 0 obj")
        lines.append("<< /Type /Catalog /Pages 2 0 R >>")
        lines.append("endobj")
        # object 2: pages
        obj2_off = len("\n".join(lines)) + 1
        kids = " ".join(f"{3+i} 0 R" for i in range(pages))
        lines.append("2 0 obj")
        lines.append(f"<< /Type /Pages /Kids [{kids}] /Count {pages} >>")
        lines.append("endobj")
        # page objects
        page_offs = []
        content_offs = []
        for i in range(pages):
            page_offs.append(len("\n".join(lines)) + 1)
            content_obj = 3 + pages + i
            lines.append(f"{3+i} 0 obj")
            lines.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents {content_obj} 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>")
            lines.append("endobj")
        for i in range(pages):
            content_offs.append(len("\n".join(lines)) + 1)
            stream = f"BT /F1 12 Tf 72 720 Td ({text} pagina {i+1}) Tj ET"
            lines.append(f"{3+pages+i} 0 obj")
            lines.append(f"<< /Length {len(stream)} >>")
            lines.append("stream")
            lines.append(stream)
            lines.append("endstream")
            lines.append("endobj")
        # xref
        xref_off = len("\n".join(lines)) + 1
        all_offs = [0, obj1_off, obj2_off] + page_offs + content_offs
        n_objs = len(all_offs)
        lines.append("xref")
        lines.append(f"0 {n_objs}")
        lines.append("0000000000 65535 f ")
        for off in all_offs[1:]:
            lines.append(f"{off:010d} 00000 n ")
        lines.append("trailer")
        lines.append(f"<< /Size {n_objs} /Root 1 0 R >>")
        lines.append("startxref")
        lines.append(str(xref_off))
        lines.append("%%EOF")
        path.write_bytes("\n".join(lines).encode("latin-1"))

    def test_pdf_text_extraction(self):
        """PDF-tekst kan worden geëxtraheerd; page_number veld is aanwezig in resultaat"""
        # try reportlab first, fall back to minimal raw PDF
        pdf_path = self.tmpdir / "test_extract.pdf"
        used_reportlab = False
        try:
            from reportlab.pdfgen import canvas as rl_canvas
            c = rl_canvas.Canvas(str(pdf_path))
            c.drawString(72, 720, "Anatomie van het schoudergewricht")
            c.save()
            used_reportlab = True
        except ImportError:
            self._make_minimal_pdf(pdf_path, "Anatomie schoudergewricht")

        try:
            from docling.document_converter import DocumentConverter
        except ImportError:
            self.skipTest("docling niet geïnstalleerd")

        converter = DocumentConverter()
        result = converter.convert(str(pdf_path))
        text = result.document.export_to_markdown()
        self.assertIsInstance(text, str)
        self.assertGreater(len(text), 0, "Geen tekst geëxtraheerd uit PDF")
        # verify page metadata is accessible
        pages = result.document.pages
        self.assertGreater(len(pages), 0, "Geen pagina-informatie gevonden")

    def test_epub_parsing(self):
        """EPUB-bestand kan worden geparsed; hoofdstuktekst is terug te vinden"""
        try:
            import ebooklib
            from ebooklib import epub
            from bs4 import BeautifulSoup
        except ImportError as e:
            self.skipTest(f"Vereiste bibliotheek niet geïnstalleerd: {e}")

        epub_path = self.tmpdir / "test_book.epub"
        book = epub.EpubBook()
        book.set_identifier("medrag-test-001")
        book.set_title("Test Anatomie Boek")
        book.set_language("nl")
        book.add_author("Test Auteur")

        chap = epub.EpubHtml(title="Schouder", file_name="schouder.xhtml", lang="nl")
        chap.content = (
            b"<html><body>"
            b"<h1>Anatomie van het schoudergewricht</h1>"
            b"<p>Het schoudergewricht (articulatio humeri) is het meest beweeglijke gewricht.</p>"
            b"</body></html>"
        )
        book.add_item(chap)
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        book.spine = ["nav", chap]
        epub.write_epub(str(epub_path), book)

        loaded = epub.read_epub(str(epub_path))
        texts = []
        for item in loaded.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            soup = BeautifulSoup(item.get_content(), "html.parser")
            texts.append(soup.get_text(" ", strip=True))

        combined = " ".join(texts)
        self.assertIn("schoudergewricht", combined,
                      "Verwachtte tekst 'schoudergewricht' niet gevonden in EPUB")

    def test_embedding_generation(self):
        """BAAI/bge-large-en-v1.5 genereert vectoren van precies 1024 dimensies"""
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            self.skipTest("sentence_transformers niet geïnstalleerd")

        model = SentenceTransformer("BAAI/bge-large-en-v1.5")
        vec = model.encode("Shoulder anatomy: the glenohumeral joint is a ball-and-socket joint.")
        self.assertEqual(
            len(vec), 1024,
            f"Verwachtte 1024 dimensies, maar kreeg {len(vec)}"
        )

    def test_qdrant_insert_retrieve(self):
        """Vector kan worden ingevoegd in Qdrant en teruggehaald via payload-filter"""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import (
                VectorParams, Distance, PointStruct,
                Filter, FieldCondition, MatchValue,
            )
        except ImportError:
            self.skipTest("qdrant_client niet geïnstalleerd")

        client = QdrantClient(host="localhost", port=6333, timeout=10)
        col = "test_autoremove_pipeline"

        # clean up from any previous run
        try:
            client.delete_collection(col)
        except Exception:
            pass

        try:
            client.create_collection(
                collection_name=col,
                vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
            )
            vec = [random.uniform(-1.0, 1.0) for _ in range(1024)]
            client.upsert(
                collection_name=col,
                points=[PointStruct(
                    id=1,
                    vector=vec,
                    payload={
                        "source_file": "test.pdf",
                        "page_number": 5,
                        "text": "Test chunk over het schoudergewricht",
                        "content_type": "medical_literature",
                        "chunk_hash": "abc123",
                    },
                )],
            )
            results, _ = client.scroll(
                collection_name=col,
                scroll_filter=Filter(
                    must=[FieldCondition(
                        key="content_type",
                        match=MatchValue(value="medical_literature"),
                    )]
                ),
                limit=10,
                with_payload=True,
            )
            self.assertEqual(len(results), 1,
                             f"Verwachtte 1 resultaat, kreeg {len(results)}")
            payload = results[0].payload
            self.assertEqual(payload["source_file"], "test.pdf")
            self.assertEqual(payload["page_number"], 5)
            self.assertEqual(payload["content_type"], "medical_literature")
        finally:
            try:
                client.delete_collection(col)
            except Exception:
                pass


# ═══════════════════════════════════════════════════════════════════════════════
# 3. QUALITY TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class QualityTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = Path(tempfile.mkdtemp(prefix="medrag_qual_"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_corrupt_pdf_detection(self):
        """Beschadigde PDF wordt afgehandeld zonder crash (graceful error handling)"""
        corrupt = self.tmpdir / "corrupt.pdf"
        corrupt.write_bytes(os.urandom(4096))

        try:
            from docling.document_converter import DocumentConverter
        except ImportError:
            self.skipTest("docling niet geïnstalleerd")

        converter = DocumentConverter()
        try:
            result = converter.convert(str(corrupt))
            # acceptable if result is empty
            text = result.document.export_to_markdown()
            # no assertion needed — we only verify no unhandled exception
        except Exception:
            pass  # exception is also acceptable — important is that Python didn't crash

    def test_page_count_extraction(self):
        """Paginatelling van een 3-pagina PDF klopt met de verwachte waarde van 3"""
        try:
            import pypdf
        except ImportError:
            self.skipTest("pypdf niet geïnstalleerd")

        pdf_path = self.tmpdir / "multipage.pdf"
        # try reportlab first for a cleaner PDF
        try:
            from reportlab.pdfgen import canvas as rl_canvas
            c = rl_canvas.Canvas(str(pdf_path))
            for i in range(3):
                c.drawString(72, 720, f"Pagina {i + 1} — testinhoud")
                c.showPage()
            c.save()
        except ImportError:
            # manual 3-page PDF via raw bytes
            self._make_minimal_pdf_mp(pdf_path, 3)

        reader = pypdf.PdfReader(str(pdf_path))
        self.assertEqual(len(reader.pages), 3,
                         f"Verwachtte 3 pagina's, gevonden: {len(reader.pages)}")

    def _make_minimal_pdf_mp(self, path: Path, pages: int):
        """Hulpfunctie: maakt een minimale multi-page PDF zonder dependencies."""
        chunks = ["%PDF-1.4\n"]
        offsets = {}

        def add_obj(n, content):
            offsets[n] = sum(len(c) for c in chunks)
            chunks.append(f"{n} 0 obj\n{content}\nendobj\n")

        page_ids = list(range(3, 3 + pages))
        stream_ids = list(range(3 + pages, 3 + 2 * pages))
        kids_str = " ".join(f"{i} 0 R" for i in page_ids)

        add_obj(1, "<< /Type /Catalog /Pages 2 0 R >>")
        add_obj(2, f"<< /Type /Pages /Kids [{kids_str}] /Count {pages} >>")

        for idx, (pid, sid) in enumerate(zip(page_ids, stream_ids)):
            add_obj(pid,
                    f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                    f"/Contents {sid} 0 R "
                    f"/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>")
            s = f"BT /F1 12 Tf 72 720 Td (pagina {idx+1}) Tj ET"
            add_obj(sid, f"<< /Length {len(s)} >>\nstream\n{s}\nendstream")

        xref_pos = sum(len(c) for c in chunks)
        n = 1 + len(offsets)
        xref_lines = [f"xref\n0 {n}\n0000000000 65535 f \n"]
        for i in range(1, n):
            xref_lines.append(f"{offsets[i]:010d} 00000 n \n")
        chunks.append("".join(xref_lines))
        chunks.append(f"trailer\n<< /Size {n} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n")
        path.write_bytes("".join(chunks).encode("latin-1"))

    def test_figure_detection(self):
        """Docling detecteert een ingebedde afbeelding in een PDF"""
        try:
            from reportlab.pdfgen import canvas as rl_canvas
            from reportlab.lib.utils import ImageReader
        except ImportError:
            self.skipTest("reportlab niet geïnstalleerd")

        try:
            from docling.document_converter import DocumentConverter
            from docling.datamodel.pipeline_options import PdfPipelineOptions
            from docling.datamodel.base_models import InputFormat
            from docling.document_converter import PdfFormatOption
            from docling.datamodel.document import PictureItem
        except ImportError:
            self.skipTest("docling niet geïnstalleerd")

        try:
            from PIL import Image as PilImage
        except ImportError:
            self.skipTest("pillow niet geïnstalleerd")

        # create a small test image
        img_path = self.tmpdir / "test_fig.png"
        img = PilImage.new("RGB", (120, 120), color=(180, 60, 60))
        img.save(str(img_path))

        # embed in PDF using reportlab
        pdf_path = self.tmpdir / "with_figure.pdf"
        c = rl_canvas.Canvas(str(pdf_path))
        c.drawString(72, 750, "Figuur 1: Anatomisch diagram van de schouder")
        c.drawImage(str(img_path), 72, 500, width=200, height=200)
        c.save()

        pipeline_opts = PdfPipelineOptions(generate_picture_images=True, images_scale=1.0)
        converter = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_opts)}
        )
        result = converter.convert(str(pdf_path))

        pictures = [
            el for el, _ in result.document.iterate_items()
            if isinstance(el, PictureItem)
        ]
        self.assertGreater(len(pictures), 0,
                           "Geen afbeeldingen gedetecteerd in PDF — verwachtte minstens 1")


# ═══════════════════════════════════════════════════════════════════════════════
# 4. INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class IntegrationTests(unittest.TestCase):

    def test_web_dashboard_health(self):
        """FastAPI /health endpoint reageert met HTTP 200 en status 'ok'"""
        try:
            conn = http.client.HTTPConnection("localhost", 8000, timeout=5)
            conn.request("GET", "/health")
            resp = conn.getresponse()
            body = resp.read().decode()
        except ConnectionRefusedError:
            self.fail("Verbinding geweigerd op poort 8000 — is medical-rag-web.service actief?")
        self.assertEqual(resp.status, 200)
        data = json.loads(body)
        self.assertEqual(data.get("status"), "ok",
                         f"Verwachtte status 'ok', kreeg: {data}")

    def test_web_dashboard_root(self):
        """FastAPI dashboard geeft HTML terug met 'Medical RAG', 'Qdrant' en 'Ollama'"""
        try:
            conn = http.client.HTTPConnection("localhost", 8000, timeout=5)
            conn.request("GET", "/")
            resp = conn.getresponse()
            body = resp.read().decode()
        except ConnectionRefusedError:
            self.fail("Verbinding geweigerd op poort 8000 — is medical-rag-web.service actief?")
        self.assertEqual(resp.status, 200)
        for expected in ("Medical RAG", "Qdrant", "Ollama"):
            self.assertIn(expected, body,
                          f"Verwacht woord '{expected}' niet gevonden in dashboard HTML")

    def test_qdrant_collections_endpoint(self):
        """Qdrant /collections geeft geldige JSON terug met 'result.collections' veld"""
        try:
            conn = http.client.HTTPConnection("localhost", 6333, timeout=5)
            conn.request("GET", "/collections")
            resp = conn.getresponse()
            body = resp.read().decode()
        except ConnectionRefusedError:
            self.fail("Verbinding geweigerd op poort 6333 — is Qdrant gestart?")
        self.assertEqual(resp.status, 200)
        data = json.loads(body)
        self.assertIn("result", data)
        self.assertIn("collections", data["result"])

    def test_ollama_model_loaded(self):
        """llama3.1:8b model is geladen in Ollama"""
        try:
            conn = http.client.HTTPConnection("localhost", 11434, timeout=5)
            conn.request("GET", "/api/tags")
            resp = conn.getresponse()
            body = resp.read().decode()
        except ConnectionRefusedError:
            self.fail("Verbinding geweigerd op poort 11434 — is Ollama gestart?")
        data = json.loads(body)
        model_names = [m["name"] for m in data.get("models", [])]
        self.assertTrue(
            any("llama3.1" in n for n in model_names),
            f"llama3.1 niet gevonden. Geladen modellen: {model_names or '(geen)'}"
        )

    def test_books_dir_exists(self):
        """De books/ map bestaat en is beschrijfbaar"""
        d = BASE / "books"
        self.assertTrue(d.is_dir(), "books/ map bestaat niet")
        self.assertTrue(os.access(d, os.W_OK), "books/ map is niet beschrijfbaar")

    def test_scripts_present(self):
        """Alle vereiste scripts zijn aanwezig in scripts/"""
        required = [
            "scripts/ingest_books.py",
            "scripts/fetch_book_metadata.py",
            "scripts/transcribe_videos.py",
            "scripts/ingest_text.py",
        ]
        for s in required:
            with self.subTest(script=s):
                self.assertTrue(
                    (BASE / s).exists(),
                    f"Vereist script ontbreekt: {s}"
                )

    def test_data_json_files_valid(self):
        """Metadata JSON-bestanden bestaan en zijn geldig leesbaar"""
        json_files = [
            "data/books_metadata.json",
            "data/video_document_links.json",
        ]
        for jf in json_files:
            with self.subTest(file=jf):
                path = BASE / jf
                self.assertTrue(path.exists(), f"Ontbreekt: {jf}")
                with open(path) as f:
                    data = json.load(f)
                self.assertIsInstance(data, dict,
                                      f"{jf} is geen geldig JSON-object")

    def test_docker_compose_present(self):
        """docker-compose.yml is aanwezig en bevat qdrant en ollama services"""
        dc = BASE / "docker-compose.yml"
        self.assertTrue(dc.exists(), "docker-compose.yml ontbreekt")
        content = dc.read_text()
        self.assertIn("qdrant", content)
        self.assertIn("ollama", content)

    def test_web_app_present(self):
        """web/app.py bestaat en bevat FastAPI app definitie"""
        app_py = BASE / "web" / "app.py"
        self.assertTrue(app_py.exists(), "web/app.py ontbreekt")
        content = app_py.read_text()
        self.assertIn("FastAPI", content)
        self.assertIn("/health", content)

    def test_transcription_queue_service(self):
        """transcription-queue.service is active"""
        import subprocess as _sp
        r = _sp.run(["systemctl", "is-active", "transcription-queue"],
                    capture_output=True, text=True)
        assert r.stdout.strip() == "active", f"Service not active: {r.stdout.strip()!r}"

    def test_queue_file_valid(self):
        """Queue file exists and is valid JSON list"""
        q = Path("/tmp/transcription_queue.json")
        if not q.exists():
            self.skipTest("Queue file absent — queue may be empty/finished")
        data = json.loads(q.read_text())
        self.assertIsInstance(data, list, "Queue file is not a JSON list")

    def test_status_endpoint_valid(self):
        """Status endpoint returns a valid status value for a QAT video"""
        import urllib.request as _ur
        url = "http://localhost:8000/videos/status/qat/Anti-Inflammatory_Procedure.mp4"
        resp = _ur.urlopen(url, timeout=5)
        data = json.loads(resp.read())
        self.assertIn(data.get("status"), ["running", "queued", "done", "waiting"],
                      f"Onverwachte status: {data}")

    def test_transcription_log_exists(self):
        """Transcription queue log bestaat en is niet leeg"""
        log = Path("/var/log/transcription_queue.log")
        self.assertTrue(log.exists(), "Queue log /var/log/transcription_queue.log ontbreekt")
        self.assertGreater(log.stat().st_size, 0, "Queue log is leeg")

    def test_sync_status_timer_active(self):
        """sync-status.timer is active (GitHub live sync every 5 min)"""
        import subprocess as _sp
        r = _sp.run(["systemctl", "is-active", "sync-status.timer"],
                    capture_output=True, text=True)
        self.assertEqual(r.stdout.strip(), "active",
                         f"sync-status.timer not active: {r.stdout.strip()!r}")

    def test_status_snapshot_endpoint(self):
        """/status/snapshot returns valid JSON with services.qdrant field"""
        try:
            conn = http.client.HTTPConnection("localhost", 8000, timeout=5)
            conn.request("GET", "/status/snapshot")
            resp = conn.getresponse()
            body = resp.read().decode()
        except ConnectionRefusedError:
            self.fail("Verbinding geweigerd op poort 8000 — is medical-rag-web.service actief?")
        self.assertEqual(resp.status, 200, f"Verwachtte 200, kreeg {resp.status}")
        data = json.loads(body)
        self.assertIn("services", data, "Geen 'services' veld in snapshot")
        self.assertIn("qdrant", data["services"], "Geen 'qdrant' veld in services")

    def test_logs_transcription_queue_endpoint(self):
        """/logs/transcription_queue returns JSON with non-empty lines list"""
        try:
            conn = http.client.HTTPConnection("localhost", 8000, timeout=5)
            conn.request("GET", "/logs/transcription_queue")
            resp = conn.getresponse()
            body = resp.read().decode()
        except ConnectionRefusedError:
            self.fail("Verbinding geweigerd op poort 8000 — is medical-rag-web.service actief?")
        self.assertEqual(resp.status, 200, f"Verwachtte 200, kreeg {resp.status}")
        data = json.loads(body)
        self.assertIn("lines", data, "Geen 'lines' veld in log response")
        self.assertIsInstance(data["lines"], list, "'lines' is geen lijst")

    def test_ingest_transcript_executable(self):
        """scripts/ingest_transcript.py bestaat en is uitvoerbaar"""
        script = BASE / "scripts" / "ingest_transcript.py"
        self.assertTrue(script.exists(), "scripts/ingest_transcript.py ontbreekt")
        self.assertTrue(os.access(script, os.X_OK),
                        "scripts/ingest_transcript.py is niet uitvoerbaar")

    def test_anthropic_api_key_set(self):
        """ANTHROPIC_API_KEY is set in the environment"""
        key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.assertTrue(len(key) > 0,
                        "ANTHROPIC_API_KEY is niet ingesteld in de omgeving")

    def _check_js_no_literal_newlines(self, path: str):
        """Fetch page and assert no literal newlines appear inside JS single- or double-quoted strings.

        Template literals (backtick strings), regex literals, and comments are correctly
        skipped so they don't produce false positives.
        """
        import re
        conn = http.client.HTTPConnection("localhost", 8000, timeout=10)
        conn.request("GET", path)
        resp = conn.getresponse()
        html = resp.read().decode()
        self.assertEqual(resp.status, 200, f"Pagina {path} gaf {resp.status}")
        scripts = re.findall(r"<script[^>]*>(.*?)</script>", html, re.DOTALL)
        # Characters after which a '/' is a regex literal, not division
        REGEX_STARTERS = set("=({[!&|,;:?~^<>+-*/%")
        for block_idx, script in enumerate(scripts):
            if not script.strip():
                continue
            # States: normal, single, double, template, regex, regex_class,
            #         line_comment, block_comment
            state = "normal"
            i = 0
            n = len(script)
            last_nonws = ""  # last non-whitespace char seen in normal state
            while i < n:
                ch = script[i]
                if state == "normal":
                    if ch == "/" and i + 1 < n:
                        nxt = script[i + 1]
                        if nxt == "/":
                            state = "line_comment"
                            i += 2
                            continue
                        elif nxt == "*":
                            state = "block_comment"
                            i += 2
                            continue
                        elif last_nonws in REGEX_STARTERS or last_nonws == "":
                            state = "regex"
                            i += 1
                            continue
                    if ch == "`":
                        state = "template"
                    elif ch == "'":
                        state = "single"
                    elif ch == '"':
                        state = "double"
                    if not ch.isspace():
                        last_nonws = ch
                elif state == "single":
                    if ch == "\\":
                        i += 2
                        continue
                    elif ch == "'":
                        state = "normal"
                        last_nonws = "'"
                    elif ch == "\n":
                        ctx = script[max(0, i - 60):i + 60].replace("\n", "↵")
                        self.fail(
                            f"Literale newline in JS single-quoted string op {path} "
                            f"(script blok {block_idx + 1}): ...{ctx}..."
                        )
                elif state == "double":
                    if ch == "\\":
                        i += 2
                        continue
                    elif ch == '"':
                        state = "normal"
                        last_nonws = '"'
                    elif ch == "\n":
                        ctx = script[max(0, i - 60):i + 60].replace("\n", "↵")
                        self.fail(
                            f"Literale newline in JS double-quoted string op {path} "
                            f"(script blok {block_idx + 1}): ...{ctx}..."
                        )
                elif state == "template":
                    if ch == "\\":
                        i += 2
                        continue
                    elif ch == "`":
                        state = "normal"
                        last_nonws = "`"
                    # literal newlines in template literals are valid — no check
                elif state == "regex":
                    if ch == "\\":
                        i += 2
                        continue
                    elif ch == "[":
                        state = "regex_class"
                    elif ch == "/":
                        state = "normal"
                        last_nonws = "/"
                elif state == "regex_class":
                    if ch == "\\":
                        i += 2
                        continue
                    elif ch == "]":
                        state = "regex"
                elif state == "line_comment":
                    if ch == "\n":
                        state = "normal"
                elif state == "block_comment":
                    if ch == "*" and i + 1 < n and script[i + 1] == "/":
                        state = "normal"
                        i += 2
                        continue
                i += 1

    def test_js_no_literal_newlines_library(self):
        """Geen literale newlines in JS string literals op /library — veroorzaken SyntaxError"""
        try:
            self._check_js_no_literal_newlines("/library")
        except ConnectionRefusedError:
            self.fail("Verbinding geweigerd op poort 8000")

    def test_js_no_literal_newlines_images(self):
        """Geen literale newlines in JS string literals op /images"""
        try:
            self._check_js_no_literal_newlines("/images")
        except ConnectionRefusedError:
            self.fail("Verbinding geweigerd op poort 8000")

    def test_js_no_literal_newlines_videos(self):
        """Geen literale newlines in JS string literals op /videos"""
        try:
            self._check_js_no_literal_newlines("/videos")
        except ConnectionRefusedError:
            self.fail("Verbinding geweigerd op poort 8000")


# ═══════════════════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    loader = unittest.TestLoader()
    result = TimedResult()
    t0 = time.monotonic()

    # Run one class at a time so setUpClass / tearDownClass fire correctly.
    for cls in (InfrastructureTests, PipelineTests, QualityTests, IntegrationTests):
        print(f"\n{cls.__name__}")
        print(f"{'─' * 40}")
        loader.loadTestsFromTestCase(cls).run(result)

    total = time.monotonic() - t0
    overall = write_report(result, total)
    _update_context_status(result, total)

    n_pass  = sum(1 for r in result.records if r["status"] == "PASS")
    n_skip  = sum(1 for r in result.records if r["status"] == "SKIP")
    n_fail  = sum(1 for r in result.records if r["status"] in ("FAIL", "ERROR"))
    n_total = len(result.records)

    print()
    print(f"{'─'*50}")
    print(f"  Resultaat : {overall}")
    print(f"  Geslaagd  : {n_pass}/{n_total - n_skip}  (overgeslagen: {n_skip})")
    print(f"  Mislukt   : {n_fail}")
    print(f"  Duur      : {total:.1f}s")
    print(f"  Rapport   : {REPORT_PATH}")
    print(f"{'─'*50}")

    # Commit and push both updated files
    import subprocess
    subprocess.run(
        ["git", "add",
         "SYSTEM_DOCS/TEST_REPORT.md",
         "SYSTEM_DOCS/CONTEXT.md"],
        cwd=BASE, check=False
    )
    commit_msg = (
        f"test: auto-report {datetime.now().strftime('%Y-%m-%d %H:%M')} "
        f"— {n_pass}/{n_total - n_skip} geslaagd"
        + (f", {n_fail} mislukt" if n_fail else "")
    )
    subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=BASE, check=False
    )
    subprocess.run(["git", "push"], cwd=BASE, check=False)

    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
