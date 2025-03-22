<template>
  <div class="control-panel" :class="[`theme-${theme}`, `size-${size}`]">
    <div class="panel-header">
      <div class="panel-title">
        <q-icon :name="icon" size="20px" class="q-mr-sm" />
        {{ title }}
      </div>
      <div class="panel-controls" v-if="$slots.controls">
        <slot name="controls"></slot>
      </div>
    </div>
    <div class="panel-content">
      <slot></slot>
    </div>
    <div class="panel-footer" v-if="$slots.footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  // 面板标题
  title: {
    type: String,
    default: '控制面板'
  },
  // 图标
  icon: {
    type: String,
    default: 'settings'
  },
  // 主题: 'primary', 'secondary', 'dark'
  theme: {
    type: String,
    default: 'primary'
  },
  // 尺寸: 'sm', 'md', 'lg', 'full'
  size: {
    type: String,
    default: 'md'
  }
});
</script>

<style lang="scss" scoped>
.control-panel {
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  overflow: hidden;
  background: #2D3238;
  border: 1px solid #3A3F45;
  box-shadow: 
    0 4px 8px rgba(0,0,0,0.2),
    inset 0 1px 1px rgba(255,255,255,0.05);
  
  // 尺寸变体
  &.size-sm {
    width: 300px;
  }
  
  &.size-md {
    width: 450px;
  }
  
  &.size-lg {
    width: 600px;
  }
  
  &.size-full {
    width: 100%;
  }
  
  // 主题变体
  &.theme-primary .panel-header {
    background: linear-gradient(180deg, #2A5CAA 0%, #1E4075 100%);
    border-bottom: 2px solid #3A6DBB;
  }
  
  &.theme-secondary .panel-header {
    background: linear-gradient(180deg, #4A4E54 0%, #3A3F45 100%);
    border-bottom: 2px solid #5A5E64;
  }
  
  &.theme-dark .panel-header {
    background: linear-gradient(180deg, #2D3238 0%, #1D2228 100%);
    border-bottom: 2px solid #3D4248;
  }
  
  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    height: 50px;
    
    .panel-title {
      display: flex;
      align-items: center;
      font-size: 16px;
      font-weight: 500;
      color: #fff;
      text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
  }
  
  .panel-content {
    flex: 1;
    padding: 16px;
    background: rgba(0,0,0,0.1);
    min-height: 100px;
  }
  
  .panel-footer {
    padding: 12px 16px;
    background: rgba(0,0,0,0.15);
    border-top: 1px solid #3A3F45;
  }
}
</style>