import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'

// 添加请求拦截器来自动包含JWT令牌
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

createApp(App).use(router).mount('#app')