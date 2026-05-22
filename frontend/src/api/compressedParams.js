/**
 * 压缩工艺参数追溯 API
 */
import request from '@/utils/request'

// 查询压缩工艺参数列表
export function listCompressedParams(params) {
  return request({
    url: '/compressed-params/compressed',
    method: 'get',
    params
  })
}

// 获取压缩工艺参数详情
export function getCompressedParamDetail(id) {
  return request({
    url: `/compressed-params/compressed/${id}`,
    method: 'get'
  })
}

// 获取压缩工艺参数统计信息
export function getCompressedParamsStats(params) {
  return request({
    url: '/compressed-params/compressed/stats',
    method: 'get',
    params
  })
}

// 获取所有 Topic 列表
export function listTopics() {
  return request({
    url: '/compressed-params/compressed/topic/PV/list',
    method: 'get'
  })
}

// 根据事件 UID 获取所有关联的压缩参数
export function getEventParams(eventUid) {
  return request({
    url: `/compressed-params/compressed/event/${eventUid}`,
    method: 'get'
  })
}
