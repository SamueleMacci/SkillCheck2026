<template>
  <div class="vertical-tabs-container">

    <!-- Sidebar con i Tab -->
    <div class="tabs-sidebar">
      <img :src="scrittaBianca" width="150px" class="titoloLogoDash" />
      <router-link to="/NuovoAnnuncio">
        <button class="nuovoAnnuncio">Nuovo annuncio</button>
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

        <ul v-if="contentBullets.length">
          <li v-for="(line, i) in contentBullets" :key="'c-' + i" class="ContenutoLi">{{ line }}</li>
        </ul>
        <div v-if="requirementsBullets.length">
          <br />
          <h3>REQUISITI</h3><br />
          <ul>
            <li v-for="(req, i) in requirementsBullets" :key="'r-' + i" class="ContenutoLi">{{ req }}</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- loading/errore mentre non c'è current -->
    <div class="tab-content" v-else>
      <p v-if="errorJobs" class="error">{{ errorJobs }}</p>
      <p v-else>Caricamento…</p>
    </div>
  </div>

  <div>
    <router-link v-if="isAuth" to="/logout">Logout</router-link>
    <router-link v-else to="/login">Login</router-link>
  </div>
</template>

<script>
import { listJobs } from '@/services/jobs';
export default {
  data() {
    return {
      activeTab: 0,
      tabs: [],
      loadingJobs: false,
      errorJobs: null,
      contenutoC: [
        {
          campo1: "Collaborare con la squadra per comprendere i requisiti del progetto e tradurli in soluzioni software efficenti",
          campo2: "Effetuare test, debug e ottimizzazione del codice per garantire prestazioni e stabilita ottimali",
          campo3: "Creare documentazione tecnica dettagliata per il codice sviluppato e i proesi implementati",
          campo4: "Collaborare con altri membri della squadra pe il completamento efficace dei progetti. "
        },
        {
          campo1: "Collaborare con altri membri della squadra pe il completamento efficace dei progetti.",
          campo2: "Creare documentazione tecnica dettagliata per il codice sviluppato",
          campo3: "Scrivere codice qualitativo, ", campo4: "Testare e fare il debug con le librerie open source"
        },
        {
          campo1: "Scrivere codice qualitativo, saper usare i principali framework",
          campo2: "Sviluppare applicazioni mobile frendly ", campo3: "le", campo4: "pu"
        },
        {
          campo1: "Sviluppare soluzioni per il cloud ",
          campo2: "Utilizzare Aws cloud, Google cloud o Azure cloud",
          campo3: "Implementare la sicurezza contro attacchi informatici ",
          campo4: "Impostare  framework di rete "
        },
      ],
      requisiti: [
        {
          campo1: "Esperienza consolidata nello sviluppo di applicazioni ",
          campo2: "Conoscenza del linguaggio di programazione c ",
          campo3: "Conoscenza dei sistemi operativi basato su linux ",
          campo4: "Capacita di problem-solving e debug efficace", campo5: "pu", campo6: "pu"
        },
        {
          campo1: "Colaborare con gli altri membri del team ",
          campo2: "Capacita di fare analisi di un progetto",
          campo3: "Capacita di problem-solving e miglioramento qualitativo ",
          campo4: "Conoscenza dei sistemi informatici", campo5: "pu", campo6: "pu"
        },
        {
          campo1: "Conoscenza del linguaggio di programazione java ",
          campo2: "Conoscenza dei principali framework di sviluppo",
          campo3: "Conoscenza del framework springboot",
          campo4: "Lavorare in team e confrontarsi con i colleghi", campo5: "pu", campo6: "pu"
        },
        {
          campo1: "Conoscenza delle prinipali piattaforme di cloud",
          campo2: "Conoscenza cybersecurity per implementare in modo sicuro il server",
          campo3: "Conoscenza dei sistemi operativi basati su linux",
          campo4: "Saper comunicare in maniera efficare con il resto del team", campo5: "pu", campo6: "pu"
        },
      ],
      scrittaBianca: require('@/assets/scrittaBianca.png'),
      imgCircle: require('@/assets/ArrowRightIcon.png'),
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
    contentBullets() {
      const block = this.contenutoC[this.activeTab];
      return block ? Object.values(block).filter(Boolean) : [];
    },
    requirementsBullets() {
      const block = this.requisiti[this.activeTab];
      return block ? Object.values(block).filter(Boolean) : [];
    },
  },

  methods: {
    goToCandidati(jobCode) {
      if (!jobCode) return;
      this.$router.push({ name: 'Candidati', params: { id: encodeURIComponent(jobCode) } });
    },

    async fetchJobs() {
      this.loadingJobs = true;
      this.errorJobs = null;
      try {
        const data = await listJobs();
        this.tabs = (data || []).map(j => ({
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
  },

  async mounted() {
    await this.fetchJobs();
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
  margin-top: -5%;
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