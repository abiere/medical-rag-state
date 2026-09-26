# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-09-26 23:53:42 UTC**

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
| Queued | 8 |
| Done | 55 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 2.73 GB / 32.86 GB (8%) |
| CPU | 5.1% |
| Disk used | 98.8 GB / 322.3 GB (32%) |
| Uptime | up 23 weeks, 1 day, 18 hours, 18 minutes |

## Recent markers
- `2026-09-26T23:53:43` **transcription_done** — Everything_Reset_Sequence_-_Part_2.mp4 complete (55/13)
- `2026-09-26T23:53:43` **ingest_failed** — Everything_Reset_Sequence_-_Part_2.mp4 ingest FAILED
- `2026-09-26T23:53:43` **transcription_done** — Everything_Reset_Sequence_-_Part_1.mp4 complete (55/13)
- `2026-09-26T23:53:43` **ingest_failed** — Everything_Reset_Sequence_-_Part_1.mp4 ingest FAILED
- `2026-09-26T23:53:42` **transcription_done** — 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4 complete (55/13)

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
2026-09-26 23:53:44,550  INFO      START  nrt/Miraculous_Sequence_-_Part_1.mp4  (689 MB)
2026-09-26 23:53:44,551  INFO      Using existing segments for Miraculous_Sequence_-_Part_1.mp4: 2 parts
2026-09-26 23:53:44,551  INFO      Transcribing 2 segments for Miraculous_Sequence_-_Part_1.mp4
2026-09-26 23:53:44,667  INFO      DONE   nrt/Miraculous_Sequence_-_Part_1.mp4  (0s, 2 segments)
2026-09-26 23:53:44,668  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Miraculous_Sequence_-_Part_1.json
2026-09-26 23:53:44,797  INFO      START  nrt/Miraculous_Sequence_-_Part_2.mp4  (664 MB)
2026-09-26 23:53:44,798  INFO      Using existing segments for Miraculous_Sequence_-_Part_2.mp4: 2 parts
2026-09-26 23:53:44,798  INFO      Transcribing 2 segments for Miraculous_Sequence_-_Part_2.mp4
2026-09-26 23:53:44,922  INFO      DONE   nrt/Miraculous_Sequence_-_Part_2.mp4  (0s, 2 segments)
2026-09-26 23:53:44,922  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Miraculous_Sequence_-_Part_2.json
```
