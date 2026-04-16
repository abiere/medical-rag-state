# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 21:12:32 UTC**

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
| Current job | `How Does Red Light Therapy Work_ – Recharge.pdf` (3 min) |
| Queued | 6 |
| Total books | 43 |
| Ingested | 29 |
| Vectors in medical_library | 2773 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (1297 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 10.84 GB / 32.86 GB (33%) |
| CPU | 50.0% |
| Disk used | 59.2 GB / 322.3 GB (19%) |
| Uptime | up 2 days, 11 hours, 29 minutes |

## Recent markers
- `2026-04-16T21:09:23.539781+00:00` **book_ingested** — Warnings and Cautions – Recharge.pdf → device_documentation: 4 chunks
- `2026-04-16T21:06:21.007703+00:00` **book_ingested** — flexbeam-wellness-ifu-2024-v2-19.pdf → device_documentation: 14 chunks
- `2026-04-16T20:58:04.937409+00:00` **book_ingested** — White-Paper-FlexBeam-Targeted-Red-Light-Device.pdf → device_documentation: 16 chunks
- `2026-04-16T20:51:14.422569+00:00` **book_ingested** — FlexBeam Applications and Usage Guide - Recharge Health.pdf → device_documentation: 3 chunks
- `2026-04-16T20:48:22.205435+00:00` **book_ingested** — How to Use FlexBeam to Boost Your Energy - Recharge Health.pdf → device_documentation: 4 chunks

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
2026-04-16 21:07:47,791  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:08:17,791  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:08:47,791  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:09:17,792  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:09:47,793  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:10:17,793  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:10:47,793  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:11:17,794  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:11:47,795  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:12:17,795  INFO      Queue paused (pause flag set) — waiting 30s
```
