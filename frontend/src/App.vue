<template>
  <div id="app">
    <nav class="navbar" v-if="$route.name !== 'login'">
      <div class="nav-container">
        <h1 class="nav-logo">Secure File Portal</h1>
        <div class="nav-user" v-if="isLoggedIn">
          <span>Welcome, <strong>{{ username }}</strong></span>
          <button @click="logout" class="btn btn-logout">Logout</button>
        </div>
      </div>
    </nav>

    <div class="container">
      <FlashMessages ref="flashMessages" />
      <router-view />
    </div>
  </div>
</template>

<script>
import FlashMessages from './components/FlashMessages.vue'

export default {
  name: 'App',
  components: {
    FlashMessages
  },
  data() {
    return {
      isLoggedIn: false,
      username: ''
    }
  },
  created() {
    // Check if user is logged in
    const token = localStorage.getItem('token')
    if (token) {
      this.isLoggedIn = true
      this.username = localStorage.getItem('username') || ''
    }
    
    // Listen for login events
    window.addEventListener('user-login', (event) => {
      this.isLoggedIn = true
      this.username = event.detail.username
    })
    
    // Listen for logout events
    window.addEventListener('user-logout', () => {
      this.isLoggedIn = false
      this.username = ''
    })
    
    // Listen for flash messages
    window.addEventListener('flash-message', (event) => {
      if (this.$refs.flashMessages) {
        this.$refs.flashMessages.addMessage(
          event.detail.message, 
          event.detail.type
        )
      }
    })
  },
  methods: {
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      this.isLoggedIn = false
      this.username = ''
      
      // Dispatch logout event
      window.dispatchEvent(new CustomEvent('user-logout'))
      
      // Show logout message directly through component reference
      if (this.$refs.flashMessages) {
        this.$refs.flashMessages.addMessage('You have been logged out', 'info')
      }
      
      this.$router.push('/login')
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --primary-color: #2563eb;
  --primary-hover: #1d4ed8;
  --secondary-color: #64748b;
  --success-color: #10b981;
  --error-color: #ef4444;
  --warning-color: #f59e0b;
  --info-color: #3b82f6;
  --bg-color: #f8fafc;
  --card-bg: #ffffff;
  --text-color: #1e293b;
  --text-light: #64748b;
  --border-color: #e2e8f0;
  --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: var(--bg-color);
  color: var(--text-color);
  line-height: 1.6;
  min-height: 100vh;
}

.navbar {
  background-color: var(--card-bg);
  box-shadow: var(--shadow);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-logo {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.btn {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background-color: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow);
}

.btn-logout {
  background-color: var(--error-color);
  color: white;
}

.btn-download {
  background-color: var(--success-color);
  color: white;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.btn-download:hover {
  background-color: #059669;
}

.btn-block {
  width: 100%;
}
/* Responsive */
@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    gap: 1rem;
  }
  
  .container {
    padding: 1rem;
  }
}
</style>