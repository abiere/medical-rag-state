# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-18 22:10:35 UTC**

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
| Current job | `2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4` |
| Queued | 12 |
| Done | 55 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 2.76 GB / 32.86 GB (8%) |
| CPU | 4.6% |
| Disk used | 83.9 GB / 322.3 GB (27%) |
| Uptime | up 1 day, 16 hours, 35 minutes |

## Recent markers
- `2026-04-18T22:10:35` **transcription_done** — 1.Upper_Body_Techniques.mp4 complete (55/13)
- `2026-04-18T22:10:35` **ingest_failed** — 1.Upper_Body_Techniques.mp4 ingest FAILED
- `2026-04-18T22:10:05` **queue_empty** — All 13 videos transcribed
- `2026-04-18T22:10:05` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-04-18T22:10:05` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED

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
2026-04-18 22:10:35,462  INFO      Transcription queue manager started
2026-04-18 22:10:35,464  INFO      Startup scan: 13 untranscribed video(s) found, 13 new entry/entries added to queue
2026-04-18 22:10:35,464  INFO      START  nrt/1.Upper_Body_Techniques.mp4  (525 MB)
2026-04-18 22:10:35,465  INFO      Using existing segments for 1.Upper_Body_Techniques.mp4: 4 parts
2026-04-18 22:10:35,465  INFO      Transcribing 4 segments for 1.Upper_Body_Techniques.mp4
2026-04-18 22:10:35,701  INFO      DONE   nrt/1.Upper_Body_Techniques.mp4  (0s, 4 segments)
2026-04-18 22:10:35,702  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/1.Upper_Body_Techniques.json
2026-04-18 22:10:35,832  INFO      START  nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (1060 MB)
2026-04-18 22:10:35,833  INFO      Using existing segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4: 2 parts
2026-04-18 22:10:35,833  INFO      Transcribing 2 segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4
```
