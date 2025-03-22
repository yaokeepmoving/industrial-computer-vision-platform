<template>
  <div class="rect-annotator-container">
    <!-- 图片调节控制面板 -->
    <div class="image-controls">
      <div class="control-item">
        <div class="scale-control">
          <label>缩放: {{ Math.round(imageScale * 100) }}%</label>
          <q-btn-group flat>
            <q-btn flat dense icon="remove" @click="adjustImageScale(-0.1)" />
            <q-btn flat dense icon="add" @click="adjustImageScale(0.1)" />
          </q-btn-group>
        </div>
      </div>
    </div>

    <!-- 标注控制面板 -->
    <div class="annotation-controls">
      <div class="step-indicator">
        {{ annotationStep === 'region' ? '第一步：标注文本区域' : '第二步：标注字符' }}
      </div>
      
      <q-btn-group>
        <q-btn 
          :color="isDrawing ? 'negative' : 'primary'" 
          :icon="isDrawing ? 'close' : 'add'" 
          @click="toggleDrawing"
        >
          {{ isDrawing ? '取消绘制' : '新建标注框' }}
        </q-btn>
        <q-btn 
          v-if="annotationStep === 'region' && selectedIndex !== -1"
          color="primary" 
          icon="text_format"
          @click="handleAnnotateCharacters(annotations[selectedIndex].id)"
        >
          标注字符
        </q-btn>
        <q-btn 
          v-if="annotationStep === 'character'"
          color="primary" 
          icon="arrow_back"
          @click="handleBackToRegions"
        >
          返回区域
        </q-btn>
        <q-btn 
          color="negative" 
          icon="delete" 
          @click="deleteSelected" 
          :disable="selectedIndex === -1"
        >
          删除选中
        </q-btn>
      </q-btn-group>
    </div>

    <!-- Konva Stage -->
    <div class="stage-container" ref="container">
      <v-stage
        ref="stage"
        :config="stageConfig"
        @mousedown="handleMouseDown"
        @mousemove="handleMouseMove"
        @mouseup="handleMouseUp"
        @click="handleStageClick"
        @wheel="handleWheel"
      >
        <v-layer>
          <v-image 
            :config="imageConfig"
            @dragstart="preventDefault"
          />
          <template v-for="(rect, index) in visibleAnnotations" :key="rect.id">
            <v-rect
              :ref="el => { if(el) rectRefs[index] = el }"
              :config="getAnnotationStyle(rect, selectedIndex === index)"
              @click="selectRect(index, $event)"
              @dragend="handleDragEnd(index, $event)"
              @transformend="handleTransformEnd(index, $event)"
            />
            <v-transformer
              v-if="selectedIndex === index"
              :config="transformerConfig"
              ref="transformer"
            />
            <!-- 标注文字 -->
            <v-text
              v-if="rect.type === 'character' && rect.label"
              :config="{
                x: rect.x,
                y: rect.y - 20,
                text: rect.label,
                fontSize: 14,
                fill: '#2196f3',
                padding: 4,
                background: '#fff',
              }"
            />
          </template>
        </v-layer>
      </v-stage>
    </div>

    <!-- 旋转提示 -->
    <div class="rotation-tip" v-if="rotationTip">
      提示：拖动矩形框四周的圆形控制点可以旋转
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick, watchEffect, computed } from 'vue'
import type { KonvaEventObject } from 'konva/lib/Node'
import Konva from 'konva'
import type { TextRegionAnnotation, CharacterAnnotation } from '../../types/annotation'
import type { Ref } from 'vue'
import { AnnotationService } from '../../services/annotation'
import { useQuasar } from 'quasar'
import { withDefaults } from 'vue'

// 获取 Quasar 实例
const $q = useQuasar()
const annotationService = new AnnotationService()

// 定义类型（使用已导入的 Konva）
type KonvaStage = Konva.Stage
type KonvaTransformer = Konva.Transformer
type KonvaRect = Konva.Rect

interface Annotation {
  id: string
  x: number
  y: number
  width: number
  height: number
  rotation: number
  label?: string // 只有字符标注需要 label
  parentId?: string 
  type: 'text_region' | 'character'
}

interface Props {
  imageUrl: string
  imageId: number
  currentImage: {
    id: number
    url: string
    filename: string
  } | null
  annotationStep?: 'region' | 'character'
  selectedRegionId?: string
  scale?: number
}

// 组件 props
const props = withDefaults(defineProps<Props>(), {
  annotationStep: 'region',
  selectedRegionId: undefined,
  scale: 1
})

// 组件 emits
const emit = defineEmits<{
  (e: 'update:annotations', annotations: any[]): void
  (e: 'annotationStatusChange', status: 'region_annotated' | 'char_annotated' | 'completed'): void
}>()

// 组件引用
const container = ref<HTMLElement | null>(null)
const stage = ref<KonvaStage | null>(null)
const transformer = ref<KonvaTransformer | null>(null)
const isDrawing = ref(false)
const startPoint = ref({ x: 0, y: 0 })
const selectedIndex = ref(-1)

const rectRefs = ref<KonvaRect[]>([])
const drawingRect = ref<Annotation | null>(null)

// 添加图片元素引用
const imageElement = ref<HTMLImageElement | null>(null)

// 缩放相关
const imageScale = ref<number>(1)

// 图片配置
const imageConfig = computed(() => ({
  image: imageElement.value,
  width: stageConfig.value.width,
  height: stageConfig.value.height
}))

// 变换控件配置
const transformerConfig = {
  rotateEnabled: true,
  rotationSnaps: [0, 45, 90, 135, 180, 225, 270, 315],
  rotationSnapTolerance: 5,
  enabledAnchors: props.annotationStep === 'character' 
    ? ['top-left', 'top-right', 'bottom-left', 'bottom-right'] 
    : ['top-left', 'top-right', 'bottom-left', 'bottom-right', 'top', 'bottom', 'left', 'right'],
  boundBoxFunc: (oldBox: any, newBox: any) => {
    const minSize = props.annotationStep === 'character' ? 10 : 20
    if (newBox.width < minSize || newBox.height < minSize) {
      return oldBox
    }
    return newBox
  },
  rotateAnchorOffset: 30,
  rotateAnchorCursor: 'grab',
  rotateAnchorStroke: '#00ff00',
  rotateAnchorFill: '#fff',
}

// 舞台配置
const stageConfig = ref({
  width: 800,
  height: 600,
})

const annotations = ref<Annotation[]>([])
const currentAnnotations = ref<any[]>([])

// 添加防抖定时器引用
const saveTimer = ref<number | null>(null)
const lastSavedAnnotations = ref<string>('') // 用于比较是否有实际改动

// 内部状态管理
const annotationStep = ref<'region' | 'character'>('region')
const selectedRegionId = ref<string | undefined>()

// 内部标注类型
interface InternalAnnotation {
  id: string
  x: number
  y: number
  width: number
  height: number
  rotation: number
  label?: string
  parentId?: string 
  type: 'text_region' | 'character'
}

// 坐标转换工具
const coordinateUtils = {
  toOriginalCoordinates(point: InternalAnnotation): BBox {
    if (!stage.value) return {
      x: point.x,
      y: point.y,
      width: point.width,
      height: point.height,
      rotation: point.rotation || 0
    }

    const stageInstance = stage.value.getStage()
    const scale = stageInstance.scaleX()
    const stagePos = stageInstance.position()

    return {
      x: Math.max(0, (point.x - stagePos.x) / scale),
      y: Math.max(0, (point.y - stagePos.y) / scale),
      width: Math.abs(point.width / scale),
      height: Math.abs(point.height / scale),
      rotation: point.rotation || 0
    }
  },

  toScreenCoordinates(bbox: BBox): Omit<InternalAnnotation, 'id' | 'type' | 'label' | 'parentId'> {
    // 添加默认值
    const defaultBBox = {
      x: 0,
      y: 0,
      width: 0,
      height: 0,
      rotation: 0,
      ...bbox
    }

    if (!stage.value) return defaultBBox

    const stageInstance = stage.value.getStage()
    const scale = stageInstance.scaleX()
    const stagePos = stageInstance.position()

    return {
      x: defaultBBox.x * scale + stagePos.x,
      y: defaultBBox.y * scale + stagePos.y,
      width: Math.abs(defaultBBox.width * scale),
      height: Math.abs(defaultBBox.height * scale),
      rotation: defaultBBox.rotation || 0
    }
  }
}

// 转换函数
const convertToInternalFormat = (ann: TextRegionAnnotation | CharacterAnnotation): InternalAnnotation => {
  if (!ann.bbox) {
    throw new Error('Missing bbox in annotation')
  }

  const screenCoords = coordinateUtils.toScreenCoordinates(ann.bbox)
  
  return {
    id: ann.id,
    ...screenCoords,
    type: ann.type,
    label: ann.type === 'character' ? ann.label : undefined,
    parentId: ann.parent_id || undefined
  }
}

const convertToApiFormat = (ann: InternalAnnotation): TextRegionAnnotation | CharacterAnnotation => {
  const bbox = coordinateUtils.toOriginalCoordinates(ann)
  
  if (ann.type === 'character') {
    return {
      id: ann.id,
      type: 'character',
      bbox,
      parent_id: ann.parentId!,
      label: ann.label!
    }
  }
  
  return {
    id: ann.id,
    type: 'text_region',
    bbox,
    parent_id: null
  }
}

// 使用 watchEffect 优化更新
watchEffect(() => {
  console.log('接收到的 modelValue:', props.currentImage)
  
  if (props.currentImage && Array.isArray(props.currentImage)) {
    currentAnnotations.value = props.currentImage.map(ann => {
      try {
        // 如果是后端返回的数据格式
        if ('labels' in ann) {
          const label = Array.isArray(ann.labels) ? ann.labels[0] : ann.labels
          if (!label?.bbox) {
            console.warn('Invalid annotation data:', ann)
            return null
          }

          // 转换为屏幕坐标
          const screenCoords = coordinateUtils.toScreenCoordinates({
            x: label.bbox.x,
            y: label.bbox.y,
            width: label.bbox.width,
            height: label.bbox.height
          })

          // 构建标注对象
          const annotation: Annotation = {
            id: ann.id,
            x: screenCoords.x,
            y: screenCoords.y,
            width: screenCoords.width!,
            height: screenCoords.height!,
            rotation: label.bbox.rotation ?? 0,
            label: label.label || '',
            type: label.type || (props.annotationStep === 'character' ? 'character' : 'text_region'),
            parentId: ann.parent_id
          }

          console.log('转换后的标注:', annotation)
          return annotation
        }
        
        // 如果已经是内部格式
        if ('x' in ann) {
          return ann as Annotation
        }

        console.warn('Unknown annotation format:', ann)
        return null
      } catch (error) {
        console.error('Error converting annotation:', error, ann)
        return null
      }
    }).filter(Boolean) as Annotation[]
  } else {
    currentAnnotations.value = []
  }
})

// 使用 computed 优化渲染
const visibleAnnotations = computed(() => {
  const filtered = currentAnnotations.value.filter(ann => {
    if (props.annotationStep === 'region') {
      return ann.type === 'text_region'
    } else {
      return ann.type === 'character' && ann.parentId === props.selectedRegionId
    }
  })
  console.log('可见标注:', filtered)
  return filtered
})

// 监听图片URL变化
watch(() => props.imageUrl, (newUrl) => {
  if (newUrl) {
    loadImage()
  }
}, { immediate: false })

// 初始化标注数据
onMounted(() => {
  loadImage()
  nextTick(() => {
    if (transformer.value && !transformer.value.nodes) {
      transformer.value.nodes = function(nodes) {
        if (nodes === undefined) {
          return this.getNodes()
        }
        this.setNodes(nodes)
        return this
      }
    }
    rotationTip.value = true
    setTimeout(() => {
      rotationTip.value = false
    }, 5000)
  })
})

// 组件卸载时清理
onUnmounted(() => {
  if (transformer.value) {
    transformer.value.destroy()
  }
  if (stage.value) {
    stage.value.destroy()
  }
  annotations.value = []
  selectedIndex.value = -1
  imageConfig.value.image = null
  if (saveTimer.value) {
    clearTimeout(saveTimer.value)
  }
})

// 加载图片
const loadImage = () => {
  const img = new Image()
  img.crossOrigin = 'anonymous'
  
  img.onload = () => {
    // 计算适合容器的图片尺寸
    const containerWidth = container.value?.clientWidth || 800
    const containerHeight = container.value?.clientHeight || 600
    const maxWidth = containerWidth
    const maxHeight = containerHeight
    
    // 计算缩放比例，保持宽高比
    const scale = Math.min(maxWidth / img.width, maxHeight / img.height)
    
    // 更新舞台尺寸
    stageConfig.value = {
      width: img.width * scale,
      height: img.height * scale
    }
    
    // 更新图片元素
    imageElement.value = img
    
    // 重置缩放
    imageScale.value = props.scale || 1
    
    if (stage.value) {
      const stageInstance = stage.value.getStage()
      if (stageInstance) {
        stageInstance.scale({ x: imageScale.value, y: imageScale.value })
        stageInstance.position({ x: 0, y: 0 })
        stageInstance.batchDraw()
      }
    }
  }
  
  img.onerror = (error) => {
    console.error('图片加载失败:', error)
    imageElement.value = null
  }
  
  img.src = props.imageUrl
}

// 阻止默认事件
const preventDefault = (e: Event) => {
  e.preventDefault()
}

// 鼠标按下
const handleMouseDown = (e: any) => {
  if (!isDrawing.value) return
  
  const stage = e.target.getStage()
  const pos = stage.getPointerPosition()
  if (!pos) return // 添加空值检查
  
  startPoint.value = pos
  
  const newAnnotation: Annotation = {
    id: crypto.randomUUID(), // 生成唯一ID
    x: pos.x,
    y: pos.y,
    width: 0,
    height: 0,
    rotation: 0,
    label: '',
    type: props.annotationStep === 'character' ? 'character' : 'text_region',
    parentId: props.annotationStep === 'character' ? props.selectedRegionId : undefined
  }
  
  drawingRect.value = newAnnotation
  annotations.value.push(newAnnotation)
}

// 鼠标移动
const handleMouseMove = (e: any) => {
  if (!isDrawing.value || !drawingRect.value) return
  
  const stage = e.target.getStage()
  const pos = stage.getPointerPosition()
  
  const width = pos.x - startPoint.value.x
  const height = pos.y - startPoint.value.y
  
  drawingRect.value.width = width
  drawingRect.value.height = height
  
  // 更新最后一个标注框
  annotations.value[annotations.value.length - 1] = { ...drawingRect.value }
}

// 鼠标松开
const handleMouseUp = () => {
  if (!isDrawing.value || !drawingRect.value) return
  
  if (
    Math.abs(drawingRect.value.width) < 10 ||
    Math.abs(drawingRect.value.height) < 10
  ) {
    annotations.value.pop() // 删除太小的框
  } else {
    // 完成绘制，选中新框
    selectedIndex.value = annotations.value.length - 1
    
    // 使用防抖保存
    const updatedAnnotations = [...annotations.value]
    handleSave(updatedAnnotations)
  }
  
  isDrawing.value = false
  drawingRect.value = null
}

// 处理标注文字变化
const handleLabelChange = () => {
  const updatedAnnotations = [...annotations.value]
  handleSave(updatedAnnotations)
}

// 切换绘制模式
const toggleDrawing = () => {
  isDrawing.value = !isDrawing.value
  if (isDrawing.value) {
    selectedIndex.value = -1 // 取消选中
    nextTick(() => {
      if (transformer.value && transformer.value.nodes) {
        transformer.value.nodes([]) // 清除变换控件
        transformer.value.getLayer()?.batchDraw()
      }
    })
  }
}

// 选择矩形框
const selectRect = (index: number, e: KonvaEventObject<MouseEvent>) => {
  // 阻止事件冒泡，避免触发 stage 的点击事件
  e.cancelBubble = true
  
  // 如果正在绘制，不处理选择
  if (isDrawing.value) return
  
  // 更新选中索引
  selectedIndex.value = index
  
  // 更新变换控件
  nextTick(() => {
    const node = rectRefs.value[index]
    if (transformer.value && transformer.value.nodes && node) {
      transformer.value.nodes([node])
      transformer.value.getLayer()?.batchDraw()
    }
  })
}

// 处理舞台点击
const handleStageClick = (e: KonvaEventObject<MouseEvent>) => {
  // 如果点击的是舞台本身（而不是其他元素）
  if (e.target === e.target.getStage()) {
    // 取消选中
    selectedIndex.value = -1
    // 清除变换控件
    nextTick(() => {
      if (transformer.value && transformer.value.nodes) {
        transformer.value.nodes([])
        transformer.value.getLayer()?.batchDraw()
      }
    })
  }
}

// 处理字符标注切换
const handleAnnotateCharacters = (regionId: string) => {
  selectedRegionId.value = regionId
  annotationStep.value = 'character'
}

// 处理返回区域标注
const handleBackToRegions = () => {
  annotationStep.value = 'region'
  selectedRegionId.value = undefined
}

// 标注状态管理
const updateAnnotationStatus = () => {
  let status: 'region_annotated' | 'char_annotated' | 'completed' = 'region_annotated'
  
  if (annotations.value.length === 0) {
    status = 'region_annotated'
  } else if (annotations.value.some(ann => ann.type === 'character')) {
    status = 'completed'
  } else {
    status = 'char_annotated'
  }
  
  emit('annotationStatusChange', status)
}

// 修改后端返回的数据类型定义
interface ApiAnnotationResponse {
  annotations: {
    id: string | number
    labels: {
      id: string | number
      type: 'text_region' | 'character'
      bbox: {
        x: number
        y: number
        width: number
        height: number
        rotation: number
      }
      label?: string
      parent_id: string | null
    }
    parent_id: string | null
  }[]
}

// 修改加载标注数据的函数
const loadAnnotations = async () => {
  try {
    const response = await annotationService.getImageAnnotation(props.imageId)
    console.log('后端返回的标注数据:', response)
    
    // 确保数据格式正确
    if (!response?.annotations) {
      console.warn('Invalid response format:', response)
      annotations.value = []
      return
    }

    // 转换为内部格式
    annotations.value = response.annotations
      .map(ann => {
        try {
          if (!ann.labels || !ann.labels.bbox) {
            console.warn('Invalid annotation format:', ann)
            return null
          }

          return convertToInternalFormat({
            id: ann.id.toString(),
            type: ann.labels.type,
            bbox: ann.labels.bbox,
            parent_id: ann.parent_id,
            label: ann.labels.label
          })
        } catch (error) {
          console.error('Error converting annotation:', error, ann)
          return null
        }
      })
      .filter(Boolean) // 过滤掉无效的数据

    console.log('转换后的标注数据:', annotations.value)
  } catch (error) {
    console.error('加载标注失败:', error)
    annotations.value = [] // 出错时清空标注
    $q.notify({
      type: 'negative',
      message: '加载标注失败，请重试',
      position: 'top'
    })
  }
}

// 修改保存标注的函数
const handleSave = async (annotations: InternalAnnotation[]) => {
  try {
    // 转换为API格式
    const apiAnnotations = annotations.map(ann => {
      const bbox = coordinateUtils.toOriginalCoordinates(ann)
      return {
        id: ann.id,
        labels: {
          id: ann.id,
          type: ann.type,
          bbox,
          label: ann.type === 'character' ? ann.label : undefined,
          parent_id: ann.parentId
        },
        parent_id: ann.parentId
      }
    })

    await annotationService.saveAnnotation(props.imageId, { annotations: apiAnnotations })
    
    // 更新最后保存的状态
    lastSavedAnnotations.value = JSON.stringify(annotations)
    
    // 通知父组件
    emit('update:annotations', apiAnnotations)
    updateAnnotationStatus()

    $q.notify({
      type: 'positive',
      message: '保存成功',
      position: 'top'
    })
  } catch (error) {
    console.error('保存标注失败:', error)
    $q.notify({
      type: 'negative',
      message: '保存标注失败，请重试',
      position: 'top'
    })
  }
}

// 监听图片变化
watch(() => props.imageId, (newId) => {
  if (newId) {
    loadAnnotations()
    // 重置状态
    annotationStep.value = 'region'
    selectedRegionId.value = undefined
  }
}, { immediate: true })

// 修改拖拽结束处理
const handleDragEnd = (index: number, e: KonvaEventObject<MouseEvent>) => {
  const node = e.target as Konva.Rect
  const updatedAnnotations = [...annotations.value]
  if (updatedAnnotations[index]) {
    // 获取新位置并保持原始比例
    const newPos = {
      x: node.x(),
      y: node.y(),
      width: updatedAnnotations[index].width,  // 保持原始宽度
      height: updatedAnnotations[index].height  // 保持原始高度
    }

    // 更新标注数据，保持其他属性不变
    updatedAnnotations[index] = {
      ...updatedAnnotations[index],
      ...newPos
    }

    // 重置节点位置，避免累积误差
    node.position({
      x: newPos.x,
      y: newPos.y
    })

    // 更新状态
    annotations.value = updatedAnnotations
    handleSave(updatedAnnotations)
  }
}

// 修改变换结束处理
const handleTransformEnd = (index: number, e: KonvaEventObject<Event>) => {
  const node = e.target as Konva.Rect
  const updatedAnnotations = [...annotations.value]
  if (updatedAnnotations[index]) {
    const scaleX = node.scaleX()
    const scaleY = node.scaleY()
    
    // 计算新的尺寸和位置
    const newData = {
      width: Math.abs(node.width() * scaleX),
      height: Math.abs(node.height() * scaleY),
      x: node.x(),
      y: node.y(),
      rotation: node.rotation()
    }
    
    // 更新标注数据，保持其他属性不变
    updatedAnnotations[index] = {
      ...updatedAnnotations[index],
      ...newData
    }
    
    // 重置节点状态
    node.scaleX(1)
    node.scaleY(1)
    node.position({
      x: newData.x,
      y: newData.y
    })
    node.width(newData.width)
    node.height(newData.height)
    
    // 更新状态
    annotations.value = updatedAnnotations
    handleSave(updatedAnnotations)
  }
}

// 修改删除处理
const deleteSelected = async () => {
  if (selectedIndex.value === -1) return

  try {
    const annotationToDelete = annotations.value[selectedIndex.value]
    const updatedAnnotations = annotations.value.filter((_, index) => index !== selectedIndex.value)
    
    // 先更新UI
    annotations.value = updatedAnnotations
    selectedIndex.value = -1
    handleSave(updatedAnnotations)
    
    // 延迟删除请求
    if (saveTimer.value) {
      clearTimeout(saveTimer.value)
    }
    
    saveTimer.value = window.setTimeout(async () => {
      try {
        if (props.annotationStep === 'region') {
          await annotationService.deleteAnnotation(props.imageId, annotationToDelete.id)
        } else {
          await annotationService.deleteCharacterAnnotation(
            props.imageId,
            props.selectedRegionId!,
            annotationToDelete.id
          )
        }

        // 删除成功提示
        $q.notify({
          type: 'positive',
          message: '删除成功',
          position: 'top'
        })
      } catch (error) {
        console.error('删除标注失败:', error)
        $q.notify({
          type: 'negative',
          message: '删除标注失败，请重试',
          position: 'top'
        })
        // 删除失败，恢复UI
        annotations.value = [...annotations.value, annotationToDelete]
        handleSave(annotations.value)
      }
    }, 500)
  } catch (error) {
    console.error('删除标注失败:', error)
    $q.notify({
      type: 'negative',
      message: '删除标注失败，请重试',
      position: 'top'
    })
  }
}

// 标注框样式
const getAnnotationStyle = (annotation: Annotation, isSelected: boolean) => {
  const isCharacter = annotation.type === 'character'
  return {
    x: annotation.x,
    y: annotation.y,
    width: annotation.width,
    height: annotation.height,
    rotation: annotation.rotation || 0,
    stroke: isSelected ? '#00ff00' : isCharacter ? '#ff9800' : '#2196f3',
    strokeWidth: isCharacter ? 1 : 2,
    dash: isCharacter ? undefined : [5, 5],
    draggable: !isDrawing.value,
    opacity: isSelected ? 1 : 0.8,
    transformsEnabled: 'all',
    strokeScaleEnabled: false,
  }
}

// 调整内部缩放
const adjustImageScale = (delta: number) => {
  const newScale = Math.max(0.1, Math.min(5, imageScale.value + delta))
  imageScale.value = newScale
  
  if (stage.value) {
    // 获取 Konva Stage 实例
    const stageInstance = stage.value.getStage()
    if (stageInstance) {
      stageInstance.scale({ x: newScale, y: newScale })
      stageInstance.batchDraw()
    }
  }
}

// 处理滚轮缩放
const handleWheel = (e: KonvaEventObject<WheelEvent>) => {
  e.evt.preventDefault()
  
  const scaleBy = 1.1
  const stageInstance = e.target.getStage()
  const oldScale = stageInstance.scaleX()
  
  const mousePointTo = {
    x: stageInstance.getPointerPosition().x / oldScale - stageInstance.x() / oldScale,
    y: stageInstance.getPointerPosition().y / oldScale - stageInstance.y() / oldScale,
  }
  
  const newScale = e.evt.deltaY > 0 ? oldScale / scaleBy : oldScale * scaleBy
  
  stageInstance.scale({ x: newScale, y: newScale })
  
  const newPos = {
    x: -(mousePointTo.x - stageInstance.getPointerPosition().x / newScale) * newScale,
    y: -(mousePointTo.y - stageInstance.getPointerPosition().y / newScale) * newScale,
  }
  
  stageInstance.position(newPos)
  stageInstance.batchDraw()
  
  imageScale.value = newScale
}

// 添加旋转提示
const rotationTip = ref(false)
</script>

<style lang="scss" scoped>
.rect-annotator-container {
  position: relative;
  width: 100%;
  height: 100%;
  background: #2b2b2b;
  border-radius: 8px;
  overflow: hidden;
}

.stage-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.image-controls {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 1;
  background: rgba(43, 43, 43, 0.9);
  padding: 16px;
  border-radius: 8px;
  color: #fff;
}

.control-item {
  
  label {
    margin-right: 8px;
    font-size: 14px;
    color: #e0e0e0;
  }
}

.scale-control {
  display: flex;
  align-items: center;
  justify-content: space-between;
  
  .q-btn-group {
    margin-left: 8px;
  }
}

.annotation-controls {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 1;
  background: rgba(255, 255, 255, 0.9);
  padding: 8px;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.step-indicator {
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 14px;
}

.rotation-tip {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  pointer-events: none;
  animation: fadeInOut 5s ease-in-out;
}

@keyframes fadeInOut {
  0%, 100% { opacity: 0; }
  10%, 90% { opacity: 1; }
}
</style>