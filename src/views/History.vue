<template>
  <q-page class="history-page q-pa-md">
    <div class="row q-col-gutter-md">
      <!-- 搜索过滤器 -->
      <div class="col-12">
        <q-card class="filter-card">
          <q-card-section>
            <div class="row q-col-gutter-md items-center">
              <div class="col-12 col-md-3">
                <q-input
                  v-model="searchText"
                  dense
                  outlined
                  label="搜索文字"
                  class="full-width"
                />
              </div>
              <div class="col-12 col-md-3">
                <q-select
                  v-model="resultType"
                  :options="['全部', '合格', '不合格']"
                  dense
                  outlined
                  label="检测结果"
                  class="full-width"
                />
              </div>
              <div class="col-12 col-md-4">
                <q-input
                  v-model="dateRange"
                  dense
                  outlined
                  label="时间范围"
                  class="full-width"
                >
                  <template v-slot:append>
                    <q-icon name="event" class="cursor-pointer">
                      <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                        <q-date v-model="dateRange" range />
                      </q-popup-proxy>
                    </q-icon>
                  </template>
                </q-input>
              </div>
              <div class="col-12 col-md-2">
                <q-btn color="primary" icon="search" label="搜索" class="full-width" />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- 历史记录表格 -->
      <div class="col-12">
        <q-card class="table-card">
          <q-card-section>
            <q-table
              :rows="records"
              :columns="columns"
              row-key="id"
              :pagination="{ rowsPerPage: 10 }"
              class="history-table"
            >
              <template v-slot:body-cell-result="props">
                <q-td :props="props">
                  <q-chip
                    :color="props.value === '合格' ? 'positive' : 'negative'"
                    text-color="white"
                    dense
                  >
                    {{ props.value }}
                  </q-chip>
                </q-td>
              </template>
              <template v-slot:body-cell-actions="props">
                <q-td :props="props">
                  <q-btn flat round dense icon="visibility" color="info" />
                  <q-btn flat round dense icon="file_download" color="primary" />
                </q-td>
              </template>
            </q-table>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'

// 搜索过滤器
const searchText = ref('')
const resultType = ref('全部')
const dateRange = ref({ from: '2024/03/01', to: '2024/03/14' })

// 表格配置
const columns = [
  { name: 'timestamp', align: 'left', label: '检测时间', field: 'timestamp' },
  { name: 'text', align: 'left', label: '识别文字', field: 'text' },
  { name: 'confidence', align: 'center', label: '置信度', field: 'confidence' },
  { name: 'result', align: 'center', label: '检测结果', field: 'result' },
  { name: 'actions', align: 'center', label: '操作', field: 'actions' }
]

// 模拟数据
const records = [
  {
    id: 1,
    timestamp: '2024-03-14 10:06:54',
    text: 'ABC123',
    confidence: '98.5%',
    result: '合格'
  },
  {
    id: 2,
    timestamp: '2024-03-14 10:05:32',
    text: 'DEF456',
    confidence: '95.2%',
    result: '合格'
  },
  {
    id: 3,
    timestamp: '2024-03-14 10:04:18',
    text: 'XYZ789',
    confidence: '82.1%',
    result: '不合格'
  }
]
</script>

<style lang="scss" scoped>
.history-page {
  background: var(--dark-page);
}

.filter-card,
.table-card {
  background: var(--dark-card);
}

.history-table {
  background: transparent;

  :deep(.q-table__card) {
    background: var(--dark-card);
  }

  :deep(.q-table__container) {
    background: transparent;
  }

  :deep(th) {
    font-weight: 500;
    color: var(--q-primary);
  }
}
</style>