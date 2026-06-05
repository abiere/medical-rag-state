# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-06-05 00:40:11 UTC**

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
| Queued | 13 |
| Done | 55 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 7.53 GB / 32.86 GB (23%) |
| CPU | 2.1% |
| Disk used | 92.0 GB / 322.3 GB (30%) |
| Uptime | up 6 weeks, 6 days, 19 hours, 4 minutes |

## Recent markers
- `2026-06-05T00:30:44` **queue_empty** — All 13 videos transcribed
- `2026-06-05T00:30:44` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-06-05T00:30:44` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED
- `2026-06-05T00:30:44` **transcription_done** — NRT_Fascial_Activation_Application_Method.mp4 complete (55/13)
- `2026-06-05T00:30:44` **ingest_failed** — NRT_Fascial_Activation_Application_Method.mp4 ingest FAILED

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
2026-06-05 00:35:14,724  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-05 00:35:44,724  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-05 00:36:14,725  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-05 00:36:44,725  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-05 00:37:14,726  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-05 00:37:44,726  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-05 00:38:14,727  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-05 00:38:44,727  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-05 00:39:14,727  INFO      Queue paused (pause flag set) — waiting 30s
2026-06-05 00:39:44,728  INFO      Queue paused (pause flag set) — waiting 30s
```
