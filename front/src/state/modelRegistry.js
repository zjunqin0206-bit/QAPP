/*
 * 文件说明：模型权重登记文件，负责在浏览器本地保存已命名的训练结果与 jobId 映射。
 * 维护重点：这里存的是前端可选模型列表，不是真实权重文件本体。
 */
import { reactive } from 'vue'

const STORAGE_KEY = 'qapp-saved-models'

// 实现思路：页面初始化时从 localStorage 读出已保存的模型列表，作为预测页候选数据源。
const loadModels = () => {
  try {
    const parsed = JSON.parse(window.localStorage.getItem(STORAGE_KEY) || '[]')
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

// 实现思路：所有模型列表修改最终都落到 localStorage，保证刷新后仍可选择。
const persist = (models) => {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(models))
}

export const modelRegistryState = reactive({
  models: loadModels()
})

// 实现思路：以 jobId 为主键更新或新增模型记录，保证同一训练任务不会重复保存多份。
export const saveModelRecord = (record = {}) => {
  const item = {
    jobId: record.jobId,
    name: record.name?.trim() || record.jobId,
    params: record.params || {},
    createdAt: record.createdAt || new Date().toISOString()
  }
  const index = modelRegistryState.models.findIndex((model) => model.jobId === item.jobId)
  if (index >= 0) modelRegistryState.models.splice(index, 1, item)
  else modelRegistryState.models.unshift(item)
  persist(modelRegistryState.models)
}

// 实现思路：通过 jobId 快速回查已保存模型，用于结果页回显和预测页选择。
export const getSavedModelByJobId = (jobId) => modelRegistryState.models.find((item) => item.jobId === jobId) || null
