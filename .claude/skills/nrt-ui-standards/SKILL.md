---
name: nrt-ui-standards
description: NRT-Amsterdam.nl design tokens, colors, components, writing rules and
  navigation patterns. Auto-invoke before building any HTML page, UI component,
  FastAPI route, or public content for this project.
---

# DESIGN.md — NRT-Amsterdam.nl
> Claude Code skill: lees dit bestand vóór elke UI-taak voor dit project.
> Gebaseerd op nrt-amsterdam.nl (live opgehaald april 2026) + Etalagebenen v1.1 protocol stijl.

---

## 1. Brand Overview

**Bedrijfsnaam:** NRT-Amsterdam.nl (altijd met koppelteken én .nl — nooit "NRT Amsterdam" of "NRT")
**Tagline:** Reset van spieren, zenuwen en meridianen
**Platform:** WordPress publieke site + FastAPI interne RAG-tool (Tailscale only)
**Doelgroep publiek:** Nederlandstalig, warm, toegankelijk — patiënten met pijn- en spanningsklachten
**Doelgroep intern:** Axel (behandelaar/eigenaar) — professioneel, efficiënt, medisch georiënteerd

**Kernkarakter:**
- Warm maar professioneel
- Wetenschappelijk onderbouwd, niet zweverig
- Transparant over wat behandelingen wel en niet zijn
- Natuurlijk, niet-invasief, zelfherstellend

---

## 2. Kleuren

### Primaire kleuren (altijd gebruiken)

| Naam | Hex | Gebruik |
|---|---|---|
| Teal Primary | `#1A6B72` | Headers, nav actief, primary buttons, sectietitels |
| Teal Dark | `#155a60` | Hover states op teal elementen |
| Teal Light | `#e8f4f5` | Achtergrond teal-secties, lichte highlights |
| Wit | `#ffffff` | Paginaachtergrond, kaarten |
| Tekst donker | `#1a1a2e` | Body tekst, H1/H2 |
| Tekst grijs | `#4a5568` | Subtekst, metadata, labels |

### Accent kleuren (contextspecifiek)

| Naam | Hex | Gebruik |
|---|---|---|
| QAT Oranje | `#FCE4D6` | QAT-gerelateerde blokken, acupunctuur secties |
| QAT Oranje border | `#f4a57e` | Border van oranje blokken |
| Protocol Geel | `#FFF2CC` | Highlight cellen in Word-protocollen, waarschuwingen |
| Protocol Geel border | `#f0c040` | Border van gele highlights |
| Succes Groen | `#22c55e` | Ingested status, positieve indicatoren |
| Wacht Oranje | `#f97316` | Processing/wachtrij status |
| Grijs achtergrond | `#f8fafc` | Pagina achtergrond intern, kaart achtergrond |
| Grijs border | `#e2e8f0` | Tabellijnen, kaartborders |

### K/A/I Classificatie kleuren (intern systeem)

| Waarde | Kleur | Hex | Betekenis |
|---|---|---|---|
| 1 (Primair) | Groen | `#16a34a` bg `#dcfce7` | Primaire bron voor dit profiel |
| 2 (Ondersteunend) | Oranje | `#ea580c` bg `#ffedd5` | Ondersteunende bron |
| 3 (Achtergrond) | Grijs | `#6b7280` bg `#f3f4f6` | Achtergrondkennis |

---

## 3. Typografie

### Publieke website (nrt-amsterdam.nl)
- **Lettertype:** Schoon sans-serif (WordPress theme — waarschijnlijk Inter of Lato)
- **H1:** Groot, bold, donker — pagina-titel
- **H2:** Medium, semi-bold, teal `#1A6B72` — sectietitels
- **H3:** Kleiner, bold, donker — subsectie headers
- **Body:** 16-17px, regelafstand ~1.6, kleur `#1a1a2e`
- **Citaten/reviews:** Cursief of licht, ingesprongen, met auteursnaam

### Interne RAG-tool (FastAPI, poort 8000)
- **Lettertype:** System UI stack — `-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- **Nav labels:** 14px, font-weight 500
- **Paginatitels:** 20-24px, font-weight 600
- **Kaart headers:** 16px, font-weight 600, kleur `#1A6B72`
- **Body/metadata:** 14px, kleur `#4a5568`
- **Code/chunks:** `monospace`, 13px, achtergrond `#f8fafc`

---

## 4. Navigatie

### Publieke website
Home | Behandelingen | Klachten | Ervaringen | Over | Blog | Afspraak

### Interne RAG-tool (FastAPI)
Dashboard | Bibliotheek | Importeer | Afbeeldingen | Protocollen | Zoeken | Video's | Terminal

**Nav stijl intern:**
- Donkere nav balk (achtergrond `#1e293b` of teal dark)
- Actieve tab: `background: rgba(255,255,255,0.15)` of `#2563eb`
- Inactieve links: `color: #e0e7ff`, geen underline
- Padding: 6px 14px, border-radius 6px
- Font-size: 14px, font-weight 500
- NAV_ITEMS is de enige source of truth — nooit hardcoded nav in individuele pagina's

---

## 5. Componenten

### Buttons

**Primary (teal):**
```css
background: #1A6B72;
color: #ffffff;
padding: 10px 20px;
border-radius: 8px;
font-weight: 600;
font-size: 14px;
border: none;
cursor: pointer;
/* hover: background: #155a60 */
```

**Secondary (outline):**
```css
background: transparent;
color: #1A6B72;
border: 2px solid #1A6B72;
padding: 8px 18px;
border-radius: 8px;
font-weight: 500;
```

**Destructief (rood — verwijder):**
```css
background: #dc2626;
color: #ffffff;
padding: 6px 14px;
border-radius: 6px;
font-weight: 500;
/* Altijd met confirmation modal — nooit direct uitvoeren */
```

**CTA stijl publieke site:** "Plan direct een afspraak" — teal, prominent, met pijltje of chevron

### Kaarten / Cards

```css
background: #ffffff;
border: 1px solid #e2e8f0;
border-radius: 12px;
padding: 20px 24px;
box-shadow: 0 1px 3px rgba(0,0,0,0.08);
```

**Kaart met teal header accent:**
```css
border-top: 3px solid #1A6B72;
```

**QAT-blok (oranje):**
```css
background: #FCE4D6;
border-left: 4px solid #f4a57e;
border-radius: 8px;
padding: 16px 20px;
```

**Protocol geel blok:**
```css
background: #FFF2CC;
border-left: 4px solid #f0c040;
border-radius: 6px;
padding: 12px 16px;
```

### Status badges

```
✅ Ingested    → groen pill: bg #dcfce7, tekst #16a34a
⏳ Bezig       → oranje pill: bg #ffedd5, tekst #ea580c
🕐 Wachtrij   → geel pill: bg #fef9c3, tekst #ca8a04
⬜ Nog niet    → grijs pill: bg #f3f4f6, tekst #6b7280
```

### K/A/I badges (bibliotheek)

Drie ronde badges per boek: **K** | **A** | **I**
- Waarde 1 → groen (primair)
- Waarde 2 → oranje (ondersteunend)
- Waarde 3 → grijs (achtergrond)

### Tabellen (intern)

```css
table { width: 100%; border-collapse: collapse; }
th { background: #1A6B72; color: white; padding: 10px 14px; text-align: left; font-size: 13px; }
td { padding: 10px 14px; border-bottom: 1px solid #e2e8f0; font-size: 14px; }
tr:hover { background: #f8fafc; }
```

### Word-protocol kolommen (Etalagebenen v1.1 standaard)
Kolombreedte: **1500 | 1900 | 4706 | 2200 DXA**
Header kleur: `#1A6B72` (teal)
QAT-rijen: `#FCE4D6` (oranje)
Highlight-cellen: `#FFF2CC` (geel)

### Confirmation modal (verwijder)

```
Titel: "Verwijder [N] chunks voor [Boektitel]?"
Body: "Dit verwijdert alle [N] vectorchunks uit Qdrant. Dit kan niet ongedaan worden gemaakt."
Buttons: [Annuleer] [Verwijder definitief →]
```

---

## 6. Contentpatronen publieke site

### Paginastructuur
1. **Hero** — H1 + korte intro + dual CTA (primary + secondary)
2. **Sectieblokken** — H2 per sectie, regelmatig afgewisseld met afbeelding
3. **Voordelen lijst** — bulletpoints met vet woord + uitleg
4. **"X is niet"** — contrast-sectie die misconcepties wegneemt
5. **Reviews/citaten** — cursief, naam + platform
6. **FAQ** — accordion Q&A
7. **Sluit-CTA** — "Plan direct een afspraak"

### Schrijfregels (altijd volgen bij contentgeneratie)
1. Geen we/wij/ons/onze als subject
2. Geen fysiotherapie/fysiotherapeut — gebruik: behandelaar, reset-therapeut
3. Aanspreekvorm: je/jij/jouw — nooit u/uw
4. Bedrijfsnaam: altijd **NRT-Amsterdam.nl** (koppelteken + .nl)
5. Uitkomsten: "verbeteren", niet "verdwijnen"
6. Toon: warm, informatief, niet-zweverig, wetenschappelijk onderbouwd

### Behandelaars/methoden (vaste terminologie)
- NRT = Neural Reset Therapy
- QAT = Quantum Alignment Technique
- GTR = Golgi Tendon Reflex
- PEMF = Pulsed Electromagnetic Field
- RLT = Red Light Therapy

### Acupunctuur notatie (Deadman standaard)
HE (niet HT) | KID (niet KI) | LIV (niet LV) | P (niet PC) | SJ (niet TW)

### QAT Balancepunten (definitief april 2026 — niet wijzigen)
CV=SP-21 rechts | GV=SP-21 links | BL=BL-58 | SJ=SJ-5
KID=KID-4 | P=P-6 | GB=GB-37 | ST=ST-40
LI=LI-6 | SI=SI-7 | LU=LU-7 | SP=SP-4 | HE=HE-5 | LIV=LIV-5

---

## 7. Paginastructuur interne tool

### Dashboard
- Systeemstatus cards (services, RAM, CPU, disk)
- Ingest progress (actieve boeken)
- Transcriptie queue status
- Snelkoppelingen naar andere pagina's

### Bibliotheek (/library)
- 6 tabs: Medische Literatuur | Acupunctuur | NRT/Kinesiologie | QAT Curriculum | Apparatuur | Video's
- Per boek: titel, auteur, K/A/I badges, chunk count, status badge, verwijder-knop
- Zoekbalk + sortering

### Importeer (/library/ingest)
- Upload zone voor PDF/EPUB
- Wachtrij overzicht
- Progress per boek

---

## 8. Logo & Afbeeldingen

**Logo SVG:** https://nrt-amsterdam.nl/wp-content/uploads/2025/10/NRT-Amsterdam.nl-Logo-1.svg
**Acupunctuur afbeeldingen:** 476 Deadman PNG's op server — /root/medical-rag/data/acupuncture_images/
**Afbeeldingsstijl publiek:** Warm, professioneel, geen stock-foto clichés

---

## 9. Do's en Don'ts

### ✅ Do
- Gebruik `NAV_ITEMS` als centrale nav definitie — nooit per pagina hardcoderen
- Teal `#1A6B72` voor alle primaire visuele accenten
- Confirmation dialog bij destructieve acties
- Status altijd visueel tonen (badge, kleur, icoon)
- Teruglink (← Terug naar X) op subpagina's

### ❌ Don't
- Nooit "we/wij/ons" als subject in publieke content
- Nooit "fysiotherapeut" of "fysiotherapie"
- Nooit "u/uw" — altijd "je/jij/jouw"
- Nooit directe verwijdering zonder confirmation + chunk count
- Nooit hardcoded nav buiten NAV_ITEMS
- Nooit "NRT Amsterdam" zonder koppelteken en .nl
- Nooit HT/KI/LV/PC/TW als acupunctuurnotatie
