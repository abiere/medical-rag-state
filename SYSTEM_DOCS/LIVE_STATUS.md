# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-18 13:43:32 UTC**

## Services
| Service | Status |
|---|---|
| medical-rag-web | ✅ active |
| transcription-queue | ✅ active |
| book-ingest-queue | ❌ inactive |
| ttyd | ✅ active |
| qdrant | ✅ healthy |
| ollama | ✅ healthy |

## Book Ingest
| Metric | Value |
|---|---|
| Current job | idle |
| Queued | 0 |
| Total books | 35 |
| Ingested | 74 |
| Vectors in medical_library | 18006 |
| Images pending approval | 2026 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `1.Upper_Body_Techniques.mp4` (11 min) |
| Queued | 13 |
| Done | 53 / 69 |
| Vectors in nrt_video_transcripts | 250 |

## System
| Metric | Value |
|---|---|
| RAM used | 6.62 GB / 32.86 GB (20%) |
| CPU | 96.6% |
| Disk used | 84.0 GB / 322.3 GB (27%) |
| Uptime | up 1 day, 8 hours, 8 minutes |

## Recent markers
- `2026-04-18T13:32:30.062230+00:00` **watchdog_restart** — transcription-queue hung (39 min stale) — restarted successfully
- `2026-04-18T12:53:54` **transcription_done** — NRT_for_Joint_Capsular_Ligaments_and_Tendons_Using_Direction_of_Ease_-_Demonstra.mp4 complete (51/14)
- `2026-04-18T12:53:54` **transcript_ingested** — NRT_for_Joint_Capsular_Ligaments_and_Tendons_Using_Direction_of_Ease_-_Demonstra.mp4 ingested into Qdrant
- `2026-04-18T12:42:47` **transcription_done** — NRT_Sports_Specific_or_Universal_Reset.mp4 complete (50/14)
- `2026-04-18T12:42:46` **ingest_failed** — NRT_Sports_Specific_or_Universal_Reset.mp4 ingest FAILED

## Nightly Consistency
```
  TRANSCRIPT ONTBREEKT IN QDRANT: Organs_and_Glands_Review.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: 2.Lower_Body_Fundamentals.json (type: nrt)
  TRANSCRIPT ONTBREEKT IN QDRANT: Pair_Balancing.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Neuromuscular_ReEducation.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_3.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Anti-Inflammatory_Procedure.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_1.json (type: qat)
  TRANSCRIPT ONTBREEKT IN QDRANT: Indicator_Muscle.json (type: qat)
```

## Queue log (last 10 lines)
```
2026-04-18 12:53:54,849  INFO      START  nrt/1.Upper_Body_Techniques.mp4  (525 MB)
2026-04-18 12:53:54,850  INFO      Splitting 1.Upper_Body_Techniques.mp4 (525 MB) into 20-min segments
2026-04-18 12:54:06,632  INFO      Split 1.Upper_Body_Techniques.mp4 into 4 segments
2026-04-18 12:54:06,632  INFO      Transcribing 4 segments for 1.Upper_Body_Techniques.mp4
2026-04-18 13:32:30,109  INFO      ────────────────────────────────────────────────────────────
2026-04-18 13:32:30,109  INFO      Transcription queue manager started
2026-04-18 13:32:30,111  INFO      Startup scan: 13 untranscribed video(s) found, 12 new entry/entries added to queue
2026-04-18 13:32:30,112  INFO      START  nrt/1.Upper_Body_Techniques.mp4  (525 MB)
2026-04-18 13:32:30,112  INFO      Using existing segments for 1.Upper_Body_Techniques.mp4: 4 parts
2026-04-18 13:32:30,112  INFO      Transcribing 4 segments for 1.Upper_Body_Techniques.mp4
```
