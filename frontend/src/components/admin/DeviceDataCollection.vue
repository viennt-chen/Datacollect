<template>
  <div>
    <!-- Action bar -->
    <v-toolbar flat color="transparent" class="mb-4">
      <div>
        <div class="text-h5 font-weight-bold d-flex align-center ga-2">
          <v-icon icon="mdi-database-cog" color="primary" />
          数据采集 - {{ deviceInfo.device_name || deviceInfo.device_code }}
        </div>
        <div class="text-caption text-medium-emphasis mt-1">
          <span class="cursor-pointer" @click="goBack">设备管理</span>
          / 数据采集
        </div>
      </div>
      <v-spacer />
      <v-btn variant="outlined" prepend-icon="mdi-arrow-left" @click="goBack">
        返回设备列表
      </v-btn>
    </v-toolbar>

    <!-- Device Info Card -->
    <v-card class="mb-4">
      <v-card-text>
        <v-table density="compact">
          <tbody>
            <tr>
              <td class="text-medium-emphasis" style="width:120px">设备编号</td><td>{{ deviceInfo.device_code }}</td>
              <td class="text-medium-emphasis" style="width:120px">设备名称</td><td>{{ deviceInfo.device_name }}</td>
              <td class="text-medium-emphasis" style="width:120px">设备类型</td><td>{{ deviceInfo.device_type || '-' }}</td>
              <td class="text-medium-emphasis" style="width:120px">设备状态</td>
              <td><v-chip :color="statusColor(deviceInfo.status)" size="small" variant="tonal">{{ getStatusText(deviceInfo.status) }}</v-chip></td>
            </tr>
          </tbody>
        </v-table>
      </v-card-text>
    </v-card>

    <!-- Tabs + Controls -->
    <v-card class="mb-4">
      <v-toolbar flat density="compact" color="transparent">
        <v-tabs v-model="activeTab" bg-color="transparent" show-arrows>
          <v-tab v-for="topicConfig in topicConfigs" :key="topicConfig.topic_name" :value="topicConfig.topic_name">
            <v-icon :icon="getTopicIcon(topicConfig.topic_type)" class="mr-1" />
            {{ getTopicDisplayName(topicConfig) }}
            <v-icon v-if="topicData[topicConfig.topic_name]?.has_data" icon="mdi-check-circle" size="small" color="success" class="ml-1" />
          </v-tab>
          <v-tab v-if="topicConfigs.length === 0" disabled>
            <v-icon icon="mdi-information" class="mr-1" />
            该设备未配置数据采集Topic
          </v-tab>
        </v-tabs>
        <v-spacer />
        <div class="d-flex align-center ga-3 mr-4">
          <v-select v-model="dataSource" :items="dataSourceOptions" label="数据源" density="compact" variant="outlined" hide-details style="max-width: 140px" :disabled="isRealtimeMode" />
          <v-chip :color="dataSourceStatusClass === 'status-error' ? 'error' : dataSourceStatusClass === 'status-loading' ? 'warning' : 'success'" size="small" variant="tonal">
            <v-icon :icon="dataSourceStatusClass === 'status-error' ? 'mdi-close-circle' : dataSourceStatusClass === 'status-loading' ? 'mdi-loading' : 'mdi-check-circle'" size="x-small" class="mr-1" />
            {{ dataSourceStatusText }}
          </v-chip>
          <v-switch v-model="autoRefresh" label="自动刷新" density="compact" hide-details />
          <v-select v-model="refreshInterval" :items="refreshIntervalOptions" density="compact" variant="outlined" hide-details style="max-width: 100px" :disabled="!autoRefresh" />
        </div>
      </v-toolbar>
    </v-card>

    <!-- Dynamic Topic Tab Content -->
    <v-window v-model="activeTab">
      <v-window-item v-for="topicConfig in topicConfigs" :key="topicConfig.topic_name" :value="topicConfig.topic_name">
        <v-card>
          <v-card-title class="d-flex align-center ga-2">
            <v-icon :icon="getTopicIcon(topicConfig.topic_type)" />
            {{ getTopicDisplayName(topicConfig) }} - 最新数据
            <v-spacer />
            <v-btn color="primary" variant="outlined" prepend-icon="mdi-refresh" size="small" :loading="topicLoading[topicConfig.topic_name]" @click="loadTopicData(topicConfig.topic_name)">
              刷新
            </v-btn>
          </v-card-title>
          <v-divider />
          <v-card-text>
            <div v-if="topicLoading[topicConfig.topic_name]" class="text-center pa-8">
              <v-progress-circular indeterminate color="primary" class="mb-2" />
              <p class="text-medium-emphasis">正在加载数据...</p>
            </div>
            <div v-else-if="!topicData[topicConfig.topic_name]?.has_data" class="text-center pa-8">
              <v-icon icon="mdi-inbox" size="48" color="grey-lighten-1" />
              <p class="text-medium-emphasis mt-2">暂无数据</p>
            </div>
            <div v-else>
              <div class="d-flex align-center ga-2 mb-4 flex-wrap">
                <v-icon icon="mdi-clock-outline" size="small" />
                <span class="text-caption">采集时间：{{ formatDateTime(topicData[topicConfig.topic_name]?.timestamp) }}</span>
                <span v-if="topicData[topicConfig.topic_name]?.original_timestamp" class="text-caption text-medium-emphasis">
                  (原始时间：{{ formatDateTime(topicData[topicConfig.topic_name]?.original_timestamp) }})
                </span>
                <v-chip v-if="topicData[topicConfig.topic_name]?.source" :color="topicData[topicConfig.topic_name]?.source === 'mqtt_realtime' ? 'success' : 'info'" size="small" variant="tonal">
                  <v-icon :icon="topicData[topicConfig.topic_name]?.source === 'mqtt_realtime' ? 'mdi-broadcast' : 'mdi-database'" size="x-small" class="mr-1" />
                  {{ topicData[topicConfig.topic_name]?.source === 'mqtt_realtime' ? 'MQTT实时' : '数据库' }}
                </v-chip>
              </div>

              <!-- Parsed view with parse rules -->
              <v-table v-if="topicConfig.parse_rules" density="compact">
                <tbody>
                  <tr v-for="rule in getOrderedParseRules(topicConfig.parse_rules)" :key="rule.key">
                    <td class="text-medium-emphasis" style="width:160px">{{ rule.label }}</td>
                    <td>{{ formatDataValue(getNestedValue(topicData[topicConfig.topic_name]?.data, rule.path), rule) }}</td>
                  </tr>
                </tbody>
              </v-table>

              <!-- Event type parsed view -->
              <v-table v-else-if="topicConfig.topic_type === 'event'" density="compact">
                <tbody>
                  <tr><td class="text-medium-emphasis" style="width:120px">事件ID</td><td>{{ topicData[topicConfig.topic_name]?.data.event_uid || '-' }}</td></tr>
                  <tr><td class="text-medium-emphasis">设备编号</td><td>{{ topicData[topicConfig.topic_name]?.data.machine_id || '-' }}</td></tr>
                  <tr><td class="text-medium-emphasis">操作员</td><td>{{ topicData[topicConfig.topic_name]?.data.operator_name || '-' }} ({{ topicData[topicConfig.topic_name]?.data.operator_id || '-' }})</td></tr>
                  <tr><td class="text-medium-emphasis">班组信息</td><td>{{ topicData[topicConfig.topic_name]?.data.group_name || '-' }} - {{ topicData[topicConfig.topic_name]?.data.factory_name || '-' }}</td></tr>
                  <tr><td class="text-medium-emphasis">开始时间</td><td>{{ formatDateTime(new Date(topicData[topicConfig.topic_name]?.data.start_time).toISOString()) }}</td></tr>
                  <tr><td class="text-medium-emphasis">结束时间</td><td>{{ formatDateTime(new Date(topicData[topicConfig.topic_name]?.data.end_time).toISOString()) }}</td></tr>
                  <tr><td class="text-medium-emphasis">总耗时</td><td>{{ formatDuration(topicData[topicConfig.topic_name]?.data.duringtime) }}</td></tr>
                  <tr><td class="text-medium-emphasis">加工耗时</td><td>{{ formatDuration(topicData[topicConfig.topic_name]?.data.machine_duringtime) }}</td></tr>
                  <tr><td class="text-medium-emphasis">工艺编号</td><td>{{ topicData[topicConfig.topic_name]?.data.process_no || '-' }}</td></tr>
                </tbody>
              </v-table>

              <!-- Raw JSON view -->
              <v-card v-else variant="outlined" class="mt-2">
                <v-card-text>
                  <pre class="text-caption" style="white-space: pre-wrap; word-break: break-all;">{{ JSON.stringify(topicData[topicConfig.topic_name]?.data, null, 2) }}</pre>
                </v-card-text>
              </v-card>

              <div class="d-flex ga-2 mt-4">
                <v-btn variant="outlined" prepend-icon="mdi-code-braces" size="small" @click="parseRawJsonData(topicConfig.topic_name)">
                  解析原始JSON
                </v-btn>
                <v-btn color="primary" variant="outlined" prepend-icon="mdi-cog" size="small" @click="openDataKeyManager(topicConfig.topic_name)">
                  管理数据键
                </v-btn>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-window-item>
    </v-window>

    <!-- Data Key Manager Dialog -->
    <v-dialog v-model="dataKeyDialogVisible" max-width="1200" persistent scrollable>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-cog" class="mr-2" />
          数据键解析与分析 - {{ getTopicDisplayName(getTopicConfigByKeyManagerTopic()) }}
          <v-spacer />
          <v-btn color="success" variant="outlined" prepend-icon="mdi-chart-bar" size="small" :disabled="currentDataKeys.length === 0" @click="runDataAnalysis" class="mr-2">
            运行分析
          </v-btn>
          <v-btn icon="mdi-close" variant="text" size="small" @click="closeDataKeyDialog" />
        </v-card-title>
        <v-divider />
        <v-card-text style="height: 70vh;">
          <v-row>
            <!-- Left Panel: Data Key Management -->
            <v-col cols="12" md="5">
              <!-- Raw JSON -->
              <v-card variant="outlined" class="mb-4">
                <v-card-title class="d-flex align-center text-subtitle-2">
                  <v-icon icon="mdi-code-braces" size="small" class="mr-1" />
                  原始JSON数据
                  <v-spacer />
                  <v-btn variant="text" prepend-icon="mdi-refresh" size="x-small" @click="parseRawJsonDataForKeyManager">刷新</v-btn>
                </v-card-title>
                <v-divider />
                <v-card-text style="max-height: 200px; overflow-y: auto;">
                  <pre class="text-caption" style="white-space: pre-wrap; word-break: break-all;">{{ formatJsonForDisplay(parsedJsonData) }}</pre>
                </v-card-text>
              </v-card>

              <!-- Data Keys List -->
              <v-card variant="outlined">
                <v-card-title class="d-flex align-center text-subtitle-2">
                  <v-icon icon="mdi-key" size="small" class="mr-1" />
                  数据键定义
                  <v-spacer />
                  <v-btn color="primary" variant="text" prepend-icon="mdi-plus-circle" size="x-small" @click="showAddDataKeyForm">添加</v-btn>
                </v-card-title>
                <v-divider />
                <v-card-text style="max-height: 400px; overflow-y: auto;">
                  <div v-if="currentDataKeys.length === 0" class="text-center pa-4">
                    <v-icon icon="mdi-inbox" size="36" color="grey-lighten-1" />
                    <p class="text-caption text-medium-emphasis mt-1">暂无数据键定义</p>
                  </div>
                  <v-list v-else density="compact">
                    <v-list-item
                      v-for="(key, index) in currentDataKeys"
                      :key="index"
                      :active="selectedKeyIndex === index"
                      @click="selectDataKey(index)"
                      rounded
                    >
                      <v-list-item-title>{{ key.label }}</v-list-item-title>
                      <v-list-item-subtitle>
                        <div>{{ key.path }}</div>
                        <div class="d-flex ga-1 mt-1">
                          <v-chip size="x-small" variant="tonal" color="primary">{{ key.type }}</v-chip>
                          <v-chip v-if="key.validation && key.validation.required" size="x-small" variant="tonal" color="warning">必填</v-chip>
                        </div>
                      </v-list-item-subtitle>
                      <template v-slot:append>
                        <div class="d-flex ga-1">
                          <v-btn icon variant="text" size="x-small" @click.stop="editDataKey(index)">
                            <v-icon icon="mdi-pencil" size="small" />
                          </v-btn>
                          <v-btn icon variant="text" size="x-small" color="error" @click.stop="deleteDataKey(index)">
                            <v-icon icon="mdi-delete" size="small" />
                          </v-btn>
                        </div>
                      </template>
                    </v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>
            </v-col>

            <!-- Right Panel: Form & Analysis -->
            <v-col cols="12" md="7">
              <!-- Add/Edit Data Key Form -->
              <v-card v-if="showDataKeyForm" variant="outlined" class="mb-4">
                <v-card-title class="text-subtitle-2">
                  <v-icon icon="mdi-plus-circle" size="small" class="mr-1" />
                  {{ editingDataKeyIndex >= 0 ? '编辑数据键' : '添加数据键' }}
                </v-card-title>
                <v-divider />
                <v-card-text>
                  <v-form>
                    <v-text-field v-model="dataKeyForm.label" label="数据键标签" placeholder="例如：温度、压力" :rules="[v => !!v || '请输入标签']" required />
                    <v-text-field v-model="dataKeyForm.path" label="JSON路径" placeholder="例如：data.temperature 或 data.sensors[0].value" :rules="[v => !!v || '请输入路径']" required hint="使用点号分隔的JSON路径，支持数组索引" persistent-hint />
                    <v-row dense class="mt-1">
                      <v-col cols="6">
                        <v-select v-model="dataKeyForm.type" :items="dataTypeOptions" label="数据类型" />
                      </v-col>
                      <v-col cols="6">
                        <v-text-field v-model="dataKeyForm.unit" label="单位" placeholder="例如：°C, MPa" />
                      </v-col>
                    </v-row>
                    <v-select v-model="dataKeyForm.formatter" :items="formatterOptions" label="分析方法" />
                    <v-textarea v-if="dataKeyForm.formatter === 'custom'" v-model="dataKeyForm.customFormatter" label="自定义格式化函数" placeholder="例如：(value) => value.toFixed(3) + ' ms'" rows="2" />

                    <!-- Validation Rules -->
                    <v-expansion-panels v-model="validationPanelModel" class="mt-2">
                      <v-expansion-panel>
                        <v-expansion-panel-title>
                          <v-icon icon="mdi-shield-check" size="small" class="mr-1" />
                          验证规则配置
                        </v-expansion-panel-title>
                        <v-expansion-panel-text>
                          <v-row dense>
                            <v-col cols="4">
                              <v-checkbox v-model="dataKeyForm.validation.required" label="必填字段" density="compact" hide-details />
                            </v-col>
                            <v-col cols="4">
                              <v-number-input v-model.number="dataKeyForm.validation.min" label="最小值" density="compact" controlVariant="stacked" />
                            </v-col>
                            <v-col cols="4">
                              <v-number-input v-model.number="dataKeyForm.validation.max" label="最大值" density="compact" controlVariant="stacked" />
                            </v-col>
                          </v-row>
                          <v-text-field v-model="dataKeyForm.validation.pattern" label="正则表达式" placeholder="例如：^[0-9]+$" density="compact" class="mt-1" />
                          <v-text-field v-model="dataKeyForm.validation.message" label="自定义验证消息" placeholder="验证失败时的提示信息" density="compact" />
                        </v-expansion-panel-text>
                      </v-expansion-panel>
                    </v-expansion-panels>

                    <div class="d-flex ga-2 mt-4">
                      <v-btn color="primary" prepend-icon="mdi-check-circle" :disabled="!canSaveDataKey" @click="saveDataKey">
                        {{ editingDataKeyIndex >= 0 ? '保存修改' : '添加' }}
                      </v-btn>
                      <v-btn variant="outlined" prepend-icon="mdi-close-circle" @click="cancelDataKeyForm">取消</v-btn>
                    </div>
                  </v-form>
                </v-card-text>
              </v-card>

              <!-- Analysis Results -->
              <v-card v-if="analysisResults.length > 0" variant="outlined" class="mb-4">
                <v-card-title class="d-flex align-center text-subtitle-2">
                  <v-icon icon="mdi-chart-bar" size="small" class="mr-1" />
                  分析结果
                  <v-spacer />
                  <v-btn variant="text" prepend-icon="mdi-download" size="x-small" @click="exportAnalysisResults">导出</v-btn>
                </v-card-title>
                <v-divider />
                <v-card-text>
                  <v-card v-for="(result, index) in analysisResults" :key="index" variant="outlined" class="mb-2">
                    <v-card-text>
                      <div class="d-flex align-center mb-2">
                        <strong>{{ result.keyLabel }}</strong>
                        <v-chip size="x-small" variant="tonal" color="primary" class="ml-2">{{ result.analysisType }}</v-chip>
                      </div>
                      <v-table v-if="result.statistics" density="compact">
                        <tbody>
                          <tr>
                            <td class="text-medium-emphasis">平均值</td><td>{{ result.statistics.mean }}</td>
                            <td class="text-medium-emphasis">最大值</td><td>{{ result.statistics.max }}</td>
                            <td class="text-medium-emphasis">最小值</td><td>{{ result.statistics.min }}</td>
                            <td class="text-medium-emphasis">标准差</td><td>{{ result.statistics.stdDev }}</td>
                          </tr>
                        </tbody>
                      </v-table>
                      <div v-if="result.trend" class="d-flex align-center ga-2 mt-1">
                        <v-icon :icon="result.trend.direction === 'up' ? 'mdi-arrow-up-right' : result.trend.direction === 'down' ? 'mdi-arrow-down-right' : 'mdi-minus'" size="small" :color="result.trend.direction === 'up' ? 'success' : result.trend.direction === 'down' ? 'error' : 'grey'" />
                        <span>{{ result.trend.direction === 'up' ? '上升' : result.trend.direction === 'down' ? '下降' : '平稳' }}</span>
                        <span class="text-caption text-medium-emphasis">变化率：{{ result.trend.rate }}%</span>
                      </div>
                      <div v-if="result.correlations && result.correlations.length > 0" class="mt-1">
                        <div v-for="(corr, idx) in result.correlations" :key="idx" class="d-flex ga-1 text-caption">
                          <span class="text-medium-emphasis">与 {{ corr.key }}:</span>
                          <span :class="getCorrelationClass(corr.coefficient)">r = {{ corr.coefficient }}</span>
                        </div>
                      </div>
                      <div v-if="result.validation" class="d-flex align-center ga-1 mt-1">
                        <v-icon :icon="result.validation.status === 'pass' ? 'mdi-check-circle' : 'mdi-close-circle'" size="small" :color="result.validation.status === 'pass' ? 'success' : 'error'" />
                        <span :class="result.validation.status === 'pass' ? 'text-success' : 'text-error'">{{ result.validation.message }}</span>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-card-text>
              </v-card>

              <!-- Data Preview -->
              <v-card v-if="selectedKeyIndex >= 0 && !showDataKeyForm" variant="outlined">
                <v-card-title class="text-subtitle-2">
                  <v-icon icon="mdi-eye" size="small" class="mr-1" />
                  数据预览
                </v-card-title>
                <v-divider />
                <v-card-text>
                  <v-table density="compact">
                    <tbody>
                      <tr><td class="text-medium-emphasis" style="width:100px">当前值</td><td>{{ getCurrentKeyValue(selectedKeyIndex) }}</td></tr>
                      <tr><td class="text-medium-emphasis">类型</td><td>{{ currentDataKeys[selectedKeyIndex]?.type }}</td></tr>
                      <tr v-if="currentDataKeys[selectedKeyIndex]?.validation">
                        <td class="text-medium-emphasis">验证状态</td>
                        <td>
                          <v-chip :color="validateKey(selectedKeyIndex) ? 'success' : 'error'" size="small" variant="tonal">
                            {{ validateKey(selectedKeyIndex) ? '通过' : '未通过' }}
                          </v-chip>
                        </td>
                      </tr>
                    </tbody>
                  </v-table>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn color="primary" prepend-icon="mdi-content-save" @click="saveParseRules">保存配置</v-btn>
          <v-btn variant="outlined" prepend-icon="mdi-close-circle" @click="closeDataKeyDialog">关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useMessage } from '@/composables/useMessage'
import { deviceAPI } from '@/api/index'
import { formatDateTime } from '@/utils/datetime'

const message = useMessage()
const route = useRoute()

const deviceInfo = reactive({
  device_code: '',
  device_name: '',
  device_type: '',
  status: ''
})

const activeTab = ref('')

const topicConfigs = ref([])
const topicData = reactive({})
const topicLoading = reactive({})

const autoRefresh = ref(false)
const refreshInterval = ref(10000)
let refreshTimer = null

const dataSource = ref('auto')
const dataSourceStatus = reactive({
  mqtt_connected: false,
  database_connected: true,
  loading: false
})

const isRealtimeMode = computed(() => dataSource.value === 'mqtt')

const dataSourceStatusClass = computed(() => {
  if (dataSourceStatus.loading) return 'status-loading'
  if (dataSource.value === 'mqtt' && !dataSourceStatus.mqtt_connected) return 'status-error'
  if (dataSource.value === 'database' && !dataSourceStatus.database_connected) return 'status-error'
  return 'status-success'
})

const dataSourceStatusIcon = computed(() => {
  if (dataSourceStatus.loading) return 'mdi-loading'
  if (dataSource.value === 'mqtt') return dataSourceStatus.mqtt_connected ? 'mdi-check-circle' : 'mdi-close-circle'
  return dataSourceStatus.database_connected ? 'mdi-check-circle' : 'mdi-close-circle'
})

const dataSourceStatusText = computed(() => {
  if (dataSourceStatus.loading) return '检测中...'
  if (dataSource.value === 'mqtt') return dataSourceStatus.mqtt_connected ? 'MQTT已连接' : 'MQTT未连接'
  return dataSourceStatus.database_connected ? '数据库正常' : '数据库异常'
})

const dataSourceOptions = [
  { title: '自动', value: 'auto' },
  { title: 'MQTT实时', value: 'mqtt' },
  { title: '数据库', value: 'database' }
]

const refreshIntervalOptions = [
  { title: '5秒', value: 5000 },
  { title: '10秒', value: 10000 },
  { title: '30秒', value: 30000 },
  { title: '1分钟', value: 60000 }
]

const dataTypeOptions = [
  { title: '字符串', value: 'string' },
  { title: '数字', value: 'number' },
  { title: '布尔值', value: 'boolean' },
  { title: '时间戳', value: 'timestamp' },
  { title: '对象', value: 'object' }
]

const formatterOptions = [
  { title: '无', value: '' },
  { title: '时间戳格式化', value: 'timestamp' },
  { title: '保留两位小数', value: 'round2' },
  { title: '保留四位小数', value: 'round4' },
  { title: '百分比显示', value: 'percentage' },
  { title: '自定义方法', value: 'custom' }
]

const dataKeyDialogVisible = ref(false)
const keyManagerTopic = ref('')
const parsedJsonData = ref(null)
const currentDataKeys = ref([])
const showDataKeyForm = ref(false)
const editingDataKeyIndex = ref(-1)
const selectedKeyIndex = ref(-1)
const validationPanelModel = ref(null)
const analysisResults = ref([])
const dataKeyForm = reactive({
  label: '',
  path: '',
  type: 'string',
  unit: '',
  formatter: '',
  customFormatter: '',
  validation: {
    required: false,
    min: null,
    max: null,
    pattern: '',
    message: ''
  }
})

const formatDuration = (milliseconds) => {
  if (!milliseconds && milliseconds !== 0) return '-'
  const seconds = milliseconds / 1000
  if (seconds < 60) {
    return `${seconds.toFixed(2)} 秒`
  }
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  if (minutes < 60) {
    return `${minutes} 分 ${remainingSeconds.toFixed(1)} 秒`
  }
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  return `${hours} 时 ${remainingMinutes} 分 ${remainingSeconds.toFixed(1)} 秒`
}

const statusColor = (status) => {
  const map = { active: 'success', inactive: 'error', maintenance: 'warning' }
  return map[status] || 'grey'
}

const getStatusText = (status) => {
  const textMap = { active: '运行中', inactive: '已停用', maintenance: '维护中' }
  return textMap[status] || status
}

const goBack = () => {
  window.history.back()
  window.dispatchEvent(new CustomEvent('showDataCollection', { detail: false }))
}

const getTopicIcon = (topicType) => {
  const iconMap = {
    pv_compress: 'mdi-chart-line',
    sv_compress: 'mdi-tune-vertical',
    alarm_compress: 'mdi-bell-ring',
    event: 'mdi-lightning-bolt'
  }
  return iconMap[topicType] || 'mdi-broadcast'
}

const getTopicDisplayName = (topicConfig) => {
  const typeDisplayMap = {
    pv_compress: 'PV 过程变量',
    sv_compress: 'SV 设定值',
    alarm_compress: 'ALARM 报警',
    event: '事件数据'
  }
  const baseName = typeDisplayMap[topicConfig.topic_type] || topicConfig.topic_type
  return topicConfig.description || baseName
}

const getOrderedParseRules = (parseRules) => {
  if (!parseRules) return []
  return Object.entries(parseRules).map(([key, rule]) => ({
    key,
    label: rule.label || key,
    path: rule.path || key,
    type: rule.type || 'string',
    unit: rule.unit || '',
    formatter: rule.formatter || null
  }))
}

const formatDataValue = (value, rule) => {
  if (value === null || value === undefined) return '-'

  if (rule.formatter === 'timestamp') {
    return formatDateTime(new Date(value).toISOString())
  }

  if (rule.formatter === 'round2') {
    return typeof value === 'number' ? value.toFixed(2) : value
  }

  if (rule.formatter === 'round4') {
    return typeof value === 'number' ? value.toFixed(4) : value
  }

  if (rule.formatter === 'percentage') {
    return typeof value === 'number' ? `${(value * 100).toFixed(2)}%` : value
  }

  if (rule.formatter === 'custom' && rule.customFormatter) {
    try {
      const formatterFn = new Function('value', `return (${rule.customFormatter})(value)`)
      return formatterFn(value)
    } catch (error) {
      return `格式化错误: ${error.message}`
    }
  }

  if (rule.unit) {
    return `${value} ${rule.unit}`
  }

  if (typeof value === 'object') {
    return JSON.stringify(value, null, 2)
  }

  return value
}

const getNestedValue = (obj, path) => {
  if (!obj || !path) return '-'
  const keys = path.split('.')
  let current = obj
  for (const key of keys) {
    if (current && typeof current === 'object' && key in current) {
      current = current[key]
    } else {
      return '-'
    }
  }
  return current ?? '-'
}

const startAutoRefresh = () => {
  stopAutoRefresh()
  if (autoRefresh.value && topicConfigs.value.length > 0) {
    refreshTimer = setInterval(() => {
      topicConfigs.value.forEach(config => {
        loadTopicData(config.topic_name, false)
      })
    }, refreshInterval.value)
  }
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

const loadDeviceTopicConfigs = async () => {
  try {
    const res = await deviceAPI.getDeviceDataCollectionConfig(deviceInfo.device_code)
    if (res.data) {
      topicConfigs.value = res.data.topic_configs || []

      if (topicConfigs.value.length > 0 && !activeTab.value) {
        activeTab.value = topicConfigs.value[0].topic_name
      }

      topicConfigs.value.forEach(config => {
        topicData[config.topic_name] = { has_data: false, data: null, timestamp: null, original_timestamp: null, source: null }
        topicLoading[config.topic_name] = false
      })

      topicConfigs.value.forEach(config => {
        loadTopicData(config.topic_name)
      })

      if (autoRefresh.value) {
        startAutoRefresh()
      }
    }
  } catch (error) {
    message.error('加载设备Topic配置失败')
  }
}

const loadDataSourceStatus = async () => {
  try {
    dataSourceStatus.loading = true
    const res = await deviceAPI.getDataSourceStatus(deviceInfo.device_code)
    if (res.data) {
      dataSourceStatus.mqtt_connected = res.data.mqtt_status?.connected || false
      dataSourceStatus.database_connected = res.data.database_status?.connected || true
    }
  } catch (error) {
    console.error('加载数据源状态失败:', error)
  } finally {
    dataSourceStatus.loading = false
  }
}

const loadTopicData = async (topicName, showLoading = true) => {
  try {
    if (showLoading) {
      topicLoading[topicName] = true
    }

    let res
    if (dataSource.value === 'mqtt') {
      res = await deviceAPI.getLatestData(deviceInfo.device_code, {
        topic_name: topicName,
        source: 'mqtt'
      })
    } else if (dataSource.value === 'database') {
      res = await deviceAPI.getLatestData(deviceInfo.device_code, {
        topic_name: topicName,
        source: 'database'
      })
    } else {
      res = await deviceAPI.getLatestData(deviceInfo.device_code, {
        topic_name: topicName,
        source: 'auto'
      })
    }

    if (res.data) {
      topicData[topicName] = {
        has_data: true,
        data: res.data.data || res.data,
        timestamp: res.data.timestamp || new Date().toISOString(),
        original_timestamp: res.data.original_timestamp || null,
        source: res.data.source || 'database'
      }
    }
  } catch (error) {
    if (showLoading) {
      message.error(`加载Topic ${topicName} 数据失败`)
    }
  } finally {
    if (showLoading) {
      topicLoading[topicName] = false
    }
  }
}

onMounted(async () => {
  deviceInfo.device_code = route.query.device_code || ''
  deviceInfo.device_name = route.query.device_name || ''

  if (deviceInfo.device_code) {
    await loadDataSourceStatus()
    await loadDeviceTopicConfigs()
  }
})

onUnmounted(() => {
  stopAutoRefresh()
})

watch(activeTab, (newTab) => {
  if (newTab && topicData[newTab] && !topicData[newTab].has_data) {
    loadTopicData(newTab)
  }
})

watch(autoRefresh, (newVal) => {
  if (newVal) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
})

watch(refreshInterval, () => {
  if (autoRefresh.value) {
    startAutoRefresh()
  }
})

const parseRawJsonData = (topicName) => {
  const data = topicData[topicName]?.data
  if (!data) {
    message.warning('暂无数据可解析')
    return
  }

  try {
    let parsedData = data
    if (typeof data === 'string') {
      parsedData = JSON.parse(data)
    }

    parsedJsonData.value = parsedData
    message.success('JSON数据解析成功')
  } catch (error) {
    message.error('JSON数据解析失败：' + error.message)
  }
}

const openDataKeyManager = (topicName) => {
  keyManagerTopic.value = topicName
  const topicConfig = topicConfigs.value.find(c => c.topic_name === topicName)

  if (topicConfig?.parse_rules) {
    currentDataKeys.value = getOrderedParseRules(topicConfig.parse_rules)
  } else {
    currentDataKeys.value = []
  }

  parseRawJsonDataForKeyManager()
  dataKeyDialogVisible.value = true
}

const parseRawJsonDataForKeyManager = () => {
  const data = topicData[keyManagerTopic.value]?.data
  if (!data) {
    parsedJsonData.value = null
    message.warning('暂无数据可解析')
    return
  }

  try {
    let parsedData = data
    if (typeof data === 'string') {
      parsedData = JSON.parse(data)
    }
    parsedJsonData.value = parsedData
  } catch (error) {
    parsedJsonData.value = null
    message.error('JSON数据解析失败：' + error.message)
  }
}

const getTopicConfigByKeyManagerTopic = () => {
  return topicConfigs.value.find(c => c.topic_name === keyManagerTopic.value) || {}
}

const formatJsonForDisplay = (jsonData) => {
  if (!jsonData) return '暂无数据'
  try {
    return JSON.stringify(jsonData, null, 2)
  } catch (error) {
    return '数据格式化失败'
  }
}

const showAddDataKeyForm = () => {
  editingDataKeyIndex.value = -1
  Object.assign(dataKeyForm, {
    label: '',
    path: '',
    type: 'string',
    unit: '',
    formatter: '',
    customFormatter: '',
    validation: {
      required: false,
      min: null,
      max: null,
      pattern: '',
      message: ''
    }
  })
  validationPanelModel.value = null
  showDataKeyForm.value = true
}

const editDataKey = (index) => {
  editingDataKeyIndex.value = index
  const key = currentDataKeys.value[index]
  Object.assign(dataKeyForm, {
    label: key.label,
    path: key.path,
    type: key.type,
    unit: key.unit || '',
    formatter: key.formatter || '',
    customFormatter: key.customFormatter || '',
    validation: key.validation || {
      required: false,
      min: null,
      max: null,
      pattern: '',
      message: ''
    }
  })
  validationPanelModel.value = null
  showDataKeyForm.value = true
}

const selectDataKey = (index) => {
  selectedKeyIndex.value = selectedKeyIndex.value === index ? -1 : index
  showDataKeyForm.value = false
}

const validateKey = (index) => {
  const key = currentDataKeys.value[index]
  if (!key || !key.validation) return true

  const value = getCurrentKeyValue(index)
  const validation = key.validation

  if (validation.required && (!value || value === '-')) {
    return false
  }

  if (key.type === 'number' && value !== '-') {
    const numValue = parseFloat(value)
    if (validation.min !== null && numValue < validation.min) {
      return false
    }
    if (validation.max !== null && numValue > validation.max) {
      return false
    }
  }

  if (validation.pattern && value !== '-') {
    const regex = new RegExp(validation.pattern)
    if (!regex.test(String(value))) {
      return false
    }
  }

  return true
}

const getCurrentKeyValue = (index) => {
  const key = currentDataKeys.value[index]
  if (!key) return '-'
  return getNestedValue(topicData[keyManagerTopic.value]?.data, key.path)
}

const deleteDataKey = (index) => {
  const key = currentDataKeys.value[index]
  if (confirm(`确定要删除数据键 "${key.label}" 吗？`)) {
    currentDataKeys.value.splice(index, 1)
    if (selectedKeyIndex.value === index) {
      selectedKeyIndex.value = -1
    } else if (selectedKeyIndex.value > index) {
      selectedKeyIndex.value--
    }
    message.success('数据键已删除')
  }
}

const canSaveDataKey = computed(() => {
  return dataKeyForm.label && dataKeyForm.path
})

const saveDataKey = () => {
  if (!dataKeyForm.label || !dataKeyForm.path) {
    message.warning('请填写数据键标签和JSON路径')
    return
  }

  const keyData = {
    label: dataKeyForm.label,
    path: dataKeyForm.path,
    type: dataKeyForm.type,
    unit: dataKeyForm.unit || undefined,
    formatter: dataKeyForm.formatter || undefined,
    customFormatter: dataKeyForm.formatter === 'custom' ? dataKeyForm.customFormatter : undefined,
    validation: dataKeyForm.validation.required || dataKeyForm.validation.min !== null ||
                dataKeyForm.validation.max !== null || dataKeyForm.validation.pattern ?
                { ...dataKeyForm.validation } : undefined
  }

  if (editingDataKeyIndex.value >= 0) {
    currentDataKeys.value[editingDataKeyIndex.value] = keyData
    message.success('数据键已更新')
  } else {
    currentDataKeys.value.push(keyData)
    message.success('数据键已添加')
  }

  cancelDataKeyForm()
}

const cancelDataKeyForm = () => {
  showDataKeyForm.value = false
  editingDataKeyIndex.value = -1
}

const runDataAnalysis = () => {
  analysisResults.value = []

  currentDataKeys.value.forEach((key, index) => {
    const value = getCurrentKeyValue(index)
    const result = {
      keyLabel: key.label,
      keyPath: key.path,
      analysisType: key.type
    }

    if (key.type === 'number' && value !== '-') {
      const numValue = parseFloat(value)
      result.statistics = {
        mean: numValue.toFixed(2),
        max: numValue.toFixed(2),
        min: numValue.toFixed(2),
        stdDev: '0.00'
      }

      result.trend = {
        direction: 'stable',
        rate: '0.00'
      }
    }

    if (key.validation) {
      const isValid = validateKey(index)
      result.validation = {
        status: isValid ? 'pass' : 'fail',
        message: isValid ? '验证通过' : (key.validation.message || '验证未通过')
      }
    }

    analysisResults.value.push(result)
  })

  if (currentDataKeys.value.length >= 2) {
    calculateCorrelations()
  }

  message.success('数据分析完成')
}

const calculateCorrelations = () => {
  const numberKeys = currentDataKeys.value
    .map((key, index) => ({ key, index }))
    .filter(({ key }) => {
      const value = getCurrentKeyValue(key)
      return key.type === 'number' && value !== '-'
    })

  if (numberKeys.length < 2) return

  for (let i = 0; i < numberKeys.length; i++) {
    const result = analysisResults.value.find(r => r.keyPath === numberKeys[i].key.path)
    if (!result) continue

    result.correlations = []

    for (let j = 0; j < numberKeys.length; j++) {
      if (i === j) continue

      result.correlations.push({
        key: numberKeys[j].key.label,
        coefficient: '1.00'
      })
    }
  }
}

const getCorrelationClass = (coefficient) => {
  const absValue = Math.abs(parseFloat(coefficient))
  if (absValue >= 0.7) return 'text-success font-weight-bold'
  if (absValue >= 0.4) return 'text-warning'
  return 'text-medium-emphasis'
}

const exportAnalysisResults = () => {
  const exportData = {
    topic: keyManagerTopic.value,
    timestamp: new Date().toISOString(),
    dataKeys: currentDataKeys.value,
    analysisResults: analysisResults.value
  }

  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `analysis-${keyManagerTopic.value}-${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)

  message.success('分析结果已导出')
}

const saveParseRules = () => {
  const topicConfig = topicConfigs.value.find(c => c.topic_name === keyManagerTopic.value)
  if (!topicConfig) {
    message.error('未找到Topic配置')
    return
  }

  const parseRules = {}
  currentDataKeys.value.forEach(key => {
    parseRules[key.path] = {
      label: key.label,
      path: key.path,
      type: key.type,
      unit: key.unit,
      formatter: key.formatter,
      customFormatter: key.customFormatter
    }
  })

  topicConfig.parse_rules = parseRules

  message.success('解析规则已保存')
  closeDataKeyDialog()
}

const closeDataKeyDialog = () => {
  dataKeyDialogVisible.value = false
  keyManagerTopic.value = ''
  parsedJsonData.value = null
  currentDataKeys.value = []
  showDataKeyForm.value = false
  editingDataKeyIndex.value = -1
  selectedKeyIndex.value = -1
  validationPanelModel.value = null
  analysisResults.value = []
}
</script>
