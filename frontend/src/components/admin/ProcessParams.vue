<template>
  <div>
    <!-- Action bar -->
    <v-toolbar flat color="transparent" class="mb-4">
      <div>
        <div class="text-h5 font-weight-bold d-flex align-center ga-2">
          <v-icon icon="mdi-tune-variant" color="primary" />
          工艺参数
        </div>
        <div class="text-caption text-medium-emphasis mt-1">
          首页 / 工艺参数
        </div>
      </div>
    </v-toolbar>

    <!-- Stats cards -->
    <v-row class="mb-4" dense>
      <v-col cols="12" sm="6" md="4" lg="2">
        <v-card>
          <v-card-text class="d-flex align-center ga-3">
            <v-icon icon="mdi-database" size="40" color="info" />
            <div>
              <div class="text-h6 font-weight-bold">{{ stats.total.toLocaleString() }}</div>
              <div class="text-caption text-medium-emphasis">总记录数</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="4" lg="2">
        <v-card>
          <v-card-text class="d-flex align-center ga-3">
            <v-icon icon="mdi-chart-line" size="40" color="success" />
            <div>
              <div class="text-h6 font-weight-bold">{{ stats.avg_value }}</div>
              <div class="text-caption text-medium-emphasis">平均参数值</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="4" lg="2">
        <v-card>
          <v-card-text class="d-flex align-center ga-3">
            <v-icon icon="mdi-arrow-up-right" size="40" color="warning" />
            <div>
              <div class="text-h6 font-weight-bold">{{ stats.max_value }}</div>
              <div class="text-caption text-medium-emphasis">最大参数值</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="4" lg="2">
        <v-card>
          <v-card-text class="d-flex align-center ga-3">
            <v-icon icon="mdi-arrow-down-right" size="40" color="error" />
            <div>
              <div class="text-h6 font-weight-bold">{{ stats.min_value }}</div>
              <div class="text-caption text-medium-emphasis">最小参数值</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="4" lg="2">
        <v-card>
          <v-card-text class="d-flex align-center ga-3">
            <v-icon icon="mdi-cog" size="40" color="purple" />
            <div>
              <div class="text-h6 font-weight-bold">{{ stats.machine_count }}</div>
              <div class="text-caption text-medium-emphasis">设备数量</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="4" lg="2">
        <v-card>
          <v-card-text class="d-flex align-center ga-3">
            <v-icon icon="mdi-layers" size="40" color="pink" />
            <div>
              <div class="text-h6 font-weight-bold">{{ stats.process_type_count }}</div>
              <div class="text-caption text-medium-emphasis">工艺类型</div>
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
                v-model="queryParams.process_type"
                label="工艺类型"
                placeholder="请输入工艺类型"
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
                v-model="queryParams.product_model"
                label="产品型号"
                placeholder="请输入产品型号"
                clearable
                density="compact"
              />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-text-field
                v-model="queryParams.param_name"
                label="参数名称"
                placeholder="请输入参数名称"
                clearable
                density="compact"
              />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-text-field
                v-model.number="queryParams.param_value_min"
                label="参数值最小"
                type="number"
                placeholder="最小值"
                clearable
                density="compact"
              />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-text-field
                v-model.number="queryParams.param_value_max"
                label="参数值最大"
                type="number"
                placeholder="最大值"
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
        <v-icon icon="mdi-chart-line" />
        参数趋势分析
        <v-spacer />
        <v-select
          v-model="trendParams.param_name"
          :items="paramNames"
          label="选择参数"
          density="compact"
          style="max-width: 200px"
          @update:model-value="loadTrendData"
        />
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
    <v-card>
      <v-card-title class="d-flex align-center ga-2">
        <v-icon icon="mdi-table" />
        工艺参数明细
        <v-spacer />
        <span class="text-caption text-medium-emphasis">共 {{ total }} 条记录</span>
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
      >
        <template v-slot:item.create_time="{ item }">
          {{ formatDateTime(item.create_time) }}
        </template>
        <template v-slot:item.process_type="{ item }">
          <v-chip v-if="item.process_type" size="small" variant="tonal" color="primary">{{ item.process_type }}</v-chip>
          <span v-else>-</span>
        </template>
        <template v-slot:item.machine_id="{ item }">
          <v-chip v-if="item.machine_id" size="small" variant="tonal" color="teal">{{ item.machine_id }}</v-chip>
          <span v-else>-</span>
        </template>
        <template v-slot:item.param_value="{ item }">
          <span :class="getValueClass(item.param_value)">{{ item.param_value }}</span>
        </template>
        <template v-slot:item.start_code="{ item }">
          <v-chip v-if="item.start_code" size="small" variant="tonal" color="orange">{{ item.start_code }}</v-chip>
          <span v-else>-</span>
        </template>
        <template v-slot:no-data>
          <div class="text-center pa-8">
            <v-icon icon="mdi-inbox" size="48" color="grey-lighten-1" />
            <p class="text-medium-emphasis mt-2">暂无数据</p>
          </div>
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { processParamApi } from '@/api'
import { formatDateTime } from '@/utils/datetime'

const showSearch = ref(true)

const intervalOptions = [
  { title: '分钟', value: 'minute' },
  { title: '小时', value: 'hour' },
  { title: '天', value: 'day' },
]

const headers = [
  { title: 'ID', key: 'id', width: '70px' },
  { title: '创建时间', key: 'create_time' },
  { title: '工艺类型', key: 'process_type' },
  { title: '设备编号', key: 'machine_id' },
  { title: '产品型号', key: 'product_model' },
  { title: '参数名称', key: 'param_name' },
  { title: '参数值', key: 'param_value' },
  { title: '单位', key: 'unit' },
  { title: '启动码', key: 'start_code' },
  { title: '工艺编号', key: 'process_no' },
  { title: '操作员', key: 'operator' },
]

const loading = ref(false)
const dataList = ref([])
const total = ref(0)
const stats = ref({
  total: 0,
  avg_value: 0,
  max_value: 0,
  min_value: 0,
  machine_count: 0,
  process_type_count: 0
})
const paramNames = ref([])
const trendChart = ref(null)
const trendChartEl = ref(null)

const queryParams = reactive({
  page: 1,
  page_size: 20,
  start_time: '',
  end_time: '',
  process_type: '',
  machine_id: '',
  product_model: '',
  param_name: '',
  param_value_min: null,
  param_value_max: null,
  start_code: ''
})

const trendParams = reactive({
  param_name: '',
  interval: 'hour',
  machine_id: '',
  start_time: '',
  end_time: '',
  process_type: ''
})

const getValueClass = (value) => {
  if (value >= stats.value.max_value * 0.9) return 'text-error'
  if (value <= stats.value.min_value * 1.1) return 'text-success'
  return ''
}

const loadData = async () => {
  loading.value = true
  try {
    const params = { ...queryParams }
    // 清除空值
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null) {
        delete params[key]
      }
    })

    const response = await processParamApi.getList(params)
    dataList.value = response.data.items || []
    total.value = response.data.total || 0

    // 提取参数名称列表
    const names = [...new Set(dataList.value.map(item => item.param_name).filter(Boolean))]
    paramNames.value = names

    // 如果是第一次加载，自动选择第一个参数显示趋势
    if (names.length > 0 && !trendParams.param_name) {
      trendParams.param_name = names[0]
      loadTrendData()
    }
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

    const response = await processParamApi.getStats(params)
    stats.value = response.data
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
}

const loadTrendData = async () => {
  if (!trendParams.param_name) return

  try {
    const params = {
      param_name: trendParams.param_name,
      interval: trendParams.interval,
      machine_id: queryParams.machine_id || undefined,
      start_time: queryParams.start_time || undefined,
      end_time: queryParams.end_time || undefined,
      process_type: queryParams.process_type || undefined
    }

    const response = await processParamApi.getTrend(params)
    const trendData = response.data || []

    // 渲染图表
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

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['平均值', '最大值', '最小值'],
      textStyle: {
        color: '#7ec8ff'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '60px',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: data.map(item => item.time_point),
      axisLabel: {
        color: '#7ec8ff',
        rotate: 45
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(0, 212, 255, 0.3)'
        }
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#7ec8ff'
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(0, 212, 255, 0.3)'
        }
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(0, 212, 255, 0.1)'
        }
      }
    },
    series: [
      {
        name: '平均值',
        type: 'line',
        smooth: true,
        data: data.map(item => item.avg_value),
        itemStyle: {
          color: '#00d4ff'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 212, 255, 0.3)' },
            { offset: 1, color: 'rgba(0, 212, 255, 0)' }
          ])
        }
      },
      {
        name: '最大值',
        type: 'line',
        smooth: true,
        data: data.map(item => item.max_value),
        itemStyle: {
          color: '#00ff88'
        }
      },
      {
        name: '最小值',
        type: 'line',
        smooth: true,
        data: data.map(item => item.min_value),
        itemStyle: {
          color: '#ffaa00'
        }
      }
    ]
  }

  trendChart.value.setOption(option)
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
  queryParams.process_type = ''
  queryParams.machine_id = ''
  queryParams.product_model = ''
  queryParams.param_name = ''
  queryParams.param_value_min = null
  queryParams.param_value_max = null
  queryParams.start_code = ''

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

    const response = await processParamApi.export(params)

    // 创建下载链接
    const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    const filename = `工艺参数_${new Date().getTime()}.csv`
    link.download = filename
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('导出失败:', error)
  }
}

// 监听窗口大小变化，重新渲染图表
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
})
</script>
