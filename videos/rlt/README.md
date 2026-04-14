# RLT Instruction Videos

Place RLT (Red Light Therapy) device instruction and protocol videos here.

**Supported formats:** MP4, MOV, MKV, M4V, WEBM, AVI

**Transcription:**
```bash
python scripts/transcribe_videos.py --type rlt
python scripts/transcribe_videos.py --type rlt --ingest   # also ingest into Qdrant
```

**Content type:** `device_rlt`
**Qdrant collection:** `device_protocols`

Like PEMF, RLT document content will have structured settings extracted
(wavelength, duration, body region, indication, contraindication).

PDF device manuals:
```bash
python scripts/ingest_books.py --books-dir ./books \
  --content-type device_rlt --collection device_protocols
```
