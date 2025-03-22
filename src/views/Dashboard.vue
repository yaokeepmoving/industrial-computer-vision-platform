<template>
  <q-page class="dashboard-page q-pa-md">
    <div class="row q-col-gutter-md">
      <!-- 系统状态卡片 -->
      <div class="col-12 col-md-6 col-lg-3">
        <q-card class="dashboard-card">
          <q-card-section>
            <div class="text-h6">系统状态</div>
            <div class="row q-mt-md items-center">
              <q-icon name="check_circle" color="positive" size="48px" />
              <div class="q-ml-md">
                <div class="text-h5">{{ systemStatus.message }}</div>
                <div class="text-caption">运行时间: {{ systemStatus.uptime }}h</div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- 检测统计卡片 -->
      <div class="col-12 col-md-6 col-lg-3">
        <q-card class="dashboard-card">
          <q-card-section>
            <div class="text-h6">今日检测</div>
            <div class="row q-mt-md items-center">
              <q-icon name="analytics" color="info" size="48px" />
              <div class="q-ml-md">
                <div class="text-h5">{{ detectionStats.total }}</div>
                <div class="text-caption">较昨日 {{ detectionStats.change > 0 ? '+' : '' }}{{ detectionStats.change }}%</div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- 缺陷统计卡片 -->
      <div class="col-12 col-md-6 col-lg-3">
        <q-card class="dashboard-card">
          <q-card-section>
            <div class="text-h6">缺陷数量</div>
            <div class="row q-mt-md items-center">
              <q-icon name="warning" color="warning" size="48px" />
              <div class="q-ml-md">
                <div class="text-h5">{{ defectStats.total }}</div>
                <div class="text-caption">较昨日 {{ defectStats.change > 0 ? '+' : '' }}{{ defectStats.change }}%</div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- 准确率卡片 -->
      <div class="col-12 col-md-6 col-lg-3">
        <q-card class="dashboard-card">
          <q-card-section>
            <div class="text-h6">识别准确率</div>
            <div class="row q-mt-md items-center">
              <q-icon name="verified" color="positive" size="48px" />
              <div class="q-ml-md">
                <div class="text-h5">{{ accuracy.value }}%</div>
                <div class="text-caption">较昨日 {{ accuracy.change > 0 ? '+' : '' }}{{ accuracy.change }}%</div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- 实时监控图表 -->
      <div class="col-12 col-lg-8">
        <q-card class="dashboard-card">
          <q-card-section>
            <div class="text-h6">实时监控</div>
            <div class="chart-container q-mt-md" style="height: 300px">
              <!-- 此处集成图表组件 -->
              <div class="text-center text-grey-6">图表加载中...</div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- 最近告警列表 -->
      <div class="col-12 col-lg-4">
        <q-card class="dashboard-card">
          <q-card-section>
            <div class="text-h6">最近告警</div>
            <q-list separator>
              <q-item v-for="alert in alerts" :key="alert.id">
                <q-item-section avatar>
                  <q-icon :name="alert.type === 'error' ? 'error' : 'warning'" :color="alert.type === 'error' ? 'negative' : 'warning'" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ alert.message }}</q-item-label>
                  <q-item-label caption>{{ Math.floor((Date.now() - alert.timestamp) / 60000) }}分钟前</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-btn flat round icon="chevron_right" /> 
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useDashboard } from '@/services/dashboard'

const dashboard = useDashboard()
const systemStatus = ref(dashboard.getSystemStatus())
const detectionStats = ref(dashboard.getDetectionStats())
const defectStats = ref(dashboard.getDefectStats())
const accuracy = ref(dashboard.getAccuracy())
</script>

<style lang="scss" scoped>
.dashboard-page {
  background: var(--dark-page);
}

.dashboard-card {
  background: var(--dark-card);
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  }
}

.chart-container {
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>