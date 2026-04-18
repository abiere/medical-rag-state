# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-18 10:46:37 UTC**

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
| Current job | `Everything_Reset_Sequence_-_Part_5.mp4` (19 min) |
| Queued | 9 |
| Done | 35 / 51 |
| Vectors in nrt_video_transcripts | 241 |

## System
| Metric | Value |
|---|---|
| RAM used | 6.63 GB / 32.86 GB (20%) |
| CPU | 96.1% |
| Disk used | 77.2 GB / 322.3 GB (25%) |
| Uptime | up 1 day, 5 hours, 11 minutes |

## Recent markers
- `2026-04-18T10:27:32` **transcription_done** — Everything_Reset_Sequence_-_Part_4.mp4 complete (34/14)
- `2026-04-18T10:27:32` **ingest_failed** — Everything_Reset_Sequence_-_Part_4.mp4 ingest FAILED
- `2026-04-18T09:58:21` **transcription_done** — Everything_Reset_Sequence_-_Part_3.mp4 complete (31/14)
- `2026-04-18T09:58:21` **ingest_failed** — Everything_Reset_Sequence_-_Part_3.mp4 ingest FAILED
- `2026-04-18T09:36:12` **transcription_done** — Everything_Reset_Sequence_-_Part_2.mp4 complete (29/14)

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
2026-04-18 09:58:21,526  INFO      Splitting Everything_Reset_Sequence_-_Part_4.mp4 (690 MB) into 20-min segments
2026-04-18 09:58:29,883  INFO      Split Everything_Reset_Sequence_-_Part_4.mp4 into 3 segments
2026-04-18 09:58:29,883  INFO      Transcribing 3 segments for Everything_Reset_Sequence_-_Part_4.mp4
2026-04-18 10:27:32,564  INFO      DONE   nrt/Everything_Reset_Sequence_-_Part_4.mp4  (1751s, 3 segments)
2026-04-18 10:27:32,565  INFO      Stats updated: Everything_Reset_Sequence_-_Part_4.mp4 — 2.4s/MB  rate=2.5s/MB (10 samples)
2026-04-18 10:27:32,566  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Everything_Reset_Sequence_-_Part_4.json
2026-04-18 10:27:32,696  INFO      START  nrt/Everything_Reset_Sequence_-_Part_5.mp4  (618 MB)
2026-04-18 10:27:32,697  INFO      Splitting Everything_Reset_Sequence_-_Part_5.mp4 (618 MB) into 20-min segments
2026-04-18 10:27:38,996  INFO      Split Everything_Reset_Sequence_-_Part_5.mp4 into 3 segments
2026-04-18 10:27:38,996  INFO      Transcribing 3 segments for Everything_Reset_Sequence_-_Part_5.mp4
```
