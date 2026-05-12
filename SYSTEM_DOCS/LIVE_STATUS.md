# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-05-12 15:47:22 UTC**

## Services
| Service | Status |
|---|---|
| medical-rag-web | ✅ active |
| transcription-queue | ⚠️ activating |
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
| Queued | 0 |
| Done | 55 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 6.22 GB / 32.86 GB (19%) |
| CPU | 0.1% |
| Disk used | 91.2 GB / 322.3 GB (30%) |
| Uptime | up 3 weeks, 4 days, 10 hours, 12 minutes |

## Recent markers
- `2026-05-12T15:46:53` **queue_empty** — All 13 videos transcribed
- `2026-05-12T15:46:53` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-05-12T15:46:53` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED
- `2026-05-12T15:46:52` **transcription_done** — NRT_Fascial_Activation_Application_Method.mp4 complete (55/13)
- `2026-05-12T15:46:52` **ingest_failed** — NRT_Fascial_Activation_Application_Method.mp4 ingest FAILED

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
2026-05-12 15:46:53,011  INFO      DONE   nrt/NRT_Sports_Specific_or_Universal_Reset.mp4  (0s, 2 segments)
2026-05-12 15:46:53,012  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/NRT_Sports_Specific_or_Universal_Reset.json
2026-05-12 15:46:53,141  INFO      Queue empty — 13 video(s) processed. Exiting.
2026-05-12 15:46:53,205  INFO      Transcription queue manager done
2026-05-12 15:47:23,462  INFO      ────────────────────────────────────────────────────────────
2026-05-12 15:47:23,462  INFO      Transcription queue manager started
2026-05-12 15:47:23,463  INFO      Startup scan: 13 untranscribed video(s) found, 13 new entry/entries added to queue
2026-05-12 15:47:23,464  INFO      START  nrt/1.Upper_Body_Techniques.mp4  (525 MB)
2026-05-12 15:47:23,464  INFO      Using existing segments for 1.Upper_Body_Techniques.mp4: 4 parts
2026-05-12 15:47:23,464  INFO      Transcribing 4 segments for 1.Upper_Body_Techniques.mp4
```
