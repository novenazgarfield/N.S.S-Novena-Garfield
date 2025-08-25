// NEXUS Research Workstation - Main JavaScript
// 优化后的模块化JS文件 - 从nexus-dashboard-restored.html提取

class NexusApp {
    constructor() {
        this.currentPage = 'dashboard';
        this.currentTheme = 'dark';
        this.currentLanguage = 'zh';
        this.isRAGActive = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupViewportHeight();
        this.setupTheme();
        this.setupLanguage();
        this.setupNavigation();
        this.setupRAGSystem();
        
        // 页面加载完成后的初始化
        document.addEventListener('DOMContentLoaded', () => {
            this.showPage('dashboard');
            this.updateActiveNav('dashboard');
        });
    }
    
    setupEventListeners() {
        // 导航按钮事件
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const page = e.currentTarget.dataset.page;
                if (page) {
                    this.showPage(page);
                    this.updateActiveNav(page);
                }
            });
        });
        
        // 主题切换
        const themeBtn = document.getElementById('themeToggle');
        if (themeBtn) {
            themeBtn.addEventListener('click', () => this.toggleTheme());
        }
        
        // 语言切换
        const langBtn = document.getElementById('languageToggle');
        if (langBtn) {
            langBtn.addEventListener('click', () => this.toggleLanguage());
        }
        
        // 设置按钮
        const settingsBtn = document.getElementById('settingsBtn');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => {
                this.showPage('settings');
                this.updateActiveNav('settings');
            });
        }
        
        // RAG发送按钮
        const sendBtn = document.getElementById('ragSendBtn');
        const ragInput = document.getElementById('ragInput');
        
        if (sendBtn && ragInput) {
            sendBtn.addEventListener('click', () => this.sendRAGMessage());
            ragInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendRAGMessage();
                }
            });
        }
        
        // 返回按钮
        const backBtn = document.getElementById('backBtn');
        if (backBtn) {
            backBtn.addEventListener('click', () => {
                this.showPage('dashboard');
                this.updateActiveNav('dashboard');
            });
        }
        
        // 窗口大小变化时重新计算视窗高度
        window.addEventListener('resize', () => {
            this.setupViewportHeight();
        });
        
        // 页面可见性变化时的处理
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.setupViewportHeight();
            }
        });
    }
    
    setupViewportHeight() {
        // 解决移动端视窗高度问题
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--real-vh', `${vh}px`);
        document.documentElement.style.setProperty('--app-height', `${window.innerHeight}px`);
    }
    
    setupTheme() {
        // 从localStorage读取主题设置
        const savedTheme = localStorage.getItem('nexus-theme') || 'dark';
        this.currentTheme = savedTheme;
        document.documentElement.setAttribute('data-theme', savedTheme);
        
        // 更新主题按钮图标
        this.updateThemeButton();
    }
    
    setupLanguage() {
        // 从localStorage读取语言设置
        const savedLanguage = localStorage.getItem('nexus-language') || 'zh';
        this.currentLanguage = savedLanguage;
        document.documentElement.setAttribute('lang', savedLanguage === 'zh' ? 'zh-CN' : 'en');
        
        // 更新语言按钮
        this.updateLanguageButton();
        
        // 应用翻译
        this.applyTranslations();
    }
    
    setupNavigation() {
        // 设置导航状态指示器
        this.updateSystemStatus();
        
        // 定期更新系统状态
        setInterval(() => {
            this.updateSystemStatus();
        }, 30000); // 30秒更新一次
    }
    
    setupRAGSystem() {
        // RAG系统初始化
        this.ragMessages = [];
        this.ragContext = '';
    }
    
    showPage(pageId) {
        // 隐藏所有页面
        document.querySelectorAll('.page-content').forEach(page => {
            page.style.display = 'none';
            page.classList.remove('fade-in');
        });
        
        // 显示目标页面
        const targetPage = document.getElementById(`${pageId}Page`);
        if (targetPage) {
            targetPage.style.display = 'flex';
            targetPage.classList.add('fade-in');
        }
        
        // 更新页面标题
        const pageTitle = document.getElementById('pageTitle');
        if (pageTitle) {
            pageTitle.textContent = this.getPageTitle(pageId);
        }
        
        this.currentPage = pageId;
        
        // 特殊页面处理
        if (pageId === 'rag') {
            this.isRAGActive = true;
            this.focusRAGInput();
        } else {
            this.isRAGActive = false;
        }
    }
    
    updateActiveNav(pageId) {
        // 更新导航按钮状态
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const activeNav = document.querySelector(`[data-page="${pageId}"]`);
        if (activeNav) {
            activeNav.classList.add('active');
        }
    }
    
    getPageTitle(pageId) {
        const titles = {
            'zh': {
                'dashboard': 'Dashboard',
                'rag': 'RAG系统',
                'changlee': 'Changlee',
                'nexus': 'NEXUS',
                'bovine': 'Bovine Insight',
                'chronicle': 'Chronicle',
                'genome': 'Genome Jigsaw',
                'molecular': 'Molecular Simulation',
                'settings': '设置'
            },
            'en': {
                'dashboard': 'Dashboard',
                'rag': 'RAG System',
                'changlee': 'Changlee',
                'nexus': 'NEXUS',
                'bovine': 'Bovine Insight',
                'chronicle': 'Chronicle',
                'genome': 'Genome Jigsaw',
                'molecular': 'Molecular Simulation',
                'settings': 'Settings'
            }
        };
        
        return titles[this.currentLanguage][pageId] || pageId;
    }
    
    toggleTheme() {
        this.currentTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        localStorage.setItem('nexus-theme', this.currentTheme);
        
        this.updateThemeButton();
        
        // 添加切换动画
        document.body.style.transition = 'background-color 0.3s, color 0.3s';
        setTimeout(() => {
            document.body.style.transition = '';
        }, 300);
    }
    
    updateThemeButton() {
        const themeBtn = document.getElementById('themeToggle');
        if (themeBtn) {
            themeBtn.textContent = this.currentTheme === 'dark' ? '☀️' : '🌙';
            themeBtn.title = this.currentTheme === 'dark' ? '切换到亮色主题' : '切换到暗色主题';
        }
    }
    
    toggleLanguage() {
        this.currentLanguage = this.currentLanguage === 'zh' ? 'en' : 'zh';
        document.documentElement.setAttribute('lang', this.currentLanguage === 'zh' ? 'zh-CN' : 'en');
        localStorage.setItem('nexus-language', this.currentLanguage);
        
        this.updateLanguageButton();
        this.applyTranslations();
    }
    
    updateLanguageButton() {
        const langBtn = document.getElementById('languageToggle');
        if (langBtn) {
            const flag = langBtn.querySelector('.language-flag');
            const text = langBtn.querySelector('.language-text');
            
            if (flag && text) {
                if (this.currentLanguage === 'zh') {
                    flag.textContent = '🇨🇳';
                    text.textContent = '简体中文';
                } else {
                    flag.textContent = '🇺🇸';
                    text.textContent = 'English';
                }
            }
        }
    }
    
    applyTranslations() {
        // 这里可以实现完整的国际化翻译
        // 目前保持简单实现
        const elements = document.querySelectorAll('[data-i18n]');
        elements.forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.getTranslation(key);
            if (translation) {
                element.textContent = translation;
            }
        });
    }
    
    getTranslation(key) {
        const translations = {
            'zh': {
                'dashboard': 'Dashboard',
                'rag_system': 'RAG系统',
                'settings': '设置',
                'under_development': '功能开发中',
                'coming_soon': '该功能正在开发中，敬请期待...'
            },
            'en': {
                'dashboard': 'Dashboard',
                'rag_system': 'RAG System',
                'settings': 'Settings',
                'under_development': 'Under Development',
                'coming_soon': 'This feature is under development, stay tuned...'
            }
        };
        
        return translations[this.currentLanguage]?.[key];
    }
    
    updateSystemStatus() {
        // 模拟系统状态更新
        const statusElements = document.querySelectorAll('.nav-status');
        statusElements.forEach((status, index) => {
            // 随机设置在线/离线状态（实际应用中应该是真实的状态检查）
            const isOnline = Math.random() > 0.3; // 70%概率在线
            status.classList.toggle('online', isOnline);
        });
    }
    
    // RAG系统相关方法
    sendRAGMessage() {
        const input = document.getElementById('ragInput');
        const sendBtn = document.getElementById('ragSendBtn');
        
        if (!input || !sendBtn) return;
        
        const message = input.value.trim();
        if (!message) return;
        
        // 禁用输入和按钮
        input.disabled = true;
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<div class="loading"></div>';
        
        // 添加用户消息到聊天
        this.addRAGMessage('user', message);
        
        // 清空输入框
        input.value = '';
        
        // 模拟AI响应（实际应用中应该调用真实的API）
        setTimeout(() => {
            const response = this.generateRAGResponse(message);
            this.addRAGMessage('assistant', response);
            
            // 重新启用输入和按钮
            input.disabled = false;
            sendBtn.disabled = false;
            sendBtn.textContent = '发送';
            
            // 聚焦输入框
            input.focus();
        }, 1500);
    }
    
    addRAGMessage(role, content) {
        const chatContainer = document.getElementById('ragChat');
        if (!chatContainer) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message fade-in`;
        
        if (role === 'user') {
            messageDiv.innerHTML = `
                <div class="message-content user-content">
                    <div class="message-text">${this.escapeHtml(content)}</div>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="message-content assistant-content">
                    <div class="message-avatar">🤖</div>
                    <div class="message-text">${this.escapeHtml(content)}</div>
                </div>
            `;
        }
        
        chatContainer.appendChild(messageDiv);
        
        // 滚动到底部
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        // 保存消息到历史
        this.ragMessages.push({ role, content, timestamp: Date.now() });
    }
    
    generateRAGResponse(message) {
        // 简单的模拟响应（实际应用中应该调用真实的RAG API）
        const responses = [
            '我理解您的问题。基于我的知识库，我可以为您提供以下信息...',
            '这是一个很好的问题。让我为您分析一下相关的文档内容...',
            '根据我检索到的相关资料，我可以给您以下建议...',
            '我已经搜索了相关的文档，以下是我找到的信息...'
        ];
        
        return responses[Math.floor(Math.random() * responses.length)];
    }
    
    focusRAGInput() {
        setTimeout(() => {
            const input = document.getElementById('ragInput');
            if (input) {
                input.focus();
            }
        }, 100);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // 工具方法
    showNotification(message, type = 'info') {
        // 简单的通知实现
        const notification = document.createElement('div');
        notification.className = `notification notification-${type} fade-in`;
        notification.textContent = message;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            background: var(--accent-blue);
            color: white;
            border-radius: 8px;
            box-shadow: var(--shadow);
            z-index: 1000;
            max-width: 300px;
        `;
        
        if (type === 'error') {
            notification.style.background = 'var(--accent-red)';
        } else if (type === 'success') {
            notification.style.background = 'var(--accent-green)';
        }
        
        document.body.appendChild(notification);
        
        // 3秒后自动移除
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
    
    // 性能监控
    measurePerformance(name, fn) {
        const start = performance.now();
        const result = fn();
        const end = performance.now();
        console.log(`${name} took ${end - start} milliseconds`);
        return result;
    }
    
    // 错误处理
    handleError(error, context = '') {
        console.error(`NEXUS Error ${context}:`, error);
        this.showNotification(`发生错误: ${error.message}`, 'error');
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    try {
        window.nexusApp = new NexusApp();
        console.log('NEXUS Application initialized successfully');
    } catch (error) {
        console.error('Failed to initialize NEXUS Application:', error);
    }
});

// 全局错误处理
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
});

// 导出给其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NexusApp;
}