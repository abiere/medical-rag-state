# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-18 05:27:25 UTC**

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
| Current job | `Integrative Manual Therapy Connective Tissue - Giammatteo.pdf` (5 min) |
| Queued | 14 |
| Total books | 37 |
| Ingested | 69 |
| Vectors in medical_library | 15876 |
| Images pending approval | 2026 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4` (16 min) |
| Queued | 14 |
| Done | 21 / 37 |
| Vectors in nrt_video_transcripts | 241 |

## System
| Metric | Value |
|---|---|
| RAM used | 14.37 GB / 32.86 GB (44%) |
| CPU | 100.0% |
| Disk used | 72.5 GB / 322.3 GB (23%) |
| Uptime | up 23 hours, 52 minutes |

## Recent markers
- `2026-04-18T05:21:56.019064+00:00` **book_ingested** — Integrative Manual Therapy Autonomic Nervous System - Giammatteo.pdf → medical_library: 186 chunks
- `2026-04-18T05:11:24.896935+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-18T05:06:24.951156+00:00` **book_ingested** — Explain Pain Supercharged - Moseley, Butler.pdf → medical_library: 399 chunks
- `2026-04-18T04:41:41.396533+00:00` **book_ingested** — Essentials of Anatomy and Physiology - Scanlon, Sanders.pdf → medical_library: 941 chunks
- `2026-04-18T04:41:24.502537+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully

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
2026-04-18 04:41:24,548  INFO      Startup scan: 14 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-18 04:41:24,549  INFO      START  nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (1060 MB)
2026-04-18 04:41:24,550  INFO      Using existing segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4: 2 parts
2026-04-18 04:41:24,550  INFO      Transcribing 2 segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4
2026-04-18 05:11:24,957  INFO      ────────────────────────────────────────────────────────────
2026-04-18 05:11:24,957  INFO      Transcription queue manager started
2026-04-18 05:11:24,959  INFO      Startup scan: 14 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-18 05:11:24,959  INFO      START  nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (1060 MB)
2026-04-18 05:11:24,960  INFO      Using existing segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4: 2 parts
2026-04-18 05:11:24,960  INFO      Transcribing 2 segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4
```
