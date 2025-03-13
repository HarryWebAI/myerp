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
    <el-card>
      <template #header>
        <div class="header-box">
          <div>
            <el-form inline>
              <el-form-item label="按品牌">
                <!-- 绑定数据 -->
                <el-select v-model="filterForm.brand_id" style="width: 100px">
                  <el-option :value="0" label="选择品牌" />
                  <el-option
                    v-for="brand in brands"
                    :label="brand.name"
                    :value="brand.id"
                    :key="brand.id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="按分类">
                <!-- 同理 -->
                <el-select v-model="filterForm.category_id" style="width: 100px">
                  <el-option :value="0" label="选择分类" />
                  <el-option
                    v-for="category in categories"
                    :label="category.name"
                    :value="category.id"
                    :key="category.id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="按名称">
                <el-input type="text" v-model="filterForm.name" placeholder="输入名称" />
              </el-form-item>
              <el-form-item>
                <el-tooltip content="点击搜索" placement="bottom" effect="light">
                  <el-button @click="onSearch(true)" round icon="search" />
                </el-tooltip>
                <el-tooltip content="取消搜索" placement="bottom" effect="light">
                  <el-button @click="onSearch(false)" round icon="close" type="info" />
                </el-tooltip>
              </el-form-item>
              <el-form-item v-if="authStore.canViewCost">
                <el-tooltip content="当前库存总成本" placement="bottom" effect="light">
                  <span style="color: red">￥{{ total_cost }}</span>
                </el-tooltip>
              </el-form-item>
            </el-form>
          </div>
          <div>
            <el-button type="success" @click="openForm('create')">新增商品</el-button>
          </div>
        </div>
      </template>

      <el-table :data="inventories">
        <el-table-column prop="full_name" label="名称" fixed />
        <el-table-column label="品牌" width="100">
          <template #default="scope">
            <span>{{ scope.row.brand.name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="分类" width="100">
          <template #default="scope">
            <span>{{ scope.row.category.name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="当前库存" width="80" align="center">
          <template #default="scope">
            <el-tooltip
              :content="'物流在途:' + scope.row.on_road + ',实际在库:' + scope.row.in_stock"
              placement="top"
              effect="light"
            >
              <el-tag type="primary" class="table-tag">{{ scope.row.current_inventory }}</el-tag>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="当前被订" width="80">
          <template #default="scope">
            <el-tag type="success" class="table-tag">{{ scope.row.been_order }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="实际可售" width="80">
          <template #default="scope">
            <el-tooltip content="实际可售小于0时, 说明您该发货了!"  placement="top" effect="light">
            <el-tag
              :type="scope.row.can_be_sold > 10 ? 'warning' :
                    scope.row.can_be_sold < 0 ? 'danger' : 'info'"
              class="table-tag">{{ scope.row.can_be_sold }}</el-tag>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="单个进价" width="130" v-if="authStore.canViewCost">
          <template #default="scope">
            <span>￥</span>
            <span>{{ scope.row.cost }}</span>
          </template>
        </el-table-column>
        <el-table-column label="库存成本" width="120" v-if="authStore.canViewCost">
          <template #default="scope">
            <span>￥</span>
            <span>{{ scope.row.total_cost }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" align="center">
          <template #default="scope">
            <el-button type="primary" @click="openForm('update', scope.row)">
              <el-icon><EditPen /></el-icon>
              <span>修改信息</span>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <PaginationView
          v-model="pagination.page"
          :page_size="10"
          :total="pagination.total"
        ></PaginationView>
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
        <el-select v-model="createInventoryFormData.brand_id">
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
        <el-select v-model="createInventoryFormData.category_id">
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
        <el-input type="number" v-model.number="createInventoryFormData.cost" />
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
        <el-select v-model="updateInventoryFormData.brand_id">
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
        <el-select v-model="updateInventoryFormData.category_id">
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
        <el-input type="number" v-model.number="updateInventoryFormData.cost" />
      </el-form-item>
    </el-form>
  </FormDialog>
</template>

<style scoped>
.header-box {
  display: flex;
  justify-content: space-between;
}
.table-tag {
  width: 50px;
}
</style>
