<template>
  <div>
    <!-- Action bar -->
    <v-toolbar flat color="transparent" class="mb-4">
      <div>
        <div class="text-h5 font-weight-bold d-flex align-center ga-2">
          <v-icon icon="mdi-package-variant-closed" color="primary" />
          物料管理
        </div>
        <div class="text-caption text-medium-emphasis mt-1">
          首页 / 物料管理
        </div>
      </div>
      <v-spacer />
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openAddDialog">
        新增物料
      </v-btn>
      <v-btn variant="outlined" prepend-icon="mdi-tag-multiple" class="ml-2" @click="openCategoryDialog">
        分类管理
      </v-btn>
      <v-btn variant="outlined" prepend-icon="mdi-upload" class="ml-2" @click="openImportDialog">
        导入物料
      </v-btn>
      <v-btn variant="outlined" prepend-icon="mdi-download" class="ml-2" @click="exportProducts">
        导出物料
      </v-btn>
    </v-toolbar>

    <!-- Tabs -->
    <v-tabs v-model="activeTab" bg-color="transparent" class="mb-4" @update:model-value="switchTab">
      <v-tab value="products">
        <v-icon icon="mdi-package-variant-closed" class="mr-1" />
        物料信息
        <v-chip size="small" class="ml-1" color="primary" variant="tonal">{{ productStats.total || 0 }}</v-chip>
      </v-tab>
      <v-tab value="orders">
        <v-icon icon="mdi-receipt" class="mr-1" />
        ERP U9 订单
        <v-chip v-if="unreadOrders > 0" size="small" class="ml-1" color="error" variant="tonal">{{ unreadOrders }}</v-chip>
      </v-tab>
      <v-tab value="logs">
        <v-icon icon="mdi-text-box-outline" class="mr-1" />
        物料查询日志
        <v-chip v-if="unreadLogs > 0" size="small" class="ml-1" color="error" variant="tonal">{{ unreadLogs }}</v-chip>
      </v-tab>
      <v-tab value="local-records">
        <v-icon icon="mdi-clipboard-check-outline" class="mr-1" />
        本地加工记录
      </v-tab>
      <v-tab value="local-orders">
        <v-icon icon="mdi-receipt-text-check" class="mr-1" />
        本地订单
        <v-chip size="small" class="ml-1" color="primary" variant="tonal">{{ localOrderStats.total_orders || 0 }}</v-chip>
      </v-tab>
    </v-tabs>

    <v-window v-model="activeTab">
      <!-- Products Tab -->
      <v-window-item value="products">
        <!-- Metric cards -->
        <v-row dense class="mb-4">
          <v-col cols="12" md="3">
            <v-card>
              <v-card-text class="d-flex align-center ga-3">
                <v-avatar color="blue-lighten-4" size="48">
                  <v-icon icon="mdi-package-variant-closed" color="blue-darken-2" />
                </v-avatar>
                <div class="flex-grow-1">
                  <div class="text-h5 font-weight-bold">{{ productStats.total?.toLocaleString() || '0' }}</div>
                  <div class="text-caption text-medium-emphasis">物料总数</div>
                  <div class="text-caption">启用：{{ productStats.active || 0 }}</div>
                </div>
                <v-btn icon variant="text" size="small" @click="loadProducts">
                  <v-icon icon="mdi-refresh" />
                </v-btn>
              </v-card-text>
              <v-divider />
              <v-card-actions class="py-1">
                <span class="text-caption text-medium-emphasis">禁用：{{ productStats.inactive || 0 }}</span>
              </v-card-actions>
            </v-card>
          </v-col>
          <v-col cols="12" md="3">
            <v-card>
              <v-card-text class="d-flex align-center ga-3">
                <v-avatar color="green-lighten-4" size="48">
                  <v-icon icon="mdi-check-circle" color="green-darken-2" />
                </v-avatar>
                <div>
                  <div class="text-h5 font-weight-bold">{{ productStats.active?.toLocaleString() || '0' }}</div>
                  <div class="text-caption text-medium-emphasis">启用中物料</div>
                  <div class="text-caption">占比：{{ getActiveRate }}%</div>
                </div>
              </v-card-text>
              <v-divider />
              <v-card-actions class="py-1">
                <span class="text-caption text-medium-emphasis">正常状态</span>
              </v-card-actions>
            </v-card>
          </v-col>
          <v-col cols="12" md="3">
            <v-card>
              <v-card-text class="d-flex align-center ga-3">
                <v-avatar color="purple-lighten-4" size="48">
                  <v-icon icon="mdi-layers" color="purple-darken-2" />
                </v-avatar>
                <div>
                  <div class="text-h5 font-weight-bold">{{ productStats.categories?.length || 0 }}</div>
                  <div class="text-caption text-medium-emphasis">物料分类</div>
                  <div class="text-caption">项目：{{ productStats.projects?.length || 0 }}</div>
                </div>
              </v-card-text>
              <v-divider />
              <v-card-actions class="py-1">
                <span class="text-caption text-medium-emphasis">分类管理</span>
              </v-card-actions>
            </v-card>
          </v-col>
          <v-col cols="12" md="3">
            <v-card>
              <v-card-text class="d-flex align-center ga-3">
                <v-avatar color="orange-lighten-4" size="48">
                  <v-icon icon="mdi-calendar-check" color="orange-darken-2" />
                </v-avatar>
                <div>
                  <div class="text-h5 font-weight-bold">{{ productStats.today_added || 0 }}</div>
                  <div class="text-caption text-medium-emphasis">今日新增</div>
                  <div class="text-caption">本周：{{ productStats.week_added || 0 }}</div>
                </div>
              </v-card-text>
              <v-divider />
              <v-card-actions class="py-1">
                <span class="text-caption text-medium-emphasis">增长趋势</span>
              </v-card-actions>
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
            <v-form @submit.prevent="loadProducts">
              <v-row dense>
                <v-col cols="12" sm="6" md="3">
                  <v-text-field v-model="queryParams.u9_material_code" label="U9 物料号" placeholder="请输入 U9 物料号" clearable density="compact" />
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-text-field v-model="queryParams.part_number" label="规格型号" placeholder="请输入规格型号" clearable density="compact" />
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-text-field v-model="queryParams.product_name" label="物料名称" placeholder="请输入物料名称" clearable density="compact" />
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-select v-model="queryParams.category" :items="allCategoryOptions" label="物料分类" clearable density="compact" />
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-select v-model="queryParams.workshop" :items="workshopOptions" label="车间" clearable density="compact" />
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-select v-model="queryParams.material_type" :items="materialTypeOptions" label="物料类型" clearable density="compact" />
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-select v-model="queryParams.status" :items="statusOptions" label="状态" clearable density="compact" />
                </v-col>
                <v-col cols="12" sm="6" md="3" class="d-flex align-center ga-2">
                  <v-btn color="primary" prepend-icon="mdi-magnify" @click="loadProducts">查询</v-btn>
                  <v-btn variant="outlined" prepend-icon="mdi-undo" @click="resetQuery">重置</v-btn>
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>
        </v-card>

        <!-- Product table -->
        <v-card>
          <v-card-title class="d-flex align-center ga-2">
            <v-icon icon="mdi-format-list-bulleted" />
            物料列表
            <v-spacer />
            <v-btn color="error" variant="outlined" prepend-icon="mdi-delete" size="small" :disabled="selectedProducts.length === 0" @click="batchDelete">
              批量删除 ({{ selectedProducts.length }})
            </v-btn>
            <v-btn variant="outlined" prepend-icon="mdi-refresh" size="small" @click="loadProducts">刷新</v-btn>
          </v-card-title>
          <v-data-table
            :headers="productHeaders"
            :items="productList"
            :loading="loading"
            :items-per-page="pagination.pageSize"
            :page="pagination.current"
            :server-items-length="pagination.total"
            show-select
            v-model="selectedProducts"
            item-value="id"
            hover
            @update:page="p => { pagination.current = p; loadProducts() }"
            @update:items-per-page="s => { pagination.pageSize = s; pagination.current = 1; loadProducts() }"
          >
            <template v-slot:item.u9_material_code="{ item }">
              <v-chip size="small" variant="tonal" color="primary">{{ item.u9_material_code }}</v-chip>
            </template>
            <template v-slot:item.part_number="{ item }">
              <v-chip size="small" variant="tonal" color="primary">{{ item.part_number }}</v-chip>
            </template>
            <template v-slot:item.project="{ item }">
              <span class="text-caption text-truncate d-inline-block" style="max-width:120px">{{ item.project || '-' }}</span>
            </template>
            <template v-slot:item.product_name="{ item }">
              <span class="text-caption text-truncate d-inline-block" style="max-width:180px">{{ item.product_name }}</span>
            </template>
            <template v-slot:item.workshop="{ item }">
              <span class="text-caption">{{ item.workshop || '-' }}</span>
            </template>
            <template v-slot:item.category="{ item }">
              <v-chip :color="categoryColor(item.category)" size="small" variant="tonal">{{ item.category || '未分类' }}</v-chip>
            </template>
            <template v-slot:item.material_type="{ item }">
              <v-chip :color="materialTypeColor(item.material_type)" size="small" variant="tonal">
                {{ materialTypeLabel(item.material_type) }}
              </v-chip>
            </template>
            <template v-slot:item.unit_work_time="{ item }">
              <v-chip size="small" variant="tonal" color="info">{{ formatUnitWorkTime(item.unit_work_time) }}</v-chip>
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
                <v-btn icon variant="text" size="small" @click="viewProduct(item)">
                  <v-icon icon="mdi-eye" size="small" />
                  <v-tooltip activator="parent" location="top">查看详情</v-tooltip>
                </v-btn>
                <v-btn icon variant="text" size="small" @click="editProduct(item)">
                  <v-icon icon="mdi-pencil" size="small" />
                  <v-tooltip activator="parent" location="top">编辑</v-tooltip>
                </v-btn>
                <v-btn icon variant="text" size="small" @click="toggleProductStatus(item)">
                  <v-icon :icon="item.status === 'active' ? 'mdi-pause-circle' : 'mdi-play-circle'" size="small" />
                  <v-tooltip activator="parent" location="top">{{ item.status === 'active' ? '禁用' : '启用' }}</v-tooltip>
                </v-btn>
                <v-btn icon variant="text" size="small" color="purple" @click="viewMaterialEvents(item)">
                  <v-icon icon="mdi-cog-transfer" size="small" />
                  <v-tooltip activator="parent" location="top">加工事件</v-tooltip>
                </v-btn>
                <v-btn icon variant="text" size="small" color="error" @click="deleteProduct(item)">
                  <v-icon icon="mdi-delete" size="small" />
                  <v-tooltip activator="parent" location="top">删除</v-tooltip>
                </v-btn>
              </div>
            </template>
            <template v-slot:no-data>
              <div class="text-center pa-8">
                <v-icon icon="mdi-inbox" size="48" color="grey-lighten-1" />
                <p class="text-medium-emphasis mt-2">暂无物料数据</p>
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-window-item>

      <!-- Orders Tab -->
      <v-window-item value="orders">
        <!-- Order query -->
        <v-card class="mb-4">
          <v-card-title class="d-flex align-center ga-2">
            <v-icon icon="mdi-magnify" />
            订单查询
          </v-card-title>
          <v-divider />
          <v-card-text>
            <v-form @submit.prevent="querySingleOrder">
              <v-row dense>
                <v-col cols="12" sm="6" md="3">
                  <v-text-field v-model="orderQuery.partNumber" label="零件号" placeholder="请输入零件号（可选）" clearable density="compact" />
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-text-field v-model="orderQuery.u9MaterialCode" label="U9 料号" placeholder="请输入 U9 料号（可选）" clearable density="compact" />
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-text-field v-model="orderQuery.startDate" label="开始日期" type="date" density="compact" />
                </v-col>
                <v-col cols="12" sm="6" md="3">
                  <v-text-field v-model="orderQuery.endDate" label="结束日期" type="date" density="compact" />
                </v-col>
                <v-col cols="12" sm="6" md="3" class="d-flex align-center ga-2">
                  <v-btn color="primary" prepend-icon="mdi-magnify" :loading="querying" @click="querySingleOrder">查询单个零件</v-btn>
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>
        </v-card>

        <!-- Single query result -->
        <v-card v-if="orderQueryResult && orderQueryResult.data" class="mb-4">
          <v-card-title class="d-flex align-center ga-2">
            <v-icon icon="mdi-receipt" />
            查询结果
            <v-spacer />
            <v-chip color="success" variant="tonal" size="small">
              <v-icon icon="mdi-check-circle" start />查询成功
            </v-chip>
          </v-card-title>
          <v-divider />
          <v-card-text>
            <v-row dense class="mb-4">
              <v-col cols="6" md="2">
                <div class="text-caption text-medium-emphasis">计划总产量</div>
                <div class="text-h6">{{ orderQueryResult.data.planned_output?.toLocaleString() || 0 }}</div>
              </v-col>
              <v-col cols="6" md="2">
                <div class="text-caption text-medium-emphasis">规格型号</div>
                <div class="text-h6">{{ orderQueryResult.data.specs || '-' }}</div>
              </v-col>
              <v-col cols="6" md="2">
                <div class="text-caption text-medium-emphasis">单件工时</div>
                <div class="text-h6">{{ formatUnitWorkTime(orderQueryResult.data.unit_work_time) }}</div>
              </v-col>
              <v-col cols="6" md="2">
                <div class="text-caption text-medium-emphasis">查询日期</div>
                <div class="text-h6">{{ orderQueryResult.data.date || '-' }}</div>
              </v-col>
              <v-col cols="6" md="2">
                <div class="text-caption text-medium-emphasis">订单数量</div>
                <div class="text-h6">{{ orderQueryResult.data.details?.length || 0 }}</div>
              </v-col>
            </v-row>
            <v-data-table
              :headers="orderDetailHeaders"
              :items="orderQueryResult.data.details || []"
              :items-per-page="10"
              density="compact"
              hover
            >
              <template v-slot:item.docNo="{ item }">
                <v-chip size="small" variant="tonal" color="primary">{{ item.docNo }}</v-chip>
              </template>
              <template v-slot:item.itemCode="{ item }">
                <v-chip size="small" variant="tonal" color="primary">{{ item.itemCode }}</v-chip>
              </template>
              <template v-slot:item.productQty="{ item }">
                <v-chip size="small" color="primary">{{ item.productQty?.toLocaleString() || 0 }}</v-chip>
              </template>
              <template v-slot:item.startDate="{ item }">
                {{ formatDate(item.startDate) || formatDate(item.orderDate) || '-' }}
              </template>
              <template v-slot:no-data>
                <div class="text-center pa-4">
                  <v-icon icon="mdi-inbox" size="36" color="grey-lighten-1" />
                  <p class="text-medium-emphasis mt-1">暂无订单数据</p>
                </div>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>

        <!-- Batch query result -->
        <v-card v-if="batchQueryResult" class="mb-4">
          <v-card-title class="d-flex align-center ga-2">
            <v-icon icon="mdi-format-list-bulleted" />
            批量查询结果
            <v-spacer />
            <v-chip color="success" variant="tonal" size="small">
              <v-icon icon="mdi-check-circle" start />{{ batchQueryResult.message }}
            </v-chip>
          </v-card-title>
          <v-divider />
          <v-card-text>
            <v-row dense class="mb-4">
              <v-col cols="6" md="3">
                <div class="text-caption text-medium-emphasis">查询物料数</div>
                <div class="text-h6">{{ batchQueryResult.total_queried }}</div>
              </v-col>
              <v-col cols="6" md="3">
                <div class="text-caption text-medium-emphasis">保存订单数</div>
                <div class="text-h6">{{ batchQueryResult.total_saved }}</div>
              </v-col>
            </v-row>
            <v-data-table
              :headers="batchResultHeaders"
              :items="batchQueryResult.results || []"
              :items-per-page="10"
              density="compact"
              hover
            >
              <template v-slot:item.part_number="{ item }">
                <v-chip size="small" variant="tonal" color="primary">{{ item.part_number }}</v-chip>
              </template>
              <template v-slot:item.status="{ item }">
                <v-chip :color="item.status === 'success' ? 'success' : 'error'" size="small" variant="tonal">
                  {{ item.status === 'success' ? '成功' : '失败' }}
                </v-chip>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>

        <!-- Loading overlay -->
        <v-overlay :model-value="querying" class="align-center justify-center" persistent>
          <v-card class="pa-4">
            <v-progress-circular indeterminate color="primary" class="mr-3" />
            {{ loadingText }}
          </v-card>
        </v-overlay>

        <!-- Scheduler management -->
        <v-card>
          <v-card-title class="d-flex align-center ga-2">
            <v-icon icon="mdi-clock-outline" />
            定时任务管理
            <v-spacer />
            <v-chip :color="schedulerStatus.is_running ? 'success' : 'grey'" variant="tonal" size="small">
              <v-icon :icon="schedulerStatus.is_running ? 'mdi-play-circle' : 'mdi-pause-circle'" start />
              {{ schedulerStatus.is_running ? '运行中' : '已停止' }}
            </v-chip>
          </v-card-title>
          <v-divider />
          <v-card-text>
            <v-row dense class="mb-4">
              <v-col cols="12" md="6">
                <div class="text-caption text-medium-emphasis">下次执行时间</div>
                <div class="d-flex align-center ga-1">
                  <v-icon icon="mdi-calendar-clock" size="small" />
                  {{ formatDateTime(schedulerStatus.next_run_time) || '未设置' }}
                </div>
              </v-col>
              <v-col cols="12" md="6">
                <div class="text-caption text-medium-emphasis">上次执行时间</div>
                <div class="d-flex align-center ga-1">
                  <v-icon icon="mdi-calendar-check" size="small" />
                  {{ formatDateTime(schedulerStatus.last_run_time) || '未执行' }}
                </div>
              </v-col>
            </v-row>

            <v-row v-if="schedulerStatus.last_run_stats" dense class="mb-4">
              <v-col cols="6" md="2">
                <div class="text-caption text-medium-emphasis">查询物料数</div>
                <div class="text-h6">{{ schedulerStatus.last_run_stats.total_products }}</div>
              </v-col>
              <v-col cols="6" md="2">
                <div class="text-caption text-medium-emphasis">成功</div>
                <div class="text-h6 text-success">{{ schedulerStatus.last_run_stats.success_count }}</div>
              </v-col>
              <v-col cols="6" md="2">
                <div class="text-caption text-medium-emphasis">失败</div>
                <div class="text-h6 text-error">{{ schedulerStatus.last_run_stats.failed_count }}</div>
              </v-col>
              <v-col cols="6" md="2">
                <div class="text-caption text-medium-emphasis">保存订单数</div>
                <div class="text-h6">{{ schedulerStatus.last_run_stats.total_saved }}</div>
              </v-col>
              <v-col cols="6" md="2">
                <div class="text-caption text-medium-emphasis">耗时</div>
                <div class="text-h6">{{ Number(schedulerStatus.last_run_stats.duration_seconds || 0).toFixed(1) }}s</div>
              </v-col>
            </v-row>

            <div class="d-flex ga-2 flex-wrap">
              <v-btn
                :color="schedulerStatus.is_running ? 'error' : 'success'"
                :prepend-icon="schedulerStatus.is_running ? 'mdi-stop-circle' : 'mdi-play-circle'"
                :loading="schedulerLoading"
                @click="toggleScheduler"
              >
                {{ schedulerStatus.is_running ? '停止定时任务' : '启动定时任务' }}
              </v-btn>
              <v-btn color="primary" prepend-icon="mdi-lightning-bolt" :loading="schedulerLoading" :disabled="!schedulerStatus.is_running" @click="triggerScheduler">
                立即执行一次
              </v-btn>
              <v-btn variant="outlined" prepend-icon="mdi-cog" :loading="schedulerLoading" @click="showSchedulerConfig = true">
                配置执行时间
              </v-btn>
              <v-btn variant="outlined" prepend-icon="mdi-refresh" :loading="schedulerLoading" @click="loadSchedulerStatus">
                刷新状态
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-window-item>

      <!-- Logs Tab -->
      <v-window-item value="logs">
        <!-- Log stats -->
        <v-row dense class="mb-4">
          <v-col cols="6" md="2">
            <v-card>
              <v-card-text class="text-center">
                <v-icon icon="mdi-text-box-outline" color="blue" size="28" />
                <div class="text-h6 mt-1">{{ logStats.total_queries || 0 }}</div>
                <div class="text-caption text-medium-emphasis">总查询数</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" md="2">
            <v-card>
              <v-card-text class="text-center">
                <v-icon icon="mdi-check-circle" color="green" size="28" />
                <div class="text-h6 mt-1">{{ logStats.success_count || 0 }}</div>
                <div class="text-caption text-medium-emphasis">成功</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" md="2">
            <v-card>
              <v-card-text class="text-center">
                <v-icon icon="mdi-close-circle" color="red" size="28" />
                <div class="text-h6 mt-1">{{ logStats.failed_count || 0 }}</div>
                <div class="text-caption text-medium-emphasis">失败</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" md="2">
            <v-card>
              <v-card-text class="text-center">
                <v-icon icon="mdi-database" color="purple" size="28" />
                <div class="text-h6 mt-1">{{ logStats.total_saved || 0 }}</div>
                <div class="text-caption text-medium-emphasis">保存订单数</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" md="2">
            <v-card>
              <v-card-text class="text-center">
                <v-icon icon="mdi-timer" color="orange" size="28" />
                <div class="text-h6 mt-1">{{ logStats.avg_duration || 0 }}s</div>
                <div class="text-caption text-medium-emphasis">平均耗时</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Log list -->
        <v-card>
          <v-card-title class="d-flex align-center ga-2">
            <v-icon icon="mdi-format-list-bulleted" />
            查询日志列表
            <v-spacer />
            <v-btn variant="outlined" prepend-icon="mdi-refresh" size="small" @click="loadLogs">刷新</v-btn>
            <v-btn color="error" variant="outlined" prepend-icon="mdi-delete" size="small" @click="showClearDialog = true">清空日志</v-btn>
          </v-card-title>
          <v-divider />
          <v-card-text>
            <v-row dense class="mb-4">
              <v-col cols="12" sm="6" md="2">
                <v-text-field v-model="logFilters.part_number" label="零件号" placeholder="输入零件号" clearable density="compact" />
              </v-col>
              <v-col cols="12" sm="6" md="2">
                <v-select v-model="logFilters.execution_type" :items="executionTypeOptions" label="执行类型" clearable density="compact" />
              </v-col>
              <v-col cols="12" sm="6" md="2">
                <v-select v-model="logFilters.status" :items="logStatusOptions" label="状态" clearable density="compact" />
              </v-col>
              <v-col cols="12" sm="6" md="2">
                <v-text-field v-model="logFilters.start_date" label="开始日期" type="date" density="compact" />
              </v-col>
              <v-col cols="12" sm="6" md="2">
                <v-text-field v-model="logFilters.end_date" label="结束日期" type="date" density="compact" />
              </v-col>
              <v-col cols="12" sm="6" md="2" class="d-flex align-center ga-2">
                <v-btn color="primary" prepend-icon="mdi-magnify" size="small" :loading="logsLoading" @click="applyFilters">查询</v-btn>
                <v-btn variant="outlined" prepend-icon="mdi-close-circle" size="small" @click="resetFilters">重置</v-btn>
              </v-col>
            </v-row>

            <v-data-table
              :headers="logHeaders"
              :items="logs"
              :loading="logsLoading"
              :items-per-page="logPagination.pageSize"
              :page="logPagination.page"
              :server-items-length="logPagination.total"
              density="compact"
              hover
              @update:page="p => { logPagination.page = p; loadLogs() }"
              @update:items-per-page="s => { logPagination.pageSize = s; logPagination.page = 1; loadLogs() }"
            >
              <template v-slot:item.status="{ item }">
                <v-chip :color="item.status === 'success' ? 'success' : 'error'" size="small" variant="tonal">
                  <v-icon :icon="item.status === 'success' ? 'mdi-check-circle' : 'mdi-close-circle'" start size="small" />
                  {{ item.status === 'success' ? '成功' : '失败' }}
                </v-chip>
              </template>
              <template v-slot:item.execution_type="{ item }">
                <v-chip :color="item.execution_type === 'auto' ? 'primary' : 'grey'" size="small" variant="tonal">
                  <v-icon :icon="item.execution_type === 'auto' ? 'mdi-clock-outline' : 'mdi-account'" start size="small" />
                  {{ item.execution_type === 'auto' ? '自动' : '手动' }}
                </v-chip>
              </template>
              <template v-slot:item.duration_seconds="{ item }">
                {{ Number(item.duration_seconds || 0).toFixed(2) }}s
              </template>
              <template v-slot:item.created_at="{ item }">
                {{ formatDateTime(item.created_at) }}
              </template>
              <template v-slot:item.actions="{ item }">
                <div class="d-flex ga-1">
                  <v-btn icon variant="text" size="small" @click="viewLogDetail(item)">
                    <v-icon icon="mdi-eye" size="small" />
                    <v-tooltip activator="parent" location="top">查看详情</v-tooltip>
                  </v-btn>
                  <v-btn icon variant="text" size="small" color="error" @click="deleteLog(item.id)">
                    <v-icon icon="mdi-delete" size="small" />
                    <v-tooltip activator="parent" location="top">删除</v-tooltip>
                  </v-btn>
                </div>
              </template>
              <template v-slot:no-data>
                <div class="text-center pa-8">
                  <v-icon icon="mdi-text-box-outline" size="48" color="grey-lighten-1" />
                  <p class="text-medium-emphasis mt-2">暂无日志数据</p>
                </div>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-window-item>

      <!-- Local Records Tab -->
      <v-window-item value="local-records">
        <!-- Stats -->
        <v-row dense class="mb-4">
          <v-col cols="6" md="2">
            <v-card>
              <v-card-text class="text-center">
                <v-icon icon="mdi-clipboard-check-outline" color="blue" size="28" />
                <div class="text-h6 mt-1">{{ localRecordStats.total_records || 0 }}</div>
                <div class="text-caption text-medium-emphasis">今日总记录</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" md="2">
            <v-card>
              <v-card-text class="text-center">
                <v-icon icon="mdi-play-circle" color="green" size="28" />
                <div class="text-h6 mt-1">{{ localRecordStats.in_progress || 0 }}</div>
                <div class="text-caption text-medium-emphasis">进行中</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" md="2">
            <v-card>
              <v-card-text class="text-center">
                <v-icon icon="mdi-check-circle" color="purple" size="28" />
                <div class="text-h6 mt-1">{{ localRecordStats.completed || 0 }}</div>
                <div class="text-caption text-medium-emphasis">已完成</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" md="2">
            <v-card>
              <v-card-text class="text-center">
                <v-icon icon="mdi-package-variant-closed" color="orange" size="28" />
                <div class="text-h6 mt-1">{{ localRecordStats.total_completed || 0 }}</div>
                <div class="text-caption text-medium-emphasis">完成数量</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" md="2">
            <v-card>
              <v-card-text class="text-center">
                <v-icon icon="mdi-speedometer" color="red" size="28" />
                <div class="text-h6 mt-1">{{ localRecordStats.overall_completion_rate || 0 }}%</div>
                <div class="text-caption text-medium-emphasis">完成率</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Local records table -->
        <v-card>
          <v-card-title class="d-flex align-center ga-2">
            <v-icon icon="mdi-format-list-bulleted" />
            本地加工记录
            <v-spacer />
            <v-btn color="primary" prepend-icon="mdi-plus" size="small" @click="openLocalRecordDialog()">新增记录</v-btn>
            <v-btn variant="outlined" prepend-icon="mdi-refresh" size="small" @click="loadLocalRecords">刷新</v-btn>
          </v-card-title>
          <v-divider />
          <v-card-text>
            <v-row dense class="mb-4">
              <v-col cols="12" sm="6" md="3">
                <v-select v-model="localRecordFilter.device_code" :items="allDevices.map(d => ({ title: d.device_name + ' (' + d.device_code + ')', value: d.device_code }))" label="设备" clearable density="compact" @update:model-value="loadLocalRecords" />
              </v-col>
              <v-col cols="12" sm="6" md="3">
                <v-text-field v-model="localRecordFilter.record_date" label="日期" type="date" density="compact" @update:model-value="loadLocalRecords" />
              </v-col>
              <v-col cols="12" sm="6" md="3">
                <v-select v-model="localRecordFilter.status" :items="localRecordStatusOptions" label="状态" clearable density="compact" @update:model-value="loadLocalRecords" />
              </v-col>
            </v-row>

            <v-data-table
              :headers="localRecordHeaders"
              :items="localRecords"
              :items-per-page="20"
              density="compact"
              hover
            >
              <template v-slot:item.device_code="{ item }">
                <v-chip size="small" variant="tonal" color="primary">{{ item.device_code }}</v-chip>
              </template>
              <template v-slot:item.part_number="{ item }">
                <v-chip size="small" variant="tonal" color="primary">{{ item.part_number || '-' }}</v-chip>
              </template>
              <template v-slot:item.completion_rate="{ item }">
                <v-progress-linear :model-value="Math.min(item.completion_rate || 0, 100)" color="success" height="20" rounded>
                  <template v-slot:default="{ value }">
                    <span class="text-caption font-weight-bold">{{ value }}%</span>
                  </template>
                </v-progress-linear>
              </template>
              <template v-slot:item.status="{ item }">
                <v-chip :color="item.status === 'completed' ? 'success' : item.status === 'paused' ? 'warning' : 'primary'" size="small" variant="tonal">
                  {{ item.status === 'completed' ? '已完成' : item.status === 'paused' ? '已暂停' : '进行中' }}
                </v-chip>
              </template>
              <template v-slot:item.actions="{ item }">
                <div class="d-flex ga-1">
                  <v-btn icon variant="text" size="small" @click="openLocalRecordDialog(item)">
                    <v-icon icon="mdi-pencil" size="small" />
                    <v-tooltip activator="parent" location="top">编辑</v-tooltip>
                  </v-btn>
                  <v-btn v-if="item.status !== 'completed'" icon variant="text" size="small" color="success" @click="completeLocalRecord(item.id)">
                    <v-icon icon="mdi-check" size="small" />
                    <v-tooltip activator="parent" location="top">标记完成</v-tooltip>
                  </v-btn>
                  <v-btn icon variant="text" size="small" color="error" @click="deleteLocalRecord(item.id)">
                    <v-icon icon="mdi-delete" size="small" />
                    <v-tooltip activator="parent" location="top">删除</v-tooltip>
                  </v-btn>
                </div>
              </template>
              <template v-slot:no-data>
                <div class="text-center pa-8">
                  <v-icon icon="mdi-inbox" size="48" color="grey-lighten-1" />
                  <p class="text-medium-emphasis mt-2">暂无加工记录</p>
                </div>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-window-item>

      <!-- Local Orders Tab -->
      <v-window-item value="local-orders">
        <!-- Stats -->
        <v-row dense class="mb-4">
          <v-col cols="6" md="3">
            <v-card>
              <v-card-text class="text-center">
                <v-icon icon="mdi-receipt" color="blue" size="28" />
                <div class="text-h6 mt-1">{{ localOrderStats.total_orders?.toLocaleString() || '0' }}</div>
                <div class="text-caption text-medium-emphasis">总订单数</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" md="3">
            <v-card>
              <v-card-text class="text-center">
                <v-icon icon="mdi-package-variant-closed" color="green" size="28" />
                <div class="text-h6 mt-1">{{ localOrderStats.total_planned_output?.toLocaleString() || '0' }}</div>
                <div class="text-caption text-medium-emphasis">计划总产量</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" md="3">
            <v-card>
              <v-card-text class="text-center">
                <v-icon icon="mdi-format-list-numbered" color="purple" size="28" />
                <div class="text-h6 mt-1">{{ localOrderStats.total_detail_count?.toLocaleString() || '0' }}</div>
                <div class="text-caption text-medium-emphasis">明细数量</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="6" md="3">
            <v-card>
              <v-card-text class="text-center">
                <v-icon icon="mdi-calendar-today" color="orange" size="28" />
                <div class="text-h6 mt-1">{{ localOrderStats.today_orders?.toLocaleString() || '0' }}</div>
                <div class="text-caption text-medium-emphasis">今日订单</div>
                <div class="text-caption">产量：{{ localOrderStats.today_planned_output?.toLocaleString() || 0 }}</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Local orders table -->
        <v-card>
          <v-card-title class="d-flex align-center ga-2">
            <v-icon icon="mdi-receipt-text-check" />
            本地订单列表
            <v-spacer />
            <v-btn variant="outlined" prepend-icon="mdi-refresh" size="small" @click="loadLocalOrders">刷新</v-btn>
            <v-btn color="primary" variant="outlined" prepend-icon="mdi-chart-bar" size="small" @click="showLocalOrderAnalysis = true; loadLocalOrderAnalysis()">综合分析</v-btn>
            <v-btn color="error" variant="outlined" prepend-icon="mdi-delete" size="small" @click="confirmClearLocalOrders">清除今日</v-btn>
          </v-card-title>
          <v-divider />
          <v-card-text>
            <v-row dense class="mb-4">
              <v-col cols="12" sm="6" md="2">
                <v-text-field v-model="localOrderFilter.part_number" label="零件号" placeholder="输入零件号" clearable density="compact" @keyup.enter="localOrderFilter.page = 1; loadLocalOrders()" />
              </v-col>
              <v-col cols="12" sm="6" md="2">
                <v-text-field v-model="localOrderFilter.doc_no" label="订单号" placeholder="输入订单号" clearable density="compact" @keyup.enter="localOrderFilter.page = 1; loadLocalOrders()" />
              </v-col>
              <v-col cols="12" sm="6" md="2">
                <v-select v-model="localOrderFilter.doc_state" :items="docStateOptions" label="订单状态" clearable density="compact" />
              </v-col>
              <v-col cols="12" sm="6" md="2">
                <v-select v-model="localOrderFilter.doc_type" :items="docTypeOptions" label="白晚班" clearable density="compact" />
              </v-col>
              <v-col cols="12" sm="6" md="2">
                <v-text-field v-model="localOrderFilter.start_date" label="开始日期" type="date" density="compact" />
              </v-col>
              <v-col cols="12" sm="6" md="2">
                <v-text-field v-model="localOrderFilter.end_date" label="结束日期" type="date" density="compact" />
              </v-col>
              <v-col cols="12" sm="6" md="2" class="d-flex align-center">
                <v-btn color="primary" prepend-icon="mdi-magnify" size="small" @click="localOrderFilter.page = 1; loadLocalOrders()">查询</v-btn>
              </v-col>
            </v-row>

            <v-data-table
              :headers="localOrderHeaders"
              :items="localOrders"
              :items-per-page="localOrderPagination.page_size"
              :page="localOrderPagination.page"
              :server-items-length="localOrderPagination.total"
              density="compact"
              hover
              show-expand
              item-value="id"
              v-model:expanded="expandedLocalOrders"
              @update:page="p => changeLocalOrderPage(p)"
              @update:items-per-page="s => { localOrderPagination.page_size = s; localOrderFilter.page = 1; loadLocalOrders() }"
            >
              <template v-slot:item.part_number="{ item }">
                <v-chip size="small" variant="tonal" color="primary">{{ item.part_number }}</v-chip>
              </template>
              <template v-slot:item.planned_output="{ item }">
                <v-chip size="small" variant="tonal" color="info">{{ item.planned_output?.toLocaleString() }}</v-chip>
              </template>
              <template v-slot:item.start_date="{ item }">
                {{ item.start_date ? new Date(item.start_date).toLocaleDateString() : '-' }}
              </template>
              <template v-slot:item.doc_state="{ item }">
                <v-chip :color="item.doc_state === '开工' ? 'primary' : item.doc_state === '完工' ? 'success' : item.doc_state === '核准中' ? 'warning' : 'grey'" size="small" variant="tonal">
                  {{ item.doc_state || '-' }}
                </v-chip>
              </template>
              <template v-slot:expanded-row="{ columns, item }">
                <tr v-if="item.details">
                  <td :colspan="columns.length" class="pa-0">
                    <v-card flat class="ma-2">
                      <v-card-text>
                        <v-data-table
                          :headers="localOrderDetailHeaders"
                          :items="item.details"
                          :items-per-page="50"
                          density="compact"
                        >
                          <template v-slot:item.doc_no="{ item: detail }">
                            <v-chip size="small" variant="tonal" color="primary">{{ detail.doc_no }}</v-chip>
                          </template>
                          <template v-slot:item.doc_state="{ item: detail }">
                            <v-chip color="success" size="small" variant="tonal">{{ detail.doc_state || '-' }}</v-chip>
                          </template>
                        </v-data-table>
                      </v-card-text>
                    </v-card>
                  </td>
                </tr>
              </template>
              <template v-slot:no-data>
                <div class="text-center pa-8">
                  <v-icon icon="mdi-inbox" size="48" color="grey-lighten-1" />
                  <p class="text-medium-emphasis mt-2">暂无订单数据</p>
                </div>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-window-item>
    </v-window>

    <!-- Add/Edit Product Dialog -->
    <v-dialog v-model="showAddDialog" max-width="700" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-plus" class="mr-2" />
          新增物料
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="closeDialogs" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-form @submit.prevent="saveProduct">
            <div class="text-subtitle-2 mb-2"><v-icon icon="mdi-information-outline" class="mr-1" />基本信息</div>
            <v-row dense>
              <v-col cols="12" md="6">
                <v-text-field v-model="formData.u9_material_code" label="U9 物料号" :rules="[v => !!v || '请输入 U9 物料号']" required />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="formData.part_number" label="规格型号" />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="formData.product_name" label="物料名称" :rules="[v => !!v || '请输入物料名称']" required />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="formData.description" label="物料描述" />
              </v-col>
            </v-row>
            <div class="text-subtitle-2 mb-2 mt-4"><v-icon icon="mdi-ruler" class="mr-1" />规格信息</div>
            <v-row dense>
              <v-col cols="12" md="4">
                <v-select v-model="formData.unit" :items="unitOptions" label="单位" />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field v-model="formData.unit_work_time" label="单件工时（小时）" type="number" min="0" step="0.00001" />
              </v-col>
              <v-col cols="12" md="4">
                <v-select v-model="formData.material_type" :items="materialTypeOptions.filter(o => o.value)" label="物料类型" />
              </v-col>
              <v-col cols="12" md="4">
                <v-select v-model="formData.category" :items="categoryOptions" label="物料分类" clearable />
              </v-col>
              <v-col cols="12" md="4">
                <v-select v-model="formData.project" :items="projectOptions" label="项目" clearable />
              </v-col>
              <v-col cols="12" md="4">
                <v-select v-model="formData.workshop" :items="workshopOptions" label="车间" clearable />
              </v-col>
              <v-col cols="12" md="4">
                <v-select v-model="formData.status" :items="statusOptions.filter(o => o.value)" label="状态" />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeDialogs">取消</v-btn>
          <v-btn color="primary" :loading="saving" @click="saveProduct">保存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="showEditDialog" max-width="700" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-pencil" class="mr-2" />
          编辑物料
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="closeDialogs" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-form @submit.prevent="saveProduct">
            <div class="text-subtitle-2 mb-2"><v-icon icon="mdi-information-outline" class="mr-1" />基本信息</div>
            <v-row dense>
              <v-col cols="12" md="6">
                <v-text-field v-model="formData.u9_material_code" label="U9 物料号" disabled />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="formData.part_number" label="规格型号" />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="formData.product_name" label="物料名称" :rules="[v => !!v || '请输入物料名称']" required />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="formData.description" label="物料描述" />
              </v-col>
            </v-row>
            <div class="text-subtitle-2 mb-2 mt-4"><v-icon icon="mdi-ruler" class="mr-1" />规格信息</div>
            <v-row dense>
              <v-col cols="12" md="4">
                <v-select v-model="formData.unit" :items="unitOptions" label="单位" />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field v-model="formData.unit_work_time" label="单件工时（小时）" type="number" min="0" step="0.00001" />
              </v-col>
              <v-col cols="12" md="4">
                <v-select v-model="formData.material_type" :items="materialTypeOptions.filter(o => o.value)" label="物料类型" />
              </v-col>
              <v-col cols="12" md="4">
                <v-select v-model="formData.category" :items="categoryOptions" label="物料分类" clearable />
              </v-col>
              <v-col cols="12" md="4">
                <v-select v-model="formData.project" :items="projectOptions" label="项目" clearable />
              </v-col>
              <v-col cols="12" md="4">
                <v-select v-model="formData.workshop" :items="workshopOptions" label="车间" clearable />
              </v-col>
              <v-col cols="12" md="4">
                <v-select v-model="formData.status" :items="statusOptions.filter(o => o.value)" label="状态" />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeDialogs">取消</v-btn>
          <v-btn color="primary" :loading="saving" @click="saveProduct">保存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- View Product Dialog -->
    <v-dialog v-model="showViewDialog" max-width="700">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-eye" class="mr-2" />
          物料详情
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="closeDialogs" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <div class="text-subtitle-2 mb-2"><v-icon icon="mdi-information-outline" class="mr-1" />基本信息</div>
          <v-table density="compact">
            <tbody>
              <tr><td class="text-medium-emphasis" style="width:120px">U9 物料号</td><td><v-chip size="small" variant="tonal" color="primary">{{ viewData.u9_material_code }}</v-chip></td></tr>
              <tr><td class="text-medium-emphasis">规格型号</td><td>{{ viewData.part_number || '-' }}</td></tr>
              <tr><td class="text-medium-emphasis">项目名称</td><td>{{ viewData.project || '-' }}</td></tr>
              <tr><td class="text-medium-emphasis">车间</td><td>{{ viewData.workshop || '未设置' }}</td></tr>
              <tr><td class="text-medium-emphasis">物料名称</td><td>{{ viewData.product_name }}</td></tr>
              <tr><td class="text-medium-emphasis">物料描述</td><td>{{ viewData.description || '暂无描述' }}</td></tr>
            </tbody>
          </v-table>
          <div class="text-subtitle-2 mb-2 mt-4"><v-icon icon="mdi-ruler" class="mr-1" />规格信息</div>
          <v-table density="compact">
            <tbody>
              <tr><td class="text-medium-emphasis" style="width:120px">单位</td><td>{{ viewData.unit || '未设置' }}</td></tr>
              <tr><td class="text-medium-emphasis">单件工时</td><td>{{ formatUnitWorkTime(viewData.unit_work_time) }}</td></tr>
              <tr><td class="text-medium-emphasis">物料分类</td><td>{{ viewData.category || '未分类' }}</td></tr>
              <tr><td class="text-medium-emphasis">物料类型</td><td><v-chip :color="materialTypeColor(viewData.material_type)" size="small" variant="tonal">{{ materialTypeLabel(viewData.material_type) }}</v-chip></td></tr>
              <tr><td class="text-medium-emphasis">状态</td><td><v-chip :color="viewData.status === 'active' ? 'success' : 'error'" size="small" variant="tonal">{{ viewData.status === 'active' ? '启用' : '禁用' }}</v-chip></td></tr>
            </tbody>
          </v-table>
          <div class="text-subtitle-2 mb-2 mt-4"><v-icon icon="mdi-clock-outline" class="mr-1" />时间信息</div>
          <v-table density="compact">
            <tbody>
              <tr><td class="text-medium-emphasis" style="width:120px">创建时间</td><td>{{ formatDateTime(viewData.created_at) }}</td></tr>
              <tr><td class="text-medium-emphasis">更新时间</td><td>{{ formatDateTime(viewData.updated_at) }}</td></tr>
              <tr><td class="text-medium-emphasis">创建人</td><td>{{ viewData.created_by || '系统' }}</td></tr>
              <tr><td class="text-medium-emphasis">更新人</td><td>{{ viewData.updated_by || '-' }}</td></tr>
            </tbody>
          </v-table>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeDialogs">关闭</v-btn>
          <v-btn color="primary" prepend-icon="mdi-pencil" @click="editFromView">编辑</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 分类管理对话框 -->
    <v-dialog v-model="showCategoryDialog" max-width="700" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-tag-multiple" class="mr-2" />
          分类管理
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="showCategoryDialog = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-row>
            <v-col cols="4">
              <div class="text-subtitle-2 mb-2">物料类型</div>
              <v-list density="compact" nav>
                <v-list-item
                  v-for="type in categoryTypeOptions"
                  :key="type.key"
                  :title="type.name"
                  :active="selectedTypeKey === type.key"
                  @click="selectedTypeKey = type.key"
                  active-color="primary"
                  rounded="lg"
                />
              </v-list>
            </v-col>
            <v-col cols="8">
              <div class="text-subtitle-2 mb-2">
                {{ categoryTypeOptions.find(t => t.key === selectedTypeKey)?.name }} - 分类列表
              </div>
              <div class="d-flex ga-2 mb-3">
                <v-text-field
                  v-model="newCategoryName"
                  label="新分类名称"
                  density="compact"
                  hide-details
                  @keyup.enter="addCategory"
                />
                <v-btn color="primary" size="small" @click="addCategory">添加</v-btn>
              </div>
              <v-list density="compact">
                <v-list-item
                  v-for="cat in (categoryData[selectedTypeKey] || [])"
                  :key="cat.id"
                >
                  <template v-slot:default>
                    <v-text-field
                      v-if="editingCategory === cat.id"
                      v-model="editingCategoryName"
                      density="compact"
                      hide-details
                      autofocus
                      @keyup.enter="saveEditCategory(cat.id)"
                      @blur="editingCategory = null"
                    />
                    <span v-else>{{ cat.category_name }}</span>
                  </template>
                  <template v-slot:append>
                    <v-btn icon variant="text" size="x-small" @click="startEditCategory(cat)">
                      <v-icon icon="mdi-pencil" size="small" />
                    </v-btn>
                    <v-btn icon variant="text" size="x-small" color="error" @click="deleteCategory(cat.id, cat.category_name)">
                      <v-icon icon="mdi-delete" size="small" />
                    </v-btn>
                  </template>
                </v-list-item>
                <v-list-item v-if="!(categoryData[selectedTypeKey] || []).length">
                  <v-list-item-title class="text-medium-emphasis">暂无分类</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Import Dialog -->
    <v-dialog v-model="showImportDialog" max-width="500" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-upload" class="mr-2" />
          导入物料
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="closeDialogs" />
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
            <p class="text-caption text-medium-emphasis">按照模板格式填写物料数据</p>
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
          <v-btn variant="text" @click="closeDialogs">取消</v-btn>
          <v-btn color="primary" :loading="uploading" :disabled="!importFile" @click="uploadImportFile">
            {{ uploading ? '上传中...' : '开始导入' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Scheduler Config Dialog -->
    <v-dialog v-model="showSchedulerConfig" max-width="500" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-cog" class="mr-2" />
          配置定时任务执行时间
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="closeSchedulerConfig" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-text-field v-model="schedulerCron" label="Cron 表达式" placeholder="例如：0 2 * * *（每天凌晨 2 点）" density="compact" />
          <div class="text-caption text-medium-emphasis mb-4">
            <v-icon icon="mdi-information-outline" size="small" />
            格式：分 时 日 月 星期
          </div>
          <div class="text-subtitle-2 mb-2">常用示例：</div>
          <div class="d-flex ga-2 flex-wrap">
            <v-chip v-for="example in cronExamples" :key="example.cron" :color="schedulerCron === example.cron ? 'primary' : 'default'" variant="outlined" @click="schedulerCron = example.cron" class="cursor-pointer">
              {{ example.cron }} - {{ example.desc }}
            </v-chip>
          </div>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="closeSchedulerConfig">取消</v-btn>
          <v-btn color="primary" :loading="schedulerLoading" @click="saveSchedulerConfig">保存配置</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Local Record Dialog -->
    <v-dialog v-model="showLocalRecordDialog" max-width="600" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon :icon="editingLocalRecord ? 'mdi-pencil' : 'mdi-plus'" class="mr-2" />
          {{ editingLocalRecord ? '编辑加工记录' : '新增加工记录' }}
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="showLocalRecordDialog = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-form @submit.prevent="saveLocalRecord">
            <v-row dense>
              <v-col cols="12" md="6">
                <v-select v-model="localRecordForm.device_code" :items="allDevices.map(d => ({ title: d.device_name + ' (' + d.device_code + ')', value: d.device_code }))" label="设备" :disabled="!!editingLocalRecord" :rules="[v => !!v || '请选择设备']" required />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="localRecordForm.part_number" label="零件号" :rules="[v => !!v || '请输入零件号']" required />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="localRecordForm.doc_no" label="订单单据号" />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="localRecordForm.u9_material_code" label="U9 物料号" />
              </v-col>
              <v-col cols="12" md="6">
                <v-number-input v-model.number="localRecordForm.planned_qty" label="计划数量" :min="0" controlVariant="stacked" />
              </v-col>
              <v-col cols="12" md="6">
                <v-number-input v-model.number="localRecordForm.completed_qty" label="完成数量" :min="0" controlVariant="stacked" />
              </v-col>
              <v-col cols="12" md="6">
                <v-number-input v-model.number="localRecordForm.eligible_qty" label="合格数量" :min="0" controlVariant="stacked" />
              </v-col>
              <v-col cols="12" md="6">
                <v-number-input v-model.number="localRecordForm.scrap_qty" label="报废数量" :min="0" controlVariant="stacked" />
              </v-col>
              <v-col cols="12" md="6">
                <v-select v-model="localRecordForm.status" :items="localRecordStatusOptions" label="状态" />
              </v-col>
              <v-col cols="12">
                <v-textarea v-model="localRecordForm.notes" label="备注" rows="2" />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showLocalRecordDialog = false">取消</v-btn>
          <v-btn color="primary" @click="saveLocalRecord">保存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Local Order Analysis Dialog -->
    <v-dialog v-model="showLocalOrderAnalysis" max-width="1000" scrollable>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-chart-bar" class="mr-2" />
          本地订单综合分析
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="showLocalOrderAnalysis = false" />
        </v-card-title>
        <v-divider />
        <v-card-text style="max-height: 70vh;">
          <v-row dense class="mb-4">
            <v-col cols="12" sm="5">
              <v-text-field v-model="localOrderAnalysisQuery.start_date" label="开始日期" type="date" density="compact" />
            </v-col>
            <v-col cols="12" sm="5">
              <v-text-field v-model="localOrderAnalysisQuery.end_date" label="结束日期" type="date" density="compact" />
            </v-col>
            <v-col cols="12" sm="2" class="d-flex align-center">
              <v-btn color="primary" prepend-icon="mdi-magnify" size="small" @click="loadLocalOrderAnalysis">分析</v-btn>
            </v-col>
          </v-row>

          <template v-if="localOrderAnalysisData">
            <v-row dense class="mb-4">
              <v-col cols="6" md="3">
                <div class="text-caption text-medium-emphasis">总订单数</div>
                <div class="text-h6">{{ localOrderAnalysisData.summary?.total_orders?.toLocaleString() }}</div>
              </v-col>
              <v-col cols="6" md="3">
                <div class="text-caption text-medium-emphasis">计划总产量</div>
                <div class="text-h6">{{ localOrderAnalysisData.summary?.total_planned_output?.toLocaleString() }}</div>
              </v-col>
              <v-col cols="6" md="3">
                <div class="text-caption text-medium-emphasis">明细数量</div>
                <div class="text-h6">{{ localOrderAnalysisData.summary?.total_details?.toLocaleString() }}</div>
              </v-col>
              <v-col cols="6" md="3">
                <div class="text-caption text-medium-emphasis">日均订单</div>
                <div class="text-h6">{{ localOrderAnalysisData.summary?.avg_daily_orders }}</div>
              </v-col>
            </v-row>

            <div v-if="localOrderAnalysisData.by_date?.length" class="mb-4">
              <div class="text-subtitle-2 mb-2">按日期分析</div>
              <v-data-table :headers="analysisByDateHeaders" :items="localOrderAnalysisData.by_date" :items-per-page="10" density="compact" />
            </div>

            <div v-if="localOrderAnalysisData.by_material?.length" class="mb-4">
              <div class="text-subtitle-2 mb-2">按物料分析 TOP10</div>
              <v-data-table :headers="analysisByMaterialHeaders" :items="localOrderAnalysisData.by_material.slice(0, 10)" :items-per-page="10" density="compact" />
            </div>

            <div v-if="localOrderAnalysisData.by_warehouse?.length" class="mb-4">
              <div class="text-subtitle-2 mb-2">按仓库分析</div>
              <v-data-table :headers="analysisByWarehouseHeaders" :items="localOrderAnalysisData.by_warehouse" :items-per-page="10" density="compact" />
            </div>

            <div v-if="localOrderAnalysisData.by_department?.length" class="mb-4">
              <div class="text-subtitle-2 mb-2">按部门分析</div>
              <v-data-table :headers="analysisByDepartmentHeaders" :items="localOrderAnalysisData.by_department" :items-per-page="10" density="compact" />
            </div>

            <div v-if="localOrderAnalysisData.by_doc_state?.length" class="mb-4">
              <div class="text-subtitle-2 mb-2">按订单状态分析</div>
              <v-data-table :headers="analysisByDocStateHeaders" :items="localOrderAnalysisData.by_doc_state" :items-per-page="10" density="compact" />
            </div>
          </template>
          <div v-else class="text-center pa-8">
            <v-progress-circular indeterminate color="primary" />
            <p class="text-medium-emphasis mt-2">加载中...</p>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Clear Local Orders Confirm Dialog -->
    <v-dialog v-model="showClearLocalOrderConfirm" max-width="400" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-alert" color="error" class="mr-2" />
          确认清除
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="showClearLocalOrderConfirm = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          确定要清除今天的全部本地订单数据吗？此操作不可恢复。
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showClearLocalOrderConfirm = false">取消</v-btn>
          <v-btn color="error" @click="doClearLocalOrders">确认清除</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Clear Logs Dialog -->
    <v-dialog v-model="showClearDialog" max-width="400" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-delete" color="error" class="mr-2" />
          清空日志
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="showClearDialog = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <p class="mb-4">请选择清空范围：</p>
          <v-radio-group v-model="clearDays">
            <v-radio label="清空所有日志" :value="null" />
            <v-radio label="保留最近 7 天" :value="7" />
            <v-radio label="保留最近 30 天" :value="30" />
            <v-radio label="保留最近 90 天" :value="90" />
          </v-radio-group>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showClearDialog = false">取消</v-btn>
          <v-btn color="error" @click="confirmClear">确认清空</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 加工事件对话框 -->
    <v-dialog v-model="materialEventsDialog" max-width="1000px" scrollable>
      <v-card style="display: flex; flex-direction: column; height: 70vh;">
        <v-card-title class="d-flex align-center flex-shrink-0">
          <v-icon icon="mdi-cog-transfer" class="mr-2" />
          {{ materialEventsMaterial?.product_name }} - 关联加工事件
          <v-chip size="small" class="ml-2" color="primary">{{ materialEventsMaterial?.u9_material_code }}</v-chip>
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" @click="materialEventsDialog = false" />
        </v-card-title>
        <v-divider class="flex-shrink-0" />
        <v-card-text style="flex: 1; overflow-y: auto;">
          <div v-if="materialEventsLoading" class="text-center pa-8">
            <v-progress-circular indeterminate color="primary" />
          </div>
          <div v-else-if="materialEventsData.length > 0">
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
                <tr v-for="e in materialEventsData" :key="e.id">
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
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'

const defaultCategoryMap = {
  product: ['成品', '半成品'],
  material: ['板材', '棒材', '管材', '型材'],
  auxiliary: ['焊材', '气体', '油脂', '其他'],
}
const categoryMap = ref({ ...defaultCategoryMap })
const allCategoryOptions = computed(() => Object.values(categoryMap.value).flat())
const categoryData = ref({})

// 分类管理对话框
const showCategoryDialog = ref(false)
const editingCategory = ref(null)
const editingCategoryName = ref('')
const newCategoryName = ref('')
const selectedTypeKey = ref('product')
const categoryTypeOptions = [
  { key: 'product', name: '产品' },
  { key: 'material', name: '原材料' },
  { key: 'auxiliary', name: '辅料' },
]
import { materialAPI, erpOrderAPI, localOrderAPI, productOrderLogAPI, orderProcessingAPI, deviceAPI, workshopAPI, projectAPI, materialCategoryAPI, eventAssociationAPI } from '@/api/index'
import * as echarts from 'echarts'
import { formatDateTime } from '@/utils/datetime'
import { useMessage, useConfirm } from '@/composables/useMessage'

const message = useMessage()
const confirmDialog = useConfirm()

// ========== Responsive data ==========
const activeTab = ref('products')
const showSearch = ref(true)

const productStats = ref({
  total: 0,
  active: 0,
  inactive: 0,
  categories: [],
  projects: [],
  today_added: 0,
  week_added: 0,
})

const productList = ref([])
const loading = ref(false)
const saving = ref(false)

const queryParams = reactive({
  u9_material_code: '',
  part_number: '',
  product_name: '',
  category: '',
  workshop: '',
  material_type: '',
  status: '',
  page: 1,
  page_size: 20,
})

const pagination = reactive({
  total: 0,
  current: 1,
  pageSize: 20,
  totalPages: 1,
  pageStart: 0,
  pageEnd: 0,
})

// Dialog state
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const showImportDialog = ref(false)
const showViewDialog = ref(false)

// Form data
const formData = reactive({
  id: null,
  u9_material_code: '',
  part_number: '',
  product_name: '',
  description: '',
  specification: '',
  category: '',
  project: '',
  workshop: '',
  unit: '',
  unit_work_time: 0,
  material_type: 'product',
  status: 'active',
})

const categoryOptions = computed(() => {
  const type = formData.material_type || 'product'
  return categoryMap.value[type] || []
})

watch(() => formData.material_type, (newType) => {
  const options = categoryMap.value[newType] || []
  if (!options.includes(formData.category)) {
    formData.category = ''
  }
})

const formErrors = reactive({
  u9_material_code: '',
  part_number: '',
  product_name: '',
  description: '',
  specification: '',
  category: '',
  unit: '',
  status: '',
  workshop: '',
})

const selectedProducts = ref([])
const selectAll = ref(false)

const unreadOrders = ref(0)
const unreadLogs = ref(0)

const viewData = ref({})

const importFile = ref(null)
const importFileModel = ref(null)

// ========== Order query data ==========
const querying = ref(false)
const loadingText = ref('查询中...')
const orderQueryResult = ref(null)
const batchQueryResult = ref(null)

const orderQuery = reactive({
  partNumber: '',
  u9MaterialCode: '',
  startDate: new Date().toISOString().split('T')[0],
  endDate: new Date().toISOString().split('T')[0],
})
const uploading = ref(false)
const fileInput = ref(null)

// ========== Order analysis data ==========
const analysisStartDate = ref(new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0])
const analysisEndDate = ref(new Date().toISOString().split('T')[0])
const analysisLoading = ref(false)
const orderAnalysis = ref(null)
const activeAnalysisTab = ref('by_date')

const analysisTabs = [
  { key: 'by_date', label: '按日期', icon: 'mdi-calendar' },
  { key: 'by_material', label: '按物料', icon: 'mdi-package-variant-closed' },
  { key: 'by_warehouse', label: '按仓库', icon: 'mdi-factory' },
  { key: 'by_doc_state', label: '按状态', icon: 'mdi-check-circle' },
  { key: 'by_department', label: '按部门', icon: 'mdi-account-group' },
  { key: 'by_project', label: '按项目', icon: 'mdi-folder' },
  { key: 'by_doc_type', label: '按类型', icon: 'mdi-file-document' },
  { key: 'trend', label: '趋势', icon: 'mdi-chart-line' },
]

// ========== Chart data ==========
const trendChartRef = ref(null)
const statusChartRef = ref(null)
const materialChartRef = ref(null)
const warehouseChartRef = ref(null)

let trendChart = null
let statusChart = null
let materialChart = null
let warehouseChart = null

// ========== Scheduler data ==========
const schedulerStatus = reactive({
  is_running: false,
  last_run_time: null,
  next_run_time: null,
  last_run_stats: null,
})
const schedulerLoading = ref(false)
const showSchedulerConfig = ref(false)
const schedulerCron = ref('0 2 * * *')

// ========== Log data ==========
const logs = ref([])
const logsLoading = ref(false)
const logStats = reactive({
  total_queries: 0,
  success_count: 0,
  failed_count: 0,
  total_saved: 0,
  avg_duration: null,
})
const logFilters = reactive({
  part_number: '',
  execution_type: '',
  status: '',
  start_date: '',
  end_date: '',
})
const logPagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})
const showClearDialog = ref(false)
const clearDays = ref(null)

// 加工事件对话框状态
const materialEventsDialog = ref(false)
const materialEventsMaterial = ref(null)
const materialEventsLoading = ref(false)
const materialEventsData = ref([])

// ========== Options ==========
const statusOptions = [
  { title: '全部', value: '' },
  { title: '启用', value: 'active' },
  { title: '禁用', value: 'inactive' },
]

const materialTypeOptions = [
  { title: '全部', value: '' },
  { title: '产品', value: 'product' },
  { title: '原材料', value: 'material' },
  { title: '辅料', value: 'auxiliary' },
]

function materialTypeLabel(type) {
  const map = { product: '产品', material: '原材料', auxiliary: '辅料' }
  return map[type] || type || '产品'
}

function materialTypeColor(type) {
  const map = { product: 'primary', material: 'orange', auxiliary: 'grey' }
  return map[type] || 'grey'
}

function categoryColor(category) {
  const map = {
    '成品': 'primary', '半成品': 'teal',
    '板材': 'orange', '棒材': 'amber', '管材': 'deep-orange', '型材': 'brown',
    '焊材': 'blue-grey', '气体': 'cyan', '油脂': 'lime', '其他': 'grey',
  }
  return map[category] || 'grey'
}

const unitOptions = [
  { title: '个', value: '个' },
  { title: '件', value: '件' },
  { title: '套', value: '套' },
  { title: '组', value: '组' },
  { title: '千克', value: '千克' },
  { title: '米', value: '米' },
  { title: '毫米', value: '毫米' },
  { title: '厘米', value: '厘米' },
]

const workshops = ref([])
const workshopOptions = computed(() => (workshops.value || []).map(w => w.name || w.workshop || w.id).filter(Boolean))

const projects = ref([])
const projectOptions = computed(() => (projects.value || []).map(p => p.name).filter(Boolean))

const executionTypeOptions = [
  { title: '全部', value: '' },
  { title: '手动', value: 'manual' },
  { title: '自动', value: 'auto' },
]

const logStatusOptions = [
  { title: '全部', value: '' },
  { title: '成功', value: 'success' },
  { title: '失败', value: 'failed' },
]

const localRecordStatusOptions = [
  { title: '全部', value: null },
  { title: '进行中', value: 'in_progress' },
  { title: '已完成', value: 'completed' },
  { title: '已暂停', value: 'paused' },
]

const docStateOptions = [
  { title: '全部', value: '' },
  { title: '开工', value: '开工' },
  { title: '完工', value: '完工' },
  { title: '核准中', value: '核准中' },
]

const docTypeOptions = [
  { title: '全部', value: '' },
  { title: '白班', value: '白班' },
  { title: '晚班', value: '晚班' },
]

const cronExamples = [
  { cron: '0 2 * * *', desc: '每天凌晨 2 点（默认）' },
  { cron: '0 8 * * *', desc: '每天早上 8 点' },
  { cron: '0 */6 * * *', desc: '每 6 小时执行一次' },
  { cron: '*/30 * * * *', desc: '每 30 分钟执行一次' },
  { cron: '0 2 * * 1', desc: '每周一凌晨 2 点' },
]

// ========== Table headers ==========
const productHeaders = [
  { title: 'U9 物料号', key: 'u9_material_code' },
  { title: '规格型号', key: 'part_number' },
  { title: '项目名称', key: 'project', width: '140px' },
  { title: '车间', key: 'workshop' },
  { title: '物料名称', key: 'product_name', width: '200px' },
  { title: '物料类型', key: 'material_type' },
  { title: '物料分类', key: 'category' },
  { title: '单件工时', key: 'unit_work_time' },
  { title: '状态', key: 'status' },
  { title: '创建时间', key: 'created_at' },
  { title: '操作', key: 'actions', sortable: false, width: '200px' },
]

const orderDetailHeaders = [
  { title: '订单编号', key: 'docNo' },
  { title: '物料编码', key: 'itemCode' },
  { title: '规格型号', key: 'specs' },
  { title: '物料名称', key: 'itemName' },
  { title: '订单数量', key: 'productQty' },
  { title: '完成仓库', key: 'completeWh' },
  { title: '订单日期', key: 'startDate' },
  { title: '腔号', key: 'cavityNumber' },
]

const batchResultHeaders = [
  { title: '零件号', key: 'part_number' },
  { title: '物料号', key: 'material_code' },
  { title: '规格型号', key: 'specs' },
  { title: '计划产量', key: 'planned_output' },
  { title: '订单数', key: 'order_count' },
  { title: '状态', key: 'status' },
  { title: '错误信息', key: 'error' },
]

const logHeaders = [
  { title: '零件号', key: 'part_number' },
  { title: '规格型号', key: 'specs' },
  { title: '计划产量', key: 'planned_output' },
  { title: '订单数', key: 'order_count' },
  { title: '保存数', key: 'saved_count' },
  { title: '状态', key: 'status' },
  { title: '执行类型', key: 'execution_type' },
  { title: '耗时', key: 'duration_seconds' },
  { title: '查询日期', key: 'query_date' },
  { title: '创建时间', key: 'created_at' },
  { title: '操作', key: 'actions', sortable: false, width: '100px' },
]

const localRecordHeaders = [
  { title: '设备', key: 'device_code' },
  { title: '订单号', key: 'doc_no' },
  { title: '零件号', key: 'part_number' },
  { title: '计划数量', key: 'planned_qty' },
  { title: '完成数量', key: 'completed_qty' },
  { title: '合格数量', key: 'eligible_qty' },
  { title: '报废数量', key: 'scrap_qty' },
  { title: '完成率', key: 'completion_rate' },
  { title: '状态', key: 'status' },
  { title: '操作', key: 'actions', sortable: false, width: '140px' },
]

const localOrderHeaders = [
  { title: '零件号', key: 'part_number' },
  { title: 'U9 物料号', key: 'u9_material_code' },
  { title: '计划产量', key: 'planned_output' },
  { title: '完成数量', key: 'total_complete_qty' },
  { title: '开始日期', key: 'start_date' },
  { title: '白晚班', key: 'doc_type' },
  { title: '订单状态', key: 'doc_state' },
  { title: '操作', key: 'actions', sortable: false, width: '80px' },
]

const localOrderDetailHeaders = [
  { title: '订单号', key: 'doc_no' },
  { title: '物料代码', key: 'item_code' },
  { title: '订单数量', key: 'product_qty' },
  { title: '完工数量', key: 'total_complete_qty' },
  { title: '合格数量', key: 'total_eligible_qty' },
  { title: '报废数量', key: 'total_scrap_qty' },
  { title: '仓库', key: 'complete_wh' },
  { title: '产线', key: 'line_code' },
  { title: '部门', key: 'department_name' },
  { title: '状态', key: 'doc_state' },
  { title: '项目', key: 'project' },
]

const analysisByDateHeaders = [
  { title: '日期', key: 'query_date' },
  { title: '订单数', key: 'order_count' },
  { title: '明细数', key: 'detail_count' },
  { title: '计划产量', key: 'total_planned_output' },
  { title: '订单数量', key: 'total_product_qty' },
]

const analysisByMaterialHeaders = [
  { title: '物料号', key: 'u9_material_code' },
  { title: '零件号', key: 'part_number' },
  { title: '订单数', key: 'order_count' },
  { title: '计划产量', key: 'total_planned_output' },
  { title: '订单数量', key: 'total_product_qty' },
]

const analysisByWarehouseHeaders = [
  { title: '仓库代码', key: 'complete_wh_code' },
  { title: '仓库名称', key: 'complete_wh' },
  { title: '订单数', key: 'order_count' },
  { title: '总数量', key: 'total_product_qty' },
  { title: '完工数量', key: 'total_complete_qty' },
  { title: '合格数量', key: 'total_eligible_qty' },
]

const analysisByDepartmentHeaders = [
  { title: '部门代码', key: 'department_code' },
  { title: '部门名称', key: 'department_name' },
  { title: '订单数', key: 'order_count' },
  { title: '总数量', key: 'total_product_qty' },
]

const analysisByDocStateHeaders = [
  { title: '状态', key: 'doc_state' },
  { title: '订单数', key: 'order_count' },
  { title: '总数量', key: 'total_product_qty' },
]

// ========== Computed ==========
const getActiveRate = computed(() => {
  if (productStats.value.total === 0) return 0
  return Math.round((productStats.value.active / productStats.value.total) * 100)
})

const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  let start = Math.max(1, pagination.current - Math.floor(maxVisible / 2))
  let end = Math.min(pagination.totalPages, start + maxVisible - 1)
  if (end - start < maxVisible - 1) {
    start = Math.max(1, end - maxVisible + 1)
  }
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

// ========== Methods ==========
const loadProducts = async () => {
  try {
    loading.value = true
    const params = {
      ...queryParams,
      page: pagination.current,
      page_size: pagination.pageSize,
    }
    const response = await materialAPI.getMaterials(params)
    productList.value = response.data.items || []
    pagination.total = response.data.total || 0
    pagination.totalPages = Math.ceil(pagination.total / pagination.pageSize)
    pagination.pageStart = (pagination.current - 1) * pagination.pageSize + 1
    pagination.pageEnd = Math.min(pagination.current * pagination.pageSize, pagination.total)
    await loadStats()
  } catch (error) {
    console.error('加载物料列表失败:', error)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const response = await materialAPI.getStats()
    productStats.value = response.data || {}
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const loadWorkshops = async () => {
  try {
    const resp = await workshopAPI.all()
    workshops.value = resp.data.items || resp.data || []
  } catch (err) {
    console.error('加载车间列表失败:', err)
  }
}

const loadProjects = async () => {
  try {
    const resp = await projectAPI.all()
    projects.value = resp.data.items || resp.data || []
  } catch (err) {
    console.error('加载项目列表失败:', err)
  }
}

const loadCategories = async () => {
  try {
    const resp = await materialCategoryAPI.list()
    const items = resp.data.items || []
    if (items.length > 0) {
      const newMap = {}
      const newData = {}
      for (const group of items) {
        newMap[group.type_key] = group.categories.map(c => c.category_name)
        newData[group.type_key] = group.categories
      }
      categoryMap.value = newMap
      categoryData.value = newData
    }
  } catch (err) {
    console.error('加载分类列表失败:', err)
  }
}

const openCategoryDialog = () => {
  showCategoryDialog.value = true
  selectedTypeKey.value = 'product'
  newCategoryName.value = ''
  editingCategory.value = null
}

const addCategory = async () => {
  const name = newCategoryName.value.trim()
  if (!name) return
  const typeInfo = categoryTypeOptions.find(t => t.key === selectedTypeKey.value)
  try {
    await materialCategoryAPI.create({
      type_key: selectedTypeKey.value,
      type_name: typeInfo.name,
      category_name: name,
    })
    newCategoryName.value = ''
    await loadCategories()
  } catch (err) {
    alert('添加失败：' + (err.response?.data?.detail || err.message))
  }
}

const startEditCategory = (cat) => {
  editingCategory.value = cat.id
  editingCategoryName.value = cat.category_name
}

const saveEditCategory = async (id) => {
  const name = editingCategoryName.value.trim()
  if (!name) return
  try {
    await materialCategoryAPI.update(id, { category_name: name })
    editingCategory.value = null
    editingCategoryName.value = ''
    await loadCategories()
  } catch (err) {
    alert('更新失败：' + (err.response?.data?.detail || err.message))
  }
}

const deleteCategory = async (id, name) => {
  if (!confirm(`确定删除分类"${name}"吗？`)) return
  try {
    await materialCategoryAPI.delete(id)
    await loadCategories()
  } catch (err) {
    alert('删除失败：' + (err.response?.data?.detail || err.message))
  }
}

const changePage = (page) => {
  if (page < 1 || page > pagination.totalPages) return
  pagination.current = page
  loadProducts()
}

const resetQuery = () => {
  queryParams.u9_material_code = ''
  queryParams.part_number = ''
  queryParams.product_name = ''
  queryParams.category = ''
  queryParams.workshop = ''
  queryParams.material_type = ''
  queryParams.status = ''
  pagination.current = 1
  loadProducts()
}

const toggleSearch = () => {
  showSearch.value = !showSearch.value
}

const viewProduct = async (product) => {
  try {
    const response = await materialAPI.getMaterial(product.id)
    viewData.value = response.data
    showViewDialog.value = true
  } catch (error) {
    console.error('获取物料详情失败:', error)
  }
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

const viewMaterialEvents = async (material) => {
  materialEventsMaterial.value = material
  materialEventsDialog.value = true
  materialEventsLoading.value = true
  materialEventsData.value = []
  try {
    const response = await materialAPI.getMaterial(material.id)
    const mat = response.data
    const startCode = mat.u9_material_code || mat.part_number
    if (startCode) {
      const eventsRes = await eventAssociationAPI.getByMaterial(startCode, { page_size: 50 })
      materialEventsData.value = eventsRes.data?.items || []
    }
  } catch (error) {
    console.error('加载加工事件失败:', error)
  } finally {
    materialEventsLoading.value = false
  }
}

const editFromView = () => {
  showViewDialog.value = false
  editProduct(viewData.value)
}

const editProduct = (product) => {
  formData.id = product.id
  formData.u9_material_code = product.u9_material_code
  formData.part_number = product.part_number || ''
  formData.product_name = product.product_name
  formData.description = product.description || ''
  formData.specification = product.specification || ''
  formData.category = product.category || ''
  formData.project = product.project || ''
  formData.workshop = product.workshop || ''
  formData.unit = product.unit || ''
  formData.unit_work_time = product.unit_work_time != null ? Number(product.unit_work_time) : 0
  formData.material_type = product.material_type || 'product'
  formData.status = product.status || 'active'

  clearFormErrors()
  showEditDialog.value = true
  showAddDialog.value = false
}

const openAddDialog = () => {
  formData.id = null
  formData.u9_material_code = ''
  formData.part_number = ''
  formData.product_name = ''
  formData.description = ''
  formData.specification = ''
  formData.category = ''
  formData.unit = ''
  formData.unit_work_time = 0
  formData.material_type = 'product'
  formData.status = 'active'
  clearFormErrors()
  showAddDialog.value = true
}

const openImportDialog = () => {
  importFile.value = null
  importFileModel.value = null
  showImportDialog.value = true
}

const onImportFileChange = (files) => {
  if (Array.isArray(files) && files.length > 0) {
    importFile.value = files[0]
  } else if (files instanceof File) {
    importFile.value = files
  } else {
    importFile.value = null
  }
}

const validateForm = () => {
  clearFormErrors()
  let valid = true

  if (!formData.u9_material_code?.trim()) {
    formErrors.u9_material_code = '请输入 U9 物料号'
    valid = false
  }
  if (!formData.product_name?.trim()) {
    formErrors.product_name = '请输入物料名称'
    valid = false
  }

  // 成品和半成品必须填写车间信息
  if (formData.material_type === 'product' && ['成品', '半成品'].includes(formData.category) && !formData.workshop?.toString().trim()) {
    formErrors.workshop = '成品/半成品必须选择车间'
    valid = false
  }

  return valid
}

const clearFormErrors = () => {
  Object.keys(formErrors).forEach((key) => {
    formErrors[key] = ''
  })
}

const saveProduct = async () => {
  if (!validateForm()) {
    const firstError = Object.values(formErrors).find(v => v)
    if (firstError) message.error(firstError)
    return
  }

  try {
    saving.value = true
    if (formData.id) {
      const updateData = {
        part_number: formData.part_number,
        product_name: formData.product_name,
        description: formData.description,
        specification: formData.specification,
        category: formData.category,
        project: formData.project,
        workshop: formData.workshop,
        unit: formData.unit,
        unit_work_time: formData.unit_work_time,
        material_type: formData.material_type,
        status: formData.status,
      }
      await materialAPI.updateMaterial(formData.id, updateData)
    } else {
      await materialAPI.createMaterial(formData)
    }
    closeDialogs()
    loadProducts()
  } catch (error) {
    console.error('保存物料失败:', error)
    if (error.response?.status === 400) {
      const detail = error.response.data.detail
      if (detail?.includes('U9 物料号')) {
        formErrors.u9_material_code = detail
      } else if (detail?.includes('规格型号')) {
        formErrors.part_number = detail
      } else {
        alert(detail || '保存失败，请重试')
      }
    } else {
      alert('保存失败，请重试')
    }
  } finally {
    saving.value = false
  }
}

const closeDialogs = () => {
  showAddDialog.value = false
  showEditDialog.value = false
  showImportDialog.value = false
  showViewDialog.value = false
}

const toggleProductStatus = async (product) => {
  try {
    await materialAPI.updateMaterial(product.id, {
      ...product,
      status: product.status === 'active' ? 'inactive' : 'active',
    })
    loadProducts()
  } catch (error) {
    console.error('切换物料状态失败:', error)
  }
}

const deleteProduct = async (product) => {
  try {
    const ok = await confirmDialog(`确定要删除物料 "${product.product_name}" 吗？`, '确认删除', 'warning')
    if (!ok) return
    await materialAPI.deleteMaterial(product.id)
    message.success('物料已删除')
    loadProducts()
  } catch (e) {
    console.error('删除物料失败:', e)
  }
}

const batchDelete = async () => {
  if (selectedProducts.value.length === 0) return
  try {
    const ok = await confirmDialog(`确定要删除选中的 ${selectedProducts.value.length} 个物料吗？`, '确认删除', 'warning')
    if (!ok) return
    for (const id of selectedProducts.value) {
      await materialAPI.deleteMaterial(id)
    }
    selectedProducts.value = []
    message.success('批量删除成功')
    loadProducts()
  } catch (e) {
    console.error('批量删除失败:', e)
  }
}

const handleSelectAll = () => {
  if (selectAll.value) {
    selectedProducts.value = productList.value.map((p) => p.id)
  } else {
    selectedProducts.value = []
  }
}

const exportProducts = async () => {
  try {
    const { u9_material_code, part_number, product_name, category, status } = queryParams
    const response = await materialAPI.exportMaterials({ u9_material_code, part_number, product_name, category, status })
    const url = window.URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = url
    link.download = `products_${new Date().toISOString().split('T')[0]}.csv`
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('导出物料失败:', error)
  }
}

const formatUnitWorkTime = (unitWorkTime) => {
  const value = Number(unitWorkTime) || 0
  return `${value.toFixed(5)} 小时`
}

const downloadTemplate = async () => {
  try {
    const response = await materialAPI.downloadTemplate()

    if (response.data instanceof Blob) {
      const url = window.URL.createObjectURL(response.data)
      const link = document.createElement('a')
      link.href = url
      link.download = '物料导入模板.xlsx'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      setTimeout(() => window.URL.revokeObjectURL(url), 100)
    } else {
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = '物料导入模板.xlsx'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      setTimeout(() => window.URL.revokeObjectURL(url), 100)
    }
  } catch (error) {
    console.error('下载模板失败:', error)
  }
}

const uploadImportFile = async () => {
  if (!importFile.value) return
  try {
    uploading.value = true
    const response = await materialAPI.importMaterials(importFile.value)
    const result = response.data
    let msg = `导入完成：新增 ${result.imported} 条，更新 ${result.updated} 条`
    if (result.errors && result.errors.length > 0) {
      msg += `，${result.errors.length} 条错误`
      console.warn('导入错误:', result.errors)
    }
    message.success(msg)
    closeDialogs()
    loadProducts()
    loadStats()
  } catch (error) {
    console.error('导入物料失败:', error)
    message.error('导入失败：' + (error.response?.data?.detail || error.message))
  } finally {
    uploading.value = false
  }
}

// ========== Order query methods ==========
const querySingleOrder = async () => {
  if (!orderQuery.startDate || !orderQuery.endDate) {
    alert('请选择开始日期和结束日期')
    return
  }

  if (!orderQuery.partNumber && !orderQuery.u9MaterialCode) {
    alert('请输入零件号或 U9 料号')
    return
  }

  try {
    querying.value = true
    loadingText.value = '查询单个零件订单...'
    orderQueryResult.value = null
    batchQueryResult.value = null

    const response = await erpOrderAPI.querySinglePartOrder(
      orderQuery.partNumber,
      orderQuery.u9MaterialCode,
      orderQuery.startDate,
      orderQuery.endDate
    )

    // Compatible with two response formats: { data: {...} } or direct { planned_output, details, ... }
    const apiData = response.data
    if (apiData && apiData.data) {
      orderQueryResult.value = apiData
    } else {
      orderQueryResult.value = { data: apiData }
    }
  } catch (error) {
    console.error('查询单个零件订单失败:', error)
    alert('查询失败：' + (error.response?.data?.detail || error.message))
  } finally {
    querying.value = false
  }
}

const queryBatchOrders = async () => {
  if (!orderQuery.startDate || !orderQuery.endDate) {
    alert('请选择开始日期和结束日期')
    return
  }

  try {
    querying.value = true
    loadingText.value = '批量查询订单并保存...'
    orderQueryResult.value = null
    batchQueryResult.value = null

    const response = await erpOrderAPI.queryOrdersByTime({
      part_number: orderQuery.partNumber || null,
      start_date: orderQuery.startDate,
      end_date: orderQuery.endDate
    })

    batchQueryResult.value = response.data
  } catch (error) {
    console.error('批量查询订单失败:', error)
    alert('查询失败：' + (error.response?.data?.detail || error.message))
  } finally {
    querying.value = false
  }
}

const resetOrderQuery = () => {
  orderQuery.partNumber = ''
  orderQuery.startDate = new Date().toISOString().split('T')[0]
  orderQuery.endDate = new Date().toISOString().split('T')[0]
  orderQueryResult.value = null
  batchQueryResult.value = null
}

// ========== Scheduler methods ==========
const loadSchedulerStatus = async () => {
  try {
    schedulerLoading.value = true
    const response = await erpOrderAPI.getSchedulerStatus()
    schedulerStatus.is_running = response.data.is_running
    schedulerStatus.last_run_time = response.data.last_run_time
    schedulerStatus.next_run_time = response.data.next_run_time
    schedulerStatus.last_run_stats = response.data.last_run_stats
  } catch (error) {
    console.error('获取定时任务状态失败:', error)
  } finally {
    schedulerLoading.value = false
  }
}

const toggleScheduler = async () => {
  try {
    schedulerLoading.value = true
    if (schedulerStatus.is_running) {
      await erpOrderAPI.stopScheduler()
      schedulerStatus.is_running = false
      alert('定时任务已停止')
    } else {
      await erpOrderAPI.startScheduler(schedulerCron.value)
      schedulerStatus.is_running = true
      alert('定时任务已启动')
    }
    await loadSchedulerStatus()
  } catch (error) {
    console.error('定时任务操作失败:', error)
    alert('操作失败：' + (error.response?.data?.detail || error.message))
  } finally {
    schedulerLoading.value = false
  }
}

const triggerScheduler = async () => {
  try {
    schedulerLoading.value = true
    await erpOrderAPI.triggerScheduler()
    alert('已触发立即查询，请在后台查看执行日志')
  } catch (error) {
    console.error('触发定时任务失败:', error)
    alert('触发失败：' + (error.response?.data?.detail || error.message))
  } finally {
    schedulerLoading.value = false
  }
}

const closeSchedulerConfig = () => {
  showSchedulerConfig.value = false
}

const saveSchedulerConfig = async () => {
  try {
    schedulerLoading.value = true
    await erpOrderAPI.startScheduler(schedulerCron.value)
    alert('定时任务配置已保存')
    showSchedulerConfig.value = false
    await loadSchedulerStatus()
  } catch (error) {
    console.error('保存配置失败:', error)
    alert('保存失败：' + (error.response?.data?.detail || error.message))
  } finally {
    schedulerLoading.value = false
  }
}

// ========== Order analysis methods ==========
const loadOrderAnalysis = async () => {
  if (!analysisStartDate.value || !analysisEndDate.value) {
    alert('请选择开始日期和结束日期')
    return
  }

  try {
    analysisLoading.value = true
    orderAnalysis.value = null
    const response = await localOrderAPI.getComprehensiveAnalysis(
      analysisStartDate.value,
      analysisEndDate.value
    )
    orderAnalysis.value = response.data

    await nextTick()
    initCharts()
  } catch (error) {
    console.error('获取订单分析数据失败:', error)
    alert('分析失败：' + (error.response?.data?.detail || error.message))
  } finally {
    analysisLoading.value = false
  }
}

const initCharts = () => {
  if (!orderAnalysis.value) return

  initTrendChart()
  initStatusChart()
  initMaterialChart()
  initWarehouseChart()
}

const initTrendChart = () => {
  if (!trendChartRef.value || !orderAnalysis.value?.trend) return

  if (trendChart) {
    trendChart.dispose()
  }

  trendChart = echarts.init(trendChartRef.value)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['订单数量', '计划产量', '订单数量']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: orderAnalysis.value.trend.map(item => item.date)
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '订单数量',
        type: 'line',
        data: orderAnalysis.value.trend.map(item => item.order_count),
        smooth: true,
        itemStyle: { color: '#3b82f6' }
      },
      {
        name: '计划产量',
        type: 'line',
        data: orderAnalysis.value.trend.map(item => item.total_planned_output),
        smooth: true,
        itemStyle: { color: '#10b981' }
      },
      {
        name: '订单数量',
        type: 'bar',
        data: orderAnalysis.value.trend.map(item => item.total_product_qty),
        itemStyle: { color: '#f59e0b' }
      }
    ]
  }

  trendChart.setOption(option)
}

const initStatusChart = () => {
  if (!statusChartRef.value || !orderAnalysis.value?.summary?.doc_state_distribution) return

  if (statusChart) {
    statusChart.dispose()
  }

  statusChart = echarts.init(statusChartRef.value)

  const distribution = orderAnalysis.value.summary.doc_state_distribution

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '订单状态',
        type: 'pie',
        radius: '50%',
        data: distribution.map(item => ({
          value: item.count,
          name: item.doc_state
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }

  statusChart.setOption(option)
}

const initMaterialChart = () => {
  if (!materialChartRef.value || !orderAnalysis.value?.summary?.top_materials) return

  if (materialChart) {
    materialChart.dispose()
  }

  materialChart = echarts.init(materialChartRef.value)

  const materials = orderAnalysis.value.summary.top_materials

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value'
    },
    yAxis: {
      type: 'category',
      data: materials.map(item => item.part_number).reverse()
    },
    series: [
      {
        name: '计划产量',
        type: 'bar',
        data: materials.map(item => item.total_output).reverse(),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        }
      }
    ]
  }

  materialChart.setOption(option)
}

const initWarehouseChart = () => {
  if (!warehouseChartRef.value || !orderAnalysis.value?.summary?.top_warehouses) return

  if (warehouseChart) {
    warehouseChart.dispose()
  }

  warehouseChart = echarts.init(warehouseChartRef.value)

  const warehouses = orderAnalysis.value.summary.top_warehouses

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '仓库分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: warehouses.map(item => ({
          value: item.total_qty,
          name: item.complete_wh
        }))
      }
    ]
  }

  warehouseChart.setOption(option)
}

const disposeCharts = () => {
  if (trendChart) {
    trendChart.dispose()
    trendChart = null
  }
  if (statusChart) {
    statusChart.dispose()
    statusChart = null
  }
  if (materialChart) {
    materialChart.dispose()
    materialChart = null
  }
  if (warehouseChart) {
    warehouseChart.dispose()
    warehouseChart = null
  }
}

const getOrderStatePercentage = (orderCount) => {
  if (!orderAnalysis.value || !orderAnalysis.value.summary || !orderAnalysis.value.summary.total_orders) {
    return 0
  }
  return ((Number(orderCount) / Number(orderAnalysis.value.summary.total_orders)) * 100).toFixed(1)
}

const formatNumber = (num) => {
  if (num === null || num === undefined) return '0'
  return num.toLocaleString()
}

const getTrendClass = (trend) => {
  if (trend > 0) return 'trend-up'
  if (trend < 0) return 'trend-down'
  return 'trend-flat'
}

const getTrendIcon = (trend) => {
  if (trend > 0) return 'mdi-arrow-up-right'
  if (trend < 0) return 'mdi-arrow-down-right'
  return 'mdi-minus'
}

// ========== Helper functions ==========
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  } catch (e) {
    return dateStr
  }
}

// ========== Lifecycle ==========
onMounted(() => {
  loadProducts()
  loadStats()
  loadWorkshops()
  loadProjects()
  loadCategories()
  loadSchedulerStatus()

  window.addEventListener('resize', handleResize)
  document.addEventListener('keydown', handleEscKey)
})

onUnmounted(() => {
  disposeCharts()
  window.removeEventListener('resize', handleResize)
  document.removeEventListener('keydown', handleEscKey)
})

const handleResize = () => {
  if (trendChart) trendChart.resize()
  if (statusChart) statusChart.resize()
  if (materialChart) materialChart.resize()
  if (warehouseChart) warehouseChart.resize()
}

// ESC key close dialog handler
const handleEscKey = (e) => {
  if (e.key === 'Escape') {
    if (showAddDialog.value || showEditDialog.value || showViewDialog.value || showImportDialog.value) {
      closeDialogs()
    }
  }
}

// ========== Log methods ==========
const loadLogs = async () => {
  try {
    logsLoading.value = true
    const params = {
      page: logPagination.page,
      page_size: logPagination.pageSize,
    }

    if (logFilters.part_number) {
      params.part_number = logFilters.part_number
    }
    if (logFilters.execution_type) {
      params.execution_type = logFilters.execution_type
    }
    if (logFilters.status) {
      params.status = logFilters.status
    }
    if (logFilters.start_date) {
      params.start_date = logFilters.start_date
    }
    if (logFilters.end_date) {
      params.end_date = logFilters.end_date
    }

    const response = await productOrderLogAPI.getLogs(params)
    logs.value = response.data.logs || []
    logPagination.total = response.data.total || 0
  } catch (error) {
    console.error('加载日志失败:', error)
    logs.value = []
  } finally {
    logsLoading.value = false
  }
}

const loadLogStats = async () => {
  try {
    const params = {}
    if (logFilters.start_date) {
      params.start_date = logFilters.start_date
    }
    if (logFilters.end_date) {
      params.end_date = logFilters.end_date
    }

    const response = await productOrderLogAPI.getStats(params)
    logStats.total_queries = response.data.total_queries || 0
    logStats.success_count = response.data.success_count || 0
    logStats.failed_count = response.data.failed_count || 0
    logStats.total_saved = response.data.total_saved || 0
    logStats.avg_duration = response.data.avg_duration || 0
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

const applyFilters = () => {
  logPagination.page = 1
  loadLogs()
  loadLogStats()
}

const resetFilters = () => {
  logFilters.part_number = ''
  logFilters.execution_type = ''
  logFilters.status = ''
  logFilters.start_date = ''
  logFilters.end_date = ''
  applyFilters()
}

const changeLogPage = (page) => {
  if (page < 1 || page * logPagination.pageSize > logPagination.total) return
  logPagination.page = page
  loadLogs()
}

const viewLogDetail = (log) => {
  console.log('查看日志详情:', log)
}

const deleteLog = async (logId) => {
  try {
    const ok = await confirmDialog('确定要删除这条日志吗？', '确认删除', 'warning')
    if (!ok) return
    await productOrderLogAPI.deleteLog(logId)
    message.success('日志已删除')
    await loadLogs()
    await loadLogStats()
  } catch (e) {
    console.error('删除日志失败:', e)
  }
}

const confirmClear = async () => {
  try {
    const ok = await confirmDialog('确定要清空日志吗？此操作不可恢复！', '确认清空', 'warning')
    if (!ok) return
    await productOrderLogAPI.clearLogs(clearDays.value)
    showClearDialog.value = false
    clearDays.value = null
    message.success('日志已清空')
    await loadLogs()
    await loadLogStats()
  } catch (e) {
    console.error('清空日志失败:', e)
  }
}

// ========== Local record data ==========
const localRecords = ref([])
const localRecordStats = ref({
  total_records: 0,
  in_progress: 0,
  completed: 0,
  paused: 0,
  total_planned: 0,
  total_completed: 0,
  total_eligible: 0,
  total_scrap: 0,
  overall_completion_rate: 0,
})
const localRecordFilter = reactive({
  device_code: null,
  record_date: new Date().toISOString().split('T')[0],
  status: null,
})
const showLocalRecordDialog = ref(false)
const editingLocalRecord = ref(null)
const localRecordForm = reactive({
  device_code: null,
  part_number: '',
  u9_material_code: '',
  doc_no: '',
  planned_qty: null,
  completed_qty: 0,
  eligible_qty: 0,
  scrap_qty: 0,
  status: 'in_progress',
  notes: '',
})
const allDevices = ref([])

const loadAllDevices = async () => {
  try {
    const res = await deviceAPI.getDevices({ page: 1, page_size: 100 })
    allDevices.value = res.data.items || res.data || []
  } catch (e) {
    console.error('加载设备列表失败:', e)
  }
}

const loadLocalRecords = async () => {
  try {
    const params = {}
    if (localRecordFilter.device_code) params.device_code = localRecordFilter.device_code
    if (localRecordFilter.record_date) params.record_date = localRecordFilter.record_date
    if (localRecordFilter.status) params.status = localRecordFilter.status
    const res = await orderProcessingAPI.getRecords(params)
    const items = res.data.items || []
    localRecords.value = items.map(r => ({
      ...r,
      completion_rate: r.planned_qty > 0 ? Math.round(r.completed_qty / r.planned_qty * 100 * 10) / 10 : 0,
    }))
  } catch (e) {
    console.error('加载本地加工记录失败:', e)
  }
}

const loadLocalRecordStats = async () => {
  try {
    const params = {}
    if (localRecordFilter.record_date) params.record_date = localRecordFilter.record_date
    const res = await orderProcessingAPI.getStats(params)
    localRecordStats.value = res.data
  } catch (e) {
    console.error('加载本地加工记录统计失败:', e)
  }
}

const openLocalRecordDialog = (record = null) => {
  editingLocalRecord.value = record
  if (record) {
    localRecordForm.device_code = record.device_code
    localRecordForm.part_number = record.part_number || ''
    localRecordForm.u9_material_code = record.u9_material_code || ''
    localRecordForm.doc_no = record.doc_no || ''
    localRecordForm.planned_qty = record.planned_qty
    localRecordForm.completed_qty = record.completed_qty || 0
    localRecordForm.eligible_qty = record.eligible_qty || 0
    localRecordForm.scrap_qty = record.scrap_qty || 0
    localRecordForm.status = record.status || 'in_progress'
    localRecordForm.notes = record.notes || ''
  } else {
    localRecordForm.device_code = null
    localRecordForm.part_number = ''
    localRecordForm.u9_material_code = ''
    localRecordForm.doc_no = ''
    localRecordForm.planned_qty = null
    localRecordForm.completed_qty = 0
    localRecordForm.eligible_qty = 0
    localRecordForm.scrap_qty = 0
    localRecordForm.status = 'in_progress'
    localRecordForm.notes = ''
  }
  showLocalRecordDialog.value = true
}

const saveLocalRecord = async () => {
  if (!localRecordForm.device_code || !localRecordForm.part_number) {
    alert('请填写设备和零件号')
    return
  }
  try {
    if (editingLocalRecord.value) {
      await orderProcessingAPI.updateRecord(editingLocalRecord.value.id, localRecordForm)
    } else {
      await orderProcessingAPI.createRecord(localRecordForm)
    }
    showLocalRecordDialog.value = false
    loadLocalRecords()
    loadLocalRecordStats()
  } catch (e) {
    console.error('保存失败:', e)
    alert('保存失败: ' + (e.response?.data?.detail || e.message))
  }
}

const completeLocalRecord = async (id) => {
  try {
    await orderProcessingAPI.completeRecord(id)
    loadLocalRecords()
    loadLocalRecordStats()
  } catch (e) {
    console.error('标记完成失败:', e)
  }
}

const deleteLocalRecord = async (id) => {
  try {
    const ok = await confirmDialog('确定删除此记录？', '确认删除', 'warning')
    if (!ok) return
    await orderProcessingAPI.deleteRecord(id)
    message.success('记录已删除')
    loadLocalRecords()
    loadLocalRecordStats()
  } catch (e) {
    console.error('删除失败:', e)
  }
}

// ========== Local order data ==========
const localOrders = ref([])
const localOrderStats = reactive({
  total_orders: 0, total_planned_output: 0, total_detail_count: 0,
  today_orders: 0, today_planned_output: 0
})
const localOrderFilter = reactive({
  part_number: '',
  doc_no: '',
  doc_state: '',
  doc_type: '',
  start_date: new Date().toISOString().split('T')[0],
  end_date: new Date().toISOString().split('T')[0],
  page: 1,
  page_size: 20
})
const localOrderPagination = reactive({ total: 0, page: 1, page_size: 20 })
const expandedLocalOrders = ref([])
const showLocalOrderAnalysis = ref(false)
const showClearLocalOrderConfirm = ref(false)
const localOrderAnalysisData = ref(null)
const localOrderAnalysisQuery = reactive({
  start_date: new Date(Date.now() - 7 * 86400000).toISOString().split('T')[0],
  end_date: new Date().toISOString().split('T')[0]
})

const localOrderTotalPages = computed(() => Math.max(1, Math.ceil(localOrderPagination.total / localOrderPagination.page_size)))

function formatLocalOrderTime(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN', { hour12: false })
}

function getDocStateClass(state) {
  const map = {
    '开工': 'badge-state-running',
    '完工': 'badge-state-done',
    '核准中': 'badge-state-reviewing',
  }
  return map[state] || 'badge-state-default'
}

const loadLocalOrders = async () => {
  try {
    const res = await localOrderAPI.getOrderList(localOrderFilter)
    localOrders.value = res.data.items || []
    localOrderPagination.total = res.data.total || 0
    localOrderPagination.page = localOrderFilter.page
  } catch (e) {
    console.error('加载本地订单失败:', e)
  }
}

const loadLocalOrderStats = async () => {
  try {
    const res = await localOrderAPI.getOrderStats()
    Object.assign(localOrderStats, res.data)
  } catch (e) {
    console.error('加载本地订单统计失败:', e)
  }
}

const loadLocalOrderAnalysis = async () => {
  try {
    const res = await localOrderAPI.getComprehensiveAnalysis(localOrderAnalysisQuery.start_date, localOrderAnalysisQuery.end_date)
    localOrderAnalysisData.value = res.data
  } catch (e) {
    console.error('加载本地订单分析失败:', e)
  }
}

const changeLocalOrderPage = (page) => {
  localOrderFilter.page = page
  loadLocalOrders()
}

const toggleLocalOrderDetail = (order) => {
  expandedLocalOrder.value = expandedLocalOrder.value === order.id ? null : order.id
}

const confirmClearLocalOrders = () => { showClearLocalOrderConfirm.value = true }

const doClearLocalOrders = async () => {
  try {
    await localOrderAPI.clearTodayOrders()
    showClearLocalOrderConfirm.value = false
    message.success('今日本地订单已清除')
    loadLocalOrders()
    loadLocalOrderStats()
  } catch (e) {
    console.error('清除本地订单失败:', e)
  }
}

// Tab switch handler
const switchTab = (tab) => {
  activeTab.value = tab
  if (tab === 'logs') {
    loadLogs()
    loadLogStats()
  } else if (tab === 'local-records') {
    loadLocalRecords()
    loadLocalRecordStats()
    loadAllDevices()
  } else if (tab === 'local-orders') {
    loadLocalOrders()
    loadLocalOrderStats()
  }
}
</script>
