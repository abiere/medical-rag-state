# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-19 00:36:08 UTC**

## Services
| Service | Status |
|---|---|
| medical-rag-web | ✅ active |
| transcription-queue | ✅ active |
| book-ingest-queue | ✅ active |
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
| Vectors in medical_library | 17522 |
| Images pending approval | 2026 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | idle |
| Queued | 13 |
| Done | 55 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 3.62 GB / 32.86 GB (11%) |
| CPU | 90.2% |
| Disk used | 84.4 GB / 322.3 GB (27%) |
| Uptime | up 1 day, 19 hours, 0 minutes |

## Recent markers
- `2026-04-19T00:31:42` **queue_empty** — All 13 videos transcribed
- `2026-04-19T00:31:42` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-04-19T00:31:42` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED
- `2026-04-19T00:31:42` **transcription_done** — NRT_Fascial_Activation_Application_Method.mp4 complete (55/13)
- `2026-04-19T00:31:42` **ingest_failed** — NRT_Fascial_Activation_Application_Method.mp4 ingest FAILED

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
2026-04-19 00:32:12,709  INFO      Transcription queue manager started
2026-04-19 00:32:12,711  INFO      Startup scan: 13 untranscribed video(s) found, 13 new entry/entries added to queue
2026-04-19 00:32:12,711  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-19 00:32:42,712  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-19 00:33:12,712  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-19 00:33:42,712  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-19 00:34:12,713  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-19 00:34:42,714  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-19 00:35:12,714  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-19 00:35:42,714  INFO      Queue paused (pause flag set) — waiting 30s
```
