const { app, BrowserWindow, ipcMain, Tray, Menu, screen, shell } = require('electron');
const path = require('path');
const isDev = process.env.ELECTRON_IS_DEV === '1';
const Store = require('electron-store');
const AutoLaunch = require('auto-launch');

// 应用配置存储
const store = new Store();

// 自启动配置
const autoLauncher = new AutoLaunch({
  name: '长离的学习胶囊',
  path: app.getPath('exe'),
});

class ChangleeApp {
  constructor() {
    this.mainWindow = null;
    this.petWindow = null;
    this.tray = null;
    this.isQuitting = false;
  }

  async initialize() {
    // 确保单实例运行
    const gotTheLock = app.requestSingleInstanceLock();
    if (!gotTheLock) {
      app.quit();
      return;
    }

    // 应用事件监听
    app.whenReady().then(() => this.onReady());
    app.on('window-all-closed', this.onWindowAllClosed.bind(this));
    app.on('activate', this.onActivate.bind(this));
    app.on('before-quit', () => { this.isQuitting = true; });
    app.on('second-instance', this.onSecondInstance.bind(this));

    // IPC事件监听
    this.setupIpcHandlers();
  }

  async onReady() {
    // 创建系统托盘
    this.createTray();
    
    // 创建桌宠窗口
    this.createPetWindow();
    
    // 设置自启动
    this.setupAutoLaunch();
    
    console.log('🐱 长离的学习胶囊已启动');
  }

  createPetWindow() {
    const { width, height } = screen.getPrimaryDisplay().workAreaSize;
    
    this.petWindow = new BrowserWindow({
      width: 200,
      height: 200,
      x: width - 250,
      y: height - 250,
      frame: false,
      transparent: true,
      alwaysOnTop: true,
      skipTaskbar: true,
      resizable: false,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, 'preload.js')
      }
    });

    // 加载桌宠界面
    if (isDev) {
      this.petWindow.loadURL('http://localhost:3000/pet');
      this.petWindow.webContents.openDevTools({ mode: 'detach' });
    } else {
      this.petWindow.loadFile(path.join(__dirname, '../renderer/build/pet.html'));
    }

    // 桌宠窗口事件
    this.petWindow.on('closed', () => {
      this.petWindow = null;
    });

    // 防止桌宠窗口被关闭
    this.petWindow.on('close', (event) => {
      if (!this.isQuitting) {
        event.preventDefault();
        this.petWindow.hide();
      }
    });

    // 设置窗口可拖拽
    this.petWindow.setIgnoreMouseEvents(false);
  }

  createMainWindow() {
    if (this.mainWindow) {
      this.mainWindow.focus();
      return;
    }

    this.mainWindow = new BrowserWindow({
      width: 800,
      height: 600,
      minWidth: 600,
      minHeight: 400,
      icon: path.join(__dirname, '../../assets/images/icon.png'),
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, 'preload.js')
      }
    });

    // 加载主界面
    if (isDev) {
      this.mainWindow.loadURL('http://localhost:3000');
      this.mainWindow.webContents.openDevTools();
    } else {
      this.mainWindow.loadFile(path.join(__dirname, '../renderer/build/index.html'));
    }

    this.mainWindow.on('closed', () => {
      this.mainWindow = null;
    });

    // 防止主窗口被关闭时退出应用
    this.mainWindow.on('close', (event) => {
      if (!this.isQuitting) {
        event.preventDefault();
        this.mainWindow.hide();
      }
    });
  }

  createTray() {
    const iconPath = path.join(__dirname, '../../assets/images/tray-icon.png');
    this.tray = new Tray(iconPath);

    const contextMenu = Menu.buildFromTemplate([
      {
        label: '显示长离',
        click: () => {
          if (this.petWindow) {
            this.petWindow.show();
          }
        }
      },
      {
        label: '学习中心',
        click: () => {
          this.createMainWindow();
        }
      },
      { type: 'separator' },
      {
        label: '设置',
        click: () => {
          this.openSettings();
        }
      },
      {
        label: '关于',
        click: () => {
          this.showAbout();
        }
      },
      { type: 'separator' },
      {
        label: '退出',
        click: () => {
          this.isQuitting = true;
          app.quit();
        }
      }
    ]);

    this.tray.setToolTip('长离的学习胶囊');
    this.tray.setContextMenu(contextMenu);

    // 双击托盘图标显示主窗口
    this.tray.on('double-click', () => {
      this.createMainWindow();
    });
  }

  setupAutoLaunch() {
    const autoStart = store.get('autoStart', true);
    if (autoStart) {
      autoLauncher.enable();
    }
  }

  setupIpcHandlers() {
    // 显示学习胶囊
    ipcMain.handle('show-learning-capsule', async (event, wordData) => {
      this.createMainWindow();
      return { success: true };
    });

    // 获取应用设置
    ipcMain.handle('get-settings', async () => {
      return store.store;
    });

    // 保存应用设置
    ipcMain.handle('save-settings', async (event, settings) => {
      Object.keys(settings).forEach(key => {
        store.set(key, settings[key]);
      });
      return { success: true };
    });

    // 桌宠位置更新
    ipcMain.handle('update-pet-position', async (event, { x, y }) => {
      if (this.petWindow) {
        this.petWindow.setPosition(x, y);
      }
      return { success: true };
    });

    // 显示通知
    ipcMain.handle('show-notification', async (event, { title, body }) => {
      const { Notification } = require('electron');
      if (Notification.isSupported()) {
        new Notification({ title, body }).show();
      }
      return { success: true };
    });

    // 打开外部链接
    ipcMain.handle('open-external', async (event, url) => {
      shell.openExternal(url);
      return { success: true };
    });
  }

  openSettings() {
    // 创建设置窗口或在主窗口中打开设置页面
    this.createMainWindow();
    if (this.mainWindow) {
      this.mainWindow.webContents.send('navigate-to', '/settings');
    }
  }

  showAbout() {
    const { dialog } = require('electron');
    dialog.showMessageBox(this.mainWindow || this.petWindow, {
      type: 'info',
      title: '关于长离的学习胶囊',
      message: '长离的学习胶囊 V1.0',
      detail: '一款以情感陪伴为核心的桌面宠物英语学习应用\n\n让学习变得有趣，让陪伴变得智能 ✨',
      buttons: ['确定']
    });
  }

  onWindowAllClosed() {
    // 在macOS上，保持应用运行
    if (process.platform !== 'darwin') {
      // 但不退出，因为我们有桌宠和托盘
    }
  }

  onActivate() {
    if (BrowserWindow.getAllWindows().length === 0) {
      this.createPetWindow();
    }
  }

  onSecondInstance() {
    // 当用户尝试运行第二个实例时，聚焦到现有窗口
    if (this.mainWindow) {
      if (this.mainWindow.isMinimized()) this.mainWindow.restore();
      this.mainWindow.focus();
    } else {
      this.createMainWindow();
    }
  }
}

// 启动应用
const changleeApp = new ChangleeApp();
changleeApp.initialize();

// 导出应用实例（用于测试）
module.exports = changleeApp;