<template>
  <div class="model-tester">
    <div class="row q-col-gutter-md">
      <!-- 测试控制区域 -->
      <div class="col-12 col-md-4">
        <!-- 选择模型区域 -->
        <div v-if="!selectedModel" class="select-model-card">
          <q-icon name="photo_camera" size="3em" color="primary" />
          <div class="text-h6 q-mt-md">请先选择模型</div>
          <div class="text-body2 q-mt-sm text-grey">
            在模型列表中选择一个已训练完成的模型来测试
          </div>
        </div>

        <!-- 控制面板 -->
        <div v-else class="control-panel">
          <div class="text-h6 q-mb-sm">{{ selectedModel.name }}</div>
          <div class="text-caption q-mb-md">模型ID: {{ selectedModel.id }}</div>

          <q-separator class="q-my-md" />

          <!-- 参数设置 -->
          <div class="text-subtitle1 q-mb-sm">参数设置</div>
          <q-input 
            v-model.number="confThreshold" 
            type="number" 
            label="置信度阈值" 
            outlined 
            dense 
            min="0" 
            max="1" 
            step="0.05"
          />
          <q-input 
            v-model.number="iouThreshold" 
            type="number" 
            label="IOU阈值" 
            outlined 
            dense 
            min="0" 
            max="1" 
            step="0.05"
            class="q-mt-sm"
          />

          <q-separator class="q-my-md" />

          <!-- 图像上传 -->
          <div class="text-subtitle1 q-mb-sm">测试图像</div>
          <q-file
            v-model="imageFile"
            label="选择图像"
            outlined
            dense
            accept=".jpg,.jpeg,.png"
            @update:model-value="handleImageSelected"
          >
            <template v-slot:prepend>
              <q-icon name="attach_file" />
            </template>
          </q-file>

          <div class="q-mt-md">
            <q-btn 
              label="测试模型" 
              color="primary" 
              icon="science"
              @click="testModel"
              :loading="loading"
              :disable="!imageFile || loading"
              class="full-width"
            />
          </div>
        </div>
      </div>

      <!-- 测试结果区域 -->
      <div class="col-12 col-md-8">
        <q-card class="result-card">
          <q-card-section>
            <div class="text-h6">测试结果</div>

            <!-- 无图像时显示提示 -->
            <div v-if="!previewUrl && !resultImage" class="no-image-container">
              <q-icon name="insert_photo" size="4em" color="grey-5" />
              <div class="text-body1 q-mt-sm text-grey-7">
                请上传图像进行测试
              </div>
            </div>

            <!-- 预览上传的图像 -->
            <div v-else-if="previewUrl && !resultImage" class="image-preview">
              <img :src="previewUrl" alt="预览图像" />
            </div>

            <!-- 显示检测结果 -->
            <div v-else-if="resultImage" class="result-preview">
              <img :src="resultImage" alt="检测结果" />
              
              <div class="detection-list q-mt-md" v-if="detections && detections.length > 0">
                <div class="text-subtitle1 q-mb-sm">检测到的对象：</div>
                <q-list bordered separator class="rounded-borders">
                  <q-item v-for="(detection, index) in detections" :key="index">
                    <q-item-section avatar>
                      <q-avatar color="primary" text-color="white">
                        {{ index + 1 }}
                      </q-avatar>
                    </q-item-section>
                    <q-item-section>
                      <q-item-label>{{ detection.class_name }}</q-item-label>
                      <q-item-label caption>
                        置信度: {{ (detection.confidence * 100).toFixed(1) }}%
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-badge color="primary">
                        {{ detection.class_id }}
                      </q-badge>
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>
              
              <div class="no-detection q-mt-md" v-else>
                <q-icon name="info" color="info" />
                <span class="q-ml-sm">未检测到任何对象</span>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, watch } from 'vue';
import { useQuasar } from 'quasar';
import { modelService, Model } from '../../services/model';

const props = defineProps<{
  selectedModel: Model | null;
}>();

const emit = defineEmits(['update:selectedModel']);

// Quasar通知
const $q = useQuasar();

// 状态变量
const imageFile = ref<File | null>(null);
const previewUrl = ref<string | null>(null);
const loading = ref(false);
const confThreshold = ref(0.25);
const iouThreshold = ref(0.45);
const resultImage = ref<string | null>(null);
const detections = ref<any[] | null>(null);
const error = ref<string | null>(null);

// 图像选择处理
const handleImageSelected = (file: File | null) => {
  if (!file) {
    previewUrl.value = null;
    return;
  }

  // 创建图像预览
  const reader = new FileReader();
  reader.onload = (e) => {
    previewUrl.value = e.target?.result as string;
  };
  reader.readAsDataURL(file);
  
  // 重置测试结果
  resultImage.value = null;
  detections.value = null;
  error.value = null;
};

// 测试模型
const testModel = async () => {
  if (!props.selectedModel || !imageFile.value) {
    return;
  }

  loading.value = true;
  error.value = null;

  try {
    // 确保我们有base64格式的图像数据
    const imageBase64 = previewUrl.value;
    if (!imageBase64) {
      throw new Error('未能获取图像数据');
    }

    // 调用模型测试API (使用base64)
    const result = await modelService.testModelWithBase64(props.selectedModel.id, imageBase64, {
      conf_thres: confThreshold.value,
      iou_thres: iouThreshold.value
    });

    if (result.success && result.image) {
      resultImage.value = result.image;
      detections.value = result.detections || [];
      
      if (detections.value.length === 0) {
        $q.notify({
          type: 'info',
          message: '未检测到任何对象',
          position: 'top'
        });
      } else {
        $q.notify({
          type: 'positive',
          message: `检测到 ${detections.value.length} 个对象`,
          position: 'top'
        });
      }
    } else {
      error.value = result.error || '测试失败';
      $q.notify({
        type: 'negative',
        message: `测试失败: ${error.value}`,
        position: 'top'
      });
    }
  } catch (err: any) {
    error.value = err.message || '测试过程中发生错误';
    $q.notify({
      type: 'negative',
      message: `测试出错: ${error.value}`,
      position: 'top'
    });
  } finally {
    loading.value = false;
  }
};

// 当模型改变时重置状态
watch(() => props.selectedModel, () => {
  imageFile.value = null;
  previewUrl.value = null;
  resultImage.value = null;
  detections.value = null;
  error.value = null;
  
  // 如果有模型，从模型参数中获取默认阈值
  if (props.selectedModel?.parameters) {
    confThreshold.value = props.selectedModel.parameters.conf_thres || 0.25;
    iouThreshold.value = props.selectedModel.parameters.iou_thres || 0.45;
  }
});
</script>

<style lang="scss" scoped>
.model-tester {
  padding: 8px;
}

.select-model-card,
.control-panel {
  background: var(--dark-card);
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 250px;
  text-align: center;
}

.control-panel {
  align-items: stretch;
  text-align: left;
  justify-content: flex-start;
}

.result-card {
  background: var(--dark-card);
  border-radius: 8px;
  min-height: 450px;
}

.no-image-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 350px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
}

.image-preview,
.result-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 16px;
  
  img {
    max-width: 100%;
    max-height: 350px;
    object-fit: contain;
    border-radius: 4px;
  }
}

.detection-list {
  width: 100%;
}

.no-detection {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
  background: rgba(var(--q-info-rgb), 0.1);
  border-radius: 4px;
}
</style> 