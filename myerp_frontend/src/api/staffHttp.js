import Http from './http'

const http = new Http()

// 获取员工列表
const getStaffList = () => {
  const path = '/staff/allstaff/'
  return http.get(path)
}

// 创建员工
const createStaff = (data) => {
  const path = '/staff/create/'
  return http.post(path, data)
}

// 更新员工信息
const updateStaff = (uid, data) => {
  const path = `/staff/update/${uid}/`
  return http.put(path, data)
}

export default {
  getStaffList,
  createStaff,
  updateStaff
}
