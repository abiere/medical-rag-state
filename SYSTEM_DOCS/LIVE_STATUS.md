# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 09:32:28 UTC**

## Services
| Service | Status |
|---|---|
| medical-rag-web | ✅ active |
| transcription-queue | ✅ active |
| book-ingest-queue | ⚠️ deactivating |
| ttyd | ✅ active |
| qdrant | ✅ healthy |
| ollama | ✅ healthy |

## Book Ingest
| Metric | Value |
|---|---|
| Current job | `pdfcoffee.com_a-manual-of-acupuncture-peter-deadmanpdf-4-pdf-free.pdf` (154 min) |
| Queued | 0 |
| Total books | 3 |
| Ingested | 1 |
| Vectors in medical_library | 2 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (597 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 13.35 GB / 32.86 GB (41%) |
| CPU | 50.8% |
| Disk used | 56.5 GB / 322.3 GB (18%) |
| Uptime | up 1 day, 23 hours, 49 minutes |

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
2026-04-16 09:27:42,045  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 09:28:12,047  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 09:28:42,049  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 09:29:12,053  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 09:29:42,057  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 09:30:12,059  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 09:30:42,063  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 09:31:12,071  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 09:31:42,072  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 09:32:12,074  INFO      Queue paused (pause flag set) — waiting 30s
```
