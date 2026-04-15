# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-15 09:28:54 UTC**

## Services
| Service | Status |
|---|---|
| medical-rag-web | ✅ active |
| transcription-queue | ✅ active |
| book-ingest-queue | ❌ inactive |
| ttyd | ✅ active |
| qdrant | ✅ healthy |
| ollama | ✅ healthy |

## Books
| Metric | Value |
|---|---|
| Total books | 1 |
| Ingested | 0 |
| Queued | 0 |
| Current job | idle |

## Transcription
| Metric | Value |
|---|---|
| Current job | `Manual_Muscle_Testing_1.mp4` (since 2026-04-15T09:14:45) |
| Queued | 10 |
| Done | 5 |
| Total videos | 15 |

## System
| Metric | Value |
|---|---|
| RAM used | 5.52 GB / 32.86 GB (17%) |
| CPU | 93.7% |
| Disk used | 47.3 GB / 322.3 GB (15%) |
| Uptime | up 23 hours, 46 minutes |

## Recent markers
- `2026-04-15T09:14:45` **transcription_done** — Locating_Acupuncture_Points.mp4 complete (5/15)
- `2026-04-15T08:36:43` **transcription_done** — Indicator_Muscle.mp4 complete (4/15)
- `2026-04-15T08:15:42` **transcription_done** — Green_Square_Applications.mp4 complete (3/15)
- `2026-04-15T07:59:06` **transcription_done** — Emotional_Transformation_Technique.mp4 complete (2/15)
- `2026-04-15T07:34:21` **transcription_done** — Connection_to_the_Brain.mp4 complete (1/15)

## Queue log (last 10 lines)
```
2026-04-15 07:34:21,154  INFO      DONE   qat/Connection_to_the_Brain.mp4  (919s)
2026-04-15 07:34:21,276  INFO      START  qat/Emotional_Transformation_Technique.mp4
2026-04-15 07:59:06,987  INFO      DONE   qat/Emotional_Transformation_Technique.mp4  (1486s)
2026-04-15 07:59:07,054  INFO      START  qat/Green_Square_Applications.mp4
2026-04-15 08:15:42,851  INFO      DONE   qat/Green_Square_Applications.mp4  (996s)
2026-04-15 08:15:42,917  INFO      START  qat/Indicator_Muscle.mp4
2026-04-15 08:36:43,049  INFO      DONE   qat/Indicator_Muscle.mp4  (1260s)
2026-04-15 08:36:43,166  INFO      START  qat/Locating_Acupuncture_Points.mp4
2026-04-15 09:14:45,581  INFO      DONE   qat/Locating_Acupuncture_Points.mp4  (2282s)
2026-04-15 09:14:45,648  INFO      START  qat/Manual_Muscle_Testing_1.mp4
```
