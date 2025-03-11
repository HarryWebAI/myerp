<template>
  <div class="client-list-container">
    <div class="header">
      <h2>客户管理</h2>
      <el-button type="primary" @click="showCreateDialog">创建客户</el-button>
    </div>

    <el-tabs v-model="activeTab" @tab-click="handleTabClick">
      <el-tab-pane label="全部客户" name="all"></el-tab-pane>
      <el-tab-pane label="需要跟进" name="overdue"></el-tab-pane>
    </el-tabs>

    <!-- 添加筛选表单 -->
    <el-card style="margin-bottom: 20px">
      <template #header>
        <div class="filter-header">
          <span>客户筛选</span>
        </div>
      </template>
      <el-form inline>
        <el-form-item label="客户级别">
          <el-select v-model="filterForm.level" style="width: 120px" placeholder="选择客户级别">
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
          <el-input v-model="filterForm.name" placeholder="输入客户姓名" style="width: 150px" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="filterForm.telephone" placeholder="输入联系电话" style="width: 150px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onSearch(true)">搜索</el-button>
          <el-button @click="onSearch(false)">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-table
      v-loading="loading"
      :data="clientList"
      style="width: 100%"
      @row-click="handleRowClick"
    >
      <el-table-column prop="name" label="客户姓名" width="120"></el-table-column>
      <el-table-column prop="telephone" label="联系电话" width="150"></el-table-column>
      <el-table-column prop="level_display" label="客户级别" width="120">
        <template #default="{ row }">
          <el-tag :type="getLevelTagType(row.level)">{{ getLevelLabel(row.level) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="跟进状态" width="180">
        <template #default="{ row }">
          <div>
            <div>上次跟进: {{ formatDate(row.last_follow_time) }}</div>
            <div v-if="row.latest_follow_time">
              <span :class="{ 'overdue-warning': row.is_overdue }">
                最晚跟进: {{ formatDate(row.latest_follow_time) }}
              </span>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="staff_name" label="所属员工" width="120"></el-table-column>
      <el-table-column prop="created_at" label="创建时间">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button
            type="primary"
            text
            size="small"
            @click.stop="viewClientDetail(row.uid)"
          >
            查看详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加分页组件 -->
    <div class="pagination-container" v-if="activeTab === 'all'">
      <PaginationView
        v-model="pagination.page"
        :page_size="15"
        :total="pagination.total"
      />
    </div>

    <!-- 创建客户对话框 -->
    <el-dialog
      title="创建客户"
      v-model="createDialogVisible"
      width="500px"
    >
      <el-form
        :model="createForm"
        :rules="createRules"
        ref="createFormRef"
        label-width="100px"
      >
        <el-form-item label="客户姓名" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入客户姓名"></el-input>
        </el-form-item>
        <el-form-item label="联系电话" prop="telephone">
          <el-input v-model="createForm.telephone" placeholder="请输入联系电话"></el-input>
        </el-form-item>
        <el-form-item label="详细住址" prop="address">
          <el-input v-model="createForm.address" placeholder="请输入详细住址"></el-input>
        </el-form-item>
        <el-form-item label="客户级别" prop="level">
          <el-select v-model="createForm.level" placeholder="请选择客户级别">
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
          ></el-input>
        </el-form-item>
        <el-form-item label="所属员工" prop="staff" v-if="isBoss">
          <el-select v-model="createForm.staff" placeholder="请选择所属员工">
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
      level: [{ required: true, message: '请选择客户级别', trigger: 'change' }]
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

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
}

.filter-header {
  font-weight: bold;
}

.overdue-warning {
  color: #F56C6C;
  font-weight: bold;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}
</style>
