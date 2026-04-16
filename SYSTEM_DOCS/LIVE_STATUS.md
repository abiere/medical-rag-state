# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 19:02:30 UTC**

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
| Current job | `NRT Upper Body.pdf` (4 min) |
| Queued | 33 |
| Total books | 43 |
| Ingested | 6 |
| Vectors in medical_library | 2773 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (1167 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 11.08 GB / 32.86 GB (34%) |
| CPU | 50.3% |
| Disk used | 59.1 GB / 322.3 GB (19%) |
| Uptime | up 2 days, 9 hours, 19 minutes |

## Recent markers
- `2026-04-16T18:57:31.237178+00:00` **book_ingested** — NRT Lower Body.pdf → nrt_qat_curriculum: 132 chunks
- `2026-04-16T18:23:07.585962+00:00` **book_ingested** — The QAT Life Pendant eu.pdf → nrt_qat_curriculum: 2 chunks
- `2026-04-16T18:20:33.462183+00:00` **book_ingested** — The QAT Connect to the Brain eu.pdf → nrt_qat_curriculum: 2 chunks
- `2026-04-16T18:17:52.390512+00:00` **book_ingested** — The Acupuncture Pendant eu.pdf → nrt_qat_curriculum: 2 chunks
- `2026-04-16T18:15:14.315474+00:00` **book_ingested** — Quantum Alignment Technique - Home Study  2025 01092025.pdf → nrt_qat_curriculum: 47 chunks

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
2026-04-16 18:57:47,633  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:58:17,634  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:58:47,634  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:59:17,635  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:59:47,636  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:00:17,637  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:00:47,639  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:01:17,640  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:01:47,641  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 19:02:17,641  INFO      Queue paused (pause flag set) — waiting 30s
```
