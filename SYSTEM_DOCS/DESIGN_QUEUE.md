# DESIGN QUEUE — NRT-Amsterdam.nl Medical RAG
> Opgesteld: 2026-04-19 | Status: documentatie — geen wijziging
> Herstel komt later. Dit bestand legt vast welke ontwerpen bestaan en welke ontbreken.

---

## Leeswijzer

- **Status CONCEPT:** Document bestaat, is nog niet goedgekeurd voor implementatie
- **Status GOEDGEKEURD:** Concept goedgekeurd door architect — implementatie kan beginnen
- **Status IMPLEMENTATIE:** Actief in ontwikkeling
- **Status LIVE:** Geïmplementeerd in productie
- **Status ONTBREEKT:** Nog niet aangemaakt — hier staat wat het moet bevatten

---

## BESTAANDE DESIGNS (op NRT server / sterfhuis)

### DESIGN-BibliotheekRedesign-v1

- **Locatie:** NRT server (sterfhuis) — bestandsnaam: `Literatuuranalyse-BibliotheekRedesign-Design-v1.txt`
- **Status:** CONCEPT (nog niet op GitHub gemigreerd; NRT server toegankelijkheid onzeker)
- **Scope:** Data model herziening voor bibliotheek — adresseert ISSUE-010 (drie divergerende databronnen). Unificeert state.json + book_classifications.json + Qdrant payloads in één definitief datamodel.
- **Afhankelijk van:** DESIGN-Architectuur-v1 (fundament)
- **Laatste wijziging:** onbekend (document op NRT server, niet gecontroleerd)
- **Actie nodig:** Migratie van NRT server naar GitHub repo. Geblokkeerd door ISSUE-014 (Google Drive MCP niet beschikbaar).

---

### DESIGN-ImageMetadataPipeline-v1.2

- **Locatie:** NRT server (sterfhuis) — bestandsnaam: `Literatuuranalyse-ImageMetadataPipeline-Design-v1.txt` (v1.2)
- **Status:** CONCEPT (nog niet op GitHub gemigreerd)
- **Scope:** Pipeline B voor afbeeldingsmetadata — captioning, tagging, goedkeuringsflow, koppeling aan RAG.
- **Afhankelijk van:** DESIGN-Architectuur-v1; DESIGN-BibliotheekRedesign-v1
- **Laatste wijziging:** onbekend
- **Actie nodig:** Migratie van NRT server naar GitHub repo.

---

### DESIGN-Werkwijze-vLatest

- **Locatie:** NRT server (sterfhuis) — bestandsnaam: `Literatuuranalyse-Werkwijze` (nieuwste versie)
- **Status:** CONCEPT
- **Scope:** Beschrijving van de 5-stappen werkwijze voor Architect–Claude Code samenwerking
- **Afhankelijk van:** —
- **Laatste wijziging:** onbekend
- **Actie nodig:** Migratie van NRT server naar GitHub repo. Basis voor DESIGN-Governance-v1.

---

## ONTBREKENDE DESIGNS (afgesproken in Chat 3, 2026-04-19)

### DESIGN-Architectuur-v1

- **Locatie:** ONTBREEKT — nog niet aangemaakt
- **Status:** ONTBREEKT
- **Scope:**
  - Definitief datamodel voor alle entiteiten (boek, chunk, afbeelding, transcript, protocol)
  - API contract — endpoint-namen, request/response schemas
  - Fundament waarop alle andere designs steunen
  - Relatie tussen state.json, book_classifications.json, en Qdrant payloads (adresseert ISSUE-010)
- **Afhankelijk van:** niets — dit IS het fundament
- **Prioriteit:** EERST — alle andere designs wachten hierop

---

### DESIGN-Import-v1

- **Locatie:** ONTBREEKT — nog niet aangemaakt
- **Status:** ONTBREEKT
- **Scope:**
  - Drag & drop upload flow (frontend)
  - Ingest-fases beschrijving (Fase 0 ISBN, Fase 1 parse, Fase 2 audit, Fase 3 embed, Fase 4 qdrant, Fase 5 images)
  - Foutafhandeling: permanently_failed herstel, retry-logica
  - Duplicate-detectie flow
  - book_metadata-extractie: welke collecties, welke bronnen
- **Afhankelijk van:** DESIGN-Architectuur-v1
- **Prioriteit:** Hoog — direct gerelateerd aan ISSUE-005, ISSUE-006

---

### DESIGN-Afbeeldingen-v1

- **Locatie:** ONTBREEKT (Pipeline B)
- **Status:** ONTBREEKT — gedeeltelijk uitgewerkt in DESIGN-ImageMetadataPipeline-v1.2 (NRT server)
- **Scope:**
  - Extractor pipeline (Vision API, PyMuPDF, EPUB)
  - Captioning via Gemini Vision
  - Goedkeuringsflow (/images pagina)
  - Koppeling aan RAG-zoekopdrachten
- **Afhankelijk van:** DESIGN-Architectuur-v1; DESIGN-BibliotheekRedesign-v1

---

### DESIGN-Videos-v1

- **Locatie:** ONTBREEKT
- **Status:** ONTBREEKT
- **Scope:**
  - Upload flow voor video's (NRT/QAT)
  - Transcriptie pipeline (Whisper, segmentatie, part-JSON merge)
  - Ingestion naar Qdrant (ingest_transcript.py)
  - Bibliotheekweergave transcripties
  - Adresseert ISSUE-004 (merge van _partNNN.json naar definitieve JSON)
- **Afhankelijk van:** DESIGN-Architectuur-v1

---

### DESIGN-Protocollen-v1

- **Locatie:** ONTBREEKT
- **Status:** ONTBREEKT
- **Scope:**
  - Behandelprotocol generator (/protocols route)
  - RAG-query strategie per klacht
  - Appendix-triggerlogica
  - Domain MDs als context (NRT, QAT, RLT, PEMF, Klinisch)
  - Output formaat (.docx, markdown)
- **Afhankelijk van:** DESIGN-Architectuur-v1

---

### DESIGN-Nachtbatch-v1

- **Locatie:** ONTBREEKT
- **Status:** ONTBREEKT
- **Scope:**
  - nightly_maintenance.py fases (huidige 7 fases)
  - sync_status.py gedrag (wat wordt gecommit, hoe vaak)
  - sync_context.py gedrag (CONTEXT.md generatie)
  - Watchdog-logica (book-ingest-watchdog + queue-watchdog)
  - Timer configuratie (maintenance, tests, sync, watchdog)
  - Adresseert ISSUE-016 (ingest_cache niet gecommit)
- **Afhankelijk van:** DESIGN-Architectuur-v1

---

### DESIGN-API-v1

- **Locatie:** ONTBREEKT
- **Status:** ONTBREEKT
- **Scope:**
  - Volledige endpoint-documentatie (alle routes in web/app.py)
  - Request/response JSON schemas
  - Authenticatie/autorisatie (huidige: geen — Tailscale-only)
  - Foutcodes en error responses
- **Afhankelijk van:** DESIGN-Architectuur-v1

---

### DESIGN-Governance-v1

- **Locatie:** ONTBREEKT
- **Status:** ONTBREEKT
- **Scope:**
  - 5-stappen werkwijze technisch borgen (Design → Goedkeuring → Implementatie → Review → Afsluiting)
  - LESSONS_LEARNED.md structuur en update-triggers
  - Feedback loop Claude Code → Architect (adresseert ISSUE-012)
  - Drive-sync mechanisme voor design-documenten (adresseert ISSUE-014)
  - `/api/health` (quick) en `/api/status/full` (deep) endpoint specificatie
  - CLAUDE.md update-protocol (voorkomt ISSUE-001 en ISSUE-002 in de toekomst)
- **Afhankelijk van:** DESIGN-Werkwijze-vLatest (NRT server)
- **Prioriteit:** Hoog — dit fundament voorkomt structurele drift

---

## Overzicht afhankelijkheden

```
DESIGN-Werkwijze-vLatest (NRT server)
  └── DESIGN-Governance-v1 (ONTBREEKT)

DESIGN-Architectuur-v1 (ONTBREEKT) ← fundament
  ├── DESIGN-Import-v1 (ONTBREEKT)
  ├── DESIGN-BibliotheekRedesign-v1 (NRT server, migratie nodig)
  │   └── DESIGN-Afbeeldingen-v1 (ONTBREEKT)
  ├── DESIGN-Videos-v1 (ONTBREEKT)
  ├── DESIGN-Protocollen-v1 (ONTBREEKT)
  ├── DESIGN-Nachtbatch-v1 (ONTBREEKT)
  └── DESIGN-API-v1 (ONTBREEKT)
```

---

## Migratie NRT server → GitHub (open acties)

De volgende bestanden staan op de NRT server (sterfhuis) en moeten gemigreerd worden:

| Bestand | Doellocatie | Geblokkeerd door |
|---|---|---|
| Literatuuranalyse-BibliotheekRedesign-Design-v1.txt | docs/ of SYSTEM_DOCS/ | ISSUE-014 (Drive MCP) |
| Literatuuranalyse-ImageMetadataPipeline-Design-v1.txt | docs/ of SYSTEM_DOCS/ | ISSUE-014 (Drive MCP) |
| Literatuuranalyse-Werkwijze (nieuwste versie) | docs/ of SYSTEM_DOCS/ | ISSUE-014 (Drive MCP) |

**Totaal NRT server analysebestanden:** 51 (gemeld in Chat 3, 2026-04-19). Exacte lijst onbekend — Drive MCP niet beschikbaar.

**VRAAG AAN ARCHITECT:** Welke van de 51 bestanden zijn prioritair voor migratie? En wat is het tijdschema voor de NRT server (sterfhuis)?
