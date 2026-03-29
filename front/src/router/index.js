/*
 * 文件说明：前端路由配置文件，定义登录页、主业务壳页以及数据管理、训练、结果、预测等路由。
 * 维护重点：登录权限控制和页面跳转守卫统一放在这里。
 */
import { createRouter, createWebHashHistory } from 'vue-router'
import AppShell from '../layouts/AppShell.vue'
import LoginPage from '../pages/LoginPage.vue'
import DataManagementPage from '../pages/DataManagementPage.vue'
import ModelTrainingPage from '../pages/ModelTrainingPage.vue'
import TrainingResultPage from '../pages/TrainingResultPage.vue'
import PredictionPage from '../pages/PredictionPage.vue'
import { sessionState } from '../state/session'

// 实现思路：集中声明所有页面路由，并把登录前后可访问范围直接体现在路由树中。
const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      redirect: '/app/data-management'
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
      meta: { guestOnly: true }
    },
    {
      path: '/app',
      component: AppShell,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          redirect: '/app/data-management'
        },
        {
          path: 'data-management',
          name: 'data-management',
          component: DataManagementPage
        },
        {
          path: 'model-training',
          name: 'model-training',
          component: ModelTrainingPage
        },
        {
          path: 'model-training/result/:jobId',
          name: 'model-training-result',
          component: TrainingResultPage
        },
        {
          path: 'prediction',
          name: 'prediction',
          component: PredictionPage
        }
      ]
    }
  ]
})

// 实现思路：在全局前置守卫里统一控制登录页和业务页的访问边界。
router.beforeEach((to) => {
  if (to.meta.requiresAuth && !sessionState.isAuthenticated) {
    return { name: 'login' }
  }

  if (to.meta.guestOnly && sessionState.isAuthenticated) {
    return { name: 'data-management' }
  }

  return true
})

export default router
