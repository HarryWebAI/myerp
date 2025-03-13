<script setup>
import { onMounted, ref, reactive, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import inventoryHttp from '@/api/inventoryHttp'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Refresh, Document, Timer } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const receive_id = route.params.id
const receiveData = ref(null)
const loading = ref(false)
const editVisible = ref(false)
const currentDetail = reactive({
  id: null,
  inventory: {},
  quantity: 0,
  oldQuantity: 0
})

// 计算总数量
const totalQuantity = computed(() => {
  if (!receiveData.value?.details) return 0
  return receiveData.value.details.reduce((sum, item) => sum + item.quantity, 0)
})

// 格式化金额
const formatPrice = (price) => {
  if (!price) return '¥0.00'
  return `¥${Number(price).toFixed(2)}`
}

// 格式化时间
const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

// 获取收货明细数据
const fetchDetails = () => {
  loading.value = true
  inventoryHttp.requestReceiveDetails(receive_id).then((result) => {
    loading.value = false
    if (result.status == 200) {
      receiveData.value = result.data
    } else {
      ElMessage.error('数据请求失败!')
    }
  }).catch(() => {
    loading.value = false
    ElMessage.error('数据请求失败!')
  })
}

// 返回列表页
const goBack = () => {
  router.push({ name: 'inventory_receive_list' })
}

// 打开编辑对话框
const handleEdit = (row) => {
  currentDetail.id = row.id
  currentDetail.inventory = row.inventory
  currentDetail.oldQuantity = row.quantity
  currentDetail.quantity = row.quantity
  editVisible.value = true
}

// 提交数量修改
const handleSubmitEdit = () => {
  if (currentDetail.quantity === currentDetail.oldQuantity) {
    ElMessage.warning('数量未变更!')
    return
  }

  if (currentDetail.quantity < 0) {
    ElMessage.warning('数量不能为负数!')
    return
  }

  inventoryHttp
    .updateReceiveDetail(currentDetail.id, {
      quantity: currentDetail.quantity,
    })
    .then((result) => {
      if (result.status == 200) {
        ElMessage.success('修改成功!')
        editVisible.value = false
        fetchDetails()
      } else {
        ElMessage.error(result.data.detail || '修改失败!')
      }
    })
}

// 删除明细
const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该明细吗?', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    inventoryHttp.deleteReceiveDetail(row.id).then((result) => {
      if (result.status == 200) {
        ElMessage.success('删除成功!')
        if (result.data.order_deleted) {
          router.push({ name: 'inventory_receive_list' })
        } else {
          fetchDetails()
        }
      } else {
        ElMessage.error(result.data.detail || '删除失败!')
      }
    })
  })
}

onMounted(() => {
  fetchDetails()
})
</script>

<template>
  <div class="receive-detail" v-loading="loading">
    <!-- 顶部导航栏 -->
    <div class="nav-bar">
      <div class="left">
        <el-button @click="goBack" :icon="ArrowLeft" plain>返回列表</el-button>
      </div>
      <div class="center">
        <h2>收货单详情</h2>
      </div>
      <div class="right">
        <el-button @click="fetchDetails" :icon="Refresh" plain>刷新</el-button>
      </div>
    </div>

    <div class="content" v-if="receiveData">
      <!-- 基本信息卡片 -->
      <div class="info-card">
        <div class="info-header">
          <el-tag size="large" type="primary">收货单号：{{ receiveData.id }}</el-tag>
          <el-tag size="large" type="success">{{ receiveData.brand?.name }}</el-tag>
        </div>
        <div class="info-body">
          <div class="info-item">
            <i class="el-icon"><Document /></i>
            <span class="label">收货人：</span>
            <span class="value">{{ receiveData.user?.name }}</span>
          </div>
          <div class="info-item">
            <i class="el-icon"><Timer /></i>
            <span class="label">收货时间：</span>
            <span class="value">{{ formatTime(receiveData.create_time) }}</span>
          </div>
        </div>
        <div class="info-footer">
          <div class="summary-item">
            <span class="label">收货总量：</span>
            <span class="value highlight">{{ totalQuantity }}件</span>
          </div>
        </div>
      </div>

      <!-- 收货明细表格 -->
      <div class="detail-card">
        <div class="card-title">收货明细</div>
        <el-table :data="receiveData.details" border stripe>
          <el-table-column type="index" label="序号" width="60" align="center" />
          <el-table-column label="商品信息" min-width="300">
            <template #default="scope">
              <div class="product-info">
                <div class="product-name">{{ scope.row.inventory.name }}</div>
                <div class="product-spec">
                  <el-tag size="small">{{ scope.row.inventory.size }}</el-tag>
                  <el-tag size="small" type="info">{{ scope.row.inventory.color }}</el-tag>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="数量" prop="quantity" width="100" align="center">
            <template #default="scope">
              <span class="quantity">{{ scope.row.quantity }}</span>
            </template>
          </el-table-column>
          <el-table-column label="单价" width="120" align="right">
            <template #default="scope">
              <span class="price">{{ formatPrice(scope.row.inventory.cost) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="小计" width="120" align="right">
            <template #default="scope">
              <span class="total-price">{{ formatPrice(scope.row.inventory.cost * scope.row.quantity) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="scope">
              <el-button-group>
                <el-button type="primary" size="small" @click="handleEdit(scope.row)">
                  修改
                </el-button>
                <el-button type="danger" size="small" @click="handleDelete(scope.row)">
                  删除
                </el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 操作日志 -->
      <div class="log-card">
        <div class="card-title">操作日志</div>
        <el-timeline>
          <el-timeline-item
            v-for="log in receiveData.logs"
            :key="log.id"
            :timestamp="formatTime(log.create_time)"
            type="primary"
          >
            <div class="log-content">
              <div class="log-header">
                <el-tag size="small">{{ log.operator_name }}</el-tag>
              </div>
              <div class="log-body">
                <pre>{{ log.content }}</pre>
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
      </div>
    </div>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editVisible" title="修改数量" width="400px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="商品名称">
          <div class="dialog-product-info">
            <div class="product-name">{{ currentDetail.inventory.name }}</div>
            <div class="product-spec">
              <el-tag size="small">{{ currentDetail.inventory.size }}</el-tag>
              <el-tag size="small" type="info">{{ currentDetail.inventory.color }}</el-tag>
            </div>
          </div>
        </el-form-item>
        <el-form-item label="单价">
          <span class="price">{{ formatPrice(currentDetail.inventory.cost) }}</span>
        </el-form-item>
        <el-form-item label="原数量">
          <span>{{ currentDetail.oldQuantity }}</span>
        </el-form-item>
        <el-form-item label="新数量">
          <el-input-number
            v-model="currentDetail.quantity"
            :min="0"
            :precision="0"
            :step="1"
            controls-position="right"
          />
        </el-form-item>
        <el-form-item label="变更后小计">
          <span class="total-price">{{ formatPrice(currentDetail.quantity * currentDetail.inventory.cost) }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitEdit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.receive-detail {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding: 0 20px;
  height: 60px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.nav-bar h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-card {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.info-header {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.info-body {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-item .label {
  color: #909399;
}

.info-item .value {
  color: #303133;
  font-weight: 500;
}

.info-footer {
  display: flex;
  justify-content: flex-end;
  gap: 24px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.summary-item .label {
  color: #909399;
}

.summary-item .value.highlight {
  color: #409eff;
  font-size: 18px;
  font-weight: bold;
}

.detail-card, .log-card {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.card-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 20px;
  padding-left: 10px;
  border-left: 4px solid #409eff;
}

.product-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.product-name {
  font-weight: 500;
  color: #303133;
}

.product-spec {
  display: flex;
  gap: 8px;
}

.quantity {
  font-weight: 500;
  color: #303133;
}

.price {
  color: #f56c6c;
  font-weight: 500;
}

.total-price {
  color: #f56c6c;
  font-weight: bold;
}

.log-content {
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.log-header {
  margin-bottom: 8px;
}

.log-body pre {
  margin: 0;
  white-space: pre-wrap;
  font-family: inherit;
  color: #606266;
  font-size: 13px;
  line-height: 1.5;
}

.dialog-product-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

:deep(.el-timeline-item__timestamp) {
  color: #909399;
  font-size: 13px;
}

:deep(.el-timeline-item__content) {
  color: #303133;
}
</style>
