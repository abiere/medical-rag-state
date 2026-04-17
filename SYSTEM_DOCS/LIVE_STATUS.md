# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-17 19:47:12 UTC**

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
| Current job | `Touch for Health_ The Complete Edition_ A Practical Guide to Natural Health With Acupressure Touch_nodrm.pdf` (13 min) |
| Queued | 2 |
| Total books | 18 |
| Ingested | 53 |
| Vectors in medical_library | 9633 |
| Images pending approval | 2026 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4` (6 min) |
| Queued | 14 |
| Done | 21 / 37 |
| Vectors in video_transcripts | ? |

## System
| Metric | Value |
|---|---|
| RAM used | 15.45 GB / 32.86 GB (47%) |
| CPU | 100.0% |
| Disk used | 67.4 GB / 322.3 GB (22%) |
| Uptime | up 14 hours, 11 minutes |

## Recent markers
- `2026-04-17T19:41:12.894300+00:00` **watchdog_restart** — transcription-queue hung (32 min stale) — restarted successfully
- `2026-04-17T19:33:46.047756+00:00` **book_ingested** — Sobotta Tables of Muscles, Joints and Nerves, English_Latin_ Tables to 17th ed. of the Sobotta Atlas_nodrm.epub → medical_library: 35 chunks
- `2026-04-17T19:17:21.581653+00:00` **book_ingested** — Sobotta Atlas of Anatomy, Vol.1, 17th ed., English_Latin_ General anatomy and Musculoskeletal System_nodrm.epub → medical_library: 372 chunks
- `2026-04-17T18:45:38.452192+00:00` **book_ingested** — Sobotta Atlas of Anatomy, Vol. 3, 17th ed., English_Latin_ Head, Neck and Neuroanatomy_nodrm.epub → medical_library: 381 chunks
- `2026-04-17T18:41:11.956447+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully

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
2026-04-17 19:09:12,067  INFO      Startup scan: 14 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 19:09:12,068  INFO      START  nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (1060 MB)
2026-04-17 19:09:12,069  INFO      Using existing segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4: 2 parts
2026-04-17 19:09:12,069  INFO      Transcribing 2 segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4
2026-04-17 19:41:12,932  INFO      ────────────────────────────────────────────────────────────
2026-04-17 19:41:12,932  INFO      Transcription queue manager started
2026-04-17 19:41:12,933  INFO      Startup scan: 14 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 19:41:12,934  INFO      START  nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (1060 MB)
2026-04-17 19:41:12,934  INFO      Using existing segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4: 2 parts
2026-04-17 19:41:12,935  INFO      Transcribing 2 segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4
```
