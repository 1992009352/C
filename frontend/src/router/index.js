import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/Dashboard.vue'), meta: { title: '仪表盘', icon: 'Odometer' } },
      { path: 'finance', name: 'Finance', component: () => import('@/views/Finance.vue'), meta: { title: '财务管理', icon: 'Wallet' } },
      { path: 'health', name: 'Health', component: () => import('@/views/Health.vue'), meta: { title: '健康管理', icon: 'FirstAidKit' } },
      { path: 'exercise', name: 'Exercise', component: () => import('@/views/Exercise.vue'), meta: { title: '运动记录', icon: 'Trophy' } },
      { path: 'diet', name: 'Diet', component: () => import('@/views/Diet.vue'), meta: { title: '饮食管理', icon: 'Coffee' } },
      { path: 'todo', name: 'Todo', component: () => import('@/views/Todo.vue'), meta: { title: '待办事项', icon: 'Finished' } },
      { path: 'notes', name: 'Notes', component: () => import('@/views/Notes.vue'), meta: { title: '笔记管理', icon: 'Notebook' } },
      { path: 'habits', name: 'Habits', component: () => import('@/views/Habits.vue'), meta: { title: '习惯追踪', icon: 'AlarmClock' } },
      { path: 'reading', name: 'Reading', component: () => import('@/views/Reading.vue'), meta: { title: '阅读管理', icon: 'Reading' } },
      { path: 'experiences', name: 'Experiences', component: () => import('@/views/Experiences.vue'), meta: { title: '人生经历', icon: 'MapLocation' } },
      { path: 'contacts', name: 'Contacts', component: () => import('@/views/Contacts.vue'), meta: { title: '联系人', icon: 'User' } },
      { path: 'passwords', name: 'Passwords', component: () => import('@/views/Passwords.vue'), meta: { title: '密码管理', icon: 'Lock' } },
      { path: 'goals', name: 'Goals', component: () => import('@/views/Goals.vue'), meta: { title: '目标管理', icon: 'Flag' } },
      { path: 'profile', name: 'Profile', component: () => import('@/views/Profile.vue'), meta: { title: '个人设置', icon: 'Setting' } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (!to.meta.public && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
