# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-05-04 00:31:48 UTC**

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
| RAM used | 5.56 GB / 32.86 GB (17%) |
| CPU | 6.4% |
| Disk used | 89.6 GB / 322.3 GB (29%) |
| Uptime | up 2 weeks, 2 days, 18 hours, 56 minutes |

## Recent markers
- `2026-05-04T00:30:31` **transcription_done** — 1.Upper_Body_Techniques.mp4 complete (55/13)
- `2026-05-04T00:30:31` **ingest_failed** — 1.Upper_Body_Techniques.mp4 ingest FAILED
- `2026-05-04T00:30:00` **queue_empty** — All 13 videos transcribed
- `2026-05-04T00:30:00` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-05-04T00:30:00` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED

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
2026-05-04 00:30:30,998  INFO      Transcription queue manager started
2026-05-04 00:30:30,999  INFO      Startup scan: 13 untranscribed video(s) found, 13 new entry/entries added to queue
2026-05-04 00:30:31,000  INFO      START  nrt/1.Upper_Body_Techniques.mp4  (525 MB)
2026-05-04 00:30:31,000  INFO      Using existing segments for 1.Upper_Body_Techniques.mp4: 4 parts
2026-05-04 00:30:31,000  INFO      Transcribing 4 segments for 1.Upper_Body_Techniques.mp4
2026-05-04 00:30:31,235  INFO      DONE   nrt/1.Upper_Body_Techniques.mp4  (0s, 4 segments)
2026-05-04 00:30:31,237  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/1.Upper_Body_Techniques.json
2026-05-04 00:30:31,368  INFO      Queue paused (pause flag set) — waiting 30s
2026-05-04 00:31:01,368  INFO      Queue paused (pause flag set) — waiting 30s
2026-05-04 00:31:31,369  INFO      Queue paused (pause flag set) — waiting 30s
```
