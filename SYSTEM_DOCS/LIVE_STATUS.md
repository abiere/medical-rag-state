# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-18 18:11:05 UTC**

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
| Queued | 8 |
| Done | 55 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 8.79 GB / 32.86 GB (27%) |
| CPU | 13.9% |
| Disk used | 83.9 GB / 322.3 GB (27%) |
| Uptime | up 1 day, 12 hours, 35 minutes |

## Recent markers
- `2026-04-18T18:11:06` **ingest_failed** — Everything_Reset_Sequence_-_Part_3.mp4 ingest FAILED
- `2026-04-18T18:11:06` **transcription_done** — Everything_Reset_Sequence_-_Part_2.mp4 complete (55/13)
- `2026-04-18T18:11:06` **ingest_failed** — Everything_Reset_Sequence_-_Part_2.mp4 ingest FAILED
- `2026-04-18T18:11:05` **transcription_done** — Everything_Reset_Sequence_-_Part_1.mp4 complete (55/13)
- `2026-04-18T18:11:05` **ingest_failed** — Everything_Reset_Sequence_-_Part_1.mp4 ingest FAILED

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
2026-04-18 18:11:05,890  INFO      START  nrt/Everything_Reset_Sequence_-_Part_2.mp4  (499 MB)
2026-04-18 18:11:05,890  INFO      Using existing segments for Everything_Reset_Sequence_-_Part_2.mp4: 3 parts
2026-04-18 18:11:05,890  INFO      Transcribing 3 segments for Everything_Reset_Sequence_-_Part_2.mp4
2026-04-18 18:11:06,110  INFO      DONE   nrt/Everything_Reset_Sequence_-_Part_2.mp4  (0s, 3 segments)
2026-04-18 18:11:06,111  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Everything_Reset_Sequence_-_Part_2.json
2026-04-18 18:11:06,241  INFO      START  nrt/Everything_Reset_Sequence_-_Part_3.mp4  (565 MB)
2026-04-18 18:11:06,242  INFO      Using existing segments for Everything_Reset_Sequence_-_Part_3.mp4: 2 parts
2026-04-18 18:11:06,242  INFO      Transcribing 2 segments for Everything_Reset_Sequence_-_Part_3.mp4
2026-04-18 18:11:06,414  INFO      DONE   nrt/Everything_Reset_Sequence_-_Part_3.mp4  (0s, 2 segments)
2026-04-18 18:11:06,415  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Everything_Reset_Sequence_-_Part_3.json
```
