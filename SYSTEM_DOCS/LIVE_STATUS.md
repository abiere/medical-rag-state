# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-18 21:40:28 UTC**

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
| Vectors in medical_library | 17524 |
| Images pending approval | 2026 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | idle |
| Queued | 2 |
| Done | 55 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 2.74 GB / 32.86 GB (8%) |
| CPU | 5.4% |
| Disk used | 83.9 GB / 322.3 GB (27%) |
| Uptime | up 1 day, 16 hours, 5 minutes |

## Recent markers
- `2026-04-18T21:40:29` **transcription_done** — NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows.mp4 complete (55/13)
- `2026-04-18T21:40:29` **ingest_failed** — NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows.mp4 ingest FAILED
- `2026-04-18T21:40:29` **transcription_done** — Miraculous_Sequence_-_Part_2.mp4 complete (55/13)
- `2026-04-18T21:40:29` **ingest_failed** — Miraculous_Sequence_-_Part_2.mp4 ingest FAILED
- `2026-04-18T21:40:28` **transcription_done** — Miraculous_Sequence_-_Part_1.mp4 complete (55/13)

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
2026-04-18 21:40:28,882  INFO      START  nrt/Miraculous_Sequence_-_Part_2.mp4  (664 MB)
2026-04-18 21:40:28,882  INFO      Using existing segments for Miraculous_Sequence_-_Part_2.mp4: 2 parts
2026-04-18 21:40:28,882  INFO      Transcribing 2 segments for Miraculous_Sequence_-_Part_2.mp4
2026-04-18 21:40:29,023  INFO      DONE   nrt/Miraculous_Sequence_-_Part_2.mp4  (0s, 2 segments)
2026-04-18 21:40:29,024  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Miraculous_Sequence_-_Part_2.json
2026-04-18 21:40:29,154  INFO      START  nrt/NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows.mp4  (990 MB)
2026-04-18 21:40:29,154  INFO      Using existing segments for NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows.mp4: 2 parts
2026-04-18 21:40:29,154  INFO      Transcribing 2 segments for NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows.mp4
2026-04-18 21:40:29,292  INFO      DONE   nrt/NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows.mp4  (0s, 2 segments)
2026-04-18 21:40:29,293  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows.json
```
