# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-17 14:42:07 UTC**

## Services
| Service | Status |
|---|---|
| medical-rag-web | ✅ active |
| transcription-queue | ❌ inactive |
| book-ingest-queue | ✅ active |
| ttyd | ✅ active |
| qdrant | ✅ healthy |
| ollama | ✅ healthy |

## Book Ingest
| Metric | Value |
|---|---|
| Current job | `Bates' Guide To Physical Examination and History Taking_nodrm.epub` (3 min) |
| Queued | 6 |
| Total books | 57 |
| Ingested | 41 |
| Vectors in medical_library | 3680 |
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
| RAM used | 9.67 GB / 32.86 GB (29%) |
| CPU | 50.1% |
| Disk used | 60.6 GB / 322.3 GB (20%) |
| Uptime | up 9 hours, 6 minutes |

## Recent markers
- `2026-04-17T14:38:20.635476+00:00` **book_ingested** — Anatomy Trains_ Myofascial Meridians for Manual and Movement Therapists_nodrm.epub → medical_library: 432 chunks
- `2026-04-17T14:18:06` **queue_empty** — All 14 videos transcribed
- `2026-04-17T14:18:06` **transcription_failed** — NRT_for_Joint_Capsular_Ligaments_and_Tendons_Using_Direction_of_Ease_-_Demonstra.mp4 FAILED (21/14)
- `2026-04-17T14:18:06` **transcription_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 FAILED (21/14)
- `2026-04-17T14:18:06` **transcription_failed** — NRT_Fascial_Activation_Application_Method.mp4 FAILED (21/14)

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
2026-04-17 14:18:06,352  WARNING   Skipping nrt/Everything_Reset_Sequence_-_Part_4.mp4 (690 MB > limit 400 MB)
2026-04-17 14:18:06,417  WARNING   Skipping nrt/Everything_Reset_Sequence_-_Part_5.mp4 (618 MB > limit 400 MB)
2026-04-17 14:18:06,482  WARNING   Skipping nrt/Miraculous_Sequence_-_Part_1.mp4 (689 MB > limit 400 MB)
2026-04-17 14:18:06,548  WARNING   Skipping nrt/Miraculous_Sequence_-_Part_2.mp4 (664 MB > limit 400 MB)
2026-04-17 14:18:06,613  WARNING   Skipping nrt/NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows.mp4 (990 MB > limit 400 MB)
2026-04-17 14:18:06,678  WARNING   Skipping nrt/NRT_Fascial_Activation_Application_Method.mp4 (1871 MB > limit 400 MB)
2026-04-17 14:18:06,748  WARNING   Skipping nrt/NRT_Sports_Specific_or_Universal_Reset.mp4 (957 MB > limit 400 MB)
2026-04-17 14:18:06,814  WARNING   Skipping nrt/NRT_for_Joint_Capsular_Ligaments_and_Tendons_Using_Direction_of_Ease_-_Demonstra.mp4 (639 MB > limit 400 MB)
2026-04-17 14:18:06,846  INFO      Queue empty — 14 video(s) processed. Exiting.
2026-04-17 14:18:06,911  INFO      Transcription queue manager done
```
