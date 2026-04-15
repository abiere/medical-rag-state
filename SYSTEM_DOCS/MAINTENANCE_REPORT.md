# Maintenance Report — Medical RAG

**Datum:** 15-04-2026 00:30:31  
**Duur:** 35.3s  
**Uitslag:** ⚠️ WARNING  

---

## Samenvatting

| Fase | Status | Duur | Bevinding |
|---|---|---|---|
| Pre-checks | ✅ OK | 0.2s | Schijf: 270.0 GB vrij, 13% gebruikt |
| Qdrant maintenance | ✅ OK | 0.0s | Geen collecties aangemaakt — niets te onderhouden |
| Data consistentie | ✅ OK | 0.0s | 0 boeken in metadata, 0 ingested |
| Software check | ⚠️ WARNING | 35.2s | 73 pip-pakket(ten) verouderd: |
| Opruimen | ✅ OK | 0.0s | /tmp: geen verouderde bestanden |

**Schijf voor:** 270.0 GB vrij  
**Schijf na:** 270.0 GB vrij  
**Vrijgemaakt:** —  

---

## ✅ Pre-checks

- Schijf: 270.0 GB vrij, 13% gebruikt
- RAM: 31.9 GB beschikbaar, 3% gebruikt
- Qdrant: ✓ online
- Ollama: ✓ online (llama3.1:8b)
- Docker: 2 container(s) actief
  • qdrant: Up 13 hours (healthy)
  • ollama: Up 13 hours (healthy)

## ✅ Qdrant maintenance

- Geen collecties aangemaakt — niets te onderhouden

## ✅ Data consistentie

- 0 boeken in metadata, 0 ingested
- 0 afbeeldingen gecontroleerd — geen wees-bestanden
- Consistentie: geen problemen gevonden

## ⚠️ Software check

- 73 pip-pakket(ten) verouderd:
  • antlr4-python3-runtime  4.9.3 → 4.13.2
  • Automat  22.10.0 → 25.4.16
  • Babel  2.10.3 → 2.18.0
  • bcrypt  3.2.2 → 5.0.0
  • blinker  1.7.0 → 1.9.0
  • boto3  1.34.46 → 1.42.89
  • botocore  1.34.46 → 1.42.89
  • chardet  5.2.0 → 7.4.3
  • click  8.1.6 → 8.3.2
  • configobj  5.0.8 → 5.0.9
  • cryptography  41.0.7 → 46.0.7
  • cuda-pathfinder  1.5.2 → 1.5.3
  • cuda-toolkit  13.0.2 → 13.2.1
  • dbus-python  1.3.2 → 1.4.0
  • docker  5.0.3 → 7.1.0
  • filelock  3.25.2 → 3.28.0
  • httplib2  0.20.4 → 0.31.2
  • idna  3.6 → 3.11
  • incremental  22.10.0 → 24.11.0
  • Jinja2  3.1.2 → 3.1.6
  • jmespath  1.0.1 → 1.1.0
  • jsonpatch  1.32 → 1.33
  • jsonpointer  2.0 → 3.1.1
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
  • packaging  24.0 → 26.1
  • pip  24.0 → 26.0.1
  • pyasn1  0.4.8 → 0.6.3
  • pyasn1-modules  0.2.8 → 0.4.2
  • Pygments  2.17.2 → 2.20.0
  • PyGObject  3.48.2 → 3.56.2
  • PyJWT  2.7.0 → 2.12.1
  • pyOpenSSL  23.2.0 → 26.0.0
  • pyparsing  3.1.1 → 3.3.2
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
  • ollama/ollama:latest	24 hours ago	9.89GB
  • qdrant/qdrant:latest	2 weeks ago	285MB
- Qdrant nieuwste release: v1.17.1 (2026-03-27)
- Ollama nieuwste release: v0.20.7 (2026-04-13)

## ✅ Opruimen

- /tmp: geen verouderde bestanden
- web.log: 8 regels — geen rotatie nodig
- Totaal vrijgemaakt: 0 (niets te verwijderen)

---

## Aanbevelingen

- **Pip-pakketten:** Update selectief met `pip install <pakket> --break-system-packages`. Nooit `pip install --upgrade-all` — kan LlamaIndex/Docling breken.

---

*Gegenereerd door `scripts/nightly_maintenance.py` op 15-04-2026 00:30:31*