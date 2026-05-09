# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-05-09 00:42:33 UTC**

## Services
| Service | Status |
|---|---|
| medical-rag-web | ✅ active |
| transcription-queue | ✅ active |
| book-ingest-queue | ❌ inactive |
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
| RAM used | 11.89 GB / 32.86 GB (36%) |
| CPU | 0.4% |
| Disk used | 90.7 GB / 322.3 GB (29%) |
| Uptime | up 3 weeks, 19 hours, 7 minutes |

## Recent markers
- `2026-05-09T00:30:34` **queue_empty** — All 13 videos transcribed
- `2026-05-09T00:30:34` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-05-09T00:30:34` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED
- `2026-05-09T00:30:34` **transcription_done** — NRT_Fascial_Activation_Application_Method.mp4 complete (55/13)
- `2026-05-09T00:30:34` **ingest_failed** — NRT_Fascial_Activation_Application_Method.mp4 ingest FAILED

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
2026-05-09 00:37:34,719  INFO      Queue paused (pause flag set) — waiting 30s
2026-05-09 00:38:04,719  INFO      Queue paused (pause flag set) — waiting 30s
2026-05-09 00:38:34,720  INFO      Queue paused (pause flag set) — waiting 30s
2026-05-09 00:39:04,720  INFO      Queue paused (pause flag set) — waiting 30s
2026-05-09 00:39:34,720  INFO      Queue paused (pause flag set) — waiting 30s
2026-05-09 00:40:04,721  INFO      Queue paused (pause flag set) — waiting 30s
2026-05-09 00:40:34,721  INFO      Queue paused (pause flag set) — waiting 30s
2026-05-09 00:41:04,722  INFO      Queue paused (pause flag set) — waiting 30s
2026-05-09 00:41:34,722  INFO      Queue paused (pause flag set) — waiting 30s
2026-05-09 00:42:04,723  INFO      Queue paused (pause flag set) — waiting 30s
```
