# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-15 07:50:03 UTC**

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
| Current job | `Emotional_Transformation_Technique.mp4` (since 2026-04-15T07:34:21) |
| Queued | 14 |
| Done | 1 |
| Total videos | 15 |

## System
| Metric | Value |
|---|---|
| RAM used | 5.64 GB / 32.86 GB (17%) |
| CPU | 96.1% |
| Disk used | 39.6 GB / 322.3 GB (13%) |
| Uptime | up 22 hours, 7 minutes |

## Recent markers
- `2026-04-15T07:34:21` **transcription_done** — Connection_to_the_Brain.mp4 complete (1/15)
- `2026-04-15T06:48:17` **test_marker** — notify.sh werkt correct

## Queue log (last 10 lines)
```
2026-04-15 06:27:18,256  INFO      Startup scan: 15 untranscribed video(s) found, 15 new entry/entries added to queue
2026-04-15 06:27:18,256  INFO      START  qat/Anti-Inflammatory_Procedure.mp4
2026-04-15 06:39:19,806  INFO      DONE   qat/Anti-Inflammatory_Procedure.mp4  (722s)
2026-04-15 06:39:19,813  INFO      START  qat/Connection_to_the_Brain.mp4
2026-04-15 07:19:02,439  INFO      ────────────────────────────────────────────────────────────
2026-04-15 07:19:02,439  INFO      Transcription queue manager started
2026-04-15 07:19:02,441  INFO      Startup scan: 15 untranscribed video(s) found, 1 new entry/entries added to queue
2026-04-15 07:19:02,442  INFO      START  qat/Connection_to_the_Brain.mp4
2026-04-15 07:34:21,154  INFO      DONE   qat/Connection_to_the_Brain.mp4  (919s)
2026-04-15 07:34:21,276  INFO      START  qat/Emotional_Transformation_Technique.mp4
```
