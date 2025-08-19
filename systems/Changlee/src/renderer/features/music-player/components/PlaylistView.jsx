import React from 'react';

const PlaylistView = ({ playlist, currentTrack, onTrackSelect, onClose }) => {
  return (
    <div className="playlist-view">
      <div className="playlist-header">
        <h4>播放列表 ({playlist.length})</h4>
        <button className="close-btn" onClick={onClose}>
          ✕
        </button>
      </div>
      
      <div className="playlist-content">
        {playlist.length === 0 ? (
          <div className="empty-playlist">
            <p>暂无音乐文件</p>
            <p>点击"扫描本地音乐"来添加音乐</p>
          </div>
        ) : (
          <div className="track-list">
            {playlist.map((track, index) => (
              <div
                key={track.id || index}
                className={`track-item ${
                  currentTrack && currentTrack.id === track.id ? 'active' : ''
                }`}
                onClick={() => onTrackSelect(track)}
              >
                <div className="track-info">
                  <div className="track-title">{track.title}</div>
                  <div className="track-details">
                    <span className="track-artist">
                      {track.artist || '未知艺术家'}
                    </span>
                    {track.duration && (
                      <span className="track-duration">
                        {formatDuration(track.duration)}
                      </span>
                    )}
                  </div>
                </div>
                {currentTrack && currentTrack.id === track.id && (
                  <div className="playing-indicator">
                    🎵
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const formatDuration = (duration) => {
  if (!duration || isNaN(duration)) return '';
  const minutes = Math.floor(duration / 60);
  const seconds = Math.floor(duration % 60);
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
};

export default PlaylistView;