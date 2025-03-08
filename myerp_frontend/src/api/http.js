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

  post = async (path, data) => {
    try {
      const response = await this.instance.post(path, data)
      return {
        status: response.status,
        data: response.data,
      }
    } catch (error) {
      return {
        status: error.response.status,
        data: error.response.data,
      }
    }
  }

  put = async (path, data) => {
    try {
      const response = await this.instance.put(path, data)
      return {
        status: response.status,
        data: response.data,
      }
    } catch (error) {
      return {
        status: error.response.status,
        data: error.response.data,
      }
    }
  }

  get = async (path, params) => {
    console.log(params)
    try {
      const response = await this.instance.get(path, { params })
      return {
        status: response.status,
        data: response.data,
      }
    } catch (error) {
      return {
        status: error.response.status,
        data: error.response.data,
      }
    }
  }

  delete = async (path) => {
    try {
      const response = await this.instance.delete(path)
      return {
        status: response.status,
        data: response.data,
      }
    } catch (error) {
      return {
        status: error.response.status,
        data: error.response.data,
      }
    }
  }
}

export default Http
