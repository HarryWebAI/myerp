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
      console.log(result)
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
  order_id: 0,
  amount: 0,
  payment_method: 'cash',
  payment_date: new Date().toISOString().split('T')[0],
  note: ''
})
const paymentForm = ref()

// 打开尾款支付表单
const openPaymentForm = (order) => {
  paymentFormData.order_id = order.id
  paymentFormData.amount = order.pending_balance
  paymentFormVisible.value = true
}

// 提交尾款支付
const submitPayment = () => {
  paymentForm.value.validate((valid) => {
    if (valid) {
      orderHttp.payBalance(paymentFormData).then((result) => {
        if (result.status === 201) {
          ElMessage.success('尾款支付成功!')
          paymentFormVisible.value = false
          // 重新加载订单列表
          getOrders(pagination.page, filterForm)
        } else {
          ElMessage.error('尾款支付失败!')
        }
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

// 支付方式选项
const paymentMethodOptions = [
  { label: '现金', value: 'cash' },
  { label: '银行转账', value: 'bank_transfer' },
  { label: '支付宝', value: 'alipay' },
  { label: '微信支付', value: 'wechat_pay' }
]

// 支付表单验证规则
const paymentFormRules = {
  amount: [
    { required: true, message: '请输入支付金额', trigger: 'blur' },
    { type: 'number', message: '金额必须为数字', trigger: 'blur' }
  ],
  payment_method: [
    { required: true, message: '请选择支付方式', trigger: 'change' }
  ],
  payment_date: [
    { required: true, message: '请选择支付日期', trigger: 'blur' }
  ]
}
</script>

<template>
  <MainBox title="订单列表">
    <el-card class="order-list-card">
      <template #header>
        <div class="dashboard-header">
          <div class="filter-section">
            <div class="filter-header">
              <span class="filter-title">订单筛选</span>
              <div class="filter-actions">
                <el-button type="primary" @click="onSearch(true)" size="small" icon="Search">搜索</el-button>
                <el-button @click="onSearch(false)" size="small" icon="RefreshRight">重置</el-button>
              </div>
            </div>

            <!-- 使用Element Plus栅格布局 -->
            <el-form size="small" class="filter-form" label-position="left">
              <!-- 第一行：品牌、客户、员工 -->
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-form-item label="品牌" label-width="40px">
                    <el-select v-model="filterForm.brand_id" placeholder="全部品牌" class="fixed-width-select">
                      <el-option :value="0" label="全部品牌" />
                      <el-option
                        v-for="brand in brands"
                        :label="brand.name"
                        :value="brand.id"
                        :key="brand.id"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="客户" label-width="40px">
                    <el-select v-model="filterForm.client_uid" placeholder="全部客户" class="width-220">
                      <el-option :value="''" label="全部客户" />
                      <el-option
                        v-for="client in clients"
                        :label="client.name"
                        :value="client.uid"
                        :key="client.uid"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="员工" label-width="40px">
                    <el-select v-model="filterForm.staff_uid" placeholder="全部员工" class="width-220">
                      <el-option :value="''" label="全部员工" />
                      <el-option
                        v-for="staff in staffs"
                        :label="staff.name"
                        :value="staff.uid"
                        :key="staff.uid"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <!-- 第二行：发货状态、付款状态、订单日期 -->
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="status-group">
                    <el-form-item label="发货" label-width="40px">
                      <el-select v-model="filterForm.delivery_status" class="status-select">
                        <el-option
                          v-for="option in deliveryStatusOptions"
                          :key="option.value"
                          :label="option.label"
                          :value="option.value"
                        />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="付款" label-width="40px" style="margin-left: 25px;">
                      <el-select v-model="filterForm.payment_status" class="status-select">
                        <el-option
                          v-for="option in paymentStatusOptions"
                          :key="option.value"
                          :label="option.label"
                          :value="option.value"
                        />
                      </el-select>
                    </el-form-item>
                  </div>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="日期" label-width="40px">
                    <el-date-picker
                      v-model="filterForm.date_start"
                      type="date"
                      placeholder="开始日期"
                      format="YYYY-MM-DD"
                      class="width-220"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="直到" label-width="40px">
                    <el-date-picker
                      v-model="filterForm.date_end"
                      type="date"
                      placeholder="结束日期"
                      format="YYYY-MM-DD"
                      class="width-220"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </div>
          <div class="summary-dashboard">
            <div class="summary-item-card">
              <div class="summary-icon-container total-amount">
                <el-icon><Money /></el-icon>
              </div>
              <div class="summary-details">
                <div class="summary-label">当月总销量</div>
                <div class="summary-value amount">￥{{ totalAmount }}</div>
              </div>
            </div>
            <div class="summary-item-card">
              <div class="summary-icon-container total-profit">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="summary-details">
                <div class="summary-label">当月总利润</div>
                <div class="summary-value profit">￥{{ totalGrossProfit }}</div>
              </div>
            </div>
            <div class="summary-item-card">
              <div class="summary-icon-container pending-payment">
                <el-icon><WalletFilled /></el-icon>
              </div>
              <div class="summary-details">
                <div class="summary-label">待收尾款</div>
                <div class="summary-value pending">￥{{ totalPendingBalance }}</div>
              </div>
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
        <el-table-column label="总金额">
          <template #default="scope">
            <span class="table-amount">￥{{ scope.row.total_amount }}</span>
          </template>
        </el-table-column>
        <el-table-column label="已付订金" >
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
            <span :class="['table-profit', { 'positive-profit': scope.row.gross_profit > 0, 'negative-profit': scope.row.gross_profit < 0 }]">
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
      <el-form-item label="支付金额" prop="amount">
        <el-input-number v-model.number="paymentFormData.amount" :precision="2" :min="0" style="width: 100%" />
      </el-form-item>
      <el-form-item label="支付方式" prop="payment_method">
        <el-select v-model="paymentFormData.payment_method" style="width: 100%">
          <el-option
            v-for="option in paymentMethodOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="支付日期" prop="payment_date">
        <el-date-picker
          v-model="paymentFormData.payment_date"
          type="date"
          style="width: 100%"
          format="YYYY-MM-DD"
        />
      </el-form-item>
      <el-form-item label="备注" prop="note">
        <el-input type="textarea" v-model="paymentFormData.note" :rows="3" />
      </el-form-item>
    </el-form>
  </FormDialog>
</template>

<style scoped>
/* 主卡片样式 */
.order-list-card {
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

/* 头部仪表盘区域 */
.dashboard-header {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 筛选区样式 */
.filter-section {
  background-color: #f9fafc;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.filter-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
}

.filter-title::before {
  content: '';
  display: inline-block;
  width: 3px;
  height: 16px;
  background-color: #409EFF;
  margin-right: 8px;
  border-radius: 2px;
}

.filter-actions {
  display: flex;
  gap: 8px;
}

.filter-form {
  width: 100%;
}

/* 栅格布局样式 */
.full-width-select {
  width: 100%;
}

.fixed-width-select {
  width: 250px !important;
}

.width-220 {
  width: 220px !important;
}

.status-group {
  display: flex;
  width: 100%;
}

.status-select {
  width: 92px; /* 调整宽度，使两个状态选择器加label宽度等于品牌选择器加label宽度 */
}

/* 汇总卡片样式 */
.summary-dashboard {
  display: flex;
  gap: 20px;
  margin-top: 10px;
}

.summary-item-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 15px;
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.summary-item-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.summary-icon-container {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.summary-icon-container :deep(svg) {
  width: 24px;
  height: 24px;
  color: white;
}

.total-amount {
  background-color: #409EFF;
}

.total-profit {
  background-color: #67C23A;
}

.pending-payment {
  background-color: #E6A23C;
}

.summary-details {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.summary-label {
  font-size: 13px;
  color: #909399;
}

.summary-value {
  font-size: 18px;
  font-weight: 600;
}

.amount {
  color: #409EFF;
}

.profit {
  color: #67C23A;
}

.pending {
  color: #E6A23C;
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
  justify-content: flex-end;
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .status-group {
    flex-direction: column;
    gap: 10px;
  }

  .status-select {
    width: 100%;
  }

  .fixed-width-select,
  .width-220 {
    width: 100% !important;
  }

  .summary-dashboard {
    flex-direction: column;
  }
}
</style>
