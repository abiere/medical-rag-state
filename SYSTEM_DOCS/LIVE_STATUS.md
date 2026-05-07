# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-05-07 19:13:52 UTC**

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
| Queued | 5 |
| Done | 55 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 11.75 GB / 32.86 GB (36%) |
| CPU | 7.5% |
| Disk used | 90.4 GB / 322.3 GB (29%) |
| Uptime | up 2 weeks, 6 days, 13 hours, 38 minutes |

## Recent markers
- `2026-05-07T19:13:52` **transcription_done** — How_to_Reset_23_More_Muscles.mp4 complete (55/13)
- `2026-05-07T19:13:52` **ingest_failed** — How_to_Reset_23_More_Muscles.mp4 ingest FAILED
- `2026-05-07T19:13:52` **transcription_done** — Everything_Reset_Sequence_-_Part_5.mp4 complete (55/13)
- `2026-05-07T19:13:52` **ingest_failed** — Everything_Reset_Sequence_-_Part_5.mp4 ingest FAILED
- `2026-05-07T19:13:52` **transcription_done** — Everything_Reset_Sequence_-_Part_4.mp4 complete (55/13)

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
2026-05-07 19:13:52,601  INFO      START  nrt/How_to_Reset_23_More_Muscles.mp4  (412 MB)
2026-05-07 19:13:52,601  INFO      Using existing segments for How_to_Reset_23_More_Muscles.mp4: 2 parts
2026-05-07 19:13:52,601  INFO      Transcribing 2 segments for How_to_Reset_23_More_Muscles.mp4
2026-05-07 19:13:52,740  INFO      DONE   nrt/How_to_Reset_23_More_Muscles.mp4  (0s, 2 segments)
2026-05-07 19:13:52,741  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/How_to_Reset_23_More_Muscles.json
2026-05-07 19:13:52,872  INFO      START  nrt/Miraculous_Sequence_-_Part_1.mp4  (689 MB)
2026-05-07 19:13:52,873  INFO      Using existing segments for Miraculous_Sequence_-_Part_1.mp4: 2 parts
2026-05-07 19:13:52,873  INFO      Transcribing 2 segments for Miraculous_Sequence_-_Part_1.mp4
2026-05-07 19:13:52,997  INFO      DONE   nrt/Miraculous_Sequence_-_Part_1.mp4  (0s, 2 segments)
2026-05-07 19:13:52,998  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Miraculous_Sequence_-_Part_1.json
```
