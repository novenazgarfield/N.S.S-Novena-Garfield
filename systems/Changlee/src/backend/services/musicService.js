/**
 * Changlee's Groove: 桌宠音乐集成模块
 * 音乐服务 - 提供音乐播放相关的API服务
 */

const path = require('path');
const fs = require('fs');
const MusicScanner = require('./musicScanner');

class MusicService {
  constructor() {
    this.scanner = new MusicScanner();
    this.playlistPath = path.join(__dirname, '../../database/music_playlist.json');
    this.configPath = path.join(__dirname, '../../database/music_config.json');
    this.currentTrack = null;
    this.isPlaying = false;
    this.volume = 0.7;
    this.currentTime = 0;
    this.duration = 0;
    this.playMode = 'sequence'; // sequence, random, repeat
    this.currentIndex = 0;
    
    this.init();
  }

  /**
   * 初始化音乐服务
   */
  async init() {
    try {
      // 确保数据库目录存在
      const dbDir = path.dirname(this.playlistPath);
      if (!fs.existsSync(dbDir)) {
        fs.mkdirSync(dbDir, { recursive: true });
      }

      // 加载配置和播放列表
      await this.loadConfig();
      await this.scanner.loadPlaylist(this.playlistPath);
      
      console.log('音乐服务初始化完成');
    } catch (error) {
      console.error('音乐服务初始化失败:', error);
    }
  }

  /**
   * 加载音乐配置
   */
  async loadConfig() {
    try {
      if (fs.existsSync(this.configPath)) {
        const config = JSON.parse(await fs.promises.readFile(this.configPath, 'utf8'));
        this.volume = config.volume || 0.7;
        this.playMode = config.playMode || 'sequence';
        this.scanner.setMusicFolders(config.musicFolders || []);
      }
    } catch (error) {
      console.error('加载音乐配置失败:', error);
    }
  }

  /**
   * 保存音乐配置
   */
  async saveConfig() {
    try {
      const config = {
        volume: this.volume,
        playMode: this.playMode,
        musicFolders: this.scanner.musicFolders,
        lastUpdated: new Date().toISOString()
      };
      
      await fs.promises.writeFile(this.configPath, JSON.stringify(config, null, 2), 'utf8');
    } catch (error) {
      console.error('保存音乐配置失败:', error);
    }
  }

  /**
   * 设置音乐文件夹
   * @param {string[]} folders - 文件夹路径数组
   */
  async setMusicFolders(folders) {
    this.scanner.setMusicFolders(folders);
    await this.saveConfig();
    return { success: true, message: '音乐文件夹设置成功' };
  }

  /**
   * 扫描音乐文件
   */
  async scanMusic() {
    try {
      const files = await this.scanner.scanAllFolders();
      await this.scanner.savePlaylist(this.playlistPath);
      return {
        success: true,
        message: `扫描完成，发现 ${files.length} 个音频文件`,
        data: {
          totalFiles: files.length,
          stats: this.scanner.getStats()
        }
      };
    } catch (error) {
      return {
        success: false,
        message: '扫描音乐文件失败',
        error: error.message
      };
    }
  }

  /**
   * 获取播放列表
   */
  getPlaylist() {
    return {
      success: true,
      data: {
        playlist: this.scanner.getPlaylist(),
        stats: this.scanner.getStats(),
        currentTrack: this.currentTrack,
        currentIndex: this.currentIndex,
        isPlaying: this.isPlaying,
        volume: this.volume,
        playMode: this.playMode
      }
    };
  }

  /**
   * 搜索音乐
   * @param {string} query - 搜索关键词
   */
  searchMusic(query) {
    const results = this.scanner.search(query);
    return {
      success: true,
      data: {
        query,
        results,
        total: results.length
      }
    };
  }

  /**
   * 按艺术家分组获取音乐
   */
  getMusicByArtist() {
    const grouped = this.scanner.groupByArtist();
    return {
      success: true,
      data: grouped
    };
  }

  /**
   * 播放指定音乐
   * @param {string} trackId - 音乐ID
   */
  playTrack(trackId) {
    const track = this.scanner.findById(trackId);
    if (!track) {
      return {
        success: false,
        message: '找不到指定的音乐文件'
      };
    }

    // 检查文件是否存在
    if (!fs.existsSync(track.path)) {
      return {
        success: false,
        message: '音乐文件不存在或已被移动'
      };
    }

    this.currentTrack = track;
    this.isPlaying = true;
    this.currentIndex = this.scanner.getPlaylist().findIndex(t => t.id === trackId);

    return {
      success: true,
      message: '开始播放',
      data: {
        track: this.currentTrack,
        index: this.currentIndex
      }
    };
  }

  /**
   * 暂停播放
   */
  pauseTrack() {
    this.isPlaying = false;
    return {
      success: true,
      message: '已暂停播放'
    };
  }

  /**
   * 恢复播放
   */
  resumeTrack() {
    if (!this.currentTrack) {
      return {
        success: false,
        message: '没有可播放的音乐'
      };
    }

    this.isPlaying = true;
    return {
      success: true,
      message: '继续播放',
      data: {
        track: this.currentTrack
      }
    };
  }

  /**
   * 停止播放
   */
  stopTrack() {
    this.isPlaying = false;
    this.currentTime = 0;
    return {
      success: true,
      message: '已停止播放'
    };
  }

  /**
   * 下一首
   */
  nextTrack() {
    const playlist = this.scanner.getPlaylist();
    if (playlist.length === 0) {
      return {
        success: false,
        message: '播放列表为空'
      };
    }

    let nextIndex;
    switch (this.playMode) {
      case 'random':
        nextIndex = Math.floor(Math.random() * playlist.length);
        break;
      case 'repeat':
        nextIndex = this.currentIndex; // 重复当前歌曲
        break;
      default: // sequence
        nextIndex = (this.currentIndex + 1) % playlist.length;
    }

    const nextTrack = playlist[nextIndex];
    return this.playTrack(nextTrack.id);
  }

  /**
   * 上一首
   */
  previousTrack() {
    const playlist = this.scanner.getPlaylist();
    if (playlist.length === 0) {
      return {
        success: false,
        message: '播放列表为空'
      };
    }

    let prevIndex;
    switch (this.playMode) {
      case 'random':
        prevIndex = Math.floor(Math.random() * playlist.length);
        break;
      case 'repeat':
        prevIndex = this.currentIndex; // 重复当前歌曲
        break;
      default: // sequence
        prevIndex = this.currentIndex === 0 ? playlist.length - 1 : this.currentIndex - 1;
    }

    const prevTrack = playlist[prevIndex];
    return this.playTrack(prevTrack.id);
  }

  /**
   * 设置音量
   * @param {number} volume - 音量值 (0-1)
   */
  async setVolume(volume) {
    if (volume < 0 || volume > 1) {
      return {
        success: false,
        message: '音量值必须在0-1之间'
      };
    }

    this.volume = volume;
    await this.saveConfig();
    
    return {
      success: true,
      message: '音量设置成功',
      data: { volume: this.volume }
    };
  }

  /**
   * 设置播放模式
   * @param {string} mode - 播放模式 (sequence, random, repeat)
   */
  async setPlayMode(mode) {
    const validModes = ['sequence', 'random', 'repeat'];
    if (!validModes.includes(mode)) {
      return {
        success: false,
        message: '无效的播放模式'
      };
    }

    this.playMode = mode;
    await this.saveConfig();
    
    return {
      success: true,
      message: '播放模式设置成功',
      data: { playMode: this.playMode }
    };
  }

  /**
   * 更新播放进度
   * @param {number} currentTime - 当前播放时间
   * @param {number} duration - 总时长
   */
  updateProgress(currentTime, duration) {
    this.currentTime = currentTime;
    this.duration = duration;
    
    return {
      success: true,
      data: {
        currentTime: this.currentTime,
        duration: this.duration,
        progress: duration > 0 ? currentTime / duration : 0
      }
    };
  }

  /**
   * 获取当前播放状态
   */
  getPlaybackState() {
    return {
      success: true,
      data: {
        currentTrack: this.currentTrack,
        currentIndex: this.currentIndex,
        isPlaying: this.isPlaying,
        volume: this.volume,
        playMode: this.playMode,
        currentTime: this.currentTime,
        duration: this.duration,
        progress: this.duration > 0 ? this.currentTime / this.duration : 0
      }
    };
  }

  /**
   * 创建随机播放列表
   * @param {number} count - 歌曲数量
   */
  createRandomPlaylist(count = 20) {
    const allTracks = this.scanner.getPlaylist();
    if (allTracks.length === 0) {
      return {
        success: false,
        message: '没有可用的音乐文件'
      };
    }

    const shuffled = [...allTracks].sort(() => Math.random() - 0.5);
    const randomPlaylist = shuffled.slice(0, Math.min(count, shuffled.length));

    return {
      success: true,
      message: `创建了包含 ${randomPlaylist.length} 首歌的随机播放列表`,
      data: randomPlaylist
    };
  }

  /**
   * 获取音乐文件的URL（用于前端播放）
   * @param {string} trackId - 音乐ID
   */
  getTrackUrl(trackId) {
    const track = this.scanner.findById(trackId);
    if (!track || !fs.existsSync(track.path)) {
      return {
        success: false,
        message: '音乐文件不存在'
      };
    }

    // 返回文件路径，前端可以通过file://协议访问
    return {
      success: true,
      data: {
        url: `file://${track.path}`,
        track: track
      }
    };
  }
}

module.exports = MusicService;