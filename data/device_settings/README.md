# Device Settings

Manually curated device protocol files for PEMF and RLT.

Place structured settings files here as `.txt` or `.md` for ingestion:

```bash
# Ingest a PEMF settings guide
python scripts/ingest_text.py \
  --file data/device_settings/PEMF_Protocols.md \
  --content-type device_pemf \
  --title "PEMF Protocol Guide" \
  --author "Axel Biere"

# Ingest an RLT settings guide
python scripts/ingest_text.py \
  --file data/device_settings/RLT_Protocols.md \
  --content-type device_rlt \
  --title "RLT Protocol Guide" \
  --author "Axel Biere"
```

The ingestion pipeline will automatically extract structured fields:
- Setting, Program, Intensity, Duration
- Indication, Contraindication, Body region

These structured fields are stored in Qdrant payload and enable
auto-population of §2 (Behandeling) in treatment protocols.
