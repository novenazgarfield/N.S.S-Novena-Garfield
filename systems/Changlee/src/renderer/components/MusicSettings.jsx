/**
 * Changlee's Groove: 桌宠音乐集成模块
 * 音乐设置组件 - 配置音乐文件夹和扫描设置
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';

const SettingsOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  backdrop-filter: blur(5px);
`;

const SettingsPanel = styled(motion.div)`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  width: 500px;
  max-height: 70vh;
  color: white;
  font-family: 'Arial', sans-serif;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
`;

const Header = styled.div`
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Title = styled.h2`
  margin: 0;
  font-size: 20px;
  font-weight: 600;
`;

const CloseButton = styled.button`
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: scale(1.1);
  }
`;

const Content = styled.div`
  padding: 20px;
  max-height: 50vh;
  overflow-y: auto;
`;

const Section = styled.div`
  margin-bottom: 25px;
`;

const SectionTitle = styled.h3`
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 500;
  opacity: 0.9;
`;

const FolderList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 15px;
`;

const FolderItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  padding: 12px;
  border-radius: 8px;
  font-size: 14px;
`;

const FolderPath = styled.span`
  flex: 1;
  margin-right: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const RemoveButton = styled.button`
  background: rgba(255, 107, 107, 0.8);
  border: none;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255, 107, 107, 1);
  }
`;

const AddButton = styled.button`
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
  width: 100%;

  &:hover {
    background: rgba(255, 255, 255, 0.3);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const ScanButton = styled.button`
  background: linear-gradient(45deg, #ff6b6b, #feca57);
  border: none;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  width: 100%;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const Stats = styled.div`
  background: rgba(255, 255, 255, 0.1);
  padding: 15px;
  border-radius: 8px;
  font-size: 14px;
`;

const StatItem = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;

  &:last-child {
    margin-bottom: 0;
  }
`;

const LoadingSpinner = styled.div`
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;

const MusicSettings = ({ isVisible, onClose }) => {
  const [musicFolders, setMusicFolders] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const [message, setMessage] = useState('');

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

  // 加载当前设置
  const loadSettings = async () => {
    try {
      const result = await apiCall('/api/music/playlist');
      if (result.success) {
        setStats(result.data.stats);
        // 从配置中获取文件夹列表（这里需要后端支持）
        // 暂时使用默认文件夹
        setMusicFolders([]);
      }
    } catch (error) {
      console.error('加载设置失败:', error);
    }
  };

  // 添加音乐文件夹
  const addMusicFolder = async () => {
    if (window.electronAPI && window.electronAPI.selectMusicFolder) {
      try {
        const folderPath = await window.electronAPI.selectMusicFolder();
        if (folderPath && !musicFolders.includes(folderPath)) {
          const newFolders = [...musicFolders, folderPath];
          setMusicFolders(newFolders);
          
          // 保存到后端
          const result = await apiCall('/api/music/folders', {
            method: 'POST',
            body: JSON.stringify({ folders: newFolders })
          });
          
          if (result.success) {
            setMessage('文件夹添加成功！');
            setTimeout(() => setMessage(''), 3000);
          }
        }
      } catch (error) {
        console.error('添加文件夹失败:', error);
        setMessage('添加文件夹失败');
        setTimeout(() => setMessage(''), 3000);
      }
    } else {
      // 如果没有Electron API，使用Web API（受限）
      setMessage('请在桌面应用中使用此功能');
      setTimeout(() => setMessage(''), 3000);
    }
  };

  // 移除音乐文件夹
  const removeMusicFolder = async (folderPath) => {
    const newFolders = musicFolders.filter(folder => folder !== folderPath);
    setMusicFolders(newFolders);
    
    try {
      const result = await apiCall('/api/music/folders', {
        method: 'POST',
        body: JSON.stringify({ folders: newFolders })
      });
      
      if (result.success) {
        setMessage('文件夹移除成功！');
        setTimeout(() => setMessage(''), 3000);
      }
    } catch (error) {
      console.error('移除文件夹失败:', error);
    }
  };

  // 扫描音乐文件
  const scanMusic = async () => {
    if (musicFolders.length === 0) {
      setMessage('请先添加音乐文件夹');
      setTimeout(() => setMessage(''), 3000);
      return;
    }

    setIsLoading(true);
    setMessage('正在扫描音乐文件...');
    
    try {
      const result = await apiCall('/api/music/scan', {
        method: 'POST'
      });
      
      if (result.success) {
        setStats(result.data.stats);
        setMessage(`扫描完成！发现 ${result.data.totalFiles} 个音频文件`);
      } else {
        setMessage('扫描失败: ' + result.error);
      }
    } catch (error) {
      console.error('扫描失败:', error);
      setMessage('扫描失败');
    } finally {
      setIsLoading(false);
      setTimeout(() => setMessage(''), 5000);
    }
  };

  // 初始化
  useEffect(() => {
    if (isVisible) {
      loadSettings();
    }
  }, [isVisible]);

  if (!isVisible) return null;

  return (
    <SettingsOverlay
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <SettingsPanel
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
      >
        <Header>
          <Title>🎵 音乐设置</Title>
          <CloseButton onClick={onClose}>✕</CloseButton>
        </Header>

        <Content>
          <Section>
            <SectionTitle>音乐文件夹</SectionTitle>
            <FolderList>
              {musicFolders.length === 0 ? (
                <div style={{ opacity: 0.7, textAlign: 'center', padding: '20px' }}>
                  暂无音乐文件夹，请添加包含音乐文件的文件夹
                </div>
              ) : (
                musicFolders.map((folder, index) => (
                  <FolderItem key={index}>
                    <FolderPath title={folder}>{folder}</FolderPath>
                    <RemoveButton onClick={() => removeMusicFolder(folder)}>
                      移除
                    </RemoveButton>
                  </FolderItem>
                ))
              )}
            </FolderList>
            <AddButton onClick={addMusicFolder} disabled={isLoading}>
              📁 添加音乐文件夹
            </AddButton>
          </Section>

          <Section>
            <SectionTitle>扫描音乐</SectionTitle>
            <ScanButton onClick={scanMusic} disabled={isLoading}>
              {isLoading ? (
                <>
                  <LoadingSpinner /> 扫描中...
                </>
              ) : (
                '🔍 扫描音乐文件'
              )}
            </ScanButton>
          </Section>

          {stats && (
            <Section>
              <SectionTitle>音乐库统计</SectionTitle>
              <Stats>
                <StatItem>
                  <span>总文件数:</span>
                  <span>{stats.totalFiles}</span>
                </StatItem>
                <StatItem>
                  <span>总大小:</span>
                  <span>{stats.totalSizeFormatted}</span>
                </StatItem>
                <StatItem>
                  <span>艺术家数:</span>
                  <span>{stats.totalArtists}</span>
                </StatItem>
                <StatItem>
                  <span>支持格式:</span>
                  <span>{stats.formats.join(', ').toUpperCase()}</span>
                </StatItem>
              </Stats>
            </Section>
          )}

          {message && (
            <Section>
              <div style={{ 
                background: 'rgba(255, 255, 255, 0.2)', 
                padding: '10px', 
                borderRadius: '8px',
                textAlign: 'center',
                fontSize: '14px'
              }}>
                {message}
              </div>
            </Section>
          )}
        </Content>
      </SettingsPanel>
    </SettingsOverlay>
  );
};

export default MusicSettings;