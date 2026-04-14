# Maintenance Report — Medical RAG

**Datum:** 14-04-2026 19:05:03  
**Duur:** 15.6s  
**Uitslag:** ⚠️ WARNING  

---

## Samenvatting

| Fase | Status | Duur | Bevinding |
|---|---|---|---|
| Pre-checks | ✅ OK | 0.2s | Schijf: 291.1 GB vrij, 6% gebruikt |
| Qdrant maintenance | ✅ OK | 0.0s | Geen collecties aangemaakt — niets te onderhouden |
| Data consistentie | ✅ OK | 0.0s | 0 boeken in metadata, 0 ingested |
| Software check | ⚠️ WARNING | 15.4s | 55 pip-pakket(ten) verouderd: |
| Opruimen | ✅ OK | 0.0s | /tmp: geen verouderde bestanden |

**Schijf voor:** 291.1 GB vrij  
**Schijf na:** 291.1 GB vrij  
**Vrijgemaakt:** —  

---

## ✅ Pre-checks

- Schijf: 291.1 GB vrij, 6% gebruikt
- RAM: 31.4 GB beschikbaar, 4% gebruikt
- Qdrant: ✓ online
- Ollama: ✓ online (llama3.1:8b)
- Docker: 2 container(s) actief
  • qdrant: Up 8 hours (healthy)
  • ollama: Up 8 hours (healthy)

## ✅ Qdrant maintenance

- Geen collecties aangemaakt — niets te onderhouden

## ✅ Data consistentie

- 0 boeken in metadata, 0 ingested
- 0 afbeeldingen gecontroleerd — geen wees-bestanden
- Consistentie: geen problemen gevonden

## ⚠️ Software check

- 55 pip-pakket(ten) verouderd:
  • attrs  23.2.0 → 26.1.0
  • Automat  22.10.0 → 25.4.16
  • Babel  2.10.3 → 2.18.0
  • bcrypt  3.2.2 → 5.0.0
  • blinker  1.7.0 → 1.9.0
  • boto3  1.34.46 → 1.42.89
  • botocore  1.34.46 → 1.42.89
  • certifi  2023.11.17 → 2026.2.25
  • chardet  5.2.0 → 7.4.3
  • click  8.1.6 → 8.3.2
  • configobj  5.0.8 → 5.0.9
  • cryptography  41.0.7 → 46.0.7
  • dbus-python  1.3.2 → 1.4.0
  • docker  5.0.3 → 7.1.0
  • httplib2  0.20.4 → 0.31.2
  • idna  3.6 → 3.11
  • incremental  22.10.0 → 24.11.0
  • Jinja2  3.1.2 → 3.1.6
  • jmespath  1.0.1 → 1.1.0
  • jsonpatch  1.32 → 1.33
  • jsonpointer  2.0 → 3.1.1
  • jsonschema  4.10.3 → 4.26.0
  • launchpadlib  1.11.0 → 2.1.0
  • lazr.uri  1.0.6 → 1.0.7
  • markdown-it-py  3.0.0 → 4.0.0
  • MarkupSafe  2.1.5 → 3.0.3
  • oauthlib  3.2.2 → 3.3.1
  • packaging  24.0 → 26.0
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
  • requests  2.31.0 → 2.33.1
  • rich  13.7.1 → 15.0.0
  • s3transfer  0.10.1 → 0.16.0
  • service-identity  24.1.0 → 24.2.0
  • setuptools  68.1.2 → 82.0.1
  • six  1.16.0 → 1.17.0
  • ssh-import-id  5.11 → 5.13
  • texttable  1.6.7 → 1.7.0
  • Twisted  24.3.0 → 25.5.0
  • urllib3  2.0.7 → 2.6.3
  • wadllib  1.3.6 → 2.0.0
  • websocket-client  1.7.0 → 1.9.0
  • wheel  0.42.0 → 0.46.3
  • zope.interface  6.1 → 8.3
- Docker images:
  • ollama/ollama:latest	18 hours ago	9.89GB
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

*Gegenereerd door `scripts/nightly_maintenance.py` op 14-04-2026 19:05:03*