# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-17 20:32:13 UTC**

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
| Current job | `354229827-daniel-keown-the-spark-in-the-machine-how-the-science-of-acupuncture-explains-the-mysteries-of-western-medicine-singi.pdf` |
| Queued | 17 |
| Total books | 37 |
| Ingested | 56 |
| Vectors in medical_library | 10713 |
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
| RAM used | 15.2 GB / 32.86 GB (46%) |
| CPU | 100.0% |
| Disk used | 68.6 GB / 322.3 GB (22%) |
| Uptime | up 14 hours, 56 minutes |

## Recent markers
- `2026-04-17T20:31:11.813083+00:00` **book_ingested** — 756201384-The-Foundations-of-Chinese-Medicine-A-Comprehensive-Text-3rd-Edition-ISBN-0702052167-978-0702052163.pdf → medical_library: 33 chunks
- `2026-04-17T20:23:13.478521+00:00` **book_ingested** — Whole Brain Living_ The Anatomy of Choice and the Four Characters That Drive Our Life_nodrm.epub → medical_library: 252 chunks
- `2026-04-17T20:11:13.440274+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T20:10:50.740046+00:00` **book_ingested** — Touch for Health_ The Complete Edition_ A Practical Guide to Natural Health With Acupressure Touch.epub → medical_library: 313 chunks
- `2026-04-17T19:53:36.558093+00:00` **book_ingested** — Touch for Health_ The Complete Edition_ A Practical Guide to Natural Health With Acupressure Touch_nodrm.pdf → medical_library: 482 chunks

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
2026-04-17 19:41:12,933  INFO      Startup scan: 14 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 19:41:12,934  INFO      START  nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (1060 MB)
2026-04-17 19:41:12,934  INFO      Using existing segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4: 2 parts
2026-04-17 19:41:12,935  INFO      Transcribing 2 segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4
2026-04-17 20:11:13,485  INFO      ────────────────────────────────────────────────────────────
2026-04-17 20:11:13,485  INFO      Transcription queue manager started
2026-04-17 20:11:13,486  INFO      Startup scan: 14 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 20:11:13,486  INFO      START  nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (1060 MB)
2026-04-17 20:11:13,487  INFO      Using existing segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4: 2 parts
2026-04-17 20:11:13,487  INFO      Transcribing 2 segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4
```
