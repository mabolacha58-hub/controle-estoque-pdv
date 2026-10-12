const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  isElectron: true,

  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  isDev: () => ipcRenderer.invoke('is-dev'),

  // File dialogs
  saveFile: (options) => ipcRenderer.invoke('save-file', options),
  openFile: (options) => ipcRenderer.invoke('open-file', options),
  showMessageBox: (options) => ipcRenderer.invoke('show-message-box', options),

  // Notifications
  showNotification: (title, body) =>
    ipcRenderer.invoke('show-notification', { title, body }),

  // Print / PDF
  printPDF: (html, options) =>
    ipcRenderer.invoke('print-pdf', { html, options }),

  // Persistent config storage (window state, etc.)
  getConfig: (key) => ipcRenderer.invoke('get-config', key),
  setConfig: (key, value) =>
    ipcRenderer.invoke('set-config', { key, value }),

  // Listen for menu actions from main process
  onMenuAction: (callback) => {
    ipcRenderer.on('menu-action', (_, action) => callback(action));
  },

  // Listen for navigation commands from menu
  onNavigate: (callback) => {
    ipcRenderer.on('navigate', (_, path) => callback(path));
  },

  // Remove listeners (cleanup)
  removeAllListeners: (channel) => {
    ipcRenderer.removeAllListeners(channel);
  },
});
