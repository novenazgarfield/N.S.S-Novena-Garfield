/**
 * 长离的学习胶囊 - 网页版应用
 * 支持智能问答、文档分析、文献检索
 */

class ChangleeWebApp {
    constructor() {
        this.apiBase = 'http://localhost:3001/api';
        this.currentMode = 'chat';
        this.isConnected = false;
        this.isTyping = false;
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.checkSystemStatus();
        this.setupAutoResize();
    }

    setupEventListeners() {
        // 模式切换
        document.querySelectorAll('.mode-card').forEach(card => {
            card.addEventListener('click', () => {
                const mode = card.dataset.mode;
                this.switchMode(mode);
            });
        });

        // 智能问答
        const sendButton = document.getElementById('send-button');
        const messageInput = document.getElementById('message-input');
        
        sendButton.addEventListener('click', () => this.sendMessage());
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // 快捷问题
        document.querySelectorAll('.quick-action').forEach(action => {
            action.addEventListener('click', () => {
                const question = action.dataset.question;
                const search = action.dataset.search;
                
                if (question) {
                    this.sendMessage(question);
                } else if (search) {
                    this.searchDocuments(search);
                }
            });
        });

        // 文档上传
        const uploadArea = document.getElementById('upload-area');
        const fileInput = document.getElementById('file-input');

        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        uploadArea.addEventListener('drop', this.handleDrop.bind(this));
        fileInput.addEventListener('change', this.handleFileSelect.bind(this));

        // 文献检索
        const searchButton = document.getElementById('search-button');
        const searchInput = document.getElementById('search-input');
        
        searchButton.addEventListener('click', () => this.searchDocuments());
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.searchDocuments();
            }
        });
    }

    switchMode(mode) {
        // 更新模式卡片状态
        document.querySelectorAll('.mode-card').forEach(card => {
            card.classList.remove('active');
        });
        document.querySelector(`[data-mode="${mode}"]`).classList.add('active');

        // 切换内容区域
        document.querySelectorAll('.mode-content').forEach(content => {
            content.classList.add('hidden');
        });
        document.getElementById(`${mode}-mode`).classList.remove('hidden');

        this.currentMode = mode;
    }

    async checkSystemStatus() {
        try {
            const response = await fetch(`${this.apiBase}/rag/status`);
            const data = await response.json();
            
            if (data.success && data.data.isConnected) {
                this.updateStatus(true, 'RAG系统已连接');
                this.isConnected = true;
            } else {
                this.updateStatus(false, 'RAG系统离线');
            }
        } catch (error) {
            console.error('状态检查失败:', error);
            this.updateStatus(false, '系统连接失败');
        }
    }

    updateStatus(connected, message) {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        
        statusDot.classList.toggle('connected', connected);
        statusText.textContent = message;
        this.isConnected = connected;
    }

    async sendMessage(message = null) {
        const input = document.getElementById('message-input');
        const text = message || input.value.trim();
        
        if (!text) return;

        // 清空输入框
        if (!message) input.value = '';

        // 添加用户消息
        this.addMessage(text, 'user');

        // 显示输入状态
        this.showTypingIndicator();

        try {
            const response = await fetch(`${this.apiBase}/rag/ask`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question: text,
                    context: {
                        type: 'web_chat',
                        timestamp: new Date().toISOString()
                    }
                })
            });

            const data = await response.json();
            
            if (data.success && data.data.answer) {
                this.addMessage(data.data.answer, 'bot', data.data.sources);
            } else {
                this.addMessage('抱歉，我现在无法回答这个问题。请稍后再试。', 'bot');
            }
        } catch (error) {
            console.error('发送消息失败:', error);
            this.addMessage('网络连接出现问题，请检查系统状态。', 'bot');
        } finally {
            this.hideTypingIndicator();
        }
    }

    async searchDocuments(query = null) {
        const input = document.getElementById('search-input');
        const text = query || input.value.trim();
        
        if (!text) return;

        // 清空输入框
        if (!query) input.value = '';

        // 添加用户消息到搜索区域
        this.addMessage(text, 'user', null, 'search-messages-area');

        // 显示搜索状态
        this.showTypingIndicator('search-messages-area');

        try {
            const response = await fetch(`${this.apiBase}/rag/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: text,
                    options: {
                        documentType: '全部',
                        scope: '全文',
                        detail: '详细'
                    }
                })
            });

            const data = await response.json();
            
            if (data.success && data.data.answer) {
                this.addMessage(data.data.answer, 'bot', data.data.sources, 'search-messages-area');
            } else {
                this.addMessage('在已上传的文档中没有找到相关信息。', 'bot', null, 'search-messages-area');
            }
        } catch (error) {
            console.error('文献检索失败:', error);
            this.addMessage('检索过程中出现错误，请稍后再试。', 'bot', null, 'search-messages-area');
        } finally {
            this.hideTypingIndicator('search-messages-area');
        }
    }

    addMessage(text, type, sources = null, containerId = 'messages-area') {
        const messagesArea = document.getElementById(containerId);
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = type === 'user' ? '👤' : (containerId.includes('search') ? '🔍' : '🐱');

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        
        // 处理换行
        const formattedText = text.replace(/\n/g, '<br>');
        bubble.innerHTML = formattedText;

        // 添加来源信息
        if (sources && sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.style.cssText = 'margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.2); font-size: 0.85rem; opacity: 0.8;';
            sourcesDiv.innerHTML = '<strong>📚 参考资料:</strong><br>' + 
                sources.map(source => `• ${source.title || source.filename || '文档'}`).join('<br>');
            bubble.appendChild(sourcesDiv);
        }

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(bubble);
        messagesArea.appendChild(messageDiv);

        // 滚动到底部
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }

    showTypingIndicator(containerId = 'messages-area') {
        const messagesArea = document.getElementById(containerId);
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = `typing-${containerId}`;
        
        typingDiv.innerHTML = `
            <div class="typing-dots">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
            <span>长离正在思考...</span>
        `;
        
        messagesArea.appendChild(typingDiv);
        messagesArea.scrollTop = messagesArea.scrollHeight;
        this.isTyping = true;
    }

    hideTypingIndicator(containerId = 'messages-area') {
        const typingIndicator = document.getElementById(`typing-${containerId}`);
        if (typingIndicator) {
            typingIndicator.remove();
        }
        this.isTyping = false;
    }

    handleDragOver(e) {
        e.preventDefault();
        document.getElementById('upload-area').classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        document.getElementById('upload-area').classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        document.getElementById('upload-area').classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        this.uploadFiles(files);
    }

    handleFileSelect(e) {
        const files = e.target.files;
        this.uploadFiles(files);
    }

    async uploadFiles(files) {
        if (!files || files.length === 0) return;

        const uploadArea = document.getElementById('upload-area');
        const resultsDiv = document.getElementById('analysis-results');
        const contentDiv = document.getElementById('analysis-content');

        // 显示上传状态
        uploadArea.classList.add('loading');
        uploadArea.innerHTML = `
            <div class="upload-icon">⏳</div>
            <div style="font-size: 1.2rem; margin-bottom: 10px;">正在上传和分析文档...</div>
            <div style="font-size: 0.9rem; opacity: 0.8;">请稍候，长离正在努力分析中</div>
        `;

        try {
            for (const file of files) {
                // 验证文件
                if (!this.validateFile(file)) continue;

                // 上传文件
                const formData = new FormData();
                formData.append('file', file);
                formData.append('metadata', JSON.stringify({
                    category: 'web_upload',
                    uploadTime: new Date().toISOString()
                }));

                const uploadResponse = await fetch(`${this.apiBase}/rag/upload`, {
                    method: 'POST',
                    body: formData
                });

                const uploadResult = await uploadResponse.json();
                
                if (uploadResult.success) {
                    // 分析文档
                    const analysisResponse = await fetch(`${this.apiBase}/rag/analyze-document`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            documentId: uploadResult.data.documentId,
                            difficulty: 2
                        })
                    });

                    const analysisResult = await analysisResponse.json();
                    
                    if (analysisResult.success) {
                        this.displayAnalysisResults(file.name, analysisResult.data);
                        resultsDiv.classList.remove('hidden');
                    }
                }
            }
        } catch (error) {
            console.error('文件处理失败:', error);
            contentDiv.innerHTML = `
                <div style="color: #ff6b6b; text-align: center; padding: 20px;">
                    ❌ 文件处理失败: ${error.message}
                </div>
            `;
            resultsDiv.classList.remove('hidden');
        } finally {
            // 恢复上传区域
            uploadArea.classList.remove('loading');
            uploadArea.innerHTML = `
                <div class="upload-icon">📤</div>
                <div style="font-size: 1.2rem; margin-bottom: 10px;">点击或拖拽文件到这里上传</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">支持 PDF, DOC, DOCX, TXT 格式，最大 50MB</div>
            `;
        }
    }

    validateFile(file) {
        const allowedTypes = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain'
        ];

        if (!allowedTypes.includes(file.type)) {
            alert(`不支持的文件类型: ${file.name}`);
            return false;
        }

        if (file.size > 50 * 1024 * 1024) {
            alert(`文件过大: ${file.name} (最大50MB)`);
            return false;
        }

        return true;
    }

    displayAnalysisResults(filename, data) {
        const contentDiv = document.getElementById('analysis-content');
        
        let html = `
            <div style="background: rgba(255,255,255,0.1); border-radius: 15px; padding: 20px; margin-bottom: 20px;">
                <h4>📄 ${filename}</h4>
                <div style="margin-top: 15px;">
        `;

        if (data.words && data.words.length > 0) {
            html += `
                <h5>🎯 提取的单词 (${data.words.length}个):</h5>
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; margin-top: 10px;">
            `;
            
            data.words.forEach(word => {
                html += `
                    <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px; text-align: center;">
                        <div style="font-weight: bold; margin-bottom: 5px;">${word.word}</div>
                        <div style="font-size: 0.8rem; opacity: 0.8;">${word.phonetic || ''}</div>
                        <div style="font-size: 0.9rem; margin-top: 5px;">${word.definition}</div>
                    </div>
                `;
            });
            
            html += '</div>';
        }

        if (data.rawResponse) {
            html += `
                <h5>🤖 长离的分析:</h5>
                <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-top: 10px; white-space: pre-wrap;">
                    ${data.rawResponse}
                </div>
            `;
        }

        html += `
                </div>
                <div style="margin-top: 15px; text-align: center;">
                    <button onclick="app.askAboutDocument('${filename}')" style="background: linear-gradient(135deg, #4ecdc4, #44a08d); border: none; border-radius: 20px; padding: 10px 20px; color: white; cursor: pointer;">
                        💬 向长离提问关于这个文档
                    </button>
                </div>
            </div>
        `;

        contentDiv.innerHTML = html;
    }

    askAboutDocument(filename) {
        // 切换到智能问答模式
        this.switchMode('chat');
        
        // 预填充问题
        const input = document.getElementById('message-input');
        input.value = `请详细分析文档《${filename}》的内容，包括主要知识点和学习建议。`;
        input.focus();
    }

    setupAutoResize() {
        // 自动调整文本框高度
        const inputs = document.querySelectorAll('.message-input');
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                input.style.height = 'auto';
                input.style.height = Math.min(input.scrollHeight, 120) + 'px';
            });
        });
    }

    // 定期检查系统状态
    startStatusCheck() {
        setInterval(() => {
            this.checkSystemStatus();
        }, 30000); // 每30秒检查一次
    }
}

// 初始化应用
const app = new ChangleeWebApp();

// 启动状态检查
app.startStatusCheck();

// 全局错误处理
window.addEventListener('error', (e) => {
    console.error('应用错误:', e.error);
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('未处理的Promise拒绝:', e.reason);
});