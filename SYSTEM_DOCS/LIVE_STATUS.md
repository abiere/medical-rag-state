# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 16:02:22 UTC**

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
| Current job | `03_trail_guide_to_the_body_6th.pdf` (16 min) |
| Queued | 2 |
| Total books | 3 |
| Ingested | 1 |
| Vectors in medical_library | ? |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (986 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 4.14 GB / 32.86 GB (13%) |
| CPU | 13.7% |
| Disk used | 56.4 GB / 322.3 GB (18%) |
| Uptime | up 2 days, 6 hours, 19 minutes |

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
2026-04-16 15:57:47,076  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 15:58:17,077  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 15:58:47,079  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 15:59:17,080  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 15:59:47,081  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 16:00:17,084  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 16:00:47,085  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 16:01:17,089  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 16:01:47,091  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 16:02:17,093  INFO      Queue paused (pause flag set) — waiting 30s
```
