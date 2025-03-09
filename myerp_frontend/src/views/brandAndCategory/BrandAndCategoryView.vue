<script setup>
import MainBox from '@/components/MainBox.vue'
import FormDialog from '@/components/FormDialog.vue'
import brandAndCategoryHttp from '@/api/brandAndCategoryHttp'
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

/**获取数据 */
let brands = ref([])
let categories = ref([])

onMounted(() => {
  let brands_result = brandAndCategoryHttp.requesetBrandData()
  let categories_result = brandAndCategoryHttp.requesetCategoryData()
  brands_result.then((result) => {
    if (result.status == 200) {
      brands.value = result.data
    } else {
      ElMessage.error('请求数据失败!')
    }
  })
  categories_result.then((result) => {
    if (result.status == 200) {
      categories.value = result.data
    } else {
      ElMessage.error('请求数据失败!')
    }
  })
})

/**品牌表单 */
let brandFormVisable = ref(false)
let brandFormData = reactive({
  id: 0,
  name: '',
  intro: '',
})
const brandForm = ref()
const brandFormRules = reactive({
  name: [
    { required: true, message: '必须填写品牌名称!', trigger: 'blue' },
    { min: 2, max: 10, message: '品牌名称必须2~10个字!', trigger: 'blur' },
  ],
  intro: [
    { required: true, message: '必须填写品牌简介!', trigger: 'blue' },
    { min: 2, max: 100, message: '品牌简介必须2~100个字!', trigger: 'blur' },
  ],
})
const editBrand = () => {
  brandForm.value.validate((valid, fields) => {
    if (valid) {
      brandAndCategoryHttp.editData('brand', brandFormData).then((result) => {
        if (result.status == 200) {
          let index = brands.value.findIndex((brand) => brand.id === result.data.id)
          brands.value.splice(index, 1, result.data)
          brandFormVisable.value = false
          ElMessage.success('品牌修改成功!')
        } else {
          ElMessage.error('修改失败!')
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

/**种类表单 */
let categoryFormVisable = ref(false)
let categoryFormData = reactive({
  id: 0,
  name: '',
})
const categoryForm = ref()
const categoryFormRules = reactive({
  name: [
    { required: true, message: '必须填写商品种类!', trigger: 'blue' },
    { min: 2, max: 10, message: '种类名称只能2~10个字!', trigger: 'blur' },
  ],
})

const editCategory = () => {
  categoryForm.value.validate((valid, fields) => {
    if (valid) {
      brandAndCategoryHttp.editData('category', categoryFormData).then((result) => {
        if (result.status == 200) {
          let index = categories.value.findIndex((category) => category.id === result.data.id)
          categories.value.splice(index, 1, result.data)
          categoryFormVisable.value = false
          ElMessage.success('种类修改成功!')
        } else {
          ElMessage.error('修改失败!')
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

/**编辑表单开关 */
const openForm = (form, data) => {
  if (form == 'brand') {
    Object.assign(brandFormData, data)
    brandFormVisable.value = true
  } else if (form == 'category') {
    Object.assign(categoryFormData, data)
    categoryFormVisable.value = true
  } else {
    ElMessage.error('错误!没有找到对应行为!')
  }
}

/**删除功能 */
const onDelete = (model, id) => {
  ElMessageBox.confirm('确认删除该条数据?', '确认删除?', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      brandAndCategoryHttp.deleteData(model, id).then((result) => {
        if (result.status == 204) {
          ElMessage.success('成功删除!')
          setTimeout(() => {
            window.location.reload()
          }, 500)
        } else {
          ElMessage.error('删除失败!')
        }
      })
    })
    .catch(() => {
      ElMessage.info('取消删除!')
    })
}

/**新增功能_品牌 */
let addBrandFormVisable = ref(false)
let addBrandFormData = reactive({
  name: '',
  intro: '',
})
const addBrandForm = ref()
// 规则直接采用上面定义好的
const createBrand = () => {
  brandAndCategoryHttp.createData('brand', addBrandFormData).then((result) => {
    if (result.status == 201) {
      brands.value.push(result.data)
      addBrandFormVisable.value = false
      ElMessage.success('新增品牌成功!')
    } else {
      ElMessage.error('错误!')
    }
  })
}

/**新增功能_种类 */
let addCategoryFormVisable = ref(false)
let addCategoryFormData = reactive({
  name: '',
})
const addCategoryForm = ref()
const createCategory = () => {
  brandAndCategoryHttp.createData('category', addCategoryFormData).then((result) => {
    if (result.status == 201) {
      categories.value.push(result.data)
      addCategoryFormVisable.value = false
      ElMessage.success('新增种类成功!')
    } else {
      ElMessage.error('错误!')
    }
  })
}

/**新增表单开关 */
const openAddform = (form) => {
  if (form == 'brand') {
    addBrandFormData.name = ''
    addBrandFormData.intro = ''
    addBrandFormVisable.value = true
  } else if (form == 'category') {
    addCategoryFormData.name = ''
    addCategoryFormVisable.value = true
  } else {
    ElMessage.error('错误!没有找到对应行为!')
  }
}
</script>

<template>
  <MainBox title="品牌种类">
    <div class="main-body">
      <el-card class="body-card">
        <template #header>
          <div class="card-header">
            <h3>品牌</h3>
            <div>
              <el-button type="success" @click="openAddform('brand')">
                <el-icon><Plus /></el-icon>
                <span>新增品牌</span>
              </el-button>
            </div>
          </div>
        </template>
        <el-table :data="brands">
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="intro" label="简介" min-width="140" align="center" />
          <el-table-column label="操作" width="120" align="center" fixed="right">
            <template #default="scope">
              <div class="table-btn-group">
                <div>
                  <el-tooltip content="编辑" placement="top" effect="light">
                    <el-button type="primary" @click="openForm('brand', scope.row)">
                      <el-icon><Edit /></el-icon>
                    </el-button>
                  </el-tooltip>
                </div>
                <div>
                  <el-tooltip content="删除" placement="top" effect="light">
                    <el-button type="danger" @click="onDelete('brand', scope.row.id)" disabled>
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </el-tooltip>
                </div>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <el-card class="body-card">
        <template #header>
          <div class="card-header">
            <h3>种类</h3>
            <div>
              <el-button type="success" @click="openAddform('category')">
                <el-icon><Plus /></el-icon>
                <span>新增种类</span>
              </el-button>
            </div>
          </div>
        </template>
        <el-table :data="categories">
          <el-table-column prop="name" label="名称" />
          <el-table-column label="操作" width="120" align="center" fixed="right">
            <template #default="scope">
              <div class="table-btn-group">
                <div>
                  <el-tooltip content="编辑" placement="top" effect="light">
                    <el-button type="primary" @click="openForm('category', scope.row)">
                      <el-icon><Edit /></el-icon>
                    </el-button>
                  </el-tooltip>
                </div>
                <div>
                  <el-tooltip content="删除" placement="top" effect="light">
                    <el-button type="danger" @click="onDelete('category', scope.row.id)" disabled>
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </el-tooltip>
                </div>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </MainBox>

  <!-- 品牌编辑表单 -->
  <FormDialog v-model="brandFormVisable" title="修改品牌信息" @submit="editBrand">
    <el-form ref="brandForm" :model="brandFormData" :rules="brandFormRules">
      <el-form-item label="品牌名称" prop="name">
        <el-input type="text" v-model="brandFormData.name" />
      </el-form-item>
      <el-form-item label="品牌简介" prop="intro">
        <el-input type="text" v-model="brandFormData.intro" />
      </el-form-item>
    </el-form>
  </FormDialog>
  <!-- 种类编辑表单 -->
  <FormDialog v-model="categoryFormVisable" title="编辑商品种类" @submit="editCategory">
    <el-form ref="categoryForm" :model="categoryFormData" :rules="categoryFormRules">
      <el-form-item label="种类名称" prop="name">
        <el-input type="text" v-model="categoryFormData.name" />
      </el-form-item>
    </el-form>
  </FormDialog>
  <!-- 新增品牌表单 -->
  <FormDialog v-model="addBrandFormVisable" title="新增品牌" @submit="createBrand">
    <el-form ref="addBrandForm" :model="addBrandFormData" :rules="brandFormRules">
      <el-form-item label="品牌名称" prop="name">
        <el-input type="text" v-model="addBrandFormData.name" />
      </el-form-item>
      <el-form-item label="品牌简介" prop="intro">
        <el-input type="text" v-model="addBrandFormData.intro" />
      </el-form-item>
    </el-form>
  </FormDialog>
  <!-- 新增种类表单 -->
  <FormDialog v-model="addCategoryFormVisable" title="新增种类" @submit="createCategory">
    <el-form ref="addCategoryForm" :model="addCategoryFormData" :rules="categoryFormRules">
      <el-form-item label="种类名称" prop="name">
        <el-input type="text" v-model="addCategoryFormData.name" />
      </el-form-item>
    </el-form>
  </FormDialog>
</template>

<style scoped>
.main-body,
.card-header,
.table-btn-group {
  display: flex;
  justify-content: space-between;
}
.body-card {
  width: 49.5%;
  min-height: 500px;
}
</style>
