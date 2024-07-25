const { app, BrowserWindow, Tray, Menu, dialog } = require('electron');
const path = require('path');
const { exec } = require('child_process');
let mainWindow;
let tray = null;
let flaskProcess = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 650,
    icon: path.join(__dirname, 'tray_icon.ico'), // 设置窗口图标
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: false,
    },
    autoHideMenuBar: true,
  });

  mainWindow.loadURL('http://localhost:5000'); // 确保Flask应用程序在这个端口上运行
  mainWindow.on('close', (event) => {
    event.preventDefault(); // 拦截默认的关闭操作

    const choice = dialog.showMessageBoxSync(mainWindow, {
      type: 'question',
      buttons: ['隐藏到托盘', '关闭程序'],
      title: '确认',
      message: '你想要关闭程序还是隐藏到托盘？',
    });

    if (choice === 0) { // 用户选择了“隐藏到托盘”
      mainWindow.hide();
    } else { // 用户选择了“关闭程序”
      mainWindow.destroy();
      app.quit();
    }
  });

  mainWindow.on('closed', function () {
    mainWindow = null;
  });
}

function createTray() {
  tray = new Tray(path.join(__dirname, 'tray_icon.png')); // 设置托盘图标
  const contextMenu = Menu.buildFromTemplate([
    {
      label: '退出', click: () => {
        mainWindow.destroy(); // 确保窗口被真正关闭
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
