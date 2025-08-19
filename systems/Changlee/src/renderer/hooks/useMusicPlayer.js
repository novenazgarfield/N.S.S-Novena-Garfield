/**
 * Changlee's Groove: 桌宠音乐集成模块
 * 音乐播放器React Hook
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import musicAPI from '../services/musicApi';

export const useMusicPlayer = () => {
  // 播放状态
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTrack, setCurrentTrack] = useState(null);
  const [playlist, setPlaylist] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [volume, setVolume] = useState(0.7);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [playMode, setPlayMode] = useState('sequence');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // 音频引用
  const audioRef = useRef(null);
  const progressUpdateInterval = useRef(null);

  /**
   * 错误处理
   */
  const handleError = useCallback((error, context = '') => {
    console.error(`音乐播放器错误 ${context}:`, error);
    setError(error.message || '未知错误');
    setIsLoading(false);
  }, []);

  /**
   * 清除错误
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * 加载播放列表
   */
  const loadPlaylist = useCallback(async () => {
    try {
      setIsLoading(true);
      clearError();
      
      const result = await musicAPI.getPlaylist();
      if (result.success) {
        setPlaylist(result.data.playlist);
        setCurrentTrack(result.data.currentTrack);
        setCurrentIndex(result.data.currentIndex);
        setIsPlaying(result.data.isPlaying);
        setVolume(result.data.volume);
        setPlayMode(result.data.playMode);
      }
    } catch (error) {
      handleError(error, '加载播放列表');
    } finally {
      setIsLoading(false);
    }
  }, [handleError, clearError]);

  /**
   * 加载播放状态
   */
  const loadPlaybackState = useCallback(async () => {
    try {
      const result = await musicAPI.getPlaybackState();
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
    } catch (error) {
      handleError(error, '加载播放状态');
    }
  }, [handleError]);

  /**
   * 播放指定音乐
   */
  const playTrack = useCallback(async (trackId) => {
    try {
      setIsLoading(true);
      clearError();

      const result = await musicAPI.playTrack(trackId);
      if (result.success) {
        const track = result.data.track;
        setCurrentTrack(track);
        setCurrentIndex(result.data.index);
        
        // 获取音乐文件URL并播放
        const urlResult = await musicAPI.getTrackUrl(trackId);
        if (urlResult.success && audioRef.current) {
          audioRef.current.src = urlResult.data.url;
          audioRef.current.load();
          await audioRef.current.play();
          setIsPlaying(true);
        }
      }
    } catch (error) {
      handleError(error, '播放音乐');
    } finally {
      setIsLoading(false);
    }
  }, [handleError, clearError]);

  /**
   * 播放/暂停切换
   */
  const togglePlayPause = useCallback(async () => {
    try {
      if (!currentTrack) {
        // 如果没有当前音乐，播放第一首
        if (playlist.length > 0) {
          await playTrack(playlist[0].id);
        }
        return;
      }

      if (isPlaying) {
        await musicAPI.pauseTrack();
        audioRef.current?.pause();
        setIsPlaying(false);
      } else {
        await musicAPI.resumeTrack();
        await audioRef.current?.play();
        setIsPlaying(true);
      }
    } catch (error) {
      handleError(error, '播放/暂停');
    }
  }, [currentTrack, isPlaying, playlist, playTrack, handleError]);

  /**
   * 下一首
   */
  const nextTrack = useCallback(async () => {
    try {
      const result = await musicAPI.nextTrack();
      if (result.success && result.data.track) {
        await playTrack(result.data.track.id);
      }
    } catch (error) {
      handleError(error, '下一首');
    }
  }, [playTrack, handleError]);

  /**
   * 上一首
   */
  const previousTrack = useCallback(async () => {
    try {
      const result = await musicAPI.previousTrack();
      if (result.success && result.data.track) {
        await playTrack(result.data.track.id);
      }
    } catch (error) {
      handleError(error, '上一首');
    }
  }, [playTrack, handleError]);

  /**
   * 设置音量
   */
  const changeVolume = useCallback(async (newVolume) => {
    try {
      setVolume(newVolume);
      if (audioRef.current) {
        audioRef.current.volume = newVolume;
      }
      await musicAPI.setVolume(newVolume);
    } catch (error) {
      handleError(error, '设置音量');
    }
  }, [handleError]);

  /**
   * 设置播放模式
   */
  const changePlayMode = useCallback(async (newMode) => {
    try {
      setPlayMode(newMode);
      await musicAPI.setPlayMode(newMode);
    } catch (error) {
      handleError(error, '设置播放模式');
    }
  }, [handleError]);

  /**
   * 循环播放模式
   */
  const togglePlayMode = useCallback(async () => {
    const modes = ['sequence', 'random', 'repeat'];
    const currentModeIndex = modes.indexOf(playMode);
    const nextMode = modes[(currentModeIndex + 1) % modes.length];
    await changePlayMode(nextMode);
  }, [playMode, changePlayMode]);

  /**
   * 设置播放进度
   */
  const seekTo = useCallback((time) => {
    if (audioRef.current && duration > 0) {
      audioRef.current.currentTime = time;
      setCurrentTime(time);
    }
  }, [duration]);

  /**
   * 搜索音乐
   */
  const searchMusic = useCallback(async (query) => {
    try {
      setIsLoading(true);
      const result = await musicAPI.searchMusic(query);
      return result.success ? result.data.results : [];
    } catch (error) {
      handleError(error, '搜索音乐');
      return [];
    } finally {
      setIsLoading(false);
    }
  }, [handleError]);

  /**
   * 扫描音乐文件
   */
  const scanMusic = useCallback(async () => {
    try {
      setIsLoading(true);
      const result = await musicAPI.scanMusic();
      if (result.success) {
        await loadPlaylist(); // 重新加载播放列表
      }
      return result;
    } catch (error) {
      handleError(error, '扫描音乐');
      return { success: false, error: error.message };
    } finally {
      setIsLoading(false);
    }
  }, [loadPlaylist, handleError]);

  /**
   * 设置音乐文件夹
   */
  const setMusicFolders = useCallback(async (folders) => {
    try {
      setIsLoading(true);
      const result = await musicAPI.setMusicFolders(folders);
      return result;
    } catch (error) {
      handleError(error, '设置音乐文件夹');
      return { success: false, error: error.message };
    } finally {
      setIsLoading(false);
    }
  }, [handleError]);

  /**
   * 创建随机播放列表
   */
  const createRandomPlaylist = useCallback(async (count = 20) => {
    try {
      const result = await musicAPI.createRandomPlaylist(count);
      return result.success ? result.data : [];
    } catch (error) {
      handleError(error, '创建随机播放列表');
      return [];
    }
  }, [handleError]);

  /**
   * 音频事件处理
   */
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime);
    };

    const handleLoadedMetadata = () => {
      setDuration(audio.duration);
    };

    const handleEnded = () => {
      nextTrack();
    };

    const handleError = (e) => {
      console.error('音频播放错误:', e);
      setIsPlaying(false);
      setError('音频播放失败');
    };

    const handleCanPlay = () => {
      clearError();
    };

    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('error', handleError);
    audio.addEventListener('canplay', handleCanPlay);

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('error', handleError);
      audio.removeEventListener('canplay', handleCanPlay);
    };
  }, [nextTrack, clearError]);

  /**
   * 定期同步播放进度到后端
   */
  useEffect(() => {
    if (isPlaying && currentTime > 0 && duration > 0) {
      if (progressUpdateInterval.current) {
        clearInterval(progressUpdateInterval.current);
      }
      
      progressUpdateInterval.current = setInterval(async () => {
        try {
          await musicAPI.updateProgress(currentTime, duration);
        } catch (error) {
          // 静默处理进度更新错误
          console.warn('更新播放进度失败:', error);
        }
      }, 5000); // 每5秒同步一次
    } else {
      if (progressUpdateInterval.current) {
        clearInterval(progressUpdateInterval.current);
        progressUpdateInterval.current = null;
      }
    }

    return () => {
      if (progressUpdateInterval.current) {
        clearInterval(progressUpdateInterval.current);
      }
    };
  }, [isPlaying, currentTime, duration]);

  /**
   * 格式化时间
   */
  const formatTime = useCallback((seconds) => {
    if (!seconds || isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }, []);

  /**
   * 获取播放进度百分比
   */
  const getProgress = useCallback(() => {
    return duration > 0 ? (currentTime / duration) * 100 : 0;
  }, [currentTime, duration]);

  return {
    // 状态
    isPlaying,
    currentTrack,
    playlist,
    currentIndex,
    volume,
    currentTime,
    duration,
    playMode,
    isLoading,
    error,
    
    // 音频引用
    audioRef,
    
    // 操作方法
    loadPlaylist,
    loadPlaybackState,
    playTrack,
    togglePlayPause,
    nextTrack,
    previousTrack,
    changeVolume,
    changePlayMode,
    togglePlayMode,
    seekTo,
    searchMusic,
    scanMusic,
    setMusicFolders,
    createRandomPlaylist,
    clearError,
    
    // 工具方法
    formatTime,
    getProgress
  };
};

export default useMusicPlayer;