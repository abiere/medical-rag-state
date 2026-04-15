# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-15 10:09:34 UTC**

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
| Ingested | 1 |
| Queued | 0 |
| Current job | idle |

## Transcription
| Metric | Value |
|---|---|
| Current job | `Neurological_Disorganization.mp4` (since 2026-04-15T10:06:21) |
| Queued | 6 |
| Done | 9 |
| Total videos | 15 |

## System
| Metric | Value |
|---|---|
| RAM used | 11.87 GB / 32.86 GB (36%) |
| CPU | 96.6% |
| Disk used | 39.7 GB / 322.3 GB (13%) |
| Uptime | up 1 day, 26 minutes |

## Recent markers
- `2026-04-15T10:08:53.430330+00:00` **book_ingested** — test_acupuncture.pdf → acupuncture_points: 2 chunks, score 5.00
- `2026-04-15T10:06:21` **transcription_done** — Meridian_Testing_and_Treatment.mp4 complete (9/15)
- `2026-04-15T09:58:31` **transcription_done** — Manual_Muscle_Testing_3.mp4 complete (8/15)
- `2026-04-15T09:50:30` **transcription_done** — Manual_Muscle_Testing_2.mp4 complete (7/15)
- `2026-04-15T09:30:04` **transcription_done** — Manual_Muscle_Testing_1.mp4 complete (6/15)

## Queue log (last 10 lines)
```
2026-04-15 09:14:45,581  INFO      DONE   qat/Locating_Acupuncture_Points.mp4  (2282s)
2026-04-15 09:14:45,648  INFO      START  qat/Manual_Muscle_Testing_1.mp4
2026-04-15 09:30:04,393  INFO      DONE   qat/Manual_Muscle_Testing_1.mp4  (919s)
2026-04-15 09:30:04,462  INFO      START  qat/Manual_Muscle_Testing_2.mp4
2026-04-15 09:50:30,177  INFO      DONE   qat/Manual_Muscle_Testing_2.mp4  (1226s)
2026-04-15 09:50:30,295  INFO      START  qat/Manual_Muscle_Testing_3.mp4
2026-04-15 09:58:31,807  INFO      DONE   qat/Manual_Muscle_Testing_3.mp4  (482s)
2026-04-15 09:58:31,925  INFO      START  qat/Meridian_Testing_and_Treatment.mp4
2026-04-15 10:06:21,409  INFO      DONE   qat/Meridian_Testing_and_Treatment.mp4  (469s)
2026-04-15 10:06:21,476  INFO      START  qat/Neurological_Disorganization.mp4
```
