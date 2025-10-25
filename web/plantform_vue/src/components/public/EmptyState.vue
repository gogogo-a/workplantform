<template>
  <div class="empty-state">
    <div class="empty-icon">
      <el-icon :size="64"><component :is="icon" /></el-icon>
    </div>
    <p class="empty-text">{{ text }}</p>
    <p v-if="subtext" class="empty-subtext">{{ subtext }}</p>
    <slot name="action"></slot>
  </div>
</template>

<script setup>
import { Document } from '@element-plus/icons-vue'

defineProps({
  icon: {
    type: [String, Object],
    default: () => Document
  },
  text: {
    type: String,
    default: '暂无数据'
  },
  subtext: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  min-height: 300px;
}

.empty-icon {
  color: var(--text-tertiary);
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-text {
  color: var(--text-secondary);
  font-size: 16px;
  margin-bottom: 8px;
}

.empty-subtext {
  color: var(--text-tertiary);
  font-size: 14px;
  margin-bottom: 20px;
}
</style>

