<template>
  <q-page class="not-found-page q-pa-md">
    <div class="row items-center justify-center" style="height: 100vh">
      <div class="text-center">
        <q-icon name="error_outline" size="100px" color="negative" />
        <div class="text-h4 q-mt-md">404</div>
        <div class="text-subtitle1 q-mt-sm">页面未找到</div>
        <q-btn
          color="primary"
          icon="home"
          label="返回首页"
          to="/"
          class="q-mt-lg"
        />
      </div>
    </div>
  </q-page>
</template>

<script setup>
// 组件逻辑待实现
</script>

<style lang="scss" scoped>
.not-found-page {
  background: var(--dark-page);
}
</style>