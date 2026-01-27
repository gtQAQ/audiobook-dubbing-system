<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>文件下载列表</span>
      </div>
    </template>
    
    <el-table :data="tableData" style="width: 100%" v-loading="loading">
      <el-table-column prop="emo_type" label="情感" width="120">
        <template #default="scope">
          <el-tag :type="getEmoTag(scope.row.emo_type)">
            {{ getEmoLabel(scope.row.emo_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="创建时间" width="180">
        <template #default="scope">
          {{ formatDate(scope.row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column label="音频试听">
        <template #default="scope">
          <audio controls :src="scope.row.audio_path" class="mini-audio"></audio>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="scope">
          <el-button type="primary" link @click="download(scope.row)">下载</el-button>
          <el-popconfirm title="确定删除吗?" @confirm="handleDelete(scope.row)">
            <template #reference>
              <el-button type="danger" link>删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const tableData = ref([])
const loading = ref(false)

const emoMap = {
  0: '喜',
  1: '怒',
  2: '哀',
  3: '惧'
}

const getEmoLabel = (type) => emoMap[type] || '未知'
const getEmoTag = (type) => {
  // 根据情感类型返回对应的标签样式 (success, danger, etc.)
  switch(type) {
    case 0: return 'success'
    case 1: return 'danger'
    case 2: return 'info'
    case 3: return 'warning'
    default: return ''
  }
}

const formatDate = (dateStr) => {
  // 格式化日期字符串为本地时间格式。
  return new Date(dateStr).toLocaleString()
}

const fetchData = async () => {
  // 获取当前用户的音频历史记录。
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const res = await axios.get('/audio/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    tableData.value = res.data
  } catch (error) {
    ElMessage.error('获取列表失败')
  } finally {
    loading.value = false
  }
}

const handleDelete = async (row) => {
  // 删除指定的音频记录。
  try {
    const token = localStorage.getItem('access_token')
    await axios.delete(`/audio/${row.id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const download = (row) => {
  // 触发音频文件的浏览器下载。
  const link = document.createElement('a')
  link.href = row.audio_path
  link.download = `audio_${row.id}.wav`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.mini-audio {
  height: 30px;
  width: 100%;
}
</style>
