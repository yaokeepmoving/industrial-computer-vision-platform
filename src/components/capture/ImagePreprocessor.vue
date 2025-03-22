<template>
  <div class="image-preprocessor">
    <camera-capture @capture="handleImageCapture" />
    
    <div class="processing-controls" v-if="capturedImage">
      <div class="preview-container">
        <canvas ref="previewCanvas" class="preview-canvas" />
        <div class="character-boxes" v-if="showCharacterBoxes">
          <div
            v-for="(box, index) in characterBoxes"
            :key="index"
            class="char-box"
            :style="{
              left: `${box.x}px`,
              top: `${box.y}px`,
              width: `${box.width}px`,
              height: `${box.height}px`
            }"
          />
        </div>
      </div>
      
      <div class="controls">
        <q-btn-group spread>
          <q-btn
            icon="invert_colors"
            label="灰度化"
            color="primary"
            @click="applyGrayscale"
          />
          <q-btn
            icon="contrast"
            label="二值化"
            color="secondary"
            @click="applyThreshold"
          />
          <q-btn
            icon="blur_on"
            label="降噪"
            color="accent"
            @click="applyMedianFilter"
          />
          <q-btn
            icon="border_clear"
            label="边缘检测"
            color="info"
            @click="applyEdgeDetection"
          />
        </q-btn-group>
        
        <div class="settings q-mt-md">
          <q-slider
            v-model="threshold"
            :min="0"
            :max="255"
            :step="1"
            label
            label-always
            color="secondary"
            class="q-mt-md"
          >
            <template v-slot:thumb-label>
              阈值: {{ threshold }}
            </template>
          </q-slider>
          
          <q-slider
            v-model="contrast"
            :min="-100"
            :max="100"
            :step="1"
            label
            label-always
            color="secondary"
            class="q-mt-md"
          >
            <template v-slot:thumb-label>
              对比度: {{ contrast }}
            </template>
          </q-slider>
        </div>
        
        <div class="actions q-mt-lg">
          <q-btn
            icon="save"
            label="保存处理结果"
            color="positive"
            @click="saveProcessedImage"
          />
          <q-btn
            icon="refresh"
            label="重置"
            color="warning"
            class="q-ml-sm"
            @click="resetImage"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import CameraCapture from './CameraCapture.vue'
import { ImageProcessor } from '../../utils/imageProcessor'

const $q = useQuasar()

// 状态变量
const previewCanvas = ref(null)
const capturedImage = ref(null)
const originalImageData = ref(null)
const threshold = ref(128)
const contrast = ref(0)
const autoThreshold = ref(false)
const showCharacterBoxes = ref(false)
const characterBoxes = ref([])

// 处理图像捕获
function handleImageCapture(imageData) {
  capturedImage.value = imageData
  loadImageToCanvas(imageData.imageData)
}

// 将图像加载到Canvas
function loadImageToCanvas(dataUrl) {
  const canvas = previewCanvas.value
  const ctx = canvas.getContext('2d')
  const img = new Image()
  
  img.onload = () => {
    canvas.width = img.width
    canvas.height = img.height
    ctx.drawImage(img, 0, 0)
    originalImageData.value = ctx.getImageData(0, 0, canvas.width, canvas.height)
  }
  
  img.src = dataUrl
}

// 应用灰度转换
function applyGrayscale() {
  const canvas = previewCanvas.value
  const ctx = canvas.getContext('2d')
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
  const processedData = ImageProcessor.toGrayscale(imageData)
  ctx.putImageData(processedData, 0, 0)
}

// 应用二值化
function applyThreshold() {
  const canvas = previewCanvas.value
  const ctx = canvas.getContext('2d')
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
  
  let processedData
  if (autoThreshold.value) {
    // 使用自适应阈值
    processedData = ImageProcessor.adaptiveThreshold(imageData)
  } else {
    // 使用OTSU算法计算最佳阈值
    const optimalThreshold = ImageProcessor.calculateOptimalThreshold(imageData)
    threshold.value = optimalThreshold
    processedData = ImageProcessor.threshold(imageData, threshold.value)
  }
  
  // 应用形态学操作
  processedData = ImageProcessor.erode(processedData)
  processedData = ImageProcessor.dilate(processedData)
  
  ctx.putImageData(processedData, 0, 0)
  
  // 进行字符分割
  const chars = ImageProcessor.segmentCharacters(processedData)
  characterBoxes.value = chars
  showCharacterBoxes.value = true
  
  // 提取每个字符的特征
  chars.forEach(char => {
    const features = ImageProcessor.extractFeatures(processedData, char)
    console.log('Character features:', features)
  })
}

// 应用中值滤波
function applyMedianFilter() {
  const canvas = previewCanvas.value
  const ctx = canvas.getContext('2d')
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
  const processedData = ImageProcessor.medianFilter(imageData)
  ctx.putImageData(processedData, 0, 0)
}

// 保存处理结果
function saveProcessedImage() {
  const canvas = previewCanvas.value
  const processedDataUrl = canvas.toDataURL('image/png')
  
  // 触发下载
  const link = document.createElement('a')
  link.download = `processed-image-${new Date().getTime()}.png`
  link.href = processedDataUrl
  link.click()
  
  $q.notify({
    type: 'positive',
    message: '图像已保存',
    position: 'top'
  })
}

// 应用边缘检测
function applyEdgeDetection() {
  const canvas = previewCanvas.value
  const ctx = canvas.getContext('2d')
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
  const processedData = ImageProcessor.detectEdges(imageData)
  ctx.putImageData(processedData, 0, 0)
}

// 重置图像
function resetImage() {
  if (originalImageData.value) {
    const canvas = previewCanvas.value
    const ctx = canvas.getContext('2d')
    ctx.putImageData(originalImageData.value, 0, 0)
    
    // 重置参数
    threshold.value = 128
    contrast.value = 0
  }
}
</script>

<style lang="scss" scoped>
.image-preprocessor {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  
  .processing-controls {
    display: flex;
    gap: 20px;
    
    .preview-container {
      flex: 1;
      min-width: 0;
      background: #000;
      border-radius: 8px;
      overflow: hidden;
      position: relative;
      
      .preview-canvas {
        width: 100%;
        height: auto;
        display: block;
      }
      
      .character-boxes {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        
        .char-box {
          position: absolute;
          border: 2px solid #00ff00;
          background: rgba(0, 255, 0, 0.1);
        }
      }
    }
    
    .controls {
      width: 300px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      
      .settings {
        background: rgba(255, 255, 255, 0.05);
        padding: 16px;
        border-radius: 8px;
      }
      
      .actions {
        display: flex;
        justify-content: center;
        gap: 8px;
      }
    }
  }
}
</style>