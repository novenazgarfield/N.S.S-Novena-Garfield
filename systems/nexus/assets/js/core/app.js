/**
 * NEXUS 应用核心
 * 负责应用初始化和全局状态管理
 */

class NexusApp {
    constructor() {
        this.currentPage = 'dashboard';
        this.currentTheme = 'dark';
        this.i18n = null;
        this.isInitialized = false;
        
        // 绑定方法到实例
        this.init = this.init.bind(this);
        this.setTheme = this.setTheme.bind(this);
        this.setPage = this.setPage.bind(this);
    }

    /**
     * 初始化应用
     */
    async init() {
        if (this.isInitialized) return;
        
        try {
            console.log('🚀 初始化 NEXUS 应用...');
            
            // 初始化视窗高度
            this.initViewportHeight();
            
            // 初始化国际化
            await this.initI18n();
            
            // 初始化主题
            this.initTheme();
            
            // 初始化路由
            this.initRouter();
            
            // 初始化事件监听
            this.initEventListeners();
            
            // 标记为已初始化
            this.isInitialized = true;
            
            console.log('✅ NEXUS 应用初始化完成');
            
        } catch (error) {
            console.error('❌ NEXUS 应用初始化失败:', error);
        }
    }

    /**
     * 初始化视窗高度
     */
    initViewportHeight() {
        const setVH = () => {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--real-vh', `${vh}px`);
        };
        
        setVH();
        window.addEventListener('resize', setVH);
        window.addEventListener('orientationchange', () => {
            setTimeout(setVH, 100);
        });
    }

    /**
     * 初始化国际化
     */
    async initI18n() {
        if (window.I18nManager) {
            this.i18n = new window.I18nManager();
            await this.i18n.init();
        }
    }

    /**
     * 初始化主题
     */
    initTheme() {
        const savedTheme = localStorage.getItem('nexus_theme') || 'dark';
        this.setTheme(savedTheme);
    }

    /**
     * 初始化路由
     */
    initRouter() {
        // 从URL获取初始页面
        const hash = window.location.hash.slice(1);
        if (hash) {
            this.setPage(hash);
        }
        
        // 监听hash变化
        window.addEventListener('hashchange', () => {
            const newHash = window.location.hash.slice(1);
            if (newHash) {
                this.setPage(newHash);
            }
        });
    }

    /**
     * 初始化事件监听
     */
    initEventListeners() {
        // 移动端菜单
        const mobileMenuBtn = document.getElementById('mobileMenuBtn');
        const mobileOverlay = document.getElementById('mobileOverlay');
        
        if (mobileMenuBtn) {
            mobileMenuBtn.addEventListener('click', this.toggleMobileMenu.bind(this));
        }
        
        if (mobileOverlay) {
            mobileOverlay.addEventListener('click', this.closeMobileMenu.bind(this));
        }
        
        // 导航链接
        const navLinks = document.querySelectorAll('[data-page]');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetPage = link.getAttribute('data-page');
                if (targetPage) {
                    this.setPage(targetPage);
                }
            });
        });
        
        // 快速操作按钮
        this.initQuickActions();
        
        // 键盘快捷键
        document.addEventListener('keydown', this.handleKeyboard.bind(this));
    }

    /**
     * 初始化快速操作按钮
     */
    initQuickActions() {
        // 开始对话按钮
        const startChatBtn = document.querySelector('[data-action="start-chat"]');
        if (startChatBtn) {
            startChatBtn.addEventListener('click', () => {
                this.setPage('rag-chat');
            });
        }
        
        // 管理文件按钮
        const manageFilesBtn = document.querySelector('[data-action="manage-files"]');
        if (manageFilesBtn) {
            manageFilesBtn.addEventListener('click', () => {
                this.setPage('file-manager');
            });
        }
    }

    /**
     * 设置主题
     */
    setTheme(theme) {
        this.currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('nexus_theme', theme);
        
        // 更新主题切换按钮
        const themeBtn = document.querySelector('.theme-toggle');
        if (themeBtn) {
            themeBtn.textContent = theme === 'dark' ? '🌙' : '☀️';
        }
    }

    /**
     * 切换主题
     */
    toggleTheme() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    }

    /**
     * 设置当前页面
     */
    setPage(page) {
        if (this.currentPage === page) return;
        
        const previousPage = this.currentPage;
        this.currentPage = page;
        
        // 更新URL
        if (window.location.hash.slice(1) !== page) {
            window.location.hash = page;
        }
        
        // 切换页面显示
        this.showPage(page);
        
        // 更新导航状态
        this.updateNavigation(page);
        
        // 触发页面变化事件
        this.emit('pageChange', { page, previousPage });
    }

    /**
     * 显示指定页面
     */
    showPage(pageId) {
        const pages = document.querySelectorAll('.page');
        pages.forEach(page => {
            const isTargetPage = page.getAttribute('data-page') === pageId;
            page.style.display = isTargetPage ? 'block' : 'none';
        });
    }

    /**
     * 更新导航状态
     */
    updateNavigation(pageId) {
        const navItems = document.querySelectorAll('[data-page]');
        navItems.forEach(nav => {
            if (nav.getAttribute('data-page') === pageId) {
                nav.classList.add('active');
            } else {
                nav.classList.remove('active');
            }
        });
    }

    /**
     * 切换移动端菜单
     */
    toggleMobileMenu() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.getElementById('mobileOverlay');
        
        if (sidebar && overlay) {
            const isOpen = sidebar.classList.contains('mobile-open');
            
            if (isOpen) {
                this.closeMobileMenu();
            } else {
                sidebar.classList.add('mobile-open');
                overlay.classList.add('show');
                document.body.style.overflow = 'hidden';
            }
        }
    }

    /**
     * 关闭移动端菜单
     */
    closeMobileMenu() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.getElementById('mobileOverlay');
        
        if (sidebar && overlay) {
            sidebar.classList.remove('mobile-open');
            overlay.classList.remove('show');
            document.body.style.overflow = '';
        }
    }

    /**
     * 处理键盘事件
     */
    handleKeyboard(event) {
        // Ctrl/Cmd + K: 打开搜索
        if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
            event.preventDefault();
            // TODO: 打开搜索功能
        }
        
        // ESC: 关闭模态框
        if (event.key === 'Escape') {
            this.closeMobileMenu();
            // TODO: 关闭其他模态框
        }
    }

    /**
     * 简单的事件发射器
     */
    emit(event, data) {
        const customEvent = new CustomEvent(`nexus:${event}`, { detail: data });
        document.dispatchEvent(customEvent);
    }

    /**
     * 事件监听器
     */
    on(event, callback) {
        document.addEventListener(`nexus:${event}`, callback);
    }
}

// 创建全局应用实例
window.nexusApp = new NexusApp();

// DOM加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.nexusApp.init);
} else {
    window.nexusApp.init();
}