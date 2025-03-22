<template>
  <div class="mes-integration">
    <div class="status-panel">
      <q-card flat bordered>
        <q-card-section>
          <div class="text-h6">MES系统连接状态</div>
          <q-chip :color="connectionStatus === 'connected' ? 'positive' : 'negative'" text-color="white" icon="link">
            {{ connectionStatus === 'connected' ? '已连接' : '未连接' }}
          </q-chip>
        </q-card-section>

        <q-card-section>
          <q-form @submit="connect">
            <q-input v-model="config.host" label="MES服务器地址" :disable="connectionStatus === 'connected'" />
            <q-input v-model="config.port" label="端口" type="number" :disable="connectionStatus === 'connected'" />
            <q-input v-model="config.token" label="访问令牌" :type="showToken ? 'text' : 'password'"
              :disable="connectionStatus === 'connected'">
              <template v-slot:append>
                <q-icon :name="showToken ? 'visibility_off' : 'visibility'" class="cursor-pointer"
                  @click="showToken = !showToken" />
              </template>
            </q-input>

            <div class="row justify-end q-mt-md">
              <q-btn :label="connectionStatus === 'connected' ? '断开连接' : '连接'"
                :color="connectionStatus === 'connected' ? 'negative' : 'primary'" type="submit" />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </div>

    <div class="data-sync-panel q-mt-md">
      <q-card flat bordered>
        <q-card-section>
          <div class="text-h6">数据同步</div>
          <div class="row items-center q-mt-sm">
            <q-chip :color="syncStatus === 'syncing' ? 'warning' : 'grey'" text-color="white" icon="sync"
              :loading="syncStatus === 'syncing'">
              {{ getSyncStatusText() }}
            </q-chip>
            <q-space />
            <span class="text-caption">
              上次同步: {{ lastSyncTime ? formatDate(lastSyncTime) : '从未同步' }}
            </span>
          </div>
        </q-card-section>

        <q-card-section>
          <q-list bordered separator>
            <q-item>
              <q-item-section>
                <q-item-label>生产订单</q-item-label>
                <q-item-label caption>同步MES系统中的生产订单信息</q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-toggle v-model="syncConfig.orders" />
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label>质检数据</q-item-label>
                <q-item-label caption>上传识别结果到MES系统</q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-toggle v-model="syncConfig.quality" />
              </q-item-section>
            </q-item>

            <q-item>
              <q-item-section>
                <q-item-label>设备状态</q-item-label>
                <q-item-label caption>同步设备运行状态到MES系统</q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-toggle v-model="syncConfig.device" />
              </q-item-section>
            </q-item>
          </q-list>

          <div class="row justify-between q-mt-md">
            <q-btn label="立即同步" color="primary" :disable="!isConnected || syncStatus === 'syncing'"
              @click="startSync" />
            <q-btn-group outline>
              <q-btn label="导入配置" icon="upload" @click="importConfig" />
              <q-btn label="导出配置" icon="download" @click="exportConfig" />
            </q-btn-group>
          </div>
        </q-card-section>
      </q-card>
    </div>

    <div class="log-panel q-mt-md">
      <q-card flat bordered>
        <q-card-section>
          <div class="text-h6">同步日志</div>
        </q-card-section>

        <q-card-section class="log-content">
          <q-list bordered separator>
            <q-item v-for="(log, index) in syncLogs" :key="index">
              <q-item-section avatar>
                <q-icon :name="getLogIcon(log.type)" :color="getLogColor(log.type)" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ log.message }}</q-item-label>
                <q-item-label caption>{{ formatDate(log.timestamp) }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useQuasar } from 'quasar'
import { date } from 'quasar'
import { mesService } from '@/utils/mesService'

const $q = useQuasar()

// 连接状态
const connectionStatus = ref('disconnected') // connected, disconnected
const showToken = ref(false)

// MES配置
const config = ref({
  host: '',
  port: 8080,
  token: ''
})

// 同步状态
const syncStatus = ref('idle') // idle, syncing, error
const lastSyncTime = ref(null)
const syncLogs = ref([])

// 同步配置
const syncConfig = ref({
  orders: true,
  quality: true,
  device: true
})

// 计算属性
const isConnected = computed(() => connectionStatus.value === 'connected')

// 连接MES系统
async function connect() {
  if (connectionStatus.value === 'connected') {
    // 断开连接
    const result = await mesService.disconnect()
    if (result.success) {
      connectionStatus.value = 'disconnected'
      addLog('info', result.message)
    } else {
      addLog('error', result.message)
    }
  } else {
    // 建立连接
    const result = await mesService.connect(config.value)
    if (result.success) {
      connectionStatus.value = 'connected'
      addLog('success', result.message)
    } else {
      addLog('error', result.message)
    }
  }

  // 开始同步
  async function startSync() {
    syncStatus.value = 'syncing'
    addLog('info', '开始数据同步')

    const result = await mesService.syncData(syncConfig.value)
    if (result.success) {
      syncStatus.value = 'idle'
      lastSyncTime.value = Date.now()
      addLog('success', result.message)
    } else {
      syncStatus.value = 'error'
      addLog('error', result.message)
    }
  }

  // 导入配置
  async function importConfig() {
    const result = await mesService.importConfig(config.value)
    $q.notify({
      type: result.success ? 'positive' : 'negative',
      message: result.message
    })
  }

  // 导出配置
  async function exportConfig() {
    const result = await mesService.exportConfig()
    if (result.success) {
      config.value = result.data
      $q.notify({
        type: 'positive',
        message: result.message
      })
    } else {
      $q.notify({
        type: 'negative',
        message: result.message
      })
    }
  }

  // 添加日志
  function addLog(type, message) {
    syncLogs.value.unshift({
      type,
      message,
      timestamp: Date.now()
    })
  }

  // 获取同步状态文本
  function getSyncStatusText() {
    const statusMap = {
      idle: '等待同步',
      syncing: '同步中',
      error: '同步错误'
    }
    return statusMap[syncStatus.value]
  }

  // 获取日志图标
  function getLogIcon(type) {
    const iconMap = {
      info: 'info',
      success: 'check_circle',
      error: 'error',
      warning: 'warning'
    }
    return iconMap[type] || 'info'
  }

  // 获取日志颜色
  function getLogColor(type) {
    const colorMap = {
      info: 'info',
      success: 'positive',
      error: 'negative',
      warning: 'warning'
    }
    return colorMap[type] || 'grey'
  }

  // 格式化日期
  function formatDate(timestamp) {
    return date.formatDate(timestamp, 'YYYY-MM-DD HH:mm:ss')
  }
}
</script>

<style scoped>
.mes-integration {
  height: 100%;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  overflow-y: auto;
}

.log-content {
  max-height: 300px;
  overflow-y: auto;
}
</style>