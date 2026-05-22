<template>
  <div>
    <!-- Header -->
    <v-toolbar flat color="transparent" class="mb-4">
      <div>
        <div class="text-h5 font-weight-bold d-flex align-center ga-2">
          <v-icon icon="mdi-sitemap" color="primary" />
          生产流程管理
        </div>
        <div class="text-caption text-medium-emphasis mt-1">首页 / 生产流程管理</div>
      </div>
    </v-toolbar>

    <!-- Tabs -->
    <v-tabs v-model="activeTab" bg-color="transparent" class="mb-4">
      <v-tab value="templates" prepend-icon="mdi-file-tree">工艺路线模板</v-tab>
      <v-tab value="instances" prepend-icon="mdi-play-circle-outline">流程执行跟踪</v-tab>
    </v-tabs>

    <v-tabs-window v-model="activeTab">
      <!-- Tab 1: 模板编辑器 -->
      <v-tabs-window-item value="templates">
        <v-row dense>
          <!-- 左侧模板列表 -->
          <v-col cols="2">
            <v-card height="calc(100vh - 220px)">
              <v-card-title class="text-subtitle-2 d-flex align-center">
                模板列表
                <v-spacer />
                <v-btn size="x-small" icon="mdi-plus" color="primary" @click="openAddFlow" />
              </v-card-title>
              <v-divider />
              <v-text-field
                v-model="templateSearch"
                placeholder="搜索..."
                prepend-inner-icon="mdi-magnify"
                density="compact"
                variant="outlined"
                hide-details
                class="pa-2"
                clearable
              />
              <v-list density="compact" class="overflow-y" style="height: calc(100vh - 330px)">
                <v-list-item
                  v-for="flow in filteredTemplates"
                  :key="flow.id"
                  :active="selectedFlowId === flow.id"
                  @click="selectFlow(flow.id)"
                  :title="flow.flow_name"
                  :subtitle="flow.flow_code"
                >
                  <template #append>
                    <v-chip :color="flow.status === 'active' ? 'success' : 'grey'" size="x-small" variant="flat">
                      {{ flow.node_count || 0 }}节点
                    </v-chip>
                  </template>
                </v-list-item>
              </v-list>
            </v-card>
          </v-col>

          <!-- 中央画布 -->
          <v-col cols="7">
            <v-card height="calc(100vh - 220px)">
              <v-card-title class="text-subtitle-2 d-flex align-center ga-2 py-1">
                <v-btn size="small" variant="tonal" color="orange" @click="addNode('process')">
                  <v-icon icon="mdi-cog" start /> 添加工序
                </v-btn>
                <v-btn size="small" variant="tonal" color="blue" @click="openMaterialSelector">
                  <v-icon icon="mdi-package-variant" start /> 添加物料
                </v-btn>
                <v-divider vertical class="mx-2" />
                <v-btn size="small" variant="outlined" @click="fitView">适应画布</v-btn>
                <v-btn size="small" variant="outlined" @click="clearAll">清空</v-btn>
                <v-spacer />
                <v-btn size="small" color="primary" prepend-icon="mdi-content-save" @click="saveFlow">
                  保存
                </v-btn>
              </v-card-title>
              <v-divider />
              <div style="height: calc(100vh - 280px)">
                <VueFlow
                  ref="vueFlowRef"
                  v-model:nodes="nodes"
                  v-model:edges="edges"
                  :node-types="nodeTypes"
                  :default-viewport="{ zoom: 1, x: 0, y: 0 }"
                  :snap-to-grid="true"
                  :snap-grid="[10, 10]"
                  fit-view-on-init
                  @node-click="onNodeClick"
                  @pane-click="onPaneClick"
                  @connect="onConnect"
                >
                  <Background />
                  <Controls />
                  <MiniMap />
                </VueFlow>
              </div>
            </v-card>
          </v-col>

          <!-- 右侧属性面板 -->
          <v-col cols="3">
            <v-card height="calc(100vh - 220px)">
              <v-card-title class="text-subtitle-2">属性面板</v-card-title>
              <v-divider />
              <v-card-text class="overflow-y" style="height: calc(100vh - 280px)">
                <!-- 模板信息 -->
                <div v-if="!selectedNodeId">
                  <div class="text-subtitle-2 mb-2">模板信息</div>
                  <v-text-field v-model="flowMeta.flow_code" label="流程编码 *" density="compact" />
                  <v-text-field v-model="flowMeta.flow_name" label="流程名称 *" density="compact" />
                  <v-textarea v-model="flowMeta.description" label="描述" density="compact" rows="2" />
                  <v-select v-model="flowMeta.status" :items="[{title:'启用',value:'active'},{title:'停用',value:'inactive'}]" label="状态" density="compact" />
                </div>

                <!-- 节点属性 -->
                <div v-else>
                  <div class="d-flex align-center mb-2">
                    <v-chip :color="selectedNodeData?.type === 'process' ? 'orange' : 'blue'" size="small" variant="flat">
                      {{ selectedNodeData?.type === 'process' ? '工序' : '物料' }}
                    </v-chip>
                    <v-spacer />
                    <v-btn size="x-small" icon="mdi-delete" color="error" variant="text" @click="deleteSelectedNode" />
                  </div>

                  <!-- 工序节点属性 -->
                  <template v-if="selectedNodeData?.type === 'process'">
                    <v-text-field v-model="selectedNodeData.data.label" label="工序名称 *" density="compact" @update:model-value="updateNodeData" />
                    <v-text-field v-model="selectedNodeData.data.process_code" label="工序编码" density="compact" @update:model-value="updateNodeData" />
                    <v-text-field v-model="selectedNodeData.data.device_type" label="设备类型" density="compact" @update:model-value="updateNodeData" />
                    <v-text-field v-model.number="selectedNodeData.data.expected_duration_min" label="预计工时(分钟)" density="compact" type="number" @update:model-value="updateNodeData" />
                    <v-textarea v-model="selectedNodeData.data.description" label="描述" density="compact" rows="2" @update:model-value="updateNodeData" />
                  </template>

                  <!-- 物料节点属性 -->
                  <template v-if="selectedNodeData?.type === 'material'">
                    <div class="d-flex align-center mb-2">
                      <span class="text-caption text-medium-emphasis">从物料库选择：</span>
                      <v-btn size="x-small" variant="tonal" color="blue" class="ml-auto" @click="openMaterialSelectorForEdit">选择物料</v-btn>
                    </div>
                    <v-text-field v-model="selectedNodeData.data.label" label="物料名称 *" density="compact" @update:model-value="updateNodeData" />
                    <v-text-field v-model="selectedNodeData.data.material_code" label="物料编码(U9)" density="compact" readonly @update:model-value="updateNodeData" />
                    <v-text-field v-model="selectedNodeData.data.part_number" label="规格型号/零件号" density="compact" @update:model-value="updateNodeData" />
                    <v-text-field v-model.number="selectedNodeData.data.quantity" label="数量" density="compact" type="number" @update:model-value="updateNodeData" />
                  </template>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-tabs-window-item>

      <!-- Tab 2: 流程执行跟踪 -->
      <v-tabs-window-item value="instances">
        <!-- 统计卡片 -->
        <v-row class="mb-4">
          <v-col cols="6" sm="3">
            <v-card color="primary" variant="tonal">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ instanceStats.total }}</div>
                <div class="text-caption">总实例数</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" sm="3">
            <v-card color="info" variant="tonal">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ instanceStats.in_progress }}</div>
                <div class="text-caption">进行中</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" sm="3">
            <v-card color="success" variant="tonal">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ instanceStats.completed }}</div>
                <div class="text-caption">已完成</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" sm="3">
            <v-card color="warning" variant="tonal">
              <v-card-text class="text-center">
                <div class="text-h4 font-weight-bold">{{ instanceStats.paused }}</div>
                <div class="text-caption">已暂停</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- 筛选 + 操作栏 -->
        <v-card class="mb-4">
          <v-card-text>
            <v-row dense>
              <v-col cols="12" sm="2">
                <v-text-field v-model="instanceFilters.record_date" label="日期" type="date" density="compact" hide-details clearable />
              </v-col>
              <v-col cols="12" sm="2">
                <v-text-field v-model="instanceFilters.doc_no" label="订单号" density="compact" hide-details clearable />
              </v-col>
              <v-col cols="12" sm="2">
                <v-text-field v-model="instanceFilters.part_number" label="零件号" density="compact" hide-details clearable />
              </v-col>
              <v-col cols="12" sm="2">
                <v-select v-model="instanceFilters.status" :items="instanceStatusOptions" label="状态" density="compact" hide-details clearable />
              </v-col>
              <v-col cols="12" sm="1">
                <v-btn color="primary" icon="mdi-magnify" @click="loadInstances" />
              </v-col>
              <v-col cols="12" sm="3" class="text-right">
                <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreateInstance">创建实例</v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- 实例列表 -->
        <v-card>
          <v-data-table-server
            :headers="instanceHeaders"
            :items="instances"
            :items-length="instanceTotal"
            :loading="instanceLoading"
            :items-per-page="instancePageSize"
            @update:options="loadInstances"
            hover
          >
            <template #item.flow_name="{ item }">{{ getFlowName(item.flow_id) }}</template>
            <template #item.progress="{ item }">
              <div class="d-flex align-center ga-2" style="min-width:120px">
                <v-progress-linear :model-value="getProgress(item)" color="primary" height="8" rounded />
                <span class="text-caption">{{ getProgressText(item) }}</span>
              </div>
            </template>
            <template #item.status="{ item }">
              <v-chip :color="getStatusColor(item.status)" size="small" variant="flat">{{ getStatusLabel(item.status) }}</v-chip>
            </template>
            <template #item.actions="{ item }">
              <v-btn size="x-small" icon="mdi-eye" variant="text" color="primary" @click="viewInstance(item)" />
              <v-btn size="x-small" icon="mdi-check-all" variant="text" color="success" @click="completeInstance(item)" />
              <v-btn size="x-small" icon="mdi-delete" variant="text" color="error" @click="deleteInstance(item)" />
            </template>
          </v-data-table-server>
        </v-card>

        <!-- 实例详情对话框（流程图视图） -->
        <v-dialog v-model="instanceDetailDialog" max-width="1200" persistent>
          <v-card v-if="selectedInstance" height="700">
            <v-card-title class="d-flex align-center">
              <span>流程执行详情 #{{ selectedInstance.id }}</span>
              <v-spacer />
              <v-btn icon="mdi-close" variant="text" @click="instanceDetailDialog = false" />
            </v-card-title>
            <v-divider />
            <v-card-text class="pa-0 d-flex" style="height: 630px">
              <!-- 流程图 -->
              <div style="flex: 1">
                <VueFlow
                  :nodes="instanceNodes"
                  :edges="instanceEdges"
                  :node-types="nodeTypes"
                  :default-viewport="{ zoom: 0.9, x: 0, y: 0 }"
                  fit-view-on-init
                  :nodes-draggable="false"
                  :nodes-connectable="false"
                  @node-click="onInstanceNodeClick"
                >
                  <Background />
                  <Controls />
                </VueFlow>
              </div>
              <!-- 节点状态面板 -->
              <v-card width="300" class="border-s" tile>
                <v-card-title class="text-subtitle-2">节点状态</v-card-title>
                <v-divider />
                <v-card-text class="overflow-y" style="height: 570px">
                  <div v-for="node in instanceFlowNodes" :key="node.id" class="mb-2">
                    <v-card
                      variant="outlined"
                      :color="getNodeStatusColor(instanceNodeStatuses[node.id])"
                      @click="selectedInstanceNodeId = node.id"
                      :class="{ 'border-lg': selectedInstanceNodeId === node.id }"
                    >
                      <v-card-text class="pa-2">
                        <div class="d-flex align-center">
                          <v-chip :color="node.type === 'process' ? 'orange' : 'blue'" size="x-small" variant="flat" class="mr-2">
                            {{ node.type === 'process' ? '工序' : '物料' }}
                          </v-chip>
                          <span class="text-body-2 font-weight-bold">{{ node.data?.label }}</span>
                        </div>
                        <div class="d-flex align-center mt-1 ga-1">
                          <v-chip :color="getNodeStatusColor(instanceNodeStatuses[node.id])" size="x-small" variant="flat">
                            {{ getNodeStatusLabel(instanceNodeStatuses[node.id]) }}
                          </v-chip>
                          <v-spacer />
                          <v-btn-group density="compact" variant="outlined" size="x-small">
                            <v-btn @click.stop="updateInstanceNodeStatus(node.id, 'pending')">待</v-btn>
                            <v-btn @click.stop="updateInstanceNodeStatus(node.id, 'in_progress')">中</v-btn>
                            <v-btn @click.stop="completeInstanceNode(node.id)">完</v-btn>
                          </v-btn-group>
                        </div>
                      </v-card-text>
                    </v-card>
                  </div>
                </v-card-text>
              </v-card>
            </v-card-text>
          </v-card>
        </v-dialog>

        <!-- 创建实例对话框 -->
        <v-dialog v-model="createInstanceDialog" max-width="500">
          <v-card>
            <v-card-title>创建流程实例</v-card-title>
            <v-divider />
            <v-card-text>
              <v-select v-model="newInstanceData.flow_id" :items="templateOptions" item-title="label" item-value="value" label="工艺路线模板 *" density="compact" />
              <v-text-field v-model="newInstanceData.doc_no" label="订单单据号" density="compact" />
              <v-text-field v-model="newInstanceData.part_number" label="零件号" density="compact" />
              <v-text-field v-model="newInstanceData.device_code" label="主设备" density="compact" />
              <v-text-field v-model.number="newInstanceData.planned_qty" label="计划数量" density="compact" type="number" />
              <v-text-field v-model="newInstanceData.record_date" label="日期" type="date" density="compact" />
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn variant="outlined" @click="createInstanceDialog = false">取消</v-btn>
              <v-btn color="primary" @click="submitCreateInstance">创建</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <!-- 物料选择对话框 -->
        <v-dialog v-model="materialSelectorDialog" max-width="700">
          <v-card>
            <v-card-title class="d-flex align-center">
              选择物料
              <v-spacer />
              <v-btn icon="mdi-close" variant="text" @click="materialSelectorDialog = false" />
            </v-card-title>
            <v-divider />
            <v-card-text>
              <v-text-field
                v-model="materialSearch"
                placeholder="搜索物料名称、编码、规格型号..."
                prepend-inner-icon="mdi-magnify"
                density="compact"
                variant="outlined"
                hide-details
                clearable
                class="mb-3"
                @update:model-value="searchMaterials"
              />
              <v-data-table-server
                :headers="materialHeaders"
                :items="materialList"
                :items-length="materialTotal"
                :loading="materialLoading"
                :items-per-page="materialPageSize"
                hover
                density="compact"
                @update:options="loadMaterials"
              >
                <template #item.material_type="{ item }">
                  <v-chip :color="getMaterialTypeColor(item.material_type)" size="x-small" variant="flat">
                    {{ getMaterialTypeLabel(item.material_type) }}
                  </v-chip>
                </template>
                <template #item.actions="{ item }">
                  <v-btn size="x-small" color="primary" variant="tonal" @click="selectMaterial(item)">选择</v-btn>
                </template>
              </v-data-table-server>
            </v-card-text>
          </v-card>
        </v-dialog>
      </v-tabs-window-item>
    </v-tabs-window>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, markRaw } from 'vue'
import { VueFlow, useVueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import { productionFlowAPI, productionFlowInstanceAPI, materialAPI } from '@/api'
import ProcessNode from './flow/ProcessNode.vue'
import MaterialNode from './flow/MaterialNode.vue'

const nodeTypes = {
  process: markRaw(ProcessNode),
  material: markRaw(MaterialNode),
}

const activeTab = ref('templates')

// ============ Vue Flow ============
const vueFlowRef = ref(null)
const nodes = ref([])
const edges = ref([])
const selectedNodeId = ref(null)

const { fitView: ffv, addNodes: fan, removeNodes: frn, getNodes, getEdges } = useVueFlow({ id: 'template-editor' })

function fitView() { ffv() }

function addNode(type) {
  const id = `${type}_${Date.now()}`
  const label = type === 'process' ? '新工序' : '新物料'
  const newNode = {
    id,
    type,
    position: { x: 200 + Math.random() * 200, y: 100 + Math.random() * 200 },
    data: { label, ...(type === 'process' ? { process_code: '', device_type: '', expected_duration_min: null, description: '' } : { material_code: '', part_number: '', quantity: null }) },
  }
  nodes.value = [...nodes.value, newNode]
  selectedNodeId.value = id
}

function onNodeClick({ node }) {
  selectedNodeId.value = node.id
}

function onPaneClick() {
  selectedNodeId.value = null
}

function onConnect(params) {
  const id = `e_${params.source}_${params.target}_${Date.now()}`
  edges.value = [...edges.value, { ...params, id, animated: true }]
}

function deleteSelectedNode() {
  if (!selectedNodeId.value) return
  nodes.value = nodes.value.filter(n => n.id !== selectedNodeId.value)
  edges.value = edges.value.filter(e => e.source !== selectedNodeId.value && e.target !== selectedNodeId.value)
  selectedNodeId.value = null
}

function clearAll() {
  if (!confirm('确认清空所有节点和连线？')) return
  nodes.value = []
  edges.value = []
  selectedNodeId.value = null
}

const selectedNodeData = computed(() => {
  if (!selectedNodeId.value) return null
  return nodes.value.find(n => n.id === selectedNodeId.value)
})

function updateNodeData() {
  // Vue reactivity handles it automatically via v-model
}

// ============ 模板管理 ============
const templates = ref([])
const templateSearch = ref('')
const selectedFlowId = ref(null)
const flowMeta = reactive({ flow_code: '', flow_name: '', description: '', status: 'active' })

const filteredTemplates = computed(() => {
  if (!templateSearch.value) return templates.value
  const kw = templateSearch.value.toLowerCase()
  return templates.value.filter(f => f.flow_name.toLowerCase().includes(kw) || f.flow_code.toLowerCase().includes(kw))
})

const templateOptions = computed(() =>
  templates.value.filter(f => f.status === 'active').map(f => ({ label: `${f.flow_name} (${f.flow_code})`, value: f.id }))
)

async function loadTemplates() {
  try {
    const res = await productionFlowAPI.templates()
    templates.value = res.data
  } catch (e) { console.error('加载模板失败', e) }
}

async function selectFlow(id) {
  selectedFlowId.value = id
  selectedNodeId.value = null
  try {
    const res = await productionFlowAPI.get(id)
    const flow = res.data
    flowMeta.flow_code = flow.flow_code
    flowMeta.flow_name = flow.flow_name
    flowMeta.description = flow.description
    flowMeta.status = flow.status
    nodes.value = flow.nodes_data || []
    edges.value = flow.edges_data || []
  } catch (e) { console.error('加载模板详情失败', e) }
}

function openAddFlow() {
  selectedFlowId.value = null
  selectedNodeId.value = null
  flowMeta.flow_code = ''
  flowMeta.flow_name = ''
  flowMeta.description = ''
  flowMeta.status = 'active'
  nodes.value = []
  edges.value = []
}

// ============ 物料选择 ============
const materialSelectorDialog = ref(false)
const materialSearch = ref('')
const materialList = ref([])
const materialTotal = ref(0)
const materialLoading = ref(false)
const materialPageSize = ref(10)
const materialPage = ref(1)
const materialSelectorMode = ref('add') // 'add' = 添加新节点, 'edit' = 编辑已有节点

const materialHeaders = [
  { title: '物料名称', key: 'product_name' },
  { title: 'U9编码', key: 'u9_material_code', width: 120 },
  { title: '规格型号', key: 'part_number', width: 120 },
  { title: '类型', key: 'material_type', width: 80 },
  { title: '操作', key: 'actions', width: 70, sortable: false },
]

function openMaterialSelector() {
  materialSelectorMode.value = 'add'
  materialSearch.value = ''
  materialList.value = []
  materialTotal.value = 0
  materialSelectorDialog.value = true
  loadMaterials({ page: 1, itemsPerPage: materialPageSize.value })
}

function openMaterialSelectorForEdit() {
  materialSelectorMode.value = 'edit'
  materialSearch.value = ''
  materialList.value = []
  materialTotal.value = 0
  materialSelectorDialog.value = true
  loadMaterials({ page: 1, itemsPerPage: materialPageSize.value })
}

async function loadMaterials({ page = 1, itemsPerPage = 10 }) {
  materialLoading.value = true
  materialPage.value = page
  materialPageSize.value = itemsPerPage
  try {
    const params = { page, page_size: itemsPerPage, status: 'active' }
    if (materialSearch.value) params.product_name = materialSearch.value
    const res = await materialAPI.getMaterials(params)
    materialList.value = res.data.items
    materialTotal.value = res.data.total
  } catch (e) {
    console.error('加载物料失败', e)
  } finally {
    materialLoading.value = false
  }
}

function searchMaterials() {
  loadMaterials({ page: 1, itemsPerPage: materialPageSize.value })
}

function getMaterialTypeColor(type) {
  const map = { product: 'primary', semi_finished: 'teal', material: 'orange', auxiliary: 'grey' }
  return map[type] || 'grey'
}

function getMaterialTypeLabel(type) {
  const map = { product: '产品', semi_finished: '半成品', material: '原材料', auxiliary: '辅料' }
  return map[type] || type
}

function selectMaterial(item) {
  materialSelectorDialog.value = false

  if (materialSelectorMode.value === 'add') {
    // 添加新物料节点
    const id = `material_${Date.now()}`
    const newNode = {
      id,
      type: 'material',
      position: { x: 200 + Math.random() * 200, y: 100 + Math.random() * 200 },
      data: {
        label: item.product_name || item.u9_material_code,
        material_code: item.u9_material_code || '',
        part_number: item.part_number || '',
        quantity: null,
        material_id: item.id,
      },
    }
    nodes.value = [...nodes.value, newNode]
    selectedNodeId.value = id
  } else {
    // 编辑已有节点
    if (selectedNodeData.value && selectedNodeData.value.type === 'material') {
      selectedNodeData.value.data.label = item.product_name || item.u9_material_code
      selectedNodeData.value.data.material_code = item.u9_material_code || ''
      selectedNodeData.value.data.part_number = item.part_number || ''
      selectedNodeData.value.data.material_id = item.id
    }
  }
}

async function saveFlow() {
  if (!flowMeta.flow_code || !flowMeta.flow_name) {
    alert('请填写流程编码和名称')
    return
  }
  const payload = { ...flowMeta, nodes_data: nodes.value, edges_data: edges.value }
  try {
    if (selectedFlowId.value) {
      await productionFlowAPI.update(selectedFlowId.value, payload)
    } else {
      const res = await productionFlowAPI.create(payload)
      selectedFlowId.value = res.data.id
    }
    await loadTemplates()
    alert('保存成功')
  } catch (e) {
    alert('保存失败: ' + (e.response?.data?.detail || e.message))
  }
}

// ============ 实例跟踪 ============
const instances = ref([])
const instanceTotal = ref(0)
const instanceLoading = ref(false)
const instancePageSize = ref(20)
const instanceStats = reactive({ total: 0, in_progress: 0, completed: 0, paused: 0, cancelled: 0 })
const instanceFilters = reactive({ record_date: '', doc_no: '', part_number: '', status: '' })
const instanceDetailDialog = ref(false)
const selectedInstance = ref(null)
const selectedInstanceNodeId = ref(null)
const createInstanceDialog = ref(false)
const newInstanceData = reactive({ flow_id: null, doc_no: '', part_number: '', device_code: '', planned_qty: null, record_date: '' })

const instanceHeaders = [
  { title: 'ID', key: 'id', width: 60 },
  { title: '工艺路线', key: 'flow_name' },
  { title: '订单号', key: 'doc_no' },
  { title: '零件号', key: 'part_number' },
  { title: '进度', key: 'progress', sortable: false },
  { title: '状态', key: 'status' },
  { title: '操作', key: 'actions', sortable: false, width: 120 },
]

const instanceStatusOptions = [
  { title: '进行中', value: 'in_progress' },
  { title: '已完成', value: 'completed' },
  { title: '已暂停', value: 'paused' },
]

function getFlowName(flowId) {
  const f = templates.value.find(t => t.id === flowId)
  return f ? f.flow_name : `#${flowId}`
}

function getProgress(item) {
  const ns = item.node_statuses || {}
  const vals = Object.values(ns)
  if (vals.length === 0) return 0
  const done = vals.filter(s => s === 'completed' || s === 'skipped').length
  return Math.round(done / vals.length * 100)
}

function getProgressText(item) {
  const ns = item.node_statuses || {}
  const vals = Object.values(ns)
  const done = vals.filter(s => s === 'completed' || s === 'skipped').length
  return `${done}/${vals.length}`
}

function getStatusColor(s) {
  return { in_progress: 'info', completed: 'success', paused: 'warning', cancelled: 'grey' }[s] || 'grey'
}
function getStatusLabel(s) {
  return { in_progress: '进行中', completed: '已完成', paused: '已暂停', cancelled: '已取消' }[s] || s
}
function getNodeStatusColor(s) {
  return { pending: 'grey-lighten-1', in_progress: 'info', completed: 'success', skipped: 'warning' }[s] || 'grey-lighten-1'
}
function getNodeStatusLabel(s) {
  return { pending: '待处理', in_progress: '进行中', completed: '已完成', skipped: '已跳过' }[s] || s || '待处理'
}

// 实例流程图数据
const instanceFlowNodes = computed(() => {
  if (!selectedInstance.value) return []
  const flow = templates.value.find(t => t.id === selectedInstance.value.flow_id)
  // 需要从API获取完整模板数据
  return []
})

const instanceNodeStatuses = computed(() => selectedInstance.value?.node_statuses || {})

// 实例流程图节点（带状态颜色）
const instanceNodes = ref([])
const instanceEdges = ref([])

async function loadInstanceFlowView() {
  if (!selectedInstance.value) return
  try {
    const flowRes = await productionFlowAPI.get(selectedInstance.value.flow_id)
    const flow = flowRes.data
    const ns = selectedInstance.value.node_statuses || {}

    instanceNodes.value = (flow.nodes_data || []).map(node => ({
      ...node,
      style: {
        ...node.style,
        border: `3px solid ${getNodeStatusBorderColor(ns[node.id])}`,
        background: getNodeStatusBg(ns[node.id]),
      },
    }))
    instanceEdges.value = flow.edges_data || []
  } catch (e) {
    console.error('加载实例流程图失败', e)
  }
}

function getNodeStatusBorderColor(status) {
  return { completed: '#4caf50', in_progress: '#2196f3', skipped: '#ff9800' }[status] || '#bdbdbd'
}

function getNodeStatusBg(status) {
  return { completed: '#e8f5e9', in_progress: '#e3f2fd', skipped: '#fff3e0' }[status] || '#f5f5f5'
}

function onInstanceNodeClick({ node }) {
  selectedInstanceNodeId.value = node.id
}

async function updateInstanceNodeStatus(nodeId, status) {
  if (!selectedInstance.value) return
  try {
    const res = await productionFlowInstanceAPI.updateStep(selectedInstance.value.id, nodeId, { status })
    selectedInstance.value = res.data
    await loadInstanceFlowView()
    await loadInstances()
  } catch (e) { alert('更新失败: ' + (e.response?.data?.detail || e.message)) }
}

async function completeInstanceNode(nodeId) {
  if (!selectedInstance.value) return
  try {
    const res = await productionFlowInstanceAPI.completeNode(selectedInstance.value.id, nodeId)
    selectedInstance.value = res.data
    await loadInstanceFlowView()
    await loadInstances()
  } catch (e) { alert('完成失败: ' + (e.response?.data?.detail || e.message)) }
}

async function loadInstances() {
  instanceLoading.value = true
  try {
    const params = { page: 1, page_size: instancePageSize.value }
    if (instanceFilters.record_date) params.record_date = instanceFilters.record_date
    if (instanceFilters.doc_no) params.doc_no = instanceFilters.doc_no
    if (instanceFilters.part_number) params.part_number = instanceFilters.part_number
    if (instanceFilters.status) params.status = instanceFilters.status
    const res = await productionFlowInstanceAPI.list(params)
    instances.value = res.data.items
    instanceTotal.value = res.data.total
  } catch (e) { console.error('加载实例失败', e) }
  finally { instanceLoading.value = false }
}

async function loadInstanceStats() {
  try {
    const res = await productionFlowInstanceAPI.stats()
    Object.assign(instanceStats, res.data)
  } catch (e) { console.error('加载统计失败', e) }
}

async function viewInstance(item) {
  try {
    const res = await productionFlowInstanceAPI.get(item.id)
    selectedInstance.value = res.data
    instanceDetailDialog.value = true
    await loadInstanceFlowView()
  } catch (e) { console.error('加载详情失败', e) }
}

async function completeInstance(item) {
  if (!confirm('确认完成整个流程？')) return
  try {
    await productionFlowInstanceAPI.complete(item.id)
    await loadInstances()
    await loadInstanceStats()
  } catch (e) { alert('完成失败: ' + (e.response?.data?.detail || e.message)) }
}

async function deleteInstance(item) {
  if (!confirm('确认删除？')) return
  try {
    await productionFlowInstanceAPI.delete(item.id)
    await loadInstances()
    await loadInstanceStats()
  } catch (e) { alert('删除失败: ' + (e.response?.data?.detail || e.message)) }
}

function openCreateInstance() {
  newInstanceData.flow_id = null
  newInstanceData.doc_no = ''
  newInstanceData.part_number = ''
  newInstanceData.device_code = ''
  newInstanceData.planned_qty = null
  newInstanceData.record_date = new Date().toISOString().slice(0, 10)
  createInstanceDialog.value = true
}

async function submitCreateInstance() {
  if (!newInstanceData.flow_id) { alert('请选择模板'); return }
  try {
    await productionFlowInstanceAPI.create({ ...newInstanceData })
    createInstanceDialog.value = false
    await loadInstances()
    await loadInstanceStats()
  } catch (e) { alert('创建失败: ' + (e.response?.data?.detail || e.message)) }
}

// ============ Init ============
onMounted(async () => {
  await loadTemplates()
  await loadInstances()
  await loadInstanceStats()
})
</script>

<style>
@import '@vue-flow/core/dist/style.css';
@import '@vue-flow/core/dist/theme-default.css';
@import '@vue-flow/controls/dist/style.css';
@import '@vue-flow/minimap/dist/style.css';
</style>
