# SkillCheck – Frontend (Vue)

Frontend per la gestione di annunci e candidati.

## Requisiti

- Node 16+ (consigliato 18)
- Backend DRF in esecuzione su `http://127.0.0.1:8001` (o altro host)

## Configurazione ambiente

Crea un file **`.env.development.local`** nella root del progetto (stessa cartella di `package.json`) con:

```
VUE_APP_API_BASE=http://127.0.0.1:8001
```

> Se il backend gira altrove, cambia l’URL.  
> In produzione usa un file **`.env.production`** con la stessa chiave.

## Installazione & avvio

```bash
npm install
npm run serve
```

## Build produzione

```bash
npm run build
```

---

## Contratto API (usato dal frontend)

### Annunci

- **GET** `/api/jobs/` → lista annunci, ogni item include:

```json
{
  "code": "#xx024x",
  "name": "Programmatore Software",
  "deadline": "2025-12-10",
  "content": "...",
  "counts": { "contact": 0, "ok": 0, "pending": 0, "rejected": 0 }
}
```

- **GET** `/api/jobs/:code/` → dettaglio singolo annuncio (con `counts`)
- **POST** `/api/jobs/` → crea annuncio

Body esempio:
```json
{ "name": "...", "content": "...", "deadline": "YYYY-MM-DD" }
```

### Candidati

- **GET** `/api/candidates/?job=<code>` → lista candidati per annuncio
- **PATCH** `/api/candidates/:id/` → aggiorna **status globale** (`ok` | `rejected` | `pending` | `contact`)
- **PATCH** `/api/candidates/:id/state/` → aggiorna **stati di fase** (`status_cv` | `status_hr` | `status_tech`)

> I contatori della *dashboard* riflettono lo **status globale** del candidato (normalizzato) calcolato dal backend.

---

## Test rapidi (checklist)

- Crea annuncio → appare in dashboard → freccia → pagina Candidati ok
- Assumi/Scarta 1 candidato → contatori pagina e dashboard coerenti
- Assumi/Scarta **bulk** → contatori coerenti
- Refresh dashboard → contatori coerenti
- Annuncio senza candidati → messaggio “Nessun candidato…”

---

## Note / TODO

- Allineamento “intelligente” dei 3 stati di fase con lo status globale: **TODO** (backlog).
- Se presente, il token di autenticazione è letto da `localStorage.auth_token` ed inviato come:
  ```http
  Authorization: Token <token>
  ```

---

## (Facoltativo) Far leggere ad `api.js` la variabile d’ambiente

Se vuoi evitare l’URL hard‑coded e usare `VUE_APP_API_BASE`, puoi sostituire il contenuto di `src/services/api.js` con:

```js
// src/services/api.js
import axios from 'axios';

const baseURL = process.env.VUE_APP_API_BASE || 'http://127.0.0.1:8001';

const api = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
});

const bootToken = localStorage.getItem('auth_token');
if (bootToken) {
  api.defaults.headers.common.Authorization = `Token ${bootToken}`;
}

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) config.headers.Authorization = `Token ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err?.response?.status === 401) {
      localStorage.removeItem('auth_token');
      delete api.defaults.headers.common.Authorization;
      if (!window.location.pathname.includes('/login')) {
        const next = encodeURIComponent(window.location.pathname + window.location.search);
        window.location.href = `/login?next=${next}`;
      }
    }
    return Promise.reject(err);
  }
);

export default api;
```