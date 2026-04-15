# Protocol Structure — AI Instructions
> Defines what a good treatment protocol looks like.
> Used to train the AI on what content is relevant for protocol generation.

## Protocol Sections

### 1. Klinisch Perspectief (Clinical Perspective)
- Written for a non-medical specialist
- Explains WHAT the condition is in understandable terms
- Western medical view + TCM view
- NOT too technical — practitioner needs to understand what they are treating
- Sources: medical literature (pathophysiology chapters)

### 2. Oorzaken (Causes)
- Which specific tissues CAUSE the condition
- Format: Gebied (area) | Weefsels en structuren | Rationale
- Important: these tissues can be treated with QAT blue pads
- Sources: pathophysiology, anatomy atlases

### 3. Mogelijke Gevolgen (Possible Consequences)  
- Which tissues are AFFECTED by the condition
- Same format as causes
- Important: these tissues can also be treated with QAT
- Sources: pathophysiology, clinical medicine

### 4. Anatomische Referentie (Anatomical Reference)
- Sobotta figure numbers relevant to this condition
- Used for visualization during QAT treatment
- Example: "Fig. 4.155 A. iliaca communis en A. femoralis"

### 5. TCM Perspectief
- TCM pattern diagnosis (e.g. Blood Stasis, Cold Bi-obstruction)
- Sources: Deadman, Cecil-Sterman, TCM textbooks

### 6. QAT Behandeling
- Which QAT techniques to apply
- Blue pad placement areas (tissue-based)
- Red pad for inflammation
- Green pad for meridians/nerves
- Sources: QAT curriculum (separate collection)

### 7. Acupunctuur Basisprotocol
- Primary acupuncture points with:
  * Point code (ST-36)
  * Point name (Zusanli)  
  * Meridian
  * Indication/rationale (from Deadman)
  * Image from Deadman
- Sources: Deadman (primary), Cecil-Sterman

### 8. Aanvullende Protocollen (Additional Protocols)
- Condition-specific additions
- Same format as basis protocol

### 9. QAT Meridiaan Balancering
- Balance points per meridian
- Sources: QAT curriculum

### 10. Literatuurreferentie
- Full citations with page numbers
- Format: Bron | Pagina | Rationale

## Training Example
The Etalagebenen (Claudicatio Intermittens) protocol is a GOLD STANDARD example.
When tagging chunks, assess: would this chunk contribute to any of the 
sections above? If yes, tag accordingly with high protocol_relevance score.

## Image Selection Rules
- For QAT visualization: use anatomical images (Sobotta) showing the 
  tissue being treated
- For acupuncture: use point location images from Deadman
- Schematic body diagrams may be generated for pad placement visualization
- Image selection is ALWAYS confirmed by the practitioner — AI pre-selects,
  human approves
