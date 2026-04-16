# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 19:22:30 UTC**

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
| Current job | `How to Reset 23 More Muscles - Times.pdf` |
| Queued | 31 |
| Total books | 43 |
| Ingested | 8 |
| Vectors in medical_library | 2773 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (1187 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 11.27 GB / 32.86 GB (34%) |
| CPU | 50.1% |
| Disk used | 59.1 GB / 322.3 GB (19%) |
| Uptime | up 2 days, 9 hours, 39 minutes |

## Recent markers
- `2026-04-16T19:22:20.206039+00:00` **book_ingested** — Miraculous Sequence - Times.pdf → nrt_qat_curriculum: 1 chunks
- `2026-04-16T19:21:16.476708+00:00` **book_ingested** — NRT Upper Body.pdf → nrt_qat_curriculum: 157 chunks
- `2026-04-16T18:57:31.237178+00:00` **book_ingested** — NRT Lower Body.pdf → nrt_qat_curriculum: 132 chunks
- `2026-04-16T18:23:07.585962+00:00` **book_ingested** — The QAT Life Pendant eu.pdf → nrt_qat_curriculum: 2 chunks
- `2026-04-16T18:20:33.462183+00:00` **book_ingested** — The QAT Connect to the Brain eu.pdf → nrt_qat_curriculum: 2 chunks

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
2026-04-16 19:17:47,667  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:18:17,667  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:18:47,668  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:19:17,668  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:19:47,671  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:20:17,671  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:20:47,672  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:21:17,672  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:21:47,673  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:22:17,674  INFO      Queue paused (pause flag set) — waiting 30s
```
