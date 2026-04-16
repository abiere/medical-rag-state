# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 14:51:54 UTC**

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
| Current job | `01_deadman_manual_of_acupuncture.pdf` (13 min) |
| Queued | 2 |
| Total books | 3 |
| Ingested | 1 |
| Vectors in medical_library | ? |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (916 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 11.45 GB / 32.86 GB (35%) |
| CPU | 25.2% |
| Disk used | 55.7 GB / 322.3 GB (18%) |
| Uptime | up 2 days, 5 hours, 9 minutes |

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
2026-04-16 14:47:16,754  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 14:47:46,755  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 14:48:16,756  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 14:48:46,759  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 14:49:16,762  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 14:49:46,763  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 14:50:16,764  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 14:50:46,767  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 14:51:16,769  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 14:51:46,772  INFO      Queue paused (pause flag set) — waiting 30s
```
