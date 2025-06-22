const { contextBridge, ipcRenderer } = require('electron');

// Expose any APIs if needed in the future
contextBridge.exposeInMainWorld('electronAPI', {
  closeApp: () => ipcRenderer.send('app-close'),
  selectDirectory: () => ipcRenderer.invoke('select-directory'),
  copyFilesToBackend: (filePaths) => ipcRenderer.invoke('copy-files-to-backend', filePaths)
}); 