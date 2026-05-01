# Test Report — Medical RAG

**Datum:** 01-05-2026 00:00:34  
**Duur:** 21.5s  
**Uitslag:** ❌ MISLUKT  
**Score:** 38/39 geslaagd
  (0 overgeslagen, 1 mislukt, 0 fouten)

---

## InfrastructureTests

| Status | Test | Beschrijving | Tijd |
|---|---|---|---|
| ✅ PASS | `test_disk_space` | Vrije schijfruimte is groter dan 10 GB | 10 ms |
| ✅ PASS | `test_docling_import` | Docling kan worden geïmporteerd (PDF-extractie backend) | 0 ms |
| ✅ PASS | `test_ebooklib_import` | ebooklib kan worden geïmporteerd (EPUB-parser) | 0 ms |
| ✅ PASS | `test_ollama_running` | Ollama draait op localhost:11434 en geeft HTTP 200 terug op /api/tags | 3 ms |
| ✅ PASS | `test_qdrant_client_import` | qdrant_client kan worden geïmporteerd (vector store client) | 886 ms |
| ✅ PASS | `test_qdrant_running` | Qdrant draait op localhost:6333 en geeft HTTP 200 terug op /healthz | 2 ms |
| ✅ PASS | `test_ram_available` | Beschikbaar werkgeheugen is groter dan 4 GB | 0 ms |
| ✅ PASS | `test_sentence_transformers_import` | sentence_transformers kan worden geïmporteerd (embedding model) | 5659 ms |

## PipelineTests

| Status | Test | Beschrijving | Tijd |
|---|---|---|---|
| ✅ PASS | `test_embedding_generation` | BAAI/bge-large-en-v1.5 genereert vectoren van precies 1024 dimensies | 2955 ms |
| ✅ PASS | `test_epub_parsing` | EPUB-bestand kan worden geparsed; hoofdstuktekst is terug te vinden | 66 ms |
| ✅ PASS | `test_pdf_text_extraction` | PDF-tekst kan worden geëxtraheerd; page_number veld is aanwezig in resultaat | 3970 ms |
| ✅ PASS | `test_qdrant_insert_retrieve` | Vector kan worden ingevoegd in Qdrant en teruggehaald via payload-filter | 90 ms |

## QualityTests

| Status | Test | Beschrijving | Tijd |
|---|---|---|---|
| ✅ PASS | `test_corrupt_pdf_detection` | Beschadigde PDF wordt afgehandeld zonder crash (graceful error handling) | 36 ms |
| ✅ PASS | `test_figure_detection` | Docling detecteert een ingebedde afbeelding in een PDF | 2324 ms |
| ✅ PASS | `test_page_count_extraction` | Paginatelling van een 3-pagina PDF klopt met de verwachte waarde van 3 | 56 ms |

## IntegrationTests

| Status | Test | Beschrijving | Tijd |
|---|---|---|---|
| ❌ FAIL | `test_anthropic_api_key_set` | ANTHROPIC_API_KEY is set in the environment | 0 ms |
| ✅ PASS | `test_book_metadata_vision_imports` | book_metadata_vision importeert correct en ISBN validatie werkt | 1 ms |
| ✅ PASS | `test_books_dir_exists` | De books/ map bestaat en is beschrijfbaar | 0 ms |
| ✅ PASS | `test_data_json_files_valid` | Metadata JSON-bestanden bestaan en zijn geldig leesbaar | 0 ms |
| ✅ PASS | `test_docker_compose_present` | docker-compose.yml is aanwezig en bevat qdrant en ollama services | 0 ms |
| ✅ PASS | `test_images_prio_dropdown_unicode` | Prioriteit dropdown gebruikt class-check, niet fragiele textContent/unicode vergelijking | 92 ms |
| ✅ PASS | `test_ingest_transcript_executable` | scripts/ingest_transcript.py bestaat en is uitvoerbaar | 0 ms |
| ✅ PASS | `test_js_no_literal_newlines_images` | Geen literale newlines in JS string literals op /images | 66 ms |
| ✅ PASS | `test_js_no_literal_newlines_library` | Geen literale newlines in JS string literals op /library — veroorzaken SyntaxError | 81 ms |
| ✅ PASS | `test_js_no_literal_newlines_videos` | Geen literale newlines in JS string literals op /videos | 2508 ms |
| ✅ PASS | `test_logs_transcription_queue_endpoint` | /logs/transcription_queue returns JSON with non-empty lines list | 1014 ms |
| ✅ PASS | `test_no_quotes_in_event_handler_attrs` | Verify no JS event handlers in rendered HTML contain empty string
        literals ('') that cause SyntaxError. Strips <script> blocks first so
        JS source code with template literals is not scanned as HTML attributes.
        Catches the category of bug that broke /library (oninput with '' in
        f-string attribute). | 199 ms |
| ✅ PASS | `test_ollama_model_loaded` | llama3.1:8b model is geladen in Ollama | 2 ms |
| ✅ PASS | `test_qdrant_collections_endpoint` | Qdrant /collections geeft geldige JSON terug met 'result.collections' veld | 1 ms |
| ✅ PASS | `test_queue_file_valid` | Queue file exists and is valid JSON list | 0 ms |
| ✅ PASS | `test_scripts_present` | Alle vereiste scripts zijn aanwezig in scripts/ | 0 ms |
| ✅ PASS | `test_status_endpoint_valid` | Status endpoint returns a valid status value for a QAT video | 2 ms |
| ✅ PASS | `test_status_snapshot_endpoint` | /status/snapshot returns valid JSON with services.qdrant field | 567 ms |
| ✅ PASS | `test_sync_status_timer_active` | sync-status.timer is active (GitHub live sync every 5 min) | 5 ms |
| ✅ PASS | `test_transcription_log_exists` | Transcription queue log bestaat en is niet leeg | 0 ms |
| ✅ PASS | `test_transcription_queue_service` | transcription-queue.service is enabled (active or inactive — empty queue is ok) | 12 ms |
| ✅ PASS | `test_web_app_present` | web/app.py bestaat en bevat FastAPI app definitie | 1 ms |
| ✅ PASS | `test_web_dashboard_health` | FastAPI /health endpoint reageert met HTTP 200 en status 'ok' | 2 ms |
| ✅ PASS | `test_web_dashboard_root` | FastAPI dashboard geeft HTML terug met 'Medical RAG', 'Qdrant' en 'Ollama' | 932 ms |

---

## Mislukte tests — details

### `IntegrationTests.test_anthropic_api_key_set`

```
Traceback (most recent call last):
  File "/root/medical-rag/scripts/run_tests.py", line 862, in test_anthropic_api_key_set
    self.assertTrue(len(key) > 0,
AssertionError: False is not true : ANTHROPIC_API_KEY is niet ingesteld in de omgeving
```

---

## Aanbevelingen

- **Onderzoek `test_anthropic_api_key_set`:** zie details hierboven

---

*Gegenereerd door `scripts/run_tests.py`*