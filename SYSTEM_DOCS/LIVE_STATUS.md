# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 21:17:32 UTC**

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
| Current job | `Why FlexBeam - Recharge Health.pdf` (1 min) |
| Queued | 4 |
| Total books | 43 |
| Ingested | 31 |
| Vectors in medical_library | 2773 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (1302 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 10.82 GB / 32.86 GB (33%) |
| CPU | 40.8% |
| Disk used | 59.2 GB / 322.3 GB (19%) |
| Uptime | up 2 days, 11 hours, 34 minutes |

## Recent markers
- `2026-04-16T21:16:11.722420+00:00` **book_ingested** — How FlexBeam Works Using Red Light Therapy Principles – Recharge.pdf → device_documentation: 4 chunks
- `2026-04-16T21:13:30.558886+00:00` **book_ingested** — How Does Red Light Therapy Work_ – Recharge.pdf → device_documentation: 7 chunks
- `2026-04-16T21:09:23.539781+00:00` **book_ingested** — Warnings and Cautions – Recharge.pdf → device_documentation: 4 chunks
- `2026-04-16T21:06:21.007703+00:00` **book_ingested** — flexbeam-wellness-ifu-2024-v2-19.pdf → device_documentation: 14 chunks
- `2026-04-16T20:58:04.937409+00:00` **book_ingested** — White-Paper-FlexBeam-Targeted-Red-Light-Device.pdf → device_documentation: 16 chunks

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
2026-04-16 21:12:47,796  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:13:17,796  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:13:47,797  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:14:17,798  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:14:47,798  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:15:17,799  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:15:47,799  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:16:17,800  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:16:47,800  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 21:17:17,801  INFO      Queue paused (pause flag set) — waiting 30s
```
