import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

class Http {
  constructor() {
    this.instance = axios.create({
      baseURL: import.meta.env.VITE_BASE_URL,
      timeout: 10000,
    })

    this.instance.interceptors.request.use((config) => {
      const authStore = useAuthStore()
      const token = authStore.token
      if (token) {
        config.headers.Authorization = 'JWT' + ' ' + authStore.token
      }
      return config
    })
  }

  post = (path, data) => {
    return (
      this.instance
        // 传输数据
        .post(path, data)
        // 如果成功(200)
        .then((response) => {
          return {
            status: response.status,
            data: response.data,
          }
        })
        // 如果失败(非200)
        .catch((error) => {
          return {
            status: error.response.status,
            data: error.response.data,
          }
        })
    )
  }

  put = (path, data) => {
    return this.instance
      .put(path, data)
      .then((response) => {
        return {
          status: response.status,
          data: response.data,
        }
      })
      .catch((error) => {
        return {
          status: error.response.status,
          data: error.response.data,
        }
      })
  }
}

export default Http
