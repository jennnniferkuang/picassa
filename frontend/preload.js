const { contextBridge } = require('electron');

// Expose any APIs if needed in the future
contextBridge.exposeInMainWorld('electronAPI', {
  // Add any future APIs here
}); 