# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-11-17 15:08:18 UTC**

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
| Queued | 11 |
| Done | 55 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 4.03 GB / 32.86 GB (12%) |
| CPU | 7.3% |
| Disk used | 138.4 GB / 322.3 GB (45%) |
| Uptime | up 30 weeks, 4 days, 9 hours, 32 minutes |

## Recent markers
- `2026-11-17T15:08:18` **ingest_failed** — 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4 ingest FAILED
- `2026-11-17T15:08:18` **transcription_done** — 1.Upper_Body_Techniques.mp4 complete (55/13)
- `2026-11-17T15:08:18` **ingest_failed** — 1.Upper_Body_Techniques.mp4 ingest FAILED
- `2026-11-17T15:07:48` **queue_empty** — All 13 videos transcribed
- `2026-11-17T15:07:47` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)

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
2026-11-17 15:08:20,468  INFO      START  nrt/How_to_Reset_23_More_Muscles.mp4  (412 MB)
2026-11-17 15:08:20,469  INFO      Using existing segments for How_to_Reset_23_More_Muscles.mp4: 2 parts
2026-11-17 15:08:20,469  INFO      Transcribing 2 segments for How_to_Reset_23_More_Muscles.mp4
2026-11-17 15:08:20,585  INFO      DONE   nrt/How_to_Reset_23_More_Muscles.mp4  (0s, 2 segments)
2026-11-17 15:08:20,585  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/How_to_Reset_23_More_Muscles.json
2026-11-17 15:08:20,715  INFO      START  nrt/Miraculous_Sequence_-_Part_1.mp4  (689 MB)
2026-11-17 15:08:20,715  INFO      Using existing segments for Miraculous_Sequence_-_Part_1.mp4: 2 parts
2026-11-17 15:08:20,716  INFO      Transcribing 2 segments for Miraculous_Sequence_-_Part_1.mp4
2026-11-17 15:08:20,850  INFO      DONE   nrt/Miraculous_Sequence_-_Part_1.mp4  (0s, 2 segments)
2026-11-17 15:08:20,851  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Miraculous_Sequence_-_Part_1.json
```
