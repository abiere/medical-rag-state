# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-26 00:32:28 UTC**

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
| RAM used | 4.32 GB / 32.86 GB (13%) |
| CPU | 6.4% |
| Disk used | 88.1 GB / 322.3 GB (28%) |
| Uptime | up 1 week, 1 day, 18 hours, 57 minutes |

## Recent markers
- `2026-04-26T00:30:56` **queue_empty** — All 13 videos transcribed
- `2026-04-26T00:30:56` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-04-26T00:30:55` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED
- `2026-04-26T00:30:55` **transcription_done** — NRT_Fascial_Activation_Application_Method.mp4 complete (55/13)
- `2026-04-26T00:30:55` **ingest_failed** — NRT_Fascial_Activation_Application_Method.mp4 ingest FAILED

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
2026-04-26 00:30:55,983  INFO      DONE   nrt/NRT_Sports_Specific_or_Universal_Reset.mp4  (0s, 2 segments)
2026-04-26 00:30:55,984  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/NRT_Sports_Specific_or_Universal_Reset.json
2026-04-26 00:30:56,113  INFO      Queue empty — 13 video(s) processed. Exiting.
2026-04-26 00:30:56,177  INFO      Transcription queue manager done
2026-04-26 00:31:26,464  INFO      ────────────────────────────────────────────────────────────
2026-04-26 00:31:26,464  INFO      Transcription queue manager started
2026-04-26 00:31:26,466  INFO      Startup scan: 13 untranscribed video(s) found, 13 new entry/entries added to queue
2026-04-26 00:31:26,466  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-26 00:31:56,466  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-26 00:32:26,466  INFO      Queue paused (pause flag set) — waiting 30s
```
