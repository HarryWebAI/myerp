import Http from './http'

const http = new Http()

// 获取客户列表（带分页）
const getClientList = (page = 1, params = {}) => {
  const path = `/client/?page=${page}`
  return http.get(path, params)
}

// 获取今日需要跟进的客户列表
const getOverdueClients = (params) => {
  const path = '/client/overdue/'
  return http.get(path, params)
}

// 创建新客户
const createClient = (data) => {
  const path = '/client/'
  return http.post(path, data)
}

// 获取客户详情
const getClientDetail = (uid) => {
  const path = `/client/${uid}/`
  return http.get(path)
}

// 更新客户信息
const updateClient = (uid, data) => {
  const path = `/client/${uid}/`
  return http.put(path, data)
}

// 跟进客户
const followClient = (uid, data) => {
  const path = `/client/${uid}/follow/`
  return http.post(path, data)
}

export default {
  getClientList,
  getOverdueClients,
  createClient,
  getClientDetail,
  updateClient,
  followClient
}
