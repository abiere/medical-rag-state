# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-06-12 00:42:59 UTC**

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
| Queued | 12 |
| Done | 55 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 7.19 GB / 32.86 GB (22%) |
| CPU | 0.3% |
| Disk used | 92.2 GB / 322.3 GB (30%) |
| Uptime | up 7 weeks, 6 days, 19 hours, 7 minutes |

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
2026-06-12 00:38:12,111  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-12 00:38:42,111  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-12 00:39:12,112  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-12 00:39:42,112  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-12 00:40:12,113  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-12 00:40:42,113  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-12 00:41:12,113  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-12 00:41:42,114  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-12 00:42:12,114  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-12 00:42:42,115  INFO      Queue paused (pause flag set) — waiting 30s
```
