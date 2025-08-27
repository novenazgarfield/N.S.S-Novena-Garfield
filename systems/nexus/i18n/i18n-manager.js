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
            
            // 检查是否是侧边栏导航项且启用了英文固定模式
            const isNavItem = element.closest('.nav-item') && key.startsWith('nav.');
            if (isNavItem && window.sidebarEnglishMode) {
                return; // 跳过侧边栏项的翻译
            }
            
            if (element.tagName === 'INPUT' && element.type === 'text') {
                element.placeholder = text;
            } else {
                element.textContent = text;
            }
        });
        
        // 更新特定元素
        this.updateSpecificElements(lang);
        
        // 如果启用了侧边栏英文模式，重新应用英文
        if (window.sidebarEnglishMode && typeof window.updateSidebarToEnglish === 'function') {
            window.updateSidebarToEnglish();
        }
    }
    
    // 更新特定元素
    updateSpecificElements(lang) {
        // 更新页面标题
        const titleElement = document.querySelector('.page-title');
        if (titleElement && titleElement.textContent) {
            const currentTitle = titleElement.textContent.trim();
            // 根据当前显示的页面更新标题
            if (currentTitle.includes('Dashboard') || currentTitle.includes('ダッシュボード') || currentTitle.includes('仪表板')) {
                titleElement.textContent = lang.titles.dashboard;
            } else if (currentTitle.includes('RAG System') || currentTitle.includes('RAGシステム') || currentTitle.includes('RAG系统')) {
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
                '基因组星云': lang.nav.genomeNebula,
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
            if (text.includes('NEXUS Remote Control') || text.includes('NEXUS远程控制') || text.includes('NEXUSリモートコントロール')) {
                title.textContent = this.currentLanguage === 'en-US' ? 
                    'NEXUS Remote Control' : 
                    this.currentLanguage === 'ja-JP' ?
                    'NEXUSリモートコントロール' :
                    'NEXUS远程控制';
            }
            else if (text.includes('RAG System') || text.includes('RAG系统') || text.includes('RAGシステム')) {
                title.textContent = this.currentLanguage === 'en-US' ? 
                    'RAG System' : 
                    this.currentLanguage === 'ja-JP' ?
                    'RAGシステム' :
                    'RAG系统';
            }
            else if (text.includes('Unified Platform') || text.includes('统一平台') || text.includes('統合プラットフォーム')) {
                title.textContent = this.currentLanguage === 'en-US' ? 
                    'Unified Platform' : 
                    this.currentLanguage === 'ja-JP' ?
                    '統合プラットフォーム' :
                    '统一平台';
            }
        });
        
        // 更新卡片描述
        const descriptions = document.querySelectorAll('.card-description');
        console.log('🔍 找到描述元素数量:', descriptions.length);
        descriptions.forEach((desc, index) => {
            const text = desc.textContent.trim();
            console.log(`🔍 描述${index + 1}:`, text.substring(0, 50) + '...');
            console.log('🔍 当前语言:', this.currentLanguage);
            
            // NEXUS卡片描述 - 匹配所有可能的文本
            if (text.includes('突破局域网限制') || 
                text.includes('Break through LAN restrictions') || 
                text.includes('LANの制限を突破し') ||
                text.includes('真のグローバルリモート電源管理')) {
                console.log('🔄 匹配到NEXUS描述，开始更新...');
                desc.textContent = this.currentLanguage === 'en-US' ? 
                    'Break through LAN restrictions to achieve true global remote power management. Support remote boot, shutdown, restart with enterprise-level security.' : 
                    this.currentLanguage === 'ja-JP' ?
                    'LANの制限を突破し、真のグローバルリモート電源管理を実現。リモート起動、シャットダウン、再起動をエンタープライズレベルのセキュリティで支援。' :
                    '突破局域网限制，实现真正的全球远程电源管理。支持远程开机、关机、重启，企业级安全保障。';
                console.log('✅ NEXUS描述已更新为:', desc.textContent.substring(0, 50) + '...');
            }
            // RAG系统描述 - 保持不变，因为已经是英文
            // Unified Platform描述 - 匹配所有可能的文本
            else if (text.includes('整个研究工作站') || 
                     text.includes('Unified installer') || 
                     text.includes('研究ワークステーション全体') ||
                     text.includes('統合インストーラー') ||
                     text.includes('ワンストップのシステム管理体験')) {
                console.log('🔄 匹配到Unified Platform描述，开始更新...');
                desc.textContent = this.currentLanguage === 'en-US' ? 
                    'Unified installer, launcher and manager for the entire research workstation, providing a one-stop system management experience.' : 
                    this.currentLanguage === 'ja-JP' ?
                    '研究ワークステーション全体の統合インストーラー、ランチャー、マネージャーで、ワンストップのシステム管理体験を提供。' :
                    '整个研究工作站的统一安装器、启动器和管理器，提供一站式的系统管理体验。';
                console.log('✅ Unified Platform描述已更新为:', desc.textContent.substring(0, 50) + '...');
            }
        });
        
        // 更新特性列表
        const features = document.querySelectorAll('.feature-item span:last-child');
        features.forEach(feature => {
            const text = feature.textContent.trim();
            
            // NEXUS特性 - 支持三种语言
            if (text.includes('全球远程访问') || text.includes('Global remote access') || text.includes('グローバルリモートアクセス') || text.includes('云服务器中转')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'Global remote access - Cloud server relay' : 
                    this.currentLanguage === 'ja-JP' ?
                    'グローバルリモートアクセス - クラウドサーバーリレー' :
                    '全球远程访问 - 云服务器中转';
            }
            else if (text.includes('完整电源管理') || text.includes('Complete power management') || text.includes('完全な電源管理') || text.includes('WOL')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'Complete power management - WOL/Shutdown/Restart' : 
                    this.currentLanguage === 'ja-JP' ?
                    '完全な電源管理 - WOL/シャットダウン/再起動' :
                    '完整电源管理 - WOL/关机/重启';
            }
            else if (text.includes('零命令行体验') || text.includes('Zero command line experience') || text.includes('コマンドライン不要') || text.includes('图形化界面')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'Zero command line experience - GUI interface' : 
                    this.currentLanguage === 'ja-JP' ?
                    'コマンドライン不要 - GUIインターフェース' :
                    '零命令行体验 - 图形化界面';
            }
            else if (text.includes('移动端优化') || text.includes('Mobile optimization') || text.includes('モバイル最適化') || text.includes('PWA')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'Mobile optimization - PWA native experience' : 
                    this.currentLanguage === 'ja-JP' ?
                    'モバイル最適化 - PWAネイティブ体験' :
                    '移动端优化 - PWA原生体验';
            }
            else if (text.includes('企业级安全') || text.includes('Enterprise security') || text.includes('エンタープライズセキュリティ') || text.includes('256位加密')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'Enterprise security - 256-bit encryption' : 
                    this.currentLanguage === 'ja-JP' ?
                    'エンタープライズセキュリティ - 256ビット暗号化' :
                    '企业级安全 - 256位加密';
            }
            
            // RAG特性
            else if (text.includes('多格式文档') || text.includes('Multi-format documents') || text.includes('複数文書形式') || text.includes('PDF/DOCX')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'Multi-format documents - PDF/DOCX/Excel/Markdown' : 
                    this.currentLanguage === 'ja-JP' ?
                    '複数文書形式サポート - PDF/DOCX/Excel/Markdown' :
                    '多格式文档 - PDF/DOCX/Excel/Markdown';
            }
            else if (text.includes('智能检索') || text.includes('Intelligent retrieval') || text.includes('インテリジェント検索') || text.includes('向量语义搜索')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'Intelligent retrieval - Vector semantic search' : 
                    this.currentLanguage === 'ja-JP' ?
                    'インテリジェント検索 - ベクトル意味検索' :
                    '智能检索 - 向量语义搜索';
            }
            else if (text.includes('记忆系统') || text.includes('Memory system') || text.includes('メモリシステム') || text.includes('永久/临时记忆')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'Memory system - Permanent/Temporary memory management' : 
                    this.currentLanguage === 'ja-JP' ?
                    'メモリシステム - 永続/一時メモリ管理' :
                    '记忆系统 - 永久/临时记忆管理';
            }
            else if (text.includes('多轮对话') || text.includes('Multi-turn dialogue') || text.includes('マルチターン対話') || text.includes('上下文理解')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'Multi-turn dialogue - Context understanding' : 
                    this.currentLanguage === 'ja-JP' ?
                    'マルチターン対話 - コンテキスト理解' :
                    '多轮对话 - 上下文理解';
            }
            else if (text.includes('API管理') || text.includes('API management') || text.includes('API管理') || text.includes('多模型支持')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'API management - Multi-model support' : 
                    this.currentLanguage === 'ja-JP' ?
                    'API管理 - マルチモデルサポート' :
                    'API管理 - 多模型支持';
            }
            
            // Unified Platform特性
            else if (text.includes('系统级部署') || text.includes('System-level deployment') || text.includes('システムレベルデプロイ') || text.includes('舰队总指挥')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'System-level deployment - Fleet command capability' : 
                    this.currentLanguage === 'ja-JP' ?
                    'システムレベルデプロイ - フリートコマンド機能' :
                    '系统级部署 - 舰队总指挥能力';
            }
            else if (text.includes('依赖检查') || text.includes('Dependency check') || text.includes('依存関係チェック') || text.includes('自动环境配置')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'Dependency check - Automatic environment configuration' : 
                    this.currentLanguage === 'ja-JP' ?
                    '依存関係チェック - 自動環境設定' :
                    '依赖检查 - 自动环境配置';
            }
            else if (text.includes('状态监控') || text.includes('Status monitoring') || text.includes('ステータス監視') || text.includes('实时系统状态')) {
                feature.textContent = this.currentLanguage === 'en-US' ? 
                    'Status monitoring - Real-time system status' : 
                    this.currentLanguage === 'ja-JP' ?
                    'ステータス監視 - リアルタイムシステム状態' :
                    '状态监控 - 实时系统状态';
            }
        });
        
        // 更新按钮文本
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(button => {
            const text = button.textContent.trim();
            
            // Launch按钮
            if (text.includes('启动 NEXUS') || text.includes('Launch NEXUS') || text.includes('NEXUS起動')) {
                button.textContent = this.currentLanguage === 'en-US' ? 
                    '🚀 Launch NEXUS' : 
                    this.currentLanguage === 'ja-JP' ?
                    '🚀 NEXUS起動' :
                    '🚀 启动 NEXUS';
            }
            else if (text.includes('启动 RAG') || text.includes('Launch RAG') || text.includes('RAG起動')) {
                button.textContent = this.currentLanguage === 'en-US' ? 
                    '🧠 Launch RAG' : 
                    this.currentLanguage === 'ja-JP' ?
                    '🧠 RAG起動' :
                    '🧠 启动 RAG';
            }
            else if (text.includes('管理平台') || text.includes('Management Platform') || text.includes('管理プラットフォーム')) {
                button.textContent = this.currentLanguage === 'en-US' ? 
                    '🚀 Management Platform' : 
                    this.currentLanguage === 'ja-JP' ?
                    '🚀 管理プラットフォーム' :
                    '🚀 管理平台';
            }
            
            // 文档按钮
            else if ((text.includes('文档') && !text.includes('文档库')) || text.includes('Documentation') || text.includes('ドキュメント')) {
                button.textContent = this.currentLanguage === 'en-US' ? 
                    '📁 Documentation' : 
                    this.currentLanguage === 'ja-JP' ?
                    '📁 ドキュメント' :
                    '📁 文档';
            }
            else if (text.includes('文档库') || text.includes('Document Library') || text.includes('ドキュメントライブラリ')) {
                button.textContent = this.currentLanguage === 'en-US' ? 
                    '📚 Document Library' : 
                    this.currentLanguage === 'ja-JP' ?
                    '📚 ドキュメントライブラリ' :
                    '📚 文档库';
            }
            else if (text.includes('系统状态') || text.includes('System Status') || text.includes('システムステータス')) {
                button.textContent = this.currentLanguage === 'en-US' ? 
                    '📋 System Status' : 
                    this.currentLanguage === 'ja-JP' ?
                    '📋 システムステータス' :
                    '📋 系统状态';
            }
        });
        
        // 更新RAG对话框欢迎语 - 匹配所有语言版本
        const ragWelcomeMessage = document.querySelector('.message-content');
        if (ragWelcomeMessage && (
            ragWelcomeMessage.textContent.includes('你好！我是RAG智能助手') ||
            ragWelcomeMessage.textContent.includes('Hello! I am the RAG AI assistant') ||
            ragWelcomeMessage.textContent.includes('こんにちは！私はRAG AIアシスタント')
        )) {
            console.log('🔄 更新RAG欢迎语，当前语言:', this.currentLanguage);
            ragWelcomeMessage.textContent = this.currentLanguage === 'en-US' ? 
                'Hello! I am the RAG AI assistant, I can help you analyze documents and answer questions. Please upload documents or ask questions directly.' : 
                this.currentLanguage === 'ja-JP' ?
                'こんにちは！私はRAG AIアシスタントです。文書の分析や質問への回答をお手伝いできます。文書をアップロードするか、直接質問してください。' :
                '你好！我是RAG智能助手，可以帮你分析文档、回答问题。请上传文档或直接提问。';
            console.log('✅ RAG欢迎语已更新为:', ragWelcomeMessage.textContent.substring(0, 30) + '...');
        }
        
        console.log('🔄 具体文本内容更新完成');
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
    
    // 公共方法：更新所有元素
    updateElements() {
        this.applyLanguage(this.currentLanguage);
    }
}

// 获取浏览器语言
function getBrowserLanguage() {
    const browserLang = navigator.language || navigator.userLanguage;
    
    // 支持的语言映射
    const supportedLanguages = {
        'zh': 'zh-CN',
        'zh-CN': 'zh-CN',
        'zh-Hans': 'zh-CN',
        'en': 'en-US',
        'en-US': 'en-US',
        'ja': 'ja-JP',
        'ja-JP': 'ja-JP'
    };
    
    // 精确匹配
    if (supportedLanguages[browserLang]) {
        return supportedLanguages[browserLang];
    }
    
    // 语言前缀匹配
    const langPrefix = browserLang.split('-')[0];
    if (supportedLanguages[langPrefix]) {
        return supportedLanguages[langPrefix];
    }
    
    // 默认返回中文
    return 'zh-CN';
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