# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-08-22 17:44:20 UTC**

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
| RAM used | 5.26 GB / 32.86 GB (16%) |
| CPU | 5.1% |
| Disk used | 94.8 GB / 322.3 GB (31%) |
| Uptime | up 18 weeks, 1 day, 12 hours, 8 minutes |

## Recent markers
- `2026-08-22T17:44:20` **transcription_done** — 1.Upper_Body_Techniques.mp4 complete (55/13)
- `2026-08-22T17:44:20` **ingest_failed** — 1.Upper_Body_Techniques.mp4 ingest FAILED
- `2026-08-22T17:43:50` **queue_empty** — All 13 videos transcribed
- `2026-08-22T17:43:50` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-08-22T17:43:50` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED

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
2026-08-22 17:44:21,637  INFO      START  nrt/Everything_Reset_Sequence_-_Part_3.mp4  (565 MB)
2026-08-22 17:44:21,637  INFO      Using existing segments for Everything_Reset_Sequence_-_Part_3.mp4: 2 parts
2026-08-22 17:44:21,638  INFO      Transcribing 2 segments for Everything_Reset_Sequence_-_Part_3.mp4
2026-08-22 17:44:21,750  INFO      DONE   nrt/Everything_Reset_Sequence_-_Part_3.mp4  (0s, 2 segments)
2026-08-22 17:44:21,751  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Everything_Reset_Sequence_-_Part_3.json
2026-08-22 17:44:21,880  INFO      START  nrt/Everything_Reset_Sequence_-_Part_4.mp4  (690 MB)
2026-08-22 17:44:21,880  INFO      Using existing segments for Everything_Reset_Sequence_-_Part_4.mp4: 3 parts
2026-08-22 17:44:21,880  INFO      Transcribing 3 segments for Everything_Reset_Sequence_-_Part_4.mp4
2026-08-22 17:44:22,052  INFO      DONE   nrt/Everything_Reset_Sequence_-_Part_4.mp4  (0s, 3 segments)
2026-08-22 17:44:22,053  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Everything_Reset_Sequence_-_Part_4.json
```
