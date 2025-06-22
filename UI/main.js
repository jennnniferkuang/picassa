const { app, BrowserWindow, screen, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require("child_process");
const os = require("os");

function createWindow() {
  const { width: screenWidth, height: screenHeight } = screen.getPrimaryDisplay().workAreaSize;
  
  // Calculate window size as a percentage of screen size
  const winWidth = Math.max(350, Math.min(500, screenWidth * 0.25)); // 25% of screen width, min 350px, max 500px
  const winHeight = Math.max(400, Math.min(700, screenHeight * 0.4)); // 40% of screen height, min 400px, max 700px
  
  // Calculate minimum sizes based on screen size
  const minWidth = Math.max(350, screenWidth * 0.15); // 15% of screen width, min 350px
  const minHeight = Math.max(300, screenHeight * 0.25); // 25% of screen height, min 300px

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

// Use the correct Python executable depending on the platform
const pythonExecutable = process.platform === 'win32' ? 'python' : 'python3';

// Resolve the absolute path to main.py
const backendScript = path.join(__dirname, '..', 'backend', 'main.py');

// Spawn the backend process
const backendProcess = spawn(
  pythonExecutable,
  [backendScript],
  { stdio: 'inherit', shell: false }
);

// Optional: Handle backend process exit
backendProcess.on('close', (code) => {
  console.log(`Backend process exited with code ${code}`);
});

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