import Http from './http'

const http = new Http()

const login = (data) => {
  const path = '/staff/login/'

  return http.post(path, data)
}

export default { login }
