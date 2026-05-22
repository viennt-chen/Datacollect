<template>
  <div class="device-detail-dashboard" :class="{ 'fullscreen-mode': isFullscreen }">
    <div class="page-header">
      <div class="header-left">
        <button class="back-btn" @click="goBack">
          <i class="mdi mdi-arrow-left"></i>
          <span>返回设备监控</span>
        </button>
        <h1 class="device-title">{{ deviceInfo.name || deviceCode }}</h1>
        <div class="device-meta">
          <span class="meta-item">
            <i class="mdi mdi-tag"></i>
            {{ deviceInfo.code }}
          </span>
          <span class="meta-item" v-if="deviceInfo.type">
            <i class="mdi mdi-cpu-64-bit"></i>
            {{ deviceInfo.type }}
          </span>
          <span class="meta-item" v-if="deviceInfo.model">
            <i class="mdi mdi-harddisk"></i>
            {{ deviceInfo.model }}
          </span>
          <span class="meta-item" v-if="deviceInfo.manufacturer">
            <i class="mdi mdi-factory"></i>
            {{ deviceInfo.manufacturer }}
          </span>
          <span class="meta-item" v-if="deviceInfo.line_code">
            <i class="mdi mdi-sitemap"></i>
            {{ deviceInfo.line_code }}
          </span>
          <span class="meta-item" v-if="deviceInfo.location">
            <i class="mdi mdi-map-marker"></i>
            {{ deviceInfo.location }}
          </span>
          <span class="meta-item" v-if="deviceInfo.mqtt_topics_count > 0">
            <i class="mdi mdi-broadcast"></i>
            {{ deviceInfo.mqtt_topics_count }} Topic
          </span>
          <span :class="['status-badge', deviceInfo.status]">
            <span class="status-dot" :class="deviceInfo.status"></span>
            {{ deviceInfo.statusText }}
          </span>
        </div>
      </div>
      <div class="header-right">
        <button class="fullscreen-btn" @click="toggleFullscreen" :title="isFullscreen ? '退出全屏' : '全屏显示'">
          <i :class="isFullscreen ? 'mdi mdi-fullscreen-exit' : 'mdi mdi-fullscreen'"></i>
          <span>{{ isFullscreen ? '退出全屏' : '全屏' }}</span>
        </button>
      </div>
    </div>

    <div class="dashboard-content">
      <div class="row row-1">
        <div class="panel kpi-panel">
          <div class="panel-header">
            <i class="mdi mdi-speedometer"></i>
            <span>关键 KPI</span>
          </div>
          <div class="panel-body">
            <div class="kpi-grid">
              <div class="kpi-item">
                <div class="kpi-icon" style="background: linear-gradient(135deg, #00ff88, #00cc6a)">
                  <i class="mdi mdi-package-variant-closed"></i>
                </div>
                <div class="kpi-info">
                  <div class="kpi-label">今日产量</div>
                  <div class="kpi-value">{{ kpiData.todayOutput.toLocaleString() }}</div>
                  <div class="kpi-unit">件</div>
                </div>
              </div>
              <div class="kpi-item">
                <div class="kpi-icon" style="background: linear-gradient(135deg, #00d4ff, #0099ff)">
                  <i class="mdi mdi-check-circle"></i>
                </div>
                <div class="kpi-info">
                  <div class="kpi-label">合格数量</div>
                  <div class="kpi-value">{{ kpiData.qualifiedCount.toLocaleString() }}</div>
                  <div class="kpi-unit">件</div>
                </div>
              </div>
              <div class="kpi-item">
                <div class="kpi-icon" style="background: linear-gradient(135deg, #ffaa00, #ff8800)">
                  <i class="mdi mdi-clock"></i>
                </div>
                <div class="kpi-info">
                  <div class="kpi-label">平均节拍</div>
                  <div class="kpi-value">{{ kpiData.avgCycleTime }}</div>
                  <div class="kpi-unit">秒/件</div>
                </div>
              </div>
              <div class="kpi-item">
                <div class="kpi-icon" style="background: linear-gradient(135deg, #ff4444, #ff2222)">
                  <i class="mdi mdi-alert"></i>
                </div>
                <div class="kpi-info">
                  <div class="kpi-label">报警次数</div>
                  <div class="kpi-value">{{ kpiData.alarmCount }}</div>
                  <div class="kpi-unit">次</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="panel current-product-panel">
          <div class="panel-header">
            <i class="mdi mdi-package-variant"></i>
            <span>当前加工产品</span>
          </div>
          <div class="panel-body">
            <div v-if="currentPart.part_number" class="current-product-info">
              <div class="product-item">
                <div class="product-label">零件号</div>
                <div class="product-value product-number">{{ currentPart.part_number }}</div>
              </div>
              <div class="product-item" v-if="currentPart.product_name">
                <div class="product-label">产品名称</div>
                <div class="product-value">{{ currentPart.product_name }}</div>
              </div>
              <div class="product-item" v-if="currentPart.u9_material_code">
                <div class="product-label">U9物料号</div>
                <div class="product-value">{{ currentPart.u9_material_code }}</div>
              </div>
            </div>
            <div v-else class="no-product">
              <i class="mdi mdi-inbox"></i>
              <span>暂无加工产品</span>
            </div>
          </div>
        </div>

        <div class="panel order-panel">
          <div class="panel-header">
            <i class="mdi mdi-clipboard-text"></i>
            <span>订单信息</span>
          </div>
          <div class="panel-body">
            <div v-if="currentOrder" class="order-info">
              <div class="order-item">
                <div class="order-label">单据编号</div>
                <div class="order-value">{{ currentOrder.doc_no || '-' }}</div>
              </div>
              <div class="order-item">
                <div class="order-label">计划数量</div>
                <div class="order-value highlight">{{ currentOrder.planned_output ?? '-' }} <small>件</small></div>
              </div>
              <div class="order-item" v-if="currentOrder.product_qty != null">
                <div class="order-label">订单数量</div>
                <div class="order-value">{{ currentOrder.product_qty }} <small>件</small></div>
              </div>
              <div class="order-item" v-if="currentOrder.total_complete_qty != null">
                <div class="order-label">累计完成</div>
                <div class="order-value">{{ currentOrder.total_complete_qty }} <small>件</small></div>
              </div>
              <div class="order-item" v-if="currentOrder.total_eligible_qty != null">
                <div class="order-label">合格数量</div>
                <div class="order-value">{{ currentOrder.total_eligible_qty }} <small>件</small></div>
              </div>
              <div class="order-item" v-if="currentOrder.doc_state">
                <div class="order-label">单据状态</div>
                <div class="order-value">
                  <span class="doc-state-tag" :class="currentOrder.doc_state">{{ currentOrder.doc_state }}</span>
                </div>
              </div>
              <div class="order-item" v-if="currentOrder.line_code">
                <div class="order-label">产线</div>
                <div class="order-value">{{ currentOrder.line_code }}</div>
              </div>
              <div class="order-item" v-if="currentOrder.mold_no">
                <div class="order-label">模具号</div>
                <div class="order-value">{{ currentOrder.mold_no }}</div>
              </div>
              <div class="order-progress" v-if="currentOrder.planned_output && currentOrder.total_complete_qty != null">
                <div class="progress-label">
                  <span>完成进度</span>
                  <span>{{ currentOrder.total_complete_qty }} / {{ currentOrder.planned_output }}</span>
                </div>
                <div class="progress-bar">
                  <div class="progress-value" :style="{ width: Math.min((currentOrder.total_complete_qty / currentOrder.planned_output) * 100, 100) + '%' }"></div>
                </div>
              </div>
            </div>
            <div v-else class="no-product">
              <i class="mdi mdi-inbox"></i>
              <span>暂无订单信息</span>
            </div>
          </div>
        </div>

        <div class="panel local-order-panel">
          <div class="panel-header">
            <i class="mdi mdi-clipboard-check"></i>
            <span>本地加工记录</span>
            <span class="local-order-status-tag" :class="'tag-' + localOrder.status" v-if="localOrder.status">
              {{ localOrder.status === 'completed' ? '已完成' : localOrder.status === 'paused' ? '已暂停' : '进行中' }}
            </span>
          </div>
          <div class="panel-body">
            <div v-if="localOrder.id" class="local-order-info">
              <div class="local-order-doc">
                <i class="mdi mdi-receipt"></i>
                <span>{{ localOrder.doc_no || '无单据号' }}</span>
              </div>
              <div class="local-order-quantities">
                <div class="lq-item">
                  <div class="lq-label">计划</div>
                  <div class="lq-value">{{ localOrder.planned_qty ?? '-' }}</div>
                </div>
                <div class="lq-item">
                  <div class="lq-label">完成</div>
                  <div class="lq-value highlight">{{ localOrder.completed_qty }}</div>
                </div>
                <div class="lq-item">
                  <div class="lq-label">合格</div>
                  <div class="lq-value success">{{ localOrder.eligible_qty }}</div>
                </div>
                <div class="lq-item" v-if="localOrder.scrap_qty > 0">
                  <div class="lq-label">报废</div>
                  <div class="lq-value danger">{{ localOrder.scrap_qty }}</div>
                </div>
              </div>
              <div class="local-order-progress" v-if="localOrder.planned_qty > 0">
                <div class="lo-progress-label">
                  <span>完成进度</span>
                  <span class="lo-progress-rate">{{ localOrder.completion_rate }}%</span>
                </div>
                <div class="lo-progress-bar">
                  <div class="lo-progress-fill" :style="{ width: Math.min(localOrder.completion_rate, 100) + '%' }"></div>
                </div>
              </div>
            </div>
            <div v-else class="no-product">
              <i class="mdi mdi-inbox"></i>
              <span>暂无本地加工记录</span>
            </div>
          </div>
        </div>

        <div class="panel oee-panel">
          <div class="panel-header">
            <i class="mdi mdi-chart-pie"></i>
            <span>OEE 分析</span>
          </div>
          <div class="panel-body">
            <div ref="oeeEl" class="oee-chart"></div>
          </div>
        </div>
      </div>

      <div class="row row-2">
        <div class="panel">
          <div class="panel-header">
            <i class="mdi mdi-chart-pie"></i>
            <span>停机分类占比</span>
          </div>
          <div class="panel-body">
            <div ref="downtimeEl" class="pie-chart"></div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-header">
            <i class="mdi mdi-chart-line"></i>
            <span>合格率每小时趋势</span>
          </div>
          <div class="panel-body">
            <div ref="qualityTrendEl" class="line-chart"></div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-header">
            <i class="mdi mdi-alert-circle"></i>
            <span>质量问题分类占比</span>
          </div>
          <div class="panel-body">
            <div ref="qualityIssueEl" class="pie-chart"></div>
          </div>
        </div>
      </div>

      <div class="row row-3">
        <div class="panel wide-panel">
          <div class="panel-header">
            <i class="mdi mdi-chart-bar"></i>
            <span>每小时产量</span>
          </div>
          <div class="panel-body">
            <div ref="hourlyOutputEl" class="combo-chart"></div>
          </div>
        </div>
      </div>

      <div class="row row-4">
        <div class="panel">
          <div class="panel-header">
            <i class="mdi mdi-heart-pulse"></i>
            <span>设备状态</span>
          </div>
          <div class="panel-body">
            <div ref="deviceStatusEl" class="status-chart"></div>
          </div>
        </div>
        <div class="panel">
          <div class="panel-header">
            <i class="mdi mdi-bell"></i>
            <span>报警和故障</span>
          </div>
          <div class="panel-body">
            <div class="alarm-list">
              <div class="alarm-item" v-for="(alarm, index) in alarmList" :key="index" :class="alarm.level">
                <div class="alarm-icon">
                  <i :class="alarm.level === 'error' ? 'mdi mdi-close-circle' : 'mdi mdi-alert'"></i>
                </div>
                <div class="alarm-content">
                  <div class="alarm-title">{{ alarm.title }}</div>
                  <div class="alarm-desc">{{ alarm.desc }}</div>
                  <div class="alarm-time">{{ alarm.time }}</div>
                </div>
              </div>
              <div v-if="alarmList.length === 0" class="empty-state">
                <i class="mdi mdi-check-circle"></i>
                <span>暂无报警记录</span>
              </div>
            </div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-header">
            <i class="mdi mdi-timer"></i>
            <span>节拍</span>
          </div>
          <div class="panel-body">
            <div ref="cycleTimeEl" class="line-chart"></div>
          </div>
        </div>
      </div>

      <div class="row row-5">
        <div class="panel wide-panel">
          <div class="panel-header">
            <i class="mdi mdi-format-list-bulleted"></i>
            <span>生产事件</span>
          </div>
          <div class="panel-body">
            <div class="event-list-scroll" ref="eventListEl">
              <div class="event-item" v-for="(event, index) in eventList" :key="index">
                <div class="event-time">{{ event.time }}</div>
                <div class="event-code">{{ event.code }}</div>
                <div class="event-duration">{{ event.duration }}</div>
                <div class="event-status" :class="event.status">{{ event.statusText }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { dashboardApi, deviceAPI } from '@/api/index'

const route = useRoute()
const router = useRouter()

const deviceCode = ref(route.query.code || '')
const deviceIdentifier = ref(null)
const deviceInfo = reactive({
  code: '',
  name: '',
  type: '',
  status: 'running',
  statusText: '运行中'
})

const oeeEl = ref(null)
const downtimeEl = ref(null)
const qualityTrendEl = ref(null)
const qualityIssueEl = ref(null)
const hourlyOutputEl = ref(null)
const deviceStatusEl = ref(null)
const cycleTimeEl = ref(null)
const eventListEl = ref(null)

let oeeChart = null
let downtimeChart = null
let qualityTrendChart = null
let qualityIssueChart = null
let hourlyOutputChart = null
let deviceStatusChart = null
let cycleTimeChart = null

const kpiData = reactive({
  todayOutput: 0,
  qualifiedCount: 0,
  avgCycleTime: 0,
  alarmCount: 0
})

const alarmList = ref([])
const eventList = ref([])
const activeStatuses = ref([])
const isFullscreen = ref(false)
let eventScrollTimer = null
let refreshTimer = null
let monitorStatusTimer = null
let previousEventCount = 0
let hasNewEvents = false

const currentPart = reactive({
  part_number: null,
  product_name: null,
  u9_material_code: null,
  start_code: null,
  specification: null,
  category: null,
  project: null,
  order_info: null
})

const currentOrder = reactive({
  doc_no: null,
  planned_output: null,
  product_qty: null,
  total_complete_qty: null,
  total_eligible_qty: null,
  doc_state: null,
  line_code: null,
  mold_no: null,
})

const localOrder = reactive({
  id: null,
  doc_no: null,
  part_number: null,
  planned_qty: null,
  completed_qty: 0,
  eligible_qty: 0,
  scrap_qty: 0,
  status: null,
  completion_rate: 0,
})

const goBack = () => {
  router.push({ name: 'DashboardMachine' })
}

const toggleFullscreen = async () => {
  if (!document.fullscreenElement) {
    try {
      await document.documentElement.requestFullscreen()
      isFullscreen.value = true
    } catch (error) {
      console.error('全屏失败:', error)
    }
  } else {
    try {
      await document.exitFullscreen()
      isFullscreen.value = false
    } catch (error) {
      console.error('退出全屏失败:', error)
    }
  }
}

const handleFullscreenChange = () => {
  isFullscreen.value = !!document.fullscreenElement
  setTimeout(() => {
    resizeCharts()
  }, 300)
}

const handleFullscreenKey = (e) => {
  if (e.key === 'F11' || (e.key === 'Escape' && isFullscreen.value)) {
    e.preventDefault()
    toggleFullscreen()
  }
}

const loadDeviceDetail = async () => {
  if (!deviceCode.value) return
  
  try {
    const response = await dashboardApi.getDeviceDetailData({
      device_code: deviceCode.value,
      days: 1
    })
    
    if (response.data) {
      Object.assign(deviceInfo, response.data.device_info || {})
      deviceIdentifier.value = response.data.device_info?.device_code || null
      Object.assign(kpiData, response.data.kpi || {})
      alarmList.value = (response.data.alarms || []).slice(0, 5)

      const newEvents = response.data.events || []
      const currentCount = newEvents.length

      if (currentCount !== previousEventCount && currentCount > 0) {
        hasNewEvents = true
        previousEventCount = currentCount
      }

      eventList.value = newEvents.slice(0, 10)

      // 从 dashboard API 获取产品和订单信息
      if (response.data.current_product) {
        Object.assign(currentPart, {
          part_number: response.data.current_product.part_number,
          product_name: response.data.current_product.product_name,
          u9_material_code: response.data.current_product.u9_material_code,
          start_code: response.data.current_product.part_number,
          specification: response.data.current_product.specification,
          category: response.data.current_product.category,
          project: response.data.current_product.project,
        })
      }
      if (response.data.current_order) {
        Object.assign(currentOrder, response.data.current_order)
      }

      if (response.data.local_order) {
        Object.assign(localOrder, response.data.local_order)
      } else {
        Object.assign(localOrder, { id: null, doc_no: null, part_number: null, planned_qty: null, completed_qty: 0, eligible_qty: 0, scrap_qty: 0, status: null, completion_rate: 0 })
      }

      initAllCharts(response.data)

      loadMonitorStatus()
    }
  } catch (error) {
    console.error('加载设备详情失败:', error)
  }
}

const loadMonitorStatus = async () => {
  if (!deviceIdentifier.value) return

  try {
    const response = await deviceAPI.getDeviceMonitorStatus(deviceIdentifier.value)
    if (response.data) {
      activeStatuses.value = response.data.active_statuses || []
      kpiData.alarmCount = response.data.alarm_count || 0
      
      if (response.data.current_part) {
        // MQTT 实时数据优先，但保留 dashboard API 的补充字段
        currentPart.part_number = response.data.current_part.part_number || currentPart.part_number
        currentPart.u9_material_code = response.data.current_part.u9_material_code || currentPart.u9_material_code
        currentPart.start_code = response.data.current_part.start_code || currentPart.start_code
        currentPart.order_info = response.data.current_part.order_info || currentPart.order_info
      }
      
      if (currentPart.part_number && !currentPart.order_info) {
        await loadOrderInfo(currentPart.part_number, currentPart.u9_material_code)
      }
      
      if (activeStatuses.value.length > 0) {
        const primaryStatus = activeStatuses.value.find(s => s.is_mutually_exclusive)
        const coexistentStatuses = activeStatuses.value.filter(s => !s.is_mutually_exclusive)
        // 拼接所有状态标签
        const labels = []
        if (primaryStatus) {
          labels.push(primaryStatus.status_label)
          // status_type → CSS class 映射（处理含空格的值）
          const statusCssMap = {
            'processing': 'processing',
            'stop': 'stop',
            'fault_stop': 'fault_stop',
            'emergency stop': 'emergency-stop',
            'mold_change': 'mold_change',
            'maintain': 'maintain',
            'material_shortage': 'material_shortage',
          }
          deviceInfo.status = statusCssMap[primaryStatus.status_type] || primaryStatus.status_type
        }
        coexistentStatuses.forEach(s => {
          if (s.status_label && !labels.includes(s.status_label)) labels.push(s.status_label)
        })
        deviceInfo.statusText = labels.join(' | ') || '运行中'
        // 有报警/缺料时覆盖为 warning 颜色
        if (coexistentStatuses.some(s => s.status_type === 'alarm' || s.status_type === 'material_shortage')) {
          deviceInfo.status = 'alarm'
        }
      } else {
        deviceInfo.status = 'running'
        deviceInfo.statusText = '运行中'
      }
    }
  } catch (error) {
    console.error('加载设备监控状态失败:', error)
  }
}

const loadOrderInfo = async (partNumber, u9MaterialCode) => {
  if (!partNumber && !u9MaterialCode) return
  
  try {
    const res = await deviceAPI.queryTodayOrderByPart(partNumber, u9MaterialCode)
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

const getStatusIcon = (statusType) => {
  const iconMap = {
    processing: 'mdi mdi-cog',
    mold_change: 'mdi mdi-refresh',
    fault: 'mdi mdi-close-circle',
    alarm: 'mdi mdi-alert',
    material_shortage: 'mdi mdi-package-variant-closed',
    stop: 'mdi mdi-pause-circle',
    plan_stop: 'mdi mdi-calendar-remove'
  }
  return iconMap[statusType] || 'mdi mdi-circle'
}

const getMatchMethodLabel = (method) => {
  const labelMap = {
    rule: '规则匹配',
    curve: '曲线匹配',
    device_status: '设备状态',
    order_status: '订单状态'
  }
  return labelMap[method] || method
}

const getMatchRuleLabel = (rule) => {
  const labelMap = {
    equals: '等于',
    not_equals: '不等于',
    contains: '包含',
    not_contains: '不包含',
    starts_with: '开头是',
    ends_with: '结尾是',
    greater_than: '大于',
    less_than: '小于',
    greater_equal: '大于等于',
    less_equal: '小于等于',
    in_range: '在范围内',
    regex: '正则匹配',
    is_true: '为true',
    is_false: '为false',
    is_empty: '为空',
    is_not_empty: '不为空'
  }
  return labelMap[rule] || rule
}

const isValueMatch = (matchedValue, actualValue) => {
  if (!matchedValue || !actualValue) return false
  return String(matchedValue) === String(actualValue)
}

const formatMatchTime = (timeStr) => {
  if (!timeStr) return ''
  try {
    const date = new Date(timeStr)
    const now = new Date()
    const diff = Math.floor((now - date) / 1000)
    
    if (diff < 60) return `${diff}秒前`
    if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
    if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
    
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return timeStr
  }
}

const initOeeChart = (data) => {
  if (!oeeEl.value) return
  oeeChart = echarts.init(oeeEl.value)
  
  const hours = data?.hourly_output?.hours || ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00']
  const oeeValues = data?.oee_trend || [72, 75, 78, 80, 65, 76, 79, 82, 77, 74]
  
  const option = {
    tooltip: { trigger: 'axis' },
    grid: { top: '10%', left: '3%', right: '5%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: hours,
      axisLabel: { color: '#8899aa', rotate: 30 },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      name: '%',
      min: 0,
      max: 100,
      nameTextStyle: { color: '#8899aa' },
      axisLabel: { color: '#8899aa' },
      splitLine: { lineStyle: { color: '#2a3a5a' } }
    },
    series: [
      {
        name: 'OEE',
        type: 'line',
        smooth: true,
        data: oeeValues,
        itemStyle: { color: '#00d4ff' },
        lineStyle: { width: 3 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 212, 255, 0.3)' },
            { offset: 1, color: 'rgba(0, 212, 255, 0.01)' }
          ])
        }
      }
    ]
  }
  
  oeeChart.setOption(option)
}

const initDowntimeChart = (data) => {
  if (!downtimeEl.value) return
  downtimeChart = echarts.init(downtimeEl.value)
  
  const downtimeData = data?.downtime_categories || [
    { value: 35, name: '设备故障' },
    { value: 25, name: '计划维护' },
    { value: 20, name: '换模调机' },
    { value: 15, name: '待料' },
    { value: 5, name: '其他' }
  ]
  
  const option = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'right', textStyle: { color: '#8899aa' } },
    series: [
      {
        name: '停机原因',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['40%', '50%'],
        itemStyle: { borderRadius: 8, borderColor: '#1a2a3a', borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold', color: '#fff' } },
        data: downtimeData.map((item, index) => ({
          ...item,
          itemStyle: { color: ['#ff4444', '#ffaa00', '#00d4ff', '#00ff88', '#aa00ff'][index] }
        }))
      }
    ]
  }
  
  downtimeChart.setOption(option)
}

const initQualityTrendChart = (data) => {
  if (!qualityTrendEl.value) return
  qualityTrendChart = echarts.init(qualityTrendEl.value)
  
  const hours = data?.quality_trend?.hours || ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00']
  const rates = data?.quality_trend?.rates || [98.5, 97.2, 99.1, 98.8, 96.5, 97.8, 98.2, 99.0, 98.5, 97.9]
  
  const option = {
    tooltip: { trigger: 'axis' },
    grid: { top: '10%', left: '3%', right: '5%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: hours,
      axisLabel: { color: '#8899aa', rotate: 30 },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      name: '%',
      min: 90,
      max: 100,
      nameTextStyle: { color: '#8899aa' },
      axisLabel: { color: '#8899aa' },
      splitLine: { lineStyle: { color: '#2a3a5a' } }
    },
    series: [
      {
        name: '合格率',
        type: 'line',
        smooth: true,
        data: rates,
        itemStyle: { color: '#00ff88' },
        lineStyle: { width: 3 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 255, 136, 0.3)' },
            { offset: 1, color: 'rgba(0, 255, 136, 0.01)' }
          ])
        }
      }
    ]
  }
  
  qualityTrendChart.setOption(option)
}

const initQualityIssueChart = (data) => {
  if (!qualityIssueEl.value) return
  qualityIssueChart = echarts.init(qualityIssueEl.value)
  
  const issueData = data?.quality_issues || [
    { value: 40, name: '尺寸超差' },
    { value: 25, name: '表面缺陷' },
    { value: 20, name: '装配不良' },
    { value: 10, name: '材料问题' },
    { value: 5, name: '其他' }
  ]
  
  const option = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'right', textStyle: { color: '#8899aa' } },
    series: [
      {
        name: '质量问题',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['40%', '50%'],
        itemStyle: { borderRadius: 8, borderColor: '#1a2a3a', borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold', color: '#fff' } },
        data: issueData.map((item, index) => ({
          ...item,
          itemStyle: { color: ['#ff4444', '#ffaa00', '#00d4ff', '#00ff88', '#aa00ff'][index] }
        }))
      }
    ]
  }
  
  qualityIssueChart.setOption(option)
}

const initHourlyOutputChart = (data) => {
  if (!hourlyOutputEl.value) return
  hourlyOutputChart = echarts.init(hourlyOutputEl.value)
  
  const hours = data?.hourly_output?.hours || ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00']
  const outputs = data?.hourly_output?.outputs || [45, 52, 48, 55, 30, 50, 53, 49, 51, 47]
  const qualified = data?.hourly_output?.qualified || [44, 50, 47, 54, 29, 49, 52, 48, 50, 46]
  
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['产量', '合格数'], textStyle: { color: '#8899aa' }, top: 0 },
    grid: { top: '15%', left: '3%', right: '5%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: hours,
      axisLabel: { color: '#8899aa', rotate: 30 },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      name: '件',
      nameTextStyle: { color: '#8899aa' },
      axisLabel: { color: '#8899aa' },
      splitLine: { lineStyle: { color: '#2a3a5a' } }
    },
    series: [
      {
        name: '产量',
        type: 'bar',
        data: outputs,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#00d4ff' },
            { offset: 1, color: '#0099ff' }
          ]),
          borderRadius: [4, 4, 0, 0]
        }
      },
      {
        name: '合格数',
        type: 'line',
        smooth: true,
        data: qualified,
        itemStyle: { color: '#00ff88' },
        lineStyle: { width: 3 },
        symbol: 'circle',
        symbolSize: 6
      }
    ]
  }
  
  hourlyOutputChart.setOption(option)
}

const initDeviceStatusChart = (data) => {
  if (!deviceStatusEl.value) return
  deviceStatusChart = echarts.init(deviceStatusEl.value)
  
  const statusData = data?.device_status || [
    { value: 65, name: '运行', itemStyle: { color: '#00ff88' } },
    { value: 15, name: '待机', itemStyle: { color: '#00d4ff' } },
    { value: 10, name: '报警', itemStyle: { color: '#ffaa00' } },
    { value: 10, name: '故障', itemStyle: { color: '#ff4444' } }
  ]
  
  const option = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'right', textStyle: { color: '#8899aa' } },
    series: [
      {
        name: '设备状态',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['40%', '50%'],
        itemStyle: { borderRadius: 8, borderColor: '#1a2a3a', borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold', color: '#fff' } },
        data: statusData
      }
    ]
  }
  
  deviceStatusChart.setOption(option)
}

const initCycleTimeChart = (data) => {
  if (!cycleTimeEl.value) return
  cycleTimeChart = echarts.init(cycleTimeEl.value)
  
  const hours = data?.cycle_time?.hours || ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00']
  const times = data?.cycle_time?.times || [45, 42, 48, 44, 50, 43, 46, 47, 44, 45]
  const standardTime = data?.cycle_time?.standard || 45
  
  const option = {
    tooltip: { trigger: 'axis' },
    grid: { top: '10%', left: '3%', right: '5%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: hours,
      axisLabel: { color: '#8899aa', rotate: 30 },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      name: '秒',
      nameTextStyle: { color: '#8899aa' },
      axisLabel: { color: '#8899aa' },
      splitLine: { lineStyle: { color: '#2a3a5a' } }
    },
    series: [
      {
        name: '实际节拍',
        type: 'line',
        smooth: true,
        data: times,
        itemStyle: { color: '#00d4ff' },
        lineStyle: { width: 3 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 212, 255, 0.3)' },
            { offset: 1, color: 'rgba(0, 212, 255, 0.01)' }
          ])
        }
      },
      {
        name: '标准节拍',
        type: 'line',
        data: Array(hours.length).fill(standardTime),
        itemStyle: { color: '#ffaa00' },
        lineStyle: { type: 'dashed', width: 2 },
        symbol: 'none'
      }
    ]
  }
  
  cycleTimeChart.setOption(option)
}

const startEventScroll = () => {
  if (!eventListEl.value || eventList.value.length === 0) return
  
  if (eventScrollTimer) {
    clearInterval(eventScrollTimer)
    eventScrollTimer = null
  }
  
  if (!hasNewEvents) return
  
  hasNewEvents = false
  
  const container = eventListEl.value
  container.scrollTop = 0
  
  eventScrollTimer = setInterval(() => {
    const scrollPos = container.scrollTop + 1
    if (scrollPos >= container.scrollHeight - container.clientHeight) {
      container.scrollTop = 0
    } else {
      container.scrollTop = scrollPos
    }
  }, 50)
}

const initAllCharts = (data) => {
  initOeeChart(data)
  initDowntimeChart(data)
  initQualityTrendChart(data)
  initQualityIssueChart(data)
  initHourlyOutputChart(data)
  initDeviceStatusChart(data)
  initCycleTimeChart(data)
  startEventScroll()
}

const resizeCharts = () => {
  oeeChart?.resize()
  downtimeChart?.resize()
  qualityTrendChart?.resize()
  qualityIssueChart?.resize()
  hourlyOutputChart?.resize()
  deviceStatusChart?.resize()
  cycleTimeChart?.resize()
}

onMounted(() => {
  loadDeviceDetail()
  window.addEventListener('resize', resizeCharts)
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  document.addEventListener('keydown', handleFullscreenKey)
  
  refreshTimer = setInterval(() => {
    loadDeviceDetail()
  }, 30000)
  
  monitorStatusTimer = setInterval(() => {
    loadMonitorStatus()
  }, 5000)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  document.removeEventListener('keydown', handleFullscreenKey)
  
  oeeChart?.dispose()
  downtimeChart?.dispose()
  qualityTrendChart?.dispose()
  qualityIssueChart?.dispose()
  hourlyOutputChart?.dispose()
  deviceStatusChart?.dispose()
  cycleTimeChart?.dispose()
  
  if (eventScrollTimer) clearInterval(eventScrollTimer)
  if (refreshTimer) clearInterval(refreshTimer)
  if (monitorStatusTimer) clearInterval(monitorStatusTimer)
  
  if (document.fullscreenElement) {
    document.exitFullscreen()
  }
})
</script>

<style scoped>
.device-detail-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a1628 0%, #1a2a4a 50%, #0a1628 100%);
  padding: 12px;
  transition: all 0.3s ease;
}

.device-detail-dashboard.fullscreen-mode {
  padding: 8px;
  height: 100vh;
  overflow: hidden;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 16px;
  padding: 16px;
  background: rgba(10, 30, 60, 0.6);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 8px;
}

.fullscreen-mode .page-header {
  margin-bottom: 8px;
  padding: 10px 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.fullscreen-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 6px;
  color: #00d4ff;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
  white-space: nowrap;
}

.fullscreen-btn:hover {
  background: rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
}

.fullscreen-btn i {
  font-size: 16px;
}

.fullscreen-mode .fullscreen-btn {
  background: rgba(0, 212, 255, 0.15);
  border-color: rgba(0, 212, 255, 0.4);
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 6px;
  color: #00d4ff;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
  flex-shrink: 0;
}

.fullscreen-mode .back-btn {
  padding: 6px 12px;
  font-size: 13px;
}

.back-btn:hover {
  background: rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
}

.device-title {
  font-size: 24px;
  font-weight: bold;
  color: #fff;
  margin: 0;
  flex-shrink: 0;
}

.fullscreen-mode .device-title {
  font-size: 20px;
}

.device-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: auto;
}

.fullscreen-mode .device-meta {
  gap: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
}

.fullscreen-mode .meta-item {
  font-size: 12px;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
}

.fullscreen-mode .status-badge {
  padding: 4px 8px;
  font-size: 12px;
}

.status-badge.running {
  background: rgba(0, 255, 136, 0.2);
  color: #00ff88;
}

.status-badge.processing {
  background: rgba(0, 255, 136, 0.2);
  color: #00ff88;
}

.status-badge.stopped {
  background: rgba(136, 153, 170, 0.2);
  color: #8899aa;
}

.status-badge.stop {
  background: rgba(136, 153, 170, 0.2);
  color: #8899aa;
}

.status-badge.mold_change {
  background: rgba(136, 153, 170, 0.2);
  color: #8899aa;
}

.status-badge.maintenance {
  background: rgba(170, 100, 255, 0.2);
  color: #aa64ff;
}

.status-badge.maintain {
  background: rgba(170, 100, 255, 0.2);
  color: #aa64ff;
}

.status-badge.error {
  background: rgba(255, 68, 68, 0.2);
  color: #ff4444;
}

.status-badge.fault {
  background: rgba(255, 68, 68, 0.2);
  color: #ff4444;
}

.status-badge.fault_stop {
  background: rgba(255, 68, 68, 0.2);
  color: #ff4444;
}

.status-badge.emergency-stop {
  background: rgba(255, 34, 34, 0.2);
  color: #ff2222;
}

.status-badge.warning {
  background: rgba(255, 170, 0, 0.2);
  color: #ffaa00;
}

.status-badge.alarm {
  background: rgba(230, 162, 60, 0.2);
  color: #E6A23C;
}

.status-badge.material_shortage {
  background: rgba(230, 162, 60, 0.2);
  color: #E6A23C;
}

.status-badge.plan_stop {
  background: rgba(136, 153, 170, 0.2);
  color: #8899aa;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.status-dot.running,
.status-dot.processing {
  background: #00ff88;
}

.status-dot.stopped,
.status-dot.stop,
.status-dot.mold_change,
.status-dot.plan_stop {
  background: #8899aa;
}

.status-dot.maintenance,
.status-dot.maintain {
  background: #aa64ff;
}

.status-dot.error,
.status-dot.fault,
.status-dot.fault_stop {
  background: #ff4444;
}

.status-dot.emergency-stop {
  background: #ff2222;
}

.status-dot.warning {
  background: #ffaa00;
}

.status-dot.alarm {
  background: #E6A23C;
}

.status-dot.material_shortage {
  background: #E6A23C;
}

.fullscreen-mode .status-dot {
  width: 6px;
  height: 6px;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.fullscreen-mode .dashboard-content {
  gap: 8px;
  height: calc(100vh - 80px);
}

.row {
  display: grid;
  gap: 12px;
}

.fullscreen-mode .row {
  gap: 8px;
}

.row-1 {
  grid-template-columns: 1.2fr 0.8fr 0.8fr 0.8fr 1fr;
}

.fullscreen-mode .row-1 {
  flex: 0 0 auto;
}

.row-2 {
  grid-template-columns: 1fr 1.5fr 1fr;
}

.fullscreen-mode .row-2 {
  flex: 1;
  min-height: 0;
}

.row-3 {
  grid-template-columns: 1fr;
}

.fullscreen-mode .row-3 {
  flex: 1;
  min-height: 0;
}

.row-4 {
  grid-template-columns: 1fr 1fr 1fr;
}

.fullscreen-mode .row-4 {
  flex: 1;
  min-height: 0;
}

.row-5 {
  grid-template-columns: 1fr;
}

.fullscreen-mode .row-5 {
  flex: 0 0 auto;
  max-height: 180px;
}

.fullscreen-mode .dashboard-content {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 80px);
}

.panel {
  background: rgba(10, 30, 60, 0.6);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 8px;
  overflow: hidden;
  backdrop-filter: blur(10px);
  box-shadow: 0 0 30px rgba(0, 212, 255, 0.1);
  display: flex;
  flex-direction: column;
}

.fullscreen-mode .panel {
  border-width: 1px;
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
  flex-shrink: 0;
}

.fullscreen-mode .panel-header {
  padding: 8px 12px;
  font-size: 13px;
}

.panel-body {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.fullscreen-mode .panel-body {
  padding: 8px 12px;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.fullscreen-mode .kpi-grid {
  gap: 8px;
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

.fullscreen-mode .kpi-item {
  padding: 12px;
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

.fullscreen-mode .kpi-icon {
  width: 40px;
  height: 40px;
}

.kpi-icon i {
  font-size: 24px;
  color: #fff;
}

.fullscreen-mode .kpi-icon i {
  font-size: 20px;
}

.kpi-info {
  flex: 1;
}

.kpi-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 4px;
}

.fullscreen-mode .kpi-label {
  font-size: 11px;
  margin-bottom: 2px;
}

.kpi-value {
  font-size: 24px;
  font-weight: bold;
  color: #fff;
  line-height: 1;
}

.fullscreen-mode .kpi-value {
  font-size: 20px;
}

.kpi-unit {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 4px;
}

.fullscreen-mode .kpi-unit {
  font-size: 11px;
  margin-top: 2px;
}

.oee-chart {
  width: 100%;
  height: 200px;
  flex: 1;
  min-height: 150px;
}

.fullscreen-mode .oee-chart {
  height: auto;
}

.current-product-panel {
  background: rgba(10, 30, 60, 0.6);
  border: 1px solid rgba(0, 255, 136, 0.2);
  box-shadow: 0 0 30px rgba(0, 255, 136, 0.1);
}

.current-product-panel .panel-header {
  background: linear-gradient(90deg, rgba(0, 255, 136, 0.1), transparent);
  border-bottom: 1px solid rgba(0, 255, 136, 0.2);
  color: #00ff88;
}

.current-product-panel .panel-header i {
  color: #00ff88;
}

.current-product-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.product-item {
  background: rgba(0, 255, 136, 0.05);
  border: 1px solid rgba(0, 255, 136, 0.15);
  border-radius: 6px;
  padding: 10px 12px;
}

.product-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.product-value {
  font-size: 14px;
  color: #fff;
  font-weight: 500;
  word-break: break-all;
}

.product-value.product-number {
  font-size: 18px;
  font-weight: 700;
  color: #00ff88;
  text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
}

.no-product {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 30px 20px;
  color: rgba(255, 255, 255, 0.4);
}

.no-product i {
  font-size: 32px;
  opacity: 0.5;
}

.no-product span {
  font-size: 13px;
}

.fullscreen-mode .product-item {
  padding: 8px 10px;
}

.fullscreen-mode .product-label {
  font-size: 10px;
}

.fullscreen-mode .product-value {
  font-size: 12px;
}

.fullscreen-mode .product-value.product-number {
  font-size: 16px;
}

.fullscreen-mode .no-product {
  padding: 20px 15px;
}

.fullscreen-mode .no-product i {
  font-size: 28px;
}

.fullscreen-mode .no-product span {
  font-size: 12px;
}

.order-panel {
  background: rgba(10, 30, 60, 0.6);
  border: 1px solid rgba(0, 212, 255, 0.2);
  box-shadow: 0 0 30px rgba(0, 212, 255, 0.1);
}

.order-panel .panel-header {
  background: linear-gradient(90deg, rgba(0, 212, 255, 0.1), transparent);
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
  color: #00d4ff;
}

.order-panel .panel-header i {
  color: #00d4ff;
}

.order-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.order-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(0, 212, 255, 0.04);
  border: 1px solid rgba(0, 212, 255, 0.1);
  border-radius: 5px;
  padding: 7px 10px;
}

.order-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  flex-shrink: 0;
}

.order-value {
  font-size: 13px;
  color: #fff;
  font-weight: 500;
  text-align: right;
}

.order-value.highlight {
  color: #00d4ff;
  font-size: 15px;
  font-weight: 700;
}

.order-value small {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  font-weight: 400;
}

.doc-state-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 3px;
  font-weight: 500;
}

.doc-state-tag.关闭 {
  background: rgba(0, 255, 136, 0.2);
  color: #00ff88;
}

.doc-state-tag.未审核,
.doc-state-tag.开立 {
  background: rgba(255, 170, 0, 0.2);
  color: #ffaa00;
}

.doc-state-tag.已审核 {
  background: rgba(0, 212, 255, 0.2);
  color: #00d4ff;
}

.order-progress {
  margin-top: 4px;
  padding: 8px 10px;
  background: rgba(0, 212, 255, 0.04);
  border: 1px solid rgba(0, 212, 255, 0.1);
  border-radius: 5px;
}

.order-progress .progress-label {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 6px;
}

.order-progress .progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.order-progress .progress-value {
  height: 100%;
  background: linear-gradient(90deg, #00d4ff, #00ff88);
  border-radius: 3px;
  transition: width 0.5s;
}

/* 本地加工记录面板 */
.local-order-panel {
  background: rgba(10, 30, 60, 0.6);
  border: 1px solid rgba(168, 85, 247, 0.2);
  box-shadow: 0 0 30px rgba(168, 85, 247, 0.1);
}

.local-order-panel .panel-header {
  background: linear-gradient(90deg, rgba(168, 85, 247, 0.1), transparent);
  border-bottom: 1px solid rgba(168, 85, 247, 0.2);
  color: #a855f7;
}

.local-order-panel .panel-header i {
  color: #a855f7;
}

.local-order-status-tag {
  margin-left: auto;
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 3px;
  font-weight: 500;
}

.local-order-status-tag.tag-in_progress {
  background: rgba(0, 212, 255, 0.2);
  color: #00d4ff;
}

.local-order-status-tag.tag-completed {
  background: rgba(0, 255, 136, 0.2);
  color: #00ff88;
}

.local-order-status-tag.tag-paused {
  background: rgba(255, 170, 0, 0.2);
  color: #ffaa00;
}

.local-order-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.local-order-doc {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: rgba(168, 85, 247, 0.06);
  border: 1px solid rgba(168, 85, 247, 0.15);
  border-radius: 5px;
  font-size: 13px;
  color: #fff;
  font-weight: 600;
}

.local-order-doc i {
  color: #a855f7;
  font-size: 14px;
}

.local-order-quantities {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
}

.lq-item {
  text-align: center;
  padding: 6px 4px;
  background: rgba(168, 85, 247, 0.04);
  border: 1px solid rgba(168, 85, 247, 0.1);
  border-radius: 4px;
}

.lq-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 2px;
}

.lq-value {
  font-size: 15px;
  font-weight: 700;
  color: #fff;
}

.lq-value.highlight {
  color: #a855f7;
}

.lq-value.success {
  color: #00ff88;
}

.lq-value.danger {
  color: #ff4444;
}

.local-order-progress {
  padding: 8px 10px;
  background: rgba(168, 85, 247, 0.04);
  border: 1px solid rgba(168, 85, 247, 0.1);
  border-radius: 5px;
}

.lo-progress-label {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 6px;
}

.lo-progress-rate {
  color: #a855f7;
  font-weight: 600;
}

.lo-progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(168, 85, 247, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.lo-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #a855f7, #00ff88);
  border-radius: 3px;
  transition: width 0.5s;
}

.fullscreen-mode .order-item {
  padding: 5px 8px;
}

.fullscreen-mode .order-label {
  font-size: 10px;
}

.fullscreen-mode .order-value {
  font-size: 12px;
}

.fullscreen-mode .order-value.highlight {
  font-size: 13px;
}

.fullscreen-mode .local-order-panel .panel-header {
  padding: 8px 12px;
  font-size: 13px;
}

.fullscreen-mode .local-order-doc {
  padding: 6px 8px;
  font-size: 12px;
}

.fullscreen-mode .lq-item {
  padding: 4px 2px;
}

.fullscreen-mode .lq-label {
  font-size: 9px;
}

.fullscreen-mode .lq-value {
  font-size: 13px;
}

.pie-chart,
.line-chart {
  width: 100%;
  height: 220px;
  flex: 1;
  min-height: 180px;
}

.fullscreen-mode .pie-chart,
.fullscreen-mode .line-chart {
  height: auto;
}

.combo-chart {
  width: 100%;
  height: 250px;
  flex: 1;
  min-height: 200px;
}

.fullscreen-mode .combo-chart {
  height: auto;
}

.status-chart {
  width: 100%;
  height: 220px;
  flex: 1;
  min-height: 180px;
}

.fullscreen-mode .status-chart {
  height: auto;
}

.alarm-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 220px;
  overflow-y: auto;
  flex: 1;
  min-height: 0;
}

.fullscreen-mode .alarm-list {
  gap: 8px;
  max-height: none;
}

.alarm-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: rgba(0, 212, 255, 0.05);
  border-radius: 6px;
  border-left: 3px solid #00d4ff;
}

.fullscreen-mode .alarm-item {
  padding: 8px;
  gap: 8px;
}

.alarm-item.error {
  border-left-color: #ff4444;
  background: rgba(255, 68, 68, 0.1);
}

.alarm-item.warning {
  border-left-color: #ffaa00;
  background: rgba(255, 170, 0, 0.1);
}

.alarm-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.fullscreen-mode .alarm-icon {
  font-size: 16px;
}

.alarm-item.error .alarm-icon {
  color: #ff4444;
}

.alarm-item.warning .alarm-icon {
  color: #ffaa00;
}

.alarm-content {
  flex: 1;
  min-width: 0;
}

.alarm-title {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 4px;
}

.fullscreen-mode .alarm-title {
  font-size: 12px;
  margin-bottom: 2px;
}

.alarm-desc {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 4px;
}

.fullscreen-mode .alarm-desc {
  font-size: 11px;
  margin-bottom: 2px;
}

.alarm-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.fullscreen-mode .alarm-time {
  font-size: 10px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px;
  color: rgba(255, 255, 255, 0.4);
}

.empty-state i {
  font-size: 32px;
}

.fullscreen-mode .empty-state {
  padding: 20px;
}

.event-list-scroll {
  height: 200px;
  overflow: hidden;
  position: relative;
  flex: 1;
  min-height: 0;
}

.fullscreen-mode .event-list-scroll {
  height: auto;
  max-height: 150px;
}

.event-item {
  display: grid;
  grid-template-columns: 120px 1fr 80px 100px;
  gap: 12px;
  padding: 10px 12px;
  border-bottom: 1px solid rgba(0, 212, 255, 0.1);
  font-size: 13px;
  align-items: center;
}

.fullscreen-mode .event-item {
  padding: 8px 10px;
  font-size: 12px;
  gap: 8px;
}

.event-item:nth-child(even) {
  background: rgba(0, 212, 255, 0.03);
}

.fullscreen-mode .event-item:nth-child(even) {
  background: rgba(0, 212, 255, 0.05);
}

.event-time {
  color: rgba(255, 255, 255, 0.5);
  font-family: 'Courier New', monospace;
}

.fullscreen-mode .event-time {
  font-size: 11px;
}

.event-code {
  color: #fff;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.fullscreen-mode .event-code {
  font-size: 12px;
}

.event-duration {
  color: #00d4ff;
  text-align: center;
}

.fullscreen-mode .event-duration {
  font-size: 11px;
}

.event-status {
  text-align: center;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.fullscreen-mode .event-status {
  padding: 3px 6px;
  font-size: 11px;
}

.event-status.completed {
  background: rgba(0, 255, 136, 0.2);
  color: #00ff88;
}

.event-status.running {
  background: rgba(0, 212, 255, 0.2);
  color: #00d4ff;
}

@media (max-width: 1600px) {
  .row-1 {
    grid-template-columns: 1fr 1fr 1fr;
  }

  .row-2 {
    grid-template-columns: 1fr 1fr;
  }

  .row-4 {
    grid-template-columns: 1fr 1fr;
  }

  .local-order-quantities {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1200px) {
  .row-1,
  .row-2,
  .row-4 {
    grid-template-columns: 1fr;
  }

  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .local-order-quantities {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 1920px) {
  .fullscreen-mode .device-title {
    font-size: 22px;
  }
  
  .fullscreen-mode .kpi-value {
    font-size: 22px;
  }
}

@media (min-width: 2560px) {
  .fullscreen-mode .device-title {
    font-size: 28px;
  }
  
  .fullscreen-mode .kpi-value {
    font-size: 32px;
  }
  
  .fullscreen-mode .panel-header {
    font-size: 16px;
  }
}

.status-count {
  margin-left: auto;
  font-size: 12px;
  color: rgba(0, 212, 255, 0.8);
  font-weight: normal;
  background: rgba(0, 212, 255, 0.1);
  padding: 2px 8px;
  border-radius: 10px;
}

.active-statuses-container {
  width: 100%;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.active-statuses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

.active-status-card {
  background: rgba(0, 212, 255, 0.05);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 8px;
  padding: 12px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.active-status-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, currentColor, transparent);
  opacity: 0.6;
}

.active-status-card.processing {
  border-color: rgba(0, 255, 136, 0.3);
  background: rgba(0, 255, 136, 0.05);
  color: #00ff88;
}

.active-status-card.processing::before {
  background: linear-gradient(90deg, transparent, #00ff88, transparent);
  opacity: 0.8;
}

.active-status-card.mold_change {
  border-color: rgba(0, 212, 255, 0.3);
  background: rgba(0, 212, 255, 0.05);
  color: #00d4ff;
}

.active-status-card.mold_change::before {
  background: linear-gradient(90deg, transparent, #00d4ff, transparent);
  opacity: 0.8;
}

.active-status-card.fault {
  border-color: rgba(255, 68, 68, 0.3);
  background: rgba(255, 68, 68, 0.05);
  color: #ff4444;
}

.active-status-card.fault::before {
  background: linear-gradient(90deg, transparent, #ff4444, transparent);
  opacity: 0.8;
}

.active-status-card.alarm {
  border-color: rgba(255, 170, 0, 0.3);
  background: rgba(255, 170, 0, 0.05);
  color: #ffaa00;
}

.active-status-card.alarm::before {
  background: linear-gradient(90deg, transparent, #ffaa00, transparent);
  opacity: 0.8;
}

.active-status-card.material_shortage {
  border-color: rgba(170, 0, 255, 0.3);
  background: rgba(170, 0, 255, 0.05);
  color: #aa00ff;
}

.active-status-card.material_shortage::before {
  background: linear-gradient(90deg, transparent, #aa00ff, transparent);
  opacity: 0.8;
}

.active-status-card.stop {
  border-color: rgba(136, 153, 170, 0.3);
  background: rgba(136, 153, 170, 0.05);
  color: #8899aa;
}

.active-status-card.stop::before {
  background: linear-gradient(90deg, transparent, #8899aa, transparent);
  opacity: 0.8;
}

.active-status-card.plan_stop {
  border-color: rgba(100, 149, 237, 0.3);
  background: rgba(100, 149, 237, 0.05);
  color: #6495ed;
}

.active-status-card.plan_stop::before {
  background: linear-gradient(90deg, transparent, #6495ed, transparent);
  opacity: 0.8;
}

.active-status-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.status-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.status-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: rgba(0, 0, 0, 0.2);
}

.status-icon i {
  font-size: 18px;
}

.status-card-title {
  flex: 1;
  min-width: 0;
}

.status-label {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  line-height: 1.2;
}

.status-type {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 2px;
}

.status-badge-active {
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  background: rgba(0, 255, 136, 0.2);
  color: #00ff88;
  border: 1px solid rgba(0, 255, 136, 0.3);
  flex-shrink: 0;
}

.status-badge {
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}

.status-badge.badge-primary {
  background: rgba(0, 212, 255, 0.2);
  color: #00d4ff;
  border: 1px solid rgba(0, 212, 255, 0.3);
}

.status-badge.badge-secondary {
  background: rgba(255, 170, 0, 0.2);
  color: #ffaa00;
  border: 1px solid rgba(255, 170, 0, 0.3);
}

.status-card-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.status-info-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.info-label {
  color: rgba(255, 255, 255, 0.5);
  flex-shrink: 0;
  min-width: 60px;
}

.info-value {
  color: rgba(255, 255, 255, 0.8);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 1600px) {
  .active-statuses-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  }
}

@media (max-width: 1200px) {
  .active-statuses-grid {
    grid-template-columns: 1fr;
  }
}

.fullscreen-mode .active-status-card {
  padding: 8px;
}

.fullscreen-mode .status-icon {
  width: 30px;
  height: 30px;
}

.fullscreen-mode .status-icon i {
  font-size: 16px;
}

.fullscreen-mode .status-label {
  font-size: 13px;
}

.fullscreen-mode .status-info-row {
  font-size: 11px;
}
</style>
