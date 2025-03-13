<script setup>
import MainBox from '@/components/MainBox.vue'
import FormDialog from '@/components/FormDialog.vue'
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import brandAndCategoryHttp from '@/api/systemHttp'
import inventoryHttp from '@/api/inventoryHttp'
import { ElMessage } from 'element-plus'
import { CirclePlus, Delete } from '@element-plus/icons-vue'

const router = useRouter()

/** 获取数据 */
let brands = ref([])
let categories = ref([])

onMounted(() => {
  brandAndCategoryHttp.requesetBrandData().then((reuslt) => {
    if (reuslt.status == 200) {
      brands.value = reuslt.data
    } else {
      ElMessage.error('数据请求失败!')
    }
  })
  brandAndCategoryHttp.requesetCategoryData().then((reuslt) => {
    if (reuslt.status == 200) {
      categories.value = reuslt.data
    } else {
      ElMessage.error('数据请求失败!')
    }
  })
})

/** 品牌筛选 */
let filterForm = reactive({
  brand_id: 0,
})
let inventories = ref([])

/** 锚定收货品牌 */
const confirmBrand = (showMessage = true) => {
  inventories.value = []
  details.length = 0
  inventoryHttp.requestAllInventoryData(filterForm.brand_id).then((result) => {
    if (result.status == 200) {
      selectedInventoryMap.value.clear()
      addButtonVisable.value = true
      // 筛选出有在途数量的商品（on_road > 0）
      const filteredInventories = result.data.filter((item) => item.on_road > 0)
      if (filteredInventories.length > 0) {
        inventories.value = filteredInventories
        if (showMessage) {
          ElMessage({
            message: '请点击右侧蓝色按钮开始收货!',
            type: 'success',
            customClass: 'blue-bg-message',
          })
        }
      } else {
        ElMessage.info('当前品牌没有在途商品!')
      }
    } else {
      ElMessage.error('数据请求失败!')
    }
  })
}

/** 点我收货按钮开关 */
let addButtonVisable = ref(false)

watch(
  () => filterForm.brand_id,
  () => {
    details.length = 0
    addButtonVisable.value = false
  },
)

/** 动态表格 */
let details = reactive([])
const addRow = () => {
  details.push({
    inventory_id: 0,
    quantity: 1,
  })
}
const deleteRow = (index) => {
  details.splice(index, 1)
}

/** 点击收货按钮处理数据 */
// 最终提交的数据
let receiveData = reactive({
  brand_id: 0,
  details: [],
})
// 提交表单展示的收货详情
let receiveDataDetails = ref([])
// 提交表单的开关
let confirmDialog = ref(false)
// 开始验证和处理数据
const onReceive = () => {
  receiveData.brand_id = filterForm.brand_id
  receiveData.details = []
  receiveDataDetails.value = []

  if (details.length < 1) {
    ElMessage.error('你没有收任何货物!')
    return
  }

  const inventoryIds = new Set() // 用于检测重复的集合
  const duplicateItems = [] // 记录重复商品的名称

  for (let detail of details) {
    // 验证空行
    if (!detail.inventory_id) {
      ElMessage.error('错误!请删除空行!')
      return
    }
    // 验证收货数量
    if (detail.quantity < 1) {
      ElMessage.error('错误!收货数量不能为0!')
      return
    }
    // 验证是否重复收同一货物
    if (inventoryIds.has(detail.inventory_id)) {
      const itemName =
        inventories.value.find((inv) => inv.id === detail.inventory_id)?.full_name || '未知商品'
      duplicateItems.push(itemName)
    } else {
      inventoryIds.add(detail.inventory_id)
    }

    // 找到货物在货物列表中的索引
    let index = inventories.value.findIndex((inventory) => inventory.id == detail.inventory_id)

    // 验证货物是否属于当前锚定的品牌
    if (inventories.value[index].brand.id != receiveData.brand_id) {
      ElMessage.error('错误!单次收货必须同一品牌!')
      return
    }

    // 验证收货数量不能超过在途数量
    if (detail.quantity > inventories.value[index].on_road) {
      ElMessage.error(
        `错误!收货数量不能超过在途数量! ${inventories.value[index].full_name} 最多只能收 ${inventories.value[index].on_road} 件`,
      )
      return
    }

    // 配置提交表单展示的收货详情
    inventories.value[index].quantity = detail.quantity
    receiveDataDetails.value.push(inventories.value[index])
  }

  // 验证货物是否重复
  if (duplicateItems.length > 0) {
    ElMessage.error(`禁止重复收货：${duplicateItems.join('、')}`)
    return
  }

  // 配置提交详情
  receiveData.details = details

  // 打开表单
  confirmDialog.value = true
}

/** 确认收货 */
const confirmReceive = () => {
  if (receiveData.brand_id != filterForm.brand_id) {
    ElMessage.error('错误!单次收货必须同一品牌!')
    return
  }

  inventoryHttp
    .createReceiveData(receiveData)
    .then((result) => {
      if (result.status == 201) {
        ElMessage({
          message: result.data.message,
          type: 'success',
          customClass: 'blue-bg-message',
        })
        router.push({ name: 'inventory_receive_detail', params: { id: result.data.receive_id } })
      } else {
        ElMessage.error('请求失败! ' + (result.data?.detail || ''))
      }
    })
    .catch((error) => {
      ElMessage.error('请求错误! ' + (error.response?.data?.detail || error.message || '未知错误'))
    })
}

/** 禁用重复option */
// 使用Map来记录行索引到选择ID的映射，而不是简单的Set
const selectedInventoryMap = ref(new Map())

// 计算已选商品ID集合
const getSelectedIds = () => {
  const ids = new Set()
  for (const id of selectedInventoryMap.value.values()) {
    if (id !== 0) {
      ids.add(id)
    }
  }
  return ids
}

// 在每行的select选择事件中更新选中状态
const handleSelectChange = (row, rowIndex, value) => {
  // 更新该行的选择到映射
  selectedInventoryMap.value.set(rowIndex, value)
}

// 生成带禁用状态的选项
const getDisabledStatus = (inventoryId, rowIndex) => {
  // 如果当前行已经选择了这个ID，不禁用
  if (selectedInventoryMap.value.get(rowIndex) === inventoryId) {
    return false
  }

  // 检查是否有其他行选择了这个ID
  const selectedIds = getSelectedIds()
  return selectedIds.has(inventoryId)
}
</script>

<template>
  <MainBox title="收货入库">
    <!-- 顶部卡片区域 -->
    <el-card class="brand-select-card" shadow="hover">
      <div class="brand-select-content">
        <div class="brand-select-left">
          <el-form :inline="true">
            <el-form-item label="收货品牌">
              <el-select
                v-model="filterForm.brand_id"
                placeholder="请选择收货品牌"
                class="brand-select"
                :disabled="addButtonVisable"
              >
                <el-option :value="0" label="请先选择品牌..." />
                <el-option
                  v-for="brand in brands"
                  :key="brand.id"
                  :value="brand.id"
                  :label="brand.name"
                />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-tooltip
                content="注意!一次性只能收同一品牌的货!确认后不可更改!"
                placement="right"
                effect="light"
                v-if="!addButtonVisable"
              >
                <el-button type="primary" @click="confirmBrand">
                  确认品牌，开始收货
                </el-button>
              </el-tooltip>
            </el-form-item>
          </el-form>
        </div>
        <div class="brand-select-right" v-if="addButtonVisable">
          <el-tooltip content="点击增加一行数据!" placement="left" effect="light">
            <el-button type="success" @click="addRow" class="add-row-btn">
              <el-icon><CirclePlus /></el-icon>
              添加收货商品
            </el-button>
          </el-tooltip>
        </div>
      </div>
    </el-card>

    <!-- 收货明细表格 -->
    <el-card class="detail-table-card" shadow="hover" v-if="addButtonVisable">
      <template #header>
        <div class="card-header">
          <span class="header-title">收货明细</span>
          <el-tag type="info" effect="plain">
            已添加 {{ details.length }} 个商品
          </el-tag>
        </div>
      </template>

      <el-table
        :data="details"
        border
        stripe
        style="width: 100%"
        :header-cell-style="{ background: '#f5f7fa' }"
      >
        <el-table-column label="序号" width="80" type="index" align="center" />

        <el-table-column label="收货商品" min-width="300">
          <template #default="{ row, $index }">
            <el-select
              v-model="row.inventory_id"
              @change="(val) => handleSelectChange(row, $index, val)"
              filterable
              placeholder="请选择商品"
              class="product-select"
            >
              <el-option :value="0" label="请选择商品" />
              <el-option
                v-for="inventory in inventories"
                :key="inventory.id"
                :label="
                  inventory.category.name + '-' + inventory.full_name + ', 在途: ' + inventory.on_road
                "
                :value="inventory.id"
                :disabled="getDisabledStatus(inventory.id, $index)"
              >
                <div class="product-option">
                  <span class="product-category">{{ inventory.category.name }}</span>
                  <span class="product-name">{{ inventory.full_name }}</span>
                  <span class="product-on-road">在途: {{ inventory.on_road }}</span>
                </div>
              </el-option>
            </el-select>
          </template>
        </el-table-column>

        <el-table-column label="收货数量" width="200" align="center">
          <template #default="{ row }">
            <el-input-number
              v-model="row.quantity"
              :min="1"
              controls-position="right"
              class="quantity-input"
            />
          </template>
        </el-table-column>

        <el-table-column label="操作" width="120" align="center" fixed="right">
          <template #default="{ $index }">
            <el-button
              type="danger"
              circle
              :icon="Delete"
              @click="deleteRow($index)"
            />
          </template>
        </el-table-column>
      </el-table>

      <!-- 提交按钮 -->
      <div class="submit-area">
        <el-button
          type="primary"
          size="large"
          @click="onReceive"
          :disabled="details.length === 0"
        >
          确认收货
        </el-button>
      </div>
    </el-card>
  </MainBox>

  <!-- 确认收货对话框 -->
  <FormDialog
    title="确认收货"
    v-model="confirmDialog"
    @submit="confirmReceive"
    width="800px"
  >
    <el-form :model="receiveData" label-width="100px" class="confirm-form">
      <el-form-item label="收货品牌">
        <el-select v-model="receiveData.brand_id" disabled class="form-select">
          <el-option
            v-for="brand in brands"
            :key="brand.id"
            :value="brand.id"
            :label="brand.name"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="收货详情">
        <div class="warning-box">
          <el-alert
            title="请仔细核对收货信息，确认后不可更改！"
            type="warning"
            :closable="false"
            show-icon
          >
            <template #default>
              如有错误请返回修改
            </template>
          </el-alert>
        </div>
        <el-table
          :data="receiveDataDetails"
          border
          stripe
          :header-cell-style="{ background: '#f5f7fa' }"
        >
          <el-table-column prop="full_name" label="商品名称" min-width="200" />
          <el-table-column prop="category.name" label="商品分类" width="120" align="center" />
          <el-table-column label="收货数量" width="200" align="right">
            <template #default="scope">
              <div class="quantity-cell">
                <span class="quantity-detail">
                  在途: {{ scope.row.on_road }}
                </span>
                <span class="quantity-total">
                  收货: {{ scope.row.quantity }}
                </span>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-form-item>
    </el-form>
  </FormDialog>
</template>

<style scoped>
.brand-select-card {
  margin-bottom: 20px;
}

.brand-select-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand-select {
  width: 200px;
}

.detail-table-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 16px;
  font-weight: 500;
}

.product-select {
  width: 100%;
}

.product-option {
  display: flex;
  align-items: center;
  gap: 12px;
}

.product-category {
  color: #409EFF;
  font-weight: 500;
}

.product-name {
  flex: 1;
}

.product-on-road {
  color: #F56C6C;
  font-weight: 500;
}

.quantity-input {
  width: 130px;
}

.submit-area {
  margin-top: 20px;
  text-align: center;
}

.confirm-form {
  padding: 20px;
}

.form-select {
  width: 100%;
}

.warning-box {
  margin-bottom: 15px;
}

.quantity-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.quantity-detail {
  color: #606266;
  font-size: 13px;
}

.quantity-total {
  color: #F56C6C;
  font-weight: 500;
}

.add-row-btn {
  width: 160px;
}

:deep(.el-card__header) {
  padding: 15px 20px;
  border-bottom: 1px solid #EBEEF5;
}

:deep(.el-form--inline .el-form-item) {
  margin-right: 20px;
}

:deep(.el-input-number .el-input__wrapper) {
  padding-left: 11px;
  padding-right: 11px;
}

:deep(.el-select-dropdown__item) {
  padding: 0 15px;
}
</style>

<style>
/** 自定义Elmessage */
.blue-bg-message {
  background-color: #409eff !important;
  border-color: #409eff !important;
}

.blue-bg-message .el-message__icon,
.blue-bg-message .el-message__content {
  color: #fff !important;
}
</style>
