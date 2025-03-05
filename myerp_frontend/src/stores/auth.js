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

  return { setToken, clearToken, user, token, isLogined }
})
