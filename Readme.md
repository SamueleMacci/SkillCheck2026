# SkillCheck2026

Piattaforma HR basata su AI: gestione annunci di lavoro, candidature, confronto CV/annuncio tramite modelli NLP (spaCy, BERT, T5) e test di personalità.

## Struttura del repository

- **`SkillCheck/`** — il progetto che gira davvero. Backend Django (`skillApp`) con API REST + frontend Vue già compilato e servito da Django stesso.
- **`Skillcheck-Vue/`** — sorgente del frontend Vue (`skill_check_vue`), da cui viene generata la build che finisce in `SkillCheck/skillCheck/static/skillcheck/`. Contiene anche una vecchia variante di backend Django, non collegata al progetto in esecuzione.
- **`TRAININGAPP/`** — app separata per l'addestramento dei modelli ML, non necessaria per far girare SkillCheck.

Per usare l'app basta `SkillCheck/`. `Skillcheck-Vue/` serve solo se devi modificare il frontend.

## Prerequisiti

- Python 3.11
- PostgreSQL (con un'istanza in esecuzione su `localhost:5432`)
- Node.js + npm (solo se devi modificare il frontend Vue)

## 1. Setup del backend

```bash
cd SkillCheck/skillCheck
python -m venv venv311
# Windows:
.\venv311\Scripts\activate
# macOS/Linux:
source venv311/bin/activate

pip install -r requirements.txt
```

### Database

Il progetto si aspetta un database PostgreSQL con queste credenziali **hardcoded** in `skillCheck/settings.py` (non ci sono variabili d'ambiente per queste, va creato così com'è oppure va modificato il file):

```
NAME:     data
USER:     postgres
PASSWORD: user
HOST:     localhost
PORT:     5432
```

Crea il database (se non esiste già):

```sql
CREATE DATABASE data;
```

Poi applica le migration:

```bash
python manage.py migrate
```

### Modelli Machine Learning

I pesi dei modelli non sono nel repository (dimensioni troppo grandi per GitHub). Vanno scaricati e posizionati manualmente dentro `SkillCheck/skillCheck/modelli/`:

| Cartella | Contenuto | Link |
|---|---|---|
| `modelli/comparer/model.safetensors` | BERT — confronto CV/annuncio | https://drive.google.com/file/d/1Bn_JuKy0UdRA8h5bNTWVIxOQcHEhC8K9/view?usp=drive_link |
| `modelli/questioner/model.safetensors` | T5 — generazione domande | https://drive.google.com/file/d/1At5JHVMmgrh15vU4-9S1J0bDAXnbVvzU/view?usp=drive_link |
| `modelli/qwen_hr/` | LLM — consigli IA per candidati scartati (~2.9GB) | *(link da recuperare/aggiungere)* |
| `modelli/recognizer/` | spaCy NER — già incluso nel repo, nessun download necessario |  |

**Opzionale**: per una segmentazione delle frasi in italiano migliore, installa anche:
```bash
python -m spacy download it_core_news_sm
```
Se non lo installi, il codice usa automaticamente un fallback più semplice (`spacy.blank("it")`) — l'app funziona comunque.

### Avvio del server

```bash
python manage.py runserver 8000
```

Poi apri `http://localhost:8000/skillcheck/`.

**Nota sulle performance**: al primo avvio (e ad ogni comando `manage.py`, non solo `runserver`) viene caricato in RAM il modello `qwen_hr` (~2.9GB) — su macchine con poca RAM libera questo può richiedere secondi e, se giri un secondo processo `manage.py` in parallelo, causare crash per mancanza di memoria. Per saltare questo caricamento durante lo sviluppo (es. per testare rapidamente senza bisogno dei consigli IA):

```bash
# Windows PowerShell
$env:SKILLCHECK_SKIP_QWEN="1"; python manage.py runserver 8000
# macOS/Linux
SKILLCHECK_SKIP_QWEN=1 python manage.py runserver 8000
```

## 2. Modificare il frontend (opzionale)

Il frontend Vue è già compilato e committato dentro `SkillCheck/skillCheck/static/skillcheck/` — **non serve Node.js solo per far girare l'app**. Serve solo se vuoi modificare l'interfaccia.

```bash
cd Skillcheck-Vue/Skillcheck/skillCheck/skill_check_vue
npm install
npm run build
```

Dopo la build, i file vanno copiati manualmente nel progetto Django in esecuzione (non c'è un passaggio automatico):

```bash
# da skill_check_vue/dist/ verso SkillCheck/skillCheck/
cp dist/js/*.js dist/js/*.js.map ../../../../../SkillCheck/skillCheck/static/skillcheck/js/
cp dist/css/*.css ../../../../../SkillCheck/skillCheck/static/skillcheck/css/
cp dist/index.html ../../../../../SkillCheck/skillCheck/templates/skillcheck/index.html
```

Poi riavvia il server Django e fai un **hard refresh** del browser (Ctrl+Shift+R) — Django tiene in cache il vecchio `index.html` e il browser i vecchi file JS/CSS.

> Il frontend **non va avviato separatamente** con `npm run serve`: le chiamate API sono configurate per un backend sulla stessa origine (`/api/`), e il progetto non ha CORS configurato per supportare un frontend su una porta diversa.

## Problemi noti

- **Credenziali in chiaro nel codice**: password del database ed email SMTP sono hardcoded in `settings.py` e finiscono nel repository. Da spostare in variabili d'ambiente se il repo diventa pubblico o si aggiungono più collaboratori.
- **`requirements.txt` va tenuto aggiornato a mano**: non generato automaticamente, verificare che coincida con l'ambiente funzionante se si aggiungono dipendenze.
