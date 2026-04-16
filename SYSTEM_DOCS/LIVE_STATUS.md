# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 21:02:32 UTC**

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
| Current job | `flexbeam-wellness-ifu-2024-v2-19.pdf` (4 min) |
| Queued | 8 |
| Total books | 43 |
| Ingested | 27 |
| Vectors in medical_library | 2773 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (1287 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 10.83 GB / 32.86 GB (33%) |
| CPU | 44.5% |
| Disk used | 59.2 GB / 322.3 GB (19%) |
| Uptime | up 2 days, 11 hours, 19 minutes |

## Recent markers
- `2026-04-16T20:58:04.937409+00:00` **book_ingested** — White-Paper-FlexBeam-Targeted-Red-Light-Device.pdf → device_documentation: 16 chunks
- `2026-04-16T20:51:14.422569+00:00` **book_ingested** — FlexBeam Applications and Usage Guide - Recharge Health.pdf → device_documentation: 3 chunks
- `2026-04-16T20:48:22.205435+00:00` **book_ingested** — How to Use FlexBeam to Boost Your Energy - Recharge Health.pdf → device_documentation: 4 chunks
- `2026-04-16T20:45:44.656419+00:00` **book_ingested** — How to Use FlexBeam to Sleep Better - Recharge Health.pdf → device_documentation: 4 chunks
- `2026-04-16T20:42:40.524444+00:00` **book_ingested** — How to Use FlexBeam to Improve Your Breathing - Recharge Health.pdf → device_documentation: 4 chunks

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
2026-04-16 20:57:47,780  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:58:17,781  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:58:47,781  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:59:17,782  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:59:47,782  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:00:17,783  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:00:47,783  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:01:17,784  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:01:47,784  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:02:17,785  INFO      Queue paused (pause flag set) — waiting 30s
```
