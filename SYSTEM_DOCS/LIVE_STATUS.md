# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 14:41:44 UTC**

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
| Current job | `01_deadman_manual_of_acupuncture.pdf` (3 min) |
| Queued | 2 |
| Total books | 3 |
| Ingested | 1 |
| Vectors in medical_library | ? |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (906 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 8.01 GB / 32.86 GB (24%) |
| CPU | 41.7% |
| Disk used | 55.7 GB / 322.3 GB (18%) |
| Uptime | up 2 days, 4 hours, 58 minutes |

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
2026-04-16 14:38:16,716  INFO      ────────────────────────────────────────────────────────────
2026-04-16 14:38:16,717  INFO      Transcription queue manager started
2026-04-16 14:38:16,721  INFO      Startup scan: 19 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-16 14:38:16,724  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 14:38:46,726  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 14:39:16,728  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 14:39:46,730  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 14:40:16,732  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 14:40:46,733  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 14:41:16,734  INFO      Queue paused (pause flag set) — waiting 30s
```
