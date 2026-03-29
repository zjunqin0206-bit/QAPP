/*
 * 文件说明：训练与预测服务接口文件，负责训练任务、结果查询、健康检查与预测请求。
 * 维护重点：该文件面向独立的深度学习服务，与 Iris CRUD 接口分开维护。
 */
import axios from 'axios'

// 实现思路：训练服务单独创建请求实例，避免和普通业务接口共享超时与路由前缀。
const trainHttp = axios.create({
  baseURL: import.meta.env.VITE_TRAIN_API_BASE_URL || '',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

trainHttp.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error?.response?.data?.message ||
      error?.response?.data?.msg ||
      error?.message ||
      '请求失败，请稍后重试'
    return Promise.reject(new Error(message))
  }
)

// 实现思路：通过健康检查接口快速确认训练服务是否可用。
export const getTrainHealth = () => trainHttp.get('/health')

// 实现思路：先获取后端提供的可选超参数，让前端配置页完全受服务端控制。
export const getTrainOptions = () => trainHttp.get('/api/v1/train/options')

// 实现思路：训练提交接口统一接收参数对象，返回 jobId 供轮询和结果页使用。
export const createTrainJob = (data) => trainHttp.post('/api/v1/train/jobs', data)

// 实现思路：轮询接口只关注任务进度，因此保持最小请求参数集。
export const getTrainJob = (jobId) => trainHttp.get(`/api/v1/train/jobs/${jobId}`)

// 实现思路：结果接口统一返回指标、图像地址与模型参数，供结果页集中展示。
export const getTrainResult = (jobId) => trainHttp.get(`/api/v1/train/jobs/${jobId}/result`)

// 实现思路：预测接口接收 jobId 与特征向量，支持选择指定模型进行推理。
export const predictIris = (data) => trainHttp.post('/api/v1/predict', data)
