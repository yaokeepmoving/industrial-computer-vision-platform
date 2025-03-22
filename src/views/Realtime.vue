<template>
  <q-page class="realtime-page q-pa-md">
    <div class="row q-col-gutter-md">
      <!-- 相机预览区域 -->
      <div class="col-12 col-lg-8">
        <q-card class="camera-card">
          <q-card-section>
            <div class="text-h6">相机预览</div>
            <camera-capture class="q-mt-md" />
          </q-card-section>
        </q-card>
      </div>

      <!-- 检测结果区域 -->
      <div class="col-12 col-lg-4">
        <q-card class="result-card">
          <q-card-section>
            <div class="text-h6">检测结果</div>
            <div class="result-container q-mt-md">
              <div class="text-h5 text-center text-positive">合格</div>
              <q-list separator>
                <q-item>
                  <q-item-section>
                    <q-item-label>检测时间</q-item-label>
                    <q-item-label caption>2024-03-14 10:06:54</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label>识别文字</q-item-label>
                    <q-item-label caption>ABC123</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label>置信度</q-item-label>
                    <q-item-label caption>98.5%</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </q-card-section>
        </q-card>

        <!-- 相机控制面板 -->
        <q-card class="control-card q-mt-md">
          <q-card-section>
            <div class="text-h6">相机控制</div>
            <div class="q-mt-md">
              <q-btn-group spread>
                <q-btn color="primary" icon="play_arrow" label="开始检测" />
                <q-btn color="negative" icon="stop" label="停止检测" />
              </q-btn-group>
              <q-list class="q-mt-md">
                <q-item>
                  <q-item-section>
                    <q-item-label>曝光时间</q-item-label>
                    <q-slider v-if="settings" v-model="settings.exposure" :min="0" :max="100" label @update:model-value="val => updateSettings('exposure', val)" />
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label>增益</q-item-label>
                    <q-slider v-if="settings" v-model="settings.gain" :min="0" :max="100" label @update:model-value="val => updateSettings('gain', val)" />
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import CameraCapture from '../components/capture/CameraCapture.vue'
import { useRealtime } from '@/services/realtime'
import { MockCameraService } from '@/services/camera'

// 初始化相机服务
const cameraService = new MockCameraService()
const settings = ref(null)

// 获取相机设置
onMounted(async () => {
  settings.value = await cameraService.getSettings()
})

// 更新相机设置
const updateSettings = async (key, value) => {
  await cameraService.updateSettings({ [key]: value })
}

const { getLatestResult, startSimulation } = useRealtime()
const detectionResult = getLatestResult()

// 启动模拟数据更新
startSimulation()
</script>

<style lang="scss" scoped>
.realtime-page {
  background: var(--dark-page);
}

.camera-card,
.result-card,
.control-card {
  background: var(--dark-card);
}

.result-container {
  .text-h5 {
    padding: 1rem;
    border-radius: 8px;
    background: rgba(46, 125, 50, 0.1);
  }
}
</style>