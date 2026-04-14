# NRT Training Videos

Place NRT (Neural Reset Therapy) training videos here.

**Supported formats:** MP4, MOV, MKV, M4V, WEBM, AVI

**Transcription:**
```bash
python scripts/transcribe_videos.py --type nrt
python scripts/transcribe_videos.py --type nrt --ingest   # also ingest into Qdrant
```

**Content type:** `training_nrt`
**Qdrant collection:** `training_materials`

**Naming convention:** Use descriptive filenames that match related PDF manuals.
Example: `NRT_Shoulder_Advanced.mp4` will auto-link to `NRT_Shoulder_Manual.pdf`
if both share enough words.

Transcripts are saved to: `data/transcripts/{video_stem}.json` and `.txt`
