# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-17 11:11:44 UTC**

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
| Current job | `QRS-101-Home-System-Brochure.pdf` (4 min) |
| Queued | 4 |
| Total books | 49 |
| Ingested | 37 |
| Vectors in medical_library | 3248 |
| Images pending approval | 2026 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `16_Expanded__Revised__and_New_Techniques.mp4` (21 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 13.95 GB / 32.86 GB (42%) |
| CPU | 99.9% |
| Disk used | 59.3 GB / 322.3 GB (19%) |
| Uptime | up 5 hours, 36 minutes |

## Recent markers
- `2026-04-17T11:07:03.654184+00:00` **book_ingested** — QRS Quantron Resonance 101 Home System.pdf → device_documentation: 9 chunks
- `2026-04-17T10:50:44.521401+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T10:49:54.673786+00:00` **book_ingested** — 03_trail_guide_to_the_body_6th.pdf → medical_library: 473 chunks
- `2026-04-17T10:20:43.823985+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T09:50:43.375272+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully

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
2026-04-17 09:50:43,428  INFO      Startup scan: 19 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 09:50:43,428  INFO      START  nrt/16_Expanded__Revised__and_New_Techniques.mp4
2026-04-17 10:20:43,888  INFO      ────────────────────────────────────────────────────────────
2026-04-17 10:20:43,888  INFO      Transcription queue manager started
2026-04-17 10:20:43,889  INFO      Startup scan: 19 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 10:20:43,890  INFO      START  nrt/16_Expanded__Revised__and_New_Techniques.mp4
2026-04-17 10:50:44,557  INFO      ────────────────────────────────────────────────────────────
2026-04-17 10:50:44,558  INFO      Transcription queue manager started
2026-04-17 10:50:44,559  INFO      Startup scan: 19 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 10:50:44,559  INFO      START  nrt/16_Expanded__Revised__and_New_Techniques.mp4
```
