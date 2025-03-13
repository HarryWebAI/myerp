<script setup>
import MainBox from '@/components/MainBox.vue'
import FormDialog from '@/components/FormDialog.vue'
import staffHttp from '@/api/staffHttp'
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, View } from '@element-plus/icons-vue'
import { telphoneRegExp, chineseNameRegExp } from '@/utils/regExp'

/**获取数据 */
let staffs = ref([])

onMounted(() => {
  fetchStaffs()
})

const fetchStaffs = () => {
  staffHttp.getStaffList().then((result) => {
    if (result.status == 200) {
      staffs.value = result.data
    } else {
      ElMessage.error('请求员工数据失败!')
    }
  }).catch(error => {
    console.error('获取员工数据出错:', error)
    ElMessage.error('请求员工数据出错!')
  })
}

/**编辑表单 */
let staffFormVisible = ref(false)
let staffFormData = reactive({
  uid: '',
  account: '',
  name: '',
  telephone: '',
  is_active: true,
  is_manager: false,
  is_storekeeper: false
})
const staffForm = ref()
const staffFormRules = reactive({
  account: [
    { required: true, message: '必须填写登录账号!', trigger: 'blur' },
    { min: 4, max: 20, message: '账号长度必须在4-20个字符之间!', trigger: 'blur' },
  ],
  name: [
    { required: true, message: '必须填写员工姓名!', trigger: 'blur' },
    { pattern: chineseNameRegExp, message: '请输入正确的中文姓名格式!', trigger: 'blur' },
  ],
  telephone: [
    { required: true, message: '必须填写联系电话!', trigger: 'blur' },
    { pattern: telphoneRegExp, message: '请输入正确的手机号码格式!', trigger: 'blur' },
  ]
})

const editStaff = () => {
  staffForm.value.validate((valid, fields) => {
    if (valid) {
      // 准备要更新的数据
      const updateData = {
        name: staffFormData.name,
        telephone: staffFormData.telephone,
        is_active: staffFormData.is_active,
        is_manager: staffFormData.is_manager,
        is_storekeeper: staffFormData.is_storekeeper
      }

      staffHttp.updateStaff(staffFormData.uid, updateData).then((result) => {
        if (result.status == 200) {
          // 更新本地数据
          const index = staffs.value.findIndex(staff => staff.uid === result.data.uid)
          if (index !== -1) {
            staffs.value.splice(index, 1, result.data)
          }

          staffFormVisible.value = false
          ElMessage.success('员工信息修改成功!')
        } else {
          ElMessage.error('修改失败!')
        }
      }).catch(error => {
        console.error('修改员工信息出错:', error)
        // 尝试显示后端返回的详细错误信息
        if (error.response && error.response.data) {
          const errorData = error.response.data
          if (typeof errorData === 'object') {
            // 处理多个字段的错误
            for (const key in errorData) {
              ElMessage.error(`${key}: ${errorData[key]}`)
            }
          } else {
            ElMessage.error(String(errorData))
          }
        } else {
          ElMessage.error('修改出错!')
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

/**打开编辑表单 */
const openForm = (data) => {
  Object.assign(staffFormData, data)
  staffFormVisible.value = true
}

/**删除功能 */
const onDelete = (uid) => {
  // 删除员工的接口暂未实现，需要后端提供
  ElMessageBox.confirm('确定要删除该员工吗？', '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.warning(`删除员工(ID: ${uid})功能暂未实现，请联系管理员添加相关接口`)
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

/**新增功能 */
let addStaffFormVisible = ref(false)
let addStaffFormData = reactive({
  account: '',
  name: '',
  telephone: '',
  password: '',
  is_manager: false,
  is_storekeeper: false
})
const addStaffForm = ref()
const addStaffFormRules = reactive({
  account: [
    { required: true, message: '必须填写登录账号!', trigger: 'blur' },
    { min: 4, max: 20, message: '账号长度必须在4-20个字符之间!', trigger: 'blur' },
  ],
  name: [
    { required: true, message: '必须填写员工姓名!', trigger: 'blur' },
    { pattern: chineseNameRegExp, message: '请输入正确的中文姓名格式!', trigger: 'blur' },
  ],
  telephone: [
    { required: true, message: '必须填写联系电话!', trigger: 'blur' },
    { pattern: telphoneRegExp, message: '请输入正确的手机号码格式!', trigger: 'blur' },
  ],
  password: [
    { min: 6, max: 30, message: '密码长度必须在6-30个字符之间!', trigger: 'blur' },
  ]
})

const createStaff = () => {
  addStaffForm.value.validate((valid, fields) => {
    if (valid) {
      // 如果密码为空，后端会使用默认密码
      const data = { ...addStaffFormData }
      if (!data.password) {
        delete data.password
      }

      staffHttp.createStaff(data).then((result) => {
        if (result.status == 201) {
          staffs.value.push(result.data)
          addStaffFormVisible.value = false
          ElMessage.success('新增员工成功!')
          // 重置表单
          resetAddForm()
        } else {
          ElMessage.error('新增失败!')
        }
      }).catch(error => {
        console.error('新增员工出错:', error)
        // 尝试显示后端返回的详细错误信息
        if (error.response && error.response.data) {
          const errorData = error.response.data
          if (typeof errorData === 'object') {
            // 处理多个字段的错误
            for (const key in errorData) {
              ElMessage.error(`${key}: ${errorData[key]}`)
            }
          } else {
            ElMessage.error(String(errorData))
          }
        } else {
          ElMessage.error('新增出错!')
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

/**打开新增表单 */
const openAddForm = () => {
  resetAddForm()
  addStaffFormVisible.value = true
}

/**重置新增表单 */
const resetAddForm = () => {
  addStaffFormData.account = ''
  addStaffFormData.name = ''
  addStaffFormData.telephone = ''
  addStaffFormData.password = ''
  addStaffFormData.is_manager = false
  addStaffFormData.is_storekeeper = false
}

/**查看员工详情 */
let detailStaffFormVisible = ref(false)
let detailStaffData = reactive({
  uid: '',
  account: '',
  name: '',
  telephone: '',
  is_active: true,
  is_manager: false,
  is_storekeeper: false
})

const viewDetail = (staff) => {
  Object.assign(detailStaffData, staff)
  detailStaffFormVisible.value = true
}
</script>

<template>
  <MainBox title="员工管理">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>员工列表</h3>
          <el-button type="success" @click="openAddForm">
            <el-icon><Plus /></el-icon>
            <span>新增员工</span>
          </el-button>
        </div>
      </template>

      <!-- 员工列表表格 -->
      <el-table :data="staffs" border stripe>
        <el-table-column prop="account" label="登录账号" width="150" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="telephone" label="联系电话" width="150" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="角色" min-width="200">
          <template #default="scope">
            <el-tag v-if="scope.row.is_boss" type="danger" effect="dark" class="role-tag">老板</el-tag>
            <el-tag v-if="scope.row.is_manager" type="warning" effect="dark" class="role-tag">门店经理</el-tag>
            <el-tag v-if="scope.row.is_storekeeper" type="primary" effect="dark" class="role-tag">仓库管理</el-tag>
            <el-tag v-if="!scope.row.is_boss && !scope.row.is_manager && !scope.row.is_storekeeper" type="info" effect="plain" class="role-tag">普通员工</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="scope">
            <el-button-group>
              <el-tooltip content="查看详情" placement="top" effect="light">
                <el-button type="info" @click="viewDetail(scope.row)">
                  <el-icon><View /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="编辑" placement="top" effect="light">
                <el-button type="primary" @click="openForm(scope.row)">
                  <el-icon><Edit /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="删除功能已禁用" placement="top" effect="light">
                <el-button type="danger" disabled @click="onDelete(scope.row.uid)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </MainBox>

  <!-- 编辑员工表单 -->
  <FormDialog v-model="staffFormVisible" title="修改员工信息" @submit="editStaff">
    <el-form ref="staffForm" :model="staffFormData" :rules="staffFormRules" label-width="100px">
      <el-form-item label="登录账号" prop="account">
        <el-input v-model="staffFormData.account" placeholder="请输入登录账号" disabled />
      </el-form-item>
      <el-form-item label="姓名" prop="name">
        <el-input v-model="staffFormData.name" placeholder="请输入员工姓名" />
      </el-form-item>
      <el-form-item label="联系电话" prop="telephone">
        <el-input v-model="staffFormData.telephone" placeholder="请输入联系电话" />
      </el-form-item>
      <el-form-item label="员工状态">
        <el-switch
          v-model="staffFormData.is_active"
          active-text="启用"
          inactive-text="禁用"
          :active-value="true"
          :inactive-value="false"
        />
      </el-form-item>
      <el-form-item label="角色设置">
        <el-checkbox v-model="staffFormData.is_manager" label="门店经理" border />
        <el-checkbox v-model="staffFormData.is_storekeeper" label="仓库管理" border />
      </el-form-item>
    </el-form>
  </FormDialog>

  <!-- 新增员工表单 -->
  <FormDialog v-model="addStaffFormVisible" title="新增员工" @submit="createStaff">
    <el-form ref="addStaffForm" :model="addStaffFormData" :rules="addStaffFormRules" label-width="100px">
      <el-form-item label="登录账号" prop="account">
        <el-input v-model="addStaffFormData.account" placeholder="请输入登录账号" />
      </el-form-item>
      <el-form-item label="姓名" prop="name">
        <el-input v-model="addStaffFormData.name" placeholder="请输入员工姓名" />
      </el-form-item>
      <el-form-item label="联系电话" prop="telephone">
        <el-input v-model="addStaffFormData.telephone" placeholder="请输入联系电话" />
      </el-form-item>
      <el-form-item label="初始密码" prop="password">
        <el-input v-model="addStaffFormData.password" type="password" placeholder="不填则使用默认密码111111" show-password />
      </el-form-item>
      <el-form-item label="角色设置">
        <el-checkbox v-model="addStaffFormData.is_manager" label="门店经理" border />
        <el-checkbox v-model="addStaffFormData.is_storekeeper" label="仓库管理" border />
      </el-form-item>
    </el-form>
  </FormDialog>

  <!-- 员工详情 -->
  <el-dialog v-model="detailStaffFormVisible" title="员工详情" width="500px">
    <el-descriptions :column="1" border>
      <el-descriptions-item label="登录账号">{{ detailStaffData.account }}</el-descriptions-item>
      <el-descriptions-item label="姓名">{{ detailStaffData.name }}</el-descriptions-item>
      <el-descriptions-item label="联系电话">{{ detailStaffData.telephone }}</el-descriptions-item>
      <el-descriptions-item label="状态">
        <el-tag :type="detailStaffData.is_active ? 'success' : 'danger'">
          {{ detailStaffData.is_active ? '启用' : '禁用' }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="角色">
        <div class="roles-container">
          <el-tag v-if="detailStaffData.is_boss" type="danger" effect="dark" class="role-tag">老板</el-tag>
          <el-tag v-if="detailStaffData.is_manager" type="warning" effect="dark" class="role-tag">门店经理</el-tag>
          <el-tag v-if="detailStaffData.is_storekeeper" type="primary" effect="dark" class="role-tag">仓库管理</el-tag>
          <el-tag v-if="!detailStaffData.is_boss && !detailStaffData.is_manager && !detailStaffData.is_storekeeper" type="info" effect="plain">普通员工</el-tag>
        </div>
      </el-descriptions-item>
    </el-descriptions>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="detailStaffFormVisible = false">关闭</el-button>
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

.role-tag {
  margin-right: 5px;
}

.roles-container {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
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
