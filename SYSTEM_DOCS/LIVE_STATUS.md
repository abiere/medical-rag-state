# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 17:52:27 UTC**

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
| Current job | `02_travell_simons_myofascial_pain_vol1.pdf` |
| Queued | 40 |
| Total books | 43 |
| Ingested | 2 |
| Vectors in medical_library | 1013 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (1097 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 4.32 GB / 32.86 GB (13%) |
| CPU | 84.4% |
| Disk used | 58.5 GB / 322.3 GB (19%) |
| Uptime | up 2 days, 8 hours, 9 minutes |

## Recent markers
- `2026-04-16T17:08:48.701647+00:00` **book_ingested** — 01_deadman_manual_of_acupuncture.pdf → medical_library: 1013 chunks
- `2026-04-16T05:20:54.750223+00:00` **watchdog_restart** — book-ingest-queue hung (41 min stale) — restarted successfully
- `2026-04-16T04:40:08.074792+00:00` **watchdog_restart** — book-ingest-queue hung (31 min stale) — restarted successfully
- `2026-04-16T04:09:34.281903+00:00` **watchdog_restart** — book-ingest-queue hung (32 min stale) — restarted successfully
- `2026-04-16T03:37:44.605626+00:00` **watchdog_restart** — book-ingest-queue hung (32 min stale) — restarted successfully

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
2026-04-16 17:47:47,472  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 17:48:17,473  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 17:48:47,474  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 17:49:17,477  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 17:49:47,478  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 17:50:17,478  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 17:50:47,480  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 17:51:17,483  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 17:51:47,484  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 17:52:17,485  INFO      Queue paused (pause flag set) — waiting 30s
```
