/*
 * 文件说明：Iris 数据管理接口文件，负责列表、详情、新增、编辑、删除与条件筛选请求。
 * 维护重点：保持字段命名与后端接口一致，减少页面层的请求拼装。
 */
import http from './http'

// 实现思路：列表查询单独封装，页面刷新和重置筛选都复用这一入口。
export const getIrisList = () => http.get('/api/iris/list')

// 实现思路：详情查询用于编辑回填，参数只保留主键 id。
export const getIrisById = (id) => http.get(`/api/iris/get/${id}`)

// 实现思路：新增接口透传标准表单对象，保持页面和后端字段一致。
export const addIris = (data) => http.post('/api/iris/add', data)

// 实现思路：更新时同时携带目标 id 和最新表单内容，保持编辑逻辑清晰。
export const updateIris = (id, data) => http.put(`/api/iris/update/${id}`, data)

// 实现思路：删除接口只接受主键，页面先确认后再执行。
export const deleteIris = (id) => http.delete(`/api/iris/delete/${id}`)

// 实现思路：条件筛选单独走 POST，请求体承载区间与品种等复合条件。
export const filterIris = (data) => http.post('/api/iris/filter', data)
