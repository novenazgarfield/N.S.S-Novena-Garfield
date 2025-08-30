        let currentPage = 'dashboard';
        let currentTheme = 'dark';
        let i18n = null; // 国际化管理器实例
        
        // 聊天记录存储系统
        const CHAT_STORAGE_KEY = 'nexus_rag_chat_history';
        const MAX_STORED_MESSAGES = 100; // 最多存储100条消息
        let currentTaskName = 'nexus_chat';
        
        // 聊天记录管理函数
        function saveChatHistory() {
            try {
                const messages = [];
                const messageElements = document.querySelectorAll('#chatMessages .message');
                
                messageElements.forEach(element => {
                    const avatar = element.querySelector('.message-avatar')?.textContent || '👤';
                    const content = element.querySelector('.message-content')?.innerHTML || '';
                    const role = avatar === '🧠' ? 'assistant' : 'user';
                    
                    if (content.trim()) {
                        messages.push({
                            role: role,
                            content: content,
                            avatar: avatar,
                            timestamp: Date.now()
                        });
                    }
                });
                
                // 只保留最新的消息
                const recentMessages = messages.slice(-MAX_STORED_MESSAGES);
                localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(recentMessages));
                
                console.log(`💾 已保存 ${recentMessages.length} 条聊天记录`);
            } catch (error) {
                console.error('保存聊天记录失败:', error);
            }
        }
        
        function loadChatHistory() {
            try {
                const stored = localStorage.getItem(CHAT_STORAGE_KEY);
                if (!stored) return false;
                
                const messages = JSON.parse(stored);
                if (!Array.isArray(messages) || messages.length === 0) return false;
                
                const chatMessages = document.getElementById('chatMessages');
                if (!chatMessages) return false;
                
                // 清空现有消息（除了欢迎消息）
                const welcomeMessage = chatMessages.querySelector('.message');
                chatMessages.innerHTML = '';
                
                // 恢复欢迎消息
                if (welcomeMessage) {
                    chatMessages.appendChild(welcomeMessage);
                }
                
                // 恢复历史消息
                messages.forEach(msg => {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'message';
                    messageDiv.innerHTML = `
                        <div class="message-avatar">${msg.avatar}</div>
                        <div class="message-content">${msg.content}</div>
                    `;
                    chatMessages.appendChild(messageDiv);
                });
                
                // 滚动到底部
                chatMessages.scrollTop = chatMessages.scrollHeight;
                
                console.log(`📚 已恢复 ${messages.length} 条聊天记录`);
                return true;
            } catch (error) {
                console.error('加载聊天记录失败:', error);
                return false;
            }
        }
        
        function clearChatHistory() {
            try {
                localStorage.removeItem(CHAT_STORAGE_KEY);
                console.log('🗑️ 已清空本地聊天记录');
            } catch (error) {
                console.error('清空聊天记录失败:', error);
            }
        }
        
        function showStorageStatus() {
            try {
                const stored = localStorage.getItem(CHAT_STORAGE_KEY);
                let messageCount = 0;
                let storageSize = 0;
                let lastUpdate = '无';
                
                if (stored) {
                    const messages = JSON.parse(stored);
                    messageCount = messages.length;
                    storageSize = new Blob([stored]).size;
                    
                    // 找到最新消息的时间戳
                    if (messages.length > 0) {
                        const latestTimestamp = Math.max(...messages.map(m => m.timestamp || 0));
                        if (latestTimestamp > 0) {
                            lastUpdate = new Date(latestTimestamp).toLocaleString('zh-CN');
                        }
                    }
                }
                
                const statusMessage = `📊 **聊天记录存储状态**

💬 **消息数量:** ${messageCount} 条  
📦 **存储大小:** ${(storageSize / 1024).toFixed(2)} KB  
🕒 **最后更新:** ${lastUpdate}  
💾 **存储位置:** 浏览器本地存储  
🔄 **自动保存:** 已启用  

> 💡 **提示:** 聊天记录会自动保存到浏览器本地存储，刷新页面后会自动恢复。最多保存 ${MAX_STORED_MESSAGES} 条消息。`;
                
                addMessage(statusMessage, 'assistant');
                
            } catch (error) {
                console.error('获取存储状态失败:', error);
                addMessage('❌ 获取存储状态失败', 'assistant');
            }
            
            toggleFunctionMenu();
        }
        
        // 全局变量，供i18n-manager.js访问
        window.sidebarEnglishMode = false;

        // 页面标题映射
        const pageTitles = {
            'dashboard': '仪表板',
            'project-info': 'N.S.S - Novena Garfield',
            'rag-system': 'RAG System',
            'changlee': 'Changlee',
            'nexus': 'NEXUS',
            'bovine': 'Bovine Insight',
            'chronicle': 'Chronicle',
            'genome': 'Genome Nebula',
            'molecular': 'Molecular Simulation',
            'settings': 'Settings'
        };

        function showPage(pageId) {
            // 更新导航状态
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            if (event && event.target) {
                event.target.classList.add('active');
            }
            
            // 隐藏连接状态框（只在RAG页面显示）
            if (pageId !== 'rag-system') {
                hideConnectionStatus();
            }
            
            // 隐藏所有内容
            document.getElementById('dashboard-content').style.display = 'none';
            document.getElementById('rag-chat').style.display = 'none';
            document.getElementById('settings-page').style.display = 'none';
            document.getElementById('empty-page').style.display = 'none';
            document.getElementById('project-info-page').style.display = 'none';
            document.getElementById('molecular-page').style.display = 'none';
            document.getElementById('genome-page').style.display = 'none';
            
            // 显示对应内容和更新标题
            if (pageId === 'dashboard') {
                document.getElementById('dashboard-content').style.display = 'block';
            } else if (pageId === 'rag-system') {
                showRAGChat();
                return; // RAG有自己的导航更新逻辑
            } else if (pageId === 'settings') {
                document.getElementById('settings-page').style.display = 'block';
                currentPage = 'settings'; // 更新当前页面状态
                
                // 更新设置页面的导航状态
                document.querySelectorAll('.nav-item').forEach(item => {
                    item.classList.remove('active');
                });
                document.querySelector('[onclick="showPage(\'settings\')"]').classList.add('active');
                
                // 同步设置页面的语言选择器和更新页面标题
                updateLanguageSwitcher();
                updatePageTitle();
            } else if (pageId === 'project-info') {
                document.getElementById('project-info-page').style.display = 'block';
                currentPage = 'project-info';
                
                // 更新导航状态
                document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
                
                // 更新页面标题
                updatePageTitle();
            } else if (pageId === 'molecular') {
                // 分子模拟页面 - 显示内嵌页面
                document.getElementById('molecular-page').style.display = 'block';
                currentPage = 'molecular'; // 更新当前页面状态
                
                // 更新页面标题
                updatePageTitle();
            } else if (pageId === 'genome') {
                // 基因星云页面 - 显示内嵌页面
                document.getElementById('genome-page').style.display = 'block';
                currentPage = 'genome'; // 更新当前页面状态
                
                // 更新页面标题
                updatePageTitle();
            } else {
                // 其他页面显示空白页面
                document.getElementById('empty-page').style.display = 'flex';
            }
            
            // 更新页面标题 (只对没有特定处理的页面)
            if (pageId !== 'molecular' && pageId !== 'genome' && pageId !== 'settings' && pageId !== 'project-info') {
                const titleElement = document.querySelector('.page-title');
                if (titleElement) {
                    const titleKey = `titles.${pageId.replace('-', '')}`;
                    titleElement.setAttribute('data-i18n', titleKey);
                    if (i18n) {
                        titleElement.textContent = i18n.t(titleKey, pageTitles[pageId] || 'Dashboard');
                    }
                }
                currentPage = pageId;
            }
        }

        function showRAGChat() {
            document.getElementById('dashboard-content').style.display = 'none';
            document.getElementById('rag-chat').style.display = 'flex';
            document.getElementById('settings-page').style.display = 'none';
            document.getElementById('empty-page').style.display = 'none';
            // 更新页面标题
            const titleElement = document.querySelector('.page-title');
            if (titleElement) {
                titleElement.setAttribute('data-i18n', 'titles.ragsystem');
                if (i18n) {
                    titleElement.textContent = i18n.t('titles.ragsystem', 'RAG System');
                }
            }
            
            // 更新当前页面状态
            currentPage = 'rag-system';
            
            // 更新导航状态
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            document.querySelector('[onclick="showPage(\'rag-system\')"]').classList.add('active');
        }

        // 简化的主题切换功能 - 只在深色和浅色间切换
        function toggleTheme() {
            const themeToggle = document.getElementById('themeToggle');
            
            if (currentTheme === 'dark') {
                currentTheme = 'light';
                document.documentElement.setAttribute('data-theme', 'light');
                themeToggle.textContent = '☀️';
            } else {
                currentTheme = 'dark';
                document.documentElement.removeAttribute('data-theme');
                themeToggle.textContent = '🌙';
            }
            
            // 保存主题设置
            localStorage.setItem('theme', currentTheme);
            
            // 同步设置页面的下拉菜单
            const themeSelect = document.getElementById('themeSelect');
            if (themeSelect) {
                themeSelect.value = currentTheme;
            }
        }

        // 设置页面的主题切换
        function changeThemeMode(theme) {
            currentTheme = theme;
            const themeToggle = document.getElementById('themeToggle');
            
            if (theme === 'light') {
                document.documentElement.setAttribute('data-theme', 'light');
                themeToggle.textContent = '☀️';
            } else if (theme === 'dark') {
                document.documentElement.removeAttribute('data-theme');
                themeToggle.textContent = '🌙';
            } else if (theme === 'auto') {
                // 跟随系统主题
                const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                if (prefersDark) {
                    document.documentElement.removeAttribute('data-theme');
                    themeToggle.textContent = '🌙';
                } else {
                    document.documentElement.setAttribute('data-theme', 'light');
                    themeToggle.textContent = '☀️';
                }
            }
            
            // 保存主题设置
            localStorage.setItem('theme', theme);
        }

        // 初始化主题
        function initTheme() {
            const savedTheme = localStorage.getItem('theme') || 'dark';
            currentTheme = savedTheme;
            const themeToggle = document.getElementById('themeToggle');
            const themeSelect = document.getElementById('themeSelect');
            
            if (savedTheme === 'light') {
                document.documentElement.setAttribute('data-theme', 'light');
                themeToggle.textContent = '☀️';
                if (themeSelect) themeSelect.value = 'light';
            } else if (savedTheme === 'dark') {
                document.documentElement.removeAttribute('data-theme');
                themeToggle.textContent = '🌙';
                if (themeSelect) themeSelect.value = 'dark';
            } else if (savedTheme === 'auto') {
                const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                if (prefersDark) {
                    document.documentElement.removeAttribute('data-theme');
                    themeToggle.textContent = '🌙';
                } else {
                    document.documentElement.setAttribute('data-theme', 'light');
                    themeToggle.textContent = '☀️';
                }
                if (themeSelect) themeSelect.value = 'auto';
            }
        }

        // 强制固定侧边栏宽度
        function forceSidebarWidth() {
            const sidebar = document.querySelector('.sidebar');
            if (sidebar) {
                sidebar.style.setProperty('width', '280px', 'important');
                sidebar.style.setProperty('min-width', '280px', 'important');
                sidebar.style.setProperty('max-width', '280px', 'important');
                sidebar.style.setProperty('flex-shrink', '0', 'important');
                sidebar.style.setProperty('overflow', 'hidden', 'important');
            }
            
            console.log('🔧 强制固定侧边栏宽度完成');
        }



        // 侧边栏英文固定功能

        function toggleSidebarEnglish(enabled) {
            window.sidebarEnglishMode = enabled;
            localStorage.setItem('sidebarEnglish', enabled);
            
            if (enabled) {
                // 固定侧边栏为英文
                window.updateSidebarToEnglish();
            } else {
                // 恢复正常国际化
                if (i18n) {
                    i18n.updateElements();
                }
            }
            
            // 无论如何都强制固定侧边栏宽度
            setTimeout(forceSidebarWidth, 100);
        }

        window.updateSidebarToEnglish = function() {
            console.log('🔍 updateSidebarToEnglish 被调用');
            
            const navItems = {
                'dashboard': 'Dashboard',
                'rag-system': 'RAG System', 
                'changlee': 'Changlee',
                'nexus': 'NEXUS',
                'bovine': 'Bovine Insight',
                'chronicle': 'Chronicle',
                'genome': 'Genome Nebula',
                'molecular': 'Kinetic Scope',
                'settings': 'Settings'
            };

            const allNavItems = document.querySelectorAll('.nav-item');
            console.log('🔍 找到的导航项数量:', allNavItems.length);

            document.querySelectorAll('.nav-item').forEach((item, index) => {
                const onclick = item.getAttribute('onclick');
                const pageId = onclick?.match(/showPage\('([^']+)'\)/)?.[1];
                console.log(`🔍 导航项 ${index}:`, { onclick, pageId, hasMapping: !!navItems[pageId] });
                
                if (pageId && navItems[pageId]) {
                    const textElement = item.querySelector('.nav-item-text');
                    console.log(`🔍 文本元素 ${pageId}:`, { 
                        exists: !!textElement, 
                        currentText: textElement?.textContent,
                        newText: navItems[pageId]
                    });
                    
                    if (textElement) {
                        textElement.textContent = navItems[pageId];
                        // 强制应用固定宽度样式，防止文本撑大侧边栏
                        textElement.style.width = '180px';
                        textElement.style.maxWidth = '180px';
                        textElement.style.overflow = 'hidden';
                        textElement.style.textOverflow = 'ellipsis';
                        textElement.style.whiteSpace = 'nowrap';
                        console.log(`✅ 已更新 ${pageId} 为 ${navItems[pageId]}`);
                    }
                }
            });
            
            // 强制固定侧边栏宽度
            const sidebar = document.querySelector('.sidebar');
            if (sidebar) {
                sidebar.style.width = '280px';
                sidebar.style.minWidth = '280px';
                sidebar.style.maxWidth = '280px';
                sidebar.style.flexShrink = '0';
            }
        }

        function initSidebarEnglish() {
            const saved = localStorage.getItem('sidebarEnglish') === 'true';
            const toggle = document.getElementById('sidebarEnglishToggle');
            console.log('🔍 初始化侧边栏英文模式:', { saved, toggleExists: !!toggle });
            
            if (toggle) {
                toggle.checked = saved;
                window.sidebarEnglishMode = saved;
                console.log('🔍 设置侧边栏英文模式:', window.sidebarEnglishMode);
                
                if (saved) {
                    console.log('🔍 调用updateSidebarToEnglish...');
                    window.updateSidebarToEnglish();
                    
                    // 延迟再次应用，确保不被其他代码覆盖
                    setTimeout(() => {
                        if (window.sidebarEnglishMode) {
                            console.log('🔍 延迟重新应用侧边栏英文锁定...');
                            window.updateSidebarToEnglish();
                        }
                    }, 1500);
                }
            }
        }

        async function sendMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // 添加用户消息
            addMessage(message, 'user');
            input.value = '';
            
            // 显示加载状态
            const loadingMessage = addMessage('🤔 正在思考中...', 'assistant');
            
            try {
                // 检查RAG系统状态
                if (window.ragSystemReady === false) {
                    loadingMessage.remove();
                    addMessage('⚠️ RAG系统当前不可用，请等待系统就绪或刷新页面重试。', 'assistant');
                    return;
                }
                
                // 调用RAG系统API (带重试机制)
                let response;
                let lastError;
                const maxRetries = 2;
                
                for (let attempt = 0; attempt <= maxRetries; attempt++) {
                    try {
                        const controller = new AbortController();
                        const timeoutId = setTimeout(() => controller.abort(), RAG_CONFIG.timeout);
                        
                        // 使用动态配置系统发送请求
                        const apiUrl = RAG_CONFIG.baseURL || (window.dynamicConfig ? window.dynamicConfig.getApiEndpoint('rag_api') : 'http://localhost:5000');
                        
                        response = await fetch(`${apiUrl}${RAG_CONFIG.endpoints.chat}`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                message: message,
                                task_name: 'nexus_chat'
                            }),
                            signal: controller.signal
                        });
                        
                        clearTimeout(timeoutId);
                        break; // 成功则跳出重试循环
                        
                    } catch (error) {
                        lastError = error;
                        if (attempt < maxRetries) {
                            console.log(`🔄 重试第 ${attempt + 1} 次...`);
                            await new Promise(resolve => setTimeout(resolve, 1000)); // 等待1秒后重试
                        }
                    }
                }
                
                if (!response) {
                    throw lastError; // 如果所有重试都失败，抛出最后一个错误
                }
                
                const data = await response.json();
                
                // 移除加载消息
                loadingMessage.remove();
                
                if (data.success) {
                    addMessage(data.response, 'assistant');
                } else {
                    addMessage(`❌ 抱歉，处理您的问题时出现错误: ${data.error}`, 'assistant');
                }
                
            } catch (error) {
                // 移除加载消息
                loadingMessage.remove();
                
                console.error('API调用失败:', error);
                
                // 更详细的错误信息
                let errorMessage = '❌ <strong>RAG系统调用失败</strong><br>';
                
                if (error.name === 'AbortError') {
                    errorMessage += '错误类型: 请求超时<br>';
                    errorMessage += `超时时间: ${RAG_CONFIG.timeout/1000}秒<br>`;
                } else if (error.name === 'TypeError' && error.message.includes('fetch')) {
                    errorMessage += '错误类型: 网络连接失败<br>';
                    errorMessage += `服务地址: ${RAG_CONFIG.baseURL}<br>`;
                } else if (error.name === 'SyntaxError') {
                    errorMessage += '错误类型: 服务器响应格式错误<br>';
                } else {
                    errorMessage += `错误类型: ${error.name}<br>`;
                }
                
                errorMessage += `错误详情: ${error.message}<br>`;
                errorMessage += `时间戳: ${new Date().toLocaleString('zh-CN')}<br>`;
                errorMessage += '<br>🔧 <strong>建议操作:</strong><br>';
                errorMessage += '1. 检查网络连接<br>';
                errorMessage += '2. 刷新页面重试<br>';
                errorMessage += '3. 联系系统管理员<br>';
                
                addMessage(errorMessage, 'assistant');
                
                // 标记系统为不可用
                window.ragSystemReady = false;
            }
        }

        // ===== Markdown 渲染核心函数 =====
        
        /**
         * 安全的Markdown渲染函数
         * @param {string} markdownText - 原始Markdown文本
         * @param {Object} options - 渲染选项
         * @returns {string} - 安全的HTML字符串
         */
        function renderMarkdown(markdownText, options = {}) {
            try {
                // 配置marked.js选项
                const markedOptions = {
                    breaks: true,           // 支持换行符转换
                    gfm: true,             // 启用GitHub风格Markdown
                    headerIds: false,      // 禁用标题ID（安全考虑）
                    mangle: false,         // 禁用邮箱混淆
                    sanitize: false,       // 我们使用DOMPurify进行净化
                    ...options
                };

                // 使用marked.js渲染Markdown
                let htmlContent = marked.parse(markdownText, markedOptions);

                // 使用DOMPurify进行XSS防护（安全加固）
                if (typeof DOMPurify !== 'undefined') {
                    htmlContent = DOMPurify.sanitize(htmlContent, {
                        ALLOWED_TAGS: [
                            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                            'p', 'br', 'strong', 'em', 'u', 's', 'del',
                            'code', 'pre', 'blockquote',
                            'ul', 'ol', 'li',
                            'a', 'hr', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
                            'span', 'div'
                        ],
                        ALLOWED_ATTR: ['href', 'title', 'class', 'id'],
                        ALLOW_DATA_ATTR: false,
                        FORBID_SCRIPT: true,
                        FORBID_TAGS: ['script', 'object', 'embed', 'form', 'input'],
                        KEEP_CONTENT: true
                    });
                }

                return htmlContent;
            } catch (error) {
                console.warn('🚨 Markdown渲染失败，回退到纯文本:', error);
                // 渲染失败时回退到安全的纯文本显示
                return markdownText.replace(/</g, '&lt;').replace(/>/g, '&gt;');
            }
        }

        /**
         * 检测文本是否包含Markdown语法
         * @param {string} text - 待检测的文本
         * @returns {boolean} - 是否包含Markdown语法
         */
        function containsMarkdown(text) {
            const markdownPatterns = [
                /#{1,6}\s/,                    // 标题
                /\*\*.*?\*\*/,                 // 粗体
                /\*.*?\*/,                     // 斜体
                /`.*?`/,                       // 行内代码
                /```[\s\S]*?```/,              // 代码块
                /^\s*[-*+]\s/m,                // 无序列表
                /^\s*\d+\.\s/m,                // 有序列表
                /^\s*>\s/m,                    // 引用
                /\[.*?\]\(.*?\)/,              // 链接
                /^\s*\|.*\|/m,                 // 表格
                /^\s*---+\s*$/m,               // 分隔线
                /<(strong|em|code|pre|h[1-6]|ul|ol|li|blockquote|a|br|p)(\s[^>]*)?>.*?<\/\1>/i, // HTML标签
                /<br\s*\/?>/i,                 // 单独的br标签
                /\s{2,}$/m                     // 行尾双空格（Markdown换行）
            ];
            
            return markdownPatterns.some(pattern => pattern.test(text));
        }

        // ===== 升级后的消息添加函数 =====
        
        function addMessage(content, sender) {
            const messagesContainer = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            
            const avatar = sender === 'user' ? '👤' : '🧠';
            
            // 🔥 核心升级：智能Markdown渲染
            let processedContent;
            
            if (sender === 'assistant' && containsMarkdown(content)) {
                // AI回复且包含Markdown语法 -> 渲染为富文本
                processedContent = renderMarkdown(content);
                console.log('🎨 Markdown渲染已应用');
            } else {
                // 用户消息或纯文本 -> 保持原样（但转义HTML）
                processedContent = content.replace(/</g, '&lt;').replace(/>/g, '&gt;');
            }
            
            messageDiv.innerHTML = `
                <div class="message-avatar">${avatar}</div>
                <div class="message-content">${processedContent}</div>
            `;
            
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            
            // 自动保存聊天记录
            saveChatHistory();
            
            // 返回消息元素，以便后续操作
            return messageDiv;
        }

        // 功能菜单控制
        function toggleFunctionMenu() {
            const menu = document.getElementById('functionMenu');
            const btn = document.getElementById('functionBtn');
            
            if (menu.classList.contains('show')) {
                menu.classList.remove('show');
                btn.classList.remove('active');
            } else {
                menu.classList.add('show');
                btn.classList.add('active');
            }
        }

        // 点击其他地方关闭菜单
        document.addEventListener('click', function(event) {
            const menu = document.getElementById('functionMenu');
            const btn = document.getElementById('functionBtn');
            
            if (!btn.contains(event.target) && !menu.contains(event.target)) {
                menu.classList.remove('show');
                btn.classList.remove('active');
            }
        });

        // 功能菜单项
        async function uploadFile() {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '*/*'; // 支持所有文件类型
            input.multiple = true; // 支持多文件上传
            input.onchange = async function(e) {
                const files = Array.from(e.target.files);
                if (files.length === 0) return;
                
                // 显示上传的文件
                files.forEach(file => {
                    let icon = '📁';
                    if (file.type.startsWith('image/')) {
                        icon = '🖼️';
                    } else if (file.type.includes('pdf')) {
                        icon = '📄';
                    } else if (file.type.includes('document') || file.type.includes('word')) {
                        icon = '📝';
                    } else if (file.name.endsWith('.md') || file.name.endsWith('.markdown')) {
                        icon = '📋';
                    } else if (file.name.endsWith('.txt')) {
                        icon = '📄';
                    } else if (file.name.match(/\.(py|js|html|css|json|xml|yml|yaml)$/)) {
                        icon = '💻';
                    }
                    addMessage(`${icon} 正在上传文件: ${file.name}`, 'user');
                });
                
                // 显示处理状态
                const processingMessage = addMessage('📤 正在处理文件，请稍等...', 'assistant');
                
                try {
                    // 逐个上传文件（后端只支持单文件上传）
                    let successCount = 0;
                    let errorCount = 0;
                    
                    for (const file of files) {
                        try {
                            // 检查文件大小（50MB限制）
                            const maxSize = 50 * 1024 * 1024; // 50MB
                            if (file.size > maxSize) {
                                errorCount++;
                                addMessage(`❌ ${file.name} 文件过大: ${(file.size / (1024*1024)).toFixed(2)}MB > 50MB`, 'assistant');
                                continue;
                            }
                            
                            // 显示文件信息
                            addMessage(`📤 正在上传 ${file.name} (${(file.size / 1024).toFixed(1)}KB)...`, 'assistant');
                            
                            // 创建FormData
                            const formData = new FormData();
                            formData.append('file', file); // 使用'file'而不是'files'
                            
                            // 调用上传API
                            const controller = new AbortController();
                            const timeoutId = setTimeout(() => controller.abort(), RAG_CONFIG.timeout * 3); // 上传需要更长时间
                            
                            const response = await fetch(`${RAG_CONFIG.baseURL}${RAG_CONFIG.endpoints.upload}`, {
                                method: 'POST',
                                body: formData,
                                signal: controller.signal
                            });
                            
                            clearTimeout(timeoutId);
                            
                            if (!response.ok) {
                                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                            }
                            
                            const data = await response.json();
                            
                            if (data.success) {
                                successCount++;
                                addMessage(`✅ ${file.name} 上传成功！(${data.document.chunks_count}个文本块)`, 'assistant');
                            } else {
                                errorCount++;
                                addMessage(`❌ ${file.name} 处理失败: ${data.error}`, 'assistant');
                            }
                            
                            // 添加延迟避免并发问题
                            await new Promise(resolve => setTimeout(resolve, 500));
                            
                        } catch (fileError) {
                            errorCount++;
                            console.error(`文件 ${file.name} 上传失败:`, fileError);
                            
                            let errorMsg = fileError.message;
                            if (fileError.name === 'AbortError') {
                                errorMsg = '上传超时，请检查网络连接或文件大小';
                            } else if (errorMsg.includes('Failed to fetch')) {
                                errorMsg = '网络连接失败，请检查网络状态后重试';
                            }
                            
                            addMessage(`❌ ${file.name} 上传失败: ${errorMsg}`, 'assistant');
                        }
                    }
                    
                    // 移除处理消息
                    processingMessage.remove();
                    
                    // 显示总结
                    if (successCount > 0) {
                        addMessage(`🎉 成功上传 ${successCount} 个文件！现在可以向我提问相关内容了。`, 'assistant');
                    }
                    if (errorCount > 0) {
                        addMessage(`⚠️ ${errorCount} 个文件上传失败，请检查文件格式和大小。`, 'assistant');
                    }
                    
                } catch (error) {
                    // 移除处理消息
                    processingMessage.remove();
                    
                    console.error('文件上传失败:', error);
                    addMessage('❌ 文件上传失败，请确保后端服务正在运行。', 'assistant');
                }
            };
            input.click();
            toggleFunctionMenu();
        }



        function recordAudio() {
            addMessage('🎤 语音输入功能开发中...', 'user');
            setTimeout(() => {
                addMessage('语音输入功能即将上线，敬请期待！', 'assistant');
            }, 500);
            toggleFunctionMenu();
        }

        // 重新连接RAG系统
        async function reconnectRAG() {
            addMessage('🔄 正在重新连接RAG系统...', 'assistant');
            
            // 重置连接状态
            window.ragSystemReady = undefined;
            
            // 重新测试连接
            await testRAGConnection();
            
            toggleFunctionMenu();
        }

        async function clearChat() {
            try {
                // 调用清空API
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), RAG_CONFIG.timeout);
                
                const response = await fetch(`${RAG_CONFIG.baseURL}${RAG_CONFIG.endpoints.clear}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        task_name: 'nexus_chat'
                    }),
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);
                
                const data = await response.json();
                
                if (data.success) {
                    // 清空前端聊天记录
                    const messagesContainer = document.getElementById('chatMessages');
                    messagesContainer.innerHTML = `
                        <div class="message">
                            <div class="message-avatar">🧠</div>
                            <div class="message-content">
                                你好！我是RAG智能助手，可以帮你分析文档、回答问题。<br><br>📋 支持格式：Markdown (.md), 文本 (.txt), 代码文件 (.py, .js, .html, .css), 配置文件 (.json, .xml, .yml) 等<br><br>请上传文档或直接提问！
                            </div>
                        </div>
                    `;
                    
                    // 清空本地存储
                    clearChatHistory();
                    
                    addMessage('✅ 聊天记录已清空', 'assistant');
                } else {
                    addMessage(`❌ 清空失败: ${data.error}`, 'assistant');
                }
                
            } catch (error) {
                console.error('清空聊天记录失败:', error);
                addMessage('❌ 清空聊天记录失败，请确保后端服务正在运行。', 'assistant');
            }
            
            toggleFunctionMenu();
        }

        // RAG系统配置 - 使用动态配置系统
        const RAG_CONFIG = {
            baseURL: null, // 将由动态配置系统设置
            fallbackURLs: [
                'http://localhost:5000',
                'http://127.0.0.1:5000',
                `${window.location.protocol}//${window.location.hostname}:5000`
            ],
            endpoints: {
                health: '/api/health',
                chat: '/api/chat',
                history: '/api/history',
                upload: '/api/upload',
                clear: '/api/clear'
            },
            timeout: 60000
        };
        
        // 动态配置加载完成后更新RAG配置
        window.addEventListener('configLoaded', (event) => {
            const config = event.detail;
            if (config.apiEndpoints && config.apiEndpoints.rag_api) {
                RAG_CONFIG.baseURL = config.apiEndpoints.rag_api;
                console.log('✅ RAG配置已更新:', RAG_CONFIG.baseURL);
                
                // 如果RAG聊天界面已打开，重新检查连接
                if (currentPage === 'rag-system') {
                    checkRAGConnection();
                }
            }
        });

        // 状态框显示控制
        let statusTimeout = null;
        
        // 显示连接状态
        function showConnectionStatus() {
            const statusBar = document.getElementById('connectionStatus');
            statusBar.classList.add('show');
            
            // 清除之前的自动隐藏定时器
            if (statusTimeout) {
                clearTimeout(statusTimeout);
                statusTimeout = null;
            }
        }
        
        // 隐藏连接状态
        function hideConnectionStatus() {
            const statusBar = document.getElementById('connectionStatus');
            statusBar.classList.remove('show');
        }
        
        // 自动隐藏连接状态（仅在成功时）
        function autoHideConnectionStatus(delay = 3000) {
            if (statusTimeout) {
                clearTimeout(statusTimeout);
            }
            statusTimeout = setTimeout(() => {
                hideConnectionStatus();
            }, delay);
        }
        
        // 更新连接状态显示
        function updateConnectionStatus(status, message, details = '') {
            // 只在RAG系统页面显示状态框
            if (currentPage !== 'rag-system') {
                return;
            }
            
            const statusBar = document.getElementById('connectionStatus');
            const statusDot = statusBar.querySelector('.status-dot');
            const statusText = statusBar.querySelector('.status-text');
            const statusDetails = document.getElementById('statusDetails');
            
            // 清除所有状态类
            statusBar.className = 'connection-status show';
            
            switch (status) {
                case 'connecting':
                    statusBar.classList.add('warning');
                    statusDot.textContent = '🔄';
                    showConnectionStatus();
                    break;
                case 'connected':
                    statusBar.classList.add('connected');
                    statusDot.textContent = '✅';
                    showConnectionStatus();
                    // 成功连接后3秒自动隐藏
                    autoHideConnectionStatus(3000);
                    break;
                case 'error':
                    statusBar.classList.add('error');
                    statusDot.textContent = '❌';
                    showConnectionStatus();
                    // 错误状态不自动隐藏，需要用户手动关闭
                    break;
                case 'warning':
                    statusBar.classList.add('warning');
                    statusDot.textContent = '⚠️';
                    showConnectionStatus();
                    break;
            }
            
            statusText.textContent = message;
            statusDetails.textContent = details;
        }

        // 尝试连接到指定URL
        async function tryConnectToURL(baseURL) {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), RAG_CONFIG.timeout);
            
            try {
                const response = await fetch(`${baseURL}${RAG_CONFIG.endpoints.health}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);
                
                if (response.ok) {
                    const data = await response.json();
                    return { success: true, data, baseURL };
                } else {
                    return { success: false, error: `HTTP ${response.status}: ${response.statusText}`, baseURL };
                }
            } catch (error) {
                clearTimeout(timeoutId);
                return { success: false, error: error.message, baseURL };
            }
        }

        // 测试RAG系统连接
        async function testRAGConnection() {
            console.log('🔍 开始测试RAG系统连接...');
            updateConnectionStatus('connecting', '正在连接RAG系统...', '尝试多个服务器地址...');
            
            // 构建要尝试的URL列表
            const urlsToTry = [RAG_CONFIG.baseURL, ...RAG_CONFIG.fallbackURLs.filter(url => url !== RAG_CONFIG.baseURL)];
            
            console.log('🔗 尝试连接的URL:', urlsToTry);
            
            for (let i = 0; i < urlsToTry.length; i++) {
                const currentURL = urlsToTry[i];
                console.log(`🔄 尝试连接 ${i + 1}/${urlsToTry.length}: ${currentURL}`);
                
                updateConnectionStatus('connecting', 
                    `正在连接RAG系统... (${i + 1}/${urlsToTry.length})`,
                    `当前尝试: ${currentURL}`
                );
                
                const result = await tryConnectToURL(currentURL);
                
                if (result.success) {
                    console.log('✅ RAG系统连接成功:', result.data);
                    
                    // 更新配置为成功的URL
                    RAG_CONFIG.baseURL = result.baseURL;
                    
                    // 更新状态栏
                    updateConnectionStatus('connected', 
                        `RAG系统已就绪 (${result.data.chat_history_count}条历史, ${result.data.documents_count}个文档)`,
                        `前端地址: ${window.location.origin}\nAPI地址: ${result.baseURL}\n系统时间: ${new Date().toLocaleString('zh-CN')}`
                    );
                    
                    // 显示系统状态（仅在首次连接时）
                    if (window.ragSystemReady === undefined) {
                        addMessage(`🎉 **RAG系统已就绪**

📊 聊天历史: ${result.data.chat_history_count} 条  
📚 文档数量: ${result.data.documents_count} 个  
🕒 系统时间: ${new Date().toLocaleString('zh-CN')}  
🌐 前端地址: ${window.location.origin}  
💡 您可以开始与AI助手对话了！`, 'assistant');
                    }
                    
                    // 设置连接状态
                    window.ragSystemReady = true;
                    return;
                }
                
                console.log(`❌ 连接失败 ${currentURL}:`, result.error);
            }
            
            // 所有URL都失败了
            console.error('❌ 所有RAG服务器地址都无法连接');
            
            updateConnectionStatus('error', 'RAG系统连接失败', 
                `已尝试 ${urlsToTry.length} 个服务器地址\n\n🔧 快速解决方案:\n1. 运行: python start_rag_tunnel.py\n2. 等待隧道URL显示\n3. 刷新页面或点击重新连接\n\n点击 ✕ 关闭此提示`
            );
            
            let errorMessage = '⚠️ <strong>RAG系统连接异常</strong><br>';
            errorMessage += '错误类型: 网络连接失败<br>';
            errorMessage += `错误详情: 无法连接到任何RAG服务器<br>`;
            errorMessage += `尝试的地址: ${urlsToTry.join(', ')}<br>`;
            errorMessage += `当前页面: ${window.location.href}<br>`;
            errorMessage += '<br>🚀 <strong>快速解决方案:</strong><br>';
            errorMessage += '1. 在终端运行: <code>python start_rag_tunnel.py</code><br>';
            errorMessage += '2. 等待显示隧道URL<br>';
            errorMessage += '3. 刷新页面或点击功能菜单中的"重新连接"<br>';
            errorMessage += '<br>🔧 <strong>其他解决方案:</strong><br>';
            errorMessage += '• 本地访问: <a href="http://localhost:52943/systems/nexus/nexus-dashboard-restored.html" target="_blank">http://localhost:52943</a><br>';
            errorMessage += '• 手动启动隧道: <code>cloudflared tunnel --url http://localhost:5000</code><br>';
            errorMessage += '• 查看详细指南: TUNNEL_ACCESS_GUIDE.md<br>';
            errorMessage += '<br>💡 您仍可以使用其他功能，但AI对话功能暂时不可用。';
            
            addMessage(errorMessage, 'assistant');
            
            // 设置连接状态
            window.ragSystemReady = false;
        }

        // AI状态检查函数
        async function checkAIStatus() {
            const statusElement = document.getElementById('aiStatusInfo');
            if (!statusElement) return;
            
            try {
                // 检查中央能源API
                const energyResponse = await fetch('http://localhost:56420/api/energy/health');
                const energyData = await energyResponse.json();
                
                // 检查动态RAG API
                const ragResponse = await fetch('http://localhost:60010/api/health');
                const ragData = await ragResponse.json();
                
                if (energyData.status === 'healthy' && ragData.status === 'healthy') {
                    statusElement.innerHTML = i18n ? i18n.t('settings.aiOnline') : '✅ AI系统运行正常';
                    statusElement.style.color = 'var(--success-color)';
                } else {
                    statusElement.innerHTML = i18n ? i18n.t('settings.aiPartial') : '⚠️ AI系统部分异常';
                    statusElement.style.color = 'var(--warning-color)';
                }
            } catch (error) {
                statusElement.innerHTML = i18n ? i18n.t('settings.aiOffline') : '❌ AI系统离线';
                statusElement.style.color = 'var(--error-color)';
            }
        }

        // AI配置管理系统
        class AIConfigManager {
            constructor() {
                this.energyApiUrl = 'http://localhost:56420';  // 中央能源API地址
                this.currentUserId = 'default_user';  // 当前用户ID
                this.currentProjectId = 'default';    // 当前项目ID
                this.availableModels = {};
                this.userConfigs = [];
                
                this.initEventListeners();
                this.loadAvailableModels();
            }
            
            initEventListeners() {
                // AI配置按钮点击事件 - 注释掉，因为我们使用onclick属性
                // document.getElementById('aiConfigBtn').addEventListener('click', () => {
                //     this.showConfigModal();
                // });
                
                // 关闭模态框
                document.getElementById('aiConfigClose').addEventListener('click', () => {
                    this.hideConfigModal();
                });
                
                // 点击模态框背景关闭
                document.getElementById('aiConfigModal').addEventListener('click', (e) => {
                    if (e.target.id === 'aiConfigModal') {
                        this.hideConfigModal();
                    }
                });
                
                // 提供商选择变化
                document.getElementById('providerSelect').addEventListener('change', () => {
                    this.updateModelOptions();
                });
                
                // 保存配置
                document.getElementById('saveConfigBtn').addEventListener('click', () => {
                    this.saveConfig();
                });
                
                // 测试配置
                document.getElementById('testConfigBtn').addEventListener('click', () => {
                    this.testConfig();
                });
            }
            
            async loadAvailableModels() {
                try {
                    const response = await fetch(`${this.energyApiUrl}/api/energy/models/available`);
                    const data = await response.json();
                    
                    if (data.success) {
                        this.availableModels = data.models;
                        this.updateModelOptions();
                    }
                } catch (error) {
                    console.error('加载可用模型失败:', error);
                }
            }
            
            updateModelOptions() {
                const providerSelect = document.getElementById('providerSelect');
                const modelSelect = document.getElementById('modelSelect');
                const selectedProvider = providerSelect.value;
                
                // 清空现有选项
                modelSelect.innerHTML = '';
                
                // 添加对应提供商的模型选项
                if (this.availableModels[selectedProvider]) {
                    this.availableModels[selectedProvider].forEach(model => {
                        const option = document.createElement('option');
                        option.value = model;
                        option.textContent = this.getModelDisplayName(model);
                        modelSelect.appendChild(option);
                    });
                }
            }
            
            getModelDisplayName(model) {
                const displayNames = {
                    'gemini-2.0-flash-exp': 'Gemini 2.0 Flash (实验版)',
                    'gemini-1.5-pro': 'Gemini 1.5 Pro',
                    'gemini-1.5-flash': 'Gemini 1.5 Flash',
                    'gpt-4': 'GPT-4',
                    'gpt-4-turbo': 'GPT-4 Turbo',
                    'gpt-3.5-turbo': 'GPT-3.5 Turbo',
                    'claude-3-opus': 'Claude 3 Opus',
                    'claude-3-sonnet': 'Claude 3 Sonnet',
                    'claude-3-haiku': 'Claude 3 Haiku'
                };
                return displayNames[model] || model;
            }
            
            async showConfigModal() {
                document.getElementById('aiConfigModal').classList.add('show');
                await this.loadUserConfigs();
                this.renderConfigList();
            }
            
            hideConfigModal() {
                document.getElementById('aiConfigModal').classList.remove('show');
            }
            
            async loadUserConfigs() {
                try {
                    const response = await fetch(
                        `${this.energyApiUrl}/api/energy/config/list?user_id=${this.currentUserId}`
                    );
                    const data = await response.json();
                    
                    if (data.success) {
                        this.userConfigs = data.configs;
                    }
                } catch (error) {
                    console.error('加载用户配置失败:', error);
                    this.userConfigs = [];
                }
            }
            
            renderConfigList() {
                const container = document.getElementById('configListContainer');
                
                if (this.userConfigs.length === 0) {
                    container.innerHTML = `
                        <div style="text-align: center; padding: 40px; color: var(--text-muted);">
                            <div style="font-size: 48px; margin-bottom: 16px;">🤖</div>
                            <div>${window.i18n ? window.i18n.t('settings.noConfigs') : '还没有保存的AI配置'}</div>
                            <div style="font-size: 12px; margin-top: 8px;">${window.i18n ? window.i18n.t('settings.addFirstConfig') : '添加您的第一个AI模型配置'}</div>
                        </div>
                    `;
                    return;
                }
                
                container.innerHTML = this.userConfigs.map(config => `
                    <div class="config-item">
                        <div class="config-item-header">
                            <div class="config-item-title">
                                <span class="provider-badge">${config.provider}</span>
                                ${config.model_name}
                                ${config.is_active ? `<span class="status-badge active">${window.i18n ? window.i18n.t('settings.configActive') : '●活跃'}</span>` : `<span class="status-badge inactive">${window.i18n ? window.i18n.t('settings.configInactive') : '●停用'}</span>`}
                            </div>
                            <div class="config-item-actions">
                                <button class="config-item-btn ${config.is_active ? 'active' : ''}" 
                                        onclick="aiConfigManager.toggleConfig('${config.config_id}')"
                                        title="${config.is_active ? (window.i18n ? window.i18n.t('settings.deactivateConfig') : '停用') : (window.i18n ? window.i18n.t('settings.activateConfig') : '启用')}">
                                    ${config.is_active ? '●' : '○'}
                                </button>
                                <button class="config-item-btn" 
                                        onclick="aiConfigManager.editConfig('${config.config_id}')"
                                        title="${window.i18n ? window.i18n.t('settings.editConfig') : '编辑'}">
                                    ✏️
                                </button>
                                <button class="config-item-btn" 
                                        onclick="aiConfigManager.deleteConfig('${config.config_id}')"
                                        title="${window.i18n ? window.i18n.t('settings.deleteConfig') : '删除'}">
                                    🗑️
                                </button>
                            </div>
                        </div>
                        <div class="config-item-info">
                            <div>作用域: ${this.getScopeDisplayName(config.scope)}</div>
                            <div>优先级: ${config.priority}</div>
                            <div>使用次数: ${config.usage_count}</div>
                            <div>API密钥: ${config.api_key_masked}</div>
                            ${config.last_used ? `<div>最后使用: ${new Date(config.last_used * 1000).toLocaleString()}</div>` : ''}
                            ${config.description ? `<div>描述: ${config.description}</div>` : ''}
                        </div>
                    </div>
                `).join('');
            }
            
            getScopeDisplayName(scope) {
                const scopeNames = {
                    'global': '全局生效',
                    'user': '用户级别',
                    'project': '项目级别'
                };
                return scopeNames[scope] || scope;
            }
            
            async saveConfig() {
                const formData = {
                    user_id: this.currentUserId,
                    project_id: this.currentProjectId,
                    provider: document.getElementById('providerSelect').value,
                    model_name: document.getElementById('modelSelect').value,
                    api_key: document.getElementById('apiKeyInput').value,
                    api_endpoint: document.getElementById('apiEndpointInput').value || '',
                    scope: document.getElementById('scopeSelect').value,
                    priority: parseInt(document.getElementById('priorityInput').value) || 0,
                    max_tokens: parseInt(document.getElementById('maxTokensInput').value) || 4096,
                    temperature: parseFloat(document.getElementById('temperatureInput').value) || 0.7,
                    description: document.getElementById('descriptionInput').value || ''
                };
                
                // 验证必需字段
                if (!formData.api_key) {
                    alert('请输入API密钥');
                    return;
                }
                
                try {
                    const response = await fetch(`${this.energyApiUrl}/api/energy/config`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(formData)
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        alert('配置保存成功！');
                        this.clearForm();
                        await this.loadUserConfigs();
                        this.renderConfigList();
                    } else {
                        alert(`保存失败: ${data.error}`);
                    }
                } catch (error) {
                    console.error('保存配置失败:', error);
                    alert('保存失败，请检查网络连接');
                }
            }
            
            async testConfig() {
                const formData = {
                    provider: document.getElementById('providerSelect').value,
                    model_name: document.getElementById('modelSelect').value,
                    api_key: document.getElementById('apiKeyInput').value
                };
                
                if (!formData.api_key) {
                    alert('请先输入API密钥');
                    return;
                }
                
                try {
                    const response = await fetch(`${this.energyApiUrl}/api/energy/test`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(formData)
                    });
                    
                    const data = await response.json();
                    
                    if (data.success && data.test_result.valid) {
                        alert('✅ API密钥测试成功！');
                    } else {
                        alert('❌ API密钥测试失败，请检查密钥是否正确');
                    }
                } catch (error) {
                    console.error('测试配置失败:', error);
                    alert('测试失败，请检查网络连接');
                }
            }
            
            async toggleConfig(configId) {
                try {
                    const config = this.userConfigs.find(c => c.config_id === configId);
                    if (!config) return;
                    
                    const response = await fetch(`${this.energyApiUrl}/api/energy/config/${configId}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            is_active: !config.is_active
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        await this.loadUserConfigs();
                        this.renderConfigList();
                    } else {
                        alert(`操作失败: ${data.error}`);
                    }
                } catch (error) {
                    console.error('切换配置状态失败:', error);
                    alert('操作失败，请检查网络连接');
                }
            }
            
            async deleteConfig(configId) {
                if (!confirm('确定要删除这个配置吗？此操作不可撤销。')) {
                    return;
                }
                
                try {
                    const response = await fetch(`${this.energyApiUrl}/api/energy/config/${configId}`, {
                        method: 'DELETE'
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        alert('配置删除成功');
                        await this.loadUserConfigs();
                        this.renderConfigList();
                    } else {
                        alert(`删除失败: ${data.error}`);
                    }
                } catch (error) {
                    console.error('删除配置失败:', error);
                    alert('删除失败，请检查网络连接');
                }
            }
            
            editConfig(configId) {
                const config = this.userConfigs.find(c => c.config_id === configId);
                if (!config) return;
                
                // 填充表单
                document.getElementById('providerSelect').value = config.provider;
                this.updateModelOptions();
                setTimeout(() => {
                    document.getElementById('modelSelect').value = config.model_name;
                }, 100);
                document.getElementById('apiKeyInput').value = ''; // 不显示现有密钥
                document.getElementById('apiEndpointInput').value = config.api_endpoint;
                document.getElementById('scopeSelect').value = config.scope;
                document.getElementById('priorityInput').value = config.priority;
                document.getElementById('maxTokensInput').value = config.max_tokens;
                document.getElementById('temperatureInput').value = config.temperature;
                document.getElementById('descriptionInput').value = config.description;
                
                // 滚动到表单顶部
                document.getElementById('configForm').scrollIntoView({ behavior: 'smooth' });
            }
            
            clearForm() {
                document.getElementById('providerSelect').value = 'google';
                this.updateModelOptions();
                document.getElementById('apiKeyInput').value = '';
                document.getElementById('apiEndpointInput').value = '';
                document.getElementById('scopeSelect').value = 'user';
                document.getElementById('priorityInput').value = '0';
                document.getElementById('maxTokensInput').value = '4096';
                document.getElementById('temperatureInput').value = '0.7';
                document.getElementById('descriptionInput').value = '';
            }
            
            // 获取最佳配置（供RAG系统使用）
            async getBestConfig() {
                try {
                    const response = await fetch(
                        `${this.energyApiUrl}/api/energy/config/best?user_id=${this.currentUserId}&project_id=${this.currentProjectId}`
                    );
                    const data = await response.json();
                    
                    if (data.success) {
                        return data.config;
                    }
                } catch (error) {
                    console.error('获取最佳配置失败:', error);
                }
                return null;
            }
        }
        
        // 全局AI配置管理器实例
        let aiConfigManager;

        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {
            initTheme();
            
            // 恢复聊天记录
            setTimeout(() => {
                const restored = loadChatHistory();
                if (restored) {
                    console.log('📚 聊天记录已恢复');
                }
            }, 500); // 延迟500ms确保DOM完全加载
            
            // 测试RAG系统连接
            setTimeout(() => {
                testRAGConnection();
            }, 1000);
            
            // 监听系统主题变化（仅在auto模式下）
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
                if (currentTheme === 'auto') {
                    const themeToggle = document.getElementById('themeToggle');
                    if (e.matches) {
                        document.documentElement.removeAttribute('data-theme');
                        themeToggle.textContent = '🌙';
                    } else {
                        document.documentElement.setAttribute('data-theme', 'light');
                        themeToggle.textContent = '☀️';
                    }
                }
            });
        });

        // 回车发送消息
        document.addEventListener('DOMContentLoaded', function() {
            const chatInput = document.getElementById('chatInput');
            if (chatInput) {
                chatInput.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        sendMessage();
                    }
                });
            }
        });

        // 🌐 国际化初始化
        function initializeI18n() {
            try {
                console.log('🌐 开始初始化国际化系统...');
                console.log('🌐 LANGUAGES对象存在:', typeof LANGUAGES !== 'undefined');
                console.log('🌐 initI18n函数存在:', typeof initI18n === 'function');
                
                i18n = initI18n();
                window.i18n = i18n; // 确保全局可访问
                if (i18n) {
                    console.log('🌐 国际化系统初始化成功');
                    console.log('🌐 当前语言:', i18n.getCurrentLanguage());
                    console.log('🌐 测试AI翻译键:');
                    console.log('  - settings.ai:', i18n.t('settings.ai'));
                    console.log('  - settings.aiConfig:', i18n.t('settings.aiConfig'));
                    console.log('  - settings.aiOffline:', i18n.t('settings.aiOffline'));
                    
                    // 更新语言切换器显示
                    updateLanguageSwitcher();
                    
                    // 监听语言变化
                    i18n.addObserver((language) => {
                        console.log(`🌐 语言切换到: ${language}`);
                        updateLanguageSwitcher();
                        updatePageTitle();
                    });
                } else {
                    console.warn('🌐 国际化系统初始化失败');
                }
            } catch (error) {
                console.error('🌐 国际化系统初始化错误:', error);
            }
        }

        // 更新语言切换器显示
        function updateLanguageSwitcher() {
            if (!i18n) return;
            
            const currentLang = i18n.getCurrentLanguage();
            const langData = LANGUAGES[currentLang];
            
            if (langData) {
                const flagElement = document.querySelector('.language-flag');
                const nameElement = document.querySelector('.language-name');
                
                if (flagElement) flagElement.textContent = langData.flag;
                if (nameElement) nameElement.textContent = langData.name;
                
                // 更新下拉选项的激活状态
                document.querySelectorAll('.language-option').forEach(option => {
                    option.classList.remove('active');
                    if (option.dataset.lang === currentLang) {
                        option.classList.add('active');
                    }
                });
                
                // 同步设置页面的语言选择器
                const languageSelect = document.getElementById('languageSelect');
                if (languageSelect) {
                    languageSelect.value = currentLang;
                }
            }
        }
        
        // 从设置页面切换语言
        function changeLanguageFromSettings(language) {
            if (i18n) {
                console.log(`🌐 从设置页面切换语言到: ${language}`);
                
                // 立即强制固定宽度
                forceSidebarWidth();
                
                i18n.switchLanguage(language);
                
                // 语言切换后多次强制固定侧边栏宽度
                setTimeout(forceSidebarWidth, 50);
                setTimeout(forceSidebarWidth, 200);
                setTimeout(forceSidebarWidth, 500);
            }
        }

        // 更新页面标题
        function updatePageTitle() {
            const titleElement = document.querySelector('.page-title');
            if (titleElement && currentPage && window.i18n && window.LANGUAGES) {
                try {
                    const currentLang = window.i18n.getCurrentLanguage();
                    const translations = window.LANGUAGES[currentLang];
                    
                    // 映射页面ID到标题key
                    let titleKey = null;
                    if (currentPage === 'molecular') {
                        titleKey = 'molecular';
                    } else if (currentPage === 'genome') {
                        titleKey = 'genome';
                    } else if (currentPage === 'dashboard') {
                        titleKey = 'dashboard';
                    }
                    
                    if (titleKey && translations && translations.titles && translations.titles[titleKey]) {
                        titleElement.textContent = translations.titles[titleKey];
                    } else {
                        // 使用默认标题
                        titleElement.textContent = pageTitles[currentPage] || '仪表板';
                    }
                } catch (error) {
                    console.warn('⚠️ 更新页面标题失败:', error);
                    titleElement.textContent = pageTitles[currentPage] || '仪表板';
                }
            } else if (titleElement && currentPage) {
                // 如果新系统不可用，使用默认标题
                titleElement.textContent = pageTitles[currentPage] || '仪表板';
            }
        }

        // 📱 移动端菜单功能
        function initializeMobileMenu() {
            const mobileMenuBtn = document.getElementById('mobileMenuBtn');
            const sidebar = document.querySelector('.sidebar');
            const mobileOverlay = document.getElementById('mobileOverlay');
            
            if (!mobileMenuBtn || !sidebar || !mobileOverlay) return;
            
            // 汉堡菜单点击事件
            mobileMenuBtn.addEventListener('click', function() {
                const isOpen = sidebar.classList.contains('mobile-open');
                
                if (isOpen) {
                    closeMobileMenu();
                } else {
                    openMobileMenu();
                }
            });
            
            // 遮罩层点击关闭菜单
            mobileOverlay.addEventListener('click', closeMobileMenu);
            
            // 侧边栏导航项点击后关闭菜单
            document.querySelectorAll('.nav-item').forEach(item => {
                item.addEventListener('click', () => {
                    if (window.innerWidth <= 768) {
                        setTimeout(closeMobileMenu, 150); // 延迟关闭，让页面切换动画先执行
                    }
                });
            });
            
            // 监听窗口大小变化
            window.addEventListener('resize', function() {
                if (window.innerWidth > 768) {
                    closeMobileMenu();
                }
            });
        }

        // 打开移动端菜单
        function openMobileMenu() {
            const mobileMenuBtn = document.getElementById('mobileMenuBtn');
            const sidebar = document.querySelector('.sidebar');
            const mobileOverlay = document.getElementById('mobileOverlay');
            
            mobileMenuBtn.classList.add('active');
            sidebar.classList.add('mobile-open');
            mobileOverlay.style.display = 'block';
            
            // 延迟显示遮罩层动画
            setTimeout(() => {
                mobileOverlay.classList.add('show');
            }, 10);
            
            // 防止背景滚动
            document.body.style.overflow = 'hidden';
        }

        // 关闭移动端菜单
        function closeMobileMenu() {
            const mobileMenuBtn = document.getElementById('mobileMenuBtn');
            const sidebar = document.querySelector('.sidebar');
            const mobileOverlay = document.getElementById('mobileOverlay');
            
            mobileMenuBtn.classList.remove('active');
            sidebar.classList.remove('mobile-open');
            mobileOverlay.classList.remove('show');
            
            // 延迟隐藏遮罩层
            setTimeout(() => {
                mobileOverlay.style.display = 'none';
            }, 300);
            
            // 恢复背景滚动
            document.body.style.overflow = '';
        }

        // 🌐 语言切换功能
        function initializeLanguageSwitcher() {
            const languageBtn = document.getElementById('languageBtn');
            const languageDropdown = document.getElementById('languageDropdown');
            const languageOptions = document.querySelectorAll('.language-option');
            
            if (!languageBtn || !languageDropdown) return;
            
            // 语言按钮点击事件
            languageBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                languageDropdown.classList.toggle('show');
            });
            
            // 语言选项点击事件
            languageOptions.forEach(option => {
                option.addEventListener('click', function() {
                    const selectedLang = this.dataset.lang;
                    console.log('🌐 点击语言选项:', selectedLang);
                    console.log('🌐 i18n对象存在:', !!i18n);
                    
                    if (i18n && selectedLang) {
                        console.log('🌐 开始切换语言到:', selectedLang);
                        
                        // 立即强制固定宽度
                        forceSidebarWidth();
                        
                        i18n.switchLanguage(selectedLang);
                        
                        // 语言切换后多次强制固定侧边栏宽度
                        setTimeout(forceSidebarWidth, 50);
                        setTimeout(forceSidebarWidth, 200);
                        setTimeout(forceSidebarWidth, 500);
                    } else {
                        console.error('🌐 语言切换失败 - i18n:', !!i18n, 'selectedLang:', selectedLang);
                    }
                    
                    languageDropdown.classList.remove('show');
                });
            });
            
            // 点击其他地方关闭下拉菜单
            document.addEventListener('click', function() {
                languageDropdown.classList.remove('show');
            });
            
            // 阻止下拉菜单内部点击事件冒泡
            languageDropdown.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        }

        // 🔙 智能返回功能
        function goBack() {
            // 检查是否有历史记录且不是从外部链接直接进入
            if (window.history.length > 1 && document.referrer && 
                document.referrer.includes(window.location.hostname)) {
                window.history.back();
            } else {
                // 如果没有合适的历史记录，返回到主页面或Dashboard
                showPage('dashboard');
            }
        }

        // 📱 移动端适配优化
        function initializeMobileOptimizations() {
            // 设置CSS自定义属性用于移动端高度计算
            function setAppHeight() {
                const vh = window.innerHeight * 0.01;
                document.documentElement.style.setProperty('--app-height', `${window.innerHeight}px`);
            }
            
            // 初始设置
            setAppHeight();
            
            // 监听窗口大小变化（处理移动端地址栏隐藏/显示）
            window.addEventListener('resize', setAppHeight);
            window.addEventListener('orientationchange', () => {
                setTimeout(setAppHeight, 100);
            });
            
            // 移动端触摸优化
            if ('ontouchstart' in window) {
                document.body.classList.add('touch-device');
                
                // 防止双击缩放
                let lastTouchEnd = 0;
                document.addEventListener('touchend', function(event) {
                    const now = (new Date()).getTime();
                    if (now - lastTouchEnd <= 300) {
                        event.preventDefault();
                    }
                    lastTouchEnd = now;
                }, false);
            }
            
            // 移动端键盘处理
            if (/iPhone|iPad|iPod|Android/i.test(navigator.userAgent)) {
                const viewport = document.querySelector('meta[name=viewport]');
                if (viewport) {
                    // 输入框获得焦点时调整视口
                    document.addEventListener('focusin', function(e) {
                        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                            viewport.setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no');
                            // 延迟重新计算视窗高度，等待键盘弹出
                            setTimeout(setRealViewportHeight, 300);
                        }
                    });
                    
                    // 输入框失去焦点时恢复视口
                    document.addEventListener('focusout', function(e) {
                        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                            viewport.setAttribute('content', 'width=device-width, initial-scale=1.0, user-scalable=no, viewport-fit=cover');
                            // 延迟重新计算视窗高度，等待键盘收起
                            setTimeout(setRealViewportHeight, 300);
                        }
                    });
                }
                
                // 额外的视觉视窗变化监听（iOS Safari专用）
                if (window.visualViewport) {
                    window.visualViewport.addEventListener('resize', setRealViewportHeight);
                }
            }
        }

        // 🔗 显示项目说明页面
        function goToProjectInfo() {
            showPage('project-info');
        }

        // 🔙 智能返回按钮处理
        function handleBackButton() {
            if (currentPage === 'dashboard') {
                // 在Dashboard页面，点击←进入项目说明
                showPage('project-info');
            } else if (currentPage === 'project-info') {
                // 在项目说明页面，点击←返回Dashboard
                goBack();
            } else {
                // 其他页面，使用智能返回
                goBack();
            }
        }

        // 🚀 主初始化函数
        // 动态视窗高度处理
        function setRealViewportHeight() {
            // 获取真实的视窗高度（排除浏览器UI）
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--real-vh', `${vh}px`);
        }

        // 初始设置
        setRealViewportHeight();

        // 监听窗口大小变化和方向变化
        window.addEventListener('resize', setRealViewportHeight);
        window.addEventListener('orientationchange', function() {
            // 延迟执行，等待方向变化完成
            setTimeout(setRealViewportHeight, 100);
        });

        document.addEventListener('DOMContentLoaded', function() {
            console.log('🚀 NEXUS Research Workstation 初始化中...');
            
            // 初始化AI配置管理器
            aiConfigManager = new AIConfigManager();
            console.log('🧠 AI配置管理器已初始化');
            
            // 检查AI状态
            checkAIStatus();
            
            // 确保视窗高度正确设置
            setRealViewportHeight();
            
            // 初始化国际化系统
            initializeI18n();
            
            // 延迟刷新翻译以确保新的AI翻译键生效
            setTimeout(() => {
                if (window.i18n) {
                    window.i18n.applyLanguage(window.i18n.getCurrentLanguage());
                    console.log('🌐 AI翻译键已刷新');
                    
                    // 强制刷新侧边栏翻译（但要检查英文锁定模式）
                    if (!window.sidebarEnglishMode) {
                        document.querySelectorAll('.nav-item-text[data-i18n]').forEach(element => {
                            const key = element.getAttribute('data-i18n');
                            const text = window.i18n.t(key);
                            if (text && text !== key) {
                                element.textContent = text;
                            }
                        });
                        console.log('🌐 侧边栏翻译已强制刷新');
                    } else {
                        console.log('🌐 侧边栏英文锁定模式已启用，跳过翻译刷新');
                        // 重新应用英文锁定
                        if (typeof window.updateSidebarToEnglish === 'function') {
                            window.updateSidebarToEnglish();
                        }
                    }
                }
            }, 1000);
            
            // 初始化移动端菜单
            initializeMobileMenu();
            
            // 初始化语言切换器
            initializeLanguageSwitcher();
            
            // 初始化移动端优化
            initializeMobileOptimizations();
            
            // 初始化侧边栏英文固定功能
            initSidebarEnglish();
            
            // 强制固定侧边栏宽度
            setTimeout(forceSidebarWidth, 500);
            
            // 监控侧边栏宽度变化 - 高频监控
            const sidebar = document.querySelector('.sidebar');
            if (sidebar) {
                // 高频检查并修复宽度
                setInterval(function() {
                    const currentWidth = sidebar.offsetWidth;
                    if (currentWidth !== 280) {
                        console.log('🚨 检测到宽度异常:', currentWidth, '立即修复!');
                        forceSidebarWidth();
                    }
                }, 100); // 每100ms检查一次
                
                // 监听DOM变化
                const observer = new MutationObserver(function() {
                    forceSidebarWidth();
                });
                
                observer.observe(sidebar, {
                    attributes: true,
                    childList: true,
                    subtree: true
                });
                
                // 监听窗口大小变化
                window.addEventListener('resize', forceSidebarWidth);
            }
            
            console.log('✅ NEXUS Research Workstation 初始化完成');
            
            // 初始化3D模拟控制
            initialize3DSimulations();
            
            // 测试语言切换功能
            setTimeout(() => {
                console.log('🧪 测试语言切换功能...');
                console.log('🧪 i18n对象:', i18n);
                console.log('🧪 LANGUAGES对象:', typeof LANGUAGES !== 'undefined' ? 'loaded' : 'not loaded');
                if (i18n) {
                    console.log('🧪 当前语言:', i18n.getCurrentLanguage());
                    console.log('🧪 支持的语言:', Object.keys(LANGUAGES));
                }
            }, 1000);
        });

        // 🧬 3D模拟系统控制
        let molecularSimulation = null;
        let genomeSimulation = null;

        function initialize3DSimulations() {
            console.log('🧬 初始化3D模拟控制系统...');
            
            // 分子模拟控制
            const molecularStartBtn = document.getElementById('molecular-start-btn');
            const molecularStopBtn = document.getElementById('molecular-stop-btn');
            const molecularVersionRadios = document.querySelectorAll('input[name="molecular-version"]');
            
            if (molecularStartBtn) {
                molecularStartBtn.addEventListener('click', () => startMolecularSimulation());
            }
            if (molecularStopBtn) {
                molecularStopBtn.addEventListener('click', () => stopMolecularSimulation());
            }
            
            molecularVersionRadios.forEach(radio => {
                radio.addEventListener('change', () => updateMolecularVersionDisplay());
            });
            
            // 基因星云控制
            const genomeStartBtn = document.getElementById('genome-start-btn');
            const genomeStopBtn = document.getElementById('genome-stop-btn');
            const genomeVersionRadios = document.querySelectorAll('input[name="genome-version"]');
            
            if (genomeStartBtn) {
                genomeStartBtn.addEventListener('click', () => startGenomeSimulation());
            }
            if (genomeStopBtn) {
                genomeStopBtn.addEventListener('click', () => stopGenomeSimulation());
            }
            
            genomeVersionRadios.forEach(radio => {
                radio.addEventListener('change', () => updateGenomeVersionDisplay());
            });
            
            console.log('✅ 3D模拟控制系统初始化完成');
        }

        // 分子模拟控制函数
        function startMolecularSimulation() {
            console.log('🚀 函数被调用了！');
            console.log('🚀 启动Kinetic Scope观测...');
            
            const container = document.getElementById('molecular-canvas-container');
            console.log('🔍 容器检查:', { containerExists: !!container, containerHTML: container ? container.innerHTML.substring(0, 200) : 'N/A' });
            
            // 获取选择的版本
            const versionRadio = document.querySelector('input[name="molecular-version"]:checked');
            console.log('🔍 版本选择检查:', { radioExists: !!versionRadio, radioValue: versionRadio ? versionRadio.value : 'N/A' });
            
            if (!versionRadio) {
                throw new Error('无法找到版本选择选项');
            }
            
            const selectedVersion = versionRadio.value;
            const isLite = selectedVersion === 'lite';
            
            // 更新UI状态 - 移除statusElement引用，直接更新容器状态
            
            // 清空容器
            container.innerHTML = '';
            
            // 创建3D演示
            try {
                console.log('🔍 开始创建分子演示...', { 
                    containerExists: !!container, 
                    containerWidth: container.clientWidth, 
                    containerHeight: container.clientHeight,
                    isLite 
                });
                
                // 先加载Three.js库，然后创建3D场景
                loadThreeJS().then(() => {
                    molecularSimulation = createMolecularScene(container, isLite);
                    console.log('✅ 3D分子演示创建成功:', !!molecularSimulation);
                }).catch(error => {
                    console.warn('⚠️ Three.js加载失败，使用2D备用方案:', error);
                    // 如果3D加载失败，使用2D备用方案
                    molecularSimulation = createSimpleMolecularDemo(container, isLite);
                    console.log('✅ 2D分子演示创建成功:', !!molecularSimulation);
                });
                console.log('✅ 分子演示初始化完成');
                
                // 添加停止按钮到画布上方
                const stopButton = document.createElement('button');
                stopButton.className = 'control-btn stop-btn';
                stopButton.style.position = 'absolute';
                stopButton.style.top = '10px';
                stopButton.style.right = '10px';
                stopButton.style.zIndex = '1000';
                console.log('🔍 Debug i18n:', {
                    i18nExists: !!window.i18n,
                    currentLanguage: window.i18n ? window.i18n.currentLanguage : 'N/A',
                    translationKey: 'cards.molecularSimulation.buttons.stop'
                });
                
                // 添加按钮到DOM
                stopButton.addEventListener('click', stopMolecularSimulation);
                container.appendChild(stopButton);
                
                // 获取正确的翻译文本
                let stopText = '停止观测'; // 默认中文
                if (window.i18n) {
                    console.log('🔍 i18n object:', window.i18n);
                    console.log('🔍 Current language:', window.i18n.currentLanguage);
                    console.log('🔍 Available translations:', Object.keys(window.i18n.translations));
                    
                    // 测试翻译
                    const testKey = 'cards.molecularSimulation.buttons.stop';
                    stopText = window.i18n.t(testKey);
                    console.log('🔍 Translation key:', testKey);
                    console.log('🔍 Stop button translation:', stopText);
                    
                    // 直接访问翻译数据
                    const currentLang = window.i18n.currentLanguage;
                    const directTranslation = window.i18n.translations[currentLang]?.cards?.molecularSimulation?.buttons?.stop;
                    console.log('🔍 Direct translation access:', directTranslation);
                } else {
                    console.log('❌ window.i18n not available');
                }
                
                // 创建按钮内容
                stopButton.innerHTML = `
                    <span class="btn-icon">⏹️</span>
                    <span class="btn-text" data-i18n="cards.molecularSimulation.buttons.stop">${stopText}</span>
                `;
                
                // 更新动态生成内容的多语言
                if (window.i18n) {
                    window.i18n.updateElements();
                }
                
                // 更新页面标题 - 使用多语言系统
                const titleElement = document.querySelector('.page-title');
                if (titleElement && window.i18n && window.LANGUAGES) {
                    try {
                        const currentLang = window.i18n.getCurrentLanguage();
                        const translations = window.LANGUAGES[currentLang];
                        if (translations && translations.titles && translations.titles.molecular) {
                            titleElement.textContent = translations.titles.molecular;
                        } else {
                            titleElement.textContent = '动力学观测仪';
                        }
                    } catch (error) {
                        console.warn('⚠️ 更新页面标题失败:', error);
                        titleElement.textContent = '动力学观测仪';
                    }
                } else {
                    if (titleElement) {
                        titleElement.textContent = '动力学观测仪';
                    }
                }
            } catch (error) {
                console.error('❌ Kinetic Scope观测启动失败:', error);
                console.error('❌ 错误详情:', error.stack);
                
                // 恢复占位符
                container.innerHTML = `
                    <div class="canvas-placeholder">
                        <div class="placeholder-icon">🔬</div>
                        <h3 data-i18n="cards.molecularSimulation.title">Kinetic Scope</h3>
                        <p data-i18n="cards.molecularSimulation.error">启动失败，请重试</p>
                        <p style="color: red; font-size: 12px; margin-top: 10px;">错误: ${error.message}</p>
                        
                        <div class="canvas-controls">
                            <button id="molecular-start-btn" class="control-btn start-btn">
                                <span class="btn-icon">▶️</span>
                                <span class="btn-text" data-i18n="cards.molecularSimulation.buttons.start">启动观测</span>
                            </button>
                            
                            <div class="version-selector">
                                <label>
                                    <input type="radio" name="molecular-version" value="lite" checked>
                                    <span data-i18n="cards.molecularSimulation.versions.lite">轻量版</span>
                                </label>
                                <label>
                                    <input type="radio" name="molecular-version" value="full">
                                    <span data-i18n="cards.molecularSimulation.versions.full">完整版</span>
                                </label>
                            </div>
                        </div>
                    </div>
                `;
                
                // 重新绑定事件并更新多语言
                setTimeout(() => {
                    console.log('🔄 重新绑定事件监听器');
                    const newStartBtn = document.getElementById('molecular-start-btn');
                    if (newStartBtn) {
                        newStartBtn.addEventListener('click', startMolecularSimulation);
                        console.log('✅ 事件监听器绑定成功');
                    } else {
                        console.log('❌ 找不到按钮元素');
                    }
                    
                    // 更新错误恢复内容的多语言
                    if (window.i18n) {
                        window.i18n.updateElements();
                    }
                }, 100);
            }
        }

        function stopMolecularSimulation() {
            console.log('⏹️ 停止Kinetic Scope观测...');
            
            const container = document.getElementById('molecular-canvas-container');
            if (!container) {
                console.error('❌ 找不到容器元素');
                return;
            }
            
            // 清理3D场景
            if (molecularSimulation) {
                try {
                    molecularSimulation.cleanup();
                    console.log('✅ 3D场景清理完成');
                } catch (error) {
                    console.error('❌ 清理3D场景时出错:', error);
                }
                molecularSimulation = null;
            }
            
            // 恢复占位符
            console.log('🔄 恢复占位符界面...');
            container.innerHTML = `
                <div class="canvas-placeholder">
                    <div class="placeholder-icon">🔬</div>
                    <h3 data-i18n="cards.molecularSimulation.title">Kinetic Scope</h3>
                    <p data-i18n="cards.molecularSimulation.subtitle">动力学观测仪 - 选择版本并点击启动观测</p>
                    
                    <div class="canvas-controls">
                        <button id="molecular-start-btn" class="control-btn start-btn">
                            <span class="btn-icon">▶️</span>
                            <span class="btn-text" data-i18n="cards.molecularSimulation.buttons.launch">启动观测</span>
                        </button>
                        <button id="molecular-stop-btn" class="control-btn stop-btn" style="display: none;">
                            <span class="btn-icon">⏹️</span>
                            <span class="btn-text" data-i18n="cards.molecularSimulation.buttons.stop">停止观测</span>
                        </button>
                        
                        <div class="version-selector">
                            <label>
                                <input type="radio" name="molecular-version" value="lite" checked>
                                <span data-i18n="cards.molecularSimulation.versions.lite">轻量版</span>
                            </label>
                            <label>
                                <input type="radio" name="molecular-version" value="full">
                                <span data-i18n="cards.molecularSimulation.versions.full">完整版</span>
                            </label>
                        </div>
                    </div>
                </div>
            `;
            console.log('✅ 占位符界面恢复完成');
            
            // 应用当前语言的翻译
            if (window.i18n) {
                container.querySelectorAll('[data-i18n]').forEach(element => {
                    const key = element.getAttribute('data-i18n');
                    const text = window.i18n.t(key);
                    element.textContent = text;
                });
                
                // 恢复页面标题到动力学观测仪（因为用户在该页面）
                const titleElement = document.querySelector('.page-title');
                if (titleElement && window.i18n && window.LANGUAGES) {
                    try {
                        const currentLang = window.i18n.getCurrentLanguage();
                        const translations = window.LANGUAGES[currentLang];
                        if (translations && translations.titles && translations.titles.molecular) {
                            titleElement.textContent = translations.titles.molecular;
                        } else {
                            titleElement.textContent = '动力学观测仪';
                        }
                    } catch (error) {
                        console.warn('⚠️ 恢复分子模拟页面标题失败:', error);
                        titleElement.textContent = '动力学观测仪';
                    }
                } else {
                    if (titleElement) {
                        titleElement.textContent = '动力学观测仪';
                    }
                }
            }
            
            // 重新绑定事件监听器
            setTimeout(() => {
                const newStartBtn = document.getElementById('molecular-start-btn');
                const newStopBtn = document.getElementById('molecular-stop-btn');
                if (newStartBtn) {
                    newStartBtn.addEventListener('click', startMolecularSimulation);
                }
                if (newStopBtn) {
                    newStopBtn.addEventListener('click', stopMolecularSimulation);
                }
            }, 100);
            
            console.log('✅ Kinetic Scope观测已停止');
        }

        function updateMolecularVersionDisplay() {
            const selectedVersion = document.querySelector('input[name="molecular-version"]:checked').value;
            console.log('🔬 Kinetic Scope版本切换:', selectedVersion === 'lite' ? '轻量版' : '完整版');
        }

        // 基因星云控制函数
        function startGenomeSimulation() {
            console.log('🚀 启动基因星云...');
            
            const container = document.getElementById('genome-canvas-container');
            
            // 获取选择的版本
            const selectedVersion = document.querySelector('input[name="genome-version"]:checked').value;
            const isLite = selectedVersion === 'lite';
            
            // 更新UI状态 - 移除statusElement引用
            
            // 清空容器
            container.innerHTML = '';
            
            // 创建3D演示
            try {
                console.log('🔍 开始创建基因星云演示...', { 
                    containerExists: !!container, 
                    containerWidth: container.clientWidth, 
                    containerHeight: container.clientHeight,
                    isLite 
                });
                
                // 先加载Three.js库，然后创建3D场景
                loadThreeJS().then(() => {
                    genomeSimulation = createGenomeScene(container, isLite);
                    console.log('✅ 3D基因星云演示创建成功:', !!genomeSimulation);
                }).catch(error => {
                    console.warn('⚠️ Three.js加载失败，使用2D备用方案:', error);
                    // 如果3D加载失败，使用2D备用方案
                    genomeSimulation = createSimpleGenomeDemo(container, isLite);
                    console.log('✅ 2D基因星云演示创建成功:', !!genomeSimulation);
                });
                console.log('✅ 基因星云演示初始化完成');
                
                // 添加停止按钮到画布上方
                const stopButton = document.createElement('button');
                stopButton.className = 'control-btn stop-btn';
                stopButton.style.position = 'absolute';
                stopButton.style.top = '10px';
                stopButton.style.right = '10px';
                stopButton.style.zIndex = '1000';
                stopButton.innerHTML = '<span class="btn-icon">⏹️</span><span class="btn-text" data-i18n="cards.genomeNebula.buttons.stop">停止星云</span>';
                stopButton.addEventListener('click', stopGenomeSimulation);
                container.appendChild(stopButton);
                
                // 更新新创建按钮的多语言文本
                if (window.i18n) {
                    window.i18n.updateElements();
                }
                
                console.log('✅ 基因星云启动成功');
                
                // 更新页面标题 - 使用多语言系统
                const titleElement = document.querySelector('.page-title');
                if (titleElement && window.i18n && window.LANGUAGES) {
                    try {
                        const currentLang = window.i18n.getCurrentLanguage();
                        const translations = window.LANGUAGES[currentLang];
                        if (translations && translations.titles && translations.titles.genome) {
                            titleElement.textContent = translations.titles.genome;
                        } else {
                            titleElement.textContent = '基因星云';
                        }
                    } catch (error) {
                        console.warn('⚠️ 更新基因星云页面标题失败:', error);
                        titleElement.textContent = '基因星云';
                    }
                } else {
                    if (titleElement) {
                        titleElement.textContent = '基因星云';
                    }
                }
            } catch (error) {
                console.error('❌ 基因星云启动失败:', error);
                alert('基因星云启动失败: ' + error.message);
                
                // 恢复占位符
                container.innerHTML = `
                    <div class="canvas-placeholder">
                        <div class="placeholder-icon">🌌</div>
                        <h3 data-i18n="cards.genomeNebula.title">基因星云</h3>
                        <p data-i18n="cards.genomeNebula.error">启动失败，请重试</p>
                        
                        <div class="canvas-controls">
                            <button id="genome-start-btn" class="control-btn start-btn">
                                <span class="btn-icon">▶️</span>
                                <span class="btn-text" data-i18n="cards.genomeNebula.buttons.launch">启动星云</span>
                            </button>
                            
                            <div class="version-selector">
                                <label>
                                    <input type="radio" name="genome-version" value="lite" checked>
                                    <span data-i18n="cards.genomeNebula.versions.lite">轻量版</span>
                                </label>
                                <label>
                                    <input type="radio" name="genome-version" value="full">
                                    <span data-i18n="cards.genomeNebula.versions.full">完整版</span>
                                </label>
                            </div>
                        </div>
                    </div>
                `;
                
                // 重新绑定事件并更新多语言
                setTimeout(() => {
                    const newStartBtn = document.getElementById('genome-start-btn');
                    if (newStartBtn) {
                        newStartBtn.addEventListener('click', startGenomeSimulation);
                    }
                    
                    // 更新恢复内容的多语言文本
                    if (window.i18n) {
                        window.i18n.updateElements();
                    }
                }, 100);
            }
        }

        function stopGenomeSimulation() {
            console.log('⏹️ 停止基因星云...');
            
            const container = document.getElementById('genome-canvas-container');
            if (!container) {
                console.error('❌ 找不到基因星云容器元素');
                return;
            }
            
            // 清理3D场景
            if (genomeSimulation) {
                try {
                    genomeSimulation.cleanup();
                    console.log('✅ 基因星云3D场景清理完成');
                } catch (error) {
                    console.error('❌ 清理基因星云3D场景时出错:', error);
                }
                genomeSimulation = null;
            }
            
            // 恢复占位符
            console.log('🔄 恢复基因星云占位符界面...');
            container.innerHTML = `
                <div class="canvas-placeholder">
                    <div class="placeholder-icon">🌌</div>
                    <h3 data-i18n="cards.genomeNebula.title">基因星云</h3>
                    <p data-i18n="cards.genomeNebula.subtitle">选择版本并点击启动按钮开始可视化</p>
                    
                    <div class="canvas-controls">
                        <button id="genome-start-btn" class="control-btn start-btn">
                            <span class="btn-icon">▶️</span>
                            <span class="btn-text" data-i18n="cards.genomeNebula.buttons.launch">启动星云</span>
                        </button>
                        <button id="genome-stop-btn" class="control-btn stop-btn" style="display: none;">
                            <span class="btn-icon">⏹️</span>
                            <span class="btn-text" data-i18n="cards.genomeNebula.buttons.stop">停止星云</span>
                        </button>
                        
                        <div class="version-selector">
                            <label>
                                <input type="radio" name="genome-version" value="lite" checked>
                                <span data-i18n="cards.genomeNebula.versions.lite">轻量版</span>
                            </label>
                            <label>
                                <input type="radio" name="genome-version" value="full">
                                <span data-i18n="cards.genomeNebula.versions.full">完整版</span>
                            </label>
                        </div>
                    </div>
                </div>
            `;
            
            // 重新绑定事件监听器
            setTimeout(() => {
                console.log('🔄 重新绑定基因星云事件监听器...');
                const newStartBtn = document.getElementById('genome-start-btn');
                const newStopBtn = document.getElementById('genome-stop-btn');
                if (newStartBtn) {
                    newStartBtn.addEventListener('click', startGenomeSimulation);
                    console.log('✅ 基因星云启动按钮事件绑定成功');
                } else {
                    console.log('❌ 找不到基因星云启动按钮');
                }
                if (newStopBtn) {
                    newStopBtn.addEventListener('click', stopGenomeSimulation);
                    console.log('✅ 基因星云停止按钮事件绑定成功');
                } else {
                    console.log('❌ 找不到基因星云停止按钮');
                }
            }, 100);
            
            // 更新重新生成内容的多语言文本
            if (window.i18n) {
                window.i18n.updateElements();
                
                // 恢复页面标题到基因星云（因为用户在该页面）
                const titleElement = document.querySelector('.page-title');
                if (titleElement && window.i18n && window.LANGUAGES) {
                    try {
                        const currentLang = window.i18n.getCurrentLanguage();
                        const translations = window.LANGUAGES[currentLang];
                        if (translations && translations.titles && translations.titles.genome) {
                            titleElement.textContent = translations.titles.genome;
                        } else {
                            titleElement.textContent = '基因星云';
                        }
                    } catch (error) {
                        console.warn('⚠️ 恢复基因星云页面标题失败:', error);
                        titleElement.textContent = '基因星云';
                    }
                } else {
                    if (titleElement) {
                        titleElement.textContent = '基因星云';
                    }
                }
            }
            
            console.log('✅ 基因星云已停止');
        }

        function updateGenomeVersionDisplay() {
            const selectedVersion = document.querySelector('input[name="genome-version"]:checked').value;
            console.log('🌌 基因星云版本切换:', selectedVersion === 'lite' ? '轻量版' : '完整版');
        }

        // 动态加载Three.js库
        function loadThreeJS() {
            return new Promise((resolve, reject) => {
                if (window.THREE) {
                    resolve();
                    return;
                }
                
                console.log('📦 加载Three.js库...');
                
                const script = document.createElement('script');
                script.src = 'https://unpkg.com/three@0.158.0/build/three.min.js';
                script.onload = () => {
                    // 加载OrbitControls - 使用可靠的CDN版本
                    const controlsScript = document.createElement('script');
                    controlsScript.src = 'https://cdn.skypack.dev/three@0.158.0/examples/jsm/controls/OrbitControls.js';
                    controlsScript.onload = () => {
                        console.log('✅ Three.js和OrbitControls库加载完成');
                        resolve();
                    };
                    controlsScript.onerror = (error) => {
                        console.warn('⚠️ OrbitControls加载失败，尝试备用方案');
                        // 如果OrbitControls加载失败，仍然继续，但不使用控制器
                        resolve();
                    };
                    document.head.appendChild(controlsScript);
                };
                script.onerror = reject;
                document.head.appendChild(script);
            });
        }

        // 创建简化的分子演示
        function createSimpleMolecularDemo(container, isLite) {
            console.log('🧪 创建简化分子演示...');
            
            try {
                const canvas = document.createElement('canvas');
                console.log('✅ Canvas元素创建成功');
                
                // 确保容器有合理的尺寸
                const width = container.clientWidth || 800;
                const height = container.clientHeight || 600;
                
                console.log('🔍 分子演示容器尺寸:', { width, height, clientWidth: container.clientWidth, clientHeight: container.clientHeight });
                
                canvas.width = width;
                canvas.height = height;
                canvas.style.width = '100%';
                canvas.style.height = '100%';
                canvas.style.background = 'linear-gradient(135deg, #0a0a2e, #16213e)';
                console.log('✅ Canvas样式设置完成');
                
                container.appendChild(canvas);
                console.log('✅ Canvas添加到容器');
                
                const ctx = canvas.getContext('2d');
                console.log('✅ 2D上下文获取成功:', !!ctx);
                
                if (!ctx) {
                    throw new Error('无法获取2D渲染上下文');
                }
                
                // 分子原子数据
                const atoms = [
                    { x: 200, y: 200, radius: 20, color: '#909090', element: 'C' },
                    { x: 280, y: 200, radius: 20, color: '#909090', element: 'C' },
                    { x: 320, y: 150, radius: 20, color: '#909090', element: 'C' },
                    { x: 280, y: 100, radius: 15, color: '#3050F8', element: 'N' },
                    { x: 200, y: 100, radius: 20, color: '#909090', element: 'C' },
                    { x: 160, y: 150, radius: 15, color: '#3050F8', element: 'N' },
                    { x: 360, y: 150, radius: 18, color: '#FF0D0D', element: 'O' },
                    { x: 180, y: 240, radius: 12, color: '#FFFFFF', element: 'H' },
                    { x: 300, y: 240, radius: 12, color: '#FFFFFF', element: 'H' },
                    { x: 300, y: 60, radius: 12, color: '#FFFFFF', element: 'H' }
                ];
                
                let rotation = 0;
                
                function animate() {
                    if (!canvas.parentNode) return;
                    
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    
                    // 绘制连接线
                    ctx.strokeStyle = '#444';
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    // 简化的分子键
                    const bonds = [
                        [0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0], [2, 6]
                    ];
                    
                    bonds.forEach(([i, j]) => {
                        const a1 = atoms[i];
                        const a2 = atoms[j];
                        ctx.moveTo(a1.x, a1.y);
                        ctx.lineTo(a2.x, a2.y);
                    });
                    ctx.stroke();
                    
                    // 绘制原子
                    atoms.forEach(atom => {
                        ctx.beginPath();
                        ctx.arc(atom.x, atom.y, atom.radius, 0, Math.PI * 2);
                        ctx.fillStyle = atom.color;
                        ctx.fill();
                        ctx.strokeStyle = '#fff';
                        ctx.lineWidth = 1;
                        ctx.stroke();
                        
                        // 绘制元素符号
                        ctx.fillStyle = '#000';
                        ctx.font = '12px Arial';
                        ctx.textAlign = 'center';
                        ctx.fillText(atom.element, atom.x, atom.y + 4);
                    });
                    
                    // 添加标题
                    ctx.fillStyle = '#fff';
                    ctx.font = '16px Arial';
                    ctx.textAlign = 'center';
                    ctx.fillText('咖啡因分子 (C₈H₁₀N₄O₂)', canvas.width / 2, 30);
                    
                    rotation += 0.01;
                    requestAnimationFrame(animate);
                }
                
                animate();
                
                // 处理窗口大小变化
                function onWindowResize() {
                    if (!container.parentNode) return;
                    canvas.width = container.clientWidth;
                    canvas.height = container.clientHeight;
                }
                window.addEventListener('resize', onWindowResize);
                
                return {
                    cleanup: () => {
                        window.removeEventListener('resize', onWindowResize);
                        if (canvas.parentNode) {
                            canvas.parentNode.removeChild(canvas);
                        }
                    }
                };
                
            } catch (error) {
                console.error('❌ 创建分子演示失败:', error);
                throw error;
            }
        }

        // 创建分子模拟场景（Three.js版本，备用）
        function createMolecularScene(container, isLite) {
            console.log('🧪 创建分子模拟场景...');
            
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x000011);
            
            const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(0, 0, 10);
            camera.lookAt(0, 0, 0);
            
            const renderer = new THREE.WebGLRenderer({ antialias: !isLite });
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, isLite ? 1 : 2));
            container.appendChild(renderer.domElement);
            
            // 实现基础的鼠标控制
            let isMouseDown = false;
            let mouseX = 0, mouseY = 0;
            let targetRotationX = 0, targetRotationY = 0;
            let rotationX = 0, rotationY = 0;
            let isDragging = false;
            
            renderer.domElement.addEventListener('mousedown', (event) => {
                isMouseDown = true;
                mouseX = event.clientX;
                mouseY = event.clientY;
            });
            
            renderer.domElement.addEventListener('mouseup', () => {
                isMouseDown = false;
                isDragging = false;
            });
            
            renderer.domElement.addEventListener('mouseleave', () => {
                isMouseDown = false;
                isDragging = false;
            });
            
            // 鼠标滚轮缩放
            renderer.domElement.addEventListener('wheel', (event) => {
                event.preventDefault();
                const scale = event.deltaY > 0 ? 1.1 : 0.9;
                camera.position.multiplyScalar(scale);
                // 限制缩放范围
                const distance = camera.position.length();
                if (distance < 5) camera.position.normalize().multiplyScalar(5);
                if (distance > 50) camera.position.normalize().multiplyScalar(50);
            });
            
            // 添加光照
            const ambientLight = new THREE.AmbientLight(0x404040, 0.8);
            scene.add(ambientLight);
            
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
            directionalLight.position.set(10, 10, 5);
            scene.add(directionalLight);
            
            // 创建分子
            const atomGroup = new THREE.Group();
            scene.add(atomGroup);
            
            // 简化的咖啡因分子 - 居中显示
            const atoms = [
                { element: 'C', x: -1.05, y: -1.2, z: 0, color: 0x909090 },
                { element: 'C', x: 0.35, y: -1.2, z: 0, color: 0x909090 },
                { element: 'C', x: 1.05, y: 0, z: 0, color: 0x909090 },
                { element: 'N', x: 0.35, y: 1.2, z: 0, color: 0x3050F8 },
                { element: 'C', x: -1.05, y: 1.2, z: 0, color: 0x909090 },
                { element: 'N', x: -1.75, y: 0, z: 0, color: 0x3050F8 },
                { element: 'O', x: 2.25, y: 0, z: 0, color: 0xFF0D0D },
                { element: 'H', x: -1.55, y: -2.1, z: 0, color: 0xFFFFFF },
                { element: 'H', x: 0.85, y: -2.1, z: 0, color: 0xFFFFFF },
                { element: 'H', x: 0.85, y: 2.1, z: 0, color: 0xFFFFFF }
            ];
            
            atoms.forEach((atom, index) => {
                const radius = atom.element === 'H' ? 0.3 : 0.4;
                const geometry = new THREE.SphereGeometry(radius, isLite ? 4 : 8, isLite ? 4 : 8);
                const material = new THREE.MeshLambertMaterial({ color: atom.color });
                const mesh = new THREE.Mesh(geometry, material);
                mesh.position.set(atom.x, atom.y, atom.z);
                
                // 添加原子信息
                mesh.userData = {
                    id: `原子-${index + 1}`,
                    element: atom.element,
                    position: { x: atom.x.toFixed(1), y: atom.y.toFixed(1), z: atom.z.toFixed(1) },
                    type: getAtomType(atom.element),
                    bonds: getBondCount(atom.element)
                };
                
                atomGroup.add(mesh);
            });
            
            function getAtomType(element) {
                const types = {
                    'C': '碳原子',
                    'N': '氮原子', 
                    'O': '氧原子',
                    'H': '氢原子'
                };
                return types[element] || '未知原子';
            }
            
            function getBondCount(element) {
                const bonds = {
                    'C': 4,
                    'N': 3,
                    'O': 2,
                    'H': 1
                };
                return bonds[element] || 0;
            }
            
            // 创建固定信息框
            const infoPanel = document.createElement('div');
            infoPanel.style.cssText = `
                position: absolute;
                bottom: 10px;
                right: 10px;
                width: 200px;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 12px;
                border-radius: 6px;
                font-size: 12px;
                z-index: 1000;
                border: 1px solid #333;
                display: none;
            `;
            infoPanel.innerHTML = '<div style="color: #999;">将鼠标悬停在基因点上查看信息</div>';
            container.appendChild(infoPanel);
            
            // 鼠标交互
            const raycaster = new THREE.Raycaster();
            const mouse = new THREE.Vector2();
            let hoveredObject = null;
            
            function onMouseMove(event) {
                // 处理拖拽旋转
                if (isMouseDown) {
                    const deltaX = event.clientX - mouseX;
                    const deltaY = event.clientY - mouseY;
                    
                    // 检测是否开始拖拽
                    if (!isDragging && (Math.abs(deltaX) > 3 || Math.abs(deltaY) > 3)) {
                        isDragging = true;
                    }
                    
                    if (isDragging) {
                        targetRotationY += deltaX * 0.01;
                        targetRotationX += deltaY * 0.01;
                    }
                    
                    mouseX = event.clientX;
                    mouseY = event.clientY;
                } else if (!isDragging) {
                    // 处理悬停检测（只在非拖拽状态下）
                    const rect = renderer.domElement.getBoundingClientRect();
                    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
                    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
                    
                    raycaster.setFromCamera(mouse, camera);
                    const intersects = raycaster.intersectObjects(atomGroup.children);
                    
                    if (intersects.length > 0) {
                        const intersected = intersects[0].object;
                        
                        if (hoveredObject !== intersected) {
                            // 恢复之前悬停对象的颜色
                            if (hoveredObject) {
                                hoveredObject.material.emissive.setHex(0x000000);
                            }
                            
                            // 高亮当前悬停对象
                            hoveredObject = intersected;
                            hoveredObject.material.emissive.setHex(0x444444);
                            
                            // 显示信息提示
                            const info = intersected.userData;
                            infoPanel.innerHTML = `
                                <div style="font-weight: bold; color: #4FC3F7; margin-bottom: 5px;">${info.id}</div>
                                <div><span style="color: #81C784;">元素:</span> ${info.element}</div>
                                <div><span style="color: #FFB74D;">类型:</span> ${info.type}</div>
                                <div><span style="color: #F06292;">键数:</span> ${info.bonds}</div>
                                <div style="margin-top: 5px; font-size: 10px; color: #999;">
                                    位置: (${info.position.x}, ${info.position.y}, ${info.position.z})
                                </div>
                            `;
                            infoPanel.style.display = 'block';
                        }
                    } else {
                        // 没有悬停对象
                        if (hoveredObject) {
                            hoveredObject.material.emissive.setHex(0x000000);
                            hoveredObject = null;
                        }
                        infoPanel.style.display = 'none';
                    }
                }
            }
            
            renderer.domElement.addEventListener('mousemove', onMouseMove);
            
            // 动画循环
            function animate() {
                if (!renderer.domElement.parentNode) return; // 检查是否还在DOM中
                
                requestAnimationFrame(animate);
                
                // 平滑旋转
                rotationX += (targetRotationX - rotationX) * 0.1;
                rotationY += (targetRotationY - rotationY) * 0.1;
                
                // 应用旋转到场景
                atomGroup.rotation.x = rotationX;
                atomGroup.rotation.y = rotationY;
                
                renderer.render(scene, camera);
            }
            animate();
            
            // 处理窗口大小变化
            function onWindowResize() {
                if (!container.parentNode) return;
                
                camera.aspect = container.clientWidth / container.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, container.clientHeight);
            }
            window.addEventListener('resize', onWindowResize);
            
            return {
                cleanup: () => {
                    window.removeEventListener('resize', onWindowResize);
                    renderer.domElement.removeEventListener('mousemove', onMouseMove);
                    renderer.domElement.removeEventListener('mousedown', () => {});
                    renderer.domElement.removeEventListener('mouseup', () => {});
                    renderer.domElement.removeEventListener('mouseleave', () => {});
                    renderer.domElement.removeEventListener('wheel', () => {});
                    if (tooltip && tooltip.parentNode) {
                        infoPanel.parentNode.removeChild(infoPanel);
                    }
                    if (renderer.domElement.parentNode) {
                        renderer.domElement.parentNode.removeChild(renderer.domElement);
                    }
                    renderer.dispose();
                }
            };
        }

        // 创建简化的基因星云演示
        function createSimpleGenomeDemo(container, isLite) {
            console.log('🌌 创建简化基因星云演示...');
            
            try {
                const canvas = document.createElement('canvas');
                console.log('✅ Canvas元素创建成功');
                
                // 确保容器有合理的尺寸
                const width = container.clientWidth || 800;
                const height = container.clientHeight || 600;
                
                console.log('🔍 基因星云容器尺寸:', { width, height, clientWidth: container.clientWidth, clientHeight: container.clientHeight });
                
                canvas.width = width;
                canvas.height = height;
                canvas.style.width = '100%';
                canvas.style.height = '100%';
                canvas.style.background = 'linear-gradient(135deg, #0a0a2e, #16213e, #1a1a3a)';
                console.log('✅ Canvas样式设置完成');
                
                container.appendChild(canvas);
                console.log('✅ Canvas添加到容器');
                
                const ctx = canvas.getContext('2d');
                console.log('✅ 2D上下文获取成功:', !!ctx);
                
                if (!ctx) {
                    throw new Error('无法获取2D渲染上下文');
                }
            
                // 基因点数据
                const geneCount = isLite ? 50 : 150;
                const genes = [];
                
                for (let i = 0; i < geneCount; i++) {
                    const importance = Math.random();
                    let color;
                    if (importance > 0.8) {
                        color = '#FF1744'; // 红色 - 高重要性
                    } else if (importance > 0.5) {
                        color = '#9C27B0'; // 紫色 - 中重要性
                    } else {
                        color = '#3F51B5'; // 蓝色 - 低重要性
                    }
                    
                    genes.push({
                        x: Math.random() * canvas.width,
                        y: Math.random() * canvas.height,
                        z: Math.random() * 100, // 模拟深度
                        radius: 2 + importance * 6,
                        color: color,
                        importance: importance,
                        vx: (Math.random() - 0.5) * 0.5,
                        vy: (Math.random() - 0.5) * 0.5,
                        pulse: Math.random() * Math.PI * 2
                    });
                }
                
                let time = 0;
                
                function animate() {
                    if (!canvas.parentNode) return;
                    
                    ctx.fillStyle = 'rgba(10, 10, 46, 0.1)';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    // 绘制连接线（基因网络）
                    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
                    ctx.lineWidth = 1;
                    
                    for (let i = 0; i < genes.length; i++) {
                        for (let j = i + 1; j < genes.length; j++) {
                            const gene1 = genes[i];
                            const gene2 = genes[j];
                            const distance = Math.sqrt(
                                Math.pow(gene1.x - gene2.x, 2) + 
                                Math.pow(gene1.y - gene2.y, 2)
                            );
                            
                            if (distance < 100 && gene1.importance > 0.6 && gene2.importance > 0.6) {
                                ctx.beginPath();
                                ctx.moveTo(gene1.x, gene1.y);
                                ctx.lineTo(gene2.x, gene2.y);
                                ctx.stroke();
                            }
                        }
                    }
                    
                    // 绘制基因点
                    genes.forEach(gene => {
                        // 更新位置
                        gene.x += gene.vx;
                        gene.y += gene.vy;
                        gene.pulse += 0.1;
                        
                        // 边界反弹
                        if (gene.x < 0 || gene.x > canvas.width) gene.vx *= -1;
                        if (gene.y < 0 || gene.y > canvas.height) gene.vy *= -1;
                        
                        // 脉冲效果
                        const pulseRadius = gene.radius + Math.sin(gene.pulse) * 2;
                        
                        // 绘制光晕
                        const gradient = ctx.createRadialGradient(
                            gene.x, gene.y, 0,
                            gene.x, gene.y, pulseRadius * 2
                        );
                        gradient.addColorStop(0, gene.color + '80');
                        gradient.addColorStop(1, gene.color + '00');
                        
                        ctx.fillStyle = gradient;
                        ctx.beginPath();
                        ctx.arc(gene.x, gene.y, pulseRadius * 2, 0, Math.PI * 2);
                        ctx.fill();
                        
                        // 绘制核心
                        ctx.fillStyle = gene.color;
                        ctx.beginPath();
                        ctx.arc(gene.x, gene.y, pulseRadius, 0, Math.PI * 2);
                        ctx.fill();
                    });
                    
                    // 添加标题和统计
                    ctx.fillStyle = '#fff';
                    ctx.font = '16px Arial';
                    ctx.textAlign = 'center';
                    ctx.fillText('Genome 表达星云', canvas.width / 2, 30);
                    
                    ctx.font = '12px Arial';
                    ctx.textAlign = 'left';
                    ctx.fillText(`基因数量: ${geneCount}`, 20, canvas.height - 60);
                    ctx.fillStyle = '#FF1744';
                    ctx.fillText('● 高表达', 20, canvas.height - 40);
                    ctx.fillStyle = '#9C27B0';
                    ctx.fillText('● 中表达', 100, canvas.height - 40);
                    ctx.fillStyle = '#3F51B5';
                    ctx.fillText('● 低表达', 180, canvas.height - 40);
                    
                    time += 0.01;
                    requestAnimationFrame(animate);
                }
                
                animate();
                
                // 处理窗口大小变化
                function onWindowResize() {
                    if (!container.parentNode) return;
                    canvas.width = container.clientWidth;
                    canvas.height = container.clientHeight;
                }
                window.addEventListener('resize', onWindowResize);
                
                return {
                    cleanup: () => {
                        window.removeEventListener('resize', onWindowResize);
                        if (canvas.parentNode) {
                            canvas.parentNode.removeChild(canvas);
                        }
                    }
                };
            
            } catch (error) {
                console.error('❌ 创建基因星云演示失败:', error);
                throw error;
            }
        }

        // 创建基因星云场景（Three.js版本，备用）
        function createGenomeScene(container, isLite) {
            console.log('🌌 创建基因星云场景...');
            
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x000011);
            
            const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(0, 0, 50);
            camera.lookAt(0, 0, 0);
            
            const renderer = new THREE.WebGLRenderer({ antialias: !isLite });
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, isLite ? 1 : 2));
            container.appendChild(renderer.domElement);
            
            // 实现基础的鼠标控制
            let isMouseDown = false;
            let mouseX = 0, mouseY = 0;
            let targetRotationX = 0, targetRotationY = 0;
            let rotationX = 0, rotationY = 0;
            let targetPanX = 0, targetPanY = 0;
            let panX = 0, panY = 0;
            let isDragging = false;
            let isShiftPressed = false;
            
            // 键盘事件监听
            document.addEventListener('keydown', (event) => {
                if (event.key === 'Shift') isShiftPressed = true;
            });
            
            document.addEventListener('keyup', (event) => {
                if (event.key === 'Shift') isShiftPressed = false;
            });
            
            renderer.domElement.addEventListener('mousedown', (event) => {
                isMouseDown = true;
                mouseX = event.clientX;
                mouseY = event.clientY;
                isShiftPressed = event.shiftKey; // 检测Shift键
            });
            
            renderer.domElement.addEventListener('mouseup', () => {
                isMouseDown = false;
                isDragging = false;
            });
            
            renderer.domElement.addEventListener('mouseleave', () => {
                isMouseDown = false;
                isDragging = false;
            });
            
            // 鼠标滚轮缩放
            renderer.domElement.addEventListener('wheel', (event) => {
                event.preventDefault();
                const scale = event.deltaY > 0 ? 1.1 : 0.9;
                camera.position.multiplyScalar(scale);
                // 限制缩放范围
                const distance = camera.position.length();
                if (distance < 10) camera.position.normalize().multiplyScalar(10);
                if (distance > 200) camera.position.normalize().multiplyScalar(200);
            });
            
            // 添加光照
            const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
            scene.add(ambientLight);
            
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.4);
            directionalLight.position.set(50, 50, 25);
            scene.add(directionalLight);
            
            // 创建基因点云
            const geneGroup = new THREE.Group();
            scene.add(geneGroup);
            
            const geneCount = isLite ? 100 : 500;
            const geneData = []; // 存储基因数据用于悬停显示
            
            for (let i = 0; i < geneCount; i++) {
                const importance = Math.random();
                const size = 0.2 + importance * 0.8;
                
                let color, geneType;
                if (importance > 0.8) {
                    color = new THREE.Color(0xFF1744); // 红色
                    geneType = '关键基因';
                } else if (importance > 0.5) {
                    color = new THREE.Color(0x9C27B0); // 紫色
                    geneType = '调节基因';
                } else {
                    color = new THREE.Color(0x3F51B5); // 蓝色
                    geneType = '结构基因';
                }
                
                const geometry = new THREE.SphereGeometry(size, isLite ? 3 : 6, isLite ? 3 : 6);
                const material = new THREE.MeshLambertMaterial({ color: color });
                const mesh = new THREE.Mesh(geometry, material);
                
                mesh.position.set(
                    (Math.random() - 0.5) * 100,
                    (Math.random() - 0.5) * 100,
                    (Math.random() - 0.5) * 100
                );
                
                // 存储基因信息
                const geneInfo = {
                    id: `GENE_${i.toString().padStart(3, '0')}`,
                    type: geneType,
                    importance: (importance * 100).toFixed(1) + '%',
                    expression: (Math.random() * 10).toFixed(2),
                    position: {
                        x: mesh.position.x.toFixed(1),
                        y: mesh.position.y.toFixed(1),
                        z: mesh.position.z.toFixed(1)
                    }
                };
                
                mesh.userData = geneInfo;
                geneData.push(geneInfo);
                geneGroup.add(mesh);
            }
            
            // 创建固定信息框
            const infoPanel = document.createElement('div');
            infoPanel.style.cssText = `
                position: absolute;
                bottom: 10px;
                right: 10px;
                width: 200px;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 12px;
                border-radius: 6px;
                font-size: 12px;
                z-index: 1000;
                border: 1px solid #333;
                display: none;
            `;
            infoPanel.innerHTML = '<div style="color: #999;">将鼠标悬停在原子上查看信息</div>';
            container.appendChild(infoPanel);
            
            // 鼠标交互
            const raycaster = new THREE.Raycaster();
            const mouse = new THREE.Vector2();
            let hoveredObject = null;
            
            function onMouseMove(event) {
                // 处理拖拽旋转
                if (isMouseDown) {
                    const deltaX = event.clientX - mouseX;
                    const deltaY = event.clientY - mouseY;
                    
                    // 检测是否开始拖拽
                    if (!isDragging && (Math.abs(deltaX) > 3 || Math.abs(deltaY) > 3)) {
                        isDragging = true;
                    }
                    
                    if (isDragging) {
                        if (isShiftPressed) {
                            // Shift + 拖拽 = 平移
                            targetPanX += deltaX * 0.1;
                            targetPanY -= deltaY * 0.1;
                        } else {
                            // 普通拖拽 = 旋转
                            targetRotationY += deltaX * 0.01;
                        targetRotationX += deltaY * 0.01;
                        }
                    }
                    
                    mouseX = event.clientX;
                    mouseY = event.clientY;
                } else if (!isDragging) {
                    // 处理悬停检测（只在非拖拽状态下）
                    const rect = renderer.domElement.getBoundingClientRect();
                    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
                    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
                    
                    raycaster.setFromCamera(mouse, camera);
                    const intersects = raycaster.intersectObjects(geneGroup.children);
                    
                    if (intersects.length > 0) {
                        const intersected = intersects[0].object;
                        
                        if (hoveredObject !== intersected) {
                            // 恢复之前悬停对象的颜色
                            if (hoveredObject) {
                                hoveredObject.material.emissive.setHex(0x000000);
                            }
                            
                            // 高亮当前悬停对象
                            hoveredObject = intersected;
                            hoveredObject.material.emissive.setHex(0x444444);
                            
                            // 显示信息提示
                            const info = intersected.userData;
                            infoPanel.innerHTML = `
                                <div style="font-weight: bold; color: #4FC3F7; margin-bottom: 5px;">${info.id}</div>
                                <div><span style="color: #81C784;">类型:</span> ${info.type}</div>
                                <div><span style="color: #FFB74D;">重要性:</span> ${info.importance}</div>
                                <div><span style="color: #F06292;">表达量:</span> ${info.expression}</div>
                                <div style="margin-top: 5px; font-size: 10px; color: #999;">
                                    位置: (${info.position.x}, ${info.position.y}, ${info.position.z})
                                </div>
                            `;
                            infoPanel.style.display = 'block';
                        }
                    } else {
                        // 没有悬停对象
                        if (hoveredObject) {
                            hoveredObject.material.emissive.setHex(0x000000);
                            hoveredObject = null;
                        }
                        infoPanel.style.display = 'none';
                    }
                }
            }
            
            renderer.domElement.addEventListener('mousemove', onMouseMove);
            
            // 动画循环
            function animate() {
                if (!renderer.domElement.parentNode) return;
                
                requestAnimationFrame(animate);
                
                // 平滑旋转和平移
                rotationX += (targetRotationX - rotationX) * 0.1;
                rotationY += (targetRotationY - rotationY) * 0.1;
                panX += (targetPanX - panX) * 0.1;
                panY += (targetPanY - panY) * 0.1;
                
                // 应用旋转到场景
                geneGroup.rotation.x = rotationX;
                geneGroup.rotation.y = rotationY;
                geneGroup.position.x = panX;
                geneGroup.position.y = panY;
                
                renderer.render(scene, camera);
            }
            animate();
            
            // 处理窗口大小变化
            function onWindowResize() {
                if (!container.parentNode) return;
                
                camera.aspect = container.clientWidth / container.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, container.clientHeight);
            }
            window.addEventListener('resize', onWindowResize);
            
            return {
                cleanup: () => {
                    window.removeEventListener('resize', onWindowResize);
                    renderer.domElement.removeEventListener('mousemove', onMouseMove);
                    renderer.domElement.removeEventListener('mousedown', () => {});
                    renderer.domElement.removeEventListener('mouseup', () => {});
                    renderer.domElement.removeEventListener('mouseleave', () => {});
                    renderer.domElement.removeEventListener('wheel', () => {});
                    if (tooltip && tooltip.parentNode) {
                        tooltip.parentNode.removeChild(tooltip);
                    }
                    if (renderer.domElement.parentNode) {
                        renderer.domElement.parentNode.removeChild(renderer.domElement);
                    }
                    renderer.dispose();
                }
            };
        }
