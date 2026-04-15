# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-15 11:43:04 UTC**

## Services
| Service | Status |
|---|---|
| medical-rag-web | ✅ active |
| transcription-queue | ❌ inactive |
| book-ingest-queue | ❌ inactive |
| ttyd | ✅ active |
| qdrant | ✅ healthy |
| ollama | ✅ healthy |

## Library
| Metric | Value |
|---|---|
| Total books | 1 |
| Ingested | 1 |
| Queued | 0 |
| Current job | idle |
| Images pending approval | 0 |
| Images approved | 0 |

## Transcription
| Metric | Value |
|---|---|
| Current job | idle |
| Queued | 0 |
| Done | 15 |
| Total videos | 15 |

## System
| Metric | Value |
|---|---|
| RAM used | 1.51 GB / 32.86 GB (5%) |
| CPU | 0.0% |
| Disk used | 39.7 GB / 322.3 GB (13%) |
| Uptime | up 1 day, 2 hours, 0 minutes |

## Recent markers
- `2026-04-15T11:28:04` **queue_empty** — All 15 videos transcribed
- `2026-04-15T11:28:04` **transcription_done** — Anti-Inflammatory_Procedure.mp4 complete (15/15)
- `2026-04-15T11:20:11` **transcription_done** — Provocative_Testing.mp4 complete (14/15)
- `2026-04-15T11:11:43` **transcription_done** — Pair_Balancing.mp4 complete (13/15)
- `2026-04-15T10:59:40` **transcription_done** — Organs_and_Glands_Review.mp4 complete (12/15)

## Queue log (last 10 lines)
```
2026-04-15 10:40:45,721  INFO      START  qat/Organs_and_Glands_Review.mp4
2026-04-15 10:59:40,181  INFO      DONE   qat/Organs_and_Glands_Review.mp4  (1134s)
2026-04-15 10:59:40,298  INFO      START  qat/Pair_Balancing.mp4
2026-04-15 11:11:43,880  INFO      DONE   qat/Pair_Balancing.mp4  (724s)
2026-04-15 11:11:44,008  INFO      START  qat/Provocative_Testing.mp4
2026-04-15 11:20:11,143  INFO      DONE   qat/Provocative_Testing.mp4  (507s)
2026-04-15 11:20:11,261  INFO      START  qat/Anti-Inflammatory_Procedure.mp4
2026-04-15 11:28:04,345  INFO      DONE   qat/Anti-Inflammatory_Procedure.mp4  (473s)
2026-04-15 11:28:04,513  INFO      Queue empty — 15 video(s) processed. Exiting.
2026-04-15 11:28:04,629  INFO      Transcription queue manager done
```
