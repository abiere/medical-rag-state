# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 19:57:31 UTC**

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
| Current job | `Advanced Seminar Manual- HS 08272022.pdf` (31 min) |
| Queued | 29 |
| Total books | 43 |
| Ingested | 10 |
| Vectors in medical_library | 2773 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (1222 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 11.35 GB / 32.86 GB (34%) |
| CPU | 44.2% |
| Disk used | 59.2 GB / 322.3 GB (19%) |
| Uptime | up 2 days, 10 hours, 14 minutes |

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
2026-04-16 19:52:47,710  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:53:17,711  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:53:47,712  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:54:17,712  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:54:47,713  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:55:17,714  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:55:47,714  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:56:17,715  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:56:47,715  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:57:17,716  INFO      Queue paused (pause flag set) — waiting 30s
```
