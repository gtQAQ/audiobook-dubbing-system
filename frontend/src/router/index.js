import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // 路由配置定义
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        redirect: '/upload'
      },
      {
        path: 'upload',
        name: 'Upload',
        component: () => import('../views/Upload.vue')
      },
      {
        path: 'synthesize',
        name: 'Synthesize',
        component: () => import('../views/Synthesize.vue')
      },
      {
        path: 'history',
        name: 'History',
        component: () => import('../views/History.vue')
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/Profile.vue')
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/Users.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局路由守卫：检查用户是否登录，未登录则跳转至登录页。
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.name !== 'Login' && !token) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router
