<script setup>
import MainBox from '@/components/MainBox.vue'
import { onMounted, reactive, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import orderHttp from '@/api/orderHttp'
import timeFormatter from '@/utils/timeFormatter'
import { ElMessage, ElMessageBox } from 'element-plus'
import FormDialog from '@/components/FormDialog.vue'
import installerHttp from '@/api/installerHttp'
import dayjs from 'dayjs'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const orderId = route.params.id
const order = ref({})
const installers = ref([])
const loading = ref(true)

onMounted(() => {
  // 获取订单详情
  orderHttp.getOrderDetail(orderId).then((result) => {
    if (result.status === 200) {
      order.value = result.data
    } else {
      ElMessage.error('获取订单详情失败!')
    }
  })
  // 获取安装师傅列表
  installerHttp.requetAllInstallerData().then((result) => {
    if (result.status === 200) {
      installers.value = result.data
    } else {
      ElMessage.error('获取安装师傅列表失败!')
    }
  })
})

const installFormRef = ref()
const installFormData = reactive({
  installer_id: '',
  install_fee: 0,
  transport_fee: 0
})
const installFormRules = ref({
  installer_id: [{ required: true, message: '请选择安装师傅', trigger: 'blur' }],
  installation_fee: [{ required: true, message: '请输入安装费用', trigger: 'blur' }],
  transportation_fee: [{ required: true, message: '请输入运输费用', trigger: 'blur' }]
})
let installFormVisible = ref(false)

const handleInstall = () => {
  installFormData.installer_id = ''
  installFormData.installation_fee = 0
  installFormData.transportation_fee = 0
  installFormVisible.value = true
}

const handleInstallSubmit = () => {
  if (installFormData.installer_id === '') {
    ElMessage.error('请选择安装师傅!')
    return
  }
  if (installFormData.installation_fee === 0) {
    ElMessage.error('请输入安装费用!')
    return
  }
  if (installFormData.transportation_fee === 0) {
    ElMessage.error('请输入运输费用!')
    return
  }
  orderHttp.orderInstall(installFormData, orderId).then((result) => {
    if (result.status === 200) {
      ElMessage.success('一键出库成功!')
      setTimeout(() => {
        window.location.reload()
      }, 500);
    } else {
      ElMessage.error(result.data.detail)
    }
  })
}

/**
 * 订单作废功能
 */
const handleAbandonOrder = () => {
  ElMessageBox.confirm(
    '确定要作废该订单吗？此操作将永久删除该订单，且无法恢复！',
    '订单作废确认',
    {
      confirmButtonText: '确定作废',
      cancelButtonText: '取消',
      type: 'warning',
      distinguishCancelAndClose: true,
      closeOnClickModal: false
    }
  )
    .then(() => {
      orderHttp.abandonOrder({ order_id: orderId }).then((result) => {
        if (result.status === 200) {
          ElMessage.error(`订单${order.value.order_number}已作废！`)
          // 跳转回订单列表页
          setTimeout(() => {
            router.push('/order/list')
          }, 1000)
        } else {
          ElMessage.error(result.data.detail || '作废订单失败！')
        }
      })
      .catch(error => {
        console.error('作废订单出错:', error)
        ElMessage.error('作废订单失败: ' + (error.response?.data?.detail || error.message || '未知错误'))
      })
    })
    .catch(() => {
      ElMessage.info('已取消作废操作')
    })
}
</script>

<template>
  <MainBox title="订单详情">
    <el-card v-if="order">
      <template #header>
        <div class="header-box">
          <h3>订单号: {{ order.order_number }}</h3>
          <div>
            <el-tag :type="order.delivery_status === 1 ? 'warning' : 'success'" class="status-tag">
              {{ order.delivery_status === 1 ? '新订单' : '已送货' }}
            </el-tag>
            <el-tag :type="order.payment_status === 1 ? 'warning' : 'success'" class="status-tag">
              {{ order.payment_status === 1 ? '未结清' : '已结清' }}
            </el-tag>
          </div>
        </div>
      </template>

      <!-- 订单基本信息 -->
      <el-descriptions title="订单信息" :column="3" border>
        <el-descriptions-item label="下单日期">{{ order.sign_time ? timeFormatter.stringFromDate(order.sign_time) : '-'
        }}</el-descriptions-item>
        <el-descriptions-item label="客户">{{ order.client?.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="品牌">{{ order.brand?.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="业务员">{{ order.staff?.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="安装师傅">{{ order.installer?.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="安装地址">{{ order.address || '-' }}</el-descriptions-item>
        <el-descriptions-item label="总金额">
          <span class="amount">￥{{ order.total_amount }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="订金">
          <span>￥{{ order.down_payment }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="待付尾款">
          <span :class="{ 'pending-balance': order.pending_balance > 0 }">
            ￥{{ order.pending_balance }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="总成本" v-if="authStore.canViewCost">
          <span>￥{{ order.total_cost }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="毛利润" v-if="authStore.canViewCost">
          <span :class="['table-profit', { 'positive-profit': order.gross_profit > 0, 'negative-profit': order.gross_profit < 0 }]">
            ￥{{ order.gross_profit }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="备注">{{ order.remark || '-' }}</el-descriptions-item>
      </el-descriptions>

      <!-- 订单明细表格 -->
      <div class="details-section">
        <h3>订单明细</h3>
        <el-table :data="order.details" border style="width: 100%">
          <el-table-column label="商品名称" min-width="200">
            <template #default="scope">
              {{ scope.row.inventory_data?.full_name || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="分类" width="100">
            <template #default="scope">
              {{ scope.row.inventory_data?.category || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="80" align="center" />
          <el-table-column label="单价" width="120" v-if="authStore.canViewCost">
            <template #default="scope">
              <span>￥{{ scope.row.inventory_data?.cost || '0' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="金额" width="120" v-if="authStore.canViewCost">
            <template #default="scope">
              <span>￥{{ (scope.row.inventory_data?.cost || 0) * scope.row.quantity }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="install-section" v-if="order.delivery_status === 1">
        <div>
          <p class="install-note success-note"> - 如果货物齐全, 经与客户沟通后, 可以安排师傅出货, 上门安装完毕后请点击右侧的"一键出库", 完成出库!</p>
          <p class="install-note danger-note"> - 如果客户取消订单, 可以点击"作废订单"按钮, 该订单将被永久删除!</p>
        </div>
        <div class="action-buttons">
          <el-button type="success" @click="handleInstall()">一键出库</el-button>
          <el-button type="danger" @click="handleAbandonOrder">作废订单</el-button>
        </div>
      </div>
      <div class="install-section" v-else>
        <div>
          <template v-if="order.status === 'DELIVERED'">
            <p class="install-note install-note-success">订单已出库</p>
          </template>
          <template v-if="order.status === 'INSTALLED' && authStore.canViewCost">
            <p :class="['install-note', order.gross_profit >= 0 ? 'install-note-success' : 'install-note-danger']">
              订单已出库，本单{{ order.gross_profit >= 0 ? '盈利' : '亏损' }}
              <el-tag :type="order.gross_profit >= 0 ? 'success' : 'danger'">
                ￥ {{ order.gross_profit }}
              </el-tag>
            </p>
          </template>
          <template v-if="order.status === 'INSTALLED' && !authStore.canViewCost">
            <p class="install-note install-note-success">订单已安装完成</p>
          </template>
        </div>
      </div>

      <!-- 操作日志 -->
      <div class="log-section">
        <h3>操作日志</h3>
        <el-timeline>
          <el-timeline-item v-for="(log, index) in order.operation_logs" :key="index"
            :timestamp="log.created_at ? timeFormatter.stringFromDateTime(log.created_at) : '-'" type="primary">
            {{ log.description }}
            <p class="log-note">{{ log.operator_name ? `操作人: ${log.operator_name}` : '' }}</p>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-card>

    <el-empty v-else description="加载中..." />
  </MainBox>

  <!-- 一键出库表单 -->
  <FormDialog title="一键出库" v-model="installFormVisible" @submit="handleInstallSubmit" width="600">
    <el-form
      ref="installFormRef"
      :model="installFormData"
      :rules="installFormRules"
      :label-width="80"
    >
      <el-form-item label="安装师傅" prop="installer_id">
        <el-select v-model="installFormData.installer_id" placeholder="请选择安装师傅">
          <el-option v-for="item in installers" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="安装费用" prop="installation_fee">
        <el-input-number v-model="installFormData.installation_fee" :precision="2" :step="100" :min="0"
          style="width: 100%"></el-input-number>
      </el-form-item>
      <el-form-item label="运输费用" prop="transportation_fee">
        <el-input-number :precision="2" :step="100" :min="0" style="width: 100%"
          v-model="installFormData.transportation_fee" />
      </el-form-item>
    </el-form>
  </FormDialog>
</template>

<style scoped>
.header-box {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-tag {
  margin-left: 10px;
}

.details-section,
.log-section {
  margin-top: 20px;
}

.amount {
  font-weight: bold;
  color: #409EFF;
}

.pending-balance {
  color: #E6A23C;
  font-weight: bold;
}

.table-profit {
  font-weight: 500;
}

.positive-profit {
  color: #67C23A;
  font-weight: bold;
}

.negative-profit {
  color: #F56C6C;
  font-weight: bold;
}

.log-note {
  color: #909399;
  font-size: 12px;
  margin: 5px 0 0 0;
}

.install-section {
  margin-top: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.install-note {
  color: #909399;
  font-size: 12px;
  margin: 5px 0 0 0;
}

.success-note {
  color: #67C23A !important;
  font-weight: bold;
  font-size: 13px !important;
}

.danger-note {
  color: #F56C6C !important;
  font-weight: bold;
  font-size: 13px !important;
}

.install-note-success {
  color: #67C23A;
  font-weight: bold;
}

.install-note-danger {
  color: #F56C6C;
  font-weight: bold;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.warning-note {
  color: #E6A23C;
  margin-top: 5px;
}
</style>
