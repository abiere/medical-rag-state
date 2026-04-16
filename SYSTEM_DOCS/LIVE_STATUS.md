# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 15:12:19 UTC**

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
| Current job | `01_deadman_manual_of_acupuncture.pdf` (34 min) |
| Queued | 2 |
| Total books | 3 |
| Ingested | 1 |
| Vectors in medical_library | ? |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (936 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 9.84 GB / 32.86 GB (30%) |
| CPU | 20.6% |
| Disk used | 55.7 GB / 322.3 GB (18%) |
| Uptime | up 2 days, 5 hours, 29 minutes |

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
2026-04-16 15:07:46,822  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 15:08:16,824  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 15:08:46,827  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 15:09:16,829  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 15:09:46,830  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 15:10:16,830  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 15:10:46,832  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 15:11:16,833  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 15:11:46,835  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 15:12:16,836  INFO      Queue paused (pause flag set) — waiting 30s
```
