# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-18 07:17:27 UTC**

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
| Current job | `dokumen.pub_atlas-of-acupuncture-1nbsped-0443100284-9780443100284.pdf` (455 min) |
| Queued | 10 |
| Total books | 37 |
| Ingested | 73 |
| Vectors in medical_library | 18251 |
| Images pending approval | 2026 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4` (6 min) |
| Queued | 14 |
| Done | 21 / 37 |
| Vectors in nrt_video_transcripts | 241 |

## System
| Metric | Value |
|---|---|
| RAM used | 9.4 GB / 32.86 GB (29%) |
| CPU | 100.0% |
| Disk used | 73.4 GB / 322.3 GB (24%) |
| Uptime | up 1 day, 1 hour, 42 minutes |

## Recent markers
- `2026-04-18T07:11:27.682421+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-18T07:10:06.627685+00:00` **book_ingested** — Orthopedic Physical Assessment 7e editie - Magee, Manske.epub → medical_library: 1566 chunks
- `2026-04-18T06:41:26.724209+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-18T06:13:48.384840+00:00` **book_ingested** — Mobilizing the Myofascial System - Killens, Lee.pdf → medical_library: 379 chunks
- `2026-04-18T06:11:26.142009+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully

## Nightly Consistency
```
  TRANSCRIPT ONTBREEKT IN QDRANT: Organs_and_Glands_Review.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: 2.Lower_Body_Fundamentals.json (type: nrt)
  TRANSCRIPT ONTBREEKT IN QDRANT: Pair_Balancing.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Neuromuscular_ReEducation.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_3.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Anti-Inflammatory_Procedure.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_1.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Indicator_Muscle.json (type: qat)
```

## Queue log (last 10 lines)
```
2026-04-18 06:41:26,782  INFO      Startup scan: 14 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-18 06:41:26,782  INFO      START  nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (1060 MB)
2026-04-18 06:41:26,783  INFO      Using existing segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4: 2 parts
2026-04-18 06:41:26,783  INFO      Transcribing 2 segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4
2026-04-18 07:11:27,740  INFO      ────────────────────────────────────────────────────────────
2026-04-18 07:11:27,740  INFO      Transcription queue manager started
2026-04-18 07:11:27,742  INFO      Startup scan: 14 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-18 07:11:27,742  INFO      START  nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (1060 MB)
2026-04-18 07:11:27,743  INFO      Using existing segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4: 2 parts
2026-04-18 07:11:27,743  INFO      Transcribing 2 segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4
```
