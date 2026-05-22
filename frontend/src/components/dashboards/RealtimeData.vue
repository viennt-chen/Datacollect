<template>
  <div class="realtime-data" :class="{ 'fullscreen-mode': isFullscreen }">
    <!-- 第一行：控制栏和数据概览 -->
    <div class="row row-1">
      <!-- 筛选控制面板 -->
      <div class="panel control-panel">
        <div class="panel-header">
          <i class="mdi mdi-filter"></i>
          <span>数据筛选</span>
        </div>
        <div class="panel-body">
          <div class="filter-controls">
            <div class="filter-item">
              <label><i class="mdi mdi-format-list-bulleted"></i> 显示数量:</label>
              <select v-model="selectedLimit" @change="loadData" class="tech-select">
                <option value="10">10 条</option>
                <option value="20">20 条</option>
                <option value="50">50 条</option>
                <option value="100">100 条</option>
              </select>
            </div>
            
            <div class="filter-item">
              <label><i class="mdi mdi-cog"></i> 设备筛选:</label>
              <select v-model="selectedMachine" @change="loadData" class="tech-select">
                <option value="">全部设备</option>
                <option v-for="machine in machineList" :key="machine" :value="machine">
                  {{ machine }}
                </option>
              </select>
            </div>
            
            <div class="filter-item">
              <button class="refresh-btn" @click="loadData" :disabled="isLoading">
                <i class="mdi mdi-refresh" :class="{ 'spinning': isLoading }"></i>
                <span>刷新数据</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 实时状态面板 -->
      <div class="panel status-panel">
        <div class="panel-header">
          <i class="mdi mdi-broadcast"></i>
          <span>实时状态</span>
        </div>
        <div class="panel-body">
          <div class="status-grid">
            <div class="status-item">
              <div class="status-indicator live">
                <span class="pulse-dot"></span>
                <span class="status-text">实时更新</span>
              </div>
            </div>
            <div class="status-item">
              <div class="status-label">最后更新</div>
              <div class="status-value">{{ lastUpdateTime }}</div>
            </div>
            <div class="status-item">
              <div class="status-label">数据总数</div>
              <div class="status-value highlight">{{ realtimeData.length }}</div>
            </div>
            <div class="status-item">
              <div class="status-label">刷新间隔</div>
              <div class="status-value">10 秒</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 第二行：实时数据表格 -->
    <div class="row row-2">
      <div class="panel wide-panel">
        <div class="panel-header">
          <i class="mdi mdi-table"></i>
          <span>实时生产数据</span>
          <div class="header-actions">
            <span class="data-badge">
              <i class="mdi mdi-database"></i>
              {{ realtimeData.length }} 条记录
            </span>
          </div>
        </div>
        <div class="panel-body">
          <div class="table-container">
            <table class="tech-table">
              <thead>
                <tr>
                  <th><i class="mdi mdi-clock"></i> 时间</th>
                  <th>启动码</th>
                  <th>设备 ID</th>
                  <th>操作员</th>
                  <th>集团</th>
                  <th>工厂</th>
                  <th>产线</th>
                  <th>工站编号</th>
                  <th><i class="mdi mdi-hourglass"></i> 生产时长 (秒)</th>
                  <th><i class="mdi mdi-timer"></i> 机器时长 (秒)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(flow, index) in realtimeData" :key="index" class="data-row">
                  <td class="time-cell">{{ formatDateTime(flow.start_time) }}</td>
                  <td class="code-cell"><span class="tech-badge">{{ flow.start_code }}</span></td>
                  <td class="machine-cell">{{ flow.machine_id || '-' }}</td>
                  <td class="operator-cell">{{ flow.operator_name || flow.operator_id || '-' }}</td>
                  <td class="group-cell">{{ flow.group_short_name || flow.group_name || flow.group_code || '-' }}</td>
                  <td class="factory-cell">{{ flow.factory_name || flow.factory_code || '-' }}</td>
                  <td><span class="line-badge">{{ flow.line_code || '-' }}</span></td>
                  <td><span class="process-badge" :class="getProcessNoClass(flow.process_no)">{{ flow.process_no || '-' }}</span></td>
                  <td>
                    <span :class="getDurationClass(flow.duration_seconds)" class="duration-value">
                      {{ flow.duration_seconds ? Number(flow.duration_seconds).toFixed(2) : '-' }}
                    </span>
                  </td>
                  <td>
                    <span class="machine-duration">
                      {{ flow.machine_duration_seconds ? Number(flow.machine_duration_seconds).toFixed(2) : '-' }}
                    </span>
                  </td>
                </tr>
                <tr v-if="realtimeData.length === 0 && !isLoading" class="empty-row">
                  <td colspan="10">
                    <div class="empty-state">
                      <i class="mdi mdi-inbox"></i>
                      <p>暂无实时数据</p>
                    </div>
                  </td>
                </tr>
                <tr v-if="isLoading" class="loading-row">
                  <td colspan="10">
                    <div class="loading-state">
                      <i class="mdi mdi-refresh spinning"></i>
                      <p>加载中...</p>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { dashboardApi } from '@/api'

const props = defineProps({
  limit: {
    type: String,
    default: '20'
  },
  isFullscreen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:lastUpdate'])

const selectedLimit = ref(props.limit)
const selectedMachine = ref('')
const lastUpdateTime = ref('-')
const realtimeData = ref([])
const machineList = ref([])
const isLoading = ref(false)
let realtimeTimer = null

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  try {
    const date = new Date(datetime)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch {
    return datetime
  }
}

const getDurationClass = (duration) => {
  if (!duration) return 'duration-normal'
  if (duration < 60) return 'duration-fast'
  if (duration < 120) return 'duration-medium'
  return 'duration-slow'
}

const getProcessNoClass = (processNo) => {
  if (!processNo) return 'process-default'
  if (processNo.includes('A')) return 'process-a'
  if (processNo.includes('B')) return 'process-b'
  return 'process-default'
}

const loadData = async () => {
  if (isLoading.value) return
  
  try {
    isLoading.value = true
    
    const params = { limit: selectedLimit.value }
    if (selectedMachine.value) {
      params.machine_id = selectedMachine.value
    }
    
    const response = await dashboardApi.getRealtime(params)
    realtimeData.value = response.data.latest_flows || response.data.data || response.data || []
    
    // 提取设备列表
    machineList.value = [...new Set(
      realtimeData.value
        .map(item => item.machine_id)
        .filter(Boolean)
    )]
    
    lastUpdateTime.value = new Date().toLocaleTimeString('zh-CN')
    emit('update:lastUpdate', lastUpdateTime.value)
  } catch (error) {
    console.error('加载实时数据失败:', error)
  } finally {
    isLoading.value = false
  }
}

watch(() => props.limit, (newVal) => {
  if (newVal !== selectedLimit.value) {
    selectedLimit.value = newVal
    loadData()
  }
})

onMounted(() => {
  loadData()
  
  // 每 10 秒刷新一次
  realtimeTimer = setInterval(() => {
    loadData()
  }, 10000)
})

onUnmounted(() => {
  if (realtimeTimer) clearInterval(realtimeTimer)
})
</script>

<style scoped>
.realtime-data {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a1628 0%, #1a2a4a 50%, #0a1628 100%);
  padding: 12px;
}

.realtime-data.fullscreen-mode {
  padding: 16px;
}

.row {
  display: grid;
  gap: 12px;
  margin-bottom: 12px;
}

.row-1 {
  grid-template-columns: 1.5fr 1fr;
}

.row-2 {
  grid-template-columns: 1fr;
}

.panel {
  background: rgba(10, 30, 60, 0.6);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 8px;
  overflow: hidden;
  backdrop-filter: blur(10px);
  box-shadow: 0 0 30px rgba(0, 212, 255, 0.1);
  transition: all 0.3s ease;
}

.panel:hover {
  box-shadow: 0 0 40px rgba(0, 212, 255, 0.15);
}

.panel-header {
  padding: 12px 16px;
  background: linear-gradient(90deg, rgba(0, 212, 255, 0.1), transparent);
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
  color: #00d4ff;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-header i {
  font-size: 16px;
}

.header-actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
}

.data-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: rgba(0, 212, 255, 0.15);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 12px;
  font-size: 12px;
  color: #00d4ff;
  font-weight: 600;
}

.panel-body {
  padding: 16px;
}

.control-panel .panel-body {
  padding: 12px 16px;
}

.filter-controls {
  display: flex;
  gap: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-item label {
  font-size: 13px;
  color: #7ec8ff;
  font-weight: 500;
  white-space: nowrap;
}

.tech-select {
  padding: 8px 12px;
  background: rgba(0, 50, 100, 0.5);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 6px;
  color: #00d4ff;
  font-size: 13px;
  cursor: pointer;
  outline: none;
  transition: all 0.3s;
}

.tech-select:hover {
  border-color: rgba(0, 212, 255, 0.5);
  background: rgba(0, 50, 100, 0.7);
}

.tech-select:focus {
  border-color: #00d4ff;
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
}

.tech-select option {
  background: #0a1628;
  color: #00d4ff;
}

.refresh-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 153, 255, 0.2));
  border: 1px solid rgba(0, 212, 255, 0.4);
  border-radius: 6px;
  color: #00d4ff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.refresh-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.3), rgba(0, 153, 255, 0.3));
  border-color: #00d4ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.status-panel .panel-body {
  padding: 12px 16px;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  align-items: center;
}

.status-item {
  text-align: center;
}

.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 13px;
}

.status-indicator.live {
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.2), rgba(0, 204, 106, 0.2));
  border: 1px solid rgba(0, 255, 136, 0.4);
  color: #00ff88;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background: #00ff88;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
}

.status-label {
  font-size: 12px;
  color: #7ec8ff;
  margin-bottom: 4px;
}

.status-value {
  font-size: 16px;
  font-weight: 600;
  color: #00d4ff;
}

.status-value.highlight {
  color: #00ff88;
  text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
}

.table-container {
  overflow-x: auto;
  border-radius: 6px;
  border: 1px solid rgba(0, 212, 255, 0.1);
}

.tech-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.tech-table thead {
  background: rgba(0, 50, 100, 0.5);
}

.tech-table th {
  padding: 12px 12px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: #00d4ff;
  border-bottom: 2px solid rgba(0, 212, 255, 0.3);
  white-space: nowrap;
}

.tech-table th i {
  margin-right: 6px;
  font-size: 11px;
}

.tech-table tbody tr {
  border-bottom: 1px solid rgba(0, 212, 255, 0.1);
  transition: all 0.3s;
}

.tech-table tbody tr:hover {
  background: rgba(0, 212, 255, 0.05);
}

.tech-table td {
  padding: 12px;
  color: #b8d4ff;
  font-size: 13px;
}

.time-cell {
  color: #00d4ff;
  font-weight: 500;
  font-family: 'Consolas', 'Monaco', monospace;
}

.code-cell .tech-badge,
.line-badge {
  display: inline-block;
  padding: 4px 10px;
  background: rgba(0, 212, 255, 0.15);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 12px;
  font-size: 12px;
  color: #00d4ff;
  font-weight: 500;
}

.machine-cell {
  color: #00ff88;
  font-weight: 500;
}

.process-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.process-a {
  background: rgba(0, 255, 136, 0.2);
  border: 1px solid rgba(0, 255, 136, 0.4);
  color: #00ff88;
}

.process-b {
  background: rgba(0, 212, 255, 0.2);
  border: 1px solid rgba(0, 212, 255, 0.4);
  color: #00d4ff;
}

.process-default {
  background: rgba(148, 163, 184, 0.2);
  border: 1px solid rgba(148, 163, 184, 0.4);
  color: #94a3b8;
}

.duration-value {
  font-weight: 600;
  font-family: 'Consolas', 'Monaco', monospace;
}

.duration-fast {
  color: #00ff88;
}

.duration-medium {
  color: #ffaa00;
}

.duration-slow {
  color: #ff4444;
}

.duration-normal {
  color: #7ec8ff;
}

.machine-duration {
  color: #7ec8ff;
  font-family: 'Consolas', 'Monaco', monospace;
}

.empty-state,
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px 20px;
}

.empty-state i,
.loading-state i {
  font-size: 48px;
  color: rgba(0, 212, 255, 0.3);
}

.empty-state p,
.loading-state p {
  font-size: 14px;
  color: #7ec8ff;
  margin: 0;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-row,
.loading-row {
  background: transparent;
}

.empty-row td,
.loading-row td {
  padding: 40px 20px;
}

@media (max-width: 1400px) {
  .row-1 {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .realtime-data {
    padding: 8px;
  }
  
  .filter-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-item {
    flex-direction: column;
    align-items: stretch;
  }
  
  .status-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .tech-table {
    font-size: 12px;
  }
  
  .tech-table th,
  .tech-table td {
    padding: 8px 6px;
  }
}
</style>
