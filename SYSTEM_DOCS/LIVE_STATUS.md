# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-05-30 00:38:05 UTC**

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
| RAM used | 7.47 GB / 32.86 GB (23%) |
| CPU | 1.4% |
| Disk used | 91.9 GB / 322.3 GB (30%) |
| Uptime | up 6 weeks, 19 hours, 2 minutes |

## Recent markers
- `2026-05-30T00:30:23` **transcription_done** — 1.Upper_Body_Techniques.mp4 complete (55/13)
- `2026-05-30T00:30:23` **ingest_failed** — 1.Upper_Body_Techniques.mp4 ingest FAILED
- `2026-05-30T00:29:52` **queue_empty** — All 13 videos transcribed
- `2026-05-30T00:29:52` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-05-30T00:29:52` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED

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
2026-05-30 00:33:23,635  INFO      Queue paused (pause flag set) — waiting 30s
2026-05-30 00:33:53,635  INFO      Queue paused (pause flag set) — waiting 30s
2026-05-30 00:34:23,636  INFO      Queue paused (pause flag set) — waiting 30s
2026-05-30 00:34:53,636  INFO      Queue paused (pause flag set) — waiting 30s
2026-05-30 00:35:23,637  INFO      Queue paused (pause flag set) — waiting 30s
2026-05-30 00:35:53,637  INFO      Queue paused (pause flag set) — waiting 30s
2026-05-30 00:36:23,638  INFO      Queue paused (pause flag set) — waiting 30s
2026-05-30 00:36:53,638  INFO      Queue paused (pause flag set) — waiting 30s
2026-05-30 00:37:23,639  INFO      Queue paused (pause flag set) — waiting 30s
2026-05-30 00:37:53,639  INFO      Queue paused (pause flag set) — waiting 30s
```
