import Vue from 'vue'
import VueRouter from 'vue-router'
import HomeView from '../views/HomeView.vue'
import TrainingView from '../views/TrainingView.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/training/:tipoCurriculum',
    name: 'training',
    component: TrainingView
  },
  {
    path: '/upload',
    name: 'Upload',
    component: () => import('../views/UploadView.vue')
  },
  {
    path: '/curriculum-details',
    name: 'CurriculumDetails',
    component: () => import('../views/CurriculumDetailsView.vue')
  }



]

const router = new VueRouter({
  mode: 'history',
  routes
})

export default router
