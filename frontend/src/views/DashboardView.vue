<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h2>File Management Dashboard</h2>
      <p>Upload and download encrypted files securely</p>
    </div>

    <div class="dashboard-content">
      <div class="upload-section">
        <h3>Upload File</h3>
        <form @submit.prevent="handleUpload" class="upload-form">
          <div class="file-input-wrapper">
            <input 
              type="file" 
              id="file-input" 
              @change="handleFileSelect"
              required
            >
            <label for="file-input" class="file-label">
              <span class="file-label-text">{{ selectedFileName || 'Choose a file...' }}</span>
              <span class="file-label-button">Browse</span>
            </label>
          </div>
          <button type="submit" class="btn btn-primary" :disabled="uploading">
            {{ uploading ? 'Uploading...' : 'Upload & Encrypt' }}
          </button>
        </form>
      </div>

      <div class="files-section">
        <h3>Available Files</h3>
        <div v-if="loadingFiles" class="loading">Loading files...</div>
        <div v-else-if="files.length > 0" class="files-list">
          <table class="files-table">
            <thead>
              <tr>
                <th>Filename</th>
                <th>Size</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="file in files" :key="file.encrypted_name">
                <td>{{ file.name }}</td>
                <td>{{ formatFileSize(file.size) }}</td>
                <td>
                  <button @click="downloadFile(file)" class="btn btn-download">
                    Download & Decrypt
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="no-files">
          <p>No files available. Upload a file to get started.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'DashboardView',
  data() {
    return {
      files: [],
      loadingFiles: false,
      uploading: false,
      selectedFile: null,
      selectedFileName: ''
    }
  },
  async created() {
    await this.loadFiles()
  },
  methods: {
    async loadFiles() {
      this.loadingFiles = true
      try {
        const response = await axios.get('/api/files')
        this.files = response.data.files || []
      } catch (error) {
        // 使用全局事件总线发送消息
        window.dispatchEvent(new CustomEvent('flash-message', {
          detail: {
            message: 'Failed to load files: ' + (error.response?.data?.message || error.message),
            type: 'error'
          }
        }))
      } finally {
        this.loadingFiles = false
      }
    },
    
    handleFileSelect(event) {
      const file = event.target.files[0]
      if (file) {
        this.selectedFile = file
        this.selectedFileName = file.name
      } else {
        this.selectedFile = null
        this.selectedFileName = ''
      }
    },
    
    async handleUpload() {
      if (!this.selectedFile) {
        // 使用全局事件总线发送消息
        window.dispatchEvent(new CustomEvent('flash-message', {
          detail: {
            message: 'Please select a file to upload',
            type: 'error'
          }
        }))
        return
      }
      
      // Check file size (16MB limit)
      if (this.selectedFile.size > 16 * 1024 * 1024) {
        // 使用全局事件总线发送消息
        window.dispatchEvent(new CustomEvent('flash-message', {
          detail: {
            message: 'File size exceeds the maximum limit of 16MB',
            type: 'error'
          }
        }))
        return
      }
      
      this.uploading = true
      
      try {
        const formData = new FormData()
        formData.append('file', this.selectedFile)
        
        await axios.post('/api/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        // 使用全局事件总线发送消息
        window.dispatchEvent(new CustomEvent('flash-message', {
          detail: {
            message: `File ${this.selectedFile.name} uploaded and encrypted successfully!`,
            type: 'success'
          }
        }))
        
        // Reset file input
        this.selectedFile = null
        this.selectedFileName = ''
        document.getElementById('file-input').value = ''
        
        // Reload files list
        await this.loadFiles()
      } catch (error) {
        // 使用全局事件总线发送消息
        window.dispatchEvent(new CustomEvent('flash-message', {
          detail: {
            message: 'Upload failed: ' + (error.response?.data?.message || error.message),
            type: 'error'
          }
        }))
      } finally {
        this.uploading = false
      }
    },
    
    async downloadFile(file) {
      try {
        const response = await axios.get(`/api/download/${file.name}`, {
          responseType: 'blob'
        })
        
        // Create download link
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', file.name)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
      } catch (error) {
        // 使用全局事件总线发送消息
        window.dispatchEvent(new CustomEvent('flash-message', {
          detail: {
            message: 'Download failed: ' + (error.response?.data?.message || error.message),
            type: 'error'
          }
        }))
      }
    },
    
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }
  }
}
</script>

<style scoped>
.dashboard {
  background: var(--card-bg);
  border-radius: 1rem;
  box-shadow: var(--shadow);
  padding: 2rem;
}

.dashboard-header {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.dashboard-header h2 {
  margin-bottom: 0.5rem;
  color: var(--text-color);
}

.dashboard-header p {
  color: var(--text-light);
}

.dashboard-content {
  display: grid;
  gap: 2rem;
}

.upload-section,
.files-section {
  background: var(--bg-color);
  padding: 1.5rem;
  border-radius: 0.75rem;
}

.upload-section h3,
.files-section h3 {
  margin-bottom: 1rem;
  color: var(--text-color);
}

/* File Input */
.file-input-wrapper {
  position: relative;
  margin-bottom: 1rem;
}

.file-input-wrapper input[type="file"] {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.file-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  border: 2px dashed var(--border-color);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  background-color: var(--card-bg);
}

.file-label:hover {
  border-color: var(--primary-color);
  background-color: #f8fafc;
}

.file-label-text {
  color: var(--text-light);
  flex: 1;
}

.file-label-button {
  background-color: var(--primary-color);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
}

/* Files Table */
.files-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--card-bg);
  border-radius: 0.5rem;
  overflow: hidden;
}

.files-table thead {
  background-color: var(--bg-color);
}

.files-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--text-color);
  border-bottom: 2px solid var(--border-color);
}

.files-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.files-table tbody tr:hover {
  background-color: var(--bg-color);
}

.files-table tbody tr:last-child td {
  border-bottom: none;
}

.no-files {
  text-align: center;
  padding: 2rem;
  color: var(--text-light);
}

.loading {
  text-align: center;
  padding: 2rem;
  color: var(--text-light);
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard {
    padding: 1.5rem;
  }

  .files-table {
    font-size: 0.875rem;
  }

  .files-table th,
  .files-table td {
    padding: 0.75rem 0.5rem;
  }
}
</style>