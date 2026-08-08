<template>
  <div class="joblist-container">
    <header class="joblist-header">
      <router-link to="/" class="site-title">SkillCheck</router-link>
    </header>

    <main class="joblist-main">
      <h1>Elenco Offerte Lavoro</h1>

      <p v-if="loading">Caricamento…</p>
      <p v-else-if="error" class="error">{{ error }}</p>

      <ul v-else class="job-list">
        <li v-for="job in jobs" :key="job.code" class="job-item">
          <router-link :to="`/JobDescriptions/${job.code}`" class="job-title">{{ job.name }}</router-link>
          <p class="job-description">{{ truncate(job.content) }}</p>
        </li>
        <li v-if="!jobs.length">Nessuna offerta di lavoro trovata.</li>
      </ul>
    </main>
  </div>
</template>

<script>
import { listJobs } from '@/services/jobs';

export default {
  name: 'JobDescriptions',
  data() {
    return {
      jobs: [],
      loading: true,
      error: null,
    };
  },
  async mounted() {
    try {
      const data = await listJobs();
      this.jobs = (data || []).filter(j => j.is_public !== false);
    } catch (e) {
      console.error(e);
      this.error = 'Errore nel caricamento degli annunci.';
    } finally {
      this.loading = false;
    }
  },
  methods: {
    truncate(text, max = 200) {
      if (!text) return '';
      return text.length > max ? text.slice(0, max) + '…' : text;
    },
  },
};
</script>

<style scoped>
.joblist-header {
  background-color: rgb(43, 42, 42);
  padding: 16px 24px;
}
.site-title {
  color: white;
  font-size: 22px;
  font-weight: bold;
  text-decoration: none;
}
.joblist-main {
  max-width: 800px;
  margin: 32px auto;
  padding: 0 16px;
}
.job-list {
  list-style: none;
  padding: 0;
}
.job-item {
  border-bottom: 1px solid #ddd;
  padding: 20px 0;
}
.job-title {
  font-size: 20px;
  font-weight: bold;
  color: rgb(43, 42, 42);
  text-decoration: none;
}
.job-title:hover {
  text-decoration: underline;
}
.job-description {
  color: #444;
  margin: 8px 0 12px;
  white-space: pre-line;
}
.apply-btn {
  display: inline-block;
  background: rgb(43, 42, 42);
  color: white;
  padding: 8px 20px;
  border-radius: 8px;
  text-decoration: none;
  font-size: 14px;
}
.error {
  color: #b00020;
}
</style>
