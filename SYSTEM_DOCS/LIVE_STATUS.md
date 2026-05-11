# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-05-11 05:42:12 UTC**

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
| Current job | `1.Upper_Body_Techniques.mp4` |
| Queued | 13 |
| Done | 55 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 12.12 GB / 32.86 GB (37%) |
| CPU | 0.6% |
| Disk used | 90.9 GB / 322.3 GB (29%) |
| Uptime | up 3 weeks, 3 days, 6 minutes |

## Recent markers
- `2026-05-11T05:41:43` **queue_empty** — All 13 videos transcribed
- `2026-05-11T05:41:43` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-05-11T05:41:43` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED
- `2026-05-11T05:41:42` **transcription_done** — NRT_Fascial_Activation_Application_Method.mp4 complete (55/13)
- `2026-05-11T05:41:42` **ingest_failed** — NRT_Fascial_Activation_Application_Method.mp4 ingest FAILED

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
2026-05-11 05:41:43,180  INFO      Queue empty — 13 video(s) processed. Exiting.
2026-05-11 05:41:43,244  INFO      Transcription queue manager done
2026-05-11 05:42:13,474  INFO      ────────────────────────────────────────────────────────────
2026-05-11 05:42:13,474  INFO      Transcription queue manager started
2026-05-11 05:42:13,476  INFO      Startup scan: 13 untranscribed video(s) found, 13 new entry/entries added to queue
2026-05-11 05:42:13,476  INFO      START  nrt/1.Upper_Body_Techniques.mp4  (525 MB)
2026-05-11 05:42:13,477  INFO      Using existing segments for 1.Upper_Body_Techniques.mp4: 4 parts
2026-05-11 05:42:13,477  INFO      Transcribing 4 segments for 1.Upper_Body_Techniques.mp4
2026-05-11 05:42:13,737  INFO      DONE   nrt/1.Upper_Body_Techniques.mp4  (0s, 4 segments)
2026-05-11 05:42:13,738  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/1.Upper_Body_Techniques.json
```
