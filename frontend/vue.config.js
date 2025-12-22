const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      '^/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        logLevel: 'debug',
        // 根据请求头中的"x-target-port"来确定实际要转发到的端口
        router: (req) => {
          // 从请求头中获取目标端口
          const targetPort = req.headers['x-target-port'];
          if (targetPort) {
            console.log(`Proxying to port: ${targetPort}`);
            return `http://127.0.0.1:${targetPort}`;
          }
          // 默认使用5000端口
          console.log('Proxying to default port: 5000');
          return 'http://127.0.0.1:5000';
        },
        // 删除x-target-port头部，避免发送到后端
        onProxyReq: (proxyReq, req, res) => {
          if (proxyReq.getHeader('x-target-port')) {
            proxyReq.removeHeader('x-target-port');
          }
        },
        // 处理代理错误
        onError: (err, req, res) => {
          console.error('Proxy error:', err);
          res.writeHead(500, {
            'Content-Type': 'application/json',
          });
          res.end(JSON.stringify({ message: 'Proxy error: ' + err.message }));
        }
      }
    }
  }
})