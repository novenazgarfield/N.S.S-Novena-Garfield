/**
 * Changlee's Groove: 桌宠音乐集成模块
 * 音乐扫描服务 - 负责发现和管理用户的本地音乐文件
 */

const fs = require('fs');
const path = require('path');
const { promisify } = require('util');

const readdir = promisify(fs.readdir);
const stat = promisify(fs.stat);

class MusicScanner {
  constructor() {
    this.supportedFormats = ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg'];
    this.musicFolders = [];
    this.playlist = [];
  }

  /**
   * 设置音乐文件夹路径
   * @param {string[]} folders - 音乐文件夹路径数组
   */
  setMusicFolders(folders) {
    this.musicFolders = folders.filter(folder => {
      try {
        return fs.existsSync(folder) && fs.statSync(folder).isDirectory();
      } catch (error) {
        console.warn(`音乐文件夹不存在或无法访问: ${folder}`);
        return false;
      }
    });
  }

  /**
   * 递归扫描文件夹中的音频文件
   * @param {string} folderPath - 文件夹路径
   * @returns {Promise<Array>} 音频文件信息数组
   */
  async scanFolder(folderPath) {
    const audioFiles = [];

    try {
      const items = await readdir(folderPath);

      for (const item of items) {
        const itemPath = path.join(folderPath, item);
        const itemStat = await stat(itemPath);

        if (itemStat.isDirectory()) {
          // 递归扫描子文件夹
          const subFiles = await this.scanFolder(itemPath);
          audioFiles.push(...subFiles);
        } else if (itemStat.isFile()) {
          const ext = path.extname(item).toLowerCase();
          if (this.supportedFormats.includes(ext)) {
            const fileInfo = this.extractFileInfo(itemPath, item);
            audioFiles.push(fileInfo);
          }
        }
      }
    } catch (error) {
      console.error(`扫描文件夹失败: ${folderPath}`, error);
    }

    return audioFiles;
  }

  /**
   * 提取音频文件信息
   * @param {string} filePath - 文件完整路径
   * @param {string} fileName - 文件名
   * @returns {Object} 文件信息对象
   */
  extractFileInfo(filePath, fileName) {
    const ext = path.extname(fileName).toLowerCase();
    const nameWithoutExt = path.basename(fileName, ext);
    
    // 尝试从文件名解析艺术家和歌曲名
    let artist = '未知艺术家';
    let title = nameWithoutExt;
    
    // 常见格式: "艺术家 - 歌曲名" 或 "艺术家-歌曲名"
    const separators = [' - ', ' – ', ' — ', '-'];
    for (const sep of separators) {
      if (nameWithoutExt.includes(sep)) {
        const parts = nameWithoutExt.split(sep);
        if (parts.length >= 2) {
          artist = parts[0].trim();
          title = parts.slice(1).join(sep).trim();
          break;
        }
      }
    }

    return {
      id: this.generateId(filePath),
      path: filePath,
      fileName: fileName,
      title: title,
      artist: artist,
      format: ext.substring(1), // 去掉点号
      size: this.getFileSize(filePath),
      addedAt: new Date().toISOString()
    };
  }

  /**
   * 获取文件大小
   * @param {string} filePath - 文件路径
   * @returns {number} 文件大小（字节）
   */
  getFileSize(filePath) {
    try {
      return fs.statSync(filePath).size;
    } catch (error) {
      return 0;
    }
  }

  /**
   * 生成文件唯一ID
   * @param {string} filePath - 文件路径
   * @returns {string} 唯一ID
   */
  generateId(filePath) {
    return Buffer.from(filePath).toString('base64').replace(/[^a-zA-Z0-9]/g, '').substring(0, 16);
  }

  /**
   * 扫描所有配置的音乐文件夹
   * @returns {Promise<Array>} 所有音频文件信息
   */
  async scanAllFolders() {
    const allFiles = [];

    for (const folder of this.musicFolders) {
      console.log(`正在扫描音乐文件夹: ${folder}`);
      const files = await this.scanFolder(folder);
      allFiles.push(...files);
    }

    // 去重（基于文件路径）
    const uniqueFiles = allFiles.filter((file, index, self) => 
      index === self.findIndex(f => f.path === file.path)
    );

    this.playlist = uniqueFiles;
    console.log(`扫描完成，共发现 ${uniqueFiles.length} 个音频文件`);
    
    return uniqueFiles;
  }

  /**
   * 获取当前播放列表
   * @returns {Array} 播放列表
   */
  getPlaylist() {
    return this.playlist;
  }

  /**
   * 根据ID查找音频文件
   * @param {string} id - 文件ID
   * @returns {Object|null} 文件信息
   */
  findById(id) {
    return this.playlist.find(file => file.id === id) || null;
  }

  /**
   * 搜索音频文件
   * @param {string} query - 搜索关键词
   * @returns {Array} 匹配的文件列表
   */
  search(query) {
    if (!query || query.trim() === '') {
      return this.playlist;
    }

    const searchTerm = query.toLowerCase().trim();
    return this.playlist.filter(file => 
      file.title.toLowerCase().includes(searchTerm) ||
      file.artist.toLowerCase().includes(searchTerm) ||
      file.fileName.toLowerCase().includes(searchTerm)
    );
  }

  /**
   * 按艺术家分组
   * @returns {Object} 按艺术家分组的文件
   */
  groupByArtist() {
    const grouped = {};
    this.playlist.forEach(file => {
      if (!grouped[file.artist]) {
        grouped[file.artist] = [];
      }
      grouped[file.artist].push(file);
    });
    return grouped;
  }

  /**
   * 获取统计信息
   * @returns {Object} 统计信息
   */
  getStats() {
    const totalFiles = this.playlist.length;
    const totalSize = this.playlist.reduce((sum, file) => sum + file.size, 0);
    const formats = [...new Set(this.playlist.map(file => file.format))];
    const artists = [...new Set(this.playlist.map(file => file.artist))];

    return {
      totalFiles,
      totalSize,
      totalSizeFormatted: this.formatBytes(totalSize),
      formats,
      totalArtists: artists.length,
      artists: artists.slice(0, 10) // 只返回前10个艺术家
    };
  }

  /**
   * 格式化字节大小
   * @param {number} bytes - 字节数
   * @returns {string} 格式化后的大小
   */
  formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * 保存播放列表到文件
   * @param {string} filePath - 保存路径
   */
  async savePlaylist(filePath) {
    try {
      const data = {
        version: '1.0.0',
        createdAt: new Date().toISOString(),
        musicFolders: this.musicFolders,
        playlist: this.playlist,
        stats: this.getStats()
      };
      
      await fs.promises.writeFile(filePath, JSON.stringify(data, null, 2), 'utf8');
      console.log(`播放列表已保存到: ${filePath}`);
    } catch (error) {
      console.error('保存播放列表失败:', error);
      throw error;
    }
  }

  /**
   * 从文件加载播放列表
   * @param {string} filePath - 文件路径
   */
  async loadPlaylist(filePath) {
    try {
      if (!fs.existsSync(filePath)) {
        console.log('播放列表文件不存在，将创建新的播放列表');
        return;
      }

      const data = JSON.parse(await fs.promises.readFile(filePath, 'utf8'));
      this.musicFolders = data.musicFolders || [];
      this.playlist = data.playlist || [];
      
      console.log(`播放列表已加载，共 ${this.playlist.length} 个文件`);
    } catch (error) {
      console.error('加载播放列表失败:', error);
      throw error;
    }
  }
}

module.exports = MusicScanner;