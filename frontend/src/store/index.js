/**
 * 统一状态管理 Store
 * 功能：
 * 1. 全局状态管理
 * 2. WebSocket 状态同步
 * 3. 服务状态管理
 * 4. 错误状态管理
 * 5. 加载状态管理
 */

import { reactive, readonly } from 'vue'
import websocketClient from '@/utils/websocket'

// ==================== 状态定义 ====================
const state = reactive({
  // WebSocket 连接状态
  websocket: {
    connected: false,
    connecting: false,
    reconnecting: false,
    clientId: null,
    subscribedTopics: [],
    lastMessageTime: null
  },

  // MQTT 服务状态
  mqttService: {
    running: false,
    connected: false,
    messageCount: 0,
    errorCount: 0,
    lastMessageTime: null,
    messagesPerSecond: 0,
    avgProcessingTimeMs: 0
  },

  // 订单查询服务状态
  orderService: {
    running: false,
    lastRun: null,
    nextRun: null,
    totalProducts: 0,
    successfulQueries: 0,
    failedQueries: 0,
    totalSaved: 0
  },

  // 全局加载状态
  loading: {
    global: false,
    mqtt: false,
    orders: false,
    products: false,
    events: false
  },

  // 错误状态
  errors: {
    global: null,
    mqtt: null,
    orders: null,
    products: null,
    events: null
  },

  // 预警信息
  alerts: [],

  // 通知消息
  notifications: []
})

// ==================== Getter 函数 ====================
const getters = {
  // WebSocket 状态
  isWebSocketConnected: () => state.websocket.connected,
  isWebSocketConnecting: () => state.websocket.connecting,
  isWebSocketReconnecting: () => state.websocket.reconnecting,

  // MQTT 状态
  isMQTTConnected: () => state.mqttService.connected,
  isMQTTRunning: () => state.mqttService.running,
  mqttMessageCount: () => state.mqttService.messageCount,
  mqttErrorCount: () => state.mqttService.errorCount,

  // 订单服务状态
  isOrderServiceRunning: () => state.orderService.running,
  orderServiceNextRun: () => state.orderService.nextRun,

  // 加载状态
  isLoading: () => state.loading.global,
  isLoadingMQTT: () => state.loading.mqtt,
  isLoadingOrders: () => state.loading.orders,

  // 错误状态
  hasError: () => state.errors.global !== null,
  getLastError: () => state.errors.global,

  // 预警数量
  alertCount: () => state.alerts.length,
  notificationCount: () => state.notifications.length
}

// ==================== Action 函数 ====================
const actions = {
  // 初始化 WebSocket
  initWebSocket() {
    console.log('[Store] 初始化 WebSocket...')

    // 连接成功
    websocketClient.on('connected', (data) => {
      console.log('[Store] WebSocket 连接成功:', data)
      state.websocket.connected = true
      state.websocket.connecting = false
      state.websocket.reconnecting = false
      state.websocket.clientId = data.clientId
      state.websocket.lastMessageTime = new Date().toISOString()

      // 自动订阅默认 topics
      this.subscribeTopics(['mqtt_data', 'service_status', 'alert'])
    })

    // 连接中
    websocketClient.on('connecting', () => {
      console.log('[Store] WebSocket 连接中...')
      state.websocket.connecting = true
    })

    // 连接断开
    websocketClient.on('disconnected', (data) => {
      console.log('[Store] WebSocket 断开:', data)
      state.websocket.connected = false
      state.websocket.connecting = false
    })

    // 重连中
    websocketClient.on('reconnecting', (data) => {
      console.log('[Store] WebSocket 重连中:', data)
      state.websocket.reconnecting = true
      this.addNotification(
        'warning',
        `WebSocket 重连中 (${data.attempt}/${websocketClient.maxReconnectAttempts})`,
        data.delay
      )
    })

    // 重连失败
    websocketClient.on('reconnect_failed', (data) => {
      console.error('[Store] WebSocket 重连失败:', data)
      state.websocket.reconnecting = false
      this.addError('websocket', 'WebSocket 重连失败，请刷新页面')
    })

    // 收到消息
    websocketClient.on('message', (message) => {
      state.websocket.lastMessageTime = new Date().toISOString()
      this.handleWebSocketMessage(message)
    })

    // 错误
    websocketClient.on('error', (data) => {
      console.error('[Store] WebSocket 错误:', data)
      this.addError('websocket', data.error?.message || 'WebSocket 错误')
    })

    // 连接
    websocketClient.connect()
  },

  // 处理 WebSocket 消息
  handleWebSocketMessage(message) {
    const { type, action, data } = message

    switch (type) {
      case 'mqtt_data':
        // MQTT 数据推送
        console.log('[Store] 收到 MQTT 数据:', data)
        // 可以在这里触发特定的事件或更新状态
        break

      case 'service_status':
        // 服务状态更新
        console.log('[Store] 服务状态更新:', data)
        this.updateServiceStatus(data.service_type, data.data)
        break

      case 'alert':
        // 预警通知
        console.warn('[Store] 收到预警:', data)
        this.addAlert(data.alert_type, data.message, data.level)
        break

      case 'query_result':
        // 查询结果
        console.log('[Store] 查询结果:', data)
        // 处理查询结果
        break

      default:
        console.log('[Store] 未知消息类型:', type)
    }
  },

  // 更新服务状态
  updateServiceStatus(serviceType, statusData) {
    switch (serviceType) {
      case 'mqtt':
        state.mqttService = { ...state.mqttService, ...statusData }
        break
      case 'order':
        state.orderService = { ...state.orderService, ...statusData }
        break
    }
  },

  // 订阅 topics
  subscribeTopics(topics) {
    console.log('[Store] 订阅 topics:', topics)
    websocketClient.subscribe(topics)
    state.websocket.subscribedTopics = topics
  },

  // 取消订阅 topics
  unsubscribeTopics(topics) {
    console.log('[Store] 取消订阅 topics:', topics)
    websocketClient.unsubscribe(topics)
    state.websocket.subscribedTopics = state.websocket.subscribedTopics.filter(
      t => !topics.includes(t)
    )
  },

  // 设置加载状态
  setLoading(key, value) {
    if (key in state.loading) {
      state.loading[key] = value
    }
  },

  // 添加错误
  addError(key, message) {
    if (key in state.errors) {
      state.errors[key] = {
        message,
        timestamp: new Date().toISOString()
      }
    }
  },

  // 清除错误
  clearError(key) {
    if (key in state.errors) {
      state.errors[key] = null
    }
  },

  // 添加预警
  addAlert(type, message, level = 'warning') {
    const alert = {
      id: Date.now(),
      type,
      message,
      level,
      timestamp: new Date().toISOString()
    }

    state.alerts.unshift(alert)

    // 限制预警数量
    if (state.alerts.length > 50) {
      state.alerts = state.alerts.slice(0, 50)
    }

    console.log('[Store] 添加预警:', alert)
  },

  // 清除预警
  clearAlert(alertId) {
    const index = state.alerts.findIndex(a => a.id === alertId)
    if (index !== -1) {
      state.alerts.splice(index, 1)
    }
  },

  // 清除所有预警
  clearAllAlerts() {
    state.alerts = []
  },

  // 添加通知
  addNotification(type, message, duration = 5000) {
    const notification = {
      id: Date.now(),
      type,
      message,
      duration,
      timestamp: new Date().toISOString()
    }

    state.notifications.unshift(notification)

    // 自动移除
    if (duration > 0) {
      setTimeout(() => {
        this.removeNotification(notification.id)
      }, duration)
    }
  },

  // 移除通知
  removeNotification(notificationId) {
    const index = state.notifications.findIndex(n => n.id === notificationId)
    if (index !== -1) {
      state.notifications.splice(index, 1)
    }
  },

  // 查询 MQTT 状态
  queryMQTTStatus() {
    websocketClient.queryStatus('mqtt_stats')
  },

  // 查询连接状态
  queryConnectionStatus() {
    websocketClient.queryStatus('connection_stats')
  }
}

// ==================== 导出 Store ====================
export const useStore = () => {
  return {
    state: readonly(state),
    getters: readonly(getters),
    actions: readonly(actions)
  }
}

export default useStore
