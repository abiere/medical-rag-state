# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-10-10 19:26:48 UTC**

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
| Queued | 12 |
| Done | 55 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 2.8 GB / 32.86 GB (8%) |
| CPU | 5.1% |
| Disk used | 99.2 GB / 322.3 GB (32%) |
| Uptime | up 25 weeks, 1 day, 13 hours, 51 minutes |

## Recent markers
- `2026-10-10T19:26:48` **ingest_failed** — 1.Upper_Body_Techniques.mp4 ingest FAILED
- `2026-10-10T19:26:18` **queue_empty** — All 13 videos transcribed
- `2026-10-10T19:26:18` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-10-10T19:26:18` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED
- `2026-10-10T19:26:18` **transcription_done** — NRT_Fascial_Activation_Application_Method.mp4 complete (55/13)

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
2026-10-10 19:26:50,040  INFO      START  nrt/Everything_Reset_Sequence_-_Part_4.mp4  (690 MB)
2026-10-10 19:26:50,041  INFO      Using existing segments for Everything_Reset_Sequence_-_Part_4.mp4: 3 parts
2026-10-10 19:26:50,041  INFO      Transcribing 3 segments for Everything_Reset_Sequence_-_Part_4.mp4
2026-10-10 19:26:50,219  INFO      DONE   nrt/Everything_Reset_Sequence_-_Part_4.mp4  (0s, 3 segments)
2026-10-10 19:26:50,220  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Everything_Reset_Sequence_-_Part_4.json
2026-10-10 19:26:50,349  INFO      START  nrt/Everything_Reset_Sequence_-_Part_5.mp4  (618 MB)
2026-10-10 19:26:50,350  INFO      Using existing segments for Everything_Reset_Sequence_-_Part_5.mp4: 3 parts
2026-10-10 19:26:50,350  INFO      Transcribing 3 segments for Everything_Reset_Sequence_-_Part_5.mp4
2026-10-10 19:26:50,524  INFO      DONE   nrt/Everything_Reset_Sequence_-_Part_5.mp4  (0s, 3 segments)
2026-10-10 19:26:50,525  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Everything_Reset_Sequence_-_Part_5.json
```
