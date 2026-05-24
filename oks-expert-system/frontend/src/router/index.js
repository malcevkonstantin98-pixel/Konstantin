import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { title: 'Панель мониторинга' }
  },
  {
    path: '/map',
    name: 'Map',
    component: () => import('@/views/MapView.vue'),
    meta: { title: 'Карта объектов' }
  },
  {
    path: '/objects/:id',
    name: 'ObjectDetail',
    component: () => import('@/views/ObjectDetailView.vue'),
    meta: { title: 'Карточка объекта' }
  },
  {
    path: '/reports',
    name: 'FieldReports',
    component: () => import('@/views/FieldReportsView.vue'),
    meta: { title: 'Полевые отчёты' }
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('@/views/TasksView.vue'),
    meta: { title: 'Задачи и регламенты' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || 'ОКС Эксперт'} - Система управления объектами`
  next()
})

export default router
