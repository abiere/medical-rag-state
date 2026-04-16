# Test Report — Medical RAG

**Datum:** 16-04-2026 09:46:44  
**Duur:** 57.7s  
**Uitslag:** ✅ GESLAAGD  
**Score:** 33/33 geslaagd
  (0 overgeslagen, 0 mislukt, 0 fouten)

---

## InfrastructureTests

| Status | Test | Beschrijving | Tijd |
|---|---|---|---|
| ✅ PASS | `test_disk_space` | Vrije schijfruimte is groter dan 10 GB | 36 ms |
| ✅ PASS | `test_docling_import` | Docling kan worden geïmporteerd (PDF-extractie backend) | 1 ms |
| ✅ PASS | `test_ebooklib_import` | ebooklib kan worden geïmporteerd (EPUB-parser) | 1 ms |
| ✅ PASS | `test_ollama_running` | Ollama draait op localhost:11434 en geeft HTTP 200 terug op /api/tags | 9 ms |
| ✅ PASS | `test_qdrant_client_import` | qdrant_client kan worden geïmporteerd (vector store client) | 2490 ms |
| ✅ PASS | `test_qdrant_running` | Qdrant draait op localhost:6333 en geeft HTTP 200 terug op /healthz | 10 ms |
| ✅ PASS | `test_ram_available` | Beschikbaar werkgeheugen is groter dan 4 GB | 3 ms |
| ✅ PASS | `test_sentence_transformers_import` | sentence_transformers kan worden geïmporteerd (embedding model) | 16821 ms |

## PipelineTests

| Status | Test | Beschrijving | Tijd |
|---|---|---|---|
| ✅ PASS | `test_embedding_generation` | BAAI/bge-large-en-v1.5 genereert vectoren van precies 1024 dimensies | 6074 ms |
| ✅ PASS | `test_epub_parsing` | EPUB-bestand kan worden geparsed; hoofdstuktekst is terug te vinden | 196 ms |
| ✅ PASS | `test_pdf_text_extraction` | PDF-tekst kan worden geëxtraheerd; page_number veld is aanwezig in resultaat | 12356 ms |
| ✅ PASS | `test_qdrant_insert_retrieve` | Vector kan worden ingevoegd in Qdrant en teruggehaald via payload-filter | 405 ms |

## QualityTests

| Status | Test | Beschrijving | Tijd |
|---|---|---|---|
| ✅ PASS | `test_corrupt_pdf_detection` | Beschadigde PDF wordt afgehandeld zonder crash (graceful error handling) | 182 ms |
| ✅ PASS | `test_figure_detection` | Docling detecteert een ingebedde afbeelding in een PDF | 16775 ms |
| ✅ PASS | `test_page_count_extraction` | Paginatelling van een 3-pagina PDF klopt met de verwachte waarde van 3 | 180 ms |

## IntegrationTests

| Status | Test | Beschrijving | Tijd |
|---|---|---|---|
| ✅ PASS | `test_anthropic_api_key_set` | ANTHROPIC_API_KEY is set in the environment | 3 ms |
| ✅ PASS | `test_books_dir_exists` | De books/ map bestaat en is beschrijfbaar | 1 ms |
| ✅ PASS | `test_data_json_files_valid` | Metadata JSON-bestanden bestaan en zijn geldig leesbaar | 2 ms |
| ✅ PASS | `test_docker_compose_present` | docker-compose.yml is aanwezig en bevat qdrant en ollama services | 0 ms |
| ✅ PASS | `test_ingest_transcript_executable` | scripts/ingest_transcript.py bestaat en is uitvoerbaar | 0 ms |
| ✅ PASS | `test_logs_transcription_queue_endpoint` | /logs/transcription_queue returns JSON with non-empty lines list | 27 ms |
| ✅ PASS | `test_ollama_model_loaded` | llama3.1:8b model is geladen in Ollama | 8 ms |
| ✅ PASS | `test_qdrant_collections_endpoint` | Qdrant /collections geeft geldige JSON terug met 'result.collections' veld | 16 ms |
| ✅ PASS | `test_queue_file_valid` | Queue file exists and is valid JSON list | 1 ms |
| ✅ PASS | `test_scripts_present` | Alle vereiste scripts zijn aanwezig in scripts/ | 1 ms |
| ✅ PASS | `test_status_endpoint_valid` | Status endpoint returns a valid status value for a QAT video | 80 ms |
| ✅ PASS | `test_status_snapshot_endpoint` | /status/snapshot returns valid JSON with services.qdrant field | 719 ms |
| ✅ PASS | `test_sync_status_timer_active` | sync-status.timer is active (GitHub live sync every 5 min) | 26 ms |
| ✅ PASS | `test_transcription_log_exists` | Transcription queue log bestaat en is niet leeg | 1 ms |
| ✅ PASS | `test_transcription_queue_service` | transcription-queue.service is active | 15 ms |
| ✅ PASS | `test_web_app_present` | web/app.py bestaat en bevat FastAPI app definitie | 1 ms |
| ✅ PASS | `test_web_dashboard_health` | FastAPI /health endpoint reageert met HTTP 200 en status 'ok' | 11 ms |
| ✅ PASS | `test_web_dashboard_root` | FastAPI dashboard geeft HTML terug met 'Medical RAG', 'Qdrant' en 'Ollama' | 1195 ms |

---

## Aanbevelingen

Alle tests geslaagd. Het systeem is gereed voor gebruik.

---

*Gegenereerd door `scripts/run_tests.py`*