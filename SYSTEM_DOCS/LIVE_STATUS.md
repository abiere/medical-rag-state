# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-28 01:05:53 UTC**

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
| Current job | `2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4` |
| Queued | 12 |
| Done | 55 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 4.3 GB / 32.86 GB (13%) |
| CPU | 5.5% |
| Disk used | 88.6 GB / 322.3 GB (29%) |
| Uptime | up 1 week, 3 days, 19 hours, 30 minutes |

## Recent markers
- `2026-04-28T01:05:53` **transcription_done** — 1.Upper_Body_Techniques.mp4 complete (55/13)
- `2026-04-28T01:05:53` **ingest_failed** — 1.Upper_Body_Techniques.mp4 ingest FAILED
- `2026-04-28T01:05:23` **queue_empty** — All 13 videos transcribed
- `2026-04-28T01:05:22` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-04-28T01:05:22` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED

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
2026-04-28 01:05:53,211  INFO      START  nrt/1.Upper_Body_Techniques.mp4  (525 MB)
2026-04-28 01:05:53,211  INFO      Using existing segments for 1.Upper_Body_Techniques.mp4: 4 parts
2026-04-28 01:05:53,211  INFO      Transcribing 4 segments for 1.Upper_Body_Techniques.mp4
2026-04-28 01:05:53,450  INFO      DONE   nrt/1.Upper_Body_Techniques.mp4  (0s, 4 segments)
2026-04-28 01:05:53,450  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/1.Upper_Body_Techniques.json
2026-04-28 01:05:53,580  INFO      START  nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (1060 MB)
2026-04-28 01:05:53,581  INFO      Using existing segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4: 2 parts
2026-04-28 01:05:53,581  INFO      Transcribing 2 segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4
2026-04-28 01:05:53,713  INFO      DONE   nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (0s, 2 segments)
2026-04-28 01:05:53,714  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.json
```
