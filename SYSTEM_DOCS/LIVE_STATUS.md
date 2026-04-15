# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-15 19:41:32 UTC**

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
| Current job | `pdfcoffee.com_a-manual-of-acupuncture-peter-deadmanpdf-4-pdf-free.pdf` (36 min) |
| Queued | 2 |
| Total books | 3 |
| Ingested | 1 |
| Vectors in medical_library | 2 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Lower_Body_Techniques.mp4` (215 min) |
| Queued | 20 |
| Done | 15 / 35 |
| Vectors in video_transcripts | 6 |

## System
| Metric | Value |
|---|---|
| RAM used | 14.68 GB / 32.86 GB (45%) |
| CPU | 99.7% |
| Disk used | 54.1 GB / 322.3 GB (18%) |
| Uptime | up 1 day, 9 hours, 58 minutes |

## Recent markers
- `2026-04-15T11:28:04` **queue_empty** — All 15 videos transcribed
- `2026-04-15T11:28:04` **transcription_done** — Anti-Inflammatory_Procedure.mp4 complete (15/15)
- `2026-04-15T11:20:11` **transcription_done** — Provocative_Testing.mp4 complete (14/15)
- `2026-04-15T11:11:43` **transcription_done** — Pair_Balancing.mp4 complete (13/15)
- `2026-04-15T10:59:40` **transcription_done** — Organs_and_Glands_Review.mp4 complete (12/15)

## Queue log (last 10 lines)
```
2026-04-15 11:11:44,008  INFO      START  qat/Provocative_Testing.mp4
2026-04-15 11:20:11,143  INFO      DONE   qat/Provocative_Testing.mp4  (507s)
2026-04-15 11:20:11,261  INFO      START  qat/Anti-Inflammatory_Procedure.mp4
2026-04-15 11:28:04,345  INFO      DONE   qat/Anti-Inflammatory_Procedure.mp4  (473s)
2026-04-15 11:28:04,513  INFO      Queue empty — 15 video(s) processed. Exiting.
2026-04-15 11:28:04,629  INFO      Transcription queue manager done
2026-04-15 16:06:26,061  INFO      ────────────────────────────────────────────────────────────
2026-04-15 16:06:26,061  INFO      Transcription queue manager started
2026-04-15 16:06:26,063  INFO      Startup scan: 20 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-15 16:06:26,063  INFO      START  nrt/1.Lower_Body_Techniques.mp4
```
