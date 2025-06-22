const { app, BrowserWindow, screen, ipcMain } = require('electron');
const path = require('path');

function createWindow() {
  const { width: screenWidth, height: screenHeight } = screen.getPrimaryDisplay().workAreaSize;
  
  // Calculate window size as a percentage of screen size
  const winWidth = Math.max(250, Math.min(400, screenWidth * 0.15)); // 15% of screen width, min 250px, max 400px
  const winHeight = Math.max(300, Math.min(600, screenHeight * 0.25)); // 25% of screen height, min 300px, max 600px
  
  // Calculate minimum sizes based on screen size
  const minWidth = Math.max(290, screenWidth * 0.1); // 10% of screen width, min 200px
  const minHeight = Math.max(220, screenHeight * 0.15); // 15% of screen height, min 220px

  const mainWindow = new BrowserWindow({
    width: Math.round(winWidth),
    height: Math.round(winHeight),
    x: Math.round(screenWidth - winWidth - 50),
    y: Math.round(screenHeight - winHeight - 20),
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    resizable: true,
    minWidth: Math.round(minWidth),
    minHeight: Math.round(minHeight),
    vibrancy: 'under-window',
    skipTaskbar: true,
    title: '',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
  });

  ipcMain.on('app-close', () => {
    mainWindow.close();
  });

  // Make window more transparent when it loses focus
  mainWindow.on('blur', () => {
    mainWindow.setOpacity(0.5);
  });

  // Restore opacity when window gains focus
  mainWindow.on('focus', () => {
    mainWindow.setOpacity(1.0);
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