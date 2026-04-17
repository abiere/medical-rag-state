# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-17 07:26:40 UTC**

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
| Queued | 4 |
| Total books | 43 |
| Ingested | 35 |
| Vectors in medical_library | 2775 |
| Images pending approval | 1110 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `16_Expanded__Revised__and_New_Techniques.mp4` (6 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 14.85 GB / 32.86 GB (45%) |
| CPU | 98.9% |
| Disk used | 59.0 GB / 322.3 GB (19%) |
| Uptime | up 1 hour, 51 minutes |

## Recent markers
- `2026-04-17T07:20:40.911856+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T06:50:39.257058+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T06:20:36.837379+00:00` **watchdog_restart** — transcription-queue hung (37 min stale) — restarted successfully
- `2026-04-17T05:44:05` **transcription_failed** — 1.Upper_Body_Techniques.mp4 FAILED (16/19)
- `2026-04-17T05:10:41.112457+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully

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
2026-04-17 06:20:36,879  INFO      Startup scan: 19 untranscribed video(s) found, 1 new entry/entries added to queue
2026-04-17 06:20:36,880  INFO      START  nrt/16_Expanded__Revised__and_New_Techniques.mp4
2026-04-17 06:50:39,300  INFO      ────────────────────────────────────────────────────────────
2026-04-17 06:50:39,300  INFO      Transcription queue manager started
2026-04-17 06:50:39,301  INFO      Startup scan: 19 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 06:50:39,301  INFO      START  nrt/16_Expanded__Revised__and_New_Techniques.mp4
2026-04-17 07:20:40,958  INFO      ────────────────────────────────────────────────────────────
2026-04-17 07:20:40,958  INFO      Transcription queue manager started
2026-04-17 07:20:40,960  INFO      Startup scan: 19 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 07:20:40,960  INFO      START  nrt/16_Expanded__Revised__and_New_Techniques.mp4
```
