// 音乐服务 - 处理本地音乐文件扫描和管理
class MusicService {
  constructor() {
    this.supportedFormats = ['.mp3', '.wav', '.ogg', '.m4a', '.flac'];
  }

  // 扫描本地音乐文件
  async scanLocalMusic() {
    try {
      // 通过 Electron 的 IPC 调用主进程的文件扫描功能
      if (window.electronAPI && window.electronAPI.scanMusicFiles) {
        const musicFiles = await window.electronAPI.scanMusicFiles();
        return this.processMusicFiles(musicFiles);
      } else {
        // 如果在 Web 环境中，返回示例数据
        console.warn('Electron API 不可用，返回示例音乐数据');
        return this.getMockMusicData();
      }
    } catch (error) {
      console.error('扫描音乐文件失败:', error);
      return [];
    }
  }

  // 处理音乐文件数据
  processMusicFiles(files) {
    return files.map((file, index) => ({
      id: `track_${index}`,
      title: this.extractTitle(file.name),
      artist: file.artist || '未知艺术家',
      album: file.album || '未知专辑',
      duration: file.duration,
      path: file.path,
      url: `file://${file.path}`,
      size: file.size,
      format: this.getFileFormat(file.name)
    }));
  }

  // 从文件名提取标题
  extractTitle(filename) {
    const nameWithoutExt = filename.replace(/\.[^/.]+$/, '');
    // 移除常见的编号前缀
    return nameWithoutExt.replace(/^\d+[\s\-\.]*/, '');
  }

  // 获取文件格式
  getFileFormat(filename) {
    const ext = filename.toLowerCase().match(/\.[^/.]+$/);
    return ext ? ext[0] : '';
  }

  // 获取模拟音乐数据（用于测试）
  getMockMusicData() {
    return [
      {
        id: 'mock_1',
        title: '示例音乐 1',
        artist: '示例艺术家',
        album: '示例专辑',
        duration: 180,
        path: '/mock/path/music1.mp3',
        url: '/mock/path/music1.mp3',
        format: '.mp3'
      },
      {
        id: 'mock_2',
        title: '示例音乐 2',
        artist: '另一个艺术家',
        album: '另一个专辑',
        duration: 240,
        path: '/mock/path/music2.mp3',
        url: '/mock/path/music2.mp3',
        format: '.mp3'
      }
    ];
  }

  // 验证文件是否为支持的音乐格式
  isSupportedFormat(filename) {
    const ext = this.getFileFormat(filename);
    return this.supportedFormats.includes(ext);
  }

  // 获取音乐文件的元数据
  async getMusicMetadata(filePath) {
    try {
      if (window.electronAPI && window.electronAPI.getMusicMetadata) {
        return await window.electronAPI.getMusicMetadata(filePath);
      }
      return null;
    } catch (error) {
      console.error('获取音乐元数据失败:', error);
      return null;
    }
  }

  // 创建播放列表
  createPlaylist(name, tracks) {
    const playlist = {
      id: `playlist_${Date.now()}`,
      name,
      tracks,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    // 保存到本地存储
    this.savePlaylist(playlist);
    return playlist;
  }

  // 保存播放列表到本地存储
  savePlaylist(playlist) {
    try {
      const playlists = this.getPlaylists();
      playlists[playlist.id] = playlist;
      localStorage.setItem('music_playlists', JSON.stringify(playlists));
    } catch (error) {
      console.error('保存播放列表失败:', error);
    }
  }

  // 获取所有播放列表
  getPlaylists() {
    try {
      const stored = localStorage.getItem('music_playlists');
      return stored ? JSON.parse(stored) : {};
    } catch (error) {
      console.error('获取播放列表失败:', error);
      return {};
    }
  }
}

export const musicService = new MusicService();