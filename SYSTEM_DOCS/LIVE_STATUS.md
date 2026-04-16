# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 20:11:30 UTC**

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
| Current job | `Warnings and Cautions - Recharge Health.pdf` |
| Queued | 26 |
| Total books | 43 |
| Ingested | 13 |
| Vectors in medical_library | 2773 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (1236 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 11.35 GB / 32.86 GB (35%) |
| CPU | 43.2% |
| Disk used | 59.2 GB / 322.3 GB (19%) |
| Uptime | up 2 days, 10 hours, 28 minutes |

## Recent markers
- `2026-04-16T20:10:33.574002+00:00` **book_ingested** — FlexBeam_RLT_Documentation.pdf → device_documentation: 4 chunks
- `2026-04-16T20:06:50.533703+00:00` **book_ingested** — 16 Expanded Revised and New Techniques - Times.pdf → nrt_qat_curriculum: 2 chunks
- `2026-04-16T20:04:54.651154+00:00` **book_ingested** — Advanced Seminar Manual- HS 08272022.pdf → nrt_qat_curriculum: 126 chunks
- `2026-04-16T19:25:49.404384+00:00` **book_ingested** — Everything Reset Sequence - Times.pdf → nrt_qat_curriculum: 2 chunks
- `2026-04-16T19:23:22.619831+00:00` **book_ingested** — How to Reset 23 More Muscles - Times.pdf → nrt_qat_curriculum: 1 chunks

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
2026-04-16 20:06:47,728  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:07:17,728  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:07:47,729  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:08:17,729  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:08:47,730  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:09:17,730  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:09:47,731  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:10:17,731  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:10:47,732  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:11:17,732  INFO      Queue paused (pause flag set) — waiting 30s
```
