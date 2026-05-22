<template>
  <div class="production-overview" :class="{ 'fullscreen-mode': isFullscreen }">
    <!-- 第一行：关键 KPI -->
    <div class="row row-1">
      <!-- 关键 KPI -->
      <div class="panel kpi-panel">
        <div class="panel-header">
          <i class="mdi mdi-chart-line"></i>
          <span>关键 KPI</span>
        </div>
        <div class="panel-body">
          <div class="kpi-grid">
            <div class="kpi-item" v-for="(kpi, index) in kpiData" :key="index">
              <div class="kpi-icon" :style="{ background: kpi.color }">
                <i :class="kpi.icon"></i>
              </div>
              <div class="kpi-info">
                <div class="kpi-label">{{ kpi.label }}</div>
                <div class="kpi-value">{{ kpi.value }}</div>
                <div class="kpi-trend up" v-if="kpi.trend">
                  <i class="mdi mdi-arrow-up"></i>
                  {{ kpi.trend }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 质量分析 -->
      <div class="panel">
        <div class="panel-header">
          <i class="mdi mdi-chart-pie"></i>
          <span>质量分析</span>
        </div>
        <div class="panel-body">
          <div class="quality-content">
            <div ref="qualityGaugeEl" class="gauge-chart"></div>
            <div class="quality-stats">
              <div class="stat-item" v-for="(item, index) in qualityStats" :key="index">
                <span class="stat-dot" :style="{ background: item.color }"></span>
                <span class="stat-label">{{ item.label }}</span>
                <span class="stat-value">{{ item.value }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 停机时间分析 -->
      <div class="panel">
        <div class="panel-header">
          <i class="mdi mdi-history"></i>
          <span>停机时间分析</span>
        </div>
        <div class="panel-body">
          <div ref="downtimeBarEl" class="bar-chart"></div>
        </div>
      </div>

      <!-- 分产线产出 -->
      <div class="panel">
        <div class="panel-header">
          <i class="mdi mdi-chart-bar"></i>
          <span>分产线产出</span>
        </div>
        <div class="panel-body">
          <div ref="lineOutputEl" class="bar-chart"></div>
        </div>
      </div>
    </div>

    <!-- 第二行：趋势和明细 -->
    <div class="row row-2">
      <!-- OEE 趋势 -->
      <div class="panel large-panel">
        <div class="panel-header">
          <i class="mdi mdi-heart-pulse"></i>
          <span>OEE 趋势（小时）</span>
        </div>
        <div class="panel-body">
          <div ref="oeeTrendEl" class="line-chart"></div>
        </div>
      </div>

      <!-- 生产计划完成率 -->
      <div class="panel">
        <div class="panel-header">
          <i class="mdi mdi-calendar-check"></i>
          <span>生产计划完成率</span>
        </div>
        <div class="panel-body">
          <div ref="planCompleteEl" class="bar-chart"></div>
        </div>
      </div>

      <!-- 班次效率对比 -->
      <div class="panel">
        <div class="panel-header">
          <i class="mdi mdi-account-group"></i>
          <span>班次效率对比</span>
        </div>
        <div class="panel-body">
          <div ref="shiftCompareEl" class="compare-chart"></div>
        </div>
      </div>

      <!-- 故障预警与维护 -->
      <div class="panel">
        <div class="panel-header">
          <i class="mdi mdi-alert"></i>
          <span>故障预警与维护</span>
        </div>
        <div class="panel-body">
          <div class="alert-list">
            <div class="alert-item" v-for="(alert, index) in alertList" :key="index">
              <div class="alert-icon" :class="alert.type">
                <i :class="alert.icon"></i>
              </div>
              <div class="alert-content">
                <div class="alert-title">{{ alert.title }}</div>
                <div class="alert-desc">{{ alert.desc }}</div>
                <div class="alert-time">{{ alert.time }}</div>
              </div>
              <div class="alert-status" :class="alert.status">
                {{ alert.statusText }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 第三行：设备状态和产能 -->
    <div class="row row-3">
      <!-- 停机分类占比 -->
      <div class="panel">
        <div class="panel-header">
          <i class="mdi mdi-chart-pie"></i>
          <span>停机分类占比</span>
        </div>
        <div class="panel-body">
          <div ref="downtimePieEl" class="pie-chart"></div>
        </div>
      </div>

      <!-- 设备运行状态明细 -->
      <div class="panel wide-panel">
        <div class="panel-header">
          <i class="mdi mdi-table"></i>
          <span>设备运行状态明细</span>
        </div>
        <div class="panel-body">
          <div class="device-table">
            <table>
              <thead>
                <tr>
                  <th>设备编号</th>
                  <th>设备名称</th>
                  <th>生产线</th>
                  <th>运行状态</th>
                  <th>OEE</th>
                  <th>可用率</th>
                  <th>性能率</th>
                  <th>合格率</th>
                  <th>运行时长</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(device, index) in deviceList" :key="index">
                  <td class="device-code">{{ device.code }}</td>
                  <td>{{ device.name }}</td>
                  <td>{{ device.line }}</td>
                  <td>
                    <span class="status-badge" :class="device.status">
                      {{ device.statusText }}
                    </span>
                  </td>
                  <td>
                    <div class="oee-bar">
                      <div class="oee-value" :style="{ width: device.oee + '%' }"></div>
                      <span class="oee-text">{{ device.oee }}%</span>
                    </div>
                  </td>
                  <td>{{ device.availability }}%</td>
                  <td>{{ device.performance }}%</td>
                  <td>{{ device.quality }}%</td>
                  <td>{{ device.hours }}h</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 产能负载 -->
      <div class="panel">
        <div class="panel-header">
          <i class="mdi mdi-lightning-bolt"></i>
          <span>产能负载</span>
        </div>
        <div class="panel-body">
          <div ref="capacityEl" class="capacity-chart"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { dashboardApi } from '@/api'

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

const qualityGaugeEl = ref(null)
const downtimeBarEl = ref(null)
const lineOutputEl = ref(null)
const oeeTrendEl = ref(null)
const planCompleteEl = ref(null)
const shiftCompareEl = ref(null)
const downtimePieEl = ref(null)
const capacityEl = ref(null)

let qualityGauge = null
let downtimeBar = null
let lineOutput = null
let oeeTrend = null
let planComplete = null
let shiftCompare = null
let downtimePie = null
let capacity = null

const kpiData = ref([
  { label: '今日产量', value: '7,970', icon: 'mdi mdi-package-variant-closed', color: 'linear-gradient(135deg, #00d4ff, #0099ff)', trend: '2.3%' },
  { label: '在制订单', value: '26', icon: 'mdi mdi-clipboard-check', color: 'linear-gradient(135deg, #00ff88, #00cc6a)', trend: '5.1%' },
  { label: '设备开动率', value: '82.1%', icon: 'mdi mdi-cog', color: 'linear-gradient(135deg, #ffaa00, #ff8800)', trend: '1.8%' },
  { label: '合格率', value: '98.5%', icon: 'mdi mdi-check-circle', color: 'linear-gradient(135deg, #00d4ff, #0066ff)' }
])

const qualityStats = ref([
  { label: '尺寸偏差', value: 195, color: '#00d4ff' },
  { label: '表面缺陷', value: 267, color: '#00ff88' },
  { label: '功能异常', value: 172, color: '#ffaa00' },
  { label: '装配问题', value: 80, color: '#ff4444' },
  { label: '其他', value: 96, color: '#aa00ff' }
])

const alertList = ref([
  {
    type: 'complete',
    icon: 'mdi mdi-check-circle',
    title: '【维护完成】',
    desc: '磨床 #103 定期检查，已完成维护',
    time: '2026-04-13 13:43:12',
    status: 'success',
    statusText: '完成'
  },
  {
    type: 'complete',
    icon: 'mdi mdi-check-circle',
    title: '【维护完成】',
    desc: '智能机 #083 定期检查，已完成维护',
    time: '2026-04-13 07:45:45',
    status: 'success',
    statusText: '完成'
  },
  {
    type: 'warning',
    icon: 'mdi mdi-alert',
    title: '【紧急报警】',
    desc: '输送机 #024 传感器异常，已停机 3 小时 21 分钟',
    time: '2026-04-13 07:21:33',
    status: 'pending',
    statusText: '处理中'
  }
])

const deviceList = ref([
  { code: 'EQ-2023-3780', name: '打磨机', line: '生产线 3', status: 'running', statusText: '运行中', oee: 82.8, availability: 97.8, performance: 75.3, quality: 72.3, hours: 231 },
  { code: 'EQ-2023-3834', name: '包装机', line: '生产线 1', status: 'running', statusText: '运行中', oee: 87.6, availability: 82.3, performance: 54.2, quality: 80.5, hours: 168 },
  { code: 'EQ-2023-7999', name: '注塑机 A', line: '生产线 4', status: 'warning', statusText: '维护中', oee: 96.1, availability: 81.9, performance: 75.1, quality: 87.6, hours: 225 },
  { code: 'EQ-2023-1422', name: '打磨机', line: '生产线 1', status: 'running', statusText: '运行中', oee: 71.4, availability: 74.6, performance: 78.3, quality: 91.0, hours: 95 },
  { code: 'EQ-2023-8786', name: '注塑机 C', line: '生产线 1', status: 'error', statusText: '故障', oee: 75.6, availability: 86.8, performance: 59.9, quality: 75.3, hours: 168 },
  { code: 'EQ-2023-7015', name: '包装机', line: '生产线 1', status: 'running', statusText: '运行中', oee: 72.5, availability: 93.5, performance: 52.8, quality: 79.3, hours: 168 }
])

const initQualityGauge = () => {
  if (!qualityGaugeEl.value) return
  
  qualityGauge = echarts.init(qualityGaugeEl.value)
  
  const option = {
    series: [
      {
        type: 'gauge',
        startAngle: 180,
        endAngle: 0,
        min: 0,
        max: 1000,
        radius: '100%',
        pointer: { show: false },
        axisLine: {
          lineStyle: {
            width: 20,
            color: [
              [0.81, '#00ff88'],
              [1, '#2a3a5a']
            ]
          }
        },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        detail: {
          valueAnimation: true,
          offsetCenter: [0, '20%'],
          fontSize: 40,
          fontWeight: 'bold',
          color: '#fff',
          formatter: '{value}\n质量分析'
        },
        data: [{ value: 810 }]
      }
    ]
  }
  
  qualityGauge.setOption(option)
}

const initDowntimeBar = () => {
  if (!downtimeBarEl.value) return
  
  downtimeBar = echarts.init(downtimeBarEl.value)
  
  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: '10%', left: '3%', right: '10%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'value',
      name: '小时',
      nameTextStyle: { color: '#8899aa' },
      axisLabel: { color: '#8899aa' },
      splitLine: { lineStyle: { color: '#2a3a5a' } }
    },
    yAxis: {
      type: 'category',
      data: ['设备 A', '设备 B', '设备 C', '设备 D', '设备 E', '设备 F'],
      axisLabel: { color: '#8899aa' },
      splitLine: { show: false }
    },
    series: [
      {
        type: 'bar',
        data: [150, 120, 80, 50, 30, 20],
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
  
  downtimeBar.setOption(option)
}

const initLineOutput = () => {
  if (!lineOutputEl.value) return
  
  lineOutput = echarts.init(lineOutputEl.value)
  
  const option = {
    tooltip: { trigger: 'axis' },
    grid: { top: '10%', left: '3%', right: '10%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['1 号线', '2 号线', '3 号线', '4 号线', '5 号线', '6 号线', '7 号线', '8 号线'],
      axisLabel: { color: '#8899aa' },
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
        type: 'bar',
        data: [53, 79, 54, 91, 64, 58, 55, 52],
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#00d4ff' },
            { offset: 1, color: '#0066ff' }
          ]),
          borderRadius: [4, 4, 0, 0]
        }
      }
    ]
  }
  
  lineOutput.setOption(option)
}

const initOeeTrend = () => {
  if (!oeeTrendEl.value) return
  
  oeeTrend = echarts.init(oeeTrendEl.value)
  
  const option = {
    tooltip: { trigger: 'axis' },
    grid: { top: '10%', left: '3%', right: '10%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: ['00', '02', '04', '06', '08', '10', '12', '14', '16', '18', '20', '22'],
      axisLabel: { color: '#8899aa' },
      splitLine: { lineStyle: { color: '#2a3a5a' } }
    },
    yAxis: {
      type: 'value',
      name: 'OEE',
      nameTextStyle: { color: '#8899aa' },
      axisLabel: { color: '#8899aa', formatter: '{value}%' },
      splitLine: { lineStyle: { color: '#2a3a5a' } }
    },
    series: [
      {
        name: 'OEE',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        data: [65, 72, 68, 75, 82, 78, 85, 80, 76, 83, 79, 74],
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
  
  oeeTrend.setOption(option)
}

const initPlanComplete = () => {
  if (!planCompleteEl.value) return
  
  planComplete = echarts.init(planCompleteEl.value)
  
  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: '10%', left: '3%', right: '10%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      axisLabel: { color: '#8899aa' },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      name: '完成率',
      nameTextStyle: { color: '#8899aa' },
      axisLabel: { color: '#8899aa', formatter: '{value}%' },
      splitLine: { lineStyle: { color: '#2a3a5a' } }
    },
    series: [
      {
        type: 'bar',
        barWidth: '40%',
        data: [88, 77, 74, 90, 94, 90, 70],
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#00d4ff' },
            { offset: 1, color: '#0099ff' }
          ]),
          borderRadius: [4, 4, 0, 0]
        },
        label: { show: true, position: 'top', color: '#fff', formatter: '{c}%' }
      }
    ]
  }
  
  planComplete.setOption(option)
}

const initShiftCompare = () => {
  if (!shiftCompareEl.value) return
  
  shiftCompare = echarts.init(shiftCompareEl.value)
  
  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['早班', '中班', '晚班'], textStyle: { color: '#8899aa' }, top: 0 },
    grid: { top: '15%', left: '3%', right: '10%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      axisLabel: { color: '#8899aa' },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      name: '效率',
      nameTextStyle: { color: '#8899aa' },
      axisLabel: { color: '#8899aa' },
      splitLine: { lineStyle: { color: '#2a3a5a' } }
    },
    series: [
      {
        name: '早班',
        type: 'bar',
        stack: 'total',
        data: [35, 38, 32, 40, 42, 38, 30],
        itemStyle: { color: '#00d4ff', borderRadius: [4, 4, 0, 0] }
      },
      {
        name: '中班',
        type: 'bar',
        stack: 'total',
        data: [30, 32, 28, 35, 38, 34, 26],
        itemStyle: { color: '#00ff88' }
      },
      {
        name: '晚班',
        type: 'bar',
        stack: 'total',
        data: [25, 28, 24, 30, 32, 28, 22],
        itemStyle: { color: '#ffaa00', borderRadius: [0, 0, 4, 4] }
      }
    ]
  }
  
  shiftCompare.setOption(option)
}

const initDowntimePie = () => {
  if (!downtimePieEl.value) return
  
  downtimePie = echarts.init(downtimePieEl.value)
  
  const option = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'right', textStyle: { color: '#8899aa' } },
    series: [
      {
        name: '停机分类',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 10, borderColor: '#1a2a3a', borderWidth: 2 },
        label: { show: false, position: 'center' },
        emphasis: {
          label: {
            show: true,
            fontSize: 18,
            fontWeight: 'bold',
            color: '#fff'
          }
        },
        labelLine: { show: false },
        data: [
          { value: 150, name: '设备故障', itemStyle: { color: '#ff4444' } },
          { value: 120, name: '计划停机', itemStyle: { color: '#00d4ff' } },
          { value: 80, name: '换模', itemStyle: { color: '#00ff88' } },
          { value: 50, name: '待料', itemStyle: { color: '#ffaa00' } },
          { value: 30, name: '其他', itemStyle: { color: '#aa00ff' } }
        ]
      }
    ]
  }
  
  downtimePie.setOption(option)
}

const initCapacity = () => {
  if (!capacityEl.value) return
  
  capacity = echarts.init(capacityEl.value)
  
  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: '10%', left: '3%', right: '10%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['1 号线', '2 号线', '3 号线', '4 号线', '5 号线', '6 号线'],
      axisLabel: { color: '#8899aa', rotate: 45 },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      name: '负载率',
      nameTextStyle: { color: '#8899aa' },
      axisLabel: { color: '#8899aa', formatter: '{value}%' },
      splitLine: { lineStyle: { color: '#2a3a5a' } }
    },
    series: [
      {
        type: 'bar',
        data: [85, 72, 90, 68, 78, 82],
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#00d4ff' },
            { offset: 1, color: '#0066ff' }
          ]),
          borderRadius: [4, 4, 0, 0]
        },
        label: {
          show: true,
          position: 'top',
          color: '#fff',
          formatter: '{c}%'
        }
      }
    ]
  }
  
  capacity.setOption(option)
}

const initAllCharts = () => {
  initQualityGauge()
  initDowntimeBar()
  initLineOutput()
  initOeeTrend()
  initPlanComplete()
  initShiftCompare()
  initDowntimePie()
  initCapacity()
}

const resizeCharts = () => {
  qualityGauge?.resize()
  downtimeBar?.resize()
  lineOutput?.resize()
  oeeTrend?.resize()
  planComplete?.resize()
  shiftCompare?.resize()
  downtimePie?.resize()
  capacity?.resize()
}

watch(() => props.isFullscreen, () => {
  setTimeout(() => {
    resizeCharts()
  }, 300)
})

onMounted(() => {
  initAllCharts()
  window.addEventListener('resize', resizeCharts)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
  qualityGauge?.dispose()
  downtimeBar?.dispose()
  lineOutput?.dispose()
  oeeTrend?.dispose()
  planComplete?.dispose()
  shiftCompare?.dispose()
  downtimePie?.dispose()
  capacity?.dispose()
})
</script>

<style scoped>
.production-overview {
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
  grid-template-columns: 1.5fr 1fr 1fr 1fr;
}

.row-3 {
  grid-template-columns: 1fr 2fr 1fr;
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

.panel-header i {
  font-size: 16px;
}

.panel-body {
  padding: 16px;
}

/* KPI 面板 */
.kpi-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
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

/* 质量分析 */
.quality-content {
  display: flex;
  gap: 16px;
  align-items: center;
}

.gauge-chart {
  width: 140px;
  height: 140px;
  flex-shrink: 0;
}

.quality-stats {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.stat-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.stat-label {
  color: rgba(255, 255, 255, 0.6);
  flex: 1;
}

.stat-value {
  color: #fff;
  font-weight: 600;
}

/* 图表容器 */
.bar-chart,
.line-chart,
.pie-chart,
.compare-chart,
.capacity-chart {
  width: 100%;
  height: 220px;
}

/* 警报列表 */
.alert-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: rgba(0, 212, 255, 0.05);
  border-radius: 6px;
  border: 1px solid rgba(0, 212, 255, 0.1);
}

.alert-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.alert-icon.complete {
  color: #00ff88;
}

.alert-icon.warning {
  color: #ffaa00;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 4px;
}

.alert-desc {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 4px;
}

.alert-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.alert-status {
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 4px;
  flex-shrink: 0;
}

.alert-status.success {
  background: rgba(0, 255, 136, 0.2);
  color: #00ff88;
}

.alert-status.pending {
  background: rgba(255, 170, 0, 0.2);
  color: #ffaa00;
}

/* 设备表格 */
.device-table {
  overflow-x: auto;
}

.device-table table {
  width: 100%;
  border-collapse: collapse;
}

.device-table th,
.device-table td {
  padding: 10px 8px;
  text-align: left;
  border-bottom: 1px solid rgba(0, 212, 255, 0.1);
  font-size: 12px;
  white-space: nowrap;
}

.device-table th {
  color: #00d4ff;
  font-weight: 600;
  background: rgba(0, 212, 255, 0.05);
}

.device-table td {
  color: rgba(255, 255, 255, 0.8);
}

.device-code {
  font-family: 'Courier New', monospace;
  color: #00d4ff;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.status-badge.running {
  background: rgba(0, 255, 136, 0.2);
  color: #00ff88;
}

.status-badge.warning {
  background: rgba(255, 170, 0, 0.2);
  color: #ffaa00;
}

.status-badge.error {
  background: rgba(255, 68, 68, 0.2);
  color: #ff4444;
}

.oee-bar {
  width: 100%;
  height: 20px;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 10px;
  overflow: hidden;
  position: relative;
}

.oee-value {
  height: 100%;
  background: linear-gradient(90deg, #00d4ff, #0099ff);
  border-radius: 10px;
  transition: width 0.3s;
}

.oee-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 11px;
  font-weight: 600;
  color: #fff;
}

/* 响应式调整 */
@media (max-width: 1600px) {
  .row-1,
  .row-2 {
    grid-template-columns: 1fr 1fr;
  }
  
  .row-3 {
    grid-template-columns: 1fr 1fr;
  }
  
  .wide-panel {
    grid-column: span 2;
  }
}

@media (max-width: 1200px) {
  .row-1,
  .row-2,
  .row-3 {
    grid-template-columns: 1fr;
  }
  
  .wide-panel,
  .large-panel {
    grid-column: span 1;
  }
}
</style>
