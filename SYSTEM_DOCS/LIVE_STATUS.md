# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-18 11:32:57 UTC**

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
| Current job | `Miraculous_Sequence_-_Part_2.mp4` (9 min) |
| Queued | 6 |
| Done | 42 / 57 |
| Vectors in nrt_video_transcripts | 241 |

## System
| Metric | Value |
|---|---|
| RAM used | 2.52 GB / 32.86 GB (8%) |
| CPU | 6.5% |
| Disk used | 79.0 GB / 322.3 GB (26%) |
| Uptime | up 1 day, 5 hours, 57 minutes |

## Recent markers
- `2026-04-18T11:23:01` **transcription_done** — Miraculous_Sequence_-_Part_1.mp4 complete (41/14)
- `2026-04-18T11:23:01` **ingest_failed** — Miraculous_Sequence_-_Part_1.mp4 ingest FAILED
- `2026-04-18T11:03:03` **transcription_done** — How_to_Reset_23_More_Muscles.mp4 complete (39/14)
- `2026-04-18T11:03:03` **ingest_failed** — How_to_Reset_23_More_Muscles.mp4 ingest FAILED
- `2026-04-18T10:50:11` **transcription_done** — Everything_Reset_Sequence_-_Part_5.mp4 complete (37/14)

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
2026-04-18 11:03:03,428  INFO      Splitting Miraculous_Sequence_-_Part_1.mp4 (689 MB) into 20-min segments
2026-04-18 11:03:09,252  INFO      Split Miraculous_Sequence_-_Part_1.mp4 into 2 segments
2026-04-18 11:03:09,252  INFO      Transcribing 2 segments for Miraculous_Sequence_-_Part_1.mp4
2026-04-18 11:23:01,000  INFO      DONE   nrt/Miraculous_Sequence_-_Part_1.mp4  (1198s, 2 segments)
2026-04-18 11:23:01,002  INFO      Stats updated: Miraculous_Sequence_-_Part_1.mp4 — 1.7s/MB  rate=2.3s/MB (13 samples)
2026-04-18 11:23:01,002  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Miraculous_Sequence_-_Part_1.json
2026-04-18 11:23:01,133  INFO      START  nrt/Miraculous_Sequence_-_Part_2.mp4  (664 MB)
2026-04-18 11:23:01,133  INFO      Splitting Miraculous_Sequence_-_Part_2.mp4 (664 MB) into 20-min segments
2026-04-18 11:23:08,008  INFO      Split Miraculous_Sequence_-_Part_2.mp4 into 2 segments
2026-04-18 11:23:08,008  INFO      Transcribing 2 segments for Miraculous_Sequence_-_Part_2.mp4
```
