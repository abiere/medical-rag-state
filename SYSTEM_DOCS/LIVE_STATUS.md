# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 14:10:04 UTC**

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
| Current job | `969553977-Trail-Guide-to-the-Body-6th-Edition-Andrew-Biel.pdf` (5 min) |
| Queued | 2 |
| Total books | 3 |
| Ingested | 1 |
| Vectors in medical_library | 2 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (874 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 10.62 GB / 32.86 GB (32%) |
| CPU | 6.3% |
| Disk used | 58.1 GB / 322.3 GB (19%) |
| Uptime | up 2 days, 4 hours, 27 minutes |

## Recent markers
- `2026-04-16T05:20:54.750223+00:00` **watchdog_restart** — book-ingest-queue hung (41 min stale) — restarted successfully
- `2026-04-16T04:40:08.074792+00:00` **watchdog_restart** — book-ingest-queue hung (31 min stale) — restarted successfully
- `2026-04-16T04:09:34.281903+00:00` **watchdog_restart** — book-ingest-queue hung (32 min stale) — restarted successfully
- `2026-04-16T03:37:44.605626+00:00` **watchdog_restart** — book-ingest-queue hung (32 min stale) — restarted successfully
- `2026-04-16T03:05:56.398437+00:00` **watchdog_restart** — book-ingest-queue hung (31 min stale) — restarted successfully

## Nightly Consistency
```
  TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_2.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Organs_and_Glands_Review.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Pair_Balancing.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Neuromuscular_ReEducation.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_3.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Anti-Inflammatory_Procedure.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_1.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Indicator_Muscle.json (type: qat)
```

## Queue log (last 10 lines)
```
2026-04-16 14:05:13,219  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 14:05:43,220  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 14:06:13,221  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 14:06:43,222  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 14:07:13,223  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 14:07:43,226  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 14:08:13,228  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 14:08:43,231  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 14:09:13,232  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 14:09:43,234  INFO      Queue paused (pause flag set) — waiting 30s
```
