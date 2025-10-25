<template>
  <div class="register-view">
    <div class="register-container slide-in-up">
      <div class="register-card card">
        <RegisterForm />
      </div>
    </div>
  </div>
</template>

<script setup>
import RegisterForm from '@/components/login/RegisterForm.vue'
</script>

<style scoped>
.register-view {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.register-container {
  width: 100%;
  max-width: 450px;
}

.register-card {
  padding: 40px;
  background: rgba(21, 25, 50, 0.9);
  backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.register-card:hover {
  border-color: var(--neon-purple);
  box-shadow: 0 0 30px rgba(168, 85, 247, 0.3);
}
</style>

