# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-17 13:47:01 UTC**

## Services
| Service | Status |
|---|---|
| medical-rag-web | ✅ active |
| transcription-queue | ❌ inactive |
| book-ingest-queue | ❌ inactive |
| ttyd | ✅ active |
| qdrant | ✅ healthy |
| ollama | ✅ healthy |

## Book Ingest
| Metric | Value |
|---|---|
| Current job | idle |
| Queued | 0 |
| Total books | 49 |
| Ingested | 40 |
| Vectors in medical_library | 3248 |
| Images pending approval | 2026 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | idle |
| Queued | 0 |
| Done | 21 / 35 |
| Vectors in video_transcripts | 241 |

## System
| Metric | Value |
|---|---|
| RAM used | 2.52 GB / 32.86 GB (8%) |
| CPU | 0.0% |
| Disk used | 59.4 GB / 322.3 GB (19%) |
| Uptime | up 8 hours, 11 minutes |

## Recent markers
- `2026-04-17T13:09:22` **queue_empty** — All 19 videos transcribed
- `2026-04-17T13:09:22` **transcription_failed** — 1.Upper_Body_Techniques.mp4 FAILED (21/19)
- `2026-04-17T13:09:22` **transcription_failed** — NRT_for_Joint_Capsular_Ligaments_and_Tendons_Using_Direction_of_Ease_-_Demonstra.mp4 FAILED (21/19)
- `2026-04-17T13:09:22` **transcription_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 FAILED (21/19)
- `2026-04-17T13:09:22` **transcription_failed** — NRT_Fascial_Activation_Application_Method.mp4 FAILED (21/19)

## Nightly Consistency
```
  TRANSCRIPT ONTBREEKT IN QDRANT: Organs_and_Glands_Review.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Pair_Balancing.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Neuromuscular_ReEducation.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_3.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Anti-Inflammatory_Procedure.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_1.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Indicator_Muscle.json (type: qat)
  BOEK ONTBREEKT IN QDRANT: test_acupuncture.pdf (collectie: medical_library)
```

## Queue log (last 10 lines)
```
2026-04-17 13:09:21,803  WARNING   Skipping nrt/How_to_Reset_23_More_Muscles.mp4 (412 MB > limit 400 MB)
2026-04-17 13:09:21,868  WARNING   Skipping nrt/Miraculous_Sequence_-_Part_1.mp4 (689 MB > limit 400 MB)
2026-04-17 13:09:21,934  WARNING   Skipping nrt/Miraculous_Sequence_-_Part_2.mp4 (664 MB > limit 400 MB)
2026-04-17 13:09:22,000  WARNING   Skipping nrt/NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows.mp4 (990 MB > limit 400 MB)
2026-04-17 13:09:22,065  WARNING   Skipping nrt/NRT_Fascial_Activation_Application_Method.mp4 (1871 MB > limit 400 MB)
2026-04-17 13:09:22,130  WARNING   Skipping nrt/NRT_Sports_Specific_or_Universal_Reset.mp4 (957 MB > limit 400 MB)
2026-04-17 13:09:22,195  WARNING   Skipping nrt/NRT_for_Joint_Capsular_Ligaments_and_Tendons_Using_Direction_of_Ease_-_Demonstra.mp4 (639 MB > limit 400 MB)
2026-04-17 13:09:22,261  WARNING   Skipping nrt/1.Upper_Body_Techniques.mp4 (in skip_files list)
2026-04-17 13:09:22,325  INFO      Queue empty — 19 video(s) processed. Exiting.
2026-04-17 13:09:22,390  INFO      Transcription queue manager done
```
