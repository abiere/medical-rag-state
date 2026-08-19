# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-08-19 00:34:35 UTC**

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
| RAM used | 6.02 GB / 32.86 GB (18%) |
| CPU | 2.9% |
| Disk used | 94.5 GB / 322.3 GB (31%) |
| Uptime | up 17 weeks, 4 days, 18 hours, 59 minutes |

## Recent markers
- `2026-08-19T00:30:15` **transcription_done** — 1.Upper_Body_Techniques.mp4 complete (55/13)
- `2026-08-19T00:30:14` **ingest_failed** — 1.Upper_Body_Techniques.mp4 ingest FAILED
- `2026-08-19T00:29:44` **queue_empty** — All 13 videos transcribed
- `2026-08-19T00:29:44` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-08-19T00:29:44` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED

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
2026-08-19 00:30:14,961  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/1.Upper_Body_Techniques.json
2026-08-19 00:30:15,090  INFO      Queue paused (pause flag set) — waiting 30s
2026-08-19 00:30:45,090  INFO      Queue paused (pause flag set) — waiting 30s
2026-08-19 00:31:15,091  INFO      Queue paused (pause flag set) — waiting 30s
2026-08-19 00:31:45,091  INFO      Queue paused (pause flag set) — waiting 30s
2026-08-19 00:32:15,091  INFO      Queue paused (pause flag set) — waiting 30s
2026-08-19 00:32:45,092  INFO      Queue paused (pause flag set) — waiting 30s
2026-08-19 00:33:15,092  INFO      Queue paused (pause flag set) — waiting 30s
2026-08-19 00:33:45,093  INFO      Queue paused (pause flag set) — waiting 30s
2026-08-19 00:34:15,093  INFO      Queue paused (pause flag set) — waiting 30s
```
