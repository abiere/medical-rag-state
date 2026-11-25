# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-11-25 02:57:06 UTC**

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
| RAM used | 4.17 GB / 32.86 GB (13%) |
| CPU | 5.8% |
| Disk used | 138.6 GB / 322.3 GB (45%) |
| Uptime | up 31 weeks, 4 days, 21 hours, 21 minutes |

## Recent markers
- `2026-11-25T02:57:06` **ingest_failed** — 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4 ingest FAILED
- `2026-11-25T02:57:06` **transcription_done** — 1.Upper_Body_Techniques.mp4 complete (55/13)
- `2026-11-25T02:57:06` **ingest_failed** — 1.Upper_Body_Techniques.mp4 ingest FAILED
- `2026-11-25T02:56:36` **queue_empty** — All 13 videos transcribed
- `2026-11-25T02:56:35` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)

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
2026-11-25 02:57:08,681  INFO      START  nrt/Miraculous_Sequence_-_Part_1.mp4  (689 MB)
2026-11-25 02:57:08,682  INFO      Using existing segments for Miraculous_Sequence_-_Part_1.mp4: 2 parts
2026-11-25 02:57:08,682  INFO      Transcribing 2 segments for Miraculous_Sequence_-_Part_1.mp4
2026-11-25 02:57:08,810  INFO      DONE   nrt/Miraculous_Sequence_-_Part_1.mp4  (0s, 2 segments)
2026-11-25 02:57:08,811  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Miraculous_Sequence_-_Part_1.json
2026-11-25 02:57:08,940  INFO      START  nrt/Miraculous_Sequence_-_Part_2.mp4  (664 MB)
2026-11-25 02:57:08,941  INFO      Using existing segments for Miraculous_Sequence_-_Part_2.mp4: 2 parts
2026-11-25 02:57:08,941  INFO      Transcribing 2 segments for Miraculous_Sequence_-_Part_2.mp4
2026-11-25 02:57:09,065  INFO      DONE   nrt/Miraculous_Sequence_-_Part_2.mp4  (0s, 2 segments)
2026-11-25 02:57:09,066  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/Miraculous_Sequence_-_Part_2.json
```
