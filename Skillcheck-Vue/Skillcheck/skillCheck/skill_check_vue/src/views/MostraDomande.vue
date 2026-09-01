<template>
  <div class="mostra-container">
    <template v-if="completed">
      <div class="card">
        <h1>Grazie!</h1>
        <p>{{ completionMessage }}</p>
      </div>
    </template>

    <template v-else>
    <h1>Domande Selezionate</h1>

    <p v-if="loading">Caricamento…</p>
    <p v-else-if="loadError" class="error">{{ loadError }}</p>

    <form v-else @submit.prevent="submit">
      <template v-if="domandeJobDesc.length">
        <h2 class="section-title">Domande dalla Job Description</h2>
        <div v-for="(domanda, i) in domandeJobDesc" :key="'jd-' + i" class="question-container">
          <p><span class="question-number">{{ i + 1 }}.</span> {{ domanda }}</p>
          <label><input type="radio" v-model="jdAnswers[i]" :name="'jd_' + i" value="si" required /> Sì</label>
          <label><input type="radio" v-model="jdAnswers[i]" :name="'jd_' + i" value="no" required /> No</label>
        </div>
      </template>

      <template v-if="domandeResume.length">
        <h2 class="section-title">Domande Personali dal Resume</h2>
        <div v-for="(domanda, i) in domandeResume" :key="'res-' + i" class="question-container">
          <p><span class="question-number">{{ i + 1 + resumeStart }}.</span> {{ domanda }}</p>
          <label><input type="radio" v-model="resumeAnswers[i]" :name="'res_' + i" value="si" required /> Sì</label>
          <label><input type="radio" v-model="resumeAnswers[i]" :name="'res_' + i" value="no" required /> No</label>
        </div>
      </template>

      <template v-if="gapQuestions.length">
        <h2 class="section-title">Domande sui GAP (AI)</h2>
        <div v-for="(item, i) in gapQuestions" :key="'gap-' + i" class="question-container">
          <p>
            {{ item.question }}
            <span v-if="item.skill" class="skill-hint">({{ item.skill }})</span>
          </p>
          <template v-if="item.type === 'yesno'">
            <label><input type="radio" v-model="gapAnswers[i]" :name="'gap_' + i" value="si" required /> Sì</label>
            <label><input type="radio" v-model="gapAnswers[i]" :name="'gap_' + i" value="no" required /> No</label>
          </template>
          <template v-else>
            <input type="text" v-model="gapAnswers[i]" maxlength="120"
              placeholder="Risposta breve (max 120 caratteri)" />
          </template>
        </div>
      </template>

      <p v-if="submitError" class="error">{{ submitError }}</p>

      <button type="submit" class="submit-btn" :disabled="sending">
        {{ sending ? 'Invio in corso…' : 'Salva' }}
      </button>
    </form>
    </template>
  </div>
</template>

<script>
import { getMostraDomande, postMostraDomande } from '@/services/application';

export default {
  name: 'MostraDomande',
  data() {
    return {
      domandeJobDesc: [],
      domandeResume: [],
      resumeStart: 0,
      gapQuestions: [],
      jdAnswers: [],
      resumeAnswers: [],
      gapAnswers: [],
      loading: true,
      loadError: null,
      sending: false,
      submitError: null,
      completed: false,
      completionMessage: '',
    };
  },
  computed: {
    resumeId() {
      return this.$route.params.resumeId;
    },
    jobCode() {
      return this.$route.params.jobCode;
    },
  },
  async mounted() {
    try {
      const data = await getMostraDomande(this.resumeId, this.jobCode);
      this.domandeJobDesc = data.domande_job_desc || [];
      this.domandeResume = data.domande_resume || [];
      this.resumeStart = data.resume_start || 0;
      this.gapQuestions = data.gap_questions || [];
      this.jdAnswers = this.domandeJobDesc.map(() => null);
      this.resumeAnswers = this.domandeResume.map(() => null);
      this.gapAnswers = this.gapQuestions.map(q => (q.type === 'short' ? '' : null));
    } catch (e) {
      console.error(e);
      this.loadError = 'Errore nel caricamento delle domande.';
    } finally {
      this.loading = false;
    }
  },
  methods: {
    async submit() {
      this.submitError = null;
      const payload = {};

      this.domandeJobDesc.forEach((_, i) => {
        payload[`domanda_job_desc_${i + 1}`] = this.jdAnswers[i];
      });
      this.domandeResume.forEach((_, i) => {
        payload[`domanda_resume_${i + 1}`] = this.resumeAnswers[i];
      });

      // indici separati per tipo (yes/no e short), come si aspetta il backend
      let yi = 0;
      let si = 0;
      this.gapQuestions.forEach((q, i) => {
        if (q.type === 'yesno') {
          payload[`gap_yesno_${yi}`] = this.gapAnswers[i];
          yi++;
        } else {
          payload[`gap_short_${si}`] = this.gapAnswers[i] || '';
          payload[`gap_short_skill_${si}`] = q.skill || '';
          si++;
        }
      });

      this.sending = true;
      try {
        const res = await postMostraDomande(this.resumeId, this.jobCode, payload);
        // il test di personalità non è più raggiunto con un redirect automatico:
        // arriva un link via email al candidato (vedi backend, mostra_domande_api)
        this.completionMessage = res.message ||
          'Grazie! La preghiamo di controllare la sua email per la finalizzazione della sua candidatura.';
        this.completed = true;
      } catch (e) {
        console.error(e);
        this.submitError = 'Salvataggio fallito. Riprova.';
      } finally {
        this.sending = false;
      }
    },
  },
};
</script>

<style scoped>
.mostra-container {
  max-width: 700px;
  margin: 32px auto;
  padding: 0 16px;
}
.section-title {
  margin-top: 28px;
}
.question-container {
  border-bottom: 1px solid #eee;
  padding: 14px 0;
}
.question-number {
  font-weight: bold;
}
.skill-hint {
  color: #888;
  font-size: 13px;
}
.question-container label {
  margin-right: 16px;
}
.question-container input[type='text'] {
  width: 100%;
  padding: 6px;
  margin-top: 6px;
  border-radius: 6px;
  border: 1px solid #ccc;
  box-sizing: border-box;
}
.submit-btn {
  margin-top: 24px;
  background: rgb(43, 42, 42);
  color: white;
  padding: 10px 26px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  cursor: pointer;
}
.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.error {
  color: #b00020;
}
.card {
  padding: 24px;
  border: 1px solid #ddd;
  border-radius: 8px;
  max-width: 700px;
}
</style>
