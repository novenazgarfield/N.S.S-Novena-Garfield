// 通用API客户端
class ApiClient {
  constructor() {
    this.baseURL = '';
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
  }

  // 设置基础URL
  setBaseURL(url) {
    this.baseURL = url;
  }

  // 设置默认头部
  setDefaultHeaders(headers) {
    this.defaultHeaders = { ...this.defaultHeaders, ...headers };
  }

  // GET请求
  async get(endpoint, options = {}) {
    return this.request('GET', endpoint, null, options);
  }

  // POST请求
  async post(endpoint, data, options = {}) {
    return this.request('POST', endpoint, data, options);
  }

  // PUT请求
  async put(endpoint, data, options = {}) {
    return this.request('PUT', endpoint, data, options);
  }

  // DELETE请求
  async delete(endpoint, options = {}) {
    return this.request('DELETE', endpoint, null, options);
  }

  // 通用请求方法
  async request(method, endpoint, data, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      method,
      headers: { ...this.defaultHeaders, ...options.headers },
      ...options
    };

    if (data) {
      if (data instanceof FormData) {
        // 如果是FormData，移除Content-Type让浏览器自动设置
        delete config.headers['Content-Type'];
        config.body = data;
      } else {
        config.body = JSON.stringify(data);
      }
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      } else {
        return await response.text();
      }
    } catch (error) {
      console.error(`API请求失败 [${method} ${url}]:`, error);
      throw error;
    }
  }

  // 上传文件
  async uploadFile(endpoint, file, additionalData = {}) {
    const formData = new FormData();
    formData.append('file', file);
    
    Object.keys(additionalData).forEach(key => {
      formData.append(key, additionalData[key]);
    });

    return this.post(endpoint, formData);
  }

  // 下载文件
  async downloadFile(endpoint, filename) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('文件下载失败:', error);
      throw error;
    }
  }
}

const apiClient = new ApiClient();
export default apiClient;