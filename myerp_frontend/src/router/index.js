import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import MainView from '@/views/MainView.vue'
import LoginView from '@/views/LoginView.vue'
import HomeView from '@/views/home/HomeView.vue'
import BrandAndCategoryView from '@/views/system/BrandAndCategoryView.vue'
import InventoryList from '@/views/inventory/InventoryList.vue'
import InventoryPurchase from '@/views/inventory/InventoryPurchase.vue'
import PurchaseList from '@/views/inventory/PurchaseList.vue'
import PurchaseDetail from '@/views/inventory/PurchaseDetail.vue'
import InventoryReceive from '@/views/inventory/InventoryReceive.vue'
import ReceiveList from '@/views/inventory/ReceiveList.vue'
import ReceiveDetail from '@/views/inventory/ReceiveDetail.vue'
import ClientList from '@/views/client/ClientList.vue'
import ClientDetail from '@/views/client/ClientDetail.vue'
import CreateOrder from '@/views/order/CreateOrder.vue'
import OrderList from '@/views/order/OrderList.vue'
import InventoryExcel from '@/views/inventory/InventoryExcel.vue'
import InstallerView from '@/views/system/InstallerView.vue'
import StaffView from '@/views/system/StaffView.vue'
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
          meta: { requiresAuth: true }
        },
        {
          path: 'system',
          children: [
            {
              path: 'brandandcategory',
              name: 'brandandcategory',
              component: BrandAndCategoryView,
              meta: { requiresAuth: true, roles: ['is_boss', 'is_manager'] }
            },
            {
              path: 'installer',
              name: 'installer',
              component: InstallerView,
              meta: { requiresAuth: true, roles: ['is_boss', 'is_manager'] }
            },
            {
              path: 'staff',
              name: 'staff',
              component: StaffView,
              meta: { requiresAuth: true, roles: ['is_boss'] }
            }
          ],
        },
        {
          path: 'inventory',
          children: [
            {
              path: 'list',
              name: 'inventory_list',
              component: InventoryList,
              meta: { requiresAuth: true, roles: ['is_boss'] }
            },
            {
              path: 'purchase',
              name: 'inventory_purchase',
              component: InventoryPurchase,
              meta: { requiresAuth: true, roles: ['is_boss'] }
            },
            {
              path: 'purchase/list',
              name: 'inventory_purchase_list',
              component: PurchaseList,
              meta: { requiresAuth: true, roles: ['is_boss'] }
            },
            {
              path: 'purchase/detail/:id',
              name: 'inventory_purchase_detail',
              component: PurchaseDetail,
              meta: { requiresAuth: true, roles: ['is_boss'] }
            },
            {
              path: 'receive',
              name: 'inventory_receive',
              component: InventoryReceive,
              meta: { requiresAuth: true, roles: ['is_boss', 'is_storekeeper'] }
            },
            {
              path: 'receive/list',
              name: 'inventory_receive_list',
              component: ReceiveList,
              meta: { requiresAuth: true, roles: ['is_boss', 'is_storekeeper'] }
            },
            {
              path: 'receive/detail/:id',
              name: 'inventory_receive_detail',
              component: ReceiveDetail,
              meta: { requiresAuth: true, roles: ['is_boss', 'is_storekeeper'] }
            },
            {
              path: 'excel',
              name: 'inventory_excel',
              component: InventoryExcel,
              meta: { requiresAuth: true, roles: ['is_boss'] }
            },
          ],
        },
        {
          path: 'client',
          children: [
            {
              path: 'list',
              name: 'client_list',
              component: ClientList,
              meta: { requiresAuth: true }
            },
            {
              path: 'detail/:id',
              name: 'client_detail',
              component: ClientDetail,
              meta: { requiresAuth: true }
            },
          ],
        },
        {
          path: 'order',
          children: [
            {
              path: 'create',
              name: 'order_create',
              component: CreateOrder,
              meta: { requiresAuth: true, roles: ['is_boss', 'is_manager'] }
            },
            {
              path: 'list',
              name: 'order_list',
              component: OrderList,
              meta: { requiresAuth: true, roles: ['is_boss', 'is_manager'] }
            },
            {
              path: 'detail/:id',
              name: 'order_detail',
              component: () => import('@/views/order/OrderDetail.vue'),
              meta: { requiresAuth: true, roles: ['is_boss', 'is_manager'] }
            },
          ],
        }
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

  // 检查是否需要登录
  if (!authStore.isLogined && to.name !== 'login') {
    ElMessage.error('请先登录!')
    return { name: 'login' }
  }

  // 如果路由需要特定角色
  if (to.meta.roles && authStore.isLogined) {
    // 检查用户是否有所需角色
    let hasPermission = false

    // 检查是否满足角色要求
    if (to.meta.roles.includes('is_boss') && authStore.isBoss) {
      hasPermission = true
    } else if (to.meta.roles.includes('is_manager') && authStore.isManager) {
      hasPermission = true
    } else if (to.meta.roles.includes('is_storekeeper') && authStore.isStorekeeper) {
      // 对于仓库管理员，进一步限制其只能访问收货相关的页面
      if (to.name === 'inventory_receive' ||
          to.name === 'inventory_receive_list' ||
          to.name === 'inventory_receive_detail') {
        hasPermission = true
      } else {
        hasPermission = false
      }
    }

    if (!hasPermission) {
      ElMessage.error('您没有权限访问该页面!')
      return { name: 'home' }
    }
  }
})

export default router
