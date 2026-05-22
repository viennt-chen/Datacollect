<template>
  <div>
    <!-- Action bar -->
    <v-toolbar flat color="transparent" class="mb-4">
      <div>
        <div class="text-h5 font-weight-bold d-flex align-center ga-2">
          <v-icon icon="mdi-factory" color="primary" />
          车间管理
        </div>
        <div class="text-caption text-medium-emphasis mt-1">
          首页 / 车间管理
        </div>
      </div>
      <v-spacer />
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openAdd">
        新增车间
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
              <v-text-field v-model="queryParams.name" label="车间名称" placeholder="请输入车间名称" clearable density="compact" />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-text-field v-model="queryParams.code" label="车间编码" placeholder="请输入车间编码" clearable density="compact" />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-select v-model="queryParams.status" :items="statusOptions" label="状态" clearable density="compact" />
            </v-col>
            <v-col cols="12" sm="6" md="3" class="d-flex align-center ga-2">
              <v-btn color="primary" prepend-icon="mdi-magnify" @click="handleSearch">查询</v-btn>
              <v-btn variant="outlined" prepend-icon="mdi-undo" @click="resetQuery">重置</v-btn>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- Data table -->
    <v-card>
      <v-card-title class="d-flex align-center ga-2">
        <v-icon icon="mdi-format-list-bulleted" />
        车间列表
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
          <v-chip :color="item.status === 'active' ? 'success' : 'error'" size="small" variant="tonal">
            {{ item.status === 'active' ? '启用' : '禁用' }}
          </v-chip>
        </template>
        <template v-slot:item.created_at="{ item }">
          {{ formatDateTime(item.created_at) }}
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
            <v-btn icon variant="text" size="small" @click="toggleStatus(item)">
              <v-icon :icon="item.status === 'active' ? 'mdi-pause-circle' : 'mdi-play-circle'" size="small" />
              <v-tooltip activator="parent" location="top">{{ item.status === 'active' ? '禁用' : '启用' }}</v-tooltip>
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
            <p class="text-medium-emphasis mt-2">暂无车间数据</p>
          </div>
        </template>
      </v-data-table>
    </v-card>

    <!-- Add/Edit Dialog -->
    <v-dialog v-model="showAddDialog" max-width="600" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-plus" class="mr-2" />
          新增车间
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="closeDialog" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-form>
            <v-text-field v-model="formData.code" label="车间编码" :rules="[v => !!v || '请输入车间编码']" required />
            <v-text-field v-model="formData.name" label="车间名称" :rules="[v => !!v || '请输入车间名称']" required />
            <v-text-field v-model="formData.location" label="位置" />
            <v-text-field v-model="formData.manager" label="负责人" />
            <v-text-field v-model="formData.contact" label="联系电话" />
            <v-textarea v-model="formData.description" label="描述" rows="3" />
            <v-number-input v-model.number="formData.sort_order" label="排序" :min="0" controlVariant="stacked" />
            <v-select v-model="formData.status" :items="statusOptions" label="状态" />
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
          编辑车间
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="closeDialog" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-form>
            <v-text-field v-model="formData.code" label="车间编码" :rules="[v => !!v || '请输入车间编码']" required />
            <v-text-field v-model="formData.name" label="车间名称" :rules="[v => !!v || '请输入车间名称']" required />
            <v-text-field v-model="formData.location" label="位置" />
            <v-text-field v-model="formData.manager" label="负责人" />
            <v-text-field v-model="formData.contact" label="联系电话" />
            <v-textarea v-model="formData.description" label="描述" rows="3" />
            <v-number-input v-model.number="formData.sort_order" label="排序" :min="0" controlVariant="stacked" />
            <v-select v-model="formData.status" :items="statusOptions" label="状态" />
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
          车间详情
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="showViewDialog = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-table density="compact">
            <tbody>
              <tr><td class="text-medium-emphasis" style="width:120px">ID</td><td>{{ viewData.id }}</td></tr>
              <tr><td class="text-medium-emphasis">车间编码</td><td><v-chip size="small" variant="tonal" color="primary">{{ viewData.code }}</v-chip></td></tr>
              <tr><td class="text-medium-emphasis">车间名称</td><td>{{ viewData.name }}</td></tr>
              <tr><td class="text-medium-emphasis">位置</td><td>{{ viewData.location || '-' }}</td></tr>
              <tr><td class="text-medium-emphasis">负责人</td><td>{{ viewData.manager || '-' }}</td></tr>
              <tr><td class="text-medium-emphasis">联系电话</td><td>{{ viewData.contact || '-' }}</td></tr>
              <tr><td class="text-medium-emphasis">状态</td><td><v-chip :color="viewData.status === 'active' ? 'success' : 'error'" size="small" variant="tonal">{{ viewData.status === 'active' ? '启用' : '禁用' }}</v-chip></td></tr>
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useMessage, useConfirm } from '@/composables/useMessage'
import { workshopAPI } from '@/api/index'
import { formatDateTime } from '@/utils/datetime'
import { usePagination } from '@/composables/usePagination'
import { useListLoader } from '@/composables/useListLoader'
import { useCrudDialog } from '@/composables/useCrudDialog'

const message = useMessage()
const confirmDialog = useConfirm()

const showSearch = ref(true)

const statusOptions = [
  { title: '全部', value: '' },
  { title: '启用', value: 'active' },
  { title: '禁用', value: 'inactive' },
]

const headers = [
  { title: 'ID', key: 'id', width: '70px' },
  { title: '车间编码', key: 'code' },
  { title: '车间名称', key: 'name' },
  { title: '位置', key: 'location' },
  { title: '负责人', key: 'manager' },
  { title: '联系电话', key: 'contact' },
  { title: '状态', key: 'status' },
  { title: '排序', key: 'sort_order', width: '70px' },
  { title: '创建时间', key: 'created_at' },
  { title: '操作', key: 'actions', sortable: false, width: '160px' },
]

const queryParams = reactive({ name: '', code: '', status: '' })

const { page, pageSize, total, pageStart, pageEnd, pageSizes, setTotal, reset: resetPage } = usePagination()

const { loading, list, load } = useListLoader(workshopAPI.list, {
  onSuccess: (res, totalCount) => setTotal(totalCount),
  onError: () => message.error('加载车间列表失败')
})

const {
  showAddDialog, showEditDialog, showViewDialog,
  saving, formData, formErrors, viewData,
  openAdd, openEdit, openView, closeDialog, resetForm, save
} = useCrudDialog({
  createFn: workshopAPI.create,
  updateFn: workshopAPI.update,
  validateFn: (data) => {
    const errors = {}
    if (!data.code?.trim()) errors.code = '请输入车间编码'
    if (!data.name?.trim()) errors.name = '请输入车间名称'
    return { valid: Object.keys(errors).length === 0, errors }
  },
  onSuccess: () => {
    message.success(showEditDialog.value ? '车间更新成功' : '车间创建成功')
    handleSearch()
  },
  onError: (detail) => message.error('保存失败：' + detail),
  defaults: { id: null, code: '', name: '', description: '', location: '', manager: '', contact: '', status: 'active', sort_order: 0 }
})

function handleSearch() {
  load({ ...queryParams, page: page.value, page_size: pageSize.value })
}

function resetQuery() {
  Object.assign(queryParams, { name: '', code: '', status: '' })
  resetPage()
  handleSearch()
}

async function handleSave() {
  await save()
}

async function toggleStatus(item) {
  try {
    const newStatus = item.status === 'active' ? 'inactive' : 'active'
    await workshopAPI.update(item.id, { status: newStatus })
    item.status = newStatus
    message.success(`车间已${newStatus === 'active' ? '启用' : '禁用'}`)
  } catch (e) {
    message.error('状态更新失败：' + (e.response?.data?.detail || e.message))
  }
}

async function handleDelete(item) {
  const ok = await confirmDialog(`确定删除车间"${item.name}"吗？`, '确认删除', 'warning')
  if (!ok) return
  try {
    await workshopAPI.delete(item.id)
    message.success('车间已删除')
    handleSearch()
  } catch (e) {
    message.error('删除失败：' + (e.response?.data?.detail || e.message))
  }
}

onMounted(() => handleSearch())
</script>
