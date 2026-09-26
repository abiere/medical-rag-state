# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-09-26 02:51:39 UTC**

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
| Total books | 34 |
| Ingested | 74 |
| Vectors in medical_library | 17522 |
| Images pending approval | 2026 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | idle |
| Queued | 4 |
| Done | 55 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 8.93 GB / 32.86 GB (27%) |
| CPU | 5.4% |
| Disk used | 98.8 GB / 322.3 GB (32%) |
| Uptime | up 23 weeks, 21 hours, 16 minutes |

## Recent markers
- `2026-09-26T02:51:40` **transcription_done** — Miraculous_Sequence_-_Part_1.mp4 complete (55/13)
- `2026-09-26T02:51:40` **ingest_failed** — Miraculous_Sequence_-_Part_1.mp4 ingest FAILED
- `2026-09-26T02:51:39` **transcription_done** — How_to_Reset_23_More_Muscles.mp4 complete (55/13)
- `2026-09-26T02:51:39` **ingest_failed** — How_to_Reset_23_More_Muscles.mp4 ingest FAILED
- `2026-09-26T02:51:39` **transcription_done** — Everything_Reset_Sequence_-_Part_5.mp4 complete (55/13)

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
2026-09-26 02:51:40,790  INFO      Transcribing 3 segments for NRT_Fascial_Activation_Application_Method.mp4
2026-09-26 02:51:40,981  INFO      DONE   nrt/NRT_Fascial_Activation_Application_Method.mp4  (0s, 3 segments)
2026-09-26 02:51:40,982  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/NRT_Fascial_Activation_Application_Method.json
2026-09-26 02:51:41,111  INFO      START  nrt/NRT_Sports_Specific_or_Universal_Reset.mp4  (957 MB)
2026-09-26 02:51:41,112  INFO      Using existing segments for NRT_Sports_Specific_or_Universal_Reset.mp4: 2 parts
2026-09-26 02:51:41,112  INFO      Transcribing 2 segments for NRT_Sports_Specific_or_Universal_Reset.mp4
2026-09-26 02:51:41,222  INFO      DONE   nrt/NRT_Sports_Specific_or_Universal_Reset.mp4  (0s, 2 segments)
2026-09-26 02:51:41,223  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/NRT_Sports_Specific_or_Universal_Reset.json
2026-09-26 02:51:41,352  INFO      Queue empty — 13 video(s) processed. Exiting.
2026-09-26 02:51:41,416  INFO      Transcription queue manager done
```
