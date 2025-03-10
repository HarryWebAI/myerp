<script setup>
import MainBox from '@/components/MainBox.vue'
import { onMounted, ref, reactive } from 'vue'
import { useRoute } from 'vue-router'
import inventoryHttp from '@/api/inventoryHttp'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const purchases_id = route.params.id
let details = ref([])
const loading = ref(false)
const editVisible = ref(false)
const currentDetail = reactive({
  id: null,
  inventory: {},
  quantity: 0,
  oldQuantity: 0
})

// 获取采购明细数据
const fetchDetails = () => {
  loading.value = true
  inventoryHttp.requestPurchaseDetails(purchases_id).then((result) => {
    loading.value = false
    if (result.status == 200) {
      details.value = result.data
    } else {
      ElMessage.error('数据请求失败!')
    }
  })
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
const submitEdit = () => {
  // 验证数量是否为非负整数
  if (currentDetail.quantity < 0 || !Number.isInteger(Number(currentDetail.quantity))) {
    ElMessage.warning('采购数量必须为非负整数')
    return
  }

  // 如果数量没有变化，直接关闭对话框
  if (currentDetail.quantity == currentDetail.oldQuantity) {
    editVisible.value = false
    return
  }

  // 如果数量为0，调用删除接口
  if (currentDetail.quantity === 0) {
    ElMessageBox.confirm(
      `确认删除商品 "${currentDetail.inventory.full_name}" 的采购记录？`,
      '删除确认',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    ).then(() => {
      loading.value = true
      inventoryHttp.deletePurchaseDetail(currentDetail.id)
        .then(result => {
          loading.value = false
          if (result.status === 200) {
            ElMessage.success('采购记录删除成功')
            editVisible.value = false
            fetchDetails()
          } else {
            ElMessage.error(result.data.detail || '删除失败，请重试')
          }
        })
        .catch(error => {
          loading.value = false
          ElMessage.error(error.response?.data?.detail || '删除失败，请重试')
        })
    }).catch(() => {
      // 用户取消操作
    })
    return
  }

  // 数量大于0时的原有逻辑
  ElMessageBox.confirm(
    `确认将商品 "${currentDetail.inventory.full_name}" 的采购数量从 ${currentDetail.oldQuantity} 修改为 ${currentDetail.quantity}？`,
    '修改确认',
    {
      confirmButtonText: '确认修改',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    // 发送请求修改数量
    loading.value = true
    inventoryHttp.updatePurchaseDetail(currentDetail.id, { quantity: currentDetail.quantity })
      .then(result => {
        loading.value = false
        if (result.status === 200) {
          ElMessage.success('采购数量修改成功')
          editVisible.value = false
          // 重新获取数据
          fetchDetails()
        } else {
          ElMessage.error(result.data.detail || '修改失败，请重试')
        }
      })
      .catch(error => {
        loading.value = false
        ElMessage.error(error.response?.data?.detail || '修改失败，请重试')
      })
  }).catch(() => {
    // 用户取消操作
  })
}

onMounted(() => {
  fetchDetails()
})
</script>

<template>
  <MainBox title="发货详情">
    <el-card v-loading="loading">
      <div class="operation-bar">
        <el-button @click="fetchDetails" type="primary" :icon="Refresh" size="small">刷新</el-button>
      </div>
      <el-table :data="details">
        <el-table-column prop="inventory.full_name" label="名称"></el-table-column>
        <el-table-column prop="quantity" label="数量"></el-table-column>
        <el-table-column prop="inventory.cost" label="价格"></el-table-column>
        <el-table-column label="总价">
          <template #default="scope">
            {{ scope.row.quantity * scope.row.inventory.cost }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button @click="handleEdit(scope.row)" type="primary" size="small">修改数量</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 修改数量对话框 -->
    <el-dialog
      v-model="editVisible"
      title="修改采购数量"
      width="500px"
    >
      <el-form label-width="120px" class="custom-form">
        <el-form-item label="商品名称：" class="custom-label">
          <span>{{ currentDetail.inventory.full_name }}</span>
        </el-form-item>
        <el-form-item label="原发货数量：" class="custom-label">
          <span>{{ currentDetail.oldQuantity }}</span>
        </el-form-item>
        <el-form-item label="修改后数量：" class="custom-label">
          <el-input-number
            v-model="currentDetail.quantity"
            :min="1"
            controls-position="right"
          ></el-input-number>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="editVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEdit">确认修改</el-button>
        </div>
      </template>
    </el-dialog>
  </MainBox>
</template>

<style scoped>
.operation-bar {
  margin-bottom: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
