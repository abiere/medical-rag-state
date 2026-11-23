# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-11-23 00:38:41 UTC**

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
| RAM used | 4.72 GB / 32.86 GB (14%) |
| CPU | 11.3% |
| Disk used | 138.4 GB / 322.3 GB (45%) |
| Uptime | up 31 weeks, 2 days, 19 hours, 3 minutes |

## Recent markers
- `2026-11-23T00:30:33` **queue_empty** — All 13 videos transcribed
- `2026-11-23T00:30:33` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-11-23T00:30:33` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED
- `2026-11-23T00:30:33` **transcription_done** — NRT_Fascial_Activation_Application_Method.mp4 complete (55/13)
- `2026-11-23T00:30:33` **ingest_failed** — NRT_Fascial_Activation_Application_Method.mp4 ingest FAILED

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
2026-11-23 00:34:04,232  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-23 00:34:34,233  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-23 00:35:04,233  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-23 00:35:34,234  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-23 00:36:04,234  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-23 00:36:34,235  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-23 00:37:04,235  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-23 00:37:34,236  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-23 00:38:04,236  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-23 00:38:34,237  INFO      Queue paused (pause flag set) — waiting 30s
```
