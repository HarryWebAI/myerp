<script setup>
import { ref, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import MainBox from '@/components/MainBox.vue'
import FormDialog from '@/components/FormDialog.vue'

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
    { required: true, message: '必须填写旧密码', trigger: 'blur' },
    { min: 6, max: 30, message: '密码长度必须在6~30位之间', trigger: 'blur' },
  ],

  new_password: [
    { required: true, message: '必须填写旧密码', trigger: 'blur' },
    { min: 6, max: 30, message: '密码长度必须在6~30位之间', trigger: 'blur' },
  ],

  check_new_password: [
    { required: true, message: '必须填写旧密码', trigger: 'blur' },
    { min: 6, max: 30, message: '密码长度必须在6~30位之间', trigger: 'blur' },
  ],
})

const resetPassword = () => {
  console.log(resetPasswordFormData)
}
</script>

<template>
  <el-container>
    <!-- 导航部分 -->
    <el-menu
      class="side-bar"
      text-color="#fff"
      active-text-color="#ffd04b"
      background-color="#2C3E50"
      default-active="1"
      :collapse="isCollapse"
    >
      <!-- logo -->
      <el-menu-item index="1" class="brand">
        <router-link to="/" class="brand-logo">
          <el-icon><HomeFilled /></el-icon>
          <span v-show="!isCollapse">myerp</span>
        </router-link>
      </el-menu-item>

      <!-- 菜单 -->
      <el-sub-menu index="2">
        <template #title>
          <el-icon><location /></el-icon>
          <span>导航占位1</span>
        </template>
        <el-menu-item index="2-1">1-1</el-menu-item>
        <el-menu-item index="2-2">1-2</el-menu-item>
      </el-sub-menu>
    </el-menu>

    <!-- 主体部分 -->
    <el-container class="right-box">
      <!-- 页面头部 -->
      <el-header class="header">
        <div>
          <el-button @click="toggleAside" v-show="!isCollapse">
            <el-icon><Fold /></el-icon>
          </el-button>
          <el-button @click="toggleAside" v-show="isCollapse">
            <el-icon><Expand /></el-icon>
          </el-button>
        </div>

        <div v-if="authStore.isLogined">
          <el-dropdown>
            <el-button>
              <el-icon><UserFilled /></el-icon>
              <span>&nbsp;&nbsp;&nbsp;{{ authStore.user.name }}</span>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="toggleResetPasswordForm()">
                  <el-icon><Refresh /></el-icon>
                  <span>修改密码</span>
                </el-dropdown-item>
                <el-dropdown-item @click="logout">
                  <el-icon><Close /></el-icon>
                  <span>退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 页面主体 -->
      <MainBox title="主页"></MainBox>
    </el-container>
  </el-container>

  <!-- 表单 -->
  <FormDialog v-model="dialogVisible" title="修改密码" @submit="resetPassword">
    <el-form
      :model="resetPasswordFormData"
      :rules="resetPasswordFormRules"
      ref="resetPasswordForm"
      :label-width="80"
    >
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
.side-bar {
  height: 100vh;
}
.brand {
  height: 80px;
  background-color: #233241;
}
.brand-logo {
  text-decoration: none;
  font-size: 25px;
  font-weight: bold;
  color: #fff;
}
.right-box {
  background-color: #fdfdfd;
}
.header {
  background-color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 80px;
  margin-bottom: 20px;
}
</style>
