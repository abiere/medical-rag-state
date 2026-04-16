# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 18:22:28 UTC**

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
| Current job | `The QAT Life Pendant eu.pdf` (1 min) |
| Queued | 35 |
| Total books | 43 |
| Ingested | 5 |
| Vectors in medical_library | 2773 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (1127 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 10.97 GB / 32.86 GB (33%) |
| CPU | 48.5% |
| Disk used | 58.6 GB / 322.3 GB (19%) |
| Uptime | up 2 days, 8 hours, 39 minutes |

## Recent markers
- `2026-04-16T18:20:33.462183+00:00` **book_ingested** — The QAT Connect to the Brain eu.pdf → nrt_qat_curriculum: 2 chunks
- `2026-04-16T18:17:52.390512+00:00` **book_ingested** — The Acupuncture Pendant eu.pdf → nrt_qat_curriculum: 2 chunks
- `2026-04-16T18:15:14.315474+00:00` **book_ingested** — Quantum Alignment Technique - Home Study  2025 01092025.pdf → nrt_qat_curriculum: 47 chunks
- `2026-04-16T18:04:40.726696+00:00` **book_ingested** — QAT_2025_overgenomen.pdf → nrt_qat_curriculum: 72 chunks
- `2026-04-16T17:54:00.668773+00:00` **book_ingested** — 02_travell_simons_myofascial_pain_vol1.pdf → medical_library: 1760 chunks

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
2026-04-16 18:17:47,538  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:18:17,539  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:18:47,540  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:19:17,540  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:19:47,541  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:20:17,541  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:20:47,542  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:21:17,543  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:21:47,543  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:22:17,544  INFO      Queue paused (pause flag set) — waiting 30s
```
