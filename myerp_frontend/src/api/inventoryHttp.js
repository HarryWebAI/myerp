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

// 收发货接口: 获取指定品牌的所有商品
const requestAllInventoryData = (id) => {
  if (id < 1) {
    return
  }
  const path = `/allinventory/?brand_id=${id}`

  return http.get(path)
}

export default {
  createInventoryData,
  requestInventoryData,
  updateInventoryData,
  requestAllInventoryData,
}
