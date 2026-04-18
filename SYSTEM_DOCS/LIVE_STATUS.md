# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-18 13:08:24 UTC**

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
| Current job | `1.Upper_Body_Techniques.mp4` (14 min) |
| Queued | 1 |
| Done | 51 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 6.75 GB / 32.86 GB (20%) |
| CPU | 95.5% |
| Disk used | 83.9 GB / 322.3 GB (27%) |
| Uptime | up 1 day, 7 hours, 33 minutes |

## Recent markers
- `2026-04-18T12:53:54` **transcription_done** — NRT_for_Joint_Capsular_Ligaments_and_Tendons_Using_Direction_of_Ease_-_Demonstra.mp4 complete (51/14)
- `2026-04-18T12:53:54` **transcript_ingested** — NRT_for_Joint_Capsular_Ligaments_and_Tendons_Using_Direction_of_Ease_-_Demonstra.mp4 ingested into Qdrant
- `2026-04-18T12:42:47` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (50/14)
- `2026-04-18T12:42:46` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED
- `2026-04-18T12:28:31` **transcription_done** — NRT_Fascial_Activation_Application_Method.mp4 complete (48/14)

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
2026-04-18 12:53:36,144  INFO      INGEST nrt/NRT_for_Joint_Capsular_Ligaments_and_Tendons_Using_Direction_of_Ease_-_Demonstra.mp4
2026-04-18 12:53:54,719  INFO        [ingest] NRT_for_Joint_Capsular_Ligaments_and_Tendons_Using_Direction_of_Ease_-_Demonstra.json: 320 segments → 9 chunks
2026-04-18 12:53:54,719  INFO        [ingest] Loading embedding model …
2026-04-18 12:53:54,719  INFO        [ingest] Target collection: nrt_video_transcripts
2026-04-18 12:53:54,719  INFO        [ingest]   Ingested chunk 9/9 for NRT_for_Joint_Capsular_Ligaments_and_Tendons_Using_Direction_of_Ease_-_Demonstra.mp4
2026-04-18 12:53:54,719  INFO        [ingest] Done: 9 chunks ingested, 0 skipped (already exists)
2026-04-18 12:53:54,849  INFO      START  nrt/1.Upper_Body_Techniques.mp4  (525 MB)
2026-04-18 12:53:54,850  INFO      Splitting 1.Upper_Body_Techniques.mp4 (525 MB) into 20-min segments
2026-04-18 12:54:06,632  INFO      Split 1.Upper_Body_Techniques.mp4 into 4 segments
2026-04-18 12:54:06,632  INFO      Transcribing 4 segments for 1.Upper_Body_Techniques.mp4
```
