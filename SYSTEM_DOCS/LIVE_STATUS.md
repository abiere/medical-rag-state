# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-15 22:07:34 UTC**

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
| Current job | `359609833-Travell-and-Simons-Myofascial-Pain-and-Dysfunction-Vol-1-2nd-Ed-D-Simons-Et-Al-Williams-and-Wilkins-1999-WW.pdf` (11 min) |
| Queued | 2 |
| Total books | 3 |
| Ingested | 1 |
| Vectors in medical_library | 2 |
| Images pending approval | 0 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Lower_Body_Techniques.mp4` (361 min) |
| Queued | 20 |
| Done | 15 / 35 |
| Vectors in video_transcripts | 6 |

## System
| Metric | Value |
|---|---|
| RAM used | 16.42 GB / 32.86 GB (50%) |
| CPU | 96.4% |
| Disk used | 54.3 GB / 322.3 GB (18%) |
| Uptime | up 1 day, 12 hours, 24 minutes |

## Recent markers
- `2026-04-15T21:55:56.039018+00:00` **watchdog_restart** — book-ingest-queue hung (31 min stale) — restarted successfully
- `2026-04-15T21:24:34.596446+00:00` **watchdog_restart** — book-ingest-queue hung (32 min stale) — restarted successfully
- `2026-04-15T20:52:46.640439+00:00` **watchdog_restart** — book-ingest-queue hung (31 min stale) — restarted successfully
- `2026-04-15T20:21:38.292661+00:00` **watchdog_restart** — book-ingest-queue hung (77 min stale) — restarted successfully
- `2026-04-15T11:28:04` **queue_empty** — All 15 videos transcribed

## Nightly Consistency
```
_log niet gevonden_
```

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
