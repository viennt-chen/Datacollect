<template>
  <div>
    <!-- Action bar -->
    <v-toolbar flat color="transparent" class="mb-4">
      <div>
        <div class="text-h5 font-weight-bold d-flex align-center ga-2">
          <v-icon icon="mdi-cpu-64-bit" color="primary" />
          设备管理
        </div>
        <div class="text-caption text-medium-emphasis mt-1">
          首页 / 设备管理
        </div>
      </div>
      <v-spacer />
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openAddDialog">新增设备</v-btn>
      <v-btn variant="outlined" prepend-icon="mdi-upload" class="ml-2" @click="openImportDialog">导入设备</v-btn>
      <v-btn variant="outlined" prepend-icon="mdi-download" class="ml-2" @click="exportDevices">导出设备</v-btn>
    </v-toolbar>

    <!-- Tabs -->
    <v-tabs v-model="activeTab" class="mb-4">
      <v-tab value="overview">
        <v-icon start icon="mdi-view-dashboard" />
        设备总览
        <v-chip size="x-small" color="primary" class="ml-1">{{ deviceStats.total || 0 }}</v-chip>
      </v-tab>
    </v-tabs>

    <v-window v-model="activeTab">
      <v-window-item value="overview">
        <!-- Metric cards -->
        <v-row class="mb-4">
          <v-col cols="12" md="3">
            <v-card>
              <v-card-text class="d-flex align-center ga-4">
                <v-icon icon="mdi-cpu-64-bit" size="40" color="blue" />
                <div class="flex-grow-1">
                  <div class="text-h5 font-weight-bold">{{ deviceStats.total?.toLocaleString() || '0' }}</div>
                  <div class="text-caption text-medium-emphasis">设备总数</div>
                  <div class="text-caption">启用：{{ deviceStats.enabled || 0 }}</div>
                </div>
                <v-btn icon variant="text" size="small" @click="loadDevices">
                  <v-icon icon="mdi-refresh" />
                  <v-tooltip activator="parent" location="top">刷新</v-tooltip>
                </v-btn>
              </v-card-text>
              <v-divider />
              <v-card-actions class="text-caption text-medium-emphasis px-4">
                运行中：{{ deviceStats.active || 0 }}
              </v-card-actions>
            </v-card>
          </v-col>
          <v-col cols="12" md="3">
            <v-card>
              <v-card-text class="d-flex align-center ga-4">
                <v-icon icon="mdi-check-circle" size="40" color="green" />
                <div>
                  <div class="text-h5 font-weight-bold">{{ deviceStats.active || '0' }}</div>
                  <div class="text-caption text-medium-emphasis">运行中</div>
                  <div class="text-caption text-success"><v-icon icon="mdi-arrow-up" size="x-small" /> 正常运行</div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="3">
            <v-card>
              <v-card-text class="d-flex align-center ga-4">
                <v-icon icon="mdi-wrench" size="40" color="orange" />
                <div>
                  <div class="text-h5 font-weight-bold">{{ deviceStats.maintenance || '0' }}</div>
                  <div class="text-caption text-medium-emphasis">维护中</div>
                  <div class="text-caption text-warning"><v-icon icon="mdi-alert" size="x-small" /> 需要关注</div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="3">
            <v-card>
              <v-card-text class="d-flex align-center ga-4">
                <v-icon icon="mdi-close-circle" size="40" color="red" />
                <div>
                  <div class="text-h5 font-weight-bold">{{ deviceStats.inactive || '0' }}</div>
                  <div class="text-caption text-medium-emphasis">已停用</div>
                  <div class="text-caption text-error"><v-icon icon="mdi-arrow-down" size="x-small" /> 停止使用</div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Search and filters -->
        <v-card class="mb-4">
          <v-card-text>
            <v-row dense align="center">
              <v-col cols="12" md="2">
                <v-text-field v-model="searchQuery.device_code" label="设备编号" placeholder="搜索设备编号..." density="compact" clearable hide-details @keyup.enter="loadDevices" />
              </v-col>
              <v-col cols="12" md="2">
                <v-text-field v-model="searchQuery.device_name" label="设备名称" placeholder="搜索设备名称..." density="compact" clearable hide-details @keyup.enter="loadDevices" />
              </v-col>
              <v-col cols="12" md="2">
                <v-select v-model="searchQuery.status" :items="statusFilterOptions" label="状态" density="compact" clearable hide-details @update:modelValue="loadDevices" />
              </v-col>
              <v-col cols="12" md="2">
                <v-select v-model="searchQuery.device_type" :items="[{title:'全部类型',value:''},{title:'CNC',value:'CNC'},{title:'机器人',value:'Robot'},{title:'PLC',value:'PLC'},{title:'传感器',value:'Sensor'}]" label="类型" density="compact" clearable hide-details @update:modelValue="loadDevices" />
              </v-col>
              <v-col cols="12" md="4" class="d-flex justify-end ga-2">
                <template v-if="selectedDeviceCodes.length > 0">
                  <v-btn size="small" color="primary" prepend-icon="mdi-eye" @click="batchToggleDashboard(true)">
                    批量显示到看板 ({{ selectedDeviceCodes.length }})
                  </v-btn>
                  <v-btn size="small" variant="outlined" prepend-icon="mdi-eye-off" @click="batchToggleDashboard(false)">
                    批量隐藏
                  </v-btn>
                </template>
                <v-btn size="small" variant="outlined" prepend-icon="mdi-undo" @click="resetSearch">重置</v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Device table -->
        <v-card>
          <v-card-title class="d-flex align-center ga-2">
            <v-icon icon="mdi-format-list-bulleted" />
            设备列表
            <v-spacer />
            <v-btn variant="outlined" prepend-icon="mdi-refresh" size="small" @click="loadDevices">刷新</v-btn>
          </v-card-title>
          <v-data-table
            :headers="deviceHeaders"
            :items="deviceList"
            :loading="loading"
            :items-per-page="pageSize"
            :page="page"
            :server-items-length="total"
            :show-select="true"
            v-model:selected="selectedDeviceCodes"
            item-value="device_code"
            @update:page="p => { page = p; loadDevices() }"
            @update:items-per-page="s => { pageSize = s; loadDevices() }"
            hover
          >
            <template v-slot:item.device_code="{ item }">
              <v-chip size="small" variant="tonal" color="primary">{{ item.device_code }}</v-chip>
            </template>
            <template v-slot:item.device_type="{ item }">
              <v-chip size="small" variant="tonal">{{ item.device_type || '-' }}</v-chip>
            </template>
            <template v-slot:item.mqtt_topics="{ item }">
              <v-chip v-if="item.mqtt_topics && item.mqtt_topics.length > 0" size="small" variant="tonal" color="info">
                {{ item.mqtt_topics.length }} 个 Topic
              </v-chip>
              <span v-else class="text-medium-emphasis">-</span>
            </template>
            <template v-slot:item.status="{ item }">
              <template v-if="item.status">
                <v-chip v-for="(part, pi) in item.status.split(',')" :key="pi" size="x-small" variant="tonal" :color="getStatusColor(part)" class="mr-1">
                  {{ getStatusTextForPart(part) }}
                </v-chip>
              </template>
              <v-chip v-else size="x-small" variant="tonal" color="grey">未知</v-chip>
            </template>
            <template v-slot:item.updated_at="{ item }">
              {{ formatDateTime(item.updated_at) }}
            </template>
            <template v-slot:item.show_on_dashboard="{ item }">
              <v-switch :model-value="item.show_on_dashboard" @update:modelValue="toggleDashboardShow(item)" density="compact" hide-details color="primary" />
            </template>
            <template v-slot:item.actions="{ item }">
              <div class="d-flex ga-1">
                <v-btn icon variant="text" size="small" color="info" @click="navigateToDataCollection(item)">
                  <v-icon icon="mdi-harddisk" size="small" />
                  <v-tooltip activator="parent" location="top">数据采集</v-tooltip>
                </v-btn>
                <v-btn icon variant="text" size="small" @click="editDevice(item)">
                  <v-icon icon="mdi-pencil" size="small" />
                  <v-tooltip activator="parent" location="top">编辑</v-tooltip>
                </v-btn>
                <v-btn icon variant="text" size="small" color="purple" @click="viewDeviceEvents(item)">
                  <v-icon icon="mdi-cog-transfer" size="small" />
                  <v-tooltip activator="parent" location="top">加工事件</v-tooltip>
                </v-btn>
                <v-btn icon variant="text" size="small" color="error" @click="deleteDevice(item)">
                  <v-icon icon="mdi-delete" size="small" />
                  <v-tooltip activator="parent" location="top">删除</v-tooltip>
                </v-btn>
              </div>
            </template>
            <template v-slot:no-data>
              <div class="text-center pa-8">
                <v-icon icon="mdi-inbox" size="48" color="grey-lighten-1" />
                <p class="text-medium-emphasis mt-2">暂无设备数据</p>
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-window-item>
    </v-window>

    <!-- Add/Edit device dialog -->
    <v-dialog v-model="dialogVisible" max-width="700" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon :icon="isEdit ? 'mdi-pencil' : 'mdi-plus'" class="mr-2" />
          {{ isEdit ? '编辑设备' : '新增设备' }}
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="dialogVisible = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-form ref="formRef">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field v-model="formData.device_code" label="设备编号" :disabled="isEdit" placeholder="请输入设备编号" :rules="[v => !!v || '请输入设备编号']" required />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="formData.device_name" label="设备名称" placeholder="请输入设备名称" :rules="[v => !!v || '请输入设备名称']" required />
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" md="6">
                <v-select v-model="formData.device_type" :items="[{title:'CNC',value:'CNC'},{title:'机器人',value:'Robot'},{title:'PLC',value:'PLC'},{title:'传感器',value:'Sensor'},{title:'其他',value:'Other'}]" label="设备类型" placeholder="请选择设备类型" />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="formData.model" label="设备型号" placeholder="请输入设备型号" />
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field v-model="formData.manufacturer" label="制造商" placeholder="请输入制造商" />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="formData.ip_address" label="IP 地址" placeholder="请输入 IP 地址" />
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field v-model="formData.line_code" label="所属产线" placeholder="请输入产线编号" />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="formData.factory_code" label="所属工厂" placeholder="请输入工厂编号" />
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field v-model="formData.group_code" label="所属集团" placeholder="请输入集团编号" />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model="formData.location" label="安装位置" placeholder="请输入安装位置" />
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" md="6">
                <div class="d-flex align-center ga-2">
                  <span class="text-caption text-medium-emphasis">设备状态</span>
                  <v-tooltip text="设备状态由匹配规则自动更新，不可手动设置">
                    <template v-slot:activator="{ props }">
                      <v-icon v-bind="props" icon="mdi-help-circle" size="small" color="grey" />
                    </template>
                  </v-tooltip>
                </div>
                <v-chip variant="tonal" color="info" prepend-icon="mdi-lock">由规则自动匹配</v-chip>
              </v-col>
              <v-col cols="12" md="6">
                <v-switch v-model="formData.is_enabled" label="是否启用" color="primary" />
              </v-col>
            </v-row>
            <v-textarea v-model="formData.description" label="设备描述" rows="3" placeholder="请输入设备描述" />
            <v-select v-model="formData.mqtt_topics" :items="availableTopics" label="关联 Topic" multiple chips closable-chips placeholder="请选择或输入 MQTT Topic" />
            <div class="text-caption text-medium-emphasis">可选择已有 Topic 或手动输入，支持多个 Topic</div>
          </v-form>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dialogVisible = false">取消</v-btn>
          <v-btn color="primary" :loading="submitting" @click="submitForm">
            {{ isEdit ? '保存' : '创建' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Data collection dialog -->
    <v-dialog v-model="dataCollectionDialogVisible" fullscreen :scrim="false" transition="dialog-bottom-transition">
      <v-card>
        <v-toolbar color="primary">
          <v-btn icon="mdi-close" @click="dataCollectionDialogVisible = false" />
          <v-toolbar-title>数据采集 - {{ currentDevice.device_name || currentDevice.device_code }}</v-toolbar-title>
          <v-spacer />
          <v-toolbar-items>
            <v-btn variant="text" @click="dataCollectionDialogVisible = false">关闭</v-btn>
          </v-toolbar-items>
        </v-toolbar>
        <v-card-text>
          <!-- Device info -->
          <v-card variant="outlined" class="mb-4">
            <v-card-text>
              <v-row>
                <v-col cols="3"><div class="text-caption text-medium-emphasis">设备编号</div><div>{{ currentDevice.device_code }}</div></v-col>
                <v-col cols="3"><div class="text-caption text-medium-emphasis">设备名称</div><div>{{ currentDevice.device_name }}</div></v-col>
                <v-col cols="3"><div class="text-caption text-medium-emphasis">设备类型</div><div>{{ currentDevice.device_type || '-' }}</div></v-col>
                <v-col cols="3">
                  <div class="text-caption text-medium-emphasis">设备状态</div>
                  <div>
                    <template v-if="currentDevice.status">
                      <v-chip v-for="(part, pi) in currentDevice.status.split(',')" :key="pi" size="x-small" variant="tonal" :color="getStatusColor(part)" class="mr-1">
                        {{ getStatusTextForPart(part) }}
                      </v-chip>
                    </template>
                    <v-chip v-else size="x-small" variant="tonal" color="grey">未知</v-chip>
                  </div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- Device status rules -->
          <v-card variant="outlined" class="mb-4" :loading="statusLoading">
            <v-card-title class="d-flex align-center ga-2">
              <v-icon icon="mdi-pulse" />
              设备状态规则
              <v-chip :color="statusLoading ? 'warning' : 'success'" size="small" variant="tonal">
                <v-icon start :icon="statusLoading ? 'mdi-loading' : 'mdi-lan-connect'" size="x-small" />
                {{ statusLoading ? '连接中...' : '已连接' }}
              </v-chip>
              <span v-if="lastStatusUpdateTime" class="text-caption text-medium-emphasis">
                <v-icon icon="mdi-clock" size="x-small" /> 最后更新: {{ lastStatusUpdateTime }}
              </span>
              <v-spacer />
              <v-btn variant="outlined" prepend-icon="mdi-cog" size="small" @click="openStatusMonitorConfig">配置</v-btn>
              <v-btn icon variant="text" size="small" :loading="statusLoading" @click="loadDeviceStatus">
                <v-icon icon="mdi-refresh" />
              </v-btn>
            </v-card-title>
            <v-divider />
            <v-card-text>
              <v-alert v-if="hasStatusErrors" type="warning" density="compact" class="mb-4">
                <div v-for="(error, index) in statusErrors" :key="index">{{ error }}</div>
              </v-alert>

              <v-row>
                <v-col v-for="statusItem in statusItems" :key="statusItem.key" cols="6" sm="4" md="3">
                  <v-card :color="deviceStatus[statusItem.key] ? getStatusCardColor(statusItem.key) : undefined" variant="tonal" class="cursor-pointer" @click="showStatusDetail(statusItem.key)">
                    <v-card-text class="text-center pa-3">
                      <v-icon :icon="statusItem.mdiIcon" :color="deviceStatus[statusItem.key] ? 'white' : 'grey'" size="24" />
                      <div class="text-caption mt-1">{{ statusItem.label }}</div>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- Current processing product -->
          <v-card variant="outlined" class="mb-4">
            <v-card-title class="d-flex align-center ga-2">
              <v-icon icon="mdi-package-variant" />
              当前加工产品
              <v-btn variant="outlined" prepend-icon="mdi-cog" size="small" class="ml-2" @click="openCurrentProductConfig">配置</v-btn>
              <v-spacer />
              <v-chip v-if="currentPart.part_number" size="small" color="primary" variant="tonal">{{ currentPart.part_number }}</v-chip>
              <v-chip v-else size="small" color="grey" variant="tonal">无加工产品</v-chip>
            </v-card-title>
            <v-divider />
            <v-card-text>
              <template v-if="currentPart.part_number">
                <v-row>
                  <v-col cols="3"><div class="text-caption text-medium-emphasis">零件号</div><div class="font-weight-bold text-primary">{{ currentPart.part_number }}</div></v-col>
                  <v-col cols="3"><div class="text-caption text-medium-emphasis">U9物料号</div><div>{{ currentPart.u9_material_code || '-' }}</div></v-col>
                  <v-col cols="3"><div class="text-caption text-medium-emphasis">启动码</div><div>{{ currentPart.start_code || '-' }}</div></v-col>
                  <v-col cols="3"><div class="text-caption text-medium-emphasis">计划产量</div><div>{{ currentPart.order_info?.planned_output || 0 }}</div></v-col>
                </v-row>
                <!-- Order details -->
                <div v-if="currentPart.order_info && currentPart.order_info.details.length > 0" class="mt-4">
                  <div class="text-subtitle-2 mb-2"><v-icon icon="mdi-format-list-checks" size="small" /> U9订单信息 ({{ currentPart.order_info.order_count }}个订单)</div>
                  <v-table density="compact">
                    <thead>
                      <tr>
                        <th>订单号</th><th>物料代码</th><th>订单数量</th><th>完成数量</th><th>订单状态</th><th>模具编号</th><th>产线</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(detail, index) in currentPart.order_info.details" :key="index">
                        <td>{{ detail.doc_no }}</td>
                        <td>{{ detail.item_code }}</td>
                        <td>{{ detail.product_qty }}</td>
                        <td>{{ detail.total_complete_qty }}</td>
                        <td><v-chip size="x-small" variant="tonal" :color="getOrderStatusColor(detail.doc_state)">{{ getOrderStatusText(detail.doc_state) }}</v-chip></td>
                        <td>{{ detail.mold_no || '-' }}</td>
                        <td>{{ detail.line_code || '-' }}</td>
                      </tr>
                    </tbody>
                  </v-table>
                </div>
              </template>
              <v-alert v-else type="info" density="compact" variant="tonal">
                设备当前未加工产品，请检查MQTT event消息是否正常接收
              </v-alert>
            </v-card-text>
          </v-card>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Current product config dialog -->
    <v-dialog v-model="currentProductConfigDialogVisible" max-width="1200" persistent>
      <v-card :loading="configLoading">
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-cog" class="mr-2" />
          当前加工产品配置 - {{ currentDevice.device_name || currentDevice.device_code }}
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="currentProductConfigDialogVisible = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <!-- Config info -->
          <v-alert type="info" density="compact" variant="tonal" class="mb-4">
            配置从哪个MQTT Topic和字段获取当前加工产品的零件号信息。系统会按优先级依次尝试匹配，找到第一个有效值。
          </v-alert>

          <!-- Config stats -->
          <v-row class="mb-4">
            <v-col cols="4"><v-card variant="tonal"><v-card-text class="text-center"><div class="text-h5">{{ productConfigs.length }}</div><div class="text-caption">规则总数</div></v-card-text></v-card></v-col>
            <v-col cols="4"><v-card variant="tonal" color="success"><v-card-text class="text-center"><div class="text-h5">{{ productConfigs.filter(c => c.enabled).length }}</div><div class="text-caption">启用中</div></v-card-text></v-card></v-col>
            <v-col cols="4"><v-card variant="tonal" color="grey"><v-card-text class="text-center"><div class="text-h5">{{ productConfigs.filter(c => !c.enabled).length }}</div><div class="text-caption">已禁用</div></v-card-text></v-card></v-col>
          </v-row>

          <!-- Rules list -->
          <div class="d-flex align-center mb-2">
            <div class="text-subtitle-1"><v-icon icon="mdi-format-list-checks" /> 已配置规则</div>
            <v-spacer />
            <v-btn color="primary" prepend-icon="mdi-plus" size="small" @click="showAddProductRuleForm = true">添加规则</v-btn>
          </div>

          <div v-if="productConfigs.length === 0" class="text-center pa-8 text-medium-emphasis">
            <v-icon icon="mdi-inbox" size="48" color="grey-lighten-1" />
            <p>暂无配置规则，点击上方按钮添加</p>
          </div>

          <v-card v-for="(config, index) in productConfigs" :key="config.id || index" variant="outlined" class="mb-2">
            <v-card-text class="d-flex align-center">
              <div class="flex-grow-1">
                <div class="d-flex align-center ga-2">
                  <v-icon icon="mdi-broadcast" size="small" />
                  <span class="text-caption text-medium-emphasis">Topic:</span>
                  <span class="font-weight-bold">{{ config.topic_name }}</span>
                </div>
                <div class="d-flex align-center ga-2 mt-1">
                  <v-icon icon="mdi-code-braces" size="small" />
                  <span class="text-caption text-medium-emphasis">字段:</span>
                  <span>{{ config.field_path }}</span>
                </div>
                <div v-if="config.field_description" class="text-caption text-medium-emphasis mt-1">
                  <v-icon icon="mdi-tag" size="x-small" /> {{ config.field_description }}
                </div>
                <div class="text-caption text-medium-emphasis mt-1">
                  优先级: {{ config.priority }}
                </div>
              </div>
              <v-switch v-model="config.enabled" @update:modelValue="toggleProductConfig(config)" density="compact" hide-details color="primary" />
              <v-btn icon variant="text" size="small" @click="editProductConfig(config)"><v-icon icon="mdi-pencil" size="small" /></v-btn>
              <v-btn icon variant="text" size="small" color="error" @click="deleteProductConfig(config)"><v-icon icon="mdi-delete" size="small" /></v-btn>
            </v-card-text>
          </v-card>

          <!-- Add rule form -->
          <v-card v-if="showAddProductRuleForm" variant="outlined" class="mt-4">
            <v-card-title class="d-flex align-center">
              <v-icon :icon="editingProductConfigId ? 'mdi-pencil' : 'mdi-plus'" class="mr-2" />
              {{ editingProductConfigId ? '编辑规则' : '添加新规则' }}
              <v-spacer />
              <v-btn icon="mdi-close" variant="text" size="small" @click="cancelAddProductRule" />
            </v-card-title>
            <v-divider />
            <v-card-text>
              <v-select v-model="newProductRule.topic_name" :items="statusMonitorTopics.map(t => ({title: `${t.topic_name} (${t.topic_type})`, value: t.topic_name}))" label="选择Topic" @update:modelValue="onProductTopicChange" />
              <v-select v-if="currentTopicFields.length > 0" v-model="newProductRule.field_path" :items="currentTopicFields.map(f => ({title: `${f.field_path} (${f.field_type})`, value: f.field_path}))" label="选择字段" />
              <v-text-field v-else-if="newProductRule.topic_name" v-model="newProductRule.field_path" label="字段路径" placeholder="手动输入字段路径，如：payload.start_code" hint="该Topic暂无可用字段，请手动输入字段路径" persistent-hint />
              <v-text-field v-model="newProductRule.field_description" label="字段说明（可选）" placeholder="例如：start_code, part_number" />
              <v-number-input v-model.number="newProductRule.priority" label="优先级" :min="0" controlVariant="stacked" hint="数字越小优先级越高" persistent-hint />
              <v-textarea v-model="newProductRule.description" label="备注说明" rows="2" placeholder="输入备注说明" />
            </v-card-text>
            <v-divider />
            <v-card-actions>
              <v-spacer />
              <v-btn variant="text" @click="cancelAddProductRule">取消</v-btn>
              <v-btn color="primary" :disabled="!isProductRuleFormValid" @click="saveProductRule">
                {{ editingProductConfigId ? '更新' : '保存' }}
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="currentProductConfigDialogVisible = false">关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Status monitor config dialog -->
    <v-dialog v-model="statusMonitorConfigDialogVisible" max-width="1200" persistent>
      <v-card :loading="configLoading">
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-cog" class="mr-2" />
          状态规则配置 - {{ currentDevice.device_name || currentDevice.device_code }}
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="statusMonitorConfigDialogVisible = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <p class="text-medium-emphasis mb-4">为每个状态类型配置MQTT数据源和匹配规则。点击状态卡片查看可选择的Topic和字段。</p>

          <!-- Status type selector -->
          <v-row class="mb-4">
            <v-col v-for="statusType in statusTypeOptions" :key="statusType.value" cols="6" sm="4" md="3">
              <v-card :color="selectedStatusType === statusType.value ? 'primary' : undefined" :variant="selectedStatusType === statusType.value ? 'tonal' : 'outlined'" class="cursor-pointer" @click="selectedStatusType = statusType.value">
                <v-card-text class="text-center pa-3">
                  <v-icon :icon="statusType.mdiIcon" :color="selectedStatusType === statusType.value ? 'primary' : 'grey'" size="24" />
                  <div class="text-caption mt-1">{{ statusType.label }}</div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <v-alert v-if="!selectedStatusType" type="info" density="compact" variant="tonal">
            请先点击上方状态类型卡片，查看和配置该状态的匹配规则
          </v-alert>

          <!-- Config form section -->
          <div v-if="selectedStatusType">
            <h3 class="text-subtitle-1 mb-2">{{ getStatusTypeLabel(selectedStatusType) }} - 匹配规则配置</h3>
            <v-alert type="info" density="compact" variant="tonal" class="mb-4">
              数据源：从设备关联的MQTT Topic实时读取数据，按规则匹配设备状态
            </v-alert>

            <!-- Configured rules -->
            <div class="text-subtitle-2 mb-2">已配置规则</div>
            <div v-if="currentConfigs.length === 0" class="text-center pa-4 text-medium-emphasis">
              <v-icon icon="mdi-inbox" size="36" color="grey-lighten-1" />
              <p>暂无配置规则，点击下方按钮添加</p>
            </div>
            <v-card v-for="(config, index) in currentConfigs" :key="config.id || index" variant="outlined" class="mb-2">
              <v-card-text class="d-flex align-center">
                <div class="flex-grow-1">
                  <template v-if="config.conditions && config.conditions.length > 0">
                    <div v-for="(cond, ci) in config.conditions.slice(0, 3)" :key="ci" class="d-flex align-center ga-1 mb-1">
                      <v-icon icon="mdi-broadcast" size="x-small" />
                      <span class="font-weight-bold">{{ cond.topic_name }}</span>
                      <v-icon icon="mdi-arrow-right" size="x-small" color="grey" />
                      <span>{{ cond.field_path }}</span>
                      <v-chip size="x-small" variant="tonal">{{ getMatchRuleLabel(cond.match_rule) }}{{ cond.match_value ? ': ' + cond.match_value : '' }}</v-chip>
                    </div>
                    <div v-if="config.conditions.length > 3" class="text-caption text-medium-emphasis">+{{ config.conditions.length - 3 }} 个参数点</div>
                    <v-chip size="x-small" variant="tonal" color="info" class="mt-1">{{ config.logic_operator || 'AND' }}</v-chip>
                  </template>
                  <template v-else>
                    <div class="d-flex align-center ga-1">
                      <v-icon icon="mdi-broadcast" size="x-small" />
                      <span class="font-weight-bold">{{ config.topic_name || '-' }}</span>
                      <v-icon icon="mdi-arrow-right" size="x-small" color="grey" />
                      <span>{{ config.field_path || '-' }}</span>
                      <v-chip size="x-small" variant="tonal">{{ getMatchRuleLabel(config.match_rule) }}{{ config.match_value ? ': ' + config.match_value : '' }}</v-chip>
                    </div>
                  </template>
                  <div v-if="config.device_status" class="text-caption text-medium-emphasis mt-1">
                    设备状态: {{ getStatusText(config.device_status) }}
                  </div>
                </div>
                <v-switch v-model="config.enabled" @update:modelValue="toggleConfigEnabled(config)" density="compact" hide-details color="primary" />
                <v-btn icon variant="text" size="small" @click="editConfig(config)"><v-icon icon="mdi-pencil" size="small" /></v-btn>
                <v-btn icon variant="text" size="small" color="error" @click="deleteConfig(config)"><v-icon icon="mdi-delete" size="small" /></v-btn>
              </v-card-text>
            </v-card>

            <v-btn color="primary" prepend-icon="mdi-plus" class="mt-2" @click="showAddRuleForm = true; addParameterPoint(); loadCurves()">
              添加匹配规则
            </v-btn>

            <!-- Add rule form -->
            <v-card v-if="showAddRuleForm" variant="outlined" class="mt-4">
              <v-card-title class="d-flex align-center">
                <span>{{ editingConfigId ? '编辑匹配规则' : '添加匹配规则' }}</span>
                <v-spacer />
                <v-btn variant="text" size="small" @click="showRuleHelp = !showRuleHelp">
                  {{ showRuleHelp ? '收起帮助' : '规则帮助' }}
                </v-btn>
              </v-card-title>
              <v-divider />
              <v-card-text>
                <!-- Rule help -->
                <v-alert v-if="showRuleHelp" type="info" density="compact" variant="tonal" class="mb-4">
                  <div class="text-subtitle-2 mb-2">匹配规则说明</div>
                  <v-table density="compact">
                    <thead><tr><th>规则</th><th>说明</th><th>示例</th></tr></thead>
                    <tbody>
                      <tr><td><v-chip size="x-small">等于</v-chip></td><td>字段值等于指定值</td><td><code>1</code> 或 <code>"OK"</code></td></tr>
                      <tr><td><v-chip size="x-small">不等于</v-chip></td><td>字段值不等于指定值</td><td><code>0</code> 或 <code>"NG"</code></td></tr>
                      <tr><td><v-chip size="x-small">包含</v-chip></td><td>字段值包含指定字符串</td><td><code>error</code></td></tr>
                      <tr><td><v-chip size="x-small">大于/小于</v-chip></td><td>数值比较</td><td><code>100</code></td></tr>
                      <tr><td><v-chip size="x-small">在范围内</v-chip></td><td>数值在指定区间内</td><td><code>350-353</code></td></tr>
                      <tr><td><v-chip size="x-small">正则匹配</v-chip></td><td>匹配正则表达式</td><td><code>^ERR\d+$</code></td></tr>
                      <tr><td><v-chip size="x-small">为true/false</v-chip></td><td>布尔值判断</td><td>-</td></tr>
                      <tr><td><v-chip size="x-small">为空/不为空</v-chip></td><td>空值判断</td><td>-</td></tr>
                    </tbody>
                  </v-table>
                </v-alert>

                <!-- Parameter points -->
                <div class="text-subtitle-2 mb-2">参数点配置</div>
                <v-card v-for="(point, index) in newRule.parameter_points" :key="index" variant="outlined" class="mb-3">
                  <v-card-title class="d-flex align-center text-subtitle-2">
                    参数点 {{ index + 1 }}
                    <v-spacer />
                    <v-btn v-if="newRule.parameter_points.length > 1" icon="mdi-close-circle" variant="text" size="small" color="error" @click="removeParameterPoint(index)" />
                  </v-card-title>
                  <v-divider />
                  <v-card-text>
                    <v-row>
                      <v-col cols="12" md="4">
                        <v-select v-model="point.topic_name" :items="statusMonitorTopics.map(t => ({title: t.topic_name, value: t.topic_name}))" label="Topic" @update:modelValue="onPointTopicChange(point)" />
                      </v-col>
                      <v-col cols="12" md="4">
                        <v-select v-model="point.field_path" :items="(point.fields || []).map(f => ({title: f.field_path, value: f.field_path}))" label="字段路径" :disabled="!point.topic_name" @update:modelValue="onPointFieldChange(point)" />
                      </v-col>
                      <v-col cols="12" md="4" v-if="point.field_value_preview">
                        <div class="text-caption text-medium-emphasis">当前值</div>
                        <v-chip variant="tonal" color="info">{{ point.field_value_preview }}</v-chip>
                      </v-col>
                    </v-row>
                    <v-row>
                      <v-col cols="12" md="4">
                        <v-select v-model="point.match_rule" :items="matchRuleOptions.map(r => ({title: r.label, value: r.value}))" label="匹配规则" />
                      </v-col>
                      <v-col cols="12" md="4" v-if="pointNeedsValue(point)">
                        <v-text-field v-model="point.match_value" :label="'匹配值'" :placeholder="getMatchRulePlaceholder(point.match_rule)" @blur="formatMatchValue(point)" />
                        <div v-if="getMatchRuleExample(point.match_rule)" class="text-caption text-medium-emphasis">
                          <v-icon icon="mdi-lightbulb" size="x-small" /> 示例：{{ getMatchRuleExample(point.match_rule) }}
                        </div>
                      </v-col>
                      <v-col cols="12" md="4">
                        <v-select v-model="point.curve_id" :items="[{title:'不绑定',value:null},...availableCurves.map(c => ({title: c.curve_name || '曲线 ' + c.id, value: c.id}))]" label="曲线绑定（可选）" @update:modelValue="loadBoundCurve(point, index)" />
                      </v-col>
                    </v-row>

                    <!-- Curve section -->
                    <div v-if="point.topic_name && point.field_path" class="mt-2">
                      <div class="d-flex ga-2 mb-2 flex-wrap">
                        <v-btn size="small" color="primary" prepend-icon="mdi-play" :disabled="point.curveCollecting" @click="startCurveCollect(point, index)">开始采集</v-btn>
                        <v-btn size="small" variant="outlined" prepend-icon="mdi-stop" :disabled="!point.curveCollecting" @click="stopCurveCollect(point)">停止</v-btn>
                        <v-btn size="small" variant="outlined" prepend-icon="mdi-content-cut" :disabled="point.curveData.length === 0" @click="extractCurveRange(point, index)">截取</v-btn>
                        <v-btn size="small" variant="outlined" prepend-icon="mdi-content-save" :disabled="point.curveData.length === 0" @click="openSaveCurveDialog(point, index)">保存曲线</v-btn>
                        <v-btn size="small" variant="outlined" prepend-icon="mdi-delete" :disabled="point.curveData.length === 0" @click="clearCurveData(point, index)">清空</v-btn>
                        <v-chip v-if="point.curveData.length > 0" size="small" variant="tonal" color="info">已采集 {{ point.curveData.length }} 个点</v-chip>
                      </div>
                      <div :ref="el => setCurveChartRef(el, index)" style="height: 300px;" />
                    </div>

                    <!-- Field tree -->
                    <div v-if="point.topic_name && point.fields && point.fields.length > 0" class="mt-2">
                      <v-btn variant="text" size="small" @click="point.showTree = !point.showTree">
                        {{ point.showTree ? '收起字段列表' : '查看字段列表' }}
                      </v-btn>
                      <v-list v-if="point.showTree" density="compact" class="mt-1">
                        <v-list-item v-for="field in point.fields" :key="field.field_path" @click="point.field_path = field.field_path; point.field_value_preview = String(field.field_value); point.showTree = false" :active="point.field_path === field.field_path">
                          <v-list-item-title>{{ field.field_path }}</v-list-item-title>
                          <v-list-item-subtitle>{{ field.field_value }} ({{ field.field_type }})</v-list-item-subtitle>
                        </v-list-item>
                      </v-list>
                    </div>
                  </v-card-text>
                </v-card>

                <v-btn variant="outlined" prepend-icon="mdi-plus" @click="addParameterPoint" class="mb-4">添加参数点</v-btn>

                <!-- Global config -->
                <v-card variant="outlined">
                  <v-card-text>
                    <v-row>
                      <v-col v-if="newRule.parameter_points.length > 1" cols="12" md="4">
                        <div class="text-caption mb-2">参数点逻辑</div>
                        <v-btn-toggle v-model="newRule.logic_operator" mandatory>
                          <v-btn value="AND" size="small">AND (全部满足)</v-btn>
                          <v-btn value="OR" size="small">OR (任一满足)</v-btn>
                        </v-btn-toggle>
                      </v-col>
                      <v-col cols="12" md="4">
                        <v-number-input v-model.number="newRule.priority" label="优先级" :min="0" controlVariant="stacked" />
                      </v-col>
                      <v-col cols="12" md="4">
                        <v-select v-model="newRule.device_status" :items="deviceStatusOptions" label="匹配后设备状态" />
                      </v-col>
                    </v-row>
                    <v-textarea v-model="newRule.description" label="备注说明" rows="2" placeholder="输入备注说明" />
                  </v-card-text>
                </v-card>
              </v-card-text>
              <v-divider />
              <v-card-actions>
                <v-spacer />
                <v-btn variant="text" @click="cancelAddRule">取消</v-btn>
                <v-btn color="primary" :disabled="!isRuleFormValid" @click="saveNewRule">保存</v-btn>
              </v-card-actions>
            </v-card>
          </div>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="statusMonitorConfigDialogVisible = false">关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Import dialog -->
    <v-dialog v-model="importDialogVisible" max-width="600" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-upload" class="mr-2" />
          导入设备
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="importDialogVisible = false" />
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
            <p class="text-caption text-medium-emphasis">按照模板格式填写设备数据</p>
          </div>
          <div>
            <div class="text-subtitle-2 mb-1">3. 上传文件</div>
            <p class="text-caption text-medium-emphasis mb-2">选择填写好的 Excel 文件上传</p>
            <v-file-input v-model="importFile" label="选择文件" accept=".xlsx,.csv" density="compact" show-size prepend-icon="mdi-paperclip" />
          </div>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="importDialogVisible = false">取消</v-btn>
          <v-btn color="primary" :loading="uploading" :disabled="!importFile" @click="uploadImportFile">
            {{ uploading ? '上传中...' : '开始导入' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Save curve dialog -->
    <v-dialog v-model="saveCurveDialogVisible" max-width="600" persistent>
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-content-save" class="mr-2" />
          保存曲线
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="saveCurveDialogVisible = false" />
        </v-card-title>
        <v-divider />
        <v-card-text>
          <v-text-field v-model="saveCurveForm.curve_name" label="曲线名称" placeholder="如：主轴速度曲线-产品A" required />
          <v-text-field :model-value="saveCurveForm.device_code" label="设备编号" disabled />
          <v-text-field v-model="saveCurveForm.servo_axis" label="伺服轴/Topic" placeholder="Topic名称" />
          <v-text-field v-model="saveCurveForm.part_number" label="产品零件号" placeholder="可选" />
          <v-row>
            <v-col cols="6">
              <v-number-input v-model.number="saveCurveForm.value_tolerance" label="值容差" :min="0" :step="0.1" controlVariant="stacked" />
            </v-col>
            <v-col cols="6">
              <v-number-input v-model.number="saveCurveForm.time_tolerance_ms" label="时间容差(ms)" :min="0" controlVariant="stacked" />
            </v-col>
          </v-row>
          <v-text-field v-model="saveCurveForm.description" label="备注说明" placeholder="可选" />
          <div class="text-caption text-medium-emphasis">
            数据点: {{ saveCurveForm.curve_data.length }} 个
            <span v-if="saveCurveForm.total_duration_ms"> | 时长: {{ (saveCurveForm.total_duration_ms / 1000).toFixed(1) }}s</span>
          </div>
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="saveCurveDialogVisible = false">取消</v-btn>
          <v-btn color="primary" :loading="savingCurve" :disabled="!saveCurveForm.curve_name" @click="saveCurve">
            {{ savingCurve ? '保存中...' : '保存' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 加工事件对话框 -->
    <v-dialog v-model="deviceEventsDialog" max-width="1000px" scrollable>
      <v-card style="display: flex; flex-direction: column; height: 70vh;">
        <v-card-title class="d-flex align-center flex-shrink-0">
          <v-icon icon="mdi-cog-transfer" class="mr-2" />
          {{ deviceEventsDevice?.device_name }} - 关联加工事件
          <v-chip size="small" class="ml-2" color="warning">{{ deviceEventsDevice?.device_code }}</v-chip>
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" @click="deviceEventsDialog = false" />
        </v-card-title>
        <v-divider class="flex-shrink-0" />
        <v-card-text style="flex: 1; overflow-y: auto;">
          <div v-if="deviceEventsLoading" class="text-center pa-8">
            <v-progress-circular indeterminate color="primary" />
          </div>
          <div v-else-if="deviceEventsData.length > 0">
            <v-table density="compact">
              <thead>
                <tr>
                  <th>事件 UID</th>
                  <th>启动码</th>
                  <th>开始时间</th>
                  <th>加工时长</th>
                  <th>操作员</th>
                  <th>工站编号</th>
                  <th>产线</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="e in deviceEventsData" :key="e.id">
                  <td class="text-caption">{{ e.event_uid || '-' }}</td>
                  <td><v-chip size="x-small" color="primary">{{ e.start_code || '-' }}</v-chip></td>
                  <td class="text-caption">{{ formatDateTime(e.start_time) }}</td>
                  <td>{{ formatDuration(e.duringtime) }}</td>
                  <td>{{ e.operator_name || e.operator_id || '-' }}</td>
                  <td><v-chip v-if="e.process_no" size="x-small" color="pink">{{ e.process_no }}</v-chip><span v-else>-</span></td>
                  <td><v-chip v-if="e.line_code" size="x-small" color="purple">{{ e.line_code }}</v-chip><span v-else>-</span></td>
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
import { ref, reactive, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { useMessage, useConfirm } from '@/composables/useMessage'
import { deviceAPI, erpOrderAPI, servoCurveAPI, eventAssociationAPI } from '@/api/index'
import { formatDateTime } from '@/utils/datetime'
import * as echarts from 'echarts'

const message = useMessage()
const confirmDialog = useConfirm()

// 前端值提取工具函数（用于曲线采集，返回原始值）
function extractFieldValue(data, path) {
  if (!data || !path) return null
  if (path in data) return data[path]
  const keys = path.split('.')
  let current = data
  for (const key of keys) {
    if (current && typeof current === 'object' && key in current) {
      current = current[key]
    } else return null
  }
  return current
}

function applyExtraction(value, rule) {
  if (!rule || !rule.type) return value
  const str = String(value)
  try {
    if (rule.type === 'regex_extract') {
      const m = str.match(rule.params)
      return m ? m[0] : value
    } else if (rule.type === 'split') {
      return str.split(rule.params)[0]
    } else if (rule.type === 'substring') {
      if (rule.params && rule.params.includes(',')) {
        const [start, length] = rule.params.split(',').map(Number)
        return str.substring(start, start + length)
      } else {
        return str.substring(Number(rule.params))
      }
    }
  } catch (e) {
    console.error('截取规则应用失败:', e)
  }
  return value
}

// 状态
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const activeTab = ref('overview')

// 导入导出状态
const importDialogVisible = ref(false)
const importFile = ref(null)
const uploading = ref(false)

// 保存曲线对话框状态
const saveCurveDialogVisible = ref(false)
const savingCurve = ref(false)

// 加工事件对话框状态
const deviceEventsDialog = ref(false)
const deviceEventsDevice = ref(null)
const deviceEventsLoading = ref(false)
const deviceEventsData = ref([])
const saveCurveForm = reactive({
  curve_name: '',
  device_code: '',
  servo_axis: '',
  part_number: '',
  curve_data: [],
  value_tolerance: 5.0,
  time_tolerance_ms: 100,
  description: '',
  total_duration_ms: 0
})

// 批量选择状态
const selectedDeviceCodes = ref([])

// 数据采集弹窗状态
const dataCollectionDialogVisible = ref(false)
const currentDevice = reactive({
  device_code: '',
  device_name: '',
  device_type: '',
  status: ''
})
const activeDataTab = ref('')
const topicConfigs = ref([])
const topicData = reactive({})
const topicLoading = reactive({})
const autoRefresh = ref(false)
const refreshInterval = ref(10000)
let refreshTimer = null

const statusLoading = ref(false)
const lastStatusUpdateTime = ref('')
const deviceStatus = reactive({
  processing: false,
  mold_change: false,
  fault: false,
  alarm: false,
  material_shortage: false,
  stop: false,
  plan_stop: false
})
const alarmCount = ref(0)
const ruleMatchDetails = reactive({})
const statusErrors = ref([])
const hasStatusErrors = ref(false)
const currentPart = reactive({
  part_number: null,
  u9_material_code: null,
  start_code: null,
  order_info: null
})
let statusRefreshTimer = null

// 状态监控配置对话框状态
const statusMonitorConfigDialogVisible = ref(false)
const currentProductConfigDialogVisible = ref(false)
const configLoading = ref(false)
const configType = ref('product')
const selectedStatusType = ref('')
const currentConfigs = ref([])
const statusMonitorTopics = ref([])
const currentTopicFields = ref([])
const showAddRuleForm = ref(false)
const showRuleHelp = ref(false)
const editingConfigId = ref(null)
const availableCurves = ref([])

const loadCurves = async () => {
  if (!currentDevice.device_code) return
  try {
    const res = await servoCurveAPI.getDeviceCurves(currentDevice.device_code)
    availableCurves.value = res.data?.curves || []
  } catch (e) {
    console.error('加载曲线列表失败:', e)
    availableCurves.value = []
  }
}

const newRule = reactive({
  logic_operator: 'AND',
  parameter_points: [],
  priority: 0,
  device_status: '',
  description: ''
})

// 当前加工产品配置相关状态
const productConfigs = ref([])
const showAddProductRuleForm = ref(false)
const editingProductConfigId = ref(null)
const newProductRule = reactive({
  topic_name: '',
  field_path: '',
  field_description: '',
  extraction_rule: null,
  priority: 0,
  description: ''
})

// 通配符提取类型
const extractionTypes = [
  { value: 'regex_extract', label: '正则提取', icon: 'mdi-regex' },
  { value: 'split', label: '分隔符分割', icon: 'mdi-content-cut' },
  { value: 'substring', label: '位置截取', icon: 'mdi-text' }
]

const getExtractionTypeLabel = (type) => {
  const typeMap = {
    'regex_extract': '正则表达式',
    'split': '分隔符',
    'substring': '截取位置'
  }
  return typeMap[type] || type
}

const getExtractionPlaceholder = (type) => {
  const placeholderMap = {
    'regex_extract': '例如：^\\d+-\\d+',
    'split': '例如：-$$',
    'substring': '例如：0,10 或 5'
  }
  return placeholderMap[type] || ''
}

const getExtractionExample = (type) => {
  const exampleMap = {
    'regex_extract': '示例：从 "2080192-00-C$$1777317193000" 提取 "2080192-00"，使用正则 ^\\d+-\\d+',
    'split': '示例：从 "2080192-00-C$$1777317193000" 提取 "2080192-00"，使用分隔符 -$$',
    'substring': '示例：从 "2080192-00-C$$1777317193000" 提取前10个字符，使用 0,10'
  }
  return exampleMap[type] || ''
}

const sampleFieldValue = computed(() => {
  if (newProductRule.field_path && currentTopicFields.value.length > 0) {
    const field = currentTopicFields.value.find(f => f.field_path === newProductRule.field_path)
    return field?.field_value || null
  }
  return null
})

const previewExtractedValue = computed(() => {
  if (!newProductRule.extraction_rule || !sampleFieldValue.value) {
    return sampleFieldValue.value
  }
  try {
    const { type, params } = newProductRule.extraction_rule
    const value = sampleFieldValue.value
    if (type === 'regex_extract') {
      const regex = new RegExp(params)
      const match = value.match(regex)
      return match ? match[0] : value
    } else if (type === 'split') {
      const parts = value.split(params)
      return parts[0] || value
    } else if (type === 'substring') {
      if (params.includes(',')) {
        const [start, length] = params.split(',').map(Number)
        return value.substring(start, start + length)
      } else {
        const start = parseInt(params)
        return value.substring(start)
      }
    }
    return value
  } catch (e) {
    return value
  }
})

const getExtractionRuleLabel = (rule) => {
  if (!rule) return ''
  const typeMap = {
    'regex_extract': `正则: ${rule.params}`,
    'split': `分隔符: ${rule.params}`,
    'substring': `截取: ${rule.params}`
  }
  return typeMap[rule.type] || rule.params
}

// Device table headers
const deviceHeaders = [
  { title: '设备编号', key: 'device_code' },
  { title: '设备名称', key: 'device_name' },
  { title: '设备类型', key: 'device_type' },
  { title: '型号', key: 'model' },
  { title: '制造商', key: 'manufacturer' },
  { title: '产线', key: 'line_code' },
  { title: '关联 Topic', key: 'mqtt_topics', sortable: false },
  { title: '状态', key: 'status', sortable: false },
  { title: '更新时间', key: 'updated_at' },
  { title: '看板显示', key: 'show_on_dashboard', sortable: false, width: '80px' },
  { title: '操作', key: 'actions', sortable: false, width: '180px' },
]

// Status filter options
const statusFilterOptions = [
  { title: '全部状态', value: '' },
  { title: '计划加工', value: 'scheduled processing' },
  { title: '计划停机', value: 'scheduled outage' },
  { title: '故障停机', value: 'fault_stop' },
  { title: '紧急停机', value: 'emergency stop' },
  { title: '换模', value: 'mold_change' },
  { title: '维护', value: 'maintain' },
  { title: '缺料', value: 'material_shortage' },
  { title: '未知', value: 'unknown' },
]

// Device status options for rule config
const deviceStatusOptions = [
  { title: '不更新', value: '' },
  { title: '计划加工', value: 'scheduled processing' },
  { title: '计划停机', value: 'scheduled outage' },
  { title: '故障停机', value: 'fault_stop' },
  { title: '紧急停机', value: 'emergency stop' },
  { title: '换模', value: 'mold_change' },
  { title: '维护', value: 'maintain' },
  { title: '缺料', value: 'material_shortage' },
  { title: '未知', value: 'unknown' },
]

const statusTypeOptions = [
  { value: 'processing', label: '计划加工', mdiIcon: 'mdi-play-circle', color: 'success' },
  { value: 'stop', label: '计划停机', mdiIcon: 'mdi-stop-circle', color: 'error' },
  { value: 'fault_stop', label: '故障停机', mdiIcon: 'mdi-alert-circle', color: 'error' },
  { value: 'emergency stop', label: '紧急停机', mdiIcon: 'mdi-close-octagon', color: 'error' },
  { value: 'mold_change', label: '换模', mdiIcon: 'mdi-swap-horizontal', color: 'warning' },
  { value: 'maintain', label: '维护', mdiIcon: 'mdi-wrench', color: 'info' },
  { value: 'alarm', label: '报警', mdiIcon: 'mdi-bell', color: 'warning' },
  { value: 'material_shortage', label: '缺料', mdiIcon: 'mdi-package-variant', color: 'grey' }
]

const matchRuleOptions = [
  { value: 'equals', label: '等于', requiresValue: true },
  { value: 'not_equals', label: '不等于', requiresValue: true },
  { value: 'contains', label: '包含', requiresValue: true },
  { value: 'not_contains', label: '不包含', requiresValue: true },
  { value: 'starts_with', label: '开头是', requiresValue: true },
  { value: 'ends_with', label: '结尾是', requiresValue: true },
  { value: 'greater_than', label: '大于', requiresValue: true },
  { value: 'less_than', label: '小于', requiresValue: true },
  { value: 'greater_equal', label: '大于等于', requiresValue: true },
  { value: 'less_equal', label: '小于等于', requiresValue: true },
  { value: 'in_range', label: '在范围内', requiresValue: true },
  { value: 'regex', label: '正则匹配', requiresValue: true },
  { value: 'is_true', label: '为true', requiresValue: false },
  { value: 'is_false', label: '为false', requiresValue: false },
  { value: 'is_empty', label: '为空', requiresValue: false },
  { value: 'is_not_empty', label: '不为空', requiresValue: false }
]

// 分页
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 搜索条件
const searchQuery = reactive({
  device_code: '',
  device_name: '',
  status: '',
  device_type: ''
})

// 统计数据
const deviceStats = reactive({
  total: 0,
  active: 0,
  inactive: 0,
  maintenance: 0,
  enabled: 0
})

// 设备列表
const deviceList = ref([])

// 表单数据
const formData = reactive({
  device_code: '',
  device_name: '',
  device_type: '',
  model: '',
  manufacturer: '',
  line_code: '',
  factory_code: '',
  group_code: '',
  description: '',
  location: '',
  status: 'active',
  is_enabled: true,
  show_on_dashboard: false,
  ip_address: '',
  mqtt_topics: []
})

// 可用的 Topic 列表
const availableTopics = ref([
  'SHXQ/NO1/KP3/IMG/ProcesEvent',
  'SHXQ/NO1/KP3/IMG/Alarm',
  'SHXQ/NO1/KP3/IMG/PV',
  'SHXQ/NO1/KP3/IMG/SV'
])

// 计算属性
const pointNeedsValue = (point) => {
  const rule = matchRuleOptions.find(r => r.value === point.match_rule)
  return rule ? rule.requiresValue : true
}

const isRuleFormValid = computed(() => {
  if (newRule.parameter_points.length === 0) return false
  return newRule.parameter_points.every(
    p => p.topic_name && p.field_path && (
      (p.match_rule && (!pointNeedsValue(p) || p.match_value)) || p.curve_id
    )
  )
})

const isProductRuleFormValid = computed(() => {
  return newProductRule.topic_name && newProductRule.field_path
})

const isAllSelected = computed(() => {
  return deviceList.value.length > 0 && selectedDeviceCodes.value.length === deviceList.value.length
})

// Status color mapping
const getStatusColor = (part) => {
  const colorMap = {
    'processing': 'success', 'scheduled processing': 'success',
    'stop': 'warning', 'scheduled outage': 'warning',
    'fault_stop': 'error', 'emergency stop': 'error',
    'mold_change': 'warning', 'maintain': 'info',
    'material_shortage': 'warning', 'alarm': 'orange',
    'unknown': 'grey'
  }
  return colorMap[part] || 'grey'
}

const getStatusCardColor = (key) => {
  const colorMap = {
    'processing': 'success', 'stop': 'warning', 'fault_stop': 'error',
    'emergency stop': 'error', 'mold_change': 'warning', 'maintain': 'info',
    'alarm': 'orange', 'material_shortage': 'grey'
  }
  return colorMap[key] || 'grey'
}

const getOrderStatusColor = (status) => {
  const colorMap = {
    'created': 'info', 'released': 'primary', 'in_progress': 'warning',
    'completed': 'success', 'closed': 'grey'
  }
  return colorMap[status] || 'grey'
}

// 状态监控配置相关方法
const openCurrentProductConfig = async () => {
  currentProductConfigDialogVisible.value = true
  await loadAvailableTopics()
  await loadProductConfigs()
}

const openStatusMonitorConfig = async () => {
  statusMonitorConfigDialogVisible.value = true
  selectedStatusType.value = ''
  await loadAvailableTopics()
  await loadStatusMonitorConfigs()
}

const loadStatusMonitorConfigs = async () => {
  await loadStatusConfigs()
}

const loadAvailableTopics = async () => {
  try {
    configLoading.value = true
    const res = await deviceAPI.getDeviceTopicsAndFields(currentDevice.device_code)
    if (res.data) {
      statusMonitorTopics.value = res.data.topics || []
    }
  } catch (error) {
    console.error('加载Topic列表失败:', error)
    message.error('加载Topic列表失败')
  } finally {
    configLoading.value = false
  }
}

const onProductTopicChange = () => {
  const topic = statusMonitorTopics.value.find(t => t.topic_name === newProductRule.topic_name)
  if (topic && topic.fields) {
    currentTopicFields.value = [...topic.fields]
    if (topic.fields.length === 0) {
      message.warning('该Topic暂无可用字段，请检查MQTT消息是否正常接收')
    }
  } else {
    currentTopicFields.value = []
    message.warning('未找到该Topic的字段信息')
  }
  newProductRule.field_path = ''
}

const loadProductConfigs = async () => {
  try {
    configLoading.value = true
    const res = await deviceAPI.getCurrentProductConfigs(currentDevice.device_code)
    if (res.data) {
      productConfigs.value = res.data.items || []
    }
  } catch (error) {
    console.error('加载产品配置列表失败:', error)
    message.error('加载产品配置列表失败')
  } finally {
    configLoading.value = false
  }
}

const editProductConfig = (config) => {
  editingProductConfigId.value = config.id
  newProductRule.topic_name = config.topic_name
  newProductRule.field_description = config.field_description || ''
  newProductRule.extraction_rule = config.extraction_rule || null
  newProductRule.priority = config.priority || 0
  newProductRule.description = config.description || ''
  showAddProductRuleForm.value = true
  onProductTopicChange()
  newProductRule.field_path = config.field_path
}

const deleteProductConfig = async (config) => {
  try {
    const ok = await confirmDialog('确定要删除这条配置规则吗？', '确认删除', 'warning')
    if (!ok) return
    await deviceAPI.deleteCurrentProductConfig(config.id)
    message.success('删除成功')
    await loadProductConfigs()
  } catch (error) {
    console.error('删除产品配置失败:', error)
    message.error('删除产品配置失败')
  }
}

const toggleProductConfig = async (config) => {
  try {
    await deviceAPI.toggleCurrentProductConfig(config.id)
    message.success(config.enabled ? '已启用' : '已禁用')
  } catch (error) {
    console.error('切换配置状态失败:', error)
    message.error('切换配置状态失败')
    config.enabled = !config.enabled
  }
}

const saveProductRule = async () => {
  try {
    const data = {
      device_code: currentDevice.device_code,
      topic_name: newProductRule.topic_name,
      field_path: newProductRule.field_path,
      field_description: newProductRule.field_description || null,
      extraction_rule: newProductRule.extraction_rule,
      priority: newProductRule.priority,
      description: newProductRule.description || null,
      enabled: true
    }
    if (editingProductConfigId.value) {
      await deviceAPI.updateCurrentProductConfig(editingProductConfigId.value, data)
      message.success('更新成功')
    } else {
      await deviceAPI.createCurrentProductConfig(data)
      message.success('添加成功')
    }
    cancelAddProductRule()
    await loadProductConfigs()
  } catch (error) {
    console.error('保存产品配置失败:', error)
    message.error('保存产品配置失败')
  }
}

const cancelAddProductRule = () => {
  showAddProductRuleForm.value = false
  editingProductConfigId.value = null
  newProductRule.topic_name = ''
  newProductRule.field_path = ''
  newProductRule.field_description = ''
  newProductRule.extraction_rule = null
  newProductRule.priority = 0
  newProductRule.description = ''
  currentTopicFields.value = []
}

const addParameterPoint = () => {
  newRule.parameter_points.push({
    topic_name: '',
    field_path: '',
    field_value_preview: '',
    match_rule: '',
    match_value: '',
    extraction_rule: null,
    curve_id: null,
    fields: [],
    showTree: false,
    curveChart: null,
    curveData: [],
    curveCollecting: false,
    curveTimer: null,
    boundCurveData: null,
    boundCurveName: '',
    curveRangeStart: null,
    curveRangeEnd: null
  })
}

const removeParameterPoint = (index) => {
  const point = newRule.parameter_points[index]
  if (point) {
    stopCurveCollect(point)
    if (point.curveChart) {
      point.curveChart.dispose()
      point.curveChart = null
    }
  }
  newRule.parameter_points.splice(index, 1)
}

const onPointTopicChange = (point) => {
  const topic = statusMonitorTopics.value.find(t => t.topic_name === point.topic_name)
  if (topic) {
    point.fields = topic.fields || []
  } else {
    point.fields = []
  }
  point.field_path = ''
  point.field_value_preview = ''
}

const onPointFieldChange = (point) => {
  const field = (point.fields || []).find(f => f.field_path === point.field_path)
  if (field) {
    point.field_value_preview = field.field_value !== undefined ? String(field.field_value) : ''
  } else {
    point.field_value_preview = ''
  }
}

// ============ 参数曲线采集与绘制 ============
const curveChartRefs = {}

const setCurveChartRef = (el, index) => {
  if (el) {
    curveChartRefs[index] = el
  }
}

const initCurveChart = (point, index) => {
  const el = curveChartRefs[index]
  if (!el) return
  if (point.curveChart) {
    point.curveChart.dispose()
  }
  point.curveChart = echarts.init(el)
  updateCurveChart(point, index)
}

const updateCurveChart = (point, index) => {
  if (!point.curveChart) return
  const realtimeSeriesData = point.curveData.map(p => [p.time, p.value])
  const series = [
    {
      name: '实时曲线',
      type: 'line',
      smooth: true,
      symbol: 'none',
      lineStyle: { color: '#409EFF', width: 2 },
      areaStyle: { color: 'rgba(64,158,255,0.1)' },
      data: realtimeSeriesData
    }
  ]
  const legend = ['实时曲线']
  if (point.boundCurveData && point.boundCurveData.length > 0) {
    const boundData = point.boundCurveData.map(p => [p.time, p.value])
    const boundLegendName = point.boundCurveName ? `标准曲线 (${point.boundCurveName})` : '标准曲线'
    series.push({
      name: boundLegendName,
      type: 'line',
      smooth: true,
      symbol: 'none',
      lineStyle: { color: '#E6A23C', width: 2, type: 'dashed' },
      data: boundData
    })
    legend.push(boundLegendName)
  }
  const hasData = point.curveData.length > 0
  point.curveChart.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        let html = `时间: ${(params[0].data[0] / 1000).toFixed(1)}s<br/>`
        params.forEach(p => {
          html += `${p.seriesName}: ${p.data[1].toFixed(2)}<br/>`
        })
        return html
      }
    },
    legend: { data: legend, top: 0, left: 'center', textStyle: { fontSize: 12 }, icon: 'roundRect', itemWidth: 20, itemHeight: 3 },
    grid: { top: legend.length > 1 ? 35 : 30, left: 50, right: 20, bottom: 60 },
    xAxis: { type: 'value', name: '时间(s)', axisLabel: { formatter: v => (v / 1000).toFixed(0) + 's' } },
    yAxis: { type: 'value', name: '值', scale: true },
    dataZoom: hasData ? [{ type: 'slider', xAxisIndex: 0, bottom: 5, height: 20, filterMode: 'none', borderColor: '#ddd', fillerColor: 'rgba(64,158,255,0.15)', handleStyle: { color: '#409EFF' } }] : [],
    series
  }, true)
  point.curveChart.off('dataZoom')
  if (hasData) {
    point.curveChart.on('dataZoom', (params) => {
      const option = point.curveChart.getOption()
      const zoom = option.dataZoom[0]
      if (zoom && realtimeSeriesData.length > 0) {
        const allTimes = realtimeSeriesData.map(d => d[0])
        const minTime = allTimes[0]
        const maxTime = allTimes[allTimes.length - 1]
        const range = maxTime - minTime
        point.curveRangeStart = minTime + (range * (zoom.start / 100))
        point.curveRangeEnd = minTime + (range * (zoom.end / 100))
      }
    })
  }
}

const startCurveCollect = async (point, index) => {
  if (!point.topic_name || !point.field_path) {
    message.warning('请先选择Topic和字段路径')
    return
  }
  point.curveCollecting = true
  const startTime = Date.now()
  point.curveTimer = setInterval(async () => {
    try {
      const res = await deviceAPI.getLatestCompressedData({ topic: point.topic_name })
      if (res.data && res.data.data) {
        let value = extractFieldValue(res.data.data, point.field_path)
        if (value === null || value === undefined) return
        if (point.extraction_rule && point.extraction_rule.type) {
          value = applyExtraction(value, point.extraction_rule)
        }
        const numValue = Number(value)
        if (isNaN(numValue)) return
        const timeOffset = Date.now() - startTime
        point.curveData.push({ time: timeOffset, value: numValue })
        if (!point.curveChart && curveChartRefs[index]) {
          initCurveChart(point, index)
        }
        updateCurveChart(point, index)
      }
    } catch (e) {
      console.error('曲线采集失败:', e)
    }
  }, 1000)
}

const stopCurveCollect = (point) => {
  point.curveCollecting = false
  if (point.curveTimer) {
    clearInterval(point.curveTimer)
    point.curveTimer = null
  }
}

const clearCurveData = (point, index) => {
  stopCurveCollect(point)
  point.curveData = []
  point.curveRangeStart = null
  point.curveRangeEnd = null
  updateCurveChart(point, index)
}

const loadBoundCurve = async (point, index) => {
  if (!point.curve_id) {
    point.boundCurveData = null
    point.boundCurveName = ''
    if (point.curveChart) updateCurveChart(point, index)
    return
  }
  try {
    const res = await servoCurveAPI.getCurve(point.curve_id)
    if (res.data && res.data.curve_data) {
      point.boundCurveData = res.data.curve_data
      point.boundCurveName = res.data.curve_name || ''
      if (!point.curveChart && curveChartRefs[index]) {
        initCurveChart(point, index)
      }
      updateCurveChart(point, index)
    }
  } catch (e) {
    console.error('加载绑定曲线失败:', e)
  }
}

const extractCurveRange = (point, index) => {
  if (point.curveData.length === 0) return
  if (point.curveRangeStart == null || point.curveRangeEnd == null) {
    message.warning('请先拖动图表下方的滑块选择截取范围')
    return
  }
  const start = Math.min(point.curveRangeStart, point.curveRangeEnd)
  const end = Math.max(point.curveRangeStart, point.curveRangeEnd)
  const filtered = point.curveData.filter(p => p.time >= start && p.time <= end)
  if (filtered.length === 0) {
    message.warning('选区内无数据点')
    return
  }
  const baseTime = filtered[0].time
  point.curveData = filtered.map(p => ({ time: p.time - baseTime, value: p.value }))
  if (point.boundCurveData && point.boundCurveData.length > 0) {
    point.boundCurveData = point.boundCurveData.map(p => ({ time: p.time - baseTime, value: p.value }))
  }
  point.curveRangeStart = null
  point.curveRangeEnd = null
  updateCurveChart(point, index)
  message.success(`已截取 ${point.curveData.length} 个数据点`)
}

const openSaveCurveDialog = (point, index) => {
  if (point.curveData.length === 0) {
    message.warning('请先采集曲线数据')
    return
  }
  saveCurveForm.device_code = currentDevice.device_code || ''
  saveCurveForm.servo_axis = point.topic_name || ''
  saveCurveForm.curve_name = ''
  saveCurveForm.part_number = ''
  saveCurveForm.description = ''
  saveCurveForm.value_tolerance = 5.0
  saveCurveForm.time_tolerance_ms = 100
  saveCurveForm.curve_data = point.curveData.map(p => ({ time: p.time, value: p.value }))
  saveCurveForm.total_duration_ms = point.curveData.length > 0 ? point.curveData[point.curveData.length - 1].time : 0
  saveCurveDialogVisible.value = true
}

const saveCurve = async () => {
  if (!saveCurveForm.curve_name) {
    message.warning('请输入曲线名称')
    return
  }
  savingCurve.value = true
  try {
    await servoCurveAPI.createCurve({
      device_code: saveCurveForm.device_code,
      curve_name: saveCurveForm.curve_name,
      servo_axis: saveCurveForm.servo_axis,
      part_number: saveCurveForm.part_number || null,
      curve_data: saveCurveForm.curve_data,
      value_tolerance: saveCurveForm.value_tolerance,
      time_tolerance_ms: saveCurveForm.time_tolerance_ms,
      enabled: true,
      description: saveCurveForm.description || null
    })
    message.success('曲线保存成功')
    saveCurveDialogVisible.value = false
    await loadCurves()
  } catch (e) {
    console.error('保存曲线失败:', e)
    message.error('保存曲线失败')
  } finally {
    savingCurve.value = false
  }
}

const getStatusTypeLabel = (value) => {
  const option = statusTypeOptions.find(s => s.value === value)
  return option ? option.label : value
}

const getMatchRuleLabel = (value) => {
  const option = matchRuleOptions.find(r => r.value === value)
  return option ? option.label : value
}

const getMatchRuleInputType = (ruleValue) => {
  const option = matchRuleOptions.find(r => r.value === ruleValue)
  return option ? option.input_type || 'text' : 'text'
}

const getMatchRulePlaceholder = (ruleValue) => {
  const option = matchRuleOptions.find(r => r.value === ruleValue)
  return option ? option.placeholder || '输入匹配值' : '输入匹配值'
}

const getMatchRuleExample = (ruleValue) => {
  const option = matchRuleOptions.find(r => r.value === ruleValue)
  return option ? option.example || '' : ''
}

const formatMatchValue = (point) => {
  if (!point.match_value || !point.match_rule) return
  if (point.match_rule === 'in_range') {
    const val = point.match_value.trim()
    const rangeMatch = val.match(/^(\d+\.?\d*)\s*-\s*(\d+\.?\d*)$/)
    if (rangeMatch) {
      point.match_value = `[${rangeMatch[1]}, ${rangeMatch[2]}]`
    }
  }
}

const statusItems = [
  { key: 'processing', label: '计划加工', mdiIcon: 'mdi-cog', activeClass: 'status-processing' },
  { key: 'stop', label: '计划停机', mdiIcon: 'mdi-stop-circle', activeClass: 'status-stop' },
  { key: 'fault_stop', label: '故障停机', mdiIcon: 'mdi-alert-circle', activeClass: 'status-fault' },
  { key: 'emergency stop', label: '紧急停机', mdiIcon: 'mdi-close-octagon', activeClass: 'status-fault' },
  { key: 'mold_change', label: '换模', mdiIcon: 'mdi-swap-horizontal', activeClass: 'status-mold-change' },
  { key: 'maintain', label: '维护', mdiIcon: 'mdi-wrench', activeClass: 'status-maintenance' },
  { key: 'alarm', label: '报警', mdiIcon: 'mdi-bell', activeClass: 'status-alarm' },
  { key: 'material_shortage', label: '缺料', mdiIcon: 'mdi-package-variant', activeClass: 'status-material' }
]

const getStatusValueText = (statusKey) => {
  if (statusKey === 'alarm') {
    return deviceStatus.alarm ? 'Y' : 'N'
  }
  if (statusKey === 'stop') {
    if (deviceStatus.plan_stop) return 'Y'
    return deviceStatus.stop ? 'Y' : 'N'
  }
  return deviceStatus[statusKey] ? 'Y' : 'N'
}

const showStatusDetail = (statusKey) => {
  const detail = ruleMatchDetails[statusKey]
  const item = statusItems.find(s => s.key === statusKey)
  const statusText = getStatusValueText(statusKey)
  if (!detail) {
    message.info(`${item?.label || statusKey}: ${statusText} - 暂无规则匹配信息`)
    return
  }
  let detailMessage = `状态类型：${item?.label || statusKey}\n`
  detailMessage += `当前状态：${statusText}\n\n`
  if (detail.matched) {
    detailMessage += `✓ 规则已匹配\n`
    detailMessage += `匹配规则：${detail.matched_config_desc || `配置#${detail.matched_config_id}`}\n\n`
  } else if (detail.error) {
    detailMessage += `⚠ 规则评估错误\n`
    detailMessage += `错误信息：${detail.error}\n\n`
  } else {
    detailMessage += `○ 未匹配到规则\n\n`
  }
  if (detail.evaluated_configs && detail.evaluated_configs.length > 0) {
    detailMessage += `规则评估详情 (${detail.evaluated_configs.length}条)：\n`
    detailMessage += `${'─'.repeat(40)}\n`
    detail.evaluated_configs.forEach((cfg, idx) => {
      const icon = cfg.matched ? '✓' : cfg.error ? '✗' : '○'
      detailMessage += `${idx + 1}. ${cfg.description || `配置#${cfg.config_id}`} ${icon}\n`
      if (cfg.matched) detailMessage += `   匹配成功\n`
      if (cfg.error) detailMessage += `   错误：${cfg.error}\n`
      if (!cfg.matched && !cfg.error) detailMessage += `   未匹配\n`
      if (cfg.evaluation_details && cfg.evaluation_details.length > 0) {
        cfg.evaluation_details.forEach((cond, ci) => {
          detailMessage += `   条件${ci + 1}: topic=${cond.topic_name || '-'} 字段=${cond.field_path || '-'}\n`
          if (cond.steps && cond.steps.length > 0) {
            cond.steps.forEach(step => {
              if (step.step === '获取消息') {
                detailMessage += `     ${step.result === '失败' ? '✗' : '✓'} 获取消息: ${step.result}`
                if (step.reason) detailMessage += ` (${step.reason})`
                detailMessage += `\n`
              } else if (step.step === '获取字段值') {
                detailMessage += `     字段 '${step.field_path}' = ${step.actual_value} (${step.type})\n`
              } else if (step.step === '值匹配') {
                detailMessage += `     ${step.result === '匹配' ? '✓' : '✗'} ${step.actual} ${step.rule} ${step.expected} => ${step.result}\n`
              } else if (step.result === '失败') {
                detailMessage += `     ✗ ${step.step}: ${step.reason || '失败'}\n`
                if (step.payload_keys && step.payload_keys.length > 0) {
                  detailMessage += `       可用字段: ${step.payload_keys.join(', ')}\n`
                }
              }
            })
          }
        })
      }
      if (idx < detail.evaluated_configs.length - 1) detailMessage += `${'─'.repeat(40)}\n`
    })
  }
  console.log(`[状态详情] ${statusKey}:`, detail)
  message.info(detailMessage)
}

const loadStatusConfigs = async () => {
  try {
    configLoading.value = true
    const res = await deviceAPI.getAllDeviceRules(currentDevice.device_code, selectedStatusType.value)
    if (res.data) {
      currentConfigs.value = res.data.items || []
    }
  } catch (error) {
    console.error('加载配置列表失败:', error)
    message.error('加载配置列表失败')
  } finally {
    configLoading.value = false
  }
}

const toggleConfigEnabled = async (config) => {
  try {
    await deviceAPI.updateStatusConfig(config.id, { enabled: config.enabled })
    message.success(config.enabled ? '已启用' : '已禁用')
  } catch (error) {
    config.enabled = !config.enabled
    message.error('操作失败')
  }
}

const makePointBase = () => ({
  curveChart: null,
  curveData: [],
  curveCollecting: false,
  curveTimer: null,
  boundCurveData: null,
  boundCurveName: '',
  curveRangeStart: null,
  curveRangeEnd: null
})

const editConfig = (config) => {
  editingConfigId.value = config.id
  newRule.logic_operator = config.logic_operator || 'AND'
  newRule.priority = config.priority || 0
  newRule.device_status = config.device_status || ''
  newRule.description = config.description || ''
  const points = []
  if (config.conditions && config.conditions.length > 0) {
    for (const c of config.conditions) {
      const topic = statusMonitorTopics.value.find(t => t.topic_name === c.topic_name)
      const field = topic ? (topic.fields || []).find(f => f.field_path === c.field_path) : null
      points.push({
        ...makePointBase(),
        topic_name: c.topic_name || '',
        field_path: c.field_path || '',
        field_value_preview: field ? String(field.field_value) : '',
        match_rule: c.match_rule || '',
        match_value: c.match_value || '',
        extraction_rule: c.extraction_rule || null,
        curve_id: c.curve_id || null,
        fields: topic ? (topic.fields || []) : [],
        showTree: false
      })
    }
  } else if (config.topic_name && config.field_path) {
    const topic = statusMonitorTopics.value.find(t => t.topic_name === config.topic_name)
    const field = topic ? (topic.fields || []).find(f => f.field_path === config.field_path) : null
    points.push({
      ...makePointBase(),
      topic_name: config.topic_name,
      field_path: config.field_path,
      field_value_preview: field ? String(field.field_value) : '',
      match_rule: config.match_rule || '',
      match_value: config.match_value || '',
      extraction_rule: config.extraction_rule || null,
      curve_id: config.curve_id || null,
      fields: topic ? (topic.fields || []) : [],
      showTree: false
    })
  }
  newRule.parameter_points = points
  showAddRuleForm.value = true
  loadCurves()
}

const deleteConfig = async (config) => {
  try {
    const ok = await confirmDialog('确定要删除这条配置规则吗？', '确认删除', 'warning')
    if (!ok) return
    await deviceAPI.deleteStatusConfig(config.id)
    message.success('删除成功')
    await loadStatusConfigs()
    await loadDeviceStatus()
  } catch (error) {
    console.error('删除配置失败:', error)
    message.error('删除配置失败')
  }
}

const saveNewRule = async () => {
  try {
    const conditions = newRule.parameter_points.map(p => {
      const cond = {
        topic_name: p.topic_name,
        field_path: p.field_path,
        match_rule: p.curve_id ? (p.match_rule || 'curve_only') : (p.match_rule === 'curve_only' ? '' : p.match_rule),
        match_value: p.match_value || null,
        extraction_rule: p.extraction_rule && p.extraction_rule.type ? { type: p.extraction_rule.type, params: p.extraction_rule.params } : null
      }
      if (p.curve_id) cond.curve_id = parseInt(p.curve_id, 10)
      return cond
    })
    const firstPoint = newRule.parameter_points[0] || {}
    const curveIdPoint = newRule.parameter_points.find(p => p.curve_id)
    const curveId = curveIdPoint ? parseInt(curveIdPoint.curve_id, 10) : null
    const ruleData = {
      device_code: currentDevice.device_code,
      rule_scope: 'device',
      status_type: selectedStatusType.value,
      topic_name: firstPoint.topic_name || '',
      field_path: firstPoint.field_path || '',
      match_rule: firstPoint.curve_id ? (firstPoint.match_rule || 'curve_only') : (firstPoint.match_rule === 'curve_only' ? '' : firstPoint.match_rule),
      match_value: firstPoint.match_value || null,
      extraction_rule: firstPoint.extraction_rule && firstPoint.extraction_rule.type ? { type: firstPoint.extraction_rule.type, params: firstPoint.extraction_rule.params } : null,
      curve_id: curveId,
      logic_operator: newRule.logic_operator,
      conditions: conditions.length > 0 ? conditions : null,
      priority: newRule.priority,
      device_status: newRule.device_status || null,
      description: newRule.description,
      enabled: true
    }
    if (editingConfigId.value) {
      await deviceAPI.updateStatusConfig(editingConfigId.value, ruleData)
      message.success('更新成功')
    } else {
      await deviceAPI.createStatusConfig(ruleData)
      message.success('添加成功')
    }
    cancelAddRule()
    await loadStatusConfigs()
    await loadDeviceStatus()
  } catch (error) {
    console.error('保存配置失败:', error)
    message.error('保存配置失败')
  }
}

const cancelAddRule = () => {
  newRule.parameter_points.forEach(point => {
    stopCurveCollect(point)
    if (point.curveChart) {
      point.curveChart.dispose()
      point.curveChart = null
    }
  })
  showAddRuleForm.value = false
  editingConfigId.value = null
  newRule.logic_operator = 'AND'
  newRule.parameter_points = []
  newRule.priority = 0
  newRule.device_status = ''
  newRule.description = ''
}

watch(selectedStatusType, () => {
  if (selectedStatusType.value) {
    loadStatusConfigs()
    cancelAddRule()
  }
})

// 方法
const statusClassMap = {
  'processing': 'status-success',
  'scheduled processing': 'status-success',
  'stop': 'status-warning',
  'scheduled outage': 'status-warning',
  'fault_stop': 'status-danger',
  'emergency stop': 'status-danger',
  'mold_change': 'status-warning',
  'maintain': 'status-info',
  'material_shortage': 'status-warning',
  'alarm': 'status-alarm',
  'unknown': 'status-default'
}

const statusTextMap = {
  'processing': '计划加工',
  'scheduled processing': '计划加工',
  'stop': '计划停机',
  'scheduled outage': '计划停机',
  'fault_stop': '故障停机',
  'emergency stop': '紧急停机',
  'mold_change': '换模',
  'maintain': '维护',
  'material_shortage': '缺料',
  'alarm': '报警',
  'unknown': '未知'
}

const getStatusClassForPart = (part) => statusClassMap[part] || 'status-default'
const getStatusTextForPart = (part) => statusTextMap[part] || part

const getStatusClass = (status) => {
  if (!status) return 'status-default'
  const parts = status.split(',')
  return statusClassMap[parts[0]] || 'status-default'
}

const getStatusText = (status) => {
  if (!status) return '未知'
  return status.split(',').map(p => statusTextMap[p] || p).join(' | ')
}

const loadDevices = async () => {
  try {
    loading.value = true
    const params = {
      page: page.value,
      page_size: pageSize.value,
      ...searchQuery
    }
    const res = await deviceAPI.getDevices(params)
    deviceList.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch (error) {
    message.error('加载设备列表失败')
  } finally {
    loading.value = false
  }
}

const loadDeviceStats = async () => {
  try {
    const res = await deviceAPI.getStats()
    Object.assign(deviceStats, res.data || {})
  } catch (error) {
    console.error('加载设备统计失败:', error)
  }
}

// ========== 导入导出 ==========
const openImportDialog = () => {
  importFile.value = null
  importDialogVisible.value = true
}

const downloadTemplate = async () => {
  try {
    const response = await deviceAPI.downloadTemplate()
    const url = window.URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = url
    link.download = '设备导入模板.xlsx'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    setTimeout(() => window.URL.revokeObjectURL(url), 100)
  } catch (error) {
    console.error('下载模板失败:', error)
    message.error('下载模板失败')
  }
}

const exportDevices = async () => {
  try {
    const { device_code, device_name, status, device_type } = searchQuery
    const response = await deviceAPI.exportDevices({ device_code, device_name, status, device_type })
    const url = window.URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = url
    link.download = `devices_${new Date().toISOString().split('T')[0]}.csv`
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('导出设备失败:', error)
    message.error('导出设备失败')
  }
}

const uploadImportFile = async () => {
  // v-file-input returns an array or single file
  const file = Array.isArray(importFile.value) ? importFile.value[0] : importFile.value
  if (!file) return
  try {
    uploading.value = true
    const response = await deviceAPI.importDevices(file)
    const result = response.data
    let msg = `导入完成：新增 ${result.imported} 条，更新 ${result.updated} 条`
    if (result.errors && result.errors.length > 0) {
      msg += `，${result.errors.length} 条错误`
      console.warn('导入错误:', result.errors)
    }
    message.success(msg)
    importDialogVisible.value = false
    importFile.value = null
    await loadDevices()
    await loadDeviceStats()
  } catch (error) {
    console.error('导入设备失败:', error)
    message.error('导入失败：' + (error.response?.data?.detail || error.message))
  } finally {
    uploading.value = false
  }
}

const resetSearch = () => {
  searchQuery.device_code = ''
  searchQuery.device_name = ''
  searchQuery.status = ''
  searchQuery.device_type = ''
  page.value = 1
  loadDevices()
}

const openAddDialog = () => {
  isEdit.value = false
  Object.assign(formData, {
    device_code: '',
    device_name: '',
    device_type: '',
    model: '',
    manufacturer: '',
    line_code: '',
    factory_code: '',
    group_code: '',
    description: '',
    location: '',
    status: 'active',
    is_enabled: true,
    ip_address: '',
    mqtt_topics: []
  })
  formRef.value?.resetValidation()
  dialogVisible.value = true
}

const editDevice = (device) => {
  isEdit.value = true
  Object.assign(formData, {
    device_code: device.device_code,
    device_name: device.device_name,
    device_type: device.device_type || '',
    model: device.model || '',
    manufacturer: device.manufacturer || '',
    line_code: device.line_code || '',
    factory_code: device.factory_code || '',
    group_code: device.group_code || '',
    description: device.description || '',
    location: device.location || '',
    status: device.status,
    is_enabled: device.is_enabled,
    show_on_dashboard: device.show_on_dashboard,
    ip_address: device.ip_address || '',
    mqtt_topics: device.mqtt_topics || []
  })
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!formRef.value) return
  const { valid } = await formRef.value.validate()
  if (!valid) return
  try {
    submitting.value = true
    if (isEdit.value) {
      await deviceAPI.updateDevice(formData.device_code, formData)
      message.success('更新成功')
    } else {
      await deviceAPI.createDevice(formData)
      message.success('创建成功')
    }
    dialogVisible.value = false
    await loadDevices()
    await loadDeviceStats()
  } catch (error) {
    message.error(isEdit.value ? '更新失败' : '创建失败')
  } finally {
    submitting.value = false
  }
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedDeviceCodes.value = []
  } else {
    selectedDeviceCodes.value = deviceList.value.map(d => d.device_code)
  }
}

const batchToggleDashboard = async (show) => {
  try {
    await deviceAPI.batchToggleDashboard(selectedDeviceCodes.value, show)
    message.success(show ? '已批量显示到看板' : '已批量从看板隐藏')
    selectedDeviceCodes.value = []
    await loadDevices()
  } catch (error) {
    message.error('操作失败')
  }
}

const toggleDashboardShow = async (device) => {
  try {
    await deviceAPI.updateDevice(device.device_code, { show_on_dashboard: !device.show_on_dashboard })
    message.success(device.show_on_dashboard ? '已从看板隐藏' : '已在看板显示')
    await loadDevices()
  } catch (error) {
    message.error('操作失败')
  }
}

const deleteDevice = async (device) => {
  try {
    const ok = await confirmDialog(`确定要删除设备 "${device.device_name}" 吗？`, '确认删除', 'warning')
    if (!ok) return
    await deviceAPI.deleteDevice(device.device_code)
    message.success('删除成功')
    await loadDevices()
    await loadDeviceStats()
  } catch (error) {
    message.error('删除失败')
  }
}

const navigateToDataCollection = async (device) => {
  currentDevice.device_code = device.device_code
  currentDevice.device_name = device.device_name
  currentDevice.device_type = device.device_type || ''
  currentDevice.status = device.status
  dataCollectionDialogVisible.value = true
  await loadDeviceTopicConfigs()
  await loadDeviceStatus()
  startStatusAutoRefresh()
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

const viewDeviceEvents = async (device) => {
  deviceEventsDevice.value = device
  deviceEventsDialog.value = true
  deviceEventsLoading.value = true
  deviceEventsData.value = []
  try {
    const response = await eventAssociationAPI.getByDevice(device.device_code, { page_size: 50 })
    deviceEventsData.value = response.data?.items || []
  } catch (error) {
    console.error('加载加工事件失败:', error)
  } finally {
    deviceEventsLoading.value = false
  }
}

// 数据采集相关方法
const loadDeviceTopicConfigs = async () => {
  try {
    const res = await deviceAPI.getDeviceDataCollectionConfig(currentDevice.device_code)
    if (res.data) {
      topicConfigs.value = res.data.topic_configs || []
      if (topicConfigs.value.length > 0 && !activeDataTab.value) {
        activeDataTab.value = topicConfigs.value[0].topic_name
      }
      topicConfigs.value.forEach(config => {
        topicData[config.topic_name] = { has_data: false, data: null, timestamp: null, original_timestamp: null }
        topicLoading[config.topic_name] = false
      })
      topicConfigs.value.forEach(config => {
        loadTopicData(config.topic_name)
      })
      if (autoRefresh.value) {
        startAutoRefresh()
      }
    }
  } catch (error) {
    message.error('加载设备Topic配置失败')
  }
}

const loadTopicData = async (topicName, showLoading = true) => {
  try {
    if (showLoading) topicLoading[topicName] = true
    const res = await deviceAPI.getLatestCompressedData({ topic: topicName })
    if (res.data) topicData[topicName] = res.data
  } catch (error) {
    if (showLoading) message.error(`加载Topic ${topicName} 数据失败`)
  } finally {
    if (showLoading) topicLoading[topicName] = false
  }
}

const startAutoRefresh = () => {
  stopAutoRefresh()
  if (autoRefresh.value && topicConfigs.value.length > 0) {
    refreshTimer = setInterval(() => {
      topicConfigs.value.forEach(config => {
        loadTopicData(config.topic_name, false)
      })
    }, refreshInterval.value)
  }
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

const loadDeviceStatus = async () => {
  if (!currentDevice.device_code) return
  try {
    statusLoading.value = true
    const res = await deviceAPI.getDeviceMonitorStatus(currentDevice.device_code)
    if (res.data) {
      Object.assign(deviceStatus, res.data.status)
      alarmCount.value = res.data.alarm_count || 0
      const now = new Date()
      lastStatusUpdateTime.value = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      if (res.data.rule_match_details) {
        Object.assign(ruleMatchDetails, res.data.rule_match_details)
      }
      statusErrors.value = res.data.status_errors || []
      hasStatusErrors.value = res.data.has_errors || false
      if (res.data.current_part) {
        currentPart.part_number = res.data.current_part.part_number
        currentPart.u9_material_code = res.data.current_part.u9_material_code
        currentPart.start_code = res.data.current_part.start_code
        currentPart.order_info = res.data.current_part.order_info
        if (currentPart.part_number && !currentPart.order_info) {
          await loadOrderInfo(currentPart.part_number, currentPart.u9_material_code)
        }
      }
    }
  } catch (error) {
    console.error('加载设备状态失败:', error)
  } finally {
    statusLoading.value = false
  }
}

const loadOrderInfo = async (partNumber, u9MaterialCode) => {
  if (!partNumber && !u9MaterialCode) return
  try {
    const res = await erpOrderAPI.queryTodayOrderByPart(partNumber, u9MaterialCode)
    if (res.data && res.data.success) {
      currentPart.order_info = {
        planned_output: res.data.planned_output,
        order_count: res.data.order_count,
        details: res.data.details || []
      }
    }
  } catch (error) {
    console.error('查询订单信息失败:', error)
  }
}

const startStatusAutoRefresh = () => {
  stopStatusAutoRefresh()
  statusRefreshTimer = setInterval(() => {
    loadDeviceStatus()
  }, 10000)
}

const stopStatusAutoRefresh = () => {
  if (statusRefreshTimer) {
    clearInterval(statusRefreshTimer)
    statusRefreshTimer = null
  }
}

const getOrderStatusClass = (status) => {
  const classMap = { 'created': 'status-created', 'released': 'status-released', 'in_progress': 'status-progress', 'completed': 'status-completed', 'closed': 'status-closed' }
  return classMap[status] || 'status-default'
}

const getOrderStatusText = (status) => {
  const textMap = { 'created': '已创建', 'released': '已发放', 'in_progress': '生产中', 'completed': '已完成', 'closed': '已关闭' }
  return textMap[status] || status || '未知'
}

// 监听数据采集弹窗关闭
watch(dataCollectionDialogVisible, (newVal) => {
  if (!newVal) {
    stopAutoRefresh()
    stopStatusAutoRefresh()
    activeDataTab.value = ''
    topicConfigs.value = []
    Object.keys(topicData).forEach(key => delete topicData[key])
    Object.keys(topicLoading).forEach(key => delete topicLoading[key])
    Object.assign(deviceStatus, {
      processing: false, mold_change: false, fault: false, alarm: false,
      material_shortage: false, stop: false, plan_stop: false
    })
    alarmCount.value = 0
    Object.keys(ruleMatchDetails).forEach(key => delete ruleMatchDetails[key])
    statusErrors.value = []
    hasStatusErrors.value = false
    currentPart.part_number = null
    currentPart.u9_material_code = null
    currentPart.start_code = null
    currentPart.order_info = null
  }
})

// 监听状态监控配置弹窗关闭，刷新设备状态
watch(statusMonitorConfigDialogVisible, async (newVal) => {
  if (!newVal && currentDevice.device_code) {
    await loadDeviceStatus()
  }
})

watch(autoRefresh, (newVal) => {
  if (newVal) { startAutoRefresh() } else { stopAutoRefresh() }
})

watch(refreshInterval, () => {
  if (autoRefresh.value) startAutoRefresh()
})

watch(activeDataTab, (newTab) => {
  if (newTab && topicData[newTab] && !topicData[newTab].has_data) {
    loadTopicData(newTab)
  }
})

// 生命周期
onMounted(async () => {
  await loadDevices()
  await loadDeviceStats()
})

const handleCurveResize = () => {
  newRule.parameter_points.forEach(point => {
    if (point.curveChart) point.curveChart.resize()
  })
}
window.addEventListener('resize', handleCurveResize)

onUnmounted(() => {
  newRule.parameter_points.forEach(point => {
    stopCurveCollect(point)
    if (point.curveChart) {
      point.curveChart.dispose()
      point.curveChart = null
    }
  })
  Object.values(curveChartRefs).forEach(el => {
    if (el) {
      const instance = echarts.getInstanceByDom(el)
      if (instance) instance.dispose()
    }
  })
  window.removeEventListener('resize', handleCurveResize)
})
</script>
