<template>
  <div>
    <!-- Action bar -->
    <v-toolbar flat color="transparent" class="mb-4">
      <div>
        <div class="text-h5 font-weight-bold d-flex align-center ga-2">
          <v-icon icon="mdi-harddisk" color="primary" />
          数据采集管理
        </div>
        <div class="text-caption text-medium-emphasis mt-1">
          首页 / 数据采集
        </div>
      </div>
      <v-spacer />
      <v-chip
        :color="collectorStatus.is_connected ? 'success' : 'error'"
        variant="tonal"
        size="small"
        class="mr-2"
      >
        <v-icon start :icon="collectorStatus.is_connected ? 'mdi-lan-connect' : 'mdi-lan-disconnect'" size="small" />
        {{ collectorStatus.is_connected ? 'MQTT 已连接' : 'MQTT 未连接' }}
      </v-chip>
      <v-btn
        v-if="!collectorStatus.is_running"
        color="primary"
        prepend-icon="mdi-play"
        :loading="loading"
        @click="startCollector"
      >
        启动采集
      </v-btn>
      <v-btn
        v-else
        color="error"
        prepend-icon="mdi-stop"
        :loading="loading"
        @click="stopCollector"
      >
        停止采集
      </v-btn>
    </v-toolbar>

    <!-- Tabs -->
    <v-tabs v-model="activeTab" class="mb-4">
      <v-tab value="overview">
        <v-icon start icon="mdi-gauge" />
        采集概览
      </v-tab>
      <v-tab value="topics">
        <v-icon start icon="mdi-broadcast" />
        Topic 配置
        <v-chip size="x-small" color="primary" class="ml-1">{{ topicStats.total || 0 }}</v-chip>
      </v-tab>
      <v-tab value="logs">
        <v-icon start icon="mdi-text-box-outline" />
        采集日志
        <v-chip v-if="unreadLogs > 0" size="x-small" color="error" class="ml-1">{{ unreadLogs }}</v-chip>
      </v-tab>
    </v-tabs>

    <!-- Overview tab -->
    <v-window v-model="activeTab">
      <v-window-item value="overview">
        <!-- Metric cards -->
        <v-row class="mb-4">
          <v-col cols="12" md="4">
            <v-card>
              <v-card-text class="d-flex align-center ga-4">
                <v-icon icon="mdi-signal" size="40" color="blue" />
                <div>
                  <div class="text-h5 font-weight-bold">{{ collectorStatus.messages_received?.toLocaleString() || '0' }}</div>
                  <div class="text-caption text-medium-emphasis">累计接收消息</div>
                  <div class="text-caption text-success mt-1">
                    <v-icon icon="mdi-arrow-up" size="x-small" /> 实时采集
                  </div>
                </div>
                <v-spacer />
                <v-btn icon variant="text" size="small" @click="refreshMetrics">
                  <v-icon icon="mdi-refresh" />
                  <v-tooltip activator="parent" location="top">刷新</v-tooltip>
                </v-btn>
              </v-card-text>
              <v-divider v-if="collectorStatus.last_message_time" />
              <v-card-actions v-if="collectorStatus.last_message_time" class="text-caption text-medium-emphasis px-4">
                最后消息：{{ formatTimeAgo(collectorStatus.last_message_time) }}
              </v-card-actions>
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card>
              <v-card-text class="d-flex align-center ga-4">
                <v-icon icon="mdi-database" size="40" color="purple" />
                <div>
                  <div class="text-h5 font-weight-bold">{{ rawDataStats.total_records?.toLocaleString() || '0' }}</div>
                  <div class="text-caption text-medium-emphasis">原始数据记录</div>
                  <div class="text-caption text-medium-emphasis mt-1">存储：{{ formatStorageSize(rawDataStats.total_size_bytes || 0) }}</div>
                </div>
              </v-card-text>
              <v-divider />
              <v-card-actions class="text-caption text-medium-emphasis px-4">
                压缩率：{{ rawDataStats.compression_rate || 0 }}%
              </v-card-actions>
            </v-card>
          </v-col>
          <v-col cols="12" md="4">
            <v-card>
              <v-card-text class="d-flex align-center ga-4">
                <v-icon icon="mdi-pulse" size="40" color="orange" />
                <div>
                  <div class="text-h5 font-weight-bold">{{ topicStats.active || '0' }}</div>
                  <div class="text-caption text-medium-emphasis">活跃 Topic</div>
                  <div class="text-caption text-medium-emphasis mt-1">总数：{{ topicStats.total || 0 }}</div>
                </div>
              </v-card-text>
              <v-divider />
              <v-card-actions class="text-caption text-medium-emphasis px-4">
                启用率：{{ getTopicActiveRate }}%
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>

        <!-- Collector config card -->
        <v-card class="mb-4">
          <v-card-title class="d-flex align-center ga-2">
            <v-icon icon="mdi-cog" />
            采集器配置
            <v-spacer />
            <v-btn variant="outlined" prepend-icon="mdi-pencil" size="small" @click="showConfigDialog = true">
              编辑配置
            </v-btn>
          </v-card-title>
          <v-divider />
          <v-card-text>
            <v-row>
              <v-col cols="12" md="4">
                <div class="text-caption text-medium-emphasis mb-1">
                  <v-icon icon="mdi-server" size="small" /> MQTT 服务器
                </div>
                <v-chip variant="tonal" color="primary">{{ config.mqtt_server }}</v-chip>
              </v-col>
              <v-col cols="12" md="4">
                <div class="text-caption text-medium-emphasis mb-1">
                  <v-icon icon="mdi-ethernet" size="small" /> 端口
                </div>
                <v-chip variant="tonal" color="primary">{{ config.mqtt_port }}</v-chip>
              </v-col>
              <v-col cols="12" md="4">
                <div class="text-caption text-medium-emphasis mb-1">
                  <v-icon icon="mdi-broadcast" size="small" /> 订阅主题
                </div>
                <div class="d-flex flex-wrap ga-1">
                  <v-chip v-for="topic in config.topics" :key="topic" size="small" variant="tonal" color="info">
                    {{ topic }}
                  </v-chip>
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-window-item>

      <!-- Topics tab -->
      <v-window-item value="topics">
        <!-- Topic stats -->
        <v-row class="mb-4">
          <v-col cols="6" md="3">
            <v-card><v-card-text class="text-center"><div class="text-h5 font-weight-bold text-blue">{{ topicStats.total || 0 }}</div><div class="text-caption text-medium-emphasis">总 Topic 数</div></v-card-text></v-card>
          </v-col>
          <v-col cols="6" md="3">
            <v-card><v-card-text class="text-center"><div class="text-h5 font-weight-bold text-green">{{ topicStats.active || 0 }}</div><div class="text-caption text-medium-emphasis">已启用</div></v-card-text></v-card>
          </v-col>
          <v-col cols="6" md="3">
            <v-card><v-card-text class="text-center"><div class="text-h5 font-weight-bold text-red">{{ topicStats.disabled || 0 }}</div><div class="text-caption text-medium-emphasis">已禁用</div></v-card-text></v-card>
          </v-col>
          <v-col cols="6" md="3">
            <v-card><v-card-text class="text-center"><div class="text-h5 font-weight-bold text-orange">{{ topicTypeStats?.length || 0 }}</div><div class="text-caption text-medium-emphasis">类型分布</div></v-card-text></v-card>
          </v-col>
        </v-row>

        <!-- Topic toolbar -->
        <v-card class="mb-4">
          <v-card-text>
            <v-row dense align="center">
              <v-col cols="12" md="4">
                <v-text-field v-model="topicSearchQuery" label="搜索 Topic" placeholder="搜索 Topic 名称或模式..." density="compact" clearable hide-details prepend-inner-icon="mdi-magnify" />
              </v-col>
              <v-col cols="12" md="3">
                <v-select v-model="topicFilterStatus" :items="[{title:'全部状态',value:''},{title:'已启用',value:'active'},{title:'已禁用',value:'disabled'}]" label="状态" density="compact" hide-details />
              </v-col>
              <v-col cols="12" md="5" class="d-flex justify-end">
                <v-btn color="primary" prepend-icon="mdi-plus" @click="showCreateTopicDialog">新建 Topic</v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Topic table -->
        <v-card>
          <v-data-table
            :headers="topicHeaders"
            :items="filteredTopicList"
            :loading="loading"
            :items-per-page="topicPageSize"
            :page="topicPage"
            :server-items-length="topicTotal"
            @update:page="p => { topicPage = p; loadTopicConfigs() }"
            @update:items-per-page="s => { topicPageSize = s; loadTopicConfigs() }"
            hover
          >
            <template v-slot:item.id="{ item }">
              <span class="text-medium-emphasis">#{{ item.id }}</span>
            </template>
            <template v-slot:item.topic_type="{ item }">
              <v-chip size="small" variant="tonal" :color="item.topic_type === 'event' ? 'blue' : item.topic_type === 'pv_compress' ? 'green' : item.topic_type === 'sv_compress' ? 'purple' : item.topic_type === 'alarm_compress' ? 'red' : 'grey'">
                {{ item.topic_type || 'custom' }}
              </v-chip>
            </template>
            <template v-slot:item.device_code="{ item }">
              <div v-if="item.device_code">
                <v-chip size="small" variant="tonal" color="primary" prepend-icon="mdi-cpu-64-bit">{{ item.device_code }}</v-chip>
                <div class="text-caption text-medium-emphasis">{{ item.device_name }}</div>
              </div>
              <span v-else class="text-medium-emphasis">-</span>
            </template>
            <template v-slot:item.qos="{ item }">
              <v-chip size="small" variant="tonal">{{ item.qos ?? 1 }}</v-chip>
            </template>
            <template v-slot:item.storage_policy="{ item }">
              <v-chip size="small" variant="tonal" color="info">{{ item.storage_policy || 'save_raw' }}</v-chip>
            </template>
            <template v-slot:item.enabled="{ item }">
              <v-switch v-model="item.enabled" :true-value="true" :false-value="false" @update:modelValue="toggleTopicStatus(item)" density="compact" hide-details color="primary" />
            </template>
            <template v-slot:item.updated_at="{ item }">
              {{ formatDateTime(item.updated_at) }}
            </template>
            <template v-slot:item.actions="{ item }">
              <div class="d-flex ga-1">
                <v-btn icon variant="text" size="small" @click="editTopic(item)">
                  <v-icon icon="mdi-pencil" size="small" />
                  <v-tooltip activator="parent" location="top">编辑</v-tooltip>
                </v-btn>
                <v-btn icon variant="text" size="small" color="error" @click="deleteTopic(item)">
                  <v-icon icon="mdi-delete" size="small" />
                  <v-tooltip activator="parent" location="top">删除</v-tooltip>
                </v-btn>
              </div>
            </template>
            <template v-slot:no-data>
              <div class="text-center pa-8">
                <v-icon icon="mdi-inbox" size="48" color="grey-lighten-1" />
                <p class="text-medium-emphasis mt-2">暂无 Topic 配置</p>
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-window-item>

      <!-- Logs tab -->
      <v-window-item value="logs">
        <CollectorLogs />
      </v-window-item>
    </v-window>

    <!-- Topic create/edit dialog -->
    <v-dialog v-model="showTopicDialog" max-width="800" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon :icon="isEditMode ? 'mdi-pencil' : 'mdi-plus'" class="mr-2" />
          {{ isEditMode ? '编辑 Topic 配置' : '新建 Topic 配置' }}
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="showTopicDialog = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-form ref="topicFormRef">
            <v-text-field v-model="topicForm.topic_name" label="Topic 名称" placeholder="例如：SHXQ/NO1/KP3/IMG/PV" :rules="[v => !!v || '请输入 Topic 名称']" required />
            <div class="text-caption text-medium-emphasis mb-2">Topic 名称必须唯一，用于精确匹配 MQTT 消息</div>
            <v-textarea v-model="topicForm.description" label="描述信息" rows="2" placeholder="描述该 Topic 的用途和特点" />
            <v-select v-model="topicForm.topic_type" :items="[{title:'加工事件 (Event)',value:'event'},{title:'PV 压缩',value:'pv_compress'},{title:'SV 压缩',value:'sv_compress'},{title:'ALARM 压缩',value:'alarm_compress'},{title:'自定义',value:'custom'}]" label="Topic 类型" />
            <div class="text-caption text-medium-emphasis mb-2">Event 类型数据保存到 event_data 表，压缩类型分别保存到对应的分表</div>
            <v-select v-model="topicForm.device_code" :items="deviceList.map(d => ({title: `${d.device_code} - ${d.device_name}`, value: d.device_code}))" label="关联设备" clearable placeholder="请选择关联设备（可选）" />
            <div class="text-caption text-medium-emphasis mb-2">可选项，关联此 Topic 对应的设备编号</div>
            <v-number-input v-model.number="topicForm.qos" label="QoS 级别" :min="0" :max="2" controlVariant="stacked" />
            <div class="text-caption text-medium-emphasis mb-2">MQTT QoS 级别：0-最多一次，1-至少一次，2-恰好一次</div>
            <v-select v-model="topicForm.storage_policy" :items="[{title:'保存原始数据 (save_raw)',value:'save_raw'},{title:'保存解析数据 (save_parsed)',value:'save_parsed'},{title:'保存全部 (save_all)',value:'save_all'}]" label="存储策略" />
            <v-switch v-model="topicForm.enabled" label="是否启用" color="primary" />
          </v-form>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showTopicDialog = false">取消</v-btn>
          <v-btn color="primary" :loading="saving" @click="saveTopicConfig">
            {{ isEditMode ? '保存' : '创建' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Topic fields dialog -->
    <v-dialog v-model="showFieldsDialog" max-width="1000">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-format-list-bulleted" class="mr-2" />
          Topic 字段定义 - {{ currentTopic?.topic_name }}
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="showFieldsDialog = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <div v-if="currentTopicFields.length > 0">
            <v-card v-for="field in currentTopicFields" :key="field.id" variant="outlined" class="mb-2">
              <v-card-text>
                <div class="d-flex align-center ga-2 mb-2">
                  <span class="font-weight-bold">{{ field.field_name }}</span>
                  <v-chip v-if="field.is_required" size="x-small" color="error" variant="tonal">必填</v-chip>
                  <v-chip size="x-small" variant="tonal" color="primary">{{ field.data_type }}</v-chip>
                  <v-chip v-if="field.transform_type" size="x-small" variant="tonal" color="success">
                    <v-icon start icon="mdi-arrow-right" size="x-small" /> {{ field.transform_type }}
                  </v-chip>
                  <v-chip v-if="field.validation_type" size="x-small" variant="tonal" color="warning">
                    <v-icon start icon="mdi-shield-check" size="x-small" /> {{ field.validation_type }}
                  </v-chip>
                </div>
                <div class="text-caption">映射列: {{ field.db_column_name }}</div>
                <div v-if="field.description" class="text-caption text-medium-emphasis">描述: {{ field.description }}</div>
                <div v-if="field.transform_params" class="text-caption text-medium-emphasis">转换参数: {{ JSON.stringify(field.transform_params) }}</div>
                <div v-if="field.validation_params" class="text-caption text-medium-emphasis">验证参数: {{ JSON.stringify(field.validation_params) }}</div>
              </v-card-text>
            </v-card>
          </div>
          <div v-else class="text-center pa-8">
            <v-icon icon="mdi-inbox" size="48" color="grey-lighten-1" />
            <p class="text-medium-emphasis mt-2">该 Topic 暂无字段定义</p>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useMessage, useConfirm } from '@/composables/useMessage'
import CollectorLogs from './CollectorLogs.vue'
import {
  getCollectorStats,
  startCollectorService,
  stopCollectorService,
  getTopicConfigs,
  createTopicConfig,
  updateTopicConfig,
  deleteTopicConfig
} from '@/api/dataCollector'
import axios from 'axios'
import { formatDateTime } from '@/utils/datetime'

const message = useMessage()
const confirmDialog = useConfirm()

// 状态
const loading = ref(false)
const saving = ref(false)
const activeTab = ref('overview')
const unreadLogs = ref(0)
const showConfigDialog = ref(false)

// 采集器状态
const collectorStatus = reactive({
  is_connected: false,
  is_running: false,
  messages_received: 0,
  last_message_time: null as string | null
})

// 配置
const config = reactive({
  mqtt_server: 'localhost',
  mqtt_port: 1883,
  topics: [] as string[]
})

const rawDataStats = reactive({
  total_records: 0,
  total_size_bytes: 0,
  compression_rate: 0,
  topic_distribution: [] as any[]
})

const topicStats = reactive({
  total: 0,
  active: 0,
  disabled: 0
})

const topicTypeStats = ref<any[]>([])

// Topic table headers
const topicHeaders = [
  { title: 'ID', key: 'id', width: '70px' },
  { title: 'Topic 名称', key: 'topic_name' },
  { title: '关联设备', key: 'device_code' },
  { title: '类型', key: 'topic_type' },
  { title: '描述', key: 'description' },
  { title: 'QoS', key: 'qos', width: '70px' },
  { title: '存储策略', key: 'storage_policy' },
  { title: '状态', key: 'enabled', width: '80px' },
  { title: '更新时间', key: 'updated_at' },
  { title: '操作', key: 'actions', sortable: false, width: '100px' },
]

// Topic 列表
const topicPage = ref(1)
const topicPageSize = ref(20)
const topicTotal = ref(0)
const topicList = ref<any[]>([])
const topicSearchQuery = ref('')
const topicFilterStatus = ref('')

// 设备列表
const deviceList = ref<any[]>([])

// 对话框
const showTopicDialog = ref(false)
const showFieldsDialog = ref(false)
const isEditMode = ref(false)
const currentTopic = ref<any>(null)
const currentTopicFields = ref<any[]>([])

const topicFormRef = ref()
const topicForm = reactive({
  topic_name: '',
  description: '',
  topic_type: 'custom',
  enabled: true,
  qos: 1,
  storage_policy: 'save_raw',
  parse_rules: null,
  device_code: null as string | null
})

const topicFormRules = {
  topic_name: [
    { required: true, message: '请输入 Topic 名称', trigger: 'blur' }
  ]
}

// 计算属性
const getTopicActiveRate = computed(() => {
  if (!topicStats.total) return 0
  return Math.round((topicStats.active / topicStats.total) * 100)
})

const filteredTopicList = computed(() => {
  let filtered = [...topicList.value]

  if (topicSearchQuery.value) {
    const query = topicSearchQuery.value.toLowerCase()
    filtered = filtered.filter(item =>
      item.topic_name.toLowerCase().includes(query) ||
      (item.description && item.description.toLowerCase().includes(query))
    )
  }

  if (topicFilterStatus.value === 'active') {
    filtered = filtered.filter(item => item.enabled)
  } else if (topicFilterStatus.value === 'disabled') {
    filtered = filtered.filter(item => !item.enabled)
  }

  return filtered
})

// 方法
const formatTimeAgo = (dateString: string | null) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)

  if (hours > 0) return `${hours}小时前`
  if (minutes > 0) return `${minutes}分钟前`
  return '刚刚'
}

const formatStorageSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

const getTopicColor = (index: number) => {
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#40C9C6', '#F09A7C', '#A385F4']
  return colors[index % colors.length]
}

const getPriorityClass = (priority: number) => {
  if (priority >= 80) return 'priority-high'
  if (priority >= 50) return 'priority-medium'
  return 'priority-low'
}

const refreshMetrics = async () => {
  await loadCollectorStats()
  message.success('统计已刷新')
}

const loadCollectorStats = async () => {
  try {
    const res = await getCollectorStats()
    if (res.data) {
      Object.assign(collectorStatus, {
        is_connected: res.data.is_connected,
        is_running: res.data.is_running,
        messages_received: res.data.messages_received,
        last_message_time: res.data.last_message_time
      })
      Object.assign(config, {
        mqtt_server: res.data.mqtt_server,
        mqtt_port: res.data.mqtt_port,
        topics: res.data.topics || []
      })
    }
  } catch (error) {
    console.error('加载采集器状态失败:', error)
  }
}

const startCollector = async () => {
  try {
    loading.value = true
    await startCollectorService()
    message.success('采集器已启动')
    await loadCollectorStats()
  } catch (error: any) {
    message.error('启动失败：' + error.message)
  } finally {
    loading.value = false
  }
}

const stopCollector = async () => {
  try {
    loading.value = true
    await stopCollectorService()
    message.success('采集器已停止')
    await loadCollectorStats()
  } catch (error: any) {
    message.error('停止失败：' + error.message)
  } finally {
    loading.value = false
  }
}

const loadTopicConfigs = async () => {
  try {
    const params = {
      page: topicPage.value,
      page_size: topicPageSize.value
    }

    if (topicFilterStatus.value === 'active') {
      params.enabled = true
    } else if (topicFilterStatus.value === 'disabled') {
      params.enabled = false
    }

    const res = await getTopicConfigs(params)
    if (res.data) {
      topicList.value = res.data.items || []
      topicTotal.value = res.data.total || 0

      // 更新统计信息
      topicStats.total = res.data.total || 0
      topicStats.active = (res.data.items || []).filter(item => item.enabled).length
      topicStats.disabled = topicStats.total - topicStats.active
    }
  } catch (error) {
    console.error('加载 Topic 配置失败:', error)
    message.error('加载 Topic 配置失败')
  }
}

const showCreateTopicDialog = () => {
  isEditMode.value = false
  Object.assign(topicForm, {
    topic_name: '',
    description: '',
    topic_type: 'custom',
    enabled: true,
    qos: 1,
    storage_policy: 'save_raw',
    parse_rules: null,
    device_code: null
  })
  topicFormRef.value?.clearValidate()
  showTopicDialog.value = true
}

const editTopic = (topic: any) => {
  isEditMode.value = true
  currentTopic.value = topic
  Object.assign(topicForm, {
    topic_name: topic.topic_name,
    description: topic.description || '',
    topic_type: topic.topic_type || 'custom',
    enabled: topic.enabled,
    qos: topic.qos || 1,
    storage_policy: topic.storage_policy || 'save_raw',
    parse_rules: topic.parse_rules || null,
    device_code: topic.device_code || null
  })
  showTopicDialog.value = true
}

const saveTopicConfig = async () => {
  try {
    await topicFormRef.value?.validate()
    saving.value = true

    if (isEditMode.value && currentTopic.value) {
      await updateTopicConfig(currentTopic.value.id, topicForm)
      message.success('Topic 配置更新成功')
    } else {
      await createTopicConfig(topicForm)
      message.success('Topic 配置创建成功')
    }

    showTopicDialog.value = false
    await loadTopicConfigs()
  } catch (error: any) {
    if (error.response?.data?.detail) {
      message.error(error.response.data.detail)
    } else {
      message.error('保存失败')
    }
  } finally {
    saving.value = false
  }
}

const toggleTopicStatus = async (topic: any) => {
  try {
    await updateTopicConfig(topic.id, { enabled: topic.enabled })
    message.success(`Topic 已${topic.enabled ? '启用' : '禁用'}`)
    await loadTopicConfigs()
  } catch (error) {
    topic.enabled = !topic.enabled
    message.error('状态更新失败')
  }
}

const viewTopicFields = async (topic: any) => {
  currentTopic.value = topic
  currentTopicFields.value = []
  showFieldsDialog.value = true
}

const deleteTopic = async (topic: any) => {
  try {
    const ok = await confirmDialog(`确定要删除 Topic "${topic.topic_name}" 吗？此操作不可恢复。`, '确认删除', 'warning')
    if (!ok) return

    await deleteTopicConfig(topic.id)
    message.success('Topic 配置已删除')
    await loadTopicConfigs()
  } catch (error: any) {
    message.error('删除失败')
  }
}

const loadDeviceList = async () => {
  try {
    const res = await axios.get('/api/devices/', {
      params: { page: 1, page_size: 1000 }
    })
    if (res.data) {
      deviceList.value = res.data.items || []
    }
  } catch (error) {
    console.error('加载设备列表失败:', error)
  }
}

// 生命周期
onMounted(async () => {
  await loadCollectorStats()
  await loadTopicConfigs()
  await loadDeviceList()

  // 定时刷新
  setInterval(async () => {
    if (collectorStatus.is_running) {
      await loadCollectorStats()
    }
  }, 30000)
})
</script>
