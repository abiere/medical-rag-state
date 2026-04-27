# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-27 00:33:49 UTC**

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
| RAM used | 4.33 GB / 32.86 GB (13%) |
| CPU | 6.3% |
| Disk used | 88.4 GB / 322.3 GB (29%) |
| Uptime | up 1 week, 2 days, 18 hours, 58 minutes |

## Recent markers
- `2026-04-27T00:31:28` **transcription_done** — 1.Upper_Body_Techniques.mp4 complete (55/13)
- `2026-04-27T00:31:27` **ingest_failed** — 1.Upper_Body_Techniques.mp4 ingest FAILED
- `2026-04-27T00:30:57` **queue_empty** — All 13 videos transcribed
- `2026-04-27T00:30:57` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-04-27T00:30:57` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED

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
2026-04-27 00:31:27,733  INFO      START  nrt/1.Upper_Body_Techniques.mp4  (525 MB)
2026-04-27 00:31:27,733  INFO      Using existing segments for 1.Upper_Body_Techniques.mp4: 4 parts
2026-04-27 00:31:27,733  INFO      Transcribing 4 segments for 1.Upper_Body_Techniques.mp4
2026-04-27 00:31:27,969  INFO      DONE   nrt/1.Upper_Body_Techniques.mp4  (0s, 4 segments)
2026-04-27 00:31:27,970  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/1.Upper_Body_Techniques.json
2026-04-27 00:31:28,099  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-27 00:31:58,100  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-27 00:32:28,100  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-27 00:32:58,101  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-27 00:33:28,101  INFO      Queue paused (pause flag set) — waiting 30s
```
