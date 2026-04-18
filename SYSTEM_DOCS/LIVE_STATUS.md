# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-18 12:38:15 UTC**

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
| Current job | `NRT_Sports_Specific_or_Universal_Reset.mp4` (9 min) |
| Queued | 3 |
| Done | 48 / 64 |
| Vectors in nrt_video_transcripts | 241 |

## System
| Metric | Value |
|---|---|
| RAM used | 6.67 GB / 32.86 GB (20%) |
| CPU | 95.1% |
| Disk used | 82.7 GB / 322.3 GB (27%) |
| Uptime | up 1 day, 7 hours, 2 minutes |

## Recent markers
- `2026-04-18T12:28:31` **transcription_done** — NRT_Fascial_Activation_Application_Method.mp4 complete (48/14)
- `2026-04-18T12:28:31` **ingest_failed** — NRT_Fascial_Activation_Application_Method.mp4 ingest FAILED
- `2026-04-18T11:58:17` **transcription_done** — NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows.mp4 complete (45/14)
- `2026-04-18T11:58:17` **ingest_failed** — NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows.mp4 ingest FAILED
- `2026-04-18T11:42:53` **transcription_done** — Miraculous_Sequence_-_Part_2.mp4 complete (43/14)

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
2026-04-18 11:58:17,315  INFO      Splitting NRT_Fascial_Activation_Application_Method.mp4 (1871 MB) into 20-min segments
2026-04-18 11:58:27,604  INFO      Split NRT_Fascial_Activation_Application_Method.mp4 into 3 segments
2026-04-18 11:58:27,605  INFO      Transcribing 3 segments for NRT_Fascial_Activation_Application_Method.mp4
2026-04-18 12:28:31,229  INFO      DONE   nrt/NRT_Fascial_Activation_Application_Method.mp4  (1814s, 3 segments)
2026-04-18 12:28:31,230  INFO      Stats updated: NRT_Fascial_Activation_Application_Method.mp4 — 0.9s/MB  rate=2.0s/MB (16 samples)
2026-04-18 12:28:31,231  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/NRT_Fascial_Activation_Application_Method.json
2026-04-18 12:28:31,362  INFO      START  nrt/NRT_Sports_Specific_or_Universal_Reset.mp4  (957 MB)
2026-04-18 12:28:31,363  INFO      Splitting NRT_Sports_Specific_or_Universal_Reset.mp4 (957 MB) into 20-min segments
2026-04-18 12:28:36,985  INFO      Split NRT_Sports_Specific_or_Universal_Reset.mp4 into 2 segments
2026-04-18 12:28:36,985  INFO      Transcribing 2 segments for NRT_Sports_Specific_or_Universal_Reset.mp4
```
