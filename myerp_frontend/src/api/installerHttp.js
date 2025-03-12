import Http from './http'

const http = new Http()

const requetAllInstallerData = () => {
  const path = '/installers/'

  return http.get(path)
}

export default {
  requetAllInstallerData
}
