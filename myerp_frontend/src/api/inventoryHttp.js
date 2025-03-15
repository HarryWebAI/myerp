import Http from './http'

const http = new Http()

// 创建库存商品
const createInventoryData = (data) => {
  const path = '/inventory/'

  return http.post(path, data)
}

// 获取库存商品列表
const requestInventoryData = (page, params) => {
  const path = `/inventory/?page=${page}`

  return http.get(path, params)
}

// 更新库存商品
const updateInventoryData = (data) => {
  const path = `/inventory/${data.id}/`

  return http.put(path, data)
}

// 收发货接口页面获取指定品牌的所有商品(不分页)
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

// 采购明细修正
const updatePurchaseDetail = (id, data) => {
  const path = `/purchase/detail/update/${id}/`

  return http.put(path, data)
}

// 收货明细修正
const updateReceiveDetail = (id, data) => {
  const path = `/receive/detail/update/${id}/`

  return http.put(path, data)
}

// 删除采购明细
const deletePurchaseDetail = (id) => {
  const path = `/purchase/detail/delete/${id}/`

  return http.delete(path)
}

// 删除收货明细
const deleteReceiveDetail = (id) => {
  const path = `/receive/detail/delete/${id}/`

  return http.delete(path)
}

// 下载库存数据
const downloadInventoryData = () => {
  const path = '/download/'

  return http.download(path)
}

// 获取库存日志
const requestInventoryLog = () => {
  const path = '/log/'

  return http.get(path)
}

// 添加更新采购成本的函数
const updatePurchaseCost = (id, data) => {
  const path = `/purchase/cost/update/${id}/`
  return http.put(path, data)
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
  updatePurchaseDetail,
  updateReceiveDetail,
  deletePurchaseDetail,
  deleteReceiveDetail,
  downloadInventoryData,
  requestInventoryLog,
  updatePurchaseCost,
}
