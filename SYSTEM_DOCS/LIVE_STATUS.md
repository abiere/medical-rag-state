# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-18 11:53:02 UTC**

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
| Current job | `NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows.mp4` (10 min) |
| Queued | 5 |
| Done | 43 / 59 |
| Vectors in nrt_video_transcripts | 241 |

## System
| Metric | Value |
|---|---|
| RAM used | 6.61 GB / 32.86 GB (20%) |
| CPU | 94.5% |
| Disk used | 80.1 GB / 322.3 GB (26%) |
| Uptime | up 1 day, 6 hours, 17 minutes |

## Recent markers
- `2026-04-18T11:42:53` **transcription_done** — Miraculous_Sequence_-_Part_2.mp4 complete (43/14)
- `2026-04-18T11:42:53` **ingest_failed** — Miraculous_Sequence_-_Part_2.mp4 ingest FAILED
- `2026-04-18T11:23:01` **transcription_done** — Miraculous_Sequence_-_Part_1.mp4 complete (41/14)
- `2026-04-18T11:23:01` **ingest_failed** — Miraculous_Sequence_-_Part_1.mp4 ingest FAILED
- `2026-04-18T11:03:03` **transcription_done** — How_to_Reset_23_More_Muscles.mp4 complete (39/14)

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
2026-04-18 11:23:01,133  INFO      Splitting Miraculous_Sequence_-_Part_2.mp4 (664 MB) into 20-min segments
2026-04-18 11:23:08,008  INFO      Split Miraculous_Sequence_-_Part_2.mp4 into 2 segments
2026-04-18 11:23:08,008  INFO      Transcribing 2 segments for Miraculous_Sequence_-_Part_2.mp4
2026-04-18 11:42:53,123  INFO      DONE   nrt/Miraculous_Sequence_-_Part_2.mp4  (1192s, 2 segments)
2026-04-18 11:42:53,125  INFO      Stats updated: Miraculous_Sequence_-_Part_2.mp4 — 1.7s/MB  rate=2.3s/MB (14 samples)
2026-04-18 11:42:53,125  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Miraculous_Sequence_-_Part_2.json
2026-04-18 11:42:53,256  INFO      START  nrt/NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows.mp4  (990 MB)
2026-04-18 11:42:53,257  INFO      Splitting NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows.mp4 (990 MB) into 20-min segments
2026-04-18 11:42:58,560  INFO      Split NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows.mp4 into 2 segments
2026-04-18 11:42:58,560  INFO      Transcribing 2 segments for NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows.mp4
```
