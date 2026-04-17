# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-17 16:57:09 UTC**

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
| Current job | `Sobotta Atlas of Anatomy Classic_nodrm.epub` (33 min) |
| Queued | 8 |
| Total books | 64 |
| Ingested | 47 |
| Vectors in medical_library | 6468 |
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
| RAM used | 15.09 GB / 32.86 GB (46%) |
| CPU | 100.0% |
| Disk used | 64.6 GB / 322.3 GB (21%) |
| Uptime | up 11 hours, 21 minutes |

## Recent markers
- `2026-04-17T16:41:09.936544+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T16:23:13.715014+00:00` **book_ingested** — Sobotta Anatomy Textbook_nodrm.epub → medical_library: 1096 chunks
- `2026-04-17T16:11:09.149861+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T15:41:08.612443+00:00` **watchdog_restart** — transcription-queue hung (34 min stale) — restarted successfully
- `2026-04-17T15:23:28.329029+00:00` **book_ingested** — Quantum-Touch_ The Power to Heal_nodrm.epub → medical_library: 142 chunks

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
2026-04-17 16:11:09,209  INFO      Startup scan: 14 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 16:11:09,210  INFO      START  nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (1060 MB)
2026-04-17 16:11:09,210  INFO      Using existing segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4: 2 parts
2026-04-17 16:11:09,210  INFO      Transcribing 2 segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4
2026-04-17 16:41:09,979  INFO      ────────────────────────────────────────────────────────────
2026-04-17 16:41:09,979  INFO      Transcription queue manager started
2026-04-17 16:41:09,980  INFO      Startup scan: 14 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 16:41:09,981  INFO      START  nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (1060 MB)
2026-04-17 16:41:09,981  INFO      Using existing segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4: 2 parts
2026-04-17 16:41:09,981  INFO      Transcribing 2 segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4
```
