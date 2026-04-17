# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-17 13:01:54 UTC**

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
| Current job | idle |
| Queued | 14 |
| Done | 20 / 35 |
| Vectors in video_transcripts | 208 |

## System
| Metric | Value |
|---|---|
| RAM used | 3.01 GB / 32.86 GB (9%) |
| CPU | 6.3% |
| Disk used | 59.4 GB / 322.3 GB (19%) |
| Uptime | up 7 hours, 26 minutes |

## Recent markers
- `2026-04-17T12:42:00` **transcription_failed** — 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4 FAILED (19/19)
- `2026-04-17T12:42:00` **transcription_done** — 2.Upper_Body_Fundamentals.mp4 complete (19/19)
- `2026-04-17T12:42:00` **transcript_ingested** — 2.Upper_Body_Fundamentals.mp4 ingested into Qdrant
- `2026-04-17T12:21:57` **transcription_done** — 2.Lower_Body_Fundamentals.mp4 complete (18/19)
- `2026-04-17T12:21:57` **transcript_ingested** — 2.Lower_Body_Fundamentals.mp4 ingested into Qdrant

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
2026-04-17 12:41:42,254  INFO      INGEST nrt/2.Upper_Body_Fundamentals.mp4
2026-04-17 12:42:00,352  INFO        [ingest] 2.Upper_Body_Fundamentals.json: 758 segments → 22 chunks
2026-04-17 12:42:00,352  INFO        [ingest] Loading embedding model …
2026-04-17 12:42:00,352  INFO        [ingest]   Ingested chunk 19/19 for 2.Upper_Body_Fundamentals.mp4
2026-04-17 12:42:00,352  INFO        [ingest] Done: 19 chunks ingested, 3 skipped (already exists)
2026-04-17 12:42:00,482  WARNING   Skipping nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4 (1060 MB > limit 400 MB)
2026-04-17 12:42:00,547  INFO      START  nrt/3.Why_People_Hurt.mp4
2026-04-17 13:01:49,770  INFO      DONE   nrt/3.Why_People_Hurt.mp4  (1189s)
2026-04-17 13:01:49,771  INFO      Stats updated: 3.Why_People_Hurt.mp4 — 6.4s/MB  rate=4.0s/MB (4 samples)
2026-04-17 13:01:49,772  INFO      INGEST nrt/3.Why_People_Hurt.mp4
```
