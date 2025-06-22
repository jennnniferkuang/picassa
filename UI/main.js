const { app, BrowserWindow, screen, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');

function createWindow() {
  const { width: screenWidth, height: screenHeight } = screen.getPrimaryDisplay().workAreaSize;
  
  // Calculate window size as a percentage of screen size
  const winWidth = Math.max(370, Math.min(500, screenWidth * 0.25)); // 25% of screen width, min 350px, max 500px
  const winHeight = Math.max(420, Math.min(700, screenHeight * 0.4)); // 40% of screen height, min 400px, max 700px
  
  // Calculate minimum sizes based on screen size
  const minWidth = Math.max(380, screenWidth * 0.15); // 15% of screen width, min 350px
  const minHeight = Math.max(300, screenHeight * 0.25); // 25% of screen height, min 300px

  const mainWindow = new BrowserWindow({
    width: Math.round(winWidth),
    height: Math.round(winHeight),
    x: Math.round(screenWidth - winWidth - 30),
    y: Math.round(screenHeight - winHeight - 60),
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

ipcMain.handle('select-directory', async () => {
  const result = await dialog.showOpenDialog({
    properties: ['openDirectory']
  });

  if (result.canceled) return [];

  const dirPath = result.filePaths[0];
  const files = fs.readdirSync(dirPath);
  const pngFiles = files
    .filter(file => file.toLowerCase().endsWith('.png'))
    .map(file => path.join(dirPath, file));

  return pngFiles;
});

ipcMain.handle('copy-files-to-backend', async (event, filePaths) => {
  try {
    // Get the backend directory path (one level up from UI folder)
    const backendDir = path.join(__dirname, '..', 'backend');
    const targetDir = path.join(backendDir, 'initial_frames');
    
    // Create the initial_frames directory if it doesn't exist
    if (!fs.existsSync(targetDir)) {
      fs.mkdirSync(targetDir, { recursive: true });
    }
    
    const copiedFiles = [];
    
    for (const filePath of filePaths) {
      const fileName = path.basename(filePath);
      const targetPath = path.join(targetDir, fileName);
      
      // Copy the file
      fs.copyFileSync(filePath, targetPath);
      copiedFiles.push(targetPath);
    }
    
    return { success: true, files: copiedFiles, count: copiedFiles.length };
  } catch (error) {
    console.error('Error copying files:', error);
    return { success: false, error: error.message };
  }
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