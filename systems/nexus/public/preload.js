const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // App info
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  getSystemInfo: () => ipcRenderer.invoke('get-system-info'),
  
  // Navigation
  onNavigate: (callback) => ipcRenderer.on('navigate-to', callback),
  removeNavigateListener: () => ipcRenderer.removeAllListeners('navigate-to'),
  
  // System operations
  openExternal: (url) => ipcRenderer.invoke('open-external', url),
  
  // File operations
  selectFile: (options) => ipcRenderer.invoke('select-file', options),
  selectDirectory: (options) => ipcRenderer.invoke('select-directory', options),
  
  // Notifications
  showNotification: (title, body) => ipcRenderer.invoke('show-notification', { title, body })
});