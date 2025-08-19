/**
 * Changlee's Groove: 桌宠音乐集成模块
 * 音乐播放器UI组件 - 提供完整的音乐播放控制界面
 */

import React, { useState, useEffect, useRef } from 'react';
import './MusicPlayer.css';

const MusicPlayer = ({ isVisible, onClose, onPlayingStateChange }) => {
  // 播放状态
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTrack, setCurrentTrack] = useState(null);
  const [playlist, setPlaylist] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [volume, setVolume] = useState(0.7);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [playMode, setPlayMode] = useState('sequence'); // sequence, random, repeat
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredPlaylist, setFilteredPlaylist] = useState([]);

  // UI状态
  const [activeTab, setActiveTab] = useState('playlist'); // playlist, search, settings
  const [showVolumeSlider, setShowVolumeSlider] = useState(false);

  // 音频引用
  const audioRef = useRef(null);
  const progressRef = useRef(null);

  // 初始化
  useEffect(() => {
    if (isVisible) {
      loadPlaylist();
      loadPlaybackState();
    }
  }, [isVisible]);

  // 搜索过滤
  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredPlaylist(playlist);
    } else {
      const filtered = playlist.filter(track =>
        track.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        track.artist.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredPlaylist(filtered);
    }
  }, [searchQuery, playlist]);

  // 音频事件监听
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime);
      // 同步到后端
      updateProgress(audio.currentTime, audio.duration);
    };

    const handleLoadedMetadata = () => {
      setDuration(audio.duration);
    };

    const handleEnded = () => {
      handleNext();
    };

    const handleError = (e) => {
      console.error('音频播放错误:', e);
      setIsPlaying(false);
    };

    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('error', handleError);

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('error', handleError);
    };
  }, [currentTrack]);

  // 通知桌宠播放状态变化
  useEffect(() => {
    if (onPlayingStateChange) {
      onPlayingStateChange(isPlaying, currentTrack);
    }
  }, [isPlaying, currentTrack, onPlayingStateChange]);

  // API调用函数
  const apiCall = async (url, options = {}) => {
    try {
      const response = await fetch(`http://localhost:3001${url}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      });
      return await response.json();
    } catch (error) {
      console.error('API调用失败:', error);
      return { success: false, error: error.message };
    }
  };

  // 加载播放列表
  const loadPlaylist = async () => {
    setIsLoading(true);
    const result = await apiCall('/api/music/playlist');
    if (result.success) {
      setPlaylist(result.data.playlist);
      setFilteredPlaylist(result.data.playlist);
      setCurrentTrack(result.data.currentTrack);
      setCurrentIndex(result.data.currentIndex);
      setIsPlaying(result.data.isPlaying);
      setVolume(result.data.volume);
      setPlayMode(result.data.playMode);
    }
    setIsLoading(false);
  };

  // 加载播放状态
  const loadPlaybackState = async () => {
    const result = await apiCall('/api/music/state');
    if (result.success) {
      const state = result.data;
      setCurrentTrack(state.currentTrack);
      setCurrentIndex(state.currentIndex);
      setIsPlaying(state.isPlaying);
      setVolume(state.volume);
      setPlayMode(state.playMode);
      setCurrentTime(state.currentTime);
      setDuration(state.duration);
    }
  };

  // 播放指定音乐
  const playTrack = async (trackId) => {
    setIsLoading(true);
    const result = await apiCall(`/api/music/play/${trackId}`, { method: 'POST' });
    if (result.success) {
      const track = result.data.track;
      setCurrentTrack(track);
      setCurrentIndex(result.data.index);
      
      // 获取音乐文件URL并播放
      const urlResult = await apiCall(`/api/music/url/${trackId}`);
      if (urlResult.success && audioRef.current) {
        audioRef.current.src = urlResult.data.url;
        audioRef.current.load();
        audioRef.current.play();
        setIsPlaying(true);
      }
    }
    setIsLoading(false);
  };

  // 播放/暂停切换
  const togglePlayPause = async () => {
    if (!currentTrack) {
      // 如果没有当前音乐，播放第一首
      if (playlist.length > 0) {
        await playTrack(playlist[0].id);
      }
      return;
    }

    if (isPlaying) {
      await apiCall('/api/music/pause', { method: 'POST' });
      audioRef.current?.pause();
      setIsPlaying(false);
    } else {
      await apiCall('/api/music/resume', { method: 'POST' });
      audioRef.current?.play();
      setIsPlaying(true);
    }
  };

  // 下一首
  const handleNext = async () => {
    const result = await apiCall('/api/music/next', { method: 'POST' });
    if (result.success && result.data.track) {
      await playTrack(result.data.track.id);
    }
  };

  // 上一首
  const handlePrevious = async () => {
    const result = await apiCall('/api/music/previous', { method: 'POST' });
    if (result.success && result.data.track) {
      await playTrack(result.data.track.id);
    }
  };

  // 设置音量
  const handleVolumeChange = async (newVolume) => {
    setVolume(newVolume);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
    }
    await apiCall('/api/music/volume', {
      method: 'POST',
      body: JSON.stringify({ volume: newVolume })
    });
  };

  // 设置播放模式
  const handlePlayModeChange = async () => {
    const modes = ['sequence', 'random', 'repeat'];
    const currentModeIndex = modes.indexOf(playMode);
    const nextMode = modes[(currentModeIndex + 1) % modes.length];
    
    setPlayMode(nextMode);
    await apiCall('/api/music/playmode', {
      method: 'POST',
      body: JSON.stringify({ mode: nextMode })
    });
  };

  // 进度条拖拽
  const handleProgressChange = (e) => {
    if (!audioRef.current || !duration) return;
    
    const rect = progressRef.current.getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    const newTime = percent * duration;
    
    audioRef.current.currentTime = newTime;
    setCurrentTime(newTime);
  };

  // 更新播放进度到后端
  const updateProgress = async (currentTime, duration) => {
    await apiCall('/api/music/progress', {
      method: 'POST',
      body: JSON.stringify({ currentTime, duration })
    });
  };

  // 格式化时间
  const formatTime = (seconds) => {
    if (!seconds || isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // 获取播放模式图标
  const getPlayModeIcon = () => {
    switch (playMode) {
      case 'random': return '🔀';
      case 'repeat': return '🔂';
      default: return '🔁';
    }
  };

  if (!isVisible) return null;

  return (
    <div className="music-player-overlay">
      <div className="music-player">
        {/* 音频元素 */}
        <audio ref={audioRef} volume={volume} />
        
        {/* 头部 */}
        <div className="music-player-header">
          <h3>🎵 Changlee's Groove</h3>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        {/* 当前播放信息 */}
        {currentTrack && (
          <div className="current-track-info">
            <div className="track-details">
              <div className="track-title">{currentTrack.title}</div>
              <div className="track-artist">{currentTrack.artist}</div>
            </div>
            <div className="track-format">{currentTrack.format.toUpperCase()}</div>
          </div>
        )}

        {/* 播放控制 */}
        <div className="playback-controls">
          <button className="control-btn" onClick={handlePrevious}>⏮️</button>
          <button 
            className="play-pause-btn" 
            onClick={togglePlayPause}
            disabled={isLoading}
          >
            {isLoading ? '⏳' : (isPlaying ? '⏸️' : '▶️')}
          </button>
          <button className="control-btn" onClick={handleNext}>⏭️</button>
          
          <button 
            className="mode-btn" 
            onClick={handlePlayModeChange}
            title={`播放模式: ${playMode}`}
          >
            {getPlayModeIcon()}
          </button>
          
          <div className="volume-control">
            <button 
              className="volume-btn"
              onClick={() => setShowVolumeSlider(!showVolumeSlider)}
            >
              🔊
            </button>
            {showVolumeSlider && (
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={volume}
                onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
                className="volume-slider"
              />
            )}
          </div>
        </div>

        {/* 进度条 */}
        <div className="progress-container">
          <span className="time-display">{formatTime(currentTime)}</span>
          <div 
            className="progress-bar" 
            ref={progressRef}
            onClick={handleProgressChange}
          >
            <div 
              className="progress-fill"
              style={{ width: `${duration > 0 ? (currentTime / duration) * 100 : 0}%` }}
            />
          </div>
          <span className="time-display">{formatTime(duration)}</span>
        </div>

        {/* 标签页 */}
        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'playlist' ? 'active' : ''}`}
            onClick={() => setActiveTab('playlist')}
          >
            播放列表
          </button>
          <button 
            className={`tab ${activeTab === 'search' ? 'active' : ''}`}
            onClick={() => setActiveTab('search')}
          >
            搜索
          </button>
          <button 
            className={`tab ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            设置
          </button>
        </div>

        {/* 内容区域 */}
        <div className="tab-content">
          {activeTab === 'playlist' && (
            <div className="playlist-container">
              {filteredPlaylist.length === 0 ? (
                <div className="empty-state">
                  <p>暂无音乐文件</p>
                  <p>请在设置中添加音乐文件夹</p>
                </div>
              ) : (
                <div className="playlist">
                  {filteredPlaylist.map((track, index) => (
                    <div 
                      key={track.id}
                      className={`playlist-item ${currentTrack?.id === track.id ? 'active' : ''}`}
                      onClick={() => playTrack(track.id)}
                    >
                      <div className="track-info">
                        <div className="track-name">{track.title}</div>
                        <div className="track-meta">{track.artist} • {track.format.toUpperCase()}</div>
                      </div>
                      {currentTrack?.id === track.id && isPlaying && (
                        <div className="playing-indicator">🎵</div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'search' && (
            <div className="search-container">
              <input
                type="text"
                placeholder="搜索歌曲或艺术家..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="search-input"
              />
              <div className="search-results">
                {filteredPlaylist.map((track) => (
                  <div 
                    key={track.id}
                    className="search-result-item"
                    onClick={() => playTrack(track.id)}
                  >
                    <div className="track-info">
                      <div className="track-name">{track.title}</div>
                      <div className="track-meta">{track.artist}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="settings-container">
              <div className="setting-item">
                <label>音量: {Math.round(volume * 100)}%</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={volume}
                  onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
                />
              </div>
              
              <div className="setting-item">
                <label>播放模式</label>
                <select value={playMode} onChange={(e) => handlePlayModeChange()}>
                  <option value="sequence">顺序播放</option>
                  <option value="random">随机播放</option>
                  <option value="repeat">单曲循环</option>
                </select>
              </div>

              <div className="setting-item">
                <button onClick={loadPlaylist} disabled={isLoading}>
                  {isLoading ? '刷新中...' : '刷新播放列表'}
                </button>
              </div>

              <div className="stats">
                <p>总计: {playlist.length} 首歌曲</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MusicPlayer;