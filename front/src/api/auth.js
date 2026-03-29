/*
 * 文件说明：认证相关接口文件，集中提供登录、注册、退出登录和修改密码能力。
 * 维护重点：页面只关心调用方法，不直接拼接认证接口路径。
 */
import http from './http'

// 实现思路：直接透传注册表单数据，让页面只关心提交时机而不关心接口路径细节。
export const register = (data) => http.post('/api/auth/register', data)

// 实现思路：统一封装登录请求，复用基础 http 的 cookie 与错误处理能力。
export const login = (data) => http.post('/api/auth/login', data)

// 实现思路：退出接口不需要额外参数，只负责通知服务端清理当前会话。
export const logout = () => http.post('/api/auth/logout')

// 实现思路：把密码修改请求独立成方法，便于弹窗组件直接调用。
export const changePassword = (data) => http.post('/api/auth/change-password', data)
