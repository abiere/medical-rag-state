# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-18 09:47:39 UTC**

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
| Current job | `Everything_Reset_Sequence_-_Part_3.mp4` (11 min) |
| Queued | 11 |
| Done | 29 / 45 |
| Vectors in nrt_video_transcripts | 241 |

## System
| Metric | Value |
|---|---|
| RAM used | 6.62 GB / 32.86 GB (20%) |
| CPU | 96.1% |
| Disk used | 75.8 GB / 322.3 GB (24%) |
| Uptime | up 1 day, 4 hours, 12 minutes |

## Recent markers
- `2026-04-18T09:36:12` **transcription_done** — Everything_Reset_Sequence_-_Part_2.mp4 complete (29/14)
- `2026-04-18T09:36:12` **ingest_failed** — Everything_Reset_Sequence_-_Part_2.mp4 ingest FAILED
- `2026-04-18T09:12:43` **transcription_done** — Everything_Reset_Sequence_-_Part_1.mp4 complete (26/14)
- `2026-04-18T09:12:43` **ingest_failed** — Everything_Reset_Sequence_-_Part_1.mp4 ingest FAILED
- `2026-04-18T08:46:29` **transcription_done** — 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4 complete (23/14)

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
2026-04-18 09:12:43,557  INFO      Splitting Everything_Reset_Sequence_-_Part_2.mp4 (499 MB) into 20-min segments
2026-04-18 09:12:49,827  INFO      Split Everything_Reset_Sequence_-_Part_2.mp4 into 3 segments
2026-04-18 09:12:49,827  INFO      Transcribing 3 segments for Everything_Reset_Sequence_-_Part_2.mp4
2026-04-18 09:36:12,776  INFO      DONE   nrt/Everything_Reset_Sequence_-_Part_2.mp4  (1409s, 3 segments)
2026-04-18 09:36:12,777  INFO      Stats updated: Everything_Reset_Sequence_-_Part_2.mp4 — 2.7s/MB  rate=2.5s/MB (8 samples)
2026-04-18 09:36:12,778  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Everything_Reset_Sequence_-_Part_2.json
2026-04-18 09:36:12,908  INFO      START  nrt/Everything_Reset_Sequence_-_Part_3.mp4  (565 MB)
2026-04-18 09:36:12,908  INFO      Splitting Everything_Reset_Sequence_-_Part_3.mp4 (565 MB) into 20-min segments
2026-04-18 09:36:18,723  INFO      Split Everything_Reset_Sequence_-_Part_3.mp4 into 2 segments
2026-04-18 09:36:18,724  INFO      Transcribing 2 segments for Everything_Reset_Sequence_-_Part_3.mp4
```
