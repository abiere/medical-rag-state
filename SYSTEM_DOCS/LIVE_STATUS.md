# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-05-04 12:40:15 UTC**

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
| RAM used | 5.35 GB / 32.86 GB (16%) |
| CPU | 5.5% |
| Disk used | 89.7 GB / 322.3 GB (29%) |
| Uptime | up 2 weeks, 3 days, 7 hours, 4 minutes |

## Recent markers
- `2026-05-04T12:40:15` **transcription_done** — Everything_Reset_Sequence_-_Part_3.mp4 complete (55/13)
- `2026-05-04T12:40:15` **ingest_failed** — Everything_Reset_Sequence_-_Part_3.mp4 ingest FAILED
- `2026-05-04T12:40:15` **transcription_done** — Everything_Reset_Sequence_-_Part_2.mp4 complete (55/13)
- `2026-05-04T12:40:15` **ingest_failed** — Everything_Reset_Sequence_-_Part_2.mp4 ingest FAILED
- `2026-05-04T12:40:15` **transcription_done** — Everything_Reset_Sequence_-_Part_1.mp4 complete (55/13)

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
2026-05-04 12:40:15,373  INFO      DONE   nrt/Everything_Reset_Sequence_-_Part_2.mp4  (0s, 3 segments)
2026-05-04 12:40:15,374  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Everything_Reset_Sequence_-_Part_2.json
2026-05-04 12:40:15,504  INFO      START  nrt/Everything_Reset_Sequence_-_Part_3.mp4  (565 MB)
2026-05-04 12:40:15,504  INFO      Using existing segments for Everything_Reset_Sequence_-_Part_3.mp4: 2 parts
2026-05-04 12:40:15,504  INFO      Transcribing 2 segments for Everything_Reset_Sequence_-_Part_3.mp4
2026-05-04 12:40:15,612  INFO      DONE   nrt/Everything_Reset_Sequence_-_Part_3.mp4  (0s, 2 segments)
2026-05-04 12:40:15,613  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Everything_Reset_Sequence_-_Part_3.json
2026-05-04 12:40:15,742  INFO      START  nrt/Everything_Reset_Sequence_-_Part_4.mp4  (690 MB)
2026-05-04 12:40:15,743  INFO      Using existing segments for Everything_Reset_Sequence_-_Part_4.mp4: 3 parts
2026-05-04 12:40:15,743  INFO      Transcribing 3 segments for Everything_Reset_Sequence_-_Part_4.mp4
```
