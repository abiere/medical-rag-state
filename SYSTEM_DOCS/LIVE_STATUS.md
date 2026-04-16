# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 20:22:31 UTC**

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
| Current job | `How to Use FlexBeam on Feet and Ankles - Recharge Health.pdf` (1 min) |
| Queued | 22 |
| Total books | 43 |
| Ingested | 17 |
| Vectors in medical_library | 2773 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (1247 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 11.36 GB / 32.86 GB (35%) |
| CPU | 29.6% |
| Disk used | 59.2 GB / 322.3 GB (19%) |
| Uptime | up 2 days, 10 hours, 39 minutes |

## Recent markers
- `2026-04-16T20:20:35.315692+00:00` **book_ingested** — How to Use FlexBeam on Skin and Scars - Recharge Health.pdf → device_documentation: 3 chunks
- `2026-04-16T20:17:41.183791+00:00` **book_ingested** — How to Use FlexBeam for Menstrual Cramps - Recharge Health.pdf → device_documentation: 2 chunks
- `2026-04-16T20:15:41.794726+00:00` **book_ingested** — How to Use FlexBeam to Help Relieve Anxiety - Recharge Health.pdf → device_documentation: 4 chunks
- `2026-04-16T20:12:37.082591+00:00` **book_ingested** — Warnings and Cautions - Recharge Health.pdf → device_documentation: 3 chunks
- `2026-04-16T20:10:33.574002+00:00` **book_ingested** — FlexBeam_RLT_Documentation.pdf → device_documentation: 4 chunks

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
2026-04-16 20:17:47,739  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:18:17,740  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:18:47,740  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:19:17,741  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:19:47,741  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:20:17,742  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:20:47,742  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:21:17,743  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:21:47,744  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 20:22:17,744  INFO      Queue paused (pause flag set) — waiting 30s
```
