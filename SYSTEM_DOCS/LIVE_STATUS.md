# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-18 09:22:35 UTC**

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
| Current job | `Everything_Reset_Sequence_-_Part_2.mp4` (9 min) |
| Queued | 12 |
| Done | 26 / 43 |
| Vectors in nrt_video_transcripts | 241 |

## System
| Metric | Value |
|---|---|
| RAM used | 6.6 GB / 32.86 GB (20%) |
| CPU | 99.0% |
| Disk used | 75.2 GB / 322.3 GB (24%) |
| Uptime | up 1 day, 3 hours, 47 minutes |

## Recent markers
- `2026-04-18T09:12:43` **transcription_done** — Everything_Reset_Sequence_-_Part_1.mp4 complete (26/14)
- `2026-04-18T09:12:43` **ingest_failed** — Everything_Reset_Sequence_-_Part_1.mp4 ingest FAILED
- `2026-04-18T08:46:29` **transcription_done** — 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4 complete (23/14)
- `2026-04-18T08:46:29` **ingest_failed** — 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4 ingest FAILED
- `2026-04-18T08:41:30.353731+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully

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
2026-04-18 08:46:29,430  INFO      Splitting Everything_Reset_Sequence_-_Part_1.mp4 (649 MB) into 20-min segments
2026-04-18 08:46:37,588  INFO      Split Everything_Reset_Sequence_-_Part_1.mp4 into 3 segments
2026-04-18 08:46:37,588  INFO      Transcribing 3 segments for Everything_Reset_Sequence_-_Part_1.mp4
2026-04-18 09:12:43,424  INFO      DONE   nrt/Everything_Reset_Sequence_-_Part_1.mp4  (1574s, 3 segments)
2026-04-18 09:12:43,425  INFO      Stats updated: Everything_Reset_Sequence_-_Part_1.mp4 — 2.3s/MB  rate=2.5s/MB (7 samples)
2026-04-18 09:12:43,426  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Everything_Reset_Sequence_-_Part_1.json
2026-04-18 09:12:43,556  INFO      START  nrt/Everything_Reset_Sequence_-_Part_2.mp4  (499 MB)
2026-04-18 09:12:43,557  INFO      Splitting Everything_Reset_Sequence_-_Part_2.mp4 (499 MB) into 20-min segments
2026-04-18 09:12:49,827  INFO      Split Everything_Reset_Sequence_-_Part_2.mp4 into 3 segments
2026-04-18 09:12:49,827  INFO      Transcribing 3 segments for Everything_Reset_Sequence_-_Part_2.mp4
```
