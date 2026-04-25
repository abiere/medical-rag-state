# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-25 00:31:49 UTC**

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
| RAM used | 4.08 GB / 32.86 GB (12%) |
| CPU | 7.5% |
| Disk used | 88.0 GB / 322.3 GB (28%) |
| Uptime | up 1 week, 18 hours, 56 minutes |

## Recent markers
- `2026-04-25T00:30:32` **transcription_done** — 1.Upper_Body_Techniques.mp4 complete (55/13)
- `2026-04-25T00:30:32` **ingest_failed** — 1.Upper_Body_Techniques.mp4 ingest FAILED
- `2026-04-25T00:30:02` **queue_empty** — All 13 videos transcribed
- `2026-04-25T00:30:02` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-04-25T00:30:02` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED

## Nightly Consistency
```
  TRANSCRIPT ONTBREEKT IN QDRANT: 1.Upper_Body_Techniques_part002.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_1.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Everything_Reset_Sequence_-_Part_4_part001.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Indicator_Muscle.json (type: qat)
  BOEK ONTBREEKT IN QDRANT: test_acupuncture.pdf (collectie: medical_library)
  BOEK ONTBREEKT IN QDRANT: Orthopedic Physical Assessment_nodrm.epub (collectie: medical_library)
  BOEK ONTBREEKT IN QDRANT: Touch for Health_ The Complete Edition_ A Practical Guide to Natural Health With Acupressure Touch_nodrm.pdf (collectie: medical_library)
  BOEK ONTBREEKT IN QDRANT: Bates Guide to Physical Examination 14e editie - Bickley.epub (collectie: medical_library)
```

## Queue log (last 10 lines)
```
2026-04-25 00:30:32,476  INFO      Transcription queue manager started
2026-04-25 00:30:32,478  INFO      Startup scan: 13 untranscribed video(s) found, 13 new entry/entries added to queue
2026-04-25 00:30:32,478  INFO      START  nrt/1.Upper_Body_Techniques.mp4  (525 MB)
2026-04-25 00:30:32,479  INFO      Using existing segments for 1.Upper_Body_Techniques.mp4: 4 parts
2026-04-25 00:30:32,479  INFO      Transcribing 4 segments for 1.Upper_Body_Techniques.mp4
2026-04-25 00:30:32,772  INFO      DONE   nrt/1.Upper_Body_Techniques.mp4  (0s, 4 segments)
2026-04-25 00:30:32,773  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/1.Upper_Body_Techniques.json
2026-04-25 00:30:32,903  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-25 00:31:02,903  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-25 00:31:32,904  INFO      Queue paused (pause flag set) — waiting 30s
```
