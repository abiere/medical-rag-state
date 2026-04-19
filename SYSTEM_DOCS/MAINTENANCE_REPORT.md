# Maintenance Report — Medical RAG

**Datum:** 19-04-2026 00:31:53  
**Duur:** 821.0s  
**Uitslag:** ⚠️ WARNING  

---

## Samenvatting

| Fase | Status | Duur | Bevinding |
|---|---|---|---|
| Pre-checks | ✅ OK | 0.1s | Schijf: 225.2 GB vrij, 27% gebruikt |
| Qdrant maintenance | ✅ OK | 1.4s | nrt_curriculum: 0 vectoren, optimizer: ok |
| Data consistentie | ⚠️ WARNING | 784.4s | 0 boeken in metadata, 0 ingested |
| Retroaudit chunks | ✅ OK | 0.0s | Claude API actief — retroaudit wordt op aanvraag uitgevoerd via UI |
| State integriteit | ✅ OK | 13.6s | State integriteit: 76 voltooide boeken gecontroleerd, 34 OK, 0 misma… |
| Software check | ⚠️ WARNING | 21.6s | 93 pip-pakket(ten) verouderd: |
| Opruimen | ✅ OK | 0.0s | /tmp: 5 verouderd(e) bestand(en) verwijderd |

**Schijf voor:** 225.2 GB vrij  
**Schijf na:** 224.8 GB vrij  
**Vrijgemaakt:** —  

---

## ✅ Pre-checks

- Schijf: 225.2 GB vrij, 27% gebruikt
- RAM: 30.1 GB beschikbaar, 8% gebruikt
- Qdrant: ✓ online
- Ollama: ✓ online (llama3.1:8b)
- Docker: 2 container(s) actief
  • qdrant: Up 43 hours (healthy)
  • ollama: Up 43 hours (healthy)

## ✅ Qdrant maintenance

- nrt_curriculum: 0 vectoren, optimizer: ok
- nrt_curriculum: snapshot aangemaakt: nrt_curriculum-5527570280445304-2026-04-19-00-31-53.snapshot
  → opgeslagen (5.4 MB)
- qat_curriculum: 0 vectoren, optimizer: ok
- qat_curriculum: snapshot aangemaakt: qat_curriculum-5527570280445304-2026-04-19-00-31-54.snapshot
  → opgeslagen (1.8 MB)
- rlt_flexbeam: 0 vectoren, optimizer: ok
- rlt_flexbeam: snapshot aangemaakt: rlt_flexbeam-5527570280445304-2026-04-19-00-31-54.snapshot
  → opgeslagen (2.1 MB)
- medical_library: 0 vectoren, optimizer: ok
- medical_library: snapshot aangemaakt: medical_library-5527570280445304-2026-04-19-00-31-54.snapshot
  → opgeslagen (179.1 MB)
- pemf_qrs: 0 vectoren, optimizer: ok
- pemf_qrs: snapshot aangemaakt: pemf_qrs-5527570280445304-2026-04-19-00-31-55.snapshot
  → opgeslagen (1.0 MB)
- nrt_video_transcripts: 0 vectoren, optimizer: ok
- nrt_video_transcripts: snapshot aangemaakt: nrt_video_transcripts-5527570280445304-2026-04-19-00-31-55.snapshot
  → opgeslagen (3.1 MB)
- qat_video_transcripts: 0 vectoren, optimizer: ok
- qat_video_transcripts: snapshot aangemaakt: qat_video_transcripts-5527570280445304-2026-04-19-00-31-55.snapshot
  → opgeslagen (1.5 MB)

## ⚠️ Data consistentie

- 0 boeken in metadata, 0 ingested
- 25640 afbeeldingen gecontroleerd — geen wees-bestanden
- Consistentie: geen problemen gevonden
- Transcripts: 55 bestanden, 0 in Qdrant, 55 ontbreken
  → her-ingestered: NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows_part001.json
  → her-ingestered: NRT_for_Joint_Capsular_Ligaments_and_Tendons_Using_Direction_of_Ease_-_Demonstra.json
  → her-ingestered: NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows_part000.json
  → her-ingestered: Everything_Reset_Sequence_-_Part_3_part000.json
  → her-ingestered: 16_Expanded__Revised__and_New_Techniques.json
  → her-ingestered: 2.Upper_Body_Fundamentals.json
  → her-ingestered: Everything_Reset_Sequence_-_Part_1_part001.json
  → her-ingestered: 1.Upper_Body_Techniques_part000.json
  → her-ingestered: 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC_part000.json
  → her-ingestered: Healing_Organs_with_NRT.json
  → her-ingestered: Miraculous_Sequence_-_Part_2_part000.json
  → her-ingestered: 3.Why_People_Hurt.json
  → her-ingestered: How_to_Reset_23_More_Muscles_part000.json
  → her-ingestered: Miraculous_Sequence_-_Part_1_part001.json
  → her-ingestered: Neurological_Disorganization.json
  → her-ingestered: Everything_Reset_Sequence_-_Part_2_part002.json
  → her-ingestered: Everything_Reset_Sequence_-_Part_5_part002.json
  → her-ingestered: Everything_Reset_Sequence_-_Part_5_part000.json
  → her-ingestered: Everything_Reset_Sequence_-_Part_4_part000.json
  → her-ingestered: Locating_Acupuncture_Points.json
  → her-ingestered: Provocative_Testing.json
  → her-ingestered: Emotional_Transformation_Technique.json
  → her-ingestered: How_to_Reset_23_More_Muscles_part001.json
  → her-ingestered: NRT_Fascial_Activation_Application_Method_part000.json
  → her-ingestered: Miraculous_Sequence_-_Part_2_part001.json
  → her-ingestered: Meridian_Testing_and_Treatment.json
  → her-ingestered: NRT_Fascial_Activation_Application_Method_part001.json
  → her-ingestered: 1.Upper_Body_Techniques_part003.json
  → her-ingestered: Green_Square_Applications.json
  → her-ingestered: Miraculous_Sequence_-_Part_1_part000.json
  → her-ingestered: 1.Upper_Body_Techniques_part001.json
  → her-ingestered: Everything_Reset_Sequence_-_Part_4_part002.json
  → her-ingestered: Everything_Reset_Sequence_-_Part_2_part000.json
  → her-ingestered: 1.Lower_Body_Techniques.json
  → her-ingestered: Everything_Reset_Sequence_-_Part_1_part000.json
  → her-ingestered: Connection_to_the_Brain.json
  → her-ingestered: Manual_Muscle_Testing_2.json
  → her-ingestered: Organs_and_Glands_Review.json
  → her-ingestered: Everything_Reset_Sequence_-_Part_5_part001.json
  → her-ingestered: 2.Lower_Body_Fundamentals.json
  → her-ingestered: Pair_Balancing.json
  → her-ingestered: NRT_Sports_Specific_or_Universal_Reset_part001.json
  → her-ingestered: Everything_Reset_Sequence_-_Part_3_part001.json
  → her-ingestered: NRT_Sports_Specific_or_Universal_Reset_part000.json
  → her-ingestered: NRT_Fascial_Activation_Application_Method_part002.json
  → her-ingestered: Neuromuscular_ReEducation.json
  → her-ingestered: Manual_Muscle_Testing_3.json
  → her-ingestered: Everything_Reset_Sequence_-_Part_2_part001.json
  → her-ingestered: Everything_Reset_Sequence_-_Part_1_part002.json
  → her-ingestered: 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC_part001.json
  → her-ingestered: Anti-Inflammatory_Procedure.json
  → her-ingestered: 1.Upper_Body_Techniques_part002.json
  → her-ingestered: Manual_Muscle_Testing_1.json
  → her-ingestered: Everything_Reset_Sequence_-_Part_4_part001.json
  → her-ingestered: Indicator_Muscle.json
- Transcripts: 55 bestand(en) her-ingestered
- Boeken: 74 goedgekeurde audit(s) gecontroleerd, 4 ontbreken in Qdrant, 0 her-in-wachtrij gezet
  → bestand niet gevonden op disk: test_acupuncture.pdf
  → bestand niet gevonden op disk: Orthopedic Physical Assessment_nodrm.epub
  → bestand niet gevonden op disk: Touch for Health_ The Complete Edition_ A Practical Guide to Natural Health With Acupressure Touch_nodrm.pdf
  → bestand niet gevonden op disk: Bates Guide to Physical Examination 14e editie - Bickley.epub

## ✅ Retroaudit chunks

- Claude API actief — retroaudit wordt op aanvraag uitgevoerd via UI

## ✅ State integriteit

- State integriteit: 76 voltooide boeken gecontroleerd, 34 OK, 0 mismatches
- Warnings and Cautions – Recharge.pdf: 0 chunks — qdrant was leeg bij embed?
- Advanced Seminar Manual- HS 08272022.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Use FlexBeam to Sleep Better - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- FlexBeam Applications and Usage Guide - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- How Does Red Light Therapy Work_ – Recharge.pdf: 0 chunks — qdrant was leeg bij embed?
- 16 Expanded Revised and New Techniques - Times.pdf: 0 chunks — qdrant was leeg bij embed?
- How FlexBeam Works Using Red Light Therapy Principles – Recharge.pdf: 0 chunks — qdrant was leeg bij embed?
- NRT LB Techniques and Fundamentals - Times.pdf: 0 chunks — qdrant was leeg bij embed?
- QRS 101 Operating Manual.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Reset 23 More Muscles - Times.pdf: 0 chunks — qdrant was leeg bij embed?
- Quantum Alignment Technique - Home Study  2025 01092025.pdf: 0 chunks — qdrant was leeg bij embed?
- how-flexbeam-works-for-your-body.pdf: 0 chunks — qdrant was leeg bij embed?
- flexbeam-wellness-ifu-2024-v2-19.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Use FlexBeam to Boost Your Energy - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Use FlexBeam on Feet and Ankles - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Use FlexBeam to Improve Your Breathing - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- The QAT Connect to the Brain eu.pdf: 0 chunks — qdrant was leeg bij embed?
- NRT Lower Body.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Use FlexBeam on Lower Back - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- Everything Reset Sequence - Times.pdf: 0 chunks — qdrant was leeg bij embed?
- The QAT Life Pendant eu.pdf: 0 chunks — qdrant was leeg bij embed?
- QRS-101 Manual Englisch.pdf: 0 chunks — qdrant was leeg bij embed?
- The Acupuncture Pendant eu.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Use FlexBeam on Shoulders - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- QAT_2025_overgenomen.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Use FlexBeam to Help Relieve Anxiety - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- White-Paper-FlexBeam-Targeted-Red-Light-Device.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Use FlexBeam to Boost Your Immunity - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Use FlexBeam for Menstrual Cramps - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- FlexBeam_RLT_Documentation.pdf: 0 chunks — qdrant was leeg bij embed?
- Warnings and Cautions - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- QRS 101 Indication Settings English.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Use FlexBeam on Hips - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- Miraculous Sequence - Times.pdf: 0 chunks — qdrant was leeg bij embed?
- NRT UB Techniques and Fundamentals - Times.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Use FlexBeam on Skin and Scars - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- Why FlexBeam - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?
- QRS Quantron Resonance 101 Home System.pdf: 0 chunks — qdrant was leeg bij embed?
- QRS-101-Home-System-Brochure.pdf: 0 chunks — qdrant was leeg bij embed?
- NRT Upper Body.pdf: 0 chunks — qdrant was leeg bij embed?
- QRS101 Quick start - English.pdf: 0 chunks — qdrant was leeg bij embed?
- How to Use FlexBeam on Elbows - Recharge Health.pdf: 0 chunks — qdrant was leeg bij embed?

## ⚠️ Software check

- 93 pip-pakket(ten) verouderd:
  • antlr4-python3-runtime  4.9.3 → 4.13.2
  • Automat  22.10.0 → 25.4.16
  • Babel  2.10.3 → 2.18.0
  • blinker  1.7.0 → 1.9.0
  • boto3  1.34.46 → 1.42.91
  • botocore  1.34.46 → 1.42.91
  • chardet  5.2.0 → 7.4.3
  • chromadb  1.5.7 → 1.5.8
  • configobj  5.0.8 → 5.0.9
  • cryptography  41.0.7 → 46.0.7
  • cuda-pathfinder  1.5.2 → 1.5.3
  • cuda-toolkit  13.0.2 → 13.2.1
  • dbus-python  1.3.2 → 1.4.0
  • docker  5.0.3 → 7.1.0
  • docling  2.88.0 → 2.90.0
  • docling-core  2.73.0 → 2.74.0
  • docling-parse  5.8.0 → 5.9.0
  • Faker  40.13.0 → 40.15.0
  • fastapi  0.135.3 → 0.136.0
  • filelock  3.25.2 → 3.28.0
  • google-ai-generativelanguage  0.6.15 → 0.11.0
  • grpcio-status  1.71.2 → 1.80.0
  • httplib2  0.20.4 → 0.31.2
  • huggingface_hub  1.10.2 → 1.11.0
  • identify  2.6.18 → 2.6.19
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
  • lxml  6.0.4 → 6.1.0
  • markdown-it-py  3.0.0 → 4.0.0
  • MarkupSafe  2.1.5 → 3.0.3
  • mempalace  3.3.0 → 3.3.1
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
  • protobuf  5.29.6 → 7.34.1
  • pyasn1  0.4.8 → 0.6.3
  • pyasn1-modules  0.2.8 → 0.4.2
  • pydantic  2.13.0 → 2.13.2
  • pydantic_core  2.46.0 → 2.46.2
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
  • ollama/ollama:latest	5 days ago	9.89GB
  • qdrant/qdrant:latest	3 weeks ago	285MB
- Qdrant nieuwste release: v1.17.1 (2026-03-27)
- Ollama nieuwste release: v0.21.0 (2026-04-16)

## ✅ Opruimen

- /tmp: 5 verouderd(e) bestand(en) verwijderd
- Totaal vrijgemaakt: 38 KB

---

## Qdrant vectortelling

| Collectie | Vectoren |
|---|---|
| `nrt_curriculum` | 0 |
| `qat_curriculum` | 0 |
| `rlt_flexbeam` | 0 |
| `medical_library` | 0 |
| `pemf_qrs` | 0 |
| `nrt_video_transcripts` | 0 |
| `qat_video_transcripts` | 0 |

---

## ⚠ Data-inconsistenties

- TRANSCRIPT ONTBREEKT IN QDRANT: NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows_part001.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: NRT_for_Joint_Capsular_Ligaments_and_Tendons_Using_Direction_of_Ease_-_Demonstra.json (type: nrt)
- TRANSCRIPT ONTBREEKT IN QDRANT: NRT_Brain_Reset_plus_NRT_Correction_for_Congested_or_Blocked_Meridian_Flows_part000.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Everything_Reset_Sequence_-_Part_3_part000.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: 16_Expanded__Revised__and_New_Techniques.json (type: nrt)
- TRANSCRIPT ONTBREEKT IN QDRANT: 2.Upper_Body_Fundamentals.json (type: nrt)
- TRANSCRIPT ONTBREEKT IN QDRANT: Everything_Reset_Sequence_-_Part_1_part001.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: 1.Upper_Body_Techniques_part000.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC_part000.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Healing_Organs_with_NRT.json (type: nrt)
- TRANSCRIPT ONTBREEKT IN QDRANT: Miraculous_Sequence_-_Part_2_part000.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: 3.Why_People_Hurt.json (type: nrt)
- TRANSCRIPT ONTBREEKT IN QDRANT: How_to_Reset_23_More_Muscles_part000.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Miraculous_Sequence_-_Part_1_part001.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Neurological_Disorganization.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Everything_Reset_Sequence_-_Part_2_part002.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Everything_Reset_Sequence_-_Part_5_part002.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Everything_Reset_Sequence_-_Part_5_part000.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Everything_Reset_Sequence_-_Part_4_part000.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Locating_Acupuncture_Points.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Provocative_Testing.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Emotional_Transformation_Technique.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: How_to_Reset_23_More_Muscles_part001.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: NRT_Fascial_Activation_Application_Method_part000.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Miraculous_Sequence_-_Part_2_part001.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Meridian_Testing_and_Treatment.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: NRT_Fascial_Activation_Application_Method_part001.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: 1.Upper_Body_Techniques_part003.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Green_Square_Applications.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Miraculous_Sequence_-_Part_1_part000.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: 1.Upper_Body_Techniques_part001.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Everything_Reset_Sequence_-_Part_4_part002.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Everything_Reset_Sequence_-_Part_2_part000.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: 1.Lower_Body_Techniques.json (type: nrt)
- TRANSCRIPT ONTBREEKT IN QDRANT: Everything_Reset_Sequence_-_Part_1_part000.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Connection_to_the_Brain.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_2.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Organs_and_Glands_Review.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Everything_Reset_Sequence_-_Part_5_part001.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: 2.Lower_Body_Fundamentals.json (type: nrt)
- TRANSCRIPT ONTBREEKT IN QDRANT: Pair_Balancing.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: NRT_Sports_Specific_or_Universal_Reset_part001.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Everything_Reset_Sequence_-_Part_3_part001.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: NRT_Sports_Specific_or_Universal_Reset_part000.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: NRT_Fascial_Activation_Application_Method_part002.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Neuromuscular_ReEducation.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_3.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Everything_Reset_Sequence_-_Part_2_part001.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Everything_Reset_Sequence_-_Part_1_part002.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: 2021_Demos_Finding_and_Fixing_the_Glitch__Sports_Specific_Reset__and_Advanced_SC_part001.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Anti-Inflammatory_Procedure.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: 1.Upper_Body_Techniques_part002.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Manual_Muscle_Testing_1.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Everything_Reset_Sequence_-_Part_4_part001.json (type: qat)
- TRANSCRIPT ONTBREEKT IN QDRANT: Indicator_Muscle.json (type: qat)
- BOEK ONTBREEKT IN QDRANT: test_acupuncture.pdf (collectie: medical_library)
- BOEK ONTBREEKT IN QDRANT: Orthopedic Physical Assessment_nodrm.epub (collectie: medical_library)
- BOEK ONTBREEKT IN QDRANT: Touch for Health_ The Complete Edition_ A Practical Guide to Natural Health With Acupressure Touch_nodrm.pdf (collectie: medical_library)
- BOEK ONTBREEKT IN QDRANT: Bates Guide to Physical Examination 14e editie - Bickley.epub (collectie: medical_library)

---

## Aanbevelingen

- **Pip-pakketten:** Update selectief met `pip install <pakket> --break-system-packages`. Nooit `pip install --upgrade-all` — kan LlamaIndex/Docling breken.
- **Inconsistenties:** Draai `ingest_books.py` opnieuw voor de genoemde bestanden, of verwijder de vermeldingen uit `data/books_metadata.json`.

---

*Gegenereerd door `scripts/nightly_maintenance.py` op 19-04-2026 00:31:53*