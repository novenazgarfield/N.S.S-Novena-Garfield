// NEXUS Research Workstation - Themes Module
// 主题和语言相关的JavaScript模块

class ThemeManager {
    constructor() {
        this.currentTheme = 'dark';
        this.currentLanguage = 'zh';
        this.availableThemes = ['dark', 'light', 'high-contrast', 'blue', 'green', 'purple'];
        this.availableLanguages = ['zh', 'en', 'ja'];
        
        this.translations = {
            'zh': {
                // 导航
                'Dashboard': '仪表板',
                'RAG System': 'RAG System',
                'Changlee': 'Changlee',
                'NEXUS': 'NEXUS',
                'Bovine Insight': 'Bovine Insight',
                'Chronicle': 'Chronicle',
                'Genome Jigsaw': 'Genome Jigsaw',
                'Molecular Simulation': 'Molecular Simulation',
                'Settings': '设置',
                
                // 语言选择
                '简体中文': '简体中文',
                'English': 'English',
                '日本語': '日本語',
                
                // 按钮
                'Launch NEXUS': '🚀 启动 NEXUS',
                'Documentation': '📁 文档',
                'Launch RAG': '🧠 启动 RAG',
                'Document Library': '📚 文档库',
                'Management Platform': '🚀 管理平台',
                'System Status': '📋 系统状态',
                
                // RAG界面
                'Send': '发送',
                'Type your question...': '输入你的问题...'
            },
            'en': {
                // 导航
                'Dashboard': 'Dashboard',
                'RAG System': 'RAG System',
                'Changlee': 'Changlee',
                'NEXUS': 'NEXUS',
                'Bovine Insight': 'Bovine Insight',
                'Chronicle': 'Chronicle',
                'Genome Jigsaw': 'Genome Jigsaw',
                'Molecular Simulation': 'Molecular Simulation',
                'Settings': 'Settings',
                
                // 语言选择
                '简体中文': '简体中文',
                'English': 'English',
                '日本語': '日本語',
                
                // 按钮
                'Launch NEXUS': '🚀 Launch NEXUS',
                'Documentation': '📁 Documentation',
                'Launch RAG': '🧠 Launch RAG',
                'Document Library': '📚 Document Library',
                'Management Platform': '🚀 Management Platform',
                'System Status': '📋 System Status',
                
                // RAG界面
                'Send': 'Send',
                'Type your question...': 'Type your question...'
            },
            'ja': {
                // 导航
                'Dashboard': 'ダッシュボード',
                'RAG System': 'RAGシステム',
                'Changlee': 'チャンリー',
                'NEXUS': 'NEXUS',
                'Bovine Insight': '牛認識システム',
                'Chronicle': 'クロニクル',
                'Genome Jigsaw': 'ゲノムジグソー',
                'Molecular Simulation': '分子シミュレーション',
                'Settings': '設定',
                
                // 语言选择
                '简体中文': '简体中文',
                'English': 'English',
                '日本語': '日本語',
                
                // 按钮
                'Launch NEXUS': '🚀 NEXUS起動',
                'Documentation': '📁 ドキュメント',
                'Launch RAG': '🧠 RAG起動',
                'Document Library': '📚 ドキュメントライブラリ',
                'Management Platform': '🚀 管理プラットフォーム',
                'System Status': '📋 システムステータス',
                
                // RAG界面
                'Send': '送信',
                'Type your question...': '質問を入力してください...'
            }
        };
        
        this.init();
    }
    
    init() {
        this.loadSavedSettings();
        this.setupEventListeners();
        this.applyTheme();
        this.applyLanguage();
    }
    
    loadSavedSettings() {
        // 从localStorage加载保存的设置
        const savedTheme = localStorage.getItem('nexus-theme');
        const savedLanguage = localStorage.getItem('nexus-language');
        
        if (savedTheme && this.availableThemes.includes(savedTheme)) {
            this.currentTheme = savedTheme;
        }
        
        if (savedLanguage && this.availableLanguages.includes(savedLanguage)) {
            this.currentLanguage = savedLanguage;
        }
        
        // 检测系统偏好
        if (!savedTheme) {
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
                this.currentTheme = 'light';
            }
        }
        
        if (!savedLanguage) {
            const browserLang = navigator.language || navigator.userLanguage;
            if (browserLang.startsWith('ja')) {
                this.currentLanguage = 'ja';
            } else if (browserLang.startsWith('en')) {
                this.currentLanguage = 'en';
            }
        }
    }
    
    setupEventListeners() {
        // 主题切换按钮
        const themeBtn = document.getElementById('themeToggle');
        if (themeBtn) {
            themeBtn.addEventListener('click', () => {
                this.toggleTheme();
            });
        }
        
        // 语言选择按钮
        const langBtn = document.querySelector('.language-btn');
        if (langBtn) {
            langBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleLanguageDropdown();
            });
        }
        
        // 语言选项
        document.querySelectorAll('.language-option').forEach(option => {
            option.addEventListener('click', (e) => {
                const lang = e.currentTarget.dataset.lang;
                if (lang) {
                    this.setLanguage(lang);
                }
            });
        });
        
        // 点击外部关闭语言下拉菜单
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.language-selector')) {
                this.hideLanguageDropdown();
            }
        });
        
        // 监听系统主题变化
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (!localStorage.getItem('nexus-theme')) {
                    this.currentTheme = e.matches ? 'dark' : 'light';
                    this.applyTheme();
                }
            });
        }
    }
    
    toggleTheme() {
        // 在深色和浅色主题之间切换
        this.currentTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme();
        this.saveSettings();
    }
    
    setTheme(theme) {
        if (this.availableThemes.includes(theme)) {
            this.currentTheme = theme;
            this.applyTheme();
            this.saveSettings();
        }
    }
    
    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        
        // 更新主题切换按钮图标
        const themeBtn = document.getElementById('themeToggle');
        if (themeBtn) {
            themeBtn.textContent = this.currentTheme === 'dark' ? '🌙' : '☀️';
        }
        
        // 触发主题变化事件
        window.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { theme: this.currentTheme }
        }));
    }
    
    toggleLanguageDropdown() {
        const dropdown = document.querySelector('.language-dropdown');
        if (dropdown) {
            dropdown.classList.toggle('show');
        }
    }
    
    hideLanguageDropdown() {
        const dropdown = document.querySelector('.language-dropdown');
        if (dropdown) {
            dropdown.classList.remove('show');
        }
    }
    
    setLanguage(lang) {
        if (this.availableLanguages.includes(lang)) {
            this.currentLanguage = lang;
            this.applyLanguage();
            this.saveSettings();
            this.hideLanguageDropdown();
        }
    }
    
    applyLanguage() {
        // 设置HTML lang属性
        document.documentElement.lang = this.getFullLanguageCode(this.currentLanguage);
        
        // 更新语言按钮显示
        this.updateLanguageButton();
        
        // 翻译页面内容
        this.translatePage();
        
        // 触发语言变化事件
        window.dispatchEvent(new CustomEvent('languageChanged', {
            detail: { language: this.currentLanguage }
        }));
    }
    
    getFullLanguageCode(lang) {
        const codes = {
            'zh': 'zh-CN',
            'en': 'en-US',
            'ja': 'ja-JP'
        };
        return codes[lang] || 'zh-CN';
    }
    
    updateLanguageButton() {
        const langBtn = document.querySelector('.language-btn');
        if (langBtn) {
            const flags = {
                'zh': '🇨🇳',
                'en': '🇺🇸', 
                'ja': '🇯🇵'
            };
            
            const names = {
                'zh': '简体中文',
                'en': 'English',
                'ja': '日本語'
            };
            
            const flagSpan = langBtn.querySelector('span:first-child');
            const nameSpan = langBtn.querySelector('span:last-child');
            
            if (flagSpan) flagSpan.textContent = flags[this.currentLanguage];
            if (nameSpan) nameSpan.textContent = names[this.currentLanguage];
        }
    }
    
    translatePage() {
        const translations = this.translations[this.currentLanguage];
        if (!translations) return;
        
        // 翻译导航项
        document.querySelectorAll('.nav-item-text').forEach(element => {
            const key = element.textContent.trim();
            if (translations[key]) {
                element.textContent = translations[key];
            }
        });
        
        // 翻译页面标题
        const pageTitle = document.querySelector('.page-title');
        if (pageTitle) {
            const key = pageTitle.textContent.trim();
            if (translations[key]) {
                pageTitle.textContent = translations[key];
            }
        }
        
        // 翻译按钮文本
        document.querySelectorAll('button').forEach(button => {
            const key = button.textContent.trim();
            if (translations[key]) {
                button.textContent = translations[key];
            }
        });
        
        // 翻译输入框占位符
        const messageInput = document.getElementById('messageInput');
        if (messageInput) {
            const key = messageInput.placeholder;
            if (translations[key]) {
                messageInput.placeholder = translations[key];
            }
        }
        
        // 翻译发送按钮
        const sendBtn = document.getElementById('sendMessage');
        if (sendBtn) {
            const key = sendBtn.textContent.trim();
            if (translations[key]) {
                sendBtn.textContent = translations[key];
            }
        }
    }
    
    saveSettings() {
        localStorage.setItem('nexus-theme', this.currentTheme);
        localStorage.setItem('nexus-language', this.currentLanguage);
    }
    
    // 获取当前设置
    getCurrentTheme() {
        return this.currentTheme;
    }
    
    getCurrentLanguage() {
        return this.currentLanguage;
    }
    
    // 获取可用主题列表
    getAvailableThemes() {
        return [...this.availableThemes];
    }
    
    // 获取可用语言列表
    getAvailableLanguages() {
        return [...this.availableLanguages];
    }
    
    // 翻译文本
    translate(key) {
        const translations = this.translations[this.currentLanguage];
        return translations && translations[key] ? translations[key] : key;
    }
    
    // 重置为默认设置
    resetToDefaults() {
        this.currentTheme = 'dark';
        this.currentLanguage = 'zh';
        this.applyTheme();
        this.applyLanguage();
        this.saveSettings();
    }
}

// 导出模块
window.ThemeManager = ThemeManager;