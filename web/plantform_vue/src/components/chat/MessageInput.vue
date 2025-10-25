<template>
  <div class="message-input">
    <div class="input-toolbar">
      <el-button
        text
        :icon="showThinking ? View : Hide"
        @click="handleToggleThinking"
        size="small"
        :class="{ 'thinking-active': showThinking }"
        class="thinking-button"
      >
        {{ showThinking ? '显示' : '隐藏' }}思考过程
      </el-button>
      
      <el-button text :icon="Upload" size="small" @click="handleSelectFile">
        上传文件
      </el-button>
      <input
        ref="fileInputRef"
        type="file"
        accept=".pdf,.doc,.docx,.txt"
        style="display: none"
        @change="handleFileChange"
      />
    </div>

    <div class="input-container">
      <el-input
        v-model="inputMessage"
        type="textarea"
        :rows="3"
        placeholder="输入您的问题... (Shift + Enter 换行，Enter 发送)"
        :disabled="isSending"
        @keydown.enter="handleKeyDown"
        class="message-textarea"
      />
      
      <el-button
        type="primary"
        :icon="isSending ? Loading : Promotion"
        :loading="isSending"
        @click="handleSend"
        :disabled="!inputMessage.trim() || isSending"
        class="send-button"
        size="large"
      >
        {{ isSending ? '发送中...' : '发送' }}
      </el-button>
    </div>

    <!-- 已上传文件列表 -->
    <div v-if="uploadedFiles.length > 0" class="uploaded-files">
      <div
        v-for="(file, index) in uploadedFiles"
        :key="index"
        class="file-item"
      >
        <el-icon class="file-icon"><Document /></el-icon>
        <span class="file-name">{{ file.name }}</span>
        <el-icon class="remove-icon" @click="handleRemoveFile(index)"><Close /></el-icon>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore, useChatStore } from '@/store'
import { Upload, Promotion, Loading, Document, Close, View, Hide } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['send'])

const userStore = useUserStore()
const chatStore = useChatStore()

const inputMessage = ref('')
const isSending = ref(false)
const uploadedFiles = ref([]) // 暂存的文件列表
const showThinking = ref(true) // 默认显示思考过程
const fileInputRef = ref(null)

// 切换思考过程显示
const handleToggleThinking = () => {
  showThinking.value = !showThinking.value
  chatStore.toggleShowThinking()
}

// 选择文件
const handleSelectFile = () => {
  fileInputRef.value?.click()
}

// 文件选择变化
const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // 验证文件类型（移除大小限制）
  const allowedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain'
  ]
  
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('只支持 PDF、DOC、DOCX、TXT 格式的文件')
    return
  }
  
  // 暂存文件（保存原始 File 对象）
  uploadedFiles.value.push({
    name: file.name,
    size: file.size,
    type: file.type,
    file: file // 保存原始文件对象
  })
  
  ElMessage.success(`文件 ${file.name} 已添加`)
  
  // 清空 input，以便可以再次选择相同文件
  event.target.value = ''
}

// 键盘事件处理
const handleKeyDown = (event) => {
  // Shift + Enter: 换行
  if (event.shiftKey) {
    return
  }
  
  // Enter: 发送消息
  event.preventDefault()
  if (inputMessage.value.trim() && !isSending.value) {
    handleSend()
  }
}

// 发送消息
const handleSend = async () => {
  if (!inputMessage.value.trim() || isSending.value) return

  const message = inputMessage.value.trim()
  const files = [...uploadedFiles.value] // 复制文件列表
  
  inputMessage.value = ''
  uploadedFiles.value = [] // 清空文件列表
  isSending.value = true

  try {
    await emit('send', {
      content: message,
      showThinking: showThinking.value,
      files: files // 传递文件列表
    })
  } catch (error) {
    console.error('发送消息失败:', error)
  } finally {
    isSending.value = false
  }
}

// 移除文件
const handleRemoveFile = (index) => {
  uploadedFiles.value.splice(index, 1)
  ElMessage.success('文件已移除')
}

// 暴露方法给父组件
defineExpose({
  isSending
})
</script>

<style scoped>
.message-input {
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
  padding: 16px;
}

.input-toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.thinking-button {
  transition: all 0.3s ease;
  padding: 8px 16px;
  border-radius: 8px;
}

.thinking-button.thinking-active {
  background: rgba(168, 85, 247, 0.2) !important;
  color: var(--neon-purple) !important;
}

.thinking-button.thinking-active:hover {
  background: rgba(168, 85, 247, 0.3) !important;
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.message-textarea {
  flex: 1;
}

.message-textarea :deep(.el-textarea__inner) {
  background: var(--bg-tertiary);
  border-color: var(--border-color);
  color: var(--text-primary);
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  resize: none;
  transition: all 0.3s ease;
}

.message-textarea :deep(.el-textarea__inner):focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 10px rgba(99, 102, 241, 0.3);
}

.send-button {
  height: 48px;
  padding: 0 32px;
  border-radius: 24px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--neon-purple), var(--neon-blue));
  border: none;
  transition: all 0.3s ease;
}

.send-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.uploaded-files {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.file-icon {
  color: var(--primary-color);
  font-size: 16px;
}

.file-name {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-icon {
  cursor: pointer;
  color: var(--text-tertiary);
  font-size: 14px;
  transition: color 0.3s ease;
}

.remove-icon:hover {
  color: var(--danger-color);
}
</style>

