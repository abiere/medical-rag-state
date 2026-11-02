# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-11-02 00:38:34 UTC**

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
| RAM used | 3.69 GB / 32.86 GB (11%) |
| CPU | 6.3% |
| Disk used | 118.9 GB / 322.3 GB (38%) |
| Uptime | up 28 weeks, 2 days, 19 hours, 3 minutes |

## Recent markers
- `2026-11-02T00:31:03` **transcription_done** — 1.Upper_Body_Techniques.mp4 complete (55/13)
- `2026-11-02T00:31:02` **ingest_failed** — 1.Upper_Body_Techniques.mp4 ingest FAILED
- `2026-11-02T00:30:32` **queue_empty** — All 13 videos transcribed
- `2026-11-02T00:30:32` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-11-02T00:30:32` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED

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
2026-11-02 00:34:03,105  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-02 00:34:33,106  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-02 00:35:03,107  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-02 00:35:33,107  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-02 00:36:03,107  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-02 00:36:33,108  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-02 00:37:03,108  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-02 00:37:33,109  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-02 00:38:03,109  INFO      Queue paused (pause flag set) — waiting 30s
2026-11-02 00:38:33,109  INFO      Queue paused (pause flag set) — waiting 30s
```
