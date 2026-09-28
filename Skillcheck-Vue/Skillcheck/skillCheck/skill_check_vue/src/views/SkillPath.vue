<template>
  <div class="vertical-tabs-container">

    <!-- Sidebar con i Tab -->
    <div class="tabs-sidebar">
      <router-link to="/"><img :src="scrittaBianca" width="150px" class="titoloLogoDash" /></router-link>
      <h3 class="skillPathLabel">SkillPath — annunci privati</h3>
      <router-link to="/NuovoAnnuncio">
        <button class="nuovoAnnuncio">Nuovo annuncio</button>
      </router-link>
      <router-link to="/Employees">
        <button class="nuovoAnnuncio">Dipendenti</button>
      </router-link>

      <button class="buttonTab" v-for="(tab, index) in tabs" :key="tab.id || index"
        :class="{ active: activeTab === index }" @click="activeTab = index">
        <div class="contenutoButton">
          <div class="contenutoDestraButon">
            <h2>{{ tab.name }}</h2>
            <p>{{ tab.id }}</p>
            <p>Scadenza Candidatura: {{ tab.scadenza }}</p>
          </div>
          <div class="contenutoSinistraButon">
            <p>{{ tab.content }}</p>
          </div>
        </div>
      </button>
    </div>

    <!-- Contenuto del Tab -->
    <div class="tab-content" v-if="current">
      <button class="buttonVai" @click="goToCandidati(current.id)">
        <img :src="imgCircle" width="60px" class="titoloLogo" />
      </button>

      <div class="contenutoButtonC">
        <button class="contenutoButtonContact">
          <h1 class="dimNumeri">{{ current.numeroC }}</h1>
          <p class="scrittaButton">da contattare</p>
        </button>
        <button class="contenutoButtonContact">
          <h1 class="dimNumeri">{{ current.numeroI }}</h1>
          <p class="scrittaButton">idonei</p>
        </button>
        <button class="contenutoButtonContact">
          <h1 class="dimNumeri">{{ current.numeroa }}</h1>
          <p class="scrittaButton">in attesa</p>
        </button>
        <button class="contenutoButtonContact">
          <h1 class="dimNumeri">{{ current.numeroN }}</h1>
          <p class="scrittaButton">non idonei</p>
        </button>
      </div>

      <div class="contenutoPagina">
        <h1>{{ current.name }}</h1>
        <p class="idContenutoPagina">{{ current.id }}</p><br />
        <h3>Scadenza Candidatura: {{ current.scadenza }}</h3><br />
        <p class="ContenutoLi">{{ current.content }}</p>

        <div class="nominaBox">
          <h3>Nomina candidato</h3>
          <p class="hint">
            Compatibilità calcolata dal confronto CV/annuncio (IA) — dipendenti senza
            CV caricato non hanno una percentuale.
          </p>
          <div class="nominaRow">
            <select v-model="selectedEmployeeId" :disabled="loadingScores">
              <option disabled value="">
                {{ loadingScores ? 'Calcolo compatibilità…' : 'Scegli un dipendente…' }}
              </option>
              <option v-for="e in employeeScores" :key="e.id" :value="e.id">
                {{ e.nome }} — {{ e.compatibility !== null ? e.compatibility + '% compatibilità' : 'nessun CV' }}
              </option>
            </select>
            <button :disabled="!selectedEmployeeId || nominating" @click="nominate">
              {{ nominating ? 'Nomina…' : 'Nomina' }}
            </button>
          </div>
          <p v-if="!loadingScores && !employeeScores.length" class="hint">
            Nessun dipendente in elenco — <router-link to="/Employees">aggiungine uno</router-link>.
          </p>
          <p v-if="nominateMessage" class="success">{{ nominateMessage }}</p>
          <p v-if="nominateError" class="error">{{ nominateError }}</p>
        </div>
      </div>
    </div>

    <!-- loading/errore/vuoto mentre non c'è current -->
    <div class="tab-content" v-else>
      <p v-if="errorJobs" class="error">{{ errorJobs }}</p>
      <p v-else-if="loadingJobs">Caricamento…</p>
      <p v-else>Nessun annuncio privato presente.</p>
    </div>
  </div>

  <div>
    <router-link v-if="isAuth" to="/logout">Logout</router-link>
    <router-link v-else to="/login">Login</router-link>
  </div>
</template>

<script>
import { listJobs } from '@/services/jobs';
import { nominateCandidate, getEmployeeJobScores } from '@/services/employees';
export default {
  name: 'SkillPath',
  data() {
    return {
      activeTab: 0,
      tabs: [],
      loadingJobs: false,
      errorJobs: null,
      scrittaBianca: require('@/assets/scrittaBianca.png'),
      imgCircle: require('@/assets/ArrowRightIcon.png'),
      employeeScores: [],
      loadingScores: false,
      selectedEmployeeId: '',
      nominating: false,
      nominateMessage: null,
      nominateError: null,
    };
  },

  beforeRouteEnter(to, from, next) {
    next(vm => vm.fetchJobs());
  },

  beforeRouteUpdate(to, from, next) {
    this.fetchJobs().finally(() => next());
  },

  computed: {
    isAuth() { return !!localStorage.getItem('auth_token'); },
    current() {
      return this.tabs[this.activeTab] || null;
    },
  },

  watch: {
    // ricalcola la compatibilità quando si cambia annuncio selezionato
    'current.id'() {
      this.selectedEmployeeId = '';
      this.fetchEmployeeScores();
    },
  },

  methods: {
    goToCandidati(jobCode) {
      if (!jobCode) return;
      this.$router.push({
        name: 'Candidati',
        params: { id: encodeURIComponent(jobCode) },
        query: { from: 'skillpath' },
      });
    },

    async fetchJobs() {
      this.loadingJobs = true;
      this.errorJobs = null;
      try {
        const data = await listJobs();
        this.tabs = (data || []).filter(j => j.is_public === false).map(j => ({
          name: j.name,
          id: j.code,
          scadenza: j.deadline,
          content: j.content,
          numeroC: String(j.counts?.contact ?? 0).padStart(2, '0'),
          numeroI: String(j.counts?.ok ?? 0).padStart(2, '0'),
          numeroa: String(j.counts?.pending ?? 0).padStart(2, '0'),
          numeroN: String(j.counts?.rejected ?? 0).padStart(2, '0'),
        }));
        if (this.activeTab >= this.tabs.length) this.activeTab = 0;
      } catch (e) {
        console.error(e);
        this.errorJobs = 'Errore nel caricamento degli annunci.';
      } finally {
        this.loadingJobs = false;
      }
    },

    async fetchEmployeeScores() {
      if (!this.current) { this.employeeScores = []; return; }
      this.loadingScores = true;
      try {
        this.employeeScores = await getEmployeeJobScores(this.current.id);
      } catch (e) {
        console.error(e);
        this.employeeScores = [];
      } finally {
        this.loadingScores = false;
      }
    },

    async nominate() {
      if (!this.selectedEmployeeId || !this.current) return;
      this.nominating = true;
      this.nominateMessage = null;
      this.nominateError = null;
      try {
        await nominateCandidate(this.current.id, this.selectedEmployeeId);
        const nome = this.employeeScores.find(e => e.id === this.selectedEmployeeId)?.nome || '';
        this.nominateMessage = `${nome} nominato/a come candidato/a.`;
        this.selectedEmployeeId = '';
        await this.fetchJobs();
      } catch (e) {
        console.error(e);
        this.nominateError = 'Nomina fallita.';
      } finally {
        this.nominating = false;
      }
    },
  },

  async mounted() {
    await this.fetchJobs();
    await this.fetchEmployeeScores();
  },
};
</script>

<style scoped>
.ContenutoLi {
  font-size: 17px;
}

.contenutoButton {
  display: flex;
  width: 100%;
}

.contenutoDestraButon {
  color: black;
  width: 650px;
}

.contenutoSinistraButon {
  margin-left: 15px;
}

.idContenutoPagina {
  margin-left: auto;
  margin-top: 0;
  text-align: right;
  width: auto;
}

.nominaBox {
  margin-top: 24px;
  padding: 16px;
  border-radius: 10px;
  background: #f4f4f4;
  max-width: 500px;
}
.nominaRow {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}
.nominaRow select {
  flex: 1;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #ccc;
}
.nominaRow button {
  background: rgb(43, 42, 42);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 18px;
  cursor: pointer;
}
.nominaRow button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.hint {
  font-size: 13px;
  color: #666;
  margin-top: 8px;
}
.success {
  color: #1b7a2e;
  margin-top: 8px;
}
.error {
  color: #b00020;
  margin-top: 8px;
}

.skillPathLabel {
  color: white;
  margin-left: 10%;
  margin-top: 10px;
  font-family: Arial, Helvetica, sans-serif;
  font-weight: normal;
  opacity: .85;
}

/* Contenitore principale */
.vertical-tabs-container {
  display: flex;
  border-radius: 5px;
  max-width: 100%;
}

/* Sidebar dei tab */
.tabs-sidebar {
  background-color: rgb(43, 42, 42);
  width: 40%;
  height: auto;
  display: flex;
  flex-direction: column;
}

.buttonTab {
  background: white;
  padding: 20px;
  border: none;
  text-align: left;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
}

.tabs-sidebar button.active {
  background-color: white;
  color: black;
  width: 93%;
}

/* Contenuto del tab */
.tab-content {
  padding: 20px;
  flex: 1;
}

.contenutoPagina {
  width: 80%;
  margin-left: 10%;
  margin-top: 12px;
}

.tab-content h2 {
  margin-top: 0;
  color: #007bff;
}

.buttonTab {
  margin-left: 10%;
  width: 80%;
  margin-top: 20px;
  border-radius: 10px;
  background: white;
}

.nuovoAnnuncio {
  align-items: right;
  background: white;
  width: 150px;
  height: 50px;
  border-radius: 10px;
  margin-left: 62%;
  margin-top: 5%;
}

.titoloLogoDash {
  margin-top: 50px;
  margin-left: 10%;
}

.contenutoButtonC {
  display: grid;
  grid-template-columns: repeat(4, minmax(140px, 1fr));
  gap: 16px;
  margin: 16px 0 32px;
  height: auto;
}

.contenutoButtonContact {
  margin: 0;
  width: 100%;
  min-height: 120px;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid rgba(0,0,0,.06);
  background: #fff;
  box-shadow: 0 2px 12px rgba(0,0,0,.06);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.buttonVai {
  margin-left: 90%;
  border-radius: 100%;
  border: none;
  background: white;
}

.dimNumeri {
  font-size: 56px; line-height: 1; margin: 0 0 6px;
}

.scrittaButton {
  font-size: 16px; margin: 0; opacity: .9;
}
@media (max-width: 1024px) {
  .contenutoButtonC { grid-template-columns: repeat(2, minmax(160px, 1fr)); }
}
@media (max-width: 600px) {
  .contenutoButtonC { grid-template-columns: 1fr; }
}
</style>
