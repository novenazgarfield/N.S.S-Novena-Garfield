// RAG服务 - 与RAG系统后端API通信
class RagService {
  constructor() {
    this.baseURL = 'http://localhost:51657'; // RAG系统运行地址
    this.apiEndpoint = '/api/rag/query';
  }

  // 发送查询到RAG系统
  async query(question) {
    try {
      const response = await fetch(`${this.baseURL}${this.apiEndpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: question,
          user_id: 'desktop_pet_user',
          session_id: this.getSessionId()
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return this.processResponse(data);
    } catch (error) {
      console.error('RAG查询失败:', error);
      throw new Error('无法连接到RAG服务，请确保服务正在运行');
    }
  }

  // 处理RAG响应
  processResponse(data) {
    return {
      answer: data.response || data.answer || '抱歉，我没有找到相关信息。',
      sources: data.sources || [],
      confidence: data.confidence || 0,
      timestamp: Date.now()
    };
  }

  // 获取或创建会话ID
  getSessionId() {
    let sessionId = localStorage.getItem('rag_session_id');
    if (!sessionId) {
      sessionId = `desktop_pet_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('rag_session_id', sessionId);
    }
    return sessionId;
  }

  // 检查RAG服务状态
  async checkServiceStatus() {
    try {
      const response = await fetch(`${this.baseURL}/health`, {
        method: 'GET',
        timeout: 5000
      });
      return response.ok;
    } catch (error) {
      console.error('RAG服务状态检查失败:', error);
      return false;
    }
  }

  // 获取RAG系统信息
  async getSystemInfo() {
    try {
      const response = await fetch(`${this.baseURL}/api/system/info`, {
        method: 'GET'
      });

      if (response.ok) {
        return await response.json();
      }
      return null;
    } catch (error) {
      console.error('获取系统信息失败:', error);
      return null;
    }
  }

  // 上传文档到RAG系统
  async uploadDocument(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('user_id', 'desktop_pet_user');

      const response = await fetch(`${this.baseURL}/api/documents/upload`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`上传失败: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('文档上传失败:', error);
      throw error;
    }
  }

  // 获取文档列表
  async getDocuments() {
    try {
      const response = await fetch(`${this.baseURL}/api/documents/list?user_id=desktop_pet_user`, {
        method: 'GET'
      });

      if (response.ok) {
        return await response.json();
      }
      return [];
    } catch (error) {
      console.error('获取文档列表失败:', error);
      return [];
    }
  }

  // 删除文档
  async deleteDocument(documentId) {
    try {
      const response = await fetch(`${this.baseURL}/api/documents/${documentId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'desktop_pet_user'
        })
      });

      return response.ok;
    } catch (error) {
      console.error('删除文档失败:', error);
      return false;
    }
  }

  // 清空聊天历史
  async clearChatHistory() {
    try {
      const response = await fetch(`${this.baseURL}/api/chat/clear`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'desktop_pet_user',
          session_id: this.getSessionId()
        })
      });

      return response.ok;
    } catch (error) {
      console.error('清空聊天历史失败:', error);
      return false;
    }
  }
}

export const ragService = new RagService();