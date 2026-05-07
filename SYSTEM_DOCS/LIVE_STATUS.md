# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-05-07 01:58:36 UTC**

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
| Current job | `NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows.mp4` |
| Queued | 3 |
| Done | 55 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 5.58 GB / 32.86 GB (17%) |
| CPU | 5.9% |
| Disk used | 90.3 GB / 322.3 GB (29%) |
| Uptime | up 2 weeks, 5 days, 20 hours, 23 minutes |

## Recent markers
- `2026-05-07T01:58:36` **transcription_done** — Miraculous_Sequence_-_Part_2.mp4 complete (55/13)
- `2026-05-07T01:58:36` **ingest_failed** — Miraculous_Sequence_-_Part_2.mp4 ingest FAILED
- `2026-05-07T01:58:36` **transcription_done** — Miraculous_Sequence_-_Part_1.mp4 complete (55/13)
- `2026-05-07T01:58:36` **ingest_failed** — Miraculous_Sequence_-_Part_1.mp4 ingest FAILED
- `2026-05-07T01:58:36` **transcription_done** — How_to_Reset_23_More_Muscles.mp4 complete (55/13)

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
2026-05-07 01:58:36,477  INFO      START  nrt/Miraculous_Sequence_-_Part_2.mp4  (664 MB)
2026-05-07 01:58:36,478  INFO      Using existing segments for Miraculous_Sequence_-_Part_2.mp4: 2 parts
2026-05-07 01:58:36,478  INFO      Transcribing 2 segments for Miraculous_Sequence_-_Part_2.mp4
2026-05-07 01:58:36,619  INFO      DONE   nrt/Miraculous_Sequence_-_Part_2.mp4  (0s, 2 segments)
2026-05-07 01:58:36,620  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Miraculous_Sequence_-_Part_2.json
2026-05-07 01:58:36,750  INFO      START  nrt/NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows.mp4  (990 MB)
2026-05-07 01:58:36,751  INFO      Using existing segments for NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows.mp4: 2 parts
2026-05-07 01:58:36,751  INFO      Transcribing 2 segments for NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows.mp4
2026-05-07 01:58:36,894  INFO      DONE   nrt/NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows.mp4  (0s, 2 segments)
2026-05-07 01:58:36,895  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows.json
```
