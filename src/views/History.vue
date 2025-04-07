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
                  v-model="filters.searchText"
                  dense
                  outlined
                  label="搜索文字"
                  class="full-width"
                  @keyup.enter="searchRecords"
                />
              </div>
              <div class="col-12 col-md-3">
                <q-select
                  v-model="filters.status"
                  :options="['全部', '合格', '不合格']"
                  dense
                  outlined
                  label="检测结果"
                  class="full-width"
                  @update:model-value="searchRecords"
                />
              </div>
              <div class="col-12 col-md-4">
                <q-input
                  :model-value="formatDateRangeDisplay(filters.dateRange)"
                  dense
                  outlined
                  label="时间范围"
                  class="full-width"
                  readonly
                >
                  <template v-slot:append>
                    <q-icon name="event" class="cursor-pointer">
                      <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                        <q-date v-model="filters.dateRange" range @update:model-value="updateDateRange" />
                      </q-popup-proxy>
                    </q-icon>
                  </template>
                </q-input>
              </div>
              <div class="col-12 col-md-2">
                <q-btn color="primary" icon="search" label="搜索" class="full-width" @click="searchRecords" />
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
              :pagination="pagination"
              :loading="loading"
              @request="onRequest"
              class="history-table"
              binary-state-sort
            >
              <template v-slot:body-cell-status="props">
                <q-td :props="props">
                  <q-chip
                    :color="props.value === 'pass' ? 'positive' : (props.value === 'fail' ? 'negative' : 'grey')"
                    text-color="white"
                    dense
                  >
                    {{ statusText(props.value) }}
                  </q-chip>
                </q-td>
              </template>
              
              <template v-slot:body-cell-confidence="props">
                <q-td :props="props">
                  {{ props.value !== null ? `${props.value.toFixed(1)}%` : 'N/A' }}
                </q-td>
              </template>
              
              <template v-slot:body-cell-actions="props">
                <q-td :props="props">
                  <q-btn flat round dense icon="visibility" color="info" @click="viewRecord(props.row)" />
                  <q-btn flat round dense icon="delete" color="negative" @click="confirmDelete(props.row)" />
                </q-td>
              </template>
              
              <template v-slot:no-data>
                <div class="full-width row flex-center q-pa-md">
                  <q-icon name="info" size="2em" color="grey-7" />
                  <span class="text-grey-7 q-ml-sm">无历史记录数据</span>
                </div>
              </template>
            </q-table>
          </q-card-section>
        </q-card>
      </div>
    </div>
    
    <!-- 详情对话框 -->
    <q-dialog v-model="detailDialog" persistent>
      <q-card style="width: 700px; max-width: 90vw">
        <q-card-section class="row items-center">
          <div class="text-h6">检测记录详情</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        
        <q-card-section v-if="selectedRecord">
          <div class="row q-col-gutter-md">
            <!-- 检测图像 -->
            <div class="col-12 col-md-6">
              <div class="text-subtitle2 q-mb-sm">原始图像</div>
              <div class="image-container">
                <img :src="selectedRecord.imagePath" alt="检测图像" class="detection-image" v-if="selectedRecord.imagePath" />
                <div class="no-image-placeholder" v-else>无图像</div>
              </div>
            </div>
            
            <!-- 处理后图像 (如果有) -->
            <div class="col-12 col-md-6" v-if="selectedRecord.processedImagePath">
              <div class="text-subtitle2 q-mb-sm">处理后图像</div>
              <div class="image-container">
                <img :src="selectedRecord.processedImagePath" alt="处理后图像" class="detection-image" />
              </div>
            </div>
            
            <!-- 详细信息 -->
            <div class="col-12">
              <q-list separator>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>检测时间</q-item-label>
                    <q-item-label>{{ formatDateTime(selectedRecord.timestamp) }}</q-item-label>
                  </q-item-section>
                </q-item>
                
                <q-item>
                  <q-item-section>
                    <q-item-label caption>检测结果</q-item-label>
                    <q-item-label>
                      <q-chip
                        :color="selectedRecord.status === 'pass' ? 'positive' : 'negative'"
                        text-color="white"
                        dense
                      >
                        {{ statusText(selectedRecord.status) }}
                      </q-chip>
                    </q-item-label>
                  </q-item-section>
                </q-item>
                
                <q-item>
                  <q-item-section>
                    <q-item-label caption>识别文字</q-item-label>
                    <q-item-label>{{ selectedRecord.text || '无法识别' }}</q-item-label>
                  </q-item-section>
                </q-item>
                
                <q-item>
                  <q-item-section>
                    <q-item-label caption>置信度</q-item-label>
                    <q-item-label>{{ selectedRecord.confidence ? `${selectedRecord.confidence.toFixed(1)}%` : 'N/A' }}</q-item-label>
                  </q-item-section>
                </q-item>
                
                <q-item v-if="selectedRecord.deviceName">
                  <q-item-section>
                    <q-item-label caption>使用设备</q-item-label>
                    <q-item-label>{{ selectedRecord.deviceName }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </div>
        </q-card-section>
        
        <q-card-actions align="right">
          <q-btn flat label="关闭" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
    
    <!-- 删除确认对话框 -->
    <q-dialog v-model="deleteDialog" persistent>
      <q-card>
        <q-card-section class="row items-center">
          <q-avatar icon="warning" color="negative" text-color="white" />
          <span class="q-ml-sm">确定要删除此检测记录吗?</span>
        </q-card-section>
        
        <q-card-actions align="right">
          <q-btn flat label="取消" color="primary" v-close-popup />
          <q-btn flat label="删除" color="negative" @click="deleteRecord" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useQuasar } from 'quasar'
import { detectionService, Detection } from '@/services/detection'
import { formatDate } from '@/utils/date'

const $q = useQuasar()

// 状态
const loading = ref(false)
const records = ref<Detection[]>([])
const total = ref(0)
const detailDialog = ref(false)
const deleteDialog = ref(false)
const selectedRecord = ref<Detection | null>(null)
const recordToDelete = ref<Detection | null>(null)

// 日期范围接口定义
interface DateRange {
  from: string;
  to: string;
}

// 表格配置
const columns = [
  { 
    name: 'timestamp', 
    align: 'left' as const, 
    label: '检测时间', 
    field: 'timestamp', 
    format: formatDateTime 
  },
  { name: 'text', align: 'left' as const, label: '识别文字', field: 'text' },
  { name: 'confidence', align: 'center' as const, label: '置信度', field: 'confidence' },
  { name: 'status', align: 'center' as const, label: '检测结果', field: 'status' },
  { name: 'deviceName', align: 'left' as const, label: '使用设备', field: 'deviceName' },
  { name: 'actions', align: 'center' as const, label: '操作', field: 'actions' }
]

// 分页配置
const pagination = reactive({
  page: 1,
  rowsPerPage: 10,
  sortBy: 'timestamp',
  descending: true
})

// 监听分页变化
watch(() => pagination.page, (newPage) => {
  loadRecords()
})

// 过滤器
const filters = reactive({
  searchText: '',
  status: '全部',
  dateRange: { from: getTodayMinus(30), to: formatDate(new Date()) } as any,
  dateFrom: '',
  dateTo: ''
})

// 辅助函数
function getTodayMinus(days: number): string {
  const date = new Date()
  date.setDate(date.getDate() - days)
  return formatDate(date)
}

function formatDateTime(dateStr: string): string {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

function statusText(status: string): string {
  switch (status) {
    case 'pass': return '合格'
    case 'fail': return '不合格'
    case 'unknown': return '未知'
    default: return status
  }
}

// 加载数据
async function loadRecords() {
  loading.value = true
  
  try {
    const response = await detectionService.getDetections({
      page: pagination.page,
      perPage: pagination.rowsPerPage,
      searchText: filters.searchText || undefined,
      status: filters.status !== '全部' ? filters.status : undefined,
      dateFrom: filters.dateFrom || undefined,
      dateTo: filters.dateTo || undefined
    })
    
    records.value = response.items
    total.value = response.total
  } catch (error) {
    console.error('加载历史记录失败:', error)
    $q.notify({
      type: 'negative',
      message: '加载历史记录失败',
      position: 'top'
    })
  } finally {
    loading.value = false
  }
}

// 分页请求处理
function onRequest(props: any) {
  const { page, rowsPerPage } = props.pagination
  pagination.page = page
  pagination.rowsPerPage = rowsPerPage
  loadRecords()
}

// 搜索记录
function searchRecords() {
  pagination.page = 1 // 重置到第一页
  loadRecords()
}

// 更新日期范围
function updateDateRange() {
  if (filters.dateRange.from && filters.dateRange.to) {
    // 确保日期格式正确 - Quasar的q-date返回的格式是YYYY/MM/DD，需要转换为YYYY-MM-DD
    filters.dateFrom = filters.dateRange.from.replace(/\//g, '-');
    filters.dateTo = filters.dateRange.to.replace(/\//g, '-');
    console.log('日期范围:', filters.dateFrom, '至', filters.dateTo);
    searchRecords();
  }
}

// 查看记录详情
function viewRecord(record: Detection) {
  selectedRecord.value = record
  detailDialog.value = true
}

// 确认删除
function confirmDelete(record: Detection) {
  recordToDelete.value = record
  deleteDialog.value = true
}

// 删除记录
async function deleteRecord() {
  if (!recordToDelete.value) return
  
  try {
    await detectionService.deleteDetection(recordToDelete.value.id)
    
    $q.notify({
      type: 'positive',
      message: '记录已删除',
      position: 'top'
    })
    
    // 重新加载数据
    loadRecords()
  } catch (error) {
    console.error('删除记录失败:', error)
    $q.notify({
      type: 'negative',
      message: '删除记录失败',
      position: 'top'
    })
  }
}

// 组件挂载时加载数据
onMounted(() => {
  // 设置初始日期范围
  filters.dateFrom = filters.dateRange.from.replace(/\//g, '-');
  filters.dateTo = filters.dateRange.to.replace(/\//g, '-');
  
  // 加载记录
  loadRecords()
})

// 格式化日期范围字符串显示
function formatDateRangeDisplay(dateRange: any): string {
  if (!dateRange || !dateRange.from || !dateRange.to) {
    return '';
  }
  
  // 统一替换日期分隔符为横线
  const from = dateRange.from.replace(/\//g, '-');
  const to = dateRange.to.replace(/\//g, '-');
  
  // 将日期格式化为更友好的中文格式
  try {
    const fromDate = new Date(from);
    const toDate = new Date(to);
    
    const fromStr = fromDate.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
    
    const toStr = toDate.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
    
    return `${fromStr} 至 ${toStr}`;
  } catch (e) {
    // 如果日期解析失败，直接使用原始字符串
    return `${from} 至 ${to}`;
  }
}
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

.image-container {
  width: 100%;
  height: 200px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #111;
  border-radius: 4px;
  overflow: hidden;
}

.detection-image {
  max-width: 100%;
  max-height: 200px;
  object-fit: contain;
}

.no-image-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  color: #666;
  font-style: italic;
}
</style>