import axios from 'axios'

const API_BASE_URL = '/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 秒超时
  headers: {
    'Content-Type': 'application/json'
  },
  retry: 3, // 重试次数
  retryDelay: 1000 // 重试间隔
})

// 添加请求重试机制
apiClient.interceptors.response.use(
  response => response,
  error => {
    const config = error.config
    if (config && config.retry && config.__retryCount < config.retry) {
      config.__retryCount = (config.__retryCount || 0) + 1
      const delay = config.retryDelay || 1000
      console.log(`请求重试 ${config.__retryCount}/${config.retry}, ${delay}ms 后重试...`)
      return new Promise(resolve => {
        setTimeout(() => {
          resolve(apiClient(config))
        }, delay)
      })
    }
    return Promise.reject(error)
  }
)

export const dashboardApi = {
  getSummary(params) {
    return apiClient.get('/dashboard/summary', { params })
  },
  
  getTrend(params) {
    return apiClient.get('/dashboard/trend', { params })
  },
  
  getRealtime(params) {
    return apiClient.get('/dashboard/realtime', { params })
  },
  
  getMachineStats(machineId, params) {
    return apiClient.get(`/dashboard/machine/${machineId}/stats`, { params })
  },
  
  getMachineMonitorData(params) {
    return apiClient.get('/dashboard/machine-monitor', { params })
  },
  
  getDeviceDetailData(params) {
    return apiClient.get('/dashboard/device-detail', { params })
  }
}

// 认证相关 API
export const authApi = {
  login(data) {
    return apiClient.post('/auth/login', data)
  },
  
  logout() {
    return apiClient.post('/auth/logout', null, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
  },
  
  refreshToken(refreshToken) {
    return apiClient.post('/auth/refresh', { refresh_token: refreshToken })
  },
  
  getCurrentUser() {
    return apiClient.get('/auth/me', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
  },
  
  changePassword(data) {
    return apiClient.post('/auth/change-password', data, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
  }
}

// 工艺参数追溯 API
export const processParamApi = {
  getList(params) {
    return apiClient.get('/process-params', { params })
  },
  
  getById(id) {
    return apiClient.get(`/process-params/${id}`)
  },
  
  getStats(params) {
    return apiClient.get('/process-params/stats', { params })
  },
  
  getTrend(params) {
    return apiClient.get('/process-params/trend', { params })
  },
  
  export(params) {
    return apiClient.get('/process-params/export', { 
      params,
      responseType: 'blob'
    })
  },
  
  getByMachine(machineId, params) {
    return apiClient.get(`/process-params/machine/${machineId}/params`, { params })
  },
  
  getByProcessType(processType, params) {
    return apiClient.get(`/process-params/process-type/${processType}/params`, { params })
  }
}

// 产品加工信息追溯 API
export const processingEventApi = {
  getList(params) {
    return apiClient.get('/processing-events', { params })
  },
  
  getById(id) {
    return apiClient.get(`/processing-events/${id}`)
  },
  
  getByStartCode(startCode) {
    return apiClient.get(`/processing-events/start-code/${startCode}`)
  },
  
  getStats(params) {
    return apiClient.get('/processing-events/stats', { params })
  },
  
  getTrend(params) {
    return apiClient.get('/processing-events/trend', { params })
  },
  
  export(params) {
    return apiClient.get('/processing-events/export', { 
      params,
      responseType: 'blob'
    })
  }
}

// 数据采集管理 API
export const dataCollectorApi = {
  getStats() {
    return apiClient.get('/data-collector/stats')
  },
  
  getConfig() {
    return apiClient.get('/data-collector/config')
  },
  
  control(action) {
    return apiClient.post('/data-collector/control', { action })
  },
  
  getEventStats(params) {
    return apiClient.get('/data-collector/events/stats', { params })
  },
  
  getRawDataStats(params) {
    return apiClient.get('/data-collector/raw-data/stats', { params })
  },
  
  getRecentEvents(params) {
    return apiClient.get('/data-collector/recent-events', { params })
  }
}

// MQTT Topic 配置 API
export const mqttTopicConfigApi = {
  getList(params) {
    return apiClient.get('/mqtt-topic-configs/', { params })
  },
  
  create(data) {
    return apiClient.post('/mqtt-topic-configs/', data)
  },
  
  update(id, data) {
    return apiClient.put(`/mqtt-topic-configs/${id}`, data)
  },
  
  delete(id) {
    return apiClient.delete(`/mqtt-topic-configs/${id}`)
  },
  
  toggle(id) {
    return apiClient.post(`/mqtt-topic-configs/${id}/toggle`)
  },
  
  getStatsSummary() {
    return apiClient.get('/mqtt-topic-configs/stats/summary')
  },
  
  batchDelete(configIds) {
    return apiClient.post('/mqtt-topic-configs/batch/delete', configIds)
  },
  
  batchToggle(configIds, enabled) {
    return apiClient.post('/mqtt-topic-configs/batch/toggle', { config_ids: configIds, enabled })
  },

  getFields(topicIds) {
    return apiClient.get('/mqtt-topic-configs/fields', {
      params: { topic_ids: topicIds },
      paramsSerializer: params => {
        return params.topic_ids.map(id => `topic_ids=${id}`).join('&')
      }
    })
  }
}

// 采集日志管理 API
export const collectorLogAPI = {
  getCollectorLogs(params) {
    return apiClient.get('/collector-logs/', { params })
  },
  
  getCollectorLog(id) {
    return apiClient.get(`/collector-logs/${id}`)
  },
  
  getLogsByTopic(topicName) {
    return apiClient.get(`/collector-logs/topic/${topicName}`)
  },
  
  getRecentErrors(limit = 50) {
    return apiClient.get('/collector-logs/errors/recent', { params: { limit } })
  },
  
  getLogStats(days = 7) {
    return apiClient.get('/collector-logs/stats', { params: { days } })
  },
  
  clearOldLogs(days = 30) {
    return apiClient.delete('/collector-logs/clear', { params: { days } })
  }
}

// 物料管理 API
export const materialAPI = {
  getMaterials(params) {
    return apiClient.get('/materials/', { params })
  },

  getMaterial(id) {
    return apiClient.get(`/materials/${id}`)
  },

  createMaterial(data) {
    return apiClient.post('/materials', data)
  },

  updateMaterial(id, data) {
    return apiClient.put(`/materials/${id}`, data)
  },

  deleteMaterial(id) {
    return apiClient.delete(`/materials/${id}`)
  },

  getStats() {
    return apiClient.get('/materials/stats/summary')
  },

  exportMaterials(params) {
    return apiClient.get('/materials/export', { params, responseType: 'blob' })
  },

  importMaterials(file) {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/materials/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  downloadTemplate() {
    return apiClient.get('/materials/download-template', {
      responseType: 'blob'
    })
  }
}

// 兼容旧名称
export const productAPI = materialAPI

// 设备管理 API
export const deviceAPI = {
  getDevices(params) {
    return apiClient.get('/devices/', { params })
  },
  
  getDevice(deviceCode) {
    return apiClient.get(`/devices/${deviceCode}`)
  },

  createDevice(data) {
    return apiClient.post('/devices/', data)
  },

  updateDevice(deviceCode, data) {
    return apiClient.put(`/devices/${deviceCode}`, data)
  },

  deleteDevice(deviceCode) {
    return apiClient.delete(`/devices/${deviceCode}`)
  },

  batchToggleDashboard(deviceCodes, show) {
    return apiClient.post('/devices/batch/toggle-dashboard', deviceCodes, { params: { show } })
  },

  getStats() {
    return apiClient.get('/devices/stats/summary')
  },

  exportDevices(params) {
    return apiClient.get('/devices/export', { params, responseType: 'blob' })
  },

  importDevices(file) {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/devices/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  downloadTemplate() {
    return apiClient.get('/devices/download-template', { responseType: 'blob' })
  },
  
  // ALARM 数据
  getAlarmData(params) {
    return apiClient.get('/devices/alarm-data', { params })
  },
  
  // PV 数据
  getPvData(params) {
    return apiClient.get('/devices/pv-data', { params })
  },
  
  // SV 数据
  getSvData(params) {
    return apiClient.get('/devices/sv-data', { params })
  },
  
  // Event 数据
  getEventData(params) {
    return apiClient.get('/devices/event-data', { params })
  },
  
  // 获取设备数据采集配置
  getDeviceDataCollectionConfig(deviceCode) {
    return apiClient.get(`/devices/${deviceCode}/data-collection-config`)
  },
  
  // 获取最新压缩数据并解压
  getLatestCompressedData(params) {
    return apiClient.get('/devices/compressed-data/latest', { params })
  },
  
  // 数据源相关 API
  getDataSourceStatus(deviceCode) {
    return apiClient.get(`/devices/${deviceCode}/data-source/status`)
  },

  getLatestData(deviceCode, params) {
    return apiClient.get(`/devices/${deviceCode}/data-source/latest`, { params })
  },

  getHistoricalData(deviceCode, params) {
    return apiClient.get(`/devices/${deviceCode}/data-source/historical`, { params })
  },

  subscribeRealtimeData(deviceCode, params) {
    return apiClient.post(`/devices/${deviceCode}/data-source/subscribe`, null, { params })
  },

  unsubscribeRealtimeData(deviceCode, params) {
    return apiClient.post(`/devices/${deviceCode}/data-source/unsubscribe`, null, { params })
  },

  getDeviceMonitorStatus(deviceCode) {
    return apiClient.get(`/devices/${deviceCode}/monitor/status`)
  },

  syncDeviceStatus(deviceCode) {
    return apiClient.post(`/devices/${deviceCode}/sync-status`)
  },

  getDeviceTopicsAndFields(deviceCode) {
    return apiClient.get(`/devices/status-monitor-configs/device/${deviceCode}/topics`)
  },

  getStatusConfigs(deviceCode, statusType) {
    const params = statusType ? { status_type: statusType } : {}
    return apiClient.get(`/devices/status-monitor-configs/device/${deviceCode}`, { params })
  },

  getBasicRules(statusType) {
    const params = statusType ? { status_type: statusType } : {}
    return apiClient.get('/devices/status-monitor-configs/basic-rules', { params })
  },

  getAllDeviceRules(deviceCode, statusType) {
    const params = statusType ? { status_type: statusType } : {}
    return apiClient.get(`/devices/status-monitor-configs/device/${deviceCode}/all-rules`, { params })
  },
  
  createStatusConfig(data) {
    return apiClient.post('/devices/status-monitor-configs/', data)
  },
  
  updateStatusConfig(id, data) {
    return apiClient.put(`/devices/status-monitor-configs/${id}`, data)
  },
  
  deleteStatusConfig(id) {
    return apiClient.delete(`/devices/status-monitor-configs/${id}`)
  },
  
  getDeviceLatestMessage(deviceCode, topicName) {
    return apiClient.get(`/devices/${deviceCode}/mqtt/latest`, {
      params: { topic_name: topicName }
    })
  },

  // 当前加工产品配置 API
  getCurrentProductConfigs(deviceCode) {
    return apiClient.get(`/devices/current-product-configs/device/${deviceCode}`)
  },

  getDeviceAvailableTopics(deviceCode) {
    return apiClient.get(`/devices/current-product-configs/device/${deviceCode}/topics`)
  },

  createCurrentProductConfig(data) {
    return apiClient.post('/devices/current-product-configs/', data)
  },

  updateCurrentProductConfig(id, data) {
    return apiClient.put(`/devices/current-product-configs/${id}`, data)
  },

  deleteCurrentProductConfig(id) {
    return apiClient.delete(`/devices/current-product-configs/${id}`)
  },

  toggleCurrentProductConfig(id) {
    return apiClient.post(`/devices/current-product-configs/${id}/toggle`)
  },

  batchToggleProductConfigs(configIds, enabled) {
    return apiClient.post('/devices/current-product-configs/batch/toggle', {
      config_ids: configIds,
      enabled: enabled
    })
  },

  testCurrentProductConfig(id) {
    return apiClient.post(`/devices/current-product-configs/${id}/test`)
  },

  getProductConfigStats(deviceCode) {
    const params = deviceCode ? { device_code: deviceCode } : {}
    return apiClient.get('/devices/current-product-configs/stats/summary', { params })
  }
}

// DB参数曲线 API
export const servoCurveAPI = {
  getDeviceCurves(deviceCode, partNumber) {
    const params = partNumber ? { part_number: partNumber } : {}
    return apiClient.get(`/devices/servo-curves/device/${deviceCode}/curves`, { params })
  },
  
  listCurves(params) {
    return apiClient.get('/devices/servo-curves/', { params })
  },
  
  getCurve(id) {
    return apiClient.get(`/devices/servo-curves/${id}`)
  },
  
  createCurve(data) {
    return apiClient.post('/devices/servo-curves/', data)
  },
  
  updateCurve(id, data) {
    return apiClient.put(`/devices/servo-curves/${id}`, data)
  },
  
  deleteCurve(id) {
    return apiClient.delete(`/devices/servo-curves/${id}`)
  },
  
  importCSV(deviceCode, curveName, partNumber, servoAxis, file, options = {}) {
    const formData = new FormData()
    formData.append('file', file)

    const params = new URLSearchParams({
      device_code: deviceCode,
      curve_name: curveName,
      servo_axis: servoAxis
    })
    
    if (partNumber) params.append('part_number', partNumber)
    if (options.position_tolerance) params.append('position_tolerance', options.position_tolerance)
    if (options.time_tolerance_ms) params.append('time_tolerance_ms', options.time_tolerance_ms)
    if (options.description) params.append('description', options.description)
    
    return apiClient.post(`/devices/servo-curves/import/csv?${params.toString()}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  importJSON(deviceCode, curveName, partNumber, servoAxis, file, options = {}) {
    const formData = new FormData()
    formData.append('file', file)

    const params = new URLSearchParams({
      device_code: deviceCode,
      curve_name: curveName,
      servo_axis: servoAxis
    })
    
    if (partNumber) params.append('part_number', partNumber)
    if (options.position_tolerance) params.append('position_tolerance', options.position_tolerance)
    if (options.time_tolerance_ms) params.append('time_tolerance_ms', options.time_tolerance_ms)
    if (options.description) params.append('description', options.description)
    
    return apiClient.post(`/devices/servo-curves/import/json?${params.toString()}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  matchCurve(curveId, realtimeData) {
    return apiClient.post(`/devices/servo-curves/match/${curveId}`, realtimeData)
  }
}

// 报警管理 API
export const alarmAPI = {
  getAlarms(params) {
    return apiClient.get('/alarms/', { params })
  },
  
  getAlarm(id) {
    return apiClient.get(`/alarms/${id}`)
  },
  
  createAlarm(data) {
    return apiClient.post('/alarms/', data)
  },
  
  updateAlarm(id, data) {
    return apiClient.put(`/alarms/${id}`, data)
  },
  
  handleAlarm(id, data) {
    return apiClient.post(`/alarms/${id}/handle`, data)
  },
  
  deleteAlarm(id) {
    return apiClient.delete(`/alarms/${id}`)
  },
  
  batchDeleteAlarms(ids) {
    return apiClient.post('/alarms/batch/delete', ids)
  },
  
  batchHandleAlarms(ids, data) {
    return apiClient.post('/alarms/batch/handle', data, {
      params: { alarm_ids: ids }
    })
  },
  
  getStats(params) {
    return apiClient.get('/alarms/stats', { params })
  },
  
  getRecentAlarms(limit = 10) {
    return apiClient.get('/alarms/recent', { params: { limit } })
  },
  
  clearOldAlarms(days = 30) {
    return apiClient.delete('/alarms/clear', { params: { days } })
  }
}

// ========== ERP U9 订单查询 API ==========
// 对接 U9 ERP 系统，查询远程订单数据
export const erpOrderAPI = {
  // 单零件订单查询
  querySinglePartOrder(partNumber, u9MaterialCode, startDate, endDate) {
    const params = { start_date: startDate, end_date: endDate }
    if (partNumber) params.part_number = partNumber
    if (u9MaterialCode) params.u9_material_code = u9MaterialCode
    return apiClient.get('/erp-orders/query-single-part', { params })
  },
  // 按时间范围批量查询订单
  queryOrdersByTime(data) {
    return apiClient.post('/erp-orders/query-orders-by-time', data)
  },
  // 按零件号查询今日订单
  queryTodayOrderByPart(partNumber, u9MaterialCode) {
    const data = {}
    if (partNumber) data.part_number = partNumber
    if (u9MaterialCode) data.u9_material_code = u9MaterialCode
    return apiClient.post('/erp-orders/query-today-by-part', data)
  },
  // 查询今日所有订单
  queryTodayOrders(partNumber) {
    return apiClient.post('/erp-orders/query-today-orders', null, { params: { part_number: partNumber } })
  },
  // 定时任务调度器
  getSchedulerStatus() { return apiClient.get('/erp-orders/scheduler/status') },
  startScheduler(cronExpression) {
    return apiClient.post('/erp-orders/scheduler/start', null, { params: { cron_expression: cronExpression } })
  },
  stopScheduler() { return apiClient.post('/erp-orders/scheduler/stop') },
  triggerScheduler() { return apiClient.post('/erp-orders/scheduler/trigger') },
}

// ========== 本地订单数据库 API ==========
// 本地数据库订单数据的查询、统计、清除
export const localOrderAPI = {
  // 订单列表（分页）
  getOrderList(params) { return apiClient.get('/product-orders/', { params }) },
  // 订单统计
  getOrderStats(date) { return apiClient.get('/product-orders/stats', { params: { date } }) },
  // 今日订单
  getTodayOrders(partNumber) { return apiClient.get('/product-orders/today', { params: { part_number: partNumber } }) },
  // 清除今日数据
  clearTodayOrders() { return apiClient.delete('/product-orders/clear-today') },
  // 综合分析（本地快速分析）
  getComprehensiveAnalysis(startDate, endDate) {
    return apiClient.get('/product-orders/analysis/comprehensive', { params: { start_date: startDate, end_date: endDate } })
  },
}

// ========== 订单分析 API ==========
// 多维度统计分析（按部门、项目、零件、仓库、单据类型、趋势等）
export const orderAnalysisAPI = {
  // 订单汇总统计
  getSummary(startDate, endDate, partNumber) {
    const data = { start_date: startDate, end_date: endDate }
    if (partNumber) data.part_number = partNumber
    return apiClient.post('/product-orders/analysis/summary', data)
  },
  // 按部门统计
  getByDepartment(startDate, endDate, partNumber) {
    const data = { start_date: startDate, end_date: endDate }
    if (partNumber) data.part_number = partNumber
    return apiClient.post('/product-orders/analysis/by-department', data)
  },
  // 按项目统计
  getByProject(startDate, endDate, partNumber) {
    const data = { start_date: startDate, end_date: endDate }
    if (partNumber) data.part_number = partNumber
    return apiClient.post('/product-orders/analysis/by-project', data)
  },
  // 每日趋势
  getDailyTrend(startDate, endDate, partNumber) {
    const data = { start_date: startDate, end_date: endDate }
    if (partNumber) data.part_number = partNumber
    return apiClient.post('/product-orders/analysis/daily-trend', data)
  },
  // 按零件号分析
  getByPart(startDate, endDate, partNumber) {
    const data = { start_date: startDate, end_date: endDate }
    if (partNumber) data.part_number = partNumber
    return apiClient.post('/product-orders/analysis/by-part', data)
  },
  // 按单据类型统计
  getByDocType(startDate, endDate, partNumber) {
    const data = { start_date: startDate, end_date: endDate }
    if (partNumber) data.part_number = partNumber
    return apiClient.post('/product-orders/analysis/by-doc-type', data)
  },
  // 按仓库统计
  getByWarehouse(startDate, endDate, partNumber) {
    const data = { start_date: startDate, end_date: endDate }
    if (partNumber) data.part_number = partNumber
    return apiClient.post('/product-orders/analysis/by-warehouse', data)
  },
  // 综合分析（一次性获取所有维度）
  getComprehensive(startDate, endDate, partNumber) {
    const data = { start_date: startDate, end_date: endDate }
    if (partNumber) data.part_number = partNumber
    return apiClient.post('/product-orders/analysis/comprehensive', data)
  },
}

// 质量管理 API
export const qualityAPI = {
  getQualityRecords(params) {
    return apiClient.get('/quality-records/', { params })
  },
  
  getQualityRecord(id) {
    return apiClient.get(`/quality-records/${id}`)
  },
  
  createQualityRecord(data) {
    return apiClient.post('/quality-records/', data)
  },
  
  updateQualityRecord(id, data) {
    return apiClient.put(`/quality-records/${id}`, data)
  },
  
  deleteQualityRecord(id) {
    return apiClient.delete(`/quality-records/${id}`)
  },
  
  getStats(params) {
    return apiClient.get('/quality-records/stats', { params })
  },
  
  export(params) {
    return apiClient.get('/quality-records/export', { 
      params,
      responseType: 'blob'
    })
  },
  
  getDefectTypes() {
    return apiClient.get('/quality-records/defect-types')
  }
}

// ========== 产品订单查询日志 API ==========
export const productOrderLogAPI = {
  // 获取日志列表
  getLogs(params = {}) {
    return apiClient.get('/product-order-logs/', { params })
  },
  
  // 获取单条日志
  getLog(logId) {
    return apiClient.get(`/product-order-logs/${logId}`)
  },
  
  // 获取统计信息
  getStats(queryDate) {
    return apiClient.get('/product-order-logs/stats', {
      params: { query_date: queryDate }
    })
  },
  
  // 删除日志
  deleteLog(logId) {
    return apiClient.delete(`/product-order-logs/${logId}`)
  },
  
  // 清空日志
  clearLogs(days) {
    return apiClient.delete('/product-order-logs/clear', {
      params: { days }
    })
  }
}

// ========== 本地订单加工记录 API ==========
export const orderProcessingAPI = {
  // 列表查询
  getRecords(params) {
    return apiClient.get('/order-processing-records/', { params })
  },

  // 获取今日所有设备的加工记录
  getTodayRecords() {
    return apiClient.get('/order-processing-records/today')
  },

  // 获取指定设备今日加工记录
  getDeviceTodayRecords(deviceCode) {
    return apiClient.get(`/order-processing-records/device/${deviceCode}/today`)
  },

  // 获取统计
  getStats(params) {
    return apiClient.get('/order-processing-records/stats', { params })
  },

  // 创建记录
  createRecord(data) {
    return apiClient.post('/order-processing-records/', data)
  },

  // 更新记录
  updateRecord(id, data) {
    return apiClient.put(`/order-processing-records/${id}`, data)
  },

  // 标记完成
  completeRecord(id) {
    return apiClient.post(`/order-processing-records/${id}/complete`)
  },

  // 删除记录
  deleteRecord(id) {
    return apiClient.delete(`/order-processing-records/${id}`)
  }
}

// ========== 车间管理 API ==========
export const workshopAPI = {
  list(params) { return apiClient.get('/workshops/', { params }) },
  all() { return apiClient.get('/workshops/all') },
  get(id) { return apiClient.get(`/workshops/${id}`) },
  create(data) { return apiClient.post('/workshops/', data) },
  update(id, data) { return apiClient.put(`/workshops/${id}`, data) },
  delete(id) { return apiClient.delete(`/workshops/${id}`) },
}

// ========== 项目管理 API ==========
export const projectAPI = {
  list(params) { return apiClient.get('/projects/', { params }) },
  all() { return apiClient.get('/projects/all') },
  get(id) { return apiClient.get(`/projects/${id}`) },
  create(data) { return apiClient.post('/projects/', data) },
  update(id, data) { return apiClient.put(`/projects/${id}`, data) },
  delete(id) { return apiClient.delete(`/projects/${id}`) },
  exportProjects(params) { return apiClient.get('/projects/export', { params, responseType: 'blob' }) },
  importProjects(file) {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/projects/import', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  downloadTemplate() { return apiClient.get('/projects/download-template', { responseType: 'blob' }) },
}

// ========== 物料分类管理 API ==========
export const materialCategoryAPI = {
  list() { return apiClient.get('/material-categories/') },
  create(data) { return apiClient.post('/material-categories/', data) },
  update(id, data) { return apiClient.put(`/material-categories/${id}`, data) },
  delete(id) { return apiClient.delete(`/material-categories/${id}`) },
}

// ========== BOM 物料清单管理 API ==========
export const bomAPI = {
  list(params) { return apiClient.get('/bom/', { params }) },
  all() { return apiClient.get('/bom/all') },
  get(id) { return apiClient.get(`/bom/${id}`) },
  create(data) { return apiClient.post('/bom/', data) },
  update(id, data) { return apiClient.put(`/bom/${id}`, data) },
  delete(id) { return apiClient.delete(`/bom/${id}`) },
  activate(id) { return apiClient.post(`/bom/${id}/activate`) },
  archive(id) { return apiClient.post(`/bom/${id}/archive`) },
  copy(id, data) { return apiClient.post(`/bom/${id}/copy`, data) },
  getTree(id, maxLevel) { return apiClient.get(`/bom/${id}/tree`, { params: { max_level: maxLevel } }) },
  explode(id, quantity, maxLevel) { return apiClient.get(`/bom/explode/${id}`, { params: { quantity, max_level: maxLevel } }) },
  whereUsed(productId) { return apiClient.get(`/bom/where-used/${productId}`) },
  getStats() { return apiClient.get('/bom/stats/summary') },
  addItem(bomId, data) { return apiClient.post(`/bom/${bomId}/items`, data) },
  updateItem(bomId, itemId, data) { return apiClient.put(`/bom/${bomId}/items/${itemId}`, data) },
  deleteItem(bomId, itemId) { return apiClient.delete(`/bom/${bomId}/items/${itemId}`) },
  reorder(bomId, itemOrder) { return apiClient.post(`/bom/${bomId}/items/reorder`, { item_order: itemOrder }) },
  moveItem(data) { return apiClient.post('/bom/items/move', data) },
}

// ========== 工艺路线模板 API ==========
export const productionFlowAPI = {
  list(params) { return apiClient.get('/production-flows/', { params }) },
  get(id) { return apiClient.get(`/production-flows/${id}`) },
  create(data) { return apiClient.post('/production-flows/', data) },
  update(id, data) { return apiClient.put(`/production-flows/${id}`, data) },
  delete(id) { return apiClient.delete(`/production-flows/${id}`) },
  templates() { return apiClient.get('/production-flows/templates') },
}

// ========== 工艺定义 API ==========
export const processDefinitionAPI = {
  list(params) { return apiClient.get('/process-definitions/', { params }) },
  get(id) { return apiClient.get(`/process-definitions/${id}`) },
  create(data) { return apiClient.post('/process-definitions/', data) },
  update(id, data) { return apiClient.put(`/process-definitions/${id}`, data) },
  delete(id) { return apiClient.delete(`/process-definitions/${id}`) },
  getDevices(id) { return apiClient.get(`/process-definitions/${id}/devices`) },
  getTopics(id) { return apiClient.get(`/process-definitions/${id}/topics`) },
  getProducts(id) { return apiClient.get(`/process-definitions/${id}/products`) },
  getLiveParams(id) { return apiClient.get(`/process-definitions/${id}/live-params`) },
  getNextCode(processType) { return apiClient.get('/process-definitions/next-code', { params: { process_type: processType } }) },
  getStats() { return apiClient.get('/process-definitions/stats/summary') },
}

// ========== 工艺参数历史 API ==========
export const processParamHistoryAPI = {
  create(data) { return apiClient.post('/process-param-histories/', data) },
  batchCreate(data) { return apiClient.post('/process-param-histories/batch', data) },
  list(processId, params) { return apiClient.get(`/process-param-histories/${processId}`, { params }) },
}

// ========== 流程执行实例 API ==========
export const productionFlowInstanceAPI = {
  list(params) { return apiClient.get('/production-flow-instances/', { params }) },
  get(id) { return apiClient.get(`/production-flow-instances/${id}`) },
  create(data) { return apiClient.post('/production-flow-instances/', data) },
  updateStep(instanceId, nodeId, data) { return apiClient.put(`/production-flow-instances/${instanceId}/nodes/${nodeId}`, data) },
  completeNode(instanceId, nodeId) { return apiClient.post(`/production-flow-instances/${instanceId}/complete-node/${nodeId}`) },
  complete(id) { return apiClient.post(`/production-flow-instances/${id}/complete`) },
  delete(id) { return apiClient.delete(`/production-flow-instances/${id}`) },
  stats(params) { return apiClient.get('/production-flow-instances/stats', { params }) },
}

// 事件关联查询 API
export const eventAssociationAPI = {
  // 正向关联：从加工事件查其他模块
  getDevice(eventId) { return apiClient.get(`/event-associations/${eventId}/device`) },
  getMaterial(eventId) { return apiClient.get(`/event-associations/${eventId}/material`) },
  getOrders(eventId) { return apiClient.get(`/event-associations/${eventId}/orders`) },
  getProcessParams(eventId) { return apiClient.get(`/event-associations/${eventId}/process-params`) },
  getProcessDefinition(eventId) { return apiClient.get(`/event-associations/${eventId}/process-definition`) },
  getAlarms(eventId) { return apiClient.get(`/event-associations/${eventId}/alarms`) },
  getQuality(eventId) { return apiClient.get(`/event-associations/${eventId}/quality`) },
  getCompressedData(eventId) { return apiClient.get(`/event-associations/${eventId}/compressed-data`) },
  getFlowInstance(eventId) { return apiClient.get(`/event-associations/${eventId}/flow-instance`) },
  getAll(eventId) { return apiClient.get(`/event-associations/${eventId}/all`) },

  // 反向关联：从其他模块查加工事件
  getByDevice(deviceCode, params) { return apiClient.get(`/event-associations/by-device/${deviceCode}`, { params }) },
  getByMaterial(startCode, params) { return apiClient.get(`/event-associations/by-material/${startCode}`, { params }) },
  getByOrder(docNo, params) { return apiClient.get(`/event-associations/by-order/${docNo}`, { params }) },
  getByProcess(processCode, params) { return apiClient.get(`/event-associations/by-process/${processCode}`, { params }) },
}

// 添加请求拦截器，自动添加认证令牌
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token && !config.url.startsWith('/auth/login')) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 添加响应拦截器，处理 401 错误
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // 清除令牌并跳转到登录页
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_info')
      
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient
