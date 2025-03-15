<script setup>
import MainBox from '@/components/MainBox.vue'
import FormDialog from '@/components/FormDialog.vue'
import PaginationView from '@/components/PaginationView.vue'
import { onMounted, reactive, ref, watch } from 'vue'
import brandAndCategoryHttp from '@/api/systemHttp'
import { ElMessage } from 'element-plus'
import inventoryHttp from '@/api/inventoryHttp'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

/**筛选器 */
let filterForm = reactive({
  brand_id: 0,
  category_id: 0,
  name: '',
})

/**分页器 */
let pagination = reactive({
  page: 1,
  total: 0,
})

/** 获取数据 */
let brands = ref([])
let categories = ref([])
let inventories = ref([])
let total_cost = ref(0)

const getInventories = (page, params) => {
  inventoryHttp.requestInventoryData(page, params).then((result) => {
    if (result.status == 200) {
      inventories.value = result.data.results
      pagination.total = result.data.count
      total_cost.value = result.data.total_cost
    } else {
      ElMessage.error('请求数据失败!')
    }
  })
}

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

  getInventories(1, filterForm)
})

/**切换页码 */
watch(
  () => pagination.page,
  () => {
    getInventories(pagination.page, filterForm)
  },
)

/**新增商品 */
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

/**修改商品 */
let updateInventoryFormVisable = ref(false)
let updateInventoryFormData = reactive({
  id: 0,
  name: '',
  brand_id: 0,
  category_id: 0,
  size: '',
  color: '',
  cost: 0,
})
const updateInventoryForm = ref()
const updateInventory = () => {
  if (updateInventoryFormData.brand_id < 1) {
    ElMessage.error('必须选择所属品牌!')
    return
  }
  if (updateInventoryFormData.category_id < 1) {
    ElMessage.error('必须选择商品分类!')
    return
  }
  if (updateInventoryFormData.cost < 0) {
    ElMessage.error('进价不可以为负数!')
    return
  }

  updateInventoryForm.value.validate((valid, fields) => {
    if (valid) {
      updateInventoryFormData.name = updateInventoryFormData.name.toUpperCase()
      inventoryHttp.updateInventoryData(updateInventoryFormData).then((result) => {
        if (result.status == 200) {
          let index = inventories.value.findIndex((inventory) => inventory.id === result.data.id)
          inventories.value.splice(index, 1, result.data)
          ElMessage.success('编辑商品成功!')
          updateInventoryFormVisable.value = false
        } else {
          ElMessage.error('编辑失败!')
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

/**表单规则 */
const InventoryFormRules = reactive({
  name: [
    { required: true, message: '必须填写商品名称!', trigger: 'blur' },
    { min: 2, max: 30, message: '商品名称必须在2~30个字之间!', trigger: 'blur' },
  ],
  brand_id: [{ required: true, message: '必须选择所属品牌!', trigger: 'change' }],
  category_id: [{ required: true, message: '必须选择所属品牌!', trigger: 'change' }],
  size: [
    { required: true, message: '必须选择所规格!', trigger: 'change' },
    { min: 2, max: 15, message: '规格必须在2~15个字之间!', trigger: 'blur' },
  ],
  color: [
    { required: true, message: '必须选择所属颜色!', trigger: 'change' },
    { min: 2, max: 15, message: '颜色必须在2~15个字之间!', trigger: 'blur' },
  ],
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

/**表单开关 */
const openForm = (action, data) => {
  if (action == 'create') {
    createInventoryFormData.name = ''
    createInventoryFormData.brand_id = 0
    createInventoryFormData.category_id = 0
    createInventoryFormData.size = '原版'
    createInventoryFormData.color = '原色'
    createInventoryFormData.cost = 0
    createInventoryFormVisable.value = true
  } else if (action == 'update') {
    Object.assign(updateInventoryFormData, data)
    updateInventoryFormData.brand_id = data.brand.id
    updateInventoryFormData.category_id = data.category.id
    updateInventoryFormData.cost = Number(updateInventoryFormData.cost)
    updateInventoryFormVisable.value = true
  }
}

/**实现筛选功能 */
const onSearch = (action) => {
  if (action) {
    filterForm.name = filterForm.name.toUpperCase()
    getInventories(1, filterForm)
  } else {
    filterForm.brand_id = 0
    filterForm.category_id = 0
    filterForm.name = ''
    getInventories(1, filterForm)
  }
}
</script>

<template>
  <MainBox title="库存列表">
    <el-card class="inventory-list-card">
      <template #header>
        <div class="dashboard-header">
          <!-- 统计数据部分 -->
          <div class="summary-dashboard" v-if="authStore.canViewCost">
            <div class="summary-item">
              <el-icon class="summary-icon" :class="[
                total_cost > 100000 ? 'high-cost' :
                total_cost < 10000 ? 'low-cost' : 'normal-cost'
              ]"><Money /></el-icon>
              <div class="summary-content">
                <span class="summary-label">库存总成本</span>
                <span class="summary-value" :class="[
                  total_cost > 100000 ? 'high-cost-text' :
                  total_cost < 10000 ? 'low-cost-text' : 'normal-cost-text'
                ]">￥{{ total_cost }}</span>
              </div>
            </div>
          </div>

          <!-- 筛选部分 -->
          <div class="filter-section">
            <div class="filter-row">
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

              <el-select v-model="filterForm.category_id" placeholder="选择分类" clearable class="filter-item">
                <template #prefix>
                  <el-icon><Folder /></el-icon>
                </template>
                <el-option :value="0" label="全部分类" />
                <el-option
                  v-for="category in categories"
                  :label="category.name"
                  :value="category.id"
                  :key="category.id"
                />
              </el-select>

              <el-input
                v-model="filterForm.name"
                placeholder="商品名称"
                clearable
                class="filter-item"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>

            <div class="filter-actions">
              <el-button type="primary" @click="onSearch(true)" icon="Search">搜索</el-button>
              <el-button @click="onSearch(false)" icon="RefreshRight">重置</el-button>
              <el-button type="success" @click="openForm('create')" icon="Plus">新增商品</el-button>
            </div>
          </div>
        </div>
      </template>

      <el-table :data="inventories" class="inventory-table" :header-cell-style="{ background: '#f5f7fa' }">
        <el-table-column prop="full_name" label="名称" fixed min-width="200" />
        <el-table-column label="品牌" width="100">
          <template #default="scope">
            <el-tag size="small" type="info">{{ scope.row.brand.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="分类" width="100">
          <template #default="scope">
            <el-tag size="small" type="success">{{ scope.row.category.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="当前库存" width="100" align="center">
          <template #default="scope">
            <el-tooltip
              :content="'物流在途:' + scope.row.on_road + ',实际在库:' + scope.row.in_stock"
              placement="top"
              effect="light"
            >
              <el-tag type="primary" class="inventory-tag">{{ scope.row.current_inventory }}</el-tag>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="当前被订" width="100" align="center">
          <template #default="scope">
            <el-tag type="success" class="inventory-tag">{{ scope.row.been_order }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="实际可售" width="100" align="center">
          <template #default="scope">
            <el-tooltip content="实际可售小于0时, 说明您该发货了!"  placement="top" effect="light">
              <el-tag
                :type="scope.row.can_be_sold > 10 ? 'warning' :
                      scope.row.can_be_sold < 0 ? 'danger' : 'info'"
                class="inventory-tag">{{ scope.row.can_be_sold }}</el-tag>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="单个进价" width="130" v-if="authStore.canViewCost">
          <template #default="scope">
            <span class="price-value">￥{{ scope.row.cost }}</span>
          </template>
        </el-table-column>
        <el-table-column label="库存成本" width="130" v-if="authStore.canViewCost">
          <template #default="scope">
            <span class="price-value total-price">￥{{ scope.row.total_cost }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" align="center" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="openForm('update', scope.row)" class="action-button">
              <el-icon><EditPen /></el-icon>
              <span>修改信息</span>
            </el-button>
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

  <!-- 新增商品 -->
  <FormDialog title="新增商品" v-model="createInventoryFormVisable" @submit="createInventory">
    <el-form
      ref="createInventoryForm"
      :model="createInventoryFormData"
      :rules="InventoryFormRules"
      :label-width="80"
    >
      <el-form-item label="所属品牌" prop="brand_id">
        <el-select v-model="createInventoryFormData.brand_id" class="form-select">
          <el-option label="请选择所属品牌" :value="0"></el-option>
          <el-option
            v-for="brand in brands"
            :label="brand.name"
            :value="brand.id"
            :key="brand.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="商品分类" prop="category_id">
        <el-select v-model="createInventoryFormData.category_id" class="form-select">
          <el-option label="请选择商品分类" :value="0"></el-option>
          <el-option
            v-for="category in categories"
            :label="category.name"
            :value="category.id"
            :key="category.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="商品名称" prop="name">
        <el-input type="text" v-model="createInventoryFormData.name" />
      </el-form-item>
      <el-form-item label="商品尺寸" prop="size">
        <el-input type="text" v-model="createInventoryFormData.size" />
      </el-form-item>
      <el-form-item label="商品颜色" prop="color">
        <el-input type="text" v-model="createInventoryFormData.color" />
      </el-form-item>
      <el-form-item label="￥ 进价" prop="cost" v-if="authStore.canViewCost">
        <el-input-number
          v-model.number="createInventoryFormData.cost"
          :precision="2"
          :step="0.01"
          :min="0"
          style="width: 100%"
        />
      </el-form-item>
    </el-form>
  </FormDialog>

  <!-- 编辑表单 -->
  <FormDialog title="编辑商品" v-model="updateInventoryFormVisable" @submit="updateInventory">
    <el-form
      ref="updateInventoryForm"
      :model="updateInventoryFormData"
      :rules="InventoryFormRules"
      :label-width="80"
    >
      <el-form-item label="所属品牌" prop="brand_id">
        <el-select v-model="updateInventoryFormData.brand_id" class="form-select">
          <el-option label="请选择所属品牌" :value="0"></el-option>
          <el-option
            v-for="brand in brands"
            :label="brand.name"
            :value="brand.id"
            :key="brand.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="商品分类" prop="category_id">
        <el-select v-model="updateInventoryFormData.category_id" class="form-select">
          <el-option label="请选择商品分类" :value="0"></el-option>
          <el-option
            v-for="category in categories"
            :label="category.name"
            :value="category.id"
            :key="category.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="商品名称" prop="name">
        <el-input type="text" v-model="updateInventoryFormData.name" />
      </el-form-item>
      <el-form-item label="商品尺寸" prop="size">
        <el-input type="text" v-model="updateInventoryFormData.size" />
      </el-form-item>
      <el-form-item label="商品颜色" prop="color">
        <el-input type="text" v-model="updateInventoryFormData.color" />
      </el-form-item>
      <el-form-item label="￥ 进价" prop="cost" v-if="authStore.canViewCost">
        <el-input-number
          v-model.number="updateInventoryFormData.cost"
          :precision="2"
          :step="0.01"
          :min="0"
          style="width: 100%"
        />
      </el-form-item>
    </el-form>
  </FormDialog>
</template>

<style scoped>
/* 主卡片样式 */
.inventory-list-card {
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

.high-cost {
  background: #fde2e2;
  color: #F56C6C;
}

.normal-cost {
  background: #e7f6e9;
  color: #67C23A;
}

.low-cost {
  background: #f4f4f5;
  color: #909399;
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

.high-cost-text { color: #F56C6C; }
.normal-cost-text { color: #67C23A; }
.low-cost-text { color: #909399; }

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

/* 表格样式 */
.inventory-table {
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

.inventory-tag {
  width: 50px;
  font-weight: 500;
}

.price-value {
  color: #F56C6C;
  font-weight: 500;
}

.total-price {
  font-weight: bold;
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

/* 表单样式 */
.form-select {
  width: 100%;
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
</style>
