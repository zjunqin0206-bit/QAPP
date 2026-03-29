<!--
  文件说明：Iris 数据管理页，负责列表展示、分页、条件筛选、增删改和弹窗交互。
  维护重点：该页面状态较多，函数按“列表、筛选、表单、生命周期”分段维护。
-->
<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { addIris, deleteIris, filterIris, getIrisById, getIrisList, updateIris } from '../api/iris'

const SPECIES_OPTIONS = ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']
const RANGE_FIELDS = [
  { key: 'sepalLength', label: '花萼长度' },
  { key: 'sepalWidth', label: '花萼宽度' },
  { key: 'petalLength', label: '花瓣长度' },
  { key: 'petalWidth', label: '花瓣宽度' }
]

const loading = ref(false)
const irisList = ref([])
const showModal = ref(false)
const showFilterPanel = ref(false)
const isEditMode = ref(false)
const currentId = ref(null)
const hasActiveFilter = ref(false)
const toast = reactive({ show: false, message: '', type: 'success' })
const formErrors = reactive({ sepalLength: '', sepalWidth: '', petalLength: '', petalWidth: '', species: '' })
const filterErrors = reactive({ sepalLength: '', sepalWidth: '', petalLength: '', petalWidth: '' })
const formData = reactive({ sepalLength: '', sepalWidth: '', petalLength: '', petalWidth: '', species: SPECIES_OPTIONS[0] })
const filterForm = reactive({
  sepalLengthMin: '',
  sepalLengthMax: '',
  sepalWidthMin: '',
  sepalWidthMax: '',
  petalLengthMin: '',
  petalLengthMax: '',
  petalWidthMin: '',
  petalWidthMax: '',
  speciesList: []
})
const pageSize = 10
const currentPage = ref(1)

const totalPages = computed(() => Math.max(1, Math.ceil(irisList.value.length / pageSize)))
const pagedList = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return irisList.value.slice(start, start + pageSize)
})
const pageNumbers = computed(() => Array.from({ length: totalPages.value }, (_, index) => index + 1))
const formTitle = computed(() => (isEditMode.value ? '编辑数据' : '新增数据'))

// 实现思路：兼容不同列表返回结构，把数组提取逻辑统一收口。
const extractList = (payload) => {
  if (Array.isArray(payload)) return payload
  if (Array.isArray(payload?.data)) return payload.data
  if (Array.isArray(payload?.records)) return payload.records
  if (Array.isArray(payload?.rows)) return payload.rows
  return []
}

// 实现思路：详情接口可能存在多种包装层，这里统一展开成单条记录对象。
const extractDetail = (payload) => payload?.data || payload?.record || payload?.row || payload || {}

// 实现思路：把后端可能出现的驼峰、下划线和备用字段统一归一成页面可用的数据结构。
const normalizeIris = (item = {}) => ({
  id: item.id ?? item.irisId ?? null,
  sepalLength: item.sepalLength ?? item.sepal_length ?? '',
  sepalWidth: item.sepalWidth ?? item.sepal_width ?? '',
  petalLength: item.petalLength ?? item.petal_length ?? '',
  petalWidth: item.petalWidth ?? item.petal_width ?? '',
  species: item.species ?? item.variety ?? ''
})

// 实现思路：数据页内部统一管理浮动提示，增删改查和筛选都通过它反馈结果。
const showToast = (message, type = 'success') => {
  toast.show = true
  toast.message = message
  toast.type = type
  window.setTimeout(() => {
    toast.show = false
  }, 1800)
}

// 实现思路：每次打开新增弹窗前都重置表单和错误状态，避免编辑态残留。
const resetForm = () => {
  formData.sepalLength = ''
  formData.sepalWidth = ''
  formData.petalLength = ''
  formData.petalWidth = ''
  formData.species = SPECIES_OPTIONS[0]
  formErrors.sepalLength = ''
  formErrors.sepalWidth = ''
  formErrors.petalLength = ''
  formErrors.petalWidth = ''
  formErrors.species = ''
}

// 实现思路：重置筛选面板内部所有字段和错误提示，让筛选恢复到初始状态。
const resetFilterState = () => {
  filterForm.sepalLengthMin = ''
  filterForm.sepalLengthMax = ''
  filterForm.sepalWidthMin = ''
  filterForm.sepalWidthMax = ''
  filterForm.petalLengthMin = ''
  filterForm.petalLengthMax = ''
  filterForm.petalWidthMin = ''
  filterForm.petalWidthMax = ''
  filterForm.speciesList = []
  filterErrors.sepalLength = ''
  filterErrors.sepalWidth = ''
  filterErrors.petalLength = ''
  filterErrors.petalWidth = ''
}

// 实现思路：不仅清空筛选表单，还要关闭筛选弹窗并重新拉取完整列表。
const resetFilter = async () => {
  resetFilterState()
  hasActiveFilter.value = false
  showFilterPanel.value = false
  await fetchList()
}

// 实现思路：新增和编辑共用同一套字段校验，优先在前端阻断非法输入。
const validateForm = () => {
  let valid = true
  ;['sepalLength', 'sepalWidth', 'petalLength', 'petalWidth'].forEach((field) => {
    const value = Number(formData[field])
    if (formData[field] === '' || Number.isNaN(value)) {
      formErrors[field] = '请输入有效数字'
      valid = false
    } else if (value <= 0) {
      formErrors[field] = '数值必须大于 0'
      valid = false
    } else {
      formErrors[field] = ''
    }
  })

  if (!SPECIES_OPTIONS.includes(formData.species)) {
    formErrors.species = '请选择有效品种'
    valid = false
  } else {
    formErrors.species = ''
  }

  return valid
}

// 实现思路：筛选区只校验成对填写的区间字段，避免把不合法范围提交给后端。
const validateFilter = () => {
  let valid = true
  RANGE_FIELDS.forEach(({ key, label }) => {
    const minKey = `${key}Min`
    const maxKey = `${key}Max`
    filterErrors[key] = ''
    const minValue = filterForm[minKey]
    const maxValue = filterForm[maxKey]
    if (minValue === '' || maxValue === '') return
    const minNum = Number(minValue)
    const maxNum = Number(maxValue)
    if (Number.isNaN(minNum) || Number.isNaN(maxNum) || minNum > maxNum) {
      filterErrors[key] = `${label}区间不合法`
      valid = false
    }
  })
  return valid
}

// 实现思路：只把用户真正填写的筛选条件打进请求体，保持请求简洁。
const buildFilterPayload = () => {
  const payload = {}
  Object.entries(filterForm).forEach(([key, value]) => {
    if (key === 'speciesList') {
      if (value.length) payload[key] = value
      return
    }
    if (value !== '') payload[key] = Number(value)
  })
  return payload
}

// 实现思路：统一承担列表拉取和分页重置逻辑，供首屏加载和重置筛选复用。
const fetchList = async () => {
  loading.value = true
  try {
    const { data } = await getIrisList()
    irisList.value = extractList(data).map(normalizeIris)
    currentPage.value = 1
  } catch (error) {
    showToast(error.message || '获取列表失败', 'error')
  } finally {
    loading.value = false
  }
}

// 实现思路：筛选提交前先校验，再根据后端返回结果替换当前列表。
const submitFilter = async () => {
  if (!validateFilter()) return
  const payload = buildFilterPayload()
  loading.value = true
  try {
    if (!Object.keys(payload).length) {
      hasActiveFilter.value = false
      showFilterPanel.value = false
      await fetchList()
      return
    }
    const { data } = await filterIris(payload)
    irisList.value = extractList(data).map(normalizeIris)
    currentPage.value = 1
    hasActiveFilter.value = true
    showFilterPanel.value = false
    showToast('筛选完成')
  } catch (error) {
    showToast(error.message || '筛选失败', 'error')
  } finally {
    loading.value = false
  }
}

// 实现思路：用切换逻辑维护品种多选数组，让筛选按钮组保持可反选。
const toggleSpecies = (species) => {
  const index = filterForm.speciesList.indexOf(species)
  if (index >= 0) filterForm.speciesList.splice(index, 1)
  else filterForm.speciesList.push(species)
}

// 实现思路：新增时清空当前记录和编辑态，再打开表单弹窗。
const openCreateModal = () => {
  isEditMode.value = false
  currentId.value = null
  resetForm()
  showModal.value = true
}

// 实现思路：编辑前先获取详情并回填表单，避免列表数据不完整导致编辑错误。
const openEditModal = async (id) => {
  loading.value = true
  try {
    const { data } = await getIrisById(id)
    const detail = normalizeIris(extractDetail(data))
    isEditMode.value = true
    currentId.value = id
    formData.sepalLength = detail.sepalLength
    formData.sepalWidth = detail.sepalWidth
    formData.petalLength = detail.petalLength
    formData.petalWidth = detail.petalWidth
    formData.species = SPECIES_OPTIONS.includes(detail.species) ? detail.species : SPECIES_OPTIONS[0]
    showModal.value = true
  } catch (error) {
    showToast(error.message || '查询详情失败', 'error')
  } finally {
    loading.value = false
  }
}

// 实现思路：新增与编辑复用同一提交入口，根据当前模式决定调用哪个接口。
const submitForm = async () => {
  if (!validateForm()) return
  const payload = {
    sepalLength: Number(formData.sepalLength),
    sepalWidth: Number(formData.sepalWidth),
    petalLength: Number(formData.petalLength),
    petalWidth: Number(formData.petalWidth),
    species: formData.species
  }

  loading.value = true
  try {
    if (isEditMode.value && currentId.value !== null) {
      await updateIris(currentId.value, payload)
      showToast('更新成功')
    } else {
      await addIris(payload)
      showToast('新增成功')
    }
    showModal.value = false
    resetForm()
    await (hasActiveFilter.value ? submitFilter() : fetchList())
  } catch (error) {
    showToast(error.message || '提交失败', 'error')
  } finally {
    loading.value = false
  }
}

// 实现思路：删除前先做二次确认，成功后根据当前是否筛选决定刷新策略。
const handleDelete = async (id) => {
  if (!window.confirm('确定删除这条数据吗？')) return
  loading.value = true
  try {
    await deleteIris(id)
    showToast('删除成功')
    await (hasActiveFilter.value ? submitFilter() : fetchList())
  } catch (error) {
    showToast(error.message || '删除失败', 'error')
  } finally {
    loading.value = false
  }
}

// 实现思路：把壳层派发的新增事件统一落到本页的创建弹窗逻辑上。
const handleOpenCreate = () => openCreateModal()

// 实现思路：页面挂载时先加载列表，再注册来自顶层壳组件的新增事件监听。
onMounted(() => {
  fetchList()
  window.addEventListener('open-create-iris', handleOpenCreate)
})

// 实现思路：页面销毁前移除全局事件监听，避免重复绑定和内存泄漏。
onBeforeUnmount(() => {
  window.removeEventListener('open-create-iris', handleOpenCreate)
})
</script>

<template>
  <section>
    <div class="table-actions-bar">
      <button class="ghost-btn" @click="showFilterPanel = true">
        {{ hasActiveFilter ? '条件筛选 · 已启用' : '条件筛选' }}
      </button>
    </div>

    <div v-if="showFilterPanel" class="profile-modal-mask" @click.self="showFilterPanel = false">
      <div class="profile-modal-card filter-modal-card">
        <div class="profile-modal-header">
          <div>
            <p class="profile-modal-label">条件筛选</p>
            <h2>筛选数据</h2>
          </div>
          <button class="icon-btn" @click="showFilterPanel = false">关闭</button>
        </div>

        <div class="filter-stack">
          <div v-for="field in RANGE_FIELDS" :key="field.key" class="range-row">
            <label class="range-title">{{ field.label }}</label>
            <div class="range-inputs">
              <input v-model="filterForm[`${field.key}Min`]" type="number" step="0.1" placeholder="最小值" />
              <input v-model="filterForm[`${field.key}Max`]" type="number" step="0.1" placeholder="最大值" />
            </div>
            <small v-if="filterErrors[field.key]">{{ filterErrors[field.key] }}</small>
          </div>

          <div class="species-filter-row compact-species-row">
            <span class="species-filter-title">品种筛选</span>
            <div class="species-chip-group">
              <button
                v-for="species in SPECIES_OPTIONS"
                :key="species"
                type="button"
                class="species-chip"
                :class="{ active: filterForm.speciesList.includes(species) }"
                @click="toggleSpecies(species)"
              >
                {{ species }}
              </button>
            </div>
          </div>

          <div class="filter-actions-row">
            <button class="ghost-btn" @click="resetFilter">重置</button>
            <button class="primary-btn" @click="submitFilter">应用筛选</button>
          </div>
        </div>
      </div>
    </div>

    <div class="glass-card table-card">
      <div class="table-wrapper">
        <table class="iris-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>花萼长度</th>
              <th>花萼宽度</th>
              <th>花瓣长度</th>
              <th>花瓣宽度</th>
              <th>品种</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!loading && irisList.length === 0">
              <td colspan="7" class="empty">暂无数据</td>
            </tr>
            <tr v-for="item in pagedList" :key="item.id">
              <td>{{ item.id }}</td>
              <td>{{ item.sepalLength }}</td>
              <td>{{ item.sepalWidth }}</td>
              <td>{{ item.petalLength }}</td>
              <td>{{ item.petalWidth }}</td>
              <td>{{ item.species }}</td>
              <td class="ops">
                <button class="ghost-btn" @click="openEditModal(item.id)">编辑</button>
                <button class="danger-btn small-btn" @click="handleDelete(item.id)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="footer-row footer-row-clean">
      <span aria-hidden="true"></span>
      <div class="pagination">
        <button class="ghost-btn small-btn" :disabled="currentPage === 1" @click="currentPage -= 1">上一页</button>
        <button
          v-for="page in pageNumbers"
          :key="page"
          class="page-chip"
          :class="{ active: currentPage === page }"
          @click="currentPage = page"
        >
          {{ page }}
        </button>
        <button class="ghost-btn small-btn" :disabled="currentPage === totalPages" @click="currentPage += 1">下一页</button>
      </div>
      <span aria-hidden="true"></span>
    </div>

    <div v-if="showModal" class="profile-modal-mask" @click.self="showModal = false">
      <div class="profile-modal-card form-modal-card">
        <div class="profile-modal-header">
          <div>
            <p class="profile-modal-label">数据管理</p>
            <h2>{{ formTitle }}</h2>
          </div>
          <button class="icon-btn" @click="showModal = false">关闭</button>
        </div>

        <form class="data-form-grid" @submit.prevent="submitForm">
          <label>
            花萼长度
            <input v-model="formData.sepalLength" type="number" step="0.1" />
            <small v-if="formErrors.sepalLength">{{ formErrors.sepalLength }}</small>
          </label>
          <label>
            花萼宽度
            <input v-model="formData.sepalWidth" type="number" step="0.1" />
            <small v-if="formErrors.sepalWidth">{{ formErrors.sepalWidth }}</small>
          </label>
          <label>
            花瓣长度
            <input v-model="formData.petalLength" type="number" step="0.1" />
            <small v-if="formErrors.petalLength">{{ formErrors.petalLength }}</small>
          </label>
          <label>
            花瓣宽度
            <input v-model="formData.petalWidth" type="number" step="0.1" />
            <small v-if="formErrors.petalWidth">{{ formErrors.petalWidth }}</small>
          </label>
          <label class="wide-field">
            品种
            <select v-model="formData.species">
              <option v-for="item in SPECIES_OPTIONS" :key="item" :value="item">{{ item }}</option>
            </select>
            <small v-if="formErrors.species">{{ formErrors.species }}</small>
          </label>
          <div class="form-actions-row wide-field">
            <button type="button" class="ghost-btn" @click="showModal = false">取消</button>
            <button type="submit" class="primary-btn">{{ isEditMode ? '保存修改' : '立即新增' }}</button>
          </div>
        </form>
      </div>
    </div>

    <transition name="fade">
      <div v-if="toast.show" class="floating-toast" :class="toast.type">{{ toast.message }}</div>
    </transition>
  </section>
</template>
