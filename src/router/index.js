import { createRouter, createWebHistory } from 'vue-router'

// 路由配置
const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { title: '仪表盘', icon: 'dashboard' }
  },
  {
    path: '/realtime',
    name: 'Realtime',
    component: () => import('../views/Realtime.vue'),
    meta: { title: '实时监控', icon: 'monitor' }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/History.vue'),
    meta: { title: '历史记录', icon: 'history' }
  },
  {
    path: '/annotation',
    name: 'Annotation',
    component: () => import('../views/Annotation.vue'),
    meta: { title: '数据标注', icon: 'edit' }
  },
  {
    path: '/model',
    name: 'Model',
    component: () => import('../views/Model.vue'),
    meta: { title: '模型训练', icon: 'model_training' }
  },
  {
    path: '/cv-operations',
    name: 'CVOperations',
    component: () => import('../views/CVOperation.vue'),
    meta: { title: '图像处理', icon: 'science' }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue'),
    meta: { title: '系统设置', icon: 'settings' }
  },
  // 404页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
    meta: { title: '页面未找到' }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 工业铸字识别系统` : '工业铸字识别系统'
  next()
})

export default router