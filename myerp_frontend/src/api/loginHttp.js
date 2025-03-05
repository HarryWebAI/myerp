import Http from './http'

const http = new Http()

const login = (data) => {
  const path = '/staff/login/'

  return http.post(path, data)
}

const resetPassword = (data) => {
  const path = '/staff/reset/'

  return http.put(path, data)
}

export default { login, resetPassword }
