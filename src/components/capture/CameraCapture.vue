<template>
  <div class="camera-capture">
    <div class="camera-preview">
      <video
        ref="videoElement"
        class="video-stream"
        :class="{ 'is-recording': isRecording }"
        autoplay
        playsinline
      />
      <canvas ref="canvasElement" style="display: none" />
    </div>
    
    <div class="camera-controls">
      <q-btn-group spread>
        <q-btn
          icon="videocam"
          :label="isStreaming ? '停止预览' : '开始预览'"
          :color="isStreaming ? 'negative' : 'primary'"
          @click="toggleStream"
        />
        <q-btn
          icon="photo_camera"
          label="拍照"
          color="secondary"
          :disable="!isStreaming"
          @click="captureImage"
        />
        <q-btn
          icon="settings"
          label="设置"
          color="grey"
          @click="showSettings = true"
        />
      </q-btn-group>
    </div>

    <q-dialog v-model="showSettings">
      <q-card style="min-width: 350px">
        <q-card-section>
          <div class="text-h6">相机设置</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-select
            v-model="selectedDevice"
            :options="videoDevices"
            label="选择摄像头"
            option-label="label"
            option-value="deviceId"
            emit-value
            map-options
            @update:model-value="handleDeviceChange"
          />
          
          <q-select
            v-model="selectedResolution"
            :options="resolutionOptions"
            label="分辨率"
            option-label="label"
            @update:model-value="handleResolutionChange"
          />

          <div class="row q-mt-md">
            <div class="col">
              <q-toggle
                v-model="autoFocus"
                label="自动对焦"
                @update:model-value="updateCameraSettings"
              />
            </div>
            <div class="col">
              <q-toggle
                v-model="autoExposure"
                label="自动曝光"
                @update:model-value="updateCameraSettings"
              />
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="关闭" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useQuasar } from 'quasar'

const $q = useQuasar()

// 状态变量
const videoElement = ref(null)
const canvasElement = ref(null)
const isStreaming = ref(false)
const isRecording = ref(false)
const showSettings = ref(false)
const selectedDevice = ref(null)
const videoDevices = ref([])
const selectedResolution = ref(null)
const autoFocus = ref(true)
const autoExposure = ref(true)

// 分辨率选项
const resolutionOptions = [
  { label: '1920x1080', width: 1920, height: 1080 },
  { label: '1280x720', width: 1280, height: 720 },
  { label: '640x480', width: 640, height: 480 }
]

// 当前视频流
let currentStream = null

// 获取可用的视频设备
async function getVideoDevices() {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices()
    videoDevices.value = devices
      .filter(device => device.kind === 'videoinput')
      .map(device => ({
        label: device.label || `Camera ${device.deviceId.slice(0, 8)}...`,
        deviceId: device.deviceId
      }))
    
    if (videoDevices.value.length > 0 && !selectedDevice.value) {
      selectedDevice.value = videoDevices.value[0].deviceId
    }
  } catch (error) {
    console.error('获取视频设备失败:', error)
    $q.notify({
      type: 'negative',
      message: '无法访问摄像头设备',
      position: 'top'
    })
  }
}

// 开启/关闭视频流
async function toggleStream() {
  if (isStreaming.value) {
    stopStream()
  } else {
    await startStream()
  }
}

// 开启视频流
async function startStream() {
  try {
    const constraints = {
      video: {
        deviceId: selectedDevice.value ? { exact: selectedDevice.value } : undefined,
        width: selectedResolution.value?.width || 1280,
        height: selectedResolution.value?.height || 720,
        focusMode: autoFocus.value ? 'continuous' : 'manual',
        exposureMode: autoExposure.value ? 'continuous' : 'manual'
      }
    }

    currentStream = await navigator.mediaDevices.getUserMedia(constraints)
    videoElement.value.srcObject = currentStream
    isStreaming.value = true

  } catch (error) {
    console.error('启动视频流失败:', error)
    $q.notify({
      type: 'negative',
      message: '启动摄像头失败',
      position: 'top'
    })
  }
}

// 停止视频流
function stopStream() {
  if (currentStream) {
    currentStream.getTracks().forEach(track => track.stop())
    currentStream = null
  }
  if (videoElement.value) {
    videoElement.value.srcObject = null
  }
  isStreaming.value = false
}

// 拍照
function captureImage() {
  if (!isStreaming.value) return

  const video = videoElement.value
  const canvas = canvasElement.value
  const context = canvas.getContext('2d')

  // 设置canvas尺寸与视频流相同
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight

  // 将视频帧绘制到canvas
  context.drawImage(video, 0, 0, canvas.width, canvas.height)

  // 获取图像数据
  const imageData = canvas.toDataURL('image/png')

  // 发出捕获事件
  emit('capture', {
    imageData,
    timestamp: new Date().toISOString(),
    resolution: {
      width: canvas.width,
      height: canvas.height
    }
  })

  $q.notify({
    type: 'positive',
    message: '图像已捕获',
    position: 'top'
  })
}

// 处理设备变更
async function handleDeviceChange() {
  if (isStreaming.value) {
    stopStream()
    await startStream()
  }
}

// 处理分辨率变更
async function handleResolutionChange() {
  if (isStreaming.value) {
    stopStream()
    await startStream()
  }
}

// 更新相机设置
async function updateCameraSettings() {
  if (isStreaming.value) {
    stopStream()
    await startStream()
  }
}

// 组件挂载时
onMounted(async () => {
  await getVideoDevices()
  selectedResolution.value = resolutionOptions[1] // 默认选择720p
})

// 组件卸载时
onUnmounted(() => {
  stopStream()
})

// 定义事件
const emit = defineEmits(['capture'])
</script>

<style lang="scss" scoped>
.camera-capture {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  background: var(--dark-page);
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);

  .camera-preview {
    position: relative;
    width: 100%;
    aspect-ratio: 16/9;
    background: #000;
    border-radius: 4px;
    overflow: hidden;

    .video-stream {
      width: 100%;
      height: 100%;
      object-fit: cover;

      &.is-recording {
        border: 2px solid var(--q-negative);
      }
    }
  }

  .camera-controls {
    display: flex;
    justify-content: center;
    gap: 8px;
  }
}
</style>