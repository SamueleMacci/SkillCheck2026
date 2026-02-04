<template>
  <div class="register-container">
    <!-- Immagine a sinistra -->
    <div class="image-containeReg">
      <img :src="destra" alt="Register Image" width="750" height="640" />
    </div>

    <!-- Form a destra -->
    <div class="form-containerReg">
      <h1>Crea il tuo account</h1>
      <router-link to="/"><img :src="scrittaNera" width="200px" class="titoloLogo" /></router-link>

      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="nome">Nome</label>
          <input type="text" id="nome" v-model="form.nome" autocomplete="given-name" />
        </div>
        <div class="form-group">
          <label for="cognome">Cognome</label>
          <input type="text" id="cognome" v-model="form.cognome" autocomplete="family-name" />
        </div>
        <div class="form-group">
          <label for="email">Email</label>
          <input type="email" id="email" v-model="form.email" required autocomplete="email" />
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input type="password" id="password" v-model="form.password" required autocomplete="new-password" />
        </div>
        <div class="checkboxLog">
          <input type="checkbox" id="checkbox" />
          sono d'accordo con <router-link to="/Termini-e-condizioni">Termini e condizioni</router-link>
        </div>
        <div class="buttons">
          <button type="submit" class="btnLogin-btnReg">Crea Account</button>
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
      form: { nome: '', cognome: '', email: '', password: '', username: '' },
      destra: require('@/assets/parteDestra.png'),
      scrittaNera: require('@/assets/scrittaNera.png'),
      errors: []
    };
  },
  methods: {
    async handleRegister() {
      this.errors = [];
      try {
        const email = (this.form.email || '').trim().toLowerCase();
        const password = (this.form.password || '').trim();
        const username = (email.split('@')[0] || '')
          .toLowerCase().replace(/[^a-z0-9_]/g, '_').slice(0, 30);

        if (!email || !password || !username) {
          this.errors.push('username, email e password sono obbligatori');
          return;
        }

        await api.post('/register/', { username, email, password });

        const { data } = await api.post('/login/', { email, password });
        localStorage.setItem('auth_token', data.token);
        api.defaults.headers.common.Authorization = `Token ${data.token}`;

        this.$router.replace('/dashboard');
      } catch (error) {
        const msg = error?.response?.data?.detail || 'Registrazione non riuscita.';
        this.errors.push(msg);
      }
    },
  },
};
</script>

<style>
.register-container {
  text-align: center;
  display: flex;
  align-items: left;
}

.form-containerReg {
  margin-top: 5%;
  margin-left: 10%;

}

/* Stile dei campi del form */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
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
  border: 1px solid #ccc;
  border-radius: 5px;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
}

.btnLogin-btnReg {
  background-color: rgb(43, 42, 42);
  color: white;
  font-size: 15px;
  padding: 12px 50px;
  border-radius: 10px;
  margin-top: 10%;
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
