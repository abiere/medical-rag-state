# OPERATIONS — Dagelijks Gebruik & Procedures
> Bijgewerkt door Claude Code als procedures of UI wijzigen.
> Trigger: zie CLAUDE.md § Documentatie triggers

---

## Boek toevoegen

1. Ga naar `/library/ingest` → **Choose files** → Uploaden + ingesteren
2. **Max 30MB per upload** — grotere bestanden eerst opsplitsen:
   - ilovepdf.com/split-pdf (paginabereik, max 25MB per deel)
   - Of: `python3 -c "import pypdf; ..."`
3. Voortgang verschijnt automatisch in de widget (10 sec refresh)
4. Wachtrij verwerkt sequentieel — elke fase zichtbaar (parse → audit → embed → qdrant)

**Grote atlas-stijl boeken (EasyOCR faalt):**
Voeg toe aan `config/book_classifications.json`:
```json
"boek_key": { "force_ocr_engine": "google_vision", ... }
```

---

## Video toevoegen

1. Ga naar `/videos` → upload (max 400MB aanbevolen)
2. Queue verwerkt automatisch — ETA zichtbaar op basis van sec/MB model
3. **>400MB:** voeg toe aan `transcription.skip_files` in `config/settings.json`
   of splits het bestand eerst op

---

## Claude API Retroaudit starten

Wanneer chunks audit_status="skipped_ollama_timeout" hebben:

1. Ga naar `/library/ingest` → **Claude Retroaudit widget** → **Nu uitvoeren**
2. Of via settings: `/settings` → Parameters → Claude API toggle aan → Opslaan
3. Alle overgeslagen chunks verwerkt binnen minuten (10 workers parallel)

---

## Instellingen aanpassen

- Ga naar `/settings` → **Parameters tab**
- Nachtrun tijdvenster is in **Amsterdam tijd** (server loopt op UTC — let op offset)
- Na wijziging: **Opslaan** — wijzigingen direct actief

**Let op:** `config/settings.json` is gitignored — nooit handmatig committen.

---

## Server reboot procedure

```bash
# 1. Controleer of queue actief is
curl -s http://localhost:8000/api/library/progress/active

# 2. Wacht tot leeg, of stop bewust
systemctl stop book-ingest-queue transcription-queue

# 3. Reboot
reboot

# 4. Na reboot: status controleren
systemctl status medical-rag-web book-ingest-queue transcription-queue qdrant
```

---

## Handige commando's

```bash
# Inloggen
ssh root@100.66.194.55

# Logs bekijken
journalctl -u book-ingest-queue --no-pager -n 50
journalctl -u transcription-queue --no-pager -n 30
journalctl -u medical-rag-web --no-pager -n 20

# Web herstarten (ALLEEN web — nooit queue tijdens embedding)
systemctl restart medical-rag-web

# Status sync forceren
python3 /root/medical-rag/scripts/sync_status.py

# Qdrant collectie stats
curl -s http://localhost:6333/collections/medical_library | python3 -c \
  "import json,sys; d=json.load(sys.stdin); print(d['result']['points_count'])"

# Boek ingest state bekijken
cat /root/medical-rag/data/ingest_cache/*/state.json | python3 -m json.tool | \
  grep -E '"filename"|"status"'
```

---

## Waarschuwingen

- **NOOIT** `book-ingest-queue` herstarten tijdens embedding — embeddings gaan verloren
- **NOOIT** `settings.json` committen — gitignored, bevat API sleutels
- **NOOIT** `google_vision_key.json` committen — gitignored
- `BAAI/bge-large-en-v1.5` is het enige correcte embedding model — nomic geeft 0 RAG resultaten
- Destructieve UI acties (delete) tonen altijd een confirmation dialog met chunk count

---

## Troubleshooting

| Symptoom | Check | Oplossing |
|---|---|---|
| 0 chunks na OCR | `journalctl -u book-ingest-queue -n 50` | Voeg `force_ocr_engine: "google_vision"` toe aan book_classifications.json |
| Video hangt (>400MB) | Bestandsgrootte | Voeg toe aan `transcription.skip_files` in settings.json |
| Audit overgeslagen | `/library/ingest` retroaudit widget | Run retroaudit via UI of zet Claude API aan |
| GitHub push geblokkeerd | `git log --all -- <bestand>` | Gebruik git filter-branch om secret uit history te verwijderen |
| 0 RAG resultaten | `curl localhost:6333/collections/medical_library` | Controleer embedding model: altijd bge-large-en-v1.5 |
| Queue start niet | `systemctl status book-ingest-queue` | Check journalctl voor Python errors; py_compile op scripts |
| Web niet bereikbaar | `systemctl status medical-rag-web` | `systemctl restart medical-rag-web` |

---

## Claude Code Skills & Hooks (herinnering)

| Type | Naam | Wanneer |
|---|---|---|
| Skill | `nrt-ui-standards` | Lees EERST voor elke UI/HTML/CSS taak |
| Hook PreToolUse | `security_check.sh` | Automatisch bij Write/Edit — scant secrets |
| Hook PostToolUse | `py_syntax_check.sh` | Automatisch bij Write/Edit — compileert .py |
| Hook Stop | `mempalace_save.sh` | Automatisch bij sessie einde — mine SYSTEM_DOCS |
| MCP | `mempalace` | Persistent geheugen — 116+ drawers |
| MCP | `playwright` | Headless UI tests (Chromium) |
