# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-08-29 00:35:13 UTC**

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
| RAM used | 5.26 GB / 32.86 GB (16%) |
| CPU | 7.0% |
| Disk used | 94.9 GB / 322.3 GB (31%) |
| Uptime | up 19 weeks, 18 hours, 59 minutes |

## Recent markers
- `2026-08-29T00:31:24` **queue_empty** — All 13 videos transcribed
- `2026-08-29T00:31:24` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (55/13)
- `2026-08-29T00:31:24` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED
- `2026-08-29T00:31:24` **transcription_done** — NRT_Fascial_Activation_Application_Method.mp4 complete (55/13)
- `2026-08-29T00:31:24` **ingest_failed** — NRT_Fascial_Activation_Application_Method.mp4 ingest FAILED

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
2026-08-29 00:31:55,215  INFO      ────────────────────────────────────────────────────────────
2026-08-29 00:31:55,216  INFO      Transcription queue manager started
2026-08-29 00:31:55,217  INFO      Startup scan: 13 untranscribed video(s) found, 13 new entry/entries added to queue
2026-08-29 00:31:55,217  INFO      Queue paused (pause flag set) — waiting 30s
2026-08-29 00:32:25,217  INFO      Queue paused (pause flag set) — waiting 30s
2026-08-29 00:32:55,218  INFO      Queue paused (pause flag set) — waiting 30s
2026-08-29 00:33:25,218  INFO      Queue paused (pause flag set) — waiting 30s
2026-08-29 00:33:55,219  INFO      Queue paused (pause flag set) — waiting 30s
2026-08-29 00:34:25,219  INFO      Queue paused (pause flag set) — waiting 30s
2026-08-29 00:34:55,220  INFO      Queue paused (pause flag set) — waiting 30s
```
