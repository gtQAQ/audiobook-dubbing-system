<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>个人中心</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <!-- 个人资料 Tab -->
        <el-tab-pane label="个人资料" name="info">
          <el-form :model="infoForm" label-width="100px" ref="infoFormRef" :rules="infoRules">
            <el-form-item label="用户名">
              <el-input v-model="infoForm.username" disabled />
            </el-form-item>
            <el-form-item label="角色">
               <el-tag :type="infoForm.role === 'admin' ? 'danger' : 'info'">
                 {{ infoForm.role === 'admin' ? '管理员' : '普通用户' }}
               </el-tag>
            </el-form-item>
            <el-form-item label="昵称" prop="nickname">
              <el-input v-model="infoForm.nickname" />
            </el-form-item>
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="infoForm.phone" />
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="infoForm.email" />
            </el-form-item>
            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="infoForm.gender">
                <el-radio label="男">男</el-radio>
                <el-radio label="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="updateProfile" :loading="loading">保存修改</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 修改密码 Tab -->
        <el-tab-pane label="修改密码" name="password">
          <el-form :model="pwdForm" label-width="100px" ref="pwdFormRef" :rules="pwdRules">
            <el-form-item label="旧密码" prop="old_password">
              <el-input v-model="pwdForm.old_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="pwdForm.new_password" type="password" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="warning" @click="updatePassword" :loading="pwdLoading">修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeTab = ref('info')
const loading = ref(false)
const pwdLoading = ref(false)

const infoForm = reactive({
  username: '',
  role: '',
  nickname: '',
  phone: '',
  email: '',
  gender: ''
})

const pwdForm = reactive({
  old_password: '',
  new_password: ''
})

const infoRules = {
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  email: [{ type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }]
}

const pwdRules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password: [{ required: true, message: '请输入新密码', trigger: 'blur' }]
}

const fetchProfile = async () => {
  // 获取当前用户的详细信息，并填充到表单中。
  try {
    const token = localStorage.getItem('access_token')
    const res = await axios.get('/users/me', {
      headers: { Authorization: `Bearer ${token}` }
    })
    Object.assign(infoForm, res.data)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '获取个人信息失败')
  }
}

const updateProfile = async () => {
  // 提交个人资料更新（昵称、手机、邮箱、性别）。
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    await axios.put('/users/me', infoForm, {
      headers: { Authorization: `Bearer ${token}` }
    })
    ElMessage.success('个人资料更新成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '更新失败')
  } finally {
    loading.value = false
  }
}

const updatePassword = async () => {
  // 提交密码修改请求，修改成功后强制登出。
  pwdLoading.value = true
  try {
    const token = localStorage.getItem('access_token')
    // 后端期望查询参数: old_password, new_password
    // 使用 axios 的 params 对象
    await axios.put('/users/me/password', null, {
      headers: { Authorization: `Bearer ${token}` },
      params: {
        old_password: pwdForm.old_password,
        new_password: pwdForm.new_password
      }
    })
    ElMessage.success('密码修改成功，请重新登录')
    localStorage.removeItem('access_token')
    router.push('/login')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '密码修改失败')
  } finally {
    pwdLoading.value = false
  }
}

onMounted(() => {
  fetchProfile()
})
</script>

<style scoped>
.profile-container {
  display: flex;
  justify-content: center;
}
.profile-card {
  width: 600px;
  margin-top: 20px;
}
</style>
