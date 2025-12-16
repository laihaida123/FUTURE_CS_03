<template>
  <div class="login-container">
    <div class="login-card">
      <h2>Login to Secure File Portal</h2>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">Username</label>
          <input 
            type="text" 
            id="username" 
            v-model="credentials.username" 
            required 
            autofocus
            placeholder="Enter your username"
          >
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input 
            type="password" 
            id="password" 
            v-model="credentials.password" 
            required
            placeholder="Enter your password"
          >
        </div>
        <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
      </form>
      <div class="login-info">
        <p><strong>Demo Credentials:</strong></p>
        <p>Username: <code>admin</code> | Password: <code>admin123</code></p>
        <p>Username: <code>user1</code> | Password: <code>password123</code></p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'LoginView',
  data() {
    return {
      credentials: {
        username: '',
        password: ''
      },
      loading: false
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true
      try {
        const response = await axios.post('/api/login', {
          username: this.credentials.username,
          password: this.credentials.password
        })

        if (response.data.success) {
          // Store token and username in localStorage
          localStorage.setItem('token', response.data.token)
          localStorage.setItem('username', this.credentials.username)
          
          // Dispatch login event
          window.dispatchEvent(new CustomEvent('user-login', {
            detail: { username: this.credentials.username }
          }))
          
          // Redirect to dashboard or previous page
          const redirect = this.$route.query.redirect || '/dashboard'
          this.$router.push(redirect)
        } else {
          // 使用全局事件总线发送消息
          window.dispatchEvent(new CustomEvent('flash-message', {
            detail: {
              message: response.data.message || 'Login failed',
              type: 'error'
            }
          }))
        }
      } catch (error) {
        // 使用全局事件总线发送消息
        window.dispatchEvent(new CustomEvent('flash-message', {
          detail: {
            message: error.response?.data?.message || 'An error occurred during login',
            type: 'error'
          }
        }))
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 200px);
}

.login-card {
  background: var(--card-bg);
  padding: 2.5rem;
  border-radius: 1rem;
  box-shadow: var(--shadow-lg);
  width: 100%;
  max-width: 400px;
}

.login-card h2 {
  margin-bottom: 1.5rem;
  text-align: center;
  color: var(--text-color);
}

.login-form {
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color);
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.login-info {
  background-color: var(--bg-color);
  padding: 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-light);
}

.login-info code {
  background-color: var(--card-bg);
  padding: 0.2rem 0.4rem;
  border-radius: 0.25rem;
  font-family: 'Courier New', monospace;
}
</style>