import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import MainView from '@/views/MainView.vue'
import LoginView from '@/views/LoginView.vue'
import HomeView from '@/views/home/HomeView.vue'
import BrandAndCategoryView from '@/views/brandAndCategory/BrandAndCategoryView.vue'
import InventoryList from '@/views/inventory/InventoryList.vue'
import InventoryPurchase from '@/views/inventory/InventoryPurchase.vue'
import PurchaseList from '@/views/inventory/PurchaseList.vue'
import PurchaseDetail from '@/views/inventory/PurchaseDetail.vue'
import InventoryReceive from '@/views/inventory/InventoryReceive.vue'
import ReceiveList from '@/views/inventory/ReceiveList.vue'
import ReceiveDetail from '@/views/inventory/ReceiveDetail.vue'

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
        {
          path: 'inventory',
          children: [
            {
              path: 'list',
              name: 'inventory_list',
              component: InventoryList,
            },
            {
              path: 'purchase',
              name: 'inventory_purchase',
              component: InventoryPurchase,
            },
            {
              path: 'purchase/list',
              name: 'inventory_purchase_list',
              component: PurchaseList,
            },
            {
              path: 'purchase/detail/:id',
              name: 'inventory_purchase_detail',
              component: PurchaseDetail,
            },
            {
              path: 'receive',
              name: 'inventory_receive',
              component: InventoryReceive,
            },
            {
              path: 'receive/list',
              name: 'inventory_receive_list',
              component: ReceiveList,
            },
            {
              path: 'receive/detail/:id',
              name: 'inventory_receive_detail',
              component: ReceiveDetail,
            },
          ],
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
