import Http from './http'

const http = new Http()

const requetAllInstallerData = () => {
  const path = '/installer/'

  return http.get(path)
}

const createInstaller = (data) => {
  const path = '/installer/'
  return http.post(path, data)
}

const getInstallerDetail = (id) => {
  const path = `/installer/${id}/`
  return http.get(path)
}

const updateInstaller = (id, data) => {
  const path = `/installer/${id}/`
  return http.put(path, data)
}

const deleteInstaller = (id) => {
  const path = `/installer/${id}/`
  return http.delete(path)
}

export default {
  requetAllInstallerData,
  createInstaller,
  getInstallerDetail,
  updateInstaller,
  deleteInstaller
}
