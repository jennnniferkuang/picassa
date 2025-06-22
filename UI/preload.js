const { contextBridge, ipcRenderer } = require('electron');

// Expose any APIs if needed in the future
contextBridge.exposeInMainWorld('electronAPI', {
  closeApp: () => ipcRenderer.send('app-close')
}); 