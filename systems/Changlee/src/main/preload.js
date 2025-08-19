const { contextBridge, ipcRenderer } = require('electron');

// 向渲染进程暴露安全的API
contextBridge.exposeInMainWorld('electronAPI', {
  // 学习胶囊相关
  showLearningCapsule: (wordData) => ipcRenderer.invoke('show-learning-capsule', wordData),
  
  // 设置相关
  getSettings: () => ipcRenderer.invoke('get-settings'),
  saveSettings: (settings) => ipcRenderer.invoke('save-settings', settings),
  
  // 桌宠相关
  updatePetPosition: (position) => ipcRenderer.invoke('update-pet-position', position),
  
  // 通知相关
  showNotification: (notification) => ipcRenderer.invoke('show-notification', notification),
  
  // 外部链接
  openExternal: (url) => ipcRenderer.invoke('open-external', url),
  
  // 事件监听
  onNavigateTo: (callback) => ipcRenderer.on('navigate-to', callback),
  
  // 移除事件监听
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel)
});

// 桌宠专用API
contextBridge.exposeInMainWorld('petAPI', {
  // 拖拽相关
  startDrag: () => ipcRenderer.invoke('start-drag'),
  endDrag: () => ipcRenderer.invoke('end-drag'),
  
  // 动画状态
  updateAnimationState: (state) => ipcRenderer.invoke('update-animation-state', state),
  
  // 漂流瓶推送
  triggerCapsulePush: (capsuleData) => ipcRenderer.invoke('trigger-capsule-push', capsuleData)
});

// 后端API通信
contextBridge.exposeInMainWorld('backendAPI', {
  // 获取单词数据
  getWordData: (wordId) => fetch(`http://localhost:3001/api/words/${wordId}`).then(r => r.json()),
  
  // 获取学习进度
  getLearningProgress: () => fetch('http://localhost:3001/api/progress').then(r => r.json()),
  
  // 更新学习状态
  updateLearningStatus: (wordId, status) => 
    fetch(`http://localhost:3001/api/words/${wordId}/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    }).then(r => r.json()),
  
  // 获取下一个要学习的单词
  getNextWord: () => fetch('http://localhost:3001/api/words/next').then(r => r.json()),
  
  // 生成AI内容
  generateAIContent: (wordData) => 
    fetch('http://localhost:3001/api/ai/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(wordData)
    }).then(r => r.json()),
  
  // 提交拼写练习结果
  submitSpellingResult: (wordId, result) =>
    fetch(`http://localhost:3001/api/words/${wordId}/spelling`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(result)
    }).then(r => r.json())
});

// 工具函数
contextBridge.exposeInMainWorld('utils', {
  // 格式化时间
  formatTime: (timestamp) => new Date(timestamp).toLocaleString('zh-CN'),
  
  // 播放音效
  playSound: (soundName) => {
    const audio = new Audio(`../assets/sounds/${soundName}.mp3`);
    audio.play().catch(console.error);
  },
  
  // 获取随机数
  random: (min, max) => Math.floor(Math.random() * (max - min + 1)) + min,
  
  // 延迟执行
  delay: (ms) => new Promise(resolve => setTimeout(resolve, ms))
});

console.log('🔗 Preload script loaded successfully');