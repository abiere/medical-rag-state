# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 16:22:23 UTC**

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
| Current job | `01_deadman_manual_of_acupuncture.pdf` |
| Queued | 41 |
| Total books | 43 |
| Ingested | 1 |
| Vectors in medical_library | ? |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (1006 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 3.94 GB / 32.86 GB (12%) |
| CPU | 8.9% |
| Disk used | 58.3 GB / 322.3 GB (19%) |
| Uptime | up 2 days, 6 hours, 39 minutes |

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
2026-04-16 16:17:47,143  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 16:18:17,145  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 16:18:47,146  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 16:19:17,147  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 16:19:47,148  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 16:20:17,149  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 16:20:47,152  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 16:21:17,154  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 16:21:47,156  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 16:22:17,157  INFO      Queue paused (pause flag set) — waiting 30s
```
