# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-05-04 23:48:51 UTC**

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
| RAM used | 11.47 GB / 32.86 GB (35%) |
| CPU | 2.3% |
| Disk used | 89.8 GB / 322.3 GB (29%) |
| Uptime | up 2 weeks, 3 days, 18 hours, 13 minutes |

## Recent markers
- `2026-05-04T23:48:21` **queue_empty** — All 13 videos transcribed
- `2026-05-04T23:48:21` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-05-04T23:48:21` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED
- `2026-05-04T23:48:21` **transcription_done** — NRT_Fascial_Activation_Application_Method.mp4 complete (55/13)
- `2026-05-04T23:48:21` **ingest_failed** — NRT_Fascial_Activation_Application_Method.mp4 ingest FAILED

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
2026-05-04 23:48:21,468  INFO      Queue empty — 13 video(s) processed. Exiting.
2026-05-04 23:48:21,533  INFO      Transcription queue manager done
2026-05-04 23:48:51,719  INFO      ────────────────────────────────────────────────────────────
2026-05-04 23:48:51,719  INFO      Transcription queue manager started
2026-05-04 23:48:51,721  INFO      Startup scan: 13 untranscribed video(s) found, 13 new entry/entries added to queue
2026-05-04 23:48:51,721  INFO      START  nrt/1.Upper_Body_Techniques.mp4  (525 MB)
2026-05-04 23:48:51,722  INFO      Using existing segments for 1.Upper_Body_Techniques.mp4: 4 parts
2026-05-04 23:48:51,722  INFO      Transcribing 4 segments for 1.Upper_Body_Techniques.mp4
2026-05-04 23:48:51,977  INFO      DONE   nrt/1.Upper_Body_Techniques.mp4  (0s, 4 segments)
2026-05-04 23:48:51,978  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/1.Upper_Body_Techniques.json
```
