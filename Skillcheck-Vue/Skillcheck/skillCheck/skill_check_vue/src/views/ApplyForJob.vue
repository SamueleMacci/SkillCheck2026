<template>
  <div class="apply-container">
    <router-link :to="`/JobDescriptions/${jobCode}`" class="site-title">SkillCheck</router-link>

    <header>
      <h1>Carica Candidatura</h1>
    </header>

    <main>
      <form @submit.prevent="submit" class="apply-form">
        <label for="id_name">Nome e Cognome:</label><br />
        <input id="id_name" v-model="name" type="text" required /><br />

        <label for="id_email">Email:</label><br />
        <input id="id_email" v-model="email" type="email" required /><br />

        <label for="id_cv">Upload PDF:</label><br />
        <input id="id_cv" type="file" accept=".pdf" required @change="onFileChange" /><br />

        <p v-if="error" class="error">{{ error }}</p>

        <button type="submit" class="submit-btn" :disabled="sending">
          {{ sending ? 'Invio in corso…' : 'Invia Candidatura' }}
        </button>
      </form>
    </main>
  </div>
</template>

<script>
import { applyForJob } from '@/services/application';

export default {
  name: 'ApplyForJob',
  data() {
    return {
      name: '',
      email: '',
      file: null,
      sending: false,
      error: null,
    };
  },
  computed: {
    jobCode() {
      return this.$route.params.code;
    },
  },
  methods: {
    onFileChange(e) {
      this.file = e.target.files[0] || null;
    },
    async submit() {
      if (!this.file) {
        this.error = 'Carica il tuo curriculum in PDF.';
        return;
      }
      this.sending = true;
      this.error = null;
      try {
        const { resume_id, job_description_id } = await applyForJob(this.jobCode, {
          name: this.name,
          email: this.email,
          file: this.file,
        });
        this.$router.push(`/MostraDomande/${resume_id}/${job_description_id}`);
      } catch (e) {
        console.error(e);
        const data = e?.response?.data;
        this.error = data?.errors
          ? Object.values(data.errors).flat().join(' ')
          : 'Invio candidatura fallito. Riprova.';
      } finally {
        this.sending = false;
      }
    },
  },
};
</script>

<style scoped>
.apply-container {
  max-width: 600px;
  margin: 32px auto;
  padding: 0 16px;
}
.site-title {
  display: inline-block;
  margin-bottom: 16px;
  color: rgb(43, 42, 42);
  font-weight: bold;
  font-size: 18px;
  text-decoration: none;
}
.apply-form label {
  font-weight: bold;
  margin-top: 12px;
  display: inline-block;
}
.apply-form input[type='text'],
.apply-form input[type='email'] {
  width: 100%;
  padding: 8px;
  margin: 4px 0 12px;
  border-radius: 6px;
  border: 1px solid #ccc;
  box-sizing: border-box;
}
.apply-form input[type='file'] {
  margin: 4px 0 16px;
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
