<!--
  文件说明：保留的根组件占位文件，当前路由架构下实际页面由 AppShell 和各页面组件承载。
  维护重点：如果后续彻底切换到路由式布局，这个文件可以继续保持轻量或被清理。
-->
<template>
  <RouterView />
</template>

<script setup>
import { RouterView } from 'vue-router'
</script>
