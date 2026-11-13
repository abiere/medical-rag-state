# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-11-13 00:41:00 UTC**

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
| RAM used | 3.7 GB / 32.86 GB (11%) |
| CPU | 6.4% |
| Disk used | 138.1 GB / 322.3 GB (45%) |
| Uptime | up 29 weeks, 6 days, 19 hours, 5 minutes |

## Recent markers
- `2026-11-13T00:30:45` **transcription_done** — 1.Upper_Body_Techniques.mp4 complete (55/13)
- `2026-11-13T00:30:45` **ingest_failed** — 1.Upper_Body_Techniques.mp4 ingest FAILED
- `2026-11-13T00:30:15` **queue_empty** — All 13 videos transcribed
- `2026-11-13T00:30:14` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-11-13T00:30:14` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED

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
2026-11-13 00:36:15,616  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-13 00:36:45,617  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-13 00:37:15,617  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-13 00:37:45,618  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-13 00:38:15,618  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-13 00:38:45,619  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-13 00:39:15,619  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-13 00:39:45,620  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-13 00:40:15,620  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-13 00:40:45,621  INFO      Queue paused (pause flag set) — waiting 30s
```
