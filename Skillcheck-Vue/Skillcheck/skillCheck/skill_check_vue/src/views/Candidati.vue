<template>
  <div class="contenutoPaginaCandidati">
    <div class="contenutoAltpPaginaCandidati">
      <div class="contenutoAltoButton">
        <button class="buttonVai" @click="goBack()"><img :src="imgCircleBack" width="60px"
            class="titoloLogoCandidati" /></button>
      </div>
      <div class="contenutoAltoDinamico">
        <h1 class="contenutoPosizioneCandidata">{{ jobCode }}</h1>
        <p class="contenutoPosizioneContenuto">Scadenza Candidatura: {{ scadenzaCandidatura }}</p>
        <div class="container">
          <div class="text-section">
            <p :class="{ 'collapsed': expanded }">{{ text }}</p>
          </div>
          <button class="buttoneMostraDiPiù" @click="toggleText">{{ expanded ? '▲ Riduci' : '▼ Mostra di più'
          }}</button>
        </div>
      </div>
      <div class="contenutoButtonC">
        <button class="contenutoButtonContact">
          <h1 class="dimNumeri">{{ numeriTab[active].numeroC }}</h1>
          <p class="scrittaButton">da contattare</p>
        </button>
        <button class="contenutoButtonContact">
          <h1 class="dimNumeri">{{ numeriTab[active].numeroI }}</h1>
          <p class="scrittaButton">idonei</p>
        </button>
        <button class="contenutoButtonContact">
          <h1 class="dimNumeri">{{ numeriTab[active].numeroa }}</h1>
          <p class="scrittaButton">in attesa</p>
        </button>
        <button class="contenutoButtonContact">
          <h1 class="dimNumeri">{{ numeriTab[active].numeroN }}</h1>
          <p class="scrittaButton">non idonei</p>
        </button>
      </div>
    </div>
    <div class="tableCandidati">
      <div class="parteButton">
        <button class="buttoneScelta" :disabled="busyAction || !rows.some(r => r.selected)"
          @click="bulkUpdateSelected('ok')">
          Assumi
        </button>
        <button class="buttoneScelta" :disabled="busyAction || !rows.some(r => r.selected)"
          @click="bulkUpdateSelected('rejected')">
          Scarta
        </button>
      </div>

      <!-- stati -->
      <div v-if="loading" class="state state--loading">Caricamento…</div>
      <div v-else-if="error" class="state state--error">{{ error }}</div>
      <div v-else-if="rows.length === 0" class="state state--empty">
        Nessun candidato per questo annuncio.
      </div>

      <!-- tabella -->
      <table v-else class="customTable">
        <thead>
          <tr>
            <th>
              <input type="checkbox" id="selectAll" v-model="selectAll" @change="toggleAllRows" />
            </th>
            <th v-for="(header, index) in headers" :key="index">
              {{ header }}
            </th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="(row, rowIndex) in rows" :key="row.id || rowIndex" :class="{ zebra: rowIndex % 2 === 1 }">
            <td>
              <input type="checkbox" :id="'item-' + rowIndex" v-model="row.selected" @change="updateSelectAllState" />
            </td>

            <td>{{ row.name }}</td>

            <td>
              <img :src="row.info" width="40" @click="openModal('info1', row)" class="thumbnail" />
            </td>

            <td>
              <button @click="openModal('info2', row)" class="buttonMediaTab">{{ row.media }}</button>
            </td>

            <!-- CV -->
            <td>
              <select v-model="row.statusCv"
                :style="{ backgroundColor: statusToColor(row.statusCv), color: getTextColor(statusToColor(row.statusCv)) }"
                @change="saveStage(row, 'cv')">
                <option v-for="opt in categories" :key="opt.value" :value="opt.value"
                  :style="{ backgroundColor: statusToColor(opt.value), color: getTextColor(statusToColor(opt.value)) }">
                  {{ opt.label }}
                </option>
              </select>
            </td>

            <!-- HR -->
            <td>
              <select v-model="row.statusHr"
                :style="{ backgroundColor: statusToColor(row.statusHr), color: getTextColor(statusToColor(row.statusHr)) }"
                @change="saveStage(row, 'hr')">
                <option v-for="opt in categories" :key="opt.value" :value="opt.value"
                  :style="{ backgroundColor: statusToColor(opt.value), color: getTextColor(statusToColor(opt.value)) }">
                  {{ opt.label }}
                </option>
              </select>
            </td>

            <!-- Tecnico -->
            <td>
              <select v-model="row.statusTech"
                :style="{ backgroundColor: statusToColor(row.statusTech), color: getTextColor(statusToColor(row.statusTech)) }"
                @change="saveStage(row, 'tech')">
                <option v-for="opt in categories" :key="opt.value" :value="opt.value"
                  :style="{ backgroundColor: statusToColor(opt.value), color: getTextColor(statusToColor(opt.value)) }">
                  {{ opt.label }}
                </option>
              </select>
            </td>

            <td>{{ row.plus }}</td>
            <td>
              <textarea class="inputCommenti" v-model="row.commenti" rows="2"
                placeholder="Aggiungi un commento..." @input="queueSaveComment(row)"
                @blur="saveComment(row)"></textarea>
              <span v-if="row.commentSaving" class="statoCommento">Salvo…</span>
            </td>
            <td>
              <img :src="row.flag" width="30" @click="openModal('info3', row)" />
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Modal Info 1 -->
      <div v-if="showModal && modalType === 'info1'" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
          <button class="close-btn" @click="closeModal">✖</button>
          <h1>Informazioni utente:</h1>
          <h2>{{ selectedRow.name }}</h2>
          <div class="contenutoModal">
            <table class="modalInfoTable">
              <tbody>
                <tr>
                  <td>
                    <h3>Telefono:</h3>
                  </td>
                  <td class="datiTdmodal1">
                    {{ selectedRow.telefono }}
                  </td>
                </tr>
                <tr>
                  <td>
                    <h3>Email:</h3>
                  </td>
                  <td class="datiTdmodal1">
                    {{ selectedRow.email }}
                  </td>
                </tr>
                <tr>
                  <td>
                    <h3>Cv:</h3>
                  </td>
                  <td class="datiTdmodal1">
                    <template v-if="selectedRow.pdf_url">
                      <a :href="selectedRow.pdf_url" target="_blank" rel="noopener">
                        <img :src="selectedRow.cvIcon" width="40px">
                      </a>
                    </template>
                    <template v-else>
                      <img :src="selectedRow.cvIcon" width="40px" title="PDF non disponibile">
                    </template>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Modal Info 2 -->
      <div v-if="showModal && modalType === 'info2'" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
          <button class="close-btn" @click="closeModal">✖</button>
          <h1>Punteggi: {{ selectedRow.name }}</h1>
          <div class="contenutoModalPunteggio">
            <table class="modalPunteggioTable">
              <tbody>
                <tr>
                  <td>
                    <h3>Media Similarità:</h3>
                  </td>
                  <td class="datiTd">{{ fmt(selectedRow.media2) }}</td>
                </tr>
                <tr>
                  <td>
                    <h3>Voto titolo di studio:</h3>
                  </td>
                  <td class="datiTd">{{ fmt(selectedRow.votot) }}</td>
                </tr>
                <tr>
                  <td>
                    <h3>Voto competenze:</h3>
                  </td>
                  <td class="datiTd">{{ fmt(selectedRow.votoc) }}</td>
                </tr>
                <tr>
                  <td>
                    <h3>Voto esperienze:</h3>
                  </td>
                  <td class="datiTd">{{ fmt(selectedRow.votoe) }}</td>
                </tr>
                <tr>
                  <td>
                    <h3>Punteggio domande:</h3>
                  </td>
                  <td class="datiTd">{{ fmt(selectedRow.punteggioD) }}</td>
                </tr>
                <tr>
                  <td>
                    <h3>Risposte:</h3>
                  </td>
                  <td class="datiTd">
                    <template v-if="selectedRow.answers_url">
                      <a :href="selectedRow.answers_url" target="_blank" rel="noopener">
                        <img :src="selectedRow.answersIcon" width="40" alt="Apri risposte" />
                      </a>
                    </template>
                    <template v-else>—</template>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Modal Info 3 -->
      <div v-if="showModal && modalType === 'info3'" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
          <button class="close-btn" @click="closeModal">✖</button>
          <h1>Candidature di :</h1>
          <h2>{{ selectedRow.name }}</h2>
          <div class="contenutoModal">
            <li>{{ selectedRow.candidato }} </li>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { getJob } from '@/services/jobs';
import { listCandidates, updateCandidateStatus, updateCandidateStage, updateCandidateComment } from '@/services/candidates';

export default {
  name: 'Candidati',
  data() {
    return {
      // ---- tab header / top ----
      imgCircleBack: require('@/assets/ArrowLeftIcon.png'),
      scadenzaCandidatura: '10/12/2025',
      active: 0,
      numeriTab: [{ numeroC: '00', numeroI: '00', numeroa: '00', numeroN: '00' }],
      expanded: false,
      text:
        'La figura ricercata dovrà occuparsi della progettazione, sviluppo e manutenzione di applicazioni software in linguaggio C su piattaforma Linux',

      // ---- tabella ----
      headers: [
        'Cognome nome ',
        'Informazioni Utente',
        'Media totale',
        'Riscontro Tecnico su valutazione cv',
        'Riscontro prima call HR (Convocazione colloquio tecnico)',
        'Riscontro colloquio tecnico',
        'Colonna 10',
        'Commenti',
        'Altre candidature',
      ],
      rows: [], // <-- prima erano hard-coded, ora da API
      categories: [
        { label: 'Da contattare', value: 'contact' },
        { label: 'Idoneo', value: 'ok' },
        { label: 'In attesa', value: 'pending' },
        { label: 'Non idoneo', value: 'rejected' },
      ],

      selectAll: false,

      // ---- modali ----
      showModal: false,
      modalType: '',
      selectedRow: null,

      // ---- stato fetch ----
      loading: false,
      error: null,
      busyAction: false,
    };
  },

  computed: {
    rawParam() {
      return this.$route.params.id || '';
    },
    jobCode() {
      try {
        return decodeURIComponent(this.rawParam);
      } catch {
        return this.rawParam;
      }
    },
  },

  async mounted() {
    await Promise.all([this.fetchCandidates(), this.fetchJobHeader()]);
  },

  beforeUnmount() {
    this.flushPendingComments();
  },

  beforeRouteLeave(to, from, next) {
    this.flushPendingComments();
    next();
  },

  watch: {
    '$route.params.id'() {
      this.fetchCandidates();
      this.fetchJobHeader();
    },
    rows: {
      handler() { this.updateSelectAllState(); },
      deep: true
    }
  },

  methods: {
    // -------- UX base --------
    toggleText() { this.expanded = !this.expanded; },
    goBack() {
      const origin = this.$route.query.from === 'skillpath' ? 'SkillPath' : 'dashboard';
      this.$router.push({ name: origin, query: { r: Date.now() } });
    },
    // -------- tabella / selezione --------
    getTextColor(bgColor) {
      return bgColor === 'green' || bgColor === 'rgb(43, 42, 42)' || bgColor === 'red'
        ? 'white'
        : 'black';
    },
    toggleAllRows() {
      this.rows.forEach(r => { r.selected = this.selectAll; });
    },
    updateSelectAllState() {
      this.selectAll = this.rows.length > 0 && this.rows.every(r => r.selected);
    },
    printSelectedRows() {
      const ids = this.rows.filter(r => r.selected).map(r => r.id);
      alert(`ID Righe selezionate: ${ids.join(', ')}`);
    },

    // -------- modali --------
    openModal(type, row) {
      this.modalType = type;
      this.selectedRow = row;
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
      this.modalType = '';
      this.selectedRow = null;
    },
    // -------- API --------
    async fetchCandidates() {
      this.loading = true;
      this.error = null;
      try {
        if (!this.jobCode) { this.rows = []; return; }
        const list = await listCandidates(this.jobCode);
        this.rows = list.map(c => ({
          id: c.id,
          selected: false,
          name: c.full_name || c.name ||
            [c.first_name, c.last_name].filter(Boolean).join(' ') ||
            `Candidato #${c.id ?? ''}`,
          // stati
          status: this.normalizeStatus(c.status || c.state),
          statusCv: this.normalizeStatus(c.status_cv || c.cv_status || c.status),
          statusHr: this.normalizeStatus(c.status_hr || c.hr_status || c.status),
          statusTech: this.normalizeStatus(c.status_tech || c.tech_status || c.status),
          // punteggi
          media: (c.score_avg ?? c.media_totale ?? c.total_score ?? c.media ?? '—'),
          media2: (c.score_similarity_avg ?? c.media_voti_similarita ?? c.media_similarita ?? '—'),
          votot: (c.score_title ?? c.voto_titolo ?? c.voto_titolo_studio ?? '—'),
          votoc: (c.score_skills ?? c.voto_competenze ?? c.voti_competenze ?? '—'),
          votoe: (c.score_experience ?? c.voto_esperienze ?? c.voto_esperienza ?? '—'),
          punteggioD: (c.score_questions ?? c.punteggio_domande ?? '—'),
          // contatti
          telefono: c.phone || c.telefono || '',
          email: c.email || c.mail || '',
          pdf_url: c.pdf_url || null,
          answers_url: c.answers_url || null,
          // icone
          info: require('@/assets/info.png'),
          cvIcon: require('@/assets/cv.png'),
          answersIcon: require('@/assets/cv.png'),
          flag: require('@/assets/flag.png'),
          plus: c.plus ?? '',
          commenti: c.comment || c.commenti || '',
          _lastSavedComment: c.comment || c.commenti || '',
          commentSaving: false,
        }));
        const stats = { C: 0, I: 0, A: 0, N: 0 };
        for (const c of list) {
          const s = String(c.status || c.state || '').toLowerCase();
          if (['da contattare', 'contattare', 'contact'].includes(s)) stats.C++;
          else if (['idoneo', 'idonei', 'ok', 'eligible'].includes(s)) stats.I++;
          else if (['in attesa', 'attesa', 'pending'].includes(s)) stats.A++;
          else if (['non idoneo', 'scartato', 'rejected'].includes(s)) stats.N++;
        }
        this.numeriTab = [{
          numeroC: String(stats.C).padStart(2, '0'),
          numeroI: String(stats.I).padStart(2, '0'),
          numeroa: String(stats.A).padStart(2, '0'),
          numeroN: String(stats.N).padStart(2, '0'),
        }];
      } catch (e) {
        console.error(e);
        this.error = 'Impossibile caricare i candidati.';
      } finally {
        this.loading = false;
      }
    },

    async saveStatus(row) {
      try {
        await api.patch(`/api/candidates/${row.id}/`, { status: row.status });

        const stats = { C: 0, I: 0, A: 0, N: 0 };
        for (const r of this.rows) {
          const s = String(r.status || '').toLowerCase();
          if (['contact', 'contattare'].includes(s)) stats.C++;
          else if (['ok', 'idoneo', 'eligible'].includes(s)) stats.I++;
          else if (['pending', 'attesa'].includes(s)) stats.A++;
          else if (['rejected', 'non idoneo', 'scartato'].includes(s)) stats.N++;
        }
        this.numeriTab = [{
          numeroC: String(stats.C).padStart(2, '0'),
          numeroI: String(stats.I).padStart(2, '0'),
          numeroa: String(stats.A).padStart(2, '0'),
          numeroN: String(stats.N).padStart(2, '0'),
        }];
      } catch (e) {
        console.error(e);
        alert('Salvataggio stato fallito.');
      }
    },

    statusToColor(value) {
      switch (String(value || '').toLowerCase()) {
        case 'ok': return 'green';
        case 'pending': return 'yellow';
        case 'rejected': return 'red';
        case 'contact': return 'rgb(43, 42, 42)';
        default: return 'rgb(43, 42, 42)';
      }
    },
    normalizeStatus(s) {
      s = String(s || '').toLowerCase();
      if (['da contattare', 'contattare', 'contact'].includes(s)) return 'contact';
      if (['idoneo', 'idonei', 'ok', 'eligible'].includes(s)) return 'ok';
      if (['in attesa', 'attesa', 'pending'].includes(s)) return 'pending';
      if (['non idoneo', 'scartato', 'rejected'].includes(s)) return 'rejected';
      return 'pending';
    },

    async fetchJobHeader() {
      if (!this.jobCode) return;
      try {
        const data = await getJob(this.jobCode);
        this.scadenzaCandidatura = data.deadline ?? this.scadenzaCandidatura;
        this.text = data.content ?? this.text;
      } catch (e) {
        console.error('fetchJobHeader error:', e?.response?.data || e);
      }
    },

    async saveStage(row, kind) {
      try {
        const payload = {};
        if (kind === 'cv') payload.status_cv = row.statusCv;
        if (kind === 'hr') payload.status_hr = row.statusHr;
        if (kind === 'tech') payload.status_tech = row.statusTech;
        await updateCandidateStage(row.id, payload);
      } catch (e) {
        console.error(e);
        alert('Salvataggio stato (fase) fallito.');
      }
    },

    async saveComment(row) {
      if (row._lastSavedComment === row.commenti) return;
      row.commentSaving = true;
      try {
        await updateCandidateComment(row.id, row.commenti);
        row._lastSavedComment = row.commenti;
      } catch (e) {
        console.error(e);
        alert('Salvataggio commento fallito.');
      } finally {
        row.commentSaving = false;
      }
    },

    queueSaveComment(row) {
      // salva in automatico poco dopo l'ultima battitura, senza aspettare il blur
      // (utile se l'utente ricarica/naviga via prima di uscire dal campo)
      clearTimeout(this._commentTimers?.[row.id]);
      if (!this._commentTimers) this._commentTimers = {};
      this._commentTimers[row.id] = setTimeout(() => this.saveComment(row), 800);
    },

    flushPendingComments() {
      // forza subito il salvataggio di eventuali commenti non ancora sincronizzati
      // (chiamato quando si lascia la pagina, per non perdere modifiche fatte
      // meno di 800ms prima della navigazione)
      if (this._commentTimers) {
        Object.values(this._commentTimers).forEach(clearTimeout);
        this._commentTimers = {};
      }
      this.rows.forEach(row => {
        if (row._lastSavedComment !== row.commenti) this.saveComment(row);
      });
    },

    async bulkUpdateSelected(newStatus) {
      const chosen = this.rows.filter(r => r.selected);
      if (!chosen.length) {
        alert('Seleziona almeno un candidato.');
        return;
      }
      this.busyAction = true;
      try {
        await Promise.all(chosen.map(r => updateCandidateStatus(r.id, newStatus)));
        this.selectAll = false;
        this.rows = this.rows.map(r => ({ ...r, selected: false }));
        await this.fetchCandidates();
      } catch (e) {
        console.error(e);
        alert('Aggiornamento non riuscito.');
      } finally {
        this.busyAction = false;
      }
    },

    fmt(v) {
      if (v === null || v === undefined || v === '') return '—';
      return (typeof v === 'number') ? v.toFixed(2) : v;
    },
  },
};
</script>

<style scoped>
.contenutoAltoButton {
  margin-top: 2%;
  margin-left: 2%;
}

.buttonVai {
  background: rgb(43, 42, 42);
  border: none;
  border-radius: 50%;
}

.titoloLogoCandidati {
  background: white;
  border-radius: 50%;
}

.contenutoButtonC {
  height: 25%;
  width: 60%;

}

.contenutoButtonContact {
  margin-top: 5%;
  margin-left: 5%;
  height: 140px;
  width: 140px;
  border-radius: 10px;
  border: none;

}

.contenutoAltoDinamico {
  width: 35%;
  height: 200px;
}

.contenutoAltpPaginaCandidati {
  width: 100%;
  height: 20%;
  color: white;
  display: flex;
  margin-bottom: 5%;
}

.contenutoPosizioneCandidata {
  margin-top: 10%;
  margin-left: 10%;
}

.contenutoPosizioneContenuto {
  margin-top: 1%;
  margin-left: 10%;
}

.contenutoPosizioneDescrizione {
  margin-top: 1%;
  margin-left: 10%;
}

.contenutoPaginaCandidati {
  background: rgb(43, 42, 42);
}

.parteButton {
  /*border-style: groove;*/
  width: 30%;
  border-radius: 10px;
}

.buttoneScelta {
  color: white;
  background-color: rgb(43, 42, 42);
  margin-top: 5%;
  margin-bottom: 5%;
  margin-right: 5%;
  border-radius: 10px;
  width: 35%;
  height: 30px;
}

/* Stile per div della tabella*/
.tableCandidati {
  background: white;
  width: 96%;
  margin-left: 2%;
  font-family: Arial, sans-serif;
  text-align: center;
  border-radius: 10px;
}

/* Stile generale della tabella */
.customTable {
  width: 94%;
  margin-left: 3%;
  border-spacing: 0 10px;
  /* Aggiunge spazio tra le righe */
  border-collapse: separate;
  /* Permette di separare le righe per arrotondare */
}

.customTable th,
.customTable td {
  padding: 10px;
  text-align: center;
}

/* Stile per righe zebra */
.customTable tbody tr {
  background-color: #d2d8da;
  transition: background-color 0.3s ease;
  /* Transizione per hover */
}

.customTable tbody tr.zebra {
  background-color: #a4a8b4;
  /* Colore alternato per righe zebra */
}

/* Arrotondamenti per i bordi iniziali */
.customTable tbody tr td:first-child {
  border-top-left-radius: 15px;
  /* Arrotonda l'angolo superiore sinistro */
  border-bottom-left-radius: 15px;
  /* Arrotonda l'angolo inferiore sinistro */
}

/* Arrotondamenti per i bordi iniziali */
.customTable tbody tr td:last-child {
  border-top-right-radius: 15px;
  /* Arrotonda l'angolo superiore destro */
  border-bottom-right-radius: 15px;
  /* Arrotonda l'angolo inferiore destro*/
}

/* Intestazione */
.customTable thead tr {
  background-color: rgb(43, 42, 42);
  color: white;
}

/* Arrotondamenti per i bordi iniziali */
.customTable thead tr th:last-child {
  border-top-right-radius: 15px;
  /* Arrotonda l'angolo superiore destro */
  border-bottom-right-radius: 15px;
  /* Arrotonda l'angolo inferiore destro*/
}

/* Arrotondamenti per i bordi iniziali */
.customTable thead tr th:first-child {
  border-top-left-radius: 15px;
  /* Arrotonda l'angolo superiore destro */
  border-bottom-left-radius: 15px;
  /* Arrotonda l'angolo inferiore destro*/
}

.customTable thead th {
  padding: 10px;
  font-weight: bold;
  text-align: center;
}

/* Hover Effect */
.customTable tbody tr:hover {
  background-color: #d1f2eb;
}

input[type="checkbox"]::before {

  background-color: rgb(43, 42, 42);
}

input[type="checkbox"] {
  appearance: none;
  background-color: #fff;
  margin: 0;
  font: inherit;
  color: currentColor;
  width: 1.15em;
  height: 1.15em;
  border: 0.15em solid currentColor;
  border-radius: 0.15em;
  transform: translateY(-0.075em);
}

input[type="checkbox"] {
  /* ...existing styles */
  display: grid;
  place-content: center;
}

input[type="checkbox"]::before {
  content: "";
  width: 0.65em;
  height: 0.65em;
  transform: scale(0);
  transition: 120ms transform ease-in-out;
  box-shadow: inset 1em 1em var(--form-control-color);
}

input[type="checkbox"]:checked::before {
  transform: scale(1);
}

/* Stile Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: white;
  width: 50%;
  height: 50%;
  border-radius: 10px;
  position: relative;

}

/* Pulsante di chiusura rotondo con X */
.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background-color: rgb(43, 42, 42);
  color: white;
  font-size: 22px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s ease;
}

.full-image {
  max-width: 90%;
  max-height: 80vh;
  border-radius: 8px;
}

.contenutoModal {
  background: rgb(43, 42, 42);
  color: white;
  border-radius: 10px;
  margin: auto;
  width: 60%;
  height: 50%;
  padding: 10px;
  display: flex;
  align-items: center;
  justify-content: center;

}

.datiTdmodal1 {
  width: 200px;
  background: white;
  color: black;
  border-radius: 5px;
}

.contenutoModalPunteggio {
  background: rgb(43, 42, 42);
  color: white;
  border-radius: 10px;
  margin: auto;
  margin-top: 5%;
  width: 60%;
  height: 60%;
  padding: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.datiTd {
  background: white;
  color: black;
  border-radius: 5px;
  padding: 1%;
  border-spacing: 13%;
  width: 100px;
  gap: 10px;

}

.dimNumeri {
  font-size: 70px;
}

.scrittaButton {
  font-size: 20px;
}

.buttonMediaTab {
  background: white;
  width: 100px;
  height: 40px;
  border-radius: 10px;

  border: 2px solid white;
}

.inputCommenti {
  width: 160px;
  min-height: 40px;
  resize: vertical;
  font-family: inherit;
  font-size: 13px;
  padding: 6px;
  border-radius: 6px;
  border: 1px solid #ccc;
}

.statoCommento {
  display: block;
  font-size: 11px;
  opacity: .7;
  margin-top: 2px;
}

.container {
  max-width: 400px;
  margin: auto;
  padding: 20px;
  background: rgb(43, 42, 42);
  border-radius: 8px;
  text-align: left;
  position: relative;
  padding: 20px;
  text-align: left;

}

.text-section p {
  transition: all 0.3s ease-in-out;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  width: 100%;
}

.text-section .collapsed {
  max-height: none;
  white-space: normal;
  overflow: hidden;
  z-index: 10;
}

.buttoneMostraDiPiù {
  width: 40%;
  height: 40px;
  border: 2px solid white;
  background: rgb(43, 42, 42);
  border-radius: 10px;
  color: white;
  margin-top: 5%;
  left: 10%;
}
</style>
