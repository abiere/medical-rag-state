# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-17 05:46:35 UTC**

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
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `16_Expanded__Revised__and_New_Techniques.mp4` (2 min) |
| Queued | 18 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 6.47 GB / 32.86 GB (20%) |
| CPU | 100.0% |
| Disk used | 58.9 GB / 322.3 GB (19%) |
| Uptime | up 11 minutes |

## Recent markers
- `2026-04-17T05:44:05` **transcription_failed** — 1.Upper_Body_Techniques.mp4 FAILED (16/19)
- `2026-04-17T05:10:41.112457+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T04:40:40.581705+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T04:10:40.086977+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T03:40:39.748279+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully

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
2026-04-17 05:34:41,575  INFO      START  nrt/1.Upper_Body_Techniques.mp4
2026-04-17 05:35:34,588  INFO      ────────────────────────────────────────────────────────────
2026-04-17 05:35:34,588  INFO      Transcription queue manager started
2026-04-17 05:35:34,592  INFO      Startup scan: 19 untranscribed video(s) found, 19 new entry/entries added to queue
2026-04-17 05:35:34,592  INFO      START  nrt/1.Upper_Body_Techniques.mp4
2026-04-17 05:44:05,765  INFO      ────────────────────────────────────────────────────────────
2026-04-17 05:44:05,766  INFO      Transcription queue manager started
2026-04-17 05:44:05,768  INFO      Startup scan: 19 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 05:44:05,768  WARNING   Skipping nrt/1.Upper_Body_Techniques.mp4 (in skip_files list)
2026-04-17 05:44:05,836  INFO      START  nrt/16_Expanded__Revised__and_New_Techniques.mp4
```
