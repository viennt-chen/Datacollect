<template>
  <div>
    <!-- Action bar -->
    <v-toolbar flat color="transparent" class="mb-4">
      <div>
        <div class="text-h5 font-weight-bold d-flex align-center ga-2">
          <v-icon icon="mdi-file-tree" color="primary" />
          BOM 管理
        </div>
        <div class="text-caption text-medium-emphasis mt-1">
          首页 / BOM 管理
        </div>
      </div>
    </v-toolbar>

    <!-- Tabs -->
    <v-tabs v-model="activeTab" color="primary" class="mb-4">
      <v-tab value="list" prepend-icon="mdi-format-list-bulleted">BOM 列表</v-tab>
      <v-tab value="tree" prepend-icon="mdi-file-tree-outline">BOM 树形视图</v-tab>
      <v-tab value="whereused" prepend-icon="mdi-swap-horizontal">用量反查</v-tab>
      <v-tab value="mbom" prepend-icon="mdi-graph-outline">MBOM 编辑器</v-tab>
    </v-tabs>

    <v-tabs-window v-model="activeTab">
      <!-- ==================== Tab 1: BOM 列表 ==================== -->
      <v-tabs-window-item value="list">
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
                  <v-text-field v-model="queryParams.bom_code" label="BOM 编号" placeholder="请输入BOM编号" clearable density="compact" />
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-text-field v-model="queryParams.bom_name" label="BOM 名称" placeholder="请输入BOM名称" clearable density="compact" />
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

        <!-- Stats cards -->
        <v-row dense class="mb-4">
          <v-col cols="6" md="3">
            <v-card color="primary" variant="tonal">
              <v-card-text class="d-flex align-center ga-3">
                <v-icon icon="mdi-file-tree" size="36" />
                <div>
                  <div class="text-h5 font-weight-bold">{{ stats.total_boms }}</div>
                  <div class="text-caption">BOM 总数</div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" md="3">
            <v-card color="success" variant="tonal">
              <v-card-text class="d-flex align-center ga-3">
                <v-icon icon="mdi-check-circle" size="36" />
                <div>
                  <div class="text-h5 font-weight-bold">{{ stats.active_boms }}</div>
                  <div class="text-caption">已激活</div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" md="3">
            <v-card color="warning" variant="tonal">
              <v-card-text class="d-flex align-center ga-3">
                <v-icon icon="mdi-pencil-circle" size="36" />
                <div>
                  <div class="text-h5 font-weight-bold">{{ stats.draft_boms }}</div>
                  <div class="text-caption">草稿</div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" md="3">
            <v-card color="info" variant="tonal">
              <v-card-text class="d-flex align-center ga-3">
                <v-icon icon="mdi-package-variant" size="36" />
                <div>
                  <div class="text-h5 font-weight-bold">{{ stats.total_items }}</div>
                  <div class="text-caption">子项总数</div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Data table -->
        <v-card>
          <v-card-title class="d-flex align-center ga-2">
            <v-icon icon="mdi-format-list-bulleted" />
            BOM 列表
            <v-spacer />
            <v-btn color="primary" prepend-icon="mdi-plus" size="small" @click="openAddBom">新增 BOM</v-btn>
            <v-btn variant="outlined" prepend-icon="mdi-refresh" size="small" @click="handleSearch">刷新</v-btn>
          </v-card-title>
          <v-data-table
            :headers="headers"
            :items="bomList"
            :loading="loading"
            :items-per-page="pageSize"
            :page="page"
            :server-items-length="total"
            @update:page="p => { page = p; handleSearch() }"
            @update:items-per-page="s => { pageSize = s; handleSearch() }"
            hover
          >
            <template v-slot:item.bom_code="{ item }">
              <v-chip size="small" variant="tonal" color="primary">{{ item.bom_code }}</v-chip>
            </template>
            <template v-slot:item.status="{ item }">
              <v-chip :color="statusColor(item.status)" size="small" variant="tonal">
                {{ statusLabel(item.status) }}
              </v-chip>
            </template>
            <template v-slot:item.item_count="{ item }">
              <v-chip size="small" variant="outlined">{{ item.item_count }} 项</v-chip>
            </template>
            <template v-slot:item.effective_date="{ item }">
              {{ item.effective_date || '-' }}
            </template>
            <template v-slot:item.created_at="{ item }">
              {{ formatDateTime(item.created_at) }}
            </template>
            <template v-slot:item.actions="{ item }">
              <div class="d-flex ga-1">
                <v-btn icon variant="text" size="small" @click="openItemsEditor(item)">
                  <v-icon icon="mdi-format-list-checks" size="small" />
                  <v-tooltip activator="parent" location="top">编辑子项</v-tooltip>
                </v-btn>
                <v-btn icon variant="text" size="small" @click="openEditBom(item)">
                  <v-icon icon="mdi-pencil" size="small" />
                  <v-tooltip activator="parent" location="top">编辑</v-tooltip>
                </v-btn>
                <v-btn icon variant="text" size="small" color="success" @click="handleActivate(item)" v-if="item.status !== 'active'">
                  <v-icon icon="mdi-check-circle" size="small" />
                  <v-tooltip activator="parent" location="top">激活</v-tooltip>
                </v-btn>
                <v-btn icon variant="text" size="small" color="warning" @click="handleArchive(item)" v-if="item.status === 'active'">
                  <v-icon icon="mdi-archive" size="small" />
                  <v-tooltip activator="parent" location="top">归档</v-tooltip>
                </v-btn>
                <v-btn icon variant="text" size="small" color="info" @click="openCopyDialog(item)">
                  <v-icon icon="mdi-content-copy" size="small" />
                  <v-tooltip activator="parent" location="top">复制</v-tooltip>
                </v-btn>
                <v-btn icon variant="text" size="small" color="error" @click="handleDeleteBom(item)">
                  <v-icon icon="mdi-delete" size="small" />
                  <v-tooltip activator="parent" location="top">删除</v-tooltip>
                </v-btn>
              </div>
            </template>
            <template v-slot:no-data>
              <div class="text-center pa-8">
                <v-icon icon="mdi-inbox" size="48" color="grey-lighten-1" />
                <p class="text-medium-emphasis mt-2">暂无 BOM 数据</p>
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-tabs-window-item>

      <!-- ==================== Tab 2: BOM 树形视图 ==================== -->
      <v-tabs-window-item value="tree">
        <v-card class="mb-4">
          <v-card-text>
            <v-row dense>
              <v-col cols="12" md="6">
                <v-select
                  v-model="selectedBomId"
                  :items="allBoms"
                  item-title="display"
                  item-value="id"
                  label="选择 BOM"
                  placeholder="请选择一个 BOM 查看树形结构"
                  clearable
                  density="compact"
                  @update:model-value="loadBomTree"
                />
              </v-col>
              <v-col cols="12" md="2">
                <v-number-input v-model.number="maxLevel" label="最大层级" :min="1" :max="20" density="compact" controlVariant="stacked" />
              </v-col>
              <v-col cols="12" md="2">
                <v-text-field v-model.number="explodeQty" label="展开数量" type="number" density="compact" />
              </v-col>
              <v-col cols="12" md="4" class="d-flex align-center ga-2">
                <v-btn color="primary" prepend-icon="mdi-refresh" :loading="treeLoading" @click="loadBomTree" :disabled="!selectedBomId">
                  树形结构
                </v-btn>
                <v-btn color="secondary" prepend-icon="mdi-expand-all" :loading="explodeLoading" @click="handleExplode" :disabled="!selectedBomId">
                  物料展开
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <v-card v-if="treeData">
          <v-card-title class="d-flex align-center ga-2">
            <v-icon icon="mdi-file-tree-outline" />
            BOM 多级结构 — {{ treeData.product_name }}
            <v-chip size="small" variant="tonal" color="primary" class="ml-2">{{ treeData.product_code }}</v-chip>
          </v-card-title>
          <v-divider />
          <v-card-text>
            <v-treeview
              :items="[treeData]"
              item-title="label"
              item-value="key"
              item-children="children"
              open-on-click
              hoverable
              activatable
            >
              <template v-slot:prepend="{ item }">
                <v-icon :icon="item.has_bom ? 'mdi-file-tree' : 'mdi-package-variant-closed'" :color="item.has_bom ? 'primary' : 'grey'" size="small" />
              </template>
              <template v-slot:append="{ item }">
                <div class="d-flex align-center ga-2">
                  <v-chip size="x-small" variant="tonal" color="info">x{{ item.quantity }}</v-chip>
                  <span v-if="item.unit" class="text-caption text-medium-emphasis">{{ item.unit }}</span>
                  <v-chip v-if="item.reference_designator" size="x-small" variant="outlined" color="secondary">{{ item.reference_designator }}</v-chip>
                </div>
              </template>
            </v-treeview>
          </v-card-text>
        </v-card>

        <v-card v-else-if="!treeLoading">
          <v-card-text class="text-center pa-12">
            <v-icon icon="mdi-file-tree-outline" size="64" color="grey-lighten-1" />
            <p class="text-medium-emphasis mt-4">请先选择一个 BOM 以查看树形结构</p>
          </v-card-text>
        </v-card>
      </v-tabs-window-item>

      <!-- ==================== Tab 3: 用量反查 ==================== -->
      <v-tabs-window-item value="whereused">
        <v-card class="mb-4">
          <v-card-text>
            <v-row dense>
              <v-col cols="12" md="6">
                <v-autocomplete
                  v-model="whereUsedProductId"
                  :items="productList"
                  item-title="display"
                  item-value="id"
                  label="选择物料（子物料）"
                  placeholder="输入物料名称或编号搜索"
                  clearable
                  density="compact"
                  :loading="productsLoading"
                  @update:search="onProductSearch"
                />
              </v-col>
              <v-col cols="12" md="3" class="d-flex align-center">
                <v-btn color="primary" prepend-icon="mdi-magnify" :loading="whereUsedLoading" @click="loadWhereUsed" :disabled="!whereUsedProductId">
                  查询
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <v-card v-if="whereUsedResults.length > 0">
          <v-card-title class="d-flex align-center ga-2">
            <v-icon icon="mdi-swap-horizontal" />
            用量反查结果
            <v-chip size="small" variant="tonal" color="info">{{ whereUsedResults.length }} 条</v-chip>
          </v-card-title>
          <v-data-table
            :headers="whereUsedHeaders"
            :items="whereUsedResults"
            hover
          >
            <template v-slot:item.status="{ item }">
              <v-chip :color="statusColor(item.status)" size="small" variant="tonal">
                {{ statusLabel(item.status) }}
              </v-chip>
            </template>
            <template v-slot:item.bom_code="{ item }">
              <a href="#" class="text-decoration-none" @click.prevent="jumpToBom(item.bom_id)">{{ item.bom_code }}</a>
            </template>
          </v-data-table>
        </v-card>

        <v-card v-else-if="whereUsedQueried">
          <v-card-text class="text-center pa-12">
            <v-icon icon="mdi-check-circle" size="64" color="success" />
            <p class="text-medium-emphasis mt-4">该物料未被任何 BOM 引用</p>
          </v-card-text>
        </v-card>
      </v-tabs-window-item>

      <!-- ==================== Tab 4: MBOM 编辑器 ==================== -->
      <v-tabs-window-item value="mbom">
        <v-card class="mb-4">
          <v-card-text>
            <v-row dense>
              <v-col cols="12" md="6">
                <v-select
                  v-model="mbomSelectedBomId"
                  :items="allBoms"
                  item-title="display"
                  item-value="id"
                  label="选择 BOM"
                  placeholder="请选择一个 BOM 进行可视化编辑"
                  clearable
                  density="compact"
                />
              </v-col>
              <v-col cols="12" md="2">
                <v-number-input v-model.number="mbomMaxLevel" label="最大层级" :min="1" :max="20" density="compact" controlVariant="stacked" />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <MBOMEditor
          v-if="mbomSelectedBomId"
          :bom-id="mbomSelectedBomId"
          :max-level="mbomMaxLevel"
          @updated="onMbomUpdated"
        />

        <v-card v-else>
          <v-card-text class="text-center pa-12">
            <v-icon icon="mdi-graph-outline" size="64" color="grey-lighten-1" />
            <p class="text-medium-emphasis mt-4">请先选择一个 BOM 进行可视化编辑</p>
            <p class="text-caption text-medium-emphasis">支持拖拽节点重排父子关系、编辑用量、添加/删除子项</p>
          </v-card-text>
        </v-card>
      </v-tabs-window-item>
    </v-tabs-window>

    <!-- ==================== BOM Header Add/Edit Dialog ==================== -->
    <v-dialog v-model="showBomDialog" max-width="640" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon :icon="isEditingBom ? 'mdi-pencil' : 'mdi-plus'" class="mr-2" />
          {{ isEditingBom ? '编辑 BOM' : '新增 BOM' }}
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="showBomDialog = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-form ref="bomFormRef">
            <v-text-field v-model="bomForm.bom_code" label="BOM 编号" :rules="[v => !!v || '请输入BOM编号']" required />
            <v-text-field v-model="bomForm.bom_name" label="BOM 名称" :rules="[v => !!v || '请输入BOM名称']" required />
            <v-autocomplete
              v-model="bomForm.product_id"
              :items="productList"
              item-title="display"
              item-value="id"
              label="父物料"
              :rules="[v => !!v || '请选择父物料']"
              required
              :loading="productsLoading"
              @update:search="onProductSearch"
            />
            <v-text-field v-model="bomForm.version" label="版本号" placeholder="V1.0" />
            <v-row dense>
              <v-col cols="6">
                <v-text-field v-model="bomForm.effective_date" label="生效日期" type="date" />
              </v-col>
              <v-col cols="6">
                <v-text-field v-model="bomForm.expiry_date" label="失效日期" type="date" />
              </v-col>
            </v-row>
            <v-textarea v-model="bomForm.description" label="描述" rows="2" />
          </v-form>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showBomDialog = false">取消</v-btn>
          <v-btn color="primary" :loading="bomSaving" @click="handleSaveBom">保存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- ==================== BOM Items Editor Dialog ==================== -->
    <v-dialog v-model="showItemsDialog" max-width="960" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-format-list-checks" class="mr-2" />
          BOM 子项管理 — {{ currentBom?.bom_code }}
          <v-chip size="small" variant="tonal" color="primary" class="ml-2">{{ currentBom?.bom_name }}</v-chip>
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="showItemsDialog = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <div class="d-flex align-center mb-3 ga-2">
            <v-btn color="primary" prepend-icon="mdi-plus" size="small" @click="openAddItem">添加子项</v-btn>
            <v-chip v-if="currentItems.length > 0" size="small" variant="tonal" color="info">拖拽行可排序</v-chip>
          </div>
          <div v-if="itemsLoading" class="text-center pa-6">
            <v-progress-circular indeterminate color="primary" />
          </div>
          <div v-else-if="currentItems.length === 0" class="text-center pa-6">
            <v-icon icon="mdi-inbox" size="40" color="grey-lighten-1" />
            <p class="text-medium-emphasis mt-2">暂无子项，请添加物料</p>
          </div>
          <table v-else class="bom-items-table">
            <thead>
              <tr>
                <th style="width:40px"></th>
                <th v-for="h in itemHeaders" :key="h.key" :style="{ width: h.width || 'auto' }">{{ h.title }}</th>
              </tr>
            </thead>
            <draggable v-model="currentItems" tag="tbody" item-key="id" handle=".drag-handle" @end="onDragEnd" ghost-class="sortable-ghost" chosen-class="sortable-chosen">
              <template #item="{ element }">
                <tr>
                  <td><v-icon icon="mdi-drag-vertical" class="drag-handle" size="small" /></td>
                  <td>{{ element.item_no }}</td>
                  <td>
                    <div class="font-weight-medium">{{ element.child_product_name || '-' }}</div>
                    <div class="text-caption text-medium-emphasis">{{ element.child_product_code || '' }}</div>
                  </td>
                  <td>{{ element.child_specification || '' }}</td>
                  <td class="font-weight-bold">{{ element.quantity }}</td>
                  <td>{{ element.unit || '' }}</td>
                  <td>{{ element.reference_designator || '' }}</td>
                  <td>{{ element.remark || '' }}</td>
                  <td>
                    <div class="d-flex ga-1">
                      <v-btn icon variant="text" size="small" @click="openEditItem(element)">
                        <v-icon icon="mdi-pencil" size="small" />
                        <v-tooltip activator="parent" location="top">编辑</v-tooltip>
                      </v-btn>
                      <v-btn icon variant="text" size="small" color="error" @click="handleDeleteItem(element)">
                        <v-icon icon="mdi-delete" size="small" />
                        <v-tooltip activator="parent" location="top">删除</v-tooltip>
                      </v-btn>
                    </div>
                  </td>
                </tr>
              </template>
            </draggable>
          </table>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showItemsDialog = false">关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- ==================== Item Add/Edit Dialog ==================== -->
    <v-dialog v-model="showItemDialog" max-width="560" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon :icon="isEditingItem ? 'mdi-pencil' : 'mdi-plus'" class="mr-2" />
          {{ isEditingItem ? '编辑子项' : '添加子项' }}
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="showItemDialog = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-form>
            <v-autocomplete
              v-model="itemForm.child_product_id"
              :items="productList"
              item-title="display"
              item-value="id"
              label="子物料"
              :rules="[v => !!v || '请选择子物料']"
              required
              :loading="productsLoading"
              @update:search="onProductSearch"
              :disabled="isEditingItem"
            />
            <v-row dense>
              <v-col cols="6">
                <v-text-field v-model="itemForm.quantity" label="用量" type="number" :rules="[v => v > 0 || '用量必须大于0']" required />
              </v-col>
              <v-col cols="6">
                <v-text-field v-model="itemForm.unit" label="单位" placeholder="个/台/米" />
              </v-col>
            </v-row>
            <v-row dense>
              <v-col cols="6">
                <v-text-field v-model="itemForm.reference_designator" label="参考位号" placeholder="U1, R1-R3" />
              </v-col>
              <v-col cols="6">
                <v-text-field v-model.number="itemForm.item_no" label="行号" type="number" />
              </v-col>
            </v-row>
            <v-textarea v-model="itemForm.remark" label="备注" rows="2" />
          </v-form>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showItemDialog = false">取消</v-btn>
          <v-btn color="primary" :loading="itemSaving" @click="handleSaveItem">保存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- ==================== Copy Dialog ==================== -->
    <v-dialog v-model="showCopyDialog" max-width="480" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-content-copy" class="mr-2" />
          复制 BOM
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="showCopyDialog = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <p class="text-caption text-medium-emphasis mb-3">
            源 BOM：{{ copySourceBom?.bom_code }} — {{ copySourceBom?.bom_name }}
          </p>
          <v-form>
            <v-text-field v-model="copyForm.new_bom_code" label="新 BOM 编号" :rules="[v => !!v || '请输入新BOM编号']" required />
            <v-text-field v-model="copyForm.new_bom_name" label="新 BOM 名称" />
            <v-text-field v-model="copyForm.new_version" label="新版本号" placeholder="V2.0" />
          </v-form>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showCopyDialog = false">取消</v-btn>
          <v-btn color="primary" :loading="copySaving" @click="handleCopyBom">复制</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- ==================== Explode Results Dialog ==================== -->
    <v-dialog v-model="showExplodeDialog" max-width="900">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-expand-all" class="mr-2" />
          物料展开 — {{ explodeResult?.bom_code }}
          <v-chip size="small" variant="tonal" color="info" class="ml-2">共 {{ explodeResult?.total_materials }} 种物料</v-chip>
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="showExplodeDialog = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-data-table
            :headers="explodeHeaders"
            :items="explodeResult?.items || []"
            density="compact"
            hover
            :items-per-page="-1"
          >
            <template v-slot:item.total_quantity="{ item }">
              <span class="font-weight-bold text-primary">{{ Number(item.total_quantity || 0).toFixed(5) }}</span>
            </template>
            <template v-slot:item.first_level="{ item }">
              <v-chip size="x-small" variant="tonal" color="secondary">L{{ item.first_level }}</v-chip>
            </template>
          </v-data-table>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showExplodeDialog = false">关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useMessage, useConfirm } from '@/composables/useMessage'
import { bomAPI, materialAPI } from '@/api/index'
import { formatDateTime } from '@/utils/datetime'
import draggable from 'vuedraggable'
import MBOMEditor from '@/components/admin/MBOMEditor.vue'

const message = useMessage()
const confirmDialog = useConfirm()

const activeTab = ref('list')
const showSearch = ref(true)

// ==================== BOM List ====================
const statusOptions = [
  { title: '全部', value: '' },
  { title: '草稿', value: 'draft' },
  { title: '已激活', value: 'active' },
  { title: '已归档', value: 'archived' },
]

const headers = [
  { title: 'BOM 编号', key: 'bom_code', width: '150px' },
  { title: 'BOM 名称', key: 'bom_name' },
  { title: '物料名称', key: 'product_name' },
  { title: '版本', key: 'version', width: '80px' },
  { title: '状态', key: 'status', width: '100px' },
  { title: '子项数', key: 'item_count', width: '90px' },
  { title: '生效日期', key: 'effective_date', width: '120px' },
  { title: '创建时间', key: 'created_at', width: '160px' },
  { title: '操作', key: 'actions', sortable: false, width: '200px' },
]

const queryParams = reactive({ bom_code: '', bom_name: '', status: '' })
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const loading = ref(false)
const bomList = ref([])
const stats = reactive({ total_boms: 0, active_boms: 0, draft_boms: 0, total_items: 0 })

function statusColor(s) {
  return { draft: 'warning', active: 'success', archived: 'grey' }[s] || 'grey'
}
function statusLabel(s) {
  return { draft: '草稿', active: '已激活', archived: '已归档' }[s] || s
}

async function handleSearch() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (queryParams.bom_code) params.bom_code = queryParams.bom_code
    if (queryParams.bom_name) params.bom_name = queryParams.bom_name
    if (queryParams.status) params.status = queryParams.status
    const res = await bomAPI.list(params)
    bomList.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    message.error('加载 BOM 列表失败')
  } finally {
    loading.value = false
  }
}

function resetQuery() {
  Object.assign(queryParams, { bom_code: '', bom_name: '', status: '' })
  page.value = 1
  handleSearch()
}

async function loadStats() {
  try {
    const res = await bomAPI.getStats()
    Object.assign(stats, res.data)
  } catch (e) { /* ignore */ }
}

// ==================== BOM Header CRUD ====================
const showBomDialog = ref(false)
const isEditingBom = ref(false)
const bomSaving = ref(false)
const bomFormRef = ref(null)
const bomForm = reactive({
  id: null, bom_code: '', bom_name: '', product_id: null,
  version: 'V1.0', effective_date: '', expiry_date: '', description: ''
})

const bomDefaults = { id: null, bom_code: '', bom_name: '', product_id: null, version: 'V1.0', effective_date: '', expiry_date: '', description: '' }

function openAddBom() {
  Object.assign(bomForm, bomDefaults)
  isEditingBom.value = false
  showBomDialog.value = true
  ensureProductsLoaded()
}

function openEditBom(item) {
  Object.assign(bomForm, {
    id: item.id, bom_code: item.bom_code, bom_name: item.bom_name,
    product_id: item.product_id, version: item.version,
    effective_date: item.effective_date || '', expiry_date: item.expiry_date || '',
    description: item.description || ''
  })
  isEditingBom.value = true
  showBomDialog.value = true
  ensureProductsLoaded()
}

async function handleSaveBom() {
  if (!bomForm.bom_code?.trim()) { message.warning('请输入 BOM 编号'); return }
  if (!bomForm.bom_name?.trim()) { message.warning('请输入 BOM 名称'); return }
  if (!bomForm.product_id) { message.warning('请选择父物料'); return }

  bomSaving.value = true
  try {
    const data = {
      bom_code: bomForm.bom_code,
      bom_name: bomForm.bom_name,
      product_id: bomForm.product_id,
      version: bomForm.version || 'V1.0',
      description: bomForm.description || undefined,
      effective_date: bomForm.effective_date || undefined,
      expiry_date: bomForm.expiry_date || undefined,
    }
    if (isEditingBom.value) {
      await bomAPI.update(bomForm.id, data)
      message.success('BOM 更新成功')
    } else {
      await bomAPI.create(data)
      message.success('BOM 创建成功')
    }
    showBomDialog.value = false
    handleSearch()
    loadStats()
    loadAllBoms()
  } catch (e) {
    message.error('保存失败：' + (e.response?.data?.detail || e.message))
  } finally {
    bomSaving.value = false
  }
}

async function handleDeleteBom(item) {
  const ok = await confirmDialog(`确定删除 BOM "${item.bom_code}" 吗？所有子项将一并删除。`, '确认删除', 'warning')
  if (!ok) return
  try {
    await bomAPI.delete(item.id)
    message.success('BOM 已删除')
    handleSearch()
    loadStats()
    loadAllBoms()
  } catch (e) {
    message.error('删除失败：' + (e.response?.data?.detail || e.message))
  }
}

async function handleActivate(item) {
  const ok = await confirmDialog(`激活 BOM "${item.bom_code}" 将自动归档同物料的其他已激活 BOM，是否继续？`, '确认激活', 'info')
  if (!ok) return
  try {
    await bomAPI.activate(item.id)
    message.success('BOM 已激活')
    handleSearch()
    loadStats()
  } catch (e) {
    message.error('激活失败：' + (e.response?.data?.detail || e.message))
  }
}

async function handleArchive(item) {
  const ok = await confirmDialog(`确定归档 BOM "${item.bom_code}" 吗？`, '确认归档', 'warning')
  if (!ok) return
  try {
    await bomAPI.archive(item.id)
    message.success('BOM 已归档')
    handleSearch()
    loadStats()
  } catch (e) {
    message.error('归档失败：' + (e.response?.data?.detail || e.message))
  }
}

// ==================== Copy ====================
const showCopyDialog = ref(false)
const copySaving = ref(false)
const copySourceBom = ref(null)
const copyForm = reactive({ new_bom_code: '', new_bom_name: '', new_version: '' })

function openCopyDialog(item) {
  copySourceBom.value = item
  copyForm.new_bom_code = item.bom_code + '-COPY'
  copyForm.new_bom_name = item.bom_name + ' (副本)'
  copyForm.new_version = ''
  showCopyDialog.value = true
}

async function handleCopyBom() {
  if (!copyForm.new_bom_code?.trim()) { message.warning('请输入新 BOM 编号'); return }
  copySaving.value = true
  try {
    await bomAPI.copy(copySourceBom.value.id, {
      new_bom_code: copyForm.new_bom_code,
      new_bom_name: copyForm.new_bom_name || undefined,
      new_version: copyForm.new_version || undefined,
    })
    message.success('BOM 复制成功')
    showCopyDialog.value = false
    handleSearch()
    loadStats()
    loadAllBoms()
  } catch (e) {
    message.error('复制失败：' + (e.response?.data?.detail || e.message))
  } finally {
    copySaving.value = false
  }
}

// ==================== BOM Items ====================
const showItemsDialog = ref(false)
const showItemDialog = ref(false)
const isEditingItem = ref(false)
const itemSaving = ref(false)
const itemsLoading = ref(false)
const currentBom = ref(null)
const currentItems = ref([])

const itemHeaders = [
  { title: '行号', key: 'item_no', width: '70px' },
  { title: '子物料', key: 'child_product_name' },
  { title: '规格型号', key: 'child_specification' },
  { title: '用量', key: 'quantity', width: '90px' },
  { title: '单位', key: 'unit', width: '70px' },
  { title: '参考位号', key: 'reference_designator' },
  { title: '备注', key: 'remark' },
  { title: '操作', key: 'actions', sortable: false, width: '90px' },
]

const itemDefaults = { id: null, child_product_id: null, quantity: 1, unit: '', reference_designator: '', item_no: 0, remark: '' }
const itemForm = reactive({ ...itemDefaults })

function openItemsEditor(bom) {
  currentBom.value = bom
  showItemsDialog.value = true
  loadBomItems(bom.id)
  ensureProductsLoaded()
}

async function loadBomItems(bomId) {
  itemsLoading.value = true
  try {
    const res = await bomAPI.get(bomId)
    currentItems.value = res.data.items || []
  } catch (e) {
    message.error('加载子项失败')
  } finally {
    itemsLoading.value = false
  }
}

function openAddItem() {
  Object.assign(itemForm, itemDefaults)
  isEditingItem.value = false
  showItemDialog.value = true
}

function openEditItem(item) {
  Object.assign(itemForm, {
    id: item.id, child_product_id: item.child_product_id,
    quantity: parseFloat(item.quantity), unit: item.unit || '',
    reference_designator: item.reference_designator || '',
    item_no: item.item_no || 0, remark: item.remark || ''
  })
  isEditingItem.value = true
  showItemDialog.value = true
}

async function handleSaveItem() {
  if (!itemForm.child_product_id) { message.warning('请选择子物料'); return }
  if (!itemForm.quantity || itemForm.quantity <= 0) { message.warning('用量必须大于 0'); return }

  itemSaving.value = true
  try {
    const data = {
      child_product_id: itemForm.child_product_id,
      quantity: itemForm.quantity,
      unit: itemForm.unit || undefined,
      reference_designator: itemForm.reference_designator || undefined,
      item_no: itemForm.item_no || 0,
      remark: itemForm.remark || undefined,
    }
    if (isEditingItem.value) {
      await bomAPI.updateItem(currentBom.value.id, itemForm.id, data)
      message.success('子项更新成功')
    } else {
      await bomAPI.addItem(currentBom.value.id, data)
      message.success('子项添加成功')
    }
    showItemDialog.value = false
    loadBomItems(currentBom.value.id)
    handleSearch()
    loadStats()
  } catch (e) {
    message.error('保存失败：' + (e.response?.data?.detail || e.message))
  } finally {
    itemSaving.value = false
  }
}

async function handleDeleteItem(item) {
  const ok = await confirmDialog(`确定删除子项 "${item.child_product_name}" 吗？`, '确认删除', 'warning')
  if (!ok) return
  try {
    await bomAPI.deleteItem(currentBom.value.id, item.id)
    message.success('子项已删除')
    loadBomItems(currentBom.value.id)
    handleSearch()
    loadStats()
  } catch (e) {
    message.error('删除失败：' + (e.response?.data?.detail || e.message))
  }
}

async function onDragEnd() {
  const order = currentItems.value.map(item => item.id)
  try {
    await bomAPI.reorder(currentBom.value.id, order)
    currentItems.value.forEach((item, i) => { item.item_no = i + 1 })
    message.success('排序已更新')
  } catch (e) {
    message.error('排序保存失败：' + (e.response?.data?.detail || e.message))
    loadBomItems(currentBom.value.id)
  }
}

// ==================== BOM Tree ====================
const selectedBomId = ref(null)
const maxLevel = ref(10)
const explodeQty = ref(100)
const treeLoading = ref(false)
const explodeLoading = ref(false)
const treeData = ref(null)
const allBoms = ref([])

// ==================== MBOM Editor ====================
const mbomSelectedBomId = ref(null)
const mbomMaxLevel = ref(10)

function onMbomUpdated() {
  handleSearch()
  loadStats()
}

const showExplodeDialog = ref(false)
const explodeResult = ref(null)
const explodeHeaders = [
  { title: '物料名称', key: 'product_name' },
  { title: '物料编号', key: 'product_code', width: '150px' },
  { title: '零件号', key: 'part_number', width: '120px' },
  { title: '规格型号', key: 'specification' },
  { title: '总需求量', key: 'total_quantity', width: '120px' },
  { title: '单位', key: 'unit', width: '70px' },
  { title: '首次出现层级', key: 'first_level', width: '110px' },
]

async function loadAllBoms() {
  try {
    const res = await bomAPI.all()
    allBoms.value = (res.data.items || []).map(b => ({
      ...b,
      display: `${b.bom_code} — ${b.bom_name} (${b.product_name || '未知'})`
    }))
  } catch (e) { /* ignore */ }
}

function prepareTreeNodes(node, parentKey = '') {
  const key = parentKey ? `${parentKey}-${node.product_id}` : `root-${node.product_id}`
  return {
    ...node,
    key,
    label: `${node.product_name} (${node.product_code || '-'}) [x${node.quantity}]`,
    children: (node.children || []).map(c => prepareTreeNodes(c, key))
  }
}

async function loadBomTree() {
  if (!selectedBomId.value) return
  treeLoading.value = true
  treeData.value = null
  try {
    const res = await bomAPI.getTree(selectedBomId.value, maxLevel.value)
    treeData.value = prepareTreeNodes(res.data)
  } catch (e) {
    message.error('加载 BOM 树失败：' + (e.response?.data?.detail || e.message))
  } finally {
    treeLoading.value = false
  }
}

async function handleExplode() {
  if (!selectedBomId.value) return
  explodeLoading.value = true
  try {
    const res = await bomAPI.explode(selectedBomId.value, explodeQty.value, maxLevel.value)
    explodeResult.value = res.data
    showExplodeDialog.value = true
  } catch (e) {
    message.error('物料展开失败：' + (e.response?.data?.detail || e.message))
  } finally {
    explodeLoading.value = false
  }
}

// ==================== Where-Used ====================
const whereUsedProductId = ref(null)
const whereUsedLoading = ref(false)
const whereUsedResults = ref([])
const whereUsedQueried = ref(false)

const whereUsedHeaders = [
  { title: 'BOM 编号', key: 'bom_code', width: '150px' },
  { title: 'BOM 名称', key: 'bom_name' },
  { title: '父物料', key: 'parent_product_name' },
  { title: '版本', key: 'version', width: '80px' },
  { title: '状态', key: 'status', width: '100px' },
]

async function loadWhereUsed() {
  if (!whereUsedProductId.value) return
  whereUsedLoading.value = true
  whereUsedQueried.value = true
  try {
    const res = await bomAPI.whereUsed(whereUsedProductId.value)
    whereUsedResults.value = res.data.items || []
  } catch (e) {
    message.error('查询失败')
  } finally {
    whereUsedLoading.value = false
  }
}

function jumpToBom(bomId) {
  activeTab.value = 'list'
  queryParams.bom_code = ''
  queryParams.bom_name = ''
  queryParams.status = ''
  page.value = 1
  handleSearch().then(() => {
    // Try to find and highlight
  })
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
  handleSearch()
  loadStats()
  loadAllBoms()
  loadProducts('')
})
</script>

<style scoped>
.drag-handle {
  cursor: grab;
  color: rgba(0, 0, 0, 0.3);
}
.drag-handle:active {
  cursor: grabbing;
}
.bom-items-table {
  width: 100%;
  border-collapse: collapse;
}
.bom-items-table th {
  text-align: left;
  padding: 8px 12px;
  font-size: 0.75rem;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.6);
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
  white-space: nowrap;
}
.bom-items-table td {
  padding: 8px 12px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  font-size: 0.875rem;
}
.bom-items-table tbody tr:hover {
  background: rgba(0, 0, 0, 0.02);
}
:deep(.sortable-ghost) {
  opacity: 0.4;
}
:deep(.sortable-chosen) {
  background: rgba(var(--v-theme-primary), 0.05);
}
</style>
