# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-17 08:36:42 UTC**

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
| Current job | `03_trail_guide_to_the_body_6th.pdf` |
| Queued | 0 |
| Total books | 43 |
| Ingested | 35 |
| Vectors in medical_library | 2775 |
| Images pending approval | 2026 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `16_Expanded__Revised__and_New_Techniques.mp4` (16 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 7.93 GB / 32.86 GB (24%) |
| CPU | 100.0% |
| Disk used | 59.1 GB / 322.3 GB (19%) |
| Uptime | up 3 hours, 1 minute |

## Recent markers
- `2026-04-17T08:20:41.806276+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T07:50:41.516186+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T07:20:40.911856+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T06:50:39.257058+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T06:20:36.837379+00:00` **watchdog_restart** — transcription-queue hung (37 min stale) — restarted successfully

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
2026-04-17 07:20:40,960  INFO      Startup scan: 19 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 07:20:40,960  INFO      START  nrt/16_Expanded__Revised__and_New_Techniques.mp4
2026-04-17 07:50:41,556  INFO      ────────────────────────────────────────────────────────────
2026-04-17 07:50:41,556  INFO      Transcription queue manager started
2026-04-17 07:50:41,557  INFO      Startup scan: 19 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 07:50:41,558  INFO      START  nrt/16_Expanded__Revised__and_New_Techniques.mp4
2026-04-17 08:20:41,853  INFO      ────────────────────────────────────────────────────────────
2026-04-17 08:20:41,853  INFO      Transcription queue manager started
2026-04-17 08:20:41,855  INFO      Startup scan: 19 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 08:20:41,855  INFO      START  nrt/16_Expanded__Revised__and_New_Techniques.mp4
```
