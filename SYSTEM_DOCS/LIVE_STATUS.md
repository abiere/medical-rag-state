# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 06:48:14 UTC**

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
| Current job | `969553977-Trail-Guide-to-the-Body-6th-Edition-Andrew-Biel.pdf` (15 min) |
| Queued | 1 |
| Total books | 3 |
| Ingested | 1 |
| Vectors in medical_library | 2 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (432 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 3.6 GB / 32.86 GB (11%) |
| CPU | 6.4% |
| Disk used | 55.2 GB / 322.3 GB (18%) |
| Uptime | up 1 day, 21 hours, 5 minutes |

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
2026-04-16 06:43:41,446  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 06:44:11,447  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 06:44:41,449  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 06:45:11,450  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 06:45:41,451  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 06:46:11,452  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 06:46:41,453  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 06:47:11,454  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 06:47:41,456  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 06:48:11,457  INFO      Queue paused (pause flag set) — waiting 30s
```
