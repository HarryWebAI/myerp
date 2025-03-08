<script setup>
import MainBox from '@/components/MainBox.vue'
import FormDialog from '@/components/FormDialog.vue'
import { ref, reactive, onMounted, watch } from 'vue'
import brandAndCategoryHttp from '@/api/brandAndCategoryHttp'
import inventoryHttp from '@/api/inventoryHttp'
import { ElMessage } from 'element-plus'

/** 品牌筛选 */
let filterForm = reactive({
  brand_id: 0,
})
let inventories = ref([])
watch(
  () => filterForm.brand_id,
  (brand_id) => {
    inventories.value = []
    details.length = 0
    inventoryHttp.requestAllInventoryData(brand_id).then((result) => {
      if (result.status == 200) {
        if (result.data.length > 0) {
          inventories.value = result.data
          ElMessage.success('请点击右侧"+"号开始发货!')
        } else {
          ElMessage.info('当前品牌没有任何商品!')
        }
      } else {
        ElMessage.error('数据请求失败!')
      }
    })
  },
)

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
  if (createInventoryFormData.cost < 0) {
    ElMessage.error('进价不可以为复数!')
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

/** 发货 */
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

  for (const detail of details) {
    if (!detail.inventory_id) {
      ElMessage.error('错误!请删除空行!')
      return
    }
    if (detail.quantity < 1) {
      ElMessage.error('错误!发货数量不能为0!')
      return
    }

    let index = inventories.value.findIndex((inventory) => inventory.id == detail.inventory_id)

    if (inventories.value[index].brand.id != purchaseData.brand_id) {
      ElMessage.error('错误!单次发货必须同一品牌!')
      return
    }

    purchaseData.total_cost += inventories.value[index].cost * detail.quantity
    let item = inventories.value[index]
    item.quantity = detail.quantity

    purchaseDataDetails.value.push(item)
  }

  purchaseData.details = details

  confirmDialog.value = true
}

/** 确认发货 */
const confirmPurchase = () => {
  if (purchaseData.brand_id != filterForm.brand_id) {
    ElMessage.error('错误!单次发货必须同一品牌!')
  }
  console.log(purchaseData)
}
</script>

<template>
  <MainBox title="申请发货">
    <div class="table-header">
      <!-- 锚定发货品牌 -->
      <div>
        <el-form inline>
          <el-form-item label="发货品牌">
            <el-select v-model="filterForm.brand_id" style="width: 150px">
              <el-option :value="0" label="请先选择品牌..." />
              <el-option
                v-for="brand in brands"
                :key="brand.id"
                :value="brand.id"
                :label="brand.name"
              ></el-option>
            </el-select>
          </el-form-item>
        </el-form>
      </div>

      <!-- "增加一行"按钮 -->
      <div>
        <el-tooltip
          v-if="inventories.length > 0"
          content="点击增加新发货!"
          placement="left"
          effect="light"
        >
          <el-button @click="addRow"> + </el-button>
        </el-tooltip>
      </div>
    </div>

    <el-table :data="details" border style="width: 100%">
      <el-table-column label="序号" width="80" type="index" align="center" />

      <el-table-column label="发货商品">
        <template #default="{ row }">
          <el-select v-model="row.inventory_id" placeholder="请选择" @click.stop filterable>
            <el-option :value="0" label="请选择商品">
              <div class="option-container">
                <el-button type="success" @click.stop="openForm()" size="small">
                  <span>新售商品 ? 点击新增 +</span>
                </el-button>
              </div>
            </el-option>
            <el-option
              v-for="inventory in inventories"
              :key="inventory.id"
              :label="inventory.full_name + '￥' + inventory.cost"
              :value="inventory.id"
            />
          </el-select>
        </template>
      </el-table-column>

      <el-table-column label="发货数量" width="120">
        <template #default="{ row }">
          <el-input v-model.number="row.quantity" type="number" />
        </template>
      </el-table-column>

      <el-table-column label="操作" width="160" align="center">
        <template #default="{ $index }">
          <el-button type="danger" @click="deleteRow($index)"> - </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="submit-btn">
      <el-button type="primary" size="large" @click="onPurchase">点击发货</el-button>
    </div>
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
        <el-select v-model="createInventoryFormData.brand_id" disabled>
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
      <el-form-item label="￥ 进价" prop="cost">
        <el-input type="number" v-model.number="createInventoryFormData.cost" />
      </el-form-item>
    </el-form>
  </FormDialog>

  <!-- 确认发货表单 -->
  <FormDialog title="确认发货?" v-model="confirmDialog" @submit="confirmPurchase">
    <el-form :model="purchaseData" label-width="100">
      <el-form-item label="发货品牌:">
        <el-select v-model="purchaseData.brand_id" disabled>
          <el-option
            v-for="brand in brands"
            :key="brand.id"
            :value="brand.id"
            :label="brand.name"
          ></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="发货成本￥">
        <el-input v-model="purchaseData.total_cost"></el-input>
      </el-form-item>
      <el-form-item label="发货详情?">
        <el-table :data="purchaseDataDetails">
          <el-table-column prop="full_name" label="名称" />
          <el-table-column label="价格">
            <template #default="scope">
              <span>
                ￥{{ scope.row.cost }} × {{ scope.row.quantity }} =
                {{ scope.row.cost * scope.row.quantity }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </el-form-item>
    </el-form>
  </FormDialog>
</template>

<style scoped>
.table-header {
  display: flex;
  justify-content: space-between;
}

.option-container {
  text-align: center;
}

.submit-btn {
  text-align: center;
  margin-top: 10px;
}
</style>
