<script setup>
import MainBox from '@/components/MainBox.vue'
import FormDialog from '@/components/FormDialog.vue'
import installerHttp from '@/api/installerHttp'
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, View } from '@element-plus/icons-vue'

/**获取数据 */
let installers = ref([])

onMounted(() => {
  fetchInstallers()
})

const fetchInstallers = () => {
  installerHttp.requetAllInstallerData().then((result) => {
    if (result.status == 200) {
      installers.value = result.data
    } else {
      ElMessage.error('请求安装工数据失败!')
    }
  }).catch(error => {
    console.error('获取安装工数据出错:', error)
    ElMessage.error('请求安装工数据出错!')
  })
}

/**编辑表单 */
let installerFormVisible = ref(false)
let installerFormData = reactive({
  id: 0,
  name: '',
  telephone: ''
})
const installerForm = ref()
const installerFormRules = reactive({
  name: [
    { required: true, message: '必须填写安装工姓名!', trigger: 'blur' },
    { min: 2, max: 10, message: '姓名必须2~10个字!', trigger: 'blur' },
  ],
  telephone: [
    { required: true, message: '必须填写联系电话!', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码格式!', trigger: 'blur' },
  ]
})

const editInstaller = () => {
  installerForm.value.validate((valid, fields) => {
    if (valid) {
      installerHttp.updateInstaller(installerFormData.id, installerFormData).then((result) => {
        if (result.status == 200) {
          let index = installers.value.findIndex((installer) => installer.id === result.data.id)
          installers.value.splice(index, 1, result.data)
          installerFormVisible.value = false
          ElMessage.success('安装工信息修改成功!')
        } else {
          ElMessage.error('修改失败!')
        }
      }).catch(error => {
        console.error('修改安装工信息出错:', error)
        ElMessage.error('修改出错!')
      })
    } else {
      for (let key in fields) {
        ElMessage.error(fields[key][0]['message'])
      }
      return
    }
  })
}

/**打开编辑表单 */
const openForm = (data) => {
  Object.assign(installerFormData, data)
  installerFormVisible.value = true
}

/**删除功能 */
const onDelete = (id) => {
  ElMessageBox.confirm('确认删除该安装工信息?', '确认删除?', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      installerHttp.deleteInstaller(id).then((result) => {
        if (result.status == 204) {
          ElMessage.success('成功删除!')
          // 从列表中移除被删除的项
          installers.value = installers.value.filter(item => item.id !== id)
        } else {
          ElMessage.error('删除失败!')
        }
      }).catch(error => {
        console.error('删除安装工出错:', error)
        ElMessage.error('删除出错!')
      })
    })
    .catch(() => {
      ElMessage.info('取消删除!')
    })
}

/**新增功能 */
let addInstallerFormVisible = ref(false)
let addInstallerFormData = reactive({
  name: '',
  telephone: ''
})
const addInstallerForm = ref()

const createInstaller = () => {
  addInstallerForm.value.validate((valid, fields) => {
    if (valid) {
      installerHttp.createInstaller(addInstallerFormData).then((result) => {
        if (result.status == 201) {
          installers.value.push(result.data)
          addInstallerFormVisible.value = false
          ElMessage.success('新增安装工成功!')
          // 重置表单
          addInstallerFormData.name = ''
          addInstallerFormData.telephone = ''
        } else {
          ElMessage.error('新增失败!')
        }
      }).catch(error => {
        console.error('新增安装工出错:', error)
        ElMessage.error('新增出错!')
      })
    } else {
      for (let key in fields) {
        ElMessage.error(fields[key][0]['message'])
      }
      return
    }
  })
}

/**打开新增表单 */
const openAddForm = () => {
  // 重置表单数据
  addInstallerFormData.name = ''
  addInstallerFormData.telephone = ''
  addInstallerFormVisible.value = true
}

/**查看安装工详情 */
let detailInstallerFormVisible = ref(false)
let detailInstallerData = reactive({
  id: 0,
  name: '',
  telephone: '',
  current_month_installation_fee: 0
})

const viewDetail = (id) => {
  installerHttp.getInstallerDetail(id).then(result => {
    if (result.status == 200) {
      Object.assign(detailInstallerData, result.data)
      detailInstallerFormVisible.value = true
    } else {
      ElMessage.error('获取详情失败!')
    }
  }).catch(error => {
    console.error('获取安装工详情出错:', error)
    ElMessage.error('获取详情出错!')
  })
}

// 格式化金额的辅助函数
const formatCurrency = (value) => {
  if (value === null || value === undefined) return '¥0'

  // 确保数值是数字类型
  const numValue = Number(value)
  if (isNaN(numValue)) return '¥0'

  // 使用toLocaleString格式化数字，但添加错误处理
  try {
    return `¥${numValue.toLocaleString('zh-CN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`
  } catch (error) {
    console.error('格式化数字出错:', error)
    return `¥${numValue}`
  }
}
</script>

<template>
  <MainBox title="安装师傅">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>安装师傅</h3>
          <el-button type="success" @click="openAddForm">
            <el-icon><Plus /></el-icon>
            <span>新增师傅</span>
          </el-button>
        </div>
      </template>

      <!-- 安装工列表表格 -->
      <el-table :data="installers" border stripe>
        <el-table-column prop="name" label="姓名" width="380"/>
        <el-table-column prop="telephone" label="联系电话" />

        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="scope">
            <el-button-group>
              <el-tooltip content="结算费用" placement="top" effect="light">
                <el-button type="warning" @click="viewDetail(scope.row.id)">
                  <el-icon><Money /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="编辑" placement="top" effect="light">
                <el-button type="primary" @click="openForm(scope.row)">
                  <el-icon><Edit /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="删除" placement="top" effect="light">
                <el-button type="danger" @click="onDelete(scope.row.id)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </MainBox>

  <!-- 编辑安装工表单 -->
  <FormDialog v-model="installerFormVisible" title="修改安装工信息" @submit="editInstaller">
    <el-form ref="installerForm" :model="installerFormData" :rules="installerFormRules" label-width="100px">
      <el-form-item label="姓名" prop="name">
        <el-input v-model="installerFormData.name" placeholder="请输入安装工姓名" />
      </el-form-item>
      <el-form-item label="联系电话" prop="telephone">
        <el-input v-model="installerFormData.telephone" placeholder="请输入联系电话" />
      </el-form-item>
    </el-form>
  </FormDialog>

  <!-- 新增安装工表单 -->
  <FormDialog v-model="addInstallerFormVisible" title="新增安装工" @submit="createInstaller">
    <el-form ref="addInstallerForm" :model="addInstallerFormData" :rules="installerFormRules" label-width="100px">
      <el-form-item label="姓名" prop="name">
        <el-input v-model="addInstallerFormData.name" placeholder="请输入安装工姓名" />
      </el-form-item>
      <el-form-item label="联系电话" prop="telephone">
        <el-input v-model="addInstallerFormData.telephone" placeholder="请输入联系电话" />
      </el-form-item>
    </el-form>
  </FormDialog>

  <!-- 安装工详情 -->
  <el-dialog v-model="detailInstallerFormVisible" title="安装工详情" width="500px">
    <el-descriptions :column="1" border>
      <el-descriptions-item label="姓名">{{ detailInstallerData.name }}</el-descriptions-item>
      <el-descriptions-item label="联系电话">{{ detailInstallerData.telephone }}</el-descriptions-item>
      <el-descriptions-item label="本月安装费">{{ formatCurrency(detailInstallerData.current_month_installation_fee) }}</el-descriptions-item>
    </el-descriptions>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="detailInstallerFormVisible = false">关闭</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mt-4 {
  margin-top: 20px;
}

.mb-2 {
  margin-bottom: 10px;
}

.text-center {
  text-align: center;
}

.text-gray {
  color: #909399;
}

:deep(.el-descriptions__body) {
  background-color: #f5f7fa;
}

:deep(.el-descriptions__label) {
  font-weight: bold;
  color: #606266;
}

:deep(.el-descriptions__content) {
  font-size: 16px;
}
</style>
