<template>
  <div class="welcome-container">
    <div class="buttons-container">
      <h1 class="benvenuto">Benvenuto su</h1>
      <img :src="scrittaNera" width="400" class="titoloLogo" />
      <p class="contenutoWelcame">
        Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quas nobis
        nesciunt deserunt dolores, maxime aliquid facere quis quo labore odit.
      </p>

      <div class="contenitoreButton">
        <template v-if="isAuth">
          <button class="btnRegister-btn" @click="goToDashboard">Dashboard</button>
          <button class="btnLogin-btn" @click="goLogout">Logout</button>
        </template>
        <template v-else>
          <button class="btnRegister-btn" @click="goToRegister">Registrati</button>
          <button class="btnLogin-btn" @click="goToLogin">Login</button>
        </template>
      </div>

      <div class="separator">oppure</div>

      <div class="candidateBlock">
        <button class="btnCandidate" @click="goCandidate">
          Procedi come candidato
        </button>
        <p class="hint">Non serve registrarsi</p>
      </div>
    </div>
    <div class="imageContainerWelcome">
      <img :src="sinistra" alt="Welcome Image" class="imgSinistra" />
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  data() {
    return {
      sinistra: require('@/assets/parteSinistra.png'),
      scrittaNera: require('@/assets/scrittaNera.png'),
    };
  },
  computed: {
    isAuth() {
      return !!localStorage.getItem('auth_token');
    },
  },
  methods: {
    goToLogin() {
      this.$router.push('/login');
    },
    goToRegister() {
      this.$router.push('/registrati');
    },
    goCandidate() {
      // Vai alla parte "Francesco" senza autenticazione
      window.location.href = '/job_descriptions/';
    },
    goLogout() {
      this.$router.push('/logout');
    },
    goToDashboard() {
      this.$router.push('/dashboard');
    },
  },
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

.welcome-container{
  display:flex;
  align-items:center;
  justify-content:space-between;
  max-width:1200px;
  margin:0 auto; 
  padding:0 16px;
}

.buttons-container{
  width:40%;
  font-family:'Roboto', sans-serif;
  text-align:center;
  display:flex;
  flex-direction:column;
  align-items:center;
}

.imageContainerWelcome{
  width:60%; max-height:640px;
}

.imgSinistra{
  width:100%; height:100%; object-fit:cover;
}

.benvenuto{
  font-size:70px;
  color:#2b2a2a;
  margin:0;
}
.titoloLogo{
  margin-top:12px;
  display:block;
  margin-left:auto;
  margin-right:auto;
}

.contenutoWelcame{
  margin-top:20px;
  line-height:1.5;
}

.contenitoreButton{
  margin-top:40px;
  display:flex;
  gap:12px;
  justify-content:center;
}
.btnRegister-btn{
  background:#fff; color:#000; padding:12px 40px; font-size:15px;
  border-radius:10px; border:none; cursor:pointer;
  box-shadow:0 8px 16px rgba(0,0,0,.2),0 6px 20px rgba(0,0,0,.19);
}
.btnLogin-btn{
  background:#2b2a2a; color:#fff; padding:12px 50px; font-size:15px;
  border-radius:10px; border:none; cursor:pointer;
}

.separator{ margin:14px 0 6px; opacity:.6; font-size:14px; }
.candidateBlock{ margin-top:6px; }
.btnCandidate{
  background:#fff; color:#000; padding:12px 20px; font-size:15px;
  border-radius:10px; border:1px solid #ddd; cursor:pointer;
}
.hint{ font-size:13px; opacity:.7; margin-top:6px; }

@media (min-width: 1200px) {
  .welcome-container{
    max-width: 1400px;
    gap: 3%;
  }

  .imageContainerWelcome{
    width: 58%;
  }

  .buttons-container{
    width: 42%;
  }

  .benvenuto{
    font-size: 96px;
    line-height: 1.05;
  }

  .titoloLogo{
    width: 520px;
  }

  .contenutoWelcame{
    font-size: 18px;
    max-width: 640px;
    margin-left: auto;
    margin-right: auto;
  }

  .contenitoreButton .btnRegister-btn,
  .contenitoreButton .btnLogin-btn{
    padding: 14px 44px;
    font-size: 16px;
  }

  .btnCandidate{
    padding: 14px 26px;
    font-size: 16px;
  }
}

@media (min-width: 1600px) {
  .welcome-container{ max-width: 1500px; }
  .benvenuto{ font-size: 110px; }
  .titoloLogo{ width: 580px; }
  .contenutoWelcame{ font-size: 19px; max-width: 700px; }
}

</style>