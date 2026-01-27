<template>
  <el-container class="layout-container">
    <el-aside width="220px">
      <el-menu
        :default-active="activeMenu"
        class="el-menu-vertical"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <div class="logo-container">
          <span class="logo-text">有声读物配音系统</span>
        </div>
        
        <el-menu-item index="/upload">
          <el-icon><Upload /></el-icon>
          <span>文本上传</span>
        </el-menu-item>
        
        <el-menu-item index="/synthesize">
          <el-icon><Microphone /></el-icon>
          <span>音频合成</span>
        </el-menu-item>
        
        <el-menu-item index="/history">
          <el-icon><List /></el-icon>
          <span>文件下载</span>
        </el-menu-item>
        
        <el-menu-item index="/users" v-if="isAdmin">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header>
        <div class="header-left">
          <!-- 面包屑或标题 -->
          <h3>{{ pageTitle }}</h3>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="el-dropdown-link">
              {{ nickname }}
              <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main>
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Upload, Microphone, List, User, ArrowDown } from '@element-plus/icons-vue'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const nickname = ref('User')
const isAdmin = ref(false)

const activeMenu = computed(() => route.path)

const pageTitle = computed(() => {
  // 根据路由名称动态计算页面标题。
  switch(route.name) {
    case 'Upload': return '文本上传'
    case 'Synthesize': return '音频合成'
    case 'History': return '文件下载'
    case 'Profile': return '个人中心'
    case 'Users': return '用户管理'
    default: return ''
  }
})

onMounted(async () => {
  // 组件挂载时获取当前用户信息，判断是否为管理员。
  const token = localStorage.getItem('access_token')
  if (token) {
    try {
      const res = await axios.get('/users/me', {
        headers: { Authorization: `Bearer ${token}` }
      })
      nickname.value = res.data.nickname || res.data.username
      isAdmin.value = res.data.role === 'admin'
    } catch (e) {
      if (e.response && e.response.status === 401) {
        handleCommand('logout')
      }
    }
  }
})

const handleCommand = (command) => {
  // 处理下拉菜单指令：退出登录或跳转个人中心。
  if (command === 'logout') {
    localStorage.removeItem('access_token')
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.el-aside {
  background-color: #304156;
  color: #fff;
  transition: width 0.3s;
}

.logo-container {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2b3a4d;
}

.logo-text {
  color: #fff;
  font-weight: bold;
  font-size: 18px;
}

.el-menu-vertical {
  border-right: none;
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
  color: #606266;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
