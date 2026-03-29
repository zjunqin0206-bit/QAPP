/*
 * 文件说明：应用入口文件，负责挂载 Vue 应用、注册路由，并引入全局样式。
 * 维护重点：这里只保留启动流程，不承载业务状态与页面逻辑。
 */
import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

createApp(App).use(router).mount('#app')
