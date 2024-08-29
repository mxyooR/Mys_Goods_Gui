// main.js
const { app, BrowserWindow, Tray, Menu, dialog, ipcMain } = require('electron');
const path = require('path');
const { exec } = require('child_process');

let mainWindow;
let tray = null;
let flaskProcess = null;
let isQuitting = false;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 650,
    icon: path.join(__dirname, 'tray_icon.ico'),
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
    autoHideMenuBar: true,
  });

  mainWindow.loadURL('http://localhost:5000');

  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault();
      const choice = dialog.showMessageBoxSync(mainWindow, {
        type: 'question',
        buttons: ['隐藏到托盘', '关闭程序'],
        title: '确认',
        message: '你想要关闭程序还是隐藏到托盘？',
      });
      if (choice === 0) {
        mainWindow.hide();
      } else {
        isQuitting = true;
        app.quit();
      }
    }
  });

  mainWindow.on('focus', () => {
    mainWindow.webContents.send('window-focused');
  });

  mainWindow.on('blur', () => {
    mainWindow.webContents.send('window-blurred');
  });
}

function createTray() {
  tray = new Tray(path.join(__dirname, 'tray_icon.png'));
  const contextMenu = Menu.buildFromTemplate([
    {
      label: '显示', click: () => {
        mainWindow.show();
      }
    },
    {
      label: '退出', click: () => {
        isQuitting = true;
        app.quit();
      }
    }
  ]);
  tray.setToolTip('米游社商品兑换小助手');
  tray.setContextMenu(contextMenu);
  tray.on('click', () => {
    if (mainWindow.isVisible()) {
      mainWindow.hide();
    } else {
      mainWindow.show();
    }
  });
}

app.on('ready', () => {
  // 启动Flask应用
  flaskProcess = exec(path.join(__dirname, '/flask_app/dist/run/run.exe'), (err, stdout, stderr) => {
    if (err) {
      console.error(`Error: ${err}`);
      return;
    }
    console.log(`stdout: ${stdout}`);
    console.error(`stderr: ${stderr}`);
  });

  createWindow();
  createTray();
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  isQuitting = true;
  exec(`taskkill /IM run.exe /F`);
  if (flaskProcess) {
    flaskProcess.kill();
  }
});

app.on('activate', function () {
  if (mainWindow === null) {
    createWindow();
  }
});

ipcMain.on('refocus-main-window', () => {
  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore();
    mainWindow.focus();
  }
});