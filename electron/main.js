const { app, BrowserWindow, ipcMain, dialog, Menu, Tray, Notification, shell, nativeImage } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');

const isDev = !app.isPackaged;
const FLASK_PORT = 5000;
let store;

async function initStore() {
  const { default: Store } = await import('electron-store');
  store = new Store({ name: 'controle-estoque-config' });
}

let mainWindow = null;
let tray = null;
let flaskProcess = null;
let isQuitting = false;

function findPython() {
  const fs = require('fs');
  const candidates = [];

  // 1) venv local (desenvolvimento)
  const localVenv = path.join(getAppPath(), 'venv', 'Scripts', 'python.exe');
  if (fs.existsSync(localVenv)) candidates.push(localVenv);

  // 2) venv empacotado (produção)
  if (!isDev) {
    const bundledVenv = path.join(process.resourcesPath, 'venv', 'Scripts', 'python.exe');
    if (fs.existsSync(bundledVenv)) candidates.push(bundledVenv);
  }

  // 3) Python do sistema
  candidates.push('python', 'python3');

  for (const candidate of candidates) {
    if (!candidate) continue;
    if (candidate === 'python' || candidate === 'python3') return candidate;
    try {
      fs.accessSync(candidate);
      return candidate;
    } catch {
      // try next
    }
  }

  return 'python';
}

function getAppPath() {
  if (isDev) return process.cwd();
  return process.resourcesPath;
}

function resolveDbPath() {
  const fs = require('fs');
  const userDataDir = app.getPath('userData');
  const userDb = path.join(userDataDir, 'controle_estoque.db');
  if (!fs.existsSync(userDb)) {
    const bundledDb = path.join(getAppPath(), 'controle_estoque.db');
    if (fs.existsSync(bundledDb)) {
      if (!fs.existsSync(userDataDir)) fs.mkdirSync(userDataDir, { recursive: true });
      fs.copyFileSync(bundledDb, userDb);
    }
  }
  return userDb;
}

function startFlask() {
  return new Promise((resolve, reject) => {
    const python = findPython();
    const appPath = getAppPath();
    const script = path.join(appPath, 'app.py');
    const env = {
      ...process.env,
      FLASK_APP: 'app.py',
      FLASK_DEBUG: '0',
      PYTHONUNBUFFERED: '1',
      DB_PATH: resolveDbPath(),
    };

    flaskProcess = spawn(python, [script], {
      cwd: appPath,
      env,
      stdio: ['pipe', 'pipe', 'pipe'],
    });

    flaskProcess.stdout.on('data', (data) => {
      const msg = data.toString();
      console.log('[Flask]', msg.trim());
      if (msg.includes('Servidor iniciado') || msg.includes('Running on')) {
        resolve();
      }
    });

    flaskProcess.stderr.on('data', (data) => {
      const msg = data.toString();
      console.log('[Flask:err]', msg.trim());
      if (msg.includes('Running on') || msg.includes('* Running')) {
        resolve();
      }
    });

    flaskProcess.on('error', (err) => {
      console.error('[Flask] Erro ao iniciar:', err);
      reject(err);
    });

    flaskProcess.on('exit', (code) => {
      console.log('[Flask] Processo encerrado com código', code);
      if (!isQuitting) {
        app.quit();
      }
    });

    // Timeout fallback - check if server is up
    setTimeout(() => {
      const check = http.get(`http://127.0.0.1:${FLASK_PORT}`, () => {
        check.destroy();
        resolve();
      });
      check.on('error', () => {
        // Server might still be starting, resolve anyway - window will retry
        resolve();
      });
    }, 3000);
  });
}

function stopFlask() {
  if (flaskProcess) {
    if (process.platform === 'win32') {
      // Send Ctrl+C via signal to avoid DB corruption
      spawn('taskkill', ['/pid', flaskProcess.pid.toString(), '/t']);
    } else {
      flaskProcess.kill('SIGTERM');
    }
    flaskProcess = null;
  }
}

function createWindow() {
  const savedBounds = store.get('windowBounds', { width: 1280, height: 800 });
  const isMaximized = store.get('windowMaximized', false);

  mainWindow = new BrowserWindow({
    width: savedBounds.width,
    height: savedBounds.height,
    minWidth: 1024,
    minHeight: 600,
    icon: path.join(__dirname, 'icon.png'),
    title: 'Controle de Estoque — PDV/ERP',
    backgroundColor: '#0f172a',
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false,
    },
  });

  if (isMaximized) {
    mainWindow.maximize();
  }

  const menu = Menu.buildFromTemplate(buildMenu());
  Menu.setApplicationMenu(menu);

  mainWindow.loadURL(`http://127.0.0.1:${FLASK_PORT}`);

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    if (isDev) mainWindow.webContents.openDevTools();
  });

  mainWindow.on('close', (e) => {
    if (!isQuitting) {
      e.preventDefault();
      mainWindow.hide();
    }
  });

  mainWindow.on('resize', () => {
    if (!mainWindow.isMaximized() && !mainWindow.isMinimized()) {
      const bounds = mainWindow.getBounds();
      store.set('windowBounds', bounds);
    }
  });

  mainWindow.on('maximize', () => store.set('windowMaximized', true));
  mainWindow.on('unmaximize', () => store.set('windowMaximized', false));

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http://127.0.0.1') || url.startsWith('http://localhost')) {
      return { action: 'allow' };
    }
    shell.openExternal(url);
    return { action: 'deny' };
  });
}

function createTray() {
  try {
    const icon = nativeImage.createFromPath(path.join(__dirname, 'icon.png'));
    tray = new Tray(icon.resize({ width: 16, height: 16 }));
    tray.setToolTip('Controle de Estoque — PDV/ERP');

    const contextMenu = Menu.buildFromTemplate([
      {
        label: 'Abrir Janela',
        click: () => {
          if (mainWindow) mainWindow.show();
        },
      },
      { type: 'separator' },
      {
        label: 'Sair',
        click: () => {
          isQuitting = true;
          app.quit();
        },
      },
    ]);

    tray.setContextMenu(contextMenu);
    tray.on('double-click', () => {
      if (mainWindow) mainWindow.show();
    });
  } catch (e) {
    console.log('[Tray] Não foi possível criar ícone na bandeja:', e.message);
  }
}

function buildMenu() {
  const template = [
    {
      label: 'Ficheiro',
      submenu: [
        {
          label: 'Backup Manual',
          accelerator: 'CmdOrCtrl+B',
          click: () => mainWindow.webContents.send('menu-action', 'backup'),
        },
        {
          label: 'Restaurar Backup',
          click: () => mainWindow.webContents.send('menu-action', 'restore'),
        },
        { type: 'separator' },
        {
          label: 'Exportar PDF',
          accelerator: 'CmdOrCtrl+E',
          click: () => mainWindow.webContents.send('menu-action', 'export-pdf'),
        },
        { type: 'separator' },
        {
          label: 'Sair',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Alt+F4',
          click: () => {
            isQuitting = true;
            app.quit();
          },
        },
      ],
    },
    {
      label: 'Navegação',
      submenu: [
        {
          label: 'PDV (Vendas)',
          accelerator: 'F1',
          click: () => mainWindow.webContents.send('navigate', '/pdv'),
        },
        {
          label: 'Dashboard',
          accelerator: 'F2',
          click: () => mainWindow.webContents.send('navigate', '/'),
        },
        {
          label: 'Produtos',
          accelerator: 'F3',
          click: () => mainWindow.webContents.send('navigate', '/produtos'),
        },
        {
          label: 'Clientes',
          accelerator: 'F4',
          click: () => mainWindow.webContents.send('navigate', '/clientes'),
        },
        {
          label: 'Relatórios',
          accelerator: 'F5',
          click: () => mainWindow.webContents.send('navigate', '/relatorios'),
        },
        { type: 'separator' },
        {
          label: 'Recarregar',
          accelerator: 'CmdOrCtrl+R',
          click: () => mainWindow.webContents.reload(),
        },
        {
          label: 'Ferramentas de Desenvolvimento',
          accelerator: 'F12',
          click: () => mainWindow.webContents.toggleDevTools(),
        },
      ],
    },
    {
      label: 'Ajuda',
      submenu: [
        {
          label: 'Sobre',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'Sobre o Controle de Estoque',
              message: 'Controle de Estoque — PDV/ERP',
              detail: `Versão: ${app.getVersion()}\nElectron: ${process.versions.electron}\nChrome: ${process.versions.chrome}\nNode.js: ${process.versions.node}`,
            });
          },
        },
        { type: 'separator' },
        {
          label: 'Documentação',
          click: () => shell.openExternal('https://github.com/controle-estoque'),
        },
      ],
    },
  ];

  return template;
}

// ===================== IPC Handlers =====================

ipcMain.handle('get-app-version', () => app.getVersion());

ipcMain.handle('is-dev', () => isDev);

ipcMain.handle('save-file', async (_, options) => {
  const result = await dialog.showSaveDialog(mainWindow, {
    title: options.title || 'Salvar ficheiro',
    defaultPath: options.defaultPath || 'documento.pdf',
    filters: options.filters || [{ name: 'Todos', extensions: ['*'] }],
  });
  return result;
});

ipcMain.handle('open-file', async (_, options) => {
  const result = await dialog.showOpenDialog(mainWindow, {
    title: options.title || 'Abrir ficheiro',
    filters: options.filters || [{ name: 'Todos', extensions: ['*'] }],
    properties: options.properties || ['openFile'],
  });
  return result;
});

ipcMain.handle('show-message-box', async (_, options) => {
  return dialog.showMessageBox(mainWindow, options);
});

ipcMain.handle('show-notification', (_, { title, body }) => {
  if (Notification.isSupported()) {
    const notif = new Notification({ title, body, icon: path.join(__dirname, 'icon.png') });
    notif.show();
    notif.on('click', () => {
      if (mainWindow) mainWindow.show();
    });
  }
});

ipcMain.handle('print-pdf', async (_, { html, options }) => {
  const win = new BrowserWindow({ show: false, webPreferences: { contextIsolation: true } });
  await win.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(html)}`);
  const pdf = await win.webContents.printToPDF(options || {});
  win.close();

  const result = await dialog.showSaveDialog(mainWindow, {
    title: 'Salvar PDF',
    defaultPath: options?.fileName || 'documento.pdf',
    filters: [{ name: 'PDF', extensions: ['pdf'] }],
  });

  if (!result.canceled && result.filePath) {
    const fs = require('fs');
    fs.writeFileSync(result.filePath, pdf);
    return { success: true, path: result.filePath };
  }
  return { success: false };
});

ipcMain.handle('get-config', (_, key) => store.get(key));
ipcMain.handle('set-config', (_, { key, value }) => store.set(key, value));

// ===================== App Lifecycle =====================

app.whenReady().then(async () => {
  await initStore();
  if (!isDev) {
    const { autoUpdater } = require('electron-updater');
    autoUpdater.checkForUpdatesAndNotify();
  }

  try {
    await startFlask();
  } catch (err) {
    dialog.showErrorBox('Erro ao iniciar', `Não foi possível iniciar o servidor Flask:\n${err.message}`);
    app.quit();
    return;
  }

  createWindow();
  createTray();
});

app.on('before-quit', () => {
  isQuitting = true;
  stopFlask();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow) mainWindow.show();
});
