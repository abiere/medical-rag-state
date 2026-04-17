# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-17 17:57:10 UTC**

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
| Current job | `Orthopedic Physical Assessment_nodrm.epub` (23 min) |
| Queued | 6 |
| Total books | 64 |
| Ingested | 49 |
| Vectors in medical_library | 7279 |
| Images pending approval | 2026 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4` (16 min) |
| Queued | 14 |
| Done | 21 / 37 |
| Vectors in video_transcripts | 241 |

## System
| Metric | Value |
|---|---|
| RAM used | 8.5 GB / 32.86 GB (26%) |
| CPU | 100.0% |
| Disk used | 66.0 GB / 322.3 GB (21%) |
| Uptime | up 12 hours, 21 minutes |

## Recent markers
- `2026-04-17T17:41:10.919377+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T17:33:18.970769+00:00` **book_ingested** — Sobotta Atlas of Anatomy, Vol. 2, 17th ed., English_Latin_ Internal Organs_nodrm.epub → medical_library: 276 chunks
- `2026-04-17T17:11:10.480306+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T17:02:37.351437+00:00` **book_ingested** — Sobotta Atlas of Anatomy Classic_nodrm.epub → medical_library: 535 chunks
- `2026-04-17T16:41:09.936544+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully

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
2026-04-17 17:11:10,525  INFO      Startup scan: 14 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 17:11:10,525  INFO      START  nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (1060 MB)
2026-04-17 17:11:10,526  INFO      Using existing segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4: 2 parts
2026-04-17 17:11:10,526  INFO      Transcribing 2 segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4
2026-04-17 17:41:10,965  INFO      ────────────────────────────────────────────────────────────
2026-04-17 17:41:10,965  INFO      Transcription queue manager started
2026-04-17 17:41:10,966  INFO      Startup scan: 14 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 17:41:10,967  INFO      START  nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (1060 MB)
2026-04-17 17:41:10,967  INFO      Using existing segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4: 2 parts
2026-04-17 17:41:10,967  INFO      Transcribing 2 segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4
```
