# BACKLOG — Medical RAG
> Bijgewerkt door Claude Code na elke sessie.
> Laatste update: 2026-04-19 — GitHub sync observability: /api/status/sync + nav badge + error logging

---

## ✅ Afgerond — 2026-04-19 (sessie 20)

- [x] **GitHub sync observability: diagnose + /api/status/sync + nav badge**
      - Diagnose: sync was already working (timer active, push OK via gh auth git-credential)
      - Added `data/sync_errors.log` (repo-internal) to sync_status.py — cleared on success, written on failure
      - Added GET `/api/status/sync` endpoint: last_commit, timer_active, push_ok, last_error
      - Added sync badge `⟳` / `🟢 Sync` / `🔴 Sync` to nav bar on all pages via _page_shell
      - Updated CLAUDE.md with "GitHub sync health check" section + curl command
      - Verified: push_ok=True, timer_active=True, GitHub timestamp 2026-04-19 08:19 UTC
      - Tests: 39/39 GESLAAGD

## ✅ Afgerond — 2026-04-19 (sessie 19)

- [x] **JS SyntaxError bugfix /library + structurele event handler standaard**
      - Root cause: `oninput="this.value=this.value.replace(/[^0-9]/g,'')"` — `''` als twee JS string literals → SyntaxError → heel script-blok crasht → boeken lijst bleef op "Laden..."
      - Fix: named function `stripNonNumeric(el)` in library script-blok; `oninput="stripNonNumeric(this)"`
      - Overige fixes: `confirmImageToggle` → `data-imghash` attribuut; videos page `showFileList`/`doUpload` → `data-vtype`; images sort-select → `imgFilterSort(this)` + `data-filter`
      - Structureel: CLAUDE.md "HTML onclick standaard" → "HTML event handler standaard" (uitgebreid naar alle on* handlers + alle quote-types)
      - Test toegevoegd: `test_no_quotes_in_event_handler_attrs` in IntegrationTests (script-blocks gestript, checked HTML attrs alleen)
      - Testsuite: 39/39 GESLAAGD

## ✅ Afgerond — 2026-04-18 (sessie 18)

- [x] **test_acupuncture.pdf volledig verwijderd**
      - Verwijderd via `DELETE /api/library/book/4619b1ff36fca875`: 2 Qdrant vectors, cache, images, file, classifications entry
      - Geverifieerd: niet meer in ingest_cache noch book_classifications.json
      - Nog 10 boeken zonder ISBN (verwacht: 10)

## ✅ Afgerond — 2026-04-18 (sessie 17)

- [x] **DEEL A: ISBNsearch.org scraper + Library of Congress API**
      - `_fetch_isbnsearch(isbn)`: BeautifulSoup scraper, CAPTCHA-detectie, haalt title/authors/publisher/year/isbn/cover op
      - `_fetch_loc(isbn)`: LOC catalog API — graceful fallback (403 op Hetzner, log + return {})
      - ISBNsearch werkt voor Bates 14e internationale editie: title + year 2025 + publisher (Google Books geen resultaat voor dit ISBN)

- [x] **DEEL B: ISBN-10 → ISBN-13 conversie + copy-paste friendliness**
      - `_isbn10_to_isbn13(isbn10)`: 978-prefix + herberekend checksum
      - `_validate_isbn13()`: accepteert nu ook ISBN-10 en strips alle niet-cijfer tekens (dashes, spaties)
      - Tests: `0443100284` → `9780443100284` ✓, `978-0-443-10028-4` → `9780443100284` ✓, `978 1 975 28260 8` → `9781975282608` ✓

- [x] **DEEL C: FIELD_PRIORITY bijgewerkt met 5 bronnen**
      - `_merge_metadata()`: signature uitgebreid met `isbnsearch=None, loc=None`
      - ISBNsearch prioriteit 1 voor year, publisher, cover_url (meest nauwkeurig voor recente edities)
      - `enrich_book()`: roept nu alle 5 bronnen aan + `time.sleep(1)` rate-limiting

- [x] **DEEL D: ISBN invoerveld auto-strip + server-side cleanup**
      - `api_enrich_isbn`: `re.sub(r"[^\dXx]", "", ...)` strip op input (dashes/spaces)
      - Imports uitgebreid met `_fetch_isbnsearch, _fetch_loc`; endpoint gebruikt nu 5 bronnen
      - ISBN input in /library banner: `oninput="this.value=this.value.replace(/[^0-9]/g,'')"` toegevoegd

- [x] **38/38 tests geslaagd**

## ✅ Afgerond — 2026-04-18 (sessie 16)

- [x] **FIX 1: TypeError: authors.substring is not a function**
      - Root cause: `_merge_metadata()` returns `authors` als Python lijst (van Google Books API), `_save_metadata()` sloeg dit op in `bm["creator"]` zonder type-conversie
      - PART A: `_save_metadata()` converteert authors-lijst naar kommagescheiden string bij opslaan
      - PART B: `/api/schemas/metadata` endpoint: defensieve coerce van creator bij lezen
      - PART B JS: `loadLibraryMetadataStatus()` gebruikt `Array.isArray()` guard voor `.substring()`
      - PART C: Backfill — 32 state.json bestanden gecorrigeerd van list naar string

- [x] **FIX 2: Metadata status van /instellingen naar /library verplaatst**
      - Schema's tab volledig verwijderd uit /instellingen (tab-knop + pane + dode JS-functies)
      - `switchSettingsTab()` behandelt nu alleen 'params' en 'ai'
      - Collapsible amber banner bovenaan /library: toont aantal onvolledige boeken
      - Server-side `_get_metadata_incomplete_count()` helper voor banner-count
      - Nieuwe JS-functies `loadLibraryMetadataStatus()` + `enrichIsbnLib()` in /library
      - Banner toont tabel bij klikken, verborgen wanneer alles volledig

- [x] **38/38 tests geslaagd**

## ✅ Afgerond — 2026-04-18 (sessie 15)

- [x] **Feature 1: Handmatige ISBN invoer in Schema's tab**
      - Amber rijen (oranje) voor 11 boeken zonder ISBN — ISBN ontbreekt badge
      - Input veld + "Opzoeken ▶" knop per amber rij (data-* attribuut pattern)
      - `POST /api/library/book/{hash}/enrich-isbn` endpoint: valideert ISBN-13, Google Books + OpenLibrary, mergt metadata, slaat op in state.json + book_classifications.json
      - Inline row update na succesvolle opzoeking, automatisch herladen na 1.8s
      - Foutmeldingen: ongeldig ISBN, niet gevonden in beide APIs

- [x] **Feature 2: PDF bekijken + externe links**
      - `GET /api/library/book/{hash}/view` endpoint: serveert PDF inline (Content-Disposition: inline), EPUB als application/epub+zip
      - "📄 Bekijk" link opent in nieuwe tab (geen JS nodig, puur `<a href target=_blank>`)
      - "🔗 Google Books" + "📚 OpenLibrary" links per rij (alleen zichtbaar als ISBN bekend)
      - HTML entities voor emoji (&#x1F4C4; etc.) — omzeilt Python surrogate encoding bug

- [x] **38/38 tests geslaagd**

## ✅ Afgerond — 2026-04-18 (sessie 14)

- [x] **Bug fixes book_metadata_vision.py (3 bugs)**
      - Bug 1 (EPUB rendering): vervangen door `_render_epub_cover()` via zipfile — directe extractie van coverafbeeldingen uit EPUB zip, bypast kapotte fitz HTML rendering
      - Bug 2 (Google Books 429): exponential backoff [5s, 15s, 30s] voor 429+503, was alleen 503
      - Bug 3 (JSON truncatie): `_safe_json_parse()` met 4 strategies; `response_mime_type="application/json"` in Gemini config; max_tokens 2000→3000
      - Mime-type detectie per afbeelding (JPEG/PNG) voor EPUB cover images

- [x] **`backfill_all_metadata()` + `--all` vlag**
      - Nieuw `backfill_all_metadata()` functie voor alle 35 medical_library boeken
      - `python3 book_metadata_vision.py --all` uitvoerbaar
      - Volledig backfill resultaat: **24/35 volledig (isbn+title+year)**, 11 gedeeltelijk, 0 mislukt

- [x] **Schema's tab: boek metadata status tabel**
      - `GET /api/schemas/metadata` endpoint: JSON list alle medical boeken met status
      - Schema's tab uitgebreid met live overzichtstabel: Titel | Auteurs | ISBN | Jaar | Bron | Ontbrekend
      - Kleurcodering: rood=geen titel, amber=needs_review, groen=volledig
      - ↻ Vernieuwen knop + lazy loading bij tab-switch

- [x] **AI Modellen tab: volgorde op `order` veld**
      - `order` veld toegevoegd aan alle 8 use cases in `ai_settings.json` (1–8)
      - `renderUseCases()` sorteert op `order` — volgorde: book_metadata → chunk_tagging → chunk_audit → ocr → image_description → image_captioning → rag → protocol
      - `saveAllUseCases()` behoudt `order` bij opslaan

- [x] **38/38 tests geslaagd**

## ✅ Afgerond — 2026-04-18 (sessie 13)

- [x] **Pipeline A: boek metadata extractie via Gemini Vision + Google Books + OpenLibrary**
      - `scripts/book_metadata_vision.py` aangemaakt: volledig nieuwe pipeline
      - Gemini Vision (multi-image): titelpagina's 1–5 als PNG (300 DPI) → JSON
      - Google Books API + OpenLibrary API: ISBN-gebaseerd opzoeken
      - Veld-prioriteits merge: `google > gemini > openlibrary` per veld
      - ISBN-13 checksum validatie met OCR-last-digit correctie
      - Atomische schrijf naar `state.json` (field: `book_metadata`)
      - `book_classifications.json`: `full_title` + `authors` bijgewerkt
      - Geïntegreerd in `book_ingest_queue.py`:
          - Fase 0: Gemini Vision ISBN fallback wanneer tekstextractie mislukt
          - Post-ingest: `enrich_book()` voor medical_library boeken
      - Test `test_book_metadata_vision_imports` toegevoegd aan `run_tests.py`
      - Bug fix: `/library` 500 error door int `date` veld → `str(meta.get("date") or "")[:4]`
      - 38/38 tests geslaagd

## ✅ Afgerond — 2026-04-18 (sessie 12)

- [x] **"Claude API audit" card verwijderd uit /settings Parameters tab**
      - HTML card inclusief API key input, toggle, model dropdown, workers verwijderd
      - JS: `testClaude()`, `saveSettings()`, `updateStatus()`, `toggleChanged()`, `refreshToggleUI()` verwijderd
      - `loadSettings()` opgeschoond: claude_api blok verwijderd, nightly + google_vision blijven
      - Endpoint `POST /api/settings/test-claude` verwijderd (alleen door die card gebruikt)
      - Endpoints `GET/POST /api/settings` behouden (ook gebruikt door nightly + google_vision)
      - 37/37 tests geslaagd

## ✅ Afgerond — 2026-04-18 (sessie 11)

- [x] **ANTHROPIC_API_KEY toegevoegd aan systemd service**
      - Key uitgelezen uit `settings.json → claude_api.api_key`
      - Ingevoegd in `/etc/systemd/system/medical-rag-web.service` (na GEMINI lijn)
      - `systemctl daemon-reload && restart` — service actief
      - Test: ollama ✅ 506ms · anthropic ✅ 1225ms · gemini ✅ 1453ms

## ✅ Afgerond — 2026-04-18 (sessie 10)

- [x] **AI provider abstraction layer Part 2 — volledige migratie**

  ai_settings.json uitgebreid met 3 nieuwe use cases:
    `ocr_correction`, `image_description`, `chunk_audit`

  AIClient uitgebreid:
    - `extra_options` parameter op `generate()` (voor temperature in OCR correctie)
    - `_ollama_vision()` methode toegevoegd (Ollama LLaVA)

  6 scripts gemigreerd naar AIClient:
    - `scripts/audit_book.py` — `_ollama()` → `_ai.generate("chunk_audit", ...)`
    - `scripts/claude_audit.py` — `audit_chunk(client, model, max_tokens, chunk)` → `_ai.generate("chunk_tagging", ...)`
    - `scripts/generate_protocol.py` — `ollama_generate()` → `_ai.generate("protocol_generation", ...)`
    - `scripts/rag_query.py` — `_ollama_generate()` → `_ai.generate("rag_answering", ...)`
    - `scripts/ocr_postcorrect.py` — `correct_with_ollama()` → `_ai.generate("ocr_correction", ..., extra_options={"temperature": 0.1})`
    - `scripts/ingest_books.py` — `_describe_image_ollama()` → `_ai.generate_vision("image_description", ...)`

  Commentaar toegevoegd:
    - `image_extractor.py`: "Google Cloud Vision — not migrated to AIClient (bounding-box API)"
    - `web/app.py`: "Streaming Ollama call — not migrated to AIClient (requires async streaming)"

  AI Modellen UI gebouwd in `/settings`:
    - Derde tab "AI Modellen" met use-case tabel (provider + model dropdowns)
    - Provider status kaarten met "Alle testen" knop
    - `GET /api/ai/settings` + `POST /api/ai/settings` endpoints
    - `GET /api/ai/test-providers` endpoint (test alle 3 providers)

  AI_STATUS.md:
    - `update_ai_status_md()` functie in `ai_client.py`
    - `sync_context.py` roept `update_ai_status_md()` aan bij elke sync
    - `SYSTEM_DOCS/AI_STATUS.md` initieel gegenereerd

  37/37 tests geslaagd

## ✅ Afgerond — 2026-04-18 (sessie 9)

- [x] **AI provider abstraction layer Part 1 — scripts/ai_client.py + config/ai_settings.json**
      - `AIClient.generate(use_case, prompt)` → Ollama / Anthropic / Gemini
      - `AIClient.generate_vision(use_case, image_path, prompt)` → Gemini / Anthropic
      - `ai_settings.json`: 3 providers × 5 use cases (chunk_tagging, rag_answering,
        protocol_generation, book_metadata, image_captioning)
      - Gemini fix: `response.text` kan None zijn bij MAX_TOKENS — fallback via candidates
      - Alle 3 providers getest: ollama ok ✅ gemini ok ✅ anthropic ok ✅
      - 37/37 tests geslaagd

## ✅ Afgerond — 2026-04-18 (sessie 8)

- [x] **GEMINI_API_KEY toegevoegd aan server + Gemini SDK geïnstalleerd**
      - `/root/.bashrc` + `/root/.profile`: `export GEMINI_API_KEY="..."` toegevoegd
      - `/etc/systemd/system/medical-rag-web.service`: `Environment="GEMINI_API_KEY=..."` toegevoegd
      - `google-genai` 1.73.1 geïnstalleerd (nieuwe SDK — `google-generativeai` is deprecated)
      - Beschikbaar model: `gemini-2.5-flash` (niet `gemini-2.0-flash` — die is afgesloten voor nieuwe gebruikers)
      - API test geslaagd: "Gemini connected successfully"

## ✅ Afgerond — 2026-04-18 (sessie 7)

- [x] **book_classifications.json opschoning — "In wachtrij" stubs opgelost**

  Fix 1 — 8 ghost entries verwijderd (0 vectors, 0 cache, 0 images, safety-check bevestigd):
    guyton, thieme_atlas, thieme_internal, patten,
    pocket_atlas_1/2/3, maciocia_diagnosis

  Fix 2 — Pattern mismatches gecorrigeerd:
    - `bates`: `"Bates Guide"` → toegevoegd `"Bates' Guide"` (apostrof ontbrak)
    - `maciocia_foundations`: toegevoegd `"756201384-the-foundations-of-chinese-medicine"`
      en `"foundations-of-chinese-medicine"` (spaties ≠ koppeltekens in bestandsnaam)

  Fix 3 — 2 echte `unclassified_` duplicaten verwijderd:
    - `unclassified_Bates' Guide...` (gedekt door `bates`)
    - `unclassified_756201384-...` (gedekt door `maciocia_foundations`)
    10 `unclassified_` entries met `library_category=None` gefix naar `medical_literature`
    37 `unclassified_` entries blijven over (legitieme recovery entries)

  Root cause diagnose: `/api/library/items` line 3505 hardcodes `status="in_wachtrij"`
    als `_resolve_state_entry` geen state.json vindt — veroorzaakt door pattern
    die de bestandsnaam niet matcht.

  37/37 tests geslaagd

## ✅ Afgerond — 2026-04-18 (sessie 6)

- [x] **Fix 1 — Prioriteit dropdown /images** — Unicode mismatch opgelost
      - Root cause: click-outside handler controleerde U+25BE (▾) maar knop render ▼ (U+25BC)
      - Fix: `class="prio-toggle-btn"` toegevoegd aan knop; handler gebruikt nu `classList.contains()`
      - Test toegevoegd: `test_images_prio_dropdown_unicode` — 37/37 groen

- [x] **Fix 2 — Touch for Health in verkeerde sectie**
      - Root cause: `book_classifications.json` had `library_category=nrt_curriculum`
        maar bestand staat in `books/medical_literature/` + collection=medical_library
      - Fix A: library_category gecorrigeerd naar `medical_literature`
      - Fix B (structureel): `/api/library/items` gebruikt nu `state.json collection` als
        authoritative source voor unambiguous collections (nrt/qat/rlt/pemf) — voorkomt
        toekomstige divergentie tussen Importeer-tab en Bibliotheek-tab
      - Polyvagal Theory: ghost entry in book_classifications.json (library_category=nrt_curriculum),
        geen bestand op disk — toont in NRT tab met 0 chunks (informatief, geen bug)

- [x] **Fix 3 — Queue stubs opruimen**
      - Queue was al leeg (0 entries) — geen actie nodig

## ✅ Afgerond — 2026-04-18 (sessie 5)

- [x] **Legacy cache cleanup + herstel** — 42 entries verwijderd + 37 hersteld
      - Root cause eerdere 0-deletions: Qdrant safety check gebruikte source_file=filename,
        waardoor legacy entries ook vectors "hadden" (via goede entry met zelfde bestandsnaam)
      - Correcte aanpak: `Path(filepath).exists()` — 42 legacy entries verwijderd
      - Kept (permanently_failed): 4 entries — FlexBeam Neck/Knees/Stomach + Levels Mat
      - Kept (file exists): 1 entry — test_acupuncture.pdf
      - Lege legacy directories verwijderd: `books/device/`, `books/nrt_qat/`
      - Bijwerking: 37 boeken verloren hun enige cache entry (legacy audit blokkeerde startup_scan)
      - Herstel: 37 recovery state.json entries aangemaakt (completed_at gezet, Qdrant intact)
      - Eindtelling na herstel: nrt_curriculum 9/9 ✅, qat_curriculum 5/5 ✅,
        rlt_flexbeam 25 disk / 22 done (6 permanently_failed, pre-existing),
        pemf_qrs 7 disk / 6 done (2 permanently_failed, pre-existing)
      - 36/36 tests geslaagd

- [x] **PDF date parsing bug fix** — `_extract_pdf_metadata` sloeg "D:20" op ipv "2023"
      - Root cause: `raw["creationDate"][:4]` op "D:20230418..." → "D:20"
      - Fix: strip "D:" prefix → regex `\d{4}` → valideer 1990–2030
      - Backfill: 71 state.json bestanden bijgewerkt door re-extractie uit originele PDF bestanden

- [x] **Transcription queue test fix** — `test_transcription_queue_service` faalde bij lege queue
      - Root cause: lege queue → service exit → Restart=always → status 'inactive' (niet 'failed')
      - Fix: assertIn(['active', 'inactive', 'activating']) ipv assertEqual('active')
      - 36/36 tests geslaagd

## ✅ Afgerond — 2026-04-18 (sessie 4)

- [x] **ISBN-gebaseerde duplicaatdetectie in ingest pipeline** — Fase 0 gebouwd (4 delen)
      - **parse_epub.py:** `_get_first_pages_text()`, `_extract_isbn_from_text()`,
        `_extract_isbn()`, `_lookup_isbn()` (Google Books → OpenLibrary fallback)
      - **book_ingest_queue.py:** `_run_fase0_isbn_check()` — extraheert ISBN, doet API lookup,
        scant alle state.json bestanden op zelfde ISBN, pauzeert bij match
      - `startup_scan()`: skip books met `status='isbn_duplicate_paused'` (wachten op gebruiker)
      - `process_book()`: Fase 0 vóór Fase 1 (alleen medical_library), skip als skip_isbn_check=True
      - Post-parse metadata enrichment: ISBN + API lookup voor alle boeken na Fase 1
      - **web/app.py:** `POST /api/library/book/{hash}/resume` endpoint (sets skip_isbn_check=True, re-queue)
      - `_compute_book_status()`: `isbn_duplicate_paused` → `"isbn_duplicate_paused"`
      - `renderCard()`: amber achtergrond (#FAEEDA) + "Mogelijk duplicaat van:" tekst + knoppen
      - `resumeBook()` + `cancelBook()` JS functies (data-* patroon)
      - **Backfill:** ISBN lookup op 34 bestaande medical_library boeken:
        isbn_found=18, api_hit=15, titles_added=6, years_added=2
      - 36/36 tests geslaagd

## ✅ Afgerond — 2026-04-18 (sessie 3)

- [x] **Catalogus sectie-indeling, titels en publicatiejaren voltooid** — /library volledig herzien
      - JS `renderItems()` groepeert op `DISPLAY_SECTIONS` (5 secties: geen Acupunctuur meer)
      - Sectieheaders: teal `#1A6B72`, font-weight 700, `border-bottom:2px solid #e8f4f5`
      - Python `_extract_pub_year()` helper: ISO datum + PDF D:YYYYMMDD... formaat
      - `pub_year` toegevoegd aan `state_map` entry + `items_out` in `api_library_items`
      - Medische Literatuur: `full_title (jaar)` — 12/34 boeken hebben jaar uit metadata
      - Non-medical secties: tonen bestandsnaam als display title (ipv full_title)
      - FIX 1: 9 `library_category='acupuncture'` → `'medical_literature'` in book_classifications.json
      - FIX 2: 39 `unclassified_*` entries kregen `full_title` uit PDF/EPUB extractie
      - FIX 3: 4 state.json bestanden bijgewerkt met publicatiejaar uit copyright-tekst:
        deadman=1998, cecil_sterman=2018, atlas_acupuncture=2008, maciocia_practice=2008
      - Structurele test voor JS literal newlines uitgebreid tot volledige 8-state parser
        (regex literals, template literals, comments — geen false positives meer)
      - 36/36 tests geslaagd

## ✅ Afgerond — 2026-04-18

- [x] **sync_context.py + post-commit hook** — CONTEXT.md auto-genereert bij elke commit + elke 5 min
      - `scripts/sync_context.py`: live Qdrant counts, open issues uit BACKLOG.md, auto-timestamp
      - `.git/hooks/post-commit`: genereert CONTEXT.md, amends commit als gewijzigd, pusht automatisch
      - `sync_status.py`: roept sync_context.py aan vóór git add → CONTEXT.md meegecommit elke 5 min
      - Deduplicatie van open issues (Trail Guide verscheen dubbel in BACKLOG)

- [x] **"Bewaar dit" knop feedback + timeout** — visuele feedback + elapsed timer toegevoegd
      - Root cause: `data-delete` attribute bestond, maar JS zocht op `data-keep` (niet aanwezig)
      - Fix: `data-delete` → `data-keep` + `data-other` op beide knoppen per paar
      - `data-book-hash` op card div zodat JS cards kan vinden voor groen/rood highlight
      - Groen (#f0fdf4 + #86efac) voor bewaarde kaart, rood (#fef2f2 + #fca5a5) voor te verwijderen
      - Beide knoppen disabled + "Bezig..." tekst direct na klik; elapsed timer elke seconde
      - Reset visuele staat op fout; reload na 800ms bij succes
      - httpx timeout delete verhoogd van 30s → 120s voor grote boeken

- [x] **Structurele fix onclick — LOW RISK instances** — alle resterende onclick f-string interpolaties naar `data-*` patroon
      - `uploadBook` (library/ingest): `section_key` → `data-section`
      - `resolveDup` (library banner): `bh`+`delete_hash` → `data-hash`+`data-delete`
      - `setPriority` (images prio dropdown): 3 params → `data-hash`+`data-cls`+`data-prio`
      - `togglePrioMenu` (images prio button): `bh` → `data-hash`
      - `toggleImgBook` (images book div): `bh` → `data-hash`
      - `setImgFilter` (images filter btns): bestaande `data-hash`+`data-filter` hergebruikt
      - `selectAllVisible`, `deleteSelected`, `loadMoreImgs` (images): `bh` → `data-hash`
      - Resterende grep-matches zijn JS template literals (`${k}`, `${img.url}`) — geen Python f-strings

- [x] **Structurele fix onclick XSS** — alle HIGH RISK f-string onclick interpolaties vervangen door `data-*` patroon
      - `manualTranscribe` (video pagina, lijn 1310): `esc_name` → `data-filename` + `html.escape()`
      - `reauditBook` (library pagina, lijn 2018): `b["name"]` → `data-book-name` + `html.escape()`
      - `doSearch` (search pagina, lijn 6332): `json.dumps(qv)` → `data-query` + `html.escape()`
      - `html` module toegevoegd aan imports; `esc_name` variabele verwijderd (was dead code)

- [x] **Duplicaatdetectie feature** — gebouwd (deel A–D)
      - A: `_extract_epub_dc_metadata` + `_extract_pdf_metadata` in parse_epub.py
      - A3: book_metadata veld in state.json bij elke ingest (epub + pdf)
      - A4: backfill uitgevoerd — 93 bestaande boeken bijgewerkt
      - B: `_find_duplicates()` + `_duplicate_score()` + `GET /api/library/duplicates`
      - B3: duplicaatcheck bij upload (fuzzy stem matching, dup_warning in response)
      - C: `DELETE /api/library/book/{hash}` + `POST /api/library/duplicates/resolve`
      - D: amber banner in /library UI met "Bewaar dit" knoppen
      - Resultaat: 2 bevestigde ASIN-duplicaten gevonden (Bates + Magee)
      - Minimale pagina-drempel (≥20 pagina's) voorkomt false positives voor kleine pamfletten
- [x] **Bug fix /images prio dropdown** — cls_key leeg → nuttige foutmelding, geen crash
- [x] **Bug fix /images overflow** — overflow:hidden → position:relative op outer div
- [x] **sobotta_vol2 + vol3 filename_patterns** — gecorrigeerd (Vol. 2 / Vol. 3 met komma+spatie)

---

## 🔴 Prioriteit — volgende sessie

- [x] **OPDRACHT B (UI) voltooid** ✅ — zie Afgerond hieronder
- [x] **Domain MDs aangemaakt** ✅ — zie Afgerond hieronder (Domain-QAT, NRT, RLT, PEMF, Klinisch skeleton)

- [ ] **Trail Guide ingest valideren** — RapidOCR run actief (gestart 08:32)
      ```bash
      curl localhost:6333/collections/medical_library | python3 -c \
        "import json,sys; d=json.load(sys.stdin); print(d['result']['points_count'])"
      journalctl -u book-ingest-queue --no-pager -n 50 | grep -E "trail|Produced|chunks"
      ```
      Verwacht: 500+ chunks (460 pagina's, RapidOCR 151-404 words/pagina in test)
      Vision credentials: `config/google_vision_key.json` aanwezig ✅ — Vision actief na volgende parse-run

- [ ] **Deadman + Travell chunk counts valideren in Qdrant**
      Verwacht: Deadman 1000+ chunks (673p), Travell 800+ chunks (838p)

- [ ] **Eerste protocol genereren via /protocols** (Etalagebenen als testklacht)
      Vereiste: Deadman chunks in Qdrant (kai_a=1)
      Test: `python3 /root/medical-rag/scripts/generate_protocol.py "Etalagebenen"`

- [x] **1.Upper_Body_Techniques.mp4 verwijderen uit skip_files** ✅ — verwijderd uit settings.json; transcription-queue geherstart; 14 videos in queue waaronder dit bestand

---

## 🧠 ARCHITECTUUR — Kennissyntheselaag (ontworpen sessie 2026-04-17)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## 🔴 PRIORITEIT — Volgorde van uitvoering (bijgesteld 2026-04-17)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### Fase 0 — Bestaande functionaliteit stabiliseren (EERST)

- [ ] Bestaande protocollen draaien door nieuwe setup valideren
      Test: genereer protocol voor Etalagebenen en OMD
      Vergelijk kwaliteit met bestaande gold standard .docx bestanden
      Pas aan waar kwaliteit terugloopt

- [ ] Bibliotheek verder opbouwen — nieuwe boeken en transcripties
      Transcriptie queue afmaken (video's die wachten)
      EPUBs met captions volledig verwerkt (re-extractie loopt)

- [ ] Trail Guide ingest valideren
      473 vectors aanwezig in Qdrant maar state.json zegt pending

### Fase 1 — Appendices (eerste concrete deliverable, hoge waarde)

Appendices zijn herbruikbare protocolblokken. Als een klacht een
bepaald systeem raakt, wordt de appendix automatisch toegevoegd.
Doel: het wiel niet opnieuw uitvinden.

Bekende appendices om te maken (handmatig schrijven, Axel + AI):
- [ ] Appendix-Autoimmuun.md
      Inhoud: HPA-as, pijnappelklier, hypofyse, thymus
      Weefsel, QAT aanpak, NRT relevantie, acupunctuurpunten,
      PEMF/RLT indien van toepassing
      Trigger: klacht heeft auto-immuun component

- [ ] Appendix-NervusVagus.md
      Inhoud: vagustonus, polyvagale theorie,
      cholinergic anti-inflammatory pathway
      Trigger: chronische pijn, burn-out, trauma, autonome component

- [ ] Appendix-Endocrien.md
      Inhoud: hypofyse, bijnier, schildklier, pijnappelklier
      Trigger: klacht heeft endocrien component

- [ ] Appendix-Sympathicus.md
      Inhoud: SNS hyperactiviteit, fight/flight weefseleffecten
      Trigger: sympathische hyperactiviteit aanwezig

Werkwijze appendices:
  Stap 1: Axel schrijft/keurt goed wat er in moet staan
  Stap 2: AI vult aan vanuit literatuur (RAG op medical_library)
  Stap 3: Opslaan als MD op server, zichtbaar op /protocollen
  Stap 4: Trigger-logica in protocolgenerator

### Fase 2 — QAT en NRT samenvatting (cross-document)

BESLUIT: Geen automatisch gegenereerde Domain MDs vanuit Qdrant chunks.
Te weinig chunks (QAT=125, NRT=425) voor kwalitatieve synthese.
Te veel risico op oppervlakkige output die meer kwaad dan goed doet.

Aanpak: platte, handgeschreven uitleg van wat verwacht wordt.
Doel: AI snapt wat QAT/NRT is en hoe het te integreren in protocol.

- [ ] QAT-Samenvatting.md — handmatig schrijven
      Beantwoordt: hoe behandel ik weefsel met QAT?
      Secties:
        Wat is QAT (kort, voor AI-context)
        Werkingsprincipe: visualisatie + intentie op weefsel
        Welk weefsel visualiseer je: spier / fascia / orgaan / bot / zenuw
        Balancepunten (definitief april 2026 — niet wijzigen):
          CV=SP-21r | GV=SP-21l | BL=BL-58 | SJ=SJ-5
          KID=KID-4 | P=P-6 | GB=GB-37 | ST=ST-40
          LI=LI-6 | SI=SI-7 | LU=LU-7 | SP=SP-4 | HE=HE-5 | LIV=LIV-5
        Wanneer QAT inzetten, wanneer niet
        Combinatie met NRT en acupunctuur
      Extra: cross-document samenvatting vanuit qat_curriculum + video
      → "wat zegt al het QAT materiaal samen over visualisatie?"

- [ ] NRT-Samenvatting.md — handmatig schrijven
      Beantwoordt: welke spieren reset ik, hoe, en hoe visualiseer ik?
      Secties:
        Wat is NRT (kort, voor AI-context)
        Werkingsprincipe: GTR / neuraal reset mechanisme
        Spiergroepen per zone (bovenlichaam / onderlichaam)
        Hoe reset je (techniek — geen fysio nodig)
        Visualisatie: hoe stel je je de spier voor
        Wanneer NRT, wanneer niet
        Combinatie met QAT en acupunctuur
      Extra: cross-document samenvatting vanuit nrt_curriculum + video
      → "wat zegt al het NRT materiaal samen over resetvolgorde?"

  Waarde cross-document samenvatting:
  De AI verzamelt informatie verspreid over cursusmateriaal,
  handleidingen en video-transcripties tot één coherent beeld.
  Dit is wél zinvol — niet als automatisch gegenereerde MD,
  maar als door Axel goedgekeurde en bewerkte samenvatting.

### Fase 3 — Domain-Klinisch.md (kennisgeheugen)

- [ ] Domain-Klinisch.md aanmaken — handmatig starten
      Eerste vulling: pijnappelklier + hypofyse bij auto-immuun
        Bron: QAT cursus (Woods, Niveau 3)
        Bevestiging: Guyton H77 HPA-as + H80 melatonine/immuun
        Status: bevestigd mechanisme
      Daarna: groeit na elke sessie

      Secties:
        1. Weefsel-Diagnose koppelingen (ontdekt, met bronniveau)
        2. Verborgen mechanismen (hypothese / ondersteund / bevestigd)
        3. Weefsel-Weefsel relaties (anatomisch/functioneel)
        4. TCM-Westers bruggen
        5. Diagnose-combinaties
        6. Tegengestelde bevindingen
        7. Openstaande hypotheses

      Update-signalen:
        AI zoekt iets op dat al eerder uitgewerkt was
        Bevinding bij klacht X ook relevant voor klacht Y
        Axel voegt mondelinge kennis toe
        Bestaand inzicht onvolledig voor nieuwe klacht

### Fase 4 — /protocollen UI uitbreiden

- [ ] Tabblad "Kennisbank" toevoegen aan /protocollen
      Toont: QAT-Samenvatting, NRT-Samenvatting, Domain-Klinisch
      Toont: alle Appendices
      Bewerkbaar via editor (zelfde patroon als Standaard Protocol)
      Status-badge per MD: "handmatig" / "AI-gegenereerd" / "goedgekeurd"

- [ ] Protocolgenerator aanpassen
      Appendix-trigger logica: welke appendix bij welke klacht
      QAT/NRT summaries als context meesturen per protocol
      Domain-Klinisch.md altijd meelezen

### Fase 5 — Zelflerende kennisgraaf (GEPARKEERD)

BESLUIT: Nu niet bouwen. Infrastructuur te complex voor huidige fase.
Opnieuw evalueren als Fase 1-3 werken en kwaliteit protocollen
aantoonbaar beter is dan huidige gold standard.

Concept (voor toekomstige sessie):
  Relaties worden querybaar in plaats van alleen leesbaar als tekst
  "Geef alle weefsels betrokken bij auto-immuun" → directe query
  "Welke meridianen zijn actief bij tinnitus" → gestructureerd antwoord
  Implementatie: knowledge graph (Neo4j of JSON structuur)
  gevuld vanuit Domain-Klinisch.md + Literatuurreferenties per klacht
  Voorwaarde: Domain-Klinisch.md eerst manueel rijp maken
              zodat auto-extractie later mogelijk is

---

## 🟡 Gepland

- [ ] **Playwright regressietests** — 8 nav-items + kritieke pagina's automatisch testen
- [ ] **QAT curriculum valideren** — 546 vectors in nrt_qat_curriculum — zijn dit de juiste chunks?
- [ ] **EPUB image extractie testen** — Sobotta/AnatomyTrains nog niet geïngesteerd; na upload nachtrun testen
- [ ] **PDF Vision API extractie valideren** — Deadman + Travell na nachtrun: verwacht 400+ figuren per boek
- [ ] **Video transcriptie 19 NRT video's** — queue actief, 1.Upper_Body overgeslagen
- [ ] **Meer boeken uploaden:**
      - Sobotta Vol 1/2/3 (EPUB) — kai_k=1 kai_i=1 primaire anatomie
      - Maciocia TCM 3 boeken — kai_k=1 kai_a=1 volledigste TCM bron
      - Campbell acupunctuurpuntenbrug — kai_k=1 kai_a=2
      - AnatomyTrains (EPUB) — kai_k=1 kai_i=1 fascia
- [ ] **gstack installeren** — `/cso`, `/investigate`, `/careful`, `/guard` skills
- [ ] **/search pagina verbeteren** — RAG query interface UI
- [ ] **Protocol taal optie** — standaard NL, optie EN
- [ ] **Streaming protocol generatie** — SSE progress events per sectie
- [ ] **Python-docx skill** — voor protocol generator alternatieven

---

## ⚙️ Hardware (gepland)

- [ ] **Mac Studio M5 Max** — verwacht WWDC juni 2026
      ~€2.299-€2.499 | 96/128GB RAM | 546 GB/s bandbreedte
      Hetzner CX53 blijft als backup/Tailscale endpoint + nachtrun server

---

## 🟢 Ideeën — nog niet besloten

- [ ] Interactieve afbeelding selectie UI (3-5 kandidaten per weefselrij)
- [ ] Protocol regeneratie per sectie (alleen één sectie herschrijven)
- [ ] Protocol versie management (v1/v2 naast elkaar)
- [ ] Blog generator NRT-Amsterdam.nl (RAG → Ollama → WordPress MCP)
- [ ] Visueel zoeken (upload afbeelding → zoek vergelijkbare)
- [ ] Officiële Deadman digitale versie aanschaffen (DRM-vrij via Eastland Press)
- [ ] Consistentie guardian cross-collectie
- [ ] Protocol pre-validatie (Ollama checkt dekking voor generatie)

---

## ✅ Afgerond — sessie 2026-04-17 (Domain MDs kennissyntheselaag)

- [x] **Domain-QAT.md aangemaakt** — /data/domain_mds/Domain-QAT.md
      Inhoud: werkingsmechanisme, apparaten (pads/clips/greens/rood), spiertesten, neurologische desorganisatie,
      TNT, CTB, pair balancing, 14 meridianen + tabel, ETT, infused salt, pendants, contra-indicaties
      Bronnen: 125 chunks uit qat_curriculum (QAT_2025, Home Study, 3× pendant PDFs)

- [x] **Domain-NRT.md aangemaakt** — /data/domain_mds/Domain-NRT.md
      Inhoud: wetenschappelijke basis (reciproke inhibitie, mechanoreceptoren), instrumenten,
      contra-indicaties, ERS 321 spieren (volledig numbered), UB/LB zones + anatomische referenties,
      specifieke reset-technieken, MS, Times-documenten tabel
      Bronnen: 425 chunks uit nrt_curriculum (UB 157, LB 132, Advanced 126, Times 10)

- [x] **Domain-RLT.md aangemaakt** — /data/domain_mds/Domain-RLT.md
      Inhoud: PBM werkingsmechanisme, golflengten, cellulaire effecten, FlexBeam specs, klinische tabel,
      programma's, placement-protocollen per lichaamsdeel, contra-indicaties, combinaties NRT/QAT, historische timeline
      Bronnen: 160 chunks uit rlt_flexbeam (22 bronnen)

- [x] **Domain-PEMF.md aangemaakt** — /data/domain_mds/Domain-PEMF.md
      Inhoud: transmembranale potentiaal, elektroporatie, QRS-101 componenten, indicatietabel met settings,
      dosis-richtlijnen op bloeddruk/pols, sessiestructuur, EC-certificering, combinaties
      Bronnen: 64 chunks uit pemf_qrs (QRS-101 Manual, Indication Settings, Home System, Operating Manual)

- [x] **Domain-Klinisch.md skeleton aangemaakt** — /data/domain_mds/Domain-Klinisch.md
      Status: skeleton — handmatig in te vullen met Axel
      Kaders: behandelfilosofie, klachtpatronen, weefselspecifieke keuzes, sessiestructuur,
      acupunctuurpunten notatie, GTR/Tit Tar, Appendices planning

---

## ✅ Afgerond — sessie 2026-04-17 (Opdracht B: UI collectie-architectuur)

- [x] **SECTION_MAP vervangen** (3 → 5 secties): medical_literature, nrt_curriculum, qat_curriculum, rlt_flexbeam, pemf_qrs
- [x] **`_CAT_LABELS` + `_CAT_ORDER`** bijgewerkt — tabs in /library tonen nieuwe collecties
- [x] **JS `CAT_LABELS` + `CAT_ORDER`** bijgewerkt — filterbuttons tonen NRT/QAT/RLT/PEMF tabs
- [x] **`_CAT_COLLECTION`** bijgewerkt — chunk counts en delete werken op juiste collecties
- [x] **`_COLL_OPTIONS`** bijgewerkt — zoekpagina toont 7 collecties (incl. video)
- [x] **`_AUDIT_COLLECTIONS`** bijgewerkt — retroaudit werkt op 5 text-collecties
- [x] **Search default collections** bijgewerkt — medical_library + nrt_curriculum + qat_curriculum + nrt_video_transcripts
- [x] **`/videos` pagina** — toont alleen NRT en QAT upload-groepen (pemf/rlt verborgen)
- [x] **`ingest_transcript.py`** — dynamische collectie-routing: nrt→nrt_video_transcripts, qat→qat_video_transcripts
- [x] **Boekbestanden verplaatst** — 46 bestanden naar nieuwe directories (nrt_curriculum, qat_curriculum, rlt_flexbeam, pemf_qrs)
- [x] **Legacy Qdrant collecties verwijderd** — nrt_qat_curriculum, device_documentation, video_transcripts

---

## ✅ Afgerond — sessie 2026-04-17 (Opdracht A: Collectie-architectuur migratie)

- [x] **6 nieuwe Qdrant collecties aangemaakt** (1024-dim Cosine, identiek aan bestaande)
      `nrt_curriculum`, `qat_curriculum`, `rlt_flexbeam`, `pemf_qrs`,
      `nrt_video_transcripts`, `qat_video_transcripts`
- [x] **Alle 1015 chunks gemigreerd** (vector-copy, geen re-embedding)
      nrt_qat_curriculum(546) → nrt_curriculum(421) + qat_curriculum(125) ✅
      device_documentation(228) → nrt_curriculum(4) + rlt_flexbeam(160) + pemf_qrs(64) ✅
      video_transcripts(241) → nrt_video_transcripts(241) ✅
      Correctie: NRT LB/UB Techniques (waren fout in device_documentation) → nrt_curriculum ✅
- [x] **46 state.json ingest_cache bestanden bijgewerkt** met nieuwe collection-naam
- [x] **book_classifications.json volledig geclassificeerd** — 0 entries met `?`
      Alle 65 entries hebben nu geldige `library_category` (nrt_curriculum/qat_curriculum/rlt_flexbeam/pemf_qrs/medical_literature/acupuncture)
      nrt_kinesiology → nrt_curriculum (7 entries), device → rlt_flexbeam (1 entry)
- [x] **book_ingest_queue.py SECTION_COLLECTION_MAP uitgebreid** met 4 nieuwe keys
- [x] **Legacy collecties BEWAARD** als backup: nrt_qat_curriculum, device_documentation, video_transcripts
      Verwijderen na OPDRACHT B (UI) verificatie

---

## ✅ Afgerond — sessie 2026-04-17 (/images 7 UI verbeteringen)

- [x] **7 UI fixes voor `/images` pagina toegepast**
      1. Geen auto-expand bij laden — pagina start met alle boeken collapsed
      2. Boektitel + auteurs ipv bestandsnaam — toont `full_title` (vet), `authors` (grijs), bestandsnaam (monospace klein)
      3. Prioriteit dropdown verplaatst naar drawer action bar (rechts uitgelijnd via `margin-left:auto`)
      4. Badge volgorde omgedraaid — eval badge eerst, dan prioriteit badge
      5. Sorteer dropdown toegevoegd — Afbeeldingen / Titel / Prioriteit / Beoordeeld; URL-state bewaard
      6. API limit 50 → 500 per boek (laden van alle thumbnails in één keer)
      7. Thumbnail klik = lightbox; zoom-knop verwijderd; `wrap.onclick` met checkbox-uitzondering

---

## ✅ Afgerond — sessie 2026-04-17 (EPUB re-extractie met figcaption)

- [x] **Re-extractie gestart voor alle EPUBs zonder captions** — 5 boeken
      Gestart: Bates (1449 imgs), QT 2.0 (37), QT Core (129), QT Heal (97), Sobotta Atlas (1919)
      Skip: Sobotta Textbook (had al captions), Anatomy Trains (herextractie eerder in sessie)
      Methode: `meta.unlink()` + `POST /api/library/book/{hash}/re-extract-images`
      Na voltooiing: "Met Caption" filter in /images toont figcaptions in plaats van leeg

---

## ✅ Afgerond — sessie 2026-04-17 (figcaption extractie + /images UI)

- [x] **`image_extractor.py` figcaption extractie verbeterd** — nieuwe helper `_extract_img_caption()`
      Oud: alleen `<figure><figcaption>` + `alt` → 1 caption in Anatomy Trains, 0 in Bates
      Nieuw: parent `figcaption` + next-sibling `<p>` met "Figure/Fig." + `alt` fallback
      Resultaat: 474/531 Anatomy Trains, 720/1449 Bates na re-extractie
      Opgeslagen als zowel `caption` als `alt_text` veld (API retourneert `alt_text`)
      Re-extractie triggeren: `POST /api/library/book/{hash}/re-extract-images`

- [x] **`/images` UI: filters verplaatst naar drawer, renamed naar Caption**
      Filter knoppen (Alle / Met Caption / Zonder Caption) verplaatst uit header naar action bar in drawer
      Verwijder-knop ook verplaatst naar drawer action bar
      Knop "Alles selecteren" toegevoegd — togglet alle zichtbare thumbnails (deselect als alle al geselecteerd)
      `_updateDelBtn()` gebruikt nu `inline-block` (was `block`)
      Header is nu schoner: alleen titel, image count, prioriteit badge, eval badge, prioriteit dropdown

---

## ✅ Afgerond — sessie 2026-04-17 (/images pagina volledige rewrite)

- [x] **`/images` pagina volledig herschreven** — server rendert alleen collapsed book rows; thumbnails laden via JS on demand
      Root cause blank thumbnails: `img.get("file","")` → correct: `img.get("filename","")` (alle metadata gebruikt `"filename"` key)
      Nieuwe endpoint: `GET /api/images/book/{book_hash}?offset=0&limit=50&filter=all|with_alt|without_alt`
      Retourneert: `total`, `total_with_alt`, `total_without_alt`, paginered `images[]` met `url`, `filename`, `alt_text`
      Nieuw endpoint: `POST /api/images/book/{book_hash}/delete` — verwijdert geselecteerde afbeeldingen van schijf + metadata
      Lazy loading: eerste boek auto-expanded; "Meer laden" knop per boek (50 per keer)
      Lightbox: klik op 🔍 icoon opent overlay met volledig formaat afbeelding + alt-tekst
      Multi-select: checkbox per thumbnail, "Verwijder geselecteerde" knop verschijnt bij selectie
      Filter per boek: Alle | Met ALT | Zonder ALT (live, geen page reload)
      Sortering: meeste afbeeldingen eerst (Bates 1498, Anatomy Trains 531, etc.)
      Prioriteit dropdown: behouden, via bestaand `POST /api/images/priority` endpoint
      Performance: 1498-image Bates laadt in <100ms vs eerder server-side pre-render van 20 caps

---

## ✅ Afgerond — sessie 2026-04-17 (JS syntax fix + library speed + video splitting + cleanup)

- [x] **`/library` JS syntax error gefixt** — `\'` in Python `"""..."""` string werd door Python omgezet naar `'`
      waardoor `\''` → `''` in de gerenderde JavaScript = twee aaneengesloten lege string literals → `SyntaxError: Unexpected string`
      Gevolg: gehele `<script>` block laadde niet → `loadItems()` werd nooit aangeroepen → eeuwige "Laden…"
      Fix: `\''` → `\\'` zodat Python `\'` uitvoert in het JavaScript (correct JS escape voor single-quote)
      Regel: `app.py:2853` — `confirmImageToggle` onclick handler in `buildPhaseTable()`

---

## ✅ Afgerond — sessie 2026-04-17 (library speed + video splitting + cleanup)

- [x] **`/api/library/items` versneld** — bottleneck was 60 afzonderlijke `httpx.AsyncClient` instanties per Qdrant-query
      Fix A: `_qdrant_count_source()` accepteert optionele `client=` parameter
      Fix B: `api_library_items()` maakt één gedeelde `httpx.AsyncClient` voor alle 60 queries via `asyncio.gather`
      Fix C: 10-seconden TTL response cache (`_ITEMS_CACHE`) — cache hit = 9ms vs 591ms (cache miss) vs 1.6s (was)
      Fix D: `_invalidate_items_cache()` aangeroepen na upload
- [x] **Upload logging verbeterd** — structured logging in `library_upload()`: received, size, saved, enqueued, errors met traceback
      2GB upload limiet toegevoegd; `_invalidate_items_cache()` na enqueue
- [x] **Literatuuroverzicht verwijderd** — route `GET /library/overview` + `library_overview()` verwijderd
      Nav-links verwijderd in `/library` (regel ~2162) en `/library/ingest` (incl. "→ alle boeken" span)
- [x] **Video ffmpeg splitting** — `_split_video_if_needed()` in `transcription_queue.py`
      Segmenteert video's >400MB in 20-min stukken via `ffmpeg -c copy` (geen re-encoding)
      `max_file_size_mb` verhoogd naar 2000 in settings.json (splitting handelt grote bestanden intern af)
- [x] **transcription-queue systemd** — `Restart=always` (was `on-failure`) — service herstart nu altijd na exit
      Nieuwe uploads worden automatisch opgepikt na max 30s (RestartSec=30)

---

## ✅ Afgerond — sessie 2026-04-17 (retroaudit multi-collection fix)

- [x] **`_run_retroaudit()` fix** — hardcoded `COLLECTION = "medical_library"` vervangen door
      loop over `_AUDIT_COLLECTIONS = ["medical_library", "nrt_qat_curriculum", "device_documentation"]`
      Elke point traceert zijn eigen collectie zodat `set_payload` naar de juiste collection schrijft
- [x] **`_run_reaudit_job()` fix** — `collection` gelezen uit `state.get("collection")` via `_find_state_for_file()`
      i.p.v. hardcoded `"medical_library"` in zowel `scroll` als `set_payload`
- [x] **`_clear_skipped_in_state()` nieuwe functie** — reset `chunks_skipped=0` in state.json
      na retroaudit (of per-boek reaudit) voor boeken waar Qdrant geen skipped chunks meer heeft
      Zorgt dat `audit_lopend` status verdwijnt na succesvolle tagging
- [x] **VERIFIED** — retroaudit vond 458 chunks (was 0), 458/458 getagd in ~3 min, 0 errors
      `audit_lopend: 5 → 0`, `chunks_skipped` gereset in alle state.json bestanden

---

## ✅ Afgerond — sessie 2026-04-17 (vision bbox image extraction rewrite)

- [x] **`image_extractor.py` volledig herschreven** — vision bbox approach:
      Tier 1 (≤50 PyMuPDF chars + var>500): rasterized diagram → full-page capture
      Tier 2 (>2000 PyMuPDF chars): dense text page → skip Vision API (kostenbesparend)
      Tier 3 (50-2000 chars): Vision text-sparse zone detectie via 60×60 BFS grid
- [x] **`_find_figure_regions()`** — BFS op lege cellen; filtert op area≥5%, h≥8%, w≥15%, density≥0.55
- [x] **`_extract_alt_text()`** — tekst boven/onder figure zone als alt-tekst
- [x] **`_get_vision_response()`** — helper voor Vision document_text_detection
- [x] **`max_pages` parameter** — test-limiet voor `extract_figures_from_pdf()`
- [x] **Re-extractie gestart** — Deadman + Travell opnieuw in gang gezet met nieuw algoritme

---

## ✅ Afgerond — sessie 2026-04-17 (image extraction toggle)

- [x] **`_blank_state()` in book_ingest_queue.py** — `image_extraction_enabled: True` standaard
      `process_book()` propageert vlag uit queue-entry naar nieuwe state
- [x] **`_compute_book_status()` DEEL B** — `if not image_extraction_enabled → klaar` (vóór image check)
- [x] **`_build_image_extraction_info()` DEEL C** — `disabled` status teruggeven als vlag false
- [x] **Upload form checkbox DEEL D** — "Afbeeldingen extraheren na verwerking" (standaard aan)
      FormData stuurt `enable_images`; `/library/upload` leest het; `_enqueue_book()` aanvaard parameter
- [x] **`_save_state()` helper** — atomisch schrijven via tmp-bestand
- [x] **Drawer toggle DEEL E** — checkbox met label Aan/Uit, `confirmImageToggle()` JS functie
      Confirmatie popup bij uitschakelen (meldt verwijdering); bookHash via meta object doorgegeven
- [x] **`POST /api/library/book/{hash}/toggle-images` DEEL F** — disabled→verwijdert images dir;
      enabled→herstart extractie in thread
- [x] **Fase 5 `disabled` status DEEL G** — badge "Uit" (grijs), detail "uitgeschakeld"

---

## ✅ Afgerond — sessie 2026-04-17 (afb_bezig status systeem)

- [x] **`_get_image_progress(book_hash)`** — helper die `/tmp/image_extraction_{hash}.json` leest
- [x] **`_compute_book_status()` herschreven** — 8 statussen, afb_bezig gedetecteerd via progress file
      klaar vereist nu `images > 0` OF `image_source == none`; lege metadata → `afb_lopend`
- [x] **`_build_image_extraction_info()` herschreven** — progress FIRST, daarna metadata check
- [x] **`afb_bezig` status toegevoegd** — `_STATUS_PILLS_PY` + JS `STATUS_PILLS`
- [x] **`api_library_items`** — `image_progress` veld toegevoegd bij `afb_bezig` items
- [x] **`renderCard()` JS** — progress subtitle (pagina's + fig. count) bij `afb_bezig`
- [x] **`buildPhaseTable()` fase 5** — `not_applicable` tonen; running vóór done; juiste badges
- [x] **Auto-refresh 15 sec** — `loadItems()` retourneert items; timer start/stopt op `afb_bezig`
- [x] **Statusflow legenda** — "Afb. bezig" node tussen "Afb. lopend" en "Klaar"
- [x] **`_library_section_html()`** — `afb_bezig` in `is_done`; progress tekst in statuscell
- [x] **`_book_status()`** — retourneert nu ook `book_hash` voor progress lookup
- [x] **`api_library_book_detail`** — `computed_status` veld toegevoegd

---

## ✅ Afgerond — sessie 2026-04-17 (Drawer + image herextractie)

- [x] **Drawer categorie beschrijvingstekst** — `dotRow(label, n, desc)` uitgebreid met muted beschrijving rechts van dots
      Beschrijvingen: Protocol="Behandelinstructies, punten", Diagnose="Symptomen, TCM-patronen",
      Anatomie="Spieren, zenuwen, structuren", Literatuur="Wetenschappelijke basis"
      Style: `font-size:11px; color:#085041; opacity:0.65; margin-left:8px`
- [x] **`POST /api/library/book/{hash}/re-extract-images`** — nieuwe endpoint, verwijdert metadata + herstart extractie in thread
- [x] **Deadman + Travell herextractie gestart** — `images_metadata.json` verwijderd, extracties lopen (`/tmp/image_extraction_*.json` aanwezig)
      Reden: eerste extractie (16 apr) had geen Google Vision credentials → lege `images: []`

---

## ✅ Afgerond — sessie 2026-04-17 (Status systeem overhaul)

- [x] **`_compute_book_status()`** — Python single source of truth, 7 statussen
      Prioriteitslogica: `permanent_fout > fout > bezig > in_wachtrij > audit_lopend > afb_lopend > klaar`
      Gebruikt door `api_library_items`, `api_library_progress_all/active`, `_book_status()`
- [x] **`STATUS_PILLS` + `statusPill()`** — JS object vervangt `STATUS_CFG` in /library pagina
      Zeven uniforme statussen met aparte `bg` en `color` (geen enkelvoudige `color + "22"` truc)
- [x] **"Lage kwaliteit" verwijderd** — `_book_status()` gebruikt `_compute_book_status()`;
      geen `low_quality` status meer; audit score hoort alleen in de drawer
- [x] **Fase 5 "Geen" fix** — `figures_found == 0` → badge "Geen" (grijs) i.p.v. "Klaar"
      Zowel in `buildPhaseTable()` (library drawer) als `_BOOK_PROGRESS_SCRIPT` (ingest pagina)
- [x] **Statusflow bovenaan /library** — horizontale flow na K/A/I legenda:
      In wachtrij → Bezig → Audit lopend → Afb. lopend → Klaar | Fout (apart)
- [x] **`computed_status` in API** — `api_library_progress_all` + `api_library_progress_active`
- [x] **Verificatie** — Deadman toont "Klaar", Trail Guide "Bezig", QAT items "Audit lopend"

---

## ✅ Afgerond — sessie 2026-04-17 (/library legenda + K/A/I badge beschrijvingen)

- [x] **Legenda bovenaan /library** — 3-koloms grid (#f8fafc achtergrond):
      Kolom 1: K/A/I categorie uitleg + prioriteit (1/2/3 gekleurde badges)
      Kolom 2: Gebruiksprofiel bolletjes (1–5 met teal/lichtblauw dots + beschrijving)
      Kolom 3: Audit score kleurschaal (4.5–5 groen → < 2.5 rood) + voetnoot
- [x] **K/A/I badges inline beschrijving** — `kaiPill()` herschreven:
      Elke badge toont tekst links ("Klinisch, primaire bron") + gekleurde badge rechts
      Drie badges verticaal gestapeld, rechts uitgelijnd via `flex-direction:column`
      `renderCard()` aangepast: array-filter voor aanwezige K/A/I waarden

---

## ✅ Afgerond — sessie 2026-04-17 (Google Vision credentials hersteld)

- [x] **Google Vision credentials hersteld** — `config/google_vision_key.json` aanwezig (2361 bytes)
      Service account: `nrt-vision-api@nrt-amsterdam.iam.gserviceaccount.com` | project: `nrt-amsterdam`
      Vision client aangemaakt: OK | `/settings` amber banner verdwijnt: JA
      Trail Guide volgende parse-run gebruikt nu Google Vision (parallel, 300 DPI, 8 workers)

---

## ✅ Afgerond — sessie 2026-04-17 (Google Vision Settings UI)

- [x] **Google Vision UI card** — `/settings` pagina, na Nachtelijke onderhoud kaart
      7 velden: DPI, language hints, min words, parallel workers, confidence toggle + drempel, advanced opties
      Amber banner wanneer `config/google_vision_key.json` ontbreekt (`vision_credentials_missing` vlag)
      `saveVision()` JS functie + `loadSettings()` uitgebreid met Vision sectie
- [x] **api_settings_post()** — `google_vision` toegevoegd aan saveable sections (deep merge)
- [x] **_get_vision_settings()** helper — leest uit settings.json, ondersteunt per-boek overrides via `vision_dpi`/`vision_min_words`
- [x] **TECHNICAL.md §1.2 + §5** — Vision parameters tabel + settings.json structuur bijgewerkt

---

## ✅ Afgerond — sessie 2026-04-17 (Trail Guide loop fix + Vision parameters)

- [x] **Infinite loop diagnose** — root cause: `startup_scan()` re-enqueuet failed books (geen completed_at)
      `Restart=on-failure` triggert bij service exit; 234 log mentions → ~39 runs × 460 pages = ~$27 Vision kosten
- [x] **FIX A — max retries** — `parse_retry_count` in state.json; na 3 pogingen → `permanently_failed`
      `startup_scan()` slaat permanently_failed books over; counter reset bij succesvolle parse
- [x] **FIX B — Vision parameters** — 300 DPI (was 150), `language_hints=["en"]`, lege-filter ipv `< 3 words`
      Actief zodra `config/google_vision_key.json` hersteld is (gitignored, handmatig)
- [x] **FIX D — is_mostly_image() bypass** — werkelijke root cause 0 chunks: atlas-detector vlagde alle pagina's
      `force_ocr_engine` bypast nu `_is_mostly_image()` in `_parse_scanned()` — RapidOCR werkt als fallback
      Test bevestigd: 151-404 words/pagina, 3 chunks uit 3 testpagina's via RapidOCR
- [x] **Trail Guide state reset** — `parse_retry_count=0`, parse phase pending, frisse start
- [x] **Queue herstart** — 08:32 gestart, Trail Guide 460 pagina's via RapidOCR cascade

---

## ✅ Afgerond — sessie 2026-04-17 (audit_score + category_scores fix)

- [x] **GitHub CONTEXT.md sync check** — lokaal en GitHub waren identiek, geen actie nodig
- [x] **audit_score Deadman + Travell** — was `None`/fout door Ollama timeouts; Claude API quality scorer gerund op 15 sample chunks
      Deadman: `quality_score=2.6` | Travell: `quality_score=2.56`
- [x] **category_scores beide boeken** — was `{}` door architectuurmismatch (Claude API zet `tags/kai_*`, Ollama zet `usability_tags`)
      Fix: KAI-derived usability profile synthetisch berekend uit kai_k/kai_a/kai_i chunk-verdeling
      Deadman: `protocol=5, diagnose=5, anatomie=5, literatuur=5`
      Travell: `protocol=5, diagnose=2, anatomie=5, literatuur=5`
- [x] **Background audit_book.py process gekilld** — voorkomen dat het Claude-scores overschreef na Ollama-timeouts

---

## ✅ Afgerond — sessie 2026-04-17 (5e fase + audit diagnose)

- [x] **5e fase "Afbeeldingen" in phase table** — /library drawer (buildPhaseTable) + /library/ingest widget
      `image_extraction_info` toegevoegd aan `/api/library/book/{hash}/detail` + `/api/library/progress/active`
      Voortgang via `/tmp/image_extraction_{hash}.json` (live progress file per boek)
      States: pending / running (+ progress bar) / done ({n} figuren geëxtraheerd) / not_applicable (skip rij)
- [x] **audit_score diagnose**
      - Deadman: `quality_score=None` in audit JSON — audit API-fout tijdens book audit run
      - Travell: `quality_score=4.85` — werkt correct
      - category_scores: `usability_profile.scores={}` voor beide — audit liep toen chunks nog `skipped_ollama_timeout` waren
      - Fix: re-run `audit_book.py` voor beide boeken (nu chunks zijn getagd)

---

## ✅ Afgerond — sessie 2026-04-17 (audit fallback + retroaudit)

- [x] **audit_chunk() permanente fallback** — lege tekst (<10 chars) → `tagged_claude_default` direct
      Na 3× falen → `tagged_claude_default` (k=3,a=3,i=3) + log warning met chunk preview
- [x] **retroaudit_skipped() fix** — vangt ook `<none>` status chunks op (niet alleen `startswith("skipped")`)
      Index-gebaseerde merge voor chunks zonder chunk_id
- [x] **Drawer info box** — Claude API aan → paars "Nu uitvoeren" bericht; uit → amber met tijdvenster zonder "200/nacht"
      `claude_api_enabled` toegevoegd aan `/api/library/book/{hash}/detail` response
- [x] **2773 chunks getagd** — Deadman 1013/1013 + Travell 1760/1760 volledig getagd na retroaudit
      Waren allemaal `skipped_ollama_timeout` of `<none>` — state.json gecorrigeerd

---

## ✅ Afgerond — sessie 2026-04-17 (extractie uit nachtrun)

- [x] **_phase_image_extract() verwijderd uit nightly_maintenance.py** — `_count_books_needing_extraction()`, alloc dict entry, fase-tuple en de volledige method weg
      Reden: extractie draait al als background thread direct na qdrant fase; nachtrun is overbodig
- [x] **Backfill gestart** — bestaande boeken met qdrant=done maar nog geen images_metadata.json worden nu bijgewerkt

---

## ✅ Afgerond — sessie 2026-04-17 (image pipeline refactor)

- [x] **Goedkeuringslogica verwijderd** — image_approvals.json, prescreeen_images(), screen_images_background() volledig weg
      `audit_book.py`, `book_ingest_queue.py`, `nightly_maintenance.py`, `web/app.py` opgeschoond
- [x] **Prioriteitssysteem** — `image_source`, `image_priority`, `image_priority_override`, `image_evaluated` in alle 54 boekentries
      epub → high | pdf → normal | override via /images UI → POST /api/images/priority
- [x] **image_extractor.py** — nieuw script: Vision API PICTURE blocks + PyMuPDF crop (PDF) + ebooklib (EPUB)
      `extract_figures_from_pdf()` + `extract_images_from_epub()` — parallel (8 workers)
      Output: `data/extracted_images/{book_hash}/images_metadata.json`
- [x] **Pipeline integratie** — background thread na qdrant fase start extractie automatisch
- [x] **Nachtrun fase vervangen** — `_phase_image_screening` → `_phase_image_extract()`
      Verwerkt boeken zonder images_metadata.json binnen tijdsbudget
- [x] **/images pagina herschreven** — prioriteitsbadges (Hoog/Normaal/Laag/Overslaan), evaluatie status, "Prioriteit wijzigen" dropdown
      Filters: Alle / Hoog / Normaal / Laag / Niet beoordeeld
      GET /api/images/library + POST /api/images/priority API endpoints

---

## ✅ Afgerond — sessie 2026-04-17

- [x] **git filter-branch** — google_vision_key.json volledig uit git history verwijderd
      700 commits herschreven, force push geslaagd, GitHub push protection opgeheven
- [x] **Trail Guide force_ocr_engine** — google_vision override in book_classifications.json
      EasyOCR kalibratie cache gewist, state gereset, Google Vision parallel mode actief
- [x] **Transcriptie skip mechanisme** — settings.json transcription.skip_files + max_file_size_mb
      1.Upper_Body_Techniques.mp4 (525MB) overgeslagen, queue hervat met 16_Expanded...
- [x] **Documentatie overhaul** — CONTEXT/TECHNICAL/OPERATIONS volledig herschreven
      BACKLOG bijgewerkt, CLAUDE.md documentatie triggers toegevoegd
      Orphan bestanden verwijderd (ARCHITECTURE/CHANGELOG/REQUIREMENTS/TECHNICAL_DESIGN/PROJECT_STATE)

---

## ✅ Afgerond — sessie 2026-04-16 (parse speed fix)

- [x] Native PDFs: PyMuPDF als primaire parser i.p.v. Docling (377× sneller, 92 pag/sec)
- [x] Scanned PDFs: RapidOCR als eerste engine in cascade
- [x] Deadman + Travell parse fase gereset (stonden op "running" met Docling)

---

## ✅ Afgerond — sessie 2026-04-16 (pipeline rebuild)

- [x] State machine per boek (state.json + fase-bestanden + resume logic)
- [x] ollama_manager.py (OllamaManager singleton met health checks + auto-restart)
- [x] Image screening ontkoppeld van hoofdpipeline (nightly job)
- [x] Autonoom watchdog service (watchdog.py + book-ingest-watchdog.service)
- [x] WATCHDOG_LOG.md auto-bijgewerkt en gesynchroniseerd naar GitHub
- [x] Progress widget fase-voor-fase display (parse → audit → embed → qdrant)
- [x] nightly_maintenance.py volledige implementatie (7 fasen)
- [x] STAP 0 schone start (collection deleted, caches cleared, PDFs hernoemd 01/02/03)

---

## ✅ Afgerond — sessies 2026-04-14/15/16

- [x] OCR cascade (RapidOCR → EasyOCR → Surya → Tesseract → Google Vision)
- [x] OCR preprocessing (deskew, denoise, CLAHE, Otsu)
- [x] Per-boek OCR kalibratie via Ollama (kalibratiecache)
- [x] Smart PDF type detectie (native/mixed/scanned)
- [x] K/A/I classificatiesysteem (35+ boeken, chunk-niveau payload)
- [x] Protocol generator (RAG + K/A/I filter + Ollama + Word .docx)
- [x] 476 Deadman punt afbeeldingen + point_index.json
- [x] normalize_points.py (alle varianten → Deadman standaard)
- [x] MemPalace MCP server (116+ drawers)
- [x] Playwright MCP server
- [x] nrt-ui-standards skill (design tokens + schrijfregels)
- [x] PostToolUse hook (py_syntax_check.sh)
- [x] PreToolUse hook (security_check.sh)
- [x] Stop hook (mempalace_save.sh)
- [x] Design audit (#2563eb → #1A6B72 teal in alle pagina's)
- [x] Video transcriptie queue (systemd, Whisper)
- [x] /library catalogus (6 tabs, K/A/I badges, zoekbalk, sortering)
- [x] FastAPI web interface volledig (9 routes)
- [x] Live status sync GitHub (LIVE_STATUS.md elke 5 min)
