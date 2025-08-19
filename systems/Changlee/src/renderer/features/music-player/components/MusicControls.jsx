import React from 'react';

const MusicControls = ({
  isPlaying,
  currentTime,
  duration,
  volume,
  onPlay,
  onPause,
  onNext,
  onPrevious,
  onVolumeChange,
  onSeek
}) => {
  const formatTime = (time) => {
    if (!time || isNaN(time)) return '0:00';
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const handleProgressClick = (e) => {
    if (!duration) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const percentage = clickX / rect.width;
    const newTime = percentage * duration;
    onSeek(newTime);
  };

  return (
    <div className="music-controls">
      {/* 播放控制按钮 */}
      <div className="control-buttons">
        <button className="control-btn" onClick={onPrevious}>
          ⏮️
        </button>
        <button 
          className="control-btn play-pause" 
          onClick={isPlaying ? onPause : onPlay}
        >
          {isPlaying ? '⏸️' : '▶️'}
        </button>
        <button className="control-btn" onClick={onNext}>
          ⏭️
        </button>
      </div>

      {/* 进度条 */}
      <div className="progress-section">
        <span className="time-display">{formatTime(currentTime)}</span>
        <div 
          className="progress-bar" 
          onClick={handleProgressClick}
        >
          <div 
            className="progress-fill"
            style={{ 
              width: duration ? `${(currentTime / duration) * 100}%` : '0%' 
            }}
          />
        </div>
        <span className="time-display">{formatTime(duration)}</span>
      </div>

      {/* 音量控制 */}
      <div className="volume-section">
        <span>🔊</span>
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={volume}
          onChange={(e) => onVolumeChange(parseFloat(e.target.value))}
          className="volume-slider"
        />
      </div>
    </div>
  );
};

export default MusicControls;