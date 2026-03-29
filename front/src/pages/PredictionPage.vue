<!--
  文件说明：预测页，负责选择已保存权重、输入单样本特征并展示预测结果。
  维护重点：预测依赖模型库状态，页面只做选择和结果展示。
-->
<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { predictIris } from '../api/train'
import { modelRegistryState } from '../state/modelRegistry'

const featureForm = reactive({
  modelJobId: modelRegistryState.models[0]?.jobId || '',
  sepalLength: '5.1',
  sepalWidth: '3.5',
  petalLength: '1.4',
  petalWidth: '0.2'
})
const loading = ref(false)
const errorMessage = ref('')
const predictionResult = ref(null)

const savedModels = computed(() => modelRegistryState.models)
const selectedModel = computed(() => savedModels.value.find((item) => item.jobId === featureForm.modelJobId) || null)
const featureValues = computed(() => [
  Number(featureForm.sepalLength),
  Number(featureForm.sepalWidth),
  Number(featureForm.petalLength),
  Number(featureForm.petalWidth)
])
const canSubmit = computed(() => featureValues.value.every((item) => Number.isFinite(item) && item > 0))

// 实现思路：当本地模型库发生变化时，自动为预测表单补上默认可选模型。
watch(
  () => savedModels.value.length,
  () => {
    if (!featureForm.modelJobId && savedModels.value[0]) {
      featureForm.modelJobId = savedModels.value[0].jobId
    }
  }
)

// 实现思路：将当前选择的模型 jobId 与四维特征组合成请求体，直接向预测服务发起推理。
const submitPrediction = async () => {
  if (!canSubmit.value) return
  loading.value = true
  errorMessage.value = ''
  try {
    const payload = {
      features: featureValues.value
    }
    if (featureForm.modelJobId) payload.job_id = featureForm.modelJobId
    const { data } = await predictIris(payload)
    predictionResult.value = data
  } catch (error) {
    errorMessage.value = error.message || '预测失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="module-stack">
    <div class="prediction-grid">
      <div class="glass-card training-panel">
        <div class="module-section-head">
          <div>
            <p class="profile-modal-label">单样本预测</p>
            <h2>选择权重并输入特征</h2>
          </div>
        </div>

        <div v-if="errorMessage" class="inline-alert error">{{ errorMessage }}</div>

        <label class="wide-field">
          已保存权重
          <div class="select-shell">
            <select v-model="featureForm.modelJobId" class="soft-select">
              <option value="">最近一次成功模型</option>
              <option v-for="item in savedModels" :key="item.jobId" :value="item.jobId">
                {{ item.name }} · {{ item.jobId }}
              </option>
            </select>
          </div>
        </label>

        <div v-if="selectedModel" class="saved-model-card prediction-model-card">
          <span>当前权重</span>
          <strong>{{ selectedModel.name }}</strong>
          <small>{{ selectedModel.jobId }}</small>
        </div>

        <div class="training-form-grid prediction-form-grid">
          <label>
            花萼长度
            <input v-model="featureForm.sepalLength" type="number" step="0.1" />
          </label>
          <label>
            花萼宽度
            <input v-model="featureForm.sepalWidth" type="number" step="0.1" />
          </label>
          <label>
            花瓣长度
            <input v-model="featureForm.petalLength" type="number" step="0.1" />
          </label>
          <label>
            花瓣宽度
            <input v-model="featureForm.petalWidth" type="number" step="0.1" />
          </label>
        </div>

        <div class="panel-actions-row">
          <span class="helper-note">若未选择已保存权重，则使用最近一次训练成功的模型</span>
          <button class="primary-btn" :disabled="!canSubmit || loading" @click="submitPrediction">
            {{ loading ? '预测中...' : '开始预测' }}
          </button>
        </div>
      </div>

      <div class="glass-card training-panel status-panel">
        <div class="module-section-head compact-head">
          <div>
            <p class="profile-modal-label">预测结果</p>
            <h2>{{ predictionResult?.pred_class || '等待预测' }}</h2>
          </div>
        </div>

        <div v-if="predictionResult" class="prediction-result-stack">
          <div class="metrics-grid prediction-summary-grid">
            <div class="metric-card highlight-card">
              <span>类别索引</span>
              <strong>{{ predictionResult.pred_index }}</strong>
            </div>
            <div class="metric-card highlight-card">
              <span>使用优化器</span>
              <strong>{{ predictionResult.selected_params?.optimizer || '-' }}</strong>
            </div>
          </div>

          <div class="probability-stack probability-card-stack">
            <div v-for="(item, index) in predictionResult.probabilities || []" :key="index" class="probability-row probability-row-card">
              <span>类别 {{ index }}</span>
              <div class="class-bar-track probability-track">
                <i :style="{ width: `${Math.round(Number(item || 0) * 100)}%` }"></i>
              </div>
              <strong>{{ Math.round(Number(item || 0) * 100) }}%</strong>
            </div>
          </div>

          <div class="param-summary-grid compact-param-grid">
            <div v-for="(value, key) in predictionResult.selected_params || {}" :key="key" class="param-chip">
              <span>{{ key }}</span>
              <strong>{{ value }}</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
