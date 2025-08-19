/**
 * Changlee's Groove: 桌宠音乐集成模块
 * 前端音乐API服务封装
 */

const API_BASE_URL = 'http://localhost:3001/api/music';

class MusicAPI {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  /**
   * 通用API请求方法
   * @param {string} endpoint - API端点
   * @param {Object} options - 请求选项
   * @returns {Promise<Object>} API响应
   */
  async request(endpoint, options = {}) {
    try {
      const url = `${this.baseURL}${endpoint}`;
      const config = {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      };

      const response = await fetch(url, config);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || `HTTP ${response.status}`);
      }
      
      return data;
    } catch (error) {
      console.error(`音乐API请求失败 [${endpoint}]:`, error);
      throw error;
    }
  }

  /**
   * 获取播放列表
   * @returns {Promise<Object>} 播放列表数据
   */
  async getPlaylist() {
    return await this.request('/playlist');
  }

  /**
   * 搜索音乐
   * @param {string} query - 搜索关键词
   * @returns {Promise<Object>} 搜索结果
   */
  async searchMusic(query) {
    return await this.request(`/search?q=${encodeURIComponent(query)}`);
  }

  /**
   * 按艺术家分组获取音乐
   * @returns {Promise<Object>} 按艺术家分组的音乐
   */
  async getMusicByArtist() {
    return await this.request('/artists');
  }

  /**
   * 设置音乐文件夹
   * @param {string[]} folders - 文件夹路径数组
   * @returns {Promise<Object>} 设置结果
   */
  async setMusicFolders(folders) {
    return await this.request('/folders', {
      method: 'POST',
      body: JSON.stringify({ folders })
    });
  }

  /**
   * 扫描音乐文件
   * @returns {Promise<Object>} 扫描结果
   */
  async scanMusic() {
    return await this.request('/scan', {
      method: 'POST'
    });
  }

  /**
   * 播放指定音乐
   * @param {string} trackId - 音乐ID
   * @returns {Promise<Object>} 播放结果
   */
  async playTrack(trackId) {
    return await this.request(`/play/${trackId}`, {
      method: 'POST'
    });
  }

  /**
   * 暂停播放
   * @returns {Promise<Object>} 操作结果
   */
  async pauseTrack() {
    return await this.request('/pause', {
      method: 'POST'
    });
  }

  /**
   * 恢复播放
   * @returns {Promise<Object>} 操作结果
   */
  async resumeTrack() {
    return await this.request('/resume', {
      method: 'POST'
    });
  }

  /**
   * 停止播放
   * @returns {Promise<Object>} 操作结果
   */
  async stopTrack() {
    return await this.request('/stop', {
      method: 'POST'
    });
  }

  /**
   * 下一首
   * @returns {Promise<Object>} 操作结果
   */
  async nextTrack() {
    return await this.request('/next', {
      method: 'POST'
    });
  }

  /**
   * 上一首
   * @returns {Promise<Object>} 操作结果
   */
  async previousTrack() {
    return await this.request('/previous', {
      method: 'POST'
    });
  }

  /**
   * 设置音量
   * @param {number} volume - 音量值 (0-1)
   * @returns {Promise<Object>} 操作结果
   */
  async setVolume(volume) {
    return await this.request('/volume', {
      method: 'POST',
      body: JSON.stringify({ volume })
    });
  }

  /**
   * 设置播放模式
   * @param {string} mode - 播放模式 (sequence, random, repeat)
   * @returns {Promise<Object>} 操作结果
   */
  async setPlayMode(mode) {
    return await this.request('/playmode', {
      method: 'POST',
      body: JSON.stringify({ mode })
    });
  }

  /**
   * 更新播放进度
   * @param {number} currentTime - 当前播放时间
   * @param {number} duration - 总时长
   * @returns {Promise<Object>} 操作结果
   */
  async updateProgress(currentTime, duration) {
    return await this.request('/progress', {
      method: 'POST',
      body: JSON.stringify({ currentTime, duration })
    });
  }

  /**
   * 获取播放状态
   * @returns {Promise<Object>} 播放状态
   */
  async getPlaybackState() {
    return await this.request('/state');
  }

  /**
   * 获取音乐文件URL
   * @param {string} trackId - 音乐ID
   * @returns {Promise<Object>} 文件URL
   */
  async getTrackUrl(trackId) {
    return await this.request(`/url/${trackId}`);
  }

  /**
   * 创建随机播放列表
   * @param {number} count - 歌曲数量
   * @returns {Promise<Object>} 随机播放列表
   */
  async createRandomPlaylist(count = 20) {
    return await this.request('/random-playlist', {
      method: 'POST',
      body: JSON.stringify({ count })
    });
  }
}

// 创建单例实例
const musicAPI = new MusicAPI();

export default musicAPI;