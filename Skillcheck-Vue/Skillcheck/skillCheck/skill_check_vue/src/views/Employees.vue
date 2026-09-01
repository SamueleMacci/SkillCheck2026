<template>
  <div class="emp-container">
    <router-link to="/SkillPath" class="back-link">&larr; Torna a SkillPath</router-link>
    <h1>Dipendenti</h1>
    <p class="hint">Elenco interno usato per nominare candidati sugli annunci privati.</p>

    <form class="add-form" @submit.prevent="addEmployee">
      <input v-model="form.nome" type="text" placeholder="Nome e cognome" required />
      <input v-model="form.email" type="email" placeholder="Email" required />
      <input v-model="form.reparto" type="text" placeholder="Reparto (opzionale)" />
      <button type="submit" :disabled="saving">{{ saving ? 'Aggiungo…' : 'Aggiungi' }}</button>
    </form>
    <p v-if="formError" class="error">{{ formError }}</p>

    <p v-if="loading">Caricamento…</p>
    <p v-else-if="loadError" class="error">{{ loadError }}</p>

    <table v-else class="emp-table">
      <thead>
        <tr>
          <th>Nome</th>
          <th>Email</th>
          <th>Reparto</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="e in employees" :key="e.id">
          <td>{{ e.nome }}</td>
          <td>{{ e.email }}</td>
          <td>{{ e.reparto || '—' }}</td>
          <td><button class="remove-btn" @click="remove(e)">Rimuovi</button></td>
        </tr>
        <tr v-if="!employees.length">
          <td colspan="4">Nessun dipendente inserito.</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import { listEmployees, createEmployee, deleteEmployee } from '@/services/employees';

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
    async addEmployee() {
      this.formError = null;
      this.saving = true;
      try {
        await createEmployee(this.form);
        this.form = { nome: '', email: '', reparto: '' };
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
</style>
