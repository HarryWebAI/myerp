import Http from './http'

const http = new Http()

// 获取所有品牌的库存总价值
export const getInventoryByBrand = () => http.get('/inventory-by-brand/')

// 获取每个员工本月的销售业绩
export const getStaffPerformance = () => http.get('/staff-performance/')

// 获取当前年份1~12月的销售数据
export const getCurrentYearMonthlySales = () => http.get('/current-year-sales/')

export default {
    getInventoryByBrand,
    getStaffPerformance,
    getCurrentYearMonthlySales
}