<template>
  <div class="custom-pagination">
    <div class="pagination-info">
      <span class="total-text">共 {{ total }} 条</span>
    </div>
    
    <div class="pagination-controls">
      <!-- 每页显示条数 -->
      <div class="page-size-selector">
        <span class="label">每页</span>
        <div class="select-wrapper">
          <select v-model="internalPageSize" @change="handlePageSizeChange" class="page-size-select">
            <option v-for="size in pageSizes" :key="size" :value="size">{{ size }}</option>
          </select>
          <svg class="select-arrow" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M2 4L6 8L10 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span class="label">条</span>
      </div>
      
      <!-- 分页按钮 -->
      <div class="pagination-buttons">
        <button 
          class="page-btn"
          :class="{ disabled: currentPage === 1 }"
          :disabled="currentPage === 1"
          @click="handlePrevious"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M10 12L6 8L10 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        
        <button 
          v-for="page in visiblePages" 
          :key="page"
          class="page-btn page-number"
          :class="{ active: page === currentPage, ellipsis: page === '...' }"
          :disabled="page === '...'"
          @click="handlePageClick(page)"
        >
          {{ page }}
        </button>
        
        <button 
          class="page-btn"
          :class="{ disabled: currentPage === totalPages }"
          :disabled="currentPage === totalPages"
          @click="handleNext"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M6 4L10 8L6 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
      
      <!-- 跳转 -->
      <div class="page-jumper">
        <span class="label">跳至</span>
        <input 
          v-model.number="jumpPage" 
          type="number" 
          class="jump-input"
          min="1"
          :max="totalPages"
          @keyup.enter="handleJump"
        />
        <span class="label">页</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  currentPage: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 20
  },
  total: {
    type: Number,
    default: 0
  },
  pageSizes: {
    type: Array,
    default: () => [10, 20, 50, 100]
  }
})

const emit = defineEmits(['update:currentPage', 'update:pageSize', 'page-change', 'size-change'])

const internalPageSize = ref(props.pageSize)
const jumpPage = ref(props.currentPage)

// 计算总页数
const totalPages = computed(() => {
  return Math.ceil(props.total / props.pageSize) || 1
})

// 计算可见的页码
const visiblePages = computed(() => {
  const pages = []
  const showPages = 7 // 显示的页码数量
  const halfShow = Math.floor(showPages / 2)
  
  if (totalPages.value <= showPages) {
    // 总页数少于显示数量，全部显示
    for (let i = 1; i <= totalPages.value; i++) {
      pages.push(i)
    }
  } else {
    // 总页数多于显示数量，智能显示
    if (props.currentPage <= halfShow + 1) {
      // 当前页在前面
      for (let i = 1; i <= showPages - 2; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(totalPages.value)
    } else if (props.currentPage >= totalPages.value - halfShow) {
      // 当前页在后面
      pages.push(1)
      pages.push('...')
      for (let i = totalPages.value - showPages + 3; i <= totalPages.value; i++) {
        pages.push(i)
      }
    } else {
      // 当前页在中间
      pages.push(1)
      pages.push('...')
      for (let i = props.currentPage - 1; i <= props.currentPage + 1; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(totalPages.value)
    }
  }
  
  return pages
})

// 监听 pageSize 变化
watch(() => props.pageSize, (newVal) => {
  internalPageSize.value = newVal
})

// 监听 currentPage 变化
watch(() => props.currentPage, (newVal) => {
  jumpPage.value = newVal
})

// 上一页
const handlePrevious = () => {
  if (props.currentPage > 1) {
    const newPage = props.currentPage - 1
    emit('update:currentPage', newPage)
    emit('page-change', newPage)
  }
}

// 下一页
const handleNext = () => {
  if (props.currentPage < totalPages.value) {
    const newPage = props.currentPage + 1
    emit('update:currentPage', newPage)
    emit('page-change', newPage)
  }
}

// 点击页码
const handlePageClick = (page) => {
  if (page === '...' || page === props.currentPage) return
  emit('update:currentPage', page)
  emit('page-change', page)
}

// 修改每页显示条数
const handlePageSizeChange = () => {
  emit('update:pageSize', internalPageSize.value)
  emit('size-change', internalPageSize.value)
  emit('update:currentPage', 1)
  emit('page-change', 1)
}

// 跳转页码
const handleJump = () => {
  if (jumpPage.value && jumpPage.value >= 1 && jumpPage.value <= totalPages.value) {
    emit('update:currentPage', jumpPage.value)
    emit('page-change', jumpPage.value)
  } else {
    jumpPage.value = props.currentPage
  }
}
</script>

<style scoped>
.custom-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.pagination-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.total-text {
  color: rgba(255, 255, 255, 0.7);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 每页显示条数选择器 */
.page-size-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
}

.select-wrapper {
  position: relative;
  display: inline-block;
}

.page-size-select {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background-color: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.9);
  padding: 6px 28px 6px 12px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
  outline: none;
}

.page-size-select:hover {
  background-color: rgba(255, 255, 255, 0.08);
  border-color: rgba(102, 126, 234, 0.5);
}

.page-size-select:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.select-arrow {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 12px;
  height: 12px;
  color: rgba(255, 255, 255, 0.6);
  pointer-events: none;
}

/* 分页按钮 */
.pagination-buttons {
  display: flex;
  align-items: center;
  gap: 6px;
}

.page-btn {
  min-width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
  outline: none;
  padding: 0 8px;
}

.page-btn:hover:not(.disabled):not(.ellipsis) {
  background-color: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.5);
  color: #fff;
  transform: translateY(-1px);
}

.page-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: transparent;
  color: #fff;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.page-btn.disabled {
  cursor: not-allowed;
  opacity: 0.4;
}

.page-btn.ellipsis {
  cursor: default;
  border-color: transparent;
  background-color: transparent;
}

.page-btn.ellipsis:hover {
  background-color: transparent;
  transform: none;
}

/* 跳转输入框 */
.page-jumper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.jump-input {
  width: 50px;
  height: 32px;
  background-color: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.9);
  padding: 0 8px;
  font-size: 13px;
  text-align: center;
  transition: all 0.3s ease;
  outline: none;
}

.jump-input:hover {
  background-color: rgba(255, 255, 255, 0.08);
  border-color: rgba(102, 126, 234, 0.5);
}

.jump-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

/* 移除数字输入框的箭头 */
.jump-input::-webkit-inner-spin-button,
.jump-input::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.jump-input[type="number"] {
  -moz-appearance: textfield;
}

/* 响应式 */
@media (max-width: 768px) {
  .custom-pagination {
    flex-direction: column;
    gap: 16px;
  }
  
  .pagination-controls {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>

