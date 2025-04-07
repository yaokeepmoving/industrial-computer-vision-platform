<template>
  <div class="annotation-preview-container" :class="{ 'fullscreen': isFullscreen }">
    <!-- Simple image preview (used when not interactive) -->
    <div v-if="!isInteractive && !isFullscreen" class="simple-preview" @click="enableInteractive">
      <img :src="imageUrl" class="simple-image" />
      <div class="annotation-overlay" v-if="hasAnnotations">
        <div class="annotation-indicator">
          <q-icon name="layers" color="white" size="16px" />
          <span class="annotation-count">{{ annotations.length }}</span>
        </div>
      </div>
      <div class="preview-overlay">
        <q-icon name="search" color="white" size="24px" />
        <div class="preview-text">点击查看详情</div>
      </div>
    </div>

    <!-- OpenSeadragon container (used when interactive or fullscreen) -->
    <div v-if="isInteractive || isFullscreen" ref="container" class="image-container">
      <!-- Show placeholder when loading -->
      <div v-if="loading" class="loading-placeholder">
        <q-spinner color="primary" size="48px" />
        <div class="q-mt-sm">加载中...</div>
      </div>
    </div>

    <!-- Controls overlay -->
    <div class="controls-overlay" v-if="(isInteractive || isFullscreen) && !loading">
      <div class="control-buttons">
        <!-- Zoom controls -->
        <div class="zoom-controls">
          <q-btn round flat dense color="white" icon="remove" @click="zoomOut">
            <q-tooltip>缩小</q-tooltip>
          </q-btn>
          <div class="zoom-level">{{ Math.round(zoomLevel * 100) }}%</div>
          <q-btn round flat dense color="white" icon="add" @click="zoomIn">
            <q-tooltip>放大</q-tooltip>
          </q-btn>
        </div>

        <!-- Close button (when interactive but not fullscreen) -->
        <q-btn v-if="isInteractive && !isFullscreen" round flat dense color="white" icon="close" 
          @click="disableInteractive" class="control-btn">
          <q-tooltip>关闭详情</q-tooltip>
        </q-btn>

        <!-- Fullscreen toggle -->
        <q-btn round flat dense color="white" :icon="isFullscreen ? 'fullscreen_exit' : 'fullscreen'" 
          @click="toggleFullscreen" class="control-btn">
          <q-tooltip>{{ isFullscreen ? '退出全屏' : '全屏预览' }}</q-tooltip>
        </q-btn>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue'
import OpenSeadragon from 'openseadragon'
import { createOSDAnnotator } from '@annotorious/openseadragon'
import '@annotorious/openseadragon/annotorious-openseadragon.css'
import { W3CAnnotation } from '@annotorious/openseadragon'

// Define props
interface Props {
  imageUrl: string
  annotations: W3CAnnotation[]
  height?: string
  width?: string
  showControls?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  height: '220px',
  width: '100%',
  showControls: true
})

// Component state
const container = ref<HTMLElement | null>(null)
const zoomLevel = ref(1)
const loading = ref(true)
const isFullscreen = ref(false)
const isInteractive = ref(false)

// OpenSeadragon and Annotorious instances
let viewer: any = null
let anno: any = null

// Computed properties
const hasAnnotations = computed(() => props.annotations && props.annotations.length > 0)

// Only show simplified, non-interactive image by default
// Full OSD viewer will be initialized on click or when fullscreen is requested
// This prevents too many WebGL contexts being created at once
const enableInteractive = () => {
  isInteractive.value = true
  nextTick(() => {
    initializeViewer()
  })
}

const disableInteractive = () => {
  if (!isFullscreen.value) {
    isInteractive.value = false
    cleanupViewer()
  }
}

// Process image URL to ensure it works with OpenSeadragon
const getProcessedImageUrl = () => {
  // If the URL is a data URL, we need to extract just the data part for OpenSeadragon
  if (props.imageUrl.startsWith('data:image')) {
    return props.imageUrl
  }
  return props.imageUrl
}

// Initialize with non-interactive mode
onMounted(() => {
  // Keep simple preview initially to reduce WebGL contexts
})

// Clean up on component unmount
onUnmounted(() => {
  cleanupViewer()
})

const cleanupViewer = () => {
  if (anno) {
    anno.destroy()
    anno = null
  }

  if (viewer) {
    viewer.destroy()
    viewer = null
  }
}

// Initialize OpenSeadragon viewer and Annotorious
const initializeViewer = () => {
  if (!container.value || viewer) return

  // Clean up any existing instances
  cleanupViewer()

  // Generate a unique ID for this viewer instance
  const viewerId = `osd-container-${Math.random().toString(36).substring(2, 11)}`
  container.value.id = viewerId
  
  loading.value = true

  // Initialize OpenSeadragon viewer
  viewer = OpenSeadragon({
    element: container.value,
    tileSources: {
      type: 'image',
      url: getProcessedImageUrl()
    },
    showNavigationControl: false,
    zoomPerClick: 1.2,
    animationTime: 0.3,
    blendTime: 0.1,
    constrainDuringPan: true,
    maxZoomPixelRatio: 5,
    minZoomImageRatio: 0.8,
    visibilityRatio: 0.5,
    springStiffness: 10,
    gestureSettingsMouse: {
      clickToZoom: true,
      dblClickToZoom: true
    }
  })

  // Initialize Annotorious in read-only mode
  anno = createOSDAnnotator(viewer, {
    style: (annotation: any) => {
      // Customize annotation appearance
      const type = getAnnotationType(annotation)
      return {
        fill: type === 'text_region' ? 'rgba(33, 150, 243, 0.2)' : 'rgba(255, 152, 0, 0.2)',
        stroke: type === 'text_region' ? 'rgb(33, 150, 243)' : 'rgb(255, 152, 0)',
        strokeWidth: 2
      }
    }
  })

  // Load annotations
  loadAnnotations()

  // Track when image is loaded
  viewer.addHandler('open', () => {
    loading.value = false
  })

  // Track zoom level
  viewer.addHandler('zoom', (event: any) => {
    zoomLevel.value = event.zoom
  })
  
  // Handle window resize
  window.addEventListener('resize', resizeViewer)
}

// Get annotation type
const getAnnotationType = (annotation: any): 'text_region' | 'wheel_text' => {
  if (!annotation || !annotation.body || !annotation.body.length) {
    return 'text_region' // Default type
  }

  const body = Array.isArray(annotation.body) 
    ? annotation.body.find((b: any) => b.purpose === 'tagging') 
    : annotation.body

  if (body && body.value === 'wheel_text') {
    return 'wheel_text'
  }

  return 'text_region'
}

// Load annotations
const loadAnnotations = () => {
  if (!anno || !props.annotations) return
  
  // Load annotations into Annotorious
  if (props.annotations.length > 0) {
    anno.setAnnotations(props.annotations)
  } else {
    anno.setAnnotations([])
  }
}

// Zoom in
const zoomIn = () => {
  if (viewer) {
    viewer.viewport.zoomBy(1.2)
    viewer.viewport.applyConstraints()
  }
}

// Zoom out
const zoomOut = () => {
  if (viewer) {
    viewer.viewport.zoomBy(0.8)
    viewer.viewport.applyConstraints()
  }
}

// Toggle fullscreen mode
const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
  
  if (isFullscreen.value) {
    isInteractive.value = true
    nextTick(() => {
      if (!viewer) {
        initializeViewer()
      } else {
        resizeViewer()
      }
    })
  } else {
    nextTick(() => {
      resizeViewer()
    })
  }
}

// Resize viewer on container size changes
const resizeViewer = () => {
  if (viewer) {
    viewer.viewport.resize()
    viewer.viewport.goHome()
  }
}

// Watch for prop changes
watch(() => props.imageUrl, (newUrl) => {
  if (newUrl && (isInteractive.value || isFullscreen.value)) {
    initializeViewer()
  }
})

watch(() => props.annotations, (newAnnotations) => {
  if (newAnnotations && anno) {
    loadAnnotations()
  }
})
</script>

<style lang="scss" scoped>
.annotation-preview-container {
  position: relative;
  width: v-bind(width);
  height: v-bind(height);
  background: #000;
  border-radius: 4px;
  overflow: hidden;
  
  &.fullscreen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 9999;
    border-radius: 0;
  }
}

.simple-preview {
  position: relative;
  width: 100%;
  height: 100%;
  cursor: pointer;
  
  &:hover .preview-overlay {
    opacity: 1;
  }
}

.simple-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.preview-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.preview-text {
  color: white;
  font-size: 12px;
  margin-top: 8px;
}

.annotation-overlay {
  position: absolute;
  top: 8px;
  right: 8px;
  pointer-events: none;
}

.annotation-indicator {
  display: flex;
  align-items: center;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 12px;
  padding: 2px 8px;
}

.annotation-count {
  color: white;
  font-size: 11px;
  margin-left: 4px;
}

.image-container {
  width: 100%;
  height: 100%;
  background-color: #000;
  
  /* Make sure the image fills the container */
  :deep(.openseadragon-canvas) {
    outline: none;
    width: 100% !important;
    height: 100% !important;
  }
}

.loading-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: rgba(0, 0, 0, 0.7);
}

.controls-overlay {
  position: absolute;
  top: 0;
  right: 0;
  left: 0;
  padding: 8px;
  pointer-events: none;
  z-index: 10;
  
  /* Ensure buttons are clickable */
  .q-btn {
    pointer-events: auto;
  }
}

.control-buttons {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 8px;
  float: right;
}

.zoom-controls {
  display: flex;
  align-items: center;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 20px;
  padding: 2px 8px;
  margin-right: 8px;
}

.control-btn {
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
}

.zoom-level {
  font-size: 12px;
  color: white;
  margin: 0 8px;
  min-width: 40px;
  text-align: center;
}

/* Annotation styles */
:deep(.a9s-annotationlayer) {
  z-index: 1;
  pointer-events: none;
}
</style> 