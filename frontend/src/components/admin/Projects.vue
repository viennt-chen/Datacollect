<template>
  <div>
    <!-- Action bar -->
    <v-toolbar flat color="transparent" class="mb-4">
      <div>
        <div class="text-h5 font-weight-bold d-flex align-center ga-2">
          <v-icon icon="mdi-folder-open" color="primary" />
          项目管理
        </div>
        <div class="text-caption text-medium-emphasis mt-1">
          首页 / 项目管理
        </div>
      </div>
      <v-spacer />
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openAdd">
        新增项目
      </v-btn>
      <v-btn variant="outlined" prepend-icon="mdi-upload" class="ml-2" @click="openImportDialog">
        导入项目
      </v-btn>
      <v-btn variant="outlined" prepend-icon="mdi-download" class="ml-2" @click="exportProjects">
        导出项目
      </v-btn>
    </v-toolbar>

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
        <v-form @submit.prevent="handleSearch">
          <v-row dense>
            <v-col cols="12" sm="6" md="3">
              <v-text-field v-model="queryParams.name" label="项目名称" placeholder="请输入项目名称" clearable density="compact" />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-text-field v-model="queryParams.code" label="项目编码" placeholder="请输入项目编码" clearable density="compact" />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-text-field v-model="queryParams.customer" label="客户" placeholder="请输入客户名称" clearable density="compact" />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-select v-model="queryParams.status" :items="statusOptions" label="状态" clearable density="compact" />
            </v-col>
          </v-row>
          <div class="d-flex ga-2 mt-2">
            <v-btn color="primary" prepend-icon="mdi-magnify" @click="handleSearch">查询</v-btn>
            <v-btn variant="outlined" prepend-icon="mdi-undo" @click="resetQuery">重置</v-btn>
          </div>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- Data table -->
    <v-card>
      <v-card-title class="d-flex align-center ga-2">
        <v-icon icon="mdi-format-list-bulleted" />
        项目列表
        <v-spacer />
        <v-btn variant="outlined" prepend-icon="mdi-refresh" size="small" @click="handleSearch">刷新</v-btn>
      </v-card-title>
      <v-data-table
        :headers="headers"
        :items="list"
        :loading="loading"
        :items-per-page="pageSize"
        :page="page"
        :server-items-length="total"
        @update:page="p => { page = p; handleSearch() }"
        @update:items-per-page="s => { pageSize = s; handleSearch() }"
        hover
      >
        <template v-slot:item.code="{ item }">
          <v-chip size="small" variant="tonal" color="primary">{{ item.code }}</v-chip>
        </template>
        <template v-slot:item.status="{ item }">
          <v-chip :color="statusColor(item.status)" size="small" variant="tonal">
            {{ statusLabel(item.status) }}
          </v-chip>
        </template>
        <template v-slot:item.actions="{ item }">
          <div class="d-flex ga-1">
            <v-btn icon variant="text" size="small" @click="openView(item)">
              <v-icon icon="mdi-eye" size="small" />
              <v-tooltip activator="parent" location="top">查看详情</v-tooltip>
            </v-btn>
            <v-btn icon variant="text" size="small" @click="openEdit(item)">
              <v-icon icon="mdi-pencil" size="small" />
              <v-tooltip activator="parent" location="top">编辑</v-tooltip>
            </v-btn>
            <v-btn icon variant="text" size="small" color="error" @click="handleDelete(item)">
              <v-icon icon="mdi-delete" size="small" />
              <v-tooltip activator="parent" location="top">删除</v-tooltip>
            </v-btn>
          </div>
        </template>
        <template v-slot:no-data>
          <div class="text-center pa-8">
            <v-icon icon="mdi-inbox" size="48" color="grey-lighten-1" />
            <p class="text-medium-emphasis mt-2">暂无项目数据</p>
          </div>
        </template>
      </v-data-table>
    </v-card>

    <!-- Add/Edit Dialog -->
    <v-dialog v-model="showAddDialog" max-width="600" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-plus" class="mr-2" />
          新增项目
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="closeDialog" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-form>
            <v-text-field v-model="formData.code" label="项目编码" :rules="[v => !!v || '请输入项目编码']" required />
            <v-text-field v-model="formData.name" label="项目名称" :rules="[v => !!v || '请输入项目名称']" required />
            <v-text-field v-model="formData.customer" label="客户" />
            <v-text-field v-model="formData.manager" label="负责人" />
            <v-row>
              <v-col cols="6">
                <v-text-field v-model="formData.start_date" label="开始日期" type="date" />
              </v-col>
              <v-col cols="6">
                <v-text-field v-model="formData.end_date" label="结束日期" type="date" />
              </v-col>
            </v-row>
            <v-textarea v-model="formData.description" label="描述" rows="3" />
            <v-number-input v-model.number="formData.sort_order" label="排序" :min="0" controlVariant="stacked" />
            <v-select v-model="formData.status" :items="statusOptions.filter(s => s.value)" label="状态" />
          </v-form>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeDialog">取消</v-btn>
          <v-btn color="primary" :loading="saving" @click="handleSave">保存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="showEditDialog" max-width="600" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-pencil" class="mr-2" />
          编辑项目
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="closeDialog" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-form>
            <v-text-field v-model="formData.code" label="项目编码" :rules="[v => !!v || '请输入项目编码']" required />
            <v-text-field v-model="formData.name" label="项目名称" :rules="[v => !!v || '请输入项目名称']" required />
            <v-text-field v-model="formData.customer" label="客户" />
            <v-text-field v-model="formData.manager" label="负责人" />
            <v-row>
              <v-col cols="6">
                <v-text-field v-model="formData.start_date" label="开始日期" type="date" />
              </v-col>
              <v-col cols="6">
                <v-text-field v-model="formData.end_date" label="结束日期" type="date" />
              </v-col>
            </v-row>
            <v-textarea v-model="formData.description" label="描述" rows="3" />
            <v-number-input v-model.number="formData.sort_order" label="排序" :min="0" controlVariant="stacked" />
            <v-select v-model="formData.status" :items="statusOptions.filter(s => s.value)" label="状态" />
          </v-form>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeDialog">取消</v-btn>
          <v-btn color="primary" :loading="saving" @click="handleSave">保存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- View Dialog -->
    <v-dialog v-model="showViewDialog" max-width="600">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-eye" class="mr-2" />
          项目详情
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="showViewDialog = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-table density="compact">
            <tbody>
              <tr><td class="text-medium-emphasis" style="width:120px">ID</td><td>{{ viewData.id }}</td></tr>
              <tr><td class="text-medium-emphasis">项目编码</td><td><v-chip size="small" variant="tonal" color="primary">{{ viewData.code }}</v-chip></td></tr>
              <tr><td class="text-medium-emphasis">项目名称</td><td>{{ viewData.name }}</td></tr>
              <tr><td class="text-medium-emphasis">客户</td><td>{{ viewData.customer || '-' }}</td></tr>
              <tr><td class="text-medium-emphasis">负责人</td><td>{{ viewData.manager || '-' }}</td></tr>
              <tr><td class="text-medium-emphasis">状态</td><td><v-chip :color="statusColor(viewData.status)" size="small" variant="tonal">{{ statusLabel(viewData.status) }}</v-chip></td></tr>
              <tr><td class="text-medium-emphasis">开始日期</td><td>{{ viewData.start_date || '-' }}</td></tr>
              <tr><td class="text-medium-emphasis">结束日期</td><td>{{ viewData.end_date || '-' }}</td></tr>
              <tr><td class="text-medium-emphasis">排序</td><td>{{ viewData.sort_order }}</td></tr>
              <tr><td class="text-medium-emphasis">描述</td><td>{{ viewData.description || '-' }}</td></tr>
              <tr><td class="text-medium-emphasis">创建时间</td><td>{{ formatDateTime(viewData.created_at) }}</td></tr>
              <tr><td class="text-medium-emphasis">更新时间</td><td>{{ formatDateTime(viewData.updated_at) }}</td></tr>
            </tbody>
          </v-table>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showViewDialog = false">关闭</v-btn>
          <v-btn color="primary" prepend-icon="mdi-pencil" @click="showViewDialog = false; openEdit(viewData)">编辑</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 导入对话框 -->
    <v-dialog v-model="showImportDialog" max-width="500" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-upload" class="mr-2" />
          导入项目
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="closeImportDialog" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <div class="mb-4">
            <div class="text-subtitle-2 mb-1">1. 下载模板</div>
            <p class="text-caption text-medium-emphasis mb-2">请先下载标准导入模板</p>
            <v-btn variant="outlined" prepend-icon="mdi-download" size="small" @click="downloadTemplate">下载模板</v-btn>
          </div>
          <div class="mb-4">
            <div class="text-subtitle-2 mb-1">2. 填写数据</div>
            <p class="text-caption text-medium-emphasis">按照模板格式填写项目数据</p>
          </div>
          <div>
            <div class="text-subtitle-2 mb-1">3. 上传文件</div>
            <p class="text-caption text-medium-emphasis mb-2">选择填写好的 Excel 文件上传</p>
            <v-file-input
              v-model="importFileModel"
              label="选择文件"
              accept=".xlsx,.xls,.csv"
              density="compact"
              show-size
              clearable
              @update:model-value="onImportFileChange"
            />
          </div>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeImportDialog">取消</v-btn>
          <v-btn color="primary" :loading="uploading" :disabled="!importFile" @click="uploadImportFile">
            {{ uploading ? '上传中...' : '开始导入' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useMessage, useConfirm } from '@/composables/useMessage'
import { projectAPI } from '@/api/index'
import { formatDateTime } from '@/utils/datetime'
import { usePagination } from '@/composables/usePagination'
import { useListLoader } from '@/composables/useListLoader'
import { useCrudDialog } from '@/composables/useCrudDialog'

const message = useMessage()
const confirmDialog = useConfirm()

const showSearch = ref(true)

const showImportDialog = ref(false)
const importFile = ref(null)
const importFileModel = ref(null)
const uploading = ref(false)

const statusOptions = [
  { title: '全部', value: '' },
  { title: '进行中', value: 'active' },
  { title: '已完成', value: 'completed' },
  { title: '已暂停', value: 'suspended' },
  { title: '已取消', value: 'cancelled' },
]

const headers = [
  { title: 'ID', key: 'id', width: '70px' },
  { title: '项目编码', key: 'code' },
  { title: '项目名称', key: 'name' },
  { title: '客户', key: 'customer' },
  { title: '负责人', key: 'manager' },
  { title: '开始日期', key: 'start_date' },
  { title: '结束日期', key: 'end_date' },
  { title: '状态', key: 'status' },
  { title: '排序', key: 'sort_order', width: '70px' },
  { title: '操作', key: 'actions', sortable: false, width: '140px' },
]

const queryParams = reactive({ name: '', code: '', customer: '', status: '' })

const { page, pageSize, total, pageStart, pageEnd, pageSizes, setTotal, reset: resetPage } = usePagination()

const { loading, list, load } = useListLoader(projectAPI.list, {
  onSuccess: (res, totalCount) => setTotal(totalCount),
  onError: () => message.error('加载项目列表失败')
})

const {
  showAddDialog, showEditDialog, showViewDialog,
  saving, formData, formErrors, viewData,
  openAdd, openEdit, openView, closeDialog, resetForm, save
} = useCrudDialog({
  createFn: projectAPI.create,
  updateFn: projectAPI.update,
  validateFn: (data) => {
    const errors = {}
    if (!data.code?.trim()) errors.code = '请输入项目编码'
    if (!data.name?.trim()) errors.name = '请输入项目名称'
    return { valid: Object.keys(errors).length === 0, errors }
  },
  onSuccess: () => {
    message.success(showEditDialog.value ? '项目更新成功' : '项目创建成功')
    handleSearch()
  },
  onError: (detail) => message.error('保存失败：' + detail),
  defaults: { id: null, code: '', name: '', description: '', customer: '', manager: '', start_date: '', end_date: '', status: 'active', sort_order: 0 }
})

function statusLabel(status) {
  const map = { active: '进行中', completed: '已完成', suspended: '已暂停', cancelled: '已取消' }
  return map[status] || status || '-'
}

function statusColor(status) {
  const map = { active: 'success', completed: 'info', suspended: 'warning', cancelled: 'error' }
  return map[status] || 'grey'
}

function handleSearch() {
  load({ ...queryParams, page: page.value, page_size: pageSize.value })
}

function resetQuery() {
  Object.assign(queryParams, { name: '', code: '', customer: '', status: '' })
  resetPage()
  handleSearch()
}

async function handleSave() {
  await save()
}

async function handleDelete(item) {
  const ok = await confirmDialog(`确定删除项目"${item.name}"吗？`, '确认删除', 'warning')
  if (!ok) return
  try {
    await projectAPI.delete(item.id)
    message.success('项目已删除')
    handleSearch()
  } catch (e) {
    message.error('删除失败：' + (e.response?.data?.detail || e.message))
  }
}

function openImportDialog() {
  importFile.value = null
  importFileModel.value = null
  showImportDialog.value = true
}

function closeImportDialog() {
  showImportDialog.value = false
  importFile.value = null
  importFileModel.value = null
}

function onImportFileChange(files) {
  if (Array.isArray(files) && files.length > 0) {
    importFile.value = files[0]
  } else if (files instanceof File) {
    importFile.value = files
  } else {
    importFile.value = null
  }
}

async function exportProjects() {
  try {
    const response = await projectAPI.exportProjects(queryParams)
    const url = window.URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = url
    link.download = `projects_${new Date().toISOString().split('T')[0]}.csv`
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('导出项目失败:', error)
    message.error('导出失败')
  }
}

async function downloadTemplate() {
  try {
    const response = await projectAPI.downloadTemplate()
    const blob = response.data instanceof Blob ? response.data : new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '项目导入模板.xlsx'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    setTimeout(() => window.URL.revokeObjectURL(url), 100)
  } catch (error) {
    console.error('下载模板失败:', error)
    message.error('下载模板失败')
  }
}

async function uploadImportFile() {
  if (!importFile.value) return
  try {
    uploading.value = true
    const response = await projectAPI.importProjects(importFile.value)
    const result = response.data
    let msg = `导入完成：新增 ${result.imported} 条，更新 ${result.updated} 条`
    if (result.errors && result.errors.length > 0) {
      msg += `，${result.errors.length} 条错误`
      console.warn('导入错误:', result.errors)
    }
    message.success(msg)
    closeImportDialog()
    handleSearch()
  } catch (error) {
    console.error('导入项目失败:', error)
    message.error('导入失败：' + (error.response?.data?.detail || error.message))
  } finally {
    uploading.value = false
  }
}

onMounted(() => handleSearch())
</script>
