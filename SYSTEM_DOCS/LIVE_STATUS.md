# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-17 13:06:55 UTC**

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
| Total books | 49 |
| Ingested | 40 |
| Vectors in medical_library | 3248 |
| Images pending approval | 2026 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `Healing_Organs_with_NRT.mp4` (4 min) |
| Queued | 9 |
| Done | 20 / 35 |
| Vectors in video_transcripts | 231 |

## System
| Metric | Value |
|---|---|
| RAM used | 6.7 GB / 32.86 GB (20%) |
| CPU | 96.4% |
| Disk used | 59.4 GB / 322.3 GB (19%) |
| Uptime | up 7 hours, 31 minutes |

## Recent markers
- `2026-04-17T13:02:09` **transcription_failed** — Everything_Reset_Sequence_-_Part_5.mp4 FAILED (20/19)
- `2026-04-17T13:02:09` **transcription_failed** — Everything_Reset_Sequence_-_Part_4.mp4 FAILED (20/19)
- `2026-04-17T13:02:09` **transcription_failed** — Everything_Reset_Sequence_-_Part_3.mp4 FAILED (20/19)
- `2026-04-17T13:02:09` **transcription_failed** — Everything_Reset_Sequence_-_Part_2.mp4 FAILED (20/19)
- `2026-04-17T13:02:09` **transcription_failed** — Everything_Reset_Sequence_-_Part_1.mp4 FAILED (20/19)

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
2026-04-17 13:02:09,065  INFO        [ingest] 3.Why_People_Hurt.json: 867 segments → 23 chunks
2026-04-17 13:02:09,065  INFO        [ingest] Loading embedding model …
2026-04-17 13:02:09,065  INFO        [ingest]   Ingested chunk 23/23 for 3.Why_People_Hurt.mp4
2026-04-17 13:02:09,066  INFO        [ingest] Done: 23 chunks ingested, 0 skipped (already exists)
2026-04-17 13:02:09,194  WARNING   Skipping nrt/Everything_Reset_Sequence_-_Part_1.mp4 (649 MB > limit 400 MB)
2026-04-17 13:02:09,259  WARNING   Skipping nrt/Everything_Reset_Sequence_-_Part_2.mp4 (499 MB > limit 400 MB)
2026-04-17 13:02:09,324  WARNING   Skipping nrt/Everything_Reset_Sequence_-_Part_3.mp4 (565 MB > limit 400 MB)
2026-04-17 13:02:09,389  WARNING   Skipping nrt/Everything_Reset_Sequence_-_Part_4.mp4 (690 MB > limit 400 MB)
2026-04-17 13:02:09,454  WARNING   Skipping nrt/Everything_Reset_Sequence_-_Part_5.mp4 (618 MB > limit 400 MB)
2026-04-17 13:02:09,520  INFO      START  nrt/Healing_Organs_with_NRT.mp4
```
