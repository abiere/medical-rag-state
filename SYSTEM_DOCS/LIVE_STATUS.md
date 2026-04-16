# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-16 00:41:09 UTC**

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
| Current job | `pdfcoffee.com_a-manual-of-acupuncture-peter-deadmanpdf-4-pdf-free.pdf` (10 min) |
| Queued | 2 |
| Total books | 3 |
| Ingested | 1 |
| Vectors in medical_library | 2 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (65 min) |
| Queued | 19 |
| Done | 16 / 35 |
| Vectors in video_transcripts | 111 |

## System
| Metric | Value |
|---|---|
| RAM used | 14.71 GB / 32.86 GB (45%) |
| CPU | 99.5% |
| Disk used | 54.3 GB / 322.3 GB (18%) |
| Uptime | up 1 day, 14 hours, 58 minutes |

## Recent markers
- `2026-04-16T00:30:40.058773+00:00` **watchdog_restart** — book-ingest-queue hung (31 min stale) — restarted successfully
- `2026-04-16T00:00:06.752609+00:00` **watchdog_restart** — book-ingest-queue hung (31 min stale) — restarted successfully
- `2026-04-15T23:35:25` **transcription_done** — 1.Lower_Body_Techniques.mp4 complete (16/20)
- `2026-04-15T23:35:25` **transcript_ingested** — 1.Lower_Body_Techniques.mp4 ingested into Qdrant
- `2026-04-15T23:28:56.799123+00:00` **watchdog_restart** — book-ingest-queue hung (31 min stale) — restarted successfully

## Nightly Consistency
```
_log niet gevonden_
```

## Queue log (last 10 lines)
```
2026-04-15 16:06:26,061  INFO      Transcription queue manager started
2026-04-15 16:06:26,063  INFO      Startup scan: 20 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-15 16:06:26,063  INFO      START  nrt/1.Lower_Body_Techniques.mp4
2026-04-15 23:33:49,373  INFO      DONE   nrt/1.Lower_Body_Techniques.mp4  (26843s)
2026-04-15 23:33:49,376  INFO      INGEST nrt/1.Lower_Body_Techniques.mp4
2026-04-15 23:35:25,255  INFO        [ingest] 1.Lower_Body_Techniques.json: 770 segments → 35 chunks
2026-04-15 23:35:25,255  INFO        [ingest] Loading embedding model …
2026-04-15 23:35:25,255  INFO        [ingest]   Ingested chunk 35/35 for 1.Lower_Body_Techniques.mp4
2026-04-15 23:35:25,255  INFO        [ingest] Done: 35 chunks ingested, 0 skipped (already exists)
2026-04-15 23:35:25,550  INFO      START  nrt/1.Upper_Body_Techniques.mp4
```
