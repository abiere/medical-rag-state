# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-17 01:47:37 UTC**

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
| Current job | `03_trail_guide_to_the_body_6th.pdf` (601 min) |
| Queued | 4 |
| Total books | 43 |
| Ingested | 35 |
| Vectors in medical_library | 2775 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (7 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 7.64 GB / 32.86 GB (23%) |
| CPU | 100.0% |
| Disk used | 59.7 GB / 322.3 GB (19%) |
| Uptime | up 2 days, 16 hours, 4 minutes |

## Recent markers
- `2026-04-17T01:40:37.484283+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-17T01:10:36.937634+00:00` **watchdog_restart** — transcription-queue hung (37 min stale) — restarted successfully
- `2026-04-17T00:36:30.945139+00:00` **book_ingested** — test_acupuncture.pdf → medical_library: 2 chunks
- `2026-04-16T21:35:10.096134+00:00` **book_ingested** — NRT UB Techniques and Fundamentals - Times.pdf → device_documentation: 2 chunks
- `2026-04-16T21:33:03.579644+00:00` **book_ingested** — NRT LB Techniques and Fundamentals - Times.pdf → device_documentation: 2 chunks

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
2026-04-17 00:33:17,978  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-17 00:33:47,979  INFO      START  nrt/1.Upper_Body_Techniques.mp4
2026-04-17 01:10:36,974  INFO      ────────────────────────────────────────────────────────────
2026-04-17 01:10:36,974  INFO      Transcription queue manager started
2026-04-17 01:10:36,975  INFO      Startup scan: 19 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 01:10:36,976  INFO      START  nrt/1.Upper_Body_Techniques.mp4
2026-04-17 01:40:37,523  INFO      ────────────────────────────────────────────────────────────
2026-04-17 01:40:37,523  INFO      Transcription queue manager started
2026-04-17 01:40:37,524  INFO      Startup scan: 19 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-17 01:40:37,525  INFO      START  nrt/1.Upper_Body_Techniques.mp4
```
