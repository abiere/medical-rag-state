# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-18 10:57:49 UTC**

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
| Total books | 36 |
| Ingested | 74 |
| Vectors in medical_library | 19572 |
| Images pending approval | 2026 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `How_to_Reset_23_More_Muscles.mp4` (7 min) |
| Queued | 8 |
| Done | 37 / 53 |
| Vectors in nrt_video_transcripts | 241 |

## System
| Metric | Value |
|---|---|
| RAM used | 6.59 GB / 32.86 GB (20%) |
| CPU | 95.8% |
| Disk used | 77.7 GB / 322.3 GB (25%) |
| Uptime | up 1 day, 5 hours, 22 minutes |

## Recent markers
- `2026-04-18T10:50:11` **transcription_done** — Everything_Reset_Sequence_-_Part_5.mp4 complete (37/14)
- `2026-04-18T10:50:11` **ingest_failed** — Everything_Reset_Sequence_-_Part_5.mp4 ingest FAILED
- `2026-04-18T10:27:32` **transcription_done** — Everything_Reset_Sequence_-_Part_4.mp4 complete (34/14)
- `2026-04-18T10:27:32` **ingest_failed** — Everything_Reset_Sequence_-_Part_4.mp4 ingest FAILED
- `2026-04-18T09:58:21` **transcription_done** — Everything_Reset_Sequence_-_Part_3.mp4 complete (31/14)

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
2026-04-18 10:27:32,697  INFO      Splitting Everything_Reset_Sequence_-_Part_5.mp4 (618 MB) into 20-min segments
2026-04-18 10:27:38,996  INFO      Split Everything_Reset_Sequence_-_Part_5.mp4 into 3 segments
2026-04-18 10:27:38,996  INFO      Transcribing 3 segments for Everything_Reset_Sequence_-_Part_5.mp4
2026-04-18 10:50:11,921  INFO      DONE   nrt/Everything_Reset_Sequence_-_Part_5.mp4  (1359s, 3 segments)
2026-04-18 10:50:11,922  INFO      Stats updated: Everything_Reset_Sequence_-_Part_5.mp4 — 2.1s/MB  rate=2.5s/MB (11 samples)
2026-04-18 10:50:11,923  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Everything_Reset_Sequence_-_Part_5.json
2026-04-18 10:50:12,053  INFO      START  nrt/How_to_Reset_23_More_Muscles.mp4  (412 MB)
2026-04-18 10:50:12,053  INFO      Splitting How_to_Reset_23_More_Muscles.mp4 (412 MB) into 20-min segments
2026-04-18 10:50:15,845  INFO      Split How_to_Reset_23_More_Muscles.mp4 into 2 segments
2026-04-18 10:50:15,845  INFO      Transcribing 2 segments for How_to_Reset_23_More_Muscles.mp4
```
