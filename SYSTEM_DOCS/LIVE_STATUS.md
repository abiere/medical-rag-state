# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-10-07 00:36:30 UTC**

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
| Queued | 12 |
| Done | 55 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 3.4 GB / 32.86 GB (10%) |
| CPU | 2.9% |
| Disk used | 98.9 GB / 322.3 GB (32%) |
| Uptime | up 24 weeks, 4 days, 19 hours, 1 minute |

## Recent markers
- `2026-10-07T00:31:02` **transcription_done** — 1.Upper_Body_Techniques.mp4 complete (55/13)
- `2026-10-07T00:31:02` **ingest_failed** — 1.Upper_Body_Techniques.mp4 ingest FAILED
- `2026-10-07T00:30:31` **queue_empty** — All 13 videos transcribed
- `2026-10-07T00:30:31` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-10-07T00:30:31` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED

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
2026-10-07 00:31:32,618  INFO      Queue paused (pause flag set) — waiting 30s
2026-10-07 00:32:02,619  INFO      Queue paused (pause flag set) — waiting 30s
2026-10-07 00:32:32,619  INFO      Queue paused (pause flag set) — waiting 30s
2026-10-07 00:33:02,620  INFO      Queue paused (pause flag set) — waiting 30s
2026-10-07 00:33:32,620  INFO      Queue paused (pause flag set) — waiting 30s
2026-10-07 00:34:02,621  INFO      Queue paused (pause flag set) — waiting 30s
2026-10-07 00:34:32,621  INFO      Queue paused (pause flag set) — waiting 30s
2026-10-07 00:35:02,621  INFO      Queue paused (pause flag set) — waiting 30s
2026-10-07 00:35:32,622  INFO      Queue paused (pause flag set) — waiting 30s
2026-10-07 00:36:02,622  INFO      Queue paused (pause flag set) — waiting 30s
```
