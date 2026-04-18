# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-18 15:44:01 UTC**

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
| Total books | 35 |
| Ingested | 74 |
| Vectors in medical_library | 18006 |
| Images pending approval | 2026 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `How_to_Reset_23_More_Muscles.mp4` |
| Queued | 6 |
| Done | 55 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 2.06 GB / 32.86 GB (6%) |
| CPU | 5.9% |
| Disk used | 83.9 GB / 322.3 GB (27%) |
| Uptime | up 1 day, 10 hours, 8 minutes |

## Recent markers
- `2026-04-18T15:44:02` **transcription_done** — Everything_Reset_Sequence_-_Part_5.mp4 complete (55/13)
- `2026-04-18T15:44:02` **ingest_failed** — Everything_Reset_Sequence_-_Part_5.mp4 ingest FAILED
- `2026-04-18T15:44:01` **transcription_done** — Everything_Reset_Sequence_-_Part_4.mp4 complete (55/13)
- `2026-04-18T15:44:01` **ingest_failed** — Everything_Reset_Sequence_-_Part_4.mp4 ingest FAILED
- `2026-04-18T15:44:01` **transcription_done** — Everything_Reset_Sequence_-_Part_3.mp4 complete (55/13)

## Nightly Consistency
```
  TRANSCRIPT ONTBREEKT IN QDRANT: Organs_and_Glands_Review.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: 2.Lower_Body_Fundamentals.json (type: nrt)
  TRANSCRIPT ONTBREEKT IN QDRANT: Pair_Balancing.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Neuromuscular_ReEducation.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_3.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Anti-Inflammatory_Procedure.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_1.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Indicator_Muscle.json (type: qat)
```

## Queue log (last 10 lines)
```
2026-04-18 15:44:01,976  INFO      START  nrt/Everything_Reset_Sequence_-_Part_5.mp4  (618 MB)
2026-04-18 15:44:01,977  INFO      Using existing segments for Everything_Reset_Sequence_-_Part_5.mp4: 3 parts
2026-04-18 15:44:01,977  INFO      Transcribing 3 segments for Everything_Reset_Sequence_-_Part_5.mp4
2026-04-18 15:44:02,248  INFO      DONE   nrt/Everything_Reset_Sequence_-_Part_5.mp4  (0s, 3 segments)
2026-04-18 15:44:02,249  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Everything_Reset_Sequence_-_Part_5.json
2026-04-18 15:44:02,381  INFO      START  nrt/How_to_Reset_23_More_Muscles.mp4  (412 MB)
2026-04-18 15:44:02,381  INFO      Using existing segments for How_to_Reset_23_More_Muscles.mp4: 2 parts
2026-04-18 15:44:02,382  INFO      Transcribing 2 segments for How_to_Reset_23_More_Muscles.mp4
2026-04-18 15:44:02,551  INFO      DONE   nrt/How_to_Reset_23_More_Muscles.mp4  (0s, 2 segments)
2026-04-18 15:44:02,552  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/How_to_Reset_23_More_Muscles.json
```
