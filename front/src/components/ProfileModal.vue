<!--
  文件说明：个人信息弹窗组件，负责展示当前用户名并提供密码修改入口。
  维护重点：组件只处理表单校验与提交，不直接管理全局登录态。
-->
<script setup>
import { reactive } from 'vue'
import { changePassword } from '../api/auth'

const props = defineProps({
  open: {
    type: Boolean,
    default: false
  },
  username: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close', 'success', 'error'])

const form = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const errors = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 实现思路：关闭弹窗或修改成功后统一清空表单和错误信息，避免残留旧输入。
const reset = () => {
  form.oldPassword = ''
  form.newPassword = ''
  form.confirmPassword = ''
  errors.oldPassword = ''
  errors.newPassword = ''
  errors.confirmPassword = ''
}

// 实现思路：先重置内部状态，再向父组件发出关闭事件，保持弹窗复用时状态干净。
const close = () => {
  reset()
  emit('close')
}

// 实现思路：把旧密码、新密码、确认密码的前端校验集中处理，提交前先阻断明显错误。
const validate = () => {
  let valid = true
  errors.oldPassword = ''
  errors.newPassword = ''
  errors.confirmPassword = ''

  if (!form.oldPassword.trim()) {
    errors.oldPassword = '请输入旧密码'
    valid = false
  }

  if (!form.newPassword.trim()) {
    errors.newPassword = '请输入新密码'
    valid = false
  } else if (form.newPassword.trim().length < 6) {
    errors.newPassword = '新密码至少 6 位'
    valid = false
  }

  if (!form.confirmPassword.trim()) {
    errors.confirmPassword = '请再次输入新密码'
    valid = false
  } else if (form.confirmPassword !== form.newPassword) {
    errors.confirmPassword = '两次输入的新密码不一致'
    valid = false
  }

  return valid
}

// 实现思路：校验通过后调用修改密码接口，成功时通过事件把结果反馈给顶层壳组件。
const submit = async () => {
  if (!validate()) return

  try {
    await changePassword({
      oldPassword: form.oldPassword.trim(),
      newPassword: form.newPassword.trim()
    })
    reset()
    emit('success', '密码修改成功')
    emit('close')
  } catch (error) {
    emit('error', error.message || '修改密码失败')
  }
}
</script>

<template>
  <transition name="fade">
    <div v-if="open" class="profile-modal-mask" @click.self="close">
      <div class="profile-modal-card">
        <div class="profile-modal-header">
          <div>
            <p class="profile-modal-label">个人信息</p>
            <h2>{{ username }}</h2>
          </div>
          <button class="icon-btn" @click="close">关闭</button>
        </div>

        <form class="profile-form" @submit.prevent="submit">
          <label>
            旧密码
            <input v-model="form.oldPassword" type="password" placeholder="请输入旧密码" />
            <small v-if="errors.oldPassword">{{ errors.oldPassword }}</small>
          </label>

          <label>
            新密码
            <input v-model="form.newPassword" type="password" placeholder="请输入新密码" />
            <small v-if="errors.newPassword">{{ errors.newPassword }}</small>
          </label>

          <label>
            确认新密码
            <input v-model="form.confirmPassword" type="password" placeholder="请再次输入新密码" />
            <small v-if="errors.confirmPassword">{{ errors.confirmPassword }}</small>
          </label>

          <div class="profile-submit-row">
            <button type="submit" class="primary-btn">修改密码</button>
          </div>
        </form>
      </div>
    </div>
  </transition>
</template>
