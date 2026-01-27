<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>用户管理 (管理员)</span>
        <el-button type="primary" @click="openCreateDialog">新增用户</el-button>
      </div>
    </template>
    
    <div class="search-bar" style="margin-bottom: 20px;">
      <el-input
        v-model="searchQuery"
        placeholder="请输入用户名或手机号搜索"
        clearable
        prefix-icon="Search"
        @input="handleSearch"
      />
    </div>
    
    <el-table :data="filteredData" style="width: 100%" v-loading="loading">
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="nickname" label="昵称" />
      <el-table-column prop="gender" label="性别" width="80" />
      <el-table-column prop="role" label="角色">
        <template #default="scope">
          <el-tag :type="scope.row.role === 'admin' ? 'danger' : 'info'">
            {{ scope.row.role }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="phone" label="手机号" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column label="操作" width="250">
        <template #default="scope">
          <el-button type="primary" link @click="openEditDialog(scope.row)">修改</el-button>
          <el-popconfirm title="重置密码为 123456 ?" @confirm="resetPassword(scope.row)">
            <template #reference>
              <el-button type="warning" link>重置密码</el-button>
            </template>
          </el-popconfirm>
          <el-popconfirm title="确定删除用户吗?" @confirm="handleDelete(scope.row)">
            <template #reference>
              <el-button type="danger" link>删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- Create/Edit User Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle">
      <el-form :model="userForm" label-width="80px" :rules="userRules" ref="userFormRef">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="isEditMode" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEditMode">
          <el-input v-model="userForm.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="userForm.nickname" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="userForm.gender">
            <el-radio label="男">男</el-radio>
            <el-radio label="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="角色" prop="role">
           <el-select v-model="userForm.role">
              <el-option label="普通用户" value="user" />
              <el-option label="管理员" value="admin" />
           </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitUser" :loading="dialogLoading">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const tableData = ref([])
const loading = ref(false)
const searchQuery = ref('')
const dialogVisible = ref(false)
const dialogLoading = ref(false)
const isEditMode = ref(false)
const userFormRef = ref(null)

const userForm = reactive({
  id: null,
  username: '',
  password: '',
  nickname: '',
  phone: '',
  email: '',
  gender: '男',
  role: 'user'
})

const userRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }]
}

const dialogTitle = computed(() => isEditMode.value ? '修改用户' : '新增用户')

// 客户端过滤：根据搜索框内容过滤用户列表 (用户名或手机号)。
const filteredData = computed(() => {
  if (!searchQuery.value) return tableData.value
  const query = searchQuery.value.toLowerCase()
  return tableData.value.filter(user => 
    user.username.toLowerCase().includes(query) || 
    (user.phone && user.phone.includes(query))
  )
})

const fetchData = async () => {
  // 获取所有用户列表 (仅限管理员)。
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const res = await axios.get('/users/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    tableData.value = res.data
  } catch (error) {
    ElMessage.error('获取用户列表失败 (权限不足?)')
  } finally {
    loading.value = false
  }
}

const handleDelete = async (row) => {
  // 删除指定用户。
  try {
    const token = localStorage.getItem('access_token')
    await axios.delete(`/users/${row.id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const resetPassword = async (row) => {
  // 重置指定用户的密码。
  try {
    const token = localStorage.getItem('access_token')
    await axios.post(`/users/${row.id}/reset_password`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    })
    ElMessage.success('重置成功')
  } catch (error) {
    ElMessage.error('重置失败')
  }
}

const openCreateDialog = () => {
  // 打开新增用户对话框，重置表单。
  isEditMode.value = false
  Object.assign(userForm, {
    id: null,
    username: '',
    password: '',
    nickname: '',
    phone: '',
    email: '',
    gender: '男',
    role: 'user'
  })
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  // 打开编辑用户对话框，填充用户数据。
  isEditMode.value = true
  Object.assign(userForm, row)
  dialogVisible.value = true
}

const submitUser = async () => {
  // 提交用户表单 (新增或修改)。
  if (!userFormRef.value) return
  
  // 仅在创建模式下验证密码
  if (isEditMode.value) {
     // 暂时移除密码验证规则或忽略
     // 实际上 Element Plus 基于 rules 属性进行验证。
     // 如果是编辑模式，我们可以将密码设置为虚拟值？
     // 或者更好的是，使规则变为条件性的。
  }

  await userFormRef.value.validate(async (valid) => {
    if (valid) {
      dialogLoading.value = true
      try {
        const token = localStorage.getItem('access_token')
        if (isEditMode.value) {
          // 编辑用户 - 调用更新接口 (假设后端支持 PUT /users/{id})
          await axios.put(`/users/${userForm.id}`, userForm, {
             headers: { Authorization: `Bearer ${token}` }
          })
          ElMessage.success('修改成功')
        } else {
          // 创建用户 - 调用注册接口
          await axios.post('/register', userForm)
          ElMessage.success('新增成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '操作失败')
      } finally {
        dialogLoading.value = false
      }
    }
  })
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
