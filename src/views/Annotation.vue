<template>
  <q-page class="annotation-page q-pa-md">
    <!-- 使用 q-scroll-area 包裹整个内容 -->
    <q-scroll-area style="height: calc(100vh - 150px)" horizontal>
      <div class="annotation-layout">
        <!-- 数据集列表 -->
        <div class="dataset-section">
          <q-card class="dataset-card">
            <q-card-section>
              <!-- 标题栏 -->
              <div class="row items-center q-pb-sm">
                <div class="col">
                  <div class="text-h6">数据集</div>
                </div>
                <div class="col-auto">
                  <q-btn icon="add" size="lg" @click="showCreateDatasetDialog">
                    <q-tooltip>新建数据集</q-tooltip>
                  </q-btn>
                </div>
              </div>

              <!-- 统计信息 -->
              <div class="dataset-stats q-mb-md">
                <div class="text-caption text-grey-7">
                  {{ datasets?.length || 0 }} 个数据集
                </div>
                <q-chip v-if="currentDataset" dense :color="getDatasetTypeColor(currentDataset.type)" text-color="white"
                  size="sm">
                  {{ getDatasetTypeLabel(currentDataset.type) }}
                </q-chip>
              </div>

              <!-- 添加滚动区域 -->
              <q-scroll-area style="height: calc(100vh - 320px)">
                <q-list separator class="dataset-list">
                  <q-item v-for="dataset in datasets" :key="dataset.id" clickable v-ripple
                    @click="selectDataset(dataset)" :class="{ 'dataset-selected': currentDataset?.id === dataset.id }">
                    <q-item-section avatar>
                      <q-icon :name="getDatasetTypeIcon(dataset.type)" :color="getDatasetTypeColor(dataset.type)" />
                    </q-item-section>

                    <q-item-section>
                      <q-item-label>{{ dataset.name }}</q-item-label>
                      <q-item-label caption class="dataset-info">
                        <span>{{ dataset.imageCount }} 张图片</span>
                        <q-chip dense :color="getDatasetTypeColor(dataset.type)" text-color="white" size="xs">
                          {{ getDatasetTypeLabel(dataset.type) }}
                        </q-chip>
                      </q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-scroll-area>
            </q-card-section>
          </q-card>
        </div>

        <!-- 标注区域 -->
        <div class="annotation-section">
          <q-card class="annotation-card">
            <q-card-section>
              <div class="row items-center q-mb-md">
                <div class="col">
                  <div class="text-h6">{{ currentDataset?.name || '请选择数据集' }}</div>
                </div>
                <div class="col-auto">
                  <q-btn-group flat v-if="currentDataset">
                    <!-- 批量删除按钮 -->
                    <q-btn v-if="selectedImages.length > 0" flat round icon="delete" color="negative"
                      @click="confirmDeleteSelected">
                      <q-tooltip>删除选中</q-tooltip>
                    </q-btn>

                    <!-- 上传图片按钮 -->
                    <q-btn flat round icon="upload" @click="uploadImagesDialog = true">
                      <q-tooltip>上传图片</q-tooltip>
                    </q-btn>

                    <!-- 重命名按钮 -->
                    <q-btn flat round icon="edit" @click="showRenameDialog(currentDataset)">
                      <q-tooltip>重命名</q-tooltip>
                    </q-btn>

                    <!-- 视图切换按钮 -->
                    <q-btn flat round icon="grid_view" @click="viewMode = 'grid'"
                      :color="viewMode === 'grid' ? 'primary' : ''">
                      <q-tooltip>网格视图</q-tooltip>
                    </q-btn>

                    <q-btn flat round icon="view_carousel" @click="viewMode = 'carousel'"
                      :color="viewMode === 'carousel' ? 'primary' : ''">
                      <q-tooltip>标注视图</q-tooltip>
                    </q-btn>

                    <!-- 更多按钮 -->
                    <q-btn flat round icon="more_vert">
                      <q-tooltip>更多</q-tooltip>
                      <q-menu>
                        <q-list padding style="min-width: 150px">
                          <q-item clickable v-close-popup @click="confirmDeleteDataset(currentDataset)"
                            class="text-negative" style="min-height: 40px">
                            <q-item-section avatar style="min-width: 28px">
                              <q-icon name="delete" />
                            </q-item-section>
                            <q-item-section>
                              <q-item-label class="text-caption">删除数据集</q-item-label>
                            </q-item-section>
                          </q-item>
                        </q-list>
                      </q-menu>
                    </q-btn>
                  </q-btn-group>
                </div>
              </div>

              <!-- 网格视图 -->
              <div v-if="viewMode === 'grid'" class="image-grid">
                <q-scroll-area style="height: calc(100vh - 320px)">
                  <div class="row q-col-gutter-sm">
                    <div v-for="image in datasetImages" :key="image.id" class="col-auto">
                      <div class="image-container">
                        <!-- 添加标注状态标记 -->
                        <q-badge v-if="image.isAnnotated" floating class="annotation-badge">
                          <q-icon name="task_alt" size="xs" />
                        </q-badge>

                        <q-img :src="image.url" :ratio="1" class="image-thumbnail" style="width: 120px"
                          @click="toggleImageSelection(image)" :class="{
                            'image-selected': selectedImages.includes(image.id),
                            'image-annotated': image.isAnnotated
                          }">
                          <template v-slot:loading>
                            <q-skeleton type="rect" />
                          </template>
                        </q-img>
                        <div class="image-actions">
                          <q-btn flat round dense icon="delete" color="negative" @click.stop="deleteImage(image)" />
                          <q-btn flat round dense icon="edit" color="primary" @click.stop="startAnnotation(image)" />
                        </div>
                      </div>
                    </div>
                  </div>
                </q-scroll-area>
              </div>

              <!-- 标注视图 -->
              <div v-else class="annotation-view">
                <div class="annotation-container">
                  <template v-if="currentImage">
                    <rect-annotator :image-url="currentImage.url" :image-id="currentImage.id"
                      :current-image="currentImage" @update:annotations="handleAnnotationsUpdate" />
                  </template>
                  <template v-else>
                    <div class="text-center text-grey-6">
                      <q-icon name="image" size="48px" />
                      <div class="q-mt-sm">请选择图片进行标注</div>
                    </div>
                  </template>
                </div>

                <!-- 缩略图列表 -->
                <div class="thumbnail-list">
                  <div class="thumbnail-scroll-container">
                    <q-btn flat round dense icon="chevron_left" class="scroll-btn left"
                      @click="scrollThumbnails('left')" />
                    <q-scroll-area horizontal style="height: 100px" ref="thumbnailScroll">
                      <div class="row no-wrap">
                        <div v-for="image in datasetImages" :key="image.id" class="col-auto">
                          <div class="thumbnail-container">
                            <!-- 添加标注状态标记 -->
                            <q-badge v-if="image.isAnnotated" floating class="annotation-badge">
                              <q-icon name="task_alt" size="xs" />
                            </q-badge>

                            <q-img :src="image.url" :ratio="1" class="thumbnail-image" style="width: 80px"
                              @click="selectImage(image)" :class="{
                                'thumbnail-selected': currentImage?.id === image.id,
                                'image-annotated': image.isAnnotated
                              }">
                              <template v-slot:loading>
                                <q-skeleton type="rect" />
                              </template>
                            </q-img>
                          </div>
                        </div>
                      </div>
                    </q-scroll-area>
                    <q-btn flat round dense icon="chevron_right" class="scroll-btn right"
                      @click="scrollThumbnails('right')" />
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </q-scroll-area>

    <!-- 上传图片对话框 -->
    <q-dialog v-model="uploadImagesDialog">
      <q-card style="min-width: 350px">
        <q-card-section class="row items-center">
          <div class="text-h6">上传图片</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section>
          <q-file v-model="uploadFiles" label="选择图片" outlined multiple accept=".jpg,.jpeg,.png"
            style="max-width: 300px">
            <template v-slot:prepend>
              <q-icon name="attach_file" />
            </template>
          </q-file>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="取消" color="primary" v-close-popup />
          <q-btn flat label="上传" color="primary" @click="handleUploadImages" :loading="uploading" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- 创建数据集对话框 -->
    <q-dialog v-model="createDatasetDialog">
      <q-card style="min-width: 350px">
        <q-card-section class="row items-center">
          <div class="text-h6">新建数据集</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <q-input v-model="newDatasetName" label="数据集名称" outlined :rules="[val => !!val || '请输入数据集名称']" />

          <q-select v-model="newDatasetType" :options="[
            { label: '文本区域数据集', value: DatasetType.TEXT_REGION },
            { label: 'OCR数据集', value: DatasetType.OCR }
          ]" label="数据集类型" outlined emit-value map-options />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="取消" color="primary" v-close-popup />
          <q-btn flat label="创建" color="primary" @click="createDataset" :loading="creating"
            :disable="!newDatasetName.trim()" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- 重命名数据集对话框 -->
    <q-dialog v-model="renameDatasetDialog" persistent>
      <q-card style="min-width: 350px">
        <q-card-section>
          <div class="text-h6">重命名数据集</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input v-model="renameDatasetName" label="数据集名称" dense autofocus :rules="[val => !!val || '请输入数据集名称']"
            @keyup.enter="renameDataset" />
        </q-card-section>

        <q-card-actions align="right" class="text-primary">
          <q-btn flat label="取消" v-close-popup />
          <q-btn flat label="确定" :loading="renaming" :disable="!renameDatasetName" @click="renameDataset" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- 删除确认对话框 -->
    <q-dialog v-model="deleteConfirmDialog">
      <q-card>
        <q-card-section class="row items-center">
          <div class="text-h6">确认删除</div>
        </q-card-section>

        <q-card-section>
          <template v-if="selectedImages.length > 0">
            确定要删除选中的 {{ selectedImages.length }} 张图片吗？此操作不可恢复。
          </template>
          <template v-else>
            确定要删除数据集 "{{ datasetToDelete?.name }}" 吗？此操作不可恢复。
          </template>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="取消" color="primary" v-close-popup />
          <q-btn flat label="删除" color="negative" @click="handleDelete" :loading="deleting" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { useQuasar } from 'quasar'
import { AnnotationService } from '../services/annotation'
import type { Dataset, Image, AnnotationLabel } from '../services/annotation'
import { DatasetType } from '../services/annotation'
import RectAnnotator from '../components/annotation/RectAnnotator.vue'

const $q = useQuasar()
const annotationService = new AnnotationService()

// 状态管理
const datasets = ref<Dataset[]>([])
const currentDataset = ref<Dataset | null>(null)
const datasetImages = ref<Image[]>([])
const currentImage = ref<Image | null>(null)
const currentImageIndex = ref<number>(-1)
const selectedImages = ref<number[]>([])

// 对话框状态
const createDatasetDialog = ref(false)
const renameDatasetDialog = ref(false)
const uploadImagesDialog = ref(false)
const deleteConfirmDialog = ref(false)

// 表单数据
const newDatasetName = ref('')
const newDatasetType = ref<DatasetType>(DatasetType.TEXT_REGION)
const renameDatasetName = ref('')
const uploadFiles = ref<File[]>([])
const datasetToDelete = ref<Dataset | null>(null)

// 加载状态
const creating = ref(false)
const renaming = ref(false)
const uploading = ref(false)
const deleting = ref(false)

// 视图模式
const viewMode = ref<'grid' | 'carousel'>('grid')

// 缩略图导航
const thumbnailScroll = ref<any>(null)

// 数据集管理
const loadDatasets = async () => {
  try {
    const response = await annotationService.getDatasets()
    datasets.value = response
  } catch (error) {
    console.error('加载数据集失败:', error)
    $q.notify({
      type: 'negative',
      message: '加载数据集失败，请重试',
      position: 'top'
    })
  }
}

const createDataset = async () => {
  if (!newDatasetName.value.trim()) return

  try {
    creating.value = true
    const dataset = await annotationService.createDataset({
      name: newDatasetName.value.trim(),
      type: newDatasetType.value
    })

    datasets.value.push(dataset)
    createDatasetDialog.value = false
    newDatasetName.value = ''
    newDatasetType.value = DatasetType.TEXT_REGION

    $q.notify({
      type: 'positive',
      message: '创建数据集成功',
      position: 'top'
    })
  } catch (error) {
    console.error('创建数据集失败:', error)
    $q.notify({
      type: 'negative',
      message: '创建数据集失败，请重试',
      position: 'top'
    })
  } finally {
    creating.value = false
  }
}

const renameDataset = async () => {
  if (!currentDataset.value || !renameDatasetName.value) return

  try {
    renaming.value = true
    const updatedDataset = await annotationService.renameDataset(
      currentDataset.value.id,
      renameDatasetName.value
    )

    // 更新本地数据
    const index = datasets.value.findIndex(d => d.id === updatedDataset.id)
    if (index !== -1) {
      datasets.value[index] = updatedDataset
    }

    // 更新当前数据集
    if (currentDataset.value.id === updatedDataset.id) {
      currentDataset.value = updatedDataset
    }

    renameDatasetDialog.value = false
    renameDatasetName.value = ''

    $q.notify({
      type: 'positive',
      message: '重命名成功',
      position: 'top'
    })
  } catch (error) {
    console.error('重命名数据集失败:', error)
    $q.notify({
      type: 'negative',
      message: error instanceof Error ? error.message : '重命名失败，请重试',
      position: 'top'
    })
  } finally {
    renaming.value = false
  }
}

const deleteDataset = async () => {
  if (!datasetToDelete.value) return

  try {
    deleting.value = true
    await annotationService.deleteDataset(datasetToDelete.value.id)
    datasets.value = datasets.value.filter(d => d.id !== datasetToDelete.value?.id)

    if (currentDataset.value?.id === datasetToDelete.value.id) {
      currentDataset.value = null
      datasetImages.value = []
      currentImage.value = null
    }

    deleteConfirmDialog.value = false
    datasetToDelete.value = null

    $q.notify({
      type: 'positive',
      message: '删除数据集成功',
      position: 'top'
    })
  } catch (error) {
    console.error('删除数据集失败:', error)
    $q.notify({
      type: 'negative',
      message: '删除数据集失败，请重试',
      position: 'top'
    })
  } finally {
    deleting.value = false
  }
}

// 图片管理
const selectDataset = async (dataset: Dataset) => {
  try {
    currentDataset.value = dataset
    currentImage.value = null
    selectedImages.value = []

    const images = await annotationService.getDatasetImages(dataset.id)
    datasetImages.value = images
  } catch (error) {
    console.error('选择数据集失败:', error)
    $q.notify({
      type: 'negative',
      message: '加载图片失败，请重试',
      position: 'top'
    })
  }
}

const handleUploadImages = async () => {
  if (!currentDataset.value || !uploadFiles.value.length) return

  try {
    uploading.value = true
    const newImages = await annotationService.uploadImages(
      currentDataset.value.id,
      uploadFiles.value
    )

    datasetImages.value.push(...newImages)
    uploadImagesDialog.value = false
    uploadFiles.value = []

    // 更新数据集图片数量
    const index = datasets.value.findIndex(d => d.id === currentDataset.value?.id)
    if (index !== -1) {
      datasets.value[index] = {
        ...datasets.value[index],
        imageCount: datasets.value[index].imageCount + newImages.length
      }
    }

    $q.notify({
      type: 'positive',
      message: '上传图片成功',
      position: 'top'
    })
  } catch (error) {
    console.error('上传图片失败:', error)
    $q.notify({
      type: 'negative',
      message: '上传图片失败，请重试',
      position: 'top'
    })
  } finally {
    uploading.value = false
  }
}

// 标注相关
const handleAnnotationsUpdate = (annotations: AnnotationLabel[]) => {
  console.log('标注已更新:', annotations)
}

// 缩略图导航
const scrollThumbnails = (direction: 'left' | 'right') => {
  const scrollAmount = 200
  const scrollArea = thumbnailScroll.value?.$refs.scroll as HTMLElement
  if (scrollArea) {
    const currentScroll = scrollArea.scrollLeft
    scrollArea.scrollTo({
      left: currentScroll + (direction === 'left' ? -scrollAmount : scrollAmount),
      behavior: 'smooth'
    })
  }
}

// 图片选择
const selectImage = async (image: Image) => {
  if (!image) return

  currentImage.value = image
  currentImageIndex.value = datasetImages.value.findIndex(img => img.id === image.id)

  // 滚动到选中的图片
  nextTick(() => {
    const scrollArea = thumbnailScroll.value?.$refs.scroll as HTMLElement
    if (scrollArea) {
      const containerWidth = scrollArea.clientWidth
      const thumbnailWidth = 88
      const targetScroll = currentImageIndex.value * thumbnailWidth - (containerWidth / 2) + (thumbnailWidth / 2)

      scrollArea.scrollTo({
        left: targetScroll,
        behavior: 'smooth'
      })
    }
  })
}

// 删除图片
const deleteImage = async (image: Image) => {
  try {
    await annotationService.deleteImage(image.id)
    datasetImages.value = datasetImages.value.filter(img => img.id !== image.id)

    if (currentImage.value?.id === image.id) {
      currentImage.value = null
    }

    // 更新数据集图片数量
    if (currentDataset.value) {
      const index = datasets.value.findIndex(d => d.id === currentDataset.value!.id)
      if (index !== -1) {
        datasets.value[index] = {
          ...datasets.value[index],
          imageCount: datasets.value[index].imageCount - 1
        }
      }
    }

    $q.notify({
      type: 'positive',
      message: '删除图片成功',
      position: 'top'
    })
  } catch (error) {
    console.error('删除图片失败:', error)
    $q.notify({
      type: 'negative',
      message: '删除图片失败，请重试',
      position: 'top'
    })
  }
}

// 开始标注
const startAnnotation = async (image: Image) => {
  viewMode.value = 'carousel'
  selectedImages.value = []
  await selectImage(image)
}

// 图片选择
const toggleImageSelection = (image: Image) => {
  const index = selectedImages.value.indexOf(image.id)
  if (index === -1) {
    selectedImages.value.push(image.id)
  } else {
    selectedImages.value.splice(index, 1)
  }
}

// 数据集对话框
const showCreateDatasetDialog = () => {
  newDatasetName.value = ''
  newDatasetType.value = DatasetType.TEXT_REGION
  createDatasetDialog.value = true
}

const showRenameDialog = (dataset: Dataset) => {
  currentDataset.value = dataset
  renameDatasetName.value = dataset.name
  renameDatasetDialog.value = true
}

const confirmDeleteDataset = (dataset: Dataset) => {
  datasetToDelete.value = dataset
  deleteConfirmDialog.value = true
}

// 删除处理
const handleDelete = async () => {
  if (selectedImages.value.length > 0) {
    try {
      deleting.value = true
      await Promise.all(selectedImages.value.map(id => annotationService.deleteImage(id)))

      datasetImages.value = datasetImages.value.filter(img => !selectedImages.value.includes(img.id))

      if (currentImage.value && selectedImages.value.includes(currentImage.value.id)) {
        currentImage.value = null
      }

      // 更新数据集图片数量
      if (currentDataset.value) {
        const index = datasets.value.findIndex(d => d.id === currentDataset.value!.id)
        if (index !== -1) {
          datasets.value[index] = {
            ...datasets.value[index],
            imageCount: datasets.value[index].imageCount - selectedImages.value.length
          }
        }
      }

      selectedImages.value = []
      deleteConfirmDialog.value = false

      $q.notify({
        type: 'positive',
        message: '删除图片成功',
        position: 'top'
      })
    } catch (error) {
      console.error('删除图片失败:', error)
      $q.notify({
        type: 'negative',
        message: '删除图片失败，请重试',
        position: 'top'
      })
    } finally {
      deleting.value = false
    }
  } else if (datasetToDelete.value) {
    await deleteDataset()
  }
}

// 确认删除选中的图片
const confirmDeleteSelected = () => {
  if (selectedImages.value.length === 0) return

  $q.dialog({
    title: '确认删除',
    message: `确定要删除选中的 ${selectedImages.value.length} 张图片吗？`,
    persistent: true,
    ok: {
      label: '删除',
      color: 'negative',
      flat: true
    },
    cancel: {
      label: '取消',
      color: 'primary',
      flat: true
    }
  }).onOk(async () => {
    try {
      deleting.value = true
      await Promise.all(selectedImages.value.map(id => annotationService.deleteImage(id)))

      // 从列表中移除已删除的图片
      datasetImages.value = datasetImages.value.filter(img => !selectedImages.value.includes(img.id))

      // 如果当前显示的图片被删除，清空当前图片
      if (currentImage.value && selectedImages.value.includes(currentImage.value.id)) {
        currentImage.value = null
      }

      // 更新数据集图片数量
      if (currentDataset.value) {
        const index = datasets.value.findIndex(d => d.id === currentDataset.value!.id)
        if (index !== -1) {
          datasets.value[index] = {
            ...datasets.value[index],
            imageCount: datasets.value[index].imageCount - selectedImages.value.length
          }
        }
      }

      // 清空选中状态
      selectedImages.value = []

      $q.notify({
        type: 'positive',
        message: '删除图片成功',
        position: 'top'
      })
    } catch (error) {
      console.error('批量删除图片失败:', error)
      $q.notify({
        type: 'negative',
        message: '删除图片失败，请重试',
        position: 'top'
      })
    } finally {
      deleting.value = false
    }
  })
}

// 数据集类型相关
const getDatasetTypeLabel = (type: DatasetType): string => {
  const labels = {
    [DatasetType.TEXT_REGION]: '文本区域',
    [DatasetType.OCR]: 'OCR识别'
  }
  return labels[type]
}

const getDatasetTypeColor = (type: DatasetType): string => {
  const colors = {
    [DatasetType.TEXT_REGION]: 'blue-8',
    [DatasetType.OCR]: 'purple-8'
  }
  return colors[type]
}

const getDatasetTypeIcon = (type: DatasetType): string => {
  const icons = {
    [DatasetType.TEXT_REGION]: 'format_shapes',
    [DatasetType.OCR]: 'text_fields'
  }
  return icons[type]
}

// 初始化
onMounted(async () => {
  console.log('组件挂载，开始加载数据集')
  await loadDatasets()
})

// 监听数据集变化
watch(() => currentDataset.value, (newDataset) => {
  if (newDataset) {
    selectDataset(newDataset)
  } else {
    datasetImages.value = []
    currentImage.value = null
    selectedImages.value = []
  }
})
</script>

<style lang="scss" scoped>
.annotation-page {
  background: var(--dark-page);
  overflow: hidden; // 防止出现垂直滚动条
}

.annotation-layout {
  display: flex;
  min-width: 1200px; // 设置最小宽度
  width: 100%;
  height: 100%;
  gap: 16px;
  padding: 10px;
}

.dataset-section {
  width: 300px; // 固定宽度
  flex-shrink: 0; // 防止压缩
}

.annotation-section {
  flex: 1; // 占据剩余空间
  min-width: 800px; // 设置最小宽度
}

.dataset-card,
.annotation-card {
  background: var(--dark-card);
  height: 100%;
}

.annotation-container {
  position: relative;
  width: 100%;
  background: #f5f5f5;
  border-radius: 8px;
  overflow: hidden;
}

.image-grid {
  .image-container {
    position: relative;
    margin: 4px;

    .annotation-badge {
      position: absolute;
      top: 8px;
      left: 8px;
      z-index: 2;
      border-radius: 50%;
      width: 22px;
      height: 22px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--industrial-blue);
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }

    .image-actions {
      position: absolute;
      top: 8px;
      right: 8px;
      display: none;
      background: rgba(0, 0, 0, 0.7);
      border-radius: 8px;
      padding: 4px;
      z-index: 2;
      transition: all 0.2s ease;

      .q-btn {
        margin: 0 2px;

        &:hover {
          transform: scale(1.1);
        }
      }
    }

    &:hover .image-actions {
      display: flex;
      gap: 4px;
    }

    .image-thumbnail {
      border: 2px solid transparent;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s ease;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

      &.image-annotated {
        border-color: var(--industrial-blue);
      }

      &:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
      }

      &.image-selected {
        border-color: var(--primary);
        box-shadow: 0 0 0 2px var(--primary);
      }
    }
  }
}

.thumbnail-list {
  margin-top: 16px;
  border-top: 1px solid var(--dark-separator);

  .thumbnail-scroll-container {
    position: relative;
    padding: 0 40px;

    .scroll-btn {
      position: absolute;
      top: 50%;
      transform: translateY(-50%);
      background: rgba(0, 0, 0, 0.5);
      color: white;
      z-index: 1;

      &.left {
        left: 0;
      }

      &.right {
        right: 0;
      }

      &:hover {
        background: rgba(0, 0, 0, 0.7);
      }
    }
  }

  .thumbnail-container {
    position: relative;
    padding: 0 4px;

    .annotation-badge {
      position: absolute;
      top: 4px;
      left: 8px;
      z-index: 2;
      border-radius: 50%;
      width: 18px;
      height: 18px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--q-positive);
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);

      .q-icon {
        font-size: 12px;
      }
    }

    .thumbnail-image {
      border: 2px solid transparent;
      border-radius: 4px;
      transition: all 0.3s ease;

      &.image-annotated {
        border-color: var(--q-positive);
      }

      &:hover {
        transform: scale(1.1);
      }

      &.thumbnail-selected {
        border-color: var(--primary);
        transform: scale(1.1);
        box-shadow: 0 0 0 2px var(--primary);
      }
    }
  }
}

.annotation-controls {
  .q-btn {
    background: rgba(0, 0, 0, 0.5);
    color: white;
    transition: all 0.2s ease;

    &:hover {
      background: rgba(0, 0, 0, 0.7);
      transform: scale(1.1);
    }
  }
}

.dataset-card {
  background: var(--dark-card);
  display: flex;
  flex-direction: column;

  .q-card-section {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 16px;
  }

  .dataset-stats {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 0;
  }

  .dataset-list {
    border-radius: 8px;
    background: var(--dark-page);
    padding: 4px;

    .q-item {
      border-radius: 6px;
      margin: 2px 0;
      min-height: 56px;
      transition: all 0.3s ease;

      &:hover {
        background: var(--industrial-blue-50);
      }

      &.dataset-selected {
        background: var(--industrial-blue-50);
        border-left: 3px solid var(--primary);
      }

      .dataset-info {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 4px;
      }
    }
  }

  // 自定义滚动条样式
  .q-scrollarea :deep(.q-scrollarea__thumb) {
    width: 4px;
    opacity: 0.3;
    transition: opacity 0.3s;

    &:hover {
      opacity: 0.5;
    }
  }
}

// 添加工业风格变量
:root {
  --industrial-blue-1: rgba(25, 118, 210, 0.05);
  --industrial-blue-2: rgba(25, 118, 210, 0.1);
  --dark-card: #1e1e1e;
  --dark-page: #121212;
  --primary: #1976d2;
  --q-positive: #21ba45;
}

// 自定义水平滚动条样式
:deep(.q-scrollarea__thumb--h) {
  opacity: 0.3;
  transition: opacity 0.3s;

  &:hover {
    opacity: 0.5;
  }
}
</style>