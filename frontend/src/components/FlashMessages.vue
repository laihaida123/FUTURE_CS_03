<template>
  <div class="flash-messages" v-if="messages.length > 0">
    <div 
      v-for="(message, index) in messages" 
      :key="index" 
      :class="['flash-message', `flash-${message.type}`]"
    >
      {{ message.text }}
      <button class="flash-close" @click="removeMessage(index)">×</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FlashMessages',
  data() {
    return {
      messages: []
    }
  },
  mounted() {
    // Listen for flash messages from anywhere in the app
    window.addEventListener('flash-message', this.handleFlashMessage)
  },
  beforeUnmount() {
    // Clean up event listener
    window.removeEventListener('flash-message', this.handleFlashMessage)
  },
  methods: {
    addMessage(text, type = 'info') {
      const message = { text, type }
      this.messages.push(message)
      // Auto-remove message after 5 seconds
      setTimeout(() => {
        const index = this.messages.indexOf(message)
        if (index !== -1) {
          this.removeMessageByIndex(index)
        }
      }, 5000)
    },
    removeMessage(index) {
      this.messages.splice(index, 1)
    },
    removeMessageByIndex(index) {
      if (index >= 0 && index < this.messages.length) {
        this.messages.splice(index, 1)
      }
    },
    handleFlashMessage(event) {
      this.addMessage(event.detail.message, event.detail.type)
    }
  }
}
</script>

<style scoped>
.flash-messages {
  margin-bottom: 1.5rem;
}

.flash-message {
  padding: 1rem 1.5rem;
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.flash-success {
  background-color: #d1fae5;
  color: #065f46;
  border-left: 4px solid var(--success-color);
}

.flash-error {
  background-color: #fee2e2;
  color: #991b1b;
  border-left: 4px solid var(--error-color);
}

.flash-info {
  background-color: #dbeafe;
  color: #1e40af;
  border-left: 4px solid var(--info-color);
}

.flash-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: inherit;
  opacity: 0.7;
  padding: 0;
  margin-left: 1rem;
  line-height: 1;
}

.flash-close:hover {
  opacity: 1;
}
</style>