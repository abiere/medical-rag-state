# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-06-28 00:36:29 UTC**

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
| Current job | idle |
| Queued | 0 |
| Total books | 34 |
| Ingested | 74 |
| Vectors in medical_library | 17522 |
| Images pending approval | 2026 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | idle |
| Queued | 13 |
| Done | 55 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 9.07 GB / 32.86 GB (28%) |
| CPU | 27.0% |
| Disk used | 92.3 GB / 322.3 GB (30%) |
| Uptime | up 10 weeks, 1 day, 19 hours, 1 minute |

## Recent markers
- `2026-06-28T00:30:28` **queue_empty** — All 13 videos transcribed
- `2026-06-28T00:30:28` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-06-28T00:30:28` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED
- `2026-06-28T00:30:27` **transcription_done** — NRT_Fascial_Activation_Application_Method.mp4 complete (55/13)
- `2026-06-28T00:30:27` **ingest_failed** — NRT_Fascial_Activation_Application_Method.mp4 ingest FAILED

## Nightly Consistency
```
  TRANSCRIPT ONTBREEKT IN QDRANT: 1.Upper_Body_Techniques_part002.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_1.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Everything_Reset_Sequence_-_Part_4_part001.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Indicator_Muscle.json (type: qat)
  BOEK ONTBREEKT IN QDRANT: test_acupuncture.pdf (collectie: medical_library)
  BOEK ONTBREEKT IN QDRANT: Orthopedic Physical Assessment_nodrm.epub (collectie: medical_library)
  BOEK ONTBREEKT IN QDRANT: Touch for Health_ The Complete Edition_ A Practical Guide to Natural Health With Acupressure Touch_nodrm.pdf (collectie: medical_library)
  BOEK ONTBREEKT IN QDRANT: Bates Guide to Physical Examination 14e editie - Bickley.epub (collectie: medical_library)
```

## Queue log (last 10 lines)
```
2026-06-28 00:31:58,460  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-28 00:32:28,460  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-28 00:32:58,461  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-28 00:33:28,461  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-28 00:33:58,462  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-28 00:34:28,462  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-28 00:34:58,463  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-28 00:35:28,463  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-28 00:35:58,463  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-28 00:36:28,464  INFO      Queue paused (pause flag set) — waiting 30s
```
