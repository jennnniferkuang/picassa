const { app, BrowserWindow, screen } = require('electron');
const path = require('path');

function createWindow() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;
  const winWidth = 250;
  const winHeight = 275;

  const mainWindow = new BrowserWindow({
    width: winWidth,
    height: winHeight,
    x: width - winWidth - 20,
    y: height - winHeight - 20,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    resizable: true,
    minWidth: 200,
    minHeight: 220,
    vibrancy: 'under-window',
    skipTaskbar: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  mainWindow.loadFile('index.html');
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
}); 