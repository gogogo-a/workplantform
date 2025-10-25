<template>
  <div class="simple-background"></div>
</template>

<script setup>
// 简单的渐变背景，无动画，性能最优
</script>

<style scoped>
.simple-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  background: linear-gradient(
    180deg,
    #0a0e27 0%,
    #151932 25%,
    #1e2139 50%,
    #151932 75%,
    #0a0e27 100%
  );
  /* 添加一些静态光晕效果 */
  background-image: 
    radial-gradient(ellipse at 20% 30%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 70%, rgba(168, 85, 247, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 50%, rgba(0, 217, 255, 0.1) 0%, transparent 60%);
  background-size: 100% 100%;
}
</style>

