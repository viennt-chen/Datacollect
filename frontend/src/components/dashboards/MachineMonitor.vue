<template>
  <div class="machine-monitor" :class="{ 'fullscreen-mode': isFullscreen }">
    <!-- 第一行：设备状态概览 -->
    <div class="row row-1">
      <!-- 设备 KPI -->
      <div class="panel kpi-panel">
        <div class="panel-header">
          <i class="mdi mdi-speedometer"></i>
          <span>设备 KPI</span>
        </div>
        <div class="panel-body">
          <div class="kpi-grid">
            <div class="kpi-item">
              <div class="kpi-icon" style="background: linear-gradient(135deg, #00d4ff, #0099ff)">
                <i class="mdi mdi-cpu-64-bit"></i>
              </div>
              <div class="kpi-info">
                <div class="kpi-label">设备总数</div>
                <div class="kpi-value">{{ deviceList.length }}</div>
                <div class="kpi-sub">
                  <span class="kpi-sub-item" v-for="(count, type) in deviceTypeStats" :key="type">
                    {{ type }}: {{ count }}
                  </span>
                </div>
              </div>
            </div>
            <div class="kpi-item">
              <div class="kpi-icon" style="background: linear-gradient(135deg, #00ff88, #00cc6a)">
                <i class="mdi mdi-cog"></i>
              </div>
              <div class="kpi-info">
                <div class="kpi-label">运行设备</div>
                <div class="kpi-value">{{ processingCount }}</div>
                <div class="kpi-trend up">
                  <i class="mdi mdi-arrow-up"></i>
                  {{ runningRate }}%
                </div>
              </div>
            </div>
            <div class="kpi-item">
              <div class="kpi-icon" style="background: linear-gradient(135deg, #00d4ff, #0099ff)">
                <i class="mdi mdi-heart-pulse"></i>
              </div>
              <div class="kpi-info">
                <div class="kpi-label">平均 OEE</div>
                <div class="kpi-value">{{ avgOee }}%</div>
              </div>
            </div>
            <div class="kpi-item">
              <div class="kpi-icon" style="background: linear-gradient(135deg, #00ff88, #00cc6a)">
                <i class="mdi mdi-play-circle"></i>
              </div>
              <div class="kpi-info">
                <div class="kpi-label">计划加工</div>
                <div class="kpi-value">{{ processingCount }}</div>
              </div>
            </div>
            <div class="kpi-item">
              <div class="kpi-icon" style="background: linear-gradient(135deg, #8899aa, #667788)">
                <i class="mdi mdi-pause-circle"></i>
              </div>
              <div class="kpi-info">
                <div class="kpi-label">计划停机</div>
                <div class="kpi-value">{{ stopCount }}</div>
              </div>
            </div>
            <div class="kpi-item">
              <div class="kpi-icon" style="background: linear-gradient(135deg, #ff4444, #ff2222)">
                <i class="mdi mdi-alert"></i>
              </div>
              <div class="kpi-info">
                <div class="kpi-label">故障停机</div>
                <div class="kpi-value">{{ faultStopCount }}</div>
              </div>
            </div>
            <div class="kpi-item">
              <div class="kpi-icon" style="background: linear-gradient(135deg, #ff2222, #cc0000)">
                <i class="mdi mdi-shield-alert"></i>
              </div>
              <div class="kpi-info">
                <div class="kpi-label">紧急停机</div>
                <div class="kpi-value">{{ emergencyStopCount }}</div>
              </div>
            </div>
            <div class="kpi-item">
              <div class="kpi-icon" style="background: linear-gradient(135deg, #8899aa, #667788)">
                <i class="mdi mdi-refresh"></i>
              </div>
              <div class="kpi-info">
                <div class="kpi-label">换模</div>
                <div class="kpi-value">{{ moldChangeCount }}</div>
              </div>
            </div>
            <div class="kpi-item">
              <div class="kpi-icon" style="background: linear-gradient(135deg, #a855f7, #7c3aed)">
                <i class="mdi mdi-wrench"></i>
              </div>
              <div class="kpi-info">
                <div class="kpi-label">维护</div>
                <div class="kpi-value">{{ maintainCount }}</div>
              </div>
            </div>
            <div class="kpi-item">
              <div class="kpi-icon" style="background: linear-gradient(135deg, #E6A23C, #d4910a)">
                <i class="mdi mdi-bell"></i>
              </div>
              <div class="kpi-info">
                <div class="kpi-label">报警</div>
                <div class="kpi-value">{{ alarmCount }}</div>
              </div>
            </div>
            <div class="kpi-item">
              <div class="kpi-icon" style="background: linear-gradient(135deg, #E6A23C, #d4910a)">
                <i class="mdi mdi-package-variant-closed"></i>
              </div>
              <div class="kpi-info">
                <div class="kpi-label">缺料</div>
                <div class="kpi-value">{{ materialShortageCount }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 设备状态分布 -->
      <div class="panel">
        <div class="panel-header">
          <i class="mdi mdi-chart-pie"></i>
          <span>设备状态分布</span>
        </div>
        <div class="panel-body">
          <div ref="statusPieEl" class="pie-chart"></div>
        </div>
      </div>

      <!-- 设备产出排行 -->
      <div class="panel">
        <div class="panel-header">
          <i class="mdi mdi-chart-bar"></i>
          <span>设备产出排行 TOP5</span>
        </div>
        <div class="panel-body">
          <div ref="outputRankEl" class="bar-chart"></div>
        </div>
      </div>

      <!-- 设备效率对比 -->
      <div class="panel">
        <div class="panel-header">
          <i class="mdi mdi-chart-line"></i>
          <span>设备效率对比</span>
        </div>
        <div class="panel-body">
          <div ref="efficiencyEl" class="bar-chart"></div>
        </div>
      </div>
    </div>

    <!-- 第二行：设备状态明细 -->
    <div class="row row-2">
      <!-- 设备状态列表 -->
      <div class="panel wide-panel">
        <div class="panel-header">
          <i class="mdi mdi-table"></i>
          <span>设备状态明细</span>
          <div class="panel-header-actions">
            <button
              v-for="filter in statusFilters"
              :key="filter.value"
              :class="['filter-btn', { active: activeStatusFilter === filter.value }]"
              @click="activeStatusFilter = filter.value"
            >
              {{ filter.label }} ({{ filter.count }})
            </button>
          </div>
        </div>
        <div class="panel-body">
          <div class="device-grid">
            <div
              class="device-card"
              v-for="device in filteredDeviceList"
              :key="device.code"
              :class="{ 'active': device.status_type === 'processing' || device.status_type === 'scheduled processing' }"
              @click="goToDeviceDetail(device.code)"
            >
              <div class="device-header">
                <div class="device-icon" :class="'type-' + (device.type || 'default').toLowerCase()">
                  <i :class="getDeviceTypeIcon(device.type)"></i>
                </div>
                <div class="device-info">
                  <div class="device-name">{{ device.name }}</div>
                  <div class="device-code-text">{{ device.code }}</div>
                </div>
                <div class="device-status" :class="device.status">
                  <span class="status-dot" :class="device.status"></span>
                  {{ device.statusText }}
                </div>
              </div>
              <div class="device-meta">
                <span class="meta-tag" v-if="device.type">
                  <i class="mdi mdi-cpu-64-bit"></i> {{ device.type }}
                </span>
                <span class="meta-tag" v-if="device.line_code">
                  <i class="mdi mdi-sitemap"></i> {{ device.line_code }}
                </span>
                <span class="meta-tag" v-if="device.manufacturer">
                  <i class="mdi mdi-factory"></i> {{ device.manufacturer }}
                </span>
                <span class="meta-tag" v-if="device.mqtt_topics_count > 0">
                  <i class="mdi mdi-broadcast"></i> {{ device.mqtt_topics_count }} Topic
                </span>
              </div>
              <div class="device-product" v-if="device.current_product">
                <div class="product-main">
                  <i class="mdi mdi-package-variant-closed"></i>
                  <span class="product-part">{{ device.current_product.part_number }}</span>
                  <span class="product-name" v-if="device.current_product.product_name">{{ device.current_product.product_name }}</span>
                </div>
                <div class="product-order" v-if="device.current_order">
                  <span class="order-tag">
                    <i class="mdi mdi-clipboard-text"></i>
                    计划 {{ device.current_order.planned_output ?? '-' }} 件
                  </span>
                  <span class="order-tag" v-if="device.current_order.total_complete_qty != null">
                    <i class="mdi mdi-check-all"></i>
                    完成 {{ device.current_order.total_complete_qty }} 件
                  </span>
                  <span class="order-tag" v-if="device.current_order.doc_state">
                    <i class="mdi mdi-flag"></i>
                    {{ device.current_order.doc_state }}
                  </span>
                </div>
              </div>
              <div class="device-product empty" v-else>
                <i class="mdi mdi-minus-circle"></i> 暂无加工产品
              </div>
              <div class="local-order" v-if="device.local_order">
                <div class="local-order-header">
                  <i class="mdi mdi-clipboard-check"></i>
                  <span class="local-order-doc">{{ device.local_order.doc_no || '本地订单' }}</span>
                  <span class="local-order-status" :class="'status-' + device.local_order.status">
                    {{ device.local_order.status === 'completed' ? '已完成' : device.local_order.status === 'paused' ? '已暂停' : '进行中' }}
                  </span>
                </div>
                <div class="local-order-progress">
                  <div class="progress-info">
                    <span>完成 {{ device.local_order.completed_qty }} / {{ device.local_order.planned_qty }}</span>
                    <span class="progress-rate">{{ device.local_order.completion_rate }}%</span>
                  </div>
                  <div class="progress-track">
                    <div class="progress-fill" :style="{ width: Math.min(device.local_order.completion_rate, 100) + '%' }"></div>
                  </div>
                </div>
                <div class="local-order-qty">
                  <span class="qty-item"><i class="mdi mdi-check-circle"></i> 合格 {{ device.local_order.eligible_qty }}</span>
                  <span class="qty-item scrap" v-if="device.local_order.scrap_qty > 0"><i class="mdi mdi-close-circle"></i> 报废 {{ device.local_order.scrap_qty }}</span>
                </div>
              </div>
              <div class="device-data">
                <div class="data-item">
                  <div class="data-label">OEE</div>
                  <div class="data-value">{{ device.oee }}%</div>
                </div>
                <div class="data-item">
                  <div class="data-label">可用率</div>
                  <div class="data-value">{{ device.availability }}%</div>
                </div>
                <div class="data-item">
                  <div class="data-label">性能率</div>
                  <div class="data-value">{{ device.performance }}%</div>
                </div>
                <div class="data-item">
                  <div class="data-label">合格率</div>
                  <div class="data-value">{{ device.quality }}%</div>
                </div>
              </div>
              <div class="device-progress">
                <div class="progress-bar">
                  <div
                    class="progress-value"
                    :style="{ width: device.oee + '%', background: getOeeColor(device.oee) }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 第三行：趋势分析 -->
    <div class="row row-3">
      <!-- 设备运行趋势 -->
      <div class="panel">
        <div class="panel-header">
          <i class="mdi mdi-heart-pulse"></i>
          <span>24 小时运行趋势</span>
        </div>
        <div class="panel-body">
          <div ref="trendEl" class="line-chart"></div>
        </div>
      </div>

      <!-- 停机原因分析 -->
      <div class="panel">
        <div class="panel-header">
          <i class="mdi mdi-history"></i>
          <span>停机原因分析</span>
        </div>
        <div class="panel-body">
          <div ref="downtimeEl" class="pie-chart"></div>
        </div>
      </div>

      <!-- 维护记录 -->
      <div class="panel">
        <div class="panel-header">
          <i class="mdi mdi-wrench"></i>
          <span>最近维护记录</span>
        </div>
        <div class="panel-body">
          <div class="maintenance-list">
            <div class="maintenance-item" v-for="(item, index) in maintenanceList" :key="index">
              <div class="maintenance-icon">
                <i class="mdi mdi-check-circle"></i>
              </div>
              <div class="maintenance-content">
                <div class="maintenance-title">{{ item.title }}</div>
                <div class="maintenance-desc">{{ item.desc }}</div>
                <div class="maintenance-time">{{ item.time }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { dashboardApi } from '@/api/index'

const router = useRouter()

const props = defineProps({
  timeRange: {
    type: String,
    default: '7'
  },
  isFullscreen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:lastUpdate'])

const statusPieEl = ref(null)
const outputRankEl = ref(null)
const efficiencyEl = ref(null)
const trendEl = ref(null)
const downtimeEl = ref(null)

let statusPie = null
let outputRank = null
let efficiency = null
let trend = null
let downtime = null

const deviceList = ref([])
const loading = ref(false)
const activeStatusFilter = ref('all')

const maintenanceList = ref([
  { title: '定期检查完成', desc: '设备维护完成', time: '2026-04-13 13:43' },
  { title: '定期检查完成', desc: '设备维护完成', time: '2026-04-13 07:45' },
  { title: '紧急维修', desc: '设备传感器更换', time: '2026-04-13 07:21' }
])

const hasStatus = (d, ...types) => {
  const parts = d.status_parts || []
  return types.some(t => parts.includes(t))
}
const processingCount = computed(() => deviceList.value.filter(d => hasStatus(d, 'processing', 'scheduled processing')).length)
const stopCount = computed(() => deviceList.value.filter(d => hasStatus(d, 'stop', 'scheduled outage')).length)
const faultStopCount = computed(() => deviceList.value.filter(d => hasStatus(d, 'fault_stop')).length)
const emergencyStopCount = computed(() => deviceList.value.filter(d => hasStatus(d, 'emergency stop')).length)
const moldChangeCount = computed(() => deviceList.value.filter(d => hasStatus(d, 'mold_change')).length)
const maintainCount = computed(() => deviceList.value.filter(d => hasStatus(d, 'maintain')).length)
const alarmCount = computed(() => deviceList.value.filter(d => hasStatus(d, 'alarm')).length)
const materialShortageCount = computed(() => deviceList.value.filter(d => hasStatus(d, 'material_shortage')).length)
const runningRate = computed(() => deviceList.value.length > 0 ? Math.round((processingCount.value / deviceList.value.length) * 100) : 0)
const avgOee = computed(() => {
  if (deviceList.value.length === 0) return 0
  const total = deviceList.value.reduce((sum, d) => sum + d.oee, 0)
  return Math.round(total / deviceList.value.length * 10) / 10
})

const deviceTypeStats = computed(() => {
  const stats = {}
  deviceList.value.forEach(d => {
    const type = d.type || '未分类'
    stats[type] = (stats[type] || 0) + 1
  })
  return stats
})

const statusFilters = computed(() => [
  { value: 'all', label: '全部', count: deviceList.value.length },
  { value: 'processing', label: '计划加工', count: processingCount.value },
  { value: 'stop', label: '计划停机', count: stopCount.value },
  { value: 'fault_stop', label: '故障停机', count: faultStopCount.value },
  { value: 'emergency stop', label: '紧急停机', count: emergencyStopCount.value },
  { value: 'mold_change', label: '换模', count: moldChangeCount.value },
  { value: 'maintain', label: '维护', count: maintainCount.value },
  { value: 'alarm', label: '报警', count: alarmCount.value },
  { value: 'material_shortage', label: '缺料', count: materialShortageCount.value }
])

const filteredDeviceList = computed(() => {
  if (activeStatusFilter.value === 'all') return deviceList.value
  const filter = activeStatusFilter.value
  return deviceList.value.filter(d => {
    const parts = d.status_parts || []
    if (parts.includes(filter)) return true
    if (filter === 'processing' && (parts.includes('scheduled processing'))) return true
    if (filter === 'stop' && (parts.includes('scheduled outage'))) return true
    return false
  })
})

const goToDeviceDetail = (deviceCode) => {
  router.push({
    path: '/device-detail',
    query: { code: deviceCode }
  })
}

const getDeviceTypeIcon = (type) => {
  const icons = {
    'CNC': 'mdi mdi-cog',
    'Robot': 'mdi mdi-robot',
    'PLC': 'mdi mdi-cpu-64-bit',
    'Sensor': 'mdi mdi-broadcast',
  }
  return icons[type] || 'mdi mdi-cog'
}

const loadMachineData = async () => {
  loading.value = true
  try {
    const response = await dashboardApi.getMachineMonitorData({
      days: parseInt(props.timeRange) || 7
    })
    
    if (response.data && response.data.devices) {
      deviceList.value = response.data.devices
    }
  } catch (error) {
    console.error('加载设备监控数据失败:', error)
  } finally {
    loading.value = false
  }
}

const getOeeColor = (oee) => {
  if (oee >= 85) return 'linear-gradient(90deg, #00ff88, #00cc6a)'
  if (oee >= 70) return 'linear-gradient(90deg, #00d4ff, #0099ff)'
  if (oee >= 60) return 'linear-gradient(90deg, #ffaa00, #ff8800)'
  return 'linear-gradient(90deg, #ff4444, #ff2222)'
}

const initStatusPie = () => {
  if (!statusPieEl.value) return
  
  statusPie = echarts.init(statusPieEl.value)
  
  const option = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'right', textStyle: { color: '#8899aa' } },
    series: [
      {
        name: '设备状态',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        itemStyle: { borderRadius: 10, borderColor: '#1a2a3a', borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold', color: '#fff' } },
        data: [
          { value: processingCount.value, name: '计划加工', itemStyle: { color: '#00ff88' } },
          { value: stopCount.value, name: '计划停机', itemStyle: { color: '#8899aa' } },
          { value: faultStopCount.value, name: '故障停机', itemStyle: { color: '#ff4444' } },
          { value: emergencyStopCount.value, name: '紧急停机', itemStyle: { color: '#ff2222' } },
          { value: moldChangeCount.value, name: '换模', itemStyle: { color: '#667788' } },
          { value: maintainCount.value, name: '维护', itemStyle: { color: '#aa64ff' } },
          { value: alarmCount.value, name: '报警', itemStyle: { color: '#E6A23C' } },
          { value: materialShortageCount.value, name: '缺料', itemStyle: { color: '#E6A23C' } }
        ]
      }
    ]
  }
  
  statusPie.setOption(option)
}

const initOutputRank = () => {
  if (!outputRankEl.value) return
  
  outputRank = echarts.init(outputRankEl.value)
  
  const sortedDevices = [...deviceList.value].sort((a, b) => b.total_events - a.total_events).slice(0, 5)
  
  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: '5%', left: '3%', right: '10%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'value',
      name: '次',
      nameTextStyle: { color: '#8899aa' },
      axisLabel: { color: '#8899aa' },
      splitLine: { lineStyle: { color: '#2a3a5a' } }
    },
    yAxis: {
      type: 'category',
      data: sortedDevices.map(d => d.name),
      axisLabel: { color: '#8899aa' },
      splitLine: { show: false }
    },
    series: [
      {
        type: 'bar',
        data: sortedDevices.map(d => d.total_events),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#00d4ff' },
            { offset: 1, color: '#0099ff' }
          ]),
          borderRadius: [0, 4, 4, 0]
        }
      }
    ]
  }
  
  outputRank.setOption(option)
}

const initEfficiency = () => {
  if (!efficiencyEl.value) return
  
  efficiency = echarts.init(efficiencyEl.value)
  
  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['可用率', '性能率', '合格率'], textStyle: { color: '#8899aa' }, top: 0 },
    grid: { top: '15%', left: '3%', right: '10%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: deviceList.value.map(d => d.name),
      axisLabel: { color: '#8899aa', rotate: 45 },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      name: '%',
      nameTextStyle: { color: '#8899aa' },
      axisLabel: { color: '#8899aa' },
      splitLine: { lineStyle: { color: '#2a3a5a' } }
    },
    series: [
      {
        name: '可用率',
        type: 'bar',
        stack: 'total',
        data: deviceList.value.map(d => d.availability),
        itemStyle: { color: '#00d4ff' }
      },
      {
        name: '性能率',
        type: 'bar',
        stack: 'total',
        data: deviceList.value.map(d => d.performance),
        itemStyle: { color: '#00ff88' }
      },
      {
        name: '合格率',
        type: 'bar',
        stack: 'total',
        data: deviceList.value.map(d => d.quality),
        itemStyle: { color: '#ffaa00' }
      }
    ]
  }
  
  efficiency.setOption(option)
}

const initTrend = () => {
  if (!trendEl.value) return
  
  trend = echarts.init(trendEl.value)
  
  const option = {
    tooltip: { trigger: 'axis' },
    grid: { top: '10%', left: '3%', right: '10%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: ['00', '04', '08', '12', '16', '20'],
      axisLabel: { color: '#8899aa' },
      splitLine: { lineStyle: { color: '#2a3a5a' } }
    },
    yAxis: {
      type: 'value',
      name: '运行设备数',
      nameTextStyle: { color: '#8899aa' },
      axisLabel: { color: '#8899aa' },
      splitLine: { lineStyle: { color: '#2a3a5a' } }
    },
    series: [
      {
        name: '运行设备',
        type: 'line',
        smooth: true,
        data: [runningCount.value, runningCount.value + 1, runningCount.value + 2, runningCount.value + 1, runningCount.value + 2, runningCount.value],
        itemStyle: { color: '#00d4ff' },
        lineStyle: { width: 3, color: '#00d4ff' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 212, 255, 0.3)' },
            { offset: 1, color: 'rgba(0, 212, 255, 0.01)' }
          ])
        }
      }
    ]
  }
  
  trend.setOption(option)
}

const initDowntime = () => {
  if (!downtimeEl.value) return
  
  downtime = echarts.init(downtimeEl.value)
  
  const option = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'right', textStyle: { color: '#8899aa' } },
    series: [
      {
        name: '停机原因',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        itemStyle: { borderRadius: 10, borderColor: '#1a2a3a', borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold', color: '#fff' } },
        data: [
          { value: faultStopCount.value + emergencyStopCount.value, name: '设备故障', itemStyle: { color: '#ff4444' } },
          { value: stopCount.value + moldChangeCount.value, name: '计划停机', itemStyle: { color: '#00d4ff' } },
          { value: maintainCount.value, name: '维护保养', itemStyle: { color: '#00ff88' } },
          { value: alarmCount.value + materialShortageCount.value, name: '报警/缺料', itemStyle: { color: '#E6A23C' } }
        ]
      }
    ]
  }
  
  downtime.setOption(option)
}

const initAllCharts = () => {
  initStatusPie()
  initOutputRank()
  initEfficiency()
  initTrend()
  initDowntime()
}

const resizeCharts = () => {
  statusPie?.resize()
  outputRank?.resize()
  efficiency?.resize()
  trend?.resize()
  downtime?.resize()
}

watch(() => props.timeRange, () => {
  loadMachineData()
})

watch(() => props.isFullscreen, () => {
  setTimeout(() => {
    resizeCharts()
  }, 300)
})

watch(deviceList, () => {
  setTimeout(() => {
    initAllCharts()
  }, 100)
}, { deep: true })

onMounted(() => {
  loadMachineData()
  window.addEventListener('resize', resizeCharts)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
  statusPie?.dispose()
  outputRank?.dispose()
  efficiency?.dispose()
  trend?.dispose()
  downtime?.dispose()
})
</script>

<style scoped>
.machine-monitor {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a1628 0%, #1a2a4a 50%, #0a1628 100%);
  padding: 12px;
}

.row {
  display: grid;
  gap: 12px;
  margin-bottom: 12px;
}

.row-1 {
  grid-template-columns: 1.2fr 1fr 1fr 1fr;
}

.row-2 {
  grid-template-columns: 1fr;
}

.row-3 {
  grid-template-columns: 1fr 1fr 1fr;
}

.panel {
  background: rgba(10, 30, 60, 0.6);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 8px;
  overflow: hidden;
  backdrop-filter: blur(10px);
  box-shadow: 0 0 30px rgba(0, 212, 255, 0.1);
}

.panel-header {
  padding: 12px 16px;
  background: linear-gradient(90deg, rgba(0, 212, 255, 0.1), transparent);
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
  display: flex;
  align-items: center;
  gap: 10px;
  color: #00d4ff;
  font-size: 14px;
  font-weight: 600;
}

.panel-header-actions {
  margin-left: auto;
  display: flex;
  gap: 6px;
}

.filter-btn {
  background: rgba(0, 212, 255, 0.08);
  border: 1px solid rgba(0, 212, 255, 0.15);
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 11px;
  padding: 3px 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  background: rgba(0, 212, 255, 0.15);
  color: #fff;
}

.filter-btn.active {
  background: rgba(0, 212, 255, 0.25);
  border-color: #00d4ff;
  color: #00d4ff;
}

.panel-body {
  padding: 16px;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}

.kpi-item {
  background: rgba(0, 212, 255, 0.05);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 8px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.kpi-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kpi-icon i {
  font-size: 24px;
  color: #fff;
}

.kpi-info {
  flex: 1;
}

.kpi-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 4px;
}

.kpi-value {
  font-size: 24px;
  font-weight: bold;
  color: #fff;
  line-height: 1;
}

.kpi-trend {
  font-size: 12px;
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.kpi-trend.up {
  color: #00ff88;
}

.kpi-sub {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 4px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.kpi-sub-item {
  background: rgba(0, 212, 255, 0.1);
  padding: 1px 6px;
  border-radius: 3px;
}

.pie-chart,
.bar-chart,
.line-chart {
  width: 100%;
  height: 220px;
}

.device-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.device-card {
  background: rgba(0, 212, 255, 0.05);
  border: 1px solid rgba(0, 212, 255, 0.1);
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s;
  cursor: pointer;
}

.device-card:hover {
  background: rgba(0, 212, 255, 0.1);
  border-color: rgba(0, 212, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 212, 255, 0.2);
}

.device-card.active {
  background: rgba(0, 255, 136, 0.08);
  border-color: rgba(0, 255, 136, 0.3);
}

.device-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.device-icon {
  width: 40px;
  height: 40px;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.device-icon i {
  font-size: 20px;
  color: #00d4ff;
}

.device-icon.type-cnc { background: rgba(0, 212, 255, 0.15); }
.device-icon.type-cnc i { color: #00d4ff; }
.device-icon.type-robot { background: rgba(168, 85, 247, 0.15); }
.device-icon.type-robot i { color: #a855f7; }
.device-icon.type-plc { background: rgba(0, 255, 136, 0.15); }
.device-icon.type-plc i { color: #00ff88; }
.device-icon.type-sensor { background: rgba(255, 170, 0, 0.15); }
.device-icon.type-sensor i { color: #ffaa00; }

.device-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}

.meta-tag {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.55);
  background: rgba(0, 212, 255, 0.06);
  border: 1px solid rgba(0, 212, 255, 0.1);
  border-radius: 3px;
  padding: 2px 8px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.meta-tag i {
  font-size: 10px;
  color: #00d4ff;
}

.device-product {
  background: rgba(0, 255, 136, 0.05);
  border: 1px solid rgba(0, 255, 136, 0.12);
  border-radius: 5px;
  padding: 8px 10px;
  margin-bottom: 10px;
}

.device-product.empty {
  background: rgba(255, 255, 255, 0.03);
  border-color: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.3);
  font-size: 12px;
  text-align: center;
  padding: 6px 10px;
}

.device-product.empty i {
  margin-right: 4px;
}

.product-main {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
  color: #00ff88;
  font-size: 13px;
  font-weight: 600;
}

.product-main i {
  font-size: 14px;
}

.product-part {
  font-family: 'Courier New', monospace;
}

.product-name {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 400;
  margin-left: 2px;
}

.product-order {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 4px;
}

.order-tag {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  display: flex;
  align-items: center;
  gap: 3px;
}

.order-tag i {
  font-size: 10px;
  color: #00d4ff;
}

.local-order {
  background: rgba(0, 212, 255, 0.06);
  border: 1px solid rgba(0, 212, 255, 0.15);
  border-radius: 5px;
  padding: 8px 10px;
  margin-bottom: 10px;
}

.local-order-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
  font-size: 12px;
}

.local-order-header i {
  color: #00d4ff;
  font-size: 13px;
}

.local-order-doc {
  color: #fff;
  font-weight: 600;
  font-family: 'Courier New', monospace;
  flex: 1;
}

.local-order-status {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 3px;
}

.local-order-status.status-in_progress {
  background: rgba(0, 212, 255, 0.2);
  color: #00d4ff;
}

.local-order-status.status-completed {
  background: rgba(0, 255, 136, 0.2);
  color: #00ff88;
}

.local-order-status.status-paused {
  background: rgba(255, 170, 0, 0.2);
  color: #ffaa00;
}

.local-order-progress {
  margin-bottom: 6px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 4px;
}

.progress-rate {
  color: #00d4ff;
  font-weight: 600;
}

.progress-track {
  width: 100%;
  height: 6px;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #00d4ff, #00ff88);
  border-radius: 3px;
  transition: width 0.3s;
}

.local-order-qty {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.55);
}

.qty-item {
  display: flex;
  align-items: center;
  gap: 3px;
}

.qty-item i {
  font-size: 10px;
  color: #00ff88;
}

.qty-item.scrap i {
  color: #ff4444;
}

.device-info {
  flex: 1;
}

.device-name {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.device-code-text {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  font-family: 'Courier New', monospace;
}

.device-status {
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.device-status.running {
  background: rgba(0, 255, 136, 0.2);
  color: #00ff88;
}

.device-status.stopped {
  background: rgba(136, 153, 170, 0.2);
  color: #8899aa;
}

.device-status.maintenance {
  background: rgba(170, 100, 255, 0.2);
  color: #aa64ff;
}

.device-status.warning {
  background: rgba(230, 162, 60, 0.2);
  color: #E6A23C;
}

.device-status.error {
  background: rgba(255, 68, 68, 0.2);
  color: #ff4444;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.device-data {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 12px;
}

.data-item {
  text-align: center;
}

.data-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 4px;
}

.data-value {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.device-progress {
  margin-top: 8px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.progress-value {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s;
}

.maintenance-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.maintenance-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: rgba(0, 212, 255, 0.05);
  border-radius: 6px;
  border: 1px solid rgba(0, 212, 255, 0.1);
}

.maintenance-icon {
  font-size: 20px;
  color: #00ff88;
  flex-shrink: 0;
}

.maintenance-content {
  flex: 1;
}

.maintenance-title {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 4px;
}

.maintenance-desc {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 4px;
}

.maintenance-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

@media (max-width: 1600px) {
  .row-1 {
    grid-template-columns: 1fr 1fr;
  }

  .row-3 {
    grid-template-columns: 1fr 1fr;
  }

  .kpi-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 1200px) {
  .row-1,
  .row-3 {
    grid-template-columns: 1fr;
  }

  .kpi-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .device-grid {
    grid-template-columns: 1fr;
  }
}
</style>
