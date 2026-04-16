# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 20:42:32 UTC**

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
| Current job | `How to Use FlexBeam to Improve Your Breathing - Recharge Health.pdf` (3 min) |
| Queued | 13 |
| Total books | 43 |
| Ingested | 22 |
| Vectors in medical_library | 2773 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (1267 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 10.83 GB / 32.86 GB (33%) |
| CPU | 43.7% |
| Disk used | 59.2 GB / 322.3 GB (19%) |
| Uptime | up 2 days, 10 hours, 59 minutes |

## Recent markers
- `2026-04-16T20:39:27.855853+00:00` **book_ingested** — How to Use FlexBeam to Boost Your Immunity - Recharge Health.pdf → device_documentation: 4 chunks
- `2026-04-16T20:36:17.167114+00:00` **book_ingested** — How to Use FlexBeam on Lower Back - Recharge Health.pdf → device_documentation: 3 chunks
- `2026-04-16T20:33:52.303979+00:00` **book_ingested** — How to Use FlexBeam on Shoulders - Recharge Health.pdf → device_documentation: 5 chunks
- `2026-04-16T20:30:20.867026+00:00` **book_ingested** — How to Use FlexBeam on Elbows - Recharge Health.pdf → device_documentation: 3 chunks
- `2026-04-16T20:26:05.262116+00:00` **book_ingested** — How to Use FlexBeam on Hips - Recharge Health.pdf → device_documentation: 3 chunks

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
2026-04-16 20:37:47,760  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:38:17,761  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:38:47,761  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:39:17,762  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:39:47,762  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:40:17,763  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:40:47,764  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:41:17,764  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:41:47,764  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:42:17,765  INFO      Queue paused (pause flag set) — waiting 30s
```
