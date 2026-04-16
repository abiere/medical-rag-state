# Test Report — Medical RAG

**Datum:** 16-04-2026 14:40:50  
**Duur:** 43.8s  
**Uitslag:** ✅ GESLAAGD  
**Score:** 33/33 geslaagd
  (0 overgeslagen, 0 mislukt, 0 fouten)

---

## InfrastructureTests

| Status | Test | Beschrijving | Tijd |
|---|---|---|---|
| ✅ PASS | `test_disk_space` | Vrije schijfruimte is groter dan 10 GB | 44 ms |
| ✅ PASS | `test_docling_import` | Docling kan worden geïmporteerd (PDF-extractie backend) | 1 ms |
| ✅ PASS | `test_ebooklib_import` | ebooklib kan worden geïmporteerd (EPUB-parser) | 1 ms |
| ✅ PASS | `test_ollama_running` | Ollama draait op localhost:11434 en geeft HTTP 200 terug op /api/tags | 8 ms |
| ✅ PASS | `test_qdrant_client_import` | qdrant_client kan worden geïmporteerd (vector store client) | 2406 ms |
| ✅ PASS | `test_qdrant_running` | Qdrant draait op localhost:6333 en geeft HTTP 200 terug op /healthz | 7 ms |
| ✅ PASS | `test_ram_available` | Beschikbaar werkgeheugen is groter dan 4 GB | 0 ms |
| ✅ PASS | `test_sentence_transformers_import` | sentence_transformers kan worden geïmporteerd (embedding model) | 14187 ms |

## PipelineTests

| Status | Test | Beschrijving | Tijd |
|---|---|---|---|
| ✅ PASS | `test_embedding_generation` | BAAI/bge-large-en-v1.5 genereert vectoren van precies 1024 dimensies | 6572 ms |
| ✅ PASS | `test_epub_parsing` | EPUB-bestand kan worden geparsed; hoofdstuktekst is terug te vinden | 224 ms |
| ✅ PASS | `test_pdf_text_extraction` | PDF-tekst kan worden geëxtraheerd; page_number veld is aanwezig in resultaat | 10083 ms |
| ✅ PASS | `test_qdrant_insert_retrieve` | Vector kan worden ingevoegd in Qdrant en teruggehaald via payload-filter | 356 ms |

## QualityTests

| Status | Test | Beschrijving | Tijd |
|---|---|---|---|
| ✅ PASS | `test_corrupt_pdf_detection` | Beschadigde PDF wordt afgehandeld zonder crash (graceful error handling) | 80 ms |
| ✅ PASS | `test_figure_detection` | Docling detecteert een ingebedde afbeelding in een PDF | 5917 ms |
| ✅ PASS | `test_page_count_extraction` | Paginatelling van een 3-pagina PDF klopt met de verwachte waarde van 3 | 146 ms |

## IntegrationTests

| Status | Test | Beschrijving | Tijd |
|---|---|---|---|
| ✅ PASS | `test_anthropic_api_key_set` | ANTHROPIC_API_KEY is set in the environment | 0 ms |
| ✅ PASS | `test_books_dir_exists` | De books/ map bestaat en is beschrijfbaar | 0 ms |
| ✅ PASS | `test_data_json_files_valid` | Metadata JSON-bestanden bestaan en zijn geldig leesbaar | 0 ms |
| ✅ PASS | `test_docker_compose_present` | docker-compose.yml is aanwezig en bevat qdrant en ollama services | 0 ms |
| ✅ PASS | `test_ingest_transcript_executable` | scripts/ingest_transcript.py bestaat en is uitvoerbaar | 0 ms |
| ✅ PASS | `test_logs_transcription_queue_endpoint` | /logs/transcription_queue returns JSON with non-empty lines list | 11 ms |
| ✅ PASS | `test_ollama_model_loaded` | llama3.1:8b model is geladen in Ollama | 11 ms |
| ✅ PASS | `test_qdrant_collections_endpoint` | Qdrant /collections geeft geldige JSON terug met 'result.collections' veld | 5 ms |
| ✅ PASS | `test_queue_file_valid` | Queue file exists and is valid JSON list | 0 ms |
| ✅ PASS | `test_scripts_present` | Alle vereiste scripts zijn aanwezig in scripts/ | 0 ms |
| ✅ PASS | `test_status_endpoint_valid` | Status endpoint returns a valid status value for a QAT video | 59 ms |
| ✅ PASS | `test_status_snapshot_endpoint` | /status/snapshot returns valid JSON with services.qdrant field | 659 ms |
| ✅ PASS | `test_sync_status_timer_active` | sync-status.timer is active (GitHub live sync every 5 min) | 9 ms |
| ✅ PASS | `test_transcription_log_exists` | Transcription queue log bestaat en is niet leeg | 0 ms |
| ✅ PASS | `test_transcription_queue_service` | transcription-queue.service is active | 9 ms |
| ✅ PASS | `test_web_app_present` | web/app.py bestaat en bevat FastAPI app definitie | 1 ms |
| ✅ PASS | `test_web_dashboard_health` | FastAPI /health endpoint reageert met HTTP 200 en status 'ok' | 1864 ms |
| ✅ PASS | `test_web_dashboard_root` | FastAPI dashboard geeft HTML terug met 'Medical RAG', 'Qdrant' en 'Ollama' | 1157 ms |

---

## Aanbevelingen

Alle tests geslaagd. Het systeem is gereed voor gebruik.

---

*Gegenereerd door `scripts/run_tests.py`*