<template>
  <q-toolbar class="industrial-status-bar">
    <!-- 左侧菜单按钮 -->
    <q-btn
      flat
      dense
      round
      icon="menu"
      aria-label="菜单"
      class="menu-button"
      @click="$emit('toggleLeftDrawer')"
    />
    
    <!-- 系统标题 -->
    <q-toolbar-title class="text-weight-medium system-title">
      <div class="title-container">
        <metal-textures type="brushed" size="full" class="title-background">
          <div class="title-content">
            工业铸字识别系统
            <q-badge
              color="accent"
              text-color="white"
              class="q-ml-sm version-badge"
            >
              v0.1.0
            </q-badge>
          </div>
        </metal-textures>
      </div>
    </q-toolbar-title>

    <!-- 右侧状态指示器 -->
    <div class="status-indicators">
      <!-- 相机状态 -->
      <div class="status-item">
        <industrial-icons 
          type="status-light" 
          :status="cameraStatus.class.replace('status-', '')" 
          size="sm" 
          class="q-mr-xs"
        />
        <span class="status-label">相机</span>
        <span class="status-value" :class="cameraStatus.class">{{ cameraStatus.text }}</span>
      </div>
      
      <!-- 模型状态 -->
      <div class="status-item">
        <industrial-icons 
          type="status-light" 
          :status="modelStatus.class.replace('status-', '')" 
          size="sm" 
          class="q-mr-xs"
        />
        <span class="status-label">模型</span>
        <span class="status-value" :class="modelStatus.class">{{ modelStatus.text }}</span>
      </div>
      
      <!-- 设备连接状态 -->
      <div class="status-item">
        <industrial-icons 
          type="status-light" 
          :status="deviceStatus.class.replace('status-', '')" 
          size="sm" 
          class="q-mr-xs"
        />
        <span class="status-label">设备</span>
        <span class="status-value" :class="deviceStatus.class">{{ deviceStatus.text }}</span>
      </div>
    </div>
  </q-toolbar>
</template>

<script setup>
import MetalTextures from '../common/MetalTextures.vue';
import IndustrialIcons from '../common/IndustrialIcons.vue';
import { ref, computed } from 'vue'
import { useDeviceStore } from '../../stores/device'

const deviceStore = useDeviceStore()

// 相机状态
const cameraStatus = computed(() => {
  const status = deviceStore.cameraStatus
  
  switch (status) {
    case 'connected':
      return { text: '已连接', class: 'running' }
    case 'disconnected':
      return { text: '未连接', class: 'error' }
    case 'initializing':
      return { text: '初始化中', class: 'warning pulse' }
    default:
      return { text: '未知', class: 'idle' }
  }
})

// 模型状态
const modelStatus = computed(() => {
  const status = deviceStore.modelStatus
  
  switch (status) {
    case 'loaded':
      return { text: '已加载', class: 'running' }
    case 'unloaded':
      return { text: '未加载', class: 'error' }
    case 'loading':
      return { text: '加载中', class: 'warning pulse' }
    default:
      return { text: '未知', class: 'idle' }
  }
})

// 设备连接状态
const deviceStatus = computed(() => {
  const status = deviceStore.connectionStatus
  
  switch (status) {
    case 'connected':
      return { text: '已连接', class: 'running' }
    case 'disconnected':
      return { text: '未连接', class: 'error' }
    case 'connecting':
      return { text: '连接中', class: 'warning pulse' }
    default:
      return { text: '未知', class: 'idle' }
  }
})
</script>

<style lang="scss" scoped>
.industrial-status-bar {
  height: 64px;
  padding: 0 16px;
  background-color: var(--dark-surface);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.menu-button {
  background: linear-gradient(145deg, #3A3F45, #2D3238);
  border: 1px solid #4A4E54;
  box-shadow: 
    inset 0 1px 1px rgba(255,255,255,0.1),
    0 1px 3px rgba(0,0,0,0.3);
}

.system-title {
  height: 40px;
  overflow: hidden;
  
  .title-container {
    height: 100%;
    max-width: 300px;
    border-radius: 4px;
    overflow: hidden;
  }
  
  .title-background {
    height: 100%;
  }
  
  .title-content {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 16px;
    font-weight: 500;
    text-shadow: 0 1px 2px rgba(0,0,0,0.5);
  }
}

.version-badge {
  font-size: 12px;
  padding: 4px 8px;
}

.status-indicators {
  display: flex;
  align-items: center;
  gap: 24px;
}

.status-item {
  display: flex;
  align-items: center;
  font-size: 14px;
  
  .status-label {
    margin-right: 8px;
    color: rgba(255, 255, 255, 0.7);
  }
  
  .status-value {
    font-weight: 500;
  }
  
  .running {
    color: var(--status-green);
  }
  
  .warning {
    color: var(--status-yellow);
  }
  
  .error {
    color: var(--status-red);
  }
  
  .idle {
    color: #aaa;
  }
  
  .pulse {
    animation: pulse 1.5s infinite;
  }
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}
</style>