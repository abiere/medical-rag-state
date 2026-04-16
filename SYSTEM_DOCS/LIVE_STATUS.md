# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 22:07:33 UTC**

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
| Current job | `03_trail_guide_to_the_body_6th.pdf` (381 min) |
| Queued | 4 |
| Total books | 43 |
| Ingested | 35 |
| Vectors in medical_library | 2773 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (1352 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 3.32 GB / 32.86 GB (10%) |
| CPU | 12.9% |
| Disk used | 59.2 GB / 322.3 GB (19%) |
| Uptime | up 2 days, 12 hours, 24 minutes |

## Recent markers
- `2026-04-16T21:35:10.096134+00:00` **book_ingested** — NRT UB Techniques and Fundamentals - Times.pdf → device_documentation: 2 chunks
- `2026-04-16T21:33:03.579644+00:00` **book_ingested** — NRT LB Techniques and Fundamentals - Times.pdf → device_documentation: 2 chunks
- `2026-04-16T21:30:47.966575+00:00` **book_ingested** — how-flexbeam-works-for-your-body.pdf → device_documentation: 44 chunks
- `2026-04-16T21:24:50.376075+00:00` **book_ingested** — Why FlexBeam - Recharge Health.pdf → device_documentation: 18 chunks
- `2026-04-16T21:16:11.722420+00:00` **book_ingested** — How FlexBeam Works Using Red Light Therapy Principles – Recharge.pdf → device_documentation: 4 chunks

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
2026-04-16 22:02:47,846  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 22:03:17,846  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 22:03:47,847  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 22:04:17,847  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 22:04:47,848  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 22:05:17,849  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 22:05:47,849  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 22:06:17,850  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 22:06:47,850  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 22:07:17,850  INFO      Queue paused (pause flag set) — waiting 30s
```
