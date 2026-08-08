<template>
  <div class="jobdetail-container">
    <header class="jobdetail-header">
      <router-link to="/" class="site-title">SkillCheck</router-link>
    </header>

    <main class="jobdetail-main">
      <p v-if="loading">Caricamento…</p>
      <p v-else-if="error" class="error">{{ error }}</p>

      <template v-else-if="job">
        <router-link to="/JobDescriptions" class="back-link">&larr; Torna agli annunci</router-link>
        <h1>{{ job.name }}</h1>
        <p v-if="job.deadline" class="deadline">Scadenza candidatura: {{ job.deadline }}</p>
        <p class="job-description">{{ job.content }}</p>
        <router-link :to="`/JobDescriptions/${job.code}/apply`" class="apply-btn">Candidati</router-link>
      </template>
    </main>
  </div>
</template>

<script>
import { getJob } from '@/services/jobs';

export default {
  name: 'JobDescriptionDetail',
  data() {
    return {
      job: null,
      loading: true,
      error: null,
    };
  },
  async mounted() {
    try {
      this.job = await getJob(this.$route.params.code);
    } catch (e) {
      console.error(e);
      this.error = 'Annuncio non trovato.';
    } finally {
      this.loading = false;
    }
  },
};
</script>

<style scoped>
.jobdetail-header {
  background-color: rgb(43, 42, 42);
  padding: 16px 24px;
}
.site-title {
  color: white;
  font-size: 22px;
  font-weight: bold;
  text-decoration: none;
}
.jobdetail-main {
  max-width: 800px;
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
.deadline {
  color: #666;
  font-size: 14px;
}
.job-description {
  white-space: pre-line;
  line-height: 1.5;
  margin: 16px 0 24px;
}
.apply-btn {
  display: inline-block;
  background: rgb(43, 42, 42);
  color: white;
  padding: 10px 26px;
  border-radius: 8px;
  text-decoration: none;
  font-size: 15px;
}
.error {
  color: #b00020;
}
</style>
