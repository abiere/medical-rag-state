# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-06-12 00:32:59 UTC**

## Services
| Service | Status |
|---|---|
| medical-rag-web | ✅ active |
| transcription-queue | ✅ active |
| book-ingest-queue | ✅ active |
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
| Queued | 12 |
| Done | 55 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 7.58 GB / 32.86 GB (23%) |
| CPU | 6.5% |
| Disk used | 92.2 GB / 322.3 GB (30%) |
| Uptime | up 7 weeks, 6 days, 18 hours, 57 minutes |

## Recent markers
- `2026-06-12T00:30:42` **transcription_done** — 1.Upper_Body_Techniques.mp4 complete (55/13)
- `2026-06-12T00:30:41` **ingest_failed** — 1.Upper_Body_Techniques.mp4 ingest FAILED
- `2026-06-12T00:30:11` **queue_empty** — All 13 videos transcribed
- `2026-06-12T00:30:11` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-06-12T00:30:11` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED

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
2026-06-12 00:30:41,739  INFO      START  nrt/1.Upper_Body_Techniques.mp4  (525 MB)
2026-06-12 00:30:41,739  INFO      Using existing segments for 1.Upper_Body_Techniques.mp4: 4 parts
2026-06-12 00:30:41,740  INFO      Transcribing 4 segments for 1.Upper_Body_Techniques.mp4
2026-06-12 00:30:41,973  INFO      DONE   nrt/1.Upper_Body_Techniques.mp4  (0s, 4 segments)
2026-06-12 00:30:41,974  WARNING   Transcript not found for ingestion: /root/medical-rag/data/transcripts/1.Upper_Body_Techniques.json
2026-06-12 00:30:42,104  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-12 00:31:12,104  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-12 00:31:42,104  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-12 00:32:12,105  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-12 00:32:42,106  INFO      Queue paused (pause flag set) — waiting 30s
```
