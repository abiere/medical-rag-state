# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-17 21:37:14 UTC**

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
| Current job | `An Introduction to Craniosacral Therapy - Kern.pdf` (10 min) |
| Queued | 13 |
| Total books | 37 |
| Ingested | 61 |
| Vectors in medical_library | 11812 |
| Images pending approval | 2026 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4` (26 min) |
| Queued | 14 |
| Done | 21 / 37 |
| Vectors in nrt_video_transcripts | 241 |

## System
| Metric | Value |
|---|---|
| RAM used | 16.14 GB / 32.86 GB (49%) |
| CPU | 100.0% |
| Disk used | 68.8 GB / 322.3 GB (22%) |
| Uptime | up 16 hours, 1 minute |

## Recent markers
- `2026-04-17T21:26:49.298895+00:00` **book_ingested** — Advanced Acupuncture - Cecil-Sterman.pdf → medical_library: 482 chunks
- `2026-04-17T21:11:14.641319+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T21:09:17.803364+00:00` **book_ingested** — Acupuncture Point Combinations - Deadman e.a..pdf → medical_library: 78 chunks
- `2026-04-17T20:59:11.362723+00:00` **book_ingested** — Acupuncture in Practice - Campbell.pdf → medical_library: 225 chunks
- `2026-04-17T20:47:29.731822+00:00` **book_ingested** — 354229827-daniel-keown-the-spark-in-the-machine-how-the-science-of-acupuncture-explains-the-mysteries-of-western-medicine-singi.pdf → medical_library: 314 chunks

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
2026-04-17 20:41:14,160  INFO      Startup scan: 14 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 20:41:14,160  INFO      START  nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (1060 MB)
2026-04-17 20:41:14,161  INFO      Using existing segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4: 2 parts
2026-04-17 20:41:14,161  INFO      Transcribing 2 segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4
2026-04-17 21:11:14,685  INFO      ────────────────────────────────────────────────────────────
2026-04-17 21:11:14,685  INFO      Transcription queue manager started
2026-04-17 21:11:14,687  INFO      Startup scan: 14 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 21:11:14,687  INFO      START  nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (1060 MB)
2026-04-17 21:11:14,688  INFO      Using existing segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4: 2 parts
2026-04-17 21:11:14,688  INFO      Transcribing 2 segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4
```
