# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-15 08:00:54 UTC**

## Services
| Service | Status |
|---|---|
| medical-rag-web | ✅ active |
| transcription-queue | ✅ active |
| ttyd | ✅ active |
| qdrant | ✅ healthy |
| ollama | ✅ healthy |

## Transcription
| Metric | Value |
|---|---|
| Current job | `Green_Square_Applications.mp4` (since 2026-04-15T07:59:07) |
| Queued | 13 |
| Done | 2 |
| Total videos | 15 |

## System
| Metric | Value |
|---|---|
| RAM used | 5.35 GB / 32.86 GB (16%) |
| CPU | 97.1% |
| Disk used | 39.6 GB / 322.3 GB (13%) |
| Uptime | up 22 hours, 18 minutes |

## Recent markers
- `2026-04-15T07:59:06` **transcription_done** — Emotional_Transformation_Technique.mp4 complete (2/15)
- `2026-04-15T07:34:21` **transcription_done** — Connection_to_the_Brain.mp4 complete (1/15)
- `2026-04-15T06:48:17` **test_marker** — notify.sh werkt correct

## Queue log (last 10 lines)
```
2026-04-15 06:39:19,806  INFO      DONE   qat/Anti-Inflammatory_Procedure.mp4  (722s)
2026-04-15 06:39:19,813  INFO      START  qat/Connection_to_the_Brain.mp4
2026-04-15 07:19:02,439  INFO      ────────────────────────────────────────────────────────────
2026-04-15 07:19:02,439  INFO      Transcription queue manager started
2026-04-15 07:19:02,441  INFO      Startup scan: 15 untranscribed video(s) found, 1 new entry/entries added to queue
2026-04-15 07:19:02,442  INFO      START  qat/Connection_to_the_Brain.mp4
2026-04-15 07:34:21,154  INFO      DONE   qat/Connection_to_the_Brain.mp4  (919s)
2026-04-15 07:34:21,276  INFO      START  qat/Emotional_Transformation_Technique.mp4
2026-04-15 07:59:06,987  INFO      DONE   qat/Emotional_Transformation_Technique.mp4  (1486s)
2026-04-15 07:59:07,054  INFO      START  qat/Green_Square_Applications.mp4
```
