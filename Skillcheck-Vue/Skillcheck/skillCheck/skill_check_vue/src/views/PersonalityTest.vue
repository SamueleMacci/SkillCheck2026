<template>
  <div class="pt-container">
    <template v-if="completed">
      <div class="card">
        <h1>Grazie!</h1>
        <p>{{ completionMessage }}</p>
        <p>Le tue risposte sono state salvate correttamente.</p>
        <p><router-link to="/JobDescriptions">Torna alla lista delle offerte</router-link></p>
      </div>
    </template>

    <template v-else>
      <h1>Test della personalità</h1>
      <p>Rispondi a tutte le domande.</p>

      <p v-if="loading">Caricamento…</p>
      <p v-else-if="loadError" class="error">{{ loadError }}</p>

      <form v-else @submit.prevent="submit">
        <div v-if="!domande.length" class="question-block">
          <p>Nessuna domanda di personalità disponibile.</p>
        </div>

        <div v-for="(domanda, i) in domande" :key="domanda.id" class="question-block">
          <p><strong>{{ i + 1 }}.</strong> {{ domanda.testo }}</p>
          <div class="radio-group">
            <label v-for="opt in scale" :key="opt.value">
              <input type="radio" v-model="answers[i]" :name="'domanda_' + i" :value="opt.value" required /> {{ opt.label }}
            </label>
          </div>
        </div>

        <p v-if="submitError" class="error">{{ submitError }}</p>

        <button v-if="domande.length" type="submit" :disabled="sending">
          {{ sending ? 'Invio in corso…' : 'Invia risposte' }}
        </button>
      </form>
    </template>
  </div>
</template>

<script>
import { getPersonalityQuestions, postPersonalityAnswers } from '@/services/application';

export default {
  name: 'PersonalityTest',
  data() {
    return {
      domande: [],
      answers: [],
      loading: true,
      loadError: null,
      sending: false,
      submitError: null,
      completed: false,
      completionMessage: '',
      scale: [
        { value: 1, label: 'Del tutto in disaccordo' },
        { value: 2, label: 'In disaccordo' },
        { value: 3, label: 'Leggermente in disaccordo' },
        { value: 4, label: 'Neutro' },
        { value: 5, label: "Leggermente d'accordo" },
        { value: 6, label: "D'accordo" },
        { value: 7, label: 'Del tutto d\'accordo' },
      ],
    };
  },
  computed: {
    resumeId() {
      return this.$route.params.resumeId;
    },
  },
  async mounted() {
    try {
      this.domande = await getPersonalityQuestions(this.resumeId);
      this.answers = this.domande.map(() => null);
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
      this.domande.forEach((_, i) => {
        payload[`domanda_${i + 1}`] = this.answers[i];
      });

      this.sending = true;
      try {
        const res = await postPersonalityAnswers(this.resumeId, payload);
        this.completionMessage = res.message;
        this.completed = true;
      } catch (e) {
        console.error(e);
        this.submitError = 'Invio risposte fallito. Riprova.';
      } finally {
        this.sending = false;
      }
    },
  },
};
</script>

<style scoped>
.pt-container {
  max-width: 700px;
  margin: 32px auto;
  padding: 0 16px;
  font-family: Arial, sans-serif;
}
.question-block {
  margin-bottom: 20px;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
}
.question-block p {
  margin: 0 0 8px;
}
.radio-group label {
  display: block;
  margin-bottom: 8px;
  cursor: pointer;
}
button {
  padding: 10px 18px;
  font-size: 16px;
  background: rgb(43, 42, 42);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}
button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.card {
  padding: 24px;
  border: 1px solid #ddd;
  border-radius: 8px;
  max-width: 700px;
}
.card a {
  color: #0a6efd;
  text-decoration: none;
}
.error {
  color: #b00020;
}
</style>
