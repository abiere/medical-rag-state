# Test Report

## Status: No tests yet

No automated tests have been written. This file is a placeholder.

## Planned test areas

| Area | Type | Notes |
|---|---|---|
| Ingestion pipeline | Integration | Ingest a known PDF; assert expected chunk count, payload fields, and image extraction |
| Embedding | Unit | Assert embedding vector dimension = 1024 |
| Qdrant round-trip | Integration | Insert a vector, query by similarity, assert retrieval |
| Ollama inference | Integration | Send a prompt, assert non-empty response |
| FastAPI endpoints | Integration | Upload, ingest, query, generate — once the web layer exists |
| Citation integrity | Unit | Assert every generated output only cites chunks that were retrieved |
| Idempotency | Integration | Run ingestion twice on the same file; assert Qdrant point count unchanged |

## Known manual tests performed

- Qdrant container healthcheck: confirmed `Up, healthy` via `docker ps`
- Ollama API: confirmed `llama3.1:8b` listed via `GET /api/tags`
- State HTTP server: confirmed `200 OK` on `http://localhost:8080/PROJECT_STATE.md`

---

*Update this file when tests are written or manual test results change.*
