/**
 * 用户相关 API
 */

import request from './request'

/**
 * 用户注册
 */
export function register(data) {
  return request({
    url: '/users',
    method: 'post',
    data
  })
}

/**
 * 用户登录（昵称+密码）
 */
export function login(data) {
  return request({
    url: '/users/login',
    method: 'post',
    data
  })
}

/**
 * 邮箱验证码登录
 */
export function emailLogin(data) {
  return request({
    url: '/users/email-login',
    method: 'post',
    data
  })
}

/**
 * 发送邮箱验证码
 */
export function sendEmailCode(data) {
  return request({
    url: '/users/email-code',
    method: 'post',
    data
  })
}

/**
 * 获取用户信息
 */
export function getUserInfo(userId) {
  return request({
    url: `/users/${userId}`,
    method: 'get'
  })
}

/**
 * 更新用户信息
 */
export function updateUserInfo(userId, data) {
  return request({
    url: `/users/${userId}`,
    method: 'patch',
    data
  })
}

/**
 * 获取用户列表（分页）
 */
export function getUserList(params) {
  return request({
    url: '/users',
    method: 'get',
    params
  })
}

/**
 * 批量删除用户
 */
export function deleteUsers(userIds) {
  return request({
    url: `/users/${userIds.join(',')}`,
    method: 'delete'
  })
}

/**
 * 设置管理员
 */
export function setAdmin(data) {
  return request({
    url: '/users/set-admin',
    method: 'patch',
    data
  })
}

