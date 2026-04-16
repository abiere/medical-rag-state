# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 20:57:32 UTC**

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
| Current job | `White-Paper-FlexBeam-Targeted-Red-Light-Device.pdf` (6 min) |
| Queued | 9 |
| Total books | 43 |
| Ingested | 26 |
| Vectors in medical_library | 2773 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (1282 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 10.82 GB / 32.86 GB (33%) |
| CPU | 48.0% |
| Disk used | 59.2 GB / 322.3 GB (19%) |
| Uptime | up 2 days, 11 hours, 14 minutes |

## Recent markers
- `2026-04-16T20:51:14.422569+00:00` **book_ingested** — FlexBeam Applications and Usage Guide - Recharge Health.pdf → device_documentation: 3 chunks
- `2026-04-16T20:48:22.205435+00:00` **book_ingested** — How to Use FlexBeam to Boost Your Energy - Recharge Health.pdf → device_documentation: 4 chunks
- `2026-04-16T20:45:44.656419+00:00` **book_ingested** — How to Use FlexBeam to Sleep Better - Recharge Health.pdf → device_documentation: 4 chunks
- `2026-04-16T20:42:40.524444+00:00` **book_ingested** — How to Use FlexBeam to Improve Your Breathing - Recharge Health.pdf → device_documentation: 4 chunks
- `2026-04-16T20:39:27.855853+00:00` **book_ingested** — How to Use FlexBeam to Boost Your Immunity - Recharge Health.pdf → device_documentation: 4 chunks

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
2026-04-16 20:52:47,776  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:53:17,776  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:53:47,776  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:54:17,777  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:54:47,777  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:55:17,778  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:55:47,778  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:56:17,779  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:56:47,779  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:57:17,780  INFO      Queue paused (pause flag set) — waiting 30s
```
