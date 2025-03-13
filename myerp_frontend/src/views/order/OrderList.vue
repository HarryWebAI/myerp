<script setup>
import MainBox from '@/components/MainBox.vue'
import FormDialog from '@/components/FormDialog.vue'
import PaginationView from '@/components/PaginationView.vue'
import { onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import brandAndCategoryHttp from '@/api/brandAndCategoryHttp'
import clientHttp from '@/api/clientHttp'
import orderHttp from '@/api/orderHttp'
import staffHttp from '@/api/staffHttp'
import timeFormatter from '@/utils/timeFormatter'
import { ElMessage } from 'element-plus'

const router = useRouter()

/**筛选器 */
let filterForm = reactive({
  brand_id: 0,
  client_uid: '',
  staff_uid: '',
  delivery_status: '',
  payment_status: '',
  date_start: '',
  date_end: '',
  order_number: '',
})

/**分页器 */
let pagination = reactive({
  page: 1,
  total: 0,
})

/** 获取数据 */
let brands = ref([])
let clients = ref([])
let staffs = ref([])
let orders = ref([])
let totalAmount = ref(0)
let totalGrossProfit = ref(0)
let totalPendingBalance = ref(0)

// 订单状态选项
const deliveryStatusOptions = [
  { label: '全部', value: '' },
  { label: '新订单', value: 1 },
  { label: '已送货', value: 2 }
]

const paymentStatusOptions = [
  { label: '全部', value: '' },
  { label: '未结清', value: 1 },
  { label: '已结清', value: 2 }
]

// 获取订单列表
const getOrders = (page, params) => {
  orderHttp.getOrderList(page, params).then((result) => {
    if (result.status == 200) {
      orders.value = result.data.results
      pagination.total = result.data.count
      totalAmount.value = result.data.monthly_total_amount || 0
      totalGrossProfit.value = result.data.monthly_total_profit || 0
      totalPendingBalance.value = result.data.total_pending_balance || 0
    } else {
      ElMessage.error('请求订单数据失败!')
    }
  })
}

onMounted(() => {
  // 获取品牌列表
  brandAndCategoryHttp.requesetBrandData().then((result) => {
    if (result.status == 200) {
      brands.value = result.data
    } else {
      ElMessage.error('品牌数据请求失败!')
    }
  })

  // 获取客户列表
  clientHttp.getAllClients().then((result) => {
    if (result.status == 200) {
      clients.value = result.data
    } else {
      ElMessage.error('客户数据请求失败!')
    }
  })

  // 获取员工列表
  staffHttp.getStaffList().then((result) => {
    if (result.status == 200) {
      staffs.value = result.data
    } else {
      ElMessage.error('员工数据请求失败!')
    }
  })

  // 获取订单列表
  getOrders(1, filterForm)
})

/**切换页码 */
watch(
  () => pagination.page,
  () => {
    getOrders(pagination.page, filterForm)
  },
)

/**处理尾款支付 */
const paymentFormVisible = ref(false)
const paymentFormData = reactive({
  order: 0,
  amount: 0
})
const paymentForm = ref()

// 保存当前订单的待付尾款
const currentPendingBalance = ref(0)

// 打开尾款支付表单
const openPaymentForm = (order) => {
  paymentFormData.order = order.id
  // 将默认金额设置为0，而不是待付尾款
  paymentFormData.amount = 0
  // 保存当前订单的待付尾款，用于后续验证
  currentPendingBalance.value = order.pending_balance
  paymentFormVisible.value = true
}

// 提交尾款支付
const submitPayment = () => {
  // 首先检查金额是否为0
  if (paymentFormData.amount === 0) {
    ElMessage.error('支付金额不能为0！')
    return
  }

  // 检查金额是否超过待付尾款
  if (paymentFormData.amount > currentPendingBalance.value) {
    ElMessage.error(`支付金额不能超过待付尾款(￥${currentPendingBalance.value})！`)
    return
  }

  paymentForm.value.validate((valid) => {
    if (valid) {
      orderHttp.payBalance(paymentFormData).then((result) => {
        if (result.status === 201) {
          ElMessage.success('尾款支付成功!')
          paymentFormVisible.value = false
          // 重新加载订单列表
          getOrders(pagination.page, filterForm)
        } else {
          // 优化错误提示，显示后端返回的具体错误信息
          const errorMsg = result.data && result.data.detail ? result.data.detail : '尾款支付失败!'
          ElMessage.error(errorMsg)
        }
      }).catch(error => {
        // 捕获网络错误或后端返回的错误
        const errorMsg = error.response && error.response.data && error.response.data.detail
          ? error.response.data.detail
          : '支付处理出错，请稍后再试!'
        ElMessage.error(errorMsg)
      })
    }
  })
}

/**查看订单详情 */
const viewOrderDetail = (orderId) => {
  // 跳转到订单详情页面 - 在新窗口中打开
  router.push({ name: 'order_detail', params: { id: orderId } })
}

/**实现筛选功能 */
const onSearch = (action) => {
  if (action) {
    // 确保日期格式正确
    if (filterForm.date_start && typeof filterForm.date_start !== 'string') {
      filterForm.date_start = filterForm.date_start.toISOString().split('T')[0]
    }
    if (filterForm.date_end && typeof filterForm.date_end !== 'string') {
      filterForm.date_end = filterForm.date_end.toISOString().split('T')[0]
    }
    getOrders(1, filterForm)
  } else {
    // 重置筛选条件
    filterForm.brand_id = 0
    filterForm.client_uid = ''
    filterForm.staff_uid = ''
    filterForm.delivery_status = ''
    filterForm.payment_status = ''
    filterForm.date_start = ''
    filterForm.date_end = ''
    getOrders(1, filterForm)
  }
}

// 支付表单验证规则
const paymentFormRules = {
  amount: [
    { required: true, message: '请输入支付金额', trigger: 'blur' },
    { type: 'number', message: '金额必须为数字', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '金额必须大于0', trigger: 'blur' }
  ]
}
</script>

<template>
  <MainBox title="订单列表">
    <el-card class="order-list-card">
      <template #header>
        <div class="dashboard-header">
          <!-- 统计数据部分 -->
          <div class="summary-dashboard">
            <div class="summary-item">
              <el-icon class="summary-icon total-amount"><Money /></el-icon>
              <div class="summary-content">
                <span class="summary-label">当月总销量</span>
                <span class="summary-value amount">￥{{ totalAmount }}</span>
              </div>
            </div>
            <div class="summary-item">
              <el-icon class="summary-icon total-profit"><TrendCharts /></el-icon>
              <div class="summary-content">
                <span class="summary-label">当月总利润</span>
                <span class="summary-value profit">￥{{ totalGrossProfit }}</span>
              </div>
            </div>
            <div class="summary-item">
              <el-icon class="summary-icon pending-payment"><WalletFilled /></el-icon>
              <div class="summary-content">
                <span class="summary-label">待收尾款</span>
                <span class="summary-value pending">￥{{ totalPendingBalance }}</span>
              </div>
            </div>
          </div>

          <!-- 筛选部分 -->
          <div class="filter-section">
            <div class="filter-row">
              <el-input
                v-model="filterForm.order_number"
                placeholder="订单编号"
                clearable
                class="filter-item"
              >
                <template #prefix>
                  <el-icon><Document /></el-icon>
                </template>
              </el-input>

              <el-select v-model="filterForm.brand_id" placeholder="选择品牌" clearable class="filter-item">
                <template #prefix>
                  <el-icon><Menu /></el-icon>
                </template>
                <el-option :value="0" label="全部品牌" />
                <el-option
                  v-for="brand in brands"
                  :label="brand.name"
                  :value="brand.id"
                  :key="brand.id"
                />
              </el-select>

              <el-select v-model="filterForm.client_uid" placeholder="选择客户" clearable class="filter-item">
                <template #prefix>
                  <el-icon><User /></el-icon>
                </template>
                <el-option :value="''" label="全部客户" />
                <el-option
                  v-for="client in clients"
                  :label="client.name"
                  :value="client.uid"
                  :key="client.uid"
                />
              </el-select>

              <el-select v-model="filterForm.staff_uid" placeholder="选择员工" clearable class="filter-item">
                <template #prefix>
                  <el-icon><UserFilled /></el-icon>
                </template>
                <el-option :value="''" label="全部员工" />
                <el-option
                  v-for="staff in staffs"
                  :label="staff.name"
                  :value="staff.uid"
                  :key="staff.uid"
                />
              </el-select>
            </div>

            <div class="filter-row">
              <el-select v-model="filterForm.delivery_status" placeholder="发货状态" clearable class="filter-item">
                <template #prefix>
                  <el-icon><Check /></el-icon>
                </template>
                <el-option
                  v-for="option in deliveryStatusOptions"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>

              <el-select v-model="filterForm.payment_status" placeholder="付款状态" clearable class="filter-item">
                <template #prefix>
                  <el-icon><Check /></el-icon>
                </template>
                <el-option
                  v-for="option in paymentStatusOptions"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>

              <el-date-picker
                v-model="filterForm.date_start"
                type="date"
                placeholder="开始日期"
                format="YYYY-MM-DD"
                class="filter-item"
              />

              <el-date-picker
                v-model="filterForm.date_end"
                type="date"
                placeholder="结束日期"
                format="YYYY-MM-DD"
                class="filter-item"
              />
            </div>

            <div class="filter-actions">
              <el-button type="primary" @click="onSearch(true)" icon="Search">搜索</el-button>
              <el-button @click="onSearch(false)" icon="RefreshRight">重置</el-button>
            </div>
          </div>
        </div>
      </template>

      <el-table :data="orders" class="order-table" :header-cell-style="{ background: '#f5f7fa' }">
        <el-table-column prop="order_number" label="订单号" fixed />
        <el-table-column label="品牌" >
          <template #default="scope">
            <span>{{ scope.row.brand_name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="客户" >
          <template #default="scope">
            <span>{{ scope.row.client_name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="下单日期" >
          <template #default="scope">
            <span>{{ scope.row.sign_time ? timeFormatter.stringFromDate(scope.row.sign_time) : '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="总金额" class="table-amount">
          <template #default="scope">
            <span class="table-amount">￥{{ scope.row.total_amount }}</span>
          </template>
        </el-table-column>
        <el-table-column label="首付订金" >
          <template #default="scope">
            <span class="table-down-payment">￥{{ scope.row.down_payment }}</span>
          </template>
        </el-table-column>
        <el-table-column label="待付尾款" >
          <template #default="scope">
            <span :class="['table-balance', { 'pending-balance': scope.row.pending_balance > 0 }]">
              ￥{{ scope.row.pending_balance }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="毛利润" >
          <template #default="scope">
            <span :class="['table-profit', { 'positive-profit': scope.row.gross_profit >= 0, 'negative-profit': scope.row.gross_profit < 0 }]">
              ￥{{ scope.row.gross_profit }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="发货状态" >
          <template #default="scope">
            <el-tag
              :type="scope.row.delivery_status === 1 ? 'warning' : 'success'"
              class="status-tag"
            >
              {{ scope.row.delivery_status === 1 ? '新订单' : '已送货' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="付款状态">
          <template #default="scope">
            <el-tag
              :type="scope.row.payment_status === 1 ? 'warning' : 'success'"
              class="status-tag"
            >
              {{ scope.row.payment_status === 1 ? '未结清' : '已结清' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="250px">
          <template #default="scope">
            <div class="action-buttons">
              <el-button type="primary" @click="viewOrderDetail(scope.row.id)" size="small" class="action-button">
                <el-icon><View /></el-icon>
                <span>查看详情</span>
              </el-button>
              <el-button
                v-if="scope.row.pending_balance > 0"
                type="success"
                @click="openPaymentForm(scope.row)"
                size="small"
                class="action-button"
              >
                <el-icon><Money /></el-icon>
                <span>支付尾款</span>
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <div class="pagination-container">
          <PaginationView
            v-model="pagination.page"
            :page_size="10"
            :total="pagination.total"
          ></PaginationView>
        </div>
      </template>
    </el-card>
  </MainBox>

  <!-- 尾款支付表单 -->
  <FormDialog title="支付尾款" v-model="paymentFormVisible" @submit="submitPayment">
    <el-form
      ref="paymentForm"
      :model="paymentFormData"
      :rules="paymentFormRules"
      label-width="100px"
    >
      <div class="payment-info">
        <el-alert
          title="注意：付款后无法撤销，请确认金额正确"
          type="warning"
          :closable="false"
          show-icon
        />
      </div>
      <el-form-item label="支付金额" prop="amount">
        <el-input-number
          v-model.number="paymentFormData.amount"
          :precision="2"
          :min="0.00"
          style="width: 100%"
          placeholder="请输入支付金额"
        />
        <div class="form-tip">
          <p>最大可支付金额: ￥{{ currentPendingBalance }}</p>
          <p>系统将记录支付操作并自动更新订单状态</p>
        </div>
      </el-form-item>
    </el-form>
  </FormDialog>
</template>

<style scoped>
/* 主卡片样式 */
.order-list-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

/* 头部布局 */
.dashboard-header {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 统计数据样式 */
.summary-dashboard {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 16px;
  background: #f6f8fc;
  border-radius: 8px;
}

.summary-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s;
}

.summary-item:hover {
  transform: translateY(-2px);
}

.summary-icon {
  padding: 8px;
  border-radius: 8px;
  font-size: 24px;
}

.total-amount {
  background: #e6f3ff;
  color: #409EFF;
}

.total-profit {
  background: #e7f6e9;
  color: #67C23A;
}

.pending-payment {
  background: #fdf5e9;
  color: #E6A23C;
}

.summary-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-label {
  font-size: 14px;
  color: #606266;
}

.summary-value {
  font-size: 20px;
  font-weight: 600;
}

.amount { color: #409EFF; }
.profit { color: #67C23A; }
.pending { color: #E6A23C; }

/* 筛选区域样式 */
.filter-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.filter-row {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-item {
  width: 220px;
}

.filter-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 8px;
  border-top: 1px solid #ebeef5;
}

/* 响应式布局 */
@media (max-width: 1200px) {
  .filter-item {
    width: 100%;
  }

  .summary-dashboard {
    flex-direction: column;
  }

  .filter-row {
    flex-direction: column;
  }
}

/* 表格样式 */
.order-table {
  margin-top: 16px;
  border-radius: 6px;
  overflow: hidden;
}

:deep(.el-table) {
  border-radius: 6px;
  overflow: hidden;
}

:deep(.el-table th) {
  font-weight: 600;
  color: #606266;
}

:deep(.el-table__row) {
  transition: background-color 0.2s ease;
}

:deep(.el-table__row:hover) {
  background-color: #f0f5ff !important;
}

.table-amount, .table-down-payment, .table-balance, .table-profit {
  font-weight: 500;
}

.table-amount{
  color: #409EFF;
  font-weight: bold;
}

.pending-balance {
  color: #E6A23C;
  font-weight: bold;
}

.positive-profit {
  color: #67C23A;
  font-weight: bold;
}

.negative-profit {
  color: #F56C6C;
  font-weight: bold;
}

.status-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-button {
  border-radius: 4px;
  transition: transform 0.2s ease;
}

.action-button:hover {
  transform: translateY(-2px);
}

/* 分页容器 */
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

/* 添加表单提示样式 */
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.payment-info {
  margin-bottom: 20px;
}
</style>
