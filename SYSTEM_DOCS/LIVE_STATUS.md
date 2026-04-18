# LIVE STATUS — auto-updated every 5 minutes
> Last update: **2026-04-18 07:57:28 UTC**

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
| Current job | `dokumen.pub_the-practice-of-chinese-medicine-the-treatment-of-diseases-with-acupuncture-and-chinese-herbs-2nd-ed-9780443074905-2152393805-0443074909.pdf` (375 min) |
| Queued | 0 |
| Total books | 36 |
| Ingested | 74 |
| Vectors in medical_library | 17879 |
| Images pending approval | 2026 |
| Images approved | 0 |

## Video Transcription
| Metric | Value |
|---|---|
| Current job | `2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4` (16 min) |
| Queued | 14 |
| Done | 21 / 37 |
| Vectors in nrt_video_transcripts | 241 |

## System
| Metric | Value |
|---|---|
| RAM used | 9.81 GB / 32.86 GB (30%) |
| CPU | 99.8% |
| Disk used | 74.0 GB / 322.3 GB (24%) |
| Uptime | up 1 day, 2 hours, 22 minutes |

## Recent markers
- `2026-04-18T07:41:27.893583+00:00` **watchdog_restart** — transcription-queue hung (30 min stale) — restarted successfully
- `2026-04-18T07:40:19.016780+00:00` **book_ingested** — QRS101 Quick start - English.pdf → pemf_qrs: 1 chunks
- `2026-04-18T07:39:12.298134+00:00` **book_ingested** — QRS-101-Home-System-Brochure.pdf → pemf_qrs: 1 chunks
- `2026-04-18T07:36:11.549305+00:00` **book_ingested** — How to Use FlexBeam on Elbows - Recharge Health.pdf → rlt_flexbeam: 3 chunks
- `2026-04-18T07:33:27.975442+00:00` **book_ingested** — The QAT Life Pendant eu.pdf → qat_curriculum: 2 chunks

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
2026-04-18 07:11:27,742  INFO      Startup scan: 14 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-18 07:11:27,742  INFO      START  nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (1060 MB)
2026-04-18 07:11:27,743  INFO      Using existing segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4: 2 parts
2026-04-18 07:11:27,743  INFO      Transcribing 2 segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4
2026-04-18 07:41:27,944  INFO      ────────────────────────────────────────────────────────────
2026-04-18 07:41:27,944  INFO      Transcription queue manager started
2026-04-18 07:41:27,945  INFO      Startup scan: 14 untranscribed video(s) found, 0 new entry/entries added to queue
2026-04-18 07:41:27,946  INFO      START  nrt/2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4  (1060 MB)
2026-04-18 07:41:27,946  INFO      Using existing segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4: 2 parts
2026-04-18 07:41:27,946  INFO      Transcribing 2 segments for 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC.mp4
```
