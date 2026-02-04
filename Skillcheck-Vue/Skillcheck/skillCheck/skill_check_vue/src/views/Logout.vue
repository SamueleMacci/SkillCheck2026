<template>
  <div style="padding:2rem">Uscita in corso…</div>
</template>

<script>
import api from '@/services/api';

export default {
  name: 'Logout',
  created() {
    api.post('/logout/').finally(() => {
      localStorage.removeItem('auth_token');
      delete api.defaults.headers.common.Authorization;
      this.$router.replace({ name: 'login' });
    });
  }
}
</script>
