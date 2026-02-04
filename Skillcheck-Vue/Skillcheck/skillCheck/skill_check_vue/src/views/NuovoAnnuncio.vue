<template>
  <form @submit.prevent="RegistraAnnuncio">
    <div class="ContenitoreAnnunci">
      <div class="ContenitoreAnnunciDestra">
        <img :src="scrittaBianca" width="150px" class="titoloLogoDash" />
        <router-link to="/dashboard">
          <button type="button" class="buttonTornaDashboard">Dashboard</button>
        </router-link>
        <div class="JobPositionDiv">
          <br>
          <h2 class="titoloNuovo">Job Position</h2>
          <input type="date" v-model="form.deadline" class="inputAnnuncio" />
          <input type="text" id="JobPosition" class="inputAnnuncio" placeholder="Scrivi qua..."
            v-model="form.JobPosition" required />
        </div>
        <div class="ContrattoDiv">
          <br>
          <h2 class="titoloNuovo">Tipologia di contratto</h2>
          <div class="button-group">
            <button v-for="option in options" :key="option.value" @click.prevent="selectedOption = option.value"
              :class="{ 'selected': selectedOption === option.value }" class="option-button">
              {{ option.label }}
            </button>
          </div>
        </div>
        <div class="ModalitaDiv">
          <br>
          <h2 class="titoloNuovo">Modalita</h2>
          <div class="button-group">
            <button v-for="option in optionsModalita" :key="option.value"
              @click.prevent="selectedModalita = option.value"
              :class="{ 'selected': selectedModalita === option.value }" class="option-buttonModalita">
              {{ option.label }}
            </button>
          </div>
        </div>
        <div class="OrarioDiv">
          <br>
          <h2 class="titoloNuovo">Orario</h2>
          <div class="button-group">
            <button v-for="option in optionsOrario" :key="option.value" @click.prevent="selectedOrario = option.value"
              :class="{ 'selected': selectedOrario === option.value }" class="option-buttonModalita">
              {{ option.label }}
            </button>
          </div>
        </div>
      </div>
      <div class="ContenitoreAnnunciSinistra">
        <button class="salvaAnnuncio" :disabled="saving" :aria-busy="saving">
          {{ saving ? 'Salvo…' : 'Salva annuncio' }}
        </button>
        <p v-if="error" class="form-error" role="alert" aria-live="polite">{{ error }}</p>
        <br>
        <h2 class="titoloNuovo">Job Description </h2>
        <textarea id="JobDescription" placeholder="Scrivi qua..." v-model="form.descrizione"></textarea>
      </div>
    </div>
  </form>
</template>

<script>
import { createJob, getJob } from '@/services/jobs';

export default {
  data() {
    return {
      form: {
        JobPosition: '',
        descrizione: '',
        deadline: '',
      },
      selectedOption: '',
      selectedModalita: '',
      selectedOrario: '',
      options: [
        { label: "Tempo indeterminato", value: "Tempo indeterminato" },
        { label: "Tempo determinato", value: "Tempo determinato" },
        { label: "Part time", value: "Part time" },
        { label: "Full-time", value: "Full-time" },
        { label: "Stage", value: "Stage" },
      ],
      optionsModalita: [
        { label: "In sede", value: "In sede" },
        { label: "Da remoto", value: "Da remoto" },
        { label: "Ibrido", value: "Ibrido" },
      ],
      optionsOrario: [
        { label: "9-18", value: "giorno" },
        { label: "9-13", value: "mattino" },
        { label: "14-18", value: "pomeriggio" },
      ],
      scrittaBianca: require('@/assets/scrittaBianca.png'),
      saving: false,
      error: ''
    };
  },
  methods: {
    async RegistraAnnuncio() {
      this.error = '';
      this.saving = true;

      try {
        if (!this.form.JobPosition) {
          this.error = 'Inserisci la Job Position';
          return;
        }

        // se la descrizione è vuota, sintetizzo i campi extra nel content
        const content =
          this.form.descrizione ||
          `Contratto: ${this.selectedOption || 'n/d'} — Modalità: ${this.selectedModalita || 'n/d'} — Orario: ${this.selectedOrario || 'n/d'}`;

        const payload = {
          name: this.form.JobPosition,
          content,
          deadline: this.form.deadline || null,
        };

        // crea JD
        const created = await createJob(payload);
        const code = created?.code ?? null;

        let jdId = created?.id ?? created?.pk ?? null;
        if (!jdId && code) {
          const full = await getJob(code);
          jdId = full?.id ?? full?.pk ?? null;
        }
        const id = String(jdId || code || '').trim();
        if (id) {
          window.location.replace(`/${encodeURIComponent(id)}/select_questions/`);
          return;
        }
        this.$router.push({ name: 'dashboard' });
      } catch (e) {
        console.error(e);
        this.error = e?.response?.data?.detail || 'Creazione annuncio non riuscita.';
      } finally {
        this.saving = false;
      }
    },

    handleCancel() {
      this.$router.push('/dashboard');
    },
  },
};
</script>

<style>
.ContenitoreAnnunci {
  display: flex;
  align-items: left;
}

.ContenitoreAnnunciDestra {
  background-color: rgb(43, 42, 42);
  width: 40%;
}

.ContenitoreAnnunciSinistra {
  width: 60%;

}

.titoloLogoDash {
  margin-top: 50px;
  margin-left: 10%;
}

.JobPositionDiv {
  margin-top: 5%;
  margin-left: 10%;
  background: white;
  width: 80%;
  height: 150px;
  border-radius: 10px;
}

.ContrattoDiv {
  margin-top: 5%;
  margin-left: 10%;
  background: white;
  width: 80%;
  height: 300px;
  border-radius: 10px;
}

.ModalitaDiv {
  margin-top: 5%;
  margin-left: 10%;
  background: white;
  width: 80%;
  height: 150px;
  border-radius: 10px;
}

.OrarioDiv {
  margin-top: 5%;
  margin-left: 10%;
  background: white;
  width: 80%;
  height: 150px;
  border-radius: 10px;
  margin-bottom: 10%;
}

.titoloNuovo {
  text-align: left;
  margin-left: 5%;
  font-size: 30px;
  font-family: Arial, Helvetica, sans-serif;
}

.inputAnnuncio {
  background: rgb(243, 241, 241);
  margin-top: 5%;
  width: 90%;
  margin-left: 5%;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-sizing: border-box;
  padding: 10px 20px;
}

textarea {
  background: rgb(243, 241, 241);
  width: 80%;
  margin-left: 10%;
  height: 50%;

  padding: 12px;

  border-radius: 4px;
  box-sizing: border-box;
  margin-top: 6px;
  margin-bottom: 16px;
}

.salvaAnnuncio {
  align-items: right;
  background: rgb(43, 42, 42);
  width: 150px;
  height: 50px;
  border-radius: 10px;
  margin-left: 65%;
  margin-top: 5%;
  color: white;
}

.button-group {
  margin-top: 5%;
  display: flex;
  gap: 10px;
  justify-content: left;
  flex-wrap: wrap;
  padding-left: 5%;
}

.option-button {
  width: 45%;
  padding: 10px 13px;
  border: 2px solid white;
  background: gainsboro;
  cursor: pointer;
  border-radius: 5px;
  font-size: 14px;
}

.option-buttonModalita {
  width: 30%;
  padding: 10px 15px;
  border: 2px solid white;
  background: gainsboro;
  cursor: pointer;
  border-radius: 5px;
  font-size: 14px;
}

.option-button:hover {
  background: rgb(43, 42, 42);
  ;
  color: white;
}

.selected {
  background: rgb(43, 42, 42);
  ;
  color: white;
}

.buttonTornaDashboard {
  align-items: right;
  background: white;
  width: 150px;
  height: 50px;
  border-radius: 10px;
  margin-left: 62%;
  margin-top: -5%;
}
</style>