/**
 * WebSocket 客户端服务
 * 功能：
 * 1. 实现与后端的 WebSocket 实时通信
 * 2. 自动重连机制
 * 3. 心跳检测
 * 4. 消息订阅/发布
 * 5. 连接状态管理
 */

class WebSocketClient {
  constructor(baseURL = null) {
    this.ws = null
    this.baseURL = baseURL || this.getWebSocketURL()
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
    this.heartbeatInterval = 30000 // 30 秒心跳
    this.heartbeatTimer = null
    this.messageHandlers = new Map()
    this.connectionState = 'disconnected' // disconnected, connecting, connected, reconnecting
    this.listeners = new Map()
    this.messageQueue = []
    this.clientId = this.generateClientId()
  }

  /**
   * 获取 WebSocket URL
   */
  getWebSocketURL() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    return `${protocol}//${window.location.host}/ws`
  }

  /**
   * 生成客户端 ID
   */
  generateClientId() {
    return `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  /**
   * 连接 WebSocket
   */
  connect() {
    if (this.ws && (this.ws.readyState === WebSocket.CONNECTING || this.ws.readyState === WebSocket.OPEN)) {
      console.log('[WebSocket] 已在连接中或已连接')
      return
    }

    this.connectionState = 'connecting'
    this.emit('connecting', { clientId: this.clientId })

    const wsURL = `${this.baseURL}?client_id=${this.clientId}`
    console.log(`[WebSocket] 正在连接：${wsURL}`)

    this.ws = new WebSocket(wsURL)

    this.ws.onopen = () => {
      console.log('[WebSocket] 连接成功')
      this.connectionState = 'connected'
      this.reconnectAttempts = 0
      this.emit('connected', { clientId: this.clientId })
      this.startHeartbeat()
      this.flushMessageQueue()
    }

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        console.log('[WebSocket] 收到消息:', message)
        this.handleMessage(message)
      } catch (error) {
        console.error('[WebSocket] 消息解析失败:', error)
      }
    }

    this.ws.onclose = (event) => {
      console.log(`[WebSocket] 连接关闭：code=${event.code}, reason=${event.reason}`)
      this.connectionState = 'disconnected'
      this.emit('disconnected', { code: event.code, reason: event.reason })
      this.stopHeartbeat()
      this.attemptReconnect()
    }

    this.ws.onerror = (error) => {
      console.error('[WebSocket] 连接错误:', error)
      this.emit('error', { error })
    }
  }

  /**
   * 处理收到的消息
   */
  handleMessage(message) {
    const { type, action, topic } = message

    // 触发全局监听器
    this.emit('message', message)

    // 触发特定类型的监听器
    if (type) {
      this.emit(`type:${type}`, message)
    }

    // 触发特定 topic 的监听器
    if (topic) {
      this.emit(`topic:${topic}`, message)
    }

    // 处理特定动作
    if (action === 'pong') {
      this.lastPongTime = Date.now()
    }
  }

  /**
   * 发送消息
   */
  send(message) {
    const messageStr = JSON.stringify(message)

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(messageStr)
    } else {
      console.warn('[WebSocket] 连接未打开，消息已加入队列')
      this.messageQueue.push(messageStr)
    }
  }

  /**
   * 刷新消息队列
   */
  flushMessageQueue() {
    while (this.messageQueue.length > 0 && this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = this.messageQueue.shift()
      this.ws.send(message)
    }
  }

  /**
   * 订阅 topic
   */
  subscribe(topics) {
    const topicList = Array.isArray(topics) ? topics : [topics]
    console.log('[WebSocket] 订阅 topics:', topicList)

    this.send({
      type: 'subscribe',
      topics: topicList
    })

    // 记录订阅
    topicList.forEach(topic => {
      if (!this.subscribedTopics) {
        this.subscribedTopics = new Set()
      }
      this.subscribedTopics.add(topic)
    })
  }

  /**
   * 取消订阅 topic
   */
  unsubscribe(topics) {
    const topicList = Array.isArray(topics) ? topics : [topics]
    console.log('[WebSocket] 取消订阅 topics:', topicList)

    this.send({
      type: 'unsubscribe',
      topics: topicList
    })

    // 移除订阅记录
    if (this.subscribedTopics) {
      topicList.forEach(topic => {
        this.subscribedTopics.delete(topic)
      })
    }
  }

  /**
   * 发送心跳
   */
  startHeartbeat() {
    this.stopHeartbeat()

    this.heartbeatTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        const now = Date.now()
        if (!this.lastPongTime || (now - this.lastPongTime) > this.heartbeatInterval * 2) {
          console.warn('[WebSocket] 心跳超时，可能连接已断开')
        }

        this.send({
          type: 'ping'
        })
      }
    }, this.heartbeatInterval)

    console.log('[WebSocket] 心跳已启动')
  }

  /**
   * 停止心跳
   */
  stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
      console.log('[WebSocket] 心跳已停止')
    }
  }

  /**
   * 尝试重连
   */
  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WebSocket] 重连次数已达上限，停止重连')
      this.emit('reconnect_failed', { attempts: this.reconnectAttempts })
      return
    }

    this.reconnectAttempts++
    this.connectionState = 'reconnecting'

    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1) // 指数退避
    console.log(`[WebSocket] ${delay}ms 后尝试第 ${this.reconnectAttempts} 次重连...`)

    this.emit('reconnecting', {
      attempt: this.reconnectAttempts,
      delay: delay
    })

    setTimeout(() => {
      this.connect()
    }, delay)
  }

  /**
   * 断开连接
   */
  disconnect() {
    console.log('[WebSocket] 主动断开连接')
    this.stopHeartbeat()
    this.reconnectAttempts = this.maxReconnectAttempts // 阻止自动重连

    if (this.ws) {
      this.ws.close(1000, 'Client disconnect')
      this.ws = null
    }

    this.connectionState = 'disconnected'
    this.emit('disconnected', { reason: 'client_initiated' })
  }

  /**
   * 注册事件监听器
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event).add(callback)

    // 返回取消订阅函数
    return () => {
      this.off(event, callback)
    }
  }

  /**
   * 移除事件监听器
   */
  off(event, callback) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).delete(callback)
    }
  }

  /**
   * 触发事件
   */
  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`[WebSocket] 触发事件 ${event} 失败:`, error)
        }
      })
    }
  }

  /**
   * 获取连接状态
   */
  getState() {
    return {
      state: this.connectionState,
      clientId: this.clientId,
      reconnectAttempts: this.reconnectAttempts,
      subscribedTopics: this.subscribedTopics ? Array.from(this.subscribedTopics) : [],
      queueLength: this.messageQueue.length
    }
  }

  /**
   * 查询服务状态
   */
  queryStatus(queryType) {
    this.send({
      type: 'query',
      query_type: queryType
    })
  }
}

// 创建全局单例
const websocketClient = new WebSocketClient()

export default websocketClient
