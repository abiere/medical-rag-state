# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-15 11:26:54 UTC**

## Services
| Service | Status |
|---|---|
| medical-rag-web | ✅ active |
| transcription-queue | ✅ active |
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
| Current job | `Anti-Inflammatory_Procedure.mp4` (since 2026-04-15T11:20:11) |
| Queued | 1 |
| Done | 14 |
| Total videos | 15 |

## System
| Metric | Value |
|---|---|
| RAM used | 5.6 GB / 32.86 GB (17%) |
| CPU | 92.9% |
| Disk used | 39.7 GB / 322.3 GB (13%) |
| Uptime | up 1 day, 1 hour, 44 minutes |

## Recent markers
- `2026-04-15T11:20:11` **transcription_done** — Provocative_Testing.mp4 complete (14/15)
- `2026-04-15T11:11:43` **transcription_done** — Pair_Balancing.mp4 complete (13/15)
- `2026-04-15T10:59:40` **transcription_done** — Organs_and_Glands_Review.mp4 complete (12/15)
- `2026-04-15T10:40:45` **transcription_done** — Neuromuscular_ReEducation.mp4 complete (11/15)
- `2026-04-15T10:32:36` **transcription_done** — Neurological_Disorganization.mp4 complete (10/15)

## Queue log (last 10 lines)
```
2026-04-15 10:32:35,993  INFO      DONE   qat/Neurological_Disorganization.mp4  (1575s)
2026-04-15 10:32:36,113  INFO      START  qat/Neuromuscular_ReEducation.mp4
2026-04-15 10:40:45,601  INFO      DONE   qat/Neuromuscular_ReEducation.mp4  (489s)
2026-04-15 10:40:45,721  INFO      START  qat/Organs_and_Glands_Review.mp4
2026-04-15 10:59:40,181  INFO      DONE   qat/Organs_and_Glands_Review.mp4  (1134s)
2026-04-15 10:59:40,298  INFO      START  qat/Pair_Balancing.mp4
2026-04-15 11:11:43,880  INFO      DONE   qat/Pair_Balancing.mp4  (724s)
2026-04-15 11:11:44,008  INFO      START  qat/Provocative_Testing.mp4
2026-04-15 11:20:11,143  INFO      DONE   qat/Provocative_Testing.mp4  (507s)
2026-04-15 11:20:11,261  INFO      START  qat/Anti-Inflammatory_Procedure.mp4
```
