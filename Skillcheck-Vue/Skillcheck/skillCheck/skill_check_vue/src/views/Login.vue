<template>
  <div class="login-container">
    <!-- Immagine a sinistra -->
    <div class="image-containerLog">
      <img :src="destra" alt="Login Image" width="810" height="640" />
    </div>
    <!-- Form a destra -->
    <div class="form-containerLog">
      <h1>Login in</h1>
      <router-link to="/"><img :src="scrittaNera" width="200px" class="titoloLogo" /></router-link>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="email">Email</label>
          <input type="text" id="email" v-model="form.email" required />
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input type="password" id="password" v-model="form.password" required /><i
            class="toggle-password fa fa-fw fa-eye-slash"></i>
        </div>
        <div>
          <h6 class="recuperoPassword"><router-link to="/Recupero">hai dimenticato pa password?</router-link></h6>
        </div>
        <div class="checkboxLog">
          <input type="checkbox" id="checkbox" placeholder="ricordati di me " />ricordati di me
        </div>
        <div class="buttons">
          <button type="submit" class="btnLogin-btnLog">Login</button>
        </div>
      </form>
    </div>

    <div v-if="errors.length" class="error-box">
      <p v-for="(e, i) in errors" :key="i">{{ e }}</p>
    </div>

  </div>
</template>

<script>
import api from '@/services/api';

export default {
  data() {
    return {
      form: { email: '', password: '' },
      destra: require('@/assets/parteDestra.png'),
      scrittaNera: require('@/assets/scrittaNera.png'),
      errors: []
    };
  },
  methods: {
    async handleLogin() {
      this.errors = [];
      try {
        localStorage.removeItem('auth_token');
        const { data } = await api.post('/login/', {
          email: (this.form.email || '').trim().toLowerCase(),
          password: (this.form.password || '').trim(),
        });

        localStorage.setItem('auth_token', data.token);
        api.defaults.headers.common.Authorization = `Token ${data.token}`;

        const next = this.$route.query.next || '/dashboard';
        this.$router.replace(next);
      } catch (error) {
        const status = error.response?.status;
        this.errors.push(status === 400 || status === 401
          ? 'Credenziali non valide.'
          : 'Errore di rete. Riprova.');
      }
    },
    handleCancel() {
      this.$router.push('/');
    },
  },
};
</script>

<style>
.login-container {
  text-align: center;
  display: flex;
  justify-content: center;
}

.form-containerLog {
  margin-left: 5%;
  margin-top: 5%;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 40px;
  max-width: 400px;
}

.form-containerLog h1 {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}

/* Stile dei campi del form */
.form-group {
  margin-bottom: 15px;
}

.form-group label text {
  text-align: left;
  display: block;
  font-size: 1rem;
  margin-bottom: 5px;
  color: #555;
}

.form-group input {
  width: 100%;
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #ad2525;
  border-radius: 5px;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
}

.recuperoPassword {
  text-align: right;
}

.btnLogin-btnLog {
  background-color: rgb(43, 42, 42);
  color: white;
  font-size: 15px;
  padding: 12px 50px;
  border-radius: 10px;
}

.checkboxLog {
  text-align: left;

}

.toggle-password {
  float: right;
  cursor: pointer;
  margin-right: 10px;
  margin-top: -25px;
}

.error-box {
  margin-top: .75rem;
  padding: .5rem .75rem;
  border: 1px solid #f2b8b5;
  background: #fdecea;
  color: #b3261e;
  border-radius: .5rem;
}
</style>
