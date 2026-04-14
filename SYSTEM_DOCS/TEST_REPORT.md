# Test Report — Medical RAG

**Datum:** 14-04-2026 19:16:36  
**Duur:** 35.4s  
**Uitslag:** ❌ MISLUKT  
**Score:** 22/24 geslaagd
  (0 overgeslagen, 0 mislukt, 2 fouten)

---

## InfrastructureTests

| Status | Test | Beschrijving | Tijd |
|---|---|---|---|
| ✅ PASS | `test_disk_space` | Vrije schijfruimte is groter dan 10 GB | 23 ms |
| ✅ PASS | `test_docling_import` | Docling kan worden geïmporteerd (PDF-extractie backend) | 1 ms |
| ✅ PASS | `test_ebooklib_import` | ebooklib kan worden geïmporteerd (EPUB-parser) | 0 ms |
| ✅ PASS | `test_ollama_running` | Ollama draait op localhost:11434 en geeft HTTP 200 terug op /api/tags | 9 ms |
| ✅ PASS | `test_qdrant_client_import` | qdrant_client kan worden geïmporteerd (vector store client) | 1993 ms |
| ✅ PASS | `test_qdrant_running` | Qdrant draait op localhost:6333 en geeft HTTP 200 terug op /healthz | 5 ms |
| ✅ PASS | `test_ram_available` | Beschikbaar werkgeheugen is groter dan 4 GB | 0 ms |
| ✅ PASS | `test_sentence_transformers_import` | sentence_transformers kan worden geïmporteerd (embedding model) | 10996 ms |

## PipelineTests

| Status | Test | Beschrijving | Tijd |
|---|---|---|---|
| ✅ PASS | `test_embedding_generation` | BAAI/bge-large-en-v1.5 genereert vectoren van precies 1024 dimensies | 11685 ms |
| ✅ PASS | `test_epub_parsing` | EPUB-bestand kan worden geparsed; hoofdstuktekst is terug te vinden | 161 ms |
| 💥 ERROR | `test_pdf_text_extraction` | PDF-tekst kan worden geëxtraheerd; page_number veld is aanwezig in resultaat | 7688 ms |
| ✅ PASS | `test_qdrant_insert_retrieve` | Vector kan worden ingevoegd in Qdrant en teruggehaald via payload-filter | 170 ms |

## QualityTests

| Status | Test | Beschrijving | Tijd |
|---|---|---|---|
| ✅ PASS | `test_corrupt_pdf_detection` | Beschadigde PDF wordt afgehandeld zonder crash (graceful error handling) | 72 ms |
| 💥 ERROR | `test_figure_detection` | Docling detecteert een ingebedde afbeelding in een PDF | 1826 ms |
| ✅ PASS | `test_page_count_extraction` | Paginatelling van een 3-pagina PDF klopt met de verwachte waarde van 3 | 87 ms |

## IntegrationTests

| Status | Test | Beschrijving | Tijd |
|---|---|---|---|
| ✅ PASS | `test_books_dir_exists` | De books/ map bestaat en is beschrijfbaar | 0 ms |
| ✅ PASS | `test_data_json_files_valid` | Metadata JSON-bestanden bestaan en zijn geldig leesbaar | 0 ms |
| ✅ PASS | `test_docker_compose_present` | docker-compose.yml is aanwezig en bevat qdrant en ollama services | 0 ms |
| ✅ PASS | `test_ollama_model_loaded` | llama3.1:8b model is geladen in Ollama | 4 ms |
| ✅ PASS | `test_qdrant_collections_endpoint` | Qdrant /collections geeft geldige JSON terug met 'result.collections' veld | 2 ms |
| ✅ PASS | `test_scripts_present` | Alle vereiste scripts zijn aanwezig in scripts/ | 1 ms |
| ✅ PASS | `test_web_app_present` | web/app.py bestaat en bevat FastAPI app definitie | 0 ms |
| ✅ PASS | `test_web_dashboard_health` | FastAPI /health endpoint reageert met HTTP 200 en status 'ok' | 4 ms |
| ✅ PASS | `test_web_dashboard_root` | FastAPI dashboard geeft HTML terug met 'Medical RAG', 'Qdrant' en 'Ollama' | 666 ms |

---

## Mislukte tests — details

### `PipelineTests.test_pdf_text_extraction`

```
Traceback (most recent call last):
  File "/root/medical-rag/scripts/run_tests.py", line 402, in test_pdf_text_extraction
    result = converter.convert(str(pdf_path))
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/pydantic/_internal/_validate_call.py", line 40, in wrapper_function
    return wrapper(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/pydantic/_internal/_validate_call.py", line 137, in __call__
    res = self.__pydantic_validator__.validate_python(pydantic_core.ArgsKwargs(args, kwargs))
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/docling/document_converter.py", line 388, in convert
    return next(all_res)
           ^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/docling/document_converter.py", line 447, in convert_all
    for conv_res in conv_res_iter:
  File "/usr/local/lib/python3.12/dist-packages/docling/document_converter.py", line 564, in _convert
    for item in map(
  File "/usr/local/lib/python3.12/dist-packages/docling/document_converter.py", line 611, in _process_document
    conv_res = self._execute_pipeline(in_doc, raises_on_error=raises_on_error)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/docling/document_converter.py", line 632, in _execute_pipeline
    pipeline = self._get_pipeline(in_doc.format)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/docling/document_converter.py", line 594, in _get_pipeline
    self.initialized_pipelines[cache_key] = pipeline_class(
                                            ^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/docling/pipeline/standard_pdf_pipeline.py", line 467, in __init__
    self._init_models()
  File "/usr/local/lib/python3.12/dist-packages/docling/pipeline/standard_pdf_pipeline.py", line 498, in _init_models
    self.table_model = table_factory.create_instance(
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/docling/models/factories/base_factory.py", line 57, in create_instance
    return _cls(options=options, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/docling/models/stages/table_structure/table_structure_model.py", line 76, in __init__
    from docling_ibm_models.tableformer.data_management.tf_predictor import (
  File "/usr/local/lib/python3.12/dist-packages/docling_ibm_models/tableformer/data_management/tf_predictor.py", line 9, in <module>
    import cv2
ImportError: libGL.so.1: cannot open shared object file: No such file or directory
```

### `QualityTests.test_figure_detection`

```
Traceback (most recent call last):
  File "/root/medical-rag/scripts/run_tests.py", line 655, in test_figure_detection
    result = converter.convert(str(pdf_path))
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/pydantic/_internal/_validate_call.py", line 40, in wrapper_function
    return wrapper(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/pydantic/_internal/_validate_call.py", line 137, in __call__
    res = self.__pydantic_validator__.validate_python(pydantic_core.ArgsKwargs(args, kwargs))
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/docling/document_converter.py", line 388, in convert
    return next(all_res)
           ^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/docling/document_converter.py", line 447, in convert_all
    for conv_res in conv_res_iter:
  File "/usr/local/lib/python3.12/dist-packages/docling/document_converter.py", line 564, in _convert
    for item in map(
  File "/usr/local/lib/python3.12/dist-packages/docling/document_converter.py", line 611, in _process_document
    conv_res = self._execute_pipeline(in_doc, raises_on_error=raises_on_error)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/docling/document_converter.py", line 632, in _execute_pipeline
    pipeline = self._get_pipeline(in_doc.format)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/docling/document_converter.py", line 594, in _get_pipeline
    self.initialized_pipelines[cache_key] = pipeline_class(
                                            ^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/docling/pipeline/standard_pdf_pipeline.py", line 467, in __init__
    self._init_models()
  File "/usr/local/lib/python3.12/dist-packages/docling/pipeline/standard_pdf_pipeline.py", line 498, in _init_models
    self.table_model = table_factory.create_instance(
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/docling/models/factories/base_factory.py", line 57, in create_instance
    return _cls(options=options, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/docling/models/stages/table_structure/table_structure_model.py", line 76, in __init__
    from docling_ibm_models.tableformer.data_management.tf_predictor import (
  File "/usr/local/lib/python3.12/dist-packages/docling_ibm_models/tableformer/data_management/tf_predictor.py", line 9, in <module>
    import cv2
ImportError: libGL.so.1: cannot open shared object file: No such file or directory
```

---

## Aanbevelingen

- **Onderzoek `test_pdf_text_extraction`:** zie details hierboven
- **Onderzoek `test_figure_detection`:** zie details hierboven

---

*Gegenereerd door `scripts/run_tests.py`*