# PEMF Instruction Videos

Place PEMF (Pulsed Electromagnetic Field) device instruction and protocol videos here.

**Supported formats:** MP4, MOV, MKV, M4V, WEBM, AVI

**Transcription:**
```bash
python scripts/transcribe_videos.py --type pemf
python scripts/transcribe_videos.py --type pemf --ingest  # also ingest into Qdrant
```

**Content type:** `device_pemf`
**Qdrant collection:** `device_protocols`

Transcribed content will have PEMF structured settings automatically extracted:
- Setting, Program, Intensity range, Duration
- Indication, Contraindication, Body region

This allows treatment protocols to auto-suggest:
`PEMF: Setting 3, Intensity 4-6, 20 minuten op lumbale regio`

PDF device manuals can also be ingested directly:
```bash
python scripts/ingest_books.py --books-dir ./books \
  --content-type device_pemf --collection device_protocols
```
