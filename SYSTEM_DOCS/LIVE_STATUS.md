# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 10:26:04 UTC**

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
| Current job | `359609833-Travell-and-Simons-Myofascial-Pain-and-Dysfunction-Vol-1-2nd-Ed-D-Simons-Et-Al-Williams-and-Wilkins-1999-WW.pdf` (53 min) |
| Queued | 2 |
| Total books | 3 |
| Ingested | 1 |
| Vectors in medical_library | 2 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (650 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 11.42 GB / 32.86 GB (35%) |
| CPU | 26.2% |
| Disk used | 56.5 GB / 322.3 GB (18%) |
| Uptime | up 2 days, 43 minutes |

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
2026-04-16 10:21:12,251  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 10:21:42,253  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 10:22:12,254  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 10:22:42,256  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 10:23:12,257  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 10:23:42,258  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 10:24:12,259  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 10:24:42,260  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 10:25:12,262  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 10:25:42,266  INFO      Queue paused (pause flag set) — waiting 30s
```
