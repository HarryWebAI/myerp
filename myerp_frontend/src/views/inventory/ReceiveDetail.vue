<script setup>
import MainBox from '@/components/MainBox.vue'
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import inventoryHttp from '@/api/inventoryHttp'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const receive_id = route.params.id
let details = ref([])

// 添加编辑相关的响应式变量
const editDialogVisible = ref(false)
const editingDetail = ref(null)
const newQuantity = ref(0)

// 加载数据的方法
const loadData = () => {
  inventoryHttp.requestReceiveDetails(receive_id).then((result) => {
    if (result.status == 200) {
      details.value = result.data
    } else {
      ElMessage.error('数据请求失败!')
    }
  })
}

onMounted(() => {
  loadData()
})

// 打开编辑对话框
const handleEdit = (row) => {
  editingDetail.value = row
  newQuantity.value = row.quantity
  editDialogVisible.value = true
}

// 保存修改
const handleSave = () => {
  if (newQuantity.value < 0 || !Number.isInteger(Number(newQuantity.value))) {
    ElMessage.warning('请输入有效的数量')
    return
  }

  // 如果数量为0，调用删除接口
  if (newQuantity.value === 0) {
    ElMessageBox.confirm(
      `确认删除商品 "${editingDetail.value.inventory_name}" 的收货记录？`,
      '删除确认',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    ).then(() => {
      inventoryHttp.deleteReceiveDetail(editingDetail.value.id)
        .then(response => {
          if (response.status === 200) {
            ElMessage.success('收货记录删除成功')
            editDialogVisible.value = false
            // 检查返回数据中的order_deleted字段
            const orderDeleted = response.data && response.data.order_deleted
            if (orderDeleted) {
              ElMessage.info('收货单已被删除，即将返回列表页面')
              router.push({name:'inventory_receive_list'})
            } else {
              loadData() // 重新加载数据
            }
          } else {
            ElMessage.error(response.data?.detail || '删除失败')
          }
        }).catch(error => {
          ElMessage.error(error.response?.data?.detail || '删除失败')
        })
    }).catch(() => {
      // 用户取消操作
    })
    return
  }

  // 数量大于0时的原有逻辑
  inventoryHttp.updateReceiveDetail(editingDetail.value.id, {
    quantity: newQuantity.value
  }).then(response => {
    if (response.status === 200) {
      ElMessage.success('修改成功')
      editDialogVisible.value = false
      loadData() // 重新加载数据
    } else {
      ElMessage.error(response.data.detail || '修改失败')
    }
  }).catch(error => {
    ElMessage.error(error.response?.data?.detail || '修改失败')
  })
}
</script>

<template>
  <MainBox title="收货详情">
    <el-card>
      <el-table :data="details">
        <el-table-column prop="inventory_name" label="名称"></el-table-column>
        <el-table-column prop="category_name" label="种类"></el-table-column>
        <el-table-column prop="quantity" label="收货数量"></el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="handleEdit(scope.row)"
            >
              修改数量
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="修改收货数量"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form label-width="120px" class="custom-form">
        <el-form-item label="商品名称：" class="custom-label">
          {{ editingDetail?.inventory_name }}
        </el-form-item>
        <el-form-item label="原收货数量：" class="custom-label">
          {{ editingDetail?.quantity }}
        </el-form-item>
        <el-form-item label="修改后数量：" class="custom-label">
          <el-input-number
            v-model="newQuantity"
            :min="0"
            controls-position="right"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSave">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </MainBox>
</template>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.custom-form :deep(.custom-label) .el-form-item__label {
  font-weight: bold;
  font-size: 15px;
  color: #2c3e50;
}

.custom-form :deep(.el-form-item__label)::after {
  content: ' ';
}
</style>
