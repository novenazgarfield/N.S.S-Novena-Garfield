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
        console.log('🌐 switchLanguage被调用，目标语言:', language);
        
        if (!this.translations[language]) {
            console.warn(`Language ${language} not supported`);
            return false;
        }
        
        console.log('🌐 语言支持，开始切换...');
        this.currentLanguage = language;
        this.setStoredLanguage(language);
        this.applyLanguage(language);
        this.notifyObservers(language);
        
        console.log('🌐 语言切换完成，当前语言:', this.currentLanguage);
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
        // 直接更新具体的文本内容
        this.updateSpecificTexts(lang);
    }
    
    // 更新具体的文本内容
    updateSpecificTexts(lang) {
        console.log('🔄 开始更新具体文本内容...');
        
        // 更新卡片标题
        const cardTitles = document.querySelectorAll('h3');
        cardTitles.forEach(title => {
            const text = title.textContent.trim();
            if (text.includes('NEXUS Remote Control') || text.includes('NEXUS远程控制')) {
                title.textContent = this.currentLanguage === 'en-US' ? 'NEXUS Remote Control' : 'NEXUS远程控制';
            }
            else if (text.includes('RAG System') || text.includes('RAG系统')) {
                title.textContent = 'RAG System';
            }
            else if (text.includes('Unified Platform') || text.includes('统一平台')) {
                title.textContent = 'Unified Platform';
            }
        });
        
        // 更新卡片描述
        const descriptions = document.querySelectorAll('.card-description, p');
        descriptions.forEach(desc => {
            const text = desc.textContent.trim();
            
            // NEXUS卡片描述
            if (text.includes('Revolutionary Remote Command') || text.includes('革命性远程命令')) {
                desc.textContent = this.currentLanguage === 'en-US' ? 
                    'Revolutionary Remote Command & Control System' : 
                    'Revolutionary Remote Command & Control System';
            }
            // RAG系统描述
            else if (text.includes('Retrieval-Augmented Generation')) {
                desc.textContent = 'Retrieval-Augmented Generation AI';
            }
            // Unified Platform描述
            else if (text.includes('整个研究工作站') || text.includes('Research Workstation Management')) {
                desc.textContent = this.currentLanguage === 'en-US' ? 
                    'Unified installer, launcher and manager for the entire research workstation, providing a one-stop system management experience.' : 
                    '整个研究工作站的统一安装器、启动器和管理器，提供一站式的系统管理体验。';
            }
        });
        
        // 更新特性列表
        const features = document.querySelectorAll('.feature-item span:last-child');
        features.forEach(feature => {
            const text = feature.textContent.trim();
            
            // NEXUS特性 - 直接设置英文文本
            if (text.includes('全球远程访问') || text.includes('Global remote access') || text.includes('云服务器中转')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'Global remote access - Cloud server relay' : 
                    '全球远程访问 - 云服务器中转';
            }
            else if (text.includes('完整电源管理') || text.includes('Complete power management') || text.includes('WOL')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'Complete power management - WOL/Shutdown/Restart' : 
                    '完整电源管理 - WOL/关机/重启';
            }
            else if (text.includes('零命令行体验') || text.includes('Zero command line experience') || text.includes('图形化界面')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'Zero command line experience - GUI interface' : 
                    '零命令行体验 - 图形化界面';
            }
            else if (text.includes('移动端优化') || text.includes('Mobile optimization') || text.includes('PWA')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'Mobile optimization - PWA native experience' : 
                    '移动端优化 - PWA原生体验';
            }
            else if (text.includes('企业级安全') || text.includes('Enterprise security') || text.includes('256位加密')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'Enterprise security - 256-bit encryption' : 
                    '企业级安全 - 256位加密';
            }
            
            // RAG特性
            else if (text.includes('多格式文档') || text.includes('Multi-format documents') || text.includes('PDF/DOCX')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'Multi-format documents - PDF/DOCX/Excel/Markdown' : 
                    '多格式文档 - PDF/DOCX/Excel/Markdown';
            }
            else if (text.includes('智能检索') || text.includes('Intelligent retrieval') || text.includes('向量语义搜索')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'Intelligent retrieval - Vector semantic search' : 
                    '智能检索 - 向量语义搜索';
            }
            else if (text.includes('记忆系统') || text.includes('Memory system') || text.includes('永久/临时记忆')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'Memory system - Permanent/Temporary memory management' : 
                    '记忆系统 - 永久/临时记忆管理';
            }
            else if (text.includes('多轮对话') || text.includes('Multi-turn dialogue') || text.includes('上下文理解')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'Multi-turn dialogue - Context understanding' : 
                    '多轮对话 - 上下文理解';
            }
            else if (text.includes('API管理') || text.includes('API management') || text.includes('多模型支持')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'API management - Multi-model support' : 
                    'API管理 - 多模型支持';
            }
            
            // Unified Platform特性
            else if (text.includes('系统级部署') || text.includes('System-level deployment') || text.includes('舰队总指挥')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'System-level deployment - Fleet command capability' : 
                    '系统级部署 - 舰队总指挥能力';
            }
            else if (text.includes('依赖检查') || text.includes('Dependency check') || text.includes('自动环境配置')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'Dependency check - Automatic environment configuration' : 
                    '依赖检查 - 自动环境配置';
            }
            else if (text.includes('状态监控') || text.includes('Status monitoring') || text.includes('实时系统状态')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'Status monitoring - Real-time system status' : 
                    '状态监控 - 实时系统状态';
            }
        });
        
        // 更新按钮文本
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(button => {
            const text = button.textContent.trim();
            
            // Launch按钮
            if (text.includes('启动 NEXUS') || text.includes('Launch NEXUS')) {
                button.textContent = this.currentLanguage === 'en-US' ? 
                    '🚀 Launch NEXUS' : 
                    '🚀 启动 NEXUS';
            }
            else if (text.includes('启动 RAG') || text.includes('Launch RAG')) {
                button.textContent = this.currentLanguage === 'en-US' ? 
                    '🧠 Launch RAG' : 
                    '🧠 启动 RAG';
            }
            else if (text.includes('管理平台') || text.includes('Management Platform')) {
                button.textContent = this.currentLanguage === 'en-US' ? 
                    '🚀 Management Platform' : 
                    '🚀 管理平台';
            }
            
            // 文档按钮
            else if (text.includes('文档') && !text.includes('文档库') || text.includes('Documentation')) {
                button.textContent = this.currentLanguage === 'en-US' ? 
                    '📁 Documentation' : 
                    '📁 文档';
            }
            else if (text.includes('文档库') || text.includes('Document Library')) {
                button.textContent = this.currentLanguage === 'en-US' ? 
                    '📚 Document Library' : 
                    '📚 文档库';
            }
            else if (text.includes('系统状态') || text.includes('System Status')) {
                button.textContent = this.currentLanguage === 'en-US' ? 
                    '📋 System Status' : 
                    '📋 系统状态';
            }
        });
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