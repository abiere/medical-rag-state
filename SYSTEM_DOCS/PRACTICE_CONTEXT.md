# Practice Context — NRT-Amsterdam.nl

## Practitioner
Axel Biere — complementary therapist, Amsterdam
Website: nrt-amsterdam.nl

## Treatment modalities (always combined, never isolated)

### NRT — Neural Reset Therapy
Neurological muscle reset via specific stimuli to the nervous system.
Resets muscle tension without massage or manipulation.
Targets: trigger points, chronic pain, movement restrictions.

### QAT — Quantum Alignment Technique
Works on meridians + deeper information layers of the body.
Requires VISUALIZATION — treatment protocols must include anatomical images.
Resets meridians and energy balance without needles.
Targets: chronic patterns, stress-related tension, tissue that won't heal.

### GTR — Golgi Tendon Reflex
Therapeutic activation of the natural safety reflex of tendons.
Resets stuck muscle patterns and corrects posture.
Targets: chronic neck/shoulder, post-prosthesis pain, post-partum pelvic issues.

### Tit Tar
Traditional Chinese bone-setting via reflex reset (not forceful manipulation).
Corrects nerve entrapments, misalignments, instability.

### PEMF — Pulsed Electromagnetic Field
Cell-level electromagnetic stimulation.
Settings: 1-10 intensity, various programs.
Targets: inflammation, poor circulation, tissue regeneration.

### RLT — Red Light Therapy
Mitochondrial activation via specific light wavelengths (red + near-infrared).
Targets: collagen, wound healing, pain, immune modulation.

## Treatment protocol structure

### §1 — Klachtbeeld (Condition)
- Definition and description of the condition
- Anatomical cause (which tissues, structures, mechanisms)
- Possible symptoms and manifestations
- Why this condition responds to the practice's approach

### §2 — Behandeling (Treatment)
- QAT tissue treatment: which tissues, in which order
  → WITH anatomical images (essential for visualization)
- NRT muscle resets: which muscles
- GTR if applicable
- Acupuncture points for meridian balancing
  → WITH acupuncture point images
- PEMF settings
- RLT settings

### §3 — Bijlagen / Rationale
- Why these tissues were selected (with page-level citations)
- Why these acupuncture points (with page-level citations)
- Full bibliography

## Image requirements

### Anatomical images (for QAT tissue visualization)
Source: EPUBs in /root/medical-rag/books/
- Sobotta Vol 1, 2, 3 — systematic anatomy
- SobottaClassic — historical anatomy plates with descriptions
- SobottaTables — anatomy tables
- SobottaTextbook
- AnatomyTrains — myofascial lines
- Magee-7e — orthopedic assessment
- Bates — clinical examination

### Acupuncture point images
Source: dedicated acupuncture image set (476 PNG files)
Format: [MERIDIAN][NN].png (e.g., GB-20.png, BL-58.png)

### Image selection UI requirements
1. For each protocol, show candidate images per tissue/structure
2. Axel selects which images to include via web interface
3. Selected images are saved to protocol
4. MEMORY: selected images per tissue are saved as "most likely choice"
   → next time same tissue appears, pre-select the previously chosen image
5. Memory file: /root/medical-rag/data/image_memory.json

## EPUB library (DRM-free)
Located in /root/medical-rag/books/ after upload:
- AnatomyTrains
- Bates
- Magee-7e
- QuantumTouch-2-NewHuman
- QuantumTouch-CoreTransformation
- QuantumTouch-PowerToHeal
- QuantumTouch-Supercharging
- Sobotta-Vol1, Vol2, Vol3
- SobottaClassic
- SobottaTables
- SobottaTextbook
- TouchForHealth
- WholeBrainLiving

## Blog articles (nrt-amsterdam.nl)
Target audience: patients with chronic pain/tension seeking natural treatment
Tone: accessible, not overly clinical
Always grounded in retrieved literature with citations
Topics align with: NRT, QAT, GTR, PEMF, RLT, specific conditions

## Writing rules (NRT-Amsterdam.nl)
- No "we/wij/ons" as subject of NRT-Amsterdam.nl
- Address patients as "je/jij/jouw" (not "u")
- Company name always: NRT-Amsterdam.nl (with hyphen and .nl)
- No mention of "fysiotherapie" or "fysiotherapeut"
- Correct titles for Axel: behandelaar, reset-therapeut, NRT-practitioner, complementair therapeut
- QAT "plaatjes" not mentioned in public content — write at effect level
