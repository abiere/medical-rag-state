# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-08-23 15:26:14 UTC**

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
| Current job | `2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4` |
| Queued | 12 |
| Done | 55 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 5.53 GB / 32.86 GB (17%) |
| CPU | 4.3% |
| Disk used | 94.4 GB / 322.3 GB (30%) |
| Uptime | up 18 weeks, 2 days, 9 hours, 50 minutes |

## Recent markers
- `2026-08-23T15:26:14` **transcription_done** — 1.Upper_Body_Techniques.mp4 complete (55/13)
- `2026-08-23T15:26:14` **ingest_failed** — 1.Upper_Body_Techniques.mp4 ingest FAILED
- `2026-08-23T15:25:44` **queue_empty** — All 13 videos transcribed
- `2026-08-23T15:25:44` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-08-23T15:25:44` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED

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
2026-08-23 15:26:15,620  INFO      START  nrt/Everything_Reset_Sequence_-_Part_3.mp4  (565 MB)
2026-08-23 15:26:15,621  INFO      Using existing segments for Everything_Reset_Sequence_-_Part_3.mp4: 2 parts
2026-08-23 15:26:15,621  INFO      Transcribing 2 segments for Everything_Reset_Sequence_-_Part_3.mp4
2026-08-23 15:26:15,750  INFO      DONE   nrt/Everything_Reset_Sequence_-_Part_3.mp4  (0s, 2 segments)
2026-08-23 15:26:15,751  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Everything_Reset_Sequence_-_Part_3.json
2026-08-23 15:26:15,881  INFO      START  nrt/Everything_Reset_Sequence_-_Part_4.mp4  (690 MB)
2026-08-23 15:26:15,882  INFO      Using existing segments for Everything_Reset_Sequence_-_Part_4.mp4: 3 parts
2026-08-23 15:26:15,882  INFO      Transcribing 3 segments for Everything_Reset_Sequence_-_Part_4.mp4
2026-08-23 15:26:16,069  INFO      DONE   nrt/Everything_Reset_Sequence_-_Part_4.mp4  (0s, 3 segments)
2026-08-23 15:26:16,069  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Everything_Reset_Sequence_-_Part_4.json
```
