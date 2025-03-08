import Http from './http'

const http = new Http()

const createInventoryData = (data) => {
  const path = '/inventory/'

  return http.post(path, data)
}

const requestInventoryData = (page, params) => {
  const path = `/inventory/?page=${page}`

  return http.get(path, params)
}

const updateInventoryData = (data) => {
  const path = `/inventory/${data.id}/`

  return http.put(path, data)
}

export default { createInventoryData, requestInventoryData, updateInventoryData }
