<template>
  <div class="emp-container">
    <router-link to="/SkillPath" class="back-link">&larr; Torna a SkillPath</router-link>
    <h1>Dipendenti</h1>
    <p class="hint">Elenco interno usato per nominare candidati sugli annunci privati.</p>

    <form class="add-form" @submit.prevent="addEmployee">
      <input v-model="form.nome" type="text" placeholder="Nome e cognome" required />
      <input v-model="form.email" type="email" placeholder="Email" required />
      <input v-model="form.reparto" type="text" placeholder="Reparto (opzionale)" />
      <label class="cv-label">
        CV (opzionale):
        <input type="file" accept=".pdf" @change="onCvChange" />
      </label>
      <button type="submit" :disabled="saving">{{ saving ? 'Aggiungo…' : 'Aggiungi' }}</button>
    </form>
    <p v-if="formError" class="error">{{ formError }}</p>

    <div class="import-box">
      <h3>Importa più dipendenti da CSV</h3>
      <p class="hint">
        CSV con colonne nome, email, reparto (opzionale), cv_path (opzionale, nome del
        file PDF caricato qui sotto). <a href="#" @click.prevent="showImportHelp = !showImportHelp">Come si fa?</a>
      </p>
      <p v-if="showImportHelp" class="hint">
        Esempio: <code>nome,email,reparto,cv_path</code> poi una riga per dipendente, es.
        <code>Mario Rossi,mario.rossi@azienda.it,IT,mario_rossi.pdf</code>. Se una riga ha un
        cv_path, carica anche il relativo PDF qui sotto (stesso nome file).
      </p>
      <div class="import-row">
        <label class="cv-label">
          File CSV:
          <input type="file" accept=".csv" @change="onImportCsvChange" />
        </label>
        <label class="cv-label">
          PDF dei CV (opzionali, anche più di uno):
          <input type="file" accept=".pdf" multiple @change="onImportCvsChange" />
        </label>
        <label class="cv-label">
          <input type="checkbox" v-model="importUpdate" /> Aggiorna chi esiste già
        </label>
        <button :disabled="!importCsvFile || importing" @click="runImport">
          {{ importing ? 'Importo…' : 'Importa' }}
        </button>
      </div>
      <p v-if="importError" class="error">{{ importError }}</p>
      <div v-if="importResult" class="import-result">
        <p>
          {{ importResult.stats.created }} creati, {{ importResult.stats.updated }} aggiornati,
          {{ importResult.stats.skipped }} saltati, {{ importResult.stats.errors }} errori.
        </p>
        <ul v-if="importResult.messages.length">
          <li v-for="(m, idx) in importResult.messages" :key="idx">{{ m }}</li>
        </ul>
      </div>
    </div>

    <p v-if="loading">Caricamento…</p>
    <p v-else-if="loadError" class="error">{{ loadError }}</p>

    <table v-else class="emp-table">
      <thead>
        <tr>
          <th>Nome</th>
          <th>Email</th>
          <th>Reparto</th>
          <th>CV</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="e in employees" :key="e.id">
          <td>{{ e.nome }}</td>
          <td>{{ e.email }}</td>
          <td>{{ e.reparto || '—' }}</td>
          <td>
            <a v-if="e.has_cv" :href="e.cv_url" target="_blank" rel="noopener">Vedi CV</a>
            <span v-else class="hint">Nessun CV</span>
          </td>
          <td><button class="remove-btn" @click="remove(e)">Rimuovi</button></td>
        </tr>
        <tr v-if="!employees.length">
          <td colspan="5">Nessun dipendente inserito.</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import { listEmployees, createEmployee, deleteEmployee, importEmployeesCsv } from '@/services/employees';

export default {
  name: 'Employees',
  data() {
    return {
      employees: [],
      loading: true,
      loadError: null,
      saving: false,
      formError: null,
      form: { nome: '', email: '', reparto: '' },
      cvFile: null,
      showImportHelp: false,
      importCsvFile: null,
      importCvFiles: [],
      importUpdate: false,
      importing: false,
      importResult: null,
      importError: null,
    };
  },
  async mounted() {
    await this.fetchEmployees();
  },
  methods: {
    async fetchEmployees() {
      this.loading = true;
      this.loadError = null;
      try {
        this.employees = await listEmployees();
      } catch (e) {
        console.error(e);
        this.loadError = 'Errore nel caricamento dei dipendenti.';
      } finally {
        this.loading = false;
      }
    },
    onCvChange(e) {
      this.cvFile = e.target.files[0] || null;
    },
    async addEmployee() {
      this.formError = null;
      this.saving = true;
      try {
        await createEmployee({ ...this.form, cvFile: this.cvFile });
        this.form = { nome: '', email: '', reparto: '' };
        this.cvFile = null;
        await this.fetchEmployees();
      } catch (e) {
        console.error(e);
        this.formError = 'Aggiunta dipendente fallita.';
      } finally {
        this.saving = false;
      }
    },
    async remove(employee) {
      if (!confirm(`Rimuovere ${employee.nome} dall'elenco dipendenti?`)) return;
      try {
        await deleteEmployee(employee.id);
        this.employees = this.employees.filter(e => e.id !== employee.id);
      } catch (e) {
        console.error(e);
        alert('Rimozione fallita.');
      }
    },
    onImportCsvChange(e) {
      this.importCsvFile = e.target.files[0] || null;
    },
    onImportCvsChange(e) {
      this.importCvFiles = Array.from(e.target.files || []);
    },
    async runImport() {
      if (!this.importCsvFile) return;
      this.importing = true;
      this.importResult = null;
      this.importError = null;
      try {
        this.importResult = await importEmployeesCsv({
          csvFile: this.importCsvFile,
          cvFiles: this.importCvFiles,
          update: this.importUpdate,
        });
        await this.fetchEmployees();
      } catch (e) {
        console.error(e);
        this.importError = (e.response && e.response.data && e.response.data.detail) || 'Import fallito.';
      } finally {
        this.importing = false;
      }
    },
  },
};
</script>

<style scoped>
.emp-container {
  max-width: 700px;
  margin: 32px auto;
  padding: 0 16px;
}
.back-link {
  display: inline-block;
  margin-bottom: 16px;
  color: #555;
  text-decoration: none;
  font-size: 14px;
}
.hint {
  color: #666;
  font-size: 14px;
  margin-bottom: 20px;
}
.add-form {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}
.add-form input {
  flex: 1;
  min-width: 140px;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #ccc;
}
.cv-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #555;
}
.add-form button {
  background: rgb(43, 42, 42);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 20px;
  cursor: pointer;
}
.add-form button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.emp-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}
.emp-table th, .emp-table td {
  text-align: left;
  padding: 8px;
  border-bottom: 1px solid #eee;
}
.remove-btn {
  background: none;
  border: 1px solid #c00;
  color: #c00;
  border-radius: 6px;
  padding: 4px 10px;
  cursor: pointer;
  font-size: 12px;
}
.error {
  color: #b00020;
}
.import-box {
  margin: 20px 0;
  padding: 16px;
  border-radius: 10px;
  background: #f4f4f4;
}
.import-box h3 {
  margin: 0 0 8px;
  font-size: 16px;
}
.import-box code {
  background: #e6e6e6;
  padding: 1px 4px;
  border-radius: 4px;
}
.import-row {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  align-items: center;
  margin-top: 8px;
}
.import-row .cv-label {
  font-size: 13px;
}
.import-row button {
  background: rgb(43, 42, 42);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 20px;
  cursor: pointer;
}
.import-row button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.import-result {
  margin-top: 12px;
  font-size: 14px;
}
.import-result ul {
  margin: 6px 0 0;
  padding-left: 20px;
  color: #666;
}
</style>
