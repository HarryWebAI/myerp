import { computed } from 'vue'
import { defineStore } from 'pinia'

const USER_KEY = 'JWT_TOKEN_FROM_MYERP_USER_INFO'
const TOKEN_KEY = 'JWT_TOKEN_FROM_MYERP_TOKEN'

export const useAuthStore = defineStore('auth', () => {
  const setToken = (data) => {
    localStorage.setItem(USER_KEY, JSON.stringify(data.user))
    localStorage.setItem(TOKEN_KEY, data.token)
  }

  const clearToken = () => {
    localStorage.removeItem(USER_KEY)
    localStorage.removeItem(TOKEN_KEY)
  }

  let user = computed(() => {
    return localStorage.getItem(USER_KEY) ? JSON.parse(localStorage.getItem(USER_KEY)) : false
  })

  let token = computed(() => {
    return localStorage.getItem(TOKEN_KEY) ? localStorage.getItem(TOKEN_KEY) : false
  })

  let isLogined = computed(() => {
    if (localStorage.getItem(USER_KEY) && localStorage.getItem(TOKEN_KEY)) {
      return true
    }

    return false
  })

  // 判断是否为老板
  const isBoss = computed(() => {
    // 如果用户信息中没有is_boss字段，但同时具有is_manager和is_storekeeper权限，可视为boss
    if (user.value && user.value.is_boss === undefined) {
      return user.value.is_manager === true && user.value.is_storekeeper === true
    }
    return user.value && user.value.is_boss === true
  })

  // 判断是否为门店经理
  const isManager = computed(() => {
    return user.value && user.value.is_manager === true
  })

  // 判断是否为仓库管理员
  const isStorekeeper = computed(() => {
    return user.value && user.value.is_storekeeper === true
  })

  // 判断是否为普通员工
  const isRegularStaff = computed(() => {
    return user.value && !user.value.is_boss && !user.value.is_manager && !user.value.is_storekeeper
  })

  // 判断是否有特定角色权限
  const hasRole = (role) => {
    if (!user.value) return false
    return user.value[role] === true
  }

  // 判断是否有权限访问特定功能
  const hasPermission = (feature) => {
    if (!user.value) return false

    // 定义功能权限映射
    const permissionMap = {
      // 所有人可访问
      'client_management': true,

      // 老板和门店经理可访问
      'system_management': isBoss.value || isManager.value,
      'order_management': isBoss.value || isManager.value,

      // 只有老板可访问
      'staff_management': isBoss.value,

      // 老板可访问所有库存功能
      'inventory_all': isBoss.value,

      // 仓库管理员只能访问收货功能
      'inventory_receive': isBoss.value || isStorekeeper.value
    }

    return permissionMap[feature] || false
  }

  // 判断是否可以查看成本相关信息（只有老板可以查看）
  const canViewCost = computed(() => {
    return isBoss.value
  })

  // 格式化成本显示，根据用户角色决定是否显示实际成本
  const formatCost = (cost) => {
    if (canViewCost.value) {
      return typeof cost === 'number' ? `￥${cost.toFixed(2)}` : `￥${cost}`
    } else {
      return '***'
    }
  }

  return {
    setToken,
    clearToken,
    user,
    token,
    isLogined,
    isBoss,
    isManager,
    isStorekeeper,
    isRegularStaff,
    hasRole,
    hasPermission,
    canViewCost,
    formatCost
  }
})
