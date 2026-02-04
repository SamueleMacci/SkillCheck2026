import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import api from './services/api'

const app = createApp(App)
app.use(store)
app.use(router)

// opzionale: accesso come this.$api nei componenti Options API
app.config.globalProperties.$api = api

app.mount('#app')
