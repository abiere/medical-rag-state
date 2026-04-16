# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 18:32:29 UTC**

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
| Current job | `NRT Lower Body.pdf` (9 min) |
| Queued | 34 |
| Total books | 43 |
| Ingested | 5 |
| Vectors in medical_library | 2773 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (1137 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 158 |

## System
| Metric | Value |
|---|---|
| RAM used | 10.94 GB / 32.86 GB (33%) |
| CPU | 49.7% |
| Disk used | 58.8 GB / 322.3 GB (19%) |
| Uptime | up 2 days, 8 hours, 49 minutes |

## Recent markers
- `2026-04-16T18:23:07.585962+00:00` **book_ingested** — The QAT Life Pendant eu.pdf → nrt_qat_curriculum: 2 chunks
- `2026-04-16T18:20:33.462183+00:00` **book_ingested** — The QAT Connect to the Brain eu.pdf → nrt_qat_curriculum: 2 chunks
- `2026-04-16T18:17:52.390512+00:00` **book_ingested** — The Acupuncture Pendant eu.pdf → nrt_qat_curriculum: 2 chunks
- `2026-04-16T18:15:14.315474+00:00` **book_ingested** — Quantum Alignment Technique - Home Study  2025 01092025.pdf → nrt_qat_curriculum: 47 chunks
- `2026-04-16T18:04:40.726696+00:00` **book_ingested** — QAT_2025_overgenomen.pdf → nrt_qat_curriculum: 72 chunks

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
2026-04-16 18:27:47,557  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:28:17,558  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:28:47,560  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:29:17,561  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:29:47,562  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:30:17,563  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:30:47,564  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:31:17,566  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:31:47,568  INFO      Queue paused (pause flag set) — waiting 30s
2026-04-16 18:32:17,569  INFO      Queue paused (pause flag set) — waiting 30s
```
