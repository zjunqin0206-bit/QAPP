import { fileURLToPath, URL } from 'node:url'

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const irisApiTarget = env.VITE_IRIS_API_PROXY_TARGET || 'http://backup.ns-3448g4cy:3000'
  const trainApiTarget = env.VITE_TRAIN_API_PROXY_TARGET || env.VITE_TRAIN_API_BASE_URL || irisApiTarget

  return {
    plugins: [vue()],
    server: {
      host: '0.0.0.0',
      port: 5173,
      allowedHosts: true,
      proxy: {
        '/api/v1': {
          target: trainApiTarget,
          changeOrigin: true
        },
        '/health': {
          target: trainApiTarget,
          changeOrigin: true
        },
        '/artifacts': {
          target: trainApiTarget,
          changeOrigin: true
        },
        '/api': {
          target: irisApiTarget,
          changeOrigin: true
        }
      }
    },
    preview: {
      host: '0.0.0.0',
      port: 5173
    },
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    }
  }
})
