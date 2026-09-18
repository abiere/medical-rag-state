# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-09-18 23:31:32 UTC**

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
| RAM used | 3.74 GB / 32.86 GB (11%) |
| CPU | 5.8% |
| Disk used | 98.6 GB / 322.3 GB (32%) |
| Uptime | up 22 weeks, 17 hours, 56 minutes |

## Recent markers
- `2026-09-18T23:31:32` **transcription_done** — 1.Upper_Body_Techniques.mp4 complete (55/13)
- `2026-09-18T23:31:32` **ingest_failed** — 1.Upper_Body_Techniques.mp4 ingest FAILED
- `2026-09-18T23:31:02` **queue_empty** — All 13 videos transcribed
- `2026-09-18T23:31:02` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-09-18T23:31:02` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED

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
2026-09-18 23:31:33,841  INFO      START  nrt/Everything_Reset_Sequence_-_Part_4.mp4  (690 MB)
2026-09-18 23:31:33,842  INFO      Using existing segments for Everything_Reset_Sequence_-_Part_4.mp4: 3 parts
2026-09-18 23:31:33,842  INFO      Transcribing 3 segments for Everything_Reset_Sequence_-_Part_4.mp4
2026-09-18 23:31:34,028  INFO      DONE   nrt/Everything_Reset_Sequence_-_Part_4.mp4  (0s, 3 segments)
2026-09-18 23:31:34,029  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Everything_Reset_Sequence_-_Part_4.json
2026-09-18 23:31:34,159  INFO      START  nrt/Everything_Reset_Sequence_-_Part_5.mp4  (618 MB)
2026-09-18 23:31:34,160  INFO      Using existing segments for Everything_Reset_Sequence_-_Part_5.mp4: 3 parts
2026-09-18 23:31:34,160  INFO      Transcribing 3 segments for Everything_Reset_Sequence_-_Part_5.mp4
2026-09-18 23:31:34,353  INFO      DONE   nrt/Everything_Reset_Sequence_-_Part_5.mp4  (0s, 3 segments)
2026-09-18 23:31:34,354  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Everything_Reset_Sequence_-_Part_5.json
```
