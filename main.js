const { app, BrowserWindow, Tray, Menu } = require('electron');
const path = require('path');
const { exec } = require('child_process');
let mainWindow;
let tray = null;
let flaskProcess = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    icon: path.join(__dirname, 'tray_icon.ico'), // 设置窗口图标
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: false,
    },
  });



  mainWindow.loadURL('http://localhost:5000'); // 确保Flask应用程序在这个端口上运行
  mainWindow.on('close', (event) => {
    event.preventDefault(); // 拦截默认的关闭操作
    mainWindow.hide(); // 隐藏窗口
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
  exec(`taskkill /IM run.exe /F`)
  if (flaskProcess) {
    flaskProcess.kill();
  }
});

app.on('activate', function () {
  if (mainWindow === null) {
    createWindow();
  }
});
