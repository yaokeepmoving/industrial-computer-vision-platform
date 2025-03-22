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
                  <q-slider
                    v-model="autoSaveInterval"
                    :min="1"
                    :max="60"
                    :step="1"
                    label
                    label-value="${value}分钟"
                    class="q-mt-md"
                  />
                </q-item-section>
              </q-item>
              <q-item>
                <q-item-section>
                  <q-item-label>数据保留时间</q-item-label>
                  <q-select
                    v-model="dataRetention"
                    :options="['7天', '30天', '90天', '180天', '365天']"
                    outlined
                    dense
                    class="q-mt-sm"
                  />
                </q-item-section>
              </q-item>
              <q-item>
                <q-item-section>
                  <q-item-label>告警阈值</q-item-label>
                  <q-input
                    v-model="alarmThreshold"
                    type="number"
                    outlined
                    dense
                    suffix="%"
                    class="q-mt-sm"
                  />
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
                  <q-input
                    v-model="mesServer"
                    outlined
                    dense
                    placeholder="http://mes.example.com"
                    class="q-mt-sm"
                  />
                </q-item-section>
              </q-item>
              <q-item>
                <q-item-section>
                  <q-item-label>API密钥</q-item-label>
                  <q-input
                    v-model="mesApiKey"
                    outlined
                    dense
                    type="password"
                    class="q-mt-sm"
                  />
                </q-item-section>
              </q-item>
              <q-item>
                <q-item-section>
                  <q-btn
                    color="primary"
                    icon="sync"
                    label="测试连接"
                    class="q-mt-md"
                  />
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
            <div class="text-h6">设备管理</div>
            <q-list separator class="q-mt-md">
              <!-- 相机设备 -->
              <q-expansion-item
                group="devices"
                icon="videocam"
                label="工业相机"
                caption="HIKVISION MV-CA060-10GM"
                default-opened
              >
                <q-card>
                  <q-card-section>
                    <div class="row q-col-gutter-md">
                      <div class="col-12">
                        <q-input
                          outlined
                          dense
                          v-model="cameraIp"
                          label="IP地址"
                        />
                      </div>
                      <div class="col-12">
                        <q-select
                          outlined
                          dense
                          v-model="cameraResolution"
                          :options="['1920x1080', '1280x720', '800x600']"
                          label="分辨率"
                        />
                      </div>
                      <div class="col-12">
                        <q-select
                          outlined
                          dense
                          v-model="cameraFormat"
                          :options="['MJPEG', 'H264', 'H265']"
                          label="视频格式"
                        />
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
              </q-expansion-item>

              <!-- 光源控制器 -->
              <q-expansion-item
                group="devices"
                icon="light_mode"
                label="光源控制器"
                caption="CST-LC100"
              >
                <q-card>
                  <q-card-section>
                    <div class="row q-col-gutter-md">
                      <div class="col-12">
                        <q-input
                          outlined
                          dense
                          v-model="lightPort"
                          label="串口号"
                        />
                      </div>
                      <div class="col-12">
                        <q-select
                          outlined
                          dense
                          v-model="lightMode"
                          :options="['连续', '频闪', '触发']"
                          label="工作模式"
                        />
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
              </q-expansion-item>

              <!-- PLC设备 -->
              <q-expansion-item
                group="devices"
                icon="memory"
                label="PLC控制器"
                caption="Siemens S7-1200"
              >
                <q-card>
                  <q-card-section>
                    <div class="row q-col-gutter-md">
                      <div class="col-12">
                        <q-input
                          outlined
                          dense
                          v-model="plcIp"
                          label="IP地址"
                        />
                      </div>
                      <div class="col-12">
                        <q-input
                          outlined
                          dense
                          v-model="plcRack"
                          type="number"
                          label="机架号"
                        />
                      </div>
                      <div class="col-12">
                        <q-input
                          outlined
                          dense
                          v-model="plcSlot"
                          type="number"
                          label="插槽号"
                        />
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
              </q-expansion-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'

// 系统参数
const autoSaveInterval = ref(5)
const dataRetention = ref('30天')
const alarmThreshold = ref(90)

// MES配置
const mesServer = ref('')
const mesApiKey = ref('')

// 相机参数
const cameraIp = ref('192.168.1.100')
const cameraResolution = ref('1920x1080')
const cameraFormat = ref('MJPEG')

// 光源参数
const lightPort = ref('COM1')
const lightMode = ref('连续')

// PLC参数
const plcIp = ref('192.168.1.200')
const plcRack = ref(0)
const plcSlot = ref(1)
</script>

<style lang="scss" scoped>
.settings-page {
  background: var(--dark-page);
}

.settings-card {
  background: var(--dark-card);
}
</style>