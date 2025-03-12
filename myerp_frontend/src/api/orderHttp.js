/**
 * 订单管理模块的http请求
 */

import Http from "./http";

const http = new Http()

// 创建订单
const createOrder = (data) => {
  const path = '/order/create/'

  return http.post(path, data)
}

// 获取订单列表（带分页）
const getOrderList = (page = 1, params = {}) => {
  const path = `/orders/?page=${page}`
  return http.get(path, params)
}

// 获取订单详情
const getOrderDetail = (orderId) => {
  const path = `/orders/${orderId}/`
  return http.get(path)
}

// 获取订单明细
const getOrderDetails = (params = {}) => {
  const path = '/order-details/'
  return http.get(path, params)
}

// 处理尾款支付
const payBalance = (data) => {
  const path = '/balance-payments/'
  return http.post(path, data)
}

// 一键出库orderInstall
const orderInstall = (data, id) => {
  const path = `/order-install/${id}/`
  return http.put(path, data)
}

export default {
  createOrder,
  getOrderList,
  getOrderDetail,
  getOrderDetails,
  payBalance,
  orderInstall
}
