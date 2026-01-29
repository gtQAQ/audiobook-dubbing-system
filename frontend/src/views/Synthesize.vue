<template>
  <div class="synthesize-container">
    <el-row>
      <el-col :span="24">
        <el-card class="box-card" style="margin-bottom: 20px;">
          <template #header>
            <div class="card-header">
              <span>音频合成设置</span>
            </div>
          </template>
          
          <el-form :model="form" label-width="80px">
            <el-form-item label="情感">
              <el-select v-model="form.emo_type" placeholder="请选择情感" style="width: 100%">
                <el-option label="喜" :value="0" />
                <el-option label="怒" :value="1" />
                <el-option label="哀" :value="2" />
                <el-option label="惧" :value="3" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="文本内容">
              <el-input
                v-model="form.text"
                type="textarea"
                :rows="10"
                placeholder="请输入要合成的文本"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="synthesize" :loading="loading" class="full-width">
                开始合成
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row>
      <el-col :span="24">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>合成结果</span>
            </div>
          </template>
          
          <div v-if="audioPath" class="result-container">
            <div class="audio-player">
              <audio controls :src="audioUrl" style="width: 100%"></audio>
            </div>
            
            <div class="actions">
              <el-button type="success" @click="saveAudio" :loading="saving">保存到文件下载</el-button>
              <el-button type="info" @click="downloadAudio">下载音频</el-button>
            </div>
          </div>
          
          <el-empty v-else description="暂无合成结果，请在上方输入并合成" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const form = reactive({
  text: '',
  emo_type: 0
})

const loading = ref(false)
const saving = ref(false)
const audioPath = ref('')
const router = useRouter()

const audioUrl = computed(() => {
  // 使用相对路径，因为我们代理或从同一源服务
  return audioPath.value
})

onMounted(() => {
  if (history.state.initialText) {
    form.text = history.state.initialText
  }
})

const synthesize = async () => {
  // 调用后端 API 进行音频合成。
  if (!form.text) {
    ElMessage.warning('请输入文本')
    return
  }
  
  loading.value = true
  try {
    const formData = new FormData()
    formData.append('text', form.text)
    formData.append('emo_type', form.emo_type)
    
    const token = localStorage.getItem('access_token')
    const res = await axios.post('/audio/synthesize', formData, {
        headers: { Authorization: `Bearer ${token}` }
    })
    
    audioPath.value = res.data.audio_path
    ElMessage.success('合成成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '合成失败')
  } finally {
    loading.value = false
  }
}

const saveAudio = async () => {
  // 将 /output/temp 下的合成音频提交为持久记录，并创建数据库记录。
  saving.value = true
  try {
    const formData = new FormData()
    formData.append('audio_path', audioPath.value)
    formData.append('emo_type', form.emo_type)
    
    const token = localStorage.getItem('access_token')
    await axios.post('/audio/save', formData, {
        headers: { Authorization: `Bearer ${token}` }
    })
    
    ElMessage.success('保存成功')
    router.push('/history')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

const downloadAudio = () => {
  // 下载合成的音频文件到本地。
  const link = document.createElement('a')
  link.href = audioUrl.value
  
  // 格式化当前时间为 YYYYMMDDHHmmss
  const now = new Date()
  const timestamp = now.getFullYear() +
    String(now.getMonth() + 1).padStart(2, '0') +
    String(now.getDate()).padStart(2, '0') +
    String(now.getHours()).padStart(2, '0') +
    String(now.getMinutes()).padStart(2, '0') +
    String(now.getSeconds()).padStart(2, '0')

  const emoMap = { 0: '喜', 1: '怒', 2: '哀', 3: '惧' }
  const emoLabel = emoMap[form.emo_type] || '未知'
  
  link.download = `试听_${emoLabel}_${timestamp}.wav`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>

<style scoped>
.full-width {
  width: 100%;
}
.result-container {
  text-align: center;
}
.audio-player {
  margin: 30px 0;
}
.actions {
  display: flex;
  justify-content: center;
  gap: 20px;
}
</style>
