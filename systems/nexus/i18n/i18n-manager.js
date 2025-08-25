// 🌐 国际化管理器 - NEXUS Research Workstation
// 处理多语言切换和文本替换

class I18nManager {
    constructor() {
        this.currentLanguage = this.getStoredLanguage() || getBrowserLanguage();
        this.translations = LANGUAGES;
        this.observers = [];
        
        // 初始化
        this.init();
    }
    
    init() {
        // 应用当前语言
        this.applyLanguage(this.currentLanguage);
        
        // 监听语言变化
        this.setupLanguageObserver();
    }
    
    // 获取存储的语言设置
    getStoredLanguage() {
        return localStorage.getItem('nexus-language');
    }
    
    // 存储语言设置
    setStoredLanguage(language) {
        localStorage.setItem('nexus-language', language);
    }
    
    // 获取当前语言
    getCurrentLanguage() {
        return this.currentLanguage;
    }
    
    // 获取可用语言列表
    getAvailableLanguages() {
        return Object.keys(this.translations).map(key => ({
            code: key,
            name: this.translations[key].name,
            flag: this.translations[key].flag
        }));
    }
    
    // 切换语言
    switchLanguage(language) {
        if (!this.translations[language]) {
            console.warn(`Language ${language} not supported`);
            return false;
        }
        
        this.currentLanguage = language;
        this.setStoredLanguage(language);
        this.applyLanguage(language);
        this.notifyObservers(language);
        
        return true;
    }
    
    // 获取翻译文本
    t(key, defaultText = '') {
        const keys = key.split('.');
        let value = this.translations[this.currentLanguage];
        
        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                return defaultText || key;
            }
        }
        
        return value || defaultText || key;
    }
    
    // 应用语言到页面
    applyLanguage(language) {
        const lang = this.translations[language];
        if (!lang) return;
        
        // 更新HTML lang属性
        document.documentElement.lang = language;
        
        // 更新所有带有data-i18n属性的元素
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const text = this.t(key);
            
            if (element.tagName === 'INPUT' && element.type === 'text') {
                element.placeholder = text;
            } else {
                element.textContent = text;
            }
        });
        
        // 更新特定元素
        this.updateSpecificElements(lang);
    }
    
    // 更新特定元素
    updateSpecificElements(lang) {
        // 更新页面标题
        const titleElement = document.querySelector('.page-title');
        if (titleElement && titleElement.textContent) {
            const currentTitle = titleElement.textContent.trim();
            // 根据当前显示的页面更新标题
            if (currentTitle.includes('Research Workstation') || currentTitle.includes('研究ワークステーション')) {
                titleElement.textContent = lang.titles.researchWorkstation;
            } else if (currentTitle.includes('RAG System') || currentTitle.includes('RAGシステム')) {
                titleElement.textContent = lang.titles.ragSystem;
            }
            // 可以添加更多页面标题的映射
        }
        
        // 更新导航项
        this.updateNavigationItems(lang);
        
        // 更新卡片内容
        this.updateCardContents(lang);
        
        // 更新聊天界面
        this.updateChatInterface(lang);
    }
    
    // 更新导航项
    updateNavigationItems(lang) {
        const navItems = document.querySelectorAll('.nav-item-text');
        navItems.forEach(item => {
            const text = item.textContent.trim();
            
            // 映射导航项文本（支持多语言反向映射）
            const navMapping = {
                // 英文
                'Dashboard': lang.nav.dashboard,
                'RAG System': lang.nav.ragSystem,
                'Changlee': lang.nav.changlee,
                'NEXUS': lang.nav.nexus,
                'Bovine Insight': lang.nav.bovineInsight,
                'Chronicle': lang.nav.chronicle,
                'Genome Jigsaw': lang.nav.genomeJigsaw,
                'Molecular Simulation': lang.nav.molecularSimulation,
                'Settings': lang.nav.settings,
                // 日语
                'ダッシュボード': lang.nav.dashboard,
                'RAGシステム': lang.nav.ragSystem,
                'チャンリー': lang.nav.changlee,
                '牛認識システム': lang.nav.bovineInsight,
                'クロニクル': lang.nav.chronicle,
                'ゲノムジグソー': lang.nav.genomeJigsaw,
                '分子シミュレーション': lang.nav.molecularSimulation,
                '設定': lang.nav.settings,
                // 中文
                '仪表板': lang.nav.dashboard,
                'RAG系统': lang.nav.ragSystem,
                '长离': lang.nav.changlee,
                '牛只识别': lang.nav.bovineInsight,
                '记录器': lang.nav.chronicle,
                '基因组拼图': lang.nav.genomeJigsaw,
                '分子模拟': lang.nav.molecularSimulation,
                '设置': lang.nav.settings
            };
            
            if (navMapping[text]) {
                item.textContent = navMapping[text];
            }
        });
    }
    
    // 更新卡片内容
    updateCardContents(lang) {
        // RAG System 卡片
        this.updateCard('rag', lang.cards.ragSystem);
        
        // Changlee 卡片
        this.updateCard('changlee', lang.cards.changlee);
        
        // NEXUS 卡片
        this.updateCard('nexus', lang.cards.nexus);
        
        // Bovine Insight 卡片
        this.updateCard('bovine', lang.cards.bovineInsight);
        
        // Chronicle 卡片
        this.updateCard('chronicle', lang.cards.chronicle);
        
        // Genome Jigsaw 卡片
        this.updateCard('genome', lang.cards.genomeJigsaw);
        
        // Molecular Simulation 卡片
        this.updateCard('molecular', lang.cards.molecularSimulation);
        
        // Unified Platform 卡片
        this.updateCard('unified', lang.cards.unifiedPlatform);
    }
    
    // 更新单个卡片
    updateCard(cardType, cardData) {
        const cardElement = document.querySelector(`.card-icon.${cardType}`)?.closest('.project-card');
        if (!cardElement) return;
        
        // 更新标题
        const titleElement = cardElement.querySelector('h3');
        if (titleElement) {
            titleElement.textContent = cardData.title;
        }
        
        // 更新副标题
        const subtitleElement = cardElement.querySelector('.card-info p');
        if (subtitleElement) {
            subtitleElement.textContent = cardData.subtitle;
        }
        
        // 更新功能列表
        const featureElements = cardElement.querySelectorAll('.feature-item span:last-child');
        featureElements.forEach((element, index) => {
            if (cardData.features[index]) {
                element.textContent = cardData.features[index];
            }
        });
        
        // 更新按钮文本
        const buttons = cardElement.querySelectorAll('.btn');
        buttons.forEach(button => {
            const buttonText = button.textContent.trim();
            
            // 根据按钮内容更新文本
            if (buttonText.includes('启动') || buttonText.includes('Launch') || buttonText.includes('起動')) {
                if (cardData.buttons.launch) {
                    button.textContent = cardData.buttons.launch;
                }
            } else if (buttonText.includes('文档') || buttonText.includes('Document') || buttonText.includes('文書')) {
                if (cardData.buttons.docs) {
                    button.textContent = cardData.buttons.docs;
                }
            } else if (buttonText.includes('游戏') || buttonText.includes('Magic') || buttonText.includes('マジック')) {
                if (cardData.buttons.games) {
                    button.textContent = cardData.buttons.games;
                }
            } else if (buttonText.includes('监控') || buttonText.includes('Monitor') || buttonText.includes('監視')) {
                if (cardData.buttons.monitor) {
                    button.textContent = cardData.buttons.monitor;
                }
            }
            // 可以添加更多按钮映射
        });
    }
    
    // 更新聊天界面
    updateChatInterface(lang) {
        // 更新输入框占位符
        const chatInput = document.querySelector('.chat-input-field');
        if (chatInput) {
            chatInput.placeholder = lang.chat.placeholder;
        }
        
        // 更新发送按钮
        const sendButton = document.querySelector('.send-btn');
        if (sendButton) {
            sendButton.textContent = lang.chat.send;
        }
        
        // 更新示例消息（如果需要）
        const welcomeMessages = document.querySelectorAll('.message-content');
        welcomeMessages.forEach(message => {
            const text = message.textContent.trim();
            if (text.includes('根据文档内容') || text.includes('Based on the document') || text.includes('文書内容に基づいて')) {
                message.textContent = lang.chat.welcome;
            } else if (text.includes('正在分析') || text.includes('analyzing') || text.includes('分析中')) {
                message.textContent = lang.chat.thinking;
            }
        });
    }
    
    // 添加语言变化观察者
    addObserver(callback) {
        this.observers.push(callback);
    }
    
    // 移除观察者
    removeObserver(callback) {
        this.observers = this.observers.filter(obs => obs !== callback);
    }
    
    // 通知观察者
    notifyObservers(language) {
        this.observers.forEach(callback => {
            try {
                callback(language);
            } catch (error) {
                console.error('Error in language observer:', error);
            }
        });
    }
    
    // 设置语言变化监听器
    setupLanguageObserver() {
        // 监听系统语言变化
        if ('addEventListener' in window) {
            window.addEventListener('languagechange', () => {
                const browserLang = getBrowserLanguage();
                if (browserLang !== this.currentLanguage && !this.getStoredLanguage()) {
                    this.switchLanguage(browserLang);
                }
            });
        }
    }
    
    // 格式化文本（支持参数替换）
    format(key, params = {}) {
        let text = this.t(key);
        
        // 替换参数
        Object.keys(params).forEach(param => {
            text = text.replace(new RegExp(`{${param}}`, 'g'), params[param]);
        });
        
        return text;
    }
    
    // 获取当前语言的方向（LTR/RTL）
    getDirection() {
        // 目前支持的语言都是LTR，如果以后添加阿拉伯语等RTL语言需要扩展
        return 'ltr';
    }
    
    // 获取当前语言的区域设置
    getLocale() {
        return this.currentLanguage;
    }
}

// 创建全局实例
let i18nManager;

// 初始化国际化管理器
function initI18n() {
    if (typeof LANGUAGES === 'undefined') {
        console.error('Languages not loaded. Please include languages.js first.');
        return null;
    }
    
    i18nManager = new I18nManager();
    return i18nManager;
}

// 便捷的翻译函数
function t(key, defaultText = '') {
    return i18nManager ? i18nManager.t(key, defaultText) : (defaultText || key);
}

// 便捷的格式化函数
function tf(key, params = {}) {
    return i18nManager ? i18nManager.format(key, params) : key;
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { I18nManager, initI18n, t, tf };
}