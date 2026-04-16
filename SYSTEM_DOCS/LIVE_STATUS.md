# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 18:07:28 UTC**

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
| Current job | `Quantum Alignment Technique - Home Study  2025 01092025.pdf` (2 min) |
| Queued | 38 |
| Total books | 43 |
| Ingested | 3 |
| Vectors in medical_library | 2773 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (1112 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 10.89 GB / 32.86 GB (33%) |
| CPU | 51.5% |
| Disk used | 58.6 GB / 322.3 GB (19%) |
| Uptime | up 2 days, 8 hours, 24 minutes |

## Recent markers
- `2026-04-16T18:04:40.726696+00:00` **book_ingested** — QAT_2025_overgenomen.pdf → nrt_qat_curriculum: 72 chunks
- `2026-04-16T17:54:00.668773+00:00` **book_ingested** — 02_travell_simons_myofascial_pain_vol1.pdf → medical_library: 1760 chunks
- `2026-04-16T17:08:48.701647+00:00` **book_ingested** — 01_deadman_manual_of_acupuncture.pdf → medical_library: 1013 chunks
- `2026-04-16T05:20:54.750223+00:00` **watchdog_restart** — book-ingest-queue hung (41 min stale) — restarted successfully
- `2026-04-16T04:40:08.074792+00:00` **watchdog_restart** — book-ingest-queue hung (31 min stale) — restarted successfully

## Nightly Consistency
```
  TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_2.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Organs_and_Glands_Review.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Pair_Balancing.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Neuromuscular_ReEducation.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_3.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Anti-Inflammatory_Procedure.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_1.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Indicator_Muscle.json (type: qat)
```

## Queue log (last 10 lines)
```
2026-04-16 18:02:47,507  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:03:17,508  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:03:47,510  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:04:17,511  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:04:47,511  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:05:17,512  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:05:47,514  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:06:17,515  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:06:47,516  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:07:17,517  INFO      Queue paused (pause flag set) — waiting 30s
```
