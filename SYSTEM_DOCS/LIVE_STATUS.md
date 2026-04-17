# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-17 15:47:08 UTC**

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
| Current job | `Sobotta Anatomy Textbook_nodrm.epub` (23 min) |
| Queued | 9 |
| Total books | 64 |
| Ingested | 45 |
| Vectors in medical_library | 5372 |
| Images pending approval | 2026 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4` (6 min) |
| Queued | 14 |
| Done | 21 / 37 |
| Vectors in video_transcripts | 241 |

## System
| Metric | Value |
|---|---|
| RAM used | 14.02 GB / 32.86 GB (43%) |
| CPU | 99.5% |
| Disk used | 63.1 GB / 322.3 GB (20%) |
| Uptime | up 10 hours, 11 minutes |

## Recent markers
- `2026-04-17T15:41:08.612443+00:00` **watchdog_restart** — transcription-queue hung (34 min stale) — restarted successfully
- `2026-04-17T15:23:28.329029+00:00` **book_ingested** — Quantum-Touch_ The Power to Heal_nodrm.epub → medical_library: 142 chunks
- `2026-04-17T15:13:36.045632+00:00` **book_ingested** — Quantum-Touch Core Transformation_ A New Way to Heal and Alter Reality_nodrm.epub → medical_library: 141 chunks
- `2026-04-17T15:03:17.284001+00:00` **book_ingested** — Quantum-Touch 2.0 - The New Human_ Discovering and Becoming_nodrm.epub → medical_library: 158 chunks
- `2026-04-17T15:02:27` **transcription_failed** — 1.Upper_Body_Techniques.mp4 FAILED (21/14)

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
2026-04-17 15:06:54,242  INFO      Startup scan: 14 untranscribed video(s) found, 1 new entry/entries added to queue
2026-04-17 15:06:54,243  INFO      START  nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (1060 MB)
2026-04-17 15:06:54,244  INFO      Using existing segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4: 2 parts
2026-04-17 15:06:54,244  INFO      Transcribing 2 segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4
2026-04-17 15:41:08,654  INFO      ────────────────────────────────────────────────────────────
2026-04-17 15:41:08,655  INFO      Transcription queue manager started
2026-04-17 15:41:08,656  INFO      Startup scan: 14 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 15:41:08,656  INFO      START  nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (1060 MB)
2026-04-17 15:41:08,657  INFO      Using existing segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4: 2 parts
2026-04-17 15:41:08,657  INFO      Transcribing 2 segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4
```
