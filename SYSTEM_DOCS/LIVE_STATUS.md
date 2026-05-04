# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-05-04 09:29:18 UTC**

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
| Queued | 0 |
| Done | 55 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 5.31 GB / 32.86 GB (16%) |
| CPU | 1.5% |
| Disk used | 89.7 GB / 322.3 GB (29%) |
| Uptime | up 2 weeks, 3 days, 3 hours, 53 minutes |

## Recent markers
- `2026-05-04T09:28:48` **queue_empty** — All 13 videos transcribed
- `2026-05-04T09:28:48` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-05-04T09:28:48` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED
- `2026-05-04T09:28:48` **transcription_done** — NRT_Fascial_Activation_Application_Method.mp4 complete (55/13)
- `2026-05-04T09:28:48` **ingest_failed** — NRT_Fascial_Activation_Application_Method.mp4 ingest FAILED

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
2026-05-04 09:28:48,467  INFO      DONE   nrt/NRT_Sports_Specific_or_Universal_Reset.mp4  (0s, 2 segments)
2026-05-04 09:28:48,468  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/NRT_Sports_Specific_or_Universal_Reset.json
2026-05-04 09:28:48,597  INFO      Queue empty — 13 video(s) processed. Exiting.
2026-05-04 09:28:48,661  INFO      Transcription queue manager done
2026-05-04 09:29:18,895  INFO      ────────────────────────────────────────────────────────────
2026-05-04 09:29:18,896  INFO      Transcription queue manager started
2026-05-04 09:29:18,897  INFO      Startup scan: 13 untranscribed video(s) found, 13 new entry/entries added to queue
2026-05-04 09:29:18,897  INFO      START  nrt/1.Upper_Body_Techniques.mp4  (525 MB)
2026-05-04 09:29:18,898  INFO      Using existing segments for 1.Upper_Body_Techniques.mp4: 4 parts
2026-05-04 09:29:18,898  INFO      Transcribing 4 segments for 1.Upper_Body_Techniques.mp4
```
