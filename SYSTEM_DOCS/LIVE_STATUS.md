# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 06:37:44 UTC**

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
| Current job | `969553977-Trail-Guide-to-the-Body-6th-Edition-Andrew-Biel.pdf` (4 min) |
| Queued | 1 |
| Total books | 3 |
| Ingested | 1 |
| Vectors in medical_library | 2 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (422 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 3.49 GB / 32.86 GB (11%) |
| CPU | 6.5% |
| Disk used | 54.7 GB / 322.3 GB (18%) |
| Uptime | up 1 day, 20 hours, 54 minutes |

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
2026-04-16 06:33:11,417  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 06:33:41,418  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 06:34:11,419  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 06:34:41,420  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 06:35:11,422  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 06:35:41,424  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 06:36:11,425  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 06:36:41,427  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 06:37:11,428  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 06:37:41,430  INFO      Queue paused (pause flag set) — waiting 30s
```
