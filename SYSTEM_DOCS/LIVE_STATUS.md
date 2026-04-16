# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 21:47:33 UTC**

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
| Current job | `03_trail_guide_to_the_body_6th.pdf` (361 min) |
| Queued | 4 |
| Total books | 43 |
| Ingested | 35 |
| Vectors in medical_library | 2773 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (1332 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 3.42 GB / 32.86 GB (10%) |
| CPU | 6.3% |
| Disk used | 59.2 GB / 322.3 GB (19%) |
| Uptime | up 2 days, 12 hours, 4 minutes |

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
2026-04-16 21:42:47,827  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:43:17,827  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:43:47,828  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:44:17,828  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:44:47,829  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:45:17,829  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:45:47,830  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:46:17,830  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:46:47,830  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:47:17,831  INFO      Queue paused (pause flag set) — waiting 30s
```
