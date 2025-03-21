<script setup>
import { ref, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import FormDialog from '@/components/FormDialog.vue'
import loginHttp from '@/api/loginHttp'

const router = useRouter()

/**用户信息 */
const authStore = useAuthStore()

/**侧边栏 */
let isCollapse = ref(false)

const toggleAside = () => {
  isCollapse.value = !isCollapse.value
}

/**退出登录 */
const logout = () => {
  ElMessageBox.confirm('即将退出登录,确认?', '退出登录?', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      ElMessage.success('成功退出!')
      authStore.clearToken()
      router.push({ name: 'login' })
    })
    .catch(() => {
      ElMessage.info('取消退出!')
    })
}

/**表单开关 */
let dialogVisible = ref(false)
const toggleResetPasswordForm = () => {
  dialogVisible.value = true
}

/**修改密码 */
let resetPasswordForm = ref()
let resetPasswordFormData = reactive({
  user: authStore.user,
  old_password: '',
  new_password: '',
  check_new_password: '',
})
const resetPasswordFormRules = reactive({
  old_password: [
    { required: true, message: '必须填写旧密码!', trigger: 'blur' },
    { min: 6, max: 30, message: '密码长度必须在6~30位之间!', trigger: 'blur' },
  ],

  new_password: [
    { required: true, message: '必须填写新密码!', trigger: 'blur' },
    { min: 6, max: 30, message: '密码长度必须在6~30位之间!', trigger: 'blur' },
  ],

  check_new_password: [
    { required: true, message: '务必再次确认新密码!', trigger: 'blur' },
    { min: 6, max: 30, message: '密码长度必须在6~30位之间!', trigger: 'blur' },
  ],
})

const resetPassword = () => {
  resetPasswordForm.value.validate((valid, fields) => {
    if (valid) {
      loginHttp.resetPassword(resetPasswordFormData, authStore.user.uid).then((result) => {
        if (result.status == 200) {
          ElMessage.success(result.data.message)
          ElMessage.success('请您重新登录!')
          authStore.clearToken()
          router.push({ name: 'login' })
        } else {
          ElMessage.error(result.data.detail)
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
</script>

<template>
  <el-container class="main-container">
    <!-- 导航部分 -->
    <el-menu class="side-bar" text-color="#fff" active-text-color="#ffd04b" background-color="#2C3E50"
      default-active="1" :collapse="isCollapse" :router="true">
      <!-- logo -->
      <el-menu-item index="1" class="brand" :route="{ name: 'home' }">
        <el-icon>
          <HomeFilled />
        </el-icon>
        <span v-show="!isCollapse">myerp</span>
      </el-menu-item>


      <el-menu-item index="2" :route="{ name: 'client_list' }">
        <el-icon>
          <User />
        </el-icon>
        <span>客户管理</span>
      </el-menu-item>

      <!-- 系统管理菜单 - 只对老板和门店经理显示 -->
      <el-sub-menu index="3" v-if="authStore.hasPermission('system_management')">
        <template #title>
          <el-icon>
            <el-icon>
              <Tools />
            </el-icon>
          </el-icon>
          <span>系统管理</span>
        </template>
        <el-menu-item index="3-1" :route="{ name: 'brandandcategory' }" v-if="authStore.hasPermission('staff_management')">
          <el-icon>
            <Menu />
          </el-icon>
          <span>品牌种类</span>
        </el-menu-item>
        <!-- 员工管理只对老板显示 -->
        <el-menu-item index="3-2" :route="{ name: 'staff' }" v-if="authStore.hasPermission('staff_management')">
          <el-icon>
            <Avatar />
          </el-icon>
          <span>员工管理</span>
        </el-menu-item>
        <el-menu-item index="3-3" :route="{ name: 'installer' }">
          <el-icon>
            <Van />
          </el-icon>
          <span>安装师傅</span>
        </el-menu-item>
      </el-sub-menu>

      <!-- 库存管理菜单 -->
      <el-sub-menu index="4" v-if="authStore.isBoss || authStore.isStorekeeper">
        <template #title>
          <el-icon>
            <Grid />
          </el-icon>
          <span>库存管理</span>
        </template>
        <!-- 只对老板显示的菜单项 -->
        <el-menu-item index="4-1" :route="{ name: 'inventory_purchase' }"
          v-if="authStore.hasPermission('inventory_all')">
          <el-icon>
            <ShoppingCart />
          </el-icon>
          <span>申请发货</span>
        </el-menu-item>
        <el-menu-item index="4-2" :route="{ name: 'inventory_purchase_list' }"
          v-if="authStore.hasPermission('inventory_all')">
          <el-icon>
            <List />
          </el-icon>
          <span>发货记录</span>
        </el-menu-item>
        <!-- 对老板和仓库管理员都显示的菜单项 -->
        <el-menu-item index="4-3" :route="{ name: 'inventory_receive' }"
          v-if="authStore.hasPermission('inventory_receive')">
          <el-icon>
            <ShoppingCartFull />
          </el-icon>
          <span>收货入库</span>
        </el-menu-item>
        <el-menu-item index="4-4" :route="{ name: 'inventory_receive_list' }"
          v-if="authStore.hasPermission('inventory_receive')">
          <el-icon>
            <Checked />
          </el-icon>
          <span>收货记录</span>
        </el-menu-item>
        <!-- 只对老板显示的菜单项 -->
        <el-menu-item index="4-5" :route="{ name: 'inventory_list' }" v-if="authStore.hasPermission('inventory_all')">
          <el-icon>
            <Tickets />
          </el-icon>
          <span>库存列表</span>
        </el-menu-item>
        <el-menu-item index="4-6" :route="{ name: 'inventory_excel' }" v-if="authStore.hasPermission('inventory_all')">
          <el-icon>
            <DCaret />
          </el-icon>
          <span>盘点备份</span>
        </el-menu-item>
      </el-sub-menu>

      <!-- 订单管理菜单 - 只对老板和门店经理显示 -->
      <el-sub-menu index="5" v-if="authStore.hasPermission('order_management')">
        <template #title>
          <el-icon>
            <Document />
          </el-icon>
          <span>订单管理</span>
        </template>
        <el-menu-item index="5-1" :route="{ name: 'order_create' }">
          <el-icon>
            <CirclePlus />
          </el-icon>
          <span>创建订单</span>
        </el-menu-item>
        <el-menu-item index="5-2" :route="{ name: 'order_list' }">
          <el-icon>
            <List />
          </el-icon>
          <span>订单列表</span>
        </el-menu-item>
      </el-sub-menu>
    </el-menu>

    <!-- 页面主体 -->
    <el-container class="main-body">
      <!-- 页面头部 -->
      <el-header class="header">
        <el-tooltip content="展开/收起" placement="right" effect="light">
          <div>
            <el-button @click="toggleAside" v-show="!isCollapse">
              <el-icon>
                <Fold />
              </el-icon>
            </el-button>
            <el-button @click="toggleAside" v-show="isCollapse">
              <el-icon>
                <Expand />
              </el-icon>
            </el-button>
          </div>
        </el-tooltip>

        <div v-if="authStore.isLogined">
          <el-dropdown>
            <el-button>
              <el-icon>
                <UserFilled />
              </el-icon>
              <span>&nbsp;&nbsp;&nbsp;{{ authStore.user.name }}</span>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="toggleResetPasswordForm()">
                  <el-icon>
                    <Refresh />
                  </el-icon>
                  <span>修改密码</span>
                </el-dropdown-item>
                <el-dropdown-item @click="logout">
                  <el-icon>
                    <Close />
                  </el-icon>
                  <span>退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主体内容 -->
      <el-main><router-view></router-view></el-main>
      <el-footer>
        <div class="copyright-container">
          <div class="copyright-line">
            <span class="copyright-text">版权所有 © 2025</span>
            <span class="author-name">HarryWebAI(刘浩宇)</span>
            <span class="copyright-text">保留所有权利</span>
          </div>
          <div class="copyright-decoration"></div>
        </div>
      </el-footer>
    </el-container>
  </el-container>

  <!-- 表单 -->
  <FormDialog v-model="dialogVisible" title="修改密码" @submit="resetPassword">
    <el-form :model="resetPasswordFormData" :rules="resetPasswordFormRules" ref="resetPasswordForm" :label-width="80">
      <el-form-item label="旧密码" prop="old_password">
        <el-input type="password" v-model="resetPasswordFormData.old_password" />
      </el-form-item>
      <el-form-item label="新的密码" prop="new_password">
        <el-input type="password" v-model="resetPasswordFormData.new_password" />
      </el-form-item>
      <el-form-item label="再输一次" prop="check_new_password">
        <el-input type="password" v-model="resetPasswordFormData.check_new_password" />
      </el-form-item>
    </el-form>
  </FormDialog>
</template>

<style scoped>
.main-container {
  background-color: #fdfdfd;
  height: 100vh;
  overflow: hidden;
  display: flex;
}

.side-bar {
  height: 100vh;
  overflow-y: auto;
  overflow-x: hidden;
}

.main-body {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.brand {
  height: 80px;
  font-size: large;
  font-weight: bold;
  background-color: #233241;
}

.header {
  height: 80px;
  background-color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.el-main {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  box-sizing: border-box;
}

.el-footer {
  flex-shrink: 0;
}

/* 版权声明样式 */
.copyright-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 0;
}

.copyright-line {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 5px;
}

.copyright-text {
  color: #909399;
  font-size: 13px;
}

.author-name {
  color: #409EFF;
  font-weight: bold;
  font-size: 16px;
  letter-spacing: 1px;
  padding: 0 5px;
  position: relative;
  transition: all 0.3s ease;
}

.author-name:hover {
  color: #66b1ff;
  transform: scale(1.05);
  text-shadow: 0 0 8px rgba(64, 158, 255, 0.4);
}

.copyright-decoration {
  width: 100px;
  height: 2px;
  background: linear-gradient(90deg, transparent, #409EFF, transparent);
  margin: 5px 0;
}
</style>
