# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-10-29 09:15:55 UTC**

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
| RAM used | 3.34 GB / 32.86 GB (10%) |
| CPU | 6.1% |
| Disk used | 119.0 GB / 322.3 GB (38%) |
| Uptime | up 27 weeks, 6 days, 3 hours, 40 minutes |

## Recent markers
- `2026-10-29T09:15:55` **ingest_failed** — 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4 ingest FAILED
- `2026-10-29T09:15:55` **transcription_done** — 1.Upper_Body_Techniques.mp4 complete (55/13)
- `2026-10-29T09:15:55` **ingest_failed** — 1.Upper_Body_Techniques.mp4 ingest FAILED
- `2026-10-29T09:15:25` **queue_empty** — All 13 videos transcribed
- `2026-10-29T09:15:25` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)

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
2026-10-29 09:15:57,297  INFO      DONE   nrt/Everything_Reset_Sequence_-_Part_5.mp4  (0s, 3 segments)
2026-10-29 09:15:57,298  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Everything_Reset_Sequence_-_Part_5.json
2026-10-29 09:15:57,428  INFO      START  nrt/How_to_Reset_23_More_Muscles.mp4  (412 MB)
2026-10-29 09:15:57,428  INFO      Using existing segments for How_to_Reset_23_More_Muscles.mp4: 2 parts
2026-10-29 09:15:57,428  INFO      Transcribing 2 segments for How_to_Reset_23_More_Muscles.mp4
2026-10-29 09:15:57,551  INFO      DONE   nrt/How_to_Reset_23_More_Muscles.mp4  (0s, 2 segments)
2026-10-29 09:15:57,552  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/How_to_Reset_23_More_Muscles.json
2026-10-29 09:15:57,682  INFO      START  nrt/Miraculous_Sequence_-_Part_1.mp4  (689 MB)
2026-10-29 09:15:57,682  INFO      Using existing segments for Miraculous_Sequence_-_Part_1.mp4: 2 parts
2026-10-29 09:15:57,682  INFO      Transcribing 2 segments for Miraculous_Sequence_-_Part_1.mp4
```
