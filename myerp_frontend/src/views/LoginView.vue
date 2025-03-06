<script setup>
import { ref, reactive } from 'vue'
import loginHttp from '@/api/loginHttp'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const formLabelWidth = 80
let loginForm = ref()
let loginFormData = reactive({
  account: '',
  password: '',
})
const loginFormRules = reactive({
  account: [
    { required: true, message: '必须填写登录账号!', trigger: 'blur' },
    { min: 4, max: 20, message: '登录账号应该在4~20位之间!', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '必须填写登录密码!', trigger: 'blur' },
    { min: 6, max: 30, message: '登录密码位数不对!', trigger: 'blur' },
  ],
})

const onLogin = () => {
  loginForm.value.validate((valid, fields) => {
    if (valid) {
      loginHttp.login(loginFormData).then((result) => {
        if (result.status == 200) {
          console.log(result.data)
          authStore.setToken(result.data)
          router.push({ name: 'main' })
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
  <div class="login-container">
    <div class="login-box">
      <h3 class="title">MyERP</h3>
      <el-form ref="loginForm" :model="loginFormData" :rules="loginFormRules">
        <el-form-item label="登录账号" prop="account" :label-width="formLabelWidth">
          <el-input type="text" v-model="loginFormData.account" />
        </el-form-item>
        <el-form-item label="登录密码" prop="password" :label-width="formLabelWidth">
          <el-input type="password" v-model="loginFormData.password" />
        </el-form-item>
        <br />
        <button type="button" class="login-btn" @click="onLogin">点击登录</button>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
* {
  box-sizing: border-box;
}

.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #2c3e50, #4582be);
}

.login-box {
  background: #fff;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
  width: 100%;
  max-width: 400px;
}

.title {
  text-align: center;
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background: #6e7dff;
  border: none;
  border-radius: 4px;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s;
}

.login-btn:hover {
  background: #5a6bd8;
}
</style>
