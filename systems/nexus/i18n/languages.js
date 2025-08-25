// 🌐 NEXUS Research Workstation - 国际化语言包
// 支持多语言界面切换

const LANGUAGES = {
    // 🇨🇳 简体中文 (默认)
    'zh-CN': {
        name: '简体中文',
        flag: '🇨🇳',
        
        // 导航和标题
        nav: {
            dashboard: 'Dashboard',
            ragSystem: 'RAG System',
            changlee: 'Changlee',
            nexus: 'NEXUS',
            bovineInsight: 'Bovine Insight',
            chronicle: 'Chronicle',
            genomeJigsaw: 'Genome Jigsaw',
            molecularSimulation: 'Molecular Simulation',
            settings: 'Settings'
        },
        
        // 页面标题
        titles: {
            dashboard: 'Dashboard',
            ragSystem: 'RAG System',
            changlee: 'Changlee',
            nexus: 'NEXUS',
            bovineInsight: 'Bovine Insight',
            chronicle: 'Chronicle',
            genomeJigsaw: 'Genome Jigsaw',
            molecularSimulation: 'Molecular Simulation'
        },
        
        // Dashboard 卡片
        cards: {
            ragSystem: {
                title: 'RAG System',
                subtitle: 'Retrieval-Augmented Generation AI',
                features: [
                    '多文档格式支持',
                    '智能对话记忆',
                    'API管理 - 多模型支持'
                ],
                buttons: {
                    launch: '🧠 启动 RAG',
                    docs: '📚 文档库'
                }
            },
            changlee: {
                title: 'Changlee',
                subtitle: '长离的学习胶囊桌宠',
                features: [
                    '情感陪伴式桌面宠物',
                    '英语学习游戏化',
                    '漂流瓶推送系统'
                ],
                buttons: {
                    launch: '🐱 启动长离',
                    games: '🎮 魔法沙滩'
                }
            },
            nexus: {
                title: 'NEXUS',
                subtitle: '统一系统管理平台',
                features: [
                    '系统级部署管理',
                    '依赖检查与安装',
                    '舰队总指挥能力'
                ],
                buttons: {
                    launch: '⚡ 启动 NEXUS',
                    monitor: '📊 系统监控'
                }
            },
            bovineInsight: {
                title: 'Bovine Insight',
                subtitle: '多摄像头牛只识别与体况评分',
                features: [
                    '多摄像头协同工作',
                    '双重身份识别技术',
                    '体况自动评分 (BCS 1-5)'
                ],
                buttons: {
                    launch: '🐄 启动识别',
                    camera: '📹 摄像头管理'
                }
            },
            chronicle: {
                title: 'Chronicle',
                subtitle: 'AI驱动的自动化实验记录仪',
                features: [
                    '全方位活动监控',
                    'AI智能分析引擎',
                    '模式识别与预测'
                ],
                buttons: {
                    launch: '📊 启动记录',
                    analysis: '🔍 数据分析'
                }
            },
            genomeJigsaw: {
                title: 'Genome Jigsaw',
                subtitle: '集成测序分析与基因组拼装',
                features: [
                    '测序数据质量控制',
                    '基因组拼装算法',
                    '序列比对与注释'
                ],
                buttons: {
                    launch: '🧬 启动分析',
                    data: '📁 测序数据'
                }
            },
            molecularSimulation: {
                title: 'Molecular Simulation',
                subtitle: '分子动力学模拟平台',
                features: [
                    '蛋白质折叠模拟',
                    '药物分子对接',
                    'GPU加速计算'
                ],
                buttons: {
                    launch: '⚛️ 启动模拟',
                    results: '📈 结果分析'
                }
            },
            unifiedPlatform: {
                title: 'Unified Platform',
                subtitle: '统一管理与部署平台',
                features: [
                    '一键部署所有系统',
                    '统一配置管理',
                    '实时状态监控'
                ],
                buttons: {
                    launch: '🚀 一键部署',
                    config: '⚙️ 配置管理'
                }
            }
        },
        
        // RAG 聊天界面
        chat: {
            placeholder: '输入你的问题...',
            send: '发送',
            welcome: '根据文档内容，我找到了相关信息...',
            thinking: '我正在分析你的问题，请稍等...',
            error: '抱歉，处理请求时出现错误'
        },
        
        // 通用按钮和操作
        common: {
            back: '返回',
            close: '关闭',
            save: '保存',
            cancel: '取消',
            confirm: '确认',
            delete: '删除',
            edit: '编辑',
            view: '查看',
            download: '下载',
            upload: '上传',
            refresh: '刷新',
            search: '搜索',
            filter: '筛选',
            sort: '排序',
            more: '更多',
            less: '收起',
            loading: '加载中...',
            success: '操作成功',
            error: '操作失败',
            warning: '警告',
            info: '提示'
        },
        
        // 状态指示
        status: {
            online: '在线',
            offline: '离线',
            connecting: '连接中',
            error: '错误',
            maintenance: '维护中',
            updating: '更新中'
        },
        
        // 主题切换
        theme: {
            light: '浅色主题',
            dark: '深色主题',
            auto: '跟随系统'
        }
    },
    
    // 🇺🇸 English
    'en-US': {
        name: 'English',
        flag: '🇺🇸',
        
        nav: {
            dashboard: 'Dashboard',
            ragSystem: 'RAG System',
            changlee: 'Changlee',
            nexus: 'NEXUS',
            bovineInsight: 'Bovine Insight',
            chronicle: 'Chronicle',
            genomeJigsaw: 'Genome Jigsaw',
            molecularSimulation: 'Molecular Simulation',
            settings: 'Settings'
        },
        
        titles: {
            dashboard: 'Dashboard',
            ragSystem: 'RAG System',
            changlee: 'Changlee',
            nexus: 'NEXUS',
            bovineInsight: 'Bovine Insight',
            chronicle: 'Chronicle',
            genomeJigsaw: 'Genome Jigsaw',
            molecularSimulation: 'Molecular Simulation'
        },
        
        cards: {
            ragSystem: {
                title: 'RAG System',
                subtitle: 'Retrieval-Augmented Generation AI',
                features: [
                    'Multi-document format support',
                    'Intelligent conversation memory',
                    'API Management - Multi-model support'
                ],
                buttons: {
                    launch: '🧠 Launch RAG',
                    docs: '📚 Document Library'
                }
            },
            changlee: {
                title: 'Changlee',
                subtitle: 'Changlee\'s Learning Capsule Pet',
                features: [
                    'Emotional companion desktop pet',
                    'Gamified English learning',
                    'Message bottle push system'
                ],
                buttons: {
                    launch: '🐱 Launch Changlee',
                    games: '🎮 Magic Beach'
                }
            },
            nexus: {
                title: 'NEXUS',
                subtitle: 'Unified System Management Platform',
                features: [
                    'System-level deployment management',
                    'Dependency check & installation',
                    'Fleet command capabilities'
                ],
                buttons: {
                    launch: '⚡ Launch NEXUS',
                    monitor: '📊 System Monitor'
                }
            },
            bovineInsight: {
                title: 'Bovine Insight',
                subtitle: 'Multi-camera Cattle Recognition & BCS',
                features: [
                    'Multi-camera coordination',
                    'Dual identity recognition',
                    'Automatic BCS scoring (1-5)'
                ],
                buttons: {
                    launch: '🐄 Launch Recognition',
                    camera: '📹 Camera Management'
                }
            },
            chronicle: {
                title: 'Chronicle',
                subtitle: 'AI-driven Automated Experiment Recorder',
                features: [
                    'Comprehensive activity monitoring',
                    'AI intelligent analysis engine',
                    'Pattern recognition & prediction'
                ],
                buttons: {
                    launch: '📊 Launch Recording',
                    analysis: '🔍 Data Analysis'
                }
            },
            genomeJigsaw: {
                title: 'Genome Jigsaw',
                subtitle: 'Integrated Sequencing Analysis & Assembly',
                features: [
                    'Sequencing data quality control',
                    'Genome assembly algorithms',
                    'Sequence alignment & annotation'
                ],
                buttons: {
                    launch: '🧬 Launch Analysis',
                    data: '📁 Sequencing Data'
                }
            },
            molecularSimulation: {
                title: 'Molecular Simulation',
                subtitle: 'Molecular Dynamics Simulation Platform',
                features: [
                    'Protein folding simulation',
                    'Drug molecular docking',
                    'GPU-accelerated computing'
                ],
                buttons: {
                    launch: '⚛️ Launch Simulation',
                    results: '📈 Result Analysis'
                }
            },
            unifiedPlatform: {
                title: 'Unified Platform',
                subtitle: 'Unified Management & Deployment',
                features: [
                    'One-click deploy all systems',
                    'Unified configuration management',
                    'Real-time status monitoring'
                ],
                buttons: {
                    launch: '🚀 One-click Deploy',
                    config: '⚙️ Configuration'
                }
            }
        },
        
        chat: {
            placeholder: 'Enter your question...',
            send: 'Send',
            welcome: 'Based on the document content, I found relevant information...',
            thinking: 'I\'m analyzing your question, please wait...',
            error: 'Sorry, an error occurred while processing the request'
        },
        
        common: {
            back: 'Back',
            close: 'Close',
            save: 'Save',
            cancel: 'Cancel',
            confirm: 'Confirm',
            delete: 'Delete',
            edit: 'Edit',
            view: 'View',
            download: 'Download',
            upload: 'Upload',
            refresh: 'Refresh',
            search: 'Search',
            filter: 'Filter',
            sort: 'Sort',
            more: 'More',
            less: 'Less',
            loading: 'Loading...',
            success: 'Success',
            error: 'Error',
            warning: 'Warning',
            info: 'Info'
        },
        
        status: {
            online: 'Online',
            offline: 'Offline',
            connecting: 'Connecting',
            error: 'Error',
            maintenance: 'Maintenance',
            updating: 'Updating'
        },
        
        theme: {
            light: 'Light Theme',
            dark: 'Dark Theme',
            auto: 'Follow System'
        }
    },
    
    // 🇯🇵 日本語
    'ja-JP': {
        name: '日本語',
        flag: '🇯🇵',
        
        nav: {
            dashboard: 'ダッシュボード',
            ragSystem: 'RAGシステム',
            changlee: 'チャンリー',
            nexus: 'NEXUS',
            bovineInsight: '牛認識システム',
            chronicle: 'クロニクル',
            genomeJigsaw: 'ゲノムジグソー',
            molecularSimulation: '分子シミュレーション',
            settings: '設定'
        },
        
        titles: {
            dashboard: 'ダッシュボード',
            ragSystem: 'RAGシステム',
            changlee: 'チャンリー',
            nexus: 'NEXUS',
            bovineInsight: '牛認識システム',
            chronicle: 'クロニクル',
            genomeJigsaw: 'ゲノムジグソー',
            molecularSimulation: '分子シミュレーション'
        },
        
        cards: {
            ragSystem: {
                title: 'RAGシステム',
                subtitle: '検索拡張生成AI',
                features: [
                    '複数文書形式サポート',
                    'インテリジェント会話メモリ',
                    'API管理 - マルチモデルサポート'
                ],
                buttons: {
                    launch: '🧠 RAG起動',
                    docs: '📚 文書ライブラリ'
                }
            },
            changlee: {
                title: 'チャンリー',
                subtitle: 'チャンリーの学習カプセルペット',
                features: [
                    '感情的コンパニオンデスクトップペット',
                    'ゲーム化英語学習',
                    'メッセージボトルプッシュシステム'
                ],
                buttons: {
                    launch: '🐱 チャンリー起動',
                    games: '🎮 マジックビーチ'
                }
            },
            nexus: {
                title: 'NEXUS',
                subtitle: '統合システム管理プラットフォーム',
                features: [
                    'システムレベル展開管理',
                    '依存関係チェック＆インストール',
                    'フリート指揮能力'
                ],
                buttons: {
                    launch: '⚡ NEXUS起動',
                    monitor: '📊 システム監視'
                }
            },
            bovineInsight: {
                title: '牛認識システム',
                subtitle: 'マルチカメラ牛認識＆体況評価',
                features: [
                    'マルチカメラ協調',
                    '二重身元認識技術',
                    '自動体況評価 (BCS 1-5)'
                ],
                buttons: {
                    launch: '🐄 認識起動',
                    camera: '📹 カメラ管理'
                }
            },
            chronicle: {
                title: 'クロニクル',
                subtitle: 'AI駆動自動実験記録器',
                features: [
                    '包括的活動監視',
                    'AIインテリジェント分析エンジン',
                    'パターン認識＆予測'
                ],
                buttons: {
                    launch: '📊 記録起動',
                    analysis: '🔍 データ分析'
                }
            },
            genomeJigsaw: {
                title: 'ゲノムジグソー',
                subtitle: '統合シーケンス分析＆アセンブリ',
                features: [
                    'シーケンスデータ品質管理',
                    'ゲノムアセンブリアルゴリズム',
                    'シーケンスアライメント＆アノテーション'
                ],
                buttons: {
                    launch: '🧬 分析起動',
                    data: '📁 シーケンスデータ'
                }
            },
            molecularSimulation: {
                title: '分子シミュレーション',
                subtitle: '分子動力学シミュレーションプラットフォーム',
                features: [
                    'タンパク質フォールディングシミュレーション',
                    '薬物分子ドッキング',
                    'GPU加速計算'
                ],
                buttons: {
                    launch: '⚛️ シミュレーション起動',
                    results: '📈 結果分析'
                }
            },
            unifiedPlatform: {
                title: '統合プラットフォーム',
                subtitle: '統合管理＆展開',
                features: [
                    'ワンクリック全システム展開',
                    '統合設定管理',
                    'リアルタイムステータス監視'
                ],
                buttons: {
                    launch: '🚀 ワンクリック展開',
                    config: '⚙️ 設定'
                }
            }
        },
        
        chat: {
            placeholder: '質問を入力してください...',
            send: '送信',
            welcome: '文書内容に基づいて、関連情報を見つけました...',
            thinking: '質問を分析中です。お待ちください...',
            error: '申し訳ございません。リクエスト処理中にエラーが発生しました'
        },
        
        common: {
            back: '戻る',
            close: '閉じる',
            save: '保存',
            cancel: 'キャンセル',
            confirm: '確認',
            delete: '削除',
            edit: '編集',
            view: '表示',
            download: 'ダウンロード',
            upload: 'アップロード',
            refresh: '更新',
            search: '検索',
            filter: 'フィルター',
            sort: 'ソート',
            more: 'もっと',
            less: '少なく',
            loading: '読み込み中...',
            success: '成功',
            error: 'エラー',
            warning: '警告',
            info: '情報'
        },
        
        status: {
            online: 'オンライン',
            offline: 'オフライン',
            connecting: '接続中',
            error: 'エラー',
            maintenance: 'メンテナンス',
            updating: '更新中'
        },
        
        theme: {
            light: 'ライトテーマ',
            dark: 'ダークテーマ',
            auto: 'システムに従う'
        }
    }
};

// 默认语言
const DEFAULT_LANGUAGE = 'zh-CN';

// 获取浏览器语言
function getBrowserLanguage() {
    const lang = navigator.language || navigator.userLanguage;
    if (LANGUAGES[lang]) {
        return lang;
    }
    // 尝试匹配语言代码的前缀
    const langPrefix = lang.split('-')[0];
    for (const key in LANGUAGES) {
        if (key.startsWith(langPrefix)) {
            return key;
        }
    }
    return DEFAULT_LANGUAGE;
}

// 导出语言包
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { LANGUAGES, DEFAULT_LANGUAGE, getBrowserLanguage };
}