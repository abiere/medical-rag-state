# Test Report — Medical RAG

**Datum:** 14-04-2026 18:46:55  
**Duur:** 0.9s  
**Uitslag:** ✅ GESLAAGD  
**Score:** 15/15 geslaagd
  (9 overgeslagen, 0 mislukt, 0 fouten)

---

## InfrastructureTests

| Status | Test | Beschrijving | Tijd |
|---|---|---|---|
| ✅ PASS | `test_disk_space` | Vrije schijfruimte is groter dan 10 GB | 24 ms |
| ⏭️ SKIP | `test_docling_import` | Docling kan worden geïmporteerd (PDF-extractie backend) | 0 ms |
| ✅ PASS | `test_ebooklib_import` | ebooklib kan worden geïmporteerd (EPUB-parser) | 0 ms |
| ✅ PASS | `test_ollama_running` | Ollama draait op localhost:11434 en geeft HTTP 200 terug op /api/tags | 7 ms |
| ⏭️ SKIP | `test_qdrant_client_import` | qdrant_client kan worden geïmporteerd (vector store client) | 0 ms |
| ✅ PASS | `test_qdrant_running` | Qdrant draait op localhost:6333 en geeft HTTP 200 terug op /healthz | 3 ms |
| ✅ PASS | `test_ram_available` | Beschikbaar werkgeheugen is groter dan 4 GB | 0 ms |
| ⏭️ SKIP | `test_sentence_transformers_import` | sentence_transformers kan worden geïmporteerd (embedding model) | 0 ms |

## PipelineTests

| Status | Test | Beschrijving | Tijd |
|---|---|---|---|
| ⏭️ SKIP | `test_embedding_generation` | BAAI/bge-large-en-v1.5 genereert vectoren van precies 1024 dimensies | 0 ms |
| ✅ PASS | `test_epub_parsing` | EPUB-bestand kan worden geparsed; hoofdstuktekst is terug te vinden | 155 ms |
| ⏭️ SKIP | `test_pdf_text_extraction` | PDF-tekst kan worden geëxtraheerd; page_number veld is aanwezig in resultaat | 1 ms |
| ⏭️ SKIP | `test_qdrant_insert_retrieve` | Vector kan worden ingevoegd in Qdrant en teruggehaald via payload-filter | 0 ms |

## QualityTests

| Status | Test | Beschrijving | Tijd |
|---|---|---|---|
| ⏭️ SKIP | `test_corrupt_pdf_detection` | Beschadigde PDF wordt afgehandeld zonder crash (graceful error handling) | 0 ms |
| ⏭️ SKIP | `test_figure_detection` | Docling detecteert een ingebedde afbeelding in een PDF | 0 ms |
| ⏭️ SKIP | `test_page_count_extraction` | Paginatelling van een 3-pagina PDF klopt met de verwachte waarde van 3 | 0 ms |

## IntegrationTests

| Status | Test | Beschrijving | Tijd |
|---|---|---|---|
| ✅ PASS | `test_books_dir_exists` | De books/ map bestaat en is beschrijfbaar | 0 ms |
| ✅ PASS | `test_data_json_files_valid` | Metadata JSON-bestanden bestaan en zijn geldig leesbaar | 0 ms |
| ✅ PASS | `test_docker_compose_present` | docker-compose.yml is aanwezig en bevat qdrant en ollama services | 0 ms |
| ✅ PASS | `test_ollama_model_loaded` | llama3.1:8b model is geladen in Ollama | 3 ms |
| ✅ PASS | `test_qdrant_collections_endpoint` | Qdrant /collections geeft geldige JSON terug met 'result.collections' veld | 1 ms |
| ✅ PASS | `test_scripts_present` | Alle vereiste scripts zijn aanwezig in scripts/ | 0 ms |
| ✅ PASS | `test_web_app_present` | web/app.py bestaat en bevat FastAPI app definitie | 0 ms |
| ✅ PASS | `test_web_dashboard_health` | FastAPI /health endpoint reageert met HTTP 200 en status 'ok' | 2 ms |
| ✅ PASS | `test_web_dashboard_root` | FastAPI dashboard geeft HTML terug met 'Medical RAG', 'Qdrant' en 'Ollama' | 748 ms |

---

## Overgeslagen tests

| Test | Reden |
|---|---|
| `InfrastructureTests.test_docling_import` | docling niet geïnstalleerd: No module named 'docling' |
| `InfrastructureTests.test_qdrant_client_import` | qdrant_client niet geïnstalleerd: No module named 'qdrant_client' |
| `InfrastructureTests.test_sentence_transformers_import` | sentence_transformers niet geïnstalleerd: No module named 'sentence_transformers' |
| `PipelineTests.test_embedding_generation` | sentence_transformers niet geïnstalleerd |
| `PipelineTests.test_pdf_text_extraction` | docling niet geïnstalleerd |
| `PipelineTests.test_qdrant_insert_retrieve` | qdrant_client niet geïnstalleerd |
| `QualityTests.test_corrupt_pdf_detection` | docling niet geïnstalleerd |
| `QualityTests.test_figure_detection` | reportlab niet geïnstalleerd |
| `QualityTests.test_page_count_extraction` | pypdf niet geïnstalleerd |

---

## Aanbevelingen

- **Installeer docling:** `pip install docling docling-core --break-system-packages`
- **Installeer qdrant-client:** `pip install qdrant-client --break-system-packages`
- **Installeer sentence-transformers:** `pip install sentence-transformers --break-system-packages`
- **Installeer reportlab (testtool):** `pip install reportlab --break-system-packages`
- **Installeer pypdf:** `pip install pypdf --break-system-packages`

---

*Gegenereerd door `scripts/run_tests.py`*