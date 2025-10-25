<template>
  <div class="document-management">
    <div class="page-header">
      <h2 class="page-title">文档管理</h2>
      <div class="header-actions">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索文档..."
          :prefix-icon="Search"
          clearable
          @clear="handleSearch"
          @keyup.enter="handleSearch"
          style="width: 240px"
        />
        <el-upload
          ref="uploadRef"
          :action="uploadAction"
          :headers="uploadHeaders"
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
          :show-file-list="false"
          :before-upload="beforeUpload"
          accept=".pdf,.doc,.docx,.txt"
        >
          <el-button type="primary" :icon="Upload">
            上传文档
          </el-button>
        </el-upload>
        <el-button :icon="RefreshRight" @click="handleRefresh">
          刷新
        </el-button>
      </div>
    </div>

    <div class="page-content">
      <el-table
        v-loading="loading"
        :data="documentList"
        stripe
        class="document-table"
        @row-click="handleRowClick"
      >
        <el-table-column prop="uuid" label="文档 ID" width="280" show-overflow-tooltip />
        
        <el-table-column prop="name" label="文件名" min-width="200">
          <template #default="{ row }">
            <div class="file-name-cell clickable">
              <el-icon class="file-icon"><Document /></el-icon>
              <span class="file-name">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ row.status_text || '未知' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="chunk_count" label="分块数" width="100" />
        
        <el-table-column prop="uploaded_at" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.uploaded_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              text
              type="primary"
              size="small"
              @click.stop="handleViewDetail(row)"
            >
              查看
            </el-button>
            <el-button
              text
              type="danger"
              size="small"
              @click.stop="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <CustomPagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          @page-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDocumentList, deleteDocument } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Upload, RefreshRight, Document } from '@element-plus/icons-vue'
import CustomPagination from '@/components/public/CustomPagination.vue'

const router = useRouter()

const loading = ref(false)
const documentList = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchKeyword = ref('')

const uploadAction = computed(() => {
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  return `${baseURL}/documents`
})

const uploadHeaders = computed(() => {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
})

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return '-'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取状态类型
const getStatusType = (status) => {
  const typeMap = {
    0: 'info',      // 未处理
    1: 'warning',   // 处理中
    2: 'success',   // 处理完成
    3: 'danger'     // 处理失败
  }
  return typeMap[status] || 'info'
}

// 获取文档列表
const fetchDocumentList = async () => {
  loading.value = true
  try {
    const data = await getDocumentList({
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: searchKeyword.value || undefined
    })
    
    console.log('文档列表数据:', data)  // 调试日志
    
    // 处理不同的返回格式
    if (Array.isArray(data)) {
      // 如果直接返回数组
      documentList.value = data
      total.value = data.length
    } else if (data.documents) {
      // 如果返回带分页信息的对象
      documentList.value = data.documents
      total.value = data.total || 0
    } else {
      documentList.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('获取文档列表失败:', error)
    ElMessage.error('获取文档列表失败')
  } finally {
    loading.value = false
  }
}

// 文件上传前验证
const beforeUpload = (file) => {
  const maxSize = 1000 * 1024 * 1024 // 10MB
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 1000MB')
    return false
  }
  
  const allowedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain'
  ]
  
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('只支持 PDF、DOC、DOCX、TXT 格式的文件')
    return false
  }
  
  return true
}

// 文件上传成功
const handleUploadSuccess = (response) => {
  ElMessage.success('文档上传成功')
  fetchDocumentList()
}

// 文件上传失败
const handleUploadError = (error) => {
  console.error('文件上传失败:', error)
  ElMessage.error('文件上传失败，请重试')
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchDocumentList()
}

// 刷新
const handleRefresh = () => {
  currentPage.value = 1
  searchKeyword.value = ''
  fetchDocumentList()
}

// 页码变化
const handlePageChange = () => {
  fetchDocumentList()
}

// 页大小变化
const handleSizeChange = () => {
  currentPage.value = 1
  fetchDocumentList()
}

// 点击行跳转到详情
const handleRowClick = (row) => {
  router.push(`/admin/documents/${row.uuid}`)
}

// 查看详情
const handleViewDetail = (document) => {
  router.push(`/admin/documents/${document.uuid}`)
}

// 删除文档
const handleDelete = async (document) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文档 "${document.name}" 吗？此操作不可恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'error'
      }
    )
    
    await deleteDocument(document.uuid)
    
    ElMessage.success('删除成功')
    fetchDocumentList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除文档失败:', error)
      ElMessage.error('删除文档失败')
    }
  }
}

onMounted(() => {
  fetchDocumentList()
})
</script>

<style scoped>
.document-management {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 24px;
  overflow: hidden;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.page-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  overflow: hidden;
}

.document-table {
  flex: 1;
  overflow: auto;
}

.document-table :deep(.el-table__header) {
  background: var(--bg-tertiary);
}

.document-table :deep(.el-table__row) {
  background: transparent;
}

.document-table :deep(.el-table__row:hover) {
  background: rgba(99, 102, 241, 0.05);
}

.file-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-name-cell.clickable {
  cursor: pointer;
}

.file-name-cell.clickable:hover .file-name {
  color: var(--primary-color);
  text-decoration: underline;
}

.file-icon {
  color: var(--primary-color);
  font-size: 16px;
}

.file-name {
  transition: all 0.3s ease;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}
</style>

