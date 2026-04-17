# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-17 04:17:40 UTC**

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
| Current job | `03_trail_guide_to_the_body_6th.pdf` (751 min) |
| Queued | 4 |
| Total books | 43 |
| Ingested | 35 |
| Vectors in medical_library | 2775 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (7 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 7.63 GB / 32.86 GB (23%) |
| CPU | 100.0% |
| Disk used | 60.5 GB / 322.3 GB (20%) |
| Uptime | up 2 days, 18 hours, 34 minutes |

## Recent markers
- `2026-04-17T04:10:40.086977+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T03:40:39.748279+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T03:10:39.008697+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T02:40:38.516593+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T02:10:37.998700+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully

## Nightly Consistency
```
  TRANSCRIPT ONTBREEKT IN QDRANT: Organs_and_Glands_Review.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Pair_Balancing.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Neuromuscular_ReEducation.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_3.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Anti-Inflammatory_Procedure.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_1.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Indicator_Muscle.json (type: qat)
  BOEK ONTBREEKT IN QDRANT: test_acupuncture.pdf (collectie: medical_library)
```

## Queue log (last 10 lines)
```
2026-04-17 03:10:39,048  INFO      Startup scan: 19 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 03:10:39,048  INFO      START  nrt/1.Upper_Body_Techniques.mp4
2026-04-17 03:40:39,795  INFO      ────────────────────────────────────────────────────────────
2026-04-17 03:40:39,795  INFO      Transcription queue manager started
2026-04-17 03:40:39,796  INFO      Startup scan: 19 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 03:40:39,797  INFO      START  nrt/1.Upper_Body_Techniques.mp4
2026-04-17 04:10:40,127  INFO      ────────────────────────────────────────────────────────────
2026-04-17 04:10:40,128  INFO      Transcription queue manager started
2026-04-17 04:10:40,129  INFO      Startup scan: 19 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 04:10:40,129  INFO      START  nrt/1.Upper_Body_Techniques.mp4
```
