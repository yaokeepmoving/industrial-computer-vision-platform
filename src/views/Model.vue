<template>
  <q-page class="model-page q-pa-md">
    <div class="row q-col-gutter-md">
      <!-- 模型列表 -->
      <div class="col-12 col-lg-4">
        <q-card class="model-card">
          <q-card-section>
            <div class="text-h6">模型列表</div>
            <q-list separator>
              <q-item v-for="i in 3" :key="i" clickable v-ripple>
                <q-item-section avatar>
                  <q-icon name="model_training" color="primary" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>模型 {{ i }}</q-item-label>
                  <q-item-label caption>版本: v1.0.{{ i }}</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-btn-group flat>
                    <q-btn flat round dense icon="play_arrow" color="positive" />
                    <q-btn flat round dense icon="more_vert">
                      <q-menu>
                        <q-list style="min-width: 100px">
                          <q-item clickable v-close-popup>
                            <q-item-section>导出</q-item-section>
                          </q-item>
                          <q-item clickable v-close-popup>
                            <q-item-section class="text-negative">删除</q-item-section>
                          </q-item>
                        </q-list>
                      </q-menu>
                    </q-btn>
                  </q-btn-group>
                </q-item-section>
              </q-item>
            </q-list>
            <q-btn
              color="primary"
              icon="add"
              label="新建模型"
              class="full-width q-mt-md"
            />
          </q-card-section>
        </q-card>
      </div>

      <!-- 训练配置 -->
      <div class="col-12 col-lg-8">
        <q-card class="training-card">
          <q-card-section>
            <div class="text-h6">训练配置</div>
            <div class="row q-col-gutter-md q-mt-md">
              <div class="col-12 col-md-6">
                <q-select
                  outlined
                  v-model="dataset"
                  :options="['数据集1', '数据集2', '数据集3']"
                  label="训练数据集"
                  class="full-width"
                />
              </div>
              <div class="col-12 col-md-6">
                <q-select
                  outlined
                  v-model="architecture"
                  :options="['CRNN', 'Transformer', 'YOLO']"
                  label="模型架构"
                  class="full-width"
                />
              </div>
              <div class="col-12 col-md-6">
                <q-input
                  outlined
                  v-model="epochs"
                  type="number"
                  label="训练轮数"
                  class="full-width"
                />
              </div>
              <div class="col-12 col-md-6">
                <q-input
                  outlined
                  v-model="batchSize"
                  type="number"
                  label="批次大小"
                  class="full-width"
                />
              </div>
            </div>
            <q-btn
              color="primary"
              icon="play_arrow"
              label="开始训练"
              class="q-mt-lg"
              :disable="!dataset || !architecture || !epochs || !batchSize"
            />
          </q-card-section>
        </q-card>

        <!-- 训练进度 -->
        <q-card class="progress-card q-mt-md">
          <q-card-section>
            <div class="text-h6">训练进度</div>
            <div class="q-mt-md">
              <div class="row items-center q-mb-sm">
                <div class="col">总进度</div>
                <div class="col-auto">50%</div>
              </div>
              <q-linear-progress
                rounded
                size="10px"
                :value="0.5"
                color="primary"
                class="q-mb-md"
              />
              <q-list separator>
                <q-item>
                  <q-item-section>
                    <q-item-label>当前轮数</q-item-label>
                    <q-item-label caption>25/50</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label>训练损失</q-item-label>
                    <q-item-label caption>0.0234</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label>验证准确率</q-item-label>
                    <q-item-label caption>98.5%</q-item-label>
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
import { ref } from 'vue'

// 训练配置
const dataset = ref(null)
const architecture = ref(null)
const epochs = ref(50)
const batchSize = ref(32)
</script>

<style lang="scss" scoped>
.model-page {
  background: var(--dark-page);
}

.model-card,
.training-card,
.progress-card {
  background: var(--dark-card);
}
</style>