# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 08:18:30 UTC**

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
| Current job | `pdfcoffee.com_a-manual-of-acupuncture-peter-deadmanpdf-4-pdf-free.pdf` (80 min) |
| Queued | 0 |
| Total books | 3 |
| Ingested | 1 |
| Vectors in medical_library | 2 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (523 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 16.38 GB / 32.86 GB (50%) |
| CPU | 50.0% |
| Disk used | 56.5 GB / 322.3 GB (18%) |
| Uptime | up 1 day, 22 hours, 35 minutes |

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
2026-04-16 08:13:41,728  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 08:14:11,733  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 08:14:41,734  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 08:15:11,735  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 08:15:41,742  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 08:16:11,745  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 08:16:41,752  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 08:17:11,753  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 08:17:41,755  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 08:18:11,756  INFO      Queue paused (pause flag set) — waiting 30s
```
