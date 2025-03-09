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

// 收发货接口页面获取指定品牌的所有商品
const requestAllInventoryData = (id) => {
  if (id < 1) {
    return false
  }
  const path = `/allinventory/?brand_id=${id}`

  return http.get(path)
}

// 发货(采购)接口
const createPurchaseData = (data) => {
  const path = '/purchase/'

  return http.post(path, data)
}

// 采购列表
const requestPurchaseData = (page) => {
  const path = `/purchase/list/?page=${page}`

  return http.get(path)
}

// 在途详情: 要么通过purchase_id获取单次采购, 要么通过brand_id获取品牌在途采购
const requestPurchaseDetails = (id) => {
  const path = `/purchase/detail/${id}`

  return http.get(path)
}

export default {
  createInventoryData,
  requestInventoryData,
  updateInventoryData,
  requestAllInventoryData,
  createPurchaseData,
  requestPurchaseData,
  requestPurchaseDetails,
}
