<template>
  <div class="login-container">
    <div class="login-card">
      <div class="title-container">
        <h2>有声读物配音系统</h2>
      </div>
      
      <el-tabs v-model="activeTab" class="login-tabs">
        <el-tab-pane label="登录" name="login">
          <el-form :model="loginForm" :rules="rules" ref="loginFormRef">
            <el-form-item prop="username">
              <el-input 
                v-model="loginForm.username" 
                placeholder="用户名" 
                prefix-icon="User"
              />
            </el-form-item>
            <el-form-item prop="password">
              <el-input 
                v-model="loginForm.password" 
                placeholder="密码" 
                prefix-icon="Lock" 
                type="password" 
                show-password
                @keyup.enter="handleLogin"
              />
            </el-form-item>
            <el-button type="primary" class="full-width" :loading="loading" @click="handleLogin">
              登录
            </el-button>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="注册" name="register">
          <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef">
            <el-form-item prop="username">
              <el-input v-model="registerForm.username" placeholder="用户名" prefix-icon="User" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input v-model="registerForm.password" placeholder="密码" prefix-icon="Lock" type="password" />
            </el-form-item>
            <el-form-item prop="nickname">
              <el-input v-model="registerForm.nickname" placeholder="昵称" prefix-icon="Postcard" />
            </el-form-item>
            <el-form-item prop="phone">
              <el-input v-model="registerForm.phone" placeholder="手机号" prefix-icon="Iphone" />
            </el-form-item>
             <el-form-item prop="email">
              <el-input v-model="registerForm.email" placeholder="邮箱" prefix-icon="Message" />
            </el-form-item>
            <el-form-item prop="gender">
               <el-radio-group v-model="registerForm.gender">
                  <el-radio label="男">男</el-radio>
                  <el-radio label="女">女</el-radio>
                </el-radio-group>
            </el-form-item>
            <el-button type="success" class="full-width" :loading="loading" @click="handleRegister">
              注册
            </el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, Postcard, Iphone, Message } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const activeTab = ref('login')
const loading = ref(false)
const loginFormRef = ref(null)
const registerFormRef = ref(null)

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  password: '',
  nickname: '',
  phone: '',
  email: '',
  gender: '男'
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const registerRules = {
  ...rules,
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }]
}

const handleLogin = async () => {
  // 处理登录逻辑：验证表单，请求 Token，保存并跳转。
  if (!loginFormRef.value) return
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const formData = new FormData()
        formData.append('username', loginForm.username)
        formData.append('password', loginForm.password)
        
        const res = await axios.post('/token', formData)
        localStorage.setItem('access_token', res.data.access_token)
        ElMessage.success('登录成功')
        router.push('/upload')
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '登录失败')
      } finally {
        loading.value = false
      }
    }
  })
}

const handleRegister = async () => {
  // 处理注册逻辑：验证表单，提交注册，成功后切换至登录页。
  if (!registerFormRef.value) return
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await axios.post('/register', registerForm)
        ElMessage.success('注册成功，请登录')
        activeTab.value = 'login'
        loginForm.username = registerForm.username
        loginForm.password = registerForm.password
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '注册失败')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #1f2a3c 0%, #3e5f7a 100%);
}

.login-card {
  width: 400px;
  background: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}

.title-container {
  text-align: center;
  margin-bottom: 20px;
  color: #304156;
}

.full-width {
  width: 100%;
}
</style>
