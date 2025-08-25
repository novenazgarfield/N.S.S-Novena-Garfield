// NEXUS Research Workstation - Navigation Module
// 导航相关的JavaScript模块

class NavigationManager {
    constructor() {
        this.currentPage = 'dashboard';
        this.pageTitles = {
            'dashboard': {
                'zh': '仪表板',
                'en': 'Dashboard', 
                'ja': 'ダッシュボード'
            },
            'rag-system': {
                'zh': 'RAG System',
                'en': 'RAG System',
                'ja': 'RAGシステム'
            },
            'changlee': {
                'zh': 'Changlee',
                'en': 'Changlee',
                'ja': 'チャンリー'
            },
            'nexus': {
                'zh': 'NEXUS',
                'en': 'NEXUS',
                'ja': 'NEXUS'
            },
            'bovine': {
                'zh': 'Bovine Insight',
                'en': 'Bovine Insight',
                'ja': '牛認識システム'
            },
            'chronicle': {
                'zh': 'Chronicle',
                'en': 'Chronicle',
                'ja': 'クロニクル'
            },
            'genome': {
                'zh': 'Genome Jigsaw',
                'en': 'Genome Jigsaw',
                'ja': 'ゲノムジグソー'
            },
            'molecular': {
                'zh': 'Molecular Simulation',
                'en': 'Molecular Simulation',
                'ja': '分子シミュレーション'
            },
            'settings': {
                'zh': '设置',
                'en': 'Settings',
                'ja': '設定'
            }
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupMobileNavigation();
    }
    
    setupEventListeners() {
        // 导航按钮事件
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const onclick = item.getAttribute('onclick');
                if (onclick) {
                    // 解析onclick中的页面ID
                    const match = onclick.match(/showPage\('([^']+)'\)/);
                    if (match) {
                        this.showPage(match[1]);
                    }
                }
            });
        });
        
        // 返回按钮事件
        const backBtn = document.querySelector('.back-btn');
        if (backBtn) {
            backBtn.addEventListener('click', () => {
                this.showPage('dashboard');
            });
        }
        
        // 移动端菜单切换
        const menuToggle = document.getElementById('menuToggle');
        if (menuToggle) {
            menuToggle.addEventListener('click', () => {
                this.toggleMobileMenu();
            });
        }
    }
    
    setupMobileNavigation() {
        // 检测移动端
        if (window.innerWidth <= 768) {
            this.setupMobileMenu();
        }
        
        // 监听窗口大小变化
        window.addEventListener('resize', () => {
            if (window.innerWidth <= 768) {
                this.setupMobileMenu();
            } else {
                this.closeMobileMenu();
            }
        });
    }
    
    setupMobileMenu() {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            // 点击外部关闭菜单
            document.addEventListener('click', (e) => {
                if (!sidebar.contains(e.target) && !e.target.closest('#menuToggle')) {
                    this.closeMobileMenu();
                }
            });
        }
    }
    
    toggleMobileMenu() {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.classList.toggle('open');
        }
    }
    
    closeMobileMenu() {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.classList.remove('open');
        }
    }
    
    showPage(pageId) {
        // 更新当前页面
        this.currentPage = pageId;
        
        // 更新导航状态
        this.updateActiveNav(pageId);
        
        // 隐藏所有内容
        this.hideAllContent();
        
        // 显示对应内容和更新标题
        if (pageId === 'dashboard') {
            this.showDashboard();
        } else if (pageId === 'rag-system') {
            this.showRAGChat();
            return; // RAG有自己的导航更新逻辑
        } else if (pageId === 'settings') {
            this.showSettings();
        } else {
            this.showEmptyPage();
        }
        
        // 更新页面标题
        this.updatePageTitle(pageId);
        
        // 关闭移动端菜单
        this.closeMobileMenu();
    }
    
    hideAllContent() {
        const contents = [
            'dashboard-content',
            'rag-chat', 
            'settings-page',
            'empty-page'
        ];
        
        contents.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.style.display = 'none';
            }
        });
    }
    
    showDashboard() {
        const dashboard = document.getElementById('dashboard-content');
        if (dashboard) {
            dashboard.style.display = 'block';
        }
    }
    
    showRAGChat() {
        const ragChat = document.getElementById('rag-chat');
        if (ragChat) {
            ragChat.style.display = 'flex';
        }
        
        // 更新页面标题
        this.updatePageTitle('rag-system');
        
        // 更新导航状态
        this.updateActiveNav('rag-system');
    }
    
    showSettings() {
        const settings = document.getElementById('settings-page');
        if (settings) {
            settings.style.display = 'block';
        }
        
        // 更新设置页面的导航状态
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const settingsNav = document.querySelector('[onclick="showPage(\'settings\')"]');
        if (settingsNav) {
            settingsNav.classList.add('active');
        }
    }
    
    showEmptyPage() {
        const emptyPage = document.getElementById('empty-page');
        if (emptyPage) {
            emptyPage.style.display = 'block';
        }
    }
    
    updateActiveNav(pageId) {
        // 移除所有active状态
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // 添加active状态到当前页面
        const activeNav = document.querySelector(`[onclick="showPage('${pageId}')"]`);
        if (activeNav) {
            activeNav.classList.add('active');
        }
    }
    
    updatePageTitle(pageId) {
        const titleElement = document.querySelector('.page-title');
        if (titleElement && this.pageTitles[pageId]) {
            const currentLang = document.documentElement.lang || 'zh';
            const langKey = currentLang.startsWith('zh') ? 'zh' : 
                           currentLang.startsWith('ja') ? 'ja' : 'en';
            
            titleElement.textContent = this.pageTitles[pageId][langKey] || 
                                     this.pageTitles[pageId]['en'] || 
                                     'Research Workstation';
        }
    }
    
    getCurrentPage() {
        return this.currentPage;
    }
    
    // 添加页面历史记录支持
    setupHistorySupport() {
        // 监听浏览器前进后退
        window.addEventListener('popstate', (e) => {
            const pageId = e.state?.pageId || 'dashboard';
            this.showPage(pageId);
        });
        
        // 初始化历史记录
        history.replaceState({ pageId: this.currentPage }, '', `#${this.currentPage}`);
    }
    
    // 更新URL和历史记录
    updateHistory(pageId) {
        const url = `#${pageId}`;
        history.pushState({ pageId }, '', url);
    }
    
    // 从URL初始化页面
    initFromURL() {
        const hash = window.location.hash.slice(1);
        if (hash && this.pageTitles[hash]) {
            this.showPage(hash);
        } else {
            this.showPage('dashboard');
        }
    }
}

// 导出模块
window.NavigationManager = NavigationManager;