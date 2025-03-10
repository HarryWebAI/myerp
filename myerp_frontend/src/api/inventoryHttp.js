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

// 采购详情
const requestPurchaseDetails = (id) => {
  const path = `/purchase/detail/${id}`

  return http.get(path)
}

// 收货接口
const createReceiveData = (data) => {
  const path = '/receive/'

  return http.post(path, data)
}

// 收货列表
const requestReceiveData = (page) => {
  const path = `/receive/list/?page=${page}`

  return http.get(path)
}

// 收货详情
const requestReceiveDetails = (id) => {
  const path = `/receive/detail/${id}`

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
  createReceiveData,
  requestReceiveData,
  requestReceiveDetails,
}
