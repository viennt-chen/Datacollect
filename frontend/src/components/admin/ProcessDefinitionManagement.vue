<template>
  <div>
    <!-- 工具栏 -->
    <v-toolbar flat color="transparent" class="mb-4">
      <div>
        <div class="d-flex align-center">
          <v-icon color="primary" class="mr-2" size="28">mdi-cog-transfer</v-icon>
          <span class="text-h5 font-weight-bold">工艺管理</span>
        </div>
        <div class="text-caption text-medium-emphasis ml-9">
          管理制造工艺及其设备与数据源关联
        </div>
      </div>
      <v-spacer />
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openDialog()">
        新增工艺
      </v-btn>
    </v-toolbar>

    <!-- 统计卡片 -->
    <v-row class="mb-4">
      <v-col cols="12" sm="4" md>
        <v-card>
          <v-card-text class="d-flex align-center">
            <v-icon size="40" color="primary" class="mr-3">mdi-cog-transfer</v-icon>
            <div>
              <div class="text-h5 font-weight-bold">{{ stats.total }}</div>
              <div class="text-caption text-medium-emphasis">总工艺数</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="4" md>
        <v-card>
          <v-card-text class="d-flex align-center">
            <v-icon size="40" color="success" class="mr-3">mdi-check-circle</v-icon>
            <div>
              <div class="text-h5 font-weight-bold">{{ stats.active }}</div>
              <div class="text-caption text-medium-emphasis">启用中</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="4" md>
        <v-card>
          <v-card-text class="d-flex align-center">
            <v-icon size="40" color="info" class="mr-3">mdi-cpu-64-bit</v-icon>
            <div>
              <div class="text-h5 font-weight-bold">{{ stats.device_count }}</div>
              <div class="text-caption text-medium-emphasis">关联设备</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="4" md>
        <v-card>
          <v-card-text class="d-flex align-center">
            <v-icon size="40" color="warning" class="mr-3">mdi-wifi</v-icon>
            <div>
              <div class="text-h5 font-weight-bold">{{ stats.topic_count }}</div>
              <div class="text-caption text-medium-emphasis">关联 Topic</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="4" md>
        <v-card>
          <v-card-text class="d-flex align-center">
            <v-icon size="40" color="deep-purple" class="mr-3">mdi-package-variant</v-icon>
            <div>
              <div class="text-h5 font-weight-bold">{{ stats.product_count }}</div>
              <div class="text-caption text-medium-emphasis">关联产品</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 筛选条件 -->
    <v-card class="mb-4">
      <v-card-title
        class="d-flex align-center py-3"
        style="cursor: pointer"
        @click="showSearch = !showSearch"
      >
        <v-icon class="mr-2">mdi-filter</v-icon>
        <span class="text-subtitle-1">筛选条件</span>
        <v-spacer />
        <v-btn
          variant="text"
          size="small"
          :icon="showSearch ? 'mdi-chevron-up' : 'mdi-chevron-down'"
        />
      </v-card-title>
      <v-divider v-if="showSearch" />
      <v-card-text v-if="showSearch">
        <v-form @submit.prevent="loadData">
          <v-row dense>
            <v-col cols="12" sm="6" md="3">
              <v-text-field
                v-model="searchKeyword"
                label="工艺编码/名称"
                prepend-inner-icon="mdi-magnify"
                density="compact"
                clearable
                @click:clear="onClearSearch"
              />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-select
                v-model="filterType"
                :items="processTypeOptions"
                item-title="text"
                item-value="value"
                label="工艺类型"
                density="compact"
                clearable
              />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-select
                v-model="filterStatus"
                :items="[{text:'启用',value:'active'},{text:'禁用',value:'inactive'}]"
                item-title="text"
                item-value="value"
                label="状态"
                density="compact"
                clearable
              />
            </v-col>
            <v-col cols="12" sm="6" md="3" class="d-flex align-center">
              <v-btn type="submit" color="primary" class="mr-2">查询</v-btn>
              <v-btn variant="text" @click="resetSearch">重置</v-btn>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-text-field
                v-model="filterParamField"
                label="工艺参数字段名"
                prepend-inner-icon="mdi-tune"
                density="compact"
                clearable
                placeholder="输入参数名筛选"
              />
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- 数据表格 -->
    <v-card>
      <v-card-title class="d-flex align-center py-3">
        <v-icon class="mr-2">mdi-format-list-bulleted</v-icon>
        <span class="text-subtitle-1">工艺列表</span>
        <v-spacer />
        <v-btn variant="outlined" size="small" prepend-icon="mdi-refresh" @click="loadData">
          刷新
        </v-btn>
      </v-card-title>
      <v-divider />
      <v-data-table-server
        :headers="headers"
        :items="items"
        :items-length="total"
        :loading="loading"
        :items-per-page="pageSize"
        :page="page"
        @update:options="onTableOptions"
        hover
      >
        <template #item.process_code="{ item }">
          <v-chip size="small" variant="tonal" color="primary">
            {{ item.process_code }}
          </v-chip>
        </template>

        <template #item.process_type="{ item }">
          <v-chip size="small" :color="getTypeColor(item.process_type)" variant="tonal">
            {{ getTypeLabel(item.process_type) }}
          </v-chip>
        </template>

        <template #item.device_count="{ item }">
          <v-chip size="small" color="info" variant="outlined">
            <v-icon start size="small">mdi-cpu-64-bit</v-icon>
            {{ (item.device_codes || []).length }}
          </v-chip>
        </template>

        <template #item.product_count="{ item }">
          <v-chip size="small" color="deep-purple" variant="outlined">
            <v-icon start size="small">mdi-package-variant</v-icon>
            {{ (item.product_codes || []).length }}
          </v-chip>
        </template>

        <template #item.topic_count="{ item }">
          <v-chip size="small" color="teal" variant="outlined">
            <v-icon start size="small">mdi-wifi</v-icon>
            {{ (item.mqtt_topic_ids || []).length }}
          </v-chip>
        </template>

        <template #item.status="{ item }">
          <v-chip
            size="small"
            :color="item.status === 'active' ? 'success' : 'error'"
            variant="tonal"
          >
            {{ item.status === 'active' ? '启用' : '禁用' }}
          </v-chip>
        </template>

        <template #item.actions="{ item }">
          <div class="d-flex ga-1">
            <v-btn icon variant="text" size="small" color="primary" @click="viewItem(item)">
              <v-icon>mdi-eye</v-icon>
              <v-tooltip activator="parent">查看</v-tooltip>
            </v-btn>
            <v-btn icon variant="text" size="small" color="primary" @click="openDialog(item)">
              <v-icon>mdi-pencil</v-icon>
              <v-tooltip activator="parent">编辑</v-tooltip>
            </v-btn>
            <v-btn icon variant="text" size="small" color="error" @click="confirmDelete(item)">
              <v-icon>mdi-delete</v-icon>
              <v-tooltip activator="parent">删除</v-tooltip>
            </v-btn>
          </div>
        </template>

        <template #no-data>
          <div class="text-center py-8">
            <v-icon icon="mdi-inbox" size="48" color="grey-lighten-1" />
            <div class="text-medium-emphasis mt-2">暂无工艺数据</div>
          </div>
        </template>
      </v-data-table-server>
    </v-card>

    <!-- 查看详情对话框 -->
    <v-dialog v-model="viewDialog" max-width="750">
      <v-card style="display: flex; flex-direction: column; height: 80vh;">
        <v-card-title class="d-flex align-center flex-shrink-0">
          <v-icon class="mr-2" color="primary">mdi-cog-transfer</v-icon>
          <span>工艺详情</span>
          <v-spacer />
          <v-btn
            icon="mdi-refresh"
            variant="text"
            size="small"
            :loading="liveParamsLoading"
            @click="viewItem_data && loadLiveParams(viewItem_data.id)"
          />
          <v-btn icon="mdi-close" variant="text" size="small" @click="viewDialog = false" />
        </v-card-title>
        <v-divider class="flex-shrink-0" />
        <v-tabs v-model="viewTab" density="compact" color="primary" class="flex-shrink-0">
          <v-tab value="info">基本信息</v-tab>
          <v-tab value="history">参数历史</v-tab>
        </v-tabs>
        <v-divider class="flex-shrink-0" />
        <v-card-text style="flex: 1; overflow-y: auto;">
          <!-- 基本信息 Tab -->
          <div v-show="viewTab === 'info'">
            <v-table density="compact">
              <tbody>
                <tr>
                  <td class="text-medium-emphasis" style="width: 120px">工艺编码</td>
                  <td><v-chip size="small" variant="tonal" color="primary">{{ viewItem_data?.process_code }}</v-chip></td>
                </tr>
                <tr>
                  <td class="text-medium-emphasis">工艺名称</td>
                  <td>{{ viewItem_data?.process_name }}</td>
                </tr>
                <tr>
                  <td class="text-medium-emphasis">工艺类型</td>
                  <td>
                    <v-chip size="small" :color="getTypeColor(viewItem_data?.process_type)" variant="tonal">
                      {{ getTypeLabel(viewItem_data?.process_type) }}
                    </v-chip>
                  </td>
                </tr>
                <tr>
                  <td class="text-medium-emphasis">状态</td>
                  <td>
                    <v-chip size="small" :color="viewItem_data?.status === 'active' ? 'success' : 'error'" variant="tonal">
                      {{ viewItem_data?.status === 'active' ? '启用' : '禁用' }}
                    </v-chip>
                  </td>
                </tr>
                <tr>
                  <td class="text-medium-emphasis">描述</td>
                  <td>{{ viewItem_data?.description || '-' }}</td>
                </tr>
                <tr>
                  <td class="text-medium-emphasis">关联设备</td>
                  <td>
                    <div class="d-flex flex-wrap ga-1">
                      <v-chip
                        v-for="code in (viewItem_data?.device_codes || [])"
                        :key="code"
                        size="small"
                        color="info"
                        variant="outlined"
                      >
                        <v-icon start size="x-small">mdi-cpu-64-bit</v-icon>
                        {{ code }}
                      </v-chip>
                      <span v-if="!(viewItem_data?.device_codes?.length)" class="text-medium-emphasis">-</span>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td class="text-medium-emphasis">关联产品</td>
                  <td>
                    <div class="d-flex flex-wrap ga-1">
                      <v-chip
                        v-for="code in (viewItem_data?.product_codes || [])"
                        :key="code"
                        size="small"
                        color="deep-purple"
                        variant="outlined"
                      >
                        <v-icon start size="x-small">mdi-package-variant</v-icon>
                        {{ getProductLabel(code) }}
                      </v-chip>
                      <span v-if="!(viewItem_data?.product_codes?.length)" class="text-medium-emphasis">-</span>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td class="text-medium-emphasis">关联 Topic</td>
                  <td>
                    <div class="d-flex flex-wrap ga-1">
                      <v-chip
                        v-for="tid in (viewItem_data?.mqtt_topic_ids || [])"
                        :key="tid"
                        size="small"
                        color="teal"
                        variant="outlined"
                      >
                        <v-icon start size="x-small">mdi-wifi</v-icon>
                        {{ getTopicLabel(tid) }}
                      </v-chip>
                      <span v-if="!(viewItem_data?.mqtt_topic_ids?.length)" class="text-medium-emphasis">-</span>
                    </div>
                  </td>
                </tr>
                <tr v-if="viewItem_data?.parameters && hasVisibleParams(viewItem_data.parameters)">
                  <td class="text-medium-emphasis">工艺参数</td>
                  <td>
                    <div v-if="liveParamsLoading" class="d-flex align-center ga-2 mb-2">
                      <v-progress-circular indeterminate size="16" />
                      <span class="text-caption text-medium-emphasis">加载实时数据中...</span>
                    </div>
                    <div v-for="(conf, name) in viewItem_data.parameters" :key="name" class="mb-1 d-flex align-center ga-2">
                      <strong>{{ name }}</strong>：
                      <span v-if="conf.set_value != null">设定值={{ conf.set_value }}</span>
                      <span v-if="conf.tolerance != null"> ±{{ conf.tolerance }}</span>
                      <span v-if="conf.unit"> {{ conf.unit }}</span>
                      <v-chip
                        v-if="liveParams?.parameters?.[name]?.set_value != null && liveParams.parameters[name].set_value !== conf.set_value"
                        size="x-small"
                        color="cyan"
                        variant="tonal"
                      >
                        实时={{ liveParams.parameters[name].set_value }}
                      </v-chip>
                    </div>
                    <div v-if="liveParams?.last_sync_time" class="text-caption text-medium-emphasis mt-2 d-flex align-center ga-1">
                      <v-icon size="x-small">mdi-sync</v-icon>
                      最近同步: {{ formatTime(liveParams.last_sync_time) }}
                      <span v-if="liveParams.last_source">| 来源: {{ liveParams.last_source }}</span>
                    </div>
                  </td>
                </tr>
                <tr v-if="viewItem_data?.parameters?._filter_rules?.length">
                  <td class="text-medium-emphasis">更新条件</td>
                  <td>
                    <v-chip v-for="(rule, i) in viewItem_data.parameters._filter_rules" :key="i" size="small" color="amber" variant="tonal" class="mr-1 mb-1">
                      {{ rule.field_path }} {{ rule.operator }} {{ rule.value }}
                    </v-chip>
                  </td>
                </tr>
              </tbody>
            </v-table>
          </div>

          <!-- 参数历史 Tab -->
          <div v-show="viewTab === 'history'">
            <div class="d-flex align-center mb-3 ga-2">
              <v-select
                v-model="historyChangeType"
                :items="[
                  { text: '全部', value: '' },
                  { text: 'MQTT 值变化', value: 'mqtt_value_change' },
                  { text: '定义变更', value: 'definition_change' }
                ]"
                item-title="text"
                item-value="value"
                density="compact"
                hide-details
                style="max-width: 180px;"
                @update:model-value="loadHistory(1)"
              />
              <v-btn size="small" variant="text" color="primary" prepend-icon="mdi-refresh" @click="loadHistory(1)">
                刷新
              </v-btn>
            </div>
            <v-table density="compact" hover>
              <thead>
                <tr>
                  <th v-for="h in historyHeaders" :key="h.key" class="text-left" style="white-space: nowrap;">{{ h.title }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="historyLoading">
                  <td :colspan="historyHeaders.length" class="text-center py-4">
                    <v-progress-circular indeterminate size="24" />
                  </td>
                </tr>
                <tr v-else-if="historyItems.length === 0">
                  <td :colspan="historyHeaders.length" class="text-center text-medium-emphasis py-4">暂无历史记录</td>
                </tr>
                <tr v-for="item in historyItems" :key="item.id">
                  <td><span class="text-caption">{{ formatTime(item.created_at) }}</span></td>
                  <td>
                    <v-chip size="x-small" :color="item.change_type === 'mqtt_value_change' ? 'cyan' : 'orange'" variant="tonal">
                      {{ item.change_type === 'mqtt_value_change' ? 'MQTT值' : '定义' }}
                    </v-chip>
                  </td>
                  <td>{{ item.param_name }}</td>
                  <td><span class="text-caption">{{ truncateValue(item.old_value) }}</span></td>
                  <td><span class="text-caption font-weight-bold">{{ truncateValue(item.new_value) }}</span></td>
                  <td>{{ item.source || '-' }}</td>
                </tr>
              </tbody>
            </v-table>
            <div v-if="historyTotal > historyPageSize" class="d-flex justify-center mt-2">
              <v-pagination
                :model-value="historyPage"
                :length="Math.ceil(historyTotal / historyPageSize)"
                density="compact"
                @update:model-value="loadHistory"
              />
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- 新增/编辑对话框 -->
    <v-dialog v-model="dialogVisible" max-width="800" persistent>
      <v-card style="display: flex; flex-direction: column; height: 80vh;">
        <v-card-title class="d-flex align-center flex-shrink-0">
          <v-icon class="mr-2" color="primary">mdi-cog-transfer</v-icon>
          <span>{{ editingItem ? '编辑工艺' : '新增工艺' }}</span>
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="dialogVisible = false" />
        </v-card-title>
        <v-divider class="flex-shrink-0" />
        <v-card-text style="flex: 1; overflow-y: auto;">
          <v-form ref="formRef" v-model="formValid">
            <v-row dense>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="form.process_code"
                  label="工艺编码（自动生成，可修改）"
                  :rules="[v => !!v || '必填']"
                  :disabled="!!editingItem"
                  :loading="codeLoading"
                  density="compact"
                  :append-icon="editingItem ? undefined : 'mdi-refresh'"
                  @click:append="fetchNextCode"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="form.process_name"
                  label="工艺名称"
                  :rules="[v => !!v || '必填']"
                  density="compact"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="form.process_type"
                  :items="processTypeOptions"
                  item-title="text"
                  item-value="value"
                  label="工艺类型"
                  density="compact"
                  @update:model-value="onTypeChange"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="form.status"
                  :items="[{text:'启用',value:'active'},{text:'禁用',value:'inactive'}]"
                  item-title="text"
                  item-value="value"
                  label="状态"
                  density="compact"
                />
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="form.description"
                  label="描述"
                  rows="2"
                  density="compact"
                  auto-grow
                />
              </v-col>

              <!-- 关联设备 -->
              <v-col cols="12">
                <div class="text-subtitle-2 mb-1 d-flex align-center">
                  <v-icon size="small" color="info" class="mr-1">mdi-cpu-64-bit</v-icon>
                  关联设备
                </div>
                <v-autocomplete
                  v-model="form.device_codes"
                  :items="deviceOptions"
                  item-title="label"
                  item-value="code"
                  label="选择设备（可多选）"
                  multiple
                  chips
                  closable-chips
                  density="compact"
                  :loading="devicesLoading"
                  @update:search="onSearchDevices"
                  @click:control="onSearchDevices('')"
                />
              </v-col>

              <!-- 关联产品 -->
              <v-col cols="12">
                <div class="text-subtitle-2 mb-1 d-flex align-center">
                  <v-icon size="small" color="deep-purple" class="mr-1">mdi-package-variant</v-icon>
                  关联产品（加工后产品）
                </div>
                <v-autocomplete
                  v-model="form.product_codes"
                  :items="productOptions"
                  item-title="label"
                  item-value="code"
                  label="输入关键词搜索，自动加载所有匹配产品"
                  multiple
                  chips
                  closable-chips
                  density="compact"
                  :loading="productsLoading"
                  @update:search="onSearchProducts"
                  @update:model-value="onProductCodesChange"
                  @click:control="loadProducts()"
                />
              </v-col>

              <!-- 关联 MQTT Topic -->
              <v-col cols="12">
                <div class="text-subtitle-2 mb-1 d-flex align-center">
                  <v-icon size="small" color="teal" class="mr-1">mdi-wifi</v-icon>
                  关联 MQTT Topic
                </div>
                <v-autocomplete
                  v-model="form.mqtt_topic_ids"
                  :items="topicOptions"
                  item-title="label"
                  item-value="id"
                  label="选择 MQTT Topic（可多选）"
                  multiple
                  chips
                  closable-chips
                  density="compact"
                  :loading="topicsLoading"
                  @update:model-value="onTopicsChange"
                />
              </v-col>

              <!-- 自动发现的 Topic 字段 -->
              <v-col cols="12" v-if="form.mqtt_topic_ids && form.mqtt_topic_ids.length > 0">
                <div class="text-subtitle-2 mb-1 d-flex align-center">
                  <v-icon size="small" color="cyan" class="mr-1">mdi-auto-fix</v-icon>
                  可用 Topic 字段
                  <v-progress-circular v-if="fieldsLoading" indeterminate size="16" class="ml-2" />
                  <v-btn
                    v-if="discoveredFields.length > 0"
                    size="x-small"
                    variant="text"
                    color="cyan"
                    @click="addAllDiscoveredFields"
                    class="ml-2"
                  >
                    全部添加
                  </v-btn>
                  <v-btn
                    size="x-small"
                    variant="text"
                    color="cyan"
                    prepend-icon="mdi-refresh"
                    @click="refreshTopicFields"
                    class="ml-1"
                  >
                    刷新
                  </v-btn>
                  <span v-if="lastRefreshTime" class="text-caption text-medium-emphasis ml-2">
                    最近更新: {{ lastRefreshTime }} (每10秒自动刷新)
                  </span>
                </div>
                <div v-if="!fieldsLoading && discoveredFields.length === 0" class="text-caption text-medium-emphasis">
                  所选 Topic 暂无可用字段（请确认 Topic 已配置 parse_rules 或已有 MQTT 消息）
                </div>
                <div v-if="discoveredFields.length > 0" class="d-flex flex-wrap ga-2">
                  <v-chip
                    v-for="field in discoveredFields"
                    :key="field.path"
                    size="small"
                    :color="paramList.some(p => p.name === field.path) ? 'success' : 'cyan'"
                    :variant="paramList.some(p => p.name === field.path) ? 'tonal' : 'outlined'"
                    @click="addFieldFromDiscovered(field)"
                    :disabled="paramList.some(p => p.name === field.path)"
                  >
                    <v-icon start size="x-small">
                      {{ field.source === 'parse_rules' ? 'mdi-file-tree' : 'mdi-broadcast' }}
                    </v-icon>
                    {{ field.path }}
                    <span v-if="field.sample_value !== null" class="ml-1 font-weight-bold">={{ field.sample_value }}</span>
                    <v-tooltip activator="parent">
                      类型: {{ field.type }}
                      <span v-if="field.sample_value !== null"> | 当前值: {{ field.sample_value }}</span>
                    </v-tooltip>
                  </v-chip>
                </div>
              </v-col>

              <!-- 参数更新条件 -->
              <v-col cols="12" v-if="form.mqtt_topic_ids && form.mqtt_topic_ids.length > 0">
                <v-expansion-panels variant="accordion" density="compact">
                  <v-expansion-panel>
                    <v-expansion-panel-title>
                      <div class="d-flex align-center">
                        <v-icon size="small" color="amber" class="mr-1">mdi-filter-cog</v-icon>
                        <span class="text-subtitle-2">参数更新条件</span>
                        <v-chip v-if="filterRules.length > 0" size="x-small" color="amber" variant="tonal" class="ml-2">
                          {{ filterRules.length }} 个条件
                        </v-chip>
                        <v-chip v-if="filterRules.length > 0 && !filterConditionMet" size="x-small" color="error" variant="tonal" class="ml-1">
                          条件未满足
                        </v-chip>
                      </div>
                    </v-expansion-panel-title>
                    <v-expansion-panel-text>
                      <div class="text-caption text-medium-emphasis mb-2">
                        设置条件后，仅当所有条件都满足时才自动更新工艺参数（AND 关系）。不设置条件则始终更新。
                      </div>
                      <div v-for="(rule, idx) in filterRules" :key="idx" class="d-flex align-center mb-2 ga-2">
                        <v-autocomplete
                          v-model="rule.field_path"
                          :items="discoveredFields"
                          item-title="path"
                          item-value="path"
                          label="MQTT 字段"
                          density="compact"
                          hide-details
                          style="max-width: 280px;"
                          clearable
                        >
                          <template #item="{ item, props }">
                            <v-list-item v-bind="props" :subtitle="`当前值: ${item.raw.sample_value ?? '-'}`" />
                          </template>
                        </v-autocomplete>
                        <v-select
                          v-model="rule.operator"
                          :items="[{ text: '等于 (==)', value: '==' }, { text: '不等于 (!=)', value: '!=' }]"
                          item-title="text"
                          item-value="value"
                          label="运算符"
                          density="compact"
                          hide-details
                          style="max-width: 140px;"
                        />
                        <v-text-field
                          v-model="rule.value"
                          label="期望值"
                          density="compact"
                          hide-details
                          style="max-width: 160px;"
                        />
                        <v-btn icon size="small" variant="text" color="error" @click="filterRules.splice(idx, 1)">
                          <v-icon size="small">mdi-delete</v-icon>
                        </v-btn>
                      </div>
                      <v-btn size="small" variant="text" color="amber" prepend-icon="mdi-plus" @click="addFilterRule">
                        添加条件
                      </v-btn>
                    </v-expansion-panel-text>
                  </v-expansion-panel>
                </v-expansion-panels>
              </v-col>

              <!-- 工艺参数 -->
              <v-col cols="12">
                <div class="text-subtitle-2 mb-1 d-flex align-center">
                  <v-icon size="small" color="warning" class="mr-1">mdi-tune</v-icon>
                  工艺参数
                  <v-chip v-if="filterRules.length > 0 && !filterConditionMet" size="x-small" color="error" variant="tonal" class="ml-2">
                    条件未满足，参数不自动更新
                  </v-chip>
                </div>
                <div v-for="(param, idx) in paramList" :key="idx" class="d-flex align-center mb-2 ga-2">
                  <v-text-field
                    v-model="param.name"
                    label="参数名"
                    density="compact"
                    hide-details
                    style="max-width: 220px;"
                  />
                  <v-text-field
                    v-model="param.set_value"
                    label="设定值"
                    density="compact"
                    hide-details
                    style="max-width: 120px;"
                  />
                  <v-text-field
                    v-model="param.tolerance"
                    label="容许误差范围"
                    type="number"
                    density="compact"
                    hide-details
                    style="max-width: 140px;"
                  />
                  <v-text-field
                    v-model="param.unit"
                    label="单位"
                    density="compact"
                    hide-details
                    style="max-width: 100px;"
                  />
                  <v-btn icon size="small" variant="text" color="error" @click="removeParam(idx)">
                    <v-icon>mdi-close</v-icon>
                  </v-btn>
                </div>
                <v-btn size="small" variant="tonal" color="primary" @click="addParam" prepend-icon="mdi-plus">
                  添加参数
                </v-btn>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-divider class="flex-shrink-0" />
        <v-card-actions class="flex-shrink-0">
          <v-spacer />
          <v-btn variant="text" @click="dialogVisible = false">取消</v-btn>
          <v-btn color="primary" :loading="saving" :disabled="!formValid" @click="saveItem">保存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 删除确认 -->
    <v-dialog v-model="deleteDialog" max-width="440">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon color="error" class="mr-2">mdi-alert</v-icon>
          <span>确认删除</span>
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="deleteDialog = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          确定要删除工艺 <strong>{{ deletingItem?.process_code }}</strong> - <strong>{{ deletingItem?.process_name }}</strong> 吗？
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="deleteDialog = false">取消</v-btn>
          <v-btn color="error" :loading="deleting" @click="deleteItem">删除</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 提示 -->
    <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="3000">
      {{ snackbarText }}
    </v-snackbar>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, onUnmounted } from 'vue'
import { processDefinitionAPI, deviceAPI, mqttTopicConfigApi, materialAPI, processParamHistoryAPI } from '@/api'

const processTypeOptions = [
  { text: '注塑成型', value: 'injection' },
  { text: 'CNC 加工', value: 'cnc' },
  { text: '装配', value: 'assembly' },
  { text: '检测', value: 'inspection' },
  { text: '其他', value: 'other' },
]

const headers = [
  { title: '工艺编码', key: 'process_code', sortable: false, minWidth: '120px' },
  { title: '工艺名称', key: 'process_name', sortable: false, minWidth: '140px' },
  { title: '类型', key: 'process_type', sortable: false, minWidth: '100px' },
  { title: '关联设备', key: 'device_count', sortable: false, align: 'center', minWidth: '90px' },
  { title: '关联产品', key: 'product_count', sortable: false, align: 'center', minWidth: '90px' },
  { title: '关联 Topic', key: 'topic_count', sortable: false, align: 'center', minWidth: '90px' },
  { title: '状态', key: 'status', sortable: false, minWidth: '80px' },
  { title: '操作', key: 'actions', sortable: false, align: 'center', minWidth: '140px' },
]

const loading = ref(false)
const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const searchKeyword = ref('')
const filterType = ref(null)
const filterStatus = ref(null)
const filterParamField = ref('')
const showSearch = ref(true)

const stats = reactive({ total: 0, active: 0, device_count: 0, topic_count: 0, product_count: 0 })

const dialogVisible = ref(false)
const editingItem = ref(null)
const formRef = ref(null)
const formValid = ref(false)
const saving = ref(false)

const viewDialog = ref(false)
const viewItem_data = ref(null)
const liveParams = ref(null)
const liveParamsLoading = ref(false)

const deleteDialog = ref(false)
const deletingItem = ref(null)
const deleting = ref(false)

const snackbar = ref(false)
const snackbarText = ref('')
const snackbarColor = ref('success')

const deviceOptions = ref([])
const topicOptions = ref([])
const productOptions = ref([])
const productSearchText = ref('')
const devicesLoading = ref(false)
const topicsLoading = ref(false)
const productsLoading = ref(false)
const codeLoading = ref(false)
let productSearchTimer = null
const MAX_SEARCH_PAGES = 3

const paramList = ref([])

// 参数更新筛选规则
const filterRules = ref([])

// Topic 字段自动发现
const discoveredFields = ref([])
const fieldsLoading = ref(false)
let fieldPollTimer = null
const POLL_INTERVAL = 10000 // 10秒轮询一次
const lastRefreshTime = ref('')
const filterConditionMet = ref(true) // 筛选条件是否满足

// 实时参数轮询
let liveParamsPollTimer = null
const LIVE_PARAMS_INTERVAL = 2000 // 2秒轮询一次

// 工艺详情 Tab
const viewTab = ref('info')

// 参数历史
const historyItems = ref([])
const historyTotal = ref(0)
const historyPage = ref(1)
const historyPageSize = 20
const historyLoading = ref(false)
const historyChangeType = ref('')

const defaultForm = () => ({
  process_code: '',
  process_name: '',
  description: '',
  process_type: 'other',
  device_codes: [],
  mqtt_topic_ids: [],
  product_codes: [],
  parameters: {},
  status: 'active',
})

const form = ref(defaultForm())

function getTypeLabel(type) {
  const opt = processTypeOptions.find(o => o.value === type)
  return opt ? opt.text : type
}

function getTypeColor(type) {
  const map = { injection: 'orange', cnc: 'blue', assembly: 'purple', inspection: 'green', other: 'grey' }
  return map[type] || 'grey'
}

function getTopicLabel(id) {
  const opt = topicOptions.value.find(t => t.id === id)
  return opt ? opt.label : `#${id}`
}

function getProductLabel(code) {
  const opt = productOptions.value.find(p => p.code === code)
  return opt ? opt.label : code
}

async function loadData() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
    }
    if (searchKeyword.value) params.keyword = searchKeyword.value
    if (filterType.value) params.process_type = filterType.value
    if (filterStatus.value) params.status = filterStatus.value
    if (filterParamField.value) params.param_field = filterParamField.value

    const res = await processDefinitionAPI.list(params)
    items.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    console.error('加载工艺列表失败:', e)
    showMsg('加载失败', 'error')
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  try {
    const res = await processDefinitionAPI.getStats()
    Object.assign(stats, res.data)
  } catch (e) {
    console.error('加载统计数据失败:', e)
  }
}

function onTableOptions({ page: p, itemsPerPage }) {
  page.value = p
  pageSize.value = itemsPerPage
  loadData()
}

function resetSearch() {
  searchKeyword.value = ''
  filterType.value = null
  filterStatus.value = null
  filterParamField.value = ''
  loadData()
}

function onClearSearch() {
  searchKeyword.value = ''
  loadData()
}

function deviceToOption(d) {
  return { code: d.device_code, label: `${d.device_code} - ${d.device_name}` }
}

async function loadDevices() {
  devicesLoading.value = true
  try {
    const res = await deviceAPI.getDevices({ page: 1, page_size: 100 })
    const list = res.data.items || res.data || []
    const options = list.map(deviceToOption)
    // 确保已选中的设备在选项中（编辑时可能不在第一页）
    const selectedCodes = new Set(options.map(o => o.code))
    const missingCodes = (form.value.device_codes || []).filter(c => !selectedCodes.has(c))
    if (missingCodes.length > 0) {
      for (const code of missingCodes) {
        try {
          const r = await deviceAPI.getDevice(code)
          const d = r.data
          options.push(deviceToOption(d))
        } catch (_) { /* ignore */ }
      }
    }
    deviceOptions.value = options
  } catch (e) {
    console.error('加载设备失败:', e)
  } finally {
    devicesLoading.value = false
  }
}

async function onSearchDevices(query) {
  devicesLoading.value = true
  try {
    const params = { page: 1, page_size: 100 }
    if (query && query.length > 0) params.keyword = query
    const res = await deviceAPI.getDevices(params)
    const list = res.data.items || res.data || []
    const options = list.map(deviceToOption)
    // 保留已选中但不在搜索结果中的项
    const resultCodes = new Set(options.map(o => o.code))
    for (const opt of deviceOptions.value) {
      if ((form.value.device_codes || []).includes(opt.code) && !resultCodes.has(opt.code)) {
        options.push(opt)
      }
    }
    deviceOptions.value = options
  } catch (e) {
    console.error('搜索设备失败:', e)
  } finally {
    devicesLoading.value = false
  }
}

async function loadTopics() {
  topicsLoading.value = true
  try {
    const res = await mqttTopicConfigApi.getList({ page: 1, page_size: 100 })
    const list = res.data.items || res.data || []
    topicOptions.value = list.map(t => ({
      id: t.id,
      label: `${t.topic_name} (${t.topic_type})`,
    }))
  } catch (e) {
    console.error('加载 MQTT Topic 失败:', e)
  } finally {
    topicsLoading.value = false
  }
}

async function onTopicsChange(topicIds) {
  if (!topicIds || topicIds.length === 0) {
    discoveredFields.value = []
    stopFieldPolling()
    return
  }
  fieldsLoading.value = true
  try {
    const res = await mqttTopicConfigApi.getFields(topicIds)
    const allFields = []
    const seen = new Set()
    for (const topic of (res.data.topics || [])) {
      for (const f of (topic.fields || [])) {
        if (!seen.has(f.path)) {
          seen.add(f.path)
          allFields.push({ ...f, source: topic.source, topic_name: topic.topic_name })
        }
      }
    }
    discoveredFields.value = allFields
    lastRefreshTime.value = new Date().toLocaleTimeString()
    startFieldPolling()
  } catch (e) {
    console.error('获取 Topic 字段失败:', e)
    discoveredFields.value = []
  } finally {
    fieldsLoading.value = false
  }
}

function addFieldFromDiscovered(field) {
  if (paramList.value.some(p => p.name === field.path)) return
  const val = field.sample_value != null ? String(field.sample_value) : ''
  paramList.value.push({
    name: field.path,
    set_value: val,
    tolerance: '',
    unit: field.unit || '',
    _fromTopic: true,
  })
}

function addAllDiscoveredFields() {
  for (const field of discoveredFields.value) {
    if (!paramList.value.some(p => p.name === field.path)) {
      const val = field.sample_value != null ? String(field.sample_value) : ''
      paramList.value.push({
        name: field.path,
        set_value: val,
        tolerance: '',
        unit: field.unit || '',
        _fromTopic: true,
      })
    }
  }
}

// 检查筛选条件是否满足
function checkFilterConditions(fields) {
  if (filterRules.value.length === 0) {
    filterConditionMet.value = true
    return true
  }
  const fieldMap = {}
  for (const f of fields) {
    fieldMap[f.path] = f
  }
  const allMet = filterRules.value.every(rule => {
    if (!rule.field_path || rule.value === '') return true
    const field = fieldMap[rule.field_path]
    if (!field || field.sample_value == null) return false
    const actual = String(field.sample_value)
    const expected = String(rule.value)
    return rule.operator === '==' ? actual === expected : actual !== expected
  })
  filterConditionMet.value = allMet
  return allMet
}

// 从 MQTT 数据刷新已添加参数的设定值（只更新来自 topic 且用户未手动修改容差的参数）
function refreshParamValuesFromFields(fields) {
  // 先检查筛选条件
  if (!checkFilterConditions(fields)) {
    return // 条件不满足，跳过更新
  }

  const fieldMap = {}
  for (const f of fields) {
    fieldMap[f.path] = f
  }

  const changes = []
  for (const param of paramList.value) {
    if (param._fromTopic && fieldMap[param.name]) {
      const f = fieldMap[param.name]
      if (f.sample_value != null) {
        // 仅当未设定容差时自动更新设定值（说明用户未手动设定范围）
        if (!param.tolerance || param.tolerance === '' || param.tolerance === '0') {
          const oldVal = param.set_value
          const newVal = String(f.sample_value)
          if (oldVal !== newVal) {
            changes.push({ param_name: param.name, old_value: oldVal, new_value: newVal, source: f.topic_name || 'mqtt' })
            param.set_value = newVal
          }
        }
      }
    }
  }

  // 记录 MQTT 值变化历史
  if (changes.length > 0 && editingItem.value) {
    recordMqttValueChanges(changes)
  }
}

async function refreshTopicFields() {
  const topicIds = form.value.mqtt_topic_ids
  if (!topicIds || topicIds.length === 0) return
  try {
    const res = await mqttTopicConfigApi.getFields(topicIds)
    const allFields = []
    const seen = new Set()
    for (const topic of (res.data.topics || [])) {
      for (const f of (topic.fields || [])) {
        if (!seen.has(f.path)) {
          seen.add(f.path)
          allFields.push({ ...f, source: topic.source, topic_name: topic.topic_name })
        }
      }
    }
    discoveredFields.value = allFields
    refreshParamValuesFromFields(allFields)
    lastRefreshTime.value = new Date().toLocaleTimeString()
  } catch (e) {
    console.error('刷新 Topic 字段失败:', e)
  }
}

function startFieldPolling() {
  stopFieldPolling()
  fieldPollTimer = setInterval(() => {
    refreshTopicFields()
  }, POLL_INTERVAL)
}

function stopFieldPolling() {
  if (fieldPollTimer) {
    clearInterval(fieldPollTimer)
    fieldPollTimer = null
  }
}

watch(dialogVisible, (val) => {
  if (val && form.value.mqtt_topic_ids && form.value.mqtt_topic_ids.length > 0) {
    startFieldPolling()
  } else {
    stopFieldPolling()
  }
})

watch(viewDialog, (val) => {
  if (!val) {
    stopLiveParamsPolling()
    liveParams.value = null
  }
})

onUnmounted(() => {
  stopFieldPolling()
  stopLiveParamsPolling()
})

function materialToOption(m) {
  return {
    code: m.u9_material_code,
    label: `${m.u9_material_code} - ${m.product_name}${m.category ? ' [' + m.category + ']' : ''}${m.part_number ? ' (' + m.part_number + ')' : ''}`,
  }
}

function onProductCodesChange(val) {
  console.log('产品选择变化:', val)
  console.log('当前表单 product_codes:', form.value.product_codes)
}

async function loadProducts(query) {
  if (productSearchTimer) {
    clearTimeout(productSearchTimer)
    productSearchTimer = null
  }

  productsLoading.value = true
  try {
    const allOptions = []
    let page = 1
    const pageSize = 500
    let hasMore = true

    while (hasMore) {
      const params = { page, page_size: pageSize, material_type: 'product' }
      if (query) {
        params.keyword = query
      }
      const res = await materialAPI.getMaterials(params)
      const list = res.data.items || res.data || []
      const options = list.map(materialToOption)
      allOptions.push(...options)

      const total = res.data.total || 0
      hasMore = allOptions.length < total && list.length === pageSize
      page++
    }

    const resultCodes = new Set(allOptions.map(o => o.code))
    const missingCodes = (form.value.product_codes || []).filter(c => !resultCodes.has(c))
    if (missingCodes.length > 0) {
      for (const code of missingCodes) {
        try {
          const r = await materialAPI.getMaterials({ page: 1, page_size: 1, u9_material_code: code })
          const found = (r.data.items || []).find(m => m.u9_material_code === code)
          if (found) allOptions.push(materialToOption(found))
          else allOptions.push({ code, label: code })
        } catch (_) {
          allOptions.push({ code, label: code })
        }
      }
    }
    productOptions.value = allOptions
  } catch (e) {
    console.error('加载产品失败:', e)
  } finally {
    productsLoading.value = false
  }
}

async function onSearchProducts(query) {
  if (productSearchTimer) {
    clearTimeout(productSearchTimer)
  }

  if (!query || query.trim().length === 0) {
    loadProducts()
    return
  }

  productsLoading.value = true
  productSearchTimer = setTimeout(async () => {
    try {
      const allOptions = []
      let page = 1
      const pageSize = 500
      let hasMore = true
      let pageCount = 0

      while (hasMore) {
        const params = { page, page_size: pageSize, material_type: 'product', keyword: query.trim() }
        const res = await materialAPI.getMaterials(params)
        const list = res.data.items || res.data || []
        const options = list.map(materialToOption)
        allOptions.push(...options)
        pageCount++

        const total = res.data.total || 0
        hasMore = allOptions.length < total && list.length === pageSize && pageCount < MAX_SEARCH_PAGES
        page++
      }

      const resultCodes = new Set(allOptions.map(o => o.code))
      for (const opt of productOptions.value) {
        if ((form.value.product_codes || []).includes(opt.code) && !resultCodes.has(opt.code)) {
          allOptions.push(opt)
        }
      }
      productOptions.value = allOptions
    } catch (e) {
      console.error('搜索产品失败:', e)
    } finally {
      productsLoading.value = false
      productSearchTimer = null
    }
  }, 300)
}

function parseParameters(params) {
  if (!params || typeof params !== 'object' || Array.isArray(params)) return []
  return Object.entries(params)
    .filter(([name]) => name !== '_filter_rules')
    .map(([name, conf]) => ({
      name,
      set_value: conf.set_value != null ? String(conf.set_value) : '',
      tolerance: conf.tolerance != null ? String(conf.tolerance) : '',
      unit: conf.unit ?? '',
      _fromTopic: conf._fromTopic ?? false,
    }))
}

function buildParameters(list) {
  const result = {}
  for (const p of list) {
    if (!p.name) continue
    const conf = {}
    if (p.set_value !== '' && p.set_value != null) {
      const n = Number(p.set_value)
      conf.set_value = isNaN(n) ? p.set_value : n
    }
    if (p.tolerance !== '' && p.tolerance != null) {
      const n = Number(p.tolerance)
      conf.tolerance = isNaN(n) ? p.tolerance : n
    }
    if (p.unit) conf.unit = p.unit
    result[p.name] = conf
  }
  // 保存筛选规则
  const validRules = filterRules.value.filter(r => r.field_path && r.value !== '')
  if (validRules.length > 0) {
    result._filter_rules = validRules
  }
  return result
}

async function fetchNextCode() {
  codeLoading.value = true
  try {
    const res = await processDefinitionAPI.getNextCode(form.value.process_type || 'other')
    form.value.process_code = res.data.code
  } catch (e) {
    console.error('获取编码失败:', e)
  } finally {
    codeLoading.value = false
  }
}

function onTypeChange() {
  if (!editingItem.value) {
    fetchNextCode()
  }
}

function viewItem(item) {
  viewItem_data.value = item
  viewTab.value = 'info'
  viewDialog.value = true
  loadHistory(1)
  loadLiveParams(item.id)
  startLiveParamsPolling(item.id)
}

async function loadLiveParams(processId) {
  liveParamsLoading.value = true
  try {
    const res = await processDefinitionAPI.getLiveParams(processId)
    liveParams.value = res.data
  } catch (e) {
    console.error('获取实时参数失败:', e)
  } finally {
    liveParamsLoading.value = false
  }
}

function startLiveParamsPolling(processId) {
  stopLiveParamsPolling()
  liveParamsPollTimer = setInterval(() => {
    if (viewDialog.value && viewItem_data.value) {
      loadLiveParams(viewItem_data.value.id)
    }
  }, LIVE_PARAMS_INTERVAL)
}

function stopLiveParamsPolling() {
  if (liveParamsPollTimer) {
    clearInterval(liveParamsPollTimer)
    liveParamsPollTimer = null
  }
}

function openDialog(item = null) {
  editingItem.value = item
  if (item) {
    form.value = {
      process_code: item.process_code,
      process_name: item.process_name,
      description: item.description || '',
      process_type: item.process_type || 'other',
      device_codes: item.device_codes || [],
      mqtt_topic_ids: item.mqtt_topic_ids || [],
      product_codes: item.product_codes || [],
      parameters: item.parameters || {},
      status: item.status || 'active',
    }
    paramList.value = parseParameters(item.parameters)
    // 加载筛选规则
    filterRules.value = (item.parameters?._filter_rules || []).map(r => ({ ...r }))
  } else {
    form.value = defaultForm()
    paramList.value = []
    filterRules.value = []
    fetchNextCode()
  }
  filterConditionMet.value = true
  loadDevices()
  loadTopics()
  loadProducts()
  if (form.value.mqtt_topic_ids && form.value.mqtt_topic_ids.length > 0) {
    onTopicsChange(form.value.mqtt_topic_ids)
  } else {
    discoveredFields.value = []
  }
  dialogVisible.value = true
}

function addParam() {
  paramList.value.push({ name: '', set_value: '', tolerance: '', unit: '' })
}

function removeParam(idx) {
  paramList.value.splice(idx, 1)
}

function addFilterRule() {
  filterRules.value.push({ field_path: '', operator: '==', value: '' })
}

async function saveItem() {
  if (!formRef.value) return
  const { valid } = await formRef.value.validate()
  if (!valid) return

  saving.value = true
  try {
    const newParams = buildParameters(paramList.value)
    const payload = {
      ...form.value,
      parameters: newParams,
    }

    console.log('保存工艺数据:', payload)

    if (editingItem.value) {
      await processDefinitionAPI.update(editingItem.value.id, payload)
      // 记录定义变更历史
      await recordDefinitionChanges(editingItem.value.id, editingItem.value.parameters || {}, newParams)
      showMsg('更新成功')
    } else {
      await processDefinitionAPI.create(payload)
      showMsg('创建成功')
    }
    dialogVisible.value = false
    loadData()
    loadStats()
  } catch (e) {
    console.error('保存失败:', e)
    const msg = e.response?.data?.detail || '操作失败'
    showMsg(msg, 'error')
  } finally {
    saving.value = false
  }
}

function confirmDelete(item) {
  deletingItem.value = item
  deleteDialog.value = true
}

async function deleteItem() {
  if (!deletingItem.value) return
  deleting.value = true
  try {
    await processDefinitionAPI.delete(deletingItem.value.id)
    showMsg('删除成功')
    deleteDialog.value = false
    loadData()
    loadStats()
  } catch (e) {
    const msg = e.response?.data?.detail || '删除失败'
    showMsg(msg, 'error')
  } finally {
    deleting.value = false
  }
}

function showMsg(text, color = 'success') {
  snackbarText.value = text
  snackbarColor.value = color
  snackbar.value = true
}

// 记录定义变更历史
async function recordDefinitionChanges(processId, oldParams, newParams) {
  const changes = []
  const oldKeys = Object.keys(oldParams).filter(k => k !== '_filter_rules')
  const newKeys = Object.keys(newParams).filter(k => k !== '_filter_rules')
  const allKeys = new Set([...oldKeys, ...newKeys])

  for (const key of allKeys) {
    const oldVal = oldParams[key] ? JSON.stringify(oldParams[key]) : null
    const newVal = newParams[key] ? JSON.stringify(newParams[key]) : null
    if (oldVal !== newVal) {
      changes.push({
        process_id: processId,
        change_type: 'definition_change',
        param_name: key,
        old_value: oldVal,
        new_value: newVal,
        source: 'manual',
      })
    }
  }
  if (changes.length > 0) {
    try {
      await processParamHistoryAPI.batchCreate({ items: changes })
    } catch (e) {
      console.error('记录定义变更历史失败:', e)
    }
  }
}

// 记录 MQTT 值变化历史
async function recordMqttValueChanges(changes) {
  if (!editingItem.value) return
  const items = changes.map(c => ({
    process_id: editingItem.value.id,
    change_type: 'mqtt_value_change',
    param_name: c.param_name,
    old_value: c.old_value != null ? String(c.old_value) : null,
    new_value: c.new_value != null ? String(c.new_value) : null,
    source: c.source || 'mqtt',
  }))
  try {
    await processParamHistoryAPI.batchCreate({ items })
  } catch (e) {
    console.error('记录 MQTT 值变化历史失败:', e)
  }
}

// 加载参数历史
async function loadHistory(page) {
  if (!viewItem_data.value) return
  historyPage.value = page
  historyLoading.value = true
  try {
    const params = { page, page_size: historyPageSize }
    if (historyChangeType.value) params.change_type = historyChangeType.value
    const res = await processParamHistoryAPI.list(viewItem_data.value.id, params)
    historyItems.value = res.data.items || []
    historyTotal.value = res.data.total || 0
  } catch (e) {
    console.error('加载参数历史失败:', e)
    historyItems.value = []
    historyTotal.value = 0
  } finally {
    historyLoading.value = false
  }
}

const historyHeaders = [
  { title: '时间', key: 'created_at', width: '150px' },
  { title: '类型', key: 'change_type', width: '90px' },
  { title: '参数名', key: 'param_name', width: '180px' },
  { title: '旧值', key: 'old_value', width: '120px' },
  { title: '新值', key: 'new_value', width: '120px' },
  { title: '来源', key: 'source', width: '100px' },
]

function hasVisibleParams(params) {
  if (!params) return false
  return Object.keys(params).filter(k => k !== '_filter_rules').length > 0
}

function truncateValue(val) {
  if (val == null) return '-'
  const s = String(val)
  return s.length > 30 ? s.slice(0, 30) + '...' : s
}

function formatTime(ts) {
  if (!ts) return '-'
  return new Date(ts).toLocaleString('zh-CN', { hour12: false })
}

onMounted(() => {
  loadData()
  loadStats()
})
</script>
