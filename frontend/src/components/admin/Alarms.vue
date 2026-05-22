<template>
  <div>
    <!-- Action bar -->
    <v-toolbar flat color="transparent" class="mb-4">
      <div>
        <div class="text-h5 font-weight-bold d-flex align-center ga-2">
          <v-icon icon="mdi-bell" color="primary" />
          报警管理
        </div>
        <div class="text-caption text-medium-emphasis mt-1">
          首页 / 报警管理
        </div>
      </div>
      <v-spacer />
      <v-btn color="success" prepend-icon="mdi-check-circle" :disabled="selectedIds.length === 0" @click="handleBatchResolve" class="mr-2">
        批量处理
      </v-btn>
      <v-btn variant="outlined" prepend-icon="mdi-delete" @click="showClearDialog = true">
        清理历史
      </v-btn>
    </v-toolbar>

    <!-- Metrics -->
    <v-row class="mb-4" dense>
      <v-col cols="12" md="3">
        <v-card>
          <v-card-text>
            <div class="d-flex align-center ga-3">
              <v-icon icon="mdi-bell" size="36" color="error" />
              <div>
                <div class="text-h5 font-weight-bold">{{ alarmStats.total?.toLocaleString() || '0' }}</div>
                <div class="text-caption text-medium-emphasis">报警总数</div>
                <div class="text-caption">严重：{{ alarmStats.critical || 0 }} | 警告：{{ alarmStats.warning || 0 }}</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card>
          <v-card-text>
            <div class="d-flex align-center ga-3">
              <v-icon icon="mdi-alert-circle" size="36" color="warning" />
              <div>
                <div class="text-h5 font-weight-bold">{{ alarmStats.pending || '0' }}</div>
                <div class="text-caption text-medium-emphasis">待处理</div>
                <div class="text-caption text-warning">需要处理</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card>
          <v-card-text>
            <div class="d-flex align-center ga-3">
              <v-icon icon="mdi-wrench" size="36" color="info" />
              <div>
                <div class="text-h5 font-weight-bold">{{ alarmStats.processing || '0' }}</div>
                <div class="text-caption text-medium-emphasis">处理中</div>
                <div class="text-caption text-info">正在处理</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card>
          <v-card-text>
            <div class="d-flex align-center ga-3">
              <v-icon icon="mdi-check-circle" size="36" color="success" />
              <div>
                <div class="text-h5 font-weight-bold">{{ alarmStats.resolved || '0' }}</div>
                <div class="text-caption text-medium-emphasis">已解决</div>
                <div class="text-caption text-success">已完成</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Search Card -->
    <v-card class="mb-4">
      <v-card-title class="d-flex align-center ga-2 cursor-pointer" @click="showSearch = !showSearch">
        <v-icon icon="mdi-filter" />
        查询条件
        <v-spacer />
        <v-btn variant="text" :icon="showSearch ? 'mdi-chevron-up' : 'mdi-chevron-down'" size="small" />
      </v-card-title>
      <v-divider v-if="showSearch" />
      <v-card-text v-if="showSearch">
        <v-form @submit.prevent="loadAlarms">
          <v-row dense>
            <v-col cols="12" sm="6" md="2">
              <v-text-field v-model="searchQuery.alarm_code" label="报警编号" placeholder="搜索报警编号..." clearable density="compact" @keyup.enter="loadAlarms" />
            </v-col>
            <v-col cols="12" sm="6" md="2">
              <v-text-field v-model="searchQuery.device_code" label="设备编号" placeholder="搜索设备编号..." clearable density="compact" @keyup.enter="loadAlarms" />
            </v-col>
            <v-col cols="12" sm="6" md="2">
              <v-select v-model="searchQuery.alarm_level" :items="levelOptions" label="报警级别" clearable density="compact" @update:model-value="loadAlarms" />
            </v-col>
            <v-col cols="12" sm="6" md="2">
              <v-select v-model="searchQuery.status" :items="statusFilterOptions" label="报警状态" clearable density="compact" @update:model-value="loadAlarms" />
            </v-col>
            <v-col cols="12" sm="6" md="2">
              <v-text-field v-model="searchQuery.start_date" label="开始日期" type="date" density="compact" @change="loadAlarms" />
            </v-col>
            <v-col cols="12" sm="6" md="2" class="d-flex align-center ga-2">
              <v-btn variant="outlined" prepend-icon="mdi-undo" @click="resetSearch">重置</v-btn>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- Data Table -->
    <v-card>
      <v-data-table
        :headers="headers"
        :items="alarmList"
        :loading="loading"
        :items-per-page="pageSize"
        :page="page"
        :server-items-length="total"
        @update:page="p => { page = p; loadAlarms() }"
        @update:items-per-page="s => { pageSize = s; loadAlarms() }"
        show-select
        v-model="selectedIds"
        item-value="id"
        hover
      >
        <template v-slot:item.alarm_code="{ item }">
          <v-chip size="small" variant="tonal" color="primary">{{ item.alarm_code }}</v-chip>
        </template>
        <template v-slot:item.alarm_level="{ item }">
          <v-chip :color="levelColor(item.alarm_level)" size="small" variant="tonal">
            {{ getLevelText(item.alarm_level) }}
          </v-chip>
        </template>
        <template v-slot:item.title="{ item }">
          <div>{{ item.title }}</div>
          <div v-if="item.description" class="text-caption text-medium-emphasis">{{ item.description }}</div>
        </template>
        <template v-slot:item.alarm_value="{ item }">
          <span v-if="item.alarm_value">{{ item.alarm_value }} / {{ item.threshold_value || '-' }}</span>
          <span v-else class="text-medium-emphasis">-</span>
        </template>
        <template v-slot:item.status="{ item }">
          <v-chip :color="statusColor(item.status)" size="small" variant="tonal">
            {{ getStatusText(item.status) }}
          </v-chip>
        </template>
        <template v-slot:item.alarm_time="{ item }">
          {{ formatDateTime(item.alarm_time) }}
        </template>
        <template v-slot:item.actions="{ item }">
          <div class="d-flex ga-1">
            <v-btn icon variant="text" size="small" @click="viewAlarm(item)">
              <v-icon icon="mdi-eye" size="small" />
              <v-tooltip activator="parent" location="top">查看详情</v-tooltip>
            </v-btn>
            <v-btn v-if="item.status === 'pending' || item.status === 'processing'" icon variant="text" size="small" color="success" @click="handleAlarm(item)">
              <v-icon icon="mdi-check" size="small" />
              <v-tooltip activator="parent" location="top">处理</v-tooltip>
            </v-btn>
            <v-btn icon variant="text" size="small" color="purple" @click="viewAlarmEvents(item)">
              <v-icon icon="mdi-cog-transfer" size="small" />
              <v-tooltip activator="parent" location="top">加工事件</v-tooltip>
            </v-btn>
            <v-btn icon variant="text" size="small" color="error" @click="deleteAlarm(item)">
              <v-icon icon="mdi-delete" size="small" />
              <v-tooltip activator="parent" location="top">删除</v-tooltip>
            </v-btn>
          </div>
        </template>
        <template v-slot:no-data>
          <div class="text-center pa-8">
            <v-icon icon="mdi-inbox" size="48" color="grey-lighten-1" />
            <p class="text-medium-emphasis mt-2">暂无报警数据</p>
          </div>
        </template>
      </v-data-table>
    </v-card>

    <!-- View Dialog -->
    <v-dialog v-model="viewDialogVisible" max-width="700">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-bell" class="mr-2" />
          报警详情
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="viewDialogVisible = false" />
        </v-card-title>
        <v-divider />
        <v-card-text v-if="currentAlarm">
          <v-table density="compact">
            <tbody>
              <tr><td class="text-medium-emphasis" style="width:120px">报警编号</td><td><v-chip size="small" variant="tonal" color="primary">{{ currentAlarm.alarm_code }}</v-chip></td></tr>
              <tr><td class="text-medium-emphasis">报警级别</td><td><v-chip :color="levelColor(currentAlarm.alarm_level)" size="small" variant="tonal">{{ getLevelText(currentAlarm.alarm_level) }}</v-chip></td></tr>
              <tr><td class="text-medium-emphasis">报警来源</td><td>{{ currentAlarm.alarm_source }}</td></tr>
              <tr><td class="text-medium-emphasis">报警类型</td><td>{{ currentAlarm.alarm_type || '-' }}</td></tr>
              <tr><td class="text-medium-emphasis">报警标题</td><td>{{ currentAlarm.title }}</td></tr>
              <tr><td class="text-medium-emphasis">报警描述</td><td>{{ currentAlarm.description || '-' }}</td></tr>
              <tr><td class="text-medium-emphasis">关联设备</td><td>{{ currentAlarm.device_code || '-' }}</td></tr>
              <tr><td class="text-medium-emphasis">设备名称</td><td>{{ currentAlarm.device_name || '-' }}</td></tr>
              <tr><td class="text-medium-emphasis">报警值</td><td>{{ currentAlarm.alarm_value || '-' }}</td></tr>
              <tr><td class="text-medium-emphasis">阈值</td><td>{{ currentAlarm.threshold_value || '-' }}</td></tr>
              <tr><td class="text-medium-emphasis">状态</td><td><v-chip :color="statusColor(currentAlarm.status)" size="small" variant="tonal">{{ getStatusText(currentAlarm.status) }}</v-chip></td></tr>
              <tr><td class="text-medium-emphasis">报警时间</td><td>{{ formatDateTime(currentAlarm.alarm_time) }}</td></tr>
              <tr><td class="text-medium-emphasis">处理人</td><td>{{ currentAlarm.handler || '-' }}</td></tr>
              <tr><td class="text-medium-emphasis">处理时间</td><td>{{ currentAlarm.handled_at ? formatDateTime(currentAlarm.handled_at) : '-' }}</td></tr>
              <tr><td class="text-medium-emphasis">处理备注</td><td>{{ currentAlarm.handle_remark || '-' }}</td></tr>
            </tbody>
          </v-table>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="viewDialogVisible = false">关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Handle Dialog -->
    <v-dialog v-model="handleDialogVisible" max-width="500" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-check-circle" class="mr-2" />
          处理报警
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="handleDialogVisible = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-form>
            <v-select v-model="handleForm.status" :items="handleStatusOptions" label="处理状态" />
            <v-text-field v-model="handleForm.handler" label="处理人" placeholder="请输入处理人" />
            <v-textarea v-model="handleForm.handle_remark" label="处理备注" :rows="4" placeholder="请输入处理备注" />
          </v-form>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="handleDialogVisible = false">取消</v-btn>
          <v-btn color="primary" :loading="submitting" @click="submitHandle">确认</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Clear Dialog -->
    <v-dialog v-model="showClearDialog" max-width="500" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-delete-sweep" class="mr-2" />
          清理历史报警
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="showClearDialog = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-form>
            <v-number-input v-model.number="clearForm.days" label="保留天数" :min="1" :max="365" controlVariant="stacked" />
            <div class="text-caption text-medium-emphasis mt-1">将清理指定天数前已解决的报警记录</div>
          </v-form>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showClearDialog = false">取消</v-btn>
          <v-btn color="error" :loading="submitting" @click="clearOldAlarms">确认清理</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 加工事件对话框 -->
    <v-dialog v-model="alarmEventsDialog" max-width="1000px" scrollable>
      <v-card style="display: flex; flex-direction: column; height: 70vh;">
        <v-card-title class="d-flex align-center flex-shrink-0">
          <v-icon icon="mdi-cog-transfer" class="mr-2" />
          报警 #{{ alarmEventsAlarm?.alarm_code }} - 关联加工事件
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" @click="alarmEventsDialog = false" />
        </v-card-title>
        <v-divider class="flex-shrink-0" />
        <v-card-text style="flex: 1; overflow-y: auto;">
          <div v-if="alarmEventsLoading" class="text-center pa-8">
            <v-progress-circular indeterminate color="primary" />
          </div>
          <div v-else-if="alarmEventsData.length > 0">
            <v-table density="compact">
              <thead>
                <tr>
                  <th>事件 UID</th>
                  <th>启动码</th>
                  <th>开始时间</th>
                  <th>加工时长</th>
                  <th>设备 ID</th>
                  <th>操作员</th>
                  <th>工站编号</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="e in alarmEventsData" :key="e.id">
                  <td class="text-caption">{{ e.event_uid || '-' }}</td>
                  <td><v-chip size="x-small" color="primary">{{ e.start_code || '-' }}</v-chip></td>
                  <td class="text-caption">{{ formatDateTime(e.start_time) }}</td>
                  <td>{{ formatDuration(e.duringtime) }}</td>
                  <td><v-chip v-if="e.machine_id" size="x-small" color="warning">{{ e.machine_id }}</v-chip><span v-else>-</span></td>
                  <td>{{ e.operator_name || e.operator_id || '-' }}</td>
                  <td><v-chip v-if="e.process_no" size="x-small" color="pink">{{ e.process_no }}</v-chip><span v-else>-</span></td>
                </tr>
              </tbody>
            </v-table>
          </div>
          <div v-else class="text-center pa-8 text-medium-emphasis">
            <v-icon icon="mdi-inbox" size="48" />
            <p class="mt-2">未找到关联加工事件</p>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useMessage, useConfirm } from '@/composables/useMessage'
import { alarmAPI, eventAssociationAPI } from '@/api/index'
import { formatDateTime } from '@/utils/datetime'

const message = useMessage()
const confirmDialog = useConfirm()

const loading = ref(false)
const submitting = ref(false)
const showSearch = ref(true)
const viewDialogVisible = ref(false)
const handleDialogVisible = ref(false)
const showClearDialog = ref(false)
const currentAlarm = ref(null)
const selectedIds = ref([])

// 加工事件对话框状态
const alarmEventsDialog = ref(false)
const alarmEventsAlarm = ref(null)
const alarmEventsLoading = ref(false)
const alarmEventsData = ref([])

const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const searchQuery = reactive({
  alarm_code: '',
  device_code: '',
  alarm_level: '',
  status: '',
  start_date: '',
  end_date: ''
})

const alarmStats = reactive({
  total: 0,
  pending: 0,
  processing: 0,
  resolved: 0,
  ignored: 0,
  critical: 0,
  warning: 0,
  info: 0
})

const alarmList = ref([])

const handleForm = reactive({
  alarm_id: null,
  status: 'resolved',
  handler: '',
  handle_remark: ''
})

const clearForm = reactive({
  days: 30
})

const levelOptions = [
  { title: '全部', value: '' },
  { title: '严重', value: 'critical' },
  { title: '警告', value: 'warning' },
  { title: '信息', value: 'info' }
]

const statusFilterOptions = [
  { title: '全部', value: '' },
  { title: '待处理', value: 'pending' },
  { title: '处理中', value: 'processing' },
  { title: '已解决', value: 'resolved' },
  { title: '已忽略', value: 'ignored' }
]

const handleStatusOptions = [
  { title: '已解决', value: 'resolved' },
  { title: '已忽略', value: 'ignored' },
  { title: '处理中', value: 'processing' }
]

const headers = [
  { title: 'ID', key: 'id', width: '60px' },
  { title: '报警编号', key: 'alarm_code' },
  { title: '报警级别', key: 'alarm_level' },
  { title: '报警类型', key: 'alarm_type' },
  { title: '报警标题', key: 'title' },
  { title: '关联设备', key: 'device_code' },
  { title: '报警值/阈值', key: 'alarm_value' },
  { title: '状态', key: 'status' },
  { title: '处理人', key: 'handler' },
  { title: '报警时间', key: 'alarm_time' },
  { title: '操作', key: 'actions', sortable: false, width: '180px' }
]

const levelColor = (level) => {
  const map = { critical: 'error', warning: 'warning', info: 'info' }
  return map[level] || 'grey'
}

const getLevelText = (level) => {
  const textMap = { critical: '严重', warning: '警告', info: '信息' }
  return textMap[level] || level
}

const statusColor = (status) => {
  const map = { pending: 'warning', processing: 'info', resolved: 'success', ignored: 'grey' }
  return map[status] || 'grey'
}

const getStatusText = (status) => {
  const textMap = { pending: '待处理', processing: '处理中', resolved: '已解决', ignored: '已忽略' }
  return textMap[status] || status
}

const loadAlarms = async () => {
  try {
    loading.value = true
    const params = {
      page: page.value,
      page_size: pageSize.value,
      ...searchQuery
    }
    const res = await alarmAPI.getAlarms(params)
    alarmList.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch (error) {
    message.error('加载报警列表失败')
  } finally {
    loading.value = false
  }
}

const loadAlarmStats = async () => {
  try {
    const params = {}
    if (searchQuery.start_date) params.start_date = searchQuery.start_date
    if (searchQuery.end_date) params.end_date = searchQuery.end_date
    const res = await alarmAPI.getStats(params)
    Object.assign(alarmStats, res.data || {})
  } catch (error) {
    console.error('加载报警统计失败:', error)
  }
}

const resetSearch = () => {
  searchQuery.alarm_code = ''
  searchQuery.device_code = ''
  searchQuery.alarm_level = ''
  searchQuery.status = ''
  searchQuery.start_date = ''
  searchQuery.end_date = ''
  page.value = 1
  loadAlarms()
  loadAlarmStats()
}

const viewAlarm = (alarm) => {
  currentAlarm.value = alarm
  viewDialogVisible.value = true
}

const formatDuration = (ms) => {
  if (!ms && ms !== 0) return '-'
  const seconds = ms / 1000
  if (seconds < 60) return `${seconds.toFixed(2)}秒`
  const minutes = seconds / 60
  if (minutes < 60) return `${minutes.toFixed(2)}分钟`
  const hours = minutes / 60
  return `${hours.toFixed(2)}小时`
}

const viewAlarmEvents = async (alarm) => {
  alarmEventsAlarm.value = alarm
  alarmEventsDialog.value = true
  alarmEventsLoading.value = true
  alarmEventsData.value = []
  try {
    const response = await alarmAPI.getAlarm(alarm.id)
    const alarmData = response.data
    if (alarmData.device_code) {
      const eventsRes = await eventAssociationAPI.getByDevice(alarmData.device_code, { page_size: 50 })
      alarmEventsData.value = eventsRes.data?.items || []
    }
  } catch (error) {
    console.error('加载加工事件失败:', error)
  } finally {
    alarmEventsLoading.value = false
  }
}

const handleAlarm = (alarm) => {
  handleForm.alarm_id = alarm.id
  handleForm.status = 'resolved'
  handleForm.handler = ''
  handleForm.handle_remark = ''
  handleDialogVisible.value = true
}

const submitHandle = async () => {
  try {
    submitting.value = true
    await alarmAPI.handleAlarm(handleForm.alarm_id, {
      status: handleForm.status,
      handler: handleForm.handler,
      handle_remark: handleForm.handle_remark
    })
    message.success('处理成功')
    handleDialogVisible.value = false
    loadAlarms()
    loadAlarmStats()
  } catch (error) {
    message.error('处理失败')
  } finally {
    submitting.value = false
  }
}

const handleBatchResolve = async () => {
  if (selectedIds.value.length === 0) {
    message.warning('请选择要处理的报警')
    return
  }

  try {
    submitting.value = true
    await alarmAPI.batchHandleAlarms(selectedIds.value, {
      status: 'resolved',
      handler: '',
      handle_remark: '批量处理'
    })
    message.success(`已处理 ${selectedIds.value.length} 条报警`)
    selectedIds.value = []
    loadAlarms()
    loadAlarmStats()
  } catch (error) {
    message.error('批量处理失败')
  } finally {
    submitting.value = false
  }
}

const deleteAlarm = async (alarm) => {
  try {
    const ok = await confirmDialog('确定要删除该报警记录吗？', '确认删除', 'warning')
    if (!ok) return
    await alarmAPI.deleteAlarm(alarm.id)
    message.success('删除成功')
    loadAlarms()
    loadAlarmStats()
  } catch (error) {
    message.error('删除失败')
  }
}

const clearOldAlarms = async () => {
  try {
    submitting.value = true
    await alarmAPI.clearOldAlarms(clearForm.days)
    message.success(`已清理 ${clearForm.days} 天前的报警记录`)
    showClearDialog.value = false
    loadAlarms()
    loadAlarmStats()
  } catch (error) {
    message.error('清理失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadAlarms()
  loadAlarmStats()
})
</script>
