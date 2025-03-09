<script setup>
import MainBox from '@/components/MainBox.vue'
import FormDialog from '@/components/FormDialog.vue'
import { ref, reactive, onMounted, watch } from 'vue'
import brandAndCategoryHttp from '@/api/brandAndCategoryHttp'
import inventoryHttp from '@/api/inventoryHttp'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

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

/** 锚定发货品牌 */
const confirmBrand = () => {
  inventories.value = []
  details.length = 0
  inventoryHttp.requestAllInventoryData(filterForm.brand_id).then((result) => {
    if (result.status == 200) {
      selectedInventoryIds.value.clear()
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
// 最终提交的数据
let purchaseData = reactive({
  brand_id: 0,
  total_cost: 0,
  details: [],
})
// 提交表单展示的发货详情
let purchaseDataDetails = ref([])
// 提交表单的开关
let confirmDialog = ref(false)
// 开始验证和处理数据
const onPurchase = () => {
  purchaseData.brand_id = filterForm.brand_id
  purchaseData.total_cost = 0
  purchaseData.details = []
  purchaseDataDetails.value = []

  if (details.length < 1) {
    ElMessage.error('你没有发任何货物!')
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
    // 验证发货数量
    if (detail.quantity < 1) {
      ElMessage.error('错误!发货数量不能为0!')
      return
    }
    // 验证是否重复发同一货物
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
    if (inventories.value[index].brand.id != purchaseData.brand_id) {
      ElMessage.error('错误!单次发货必须同一品牌!')
      return
    }

    // 计算总价
    purchaseData.total_cost += inventories.value[index].cost * detail.quantity

    // 配置提交表单展示的发货详情
    inventories.value[index].quantity = detail.quantity
    purchaseDataDetails.value.push(inventories.value[index])
  }

  // 验证货物是否重复
  if (duplicateItems.length > 0) {
    ElMessage.error(`禁止重复发货：${duplicateItems.join('、')}`)
    return
  }

  // 配置提交详情
  purchaseData.details = details

  // 打开表单
  confirmDialog.value = true
}

/** 确认发货 */
const confirmPurchase = () => {
  if (purchaseData.brand_id != filterForm.brand_id) {
    ElMessage.error('错误!单次发货必须同一品牌!')
  }

  inventoryHttp.createPurchaseData(purchaseData).then((result) => {
    if (result.status == 201) {
      console.log(result.data)
      ElMessage.success(result.data.message)
      router.push({ name: 'inventory_purchase_detail', params: { id: result.data.purchase_id } })
    } else {
      ElMessage.error('请求失败!')
    }
  })
}

/** 禁用重复option */
// 新增响应式变量记录已选商品ID
const selectedInventoryIds = ref(new Set())

// 在每行的select选择事件中更新选中状态
const handleSelectChange = (row, value) => {
  // 移除该行之前选择的ID
  selectedInventoryIds.value.delete(row.inventory_id)

  // 添加新选择的ID
  if (value !== 0) {
    selectedInventoryIds.value.add(value)
  }

  // 更新当前行的选择
  row.inventory_id = value
}

// 生成带禁用状态的选项
const getDisabledStatus = (inventoryId, currentRowId) => {
  return selectedInventoryIds.value.has(inventoryId) && inventoryId !== currentRowId
}
</script>

<template>
  <MainBox title="申请发货">
    <div class="table-header">
      <!-- 锚定发货品牌 -->
      <div>
        <el-form inline>
          <el-form-item label="发货品牌：">
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
          <el-form-item>
            <el-tooltip
              content="注意!一次性只能发同一品牌的货!确认后不可更改!"
              placement="right"
              effect="light"
              v-if="!addButtonVisable"
            >
              <el-button type="primary" @click="confirmBrand">确认品牌, 开始发货</el-button>
            </el-tooltip>
          </el-form-item>
        </el-form>
      </div>

      <!-- "增加一行"按钮 -->
      <div>
        <el-tooltip
          v-if="addButtonVisable"
          content="点击增加一行数据!"
          placement="left"
          effect="light"
        >
          <el-button @click="addRow" type="success" class="add-row-btn">
            <el-icon><CirclePlus /></el-icon>
            <span>点我发货</span>
          </el-button>
        </el-tooltip>
      </div>
    </div>

    <el-table :data="details" border style="width: 100%">
      <el-table-column label="序号" width="80" type="index" align="center" />

      <el-table-column label="发货商品">
        <template #default="{ row }">
          <el-select
            v-model="row.inventory_id"
            @change="(val) => handleSelectChange(row, val)"
            filterable
          >
            <el-option :value="0" label="请选择商品">
              <div class="option-container">
                <el-button type="success" @click.stop="openForm()" size="small">
                  <span>首次采购 ? 点击新增 +</span>
                </el-button>
              </div>
            </el-option>
            <el-option
              v-for="inventory in inventories"
              :key="inventory.id"
              :label="inventory.full_name + '￥' + inventory.cost"
              :value="inventory.id"
              :disabled="getDisabledStatus(inventory.id, row.inventory_id)"
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
    <el-form :model="purchaseData" label-width="80">
      <el-form-item label="发货品牌">
        <el-select v-model="purchaseData.brand_id" disabled>
          <el-option
            v-for="brand in brands"
            :key="brand.id"
            :value="brand.id"
            :label="brand.name"
          ></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="发货成本">
        <el-input v-model="purchaseData.total_cost"></el-input>
      </el-form-item>
      <el-form-item label="发货详情">
        <div class="warning-info">
          <h3>注意!</h3>
          <p><small>请仔细核对发货信息,[确认]后不可更改!</small></p>
          <p><small>如有错误请[返回]修改!</small></p>
        </div>
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

.add-row-btn {
  width: 160px;
}

.option-container {
  text-align: center;
}

.submit-btn {
  text-align: center;
  margin-top: 10px;
}

.warning-info {
  width: 100%;
  text-align: center;
  color: red;
  font-weight: bold;
}
</style>
