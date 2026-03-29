<!--
  文件说明：训练任务配置页，负责选择超参数、提交训练任务并轮询训练进度。
  维护重点：该页只负责训练入口和进度反馈，训练结果展示已经拆分到独立结果页。
-->
<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { createTrainJob, getTrainHealth, getTrainJob, getTrainOptions } from '../api/train'

const FIELD_ORDER = ['hidden_dim', 'epochs', 'batch_size', 'learning_rate', 'optimizer', 'activation']
const FIELD_LABELS = {
  hidden_dim: '隐藏层维度',
  epochs: '训练轮数',
  batch_size: '批大小',
  learning_rate: '学习率',
  optimizer: '优化器',
  activation: '激活函数'
}

const router = useRouter()
const healthStatus = ref('checking')
const loadingOptions = ref(false)
const submitting = ref(false)
const polling = ref(false)
const currentJobId = ref('')
const latestError = ref('')
const jobState = reactive({
  status: 'idle',
  progress: 0,
  current_epoch: 0,
  total_epochs: 0,
  error: null
})
const optionState = reactive({
  defaults: {},
  options: {},
  fixed_params: {}
})
const formState = reactive({
  hidden_dim: '',
  epochs: '',
  batch_size: '',
  learning_rate: '',
  optimizer: '',
  activation: ''
})
let pollTimer = null

const progressPercent = computed(() => Math.max(0, Math.min(100, Math.round((jobState.progress || 0) * 100))))
const canSubmit = computed(() => FIELD_ORDER.every((key) => formState[key] !== ''))
const statusLabel = computed(() => {
  const map = {
    idle: '尚未开始',
    queued: '排队中',
    running: '训练中',
    succeeded: '训练完成',
    failed: '训练失败'
  }
  return map[jobState.status] || jobState.status
})
const selectedSummary = computed(() =>
  FIELD_ORDER.map((key) => ({ label: FIELD_LABELS[key], value: formState[key] || optionState.defaults[key] || '-' }))
)

// 实现思路：统一收口轮询定时器的关闭逻辑，避免页面离开后继续请求。
const stopPolling = () => {
  if (pollTimer) {
    window.clearInterval(pollTimer)
    pollTimer = null
  }
  polling.value = false
}

// 实现思路：把后端默认超参数批量回填到表单，保证初始配置始终与服务端一致。
const hydrateForm = (defaults = {}) => {
  FIELD_ORDER.forEach((key) => {
    formState[key] = defaults[key] ?? ''
  })
}

// 实现思路：先做训练服务健康检查，为页面头部提供即时可用状态。
const loadHealth = async () => {
  try {
    const { data } = await getTrainHealth()
    healthStatus.value = data?.status === 'ok' ? 'online' : 'offline'
  } catch {
    healthStatus.value = 'offline'
  }
}

// 实现思路：进入页面时从后端拉取可选超参数与默认值，避免前端写死配置。
const loadOptions = async () => {
  loadingOptions.value = true
  latestError.value = ''
  try {
    const { data } = await getTrainOptions()
    optionState.defaults = data?.defaults || {}
    optionState.options = data?.options || {}
    optionState.fixed_params = data?.fixed_params || {}
    hydrateForm(optionState.defaults)
  } catch (error) {
    latestError.value = error.message || '获取训练参数失败'
  } finally {
    loadingOptions.value = false
  }
}

// 实现思路：把轮询返回的进度信息统一映射到页面响应式状态中。
const syncJobState = (payload = {}) => {
  jobState.status = payload.status || 'idle'
  jobState.progress = payload.progress || 0
  jobState.current_epoch = payload.current_epoch || 0
  jobState.total_epochs = payload.total_epochs || 0
  jobState.error = payload.error || null
}

// 实现思路：轮询训练任务状态，成功后直接跳转到独立结果页，失败则停留当前页提示错误。
const pollJob = async (jobId) => {
  try {
    const { data } = await getTrainJob(jobId)
    syncJobState(data)
    if (data?.status === 'succeeded') {
      stopPolling()
      router.push({ name: 'model-training-result', params: { jobId } })
      return
    }
    if (data?.status === 'failed') {
      stopPolling()
      latestError.value = data?.error || '训练失败'
    }
  } catch (error) {
    stopPolling()
    latestError.value = error.message || '获取训练进度失败'
  }
}

// 实现思路：启动轮询前先清理旧定时器，保证任一时刻只追踪一个任务。
const startPolling = (jobId) => {
  stopPolling()
  polling.value = true
  pollTimer = window.setInterval(() => {
    pollJob(jobId)
  }, 1500)
}

// 实现思路：把当前表单值转换为训练参数后提交任务，并立即进入进度轮询。
const startTraining = async () => {
  if (!canSubmit.value) return
  submitting.value = true
  latestError.value = ''
  try {
    const params = FIELD_ORDER.reduce((acc, key) => {
      const raw = formState[key]
      acc[key] = ['optimizer', 'activation'].includes(key) ? raw : Number(raw)
      return acc
    }, {})
    const { data } = await createTrainJob({ params })
    currentJobId.value = data?.job_id || ''
    syncJobState(data)
    if (currentJobId.value) {
      startPolling(currentJobId.value)
      await pollJob(currentJobId.value)
    }
  } catch (error) {
    latestError.value = error.message || '提交训练任务失败'
  } finally {
    submitting.value = false
  }
}

// 实现思路：页面首次进入时并行加载服务健康状态与超参数配置。
onMounted(async () => {
  await Promise.all([loadHealth(), loadOptions()])
})

// 实现思路：组件卸载时兜底停止轮询，防止后台继续发请求。
onBeforeUnmount(() => {
  stopPolling()
})
</script>

<template>
  <section class="module-stack">
    <div class="training-page-stack">
      <div class="glass-card training-panel">
        <div class="module-section-head">
          <div>
            <p class="profile-modal-label">模型训练</p>
            <h2>超参数配置</h2>
          </div>
          <span class="status-pill" :class="healthStatus">{{ healthStatus === 'online' ? '服务在线' : healthStatus === 'offline' ? '服务离线' : '检查中' }}</span>
        </div>

        <div v-if="latestError" class="inline-alert error">{{ latestError }}</div>

        <div class="parameter-grid">
          <label v-for="field in FIELD_ORDER" :key="field" class="parameter-card">
            <span class="field-caption">{{ FIELD_LABELS[field] }}</span>
            <div class="select-shell">
              <select v-model="formState[field]" :disabled="loadingOptions" class="soft-select">
                <option v-for="option in optionState.options[field] || []" :key="String(option)" :value="option">
                  {{ option }}
                </option>
              </select>
            </div>
          </label>
        </div>

        <div class="panel-actions-row">
          <button class="ghost-btn" @click="loadOptions">恢复默认</button>
          <button class="primary-btn" :disabled="!canSubmit || submitting" @click="startTraining">
            {{ submitting || polling ? '训练中...' : '开始训练' }}
          </button>
        </div>
      </div>

      <div class="glass-card training-panel status-panel progress-only-panel">
        <div class="module-section-head compact-head">
          <div>
            <p class="profile-modal-label">训练进度</p>
            <h2>{{ statusLabel }}</h2>
          </div>
          <span class="job-id-chip">{{ currentJobId || '未创建任务' }}</span>
        </div>

        <div class="progress-shell large-progress-shell">
          <div class="progress-bar progress-bar-lg"><span :style="{ width: `${progressPercent}%` }"></span></div>
          <div class="progress-meta">
            <span>进度 {{ progressPercent }}%</span>
            <span>{{ jobState.current_epoch }}/{{ jobState.total_epochs || optionState.defaults.epochs || '-' }} epoch</span>
          </div>
        </div>

        <div class="progress-status-card">
          <span>当前任务</span>
          <strong>{{ currentJobId || '等待创建任务' }}</strong>
          <small>训练完成后会自动跳转到结果页。</small>
        </div>
      </div>
    </div>
  </section>
</template>
