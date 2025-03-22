<template>
  <div class="model-training">
    <div class="training-header">
      <div class="status-panel">
        <q-chip
          :color="trainingStatus === 'running' ? 'positive' : 'grey'"
          text-color="white"
          icon="memory"
        >
          {{ getStatusText() }}
        </q-chip>
        <q-chip
          color="primary"
          text-color="white"
          icon="schedule"
        >
          训练时长: {{ formatDuration(trainingDuration) }}
        </q-chip>
      </div>

      <q-btn-group spread>
        <q-btn
          icon="play_arrow"
          label="开始训练"
          color="primary"
          :disable="trainingStatus === 'running'"
          @click="startTraining"
        />
        <q-btn
          icon="stop"
          label="停止训练"
          color="negative"
          :disable="trainingStatus !== 'running'"
          @click="stopTraining"
        />
        <q-btn
          icon="save"
          label="保存模型"
          color="secondary"
          :disable="!canSaveModel"
          @click="saveModel"
        />
      </q-btn-group>
    </div>

    <div class="training-content">
      <div class="metrics-panel">
        <div class="chart-container">
          <h6 class="text-subtitle1">损失函数</h6>
          <canvas ref="lossChart" />
        </div>
        <div class="chart-container">
          <h6 class="text-subtitle1">准确率</h6>
          <canvas ref="accuracyChart" />
        </div>
      </div>

      <div class="parameters-panel">
        <q-list bordered padding>
          <q-item-label header>训练参数</q-item-label>
          
          <q-item>
            <q-item-section>
              <q-item-label>学习率</q-item-label>
              <q-slider
                v-model="learningRate"
                :min="0.0001"
                :max="0.1"
                :step="0.0001"
                label
                :disable="trainingStatus === 'running'"
              />
            </q-item-section>
          </q-item>

          <q-item>
            <q-item-section>
              <q-item-label>批次大小</q-item-label>
              <q-select
                v-model="batchSize"
                :options="[16, 32, 64, 128]"
                :disable="trainingStatus === 'running'"
              />
            </q-item-section>
          </q-item>

          <q-item>
            <q-item-section>
              <q-item-label>训练轮数</q-item-label>
              <q-input
                v-model.number="epochs"
                type="number"
                :min="1"
                :disable="trainingStatus === 'running'"
              />
            </q-item-section>
          </q-item>
        </q-list>

        <q-list bordered padding class="q-mt-md">
          <q-item-label header>训练指标</q-item-label>
          
          <q-item>
            <q-item-section>
              <q-item-label>当前轮数</q-item-label>
              <q-item-label caption>{{ currentEpoch }} / {{ epochs }}</q-item-label>
            </q-item-section>
          </q-item>

          <q-item>
            <q-item-section>
              <q-item-label>当前损失</q-item-label>
              <q-item-label caption>{{ currentLoss.toFixed(4) }}</q-item-label>
            </q-item-section>
          </q-item>

          <q-item>
            <q-item-section>
              <q-item-label>当前准确率</q-item-label>
              <q-item-label caption>{{ (currentAccuracy * 100).toFixed(2) }}%</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useQuasar } from 'quasar'
import Chart from 'chart.js/auto'

const $q = useQuasar()

// 状态变量
const trainingStatus = ref('idle') // idle, running, completed
const trainingDuration = ref(0)
const canSaveModel = ref(false)

// 训练参数
const learningRate = ref(0.001)
const batchSize = ref(32)
const epochs = ref(100)
const currentEpoch = ref(0)
const currentLoss = ref(0)
const currentAccuracy = ref(0)

// 图表实例
let lossChart = null
let accuracyChart = null

// 训练数据
const lossHistory = ref([])
const accuracyHistory = ref([])

// 定时器
let durationTimer = null

// 初始化图表
onMounted(() => {
  initCharts()
})

// 清理资源
onUnmounted(() => {
  if (durationTimer) clearInterval(durationTimer)
  if (lossChart) lossChart.destroy()
  if (accuracyChart) accuracyChart.destroy()
})

// 初始化图表
function initCharts() {
  const lossCtx = document.querySelector('#lossChart').getContext('2d')
  lossChart = new Chart(lossCtx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: '训练损失',
        data: [],
        borderColor: '#1976D2',
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false
    }
  })

  const accuracyCtx = document.querySelector('#accuracyChart').getContext('2d')
  accuracyChart = new Chart(accuracyCtx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: '训练准确率',
        data: [],
        borderColor: '#21BA45',
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false
    }
  })
}

// 开始训练
function startTraining() {
  trainingStatus.value = 'running'
  currentEpoch.value = 0
  lossHistory.value = []
  accuracyHistory.value = []
  canSaveModel.value = false
  
  // 启动训练时长计时器
  trainingDuration.value = 0
  durationTimer = setInterval(() => {
    trainingDuration.value++
  }, 1000)
  
  // 模拟训练过程
  simulateTraining()
}

// 停止训练
function stopTraining() {
  trainingStatus.value = 'completed'
  clearInterval(durationTimer)
  canSaveModel.value = true
}

// 保存模型
function saveModel() {
  $q.notify({
    type: 'positive',
    message: '模型保存成功'
  })
}

// 模拟训练过程
function simulateTraining() {
  if (currentEpoch.value >= epochs.value) {
    stopTraining()
    return
  }
  
  currentEpoch.value++
  currentLoss.value = Math.random() * 0.5
  currentAccuracy.value = 0.5 + Math.random() * 0.5
  
  lossHistory.value.push(currentLoss.value)
  accuracyHistory.value.push(currentAccuracy.value)
  
  updateCharts()
  
  setTimeout(simulateTraining, 1000)
}

// 更新图表
function updateCharts() {
  const labels = Array.from({ length: currentEpoch.value }, (_, i) => i + 1)
  
  lossChart.data.labels = labels
  lossChart.data.datasets[0].data = lossHistory.value
  lossChart.update()
  
  accuracyChart.data.labels = labels
  accuracyChart.data.datasets[0].data = accuracyHistory.value
  accuracyChart.update()
}

// 获取状态文本
function getStatusText() {
  const statusMap = {
    idle: '未开始',
    running: '训练中',
    completed: '已完成'
  }
  return statusMap[trainingStatus.value]
}

// 格式化训练时长
function formatDuration(seconds) {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const remainingSeconds = seconds % 60
  
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
}
</script>

<style scoped>
.model-training {
  height: 100%;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.training-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.training-content {
  flex: 1;
  display: flex;
  gap: 1rem;
  overflow: hidden;
}

.metrics-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chart-container {
  flex: 1;
  background: white;
  border-radius: 4px;
  padding: 1rem;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.2);
}

.parameters-panel {
  width: 300px;
  overflow-y: auto;
}
</style>