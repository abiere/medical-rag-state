# DATA SNAPSHOT — 2026-04-19
> Opgesteld: 2026-04-19 ~19:20 UTC | Status: documentatie — geen wijziging
> Herstel komt later. Dit bestand legt vast wat er is op dit moment.

---

## 1. Qdrant collecties (live, 2026-04-19 ~19:20 UTC)

| Collectie | points_count | status | CLAUDE.md claim | CONTEXT.md claim |
|---|---|---|---|---|
| medical_library | **17.522** | green | 10.428 ❌ stale | 17.522 ✅ |
| nrt_curriculum | 425 | green | 425 ✅ | 425 ✅ |
| qat_curriculum | 125 | green | 125 ✅ | 125 ✅ |
| rlt_flexbeam | 160 | green | 160 ✅ | 160 ✅ |
| pemf_qrs | 64 | green | 64 ✅ | 64 ✅ |
| nrt_video_transcripts | **250** | green | 241 ❌ stale | 250 ✅ |
| qat_video_transcripts | **443** | green | 0 ❌ stale | 443 ✅ |

**Conclusie:** CONTEXT.md klopt. CLAUDE.md is stale (zie ISSUE-001).

---

## 2. book_classifications.json

- Bestand: `config/book_classifications.json`
- Versie: `1.1`
- Structuur: `{ version, last_updated, description, classifications: {...}, query_profiles: {...} }`
- **Aantal entries in `classifications`:** 60
- **Entries zonder `library_category`:** 0 — allen correct geclassificeerd ✅
- **Entries zonder `filename_patterns`:** onbekend — niet gecontroleerd in deze inventarisatie

**CLAUDE.md zegt:** "35 books, v1.1" — stale. Werkelijk: 60 entries.

---

## 3. ingest_cache state.json bestanden

- **Totaal:** 80 state.json bestanden in `data/ingest_cache/`
- **Verschil met book_classifications:** 60 (classifications) vs 80 (state.json) — 20 extra state.json bestanden. Dit kan komen door meerdere state.json per boek (bijv. deleted/orphan entries), recovery-stubs, of historische caches.

### Per collectie

| Collectie | state.json count |
|---|---|
| medical_library | 34 |
| nrt_curriculum | 9 |
| pemf_qrs | 7 |
| qat_curriculum | 5 |
| rlt_flexbeam | 25 |
| **Totaal** | **80** |

### Boeken zonder bestand op disk

**0 boeken** — alle state.json entries hebben een bijbehorend bestand op disk.

### manually_reviewed = True (14 entries)

Allen in `medical_library`:

| Bestand | Titel in state.json |
|---|---|
| Bates' Guide To Physical Examination and History Taking | Bates' Guide to Physical Examination and... |
| Sobotta Anatomy Textbook_nodrm.epub | Sobotta Anatomy Textbook |
| Quantum-Touch 2.0 - The New Human... | Quantum-Touch 2.0 - The New Human |
| CranioSacral Therapy Study Guide - Upledger.pdf | CranioSacral Therapy Study Guide |
| Quantum-Touch Core Transformation... | Quantum-Touch Core Transformation |
| Orthopedic Physical Assessment 7e editie - Magee... | ORTHOPEDIC PHYSICAL ASSESSMENT |
| Quantum-Touch_ The Power to Heal_nodrm.epub | Quantum-Touch |
| Anatomy Trains_ Myofascial Meridians... | Anatomy Trains |
| Sobotta Atlas of Anatomy Classic_nodrm.epub | Sobotta Atlas of Anatomy Classic |
| Sobotta Atlas of Anatomy, Vol.1, 17th ed... | Sobotta Atlas of Anatomy |
| Whole Brain Living_ The Anatomy of Choice... | WHOLE BRAIN LIVING |
| Sobotta Atlas of Anatomy, Vol. 3, 17th ed... | Sobotta Atlas of Anatomy, Vol. 3, 17th ed... |
| Sobotta Tables of Muscles, Joints and Nerves... | Sobotta Lerntabellen Anatomie Muskeln, G... |
| Sobotta Atlas of Anatomy, Vol. 2, 17th ed... | Sobotta Atlas of Anatomy |

**Opmerkingen:**
- `ORTHOPEDIC PHYSICAL ASSESSMENT` — all-caps in title veld, manually_reviewed=True
- `WHOLE BRAIN LIVING` — all-caps in title veld, manually_reviewed=True
- `Quantum-Touch` — 1-woord titel (te kort), manually_reviewed=True

---

## 4. Verdachte titels in book_metadata.title (43 van 80)

### medical_library (3 verdacht)

| Reden | Bestand |
|---|---|
| 1 woord kort | Quantum-Touch_ The Power to Heal_nodrm.epub |
| all-caps kort | Applied Kinesiology - Frost.pdf |
| all-caps kort | Whole Brain Living_ The Anatomy of Choice... |

### nrt_curriculum (9 leeg)

| Bestand |
|---|
| 16 Expanded Revised and New Techniques - Times.pdf |
| Miraculous Sequence - Times.pdf |
| Advanced Seminar Manual- HS 08272022.pdf |
| NRT LB Techniques and Fundamentals - Times.pdf |
| NRT Upper Body.pdf |
| How to Reset 23 More Muscles - Times.pdf |
| NRT Lower Body.pdf |
| Everything Reset Sequence - Times.pdf |
| NRT UB Techniques and Fundamentals - Times.pdf |

### qat_curriculum (5 leeg)

| Bestand |
|---|
| Quantum Alignment Technique - Home Study 2025 01092025.pdf |
| The QAT Connect to the Brain eu.pdf |
| The QAT Life Pendant eu.pdf |
| QAT_2025_overgenomen.pdf |
| The Acupuncture Pendant eu.pdf |

### pemf_qrs (5 leeg)

| Bestand |
|---|
| QRS Quantron Resonance 101 Home System.pdf |
| QRS-101-Home-System-Brochure.pdf |
| QRS 101 Operating Manual.pdf |
| QRS 101 Indication Settings English.pdf |
| QRS-101 Manual Englisch.pdf |

### rlt_flexbeam (21 leeg)

| Bestand |
|---|
| How to Use FlexBeam to Sleep Better - Recharge Health.pdf |
| How FlexBeam Works Using Red Light Therapy Principles – Recharge.pdf |
| flexbeam-wellness-ifu-2024-v2-19.pdf |
| how-flexbeam-works-for-your-body.pdf |
| How to Use FlexBeam on Hips - Recharge Health.pdf |
| Warnings and Cautions - Recharge Health.pdf |
| How to Use FlexBeam for Menstrual Cramps - Recharge Health.pdf |
| FlexBeam Applications and Usage Guide - Recharge Health.pdf |
| FlexBeam_RLT_Documentation.pdf |
| Why FlexBeam - Recharge Health.pdf |
| How to Use FlexBeam to Boost Your Energy - Recharge Health.pdf |
| How Does Red Light Therapy Work_ – Recharge.pdf |
| How to Use FlexBeam to Improve Your Breathing - Recharge Health.pdf |
| How to Use FlexBeam on Lower Back - Recharge Health.pdf |
| How to Use FlexBeam to Boost Your Immunity - Recharge Health.pdf |
| How to Use FlexBeam on Feet and Ankles - Recharge Health.pdf |
| How to Use FlexBeam to Help Relieve Anxiety - Recharge Health.pdf |
| How to Use FlexBeam on Shoulders - Recharge Health.pdf |
| How to Use FlexBeam on Skin and Scars - Recharge Health.pdf |
| Warnings and Cautions – Recharge.pdf |
| White-Paper-FlexBeam-Targeted-Red-Light-Device.pdf |

**Mogelijke verklaring:** NRT/QAT/RLT/PEMF bestanden zijn marketing-PDFs zonder formele titelpagina. Gemini Vision heeft hier geen bruikbare metadata kunnen extraheren. Dit is mogelijk verwacht gedrag — geen boek-metadata extractie geconfigureerd voor deze collecties. **Te bevestigen door architect.**

---

## 5. Orphan state.json (niet gematcht door book_classifications filename_patterns)

**1 orphan gevonden:**

| Collectie | Hash | Bestand |
|---|---|---|
| pemf_qrs | e4a45c224e71150e | Levels Mat, Pillow, Pen.pdf |

**Opmerking:** Dit is tevens een permanently_failed ingest-entry (zie §7).

---

## 6. Boeken in maintenance report maar niet in Qdrant

Bron: SYSTEM_DOCS/MAINTENANCE_REPORT.md nachtrun 19-apr 00:31.

| Bestand | Collectie | Toelichting |
|---|---|---|
| test_acupuncture.pdf | medical_library | Verwijderd in sessie 18 (2026-04-18) — uncommitted deletion in git status |
| Orthopedic Physical Assessment_nodrm.epub | medical_library | manually_reviewed=True; ingest-status onbekend |
| Touch for Health_ The Complete Edition...pdf | medical_library | Status onbekend |
| Bates Guide to Physical Examination 14e editie - Bickley.epub | medical_library | manually_reviewed=True |

**Opmerking:** test_acupuncture.pdf-deletion staat in git uncommitted (4619b1ff36fca875). De maintenance report is van vóór deze sessie; de feitelijke status van de andere 3 boeken is niet nader onderzocht.

---

## 7. Permanently failed book ingests

Bron: journalctl -u book-ingest-queue (live, 2026-04-19).

De volgende 4 boeken worden door book_ingest_queue.py permanent overgeslagen:

| Bestand | Collectie |
|---|---|
| How to Use FlexBeam on Knees - Recharge Health.pdf | rlt_flexbeam |
| How to Use FlexBeam on Neck - Recharge Health.pdf | rlt_flexbeam |
| How to Use FlexBeam on Stomach - Recharge Health.pdf | rlt_flexbeam |
| Levels Mat, Pillow, Pen.pdf | pemf_qrs |

Logmelding: `Skip (permanently failed — manual intervention required)`

**Opmerkingen:**
- De watchdog (book-ingest-watchdog.service) herstart book-ingest-queue elke minuut omdat die na leeg-draaien stopt
- De queue herstart, slaat de 4 entries over, ziet lege queue, stopt → watchdog herstart → herhaling
- Dit genereert ~60 restarts per uur in de logs

---

## 8. Transcriptie pipeline — video's vs transcripts

### Tellingen

| Type | Aantal |
|---|---|
| NRT video's op disk | 20 |
| QAT video's op disk | 15 |
| Transcript JSON-bestanden op disk | 55 (incl. part-bestanden) |
| Enkelvoudige transcripts (.json) | 22 |
| Multi-part transcripts (_partNNN.json) | 33 |

### NRT video's — transcript status

| Video | Transcript aanwezig |
|---|---|
| 1.Lower_Body_Techniques.mp4 | ✅ `1.Lower_Body_Techniques.json` |
| 1.Upper_Body_Techniques.mp4 | ✅ `_part000–003.json` (4 delen) |
| 16_Expanded__Revised__and_New_Techniques.mp4 | ✅ `.json` |
| 2.Lower_Body_Fundamentals.mp4 | ✅ `.json` |
| 2.Upper_Body_Fundamentals.mp4 | ✅ `.json` |
| 2021_Demos_Finding_and_Fixing_the_Glitch...mp4 | ✅ `_part000–001.json` (2 delen) |
| 3.Why_People_Hurt.mp4 | ✅ `.json` |
| Everything_Reset_Sequence_-_Part_1.mp4 | ✅ `_part000–002.json` (3 delen) |
| Everything_Reset_Sequence_-_Part_2.mp4 | ✅ `_part000–001.json` (2 delen) |
| Everything_Reset_Sequence_-_Part_3.mp4 | ✅ `_part000–001.json` (2 delen) |
| Everything_Reset_Sequence_-_Part_4.mp4 | ✅ `_part000–001.json` (2 delen) |
| Everything_Reset_Sequence_-_Part_5.mp4 | ✅ `_part000–001.json` (2 delen) |
| Healing_Organs_with_NRT.mp4 | ✅ `.json` |
| How_to_Reset_23_More_Muscles.mp4 | ✅ `_part000–001.json` (2 delen) |
| Miraculous_Sequence_-_Part_1.mp4 | ✅ `_part000–001.json` (2 delen) |
| Miraculous_Sequence_-_Part_2.mp4 | ✅ `_part000–001.json` (2 delen) |
| NRT_Brain_Reset...mp4 | ✅ `_part000–001.json` (2 delen) |
| NRT_Fascial_Activation_Application_Method.mp4 | ✅ `_part000–002.json` (3 delen) |
| NRT_for_Joint_Capsular_Ligaments...mp4 | ✅ `.json` |
| NRT_Sports_Specific_or_Universal_Reset.mp4 | ✅ `_part000–001.json` (2 delen) |

**Alle 20 NRT video's hebben transcript-bestanden op disk.**

Maar: de ingest-stap verwacht `{video_name}.json`. Voor de 13 video's met `_partNNN.json` wordt `{video_name}.json` niet gevonden → `ingest FAILED`. Zie ISSUE-004.

### QAT video's — transcript status

Alle 15 QAT video's hebben een bijbehorende `.json` op disk. Alle zijn succesvol ingested (443 vectors in qat_video_transcripts).

| Video | Transcript |
|---|---|
| Anti-Inflammatory_Procedure.mp4 | ✅ |
| Connection_to_the_Brain.mp4 | ✅ |
| Emotional_Transformation_Technique.mp4 | ✅ |
| Green_Square_Applications.mp4 | ✅ |
| Indicator_Muscle.mp4 | ✅ |
| Locating_Acupuncture_Points.mp4 | ✅ |
| Manual_Muscle_Testing_1.mp4 | ✅ |
| Manual_Muscle_Testing_2.mp4 | ✅ |
| Manual_Muscle_Testing_3.mp4 | ✅ |
| Meridian_Testing_and_Treatment.mp4 | ✅ |
| Neurological_Disorganization.mp4 | ✅ |
| Neuromuscular_ReEducation.mp4 | ✅ |
| Organs_and_Glands_Review.mp4 | ✅ |
| Pair_Balancing.mp4 | ✅ |
| Provocative_Testing.mp4 | ✅ |

---

## 9. Services (live, 2026-04-19 ~19:20 UTC)

| Service | Status | Opmerking |
|---|---|---|
| medical-rag-web.service | ✅ active running | Poort 8000 |
| ttyd.service | ✅ active running | Poort 7682 |
| book-ingest-watchdog.service | ✅ active running | Draait 2 dagen |
| qdrant (Docker) | ✅ healthy | 2 dagen up |
| ollama (Docker) | ✅ healthy | 2 dagen up |
| sync-status.timer | ✅ active waiting | Elke 5 min |
| queue-watchdog.timer | ✅ active waiting | Elke 10 min |
| medical-rag-maintenance.timer | ✅ active waiting | Dagelijks 00:31 |
| medical-rag-tests.timer | ✅ active waiting | Dagelijks 00:00 |
| book-ingest-queue.service | ⚪ inactive dead | Start, ziet lege queue, stopt in 100ms |
| transcription-queue.service | ⚠️ activating auto-restart | Verwerkt, stopt, herstart via Restart=always |
| medical-rag-maintenance.service | 🔴 failed | Nachtrun-service: failed state (na run 00:31) |
| medical-rag-tests.service | 🔴 failed | Test-service: failed state (na run) |

**Opmerking medical-rag-sync.timer:** Bestaat **niet** als systemd unit. CLAUDE.md health check verwijst hiernaar — dit is een fout in CLAUDE.md (zie ISSUE-002). De sync loopt via `sync-status.timer`.

---

## 10. Tests

- **39/39 GESLAAGD** — 0 mislukt, 0 overgeslagen
- Duur: 20.7s
- Laatste run: 2026-04-19 19:03 (auto) en nogmaals handmatig in deze sessie

---

## 11. AI configuratie (momentopname)

Bestand: `config/ai_settings.json`

| # | Use case | Provider | Model |
|---|---|---|---|
| 1 | book_metadata | gemini | gemini-2.5-flash |
| 2 | chunk_tagging | ollama | llama3.1:8b |
| 3 | chunk_audit | ollama | llama3.1:8b |
| 4 | ocr_correction | ollama | llama3.1:8b |
| 5 | image_description | gemini | gemini-2.5-flash |
| 6 | image_captioning | gemini | gemini-2.5-flash |
| 7 | rag_answering | ollama | llama3.1:8b |
| 8 | protocol_generation | ollama | llama3.1:8b |

---

## 12. Git status (2026-04-19 ~19:20 UTC)

- **Laatste commit:** `1cfebbd` 2026-04-19 19:14:31 UTC (`watchdog: log update`)
- **Uncommitted wijzigingen:** 45 bestanden
  - `M SYSTEM_DOCS/AI_STATUS.md` — auto-gegenereerd
  - `M SYSTEM_DOCS/MAINTENANCE_REPORT.md` — auto-gegenereerd
  - `D data/ingest_cache/00804fc4573d0453/state.json` — deletion (zie ISSUE-003)
  - `D data/ingest_cache/11c954ca86056dc4/state.json`
  - `D data/ingest_cache/2ce335d7c375fbd0/state.json`
  - `D data/ingest_cache/4619b1ff36fca875/*` — test_acupuncture.pdf (verwijderd sessie 18)
  - `D data/ingest_cache/9f3c129f024fc4ff/state.json`
  - ~37 `M data/ingest_cache/*/state.json` — gewijzigd door watchdog/nachtrun
- **Sync errors:** geen `data/sync_errors.log` aanwezig

**Opmerking:** `sync_status.timer` commitsonly SYSTEM_DOCS/ (elk 5 min). `data/ingest_cache/` wijzigingen worden niet automatisch gecommit — dit verklaart de ophoping van 45 uncommitted ingest_cache-bestanden.
