<template>
  <el-card class="upload-card">
    <template #header>
      <div class="card-header">
        <span>上传小说文本</span>
        <span class="header-subtitle">支持 .txt 格式，最大 10MB</span>
      </div>
    </template>
    
    <div class="upload-content">
      <el-upload
        class="upload-demo"
        drag
        action="/audio/upload_text"
        :headers="headers"
        :on-success="handleSuccess"
        :on-error="handleError"
        :before-upload="beforeUpload"
        accept=".txt"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或 <em>点击上传</em>
        </div>
      </el-upload>
    </div>

    <transition name="el-fade-in-linear">
      <div v-if="content" class="result-area">
        <div class="result-header">
          <div class="result-title">
            <el-icon><Document /></el-icon>
            <span>解析结果预览</span>
          </div>
          <div class="result-actions">
            <el-button type="primary" plain @click="copyContent">
              <el-icon><CopyDocument /></el-icon> 复制内容
            </el-button>
            <el-button type="success" @click="goToSynthesize">
              去合成语音 <el-icon class="el-icon--right"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>
        <div class="text-preview">
          <el-input
            v-model="content"
            :rows="12"
            type="textarea"
            placeholder="文件内容将显示在这里"
            resize="none"
          />
        </div>
      </div>
    </transition>
  </el-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import { UploadFilled, Document, CopyDocument, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const content = ref('')

const headers = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('access_token')}`
}))

const beforeUpload = (file) => {
  // 上传前检查：验证文件类型 (txt) 和大小 (10MB)。
  if (file.type !== 'text/plain' && !file.name.endsWith('.txt')) {
    ElMessage.error('只能上传 TXT 文件!')
    return false
  }
  if (file.size / 1024 / 1024 > 10) {
    ElMessage.error('文件大小不能超过 10MB!')
    return false
  }
  return true
}

const handleSuccess = (response) => {
  // 上传成功回调：更新内容和文件名显示。
  content.value = response.content
  ElMessage.success('上传解析成功')
}

const handleError = () => {
  // 上传失败回调：显示错误提示。
  ElMessage.error('上传失败，请重试')
}

const copyContent = () => {
  // 复制解析后的文本内容到剪贴板。
  navigator.clipboard.writeText(content.value)
  ElMessage.success('已复制到剪贴板')
}

const goToSynthesize = () => {
  // 跳转到合成页面，并携带当前文本内容。
  router.push({ name: 'Synthesize', state: { initialText: content.value } })
}
</script>

<style scoped>
.upload-card {
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.upload-card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-subtitle {
  font-size: 14px;
  color: #909399;
}

.upload-content {
  padding: 20px 0;
}

.upload-demo :deep(.el-upload-dragger) {
  width: 100%;
  height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  transition: border-color 0.3s;
}

.upload-demo :deep(.el-upload-dragger:hover) {
  border-color: #409eff;
}

.upload-demo .el-icon--upload {
  font-size: 60px;
  color: #c0c4cc;
  margin-bottom: 10px;
}

.result-area {
  margin-top: 30px;
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.result-title {
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: 500;
  color: #606266;
  gap: 8px;
}

.result-actions {
  display: flex;
  gap: 12px;
}

.text-preview :deep(.el-textarea__inner) {
  background-color: #f5f7fa;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.6;
  padding: 15px;
  border-radius: 4px;
}
</style>
