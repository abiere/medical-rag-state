# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 21:32:33 UTC**

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
| Current job | `NRT LB Techniques and Fundamentals - Times.pdf` (1 min) |
| Queued | 1 |
| Total books | 43 |
| Ingested | 33 |
| Vectors in medical_library | 2773 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (1317 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 10.83 GB / 32.86 GB (33%) |
| CPU | 42.4% |
| Disk used | 59.2 GB / 322.3 GB (19%) |
| Uptime | up 2 days, 11 hours, 49 minutes |

## Recent markers
- `2026-04-16T21:30:47.966575+00:00` **book_ingested** — how-flexbeam-works-for-your-body.pdf → device_documentation: 44 chunks
- `2026-04-16T21:24:50.376075+00:00` **book_ingested** — Why FlexBeam - Recharge Health.pdf → device_documentation: 18 chunks
- `2026-04-16T21:16:11.722420+00:00` **book_ingested** — How FlexBeam Works Using Red Light Therapy Principles – Recharge.pdf → device_documentation: 4 chunks
- `2026-04-16T21:13:30.558886+00:00` **book_ingested** — How Does Red Light Therapy Work_ – Recharge.pdf → device_documentation: 7 chunks
- `2026-04-16T21:09:23.539781+00:00` **book_ingested** — Warnings and Cautions – Recharge.pdf → device_documentation: 4 chunks

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
2026-04-16 21:27:47,811  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:28:17,812  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:28:47,812  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:29:17,813  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:29:47,813  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:30:17,814  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:30:47,814  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:31:17,815  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:31:47,816  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:32:17,816  INFO      Queue paused (pause flag set) — waiting 30s
```
