# NRT/QAT Bridge — AI Instructions
> This file instructs the local AI how NRT and QAT treatment methods 
> relate to medical literature. Updated by the system and Lead Architect.

## NRT — Neural Reset Therapy

NRT resets the communication between muscles and the brain.
Foundation laws:
- **Pfluger's Law of Symmetry**: stimulation on one side affects the 
  symmetrical muscle on the other side
- **Sherrington's Law of Reciprocal Innervation**: when an agonist 
  contracts, the antagonist relaxes

### What NRT needs from medical literature
- Muscle anatomy: exact location, origin, insertion, function
- Antagonist/agonist relationships per muscle group
- Spinal segments and motor nerve innervation (which nerve controls which muscle)
- Reflex arc anatomy (GTR = Golgi Tendon Reflex, muscle spindle)
- Symmetry patterns across body midline

### Tagging rule for NRT
Tag chunks as NRT-relevant if they contain:
- Muscle anatomy with nerve supply
- Spinal reflex mechanisms
- Motor neuron pathways
- Bilateral/symmetry relationships in musculoskeletal system

---

## QAT — Quantum Alignment Technique

QAT treats all tissue via the quantum field using colored treatment pads.
The practitioner can treat any tissue but needs help understanding:
1. What tissue is involved in a condition
2. Where to place the treatment pads
3. How to visualize what is being treated

### Treatment pads
- 🔵 **Blue pads (4x) + clips (6x)**: Main treatment, placed on tissue areas
- 🔴 **Red pads**: Inflammation treatment
- 🟢 **Green pads**: Acupuncture points, meridians, nerves

### What QAT needs from medical literature
- Clinical perspective on conditions (not too medical — practitioner is not 
  a medical specialist, needs to understand what to treat)
- Tissue identification: which specific tissues are involved in a condition
- Causes: which tissues cause the condition (these can be treated)
- Possible consequences: which tissues are affected (these can also be treated)
- Anatomical images for visualization during treatment
- TCM analysis as additional diagnostic layer
- Acupuncture point locations and indications (from Deadman)

### Tagging rule for QAT
Tag chunks as QAT-relevant if they contain:
- Tissue descriptions with anatomical location
- Pathophysiology explaining which tissue is involved
- Inflammation mechanisms
- Vascular, neural, fascial or muscular tissue descriptions
- Any content that helps identify WHAT to treat and WHERE

---

## The Bridge: How NRT/QAT Use Medical Literature

The medical literature is the scientific foundation that explains WHY 
a treatment works and WHAT is being treated.

Example — Claudicatio Intermittens (Etalagebenen):
- Guyton H21: atherosclerosis mechanism → explains vascular tissue to treat
- Sobotta Fig 4.155: A. femoralis anatomy → visualization for pad placement
- Deadman ST-36: "chronic damp painful obstruction" → acupuncture rationale
- QAT: blue pads on vascular tissue → practitioner knows what to visualize
- NRT: reset muscles compensating for vascular insufficiency

The AI must understand: medical literature is not used for diagnosis 
(that comes from other medical professionals) but for TREATMENT PLANNING 
— identifying which tissues to address and how.
