# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-11-04 02:45:00 UTC**

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
| RAM used | 3.31 GB / 32.86 GB (10%) |
| CPU | 6.0% |
| Disk used | 119.0 GB / 322.3 GB (38%) |
| Uptime | up 28 weeks, 4 days, 21 hours, 9 minutes |

## Recent markers
- `2026-11-04T02:45:00` **transcription_done** — 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4 complete (55/13)
- `2026-11-04T02:45:00` **ingest_failed** — 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4 ingest FAILED
- `2026-11-04T02:45:00` **transcription_done** — 1.Upper_Body_Techniques.mp4 complete (55/13)
- `2026-11-04T02:45:00` **ingest_failed** — 1.Upper_Body_Techniques.mp4 ingest FAILED
- `2026-11-04T02:44:30` **queue_empty** — All 13 videos transcribed

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
2026-11-04 02:45:03,492  INFO      START  nrt/NRT_Fascial_Activation_Application_Method.mp4  (1871 MB)
2026-11-04 02:45:03,492  INFO      Using existing segments for NRT_Fascial_Activation_Application_Method.mp4: 3 parts
2026-11-04 02:45:03,492  INFO      Transcribing 3 segments for NRT_Fascial_Activation_Application_Method.mp4
2026-11-04 02:45:03,687  INFO      DONE   nrt/NRT_Fascial_Activation_Application_Method.mp4  (0s, 3 segments)
2026-11-04 02:45:03,688  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/NRT_Fascial_Activation_Application_Method.json
2026-11-04 02:45:03,818  INFO      START  nrt/NRT_Sports_Specific_or_Universal_Reset.mp4  (957 MB)
2026-11-04 02:45:03,818  INFO      Using existing segments for NRT_Sports_Specific_or_Universal_Reset.mp4: 2 parts
2026-11-04 02:45:03,819  INFO      Transcribing 2 segments for NRT_Sports_Specific_or_Universal_Reset.mp4
2026-11-04 02:45:03,941  INFO      DONE   nrt/NRT_Sports_Specific_or_Universal_Reset.mp4  (0s, 2 segments)
2026-11-04 02:45:03,942  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/NRT_Sports_Specific_or_Universal_Reset.json
```
