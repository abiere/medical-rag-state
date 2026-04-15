# Test Report — Medical RAG

**Datum:** 15-04-2026 00:00:50  
**Duur:** 46.1s  
**Uitslag:** ✅ GESLAAGD  
**Score:** 24/24 geslaagd
  (0 overgeslagen, 0 mislukt, 0 fouten)

---

## InfrastructureTests

| Status | Test | Beschrijving | Tijd |
|---|---|---|---|
| ✅ PASS | `test_disk_space` | Vrije schijfruimte is groter dan 10 GB | 33 ms |
| ✅ PASS | `test_docling_import` | Docling kan worden geïmporteerd (PDF-extractie backend) | 4 ms |
| ✅ PASS | `test_ebooklib_import` | ebooklib kan worden geïmporteerd (EPUB-parser) | 3 ms |
| ✅ PASS | `test_ollama_running` | Ollama draait op localhost:11434 en geeft HTTP 200 terug op /api/tags | 8 ms |
| ✅ PASS | `test_qdrant_client_import` | qdrant_client kan worden geïmporteerd (vector store client) | 2400 ms |
| ✅ PASS | `test_qdrant_running` | Qdrant draait op localhost:6333 en geeft HTTP 200 terug op /healthz | 4 ms |
| ✅ PASS | `test_ram_available` | Beschikbaar werkgeheugen is groter dan 4 GB | 1 ms |
| ✅ PASS | `test_sentence_transformers_import` | sentence_transformers kan worden geïmporteerd (embedding model) | 21020 ms |

## PipelineTests

| Status | Test | Beschrijving | Tijd |
|---|---|---|---|
| ✅ PASS | `test_embedding_generation` | BAAI/bge-large-en-v1.5 genereert vectoren van precies 1024 dimensies | 5814 ms |
| ✅ PASS | `test_epub_parsing` | EPUB-bestand kan worden geparsed; hoofdstuktekst is terug te vinden | 200 ms |
| ✅ PASS | `test_pdf_text_extraction` | PDF-tekst kan worden geëxtraheerd; page_number veld is aanwezig in resultaat | 10781 ms |
| ✅ PASS | `test_qdrant_insert_retrieve` | Vector kan worden ingevoegd in Qdrant en teruggehaald via payload-filter | 281 ms |

## QualityTests

| Status | Test | Beschrijving | Tijd |
|---|---|---|---|
| ✅ PASS | `test_corrupt_pdf_detection` | Beschadigde PDF wordt afgehandeld zonder crash (graceful error handling) | 60 ms |
| ✅ PASS | `test_figure_detection` | Docling detecteert een ingebedde afbeelding in een PDF | 4749 ms |
| ✅ PASS | `test_page_count_extraction` | Paginatelling van een 3-pagina PDF klopt met de verwachte waarde van 3 | 109 ms |

## IntegrationTests

| Status | Test | Beschrijving | Tijd |
|---|---|---|---|
| ✅ PASS | `test_books_dir_exists` | De books/ map bestaat en is beschrijfbaar | 0 ms |
| ✅ PASS | `test_data_json_files_valid` | Metadata JSON-bestanden bestaan en zijn geldig leesbaar | 1 ms |
| ✅ PASS | `test_docker_compose_present` | docker-compose.yml is aanwezig en bevat qdrant en ollama services | 0 ms |
| ✅ PASS | `test_ollama_model_loaded` | llama3.1:8b model is geladen in Ollama | 3 ms |
| ✅ PASS | `test_qdrant_collections_endpoint` | Qdrant /collections geeft geldige JSON terug met 'result.collections' veld | 3 ms |
| ✅ PASS | `test_scripts_present` | Alle vereiste scripts zijn aanwezig in scripts/ | 1 ms |
| ✅ PASS | `test_web_app_present` | web/app.py bestaat en bevat FastAPI app definitie | 0 ms |
| ✅ PASS | `test_web_dashboard_health` | FastAPI /health endpoint reageert met HTTP 200 en status 'ok' | 15 ms |
| ✅ PASS | `test_web_dashboard_root` | FastAPI dashboard geeft HTML terug met 'Medical RAG', 'Qdrant' en 'Ollama' | 631 ms |

---

## Aanbevelingen

Alle tests geslaagd. Het systeem is gereed voor gebruik.

---

*Gegenereerd door `scripts/run_tests.py`*