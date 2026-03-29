<!--
  文件说明：登录与注册页，负责认证表单输入、前端校验、登录态写入和页面跳转。
  维护重点：这里聚合认证体验逻辑，不和业务页面混写。
-->
<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { login, register } from '../api/auth'
import { setSessionUser } from '../state/session'

const router = useRouter()
const authMode = reactive({ value: 'login' })
const form = reactive({
  username: 'admin',
  password: ''
})
const errors = reactive({
  username: '',
  password: ''
})
const toast = reactive({
  show: false,
  message: '',
  type: 'success'
})

// 实现思路：登录页内部维护轻量提示，统一承接注册、登录和失败反馈。
const showToast = (message, type = 'success') => {
  toast.show = true
  toast.message = message
  toast.type = type
  window.setTimeout(() => {
    toast.show = false
  }, 1800)
}

// 实现思路：按当前模式区分登录和注册的输入要求，把用户名和密码的基础校验前置。
const validate = () => {
  let valid = true
  errors.username = ''
  errors.password = ''

  if (!form.username.trim()) {
    errors.username = '请输入用户名'
    valid = false
  }

  if (!form.password.trim()) {
    errors.password = '请输入密码'
    valid = false
  } else if (authMode.value === 'register' && form.password.trim().length < 6) {
    errors.password = '密码至少 6 位'
    valid = false
  }

  return valid
}

// 实现思路：根据当前模式选择登录或注册接口，成功后写入会话并跳转到业务首页。
const submit = async () => {
  if (!validate()) return

  try {
    const payload = {
      username: form.username.trim(),
      password: form.password.trim()
    }
    const response = authMode.value === 'register' ? await register(payload) : await login(payload)
    setSessionUser(response.data?.data || response.data)
    showToast(authMode.value === 'register' ? '注册成功' : '登录成功')
    window.setTimeout(() => {
      router.push('/app/data-management')
    }, 250)
  } catch (error) {
    showToast(error.message || '认证失败', 'error')
  }
}
</script>

<template>
  <div class="login-page">
    <section class="login-panel login-hero">
      <div class="hero-copy">
        <span class="hero-kicker">QAPP</span>
        <h1>QAPP</h1>
        <p>基于深度学习的**毕业设计</p>

        <div class="hero-card-row">
          <div class="hero-mini-card">
            <strong>Data</strong>
            <span>数据管理</span>
          </div>
          <div class="hero-mini-card">
            <strong>Train</strong>
            <span>模型训练</span>
          </div>
          <div class="hero-mini-card">
            <strong>Predict</strong>
            <span>预测分析</span>
          </div>
        </div>
      </div>
      <div class="hero-orb hero-orb-large" />
      <div class="hero-orb hero-orb-small" />
      <div class="hero-grid" />
    </section>

    <section class="login-panel login-form-panel">
      <div class="login-form-shell">
        <div class="form-heading">
          <span class="form-kicker">Account</span>
          <h2>{{ authMode.value === 'login' ? '欢迎回来' : '创建账号' }}</h2>
        </div>

        <div class="segmented-control">
          <button class="segment" :class="{ active: authMode.value === 'login' }" @click="authMode.value = 'login'">登录</button>
          <button class="segment" :class="{ active: authMode.value === 'register' }" @click="authMode.value = 'register'">注册</button>
        </div>

        <form class="login-form" @submit.prevent="submit">
          <label>
            用户名
            <input v-model="form.username" type="text" placeholder="请输入用户名" />
            <small v-if="errors.username">{{ errors.username }}</small>
          </label>

          <label>
            密码
            <input v-model="form.password" type="password" placeholder="请输入密码" />
            <small v-if="errors.password">{{ errors.password }}</small>
          </label>

          <button type="submit" class="primary-btn wide-btn">{{ authMode.value === 'login' ? '登录' : '注册' }}</button>
        </form>
      </div>
    </section>

    <transition name="fade">
      <div v-if="toast.show" class="floating-toast" :class="toast.type">{{ toast.message }}</div>
    </transition>
  </div>
</template>
