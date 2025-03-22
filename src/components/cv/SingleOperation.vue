<template>
    <q-page class="cv-operations-page q-pa-md">
      <!-- 顶部工具栏 -->
      <div class="toolbar q-mb-md">
        <div class="row items-center q-col-gutter-md">
          <!-- 左侧按钮组 -->
          <div class="col-auto">
            <div class="row items-center q-gutter-sm">
              <q-btn
                color="primary"
                icon="add"
                label="新建操作"
                dense
                @click="createNewOperation"
              />
              <q-btn-group flat>
                <q-btn
                  flat
                  dense
                  icon="upload_file"
                  label="导入"
                  @click="importOperations"
                >
                  <q-tooltip>导入操作配置</q-tooltip>
                  <input
                    type="file"
                    accept=".xlsx"
                    class="hidden-input"
                    ref="fileInput"
                    @change="handleFileImport"
                  />
                </q-btn>
                <q-btn
                  flat
                  dense
                  icon="download"
                  label="导出"
                  @click="exportOperations"
                >
                  <q-tooltip>导出操作配置</q-tooltip>
                </q-btn>
              </q-btn-group>
              <q-chip
                dense
                color="grey-7"
                text-color="white"
                icon="science"
                size="sm"
              >
                {{ operations.length }} 个操作
              </q-chip>
            </div>
          </div>
  
          <!-- 右侧搜索框和刷新按钮 -->
          <div class="col">
            <div class="row items-center justify-end">
              <q-input
                v-model="searchText"
                placeholder="搜索操作名称或描述"
                dense
                outlined
                class="search-input"
                style="width: 250px"
              >
                <template v-slot:prepend>
                  <q-icon name="search" />
                </template>
                <template v-slot:append>
                  <q-icon
                    v-if="searchText"
                    name="close"
                    class="cursor-pointer"
                    @click="searchText = ''"
                  />
                </template>
              </q-input>
              <q-btn
                flat
                dense
                icon="refresh"
                class="q-ml-sm"
                @click="loadOperations"
                :loading="loading"
              >
                <q-tooltip>刷新列表</q-tooltip>
              </q-btn>
            </div>
          </div>
        </div>
      </div>
  
      <!-- 操作列表 -->
      <q-card flat bordered class="operations-card">
        <q-table
          :rows="filteredOperations"
          :columns="columns"
          row-key="id"
          :loading="loading"
          class="operations-table"
          :pagination="{ rowsPerPage: 10 }"
        >
          <!-- 自定义列 -->
          <template v-slot:body-cell-description="props">
            <q-td :props="props">
              <div class="description-cell">
                {{ props.value || '-' }}
              </div>
            </q-td>
          </template>
  
          <template v-slot:body-cell-created_at="props">
            <q-td :props="props">
              <q-chip
                dense
                size="sm"
                class="time-chip"
              >
                {{ formatDate(props.value) }}
              </q-chip>
            </q-td>
          </template>
  
          <template v-slot:body-cell-actions="props">
            <q-td :props="props" class="action-cell">
              <q-btn-group flat>
                <q-btn
                  flat
                  dense
                  icon="edit"
                  @click="editOperation(props.row)"
                >
                  <q-tooltip>编辑</q-tooltip>
                </q-btn>
                <q-btn
                  flat
                  dense
                  icon="delete"
                  color="negative"
                  @click="confirmDelete(props.row)"
                >
                  <q-tooltip>删除</q-tooltip>
                </q-btn>
              </q-btn-group>
            </q-td>
          </template>
        </q-table>
      </q-card>
  
      <!-- 编辑对话框 -->
      <q-dialog
        v-model="showCreateDialog"
        maximized
        persistent
        transition-show="slide-up"
        transition-hide="slide-down"
      >
        <q-card class="editor-dialog">
          <q-card-section class="editor-header row items-center q-py-sm">
            <div class="row items-center">
              <q-icon name="code" size="24px" color="info" class="q-mr-sm" />
              <div class="text-h6">编辑代码</div>
            </div>
            <q-space />
            <q-btn icon="close" flat round dense v-close-popup />
          </q-card-section>
  
          <q-card-section class="editor-section">
            <q-form @submit="handleSubmit" class="editor-form">
              <div class="row q-col-gutter-md">
                <!-- 左侧表单 -->
                <div class="col-12 col-md-4 form-section">
                  <!-- 基本信息卡片 -->
                  <q-card flat bordered class="q-mb-md">
                    <q-card-section>
                      <div class="text-subtitle2 q-mb-md">基本信息</div>
                      <q-input
                        v-model="editingOperation.name"
                        label="操作名称"
                        :rules="[val => !!val || '请输入操作名称']"
                        class="q-mb-md"
                        outlined
                        dense
                      >
                        <template v-slot:prepend>
                          <q-icon name="label" />
                        </template>
                      </q-input>
                      
                      <q-input
                        v-model="editingOperation.description"
                        label="描述"
                        type="textarea"
                        class="q-mb-md"
                        outlined
                        dense
                        autogrow
                      >
                        <template v-slot:prepend>
                          <q-icon name="description" />
                        </template>
                      </q-input>
  
                      <div class="row justify-end q-gutter-sm">
                        <q-btn
                          label="关闭"
                          color="grey-7"
                          flat
                          @click="closeDialog"
                        />
                        <q-btn
                          :label="editingOperation.id ? '保存' : '创建'"
                          type="submit"
                          color="primary"
                          :loading="saving"
                        />
                      </div>
                    </q-card-section>
                  </q-card>
  
                  <!-- 参数配置卡片 -->
                  <q-card flat bordered class="q-mb-md">
                    <q-card-section>
                      <div class="text-subtitle2">输入参数配置</div>
                      <div class="q-mt-sm">
                        <q-list bordered separator>
                          <q-item v-for="(param, index) in editingOperation.inputParams || []" :key="index">
                            <q-item-section>
                              <q-input 
                                v-model="param.name" 
                                dense 
                                label="参数名称"
                                :rules="[val => !!val || '请输入参数名称']"
                              >
                                <template v-slot:prepend>
                                  <q-icon :name="getParamTypeIcon(param.type)" />
                                </template>
                              </q-input>
                            </q-item-section>
                            <q-item-section>
                              <q-select
                                v-model="param.type"
                                :options="paramTypeOptions"
                                dense
                                label="参数类型"
                                :rules="[val => !!val || '请选择参数类型']"
                              >
                                <template v-slot:prepend>
                                  <q-icon :name="getParamTypeIcon(param.type)" />
                                </template>
                                <template v-slot:option="scope">
                                  <q-item v-bind="scope.itemProps">
                                    <q-item-section avatar>
                                      <q-icon :name="scope.opt.icon" />
                                    </q-item-section>
                                    <q-item-section>
                                      <q-item-label>{{ scope.opt.label }}</q-item-label>
                                    </q-item-section>
                                  </q-item>
                                </template>
                              </q-select>
                            </q-item-section>
                            <q-item-section>
                              <q-input 
                                v-model="param.description" 
                                dense 
                                label="描述"
                              />
                            </q-item-section>
                            <q-item-section>
                              <q-input 
                                v-model="param.default" 
                                dense 
                                label="默认值"
                              />
                            </q-item-section>
                            <q-item-section side>
                              <q-checkbox v-model="param.required" label="必需" />
                            </q-item-section>
                            <q-item-section side>
                              <q-btn
                                flat
                                round
                                dense
                                color="negative"
                                icon="delete"
                                @click="removeInputParam(index)"
                              />
                            </q-item-section>
                          </q-item>
                        </q-list>
                        <q-btn
                          flat
                          class="q-mt-sm"
                          icon="add"
                          label="添加输入参数"
                          @click="addInputParam"
                        />
                      </div>
                    </q-card-section>
                  </q-card>
  
                  <q-card flat bordered class="q-mb-md">
                    <q-card-section>
                      <div class="text-subtitle2">输出参数配置</div>
                      <div class="q-mt-sm">
                        <q-list bordered separator>
                          <q-item v-for="(param, index) in editingOperation.outputParams || []" :key="index">
                            <q-item-section>
                              <q-input 
                                v-model="param.name" 
                                dense 
                                label="参数名称"
                                :rules="[val => !!val || '请输入参数名称']"
                              >
                                <template v-slot:prepend>
                                  <q-icon :name="getParamTypeIcon(param.type)" />
                                </template>
                              </q-input>
                            </q-item-section>
                            <q-item-section>
                              <q-select
                                v-model="param.type"
                                :options="paramTypeOptions"
                                dense
                                label="参数类型"
                                :rules="[val => !!val || '请选择参数类型']"
                              >
                                <template v-slot:prepend>
                                  <q-icon :name="getParamTypeIcon(param.type)" />
                                </template>
                                <template v-slot:option="scope">
                                  <q-item v-bind="scope.itemProps">
                                    <q-item-section avatar>
                                      <q-icon :name="scope.opt.icon" />
                                    </q-item-section>
                                    <q-item-section>
                                      <q-item-label>{{ scope.opt.label }}</q-item-label>
                                    </q-item-section>
                                  </q-item>
                                </template>
                              </q-select>
                            </q-item-section>
                            <q-item-section>
                              <q-input 
                                v-model="param.description" 
                                dense 
                                label="描述"
                              />
                            </q-item-section>
                            <q-item-section side>
                              <q-checkbox v-model="param.required" label="必需" />
                            </q-item-section>
                            <q-item-section side>
                              <q-btn
                                flat
                                round
                                dense
                                color="negative"
                                icon="delete"
                                @click="removeOutputParam(index)"
                              />
                            </q-item-section>
                          </q-item>
                        </q-list>
                        <q-btn
                          flat
                          class="q-mt-sm"
                          icon="add"
                          label="添加输出参数"
                          @click="addOutputParam"
                        />
                      </div>
                    </q-card-section>
                  </q-card>
                </div>
  
                <!-- 右侧代码编辑器 -->
                <div class="col-12 col-md-8">
                  <q-card flat bordered class="code-editor-card">
                    <q-card-section class="code-editor-header">
                      <div class="text-subtitle2">Python 代码</div>
                      <q-space />
                      <q-btn-group flat>
                        <q-btn
                          flat
                          dense
                          icon="content_copy"
                          label="复制"
                          @click="copyCode"
                        />
                        <q-btn
                          flat
                          dense
                          icon="restart_alt"
                          label="重置"
                          @click="resetCode"
                        />
                      </q-btn-group>
                    </q-card-section>
                    <q-separator />
                    <div id="monaco-editor" class="editor-container"></div>
                  </q-card>
                </div>
              </div>
            </q-form>
          </q-card-section>
        </q-card>
      </q-dialog>
  
      <!-- 删除确认对话框 -->
      <q-dialog v-model="showDeleteDialog" persistent>
        <q-card>
          <q-card-section class="row items-center">
            <q-avatar icon="delete" color="negative" text-color="white" />
            <span class="q-ml-sm">确定要删除此操作吗？</span>
          </q-card-section>
  
          <q-card-actions align="right">
            <q-btn flat label="取消" color="primary" v-close-popup />
            <q-btn flat label="删除" color="negative" @click="deleteOperation" />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </q-page>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
  import { useQuasar } from 'quasar'
  import { cvOperationService } from '@/services/cv_operation'
  import { CVOperation, CreateCVOperationRequest, UpdateCVOperationRequest, ParamConfig, ParamType } from '@/services/cv_operation'
  import * as monaco from 'monaco-editor'
  import loader from '@monaco-editor/loader'
  import * as XLSX from 'xlsx'
  
  const $q = useQuasar()
  
  // 状态变量
  const operations = ref<CVOperation[]>([])
  const loading = ref(false)
  const showCreateDialog = ref(false)
  const showDeleteDialog = ref(false)
  const saving = ref(false)
  const searchText = ref('')
  const editor = ref<any>(null)
  const editingOperation = ref<Partial<CVOperation>>({
    name: '',
    description: '',
    code: '',
    inputParams: [],
    outputParams: []
  })
  const operationToDelete = ref<CVOperation | null>(null)
  
  // 参数类型配置
  const paramTypeOptions = [
    { label: '图像', value: ParamType.IMAGE, icon: 'image' },
    { label: '数值', value: ParamType.NUMBER, icon: 'numbers' },
    { label: '文本', value: ParamType.TEXT, icon: 'text_fields' },
    { label: '布尔值', value: ParamType.BOOLEAN, icon: 'toggle_on' },
    { label: '数组', value: ParamType.ARRAY, icon: 'view_list' },
    { label: '对象', value: ParamType.OBJECT, icon: 'data_object' }
  ]
  
  // 获取参数类型图标
  const getParamTypeIcon = (type: ParamType) => {
    return paramTypeOptions.find(opt => opt.value === type)?.icon || 'help_outline'
  }
  
  // 参数操作方法
  const addInputParam = () => {
    if (!editingOperation.value.inputParams) {
      editingOperation.value.inputParams = []
    }
    editingOperation.value.inputParams.push({
      name: '',
      type: ParamType.IMAGE,
      description: '',
      default: null,
      required: true
    })
  }
  
  const removeInputParam = (index: number) => {
    editingOperation.value.inputParams?.splice(index, 1)
  }
  
  const addOutputParam = () => {
    if (!editingOperation.value.outputParams) {
      editingOperation.value.outputParams = []
    }
    editingOperation.value.outputParams.push({
      name: '',
      type: ParamType.IMAGE,
      description: '',
      required: true
    })
  }
  
  const removeOutputParam = (index: number) => {
    editingOperation.value.outputParams?.splice(index, 1)
  }
  
  // 表格列配置
  const columns = [
    {
      name: 'name',
      required: true,
      label: '操作名称',
      align: 'left',
      field: 'name',
      sortable: true
    },
    {
      name: 'description',
      label: '描述',
      align: 'left',
      field: 'description'
    },
    {
      name: 'created_at',
      label: '创建时间',
      align: 'left',
      field: 'createdAt',
      sortable: true
    },
    {
      name: 'actions',
      label: '操作',
      align: 'center'
    }
  ]
  
  // 计算属性
  const filteredOperations = computed(() => {
    if (!searchText.value) return operations.value
    const searchLower = searchText.value.toLowerCase()
    return operations.value.filter(op => 
      op.name.toLowerCase().includes(searchLower) ||
      (op.description?.toLowerCase().includes(searchLower))
    )
  })
  
  // 方法
  const loadOperations = async () => {
    loading.value = true
    try {
      operations.value = await cvOperationService.getOperations()
    } catch (error) {
      console.error('加载操作失败:', error)
      $q.notify({
        type: 'negative',
        message: '加载操作失败'
      })
    } finally {
      loading.value = false
    }
  }
  
  const createNewOperation = () => {
    editingOperation.value = {
      name: '',
      description: '',
      code: '',
      inputParams: [],
      outputParams: []
    }
    showCreateDialog.value = true
  }
  
  const editOperation = (operation: CVOperation) => {
    editingOperation.value = { ...operation }
    showCreateDialog.value = true
  }
  
  const confirmDelete = (operation: CVOperation) => {
    operationToDelete.value = operation
    showDeleteDialog.value = true
  }
  
  const deleteOperation = async () => {
    if (!operationToDelete.value) return
    
    try {
      await cvOperationService.deleteOperation(operationToDelete.value.id)
      await loadOperations()
      showDeleteDialog.value = false
      $q.notify({
        type: 'positive',
        message: '删除成功'
      })
    } catch (error) {
      console.error('删除失败:', error)
      $q.notify({
        type: 'negative',
        message: '删除失败'
      })
    }
  }
  
  const handleSubmit = async () => {
    saving.value = true
    try {
      const operationData = {
        name: editingOperation.value.name,
        description: editingOperation.value.description,
        code: editor.value?.getValue(),
        inputParams: editingOperation.value.inputParams,
        outputParams: editingOperation.value.outputParams
      }

      if (editingOperation.value.id) {
        await cvOperationService.updateOperation(editingOperation.value.id, operationData)
      } else {
        await cvOperationService.createOperation(operationData as CreateCVOperationRequest)
      }

      await loadOperations()
      showCreateDialog.value = false
      $q.notify({
        type: 'positive',
        message: '保存成功'
      })
    } catch (error) {
      console.error('保存失败:', error)
      $q.notify({
        type: 'negative',
        message: '保存失败'
      })
    } finally {
      saving.value = false
    }
  }
  
  const closeDialog = () => {
    showCreateDialog.value = false
  }
  
  const copyCode = () => {
    const code = editor.value?.getValue()
    if (code) {
      navigator.clipboard.writeText(code)
      $q.notify({
        type: 'positive',
        message: '代码已复制到剪贴板'
      })
    }
  }
  
  const resetCode = () => {
    if (editor.value) {
      editor.value.setValue(editingOperation.value.code || '')
    }
  }
  
  const formatDate = (date: string) => {
    return new Date(date).toLocaleString()
  }
  
  // 生命周期钩子
  onMounted(async () => {
    await loadOperations()
    
    // 初始化代码编辑器
    loader.init().then(monaco => {
      editor.value = monaco.editor.create(document.getElementById('monaco-editor')!, {
        value: editingOperation.value.code || '',
        language: 'python',
        theme: 'vs-dark',
        automaticLayout: true,
        minimap: {
          enabled: false
        }
      })
    })
  })
  
  onBeforeUnmount(() => {
    if (editor.value) {
      editor.value.dispose()
    }
  })
  
  // 监听编辑操作变化
  watch(() => editingOperation.value.code, (newCode) => {
    if (editor.value && newCode !== editor.value.getValue()) {
      editor.value.setValue(newCode || '')
    }
  })
  
  // 导入导出功能
  const fileInput = ref<HTMLInputElement | null>(null)
  
  const importOperations = () => {
    fileInput.value?.click()
  }
  
  const handleFileImport = async (event: Event) => {
    const input = event.target as HTMLInputElement
    if (!input.files?.length) return
  
    try {
      const file = input.files[0]
      const wb = await readExcelFile(file)
      const ws = wb.Sheets[wb.SheetNames[0]]
      const data = XLSX.utils.sheet_to_json(ws)
  
      for (const row of data) {
        const operation = {
          name: row['操作名称'],
          description: row['描述'],
          code: row['代码'],
          inputParams: JSON.parse(row['输入参数'] || '[]'),
          outputParams: JSON.parse(row['输出参数'] || '[]')
        }
        
        try {
          await cvOperationService.createOperation(operation as CreateCVOperationRequest)
        } catch (error) {
          console.error('导入操作失败:', error)
        }
      }
  
      await loadOperations()
      $q.notify({
        type: 'positive',
        message: '导入成功'
      })
    } catch (error) {
      $q.notify({
        type: 'negative',
        message: '导入失败'
      })
    }
    
    input.value = ''
  }
  
  const exportOperations = async () => {
    try {
      const data = operations.value.map(op => ({
        '操作名称': op.name,
        '描述': op.description,
        '代码': op.code,
        '输入参数': JSON.stringify(op.inputParams),
        '输出参数': JSON.stringify(op.outputParams)
      }))
  
      const ws = XLSX.utils.json_to_sheet(data)
      const wb = XLSX.utils.book_new()
      XLSX.utils.book_append_sheet(wb, ws, 'Operations')
      XLSX.writeFile(wb, 'cv_operations.xlsx')
  
      $q.notify({
        type: 'positive',
        message: '导出成功'
      })
    } catch (error) {
      console.error('导出失败:', error)
      $q.notify({
        type: 'negative',
        message: '导出失败'
      })
    }
  }
  </script>
  
  <style lang="scss" scoped>
  // 工业化主题变量
  :root {
    --dark-page: #121212;
    --dark-card: #1e1e1e;
    --dark-card-header: #252525;
    --border-color: #2c2c2c;
    --primary: #1976d2;
    --info: #0288d1;
    --warning: #ffa000;
    --negative: #d32f2f;
  }
  
  .cv-operations-page {
    background: var(--dark-page);
    min-height: 100vh;
  }
  
  .toolbar {
    background: var(--dark-card);
    padding: 8px 12px;
    border-radius: 4px;
    border: 1px solid var(--border-color);
  }
  
  .operations-card {
    background: var(--dark-card);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    
    .operations-table {
      :deep(.q-table__card) {
        background: var(--dark-card);
      }
  
      :deep(.q-table__container) {
        background: var(--dark-card);
      }
  
      :deep(.q-table thead tr) {
        background: var(--dark-card-header);
      }
  
      :deep(.q-table tbody tr:hover) {
        background: #2a2a2a;
      }
    }
  }
  
  .description-cell {
    max-width: 300px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .time-chip {
    background: rgba(255, 255, 255, 0.05);
    font-family: monospace;
  }
  
  .action-cell {
    width: 150px;
  }
  
  .editor-dialog {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--dark-page);
  }
  
  .editor-header {
    background: var(--dark-card);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .editor-section {
    flex: 1;
    padding: 16px;
    overflow: hidden;
  }
  
  .editor-form {
    height: 100%;
  }
  
  .form-section {
    display: flex;
    flex-direction: column;
    gap: 16px;
    height: 100%;
    
    .q-card {
      border: 1px solid var(--border-color);
      border-radius: 4px;
  
      .q-card-section {
        background: var(--dark-card);
      }
  
      .text-subtitle2 {
        color: #fff;
        font-weight: 500;
      }
    }
  }
  
  .code-editor-card {
    height: 100%;
    display: flex;
    flex-direction: column;
    border: 1px solid var(--border-color);
    border-radius: 4px;
  
    .code-editor-header {
      padding: 12px 16px;
      display: flex;
      align-items: center;
      background: var(--dark-card-header);
    }
  }
  
  .editor-container {
    flex: 1;
    min-height: 400px;
  }
  
  .search-input {
    :deep(.q-field__control) {
      height: 36px;
      background: var(--dark-card-header);
    }
  
    :deep(.q-field__marginal) {
      height: 36px;
    }
  }
  
  // 调整按钮样式
  :deep(.q-btn) {
    &.q-btn--dense {
      padding: 4px 12px;
      min-height: 36px;
    }
  }
  
  .hidden-input {
    display: none;
  }
  
  // 调整按钮组样式
  :deep(.q-btn-group) {
    .q-btn {
      padding: 4px 12px;
      min-height: 36px;
      border-color: var(--border-color);
      
      .q-icon {
        font-size: 20px;
      }

      &:hover {
        background: var(--dark-card-header);
      }
    }
  }
  
  // 调整工具栏内间距
  .toolbar {
    .q-gutter-sm > * {
      margin-left: 8px;
      margin-right: 8px;
      
      &:first-child {
        margin-left: 0;
      }
      
      &:last-child {
        margin-right: 0;
      }
    }
  }
  
  // 参数类型图标样式
  :deep(.q-field__prepend) {
    .q-icon {
      font-size: 20px;
      color: var(--q-primary);
    }
  }
  
  // 参数类型选项样式
  :deep(.q-item__section--avatar) {
    .q-icon {
      font-size: 24px;
      color: var(--q-primary);
    }
  }
  </style> 