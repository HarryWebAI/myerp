import Http from './http'

const http = new Http()

// 获取员工列表
const getStaffList = () => {
  const path = '/staff/'
  return http.get(path)
}

export default {
  getStaffList
}
