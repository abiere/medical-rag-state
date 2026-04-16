# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 20:37:32 UTC**

## Services
| Service | Status |
|---|---|
| medical-rag-web | ✅ active |
| transcription-queue | ✅ active |
| book-ingest-queue | ✅ active |
| ttyd | ✅ active |
| qdrant | ✅ healthy |
| ollama | ✅ healthy |

## Book Ingest
| Metric | Value |
|---|---|
| Current job | `How to Use FlexBeam to Boost Your Immunity - Recharge Health.pdf` (1 min) |
| Queued | 14 |
| Total books | 43 |
| Ingested | 21 |
| Vectors in medical_library | 2773 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (1262 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 11.4 GB / 32.86 GB (35%) |
| CPU | 37.7% |
| Disk used | 59.2 GB / 322.3 GB (19%) |
| Uptime | up 2 days, 10 hours, 54 minutes |

## Recent markers
- `2026-04-16T20:36:17.167114+00:00` **book_ingested** — How to Use FlexBeam on Lower Back - Recharge Health.pdf → device_documentation: 3 chunks
- `2026-04-16T20:33:52.303979+00:00` **book_ingested** — How to Use FlexBeam on Shoulders - Recharge Health.pdf → device_documentation: 5 chunks
- `2026-04-16T20:30:20.867026+00:00` **book_ingested** — How to Use FlexBeam on Elbows - Recharge Health.pdf → device_documentation: 3 chunks
- `2026-04-16T20:26:05.262116+00:00` **book_ingested** — How to Use FlexBeam on Hips - Recharge Health.pdf → device_documentation: 3 chunks
- `2026-04-16T20:23:19.672366+00:00` **book_ingested** — How to Use FlexBeam on Feet and Ankles - Recharge Health.pdf → device_documentation: 4 chunks

## Nightly Consistency
```
  TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_2.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Organs_and_Glands_Review.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Pair_Balancing.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Neuromuscular_ReEducation.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_3.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Anti-Inflammatory_Procedure.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_1.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Indicator_Muscle.json (type: qat)
```

## Queue log (last 10 lines)
```
2026-04-16 20:32:47,754  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:33:17,755  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:33:47,755  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:34:17,756  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:34:47,757  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:35:17,758  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:35:47,758  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:36:17,759  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:36:47,759  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:37:17,760  INFO      Queue paused (pause flag set) — waiting 30s
```
