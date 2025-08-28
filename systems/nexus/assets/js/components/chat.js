/**
 * NEXUS 聊天组件
 * 负责RAG聊天功能的管理
 */

class ChatComponent {
    constructor() {
        this.STORAGE_KEY = 'nexus_rag_chat_history';
        this.MAX_STORED_MESSAGES = 100;
        this.currentTaskName = 'nexus_chat';
        this.isConnected = false;
        this.apiUrl = '';
        
        this.init();
    }

    /**
     * 初始化聊天组件
     */
    init() {
        this.initElements();
        this.initEventListeners();
        this.loadChatHistory();
        this.checkConnection();
    }

    /**
     * 初始化DOM元素
     */
    initElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendButton = document.getElementById('sendButton');
        this.clearButton = document.getElementById('clearChatBtn');
        this.connectionStatus = document.getElementById('connectionStatus');
    }

    /**
     * 初始化事件监听
     */
    initEventListeners() {
        if (this.sendButton) {
            this.sendButton.addEventListener('click', () => this.sendMessage());
        }

        if (this.chatInput) {
            this.chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

            this.chatInput.addEventListener('input', () => {
                this.adjustTextareaHeight();
            });
        }

        if (this.clearButton) {
            this.clearButton.addEventListener('click', () => this.clearChat());
        }
    }

    /**
     * 发送消息
     */
    async sendMessage() {
        const message = this.chatInput?.value?.trim();
        if (!message) return;

        // 添加用户消息到界面
        this.addMessage('user', message);
        
        // 清空输入框
        this.chatInput.value = '';
        this.adjustTextareaHeight();

        // 显示加载状态
        const loadingId = this.addMessage('assistant', '正在思考中...', true);

        try {
            // 发送到RAG系统
            const response = await this.sendToRAG(message);
            
            // 移除加载消息，添加实际回复
            this.removeMessage(loadingId);
            this.addMessage('assistant', response);
            
        } catch (error) {
            console.error('发送消息失败:', error);
            this.removeMessage(loadingId);
            this.addMessage('assistant', '抱歉，发生了错误。请检查连接状态。');
        }

        // 保存聊天记录
        this.saveChatHistory();
    }

    /**
     * 添加消息到聊天界面
     */
    addMessage(role, content, isLoading = false) {
        if (!this.chatMessages) return null;

        const messageId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const avatar = role === 'assistant' ? '🧠' : '👤';
        
        const messageElement = document.createElement('div');
        messageElement.className = `message ${role}-message`;
        messageElement.id = messageId;
        
        messageElement.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content ${isLoading ? 'loading' : ''}">${content}</div>
        `;

        this.chatMessages.appendChild(messageElement);
        this.scrollToBottom();

        return messageId;
    }

    /**
     * 移除消息
     */
    removeMessage(messageId) {
        const element = document.getElementById(messageId);
        if (element) {
            element.remove();
        }
    }

    /**
     * 清空聊天记录
     */
    clearChat() {
        if (this.chatMessages) {
            this.chatMessages.innerHTML = '';
        }
        localStorage.removeItem(this.STORAGE_KEY);
        console.log('🗑️ 聊天记录已清空');
    }

    /**
     * 保存聊天记录
     */
    saveChatHistory() {
        try {
            const messages = [];
            const messageElements = this.chatMessages?.querySelectorAll('.message') || [];
            
            messageElements.forEach(element => {
                const avatar = element.querySelector('.message-avatar')?.textContent || '👤';
                const content = element.querySelector('.message-content')?.innerHTML || '';
                const role = avatar === '🧠' ? 'assistant' : 'user';
                
                if (content.trim() && !element.querySelector('.loading')) {
                    messages.push({
                        role: role,
                        content: content,
                        avatar: avatar,
                        timestamp: Date.now()
                    });
                }
            });
            
            // 只保留最新的消息
            const recentMessages = messages.slice(-this.MAX_STORED_MESSAGES);
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(recentMessages));
            
            console.log(`💾 已保存 ${recentMessages.length} 条聊天记录`);
        } catch (error) {
            console.error('保存聊天记录失败:', error);
        }
    }

    /**
     * 加载聊天记录
     */
    loadChatHistory() {
        try {
            const stored = localStorage.getItem(this.STORAGE_KEY);
            if (!stored) return false;
            
            const messages = JSON.parse(stored);
            if (!Array.isArray(messages) || messages.length === 0) return false;
            
            console.log(`📚 加载 ${messages.length} 条聊天记录`);
            
            messages.forEach(msg => {
                this.addMessage(msg.role, msg.content);
            });
            
            return true;
        } catch (error) {
            console.error('加载聊天记录失败:', error);
            return false;
        }
    }

    /**
     * 发送消息到RAG系统
     */
    async sendToRAG(message) {
        const apiUrl = this.getApiUrl();
        if (!apiUrl) {
            throw new Error('API URL未配置');
        }

        const response = await fetch(`${apiUrl}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                task_name: this.currentTaskName,
                stream: false
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        return data.response || '抱歉，没有收到有效回复。';
    }

    /**
     * 获取API URL
     */
    getApiUrl() {
        // 优先使用配置的URL
        if (this.apiUrl) return this.apiUrl;
        
        // 从meta标签获取
        const metaUrl = document.querySelector('meta[name="api-url"]')?.getAttribute('content');
        if (metaUrl) return metaUrl;
        
        // 默认本地URL
        return 'http://localhost:8501';
    }

    /**
     * 设置API URL
     */
    setApiUrl(url) {
        this.apiUrl = url;
        this.checkConnection();
    }

    /**
     * 检查连接状态
     */
    async checkConnection() {
        try {
            const apiUrl = this.getApiUrl();
            const response = await fetch(`${apiUrl}/health`, {
                method: 'GET',
                timeout: 5000
            });
            
            this.isConnected = response.ok;
            this.updateConnectionStatus(this.isConnected);
            
        } catch (error) {
            this.isConnected = false;
            this.updateConnectionStatus(false, error.message);
        }
    }

    /**
     * 更新连接状态显示
     */
    updateConnectionStatus(isConnected, errorMessage = '') {
        const statusElement = document.getElementById('statusIndicator');
        if (!statusElement) return;

        if (isConnected) {
            statusElement.innerHTML = `
                <span class="status-dot" style="color: var(--status-online)">●</span>
                <span class="status-text">RAG系统已连接</span>
            `;
        } else {
            statusElement.innerHTML = `
                <span class="status-dot" style="color: var(--status-offline)">●</span>
                <span class="status-text">RAG系统未连接</span>
            `;
            
            if (errorMessage) {
                const detailsElement = document.getElementById('statusDetails');
                if (detailsElement) {
                    detailsElement.textContent = errorMessage;
                }
            }
        }
    }

    /**
     * 调整文本框高度
     */
    adjustTextareaHeight() {
        if (!this.chatInput) return;
        
        this.chatInput.style.height = 'auto';
        this.chatInput.style.height = Math.min(this.chatInput.scrollHeight, 120) + 'px';
    }

    /**
     * 滚动到底部
     */
    scrollToBottom() {
        if (this.chatMessages) {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }
    }
}

// 创建全局聊天组件实例
window.chatComponent = new ChatComponent();