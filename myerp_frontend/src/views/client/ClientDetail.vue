<template>
  <div class="client-detail-container" v-loading="loading">
    <div class="header">
      <div class="title-section">
        <h2>{{ clientInfo.name }} - 客户详情</h2>
        <el-tag :type="getLevelTagType(clientInfo.level)" v-if="clientInfo.level !== undefined">
          {{ getLevelLabel(clientInfo.level) }}
        </el-tag>
      </div>
      <div class="button-group">
        <el-button type="primary" @click="showFollowDialog">跟进客户</el-button>
        <el-button type="warning" @click="enableEdit">编辑信息</el-button>
        <el-button @click="goBack">返回</el-button>
      </div>
    </div>

    <el-card class="client-info-card">
      <template #header>
        <div class="card-header">
          <span>基本信息</span>
          <div v-if="editing">
            <el-button type="primary" size="small" @click="saveEdit" :loading="submitting">保存</el-button>
            <el-button size="small" @click="cancelEdit">取消</el-button>
          </div>
        </div>
      </template>

      <el-form
        :model="editForm"
        :disabled="!editing"
        ref="editFormRef"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户姓名" prop="name">
              <el-input v-model="editForm.name" placeholder="请输入客户姓名"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="telephone">
              <el-input v-model="editForm.telephone" placeholder="请输入联系电话"></el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="详细住址" prop="address">
          <el-input v-model="editForm.address" placeholder="请输入详细住址"></el-input>
        </el-form-item>

        <el-form-item label="备注信息" prop="remark">
          <el-input
            v-model="editForm.remark"
            type="textarea"
            placeholder="请输入备注信息"
          ></el-input>
        </el-form-item>

        <el-form-item label="所属员工" prop="staff" v-if="isBoss">
          <el-select v-model="editForm.staff" placeholder="请选择所属员工">
            <el-option
              v-for="staff in staffList"
              :key="staff.uid"
              :label="staff.name"
              :value="staff.uid"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="所属员工" v-else>
          <div>{{ getStaffName(clientInfo.staff) }}</div>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="上次跟进">
              <div>{{ formatDate(clientInfo.last_follow_time) }}</div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最晚跟进" v-if="clientInfo.latest_follow_time">
              <div :class="{ 'overdue-warning': clientInfo.is_overdue }">
                {{ formatDate(clientInfo.latest_follow_time) }}
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="创建时间">
              <div>{{ formatDate(clientInfo.created_at) }}</div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="更新时间">
              <div>{{ formatDate(clientInfo.updated_at) }}</div>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <el-card class="follow-records-card">
      <template #header>
        <div class="card-header">
          <span>跟进记录</span>
        </div>
      </template>

      <div v-if="clientInfo.follow_records && clientInfo.follow_records.length > 0">
        <el-timeline>
          <el-timeline-item
            v-for="record in sortedFollowRecords"
            :key="record.uid"
            :timestamp="formatDateTime(record.created_at)"
            placement="top"
          >
            <el-card class="follow-record-card">
              <div class="follow-record-header">
                <span>跟进人员: {{ record.staff_name }}</span>
              </div>
              <div class="follow-record-content">
                {{ record.content }}
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>
      <el-empty v-else description="暂无跟进记录"></el-empty>
    </el-card>

    <!-- 跟进客户对话框 -->
    <el-dialog
      title="跟进客户"
      v-model="followDialogVisible"
      width="500px"
    >
      <el-form
        :model="followForm"
        :rules="followRules"
        ref="followFormRef"
        label-width="100px"
      >
        <el-form-item label="客户级别" prop="client_level">
          <el-select v-model="followForm.client_level" placeholder="请选择客户级别">
            <el-option label="已成交" :value="0"></el-option>
            <el-option label="持续跟进(成交率90%)" :value="1"></el-option>
            <el-option label="潜在客户(成交率50%+)" :value="2"></el-option>
            <el-option label="暂时观望(无直接购买需求)" :value="3"></el-option>
            <el-option label="希望渺茫" :value="4"></el-option>
            <el-option label="已流失" :value="5"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="跟进内容" prop="content">
          <el-input
            v-model="followForm.content"
            type="textarea"
            placeholder="请输入跟进内容"
            :rows="4"
          ></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="followDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitFollowForm" :loading="submitting">提交</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import clientHttp from '@/api/clientHttp'
import { useAuthStore } from '@/stores/auth'
import timeFormatter from '@/utils/timeFormatter'
import staffHttp from '@/api/staffHttp'
import { telphoneRegExp, chineseNameRegExp } from '@/utils/regExp'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 状态变量
const loading = ref(false)
const submitting = ref(false)
const clientInfo = ref({})
const editing = ref(false)
const editFormRef = ref(null)
const followFormRef = ref(null)
const followDialogVisible = ref(false)
const staffList = ref([])

// 编辑表单数据
const editForm = reactive({
  name: '',
  telephone: '',
  address: '',
  remark: '',
  staff: ''
})

// 跟进表单数据和规则
const followForm = reactive({
  client_level: 1,
  content: ''
})

const followRules = {
  client_level: [{ required: true, message: '请选择客户级别', trigger: 'change' }],
  content: [{ required: true, message: '请输入跟进内容', trigger: 'blur' }]
}

// 计算属性
const isBoss = computed(() => authStore.user && authStore.user.is_boss)

const sortedFollowRecords = computed(() => {
  if (!clientInfo.value.follow_records) return []
  return [...clientInfo.value.follow_records].sort((a, b) => {
    return new Date(b.created_at) - new Date(a.created_at)
  })
})

// 方法
const loadClientDetail = async () => {
  const clientId = route.params.id
  if (!clientId) {
    ElMessage.error('客户ID不能为空')
    router.push('/client/list')
    return
  }

  loading.value = true
  try {
    const response = await clientHttp.getClientDetail(clientId)
    if (response.status === 200) {
      clientInfo.value = response.data

      // 初始化编辑表单数据
      Object.assign(editForm, {
        name: clientInfo.value.name,
        telephone: clientInfo.value.telephone,
        address: clientInfo.value.address,
        remark: clientInfo.value.remark || '',
        staff: clientInfo.value.staff
      })

      // 初始化跟进表单级别
      followForm.client_level = clientInfo.value.level
    } else {
      ElMessage.error('获取客户详情失败')
      router.push('/client/list')
    }
  } catch (error) {
    ElMessage.error('获取客户详情失败')
    console.error('获取客户详情失败:', error)
    router.push('/client/list')
  } finally {
    loading.value = false
  }
}

const enableEdit = () => {
  editing.value = true
}

const cancelEdit = () => {
  editing.value = false
  // 重置表单数据
  Object.assign(editForm, {
    name: clientInfo.value.name,
    telephone: clientInfo.value.telephone,
    address: clientInfo.value.address,
    remark: clientInfo.value.remark || '',
    staff: clientInfo.value.staff
  })
}

const saveEdit = async () => {
  if (!chineseNameRegExp.test(editForm.name)) {
    ElMessage.error('客户姓名格式错误,请输入2-15个汉字(可包含·•符号)');
    return;
  }

  if (!telphoneRegExp.test(editForm.telephone)) {
    ElMessage.error('手机号码格式错误,请输入11位数字的手机号');
    return;
  }
  submitting.value = true
  try {
    const response = await clientHttp.updateClient(clientInfo.value.uid, editForm)
    if (response.status === 200) {
      ElMessage.success('更新客户信息成功')
      editing.value = false
      loadClientDetail() // 重新加载客户详情
    } else {
      ElMessage.error(response.data.detail || '更新客户信息失败')
    }
  } catch (error) {
    ElMessage.error('更新客户信息失败')
    console.error('更新客户信息失败:', error)
  } finally {
    submitting.value = false
  }
}

const showFollowDialog = () => {
  followDialogVisible.value = true
  followForm.client_level = clientInfo.value.level
  followForm.content = ''

  if (followFormRef.value) {
    followFormRef.value.resetFields()
  }
}

const submitFollowForm = async () => {
  if (!followFormRef.value) return

  await followFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      const response = await clientHttp.followClient(clientInfo.value.uid, followForm)
      if (response.status === 200) {
        ElMessage.success('跟进客户成功')
        followDialogVisible.value = false
        loadClientDetail() // 重新加载客户详情
      } else {
        ElMessage.error(response.data.detail || '跟进客户失败')
      }
    } catch (error) {
      ElMessage.error('跟进客户失败')
      console.error('跟进客户失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

const goBack = () => {
  router.push('/client/list')
}

const formatDate = (datetime) => {
  return datetime ? timeFormatter.stringFromDate(datetime) : '--'
}

const formatDateTime = (datetime) => {
  return datetime ? timeFormatter.stringFromDateTime(datetime) : '--'
}

const getLevelTagType = (level) => {
  const types = {
    0: 'success',
    1: 'danger',
    2: 'warning',
    3: 'info',
    4: 'info',
    5: 'info'
  }
  return types[level] || 'info'
}

const getLevelLabel = (level) => {
  const labels = {
    0: '已成交',
    1: '持续跟进',
    2: '潜在客户',
    3: '暂时观望',
    4: '希望渺茫',
    5: '已流失'
  }
  return labels[level] || '未知'
}

const getStaffName = (staffUid) => {
  if (!staffUid) return '--'

  // 首先尝试使用clientInfo.staff_name
  if (clientInfo.value.staff_name) {
    return clientInfo.value.staff_name
  }

  // 如果clientInfo.staff_name不存在，从staffList查找
  const staff = staffList.value.find(s => s.uid === staffUid)
  return staff ? staff.name : `员工${staffUid}`
}

// 加载员工列表的函数
const loadStaffList = async () => {
  try {
    const response = await staffHttp.getStaffList()
    if (response.status === 200) {
      staffList.value = response.data
    } else {
      console.error('获取员工列表失败')
    }
  } catch (error) {
    console.error('获取员工列表失败:', error)
  }
}

// 加载数据
onMounted(() => {
  loadClientDetail()

  // 加载员工列表，仅当用户是老板时
  if (isBoss.value) {
    loadStaffList()
  }
})
</script>

<style scoped>
.client-detail-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-section h2 {
  margin: 0;
}

.button-group {
  display: flex;
  gap: 10px;
}

.client-info-card,
.follow-records-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.follow-record-card {
  margin-bottom: 10px;
}

.follow-record-header {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.follow-record-content {
  white-space: pre-wrap;
}

.overdue-warning {
  color: #F56C6C;
  font-weight: bold;
}
</style>
