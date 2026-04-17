# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-17 12:41:51 UTC**

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
| Queued | 16 |
| Done | 19 / 35 |
| Vectors in video_transcripts | 189 |

## System
| Metric | Value |
|---|---|
| RAM used | 3.59 GB / 32.86 GB (11%) |
| CPU | 90.3% |
| Disk used | 59.4 GB / 322.3 GB (19%) |
| Uptime | up 7 hours, 6 minutes |

## Recent markers
- `2026-04-17T12:21:57` **transcription_done** — 2.Lower_Body_Fundamentals.mp4 complete (18/19)
- `2026-04-17T12:21:57` **transcript_ingested** — 2.Lower_Body_Fundamentals.mp4 ingested into Qdrant
- `2026-04-17T12:04:36` **transcription_done** — 16_Expanded__Revised__and_New_Techniques.mp4 complete (17/19)
- `2026-04-17T12:04:36` **transcript_ingested** — 16_Expanded__Revised__and_New_Techniques.mp4 ingested into Qdrant
- `2026-04-17T11:50:45.413111+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully

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
2026-04-17 12:21:39,619  INFO      Stats updated: 2.Lower_Body_Fundamentals.mp4 — 3.7s/MB  rate=2.9s/MB (2 samples)
2026-04-17 12:21:39,620  INFO      INGEST nrt/2.Lower_Body_Fundamentals.mp4
2026-04-17 12:21:57,263  INFO        [ingest] 2.Lower_Body_Fundamentals.json: 621 segments → 19 chunks
2026-04-17 12:21:57,263  INFO        [ingest] Loading embedding model …
2026-04-17 12:21:57,263  INFO        [ingest]   Ingested chunk 19/19 for 2.Lower_Body_Fundamentals.mp4
2026-04-17 12:21:57,264  INFO        [ingest] Done: 19 chunks ingested, 0 skipped (already exists)
2026-04-17 12:21:57,360  INFO      START  nrt/2.Upper_Body_Fundamentals.mp4
2026-04-17 12:41:42,253  INFO      DONE   nrt/2.Upper_Body_Fundamentals.mp4  (1185s)
2026-04-17 12:41:42,254  INFO      Stats updated: 2.Upper_Body_Fundamentals.mp4 — 3.7s/MB  rate=3.2s/MB (3 samples)
2026-04-17 12:41:42,254  INFO      INGEST nrt/2.Upper_Body_Fundamentals.mp4
```
