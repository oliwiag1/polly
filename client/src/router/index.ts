import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue')
    },
    {
      path: '/surveys',
      name: 'surveys',
      component: () => import('@/views/SurveysListView.vue')
    },
    {
      path: '/surveys/create',
      name: 'create-survey',
      component: () => import('@/views/CreateSurveyView.vue')
    },
    {
      path: '/surveys/:id',
      name: 'fill-survey',
      component: () => import('@/views/FillSurveyView.vue')
    },
    {
      path: '/surveys/:id/stats',
      name: 'survey-stats',
      component: () => import('@/views/SurveyStatsView.vue')
    },
    {
      path: '/surveys/:id/success',
      name: 'survey-success',
      component: () => import('@/views/SurveySuccessView.vue')
    }
  ]
})

export default router
