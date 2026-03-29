<!--
  文件说明：应用主壳组件，负责顶部导航、右上角操作区、路由内容承载和全局提示。
  维护重点：所有登录后的通用布局能力都集中在这里，子页面只关注各自业务。
-->
<script setup>
import { computed, ref } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { logout } from '../api/auth'
import ProfileModal from '../components/ProfileModal.vue'
import { clearSessionUser, sessionState } from '../state/session'

const router = useRouter()
const route = useRoute()
const showProfileModal = ref(false)
const toast = ref({ show: false, message: '', type: 'success' })

const navItems = [
  { name: 'data-management', label: '数据管理', to: '/app/data-management' },
  { name: 'model-training', label: '模型训练', to: '/app/model-training' },
  { name: 'prediction', label: '预测', to: '/app/prediction' }
]

const showCreateButton = computed(() => route.name === 'data-management')
// 实现思路：把训练结果页也归并到模型训练导航高亮，避免子路由切换后菜单失去上下文。
const isNavActive = (item) => {
  if (item.name === 'model-training') return String(route.name || '').startsWith('model-training')
  return route.name === item.name
}

// 实现思路：壳层统一管理全局浮动提示，子组件通过事件上抛消息即可复用。
const showToast = (message, type = 'success') => {
  toast.value = { show: true, message, type }
  window.setTimeout(() => {
    toast.value.show = false
  }, 1800)
}

// 实现思路：优先通知后端退出，再兜底清理本地会话并跳回登录页。
const handleLogout = async () => {
  try {
    await logout()
  } catch {
    // ignore logout failure and clear local session anyway
  }
  clearSessionUser()
  router.push('/login')
}

// 实现思路：通过自定义事件通知数据页打开新增弹窗，避免顶层壳组件直接持有业务弹窗状态。
const triggerCreate = () => {
  window.dispatchEvent(new CustomEvent('open-create-iris'))
}
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand-cluster">
        <div>
          <h1>QAPP</h1>
          <p>基于深度学习的**毕业设计</p>
        </div>
        <nav class="top-nav">
          <RouterLink
            v-for="item in navItems"
            :key="item.name"
            :to="item.to"
            class="nav-link"
            :class="{ active: isNavActive(item) }"
          >
            {{ item.label }}
          </RouterLink>
        </nav>
      </div>

      <div class="topbar-actions">
        <button v-if="showCreateButton" class="primary-btn" @click="triggerCreate">新增数据</button>
        <button class="ghost-btn" @click="showProfileModal = true">个人信息</button>
        <button class="danger-btn" @click="handleLogout">退出登录</button>
      </div>
    </header>

    <main class="content-shell">
      <RouterView />
    </main>

    <ProfileModal
      :open="showProfileModal"
      :username="sessionState.user.username"
      @close="showProfileModal = false"
      @success="showToast($event, 'success')"
      @error="showToast($event, 'error')"
    />

    <transition name="fade">
      <div v-if="toast.show" class="floating-toast" :class="toast.type">{{ toast.message }}</div>
    </transition>
  </div>
</template>
