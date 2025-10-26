<template>
  <div class="chat-message" :class="{ 'is-user': isUser, 'is-ai': !isUser }">
    <div class="message-avatar">
      <el-avatar :size="36" :class="{ 'user-avatar': isUser, 'ai-avatar': !isUser }">
        <el-icon><component :is="isUser ? User : Service" /></el-icon>
      </el-avatar>
    </div>

    <div class="message-content">
      <div class="message-header">
        <span class="message-sender">{{ isUser ? '我' : 'AI 助手' }}</span>
        <span class="message-time">{{ formatTime(message.create_at) }}</span>
      </div>

      <div class="message-body">
        <!-- 思考过程 -->
        <div v-if="!isUser && message.thinking" class="thinking-process">
          <div 
            class="thinking-header" 
            :class="{ 'is-active': isThinkingExpanded }"
            @click="toggleThinking"
          >
            <el-icon class="thinking-icon"><MagicStick /></el-icon>
            <span>{{ isThinkingExpanded ? '隐藏思考过程' : '显示思考过程' }}</span>
            <el-icon class="toggle-icon" :class="{ 'is-expanded': isThinkingExpanded }">
              <ArrowDown />
            </el-icon>
          </div>
          <transition name="thinking-expand">
            <div v-show="isThinkingExpanded" class="thinking-content">{{ message.thinking }}</div>
          </transition>
        </div>

        <!-- 观察结果 -->
        <div v-if="!isUser && message.observation" class="observation-process">
          <div 
            class="observation-header" 
            :class="{ 'is-active': isObservationExpanded }"
            @click="toggleObservation"
          >
            <el-icon class="observation-icon"><View /></el-icon>
            <span>{{ isObservationExpanded ? '隐藏观察结果' : '显示观察结果' }}</span>
            <el-icon class="toggle-icon" :class="{ 'is-expanded': isObservationExpanded }">
              <ArrowDown />
            </el-icon>
          </div>
          <transition name="observation-expand">
            <div v-show="isObservationExpanded" class="observation-content">
              <template v-if="isObservationTruncated && !isObservationFullExpanded">
                {{ truncatedObservation }}
                <span class="expand-dots" @click.stop="expandObservationFull">......</span>
              </template>
              <template v-else>
                {{ message.observation }}
              </template>
            </div>
          </transition>
        </div>

        <!-- 操作过程 -->
        <div v-if="!isUser && message.action" class="action-process">
          <div 
            class="action-header" 
            :class="{ 'is-active': isActionExpanded }"
            @click="toggleAction"
          >
            <el-icon class="action-icon"><Tools /></el-icon>
            <span>{{ isActionExpanded ? '隐藏操作过程' : '显示操作过程' }}</span>
            <el-icon class="toggle-icon" :class="{ 'is-expanded': isActionExpanded }">
              <ArrowDown />
            </el-icon>
          </div>
          <transition name="action-expand">
            <div v-show="isActionExpanded" class="action-content">{{ message.action }}</div>
          </transition>
        </div>

        <!-- 用户上传的文件（可点击查看内容） -->
        <div v-if="isUser && message.file_name" class="uploaded-file">
          <div 
            class="uploaded-file-card" 
            :class="{ 'is-expanded': isFileExpanded }"
            @click="toggleFileContent"
          >
            <div class="file-header">
              <el-icon class="file-icon"><Document /></el-icon>
              <div class="file-info">
                <span class="file-name">{{ message.file_name }}</span>
                <span class="file-size">{{ formatFileSize(message.file_size) }}</span>
              </div>
              <el-icon class="toggle-icon" :class="{ 'is-expanded': isFileExpanded }">
                <ArrowDown />
              </el-icon>
            </div>
            <transition name="file-expand">
              <div v-show="isFileExpanded" class="file-content">
                <pre>{{ fileContent }}</pre>
              </div>
            </transition>
          </div>
        </div>

        <!-- 消息文本 -->
        <div class="message-text" v-html="formatMessage(message.content)"></div>

        <!-- 流式输出动画 -->
        <span v-if="isStreaming" class="cursor-blink">|</span>

        <!-- 引用文档列表 -->
        <div v-if="!isUser && message.documents && message.documents.length > 0" class="documents-list">
          <div class="documents-header">
            <el-icon class="documents-icon"><Document /></el-icon>
            <span>引用文档 ({{ message.documents.length }})</span>
          </div>
          <div class="documents-items">
            <div
              v-for="doc in message.documents"
              :key="doc.uuid"
              class="document-item"
              @click="handleDocumentClick(doc.uuid)"
            >
              <el-icon class="doc-icon"><DocumentCopy /></el-icon>
              <span class="doc-name">{{ doc.name }}</span>
              <el-icon class="doc-arrow"><Right /></el-icon>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="message-actions">
        <el-button
          v-if="!isUser"
          text
          size="small"
          :icon="CopyDocument"
          @click="handleCopy"
        >
          复制
        </el-button>
        <el-button
          v-if="!isUser"
          text
          size="small"
          :icon="RefreshRight"
          @click="handleRegenerate"
        >
          重新生成
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { User, Service, CopyDocument, RefreshRight, ArrowDown, MagicStick, Tools, View, Document, DocumentCopy, Right } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  message: {
    type: Object,
    required: true
  },
  isStreaming: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['regenerate'])
const router = useRouter()

const isUser = props.message.role === 'user'
const isThinkingExpanded = ref(true) // 默认展开思考过程
const isObservationExpanded = ref(true) // 默认展开观察结果
const isActionExpanded = ref(true) // 默认展开操作过程
const isObservationFullExpanded = ref(false) // 观察结果是否完全展开

// 观察结果截取逻辑
const MAX_OBSERVATION_LENGTH = 200
const isObservationTruncated = ref(false)
const truncatedObservation = ref('')

// 计算观察结果是否需要截取
const checkObservationTruncation = () => {
  if (props.message.observation && props.message.observation.length > MAX_OBSERVATION_LENGTH) {
    isObservationTruncated.value = true
    truncatedObservation.value = props.message.observation.substring(0, MAX_OBSERVATION_LENGTH)
  } else {
    isObservationTruncated.value = false
    truncatedObservation.value = props.message.observation || ''
  }
}

// 初始化时检查
checkObservationTruncation()

// 切换思考过程展开/折叠
const toggleThinking = () => {
  isThinkingExpanded.value = !isThinkingExpanded.value
}

// 切换观察结果展开/折叠
const toggleObservation = () => {
  isObservationExpanded.value = !isObservationExpanded.value
}

// 切换操作过程展开/折叠
const toggleAction = () => {
  isActionExpanded.value = !isActionExpanded.value
}

// 展开观察结果全部内容
const expandObservationFull = () => {
  isObservationFullExpanded.value = true
}

// 文件展开/折叠
const isFileExpanded = ref(false)
const toggleFileContent = () => {
  isFileExpanded.value = !isFileExpanded.value
}

// 文件内容（从 extra_data 获取）
const fileContent = computed(() => {
  if (props.message.extra_data && props.message.extra_data.file_content) {
    return props.message.extra_data.file_content
  }
  return '文件内容不可用'
})

// 点击文档跳转到详情页
const handleDocumentClick = (uuid) => {
  // 所有用户都跳转到 /documents/:id，组件内部会根据角色显示不同内容
  router.push(`/documents/${uuid}`)
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

// 格式化消息（支持 Markdown 简单格式）
const formatMessage = (content) => {
  if (!content) return ''
  
  // 简单的 Markdown 格式支持
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // 加粗
    .replace(/\*(.*?)\*/g, '<em>$1</em>') // 斜体
    .replace(/`(.*?)`/g, '<code>$1</code>') // 行内代码
    .replace(/\n/g, '<br>') // 换行
}

// 复制消息
const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(props.message.content)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败')
  }
}

// 重新生成
const handleRegenerate = () => {
  emit('regenerate', props.message)
}
</script>

<style scoped>
.chat-message {
  display: flex;
  gap: 12px;
  padding: 16px;
  animation: slideInUp 0.3s ease-out;
}

.chat-message.is-user {
  background: rgba(99, 102, 241, 0.05);
}

.chat-message.is-ai:hover {
  background: rgba(255, 255, 255, 0.02);
}

.message-avatar {
  flex-shrink: 0;
}

.user-avatar {
  background: var(--primary-color);
}

.ai-avatar {
  background: linear-gradient(135deg, var(--neon-purple), var(--neon-blue));
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.message-sender {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.message-time {
  font-size: 12px;
  color: var(--text-tertiary);
}

.message-body {
  margin-bottom: 8px;
}

.thinking-process {
  background: rgba(168, 85, 247, 0.1);
  border-left: 3px solid var(--neon-purple);
  padding: 8px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.thinking-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--neon-purple);
  cursor: pointer;
  user-select: none;
  transition: all 0.3s ease;
  padding: 8px 12px;
  border-radius: 6px;
  background: transparent;
}

.thinking-header:hover {
  color: var(--neon-blue);
}

.thinking-header.is-active {
  background: rgba(168, 85, 247, 0.15);
}

.thinking-icon {
  font-size: 16px;
}

.toggle-icon {
  margin-left: auto;
  font-size: 14px;
  transition: transform 0.3s ease;
}

.toggle-icon.is-expanded {
  transform: rotate(180deg);
}

.thinking-content {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-top: 4px;
  padding: 4px 12px;
}

/* 思考过程展开/折叠动画 */
.thinking-expand-enter-active,
.thinking-expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.thinking-expand-enter-from,
.thinking-expand-leave-to {
  max-height: 0;
  opacity: 0;
  margin-top: 0;
}

.thinking-expand-enter-to,
.thinking-expand-leave-from {
  max-height: 500px;
  opacity: 1;
  margin-top: 8px;
}

/* 操作过程样式 */
.action-process {
  background: rgba(59, 130, 246, 0.1);
  border-left: 3px solid var(--neon-blue);
  padding: 8px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.action-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--neon-blue);
  cursor: pointer;
  user-select: none;
  transition: all 0.3s ease;
  padding: 8px 12px;
  border-radius: 6px;
  background: transparent;
}

.action-header:hover {
  color: var(--primary-color);
}

.action-header.is-active {
  background: rgba(59, 130, 246, 0.15);
}

.action-icon {
  font-size: 16px;
}

.action-content {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-top: 4px;
  padding: 4px 12px;
  font-family: 'Courier New', monospace;
}

/* 操作过程展开/折叠动画 */
.action-expand-enter-active,
.action-expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.action-expand-enter-from,
.action-expand-leave-to {
  max-height: 0;
  opacity: 0;
  margin-top: 0;
}

.action-expand-enter-to,
.action-expand-leave-from {
  max-height: 500px;
  opacity: 1;
  margin-top: 8px;
}

/* 观察结果样式 */
.observation-process {
  background: rgba(16, 185, 129, 0.1);
  border-left: 3px solid #10b981;
  padding: 8px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.observation-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #10b981;
  cursor: pointer;
  user-select: none;
  transition: all 0.3s ease;
  padding: 8px 12px;
  border-radius: 6px;
  background: transparent;
}

.observation-header:hover {
  color: #34d399;
}

.observation-header.is-active {
  background: rgba(16, 185, 129, 0.15);
}

.observation-icon {
  font-size: 16px;
}

.observation-content {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-top: 4px;
  padding: 4px 12px;
  white-space: pre-wrap;
}

.expand-dots {
  color: #10b981;
  font-weight: 600;
  cursor: pointer;
  user-select: none;
  transition: all 0.3s ease;
  padding: 2px 4px;
  border-radius: 4px;
  display: inline-block;
}

.expand-dots:hover {
  color: #34d399;
  background: rgba(16, 185, 129, 0.1);
}

/* 观察结果展开/折叠动画 */
.observation-expand-enter-active,
.observation-expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.observation-expand-enter-from,
.observation-expand-leave-to {
  max-height: 0;
  opacity: 0;
  margin-top: 0;
}

.observation-expand-enter-to,
.observation-expand-leave-from {
  max-height: 500px;
  opacity: 1;
  margin-top: 8px;
}

/* 用户上传的文件样式 */
.uploaded-file {
  margin-bottom: 12px;
}

.uploaded-file-card {
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}

.uploaded-file-card:hover {
  background: rgba(99, 102, 241, 0.12);
  border-color: rgba(99, 102, 241, 0.3);
}

.uploaded-file-card.is-expanded {
  background: rgba(99, 102, 241, 0.12);
}

.file-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
}

.file-header .file-icon {
  font-size: 20px;
  color: var(--neon-purple);
  flex-shrink: 0;
}

.file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.file-info .file-name {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-info .file-size {
  font-size: 12px;
  color: var(--text-tertiary);
}

.file-header .toggle-icon {
  font-size: 16px;
  color: var(--neon-purple);
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.file-header .toggle-icon.is-expanded {
  transform: rotate(180deg);
}

.file-content {
  max-height: 400px;
  overflow-y: auto;
  padding: 12px 14px;
  border-top: 1px solid rgba(99, 102, 241, 0.2);
  background: rgba(0, 0, 0, 0.2);
}

.file-content pre {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-secondary);
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
  word-break: break-all;
}

/* 文件展开/折叠动画 */
.file-expand-enter-active,
.file-expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.file-expand-enter-from,
.file-expand-leave-to {
  max-height: 0;
  opacity: 0;
}

.file-expand-enter-to,
.file-expand-leave-from {
  max-height: 400px;
  opacity: 1;
}

.documents-list {
  margin-top: 16px;
  padding: 12px;
  background: rgba(99, 102, 241, 0.05);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 8px;
}

.documents-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 8px;
}

.documents-icon {
  font-size: 16px;
}

.documents-items {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.document-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(99, 102, 241, 0.05);
  border: 1px solid rgba(99, 102, 241, 0.1);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.document-item:hover {
  background: rgba(99, 102, 241, 0.1);
  border-color: rgba(99, 102, 241, 0.3);
  transform: translateX(4px);
}

.doc-icon {
  font-size: 16px;
  color: var(--primary-color);
  flex-shrink: 0;
}

.doc-name {
  flex: 1;
  font-size: 13px;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.doc-arrow {
  font-size: 14px;
  color: var(--text-tertiary);
  flex-shrink: 0;
  transition: transform 0.3s ease;
}

.document-item:hover .doc-arrow {
  transform: translateX(4px);
  color: var(--primary-color);
}

.message-text {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.8;
  word-wrap: break-word;
}

.message-text :deep(strong) {
  font-weight: 600;
  color: var(--neon-blue);
}

.message-text :deep(em) {
  font-style: italic;
  color: var(--text-secondary);
}

.message-text :deep(code) {
  background: rgba(99, 102, 241, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: var(--neon-blue);
}

.cursor-blink {
  display: inline-block;
  width: 8px;
  height: 16px;
  margin-left: 2px;
  background: var(--neon-blue);
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  50% {
    opacity: 0;
  }
}

.message-actions {
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.chat-message:hover .message-actions {
  opacity: 1;
}

.message-actions .el-button {
  color: var(--text-tertiary);
}

.message-actions .el-button:hover {
  color: var(--primary-color);
}
</style>

