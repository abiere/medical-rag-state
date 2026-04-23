# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-23 00:34:36 UTC**

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
| RAM used | 3.69 GB / 32.86 GB (11%) |
| CPU | 6.8% |
| Disk used | 87.2 GB / 322.3 GB (28%) |
| Uptime | up 5 days, 18 hours, 59 minutes |

## Recent markers
- `2026-04-23T00:29:52` **queue_empty** — All 13 videos transcribed
- `2026-04-23T00:29:52` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-04-23T00:29:52` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED
- `2026-04-23T00:29:52` **transcription_done** — NRT_Fascial_Activation_Application_Method.mp4 complete (55/13)
- `2026-04-23T00:29:52` **ingest_failed** — NRT_Fascial_Activation_Application_Method.mp4 ingest FAILED

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
2026-04-23 00:30:22,713  INFO      Startup scan: 13 untranscribed video(s) found, 13 new entry/entries added to queue
2026-04-23 00:30:22,713  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-23 00:30:52,713  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-23 00:31:22,713  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-23 00:31:52,714  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-23 00:32:22,714  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-23 00:32:52,715  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-23 00:33:22,715  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-23 00:33:52,715  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-23 00:34:22,716  INFO      Queue paused (pause flag set) — waiting 30s
```
