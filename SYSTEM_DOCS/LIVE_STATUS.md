# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-08-05 00:39:17 UTC**

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
| RAM used | 7.09 GB / 32.86 GB (22%) |
| CPU | 0.4% |
| Disk used | 93.5 GB / 322.3 GB (30%) |
| Uptime | up 15 weeks, 4 days, 19 hours, 3 minutes |

## Recent markers
- `2026-08-05T00:30:25` **queue_empty** — All 13 videos transcribed
- `2026-08-05T00:30:25` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-08-05T00:30:24` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED
- `2026-08-05T00:30:24` **transcription_done** — NRT_Fascial_Activation_Application_Method.mp4 complete (55/13)
- `2026-08-05T00:30:24` **ingest_failed** — NRT_Fascial_Activation_Application_Method.mp4 ingest FAILED

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
2026-08-05 00:34:25,478  INFO      Queue paused (pause flag set) — waiting 30s
2026-08-05 00:34:55,478  INFO      Queue paused (pause flag set) — waiting 30s
2026-08-05 00:35:25,479  INFO      Queue paused (pause flag set) — waiting 30s
2026-08-05 00:35:55,479  INFO      Queue paused (pause flag set) — waiting 30s
2026-08-05 00:36:25,479  INFO      Queue paused (pause flag set) — waiting 30s
2026-08-05 00:36:55,480  INFO      Queue paused (pause flag set) — waiting 30s
2026-08-05 00:37:25,480  INFO      Queue paused (pause flag set) — waiting 30s
2026-08-05 00:37:55,481  INFO      Queue paused (pause flag set) — waiting 30s
2026-08-05 00:38:25,481  INFO      Queue paused (pause flag set) — waiting 30s
2026-08-05 00:38:55,481  INFO      Queue paused (pause flag set) — waiting 30s
```
