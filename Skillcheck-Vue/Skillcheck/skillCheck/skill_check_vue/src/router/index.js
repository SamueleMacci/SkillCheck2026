import { createRouter, createWebHashHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import Login from '../views/Login.vue';
import NotFound from '../views/NotFound.vue';
import Registrati from '../views/Registrati.vue';
import Dashboard from '../views/dashboard.vue';
import Termini from '../views/Condizioni.vue';
import RecuperoPwd from '../views/RecuperoPwd.vue';
import NuovoAnnuncio from '../views/NuovoAnnuncio.vue';
import Candidati from '../views/Candidati.vue';
import CandidatiNonIdonei from '../views/CandidatiNonIdonei.vue';
import Logout from '../views/Logout.vue';
import JobDescriptions from '../views/JobDescriptions.vue';
import JobDescriptionDetail from '../views/JobDescriptionDetail.vue';
import ApplyForJob from '../views/ApplyForJob.vue';
import MostraDomande from '../views/MostraDomande.vue';
import PersonalityTest from '../views/PersonalityTest.vue';
import SkillPath from '../views/SkillPath.vue';
import SelectQuestions from '../views/SelectQuestions.vue';

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/login', name: 'login', component: Login },
  { path: '/registrati', name: 'registrati', component: Registrati },
  { path: '/logout', name: 'logout', component: Logout },

  { path: '/dashboard', name: 'dashboard', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/SkillPath', name: 'SkillPath', component: SkillPath, meta: { requiresAuth: true } },
  { path: '/Termini-e-condizioni', name: 'Termini-e-condizioni', component: Termini },
  { path: '/Recupero', name: 'Recupero', component: RecuperoPwd },
  { path: '/NuovoAnnuncio', name: 'NuovoAnnuncio', component: NuovoAnnuncio, meta: { requiresAuth: true } },
  { path: '/SelectQuestions/:id', name: 'SelectQuestions', component: SelectQuestions, meta: { requiresAuth: true } },
  { path: '/Candidati/:id', name: 'Candidati', component: Candidati, meta: { requiresAuth: true } },
  { path: '/CandidatiNonIdonei', name: 'CandidatiNonIdonei', component: CandidatiNonIdonei, meta: { requiresAuth: true } },
  { path: '/JobDescriptions', name: 'JobDescriptions', component: JobDescriptions },
  { path: '/JobDescriptions/:code', name: 'JobDescriptionDetail', component: JobDescriptionDetail },
  { path: '/JobDescriptions/:code/apply', name: 'ApplyForJob', component: ApplyForJob },
  { path: '/MostraDomande/:resumeId/:jobCode', name: 'MostraDomande', component: MostraDomande },
  { path: '/PersonalityTest/:resumeId', name: 'PersonalityTest', component: PersonalityTest },

  { path: '/:catchAll(.*)', name: 'NotFound', component: NotFound },
];

const router = createRouter({
  // base pubblico della SPA servita da Django
  history: createWebHashHistory('/skillcheck/'),
  routes,
});

router.beforeEach((to, from, next) => {
  const isAuth = !!localStorage.getItem('auth_token');

  if (to.meta?.requiresAuth && !isAuth) {
    return next({ name: 'login', query: { next: to.fullPath } });
  }
  if ((to.name === 'login' || to.name === 'registrati') && isAuth) {
    return next({ name: 'dashboard' });
  }
  next();
});

export default router;
