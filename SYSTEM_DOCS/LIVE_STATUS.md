# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-18 12:53:40 UTC**

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
| Current job | idle |
| Queued | 1 |
| Done | 51 / 65 |
| Vectors in nrt_video_transcripts | 241 |

## System
| Metric | Value |
|---|---|
| RAM used | 2.99 GB / 32.86 GB (9%) |
| CPU | 6.9% |
| Disk used | 83.3 GB / 322.3 GB (27%) |
| Uptime | up 1 day, 7 hours, 18 minutes |

## Recent markers
- `2026-04-18T12:42:47` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (50/14)
- `2026-04-18T12:42:46` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED
- `2026-04-18T12:28:31` **transcription_done** — NRT_Fascial_Activation_Application_Method.mp4 complete (48/14)
- `2026-04-18T12:28:31` **ingest_failed** — NRT_Fascial_Activation_Application_Method.mp4 ingest FAILED
- `2026-04-18T11:58:17` **transcription_done** — NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows.mp4 complete (45/14)

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
2026-04-18 12:28:36,985  INFO      Transcribing 2 segments for NRT_Sports_Specific_or_Universal_Reset.mp4
2026-04-18 12:42:46,963  INFO      DONE   nrt/NRT_Sports_Specific_or_Universal_Reset.mp4  (856s, 2 segments)
2026-04-18 12:42:46,964  INFO      Stats updated: NRT_Sports_Specific_or_Universal_Reset.mp4 — 0.9s/MB  rate=2.0s/MB (17 samples)
2026-04-18 12:42:46,965  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/NRT_Sports_Specific_or_Universal_Reset.json
2026-04-18 12:42:47,095  INFO      START  nrt/NRT_for_Joint_Capsular_Ligaments_and_Tendons_Using_Direction_of_Ease_-_Demonstra.mp4  (639 MB)
2026-04-18 12:42:47,096  INFO      Splitting NRT_for_Joint_Capsular_Ligaments_and_Tendons_Using_Direction_of_Ease_-_Demonstra.mp4 (639 MB) into 20-min segments
2026-04-18 12:42:50,668  INFO      Split NRT_for_Joint_Capsular_Ligaments_and_Tendons_Using_Direction_of_Ease_-_Demonstra.mp4 into 1 segments
2026-04-18 12:53:36,142  INFO      DONE   nrt/NRT_for_Joint_Capsular_Ligaments_and_Tendons_Using_Direction_of_Ease_-_Demonstra.mp4  (649s)
2026-04-18 12:53:36,143  INFO      Stats updated: NRT_for_Joint_Capsular_Ligaments_and_Tendons_Using_Direction_of_Ease_-_Demonstra.mp4 — 1.0s/MB  rate=1.9s/MB (18 samples)
2026-04-18 12:53:36,144  INFO      INGEST nrt/NRT_for_Joint_Capsular_Ligaments_and_Tendons_Using_Direction_of_Ease_-_Demonstra.mp4
```
