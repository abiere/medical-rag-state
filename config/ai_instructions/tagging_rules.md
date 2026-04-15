# Tagging Rules — AI Instructions
> Rules for how the AI should tag chunks from medical literature.
> These rules are learned and refined over time.

## Core Principle
Tag chunks based on their usefulness for QAT/NRT treatment protocol 
generation. The question to ask for each chunk:
"Would a QAT/NRT practitioner need this information to treat a patient?"

## Usability Tags

### clinical_perspective
Use when: chunk explains what a condition IS in understandable terms
Keywords: manifestation, symptoms, presentation, clinical features
Protocol section: Klinisch Perspectief
Relevance boost: +0.2 if written accessibly (not too technical)

### tissue_cause
Use when: chunk identifies tissues that CAUSE or DRIVE a condition
Keywords: caused by, results from, pathogenesis, mechanism, dysfunction
Protocol section: Oorzaken
Relevance boost: +0.3 (high value — directly tells practitioner what to treat)

### tissue_consequence  
Use when: chunk identifies tissues AFFECTED by a condition
Keywords: leads to, results in, consequence, complication, secondary
Protocol section: Mogelijke Gevolgen
Relevance boost: +0.2

### anatomy_visualization
Use when: chunk describes tissue location useful for treatment visualization
Keywords: located, runs along, borders, supplies, anatomy of
Protocol section: Anatomische Referentie
Relevance boost: +0.3 if figure reference present

### tcm_diagnosis
Use when: chunk contains TCM pattern, syndrome or diagnostic criteria
Keywords: blood stasis, bi-obstruction, qi stagnation, kidney yang, pattern
Protocol section: TCM Perspectief
Relevance boost: +0.2

### acupuncture_point
Use when: chunk describes acupuncture point location, indication or technique
Keywords: point, cun, located, invigorates, tonifies, dispels, clears
Protocol section: Acupunctuur Protocol
Relevance boost: +0.4 if point code present (ST-36 etc.)

### treatment_protocol
Use when: chunk contains structured treatment approach
Keywords: protocol, treatment, sequence, combination, first, then, follow
Protocol section: Multiple
Relevance boost: +0.2

### device_settings
Use when: chunk contains PEMF, RLT or device settings
Keywords: setting, minutes, frequency, program, PEMF, RLT, FlexBeam
Protocol section: QAT Behandeling
Relevance boost: +0.3

### nrt_relevant
Use when: chunk contains muscle-nerve relationships useful for NRT
Keywords: innervation, motor nerve, reflex, agonist, antagonist, spindle
Protocol section: NRT (separate)
Relevance boost: +0.3

## Protocol Relevance Score
Score 0.0-1.0 based on:
- 0.9-1.0: Directly usable in protocol (e.g. Deadman point indication)
- 0.7-0.8: Highly relevant context (e.g. tissue anatomy with figure)
- 0.5-0.6: Useful background (e.g. physiology explanation)
- 0.3-0.4: Peripheral relevance (e.g. general anatomy)
- 0.0-0.2: Not relevant for protocols

## Learning Notes
> Added automatically by the system when feedback is received.
> Format: "DATE — OBSERVATION — SOURCE"
[learning notes will be appended here automatically]
