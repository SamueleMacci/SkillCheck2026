<template>
  <div class="sq-container">
    <h1>Seleziona {{ maxSelections }} Domande da porre al candidato</h1>

    <p v-if="loading">Caricamento…</p>
    <p v-else-if="loadError" class="error">{{ loadError }}</p>

    <form v-else @submit.prevent="submit">
      <section v-for="cat in categories" :key="cat.key" class="cat-section">
        <h2>{{ cat.label }}</h2>
        <div class="question-container">
          <div v-for="(item, i) in cat.items" :key="i" class="question-row">
            <label>
              <input type="checkbox" v-model="item.checked" @change="onCheck(item)" />
              {{ item.text }}
            </label>
          </div>
        </div>

        <div class="new-question-container">
          <input type="text" v-model="cat.newText" class="new-question-input"
            placeholder="Nuova Domanda..." @keyup.enter.prevent="addQuestion(cat)" />
          <button type="button" class="add-question-btn" @click="addQuestion(cat)">Aggiungi Domanda</button>
        </div>
      </section>

      <p class="counter">Selezionate: {{ totalSelected }} / {{ maxSelections }}</p>
      <p v-if="submitError" class="error">{{ submitError }}</p>

      <button type="submit" class="submit-btn" :disabled="saving">
        {{ saving ? 'Salvo…' : 'Salva' }}
      </button>
    </form>
  </div>
</template>

<script>
import { getSelectQuestions, saveSelectedQuestions } from '@/services/jobs';

export default {
  name: 'SelectQuestions',
  data() {
    return {
      maxSelections: 7,
      categories: [
        { key: 'esperienze', label: 'Esperienze', items: [], newText: '' },
        { key: 'competenze', label: 'Competenze', items: [], newText: '' },
        { key: 'titoli_di_studio', label: 'Titoli di Studio', items: [], newText: '' },
      ],
      loading: true,
      loadError: null,
      saving: false,
      submitError: null,
    };
  },
  computed: {
    jobId() {
      return this.$route.params.id;
    },
    totalSelected() {
      return this.categories.reduce(
        (sum, cat) => sum + cat.items.filter(it => it.checked).length,
        0
      );
    },
  },
  async mounted() {
    try {
      const data = await getSelectQuestions(this.jobId);
      const map = {
        esperienze: data.esperienze_questions || [],
        competenze: data.competenze_questions || [],
        titoli_di_studio: data.titoli_di_studio_questions || [],
      };
      this.categories.forEach(cat => {
        cat.items = map[cat.key].map(text => ({ text, checked: false }));
      });
    } catch (e) {
      console.error(e);
      this.loadError = 'Errore nel caricamento delle domande.';
    } finally {
      this.loading = false;
    }
  },
  methods: {
    onCheck(item) {
      if (item.checked && this.totalSelected > this.maxSelections) {
        item.checked = false;
        alert(`Puoi selezionare al massimo ${this.maxSelections} domande.`);
      }
    },
    addQuestion(cat) {
      const text = cat.newText.trim();
      if (!text) return;
      cat.items.push({ text, checked: false });
      cat.newText = '';
    },
    async submit() {
      this.submitError = null;
      const payload = {};
      this.categories.forEach(cat => {
        payload[`selected_${cat.key}`] = cat.items.filter(it => it.checked).map(it => it.text);
      });

      this.saving = true;
      try {
        const res = await saveSelectedQuestions(this.jobId, payload);
        this.$router.push({ name: res.next || 'dashboard', query: { r: Date.now() } });
      } catch (e) {
        console.error(e);
        this.submitError = 'Salvataggio fallito. Riprova.';
      } finally {
        this.saving = false;
      }
    },
  },
};
</script>

<style scoped>
.sq-container {
  max-width: 800px;
  margin: 32px auto;
  padding: 0 16px;
}
.cat-section {
  margin-bottom: 24px;
}
.question-container {
  margin-bottom: 8px;
}
.question-row {
  padding: 4px 0;
}
.new-question-container {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}
.new-question-input {
  flex: 1;
  padding: 6px 8px;
  border-radius: 6px;
  border: 1px solid #ccc;
}
.add-question-btn {
  background: rgb(43, 42, 42);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 6px 14px;
  cursor: pointer;
}
.counter {
  font-weight: bold;
  margin: 16px 0 8px;
}
.submit-btn {
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
</style>
