import request from './request'

/**
 * 获取错误日志
 * @param {string} date - 日期（格式：YYYY-MM-DD）
 * @param {number} limit - 每页数量
 * @param {number} offset - 偏移量
 */
export function getErrorLogs(date = null, limit = 100, offset = 0) {
  return request({
    url: '/logs/errors',
    method: 'get',
    params: { date, limit, offset }
  })
}

/**
 * 获取可用的日志日期
 */
export function getAvailableLogDates() {
  return request({
    url: '/logs/dates',
    method: 'get'
  })
}

/**
 * 获取错误日志统计信息
 */
export function getErrorStatistics() {
  return request({
    url: '/logs/statistics',
    method: 'get'
  })
}

