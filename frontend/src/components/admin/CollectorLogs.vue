<template>
  <div>
    <!-- Action bar -->
    <v-toolbar flat color="transparent" class="mb-4">
      <div>
        <div class="text-h5 font-weight-bold d-flex align-center ga-2">
          <v-icon icon="mdi-file-document-outline" color="primary" />
          采集日志
        </div>
        <div class="text-caption text-medium-emphasis mt-1">
          首页 / 采集日志
        </div>
      </div>
      <v-spacer />
      <v-btn color="error" prepend-icon="mdi-delete-sweep" @click="showClearDialog = true">
        清除旧日志
      </v-btn>
    </v-toolbar>

    <!-- Stats cards -->
    <v-row class="mb-4" dense>
      <v-col cols="12" sm="6" md="3">
        <v-card>
          <v-card-text class="d-flex align-center ga-3">
            <v-icon icon="mdi-database" size="40" color="info" />
            <div>
              <div class="text-h6 font-weight-bold">{{ logStats.total }}</div>
              <div class="text-caption text-medium-emphasis">总日志数</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card>
          <v-card-text class="d-flex align-center ga-3">
            <v-icon icon="mdi-alert-circle" size="40" color="error" />
            <div>
              <div class="text-h6 font-weight-bold">{{ logStats.error_count }}</div>
              <div class="text-caption text-medium-emphasis">错误数</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card>
          <v-card-text class="d-flex align-center ga-3">
            <v-icon icon="mdi-alert" size="40" color="warning" />
            <div>
              <div class="text-h6 font-weight-bold">{{ logStats.warning_count }}</div>
              <div class="text-caption text-medium-emphasis">警告数</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card>
          <v-card-text class="d-flex align-center ga-3">
            <v-icon icon="mdi-information" size="40" color="success" />
            <div>
              <div class="text-h6 font-weight-bold">{{ (logStats.by_level || {})['INFO'] || 0 }}</div>
              <div class="text-caption text-medium-emphasis">信息数</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Search card -->
    <v-card class="mb-4">
      <v-card-title class="d-flex align-center ga-2 cursor-pointer" @click="showSearch = !showSearch">
        <v-icon icon="mdi-filter" />
        查询条件
        <v-spacer />
        <v-btn variant="text" :icon="showSearch ? 'mdi-chevron-up' : 'mdi-chevron-down'" size="small" />
      </v-card-title>
      <v-divider v-if="showSearch" />
      <v-card-text v-if="showSearch">
        <v-form @submit.prevent="loadLogs">
          <v-row dense>
            <v-col cols="12" sm="6" md="3">
              <v-select
                v-model="filters.log_level"
                :items="logLevelOptions"
                label="日志级别"
                placeholder="请选择"
                clearable
                density="compact"
              />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-select
                v-model="filters.log_type"
                :items="logTypeOptions"
                label="日志类型"
                placeholder="请选择"
                clearable
                density="compact"
              />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-text-field
                v-model="filters.topic_name"
                label="Topic 名称"
                placeholder="请输入 Topic 名称"
                clearable
                density="compact"
                @keyup.enter="loadLogs"
              />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-text-field
                v-model="filters.start_time"
                label="开始时间"
                type="datetime-local"
                clearable
                density="compact"
                @change="onStartTimeChange"
              />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-text-field
                v-model="filters.end_time"
                label="结束时间"
                type="datetime-local"
                clearable
                density="compact"
                @change="onEndTimeChange"
              />
            </v-col>
            <v-col cols="12" sm="6" md="3" class="d-flex align-center ga-2">
              <v-btn color="primary" prepend-icon="mdi-magnify" @click="loadLogs">查询</v-btn>
              <v-btn variant="outlined" prepend-icon="mdi-undo" @click="resetFilters">重置</v-btn>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- Quick actions -->
    <div class="d-flex ga-2 mb-4">
      <v-btn variant="tonal" color="error" prepend-icon="mdi-alert-circle" @click="loadRecentErrors">
        查看最近错误
      </v-btn>
      <v-btn variant="tonal" color="info" prepend-icon="mdi-calendar-today" @click="loadTodayLogs">
        今日日志
      </v-btn>
    </div>

    <!-- Data table -->
    <v-card>
      <v-card-title class="d-flex align-center ga-2">
        <v-icon icon="mdi-format-list-bulleted" />
        日志列表
        <v-spacer />
        <v-btn variant="outlined" prepend-icon="mdi-refresh" size="small" @click="loadLogs">刷新</v-btn>
      </v-card-title>
      <v-data-table
        :headers="headers"
        :items="logs"
        :loading="loading"
        :items-per-page="pagination.pageSize"
        :page="pagination.page"
        :server-items-length="pagination.total"
        @update:page="p => { pagination.page = p; loadLogs() }"
        @update:items-per-page="s => { pagination.pageSize = s; loadLogs() }"
        hover
      >
        <template v-slot:item.log_level="{ item }">
          <v-chip :color="getLogLevelColor(item.log_level)" size="small" variant="tonal">
            {{ item.log_level }}
          </v-chip>
        </template>
        <template v-slot:item.db_operation="{ item }">
          <v-chip v-if="item.db_operation" size="small" variant="tonal" color="grey">
            {{ item.db_operation }}
          </v-chip>
        </template>
        <template v-slot:item.execution_time_ms="{ item }">
          <span v-if="item.execution_time_ms" :class="getExecutionTimeClass(item.execution_time_ms)">
            {{ item.execution_time_ms }}ms
          </span>
        </template>
        <template v-slot:item.created_at="{ item }">
          {{ formatDateTime(item.created_at) }}
        </template>
        <template v-slot:item.actions="{ item }">
          <div class="d-flex ga-1">
            <v-btn icon variant="text" size="small" @click="viewDetail(item)">
              <v-icon icon="mdi-eye" size="small" />
              <v-tooltip activator="parent" location="top">详情</v-tooltip>
            </v-btn>
          </div>
        </template>
        <template v-slot:no-data>
          <div class="text-center pa-8">
            <v-icon icon="mdi-inbox" size="48" color="grey-lighten-1" />
            <p class="text-medium-emphasis mt-2">暂无日志数据</p>
          </div>
        </template>
      </v-data-table>
    </v-card>

    <!-- Detail Dialog -->
    <v-dialog v-model="showDetailDialog" max-width="900">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-file-document-outline" class="mr-2" />
          日志详情
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="showDetailDialog = false" />
        </v-card-title>
        <v-divider />
        <v-card-text v-if="currentLog">
          <v-table density="compact">
            <tbody>
              <tr><td class="text-medium-emphasis" style="width:120px">ID</td><td>{{ currentLog.id }}</td></tr>
              <tr>
                <td class="text-medium-emphasis">级别</td>
                <td><v-chip :color="getLogLevelColor(currentLog.log_level)" size="small" variant="tonal">{{ currentLog.log_level }}</v-chip></td>
              </tr>
              <tr><td class="text-medium-emphasis">类型</td><td>{{ currentLog.log_type }}</td></tr>
              <tr><td class="text-medium-emphasis">Topic</td><td>{{ currentLog.topic_name }}</td></tr>
              <tr><td class="text-medium-emphasis">消息 ID</td><td>{{ currentLog.message_id }}</td></tr>
              <tr><td class="text-medium-emphasis">DB 操作</td><td>{{ currentLog.db_operation }}</td></tr>
              <tr><td class="text-medium-emphasis">表名</td><td>{{ currentLog.table_name }}</td></tr>
              <tr><td class="text-medium-emphasis">影响行数</td><td>{{ currentLog.affected_rows }}</td></tr>
              <tr><td class="text-medium-emphasis">执行时间</td><td>{{ currentLog.execution_time_ms }}ms</td></tr>
              <tr><td class="text-medium-emphasis">创建时间</td><td>{{ formatDateTime(currentLog.created_at) }}</td></tr>
              <tr v-if="currentLog.summary">
                <td class="text-medium-emphasis">日志摘要</td>
                <td><div class="text-body-2" style="white-space: pre-wrap;">{{ currentLog.summary }}</div></td>
              </tr>
              <tr v-if="currentLog.error_message">
                <td class="text-medium-emphasis">错误信息</td>
                <td><div class="text-body-2 text-error" style="white-space: pre-wrap;">{{ currentLog.error_message }}</div></td>
              </tr>
            </tbody>
          </v-table>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showDetailDialog = false">关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Clear Logs Dialog -->
    <v-dialog v-model="showClearDialog" max-width="500" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-delete-sweep" class="mr-2" color="error" />
          清除旧日志
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="showClearDialog = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-form>
            <v-number-input
              v-model.number="clearDays"
              label="清除天数"
              :min="1"
              :max="365"
              controlVariant="stacked"
            />
            <div class="text-caption text-medium-emphasis mt-1">天前的日志</div>
          </v-form>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showClearDialog = false">取消</v-btn>
          <v-btn color="error" :loading="clearing" @click="confirmClearLogs">确定清除</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useMessage, useConfirm } from '@/composables/useMessage'
import { collectorLogAPI } from '@/api'
import { formatDateTime } from '@/utils/datetime'

const message = useMessage()
const confirmDialog = useConfirm()

const showSearch = ref(true)

const logLevelOptions = [
  { title: 'DEBUG', value: 'DEBUG' },
  { title: 'INFO', value: 'INFO' },
  { title: 'WARNING', value: 'WARNING' },
  { title: 'ERROR', value: 'ERROR' },
]

const logTypeOptions = [
  { title: 'MESSAGE_RECEIVED', value: 'MESSAGE_RECEIVED' },
  { title: 'DATA_STORED', value: 'DATA_STORED' },
  { title: 'DATA_TRANSFORMED', value: 'DATA_TRANSFORMED' },
  { title: 'ERROR', value: 'ERROR' },
  { title: 'SYSTEM', value: 'SYSTEM' },
]

const headers = [
  { title: 'ID', key: 'id', width: '80px' },
  { title: '级别', key: 'log_level', width: '100px' },
  { title: '类型', key: 'log_type', width: '150px' },
  { title: 'Topic 名称', key: 'topic_name', minWidth: '180px' },
  { title: 'DB 操作', key: 'db_operation', width: '100px' },
  { title: '执行时间', key: 'execution_time_ms', width: '100px' },
  { title: '错误信息', key: 'error_message', minWidth: '200px' },
  { title: '时间', key: 'created_at', width: '180px' },
  { title: '操作', key: 'actions', sortable: false, width: '100px' },
]

// 数据
const loading = ref(false)
const clearing = ref(false)
const logs = ref([])
const logStats = ref({
  total: 0,
  by_level: {},
  by_type: {},
  error_count: 0,
  warning_count: 0
})

const filters = reactive({
  log_level: '',
  log_type: '',
  topic_name: '',
  start_time: null,
  end_time: null
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const showDetailDialog = ref(false)
const showClearDialog = ref(false)
const currentLog = ref(null)
const clearDays = ref(30)

// 方法
const onStartTimeChange = (value) => {
  filters.start_time = value ? new Date(value).toISOString() : null
}

const onEndTimeChange = (value) => {
  filters.end_time = value ? new Date(value).toISOString() : null
}

const loadLogs = async () => {
  try {
    loading.value = true

    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }

    if (filters.log_level) params.log_level = filters.log_level
    if (filters.log_type) params.log_type = filters.log_type
    if (filters.topic_name) params.topic_name = filters.topic_name
    if (filters.start_time) params.start_time = filters.start_time
    if (filters.end_time) params.end_time = filters.end_time

    const response = await collectorLogAPI.getCollectorLogs(params)
    const res = response.data

    logs.value = res.items || []
    pagination.total = res.total || 0

    // 加载统计
    loadStats()

  } catch (error) {
    console.error('加载日志失败:', error)
    message.error('加载失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const params = {}
    if (filters.start_time && filters.end_time) {
      const days = Math.ceil((new Date(filters.end_time) - new Date(filters.start_time)) / (1000 * 60 * 60 * 24))
      params.days = Math.min(days, 30)
    }

    const response = await collectorLogAPI.getLogStats(params)
    const res = response.data
    logStats.value = res
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

const resetFilters = () => {
  filters.log_level = ''
  filters.log_type = ''
  filters.topic_name = ''
  filters.start_time = null
  filters.end_time = null
  pagination.page = 1
  loadLogs()
}

const loadRecentErrors = async () => {
  try {
    loading.value = true
    const response = await collectorLogAPI.getRecentErrors(50)
    const res = response.data
    logs.value = res.items || []
    pagination.total = res.total || 0
    message.success(`加载了 ${logs.value.length} 条错误日志`)
  } catch (error) {
    console.error('加载错误日志失败:', error)
    message.error('加载失败：' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const loadTodayLogs = () => {
  const now = new Date()
  const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate())

  filters.start_time = startOfDay.toISOString()
  filters.end_time = now.toISOString()
  pagination.page = 1
  loadLogs()
}

const viewDetail = (row) => {
  currentLog.value = row
  showDetailDialog.value = true
}

const confirmClearLogs = async () => {
  try {
    clearing.value = true

    const ok = await confirmDialog(`确定要清除 ${clearDays.value} 天前的所有日志吗？此操作不可恢复！`, '确认清除', 'warning')
    if (!ok) return

    await collectorLogAPI.clearOldLogs(clearDays.value)
    message.success('清除成功')
    showClearDialog.value = false
    loadLogs()

  } catch (error) {
    console.error('清除失败:', error)
    message.error('清除失败：' + (error.response?.data?.detail || error.message))
  } finally {
    clearing.value = false
  }
}

const getLogLevelColor = (level) => {
  const colors = {
    'DEBUG': 'grey',
    'INFO': 'success',
    'WARNING': 'warning',
    'ERROR': 'error'
  }
  return colors[level] || 'grey'
}

const getExecutionTimeClass = (time) => {
  if (time < 100) return 'text-success'
  if (time < 500) return 'text-warning'
  return 'text-error'
}

// 生命周期
onMounted(() => {
  loadLogs()
})
</script>
