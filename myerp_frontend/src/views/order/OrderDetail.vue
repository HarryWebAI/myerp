<script setup>
import MainBox from '@/components/MainBox.vue'
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import orderHttp from '@/api/orderHttp'
import { ElMessage } from 'element-plus'

const route = useRoute()
const orderId = route.params.id
const order = ref(null)
const orderDetails = ref([])

onMounted(() => {
  // 获取订单详情
  orderHttp.getOrderDetail(orderId).then((result) => {
    if (result.status === 200) {
      order.value = result.data
    } else {
      ElMessage.error('获取订单详情失败!')
    }
  })

  // 获取订单明细
  orderHttp.getOrderDetails({ order_id: orderId }).then((result) => {
    if (result.status === 200) {
      orderDetails.value = result.data.results
    } else {
      ElMessage.error('获取订单明细失败!')
    }
  })
})

// 日期格式化
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}
</script>

<template>
  <MainBox title="订单详情">
    <el-card v-if="order">
      <template #header>
        <div class="header-box">
          <h3>订单号: {{ order.order_number }}</h3>
          <div>
            <el-tag
              :type="order.delivery_status === 'pending' ? 'warning' :
                order.delivery_status === 'shipped' ? 'primary' : 'success'"
              class="status-tag"
            >
              {{ order.delivery_status === 'pending' ? '待发货' :
                order.delivery_status === 'shipped' ? '已发货' : '已签收' }}
            </el-tag>
            <el-tag
              :type="order.payment_status === 'down_payment' ? 'warning' : 'success'"
              class="status-tag"
            >
              {{ order.payment_status === 'down_payment' ? '已付订金' : '已付尾款' }}
            </el-tag>
          </div>
        </div>
      </template>

      <!-- 订单基本信息 -->
      <el-descriptions title="订单信息" :column="3" border>
        <el-descriptions-item label="下单日期">{{ formatDate(order.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="客户">{{ order.client?.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="品牌">{{ order.brand?.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="业务员">{{ order.staff?.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="安装师傅">{{ order.installer?.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="收货地址">{{ order.address || '-' }}</el-descriptions-item>
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
        <el-descriptions-item label="总成本">
          <span>￥{{ order.total_cost }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="毛利润">
          <span :class="{ 'positive-profit': order.gross_profit > 0, 'negative-profit': order.gross_profit < 0 }">
            ￥{{ order.gross_profit }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="备注">{{ order.note || '-' }}</el-descriptions-item>
      </el-descriptions>

      <!-- 订单明细表格 -->
      <div class="details-section">
        <h3>订单明细</h3>
        <el-table :data="orderDetails" border style="width: 100%">
          <el-table-column prop="inventory.full_name" label="商品名称" min-width="200" />
          <el-table-column prop="size" label="规格" width="100" />
          <el-table-column prop="color" label="颜色" width="100" />
          <el-table-column prop="quantity" label="数量" width="80" align="center" />
          <el-table-column label="单价" width="120">
            <template #default="scope">
              <span>￥{{ scope.row.unit_price }}</span>
            </template>
          </el-table-column>
          <el-table-column label="金额" width="120">
            <template #default="scope">
              <span>￥{{ scope.row.amount }}</span>
            </template>
          </el-table-column>
          <el-table-column label="成本" width="120">
            <template #default="scope">
              <span>￥{{ scope.row.cost }}</span>
            </template>
          </el-table-column>
          <el-table-column label="利润" width="120">
            <template #default="scope">
              <span :class="{ 'positive-profit': scope.row.profit > 0, 'negative-profit': scope.row.profit < 0 }">
                ￥{{ scope.row.profit }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 操作日志 -->
      <div class="log-section">
        <h3>操作日志</h3>
        <el-timeline>
          <el-timeline-item
            v-for="(log, index) in order.operation_logs"
            :key="index"
            :timestamp="formatDate(log.created_at)"
            :type="log.operation_type === 'create' ? 'primary' : 'success'"
          >
            {{ log.operation_type === 'create' ? '创建订单' :
               log.operation_type === 'update' ? '更新订单' :
               log.operation_type === 'payment' ? '支付尾款' : log.operation_type }}
            <p class="log-note">{{ log.note || '无备注' }}</p>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-card>

    <el-empty v-else description="加载中..." />
  </MainBox>
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
</style>
