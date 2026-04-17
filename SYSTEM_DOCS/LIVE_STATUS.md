# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-17 12:01:46 UTC**

## Services
| Service | Status |
|---|---|
| medical-rag-web | ✅ active |
| transcription-queue | ✅ active |
| book-ingest-queue | ❌ inactive |
| ttyd | ✅ active |
| qdrant | ✅ healthy |
| ollama | ✅ healthy |

## Book Ingest
| Metric | Value |
|---|---|
| Current job | idle |
| Queued | 0 |
| Total books | 49 |
| Ingested | 40 |
| Vectors in medical_library | 3248 |
| Images pending approval | 2026 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `16_Expanded__Revised__and_New_Techniques.mp4` (11 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 6.7 GB / 32.86 GB (20%) |
| CPU | 98.6% |
| Disk used | 59.4 GB / 322.3 GB (19%) |
| Uptime | up 6 hours, 26 minutes |

## Recent markers
- `2026-04-17T11:50:45.413111+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T11:46:51.672898+00:00` **book_ingested** — QRS 101 Operating Manual.pdf → device_documentation: 3 chunks
- `2026-04-17T11:44:44.248640+00:00` **book_ingested** — QRS 101 Indication Settings English.pdf → device_documentation: 9 chunks
- `2026-04-17T11:39:53.752127+00:00` **book_ingested** — QRS101 Quick start - English.pdf → device_documentation: 1 chunks
- `2026-04-17T11:38:55.837722+00:00` **book_ingested** — QRS-101 Manual Englisch.pdf → device_documentation: 41 chunks

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
2026-04-17 10:50:44,559  INFO      Startup scan: 19 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 10:50:44,559  INFO      START  nrt/16_Expanded__Revised__and_New_Techniques.mp4
2026-04-17 11:20:45,111  INFO      ────────────────────────────────────────────────────────────
2026-04-17 11:20:45,111  INFO      Transcription queue manager started
2026-04-17 11:20:45,113  INFO      Startup scan: 19 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 11:20:45,113  INFO      START  nrt/16_Expanded__Revised__and_New_Techniques.mp4
2026-04-17 11:50:45,452  INFO      ────────────────────────────────────────────────────────────
2026-04-17 11:50:45,452  INFO      Transcription queue manager started
2026-04-17 11:50:45,453  INFO      Startup scan: 19 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 11:50:45,454  INFO      START  nrt/16_Expanded__Revised__and_New_Techniques.mp4
```
