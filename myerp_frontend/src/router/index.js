import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import MainView from '@/views/MainView.vue'
import LoginView from '@/views/LoginView.vue'
import HomeView from '@/views/home/HomeView.vue'
import BrandAndCategoryView from '@/views/brandAndCategory/BrandAndCategoryView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'main',
      component: MainView,
      children: [
        {
          path: '',
          name: 'home',
          component: HomeView,
        },
        {
          path: 'brandandcategory',
          name: 'brandandcategory',
          component: BrandAndCategoryView,
        },
      ],
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
  ],
})

router.beforeEach((to) => {
  const authStore = useAuthStore()
  if (!authStore.isLogined && to.name != 'login') {
    ElMessage.error('请先登录!')
    return { name: 'login' }
  }
})

export default router
