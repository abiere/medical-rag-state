# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-20 20:01:38 UTC**

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
| RAM used | 3.16 GB / 32.86 GB (10%) |
| CPU | 6.6% |
| Disk used | 85.4 GB / 322.3 GB (28%) |
| Uptime | up 3 days, 14 hours, 26 minutes |

## Recent markers
- `2026-04-20T20:01:38` **ingest_failed** — 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4 ingest FAILED
- `2026-04-20T20:01:38` **transcription_done** — 1.Upper_Body_Techniques.mp4 complete (55/13)
- `2026-04-20T20:01:38` **ingest_failed** — 1.Upper_Body_Techniques.mp4 ingest FAILED
- `2026-04-20T20:01:08` **queue_empty** — All 13 videos transcribed
- `2026-04-20T20:01:08` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)

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
2026-04-20 20:01:38,297  INFO      START  nrt/1.Upper_Body_Techniques.mp4  (525 MB)
2026-04-20 20:01:38,297  INFO      Using existing segments for 1.Upper_Body_Techniques.mp4: 4 parts
2026-04-20 20:01:38,297  INFO      Transcribing 4 segments for 1.Upper_Body_Techniques.mp4
2026-04-20 20:01:38,527  INFO      DONE   nrt/1.Upper_Body_Techniques.mp4  (0s, 4 segments)
2026-04-20 20:01:38,528  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/1.Upper_Body_Techniques.json
2026-04-20 20:01:38,657  INFO      START  nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (1060 MB)
2026-04-20 20:01:38,658  INFO      Using existing segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4: 2 parts
2026-04-20 20:01:38,658  INFO      Transcribing 2 segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4
2026-04-20 20:01:38,773  INFO      DONE   nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (0s, 2 segments)
2026-04-20 20:01:38,774  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.json
```
