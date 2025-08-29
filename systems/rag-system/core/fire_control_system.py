"""
🎯 火控系统 (Fire Control System)
================================

实现"大宪章"第四章：知识的"掌控"
- 三段式拨盘控制
- 后端请求路由
- AI注意力精确控制
- 神之档位接口预留

Author: N.S.S-Novena-Garfield Project
Version: 2.0.0 - "Genesis" Chapter 4
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json

from utils.logger import logger

class SearchScope(Enum):
    """搜索范围枚举"""
    CURRENT_CHAT = "current_chat"      # 当前聊天
    CURRENT_DOCUMENT = "current_document"  # 当前文档
    FULL_DATABASE = "full_database"    # 全数据库
    GOD_MODE = "god_mode"             # 神之档位（未来功能）

@dataclass
class FireControlConfig:
    """火控系统配置"""
    default_scope: SearchScope = SearchScope.FULL_DATABASE
    chat_history_limit: int = 50  # 当前聊天历史限制
    document_chunk_limit: int = 100  # 当前文档块限制
    enable_god_mode: bool = False  # 是否启用神之档位
    attention_focus_weight: float = 1.0  # 注意力聚焦权重

@dataclass
class AttentionTarget:
    """注意力目标"""
    scope: SearchScope
    target_id: Optional[str] = None  # 文档ID或聊天ID
    metadata: Dict[str, Any] = None
    focus_keywords: List[str] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.focus_keywords is None:
            self.focus_keywords = []

class FireControlSystem:
    """火控系统 - AI注意力的终极控制器"""
    
    def __init__(self, config: FireControlConfig = None):
        self.config = config or FireControlConfig()
        self.current_target = AttentionTarget(scope=self.config.default_scope)
        self.chat_history = []  # 聊天历史
        self.active_documents = {}  # 活跃文档
        
        logger.info("🎯 火控系统已激活 - AI注意力控制就绪")
    
    def set_attention_target(self, scope: SearchScope, target_id: str = None, 
                           focus_keywords: List[str] = None) -> Dict[str, Any]:
        """设置注意力目标"""
        try:
            logger.info(f"🎯 设置注意力目标: {scope.value}")
            
            # 验证目标有效性
            if not self._validate_target(scope, target_id):
                return {
                    "success": False,
                    "message": f"无效的注意力目标: {scope.value}",
                    "scope": scope.value
                }
            
            # 更新当前目标
            self.current_target = AttentionTarget(
                scope=scope,
                target_id=target_id,
                focus_keywords=focus_keywords or [],
                metadata=self._get_target_metadata(scope, target_id)
            )
            
            logger.info(f"✅ 注意力目标已锁定: {scope.value}")
            
            return {
                "success": True,
                "message": f"注意力已聚焦到: {self._get_scope_description(scope)}",
                "scope": scope.value,
                "target_id": target_id,
                "metadata": self.current_target.metadata,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"设置注意力目标失败: {e}")
            return {
                "success": False,
                "message": f"火控系统错误: {str(e)}",
                "scope": scope.value
            }
    
    def get_retrieval_strategy(self, query: str) -> Dict[str, Any]:
        """根据当前注意力目标获取检索策略"""
        try:
            scope = self.current_target.scope
            
            strategy = {
                "scope": scope.value,
                "query": query,
                "target_id": self.current_target.target_id,
                "focus_keywords": self.current_target.focus_keywords,
                "filters": {},
                "boost_params": {},
                "attention_weight": self.config.attention_focus_weight
            }
            
            # 根据不同范围设置策略
            if scope == SearchScope.CURRENT_CHAT:
                strategy.update(self._get_chat_strategy(query))
            elif scope == SearchScope.CURRENT_DOCUMENT:
                strategy.update(self._get_document_strategy(query))
            elif scope == SearchScope.FULL_DATABASE:
                strategy.update(self._get_database_strategy(query))
            elif scope == SearchScope.GOD_MODE:
                strategy.update(self._get_god_mode_strategy(query))
            
            logger.info(f"🎯 检索策略已生成: {scope.value}")
            return strategy
            
        except Exception as e:
            logger.error(f"生成检索策略失败: {e}")
            return self._get_fallback_strategy(query)
    
    def _validate_target(self, scope: SearchScope, target_id: str = None) -> bool:
        """验证注意力目标的有效性"""
        if scope == SearchScope.CURRENT_DOCUMENT and not target_id:
            return False
        
        if scope == SearchScope.GOD_MODE and not self.config.enable_god_mode:
            return False
        
        return True
    
    def _get_target_metadata(self, scope: SearchScope, target_id: str = None) -> Dict[str, Any]:
        """获取目标元数据"""
        metadata = {
            "scope_description": self._get_scope_description(scope),
            "timestamp": datetime.now().isoformat()
        }
        
        if scope == SearchScope.CURRENT_CHAT:
            metadata.update({
                "chat_history_count": len(self.chat_history),
                "history_limit": self.config.chat_history_limit
            })
        elif scope == SearchScope.CURRENT_DOCUMENT and target_id:
            metadata.update({
                "document_id": target_id,
                "document_info": self.active_documents.get(target_id, {})
            })
        elif scope == SearchScope.FULL_DATABASE:
            metadata.update({
                "database_scope": "unlimited",
                "active_documents": len(self.active_documents)
            })
        
        return metadata
    
    def _get_scope_description(self, scope: SearchScope) -> str:
        """获取范围描述"""
        descriptions = {
            SearchScope.CURRENT_CHAT: "当前聊天对话",
            SearchScope.CURRENT_DOCUMENT: "当前文档内容",
            SearchScope.FULL_DATABASE: "全数据库知识",
            SearchScope.GOD_MODE: "神之档位 - 文档对比全库"
        }
        return descriptions.get(scope, "未知范围")
    
    def _get_chat_strategy(self, query: str) -> Dict[str, Any]:
        """获取聊天范围检索策略"""
        return {
            "retrieval_type": "chat_history",
            "filters": {
                "source_type": "chat",
                "limit": self.config.chat_history_limit
            },
            "boost_params": {
                "recent_messages": 2.0,
                "user_queries": 1.5,
                "context_relevance": 1.8
            },
            "search_fields": ["message_content", "context"],
            "time_decay": True
        }
    
    def _get_document_strategy(self, query: str) -> Dict[str, Any]:
        """获取文档范围检索策略"""
        return {
            "retrieval_type": "document_focused",
            "filters": {
                "document_id": self.current_target.target_id,
                "limit": self.config.document_chunk_limit
            },
            "boost_params": {
                "document_title": 2.5,
                "section_headers": 2.0,
                "paragraph_content": 1.0,
                "keyword_match": 3.0
            },
            "search_fields": ["content", "title", "headers"],
            "hierarchical_search": True
        }
    
    def _get_database_strategy(self, query: str) -> Dict[str, Any]:
        """获取全数据库检索策略"""
        return {
            "retrieval_type": "full_database",
            "filters": {
                "scope": "unlimited"
            },
            "boost_params": {
                "relevance_score": 1.0,
                "document_authority": 1.2,
                "freshness": 1.1
            },
            "search_fields": ["content", "title", "metadata"],
            "use_shields": True,
            "enable_reranking": True
        }
    
    def _get_god_mode_strategy(self, query: str) -> Dict[str, Any]:
        """获取神之档位检索策略（预留接口）"""
        return {
            "retrieval_type": "god_mode",
            "filters": {
                "primary_document": self.current_target.target_id,
                "comparison_scope": "full_database"
            },
            "boost_params": {
                "document_contrast": 3.0,
                "unique_insights": 2.5,
                "cross_reference": 2.0
            },
            "search_fields": ["content", "insights", "comparisons"],
            "enable_contrast_analysis": True,
            "generate_insights": True,
            "cross_document_analysis": True
        }
    
    def _get_fallback_strategy(self, query: str) -> Dict[str, Any]:
        """获取备用策略"""
        return {
            "retrieval_type": "fallback",
            "scope": SearchScope.FULL_DATABASE.value,
            "query": query,
            "filters": {},
            "boost_params": {},
            "error": "使用备用检索策略"
        }
    
    def update_chat_history(self, message: Dict[str, Any]):
        """更新聊天历史"""
        try:
            self.chat_history.append({
                "timestamp": datetime.now().isoformat(),
                "content": message.get("content", ""),
                "role": message.get("role", "user"),
                "metadata": message.get("metadata", {})
            })
            
            # 限制历史长度
            if len(self.chat_history) > self.config.chat_history_limit:
                self.chat_history = self.chat_history[-self.config.chat_history_limit:]
            
            logger.debug(f"聊天历史已更新，当前长度: {len(self.chat_history)}")
            
        except Exception as e:
            logger.error(f"更新聊天历史失败: {e}")
    
    def register_document(self, document_id: str, document_info: Dict[str, Any]):
        """注册活跃文档"""
        try:
            self.active_documents[document_id] = {
                "title": document_info.get("title", "未知文档"),
                "size": document_info.get("size", 0),
                "type": document_info.get("type", "unknown"),
                "timestamp": datetime.now().isoformat(),
                "metadata": document_info.get("metadata", {})
            }
            
            logger.info(f"文档已注册: {document_id}")
            
        except Exception as e:
            logger.error(f"注册文档失败: {e}")
    
    def get_fire_control_status(self) -> Dict[str, Any]:
        """获取火控系统状态"""
        try:
            return {
                "status": "operational",
                "system_version": "2.0.0-Genesis-Chapter4",
                "current_target": {
                    "scope": self.current_target.scope.value,
                    "target_id": self.current_target.target_id,
                    "focus_keywords": self.current_target.focus_keywords,
                    "metadata": self.current_target.metadata
                },
                "capabilities": [
                    "三段式拨盘控制",
                    "AI注意力精确定位",
                    "动态检索策略",
                    "聊天历史管理",
                    "文档范围控制",
                    "神之档位预留"
                ],
                "configuration": {
                    "default_scope": self.config.default_scope.value,
                    "chat_history_limit": self.config.chat_history_limit,
                    "document_chunk_limit": self.config.document_chunk_limit,
                    "god_mode_enabled": self.config.enable_god_mode,
                    "attention_focus_weight": self.config.attention_focus_weight
                },
                "statistics": {
                    "chat_history_count": len(self.chat_history),
                    "active_documents_count": len(self.active_documents),
                    "current_scope": self.current_target.scope.value
                },
                "last_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取火控系统状态失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def enable_god_mode(self, enable: bool = True):
        """启用/禁用神之档位"""
        self.config.enable_god_mode = enable
        logger.info(f"🔥 神之档位已{'启用' if enable else '禁用'}")
    
    def get_available_scopes(self) -> List[Dict[str, Any]]:
        """获取可用的搜索范围"""
        scopes = [
            {
                "value": SearchScope.CURRENT_CHAT.value,
                "label": "当前聊天",
                "description": "仅在当前对话历史中搜索",
                "icon": "💬",
                "available": True
            },
            {
                "value": SearchScope.CURRENT_DOCUMENT.value,
                "label": "当前文档", 
                "description": "仅在当前选定文档中搜索",
                "icon": "📄",
                "available": bool(self.active_documents)
            },
            {
                "value": SearchScope.FULL_DATABASE.value,
                "label": "全数据库",
                "description": "在整个知识库中搜索",
                "icon": "🗄️",
                "available": True
            }
        ]
        
        # 如果启用了神之档位
        if self.config.enable_god_mode:
            scopes.append({
                "value": SearchScope.GOD_MODE.value,
                "label": "神之档位",
                "description": "当前文档对比全数据库的终极洞察",
                "icon": "⚡",
                "available": bool(self.active_documents)
            })
        
        return scopes