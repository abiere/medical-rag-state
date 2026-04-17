# Maintenance Report — Medical RAG

**Datum:** 17-04-2026 00:30:36  
**Duur:** 186.9s  
**Uitslag:** ⚠️ WARNING  

---

## Samenvatting

| Fase | Status | Duur | Bevinding |
|---|---|---|---|
| Pre-checks | ✅ OK | 0.0s | Schijf: 249.9 GB vrij, 19% gebruikt |
| Qdrant maintenance | ✅ OK | 0.4s | video_transcripts: 0 vectoren, optimizer: ok |
| Data consistentie | ⚠️ WARNING | 167.1s | 0 boeken in metadata, 0 ingested |
| Retroaudit chunks | ✅ OK | 0.0s | Claude API actief — retroaudit wordt op aanvraag uitgevoerd via UI |
| Afbeelding screening | ✅ OK | 0.0s | Tijdsbudget afbeelding screening: 24300s |
| State integriteit | ✅ OK | 1.2s | State integriteit: 38 voltooide boeken gecontroleerd, 2 OK, 0 mismat… |
| Software check | ⚠️ WARNING | 18.1s | 86 pip-pakket(ten) verouderd: |
| Opruimen | ✅ OK | 0.0s | /tmp: 17 verouderd(e) bestand(en) verwijderd |

**Schijf voor:** 249.9 GB vrij  
**Schijf na:** 249.8 GB vrij  
**Vrijgemaakt:** —  

---

## ✅ Pre-checks

- Schijf: 249.9 GB vrij, 19% gebruikt
- RAM: 29.4 GB beschikbaar, 10% gebruikt
- Qdrant: ✓ online
- Ollama: ✓ online (llama3.1:8b)
- Docker: 2 container(s) actief
  • qdrant: Up 2 days (healthy)
  • ollama: Up 2 days (healthy)

## ✅ Qdrant maintenance

- video_transcripts: 0 vectoren, optimizer: ok
- video_transcripts: snapshot aangemaakt: video_transcripts-5527570280445304-2026-04-17-00-30-36.snapshot
  → opgeslagen (2.0 MB)
- medical_library: 0 vectoren, optimizer: ok
- medical_library: snapshot aangemaakt: medical_library-5527570280445304-2026-04-17-00-30-36.snapshot
  → opgeslagen (43.4 MB)
- nrt_qat_curriculum: 0 vectoren, optimizer: ok
- nrt_qat_curriculum: snapshot aangemaakt: nrt_qat_curriculum-5527570280445304-2026-04-17-00-30-36.snapshot
  → opgeslagen (6.8 MB)
- device_documentation: 0 vectoren, optimizer: ok
- device_documentation: snapshot aangemaakt: device_documentation-5527570280445304-2026-04-17-00-30-36.snapshot
  → opgeslagen (2.1 MB)

## ⚠️ Data consistentie

- 0 boeken in metadata, 0 ingested
- 3071 afbeeldingen gecontroleerd — geen wees-bestanden
- Consistentie: geen problemen gevonden
- Transcripts: 16 bestanden, 0 in Qdrant, 16 ontbreken
  → her-ingestered: Neurological_Disorganization.json
  → her-ingestered: Locating_Acupuncture_Points.json
  → her-ingestered: Provocative_Testing.json
  → her-ingestered: Emotional_Transformation_Technique.json
  → her-ingestered: Meridian_Testing_and_Treatment.json
  → her-ingestered: Green_Square_Applications.json
  → her-ingestered: 1.Lower_Body_Techniques.json
  → her-ingestered: Connection_to_the_Brain.json
  → her-ingestered: Manual_Muscle_Testing_2.json
  → her-ingestered: Organs_and_Glands_Review.json
  → her-ingestered: Pair_Balancing.json
  → her-ingestered: Neuromuscular_ReEducation.json
  → her-ingestered: Manual_Muscle_Testing_3.json
  → her-ingestered: Anti-Inflammatory_Procedure.json
  → her-ingestered: Manual_Muscle_Testing_1.json
  → her-ingestered: Indicator_Muscle.json
- Transcripts: 16 bestand(en) her-ingestered
- Boeken: 35 goedgekeurde audit(s) gecontroleerd, 1 ontbreken in Qdrant, 1 her-in-wachtrij gezet
  → terug in wachtrij gezet: test_acupuncture.pdf

## ✅ Retroaudit chunks

- Claude API actief — retroaudit wordt op aanvraag uitgevoerd via UI

## ✅ Afbeelding screening

- Tijdsbudget afbeelding screening: 24300s
- NRT UB Techniques and Fundamentals - Times.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- NRT Upper Body.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- How to Use FlexBeam to Boost Your Immunity - Recharge Health.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- The Acupuncture Pendant eu.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- How to Use FlexBeam on Feet and Ankles - Recharge Health.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- FlexBeam Applications and Usage Guide - Recharge Health.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- Warnings and Cautions – Recharge.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- 02_travell_simons_myofascial_pain_vol1.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- How to Use FlexBeam on Skin and Scars - Recharge Health.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- How Does Red Light Therapy Work_ – Recharge.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- How to Use FlexBeam to Boost Your Energy - Recharge Health.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- Why FlexBeam - Recharge Health.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- 01_deadman_manual_of_acupuncture.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- Advanced Seminar Manual- HS 08272022.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- Quantum Alignment Technique - Home Study  2025 01092025.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- The QAT Connect to the Brain eu.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- How to Use FlexBeam to Improve Your Breathing - Recharge Health.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- The QAT Life Pendant eu.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- Miraculous Sequence - Times.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- Warnings and Cautions - Recharge Health.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- How to Use FlexBeam on Hips - Recharge Health.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- White-Paper-FlexBeam-Targeted-Red-Light-Device.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- how-flexbeam-works-for-your-body.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- How to Use FlexBeam to Sleep Better - Recharge Health.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- How to Use FlexBeam on Elbows - Recharge Health.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- flexbeam-wellness-ifu-2024-v2-19.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- How to Use FlexBeam for Menstrual Cramps - Recharge Health.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- FlexBeam_RLT_Documentation.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- NRT Lower Body.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- QAT_2025_overgenomen.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- How to Use FlexBeam on Lower Back - Recharge Health.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- How FlexBeam Works Using Red Light Therapy Principles – Recharge.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- 16 Expanded Revised and New Techniques - Times.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- How to Use FlexBeam on Shoulders - Recharge Health.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- How to Reset 23 More Muscles - Times.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- Everything Reset Sequence - Times.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- NRT LB Techniques and Fundamentals - Times.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- How to Use FlexBeam to Help Relieve Anxiety - Recharge Health.pdf: 0 afbeeldingen gescreend (skip=0 err=0)
- Totaal: 38 boek(en) gescreend, 0 afbeeldingen verwerkt

## ✅ State integriteit

- State integriteit: 38 voltooide boeken gecontroleerd, 2 OK, 0 mismatches
- NRT UB Techniques and Fundamentals - Times.pdf: 0 chunks — qdrant was leeg bij embed?
- NRT Upper Body.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Use FlexBeam to Boost Your Immunity - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- The Acupuncture Pendant eu.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Use FlexBeam on Feet and Ankles - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- FlexBeam Applications and Usage Guide - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- Warnings and Cautions – Recharge.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Use FlexBeam on Skin and Scars - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- How Does Red Light Therapy Work_ – Recharge.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Use FlexBeam to Boost Your Energy - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- Why FlexBeam - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- Advanced Seminar Manual- HS 08272022.pdf: 0 chunks — qdrant was leeg bij embed?
- Quantum Alignment Technique - Home Study  2025 01092025.pdf: 0 chunks — qdrant was leeg bij embed?
- The QAT Connect to the Brain eu.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Use FlexBeam to Improve Your Breathing - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- The QAT Life Pendant eu.pdf: 0 chunks — qdrant was leeg bij embed?
- Miraculous Sequence - Times.pdf: 0 chunks — qdrant was leeg bij embed?
- Warnings and Cautions - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Use FlexBeam on Hips - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- White-Paper-FlexBeam-Targeted-Red-Light-Device.pdf: 0 chunks — qdrant was leeg bij embed?
- how-flexbeam-works-for-your-body.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Use FlexBeam to Sleep Better - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Use FlexBeam on Elbows - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- flexbeam-wellness-ifu-2024-v2-19.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Use FlexBeam for Menstrual Cramps - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- FlexBeam_RLT_Documentation.pdf: 0 chunks — qdrant was leeg bij embed?
- NRT Lower Body.pdf: 0 chunks — qdrant was leeg bij embed?
- QAT_2025_overgenomen.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Use FlexBeam on Lower Back - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- How FlexBeam Works Using Red Light Therapy Principles – Recharge.pdf: 0 chunks — qdrant was leeg bij embed?
- 16 Expanded Revised and New Techniques - Times.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Use FlexBeam on Shoulders - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Reset 23 More Muscles - Times.pdf: 0 chunks — qdrant was leeg bij embed?
- Everything Reset Sequence - Times.pdf: 0 chunks — qdrant was leeg bij embed?
- NRT LB Techniques and Fundamentals - Times.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Use FlexBeam to Help Relieve Anxiety - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?

## ⚠️ Software check

- 86 pip-pakket(ten) verouderd:
  • antlr4-python3-runtime  4.9.3 → 4.13.2
  • Automat  22.10.0 → 25.4.16
  • Babel  2.10.3 → 2.18.0
  • blinker  1.7.0 → 1.9.0
  • boto3  1.34.46 → 1.42.90
  • botocore  1.34.46 → 1.42.90
  • chardet  5.2.0 → 7.4.3
  • chromadb  1.5.7 → 1.5.8
  • configobj  5.0.8 → 5.0.9
  • cryptography  41.0.7 → 46.0.7
  • cuda-pathfinder  1.5.2 → 1.5.3
  • cuda-toolkit  13.0.2 → 13.2.1
  • dbus-python  1.3.2 → 1.4.0
  • docker  5.0.3 → 7.1.0
  • docling  2.88.0 → 2.89.0
  • docling-parse  5.8.0 → 5.9.0
  • fastapi  0.135.3 → 0.136.0
  • filelock  3.25.2 → 3.28.0
  • httplib2  0.20.4 → 0.31.2
  • huggingface_hub  1.10.2 → 1.11.0
  • idna  3.6 → 3.11
  • importlib_metadata  8.7.1 → 9.0.0
  • incremental  22.10.0 → 24.11.0
  • Jinja2  3.1.2 → 3.1.6
  • jmespath  1.0.1 → 1.1.0
  • jsonpatch  1.32 → 1.33
  • jsonpointer  2.0 → 3.1.1
  • latex2mathml  3.80.0 → 3.81.0
  • launchpadlib  1.11.0 → 2.1.0
  • lazr.uri  1.0.6 → 1.0.7
  • markdown-it-py  3.0.0 → 4.0.0
  • MarkupSafe  2.1.5 → 3.0.3
  • mpmath  1.3.0 → 1.4.1
  • nvidia-cublas  13.1.0.3 → 13.4.0.1
  • nvidia-cuda-cupti  13.0.85 → 13.2.75
  • nvidia-cuda-nvrtc  13.0.88 → 13.2.78
  • nvidia-cuda-runtime  13.0.96 → 13.2.75
  • nvidia-cudnn-cu13  9.19.0.56 → 9.21.0.82
  • nvidia-cufft  12.0.0.61 → 12.2.0.46
  • nvidia-cufile  1.15.1.6 → 1.17.1.22
  • nvidia-curand  10.4.0.35 → 10.4.2.55
  • nvidia-cusolver  12.0.4.66 → 12.2.0.1
  • nvidia-cusparse  12.6.3.3 → 12.7.10.1
  • nvidia-cusparselt-cu13  0.8.0 → 0.9.0
  • nvidia-nccl-cu13  2.28.9 → 2.29.7
  • nvidia-nvjitlink  13.0.88 → 13.2.78
  • nvidia-nvshmem-cu13  3.4.5 → 3.6.5
  • nvidia-nvtx  13.0.85 → 13.2.75
  • oauthlib  3.2.2 → 3.3.1
  • opencv-python-headless  4.11.0.86 → 4.13.0.92
  • packaging  24.0 → 26.1
  • pdfminer.six  20251230 → 20260107
  • pillow  10.4.0 → 12.2.0
  • pip  24.0 → 26.0.1
  • protobuf  6.33.6 → 7.34.1
  • pyasn1  0.4.8 → 0.6.3
  • pyasn1-modules  0.2.8 → 0.4.2
  • pydantic  2.13.0 → 2.13.1
  • pydantic_core  2.46.0 → 2.46.1
  • Pygments  2.17.2 → 2.20.0
  • PyGObject  3.48.2 → 3.56.2
  • PyJWT  2.7.0 → 2.12.1
  • pyOpenSSL  23.2.0 → 26.0.0
  • pyparsing  3.1.1 → 3.3.2
  • pypdf  6.10.1 → 6.10.2
  • pypdfium2  4.30.0 → 5.7.0
  • python-dateutil  2.8.2 → 2.9.0.post0
  • python-debian  0.1.49+ubuntu2 → 1.1.0
  • python-dotenv  1.0.1 → 1.2.2
  • pytz  2024.1 → 2026.1.post1
  • PyYAML  6.0.1 → 6.0.3
  • rich  13.7.1 → 15.0.0
  • s3transfer  0.10.1 → 0.16.0
  • semchunk  3.2.5 → 4.0.0
  • service-identity  24.1.0 → 24.2.0
  • setuptools  68.1.2 → 82.0.1
  • six  1.16.0 → 1.17.0
  • ssh-import-id  5.11 → 5.13
  • texttable  1.6.7 → 1.7.0
  • Twisted  24.3.0 → 25.5.0
  • typer  0.21.2 → 0.24.1
  • urllib3  2.0.7 → 2.6.3
  • wadllib  1.3.6 → 2.0.0
  • websocket-client  1.7.0 → 1.9.0
  • wheel  0.42.0 → 0.46.3
  • zope.interface  6.1 → 8.3
- Docker images:
  • ollama/ollama:latest	3 days ago	9.89GB
  • qdrant/qdrant:latest	3 weeks ago	285MB
- Qdrant nieuwste release: v1.17.1 (2026-03-27)
- Ollama nieuwste release: v0.20.7 (2026-04-13)

## ✅ Opruimen

- /tmp: 17 verouderd(e) bestand(en) verwijderd
- Totaal vrijgemaakt: 99 KB

---

## Qdrant vectortelling

| Collectie | Vectoren |
|---|---|
| `video_transcripts` | 0 |
| `medical_library` | 0 |
| `nrt_qat_curriculum` | 0 |
| `device_documentation` | 0 |

---

## ⚠ Data-inconsistenties

- TRANSCRIPT ONTBREEKT IN QDRANT: Neurological_Disorganization.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Locating_Acupuncture_Points.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Provocative_Testing.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Emotional_Transformation_Technique.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Meridian_Testing_and_Treatment.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Green_Square_Applications.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: 1.Lower_Body_Techniques.json (type: nrt)
- TRANSCRIPT ONTBREEKT IN QDRANT: Connection_to_the_Brain.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_2.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Organs_and_Glands_Review.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Pair_Balancing.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Neuromuscular_ReEducation.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_3.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Anti-Inflammatory_Procedure.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_1.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Indicator_Muscle.json (type: qat)
- BOEK ONTBREEKT IN QDRANT: test_acupuncture.pdf (collectie: medical_library)

---

## Aanbevelingen

- **Pip-pakketten:** Update selectief met `pip install <pakket> --break-system-packages`. Nooit `pip install --upgrade-all` — kan LlamaIndex/Docling breken.
- **Inconsistenties:** Draai `ingest_books.py` opnieuw voor de genoemde bestanden, of verwijder de vermeldingen uit `data/books_metadata.json`.

---

*Gegenereerd door `scripts/nightly_maintenance.py` op 17-04-2026 00:30:36*