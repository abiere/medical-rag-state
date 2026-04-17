# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-17 23:02:16 UTC**

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
| Current job | `CranioSacral Therapy Study Guide - Upledger.pdf` (13 min) |
| Queued | 10 |
| Total books | 37 |
| Ingested | 63 |
| Vectors in medical_library | 13596 |
| Images pending approval | 2026 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4` (21 min) |
| Queued | 14 |
| Done | 21 / 37 |
| Vectors in nrt_video_transcripts | 241 |

## System
| Metric | Value |
|---|---|
| RAM used | 11.97 GB / 32.86 GB (36%) |
| CPU | 99.8% |
| Disk used | 69.9 GB / 322.3 GB (23%) |
| Uptime | up 17 hours, 26 minutes |

## Recent markers
- `2026-04-17T22:48:20.513980+00:00` **book_ingested** — Bates Guide to Physical Examination 14e editie - Bickley.epub → medical_library: 1251 chunks
- `2026-04-17T22:41:16.080646+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T22:11:15.512026+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T22:09:11.097173+00:00` **book_ingested** — Applied Kinesiology - Frost.pdf → medical_library: 409 chunks
- `2026-04-17T21:41:15.153527+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully

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
2026-04-17 22:11:15,552  INFO      Startup scan: 14 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 22:11:15,552  INFO      START  nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (1060 MB)
2026-04-17 22:11:15,552  INFO      Using existing segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4: 2 parts
2026-04-17 22:11:15,553  INFO      Transcribing 2 segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4
2026-04-17 22:41:16,145  INFO      ────────────────────────────────────────────────────────────
2026-04-17 22:41:16,146  INFO      Transcription queue manager started
2026-04-17 22:41:16,148  INFO      Startup scan: 14 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 22:41:16,149  INFO      START  nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (1060 MB)
2026-04-17 22:41:16,150  INFO      Using existing segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4: 2 parts
2026-04-17 22:41:16,150  INFO      Transcribing 2 segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4
```
