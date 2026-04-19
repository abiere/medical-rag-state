# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-19 00:06:02 UTC**

## Services
| Service | Status |
|---|---|
| medical-rag-web | ✅ active |
| transcription-queue | ⚠️ activating |
| book-ingest-queue | ❌ inactive |
| ttyd | ✅ active |
| qdrant | ✅ healthy |
| ollama | ✅ healthy |

## Book Ingest
| Metric | Value |
|---|---|
| Current job | idle |
| Queued | 0 |
| Total books | 34 |
| Ingested | 74 |
| Vectors in medical_library | 17522 |
| Images pending approval | 2026 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | idle |
| Queued | 12 |
| Done | 55 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 2.76 GB / 32.86 GB (8%) |
| CPU | 4.5% |
| Disk used | 84.0 GB / 322.3 GB (27%) |
| Uptime | up 1 day, 18 hours, 30 minutes |

## Recent markers
- `2026-04-19T00:06:03` **ingest_failed** — 1.Upper_Body_Techniques.mp4 ingest FAILED
- `2026-04-19T00:05:33` **queue_empty** — All 13 videos transcribed
- `2026-04-19T00:05:32` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-04-19T00:05:32` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED
- `2026-04-19T00:05:32` **transcription_done** — NRT_Fascial_Activation_Application_Method.mp4 complete (55/13)

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
2026-04-19 00:05:33,001  INFO      Queue empty — 13 video(s) processed. Exiting.
2026-04-19 00:05:33,066  INFO      Transcription queue manager done
2026-04-19 00:06:03,213  INFO      ────────────────────────────────────────────────────────────
2026-04-19 00:06:03,213  INFO      Transcription queue manager started
2026-04-19 00:06:03,214  INFO      Startup scan: 13 untranscribed video(s) found, 13 new entry/entries added to queue
2026-04-19 00:06:03,215  INFO      START  nrt/1.Upper_Body_Techniques.mp4  (525 MB)
2026-04-19 00:06:03,215  INFO      Using existing segments for 1.Upper_Body_Techniques.mp4: 4 parts
2026-04-19 00:06:03,215  INFO      Transcribing 4 segments for 1.Upper_Body_Techniques.mp4
2026-04-19 00:06:03,492  INFO      DONE   nrt/1.Upper_Body_Techniques.mp4  (0s, 4 segments)
2026-04-19 00:06:03,493  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/1.Upper_Body_Techniques.json
```
