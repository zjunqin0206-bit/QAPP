/*
 * 文件说明：登录态存储文件，负责把当前用户信息同步到 sessionStorage 与响应式状态。
 * 维护重点：这里只管理会话身份，不承载其它业务状态。
 */
import { reactive } from 'vue'

const STORAGE_KEY = 'qapp-session'

// 实现思路：初始化时优先从 sessionStorage 恢复登录态，保证刷新页面后还能保持会话信息。
const stored = (() => {
  try {
    return JSON.parse(window.sessionStorage.getItem(STORAGE_KEY) || '{}')
  } catch {
    return {}
  }
})()

export const sessionState = reactive({
  isAuthenticated: Boolean(stored.username),
  user: {
    id: stored.id ?? null,
    username: stored.username ?? ''
  }
})

// 实现思路：登录成功后同步更新响应式状态与浏览器存储，确保页面与路由守卫立即生效。
export const setSessionUser = (user = {}) => {
  sessionState.isAuthenticated = Boolean(user?.username)
  sessionState.user.id = user?.id ?? null
  sessionState.user.username = user?.username ?? ''
  window.sessionStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      id: sessionState.user.id,
      username: sessionState.user.username
    })
  )
}

// 实现思路：退出登录时同时清空内存状态和 sessionStorage，避免残留身份信息。
export const clearSessionUser = () => {
  sessionState.isAuthenticated = false
  sessionState.user.id = null
  sessionState.user.username = ''
  window.sessionStorage.removeItem(STORAGE_KEY)
}
