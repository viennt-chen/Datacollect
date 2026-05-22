<template>
  <div class="quality-analysis" :class="{ 'fullscreen-mode': isFullscreen }">
    <!-- 第一行：质量 KPI -->
    <div class="row row-1">
      <!-- 质量 KPI -->
      <div class="panel kpi-panel">
        <div class="panel-header">
          <i class="mdi mdi-clipboard-check"></i>
          <span>质量 KPI</span>
        </div>
        <div class="panel-body">
          <div class="kpi-grid">
            <div class="kpi-item">
              <div class="kpi-icon" style="background: linear-gradient(135deg, #00ff88, #00cc6a)">
                <i class="mdi mdi-check-circle"></i>
              </div>
              <div class="kpi-info">
                <div class="kpi-label">合格率</div>
                <div class="kpi-value">{{ qualityKpi.passRate }}%</div>
                <div class="kpi-trend up">
                  <i class="mdi mdi-arrow-up"></i>
                  1.2%
                </div>
              </div>
            </div>
            <div class="kpi-item">
              <div class="kpi-icon" style="background: linear-gradient(135deg, #00d4ff, #0099ff)">
                <i class="mdi mdi-package-variant-closed"></i>
              </div>
              <div class="kpi-info">
                <div class="kpi-label">总产量</div>
                <div class="kpi-value">{{ qualityKpi.totalOutput.toLocaleString() }}</div>
              </div>
            </div>
            <div class="kpi-item">
              <div class="kpi-icon" style="background: linear-gradient(135deg, #ffaa00, #ff8800)">
                <i class="mdi mdi-alert"></i>
              </div>
              <div class="kpi-info">
                <div class="kpi-label">不良品</div>
                <div class="kpi-value">{{ qualityKpi.defectCount.toLocaleString() }}</div>
              </div>
            </div>
            <div class="kpi-item">
              <div class="kpi-icon" style="background: linear-gradient(135deg, #aa00ff, #8800ff)">
                <i class="mdi mdi-percent"></i>
              </div>
              <div class="kpi-info">
                <div class="kpi-label">不良率</div>
                <div class="kpi-value">{{ qualityKpi.defectRate }}%</div>
                <div class="kpi-trend" style="color: #ff4444">
                  <i class="mdi mdi-arrow-down"></i>
                  0.8%
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 合格率仪表盘 -->
      <div class="panel">
        <div class="panel-header">
          <i class="mdi mdi-speedometer"></i>
          <span>合格率监控</span>
        </div>
        <div class="panel-body">
          <div ref="gaugeEl" class="gauge-chart"></div>
        </div>
      </div>

      <!-- 缺陷类型分布 -->
      <div class="panel">
        <div class="panel-header">
          <i class="mdi mdi-chart-pie"></i>
          <span>缺陷类型分布</span>
        </div>
        <div class="panel-body">
          <div ref="defectPieEl" class="pie-chart"></div>
        </div>
      </div>

      <!-- 集团质量排行 -->
      <div class="panel">
        <div class="panel-header">
          <i class="mdi mdi-chart-bar"></i>
          <span>集团质量排行</span>
        </div>
        <div class="panel-body">
          <div ref="groupRankEl" class="bar-chart"></div>
        </div>
      </div>
    </div>

    <!-- 第二行：质量分析 -->
    <div class="row row-2">
      <!-- 质量趋势 -->
      <div class="panel large-panel">
        <div class="panel-header">
          <i class="mdi mdi-chart-line"></i>
          <span>质量趋势分析</span>
        </div>
        <div class="panel-body">
          <div ref="trendEl" class="line-chart"></div>
        </div>
      </div>

      <!-- 产线质量对比 -->
      <div class="panel">
        <div class="panel-header">
          <i class="mdi mdi-chart-bar"></i>
          <span>产线质量对比</span>
        </div>
        <div class="panel-body">
          <div ref="lineCompareEl" class="bar-chart"></div>
        </div>
      </div>
    </div>

    <!-- 第三行：质量明细 -->
    <div class="row row-3">
      <!-- 缺陷 TOP10 -->
      <div class="panel">
        <div class="panel-header">
          <i class="mdi mdi-format-list-numbered"></i>
          <span>缺陷 TOP10</span>
        </div>
        <div class="panel-body">
          <div class="defect-list">
            <div class="defect-item" v-for="(item, index) in defectTop10" :key="index">
              <div class="defect-rank" :class="getRankClass(index)">{{ index + 1 }}</div>
              <div class="defect-info">
                <div class="defect-name">{{ item.name }}</div>
                <div class="defect-count">{{ item.count }} 件</div>
              </div>
              <div class="defect-bar">
                <div class="bar-fill" :style="{ width: item.rate + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 质量告警 -->
      <div class="panel wide-panel">
        <div class="panel-header">
          <i class="mdi mdi-bell"></i>
          <span>质量告警</span>
        </div>
        <div class="panel-body">
          <div class="alert-list">
            <div class="alert-item" v-for="(alert, index) in alertList" :key="index">
              <div class="alert-icon" :class="alert.level">
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
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

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

const gaugeEl = ref(null)
const defectPieEl = ref(null)
const groupRankEl = ref(null)
const trendEl = ref(null)
const lineCompareEl = ref(null)

let gauge = null
let defectPie = null
let groupRank = null
let trend = null
let lineCompare = null

const qualityKpi = ref({
  passRate: 98.5,
  totalOutput: 7970,
  defectCount: 120,
  defectRate: 1.5
})

const defectTop10 = ref([
  { name: '尺寸偏差', count: 195, rate: 85 },
  { name: '表面划痕', count: 167, rate: 72 },
  { name: '颜色不均', count: 142, rate: 65 },
  { name: '装配松动', count: 128, rate: 58 },
  { name: '功能异常', count: 95, rate: 45 },
  { name: '包装破损', count: 78, rate: 38 },
  { name: '标签错误', count: 65, rate: 32 },
  { name: '毛刺', count: 52, rate: 25 },
  { name: '变形', count: 43, rate: 20 },
  { name: '其他', count: 35, rate: 15 }
])

const alertList = ref([
  { level: 'error', icon: 'mdi mdi-alert', title: '严重告警', desc: '3 号线合格率低于 95%', time: '10 分钟前', status: 'pending', statusText: '未处理' },
  { level: 'warning', icon: 'mdi mdi-bell', title: '质量预警', desc: '尺寸偏差占比上升', time: '30 分钟前', status: 'pending', statusText: '处理中' },
  { level: 'info', icon: 'mdi mdi-information', title: '质量通知', desc: '今日首检完成', time: '2 小时前', status: 'success', statusText: '已完成' }
])

const getRankClass = (index) => {
  if (index === 0) return 'rank-1'
  if (index === 1) return 'rank-2'
  if (index === 2) return 'rank-3'
  return ''
}

const initGauge = () => {
  if (!gaugeEl.value) return
  
  gauge = echarts.init(gaugeEl.value)
  
  const option = {
    series: [
      {
        type: 'gauge',
        startAngle: 180,
        endAngle: 0,
        min: 0,
        max: 100,
        radius: '100%',
        pointer: { show: false },
        axisLine: {
          lineStyle: {
            width: 20,
            color: [
              [0.985, '#00ff88'],
              [1, '#2a3a5a']
            ]
          }
        },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        detail: {
          valueAnimation: true,
          offsetCenter: [0, '0%'],
          fontSize: 40,
          fontWeight: 'bold',
          color: '#fff',
          formatter: '{value}%'
        },
        data: [{ value: qualityKpi.value.passRate }]
      }
    ]
  }
  
  gauge.setOption(option)
}

const initDefectPie = () => {
  if (!defectPieEl.value) return
  
  defectPie = echarts.init(defectPieEl.value)
  
  const option = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'right', textStyle: { color: '#8899aa' } },
    series: [
      {
        name: '缺陷类型',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        itemStyle: { borderRadius: 10, borderColor: '#1a2a3a', borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold', color: '#fff' } },
        data: [
          { value: 195, name: '尺寸偏差', itemStyle: { color: '#00d4ff' } },
          { value: 167, name: '表面划痕', itemStyle: { color: '#00ff88' } },
          { value: 142, name: '颜色不均', itemStyle: { color: '#ffaa00' } },
          { value: 128, name: '装配松动', itemStyle: { color: '#ff4444' } },
          { value: 95, name: '功能异常', itemStyle: { color: '#aa00ff' } }
        ]
      }
    ]
  }
  
  defectPie.setOption(option)
}

const initGroupRank = () => {
  if (!groupRankEl.value) return
  
  groupRank = echarts.init(groupRankEl.value)
  
  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: '5%', left: '3%', right: '10%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'value',
      name: '合格率',
      nameTextStyle: { color: '#8899aa' },
      axisLabel: { color: '#8899aa', formatter: '{value}%' },
      splitLine: { lineStyle: { color: '#2a3a5a' } }
    },
    yAxis: {
      type: 'category',
      data: ['集团 A', '集团 B', '集团 C', '集团 D', '集团 E'],
      axisLabel: { color: '#8899aa' },
      splitLine: { show: false }
    },
    series: [
      {
        type: 'bar',
        data: [99.2, 98.8, 98.5, 97.9, 97.2],
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
  
  groupRank.setOption(option)
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
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      axisLabel: { color: '#8899aa' },
      splitLine: { lineStyle: { color: '#2a3a5a' } }
    },
    yAxis: {
      type: 'value',
      name: '合格率',
      nameTextStyle: { color: '#8899aa' },
      axisLabel: { color: '#8899aa', formatter: '{value}%' },
      splitLine: { lineStyle: { color: '#2a3a5a' } }
    },
    series: [
      {
        name: '合格率',
        type: 'line',
        smooth: true,
        data: [97.8, 98.2, 98.0, 98.5, 98.8, 98.3, 98.5],
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

const initLineCompare = () => {
  if (!lineCompareEl.value) return
  
  lineCompare = echarts.init(lineCompareEl.value)
  
  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['合格率', '不良率'], textStyle: { color: '#8899aa' }, top: 0 },
    grid: { top: '15%', left: '3%', right: '10%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['1 号线', '2 号线', '3 号线', '4 号线', '5 号线'],
      axisLabel: { color: '#8899aa' },
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
        name: '合格率',
        type: 'bar',
        stack: 'total',
        data: [99.2, 98.8, 97.5, 98.9, 98.2],
        itemStyle: { color: '#00ff88' }
      },
      {
        name: '不良率',
        type: 'bar',
        stack: 'total',
        data: [0.8, 1.2, 2.5, 1.1, 1.8],
        itemStyle: { color: '#ff4444' }
      }
    ]
  }
  
  lineCompare.setOption(option)
}

const initAllCharts = () => {
  initGauge()
  initDefectPie()
  initGroupRank()
  initTrend()
  initLineCompare()
}

const resizeCharts = () => {
  gauge?.resize()
  defectPie?.resize()
  groupRank?.resize()
  trend?.resize()
  lineCompare?.resize()
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
  gauge?.dispose()
  defectPie?.dispose()
  groupRank?.dispose()
  trend?.dispose()
  lineCompare?.dispose()
})
</script>

<style scoped>
.quality-analysis {
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
  grid-template-columns: 1.5fr 1fr;
}

.row-3 {
  grid-template-columns: 1fr 2fr;
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

.panel-body {
  padding: 16px;
}

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

.gauge-chart {
  width: 100%;
  height: 220px;
}

.pie-chart,
.bar-chart,
.line-chart {
  width: 100%;
  height: 220px;
}

.defect-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.defect-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.defect-rank {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  color: #fff;
  background: rgba(0, 212, 255, 0.2);
  flex-shrink: 0;
}

.defect-rank.rank-1 {
  background: linear-gradient(135deg, #ffd700, #ffaa00);
}

.defect-rank.rank-2 {
  background: linear-gradient(135deg, #c0c0c0, #a0a0a0);
}

.defect-rank.rank-3 {
  background: linear-gradient(135deg, #cd7f32, #b87333);
}

.defect-info {
  flex: 1;
  min-width: 0;
}

.defect-name {
  font-size: 13px;
  color: #fff;
  margin-bottom: 4px;
}

.defect-count {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.defect-bar {
  width: 150px;
  height: 8px;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #00d4ff, #0099ff);
  border-radius: 4px;
  transition: width 0.3s;
}

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

.alert-icon.error {
  color: #ff4444;
}

.alert-icon.warning {
  color: #ffaa00;
}

.alert-icon.info {
  color: #00d4ff;
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

@media (max-width: 1600px) {
  .row-1,
  .row-2 {
    grid-template-columns: 1fr 1fr;
  }
  
  .row-3 {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1200px) {
  .row-1,
  .row-2,
  .row-3 {
    grid-template-columns: 1fr;
  }
}
</style>
