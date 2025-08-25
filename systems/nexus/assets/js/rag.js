// NEXUS Research Workstation - RAG System Module
// RAG系统相关的JavaScript模块

class RAGManager {
    constructor() {
        this.isActive = false;
        this.messages = [];
        this.isTyping = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.initializeMessages();
    }
    
    setupEventListeners() {
        // RAG启动按钮
        const ragButtons = document.querySelectorAll('[onclick*="showRAGChat"]');
        ragButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.showRAGChat();
            });
        });
        
        // 发送消息按钮
        const sendBtn = document.getElementById('sendMessage');
        if (sendBtn) {
            sendBtn.addEventListener('click', () => {
                this.sendMessage();
            });
        }
        
        // 输入框回车发送
        const inputField = document.getElementById('messageInput');
        if (inputField) {
            inputField.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
            
            // 输入状态监听
            inputField.addEventListener('input', () => {
                this.updateSendButton();
            });
        }
    }
    
    initializeMessages() {
        // 初始化默认消息
        this.messages = [
            {
                id: 1,
                type: 'assistant',
                content: '根据文档内容，我找到了相关信息...',
                timestamp: new Date()
            },
            {
                id: 2,
                type: 'user', 
                content: '这是一个很好的问题，让我为你详细解答...',
                timestamp: new Date()
            },
            {
                id: 3,
                type: 'assistant',
                content: '根据文档内容，我找到了相关信息...',
                timestamp: new Date()
            },
            {
                id: 4,
                type: 'assistant',
                content: '基于问题检索的结果，我可以告诉你...',
                timestamp: new Date()
            }
        ];
        
        this.renderMessages();
    }
    
    showRAGChat() {
        // 隐藏其他内容
        document.getElementById('dashboard-content').style.display = 'none';
        document.getElementById('settings-page').style.display = 'none';
        document.getElementById('empty-page').style.display = 'none';
        
        // 显示RAG聊天界面
        const ragChat = document.getElementById('rag-chat');
        if (ragChat) {
            ragChat.style.display = 'flex';
            this.isActive = true;
        }
        
        // 更新页面标题
        const titleElement = document.querySelector('.page-title');
        if (titleElement) {
            const currentLang = document.documentElement.lang || 'zh';
            const titles = {
                'zh': 'RAG System',
                'en': 'RAG System', 
                'ja': 'RAGシステム'
            };
            const langKey = currentLang.startsWith('zh') ? 'zh' : 
                           currentLang.startsWith('ja') ? 'ja' : 'en';
            titleElement.textContent = titles[langKey];
        }
        
        // 更新导航状态
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const ragNav = document.querySelector('[onclick*="rag-system"]');
        if (ragNav) {
            ragNav.classList.add('active');
        }
        
        // 滚动到底部
        this.scrollToBottom();
        
        // 聚焦输入框
        const inputField = document.getElementById('messageInput');
        if (inputField) {
            setTimeout(() => inputField.focus(), 100);
        }
    }
    
    sendMessage() {
        const inputField = document.getElementById('messageInput');
        if (!inputField) return;
        
        const message = inputField.value.trim();
        if (!message || this.isTyping) return;
        
        // 添加用户消息
        this.addMessage('user', message);
        
        // 清空输入框
        inputField.value = '';
        this.updateSendButton();
        
        // 模拟AI回复
        this.simulateAIResponse();
    }
    
    addMessage(type, content) {
        const message = {
            id: Date.now(),
            type: type,
            content: content,
            timestamp: new Date()
        };
        
        this.messages.push(message);
        this.renderMessage(message);
        this.scrollToBottom();
    }
    
    renderMessages() {
        const container = document.getElementById('chatMessages');
        if (!container) return;
        
        container.innerHTML = '';
        this.messages.forEach(message => {
            this.renderMessage(message);
        });
    }
    
    renderMessage(message) {
        const container = document.getElementById('chatMessages');
        if (!container) return;
        
        const messageElement = document.createElement('div');
        messageElement.className = 'message';
        messageElement.innerHTML = `
            <div class="message-avatar">${message.type === 'user' ? '👤' : '🧠'}</div>
            <div class="message-content">
                <div class="message-text">${this.escapeHtml(message.content)}</div>
            </div>
        `;
        
        container.appendChild(messageElement);
    }
    
    simulateAIResponse() {
        this.isTyping = true;
        this.showTypingIndicator();
        
        // 模拟响应延迟
        setTimeout(() => {
            this.hideTypingIndicator();
            
            const responses = [
                '根据文档内容，我找到了相关信息...',
                '基于您的问题，我可以提供以下解答...',
                '让我为您分析一下这个问题...',
                '根据检索到的资料，答案如下...',
                '这是一个很好的问题，让我详细回答...'
            ];
            
            const randomResponse = responses[Math.floor(Math.random() * responses.length)];
            this.addMessage('assistant', randomResponse);
            
            this.isTyping = false;
        }, 1000 + Math.random() * 2000);
    }
    
    showTypingIndicator() {
        const container = document.getElementById('chatMessages');
        if (!container) return;
        
        const typingElement = document.createElement('div');
        typingElement.className = 'message typing-indicator';
        typingElement.id = 'typingIndicator';
        typingElement.innerHTML = `
            <div class="message-avatar">🧠</div>
            <div class="message-content">
                <div class="message-text">
                    <div class="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `;
        
        container.appendChild(typingElement);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    updateSendButton() {
        const inputField = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendMessage');
        
        if (inputField && sendBtn) {
            const hasText = inputField.value.trim().length > 0;
            sendBtn.disabled = !hasText || this.isTyping;
        }
    }
    
    scrollToBottom() {
        const container = document.getElementById('chatMessages');
        if (container) {
            setTimeout(() => {
                container.scrollTop = container.scrollHeight;
            }, 100);
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // 清空聊天记录
    clearChat() {
        this.messages = [];
        this.renderMessages();
    }
    
    // 导出聊天记录
    exportChat() {
        const chatData = {
            timestamp: new Date().toISOString(),
            messages: this.messages
        };
        
        const blob = new Blob([JSON.stringify(chatData, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `rag-chat-${new Date().toISOString().slice(0, 10)}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    // 获取聊天状态
    getStatus() {
        return {
            isActive: this.isActive,
            messageCount: this.messages.length,
            isTyping: this.isTyping
        };
    }
}

// 导出模块
window.RAGManager = RAGManager;