<template>
  <div class="mbom-editor-layout">
    <!-- ==================== Left Sidebar ==================== -->
    <div class="mbom-sidebar">
      <!-- Control Panel -->
      <v-card class="mb-2" variant="outlined">
        <v-card-title
          class="text-subtitle-2 d-flex align-center pa-2 cursor-pointer"
          @click="showControlPanel = !showControlPanel"
        >
          <v-icon icon="mdi-gamepad-outline" size="18" class="mr-1" />
          控制面板
          <v-spacer />
          <v-icon :icon="showControlPanel ? 'mdi-chevron-up' : 'mdi-chevron-down'" size="18" />
        </v-card-title>
        <v-divider v-if="showControlPanel" />
        <v-card-text v-if="showControlPanel" class="pa-2">
          <div class="d-flex flex-wrap ga-1 mb-2">
            <v-btn size="small" variant="tonal" prepend-icon="mdi-magnify-plus" @click="zoomIn">放大</v-btn>
            <v-btn size="small" variant="tonal" prepend-icon="mdi-magnify-minus" @click="zoomOut">缩小</v-btn>
            <v-btn size="small" variant="tonal" prepend-icon="mdi-fit-to-page-outline" @click="fitViewAll">适应</v-btn>
          </div>
          <div class="d-flex flex-wrap ga-1 mb-2">
            <v-btn size="small" variant="tonal" prepend-icon="mdi-refresh" @click="loadTree">刷新</v-btn>
            <v-btn size="small" variant="tonal" prepend-icon="mdi-expand-all" @click="expandAllNodes">展开全部</v-btn>
            <v-btn size="small" variant="tonal" prepend-icon="mdi-collapse-all-outline" @click="collapseAllNodes">折叠全部</v-btn>
          </div>
          <v-text-field
            v-model="nodeSearch"
            density="compact"
            variant="outlined"
            prepend-inner-icon="mdi-magnify"
            placeholder="搜索节点..."
            clearable
            hide-details
            class="mb-2"
            @update:model-value="onNodeSearch"
          />
          <div class="d-flex align-center ga-2 text-caption text-medium-emphasis">
            <v-icon icon="mdi-information-outline" size="14" />
            <span>节点: {{ nodes.length }} | 连线: {{ edges.length }}</span>
          </div>
        </v-card-text>
      </v-card>

      <!-- Materials Panel -->
      <v-card variant="outlined" class="flex-grow-1 d-flex flex-column" style="min-height: 0;">
        <v-card-title
          class="text-subtitle-2 d-flex align-center pa-2 cursor-pointer"
          @click="showMaterialsPanel = !showMaterialsPanel"
        >
          <v-icon icon="mdi-package-variant" size="18" class="mr-1" />
          物料面板
          <v-spacer />
          <v-icon :icon="showMaterialsPanel ? 'mdi-chevron-up' : 'mdi-chevron-down'" size="18" />
        </v-card-title>
        <v-divider v-if="showMaterialsPanel" />
        <div v-if="showMaterialsPanel" class="d-flex flex-column" style="flex: 1; min-height: 0;">
          <v-tabs v-model="materialTab" density="compact" color="primary" class="flex-grow-0">
            <v-tab value="bomitems" size="small">当前子项</v-tab>
            <v-tab value="products" size="small">物料库</v-tab>
          </v-tabs>
          <v-tabs-window v-model="materialTab" style="flex: 1; overflow-y: auto;">
            <!-- BOM Items List -->
            <v-tabs-window-item value="bomitems">
              <div v-if="bomItemsLoading" class="text-center pa-4">
                <v-progress-circular indeterminate size="24" color="primary" />
              </div>
              <div v-else-if="bomItems.length === 0" class="text-center pa-4 text-caption text-medium-emphasis">
                暂无子项
              </div>
              <v-list v-else density="compact" nav class="pa-1">
                <v-list-item
                  v-for="item in bomItems"
                  :key="item.id"
                  class="material-item mb-1"
                  @click="highlightNode(item)"
                >
                  <template #prepend>
                    <v-icon icon="mdi-package-variant-closed" size="16" color="primary" />
                  </template>
                  <v-list-item-title class="text-caption font-weight-medium">
                    {{ item.child_product_name }}
                  </v-list-item-title>
                  <v-list-item-subtitle class="text-caption">
                    {{ item.child_product_code || '' }}
                  </v-list-item-subtitle>
                  <template #append>
                    <v-chip size="x-small" color="info" variant="tonal">x{{ item.quantity }}</v-chip>
                  </template>
                </v-list-item>
              </v-list>
            </v-tabs-window-item>

            <!-- Products Library -->
            <v-tabs-window-item value="products">
              <div class="pa-2">
                <v-text-field
                  v-model="productFilter"
                  density="compact"
                  variant="outlined"
                  prepend-inner-icon="mdi-magnify"
                  placeholder="搜索物料..."
                  clearable
                  hide-details
                  class="mb-2"
                />
              </div>
              <div v-if="productsLoading" class="text-center pa-4">
                <v-progress-circular indeterminate size="24" color="primary" />
              </div>
              <div v-else-if="filteredProducts.length === 0" class="text-center pa-4 text-caption text-medium-emphasis">
                无匹配物料
              </div>
              <v-list v-else density="compact" nav class="pa-1">
                <v-list-item
                  v-for="p in filteredProducts"
                  :key="p.id"
                  class="material-item mb-1"
                >
                  <template #prepend>
                    <v-icon icon="mdi-cube-outline" size="16" color="secondary" />
                  </template>
                  <v-list-item-title class="text-caption font-weight-medium">
                    {{ p.product_name }}
                  </v-list-item-title>
                  <v-list-item-subtitle class="text-caption">
                    {{ p.u9_material_code || p.part_number || '-' }}
                  </v-list-item-subtitle>
                  <template #append>
                    <v-btn
                      icon size="x-small" variant="text" color="primary"
                      @click.stop="quickAddFromPanel(p)"
                    >
                      <v-icon icon="mdi-plus" size="14" />
                      <v-tooltip activator="parent" location="right">添加到选中节点</v-tooltip>
                    </v-btn>
                  </template>
                </v-list-item>
              </v-list>
            </v-tabs-window-item>
          </v-tabs-window>
        </div>
      </v-card>
    </div>

    <!-- ==================== Main Canvas ==================== -->
    <div class="mbom-canvas">
      <VueFlow
        v-model:nodes="nodes"
        v-model:edges="edges"
        :default-viewport="{ zoom: 0.8, x: 0, y: 0 }"
        :min-zoom="0.2"
        :max-zoom="2"
        @node-drag-stop="onNodeDragStop"
        @pane-ready="onPaneReady"
        @node-context-menu="onNodeContextMenu"
        @node-click="onNodeClick"
      >
        <template #node-bomNode="props">
          <BOMNode
            v-bind="props"
            @edit-quantity="onEditQuantity"
            @add-child="onAddChild"
            @delete-item="onDeleteItem"
          />
        </template>
        <Background :gap="20" :size="1" />
        <Controls position="bottom-left" />
        <MiniMap position="bottom-right" />
      </VueFlow>
    </div>

    <!-- ==================== Context Menu ==================== -->
    <v-menu
      v-model="contextMenu.show"
      :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
      location="bottom start"
      :target="[contextMenu.x, contextMenu.y]"
    >
      <v-list density="compact" nav>
        <v-list-item prepend-icon="mdi-pencil" @click="onEditQuantity(contextMenu.nodeData)">
          <v-list-item-title>编辑用量</v-list-item-title>
        </v-list-item>
        <v-list-item prepend-icon="mdi-plus" @click="onAddChild(contextMenu.nodeData)">
          <v-list-item-title>添加子项</v-list-item-title>
        </v-list-item>
        <v-divider v-if="contextMenu.nodeData?.bom_item_id" />
        <v-list-item
          v-if="contextMenu.nodeData?.bom_item_id"
          prepend-icon="mdi-delete"
          color="error"
          @click="onDeleteItem(contextMenu.nodeData)"
        >
          <v-list-item-title>删除</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>

    <!-- ==================== Edit Quantity Dialog ==================== -->
    <v-dialog v-model="editDialog.show" max-width="400" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-pencil" class="mr-2" />
          编辑用量
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="editDialog.show = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <p class="text-caption text-medium-emphasis mb-3">
            物料：{{ editDialog.productName }}
          </p>
          <v-text-field
            v-model.number="editDialog.quantity"
            label="用量"
            type="number"
            :rules="[v => v > 0 || '用量必须大于0']"
            required
          />
          <v-text-field v-model="editDialog.unit" label="单位" />
          <v-text-field v-model="editDialog.reference_designator" label="参考位号" />
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="editDialog.show = false">取消</v-btn>
          <v-btn color="primary" :loading="editDialog.saving" @click="handleSaveQuantity">保存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- ==================== Add Child Dialog ==================== -->
    <v-dialog v-model="addDialog.show" max-width="480" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-plus" class="mr-2" />
          添加子项
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="addDialog.show = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <p class="text-caption text-medium-emphasis mb-3">
            父物料：{{ addDialog.parentName }}
          </p>
          <v-autocomplete
            v-model="addDialog.child_product_id"
            :items="productList"
            item-title="display"
            item-value="id"
            label="子物料"
            :rules="[v => !!v || '请选择子物料']"
            required
            :loading="productsLoading"
            @update:search="onProductSearch"
          />
          <v-row dense>
            <v-col cols="6">
              <v-text-field v-model.number="addDialog.quantity" label="用量" type="number" :rules="[v => v > 0 || '用量必须大于0']" required />
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="addDialog.unit" label="单位" />
            </v-col>
          </v-row>
          <v-text-field v-model="addDialog.reference_designator" label="参考位号" />
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="addDialog.show = false">取消</v-btn>
          <v-btn color="primary" :loading="addDialog.saving" @click="handleAddChild">添加</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- ==================== Move Confirm Dialog ==================== -->
    <v-dialog v-model="moveDialog.show" max-width="440" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-swap-horizontal" class="mr-2" />
          移动子项
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="moveDialog.show = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <p>将 <strong>{{ moveDialog.itemName }}</strong> 移动到 <strong>{{ moveDialog.targetName }}</strong>？</p>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="moveDialog.show = false">取消</v-btn>
          <v-btn color="primary" :loading="moveDialog.moving" @click="handleMove">确认移动</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { VueFlow, useVueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import BOMNode from '@/components/flow/BOMNode.vue'
import { bomAPI, materialAPI } from '@/api/index'
import { useMessage, useConfirm } from '@/composables/useMessage'

import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'

const props = defineProps({
  bomId: { type: Number, default: null },
  maxLevel: { type: Number, default: 10 },
})

const emit = defineEmits(['updated'])

const message = useMessage()
const confirmDialog = useConfirm()

const { zoomIn, zoomOut, fitView, getNodes, setNodes } = useVueFlow()

const nodes = ref([])
const edges = ref([])

// ==================== Control Panel ====================
const showControlPanel = ref(true)
const nodeSearch = ref('')
const selectedNodeId = ref(null)

function fitViewAll() {
  fitView({ padding: 0.2 })
}

function onNodeSearch(val) {
  if (!val) {
    // Clear highlight
    nodes.value.forEach(n => { n.class = '' })
    return
  }
  const lower = val.toLowerCase()
  nodes.value.forEach(n => {
    const match = n.data.product_name?.toLowerCase().includes(lower) ||
                  n.data.product_code?.toLowerCase().includes(lower) ||
                  n.data.part_number?.toLowerCase().includes(lower)
    n.class = match ? 'node-highlight' : ''
  })
}

function expandAllNodes() {
  loadTree()
}

function collapseAllNodes() {
  if (nodes.value.length === 0) return
  const root = nodes.value[0]
  nodes.value = [root]
  edges.value = []
}

function onNodeClick({ node }) {
  selectedNodeId.value = node.id
}

// ==================== Materials Panel ====================
const showMaterialsPanel = ref(true)
const materialTab = ref('bomitems')
const bomItems = ref([])
const bomItemsLoading = ref(false)
const productFilter = ref('')

async function loadBomItems() {
  if (!props.bomId) {
    bomItems.value = []
    return
  }
  bomItemsLoading.value = true
  try {
    const res = await bomAPI.get(props.bomId)
    bomItems.value = res.data.items || []
  } catch (e) {
    bomItems.value = []
  } finally {
    bomItemsLoading.value = false
  }
}

const filteredProducts = computed(() => {
  if (!productFilter.value) return allProducts.value
  const lower = productFilter.value.toLowerCase()
  return allProducts.value.filter(p =>
    p.product_name?.toLowerCase().includes(lower) ||
    p.u9_material_code?.toLowerCase().includes(lower) ||
    p.part_number?.toLowerCase().includes(lower)
  )
})

const allProducts = ref([])

async function loadAllProducts() {
  try {
    const res = await materialAPI.getMaterials({ page: 1, page_size: 500, material_type: 'product' })
    allProducts.value = res.data.items || []
  } catch (e) {
    allProducts.value = []
  }
}

function highlightNode(item) {
  const nodeId = nodes.value.find(n =>
    n.data.product_id === item.child_product_id && n.data.bom_item_id === item.id
  )?.id
  if (nodeId) {
    selectedNodeId.value = nodeId
    nodes.value.forEach(n => { n.class = '' })
    const target = nodes.value.find(n => n.id === nodeId)
    if (target) {
      target.class = 'node-highlight'
      setTimeout(() => { target.class = '' }, 3000)
    }
  }
}

async function quickAddFromPanel(product) {
  // Find the selected node or root node as parent
  const parentNode = selectedNodeId.value
    ? nodes.value.find(n => n.id === selectedNodeId.value)
    : nodes.value[0]

  if (!parentNode) {
    message.warning('请先在画布中点击选中一个父节点')
    return
  }
  if (!parentNode.data.bom_header_id) {
    message.warning('请选中一个非根节点作为父节点')
    return
  }

  addDialog.parentName = parentNode.data.product_name
  addDialog.bomId = parentNode.data.bom_header_id
  addDialog.child_product_id = product.id
  addDialog.quantity = 1
  addDialog.unit = product.unit || ''
  addDialog.reference_designator = ''
  addDialog.show = true
}

// ==================== Tree to Graph ====================
function treeToGraph(node, parentId = null, x = 0, y = 0, siblingIndex = 0, siblingCount = 1) {
  const nodeId = parentId
    ? `${parentId}-${node.product_id}-${siblingIndex}`
    : `root-${node.product_id}`

  const childNodes = node.children || []
  const totalWidth = Math.max(siblingCount * 280, 280)
  const offsetX = x - totalWidth / 2 + 140

  const resultNodes = []
  const resultEdges = []

  resultNodes.push({
    id: nodeId,
    type: 'bomNode',
    position: { x: offsetX + siblingIndex * 280, y },
    data: { ...node },
    draggable: true,
  })

  if (parentId) {
    resultEdges.push({
      id: `${parentId}->${nodeId}`,
      source: parentId,
      target: nodeId,
      type: 'smoothstep',
      animated: false,
      style: { stroke: '#1976D2', strokeWidth: 2 },
    })
  }

  if (childNodes.length > 0) {
    const childY = y + 180
    childNodes.forEach((child, idx) => {
      const childResult = treeToGraph(
        child, nodeId,
        offsetX + siblingIndex * 280,
        childY,
        idx,
        childNodes.length
      )
      resultNodes.push(...childResult.nodes)
      resultEdges.push(...childResult.edges)
    })
  }

  return { nodes: resultNodes, edges: resultEdges }
}

async function loadTree() {
  if (!props.bomId) {
    nodes.value = []
    edges.value = []
    bomItems.value = []
    return
  }
  try {
    const [treeRes] = await Promise.all([
      bomAPI.getTree(props.bomId, props.maxLevel),
      loadBomItems(),
    ])
    const tree = treeRes.data
    const graph = treeToGraph(tree)
    nodes.value = graph.nodes
    edges.value = graph.edges
    // fitView after nodes are rendered (async load means fit-view-on-init is too early)
    setTimeout(() => fitView({ padding: 0.2 }), 100)
  } catch (e) {
    message.error('加载 BOM 树失败：' + (e.response?.data?.detail || e.message))
    nodes.value = []
    edges.value = []
  }
}

watch(() => props.bomId, loadTree)
watch(() => props.bomId, () => { selectedNodeId.value = null })

// ==================== Drag and Drop ====================
async function onNodeDragStop({ node, intersectingNodes }) {
  if (!intersectingNodes || intersectingNodes.length === 0) return

  const targetNode = intersectingNodes[0]
  const draggedData = node.data
  const targetData = targetNode.data

  // Can't drop on self or same parent
  if (draggedData.product_id === targetData.product_id) return
  // Can't move root node
  if (!draggedData.bom_item_id) return
  // Can't drop onto same BOM
  if (draggedData.bom_header_id === targetData.bom_header_id) return

  moveDialog.itemName = draggedData.product_name
  moveDialog.targetName = targetData.product_name
  moveDialog.itemId = draggedData.bom_item_id
  moveDialog.sourceBomId = draggedData.bom_header_id
  moveDialog.targetBomId = targetData.bom_header_id
  moveDialog.show = true
}

const moveDialog = reactive({
  show: false,
  itemName: '',
  targetName: '',
  itemId: null,
  sourceBomId: null,
  targetBomId: null,
  moving: false,
})

async function handleMove() {
  moveDialog.moving = true
  try {
    await bomAPI.moveItem({
      item_id: moveDialog.itemId,
      source_bom_id: moveDialog.sourceBomId,
      target_bom_id: moveDialog.targetBomId,
    })
    message.success('子项已移动')
    moveDialog.show = false
    await loadTree()
    emit('updated')
  } catch (e) {
    message.error('移动失败：' + (e.response?.data?.detail || e.message))
  } finally {
    moveDialog.moving = false
  }
}

// ==================== Context Menu ====================
const contextMenu = reactive({
  show: false,
  x: 0,
  y: 0,
  nodeData: null,
})

function onNodeContextMenu({ event, node }) {
  event.preventDefault()
  contextMenu.x = event.clientX
  contextMenu.y = event.clientY
  contextMenu.nodeData = node.data
  contextMenu.show = true
}

function onPaneReady() {
  // Close context menu on pane click
  document.addEventListener('click', () => {
    contextMenu.show = false
  })
}

// ==================== Edit Quantity ====================
const editDialog = reactive({
  show: false,
  productName: '',
  bomId: null,
  itemId: null,
  quantity: 1,
  unit: '',
  reference_designator: '',
  saving: false,
})

function onEditQuantity(nodeData) {
  contextMenu.show = false
  editDialog.productName = nodeData.product_name
  editDialog.bomId = nodeData.bom_header_id
  editDialog.itemId = nodeData.bom_item_id
  editDialog.quantity = parseFloat(nodeData.quantity) || 1
  editDialog.unit = nodeData.unit || ''
  editDialog.reference_designator = nodeData.reference_designator || ''
  editDialog.show = true
}

async function handleSaveQuantity() {
  if (!editDialog.quantity || editDialog.quantity <= 0) {
    message.warning('用量必须大于 0')
    return
  }
  editDialog.saving = true
  try {
    await bomAPI.updateItem(editDialog.bomId, editDialog.itemId, {
      quantity: editDialog.quantity,
      unit: editDialog.unit || undefined,
      reference_designator: editDialog.reference_designator || undefined,
    })
    message.success('用量已更新')
    editDialog.show = false
    await loadTree()
    emit('updated')
  } catch (e) {
    message.error('更新失败：' + (e.response?.data?.detail || e.message))
  } finally {
    editDialog.saving = false
  }
}

// ==================== Add Child ====================
const addDialog = reactive({
  show: false,
  parentName: '',
  bomId: null,
  child_product_id: null,
  quantity: 1,
  unit: '',
  reference_designator: '',
  saving: false,
})

function onAddChild(nodeData) {
  contextMenu.show = false
  addDialog.parentName = nodeData.product_name
  addDialog.bomId = nodeData.bom_header_id
  addDialog.child_product_id = null
  addDialog.quantity = 1
  addDialog.unit = ''
  addDialog.reference_designator = ''
  addDialog.show = true
  loadProducts('')
}

async function handleAddChild() {
  if (!addDialog.child_product_id) {
    message.warning('请选择子物料')
    return
  }
  if (!addDialog.quantity || addDialog.quantity <= 0) {
    message.warning('用量必须大于 0')
    return
  }
  addDialog.saving = true
  try {
    await bomAPI.addItem(addDialog.bomId, {
      child_product_id: addDialog.child_product_id,
      quantity: addDialog.quantity,
      unit: addDialog.unit || undefined,
      reference_designator: addDialog.reference_designator || undefined,
    })
    message.success('子项已添加')
    addDialog.show = false
    await loadTree()
    emit('updated')
  } catch (e) {
    message.error('添加失败：' + (e.response?.data?.detail || e.message))
  } finally {
    addDialog.saving = false
  }
}

// ==================== Delete ====================
async function onDeleteItem(nodeData) {
  contextMenu.show = false
  if (!nodeData.bom_item_id) return

  const ok = await confirmDialog(
    `确定删除子项 "${nodeData.product_name}" 吗？`,
    '确认删除',
    'warning'
  )
  if (!ok) return

  try {
    await bomAPI.deleteItem(nodeData.bom_header_id, nodeData.bom_item_id)
    message.success('子项已删除')
    await loadTree()
    emit('updated')
  } catch (e) {
    message.error('删除失败：' + (e.response?.data?.detail || e.message))
  }
}

// ==================== Product Loading ====================
const productList = ref([])
const productsLoading = ref(false)
let productSearchTimer = null
const MAX_SEARCH_PAGES = 3

async function loadProducts(search) {
  if (productSearchTimer) {
    clearTimeout(productSearchTimer)
    productSearchTimer = null
  }

  productsLoading.value = true
  try {
    const allProducts = []
    let page = 1
    const pageSize = 500
    let hasMore = true

    while (hasMore) {
      const params = { page, page_size: pageSize, material_type: 'product' }
      if (search) params.keyword = search
      const res = await materialAPI.getMaterials(params)
      const items = res.data.items || []
      allProducts.push(...items)

      const total = res.data.total || 0
      hasMore = allProducts.length < total && items.length === pageSize
      page++
    }

    productList.value = allProducts.map(p => ({
      id: p.id,
      display: `${p.product_name} (${p.u9_material_code || p.part_number || '-'})`
    }))
  } catch (e) {
    productList.value = []
  } finally {
    productsLoading.value = false
  }
}

function onProductSearch(val) {
  if (productSearchTimer) clearTimeout(productSearchTimer)
  productSearchTimer = setTimeout(() => {
    loadProducts(val || '')
  }, 500)
}

// ==================== Init ====================
onMounted(() => {
  loadAllProducts()
})
</script>

<style scoped>
.mbom-editor-layout {
  display: flex;
  width: 100%;
  height: calc(100vh - 300px);
  min-height: 500px;
  gap: 8px;
}
.mbom-sidebar {
  width: 280px;
  min-width: 280px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
}
.mbom-canvas {
  flex: 1;
  min-width: 0;
}
.material-item {
  border-radius: 6px;
  min-height: 40px;
}
.material-item:hover {
  background: rgba(var(--v-theme-primary), 0.05);
}
:deep(.node-highlight) {
  filter: drop-shadow(0 0 8px rgba(255, 152, 0, 0.8));
}
:deep(.node-highlight .v-card) {
  border-color: #FF9800 !important;
  border-width: 2px !important;
}
</style>
