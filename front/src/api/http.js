/*
 * 文件说明：Iris 业务接口的基础请求封装文件，统一处理 baseURL、超时、cookie 与错误拦截。
 * 维护重点：所有依赖 code/msg/data 结构的接口都从这里透出，避免页面重复处理响应格式。
 */
import axios from 'axios'

// 创建 axios 实例，统一配置后端基地址和超时时间
// 实现思路：集中创建一个面向业务后端的 axios 实例，统一注入基础网络配置。
const http = axios.create({
  // 默认通过 Vite 代理转发到后端，避免浏览器直连 localhost 指向用户本机
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 10000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 响应拦截：统一处理后端 code/msg/data 结构与网络异常
http.interceptors.response.use(
  (response) => {
    const payload = response?.data
    if (payload && typeof payload === 'object' && 'code' in payload && payload.code !== 200) {
      return Promise.reject(new Error(payload.msg || '请求失败，请稍后重试'))
    }
    return response
  },
  (error) => {
    const message =
      error?.response?.data?.message ||
      error?.response?.data?.msg ||
      error?.message ||
      '请求失败，请稍后重试'
    return Promise.reject(new Error(message))
  }
)

export default http
