<template>
  <div>
    <!-- Action bar -->
    <v-toolbar flat color="transparent" class="mb-4">
      <div>
        <div class="text-h5 font-weight-bold d-flex align-center ga-2">
          <v-icon icon="mdi-cog-transfer" color="primary" />
          产品加工信息
        </div>
        <div class="text-caption text-medium-emphasis mt-1">
          首页 / 产品加工信息
        </div>
      </div>
    </v-toolbar>

    <!-- Stats cards -->
    <v-row class="mb-4" dense>
      <v-col cols="12" sm="6" md="4" lg="2">
        <v-card class="stat-card" @click="scrollToTable">
          <v-card-text class="d-flex align-center ga-3">
            <v-icon icon="mdi-calendar-check" size="40" color="info" />
            <div>
              <div class="text-h6 font-weight-bold">{{ stats.total.toLocaleString() }}</div>
              <div class="text-caption text-medium-emphasis">总加工数</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="4" lg="2">
        <v-card class="stat-card" @click="scrollToTable">
          <v-card-text class="d-flex align-center ga-3">
            <v-icon icon="mdi-clock-outline" size="40" color="success" />
            <div>
              <div class="text-h6 font-weight-bold">{{ formatDuration(stats.avg_duringtime) }}</div>
              <div class="text-caption text-medium-emphasis">平均加工时长</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="4" lg="2">
        <v-card class="stat-card" @click="scrollToTable">
          <v-card-text class="d-flex align-center ga-3">
            <v-icon icon="mdi-timer-outline" size="40" color="warning" />
            <div>
              <div class="text-h6 font-weight-bold">{{ formatDuration(stats.avg_machine_duringtime) }}</div>
              <div class="text-caption text-medium-emphasis">平均机器工作时间</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="4" lg="2">
        <v-card class="stat-card" @click="queryParams.machine_id = ''; handleSearch()">
          <v-card-text class="d-flex align-center ga-3">
            <v-icon icon="mdi-cog" size="40" color="error" />
            <div>
              <div class="text-h6 font-weight-bold">{{ stats.machine_count }}</div>
              <div class="text-caption text-medium-emphasis">设备数量</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="4" lg="2">
        <v-card class="stat-card" @click="scrollToTable">
          <v-card-text class="d-flex align-center ga-3">
            <v-icon icon="mdi-account-group" size="40" color="purple" />
            <div>
              <div class="text-h6 font-weight-bold">{{ stats.operator_count }}</div>
              <div class="text-caption text-medium-emphasis">操作员数量</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="4" lg="2">
        <v-card class="stat-card" @click="scrollToTable">
          <v-card-text class="d-flex align-center ga-3">
            <v-icon icon="mdi-layers" size="40" color="pink" />
            <div>
              <div class="text-h6 font-weight-bold">{{ stats.line_count }}</div>
              <div class="text-caption text-medium-emphasis">产线数量</div>
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
        <v-chip-group v-model="quickFilter" mandatory class="mr-2">
          <v-chip size="small" value="all" variant="tonal">全部</v-chip>
          <v-chip size="small" value="today" variant="tonal" color="info">今日</v-chip>
          <v-chip size="small" value="week" variant="tonal" color="success">本周</v-chip>
          <v-chip size="small" value="month" variant="tonal" color="warning">本月</v-chip>
        </v-chip-group>
        <v-btn variant="text" :icon="showSearch ? 'mdi-chevron-up' : 'mdi-chevron-down'" size="small" />
      </v-card-title>
      <v-divider v-if="showSearch" />
      <v-card-text v-if="showSearch">
        <v-form @submit.prevent="handleSearch">
          <v-row dense>
            <v-col cols="12" sm="6" md="3">
              <v-text-field
                v-model="queryParams.start_time"
                label="开始时间"
                type="datetime-local"
                clearable
                density="compact"
              />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-text-field
                v-model="queryParams.end_time"
                label="结束时间"
                type="datetime-local"
                clearable
                density="compact"
              />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-text-field
                v-model="queryParams.start_code"
                label="启动码"
                placeholder="请输入启动码"
                clearable
                density="compact"
              />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-text-field
                v-model="queryParams.skin_code"
                label="表皮码"
                placeholder="请输入表皮码"
                clearable
                density="compact"
              />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-text-field
                v-model="queryParams.machine_id"
                label="设备编号"
                placeholder="请输入设备编号"
                clearable
                density="compact"
              />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-text-field
                v-model="queryParams.operator_id"
                label="操作员 ID"
                placeholder="请输入操作员 ID"
                clearable
                density="compact"
              />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-text-field
                v-model="queryParams.group_code"
                label="集团编码"
                placeholder="请输入集团编码"
                clearable
                density="compact"
              />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-text-field
                v-model="queryParams.factory_code"
                label="工厂编码"
                placeholder="请输入工厂编码"
                clearable
                density="compact"
              />
            </v-col>
            <v-col cols="12" sm="6" md="3" class="d-flex align-center ga-2">
              <v-btn color="primary" prepend-icon="mdi-magnify" @click="handleSearch">查询</v-btn>
              <v-btn variant="outlined" prepend-icon="mdi-undo" @click="handleReset">重置</v-btn>
              <v-btn color="success" variant="tonal" prepend-icon="mdi-download" :loading="loading" @click="handleExport">导出 CSV</v-btn>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- Trend chart -->
    <v-card class="mb-4">
      <v-card-title class="d-flex align-center ga-2">
        <v-icon icon="mdi-chart-bar" />
        加工趋势分析
        <v-spacer />
        <v-select
          v-model="trendParams.interval"
          :items="intervalOptions"
          density="compact"
          style="max-width: 120px"
          @update:model-value="loadTrendData"
        />
      </v-card-title>
      <v-divider />
      <v-card-text>
        <div ref="trendChartEl" style="width: 100%; height: 400px;"></div>
      </v-card-text>
    </v-card>

    <!-- Data table -->
    <v-card ref="tableCard">
      <v-card-title class="d-flex align-center ga-2">
        <v-icon icon="mdi-table" />
        产品加工信息明细
        <v-spacer />
        <v-switch
          v-model="autoRefresh"
          label="自动刷新"
          density="compact"
          hide-details
          color="success"
          style="max-width: 140px"
        />
        <v-select
          v-model="autoRefreshInterval"
          :items="refreshIntervalOptions"
          density="compact"
          hide-details
          style="max-width: 100px"
          :disabled="!autoRefresh"
        />
        <span class="text-caption text-medium-emphasis ml-2">共 {{ total }} 条记录</span>
      </v-card-title>
      <v-data-table
        :headers="headers"
        :items="dataList"
        :loading="loading"
        :items-per-page="queryParams.page_size"
        :page="queryParams.page"
        :server-items-length="total"
        @update:page="p => { queryParams.page = p; loadData() }"
        @update:items-per-page="s => { queryParams.page_size = s; queryParams.page = 1; loadData() }"
        hover
        class="clickable-table"
        @click:row="(_, { item }) => openDetail(item)"
      >
        <template v-slot:item.start_code="{ item }">
          <v-chip v-if="item.start_code" size="small" variant="tonal" color="primary">{{ item.start_code }}</v-chip>
          <span v-else>-</span>
        </template>
        <template v-slot:item.skin_code="{ item }">
          <v-chip v-if="item.skin_code" size="small" variant="tonal" color="teal">{{ item.skin_code }}</v-chip>
          <span v-else>-</span>
        </template>
        <template v-slot:item.start_time="{ item }">
          {{ formatDateTime(item.start_time) }}
        </template>
        <template v-slot:item.end_time="{ item }">
          {{ formatDateTime(item.end_time) }}
        </template>
        <template v-slot:item.duringtime="{ item }">
          <span class="text-info">{{ formatDuration(item.duringtime) }}</span>
        </template>
        <template v-slot:item.machine_duringtime="{ item }">
          <span class="text-info">{{ formatDuration(item.machine_duringtime) }}</span>
        </template>
        <template v-slot:item.machine_id="{ item }">
          <v-chip v-if="item.machine_id" size="small" variant="tonal" color="warning">{{ item.machine_id }}</v-chip>
          <span v-else>-</span>
        </template>
        <template v-slot:item.operator="{ item }">
          {{ item.operator_name || item.operator_id || '-' }}
        </template>
        <template v-slot:item.org_info="{ item }">
          <div>
            <div>{{ item.group_name || item.group_code || '-' }}</div>
            <div class="text-caption text-medium-emphasis">{{ item.factory_name || item.factory_code || '-' }}</div>
          </div>
        </template>
        <template v-slot:item.line_code="{ item }">
          <v-chip v-if="item.line_code" size="small" variant="tonal" color="purple">{{ item.line_code }}</v-chip>
          <span v-else>-</span>
        </template>
        <template v-slot:item.process_no="{ item }">
          <v-chip v-if="item.process_no" size="small" variant="tonal" color="pink">{{ item.process_no }}</v-chip>
          <span v-else>-</span>
        </template>
        <template v-slot:item.actions="{ item }">
          <v-btn icon variant="text" size="small" color="primary" @click.stop="openDetail(item)">
            <v-icon icon="mdi-eye" size="small" />
            <v-tooltip activator="parent" location="top">查看详情</v-tooltip>
          </v-btn>
        </template>
        <template v-slot:no-data>
          <div class="text-center pa-8">
            <v-icon icon="mdi-inbox" size="48" color="grey-lighten-1" />
            <p class="text-medium-emphasis mt-2">暂无数据</p>
          </div>
        </template>
      </v-data-table>
    </v-card>

    <!-- Detail dialog -->
    <v-dialog v-model="detailDialog" max-width="1200px" scrollable>
      <v-card style="display: flex; flex-direction: column; height: 80vh;">
        <v-card-title class="d-flex align-center flex-shrink-0">
          <v-icon icon="mdi-cog-transfer" class="mr-2" />
          加工事件详情
          <v-chip v-if="selectedEvent?.event_uid" size="small" class="ml-2" color="primary">{{ selectedEvent.event_uid }}</v-chip>
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" @click="detailDialog = false" />
        </v-card-title>
        <v-divider class="flex-shrink-0" />
        <v-tabs v-model="detailTab" density="compact" color="primary" class="flex-shrink-0">
          <v-tab value="info">基本信息</v-tab>
          <v-tab value="device">
            关联设备
            <v-badge v-if="associationData.device" color="success" dot inline />
          </v-tab>
          <v-tab value="material">
            关联物料
            <v-badge v-if="associationData.material" color="info" dot inline />
          </v-tab>
          <v-tab value="params">
            工艺参数
            <v-badge v-if="associationData.counts?.process_params > 0" color="warning" :content="associationData.counts.process_params" inline />
          </v-tab>
          <v-tab value="alarms">
            报警记录
            <v-badge v-if="associationData.counts?.alarms > 0" color="error" :content="associationData.counts.alarms" inline />
          </v-tab>
          <v-tab value="quality">
            质检记录
            <v-badge v-if="associationData.counts?.quality_records > 0" color="purple" :content="associationData.counts.quality_records" inline />
          </v-tab>
          <v-tab value="orders">
            关联订单
            <v-badge v-if="associationData.counts?.orders > 0" color="teal" :content="associationData.counts.orders" inline />
          </v-tab>
          <v-tab value="compressed">
            压缩数据
            <v-badge v-if="(associationData.counts?.sv_relations || 0) + (associationData.counts?.pv_relations || 0) > 0" color="cyan" :content="(associationData.counts?.sv_relations || 0) + (associationData.counts?.pv_relations || 0)" inline />
          </v-tab>
        </v-tabs>
        <v-divider class="flex-shrink-0" />
        <v-card-text style="flex: 1; overflow-y: auto;">
          <v-tabs-window v-model="detailTab">
            <!-- 基本信息 -->
            <v-tabs-window-item value="info">
              <!-- Summary cards -->
              <v-row dense class="mb-4">
                <v-col cols="6" sm="3">
                  <v-card variant="tonal" color="warning">
                    <v-card-text class="text-center pa-3">
                      <v-icon icon="mdi-cog" size="24" />
                      <div class="text-caption mt-1">设备</div>
                      <div class="text-body-2 font-weight-bold">{{ associationData.device?.device_name || selectedEvent?.machine_id || '-' }}</div>
                    </v-card-text>
                  </v-card>
                </v-col>
                <v-col cols="6" sm="3">
                  <v-card variant="tonal" color="info">
                    <v-card-text class="text-center pa-3">
                      <v-icon icon="mdi-package-variant" size="24" />
                      <div class="text-caption mt-1">物料</div>
                      <div class="text-body-2 font-weight-bold">{{ associationData.material?.product_name || selectedEvent?.start_code || '-' }}</div>
                    </v-card-text>
                  </v-card>
                </v-col>
                <v-col cols="6" sm="3">
                  <v-card variant="tonal" color="pink">
                    <v-card-text class="text-center pa-3">
                      <v-icon icon="mdi-cog-transfer" size="24" />
                      <div class="text-caption mt-1">工艺</div>
                      <div class="text-body-2 font-weight-bold">{{ associationData.process_definition?.process_name || selectedEvent?.process_no || '-' }}</div>
                    </v-card-text>
                  </v-card>
                </v-col>
                <v-col cols="6" sm="3">
                  <v-card variant="tonal" color="purple">
                    <v-card-text class="text-center pa-3">
                      <v-icon icon="mdi-database" size="24" />
                      <div class="text-caption mt-1">关联数据</div>
                      <div class="text-body-2 font-weight-bold">
                        {{ (associationData.counts?.process_params || 0) + (associationData.counts?.alarms || 0) + (associationData.counts?.quality_records || 0) }} 条
                      </div>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col cols="12" sm="6" md="4">
                  <div class="text-caption text-medium-emphasis">事件 UID</div>
                  <div class="text-body-2">{{ selectedEvent?.event_uid || '-' }}</div>
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <div class="text-caption text-medium-emphasis">启动码</div>
                  <v-chip v-if="selectedEvent?.start_code" size="small" color="primary" variant="tonal">{{ selectedEvent.start_code }}</v-chip>
                  <span v-else>-</span>
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <div class="text-caption text-medium-emphasis">表皮码</div>
                  <v-chip v-if="selectedEvent?.skin_code" size="small" color="teal" variant="tonal">{{ selectedEvent.skin_code }}</v-chip>
                  <span v-else>-</span>
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <div class="text-caption text-medium-emphasis">设备 ID</div>
                  <v-chip v-if="selectedEvent?.machine_id" size="small" color="warning" variant="tonal">{{ selectedEvent.machine_id }}</v-chip>
                  <span v-else>-</span>
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <div class="text-caption text-medium-emphasis">工站编号</div>
                  <v-chip v-if="selectedEvent?.process_no" size="small" color="pink" variant="tonal">{{ selectedEvent.process_no }}</v-chip>
                  <span v-else>-</span>
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <div class="text-caption text-medium-emphasis">产线</div>
                  <v-chip v-if="selectedEvent?.line_code" size="small" color="purple" variant="tonal">{{ selectedEvent.line_code }}</v-chip>
                  <span v-else>-</span>
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <div class="text-caption text-medium-emphasis">开始时间</div>
                  <div class="text-body-2">{{ formatDateTime(selectedEvent?.start_time) }}</div>
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <div class="text-caption text-medium-emphasis">结束时间</div>
                  <div class="text-body-2">{{ formatDateTime(selectedEvent?.end_time) }}</div>
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <div class="text-caption text-medium-emphasis">加工时长</div>
                  <div class="text-body-2 text-info">{{ formatDuration(selectedEvent?.duringtime) }}</div>
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <div class="text-caption text-medium-emphasis">机器工作时间</div>
                  <div class="text-body-2 text-info">{{ formatDuration(selectedEvent?.machine_duringtime) }}</div>
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <div class="text-caption text-medium-emphasis">操作员</div>
                  <div class="text-body-2">{{ selectedEvent?.operator_name || selectedEvent?.operator_id || '-' }}</div>
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <div class="text-caption text-medium-emphasis">集团/工厂</div>
                  <div class="text-body-2">{{ selectedEvent?.group_name || selectedEvent?.group_code || '-' }} / {{ selectedEvent?.factory_name || selectedEvent?.factory_code || '-' }}</div>
                </v-col>
              </v-row>
            </v-tabs-window-item>

            <!-- 关联设备 -->
            <v-tabs-window-item value="device">
              <div v-if="detailLoading" class="text-center pa-8">
                <v-progress-circular indeterminate color="primary" />
              </div>
              <div v-else-if="associationData.device">
                <v-list density="compact">
                  <v-list-item prepend-icon="mdi-cog" :title="associationData.device.device_name" :subtitle="'设备编号: ' + associationData.device.device_code" />
                  <v-list-item v-if="associationData.device.device_type" prepend-icon="mdi-tag" title="设备类型" :subtitle="associationData.device.device_type" />
                  <v-list-item v-if="associationData.device.model" prepend-icon="mdi-information" title="型号" :subtitle="associationData.device.model" />
                  <v-list-item v-if="associationData.device.manufacturer" prepend-icon="mdi-factory" title="制造商" :subtitle="associationData.device.manufacturer" />
                  <v-list-item v-if="associationData.device.line_code" prepend-icon="mdi-source-branch" title="产线" :subtitle="associationData.device.line_code" />
                  <v-list-item v-if="associationData.device.location" prepend-icon="mdi-map-marker" title="位置" :subtitle="associationData.device.location" />
                  <v-list-item prepend-icon="mdi-circle" title="状态" :subtitle="associationData.device.status" />
                </v-list>
              </div>
              <div v-else class="text-center pa-8 text-medium-emphasis">
                <v-icon icon="mdi-cog-off-outline" size="48" />
                <p class="mt-2">未找到关联设备</p>
              </div>
            </v-tabs-window-item>

            <!-- 关联物料 -->
            <v-tabs-window-item value="material">
              <div v-if="detailLoading" class="text-center pa-8">
                <v-progress-circular indeterminate color="primary" />
              </div>
              <div v-else-if="associationData.material">
                <v-list density="compact">
                  <v-list-item prepend-icon="mdi-package-variant" :title="associationData.material.product_name" :subtitle="'U9 编码: ' + associationData.material.u9_material_code" />
                  <v-list-item v-if="associationData.material.part_number" prepend-icon="mdi-barcode" title="零件号" :subtitle="associationData.material.part_number" />
                  <v-list-item v-if="associationData.material.specification" prepend-icon="mdi-ruler" title="规格" :subtitle="associationData.material.specification" />
                  <v-list-item v-if="associationData.material.category" prepend-icon="mdi-shape" title="分类" :subtitle="associationData.material.category" />
                  <v-list-item v-if="associationData.material.material_type" prepend-icon="mdi-tag" title="物料类型" :subtitle="associationData.material.material_type" />
                </v-list>
              </div>
              <div v-else class="text-center pa-8 text-medium-emphasis">
                <v-icon icon="mdi-package-variant-closed" size="48" />
                <p class="mt-2">未找到关联物料</p>
              </div>
            </v-tabs-window-item>

            <!-- 工艺参数 -->
            <v-tabs-window-item value="params">
              <div v-if="detailLoading" class="text-center pa-8">
                <v-progress-circular indeterminate color="primary" />
              </div>
              <div v-else-if="detailData.processParams?.items?.length > 0">
                <v-table density="compact">
                  <thead>
                    <tr>
                      <th>参数名称</th>
                      <th>参数值</th>
                      <th>单位</th>
                      <th>工艺类型</th>
                      <th>批次号</th>
                      <th>记录时间</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="p in detailData.processParams.items" :key="p.id">
                      <td>{{ p.param_name }}</td>
                      <td class="font-weight-bold">{{ p.param_value }}</td>
                      <td>{{ p.unit || '-' }}</td>
                      <td>{{ p.process_type || '-' }}</td>
                      <td>{{ p.batch_no || '-' }}</td>
                      <td class="text-caption">{{ p.create_time || '-' }}</td>
                    </tr>
                  </tbody>
                </v-table>
              </div>
              <div v-else class="text-center pa-8 text-medium-emphasis">
                <v-icon icon="mdi-tune-variant" size="48" />
                <p class="mt-2">未找到关联工艺参数</p>
              </div>
            </v-tabs-window-item>

            <!-- 报警记录 -->
            <v-tabs-window-item value="alarms">
              <div v-if="detailLoading" class="text-center pa-8">
                <v-progress-circular indeterminate color="primary" />
              </div>
              <div v-else-if="detailData.alarms?.items?.length > 0">
                <v-table density="compact">
                  <thead>
                    <tr>
                      <th>报警代码</th>
                      <th>级别</th>
                      <th>类型</th>
                      <th>标题</th>
                      <th>报警值</th>
                      <th>状态</th>
                      <th>报警时间</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="a in detailData.alarms.items" :key="a.id || a.alarm_code">
                      <td><v-chip size="x-small" color="error">{{ a.alarm_code }}</v-chip></td>
                      <td>
                        <v-chip size="x-small" :color="a.alarm_level === 'critical' ? 'error' : a.alarm_level === 'warning' ? 'warning' : 'info'">
                          {{ a.alarm_level }}
                        </v-chip>
                      </td>
                      <td>{{ a.alarm_type || '-' }}</td>
                      <td>{{ a.title || '-' }}</td>
                      <td>{{ a.alarm_value ?? '-' }}</td>
                      <td>
                        <v-chip size="x-small" :color="a.status === 'resolved' ? 'success' : a.status === 'pending' ? 'warning' : 'grey'">
                          {{ a.status }}
                        </v-chip>
                      </td>
                      <td class="text-caption">{{ a.alarm_time || '-' }}</td>
                    </tr>
                  </tbody>
                </v-table>
              </div>
              <div v-else class="text-center pa-8 text-medium-emphasis">
                <v-icon icon="mdi-alarm-light-off" size="48" />
                <p class="mt-2">未找到关联报警记录</p>
              </div>
            </v-tabs-window-item>

            <!-- 质检记录 -->
            <v-tabs-window-item value="quality">
              <div v-if="detailLoading" class="text-center pa-8">
                <v-progress-circular indeterminate color="primary" />
              </div>
              <div v-else-if="detailData.quality?.items?.length > 0">
                <v-table density="compact">
                  <thead>
                    <tr>
                      <th>产品编号</th>
                      <th>产品名称</th>
                      <th>状态</th>
                      <th>缺陷类型</th>
                      <th>检验员</th>
                      <th>数量</th>
                      <th>合格</th>
                      <th>不合格</th>
                      <th>检验时间</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="q in detailData.quality.items" :key="q.id">
                      <td>{{ q.product_code }}</td>
                      <td>{{ q.product_name }}</td>
                      <td>
                        <v-chip size="x-small" :color="q.status === 'passed' ? 'success' : q.status === 'failed' ? 'error' : 'warning'">
                          {{ q.status === 'passed' ? '合格' : q.status === 'failed' ? '不合格' : '待检' }}
                        </v-chip>
                      </td>
                      <td>{{ q.defect_type || '-' }}</td>
                      <td>{{ q.inspector || '-' }}</td>
                      <td>{{ q.quantity }}</td>
                      <td class="text-success">{{ q.passed_quantity }}</td>
                      <td class="text-error">{{ q.failed_quantity }}</td>
                      <td class="text-caption">{{ q.inspect_time || '-' }}</td>
                    </tr>
                  </tbody>
                </v-table>
              </div>
              <div v-else class="text-center pa-8 text-medium-emphasis">
                <v-icon icon="mdi-check-circle-outline" size="48" />
                <p class="mt-2">未找到关联质检记录</p>
              </div>
            </v-tabs-window-item>

            <!-- 关联订单 -->
            <v-tabs-window-item value="orders">
              <div v-if="detailLoading" class="text-center pa-8">
                <v-progress-circular indeterminate color="primary" />
              </div>
              <div v-else-if="associationData.orders?.length > 0">
                <v-list density="compact">
                  <template v-for="o in associationData.orders" :key="o.id">
                    <v-list-item>
                      <template v-slot:prepend>
                        <v-icon icon="mdi-file-document" color="teal" />
                      </template>
                      <v-list-item-title>{{ o.doc_no }}</v-list-item-title>
                      <v-list-item-subtitle>
                        {{ o.item_name || '-' }} | 零件号: {{ o.part_number || '-' }}
                      </v-list-item-subtitle>
                      <template v-slot:append>
                        <v-chip size="x-small" :color="o.doc_state === 'completed' ? 'success' : 'grey'">{{ o.doc_state || '-' }}</v-chip>
                      </template>
                    </v-list-item>
                    <v-divider v-if="o !== associationData.orders[associationData.orders.length - 1]" />
                  </template>
                </v-list>
              </div>
              <div v-else class="text-center pa-8 text-medium-emphasis">
                <v-icon icon="mdi-file-document-outline" size="48" />
                <p class="mt-2">未找到关联订单</p>
              </div>
            </v-tabs-window-item>

            <!-- 压缩数据 -->
            <v-tabs-window-item value="compressed">
              <div v-if="detailLoading" class="text-center pa-8">
                <v-progress-circular indeterminate color="primary" />
              </div>
              <div v-else-if="detailData.compressedData">
                <v-row dense class="mb-4">
                  <v-col cols="4">
                    <v-card variant="tonal" color="cyan">
                      <v-card-text class="text-center pa-3">
                        <div class="text-h6">{{ detailData.compressedData.sv?.count || 0 }}</div>
                        <div class="text-caption">SV 设定值</div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="4">
                    <v-card variant="tonal" color="blue">
                      <v-card-text class="text-center pa-3">
                        <div class="text-h6">{{ detailData.compressedData.pv?.count || 0 }}</div>
                        <div class="text-caption">PV 过程值</div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                  <v-col cols="4">
                    <v-card variant="tonal" color="red">
                      <v-card-text class="text-center pa-3">
                        <div class="text-h6">{{ detailData.compressedData.alarm?.count || 0 }}</div>
                        <div class="text-caption">Alarm 报警</div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
                <div v-if="detailData.compressedData.summary" class="mb-4">
                  <div class="text-subtitle-2 mb-2">匹配汇总</div>
                  <v-table density="compact">
                    <tbody>
                      <tr><td>SV 记录数</td><td>{{ detailData.compressedData.summary.sv_count }}</td><td>已匹配</td><td>{{ detailData.compressedData.summary.sv_matched ? '是' : '否' }}</td></tr>
                      <tr><td>PV 记录数</td><td>{{ detailData.compressedData.summary.pv_count }}</td><td>已匹配</td><td>{{ detailData.compressedData.summary.pv_matched ? '是' : '否' }}</td></tr>
                      <tr><td>Alarm 记录数</td><td>{{ detailData.compressedData.summary.alarm_count }}</td><td>已匹配</td><td>{{ detailData.compressedData.summary.alarm_matched ? '是' : '否' }}</td></tr>
                    </tbody>
                  </v-table>
                </div>
                <div v-if="detailData.compressedData.sv?.items?.length > 0">
                  <div class="text-subtitle-2 mb-2">SV 数据（前 10 条）</div>
                  <v-table density="compact">
                    <thead>
                      <tr><th>Topic</th><th>时间戳</th><th>偏移(ms)</th></tr>
                    </thead>
                    <tbody>
                      <tr v-for="s in detailData.compressedData.sv.items.slice(0, 10)" :key="s.id">
                        <td class="text-caption">{{ s.sv_topic }}</td>
                        <td class="text-caption">{{ s.sv_timestamp }}</td>
                        <td>{{ s.time_offset_ms }}</td>
                      </tr>
                    </tbody>
                  </v-table>
                </div>
              </div>
              <div v-else class="text-center pa-8 text-medium-emphasis">
                <v-icon icon="mdi-database-off" size="48" />
                <p class="mt-2">未找到压缩数据</p>
              </div>
            </v-tabs-window-item>
          </v-tabs-window>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { processingEventApi, eventAssociationAPI } from '@/api'
import { formatDateTime } from '@/utils/datetime'

const showSearch = ref(true)

const intervalOptions = [
  { title: '分钟', value: 'minute' },
  { title: '小时', value: 'hour' },
  { title: '天', value: 'day' },
]

const headers = [
  { title: '启动码', key: 'start_code' },
  { title: '表皮码', key: 'skin_code' },
  { title: '开始时间', key: 'start_time' },
  { title: '结束时间', key: 'end_time' },
  { title: '加工时长', key: 'duringtime' },
  { title: '机器工作时间', key: 'machine_duringtime' },
  { title: '设备 ID', key: 'machine_id' },
  { title: '操作员', key: 'operator' },
  { title: '集团/工厂', key: 'org_info' },
  { title: '产线', key: 'line_code' },
  { title: '工站编号', key: 'process_no' },
  { title: '操作', key: 'actions', sortable: false, width: '80px' },
]

const loading = ref(false)
const dataList = ref([])
const total = ref(0)
const tableCard = ref(null)

// Quick filter
const quickFilter = ref('all')

// Auto refresh
const autoRefresh = ref(false)
const autoRefreshInterval = ref(30)
const refreshIntervalOptions = [
  { title: '30秒', value: 30 },
  { title: '60秒', value: 60 },
  { title: '5分钟', value: 300 },
]
let refreshTimer = null

// Detail dialog state
const detailDialog = ref(false)
const detailTab = ref('info')
const selectedEvent = ref(null)
const detailLoading = ref(false)
const associationData = ref({})
const detailData = ref({})
const stats = ref({
  total: 0,
  avg_duringtime: 0,
  avg_machine_duringtime: 0,
  machine_count: 0,
  operator_count: 0,
  line_count: 0
})
const trendChart = ref(null)
const trendChartEl = ref(null)

const queryParams = reactive({
  page: 1,
  page_size: 20,
  start_time: '',
  end_time: '',
  start_code: '',
  skin_code: '',
  machine_id: '',
  operator_id: '',
  group_code: '',
  factory_code: ''
})

const trendParams = reactive({
  interval: 'hour',
  machine_id: '',
  start_time: '',
  end_time: ''
})

// Quick filter watcher
watch(quickFilter, (val) => {
  const now = new Date()
  if (val === 'all') {
    queryParams.start_time = ''
    queryParams.end_time = ''
  } else if (val === 'today') {
    const start = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    queryParams.start_time = toLocalISOString(start)
    queryParams.end_time = toLocalISOString(now)
  } else if (val === 'week') {
    const start = new Date(now)
    start.setDate(start.getDate() - start.getDay())
    start.setHours(0, 0, 0, 0)
    queryParams.start_time = toLocalISOString(start)
    queryParams.end_time = toLocalISOString(now)
  } else if (val === 'month') {
    const start = new Date(now.getFullYear(), now.getMonth(), 1)
    queryParams.start_time = toLocalISOString(start)
    queryParams.end_time = toLocalISOString(now)
  }
  handleSearch()
})

// Auto refresh watcher
watch([autoRefresh, autoRefreshInterval], () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
  if (autoRefresh.value) {
    refreshTimer = setInterval(() => {
      loadData()
      loadStats()
    }, autoRefreshInterval.value * 1000)
  }
})

const formatDuration = (ms) => {
  if (!ms && ms !== 0) return '-'
  const seconds = ms / 1000
  if (seconds < 60) return `${seconds.toFixed(2)}秒`
  const minutes = seconds / 60
  if (minutes < 60) return `${minutes.toFixed(2)}分钟`
  const hours = minutes / 60
  return `${hours.toFixed(2)}小时`
}

const toLocalISOString = (date) => {
  const offset = date.getTimezoneOffset()
  const local = new Date(date.getTime() - offset * 60 * 1000)
  return local.toISOString().slice(0, 16)
}

const scrollToTable = () => {
  tableCard.value?.$el?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const loadData = async () => {
  loading.value = true
  try {
    const params = { ...queryParams }
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null) {
        delete params[key]
      }
    })

    const response = await processingEventApi.getList(params)
    dataList.value = response.data.items || []
    total.value = response.data.total || 0
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const params = { ...queryParams }
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null) {
        delete params[key]
      }
    })

    const response = await processingEventApi.getStats(params)
    stats.value = response.data
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
}

const loadTrendData = async () => {
  try {
    const params = {
      interval: trendParams.interval,
      machine_id: queryParams.machine_id || undefined,
      start_time: queryParams.start_time || undefined,
      end_time: queryParams.end_time || undefined
    }

    const response = await processingEventApi.getTrend(params)
    const trendData = response.data || []

    renderTrendChart(trendData)
  } catch (error) {
    console.error('加载趋势数据失败:', error)
  }
}

const renderTrendChart = (data) => {
  if (!trendChartEl.value) return

  if (!trendChart.value) {
    trendChart.value = echarts.init(trendChartEl.value)
  }

  if (!data || data.length === 0) {
    trendChart.value.clear()
    return
  }

  const option = {
    tooltip: {
      trigger: 'axis',
      confine: true,
      textStyle: { fontSize: 12 }
    },
    legend: {
      data: ['加工数量', '平均时长(秒)'],
      top: 0,
      right: 0,
      itemWidth: 16,
      itemHeight: 2,
      textStyle: { color: '#7ec8ff', fontSize: 12 }
    },
    grid: {
      left: 10,
      right: 10,
      bottom: 8,
      top: 36,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: data.map(item => item.time_point),
      axisLabel: { color: 'rgba(126,200,255,0.6)', fontSize: 11, rotate: 45 },
      axisLine: { lineStyle: { color: 'rgba(0,212,255,0.15)' } },
      axisTick: { show: false }
    },
    yAxis: [
      {
        type: 'value',
        name: '',
        axisLabel: { color: 'rgba(126,200,255,0.6)', fontSize: 11 },
        axisLine: { show: false },
        splitLine: { lineStyle: { color: 'rgba(0,212,255,0.08)' } }
      },
      {
        type: 'value',
        name: '',
        axisLabel: { color: 'rgba(126,200,255,0.6)', fontSize: 11 },
        axisLine: { show: false },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: '加工数量',
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 2, color: '#00d4ff' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0,212,255,0.25)' },
            { offset: 1, color: 'rgba(0,212,255,0)' }
          ])
        },
        data: data.map(item => item.event_count)
      },
      {
        name: '平均时长(秒)',
        type: 'line',
        smooth: true,
        symbol: 'none',
        yAxisIndex: 1,
        lineStyle: { width: 2, color: '#00ff88' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0,255,136,0.15)' },
            { offset: 1, color: 'rgba(0,255,136,0)' }
          ])
        },
        data: data.map(item => (item.avg_duringtime / 1000).toFixed(2))
      }
    ]
  }

  trendChart.value.setOption(option, true)
}

const handleSearch = () => {
  queryParams.page = 1
  loadData()
  loadStats()
  loadTrendData()
}

const handleReset = () => {
  queryParams.page = 1
  queryParams.start_time = ''
  queryParams.end_time = ''
  queryParams.start_code = ''
  queryParams.skin_code = ''
  queryParams.machine_id = ''
  queryParams.operator_id = ''
  queryParams.group_code = ''
  queryParams.factory_code = ''

  loadData()
  loadStats()
  loadTrendData()
}

const handleExport = async () => {
  try {
    const params = { ...queryParams }
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null) {
        delete params[key]
      }
    })

    const response = await processingEventApi.export(params)

    const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    const filename = `processing_events_${new Date().getTime()}.csv`
    link.download = filename
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('导出失败:', error)
  }
}

const openDetail = async (item) => {
  selectedEvent.value = item
  detailTab.value = 'info'
  detailDialog.value = true
  associationData.value = {}
  detailData.value = {}
  await loadAssociationData(item.id)
}

const loadAssociationData = async (eventId) => {
  detailLoading.value = true
  try {
    const response = await eventAssociationAPI.getAll(eventId)
    associationData.value = response.data || {}

    // Load detailed data for each tab
    const [paramsRes, alarmsRes, qualityRes, compressedRes] = await Promise.allSettled([
      eventAssociationAPI.getProcessParams(eventId),
      eventAssociationAPI.getAlarms(eventId),
      eventAssociationAPI.getQuality(eventId),
      eventAssociationAPI.getCompressedData(eventId),
    ])

    detailData.value = {
      processParams: paramsRes.status === 'fulfilled' ? paramsRes.value.data : { items: [] },
      alarms: alarmsRes.status === 'fulfilled' ? alarmsRes.value.data : { items: [] },
      quality: qualityRes.status === 'fulfilled' ? qualityRes.value.data : { items: [] },
      compressedData: compressedRes.status === 'fulfilled' ? compressedRes.value.data : null,
    }
  } catch (error) {
    console.error('加载关联数据失败:', error)
  } finally {
    detailLoading.value = false
  }
}

const handleResize = () => {
  if (trendChart.value) {
    trendChart.value.resize()
  }
}

onMounted(() => {
  loadData()
  loadStats()
  loadTrendData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (trendChart.value) {
    trendChart.value.dispose()
  }
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.clickable-table :deep(tbody tr) {
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.clickable-table :deep(tbody tr:hover) {
  background-color: rgba(0, 212, 255, 0.08) !important;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3) !important;
}
</style>
