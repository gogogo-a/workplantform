/**
 * 消息相关 API
 */

import request from './request'

/**
 * 获取会话的消息列表
 */
export function getMessageList(sessionId, params) {
  return request({
    url: `/messages/${sessionId}`,
    method: 'get',
    params
  })
}

/**
 * 发送消息（流式）
 * 使用 Server-Sent Events (SSE)
 * @param {Object|FormData} data - 消息数据或 FormData
 * @param {Boolean} isFormData - 是否为 FormData
 */
export function sendMessageStream(data, isFormData = false) {
  const token = localStorage.getItem('token')
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  
  const headers = {
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  }
  
  // 如果不是 FormData，则添加 Content-Type
  if (!isFormData) {
    headers['Content-Type'] = 'application/json'
  }
  
  // SSE 不使用 axios，使用原生 fetch
  return fetch(`${baseURL}/messages`, {
    method: 'POST',
    headers: headers,
    body: isFormData ? data : JSON.stringify(data)
  })
}

/**
 * 发送消息（非流式，备用）
 */
export function sendMessage(data) {
  return request({
    url: '/messages',
    method: 'post',
    data
  })
}

