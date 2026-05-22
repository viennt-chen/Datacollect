import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api/data-collector',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

const mqttTopicApiClient = axios.create({
  baseURL: '/api/mqtt-topic-configs',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * 获取采集器状态统计
 */
export const getCollectorStats = () => {
  return apiClient.get('/stats')
}

/**
 * 启动采集器
 */
export const startCollectorService = () => {
  return apiClient.post('/control', { action: 'start' })
}

/**
 * 停止采集器
 */
export const stopCollectorService = () => {
  return apiClient.post('/control', { action: 'stop' })
}

/**
 * 获取 Topic 分布统计
 */
export const getTopicDistribution = (params) => {
  return apiClient.get('/raw-data/stats', { params })
}

/**
 * 获取最近加工事件
 */
export const getRecentProcessingEvents = (params) => {
  return apiClient.get('/recent-events', { params })
}

/**
 * 获取采集器配置
 */
export const getCollectorConfig = () => {
  return apiClient.get('/config')
}

/**
 * 获取加工事件统计
 */
export const getProcessingEventStats = (params) => {
  return apiClient.get('/events/stats', { params })
}

/**
 * 获取原始数据统计
 */
export const getRawDataStats = (params) => {
  return apiClient.get('/raw-data/stats', { params })
}

/**
 * 获取 Topic 配置列表
 */
export const getTopicConfigs = (params) => {
  return mqttTopicApiClient.get('/', { params })
}

/**
 * 创建 Topic 配置
 */
export const createTopicConfig = (data) => {
  return mqttTopicApiClient.post('/', data)
}

/**
 * 更新 Topic 配置
 */
export const updateTopicConfig = (id, data) => {
  return mqttTopicApiClient.put(`/${id}`, data)
}

/**
 * 删除 Topic 配置
 */
export const deleteTopicConfig = (id) => {
  return mqttTopicApiClient.delete(`/${id}`)
}

export default {
  getCollectorStats,
  startCollectorService,
  stopCollectorService,
  getTopicDistribution,
  getRecentProcessingEvents,
  getCollectorConfig,
  getProcessingEventStats,
  getRawDataStats,
  getTopicConfigs,
  createTopicConfig,
  updateTopicConfig,
  deleteTopicConfig
}
