<template>
  <div class="client-list-container">
    <!-- 页面标题栏 -->
    <div class="page-header">
      <div class="left">
        <h2>客户管理</h2>
        <div class="tabs-wrapper">
          <el-tabs v-model="activeTab" @tab-click="handleTabClick">
            <el-tab-pane label="全部客户" name="all"></el-tab-pane>
            <el-tab-pane label="需要跟进" name="overdue"></el-tab-pane>
          </el-tabs>
        </div>
      </div>
      <el-button type="primary" @click="showCreateDialog" :icon="Plus">创建客户</el-button>
    </div>

    <!-- 筛选表单 -->
    <el-card class="filter-card" shadow="hover">
      <template #header>
        <div class="filter-header">
          <span><i class="el-icon-filter"></i> 客户筛选</span>
        </div>
      </template>
      <el-form inline class="filter-form">
        <el-form-item label="客户级别">
          <el-select v-model="filterForm.level" style="width: 140px" placeholder="选择客户级别">
            <el-option value="" label="全部客户" />
            <el-option :value="0" label="已成交客户" />
            <el-option :value="1" label="持续跟进" />
            <el-option :value="2" label="潜在客户" />
            <el-option :value="3" label="暂时观望" />
            <el-option :value="4" label="希望渺茫" />
            <el-option :value="5" label="已流失客户" />
          </el-select>
        </el-form-item>
        <el-form-item label="客户姓名">
          <el-input v-model="filterForm.name" placeholder="输入客户姓名" style="width: 180px" prefix-icon="el-icon-user" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="filterForm.telephone" placeholder="输入联系电话" style="width: 180px" prefix-icon="el-icon-phone" />
        </el-form-item>
        <el-form-item class="actions">
          <el-button type="primary" @click="onSearch(true)" :icon="Search">搜索</el-button>
          <el-button @click="onSearch(false)" :icon="Refresh">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 客户数据表格 -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="table-header">
          <span>客户列表</span>
          <el-tag v-if="clientList.length > 0" type="info">共 {{ clientList.length }} 位客户</el-tag>
        </div>
      </template>

      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="6" animated />
      </div>

      <div v-else>
        <el-empty v-if="clientList.length === 0" description="暂无客户数据" />

        <el-table
          v-else
          :data="clientList"
          border
          stripe
          style="width: 100%"
          @row-click="handleRowClick"
          :header-cell-style="{ background: '#f5f7fa', color: '#606266', fontWeight: 'bold' }"
        >
          <el-table-column prop="name" label="客户姓名" min-width="100" show-overflow-tooltip>
            <template #default="{ row }">
              <div class="client-name">
                <span>{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="telephone" label="联系电话" min-width="120" show-overflow-tooltip />

          <el-table-column prop="address" label="客户地址" min-width="200" show-overflow-tooltip />

          <el-table-column prop="level_display" label="客户级别" min-width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getLevelTagType(row.level)" effect="light" size="small">
                {{ getLevelLabel(row.level) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="跟进状态" min-width="160">
            <template #default="{ row }">
              <div class="follow-status">
                <div class="follow-item">
                  <span class="label">上次跟进:</span>
                  <span class="value">{{ formatDate(row.last_follow_time) }}</span>
                </div>
                <div v-if="row.latest_follow_time" class="follow-item">
                  <span class="label">最晚跟进:</span>
                  <span class="value" :class="{ 'overdue-warning': row.is_overdue }">
                    {{ formatDate(row.latest_follow_time) }}
                    <el-tag v-if="row.is_overdue" size="small" type="danger" effect="dark">已逾期</el-tag>
                  </span>
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="staff_name" label="所属员工" min-width="100" align="center" />

          <el-table-column prop="created_at" label="创建时间" min-width="150" show-overflow-tooltip>
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>

          <el-table-column label="操作" width="100" fixed="right" align="center">
            <template #default="{ row }">
              <el-button
                type="primary"
                link
                size="small"
                @click.stop="viewClientDetail(row.uid)"
                :icon="View"
              >
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分页组件 -->
      <div class="pagination-container" v-if="activeTab === 'all' && clientList.length > 0">
        <PaginationView
          v-model="pagination.page"
          :page_size="15"
          :total="pagination.total"
        />
      </div>
    </el-card>

    <!-- 创建客户对话框 -->
    <el-dialog
      title="创建客户"
      v-model="createDialogVisible"
      width="550px"
      destroy-on-close
      :close-on-click-modal="false"
    >
      <el-form
        :model="createForm"
        :rules="createRules"
        ref="createFormRef"
        label-width="100px"
        class="create-client-form"
      >
        <el-form-item label="客户姓名" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入客户姓名"></el-input>
        </el-form-item>
        <el-form-item label="联系电话" prop="telephone">
          <el-input v-model="createForm.telephone" placeholder="请输入联系电话"></el-input>
        </el-form-item>
        <el-form-item label="详细住址" prop="address">
          <el-input v-model="createForm.address" placeholder="请输入详细住址" type="textarea" :rows="2"></el-input>
        </el-form-item>
        <el-form-item label="客户级别" prop="level">
          <el-select v-model="createForm.level" placeholder="请选择客户级别" style="width: 100%">
            <el-option label="持续跟进(成交率90%)" :value="1"></el-option>
            <el-option label="潜在客户(成交率50%+)" :value="2"></el-option>
            <el-option label="暂时观望(无直接购买需求)" :value="3"></el-option>
            <el-option label="希望渺茫" :value="4"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="备注信息" prop="remark">
          <el-input
            v-model="createForm.remark"
            type="textarea"
            placeholder="请输入备注信息(选填)"
            :rows="3"
          ></el-input>
        </el-form-item>
        <el-form-item label="所属员工" prop="staff" v-if="isBoss">
          <el-select v-model="createForm.staff" placeholder="请选择所属员工" style="width: 100%">
            <el-option
              v-for="staff in staffList"
              :key="staff.uid"
              :label="staff.name"
              :value="staff.uid"
            ></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitCreateForm" :loading="submitting">创建</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import clientHttp from '@/api/clientHttp'
import { useAuthStore } from '@/stores/auth'
import timeFormatter from '@/utils/timeFormatter'
import staffHttp from '@/api/staffHttp'
import PaginationView from '@/components/PaginationView.vue'
import { chineseNameRegExp, telphoneRegExp } from '@/utils/regExp'

export default {
  name: 'ClientList',
  components: {
    PaginationView
  },

  setup() {
    const authStore = useAuthStore()
    const router = useRouter()

    // 状态变量
    const loading = ref(false)
    const clientList = ref([])
    const createDialogVisible = ref(false)
    const submitting = ref(false)
    const createFormRef = ref(null)
    const activeTab = ref('overdue')
    const staffList = ref([])

    // 分页数据
    const pagination = reactive({
      page: 1,
      total: 0
    })

    // 筛选表单数据
    const filterForm = reactive({
      level: "",
      name: '',
      telephone: ''
    })

    // 计算属性
    const isBoss = computed(() => authStore.user && authStore.user.is_boss)

    // 监听页码变化，重新加载数据
    watch(
      () => pagination.page,
      () => {
        if (activeTab.value === 'all') {
          loadClientList(pagination.page, filterForm)
        }
      }
    )

    // 创建客户表单数据和规则
    const createForm = reactive({
      name: '',
      telephone: '',
      address: '',
      level: 1,
      remark: '',
      staff: ''
    })

    const createRules = {
      name: [{ required: true, message: '请输入客户姓名', trigger: 'blur' }],
      telephone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
      address: [{ required: true, message: '请输入详细住址', trigger: 'blur' }],
      level: [{ required: true, message: '请选择客户级别', trigger: 'change' }],
      staff: [{ required: true, message: '请选择所属员工', trigger: 'change' }]
    }

    // 方法
    const loadClientList = async (page = 1, params = {}) => {
      loading.value = true
      try {
        const response = await clientHttp.getClientList(page, params)
        if (response.status === 200) {
          clientList.value = response.data.results
          pagination.total = response.data.count
        } else {
          ElMessage.error('获取客户列表失败')
        }
      } catch (error) {
        ElMessage.error('获取客户列表失败')
        console.error('获取客户列表失败:', error)
      } finally {
        loading.value = false
      }
    }

    const loadOverdueClients = async (params = {}) => {
      loading.value = true
      try {
        const response = await clientHttp.getOverdueClients(params)
        if (response.status === 200) {
          clientList.value = response.data
        } else {
          ElMessage.error('获取需要跟进的客户列表失败')
        }
      } catch (error) {
        ElMessage.error('获取需要跟进的客户列表失败')
        console.error('获取需要跟进的客户列表失败:', error)
      } finally {
        loading.value = false
      }
    }

    const handleTabClick = () => {
      // 切换标签页时，保留筛选条件
      if (activeTab.value === 'all') {
        loadClientList(1, filterForm)
      } else if (activeTab.value === 'overdue') {
        loadOverdueClients(filterForm)
      }
    }

    // 搜索功能
    const onSearch = (action) => {
      if (action) {
        // 执行搜索
        // 转换level参数：空字符串表示不筛选级别
        const params = { ...filterForm };
        if (params.level === "") {
          params.level = null;
        }

        if (activeTab.value === 'all') {
          loadClientList(1, params)
        } else {
          loadOverdueClients(params)
        }
      } else {
        // 重置筛选条件
        filterForm.level = ""
        filterForm.name = ''
        filterForm.telephone = ''

        // 加载未筛选的数据
        if (activeTab.value === 'all') {
          loadClientList(1)
        } else {
          loadOverdueClients()
        }
      }
    }

    const showCreateDialog = () => {
      createDialogVisible.value = true
      // 重置表单
      if (createFormRef.value) {
        createFormRef.value.resetFields()
      }
    }

    const submitCreateForm = async () => {
      if (!createFormRef.value) return

      await createFormRef.value.validate(async (valid) => {
        if (!valid) return

        // 使用正则表达式进行验证
        if (!chineseNameRegExp.test(createForm.name)) {
          ElMessage.error('客户姓名格式错误,请输入2-15个汉字(可包含·•符号)')
          return
        }

        if (!telphoneRegExp.test(createForm.telephone)) {
          ElMessage.error('手机号码格式错误,请输入11位数字的手机号')
          return
        }

        submitting.value = true
        try {
          const response = await clientHttp.createClient(createForm)
          if (response.status === 201 || response.status === 200) {
            ElMessage.success('创建客户成功')
            createDialogVisible.value = false
            loadClientList() // 重新加载客户列表
          } else {
            ElMessage.error(response.data.detail || '创建客户失败')
          }
        } catch (error) {
          ElMessage.error('创建客户失败')
          console.error('创建客户失败:', error)
        } finally {
          submitting.value = false
        }
      })
    }

    const viewClientDetail = (uid) => {
      router.push({ path: `/client/detail/${uid}` })
    }

    const handleRowClick = (row) => {
      viewClientDetail(row.uid)
    }

    const formatDate = (datetime) => {
      return datetime ? timeFormatter.stringFromDate(datetime) : '--'
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

    // 加载数据
    onMounted(() => {
      // 默认加载需要跟进的客户列表
      loadOverdueClients()

      // 加载员工列表，仅当用户是老板时
      if (isBoss.value) {
        // 使用staffHttp获取员工列表
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
        loadStaffList()
      }
    })

    return {
      loading,
      clientList,
      createDialogVisible,
      createForm,
      createRules,
      createFormRef,
      submitting,
      activeTab,
      staffList,
      filterForm,
      isBoss,
      pagination,
      showCreateDialog,
      submitCreateForm,
      viewClientDetail,
      handleRowClick,
      formatDate,
      getLevelTagType,
      getLevelLabel,
      handleTabClick,
      onSearch
    }
  }
}
</script>

<style scoped>
.client-list-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header .left {
  display: flex;
  align-items: center;
}

.page-header h2 {
  margin: 0;
  margin-right: 25px;
  font-size: 22px;
  color: #303133;
}

.tabs-wrapper {
  margin-bottom: 0;
}

.filter-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.filter-header {
  font-weight: bold;
  color: #409EFF;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-form .actions {
  margin-left: auto;
}

.table-card {
  border-radius: 8px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
}

.loading-container {
  padding: 20px 0;
}

.client-name {
  font-weight: 500;
  color: #303133;
}

.follow-status {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.follow-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.follow-item .label {
  color: #909399;
  font-size: 13px;
}

.overdue-warning {
  color: #F56C6C;
  font-weight: bold;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.create-client-form {
  padding: 10px 20px;
}

/* 美化表格行的悬停效果 */
:deep(.el-table__row) {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

:deep(.el-table__row:hover) {
  background-color: #f0f9ff !important;
}

/* 美化表单输入框 */
:deep(.el-input__wrapper),
:deep(.el-textarea__inner) {
  box-shadow: 0 0 0 1px #dcdfe6 inset;
}

:deep(.el-input__wrapper:hover),
:deep(.el-textarea__inner:hover) {
  box-shadow: 0 0 0 1px #c0c4cc inset;
}

:deep(.el-input__wrapper.is-focus),
:deep(.el-textarea__inner:focus) {
  box-shadow: 0 0 0 1px #409eff inset !important;
}

/* 对话框样式 */
:deep(.el-dialog__header) {
  border-bottom: 1px solid #f0f0f0;
  padding: 15px 20px;
  margin-right: 0;
}

:deep(.el-dialog__body) {
  padding: 20px;
}

:deep(.el-dialog__footer) {
  border-top: 1px solid #f0f0f0;
  padding: 15px 20px;
}

/* 标签页样式美化 */
.tabs-wrapper {
  margin-bottom: 0;
}

:deep(.el-tabs__header) {
  margin-bottom: 0;
}

:deep(.el-tabs__nav) {
  border: none;
}

:deep(.el-tabs__item) {
  font-size: 15px;
  padding: 0 20px;
  height: 40px;
  line-height: 40px;
  transition: all 0.3s;
}

:deep(.el-tabs__item.is-active) {
  color: #409EFF;
  font-weight: bold;
}

:deep(.el-tabs__active-bar) {
  height: 3px;
  border-radius: 3px;
  background-color: #409EFF;
}

:deep(.el-tabs__item:hover) {
  color: #409EFF;
}
</style>
