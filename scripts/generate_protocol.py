"""
Protocol Generator — NRT-Amsterdam.nl
Generates behandelprotocollen sectie voor sectie.
Output: Word .docx via Node.js docx library.
"""

import json
import logging
import os
import re
import subprocess
import requests
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))
from ai_client import AIClient

_ai = AIClient()

log = logging.getLogger(__name__)

BASE           = Path("/root/medical-rag")
QDRANT_URL     = "http://localhost:6333"
OLLAMA_URL     = "http://localhost:11434"
OLLAMA_MODEL   = "llama3.1:8b"
COLLECTION     = "medical_library"
POINT_INDEX    = BASE / "data/acupuncture_points/point_index.json"
CLASSIFICATIONS = BASE / "config/book_classifications.json"
PROTOCOL_DIR   = BASE / "data/protocols"
NRT_PROTOCOL   = BASE / "config/ai_instructions/nrt_standaard_protocol_v3.md"
NODE_PATH_ENV  = "/usr/lib/node_modules"

# QAT Balance points — verified April 2026
QAT_BALANCE = {
    "CV":  ("SP-21", "SP-21 rechts"),
    "GV":  ("SP-21", "SP-21 links"),
    "BL":  ("BL-58", "BL-58"),
    "SJ":  ("SJ-5",  "SJ-5"),
    "KID": ("KID-4", "KID-4"),
    "P":   ("P-6",   "P-6"),
    "GB":  ("GB-37", "GB-37"),
    "ST":  ("ST-40", "ST-40"),
    "LI":  ("LI-6",  "LI-6"),
    "SI":  ("SI-7",  "SI-7"),
    "LU":  ("LU-7",  "LU-7"),
    "SP":  ("SP-4",  "SP-4"),
    "HE":  ("HE-5",  "HE-5"),
    "LIV": ("LIV-5", "LIV-5"),
}

MERIDIAN_NAMES = {
    "LU":  "Long - Lung - Shou Taiyin",
    "LI":  "Dikke Darm - Large Intestine - Shou Yangming",
    "ST":  "Maag - Stomach - Zu Yangming",
    "SP":  "Milt - Spleen - Zu Taiyin",
    "HE":  "Hart - Heart - Shou Shaoyin",
    "SI":  "Dunne Darm - Small Intestine - Shou Taiyang",
    "BL":  "Blaas - Bladder - Zu Taiyang",
    "KID": "Nier - Kidney - Zu Shaoyin",
    "P":   "Pericardium - Shou Jueyin",
    "SJ":  "Drie Verwarmer - Sanjiao - Shou Shaoyang",
    "GB":  "Galblaas - Gall Bladder - Zu Shaoyang",
    "LIV": "Lever - Liver - Zu Jueyin",
    "GV":  "Governing Vessel - Du Mai",
    "CV":  "Conception Vessel - Ren Mai",
}

FULL_REFERENCES = {
    "Deadman":      "Deadman, P., Al-Khafaji, M. & Baker, K. (2007). A Manual of Acupuncture. Journal of Chinese Medicine Publications.",
    "Guyton":       "Hall, J.E. (2011). Guyton and Hall Textbook of Medical Physiology (12th ed.). Saunders Elsevier.",
    "Sobotta":      "Paulsen, F. & Waschke, J. (2019). Sobotta Atlas of Human Anatomy (16th ed.). Elsevier.",
    "Travell":      "Travell, J.G. & Simons, D.G. (1999). Myofascial Pain and Dysfunction: The Trigger Point Manual. Williams & Wilkins.",
    "Cecil-Sterman": "Cecil-Sterman, A. (2012). Advanced Acupuncture: A Clinic Manual. Journal of Chinese Medicine Publications.",
    "Maciocia":     "Maciocia, G. (2015). The Foundations of Chinese Medicine (3rd ed.). Churchill Livingstone.",
    "AnatomyTrains": "Myers, T.W. (2014). Anatomy Trains (3rd ed.). Churchill Livingstone.",
    "Patten":       "Patten, J. (1996). Neurological Differential Diagnosis (2nd ed.). Springer.",
    "Magee":        "Magee, D.J. & Manske, R.C. (2020). Orthopedic Physical Assessment (7th ed.). Saunders.",
    "TrailGuide":   "Biel, A. (2019). Trail Guide to the Body (6th ed.). Books of Discovery.",
}


# ─── RAG + LLM HELPERS ───────────────────────────────────────────────────────

def _get_embedding(text: str) -> list[float]:
    """
    Embed text using BAAI/bge-large-en-v1.5 via SentenceTransformers.
    This is the same model used by book_ingest_queue.py for ingest.
    Falls back to empty list on failure.
    """
    try:
        from sentence_transformers import SentenceTransformer
        # Cache model at module level to avoid reloading for each call
        global _EMBED_MODEL
        if _EMBED_MODEL is None:
            log.info("Loading BAAI/bge-large-en-v1.5 embedding model...")
            _EMBED_MODEL = SentenceTransformer("BAAI/bge-large-en-v1.5")
        return _EMBED_MODEL.encode(text).tolist()
    except Exception as e:
        log.warning("Embedding failed: %s", e)
        return []

_EMBED_MODEL = None  # module-level cache


def qdrant_search(query: str, kai_filter: dict, limit: int = 8) -> list:
    """RAG search with K/A/I filtering. Falls back to empty list on any error."""
    try:
        embedding = _get_embedding(query)
        if not embedding:
            log.warning("Empty embedding — skipping RAG for this query")
            return []

        must_conditions = [
            {"key": k, "match": {"value": v}} for k, v in kai_filter.items()
        ]

        payload: dict = {
            "vector": embedding,
            "limit":  limit,
            "with_payload": True,
        }
        if must_conditions:
            payload["filter"] = {"must": must_conditions}

        resp = requests.post(
            f"{QDRANT_URL}/collections/{COLLECTION}/points/search",
            json=payload,
            timeout=30,
        )
        results = resp.json().get("result", [])
        return [r["payload"] for r in results if r.get("score", 0) > 0.3]

    except Exception as e:
        log.warning("Qdrant search failed (continuing without RAG): %s", e)
        return []


def ollama_generate(prompt: str, system: str = None, max_tokens: int = 1500) -> str:
    """Generate text via AIClient (protocol_generation use case). Returns empty string on failure."""
    try:
        return _ai.generate("protocol_generation", prompt, system=system, max_tokens=max_tokens)
    except Exception as e:
        log.warning("AI generation failed: %s", e)
        return ""


def get_point_image(point_code: str) -> str:
    """Get Deadman image path for a point code. Returns '' if not found."""
    if not point_code or not POINT_INDEX.exists():
        return ""
    try:
        sys.path.insert(0, str(BASE / "scripts"))
        from normalize_points import normalize_point as _np
        normalized = _np(point_code)
        if normalized is None:
            return ""
        index = json.loads(POINT_INDEX.read_text())
        entry = index.get(normalized)
        if entry:
            full_path = BASE / "data/acupuncture_points" / entry["file"]
            return str(full_path) if full_path.exists() else ""
    except Exception as e:
        log.debug("get_point_image(%s): %s", point_code, e)
    return ""


def load_nrt_protocol() -> str:
    if NRT_PROTOCOL.exists():
        return NRT_PROTOCOL.read_text(encoding="utf-8")
    return ""


# ─── SECTION GENERATORS ──────────────────────────────────────────────────────

def generate_klachtbeeld(klacht: str, chunks_k: list, chunks_a: list) -> dict:
    """Section 1: Klachtbeeld. Returns {klinisch, tcm}."""
    nrt_context = load_nrt_protocol()

    klinisch_prompt = (
        f"Je bent een medisch schrijver voor NRT-Amsterdam.nl.\n"
        f"Schrijf een klinisch perspectief op '{klacht}' in het Nederlands.\n"
        f"Schrijf begrijpelijk voor een therapeut — niet te technisch, niet te simpel.\n"
        f"Maximaal 200 woorden. Geen opsommingslijsten — lopende tekst.\n"
        f"Basis op deze literatuur:\n\n"
        + "\n".join(c.get("text", "")[:400] for c in chunks_k[:4])
        + f"\n\nNRT behandelcontext:\n{nrt_context[:500]}\n\nSchrijf alleen de tekst, geen titel of inleiding."
    )

    tcm_prompt = (
        f"Je bent een TCM specialist die schrijft voor NRT-Amsterdam.nl therapeuten.\n"
        f"Schrijf een TCM perspectief op '{klacht}' in het Nederlands.\n"
        f"Vertaal TCM terminologie naar begrijpelijke taal. Maximaal 150 woorden.\n"
        f"Basis op deze literatuur:\n\n"
        + "\n".join(c.get("text", "")[:400] for c in chunks_a[:3])
        + "\n\nSchrijf alleen de tekst, geen titel."
    )

    return {
        "klinisch": ollama_generate(klinisch_prompt) or f"Klinisch overzicht {klacht} — wordt gegenereerd met literatuurdata.",
        "tcm":      ollama_generate(tcm_prompt) or f"TCM perspectief {klacht}.",
    }


def _parse_json_list(response: str, fallback: list) -> list:
    """Extract a JSON list from an Ollama response, with fallback."""
    if not response:
        return fallback
    try:
        match = re.search(r"\[.*\]", response, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(response)
    except Exception:
        return fallback


def generate_weefsel_tabel(klacht: str, chunks: list, tabel_type: str) -> list:
    """Sections 2 oorzaken/gevolgen. Returns list of row dicts."""
    prompt = (
        f"Analyseer de {tabel_type} van '{klacht}' vanuit weefsel-perspectief.\n"
        f"Geef exact 4-6 rijen in JSON array formaat. Elk item:\n"
        f'{{"gebied": "Anatomisch gebied", "weefsels": "Specifieke weefsels en structuren", '
        f'"rationale": "Pathofysiologische verklaring (2-3 zinnen)"}}\n\n'
        f"Basis op literatuur:\n"
        + "\n".join(c.get("text", "")[:300] for c in chunks[:5])
        + "\n\nReturn ALLEEN de JSON array, geen andere tekst."
    )

    rows = _parse_json_list(
        ollama_generate(prompt),
        [{"gebied": klacht, "weefsels": "Zie literatuur", "rationale": ""}],
    )
    for row in rows:
        row["image_candidates"] = find_image_candidates(row.get("gebied", ""))
    return rows


def find_image_candidates(gebied: str, max_results: int = 5) -> list:
    """Find candidate images for a tissue area."""
    images_dir = BASE / "data/extracted_images"
    if not images_dir.exists():
        return []
    candidates = []
    keywords = [kw for kw in gebied.lower().split() if len(kw) > 3]

    for img_file in list(images_dir.glob("**/*.png"))[:500]:  # cap scan
        filename_lower = img_file.name.lower()
        score = (
            sum(1 for kw in keywords if kw in filename_lower) / max(len(keywords), 1)
            if keywords else 0.0
        )
        if score > 0 or len(candidates) < 3:
            candidates.append({
                "path":        str(img_file),
                "filename":    img_file.name,
                "source":      img_file.parent.name,
                "ai_score":    round(score, 2),
                "description": f"Afbeelding uit {img_file.parent.name}",
            })

    candidates.sort(key=lambda x: x["ai_score"], reverse=True)
    return candidates[:max_results]


def generate_acupunctuur_protocol(klacht: str, chunks_a: list) -> dict:
    """Section 3: Basisprotocol + aanvullende protocollen."""

    # ── basis punten ──
    basis_prompt = (
        f"Je bent een TCM acupuncturist voor NRT-Amsterdam.nl.\n"
        f"Selecteer 4-7 acupunctuurpunten voor '{klacht}' basisprotocol.\n"
        f"Gebruik Deadman notatie: ST-36, SP-10, BL-40 etc.\n"
        f'Return JSON array:\n'
        f'[{{"punt": "ST-36", "naam": "Zusanli", "meridiaan": "ST", '
        f'"meridiaan_naam": "Maag - Stomach - Zu Yangming", '
        f'"doel": "Beschrijving doel (1-2 zinnen) in het Nederlands", '
        f'"bron": "Deadman", "pagina": "158", '
        f'"rationale": "Citaat of rationale uit Deadman"}}]\n\n'
        f"Literatuur:\n"
        + "\n".join(c.get("text", "")[:400] for c in chunks_a[:5])
        + "\n\nReturn ALLEEN de JSON array."
    )

    basis_punten = _parse_json_list(ollama_generate(basis_prompt, max_tokens=2000), [])

    for punt in basis_punten:
        punt["image_path"] = get_point_image(punt.get("punt", ""))
        # Fill in meridian name if model omitted it
        if not punt.get("meridiaan_naam") and punt.get("meridiaan"):
            punt["meridiaan_naam"] = MERIDIAN_NAMES.get(punt["meridiaan"], punt["meridiaan"])

    # ── aanvullende protocollen ──
    aanvullend_prompt = (
        f"Voor '{klacht}' protocol, welke TCM patronen vereisen aanvullende behandeling?\n"
        f"Geef 2-3 aanvullende protocollen. Return JSON:\n"
        f'[{{"naam": "3.1  Aanvullend - Lever Wind / Yang Rising", '
        f'"wanneer": "Wanneer toepassen: beschrijving (1-2 zinnen)", '
        f'"punten": [{{"punt": "LIV-3", "naam": "Taichong", "meridiaan": "LIV", '
        f'"meridiaan_naam": "Lever - Liver - Zu Jueyin", '
        f'"doel": "Doel in het Nederlands", '
        f'"bron": "Deadman", "pagina": "480", "rationale": "Rationale"}}]}}]\n\n'
        f"Literatuur:\n"
        + "\n".join(c.get("text", "")[:300] for c in chunks_a[:4])
        + "\n\nReturn ALLEEN de JSON array."
    )

    aanvullende = _parse_json_list(ollama_generate(aanvullend_prompt, max_tokens=2500), [])

    for protocol in aanvullende:
        for punt in protocol.get("punten", []):
            punt["image_path"] = get_point_image(punt.get("punt", ""))
            if not punt.get("meridiaan_naam") and punt.get("meridiaan"):
                punt["meridiaan_naam"] = MERIDIAN_NAMES.get(punt["meridiaan"], punt["meridiaan"])

    # ── QAT meridiaan balancering ──
    all_meridians: set[str] = set()
    for punt in basis_punten:
        if m := punt.get("meridiaan"):
            all_meridians.add(m)
    for protocol in aanvullende:
        for punt in protocol.get("punten", []):
            if m := punt.get("meridiaan"):
                all_meridians.add(m)

    balancering = []
    for meridian in sorted(all_meridians):
        if meridian in QAT_BALANCE:
            bal_code, bal_label = QAT_BALANCE[meridian]
            balancering.append({
                "punt":          bal_code,
                "naam":          bal_label,
                "meridiaan":     meridian,
                "meridiaan_naam": MERIDIAN_NAMES.get(meridian, meridian),
                "doel":          f"Balancepunt {MERIDIAN_NAMES.get(meridian, meridian)}",
                "image_path":    get_point_image(bal_code),
            })

    focus_text = ollama_generate(
        f"Beschrijf in 1-2 zinnen de klinische TCM focus voor '{klacht}' acupunctuur:",
        max_tokens=200,
    )

    return {
        "focus_text":  focus_text or f"TCM focus: {klacht}.",
        "basis_punten": basis_punten,
        "aanvullende":  aanvullende,
        "balancering":  balancering,
        "meridianen":   list(sorted(all_meridians)),
    }


def generate_literatuurlijst(acupunctuur: dict) -> dict:
    """Section 4: collect citations from generated content."""
    bronnen: dict[str, list] = {}
    for punt in acupunctuur.get("basis_punten", []):
        bron   = punt.get("bron", "Deadman")
        pagina = punt.get("pagina", "")
        bronnen.setdefault(bron, [])
        if pagina:
            bronnen[bron].append(pagina)
    for protocol in acupunctuur.get("aanvullende", []):
        for punt in protocol.get("punten", []):
            bron   = punt.get("bron", "Deadman")
            pagina = punt.get("pagina", "")
            bronnen.setdefault(bron, [])
            if pagina:
                bronnen[bron].append(pagina)

    literatuurlijst = [
        {
            "afkorting": afk,
            "referentie": FULL_REFERENCES.get(afk, f"{afk} — zie bibliotheek"),
        }
        for afk in bronnen
    ]
    return {"literatuurlijst": literatuurlijst}


# ─── WORD DOCUMENT GENERATOR ─────────────────────────────────────────────────

def _escape_js(text: str) -> str:
    """Escape text for safe embedding in a JS template literal."""
    if not text:
        return ""
    return (
        text
        .replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("${", "\\${")
        .replace("\n", " ")
        .replace("\r", "")
        .replace('"', '\\"')
    )


def _weefsel_rows_js(rows: list) -> str:
    parts = []
    for row in rows:
        gebied   = _escape_js(row.get("gebied", ""))
        weefsels = _escape_js(row.get("weefsels", ""))
        rat      = _escape_js(row.get("rationale", ""))
        parts.append(
            f'new TableRow({{children: ['
            f'cell("{gebied}", "E8F4F8", 1500),'
            f'cell("{weefsels}", "FFFFFF", 1900),'
            f'cell("{rat}", "FFFFFF", 5906),'
            f']}}),\n'
        )
    return "".join(parts)


def _punt_rows_js(punten: list) -> str:
    parts = []
    for punt in punten:
        code    = _escape_js(punt.get("punt", ""))
        naam    = _escape_js(punt.get("naam", ""))
        mer     = _escape_js(punt.get("meridiaan_naam") or punt.get("meridiaan", ""))
        doel    = _escape_js(punt.get("doel", ""))
        img     = _escape_js(punt.get("image_path", "") or "")
        parts.append(
            f'new TableRow({{children: ['
            f'cell("{code}  {naam}", "FFFFFF", 1500),'
            f'cell("{mer}", "FFFFFF", 1900),'
            f'cell("{doel}", "FFFFFF", 4706),'
            f'cellImg("{img}", 2200),'
            f']}}),\n'
        )
    return "".join(parts)


def _build_docx_js(data: dict, output_path: str) -> str:
    klacht  = data["klacht"]
    version = data.get("version", "1.0")
    datum   = datetime.now().strftime("%B %Y")

    aanvullende     = data.get("aanvullende", [])
    n_aanvullende   = len(aanvullende)

    # Build aanvullende sections JS
    aanvullende_js_parts = []
    for i, aanv in enumerate(aanvullende, 1):
        naam      = _escape_js(aanv.get("naam", f"3.{i}  Aanvullend"))
        wanneer   = _escape_js(aanv.get("wanneer", ""))
        punten_js = _punt_rows_js(aanv.get("punten", []))
        aanvullende_js_parts.append(f"""
    // Aanvullend {i}
    sectionHeader("{naam}", "FCE4D6"),
    textBlock("{wanneer}", "FFF2CC"),
    new Table({{
        width: {{size: 10306, type: WidthType.DXA}},
        columnWidths: [1500, 1900, 4706, 2200],
        rows: [
            headerRow(["Punt", "Meridiaan", "Doel", "Afbeelding punt"]),
            {punten_js}
        ]
    }}),""")
    aanvullende_js = "\n".join(aanvullende_js_parts)

    # Lit rows
    lit_rows_parts = []
    for item in data.get("literatuurlijst", {}).get("literatuurlijst", []):
        afk = _escape_js(item.get("afkorting", ""))
        ref = _escape_js(item.get("referentie", ""))
        lit_rows_parts.append(
            f'new TableRow({{children: ['
            f'cell("{afk}", "E8F4F8", 1500),'
            f'cell("{ref}", "FFFFFF", 8806),'
            f']}}),\n'
        )
    lit_rows_js = "".join(lit_rows_parts)

    oorzaken_js  = _weefsel_rows_js(data.get("oorzaken", []))
    gevolgen_js  = _weefsel_rows_js(data.get("gevolgen", []))
    basis_js     = _punt_rows_js(data.get("acupunctuur", {}).get("basis_punten", []))
    balancer_js  = _punt_rows_js(data.get("acupunctuur", {}).get("balancering", []))
    focus_text   = _escape_js(data.get("acupunctuur", {}).get("focus_text", ""))
    klinisch     = _escape_js(data.get("klinisch", ""))
    klacht_esc   = _escape_js(klacht)
    output_esc   = output_path.replace("\\", "\\\\").replace("'", "\\'")
    bal_section  = n_aanvullende + 1

    return f"""
const {{ Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        AlignmentType, WidthType, ShadingType, BorderStyle, ImageRun }} = require('docx');
const fs = require('fs');
const path = require('path');

function cell(text, fillColor, width) {{
    return new TableCell({{
        width: {{size: width, type: WidthType.DXA}},
        shading: {{fill: fillColor || "FFFFFF", type: ShadingType.CLEAR}},
        margins: {{top: 80, bottom: 80, left: 120, right: 120}},
        borders: {{
            top:    {{style: BorderStyle.SINGLE, size: 1, color: "CCCCCC"}},
            bottom: {{style: BorderStyle.SINGLE, size: 1, color: "CCCCCC"}},
            left:   {{style: BorderStyle.SINGLE, size: 1, color: "CCCCCC"}},
            right:  {{style: BorderStyle.SINGLE, size: 1, color: "CCCCCC"}},
        }},
        children: [new Paragraph({{
            children: [new TextRun({{text: text || "", size: 20, font: "Calibri"}})]
        }})]
    }});
}}

function cellImg(imgPath, width) {{
    if (!imgPath || !fs.existsSync(imgPath)) {{
        return cell("", "FFFFFF", width);
    }}
    try {{
        const imgData = fs.readFileSync(imgPath);
        const ext = path.extname(imgPath).slice(1).toLowerCase();
        return new TableCell({{
            width: {{size: width, type: WidthType.DXA}},
            margins: {{top: 40, bottom: 40, left: 80, right: 80}},
            children: [new Paragraph({{
                children: [new ImageRun({{
                    data: imgData,
                    transformation: {{width: 90, height: 120}},
                    type: ext === "png" ? "png" : "jpg"
                }})]
            }})]
        }});
    }} catch(e) {{
        return cell("", "FFFFFF", width);
    }}
}}

function headerRow(labels) {{
    const widths = [1500, 1900, 4706, 2200];
    return new TableRow({{
        children: labels.map((lbl, i) => new TableCell({{
            width: {{size: widths[i] || 2000, type: WidthType.DXA}},
            shading: {{fill: "1A6B72", type: ShadingType.CLEAR}},
            margins: {{top: 80, bottom: 80, left: 120, right: 120}},
            children: [new Paragraph({{
                children: [new TextRun({{
                    text: lbl, bold: true, color: "FFFFFF", size: 20, font: "Calibri"
                }})]
            }})]
        }}))
    }});
}}

function sectionHeader(text, bgColor) {{
    const isMain = !bgColor || bgColor === "1A6B72";
    const fill   = bgColor || "1A6B72";
    return new Table({{
        width: {{size: 10306, type: WidthType.DXA}},
        columnWidths: [10306],
        rows: [new TableRow({{children: [
            new TableCell({{
                width: {{size: 10306, type: WidthType.DXA}},
                shading: {{fill: fill, type: ShadingType.CLEAR}},
                margins: {{top: 120, bottom: 120, left: 160, right: 160}},
                children: [new Paragraph({{
                    children: [new TextRun({{
                        text: text,
                        bold: true,
                        color: isMain ? "FFFFFF" : "1A1A1A",
                        size: isMain ? 24 : 22,
                        font: "Calibri"
                    }})]
                }})]
            }})
        ]}})],
    }});
}}

function textBlock(text, bgColor) {{
    return new Table({{
        width: {{size: 10306, type: WidthType.DXA}},
        columnWidths: [10306],
        rows: [new TableRow({{children: [
            new TableCell({{
                width: {{size: 10306, type: WidthType.DXA}},
                shading: {{fill: bgColor || "FFFFFF", type: ShadingType.CLEAR}},
                margins: {{top: 100, bottom: 100, left: 160, right: 160}},
                children: [new Paragraph({{
                    children: [new TextRun({{text: text || "", size: 20, font: "Calibri"}})]
                }})]
            }})
        ]}})],
    }});
}}

const doc = new Document({{
    styles: {{
        default: {{ document: {{ run: {{ font: "Calibri", size: 20 }} }} }}
    }},
    sections: [{{
        properties: {{
            page: {{
                size:   {{width: 11906, height: 16838}},
                margin: {{top: 720, right: 720, bottom: 720, left: 720}}
            }}
        }},
        children: [
            // ── HEADER ──
            new Table({{
                width: {{size: 10306, type: WidthType.DXA}},
                columnWidths: [10306],
                rows: [new TableRow({{children: [
                    new TableCell({{
                        width: {{size: 10306, type: WidthType.DXA}},
                        shading: {{fill: "1A6B72", type: ShadingType.CLEAR}},
                        margins: {{top: 200, bottom: 200, left: 200, right: 200}},
                        children: [
                            new Paragraph({{
                                alignment: AlignmentType.CENTER,
                                children: [new TextRun({{
                                    text: "Behandelprotocol {klacht_esc}",
                                    bold: true, color: "FFFFFF", size: 32, font: "Calibri"
                                }})]
                            }}),
                            new Paragraph({{
                                alignment: AlignmentType.CENTER,
                                children: [new TextRun({{
                                    text: "Versie {version} — {datum} — NRT-Amsterdam.nl",
                                    color: "FFFFFF", size: 18, font: "Calibri"
                                }})]
                            }})
                        ]
                    }})
                ]}})],
            }}),
            new Paragraph({{children: []}}),

            // ── 1. KLACHTBEELD ──
            sectionHeader("1.  Klachtbeeld"),
            textBlock("{klinisch}", "FFFFFF"),
            new Paragraph({{children: []}}),

            // ── 2. QAT WEEFSEL ──
            sectionHeader("2.  QAT - TNT, CTB, ETT, Inflammation en Balancing", "FCE4D6"),
            textBlock("Basis: Volg altijd het standaard NRT-Behandelprotocol van voeten naar hoofd.", "FFF2CC"),
            new Paragraph({{spacing: {{before: 120}}}}),

            new Paragraph({{children: [new TextRun({{text: "Oorzaak", bold: true, size: 22}})], spacing: {{before: 120}}}}),
            new Table({{
                width: {{size: 10306, type: WidthType.DXA}},
                columnWidths: [1500, 1900, 5906],
                rows: [
                    new TableRow({{children: [
                        cell("Gebied", "1A6B72", 1500),
                        cell("Weefsels en structuren", "1A6B72", 1900),
                        cell("Rationale", "1A6B72", 5906),
                    ]}}),
                    {oorzaken_js}
                ]
            }}),

            new Paragraph({{children: [new TextRun({{text: "Mogelijke gevolgen", bold: true, size: 22}})], spacing: {{before: 160}}}}),
            new Table({{
                width: {{size: 10306, type: WidthType.DXA}},
                columnWidths: [1500, 1900, 5906],
                rows: [
                    new TableRow({{children: [
                        cell("Gebied", "1A6B72", 1500),
                        cell("Weefsels en structuren", "1A6B72", 1900),
                        cell("Rationale", "1A6B72", 5906),
                    ]}}),
                    {gevolgen_js}
                ]
            }}),
            new Paragraph({{children: []}}),

            // ── 3. ACUPUNCTUUR BASISPROTOCOL ──
            sectionHeader("3.  QAT Acupunctuur - Basisprotocol"),
            textBlock("{focus_text}", "FFFFFF"),
            new Table({{
                width: {{size: 10306, type: WidthType.DXA}},
                columnWidths: [1500, 1900, 4706, 2200],
                rows: [
                    headerRow(["Punt", "Meridiaan", "Doel", "Afbeelding punt"]),
                    {basis_js}
                ]
            }}),

            {aanvullende_js}

            // ── MERIDIAAN BALANCERING ──
            sectionHeader("3.{bal_section}  QAT Meridiaan Balancering", "FCE4D6"),
            new Table({{
                width: {{size: 10306, type: WidthType.DXA}},
                columnWidths: [1500, 1900, 4706, 2200],
                rows: [
                    headerRow(["Punt", "Meridiaan", "Doel", "Afbeelding punt"]),
                    {balancer_js}
                ]
            }}),
            new Paragraph({{children: []}}),

            // ── 4. LITERATUURLIJST ──
            sectionHeader("4.  Redenatie en literatuurreferentie"),
            new Paragraph({{children: [
                new TextRun({{text: "4.7  Literatuurlijst", bold: true, size: 22}})
            ], spacing: {{before: 160}}}}),
            new Table({{
                width: {{size: 10306, type: WidthType.DXA}},
                columnWidths: [1500, 8806],
                rows: [
                    new TableRow({{children: [
                        cell("Afkorting", "1A6B72", 1500),
                        cell("Volledige referentie", "1A6B72", 8806),
                    ]}}),
                    {lit_rows_js}
                ]
            }}),
        ]
    }}]
}});

Packer.toBuffer(doc).then(buffer => {{
    fs.writeFileSync('{output_esc}', buffer);
    console.log('Generated: {output_esc}');
}}).catch(err => {{
    console.error('Error:', err.message);
    process.exit(1);
}});
"""


def generate_word_document(protocol_data: dict, output_path: str) -> str:
    """Generate Word document via Node.js docx library."""
    js_code = _build_docx_js(protocol_data, output_path)
    script_path = Path("/tmp/generate_protocol_tmp.js")
    script_path.write_text(js_code, encoding="utf-8")

    env = {**os.environ, "NODE_PATH": NODE_PATH_ENV}
    result = subprocess.run(
        ["node", str(script_path)],
        capture_output=True, text=True, timeout=120, env=env,
    )
    if result.returncode != 0:
        log.error("Node.js stderr: %s", result.stderr[:1000])
        raise RuntimeError(f"Word generation failed: {result.stderr[:300]}")
    log.info("Word document generated: %s", output_path)
    return output_path


# ─── MAIN ORCHESTRATOR ───────────────────────────────────────────────────────

def generate_protocol(
    klacht: str,
    progress_fn=None,
) -> str:
    """
    Generate a complete protocol Word document for the given klacht.
    progress_fn(section, percent) is called at each milestone if provided.
    Returns path to generated .docx file.
    """

    def _progress(section: str, pct: int) -> None:
        log.info("[%d%%] %s", pct, section)
        if progress_fn:
            try:
                progress_fn(section, pct)
            except Exception:
                pass

    _progress("Bezig met opstarten…", 0)

    protocol_id_base = re.sub(r"[^a-z0-9]", "_", klacht.lower())[:40]
    timestamp        = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name        = re.sub(r"[^A-Za-z0-9_\- ]", "", klacht).strip().replace(" ", "-")
    output_path      = str(PROTOCOL_DIR / f"Behandelprotocol-{safe_name}-v1.docx")
    PROTOCOL_DIR.mkdir(parents=True, exist_ok=True)

    # ── Step 1: RAG queries ──
    _progress("RAG queries uitvoeren…", 5)
    chunks_k = qdrant_search(
        f"{klacht} anatomie weefsels pathologie oorzaak",
        {"kai_k": 1}, limit=8,
    )
    chunks_a = qdrant_search(
        f"{klacht} acupunctuur punten TCM behandeling",
        {"kai_a": 1}, limit=8,
    )
    log.info("RAG: %d clinical chunks, %d acupuncture chunks", len(chunks_k), len(chunks_a))

    # ── Step 2: Generate sections ──
    _progress("Klachtbeeld genereren…", 15)
    klachtbeeld = generate_klachtbeeld(klacht, chunks_k, chunks_a)

    _progress("Oorzaken tabel genereren…", 30)
    oorzaken = generate_weefsel_tabel(klacht, chunks_k, "oorzaken")

    _progress("Gevolgen tabel genereren…", 45)
    gevolgen = generate_weefsel_tabel(klacht, chunks_k, "mogelijke gevolgen")

    _progress("Acupunctuur protocol genereren…", 60)
    acupunctuur = generate_acupunctuur_protocol(klacht, chunks_a)

    _progress("Literatuurlijst samenstellen…", 80)
    literatuur = generate_literatuurlijst(acupunctuur)

    # ── Step 3: Assemble ──
    protocol_data = {
        "klacht":         klacht,
        "version":        "1.0",
        "klinisch":       klachtbeeld["klinisch"],
        "tcm":            klachtbeeld["tcm"],
        "oorzaken":       oorzaken,
        "gevolgen":       gevolgen,
        "acupunctuur":    acupunctuur,
        "aanvullende":    acupunctuur.get("aanvullende", []),
        "literatuurlijst": literatuur,
    }

    # ── Step 4: Word document ──
    _progress("Word document aanmaken…", 88)
    generate_word_document(protocol_data, output_path)

    # ── Step 5: Metadata ──
    _progress("Metadata opslaan…", 95)
    sys.path.insert(0, str(BASE / "scripts"))
    from protocol_metadata import save_protocol_metadata

    literature_used = []
    seen: set[str] = set()
    for chunk in chunks_k + chunks_a:
        key   = chunk.get("kai_role") or chunk.get("source_file", "unknown")
        title = chunk.get("source_file", key)
        if key not in seen:
            seen.add(key)
            literature_used.append({
                "book_key":  key,
                "title":     title,
                "chunk_ids": [],
                "pages":     [str(chunk.get("page_number", ""))] if chunk.get("page_number") else [],
                "kai_role":  chunk.get("kai_role", ""),
            })

    save_protocol_metadata(
        protocol_id=f"{protocol_id_base}_{timestamp}",
        klacht=klacht,
        literature_used=literature_used,
    )

    _progress("Klaar!", 100)
    log.info("Protocol complete: %s", output_path)
    return output_path


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
    )
    klacht = sys.argv[1] if len(sys.argv) > 1 else "Hoofdpijn"
    output = generate_protocol(klacht)
    print(f"Generated: {output}")
