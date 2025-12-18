const { defineConfig } = require('@vue/cli-service')

// 简单的轮询负载均衡器
let currentPort = 5000
const ports = [5000, 5001, 5002, 5003, 5004, 5005]

function getNextPort() {
  const port = ports[currentPort % ports.length]
  currentPort++
  return port
}

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      '/api': {
        target: `http://localhost:${getNextPort()}`,
        changeOrigin: true,
        // 路径重写，确保请求发送到正确的位置
        pathRewrite: {
          '^/api': '/api'
        },
        // 自定义代理逻辑，实现简单的轮询
        router: () => {
          return `http://localhost:${getNextPort()}`
        }
      }
    }
  }
})