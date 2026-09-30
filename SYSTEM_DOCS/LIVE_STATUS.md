# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-09-30 12:34:16 UTC**

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
| Queued | 11 |
| Done | 55 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 2.82 GB / 32.86 GB (9%) |
| CPU | 5.6% |
| Disk used | 98.8 GB / 322.3 GB (32%) |
| Uptime | up 23 weeks, 5 days, 6 hours, 58 minutes |

## Recent markers
- `2026-09-30T12:34:17` **transcription_done** — 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4 complete (55/13)
- `2026-09-30T12:34:17` **ingest_failed** — 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4 ingest FAILED
- `2026-09-30T12:34:17` **transcription_done** — 1.Upper_Body_Techniques.mp4 complete (55/13)
- `2026-09-30T12:34:17` **ingest_failed** — 1.Upper_Body_Techniques.mp4 ingest FAILED
- `2026-09-30T12:33:46` **queue_empty** — All 13 videos transcribed

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
2026-09-30 12:34:19,078  INFO      START  nrt/How_to_Reset_23_More_Muscles.mp4  (412 MB)
2026-09-30 12:34:19,078  INFO      Using existing segments for How_to_Reset_23_More_Muscles.mp4: 2 parts
2026-09-30 12:34:19,078  INFO      Transcribing 2 segments for How_to_Reset_23_More_Muscles.mp4
2026-09-30 12:34:19,203  INFO      DONE   nrt/How_to_Reset_23_More_Muscles.mp4  (0s, 2 segments)
2026-09-30 12:34:19,204  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/How_to_Reset_23_More_Muscles.json
2026-09-30 12:34:19,333  INFO      START  nrt/Miraculous_Sequence_-_Part_1.mp4  (689 MB)
2026-09-30 12:34:19,334  INFO      Using existing segments for Miraculous_Sequence_-_Part_1.mp4: 2 parts
2026-09-30 12:34:19,334  INFO      Transcribing 2 segments for Miraculous_Sequence_-_Part_1.mp4
2026-09-30 12:34:19,453  INFO      DONE   nrt/Miraculous_Sequence_-_Part_1.mp4  (0s, 2 segments)
2026-09-30 12:34:19,454  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Miraculous_Sequence_-_Part_1.json
```
