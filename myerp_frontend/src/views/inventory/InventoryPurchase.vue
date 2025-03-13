<script setup>
import MainBox from '@/components/MainBox.vue'
import FormDialog from '@/components/FormDialog.vue'
import { ref, reactive, onMounted, watch } from 'vue'
import brandAndCategoryHttp from '@/api/systemHttp'
import inventoryHttp from '@/api/inventoryHttp'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { Check, Plus, Delete, DocumentAdd } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

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

/** 锚定发货品牌 */
const confirmBrand = () => {
  inventories.value = []
  details.length = 0
  inventoryHttp.requestAllInventoryData(filterForm.brand_id).then((result) => {
    if (result.status == 200) {
      selectedInventoryMap.value.clear()
      addButtonVisable.value = true
      if (result.data.length > 0) {
        inventories.value = result.data
        ElMessage.success('请点击右侧绿色按钮开始发货!')
      } else {
        ElMessage.info('当前品牌没有任何商品!')
      }
    } else {
      ElMessage.error('数据请求失败!')
    }
  })
}

/** 点我发货按钮开关 */
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

/** 新增商品 */
let createInventoryFormVisable = ref(false)
let createInventoryFormData = reactive({
  name: '',
  brand_id: 0,
  category_id: 0,
  size: '原版',
  color: '原色',
  cost: 0,
})
const createInventoryForm = ref()
const createInventory = () => {
  if (createInventoryFormData.brand_id < 1) {
    ElMessage.error('必须选择所属品牌!')
    return
  }
  if (createInventoryFormData.category_id < 1) {
    ElMessage.error('必须选择商品分类!')
    return
  }
  if (createInventoryFormData.cost < 0) {
    ElMessage.error('进价不可以为负数!')
    return
  }

  createInventoryForm.value.validate((valid, fields) => {
    if (valid) {
      createInventoryFormData.name = createInventoryFormData.name.toUpperCase()
      inventoryHttp.createInventoryData(createInventoryFormData).then((result) => {
        if (result.status == 201) {
          inventories.value.unshift(result.data)
          ElMessage.success('创建商品成功!')
          details.unshift({
            inventory_id: result.data.id,
            quantity: 1,
          })
          createInventoryFormVisable.value = false
        } else {
          ElMessage.error('创建失败!')
        }
      })
    } else {
      for (let key in fields) {
        ElMessage.error(fields[key][0]['message'])
      }
      return
    }
  })
}

/** 新增商品表单验证规则 */
const InventoryFormRules = reactive({
  name: [
    { required: true, message: '必须填写商品名称!', trigger: 'blur' },
    { min: 2, max: 30, message: '商品名称必须在2~30个字之间', trigger: 'blur' },
  ],
  brand_id: [{ required: true, message: '必须选择所属品牌', trigger: 'change' }],
  category_id: [{ required: true, message: '必须选择所属品牌', trigger: 'change' }],
  size: [{ min: 2, max: 15, message: '规格必须在2~15个字之间!', trigger: 'blur' }],
  color: [{ min: 2, max: 15, message: '颜色必须在2~15个字之间!', trigger: 'blur' }],
  cost: [
    { required: true, message: '必须填写单个进价!', trigger: 'blur' },
    {
      type: 'number',
      message: '进价必须为数值!',
      trigger: ['blur', 'change'],
    },
    {
      pattern: /^\d+(\.\d{1,2})?$/,
      message: '进价最多保留两位小数!',
      trigger: 'blur',
    },
  ],
})

/** 表单开关 */
const openForm = () => {
  createInventoryFormData.name = ''
  createInventoryFormData.brand_id = filterForm.brand_id
  createInventoryFormData.category_id = 0
  createInventoryFormData.size = '原版'
  createInventoryFormData.color = '原色'
  createInventoryFormData.cost = 0
  createInventoryFormVisable.value = true
}

/** 点击发货按钮处理数据 */
let purchaseData = reactive({
  brand_id: 0,
  total_cost: 0,
  details: [],
})
let purchaseDataDetails = ref([])
let confirmDialog = ref(false)

const onPurchase = () => {
  purchaseData.brand_id = filterForm.brand_id
  purchaseData.total_cost = 0
  purchaseData.details = []
  purchaseDataDetails.value = []

  if (details.length < 1) {
    ElMessage.error('你没有发任何货物!')
    return
  }

  const inventoryIds = new Set()
  const duplicateItems = []

  for (let detail of details) {
    if (!detail.inventory_id) {
      ElMessage.error('错误!请删除空行!')
      return
    }
    if (detail.quantity < 1) {
      ElMessage.error('错误!发货数量不能为0!')
      return
    }
    if (inventoryIds.has(detail.inventory_id)) {
      const itemName =
        inventories.value.find((inv) => inv.id === detail.inventory_id)?.full_name || '未知商品'
      duplicateItems.push(itemName)
    } else {
      inventoryIds.add(detail.inventory_id)
    }

    let index = inventories.value.findIndex((inventory) => inventory.id == detail.inventory_id)

    if (inventories.value[index].brand.id != purchaseData.brand_id) {
      ElMessage.error('错误!单次发货必须同一品牌!')
      return
    }

    purchaseData.total_cost += inventories.value[index].cost * detail.quantity

    inventories.value[index].quantity = detail.quantity
    purchaseDataDetails.value.push(inventories.value[index])
  }

  if (duplicateItems.length > 0) {
    ElMessage.error(`禁止重复发货：${duplicateItems.join('、')}`)
    return
  }

  purchaseData.details = details
  confirmDialog.value = true
}

/** 确认发货 */
const confirmPurchase = () => {
  if (purchaseData.brand_id != filterForm.brand_id) {
    ElMessage.error('错误!单次发货必须同一品牌!')
  }

  inventoryHttp.createPurchaseData(purchaseData).then((result) => {
    if (result.status == 201) {
      ElMessage.success(result.data.message)
      router.push({ name: 'inventory_purchase_detail', params: { id: result.data.purchase_id } })
    } else {
      ElMessage.error('请求失败!')
    }
  })
}

/** 禁用重复option */
const selectedInventoryMap = ref(new Map())

const getSelectedIds = () => {
  const ids = new Set()
  for (const id of selectedInventoryMap.value.values()) {
    if (id !== 0) {
      ids.add(id)
    }
  }
  return ids
}

const handleSelectChange = (row, rowIndex, value) => {
  selectedInventoryMap.value.set(rowIndex, value)
}

const getDisabledStatus = (inventoryId, rowIndex) => {
  if (selectedInventoryMap.value.get(rowIndex) === inventoryId) {
    return false
  }
  const selectedIds = getSelectedIds()
  return selectedIds.has(inventoryId)
}
</script>

<template>
  <MainBox title="申请发货">
    <!-- 顶部卡片区域 -->
    <el-card class="brand-select-card" shadow="hover">
      <div class="brand-select-content">
        <div class="brand-select-left">
          <el-form :inline="true">
            <el-form-item label="发货品牌">
              <el-select
                v-model="filterForm.brand_id"
                placeholder="请选择发货品牌"
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
                content="注意!一次性只能发同一品牌的货!确认后不可更改!"
                placement="right"
                effect="light"
                v-if="!addButtonVisable"
              >
                <el-button type="primary" @click="confirmBrand" :icon="Check">
                  确认品牌，开始发货
                </el-button>
              </el-tooltip>
            </el-form-item>
          </el-form>
        </div>
        <div class="brand-select-right" v-if="addButtonVisable">
          <el-tooltip content="点击增加一行数据!" placement="left" effect="light">
            <el-button type="success" @click="addRow" class="add-row-btn" :icon="Plus">
              添加发货商品
            </el-button>
          </el-tooltip>
        </div>
      </div>
    </el-card>

    <!-- 发货明细表格 -->
    <el-card class="detail-table-card" shadow="hover" v-if="addButtonVisable">
      <template #header>
        <div class="card-header">
          <span class="header-title">发货明细</span>
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

        <el-table-column label="发货商品" min-width="300">
          <template #default="{ row, $index }">
            <el-select
              v-model="row.inventory_id"
              @change="(val) => handleSelectChange(row, $index, val)"
              filterable
              placeholder="请选择商品"
              class="product-select"
            >
              <el-option :value="0">
                <div class="new-product-option">
                  <el-button type="success" @click.stop="openForm()" :icon="Plus">
                    首次采购？点击新增商品
                  </el-button>
                </div>
              </el-option>
              <el-option
                v-for="inventory in inventories"
                :key="inventory.id"
                :label="inventory.category.name + '-' + inventory.full_name + (authStore.canViewCost ? ', ￥' + inventory.cost : '')"
                :value="inventory.id"
                :disabled="getDisabledStatus(inventory.id, $index)"
              >
                <div class="product-option">
                  <span class="product-category">{{ inventory.category.name }}</span>
                  <span class="product-name">{{ inventory.full_name }}</span>
                  <span class="product-cost" v-if="authStore.canViewCost">￥{{ inventory.cost }}</span>
                </div>
              </el-option>
            </el-select>
          </template>
        </el-table-column>

        <el-table-column label="发货数量" width="200" align="center">
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
          @click="onPurchase"
          :icon="DocumentAdd"
          :disabled="details.length === 0"
        >
          确认发货
        </el-button>
      </div>
    </el-card>

    <!-- 新增商品对话框 -->
    <FormDialog
      title="新增商品"
      v-model="createInventoryFormVisable"
      @submit="createInventory"
      width="500px"
    >
      <el-form
        ref="createInventoryForm"
        :model="createInventoryFormData"
        :rules="InventoryFormRules"
        label-width="100px"
        class="create-form"
      >
        <el-form-item label="所属品牌" prop="brand_id">
          <el-select
            v-model="createInventoryFormData.brand_id"
            disabled
            class="form-select"
          >
            <el-option label="请选择所属品牌" :value="0" />
            <el-option
              v-for="brand in brands"
              :label="brand.name"
              :value="brand.id"
              :key="brand.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="商品分类" prop="category_id">
          <el-select
            v-model="createInventoryFormData.category_id"
            class="form-select"
          >
            <el-option label="请选择商品分类" :value="0" />
            <el-option
              v-for="category in categories"
              :label="category.name"
              :value="category.id"
              :key="category.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="商品名称" prop="name">
          <el-input v-model="createInventoryFormData.name" />
        </el-form-item>
        <el-form-item label="商品尺寸" prop="size">
          <el-input v-model="createInventoryFormData.size" />
        </el-form-item>
        <el-form-item label="商品颜色" prop="color">
          <el-input v-model="createInventoryFormData.color" />
        </el-form-item>
        <el-form-item label="￥ 进价" prop="cost" v-if="authStore.canViewCost">
          <el-input-number
            v-model="createInventoryFormData.cost"
            :precision="2"
            :step="0.01"
            :min="0"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
    </FormDialog>

    <!-- 确认发货对话框 -->
    <FormDialog
      title="确认发货"
      v-model="confirmDialog"
      @submit="confirmPurchase"
      width="800px"
    >
      <el-form :model="purchaseData" label-width="100px" class="confirm-form">
        <el-form-item label="发货品牌">
          <el-select v-model="purchaseData.brand_id" disabled class="form-select">
            <el-option
              v-for="brand in brands"
              :key="brand.id"
              :value="brand.id"
              :label="brand.name"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="发货成本" v-if="authStore.canViewCost">
          <el-input-number
            v-model="purchaseData.total_cost"
            :precision="2"
            :step="0.01"
            :min="0"
            class="form-select"
            controls-position="right"
          >
            <template #prefix>￥</template>
          </el-input-number>
        </el-form-item>
        <el-form-item label="发货详情">
          <div class="warning-box">
            <el-alert
              title="请仔细核对发货信息，确认后不可更改！"
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
            :data="purchaseDataDetails"
            border
            stripe
            :header-cell-style="{ background: '#f5f7fa' }"
          >
            <el-table-column prop="full_name" label="商品名称" min-width="200" />
            <el-table-column prop="category.name" label="商品分类" width="120" align="center" />
            <el-table-column label="发货金额" width="200" align="right" v-if="authStore.canViewCost">
              <template #default="scope">
                <div class="price-cell">
                  <span class="price-detail">
                    ￥{{ scope.row.cost }} × {{ scope.row.quantity }}
                  </span>
                  <span class="price-total">
                    ￥{{ scope.row.cost * scope.row.quantity }}
                  </span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="发货数量" width="100" align="center" v-if="!authStore.canViewCost">
              <template #default="scope">
                {{ scope.row.quantity }}
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>
      </el-form>
    </FormDialog>
  </MainBox>
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

.new-product-option {
  padding: 5px 0;
  text-align: center;
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

.product-cost {
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

.create-form {
  padding: 20px;
}

.form-select {
  width: 100%;
}

.confirm-form {
  padding: 20px;
}

.warning-box {
  margin-bottom: 15px;
}

.price-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.price-detail {
  color: #606266;
  font-size: 13px;
}

.price-total {
  color: #F56C6C;
  font-weight: 500;
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
