<template>
  <q-page class="settings-page q-pa-md">
    <div class="row q-col-gutter-md">
      <!-- 系统参数配置 -->
      <div class="col-12 col-lg-6">
        <q-card class="settings-card">
          <q-card-section>
            <div class="text-h6">系统参数</div>
            <q-list class="q-mt-md">
              <q-item>
                <q-item-section>
                  <q-item-label>自动保存间隔</q-item-label>
                  <q-slider v-model="systemSettings.auto_save_interval" :min="1" :max="60" :step="1" label
                    :label-value=" `${systemSettings.auto_save_interval}分钟`" class="q-mt-md" @change="saveSystemSettings" />
                </q-item-section>
              </q-item>
              <q-item>
                <q-item-section>
                  <q-item-label>数据保留时间</q-item-label>
                  <q-select v-model="systemSettings.data_retention" :options="['7天', '30天', '90天', '180天', '365天']"
                    outlined dense class="q-mt-sm" @update:model-value="saveSystemSettings" />
                </q-item-section>
              </q-item>
              <q-item>
                <q-item-section>
                  <q-item-label>告警阈值</q-item-label>
                  <q-input v-model.number="systemSettings.alarm_threshold" type="number" outlined dense suffix="%"
                    class="q-mt-sm" @change="saveSystemSettings" />
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>

        <!-- MES集成配置 -->
        <q-card class="settings-card q-mt-md">
          <q-card-section>
            <div class="text-h6">MES集成</div>
            <q-list class="q-mt-md">
              <q-item>
                <q-item-section>
                  <q-item-label>服务器地址</q-item-label>
                  <q-input v-model="mesSettings.server_url" outlined dense placeholder="http://mes.example.com"
                    class="q-mt-sm" />
                </q-item-section>
              </q-item>
              <q-item>
                <q-item-section>
                  <q-item-label>API密钥</q-item-label>
                  <q-input v-model="mesSettings.api_key" outlined dense type="password" class="q-mt-sm" />
                </q-item-section>
              </q-item>
              <q-item>
                <q-item-section>
                  <q-btn color="primary" icon="sync" label="测试连接" class="q-mt-md" @click="saveMesSettings" />
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>

      <!-- 设备管理 -->
      <div class="col-12 col-lg-6">
        <q-card class="settings-card">
          <q-card-section>
            <div class="row items-center justify-between">
            <div class="text-h6">设备管理</div>
              <div>
                <q-toggle v-model="disableAutoCheck" label="禁用自动检测" dense color="warning" />
                <q-btn flat round dense icon="refresh" color="primary" @click="refreshDeviceStatus">
                  <q-tooltip>刷新设备状态</q-tooltip>
                </q-btn>
                <q-btn color="primary" icon="add" label="添加设备" @click="showAddDeviceDialog = true" />
                      </div>
                    </div>

            <!-- 设备类型筛选 -->
            <div class="q-mt-md">
              <q-tabs v-model="activeDeviceTab" dense class="text-primary" active-color="primary"
                indicator-color="primary" align="justify">
                <q-tab name="all" label="全部" />
                <q-tab name="camera" label="相机" />
                <q-tab name="light" label="光源" />
                <q-tab name="plc" label="控制器" />
              </q-tabs>
                      </div>

            <q-separator />

            <!-- 设备列表 -->
            <q-list class="q-mt-sm">
              <q-item v-for="device in filteredDevices" :key="device.id">
                <q-item-section avatar>
                  <q-avatar :color="device.status === 'online' ? 'positive' : 'grey'" text-color="white">
                    <q-icon :name="getDeviceIcon(device.type)" />
                  </q-avatar>
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ device.name }}</q-item-label>
                  <q-item-label caption>
                    <span
                      :class="{ 'text-positive': device.status === 'online', 'text-negative': device.status === 'error', 'text-grey': device.status === 'offline' }">
                      {{ deviceStatusText(device.status) }}
                    </span>
                    <span v-if="device.model"> | {{ device.model }}</span>
                    <!-- 改进配置信息显示，优先使用存储的URL -->
                    <template v-if="device.type === 'camera'">
                      <span v-if="device.config.stream_url">
                        | URL: {{ device.config.stream_url }}
                      </span>
                      <span v-else-if="device.config.source && device.config.source.includes('device:')">
                        | URL: {{ getCameraStreamUrl(device) }}
                      </span>
                      <span v-else-if="device.config.ip">
                        | IP: {{ device.config.ip }}
                      </span>
                      <span v-if="device.config.resolution"> | {{ device.config.resolution }}</span>
                    </template>
                  </q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-btn-group flat>
                    <q-btn v-if="device.type === 'camera'" flat round dense icon="visibility" color="blue-5"
                      @click="previewCamera(device)">
                      <q-tooltip>预览摄像头</q-tooltip>
                    </q-btn>
                    <q-btn v-if="device.type === 'camera'" flat round dense
                      :icon="device.status === 'online' ? 'link_off' : 'link'"
                      :color="device.status === 'online' ? 'positive' : 'grey'" @click="toggleDeviceStatus(device)">
                      <q-tooltip>{{ device.status === 'online' ? '设为离线' : '设为在线' }}</q-tooltip>
                    </q-btn>
                    <q-btn flat round dense icon="edit" color="primary" @click="editDevice(device)">
                      <q-tooltip>编辑设备</q-tooltip>
                    </q-btn>
                    <q-btn flat round dense icon="delete" color="negative" @click="confirmDeleteDevice(device)">
                      <q-tooltip>删除设备</q-tooltip>
                    </q-btn>
                  </q-btn-group>
                </q-item-section>
              </q-item>

              <q-item v-if="filteredDevices.length === 0">
                <q-item-section>
                  <div class="text-center text-grey q-pa-md">
                    <q-icon name="devices" size="48px" class="q-mb-md" />
                    <div>暂无{{ activeDeviceTab === 'all' ? '' : getDeviceTypeLabel(activeDeviceTab) }}设备</div>
                    <q-btn color="primary" label="添加设备" icon="add" class="q-mt-md"
                      @click="addNewDevice(activeDeviceTab !== 'all' ? activeDeviceTab : 'camera')" />
                      </div>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- 添加/编辑设备对话框 -->
    <q-dialog v-model="showAddDeviceDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section class="row items-center">
          <div class="text-h6">{{ isEditMode ? '编辑设备' : '添加设备' }}</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup @click="resetDeviceForm" />
        </q-card-section>

        <q-separator />

        <q-card-section>
          <q-form @submit="saveDevice">
            <q-input v-model="deviceForm.name" label="设备名称" outlined :rules="[val => !!val || '请输入设备名称']"
              class="q-mb-md" />

            <q-select v-model="deviceForm.type"
              :options="deviceTypes.map(type => ({ label: getDeviceTypeLabel(type), value: type }))" outlined
              label="设备类型" emit-value map-options class="q-mb-md" />

            <q-input v-model="deviceForm.model" label="设备型号" outlined class="q-mb-md" />

            <!-- 设备特有配置 -->
            <div class="q-mb-md">
              <div class="text-subtitle2 q-mb-sm">设备配置</div>

              <!-- 相机设备配置 -->
              <div v-if="deviceForm.type === 'camera'">
                <q-item>
                  <q-item-section>
                    <q-item-label>摄像头类型</q-item-label>
                    <q-select v-model="deviceForm.cameraType" :options="[
                      { label: '本地摄像头', value: 'local' },
                      { label: 'IP摄像头', value: 'ip' },
                      { label: 'RTSP流', value: 'rtsp' },
                      { label: 'HTTP流', value: 'http' }
                    ]" outlined dense class="q-mt-sm" />
                  </q-item-section>
                </q-item>

                <q-item v-if="deviceForm.type === 'camera' && deviceForm.cameraType === 'local'">
                  <q-item-section>
                    <q-item-label>设备ID</q-item-label>
                    <q-input v-model="deviceForm.deviceId" type="number" outlined dense placeholder="0"
                      class="q-mt-sm" />
                  </q-item-section>
                </q-item>

                <q-item v-if="deviceForm.type === 'camera' && ['ip', 'rtsp', 'http'].includes(deviceForm.cameraType)">
                  <q-item-section>
                    <q-item-label>摄像头URL</q-item-label>
                    <q-input v-model="deviceForm.streamUrl" outlined dense
                      :placeholder="getPlaceholderForCameraType(deviceForm.cameraType)" class="q-mt-sm" />
                  </q-item-section>
                </q-item>
              </div>

              <!-- 光源设备配置 -->
              <div v-if="deviceForm.type === 'light'">
                <q-input v-model="deviceForm.config.port" label="串口" outlined dense class="q-mb-sm" />
                <q-select v-model="deviceForm.config.mode" :options="['连续', '闪烁', '触发']" label="工作模式" outlined dense />
              </div>

              <!-- PLC配置 -->
              <div v-if="deviceForm.type === 'plc'">
                <q-input v-model="deviceForm.config.ip" label="IP地址" outlined dense class="q-mb-sm" />
                <div class="row q-col-gutter-sm">
                  <div class="col-6">
                    <q-input v-model.number="deviceForm.config.rack" type="number" label="机架号" outlined dense />
                  </div>
                  <div class="col-6">
                    <q-input v-model.number="deviceForm.config.slot" type="number" label="插槽号" outlined dense />
                  </div>
                </div>
              </div>
            </div>

            <div class="row justify-end q-mt-md">
              <q-btn label="取消" flat color="negative" v-close-popup @click="resetDeviceForm" class="q-mr-sm" />
              <q-btn :label="isEditMode ? '保存' : '添加'" type="submit" color="primary" />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- 确认删除对话框 -->
    <q-dialog v-model="showConfirmDeleteDialog" persistent>
      <q-card>
        <q-card-section class="row items-center">
          <q-avatar icon="delete" color="negative" text-color="white" />
          <span class="q-ml-sm">确定要删除设备 "{{ deviceToDelete?.name }}" 吗？</span>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="取消" color="primary" v-close-popup />
          <q-btn flat label="删除" color="negative" @click="deleteDevice" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- 添加摄像头预览对话框 -->
    <q-dialog v-model="showCameraPreview" :maximized="false" persistent>
      <q-card style="width: 800px; max-width: 95vw;">
        <q-card-section class="row items-center">
          <div class="text-h6">{{ selectedCamera?.name || '摄像头' }} 预览</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-card-section>
          <camera-preview v-if="selectedCameraId" :camera-id="selectedCameraId"
            :direct-url="getCameraStreamUrl(selectedCamera!)" @status-change="updateCameraPreviewStatus" />
        </q-card-section>
        <q-card-section>
          <div class="text-subtitle2">
            摄像头状态:
            <span :class="{
              'text-positive': previewCameraStatus === 'online',
              'text-negative': previewCameraStatus === 'error',
              'text-grey': previewCameraStatus === 'offline'
            }">
              {{ deviceStatusText(previewCameraStatus) }}
            </span>
          </div>
          <div class="text-caption">
            流地址: {{ selectedCamera ? getCameraStreamUrl(selectedCamera) : '' }}
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed, onBeforeUnmount } from 'vue'
import { useQuasar } from 'quasar'
import { settingsService, SystemSettings, MesSettings, Device } from '../services/settings'
import { cameraService } from '../services/camera'
import CameraPreview from '../components/common/CameraPreview.vue'

const $q = useQuasar()

// Device config type definition to fix TypeScript errors
interface DeviceConfig {
  ip?: string;
  port?: string;
  resolution?: string;
  format?: string;
  mode?: string;
  rack?: number;
  slot?: number;
  [key: string]: any; // Allow any additional properties
}

// Type-safe device form
interface DeviceForm {
  id: number;
  name: string;
  type: string;
  model: string;
  config: DeviceConfig;
  cameraType: string;
  deviceId: number;
  streamUrl: string;
}

// System settings with default values
const systemSettings = reactive<SystemSettings>({
  auto_save_interval: 5,
  data_retention: '30天',
  alarm_threshold: 90
})

// MES settings with default values
const mesSettings = reactive<MesSettings>({
  server_url: '',
  api_key: ''
})

// Device list
const devices = ref<Device[]>([])
const deviceTypes = ['camera', 'light', 'plc']

// Device form
const showAddDeviceDialog = ref(false)
const isEditMode = ref(false)
const deviceForm = reactive<DeviceForm>({
  id: 0,
  name: '',
  type: 'camera',
  model: '',
  config: {
    ip: '',
    port: '',
    resolution: '',
    format: '',
    mode: '连续',
    rack: 0,
    slot: 0
  },
  cameraType: 'local',
  deviceId: 0,
  streamUrl: ''
})

// Device to delete
const showConfirmDeleteDialog = ref(false)
const deviceToDelete = ref<Device | null>(null)

// Device type filtering
const activeDeviceTab = ref('all')

// Filtered devices based on selected tab
const filteredDevices = computed(() => {
  if (activeDeviceTab.value === 'all') {
    return devices.value
  }
  return devices.value.filter(device => device.type === activeDeviceTab.value)
})

// Save system settings
const saveSystemSettings = async () => {
  $q.loading.show({
    message: '正在保存系统设置...'
  });
  
  try {
    const result = await settingsService.updateSystemSettings(systemSettings);
    
    // 保存成功后更新本地数据
    if (result) {
      Object.assign(systemSettings, result);
    }
    
    $q.notify({
      type: 'positive',
      message: '系统设置已保存',
      position: 'top'
    });
  } catch (error) {
    console.error('Failed to save system settings:', error);
    $q.notify({
      type: 'negative',
      message: '保存系统设置失败',
      position: 'top'
    });
    
    // 保存失败时重新加载设置
    await loadSystemSettings();
  } finally {
    $q.loading.hide();
  }
}

// Save MES settings
const saveMesSettings = async () => {
  $q.loading.show({
    message: '正在保存MES设置...'
  });
  
  try {
    const result = await settingsService.updateMesSettings(mesSettings);
    
    // 保存成功后更新本地数据
    if (result) {
      Object.assign(mesSettings, result);
    }
    
    $q.notify({
      type: 'positive',
      message: 'MES设置已保存',
      position: 'top'
    });
  } catch (error) {
    console.error('Failed to save MES settings:', error);
    $q.notify({
      type: 'negative',
      message: '保存MES设置失败',
      position: 'top'
    });
    
    // 保存失败时重新加载设置
    await loadMesSettings();
  } finally {
    $q.loading.hide();
  }
}

// Load devices
const loadDevices = async () => {
  try {
    devices.value = await settingsService.getDevices()
  } catch (error) {
    console.error('Failed to load devices:', error)
    $q.notify({
      type: 'negative',
      message: '加载设备列表失败',
      position: 'top'
    })
  }
}

// Get device icon based on type
const getDeviceIcon = (type: string): string => {
  switch (type) {
    case 'camera':
      return 'videocam'
    case 'light':
      return 'lightbulb'
    case 'plc':
      return 'memory'
    default:
      return 'device_hub'
  }
}

// Edit device - Fixed TypeScript indexing issues
const editDevice = (device: Device) => {
  isEditMode.value = true
  deviceForm.id = device.id
  deviceForm.name = device.name
  deviceForm.type = device.type
  deviceForm.model = device.model || ''

  // 重置配置对象
  deviceForm.config = {
    ip: '',
    port: '',
    resolution: '',
    format: '',
    mode: '连续',
    rack: 0,
    slot: 0
  }

  // 根据设备类型设置配置
  if (device.config) {
    // 复制现有配置
    if (device.type === 'camera') {
      deviceForm.config.ip = device.config.ip || ''
      deviceForm.config.resolution = device.config.resolution || ''
      deviceForm.config.format = device.config.format || 'MJPEG'

      // 如果是本地设备，从source中提取设备ID
      if (device.config.source && device.config.source.includes('device:')) {
        const deviceId = device.config.source.split(':')[1]
        deviceForm.config.source = `device:${deviceId}`
      }
    } else if (device.type === 'light') {
      deviceForm.config.port = device.config.port || ''
      deviceForm.config.mode = device.config.mode || '连续'
    } else if (device.type === 'plc') {
      deviceForm.config.ip = device.config.ip || ''
      deviceForm.config.rack = device.config.rack || 0
      deviceForm.config.slot = device.config.slot || 0
    }
  }

  showAddDeviceDialog.value = true
}

// Confirm delete device
const confirmDeleteDevice = (device: Device) => {
  deviceToDelete.value = device
  showConfirmDeleteDialog.value = true
}

// Delete device
const deleteDevice = async () => {
  if (!deviceToDelete.value) return

  try {
    await settingsService.deleteDevice(deviceToDelete.value.id)
    await loadDevices()
    $q.notify({
      type: 'positive',
      message: '设备已删除',
      position: 'top'
    })
    showConfirmDeleteDialog.value = false
  } catch (error) {
    console.error('Failed to delete device:', error)
    $q.notify({
      type: 'negative',
      message: '删除设备失败',
      position: 'top'
    })
  }
}

// Save device - Create or Update
const saveDevice = async () => {
  try {
    // 设置配置
    if (!deviceForm.config) deviceForm.config = {};

    if (deviceForm.type === 'camera') {
      switch (deviceForm.cameraType) {
        case 'local':
          deviceForm.config.source = `device:${deviceForm.deviceId || 0}`;
          break;
        case 'rtsp':
          deviceForm.config.source = deviceForm.streamUrl;
          break;
        case 'http':
          deviceForm.config.source = deviceForm.streamUrl;
          break;
        case 'ip':
          deviceForm.config.ip = deviceForm.streamUrl;
          deviceForm.config.source = `rtsp://${deviceForm.streamUrl}:554/stream`;
          break;
      }

      // 如果是外部URL，先不要自动设置stream_url字段，让后端处理
      if (deviceForm.cameraType !== 'local') {
        deviceForm.config.is_external = true;
      }
    }

    const deviceData: any = {
      name: deviceForm.name,
      type: deviceForm.type,
      model: deviceForm.model,
      config: {}
    }

    // 根据设备类型添加配置
    if (deviceForm.type === 'camera') {
      deviceData.config = {
        ip: deviceForm.config.ip,
        resolution: deviceForm.config.resolution,
        format: deviceForm.config.format || 'MJPEG'
      }

      // 如果编辑现有设备，保留source配置
      if (isEditMode.value && devices.value.find(d => d.id === deviceForm.id)?.config?.source) {
        deviceData.config.source = devices.value.find(d => d.id === deviceForm.id)?.config?.source
      }
    } else if (deviceForm.type === 'light') {
      deviceData.config = {
        port: deviceForm.config.port,
        mode: deviceForm.config.mode
      }
    } else if (deviceForm.type === 'plc') {
      deviceData.config = {
        ip: deviceForm.config.ip,
        rack: Number(deviceForm.config.rack),
        slot: Number(deviceForm.config.slot)
      }
    }

    if (isEditMode.value) {
      // 更新现有设备
      await settingsService.updateDevice(deviceForm.id, deviceData)
      $q.notify({
        type: 'positive',
        message: '设备已更新',
        position: 'top'
      })
    } else {
      // 创建新设备
      await settingsService.createDevice(deviceData)
      $q.notify({
        type: 'positive',
        message: '设备已添加',
        position: 'top'
      })
    }

    // 重新加载设备列表
    await loadDevices()

    // 关闭对话框并重置表单
    showAddDeviceDialog.value = false
    resetDeviceForm()

    // 检查摄像头状态
    if (deviceForm.type === 'camera') {
      setTimeout(checkActiveCameras, 1000)
    }
  } catch (error) {
    console.error('保存设备失败:', error)
    $q.notify({
      type: 'negative',
      message: '保存设备失败',
      position: 'top'
    })
  }
}

// Reset device form
const resetDeviceForm = () => {
  isEditMode.value = false
  deviceForm.id = 0
  deviceForm.name = ''
  deviceForm.type = 'camera'
  deviceForm.model = ''
  deviceForm.config = {
    ip: '',
    port: '',
    resolution: '',
    format: '',
    mode: '连续',
    rack: 0,
    slot: 0
  }
  deviceForm.cameraType = 'local'
  deviceForm.deviceId = 0
  deviceForm.streamUrl = ''
}

// Device status text
const deviceStatusText = (status: string): string => {
  switch (status) {
    case 'online': return '在线'
    case 'offline': return '离线'
    case 'error': return '故障'
    default: return '未知'
  }
}

// Get device type display label
const getDeviceTypeLabel = (type: string): string => {
  switch (type) {
    case 'camera': return '相机'
    case 'light': return '光源'
    case 'plc': return '控制器'
    default: return ''
  }
}

// Add new device with pre-selected type
const addNewDevice = (type: string) => {
  resetDeviceForm()
  deviceForm.type = type
  showAddDeviceDialog.value = true
}

// Camera status check interval
let statusCheckInterval: number | null = null;

// Setup status check interval
onMounted(() => {
  // Load settings first
  Promise.all([
    loadSystemSettings(),
    loadMesSettings(),
    loadDevices()
  ]).then(() => {
    // Start periodic status check after devices are loaded
    statusCheckInterval = window.setInterval(checkActiveCameras, 10000); // Check every 10 seconds
    // Initial check
    checkActiveCameras();
  });
});

// Clean up interval when component is unmounted
onBeforeUnmount(() => {
  if (statusCheckInterval !== null) {
    clearInterval(statusCheckInterval);
  }
});

// 添加强制刷新设备状态功能
const refreshDeviceStatus = async () => {
  try {
    console.log("手动刷新设备状态");
    await loadDevices(); // 重新获取设备列表
    checkActiveCameras(); // 检查摄像头状态
  } catch (error) {
    console.error("刷新设备状态出错:", error);
  }
};

// 添加切换设备状态的函数
const toggleDeviceStatus = async (device: Device) => {
  try {
    const newStatus = device.status === 'online' ? 'offline' : 'online';
    console.log(`手动切换设备 ${device.name} 状态从 ${device.status} 到 ${newStatus}`);

    await settingsService.updateDeviceStatus(device.id, newStatus);
    device.status = newStatus;

    $q.notify({
      type: newStatus === 'online' ? 'positive' : 'warning',
      message: `${device.name} 已${newStatus === 'online' ? '上线' : '离线'}`,
      position: 'top'
    });
  } catch (error) {
    console.error(`切换设备状态出错:`, error);
    $q.notify({
      type: 'negative',
      message: '更新设备状态失败',
      position: 'top'
    });
  }
}

// 添加控制变量
const disableAutoCheck = ref(false);

// Get camera stream URL
const getCameraStreamUrl = (device: Device): string => {
  if (!device.config || !device.config.source) {
    return '未配置';
  }

  const cameraId = cameraService.getCameraIdFromDevice(device);
  if (!cameraId) {
    return '未配置';
  }

  return cameraService.getCameraStreamUrl(cameraId);
};

// 添加摄像头预览状态
const showCameraPreview = ref(false);
const selectedCamera = ref<Device | null>(null);
const selectedCameraId = ref<string | null>(null);
const previewCameraStatus = ref<'online' | 'offline' | 'error'>('offline');

// 打开摄像头预览
const previewCamera = (device: Device) => {
  selectedCamera.value = device;
  const cameraId = cameraService.getCameraIdFromDevice(device);
  if (cameraId) {
    selectedCameraId.value = cameraId;
    showCameraPreview.value = true;
  } else {
    $q.notify({
      type: 'negative',
      message: '无法获取摄像头ID，请检查配置',
      position: 'top'
    });
  }
};

// 更新预览摄像头状态
const updateCameraPreviewStatus = (status: 'online' | 'offline' | 'error') => {
  previewCameraStatus.value = status;

  // 如果当前选中的设备状态与预览状态不同，更新设备状态
  if (selectedCamera.value && selectedCamera.value.status !== status) {
    settingsService.updateDeviceStatus(selectedCamera.value.id, status);
    selectedCamera.value.status = status;

    // 更新设备列表中的状态
    const deviceIndex = devices.value.findIndex(d => d.id === selectedCamera.value?.id);
    if (deviceIndex !== -1) {
      devices.value[deviceIndex].status = status;
    }
  }
};

// Get placeholder for camera type
const getPlaceholderForCameraType = (type: string): string => {
  switch (type) {
    case 'rtsp':
      return 'rtsp://username:password@192.168.1.100:554/stream';
    case 'http':
      return 'http://192.168.1.100:8080/video';
    case 'ip':
      return '192.168.1.100';
    default:
      return '';
  }
};

// Add this function before the saveDevice function
const checkActiveCameras = async () => {
  try {
    // Refresh devices list
    await loadDevices();

    // Check camera statuses
    const cameraDevices = devices.value.filter(d => d.type === 'camera');
    for (const device of cameraDevices) {
      if (device.config?.source) {
        const cameraId = cameraService.getCameraIdFromDevice(device);
        if (cameraId) {
          const status = await cameraService.getCameraStatus(cameraId);
          if (device.status !== status.status) {
            await settingsService.updateDeviceStatus(device.id, status.status as 'error' | 'online' | 'offline');
            device.status = status.status as 'error' | 'online' | 'offline';
          }
        }
      }
    }
  } catch (error) {
    console.error('检查摄像头状态出错:', error);
  }
};

// Add these functions to load settings
const loadSystemSettings = async () => {
  try {
    const data = await settingsService.getSystemSettings();
    if (data) {
      // 确保有合理的默认值
      const defaultSettings = {
        auto_save_interval: 5,
        data_retention: '30天',
        alarm_threshold: 90
      };
      
      // 合并后端数据和默认值
      Object.assign(systemSettings, defaultSettings, data);
      console.log('System settings loaded:', systemSettings);
    }
  } catch (error) {
    console.error('Failed to load system settings:', error);
    $q.notify({
      type: 'negative',
      message: '加载系统设置失败',
      position: 'top'
    });
  }
};

const loadMesSettings = async () => {
  try {
    const data = await settingsService.getMesSettings();
    if (data) {
      // 确保有合理的默认值
      const defaultSettings = {
        server_url: '',
        api_key: ''
      };
      
      // 合并后端数据和默认值
      Object.assign(mesSettings, defaultSettings, data);
      console.log('MES settings loaded:', mesSettings);
    }
  } catch (error) {
    console.error('Failed to load MES settings:', error);
    $q.notify({
      type: 'negative',
      message: '加载MES设置失败',
      position: 'top'
    });
  }
};
</script>

<style lang="scss" scoped>
.settings-page {
  background: var(--dark-page);
}

.settings-card {
  background: var(--dark-card);
}
</style>