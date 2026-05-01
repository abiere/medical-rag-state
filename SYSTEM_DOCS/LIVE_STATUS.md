# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-05-01 14:45:43 UTC**

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
| RAM used | 4.92 GB / 32.86 GB (15%) |
| CPU | 7.0% |
| Disk used | 89.4 GB / 322.3 GB (29%) |
| Uptime | up 2 weeks, 9 hours, 10 minutes |

## Recent markers
- `2026-05-01T14:45:43` **transcription_done** — 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4 complete (55/13)
- `2026-05-01T14:45:43` **ingest_failed** — 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4 ingest FAILED
- `2026-05-01T14:45:43` **transcription_done** — 1.Upper_Body_Techniques.mp4 complete (55/13)
- `2026-05-01T14:45:43` **ingest_failed** — 1.Upper_Body_Techniques.mp4 ingest FAILED
- `2026-05-01T14:45:13` **queue_empty** — All 13 videos transcribed

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
2026-05-01 14:45:43,473  INFO      DONE   nrt/1.Upper_Body_Techniques.mp4  (0s, 4 segments)
2026-05-01 14:45:43,474  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/1.Upper_Body_Techniques.json
2026-05-01 14:45:43,605  INFO      START  nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (1060 MB)
2026-05-01 14:45:43,605  INFO      Using existing segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4: 2 parts
2026-05-01 14:45:43,605  INFO      Transcribing 2 segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4
2026-05-01 14:45:43,727  INFO      DONE   nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (0s, 2 segments)
2026-05-01 14:45:43,728  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.json
2026-05-01 14:45:43,857  INFO      START  nrt/Everything_Reset_Sequence_-_Part_1.mp4  (649 MB)
2026-05-01 14:45:43,858  INFO      Using existing segments for Everything_Reset_Sequence_-_Part_1.mp4: 3 parts
2026-05-01 14:45:43,858  INFO      Transcribing 3 segments for Everything_Reset_Sequence_-_Part_1.mp4
```
