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

export default {
  createOrder
}