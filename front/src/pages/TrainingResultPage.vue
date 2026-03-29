<!--
  文件说明：训练结果页，负责加载指定任务的指标、图像结果，并支持为权重命名保存。
  维护重点：结果页只消费训练结果，不承担训练过程控制。
-->
<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getTrainResult } from '../api/train'
import { getSavedModelByJobId, saveModelRecord } from '../state/modelRegistry'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const errorMessage = ref('')
const resultState = ref(null)
const saveForm = reactive({ name: '' })
const saveMessage = ref('')

const formatPercent = (value) => `${Math.round(Number(value || 0) * 100)}%`
const formatDecimal = (value) => Number(value || 0).toFixed(4)
const formatMetricValue = (value) => Number(value || 0).toFixed(3)
// 实现思路：兼容相对路径与绝对路径的图像地址，让结果页直接消费后端返回的图片链接。
const normalizePlotUrl = (url) => {
  if (!url) return ''
  if (/^https?:\/\//.test(url)) return url
  return url
}

const jobId = computed(() => String(route.params.jobId || ''))
const savedRecord = computed(() => getSavedModelByJobId(jobId.value))
const overviewCards = computed(() => {
  const metrics = resultState.value?.metrics
  if (!metrics) return []
  return [
    { label: 'Accuracy', value: formatPercent(metrics.test_accuracy) },
    { label: 'Precision', value: formatMetricValue(metrics.macro_precision) },
    { label: 'Recall', value: formatMetricValue(metrics.macro_recall) },
    { label: 'F1 Score', value: formatMetricValue(metrics.macro_f1) },
    { label: 'Test Loss', value: formatDecimal(metrics.test_loss) }
  ]
})
const supportCards = computed(() => {
  if (!resultState.value) return []
  return [
    { label: '样本数', value: resultState.value.data_summary?.rows ?? '-' },
    { label: '特征维度', value: resultState.value.data_summary?.feature_dim ?? '-' },
    { label: '类别数', value: resultState.value.class_names?.length ?? '-' }
  ]
})
const paramsSummary = computed(() => resultState.value?.selected_params || {})
const perClassEntries = computed(() => Object.entries(resultState.value?.per_class_metrics || {}))
const plotCards = computed(() => {
  const plots = resultState.value?.plots || {}
  return [
    { key: 'loss', title: '损失曲线', url: normalizePlotUrl(plots.loss_curve_url) },
    { key: 'accuracy', title: '准确率曲线', url: normalizePlotUrl(plots.accuracy_curve_url) },
    { key: 'confusion', title: '混淆矩阵', url: normalizePlotUrl(plots.confusion_matrix_url) },
    { key: 'perClass', title: '分类别指标图', url: normalizePlotUrl(plots.per_class_metrics_url) }
  ]
})

// 实现思路：根据路由里的 jobId 获取完整训练结果，并在已有保存记录时回填模型名称。
const loadResult = async () => {
  if (!jobId.value) return
  loading.value = true
  errorMessage.value = ''
  try {
    const { data } = await getTrainResult(jobId.value)
    resultState.value = data
    if (savedRecord.value) saveForm.name = savedRecord.value.name
  } catch (error) {
    errorMessage.value = error.message || '获取训练结果失败'
  } finally {
    loading.value = false
  }
}

// 实现思路：把当前训练任务以“名称 + jobId”的形式登记到本地模型库，供预测页复用。
const saveWeight = () => {
  if (!jobId.value || !resultState.value) return
  saveModelRecord({
    jobId: jobId.value,
    name: saveForm.name,
    params: resultState.value.selected_params,
    createdAt: new Date().toISOString()
  })
  saveMessage.value = '权重已保存'
  window.setTimeout(() => {
    saveMessage.value = ''
  }, 1800)
}

// 实现思路：结果页加载后立即拉取指定任务的训练结果。
onMounted(() => {
  loadResult()
})
</script>

<template>
  <section class="module-stack">
    <div class="result-hero-row">
      <div class="glass-card training-panel result-overview-panel">
        <div class="module-section-head compact-head">
          <div>
            <p class="profile-modal-label">训练结果</p>
            <h2>结果总览</h2>
          </div>
          <span class="job-id-chip">{{ jobId || '暂无任务' }}</span>
        </div>

        <div v-if="errorMessage" class="inline-alert error">{{ errorMessage }}</div>
        <div v-if="loading" class="chart-empty result-loading-card">正在获取结果...</div>

        <template v-else-if="resultState">
          <div class="result-metric-grid">
            <div v-for="card in overviewCards" :key="card.label" class="metric-card highlight-card">
              <span>{{ card.label }}</span>
              <strong>{{ card.value }}</strong>
            </div>
          </div>

          <div class="metrics-grid support-grid">
            <div v-for="card in supportCards" :key="card.label" class="metric-card secondary-card">
              <span>{{ card.label }}</span>
              <strong>{{ card.value }}</strong>
            </div>
          </div>
        </template>
      </div>

      <div class="glass-card training-panel save-panel">
        <div class="module-section-head compact-head">
          <div>
            <p class="profile-modal-label">权重保存</p>
            <h2>{{ savedRecord ? '已保存模型' : '保存当前权重' }}</h2>
          </div>
        </div>

        <label class="wide-field">
          权重名称
          <input v-model="saveForm.name" placeholder="例如：adam-20epoch-best" />
        </label>

        <div class="panel-actions-row panel-actions-row-end">
          <button class="ghost-btn" @click="router.push({ name: 'model-training' })">返回训练</button>
          <button class="primary-btn" :disabled="!resultState" @click="saveWeight">保存权重</button>
        </div>

        <div v-if="saveMessage" class="inline-alert success slim-alert">{{ saveMessage }}</div>
        <div v-if="savedRecord" class="saved-model-card">
          <span>当前名称</span>
          <strong>{{ savedRecord.name }}</strong>
          <small>可在预测页直接选择这个模型。</small>
        </div>
      </div>
    </div>

    <div v-if="resultState" class="plot-grid">
      <div v-for="plot in plotCards" :key="plot.key" class="glass-card visual-card plot-card">
        <div class="chart-head">
          <h3>{{ plot.title }}</h3>
        </div>
        <div v-if="plot.url" class="plot-image-shell">
          <img :src="plot.url" :alt="plot.title" class="result-plot-image" />
        </div>
        <div v-else class="chart-empty">暂无图片结果</div>
      </div>
    </div>

    <div v-if="resultState" class="training-visual-grid result-bottom-grid">
      <div class="glass-card visual-card">
        <div class="chart-head">
          <h3>分类别评估</h3>
        </div>
        <div class="class-table-shell">
          <table class="class-metrics-table">
            <thead>
              <tr>
                <th>类别</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>F1</th>
                <th>Support</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="entry in perClassEntries" :key="entry[0]">
                <td>{{ entry[0] }}</td>
                <td>{{ formatMetricValue(entry[1].precision) }}</td>
                <td>{{ formatMetricValue(entry[1].recall) }}</td>
                <td>{{ formatMetricValue(entry[1].f1) }}</td>
                <td>{{ entry[1].support }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="glass-card visual-card">
        <div class="chart-head">
          <h3>模型参数</h3>
        </div>
        <div class="param-summary-grid compact-param-grid">
          <div v-for="(value, key) in paramsSummary" :key="key" class="param-chip">
            <span>{{ key }}</span>
            <strong>{{ value }}</strong>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
