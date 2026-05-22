<template>
  <div>
    <!-- Action bar -->
    <v-toolbar flat color="transparent" class="mb-4">
      <div>
        <div class="text-h5 font-weight-bold d-flex align-center ga-2">
          <v-icon icon="mdi-clipboard-check" color="primary" />
          质量管理
        </div>
        <div class="text-caption text-medium-emphasis mt-1">
          首页 / 质量管理
        </div>
      </div>
      <v-spacer />
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openAddDialog" class="mr-2">
        新增记录
      </v-btn>
      <v-btn variant="outlined" prepend-icon="mdi-download" @click="exportRecords">
        导出记录
      </v-btn>
    </v-toolbar>

    <!-- Tabs -->
    <v-tabs v-model="activeTab" class="mb-4" bg-color="transparent">
      <v-tab value="records">
        <v-icon icon="mdi-format-list-checks" class="mr-1" />
        质量记录
        <v-chip size="small" class="ml-2" color="primary" variant="tonal">{{ qualityStats.total || 0 }}</v-chip>
      </v-tab>
      <v-tab value="defects">
        <v-icon icon="mdi-bug" class="mr-1" />
        缺陷分析
      </v-tab>
    </v-tabs>

    <!-- Quality Records Tab -->
    <v-window v-model="activeTab">
      <v-window-item value="records">
        <!-- Metrics -->
        <v-row class="mb-4" dense>
          <v-col cols="12" md="3">
            <v-card>
              <v-card-text>
                <div class="d-flex align-center ga-3">
                  <v-icon icon="mdi-clipboard-check" size="36" color="primary" />
                  <div>
                    <div class="text-h5 font-weight-bold">{{ qualityStats.total?.toLocaleString() || '0' }}</div>
                    <div class="text-caption text-medium-emphasis">记录总数</div>
                    <div class="text-caption">今日：{{ qualityStats.today || 0 }} | 本周：{{ qualityStats.week || 0 }}</div>
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
                    <div class="text-h5 font-weight-bold">{{ qualityStats.passed || '0' }}</div>
                    <div class="text-caption text-medium-emphasis">合格数</div>
                    <div class="text-caption text-success">合格率：{{ qualityStats.passRate || '0' }}%</div>
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="3">
            <v-card>
              <v-card-text>
                <div class="d-flex align-center ga-3">
                  <v-icon icon="mdi-close-circle" size="36" color="error" />
                  <div>
                    <div class="text-h5 font-weight-bold">{{ qualityStats.failed || '0' }}</div>
                    <div class="text-caption text-medium-emphasis">不合格数</div>
                    <div class="text-caption text-warning">需要关注</div>
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="3">
            <v-card>
              <v-card-text>
                <div class="d-flex align-center ga-3">
                  <v-icon icon="mdi-clock-outline" size="36" color="warning" />
                  <div>
                    <div class="text-h5 font-weight-bold">{{ qualityStats.pending || '0' }}</div>
                    <div class="text-caption text-medium-emphasis">待检验</div>
                    <div class="text-caption text-info">等待检验</div>
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
            <v-form @submit.prevent="handleSearch">
              <v-row dense>
                <v-col cols="12" sm="6" md="3">
                  <v-text-field v-model="queryParams.start_time" label="开始时间" type="datetime-local" clearable density="compact" />
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-text-field v-model="queryParams.end_time" label="结束时间" type="datetime-local" clearable density="compact" />
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-text-field v-model="queryParams.product_code" label="产品编号" placeholder="请输入产品编号" clearable density="compact" />
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-text-field v-model="queryParams.device_code" label="设备编号" placeholder="请输入设备编号" clearable density="compact" />
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-select v-model="queryParams.status" :items="statusOptions" label="检验状态" clearable density="compact" />
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-select v-model="queryParams.defect_type" :items="defectTypeOptions" label="缺陷类型" clearable density="compact" />
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-text-field v-model="queryParams.inspector" label="检验员" placeholder="请输入检验员" clearable density="compact" />
                </v-col>
                <v-col cols="12" sm="6" md="3" class="d-flex align-center ga-2">
                  <v-btn color="primary" prepend-icon="mdi-magnify" @click="handleSearch">查询</v-btn>
                  <v-btn variant="outlined" prepend-icon="mdi-undo" @click="handleReset">重置</v-btn>
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>
        </v-card>

        <!-- Data Table -->
        <v-card>
          <v-card-title class="d-flex align-center ga-2">
            <v-icon icon="mdi-table" />
            质量记录列表
            <v-spacer />
            <v-btn color="error" variant="outlined" prepend-icon="mdi-delete" size="small" :disabled="selectedIds.length === 0" @click="handleBatchDelete">
              批量删除
            </v-btn>
          </v-card-title>
          <v-data-table
            :headers="headers"
            :items="qualityRecords"
            :loading="loading"
            :items-per-page="pagination.page_size"
            :page="pagination.page"
            :server-items-length="pagination.total"
            @update:page="p => handlePageChange(p)"
            @update:items-per-page="s => { pagination.page_size = s; handleSearch() }"
            show-select
            v-model="selectedIds"
            item-value="id"
            hover
          >
            <template v-slot:item.product_code="{ item }">
              <v-chip size="small" variant="tonal" color="primary">{{ item.product_code }}</v-chip>
            </template>
            <template v-slot:item.device_code="{ item }">
              <v-chip size="small" variant="tonal" color="primary">{{ item.device_code }}</v-chip>
            </template>
            <template v-slot:item.status="{ item }">
              <v-chip :color="statusColor(item.status)" size="small" variant="tonal">
                {{ getStatusText(item.status) }}
              </v-chip>
            </template>
            <template v-slot:item.inspect_time="{ item }">
              {{ formatDateTime(item.inspect_time) }}
            </template>
            <template v-slot:item.actions="{ item }">
              <div class="d-flex ga-1">
                <v-btn icon variant="text" size="small" @click="viewRecord(item)">
                  <v-icon icon="mdi-eye" size="small" />
                  <v-tooltip activator="parent" location="top">查看</v-tooltip>
                </v-btn>
                <v-btn icon variant="text" size="small" @click="editRecord(item)">
                  <v-icon icon="mdi-pencil" size="small" />
                  <v-tooltip activator="parent" location="top">编辑</v-tooltip>
                </v-btn>
                <v-btn icon variant="text" size="small" color="purple" @click="viewRecordEvents(item)">
                  <v-icon icon="mdi-cog-transfer" size="small" />
                  <v-tooltip activator="parent" location="top">加工事件</v-tooltip>
                </v-btn>
                <v-btn icon variant="text" size="small" color="error" @click="deleteRecord(item)">
                  <v-icon icon="mdi-delete" size="small" />
                  <v-tooltip activator="parent" location="top">删除</v-tooltip>
                </v-btn>
              </div>
            </template>
            <template v-slot:no-data>
              <div class="text-center pa-8">
                <v-icon icon="mdi-inbox" size="48" color="grey-lighten-1" />
                <p class="text-medium-emphasis mt-2">暂无数据</p>
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-window-item>

      <!-- Defect Analysis Tab -->
      <v-window-item value="defects">
        <v-card>
          <v-card-title class="d-flex align-center ga-2">
            <v-icon icon="mdi-chart-bar" />
            缺陷类型分布
          </v-card-title>
          <v-card-text>
            <div ref="defectChartEl" style="width: 100%; height: 300px;" />
            <v-table density="compact" class="mt-4">
              <thead>
                <tr>
                  <th>缺陷类型</th>
                  <th>次数</th>
                  <th>占比</th>
                  <th>分布</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in defectAnalysis" :key="item.type">
                  <td>{{ item.type }}</td>
                  <td>{{ item.count }} 次</td>
                  <td>{{ item.percentage }}%</td>
                  <td>
                    <v-progress-linear :model-value="item.percentage" color="primary" height="8" rounded />
                  </td>
                </tr>
              </tbody>
            </v-table>
          </v-card-text>
        </v-card>
      </v-window-item>
    </v-window>

    <!-- Add/Edit Dialog -->
    <v-dialog v-model="showDialog" max-width="600" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon :icon="isEditing ? 'mdi-pencil' : 'mdi-plus'" class="mr-2" />
          {{ isEditing ? '编辑质量记录' : '新增质量记录' }}
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="closeDialog" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-form>
            <v-text-field v-model="formData.product_code" label="产品编号" :rules="[v => !!v || '请输入产品编号']" required />
            <v-text-field v-model="formData.product_name" label="产品名称" :rules="[v => !!v || '请输入产品名称']" required />
            <v-text-field v-model="formData.device_code" label="设备编号" :rules="[v => !!v || '请输入设备编号']" required />
            <v-select v-model="formData.status" :items="recordStatusOptions" label="检验状态" />
            <v-select v-if="formData.status === 'failed'" v-model="formData.defect_type" :items="defectTypes" label="缺陷类型" clearable />
            <v-text-field v-model="formData.inspector" label="检验员" />
            <v-textarea v-model="formData.remark" label="备注" rows="3" />
          </v-form>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeDialog">取消</v-btn>
          <v-btn color="primary" @click="handleSubmit">确定</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- View Dialog -->
    <v-dialog v-model="showViewDialog" max-width="600">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-eye" class="mr-2" />
          质量记录详情
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="showViewDialog = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-table density="compact">
            <tbody>
              <tr><td class="text-medium-emphasis" style="width:120px">记录ID</td><td>{{ viewRecordData.id }}</td></tr>
              <tr><td class="text-medium-emphasis">产品编号</td><td><v-chip size="small" variant="tonal" color="primary">{{ viewRecordData.product_code }}</v-chip></td></tr>
              <tr><td class="text-medium-emphasis">产品名称</td><td>{{ viewRecordData.product_name }}</td></tr>
              <tr><td class="text-medium-emphasis">设备编号</td><td><v-chip size="small" variant="tonal" color="primary">{{ viewRecordData.device_code }}</v-chip></td></tr>
              <tr><td class="text-medium-emphasis">检验状态</td><td><v-chip :color="statusColor(viewRecordData.status)" size="small" variant="tonal">{{ getStatusText(viewRecordData.status) }}</v-chip></td></tr>
              <tr><td class="text-medium-emphasis">缺陷类型</td><td>{{ viewRecordData.defect_type || '-' }}</td></tr>
              <tr><td class="text-medium-emphasis">检验员</td><td>{{ viewRecordData.inspector }}</td></tr>
              <tr><td class="text-medium-emphasis">检验时间</td><td>{{ formatDateTime(viewRecordData.inspect_time) }}</td></tr>
              <tr><td class="text-medium-emphasis">备注</td><td>{{ viewRecordData.remark || '-' }}</td></tr>
            </tbody>
          </v-table>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showViewDialog = false">关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 加工事件对话框 -->
    <v-dialog v-model="recordEventsDialog" max-width="1000px" scrollable>
      <v-card style="display: flex; flex-direction: column; height: 70vh;">
        <v-card-title class="d-flex align-center flex-shrink-0">
          <v-icon icon="mdi-cog-transfer" class="mr-2" />
          质检记录 #{{ recordEventsRecord?.id }} - 关联加工事件
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" @click="recordEventsDialog = false" />
        </v-card-title>
        <v-divider class="flex-shrink-0" />
        <v-card-text style="flex: 1; overflow-y: auto;">
          <div v-if="recordEventsLoading" class="text-center pa-8">
            <v-progress-circular indeterminate color="primary" />
          </div>
          <div v-else-if="recordEventsData.length > 0">
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
                <tr v-for="e in recordEventsData" :key="e.id">
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
import { ref, computed, onMounted, watch } from 'vue'
import { qualityAPI, eventAssociationAPI } from '@/api/index.js'
import { formatDateTime } from '@/utils/datetime'

const activeTab = ref('records')
const showSearch = ref(true)
const loading = ref(false)
const qualityRecords = ref([])
const defectTypes = ref([])
const defectAnalysis = ref([])
const selectedIds = ref([])
const showDialog = ref(false)
const showViewDialog = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const viewRecordData = ref({})
const defectChartEl = ref(null)

// 加工事件对话框状态
const recordEventsDialog = ref(false)
const recordEventsRecord = ref(null)
const recordEventsLoading = ref(false)
const recordEventsData = ref([])

const queryParams = ref({
  start_time: '',
  end_time: '',
  product_code: '',
  device_code: '',
  status: '',
  defect_type: '',
  inspector: '',
  page: 1,
  page_size: 20
})

const pagination = ref({
  page: 1,
  page_size: 20,
  total: 0
})

const qualityStats = ref({
  total: 0,
  today: 0,
  week: 0,
  passed: 0,
  failed: 0,
  pending: 0,
  passRate: 0
})

const formData = ref({
  product_code: '',
  product_name: '',
  device_code: '',
  status: 'passed',
  defect_type: '',
  inspector: '',
  remark: ''
})

const statusOptions = [
  { title: '全部', value: '' },
  { title: '合格', value: 'passed' },
  { title: '不合格', value: 'failed' },
  { title: '待检验', value: 'pending' }
]

const recordStatusOptions = [
  { title: '合格', value: 'passed' },
  { title: '不合格', value: 'failed' },
  { title: '待检验', value: 'pending' }
]

const defectTypeOptions = computed(() => {
  return defectTypes.value.map(t => ({ title: t, value: t }))
})

const headers = [
  { title: '记录ID', key: 'id', width: '80px' },
  { title: '产品编号', key: 'product_code' },
  { title: '产品名称', key: 'product_name' },
  { title: '设备编号', key: 'device_code' },
  { title: '检验状态', key: 'status' },
  { title: '缺陷类型', key: 'defect_type' },
  { title: '检验员', key: 'inspector' },
  { title: '检验时间', key: 'inspect_time' },
  { title: '备注', key: 'remark' },
  { title: '操作', key: 'actions', sortable: false, width: '180px' }
]

const statusColor = (status) => {
  const map = { passed: 'success', failed: 'error', pending: 'warning' }
  return map[status] || 'grey'
}

const getStatusText = (status) => {
  const statusMap = { passed: '合格', failed: '不合格', pending: '待检验' }
  return statusMap[status] || status
}

const loadQualityRecords = async () => {
  try {
    loading.value = true
    const [recordsRes, statsRes] = await Promise.all([
      qualityAPI.getQualityRecords(queryParams.value),
      qualityAPI.getStats(queryParams.value)
    ])

    qualityRecords.value = Array.isArray(recordsRes.data.data) ? recordsRes.data.data : []
    pagination.value.total = recordsRes.data.total || 0
    qualityStats.value = statsRes.data || qualityStats.value
  } catch (error) {
    console.error('加载质量记录失败:', error)
    qualityRecords.value = []
  } finally {
    loading.value = false
  }
}

const loadDefectTypes = async () => {
  try {
    const res = await qualityAPI.getDefectTypes()
    defectTypes.value = Array.isArray(res.data) ? res.data : []
  } catch (error) {
    console.error('加载缺陷类型失败:', error)
    defectTypes.value = []
  }
}

const loadDefectAnalysis = async () => {
  try {
    const res = await qualityAPI.getStats({ group_by: 'defect_type' })
    const data = Array.isArray(res.data.defect_distribution) ? res.data.defect_distribution : []
    const total = data.reduce((sum, item) => sum + (item.count || 0), 0)

    defectAnalysis.value = data.map(item => ({
      type: item.defect_type || '未知',
      count: item.count || 0,
      percentage: total > 0 ? Math.round(((item.count || 0) / total) * 100) : 0
    }))
  } catch (error) {
    console.error('加载缺陷分析失败:', error)
    defectAnalysis.value = []
  }
}

const handleSearch = () => {
  queryParams.value.page = 1
  pagination.value.page = 1
  loadQualityRecords()
}

const handleReset = () => {
  queryParams.value = {
    start_time: '',
    end_time: '',
    product_code: '',
    device_code: '',
    status: '',
    defect_type: '',
    inspector: '',
    page: 1,
    page_size: 20
  }
  pagination.value.page = 1
  loadQualityRecords()
}

const handlePageChange = (page) => {
  queryParams.value.page = page
  pagination.value.page = page
  loadQualityRecords()
}

const openAddDialog = () => {
  isEditing.value = false
  editingId.value = null
  formData.value = {
    product_code: '',
    product_name: '',
    device_code: '',
    status: 'passed',
    defect_type: '',
    inspector: '',
    remark: ''
  }
  showDialog.value = true
}

const editRecord = (record) => {
  isEditing.value = true
  editingId.value = record.id
  formData.value = {
    product_code: record.product_code,
    product_name: record.product_name,
    device_code: record.device_code,
    status: record.status,
    defect_type: record.defect_type || '',
    inspector: record.inspector,
    remark: record.remark || ''
  }
  showDialog.value = true
}

const viewRecord = (record) => {
  viewRecordData.value = record
  showViewDialog.value = true
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

const viewRecordEvents = async (record) => {
  recordEventsRecord.value = record
  recordEventsDialog.value = true
  recordEventsLoading.value = true
  recordEventsData.value = []
  try {
    const response = await qualityAPI.getQualityRecord(record.id)
    const rec = response.data
    const conditions = []
    if (rec.device_code) conditions.push(rec.device_code)
    if (rec.product_code) conditions.push(rec.product_code)
    if (conditions.length > 0) {
      const eventsRes = await eventAssociationAPI.getByDevice(rec.device_code, { page_size: 50 })
      recordEventsData.value = eventsRes.data?.items || []
    }
  } catch (error) {
    console.error('加载加工事件失败:', error)
  } finally {
    recordEventsLoading.value = false
  }
}

const deleteRecord = async (record) => {
  if (!confirm('确定要删除这条质量记录吗？')) return

  try {
    await qualityAPI.deleteQualityRecord(record.id)
    await loadQualityRecords()
  } catch (error) {
    console.error('删除质量记录失败:', error)
  }
}

const handleBatchDelete = async () => {
  if (selectedIds.value.length === 0) return
  if (!confirm(`确定要删除选中的 ${selectedIds.value.length} 条记录吗？`)) return

  try {
    await Promise.all(
      selectedIds.value.map(id => qualityAPI.deleteQualityRecord(id))
    )
    selectedIds.value = []
    await loadQualityRecords()
  } catch (error) {
    console.error('批量删除失败:', error)
  }
}

const handleSubmit = async () => {
  if (!formData.value.product_code || !formData.value.product_name || !formData.value.device_code) {
    alert('请填写必填字段')
    return
  }

  try {
    if (isEditing.value) {
      await qualityAPI.updateQualityRecord(editingId.value, formData.value)
    } else {
      await qualityAPI.createQualityRecord(formData.value)
    }
    closeDialog()
    await loadQualityRecords()
  } catch (error) {
    console.error('保存质量记录失败:', error)
  }
}

const closeDialog = () => {
  showDialog.value = false
  isEditing.value = false
  editingId.value = null
}

const exportRecords = async () => {
  try {
    const res = await qualityAPI.export(queryParams.value)
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `质量记录_${new Date().toISOString().split('T')[0]}.xlsx`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (error) {
    console.error('导出失败:', error)
  }
}

watch(activeTab, (newTab) => {
  if (newTab === 'defects') {
    loadDefectAnalysis()
  }
})

onMounted(() => {
  loadQualityRecords()
  loadDefectTypes()
})
</script>
