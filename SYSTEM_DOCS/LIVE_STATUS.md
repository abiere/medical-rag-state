# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 20:02:31 UTC**

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
| Current job | `Advanced Seminar Manual- HS 08272022.pdf` (36 min) |
| Queued | 29 |
| Total books | 43 |
| Ingested | 10 |
| Vectors in medical_library | 2773 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (1227 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 11.42 GB / 32.86 GB (35%) |
| CPU | 43.7% |
| Disk used | 59.2 GB / 322.3 GB (19%) |
| Uptime | up 2 days, 10 hours, 19 minutes |

## Recent markers
- `2026-04-16T19:25:49.404384+00:00` **book_ingested** — Everything Reset Sequence - Times.pdf → nrt_qat_curriculum: 2 chunks
- `2026-04-16T19:23:22.619831+00:00` **book_ingested** — How to Reset 23 More Muscles - Times.pdf → nrt_qat_curriculum: 1 chunks
- `2026-04-16T19:22:20.206039+00:00` **book_ingested** — Miraculous Sequence - Times.pdf → nrt_qat_curriculum: 1 chunks
- `2026-04-16T19:21:16.476708+00:00` **book_ingested** — NRT Upper Body.pdf → nrt_qat_curriculum: 157 chunks
- `2026-04-16T18:57:31.237178+00:00` **book_ingested** — NRT Lower Body.pdf → nrt_qat_curriculum: 132 chunks

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
2026-04-16 19:57:47,716  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:58:17,717  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:58:47,717  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:59:17,718  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:59:47,718  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:00:17,719  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:00:47,719  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:01:17,720  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:01:47,720  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:02:17,721  INFO      Queue paused (pause flag set) — waiting 30s
```
