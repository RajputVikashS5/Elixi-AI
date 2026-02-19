const { app, BrowserWindow, ipcMain, Tray, Menu } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// Set user data directory to avoid cache permission issues
const userDataPath = path.join(app.getPath('userData'), 'ELIXI_AI');
if (!fs.existsSync(userDataPath)) {
  fs.mkdirSync(userDataPath, { recursive: true });
}
app.setPath('userData', userDataPath);
app.commandLine.appendSwitch('disable-gpu-compositing');

let mainWindow;
let tray = null;
let pythonProcess = null;
let isQuitting = false;

// Start Python backend server
function startPythonBackend() {
  const pythonScript = path.join(__dirname, '../../../python-core/main.py');
  const pythonExe = 'C:\\Users\\Dell\\AppData\\Local\\Programs\\Python\\Python311\\python.exe';
  
  pythonProcess = spawn(pythonExe, [pythonScript], {
    detached: false,
    stdio: 'pipe',
    shell: false
  });

  pythonProcess.stdout.on('data', (data) => {
    console.log(`[Python] ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`[Python Error] ${data}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`);
  });

  pythonProcess.on('error', (err) => {
    console.error(`Failed to start Python backend: ${err.message}`);
  });
}

// Create main application window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 720,
    minWidth: 960,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, '../preload/preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      sandbox: true
    },
    icon: path.join(__dirname, '../../assets/icons/app-icon.ico'),
    frame: false,
    transparent: true,
    resizable: true
  });

  mainWindow.maximize();

  // Load the index.html
  const startUrl = path.join(__dirname, '../renderer/index.html');
  mainWindow.loadFile(startUrl);

  // Open DevTools only when explicitly requested
  if (process.argv.includes('--devtools')) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('unresponsive', () => {
    console.warn('Window became unresponsive');
    mainWindow.reload();
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle window minimize to tray
  mainWindow.on('minimize', (event) => {
    event.preventDefault();
    mainWindow.hide();
  });

  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });
}

// Create system tray
function createTray() {
  tray = new Tray(path.join(__dirname, '../../assets/icons/tray-icon.ico'));
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show ELIXI',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        }
      }
    },
    {
      label: 'Settings',
      click: () => {
        if (mainWindow) {
          mainWindow.webContents.send('open-settings');
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Exit',
      click: () => {
        isQuitting = true;
        app.quit();
      }
    }
  ]);
  tray.setContextMenu(contextMenu);
  tray.on('click', () => {
    if (mainWindow && mainWindow.isVisible()) {
      mainWindow.hide();
    } else if (mainWindow) {
      mainWindow.show();
      mainWindow.focus();
    }
  });
}

// IPC Handlers - Extended with all backend endpoints
ipcMain.handle('voice-command', async (event, command) => {
  console.log('Voice command received:', command);
  return { success: true, command };
});

ipcMain.handle('execute-command', async (event, command, args) => {
  try {
    const response = await fetch('http://localhost:5000/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command, args })
    });
    return await response.json();
  } catch (error) {
    console.error('Command execution error:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('get-system-status', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/system-status');
    return await response.json();
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('save-memory', async (event, memoryData) => {
  try {
    const response = await fetch('http://localhost:5000/memory/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(memoryData)
    });
    return await response.json();
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('load-memory', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/memory/load');
    return await response.json();
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// System Control Handlers
ipcMain.handle('system-app-list', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/system/app/list');
    return await response.json();
  } catch (error) {
    return { success: false, apps: [], error: error.message };
  }
});

ipcMain.handle('system-app-open', async (event, appName) => {
  try {
    const response = await fetch('http://localhost:5000/system/app/open', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ app_name: appName })
    });
    return await response.json();
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('hardware-volume-get', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/system/hardware/volume/get');
    return await response.json();
  } catch (error) {
    return { success: false, volume: 0, error: error.message };
  }
});

ipcMain.handle('hardware-volume-set', async (event, volume) => {
  try {
    const response = await fetch('http://localhost:5000/system/hardware/volume/set', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ volume })
    });
    return await response.json();
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('hardware-brightness-get', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/system/hardware/brightness/get');
    return await response.json();
  } catch (error) {
    return { success: false, brightness: 0, error: error.message };
  }
});

ipcMain.handle('hardware-brightness-set', async (event, brightness) => {
  try {
    const response = await fetch('http://localhost:5000/system/hardware/brightness/set', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ brightness })
    });
    return await response.json();
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('hardware-wifi-status', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/system/hardware/wifi/status');
    return await response.json();
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('system-power-sleep', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/system/power/sleep', { method: 'POST' });
    return await response.json();
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('system-power-shutdown', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/system/power/shutdown', { method: 'POST' });
    return await response.json();
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('system-power-restart', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/system/power/restart', { method: 'POST' });
    return await response.json();
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// System Monitoring Handlers
ipcMain.handle('system-monitor-overview', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/system/monitor/overview');
    return await response.json();
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('system-monitor-cpu', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/system/monitor/cpu');
    return await response.json();
  } catch (error) {
    return { success: false, usage: 0, error: error.message };
  }
});

ipcMain.handle('system-monitor-memory', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/system/monitor/memory');
    return await response.json();
  } catch (error) {
    return { success: false, usage: 0, error: error.message };
  }
});

ipcMain.handle('system-monitor-disk', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/system/monitor/disk');
    return await response.json();
  } catch (error) {
    return { success: false, usage: 0, error: error.message };
  }
});

ipcMain.handle('system-monitor-memory-processes', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/system/monitor/memory/top-processes');
    return await response.json();
  } catch (error) {
    return { success: false, processes: [], error: error.message };
  }
});

ipcMain.handle('system-monitor-network', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/system/monitor/network');
    return await response.json();
  } catch (error) {
    return { success: false, stats: {}, error: error.message };
  }
});

// Automation Handlers
ipcMain.handle('automation-commands-list', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/automation/custom-commands/list');
    return await response.json();
  } catch (error) {
    return { success: false, commands: [], error: error.message };
  }
});

ipcMain.handle('automation-commands-create', async (event, command) => {
  try {
    const response = await fetch('http://localhost:5000/automation/custom-commands/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(command)
    });
    return await response.json();
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('automation-commands-execute', async (event, commandId) => {
  try {
    const response = await fetch('http://localhost:5000/automation/custom-commands/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command_id: commandId })
    });
    return await response.json();
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('automation-workflows-list', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/automation/workflows/list');
    return await response.json();
  } catch (error) {
    return { success: false, workflows: [], error: error.message };
  }
});

ipcMain.handle('automation-workflows-create', async (event, workflow) => {
  try {
    const response = await fetch('http://localhost:5000/automation/workflows/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(workflow)
    });
    return await response.json();
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('automation-workflows-execute', async (event, workflowId) => {
  try {
    const response = await fetch('http://localhost:5000/automation/workflows/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ workflow_id: workflowId })
    });
    return await response.json();
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('automation-habits-list', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/automation/habits/list');
    return await response.json();
  } catch (error) {
    return { success: false, habits: [], error: error.message };
  }
});

ipcMain.handle('automation-suggestions-active', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/suggestions/active');
    return await response.json();
  } catch (error) {
    return { success: false, suggestions: [], error: error.message };
  }
});

// Memory & Preferences Handlers
ipcMain.handle('memory-search', async (event, query) => {
  try {
    const response = await fetch('http://localhost:5000/memory/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    return await response.json();
  } catch (error) {
    return { success: false, results: [], error: error.message };
  }
});

ipcMain.handle('memory-recent', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/memory/recent');
    return await response.json();
  } catch (error) {
    return { success: false, memories: [], error: error.message };
  }
});

ipcMain.handle('memory-statistics', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/memory/statistics');
    return await response.json();
  } catch (error) {
    return { success: false, stats: {}, error: error.message };
  }
});

ipcMain.handle('preferences-get-all', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/preferences/all');
    return await response.json();
  } catch (error) {
    return { success: false, preferences: {}, error: error.message };
  }
});

ipcMain.handle('preferences-set', async (event, key, value) => {
  try {
    const response = await fetch('http://localhost:5000/preferences/set', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key, value })
    });
    return await response.json();
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// Window Control Handler
ipcMain.handle('window-control', (event, action) => {
  if (!mainWindow) return;

  switch (action) {
    case 'minimize':
      mainWindow.minimize();
      break;
    case 'toggle-maximize':
      if (mainWindow.isMaximized()) {
        mainWindow.unmaximize();
      } else {
        mainWindow.maximize();
      }
      break;
    case 'close':
      isQuitting = true;
      app.quit();
      break;
    default:
      break;
  }
});

ipcMain.handle('close-app', () => {
  isQuitting = true;
  app.quit();
});

// ==================== STAGE 5 PHASE 5: BACKGROUND MODE & AUTO-START ====================

// Background Mode IPC Handlers
ipcMain.handle('background-mode-start', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/system/background-mode', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enable: true })
    });
    return await response.json();
  } catch (error) {
    console.error('Background mode start error:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('background-mode-stop', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/system/background-mode', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enable: false })
    });
    return await response.json();
  } catch (error) {
    console.error('Background mode stop error:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('background-mode-status', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/system/background-status');
    return await response.json();
  } catch (error) {
    console.error('Background mode status error:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('background-mode-memory', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/system/background-memory');
    return await response.json();
  } catch (error) {
    console.error('Background memory check error:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('background-mode-cleanup', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/system/background-cleanup', {
      method: 'POST'
    });
    return await response.json();
  } catch (error) {
    console.error('Background cleanup error:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('background-mode-wake-triggers', async (event, triggers) => {
  try {
    const response = await fetch('http://localhost:5000/system/background-wake-triggers', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(triggers)
    });
    return await response.json();
  } catch (error) {
    console.error('Wake triggers error:', error);
    return { success: false, error: error.message };
  }
});

// Auto-Start IPC Handlers
ipcMain.handle('auto-start-enable', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/system/auto-start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'enable' })
    });
    return await response.json();
  } catch (error) {
    console.error('Auto-start enable error:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('auto-start-disable', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/system/auto-start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'disable' })
    });
    return await response.json();
  } catch (error) {
    console.error('Auto-start disable error:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('auto-start-status', async (event) => {
  try {
    const response = await fetch('http://localhost:5000/system/auto-start-status');
    return await response.json();
  } catch (error) {
    console.error('Auto-start status error:', error);
    return { success: false, error: error.message };
  }
});

// Floating Window Control
ipcMain.handle('floating-window-show', async (event) => {
  if (mainWindow) {
    mainWindow.show();
    mainWindow.focus();
  }
  return { success: true };
});

ipcMain.handle('floating-window-hide', async (event) => {
  if (mainWindow) {
    mainWindow.hide();
  }
  return { success: true };
});

ipcMain.handle('floating-window-toggle', async (event) => {
  if (mainWindow) {
    if (mainWindow.isVisible()) {
      mainWindow.hide();
      return { success: true, visible: false };
    } else {
      mainWindow.show();
      mainWindow.focus();
      return { success: true, visible: true };
    }
  }
  return { success: false };
});

ipcMain.handle('floating-window-position', async (event, x, y) => {
  if (mainWindow) {
    mainWindow.setPosition(x, y);
    return { success: true };
  }
  return { success: false };
});

ipcMain.handle('floating-window-size', async (event, width, height) => {
  if (mainWindow) {
    mainWindow.setSize(width, height, true);
    return { success: true };
  }
  return { success: false };
});

ipcMain.handle('floating-window-always-on-top', async (event, alwaysOnTop) => {
  if (mainWindow) {
    mainWindow.setAlwaysOnTop(alwaysOnTop);
    return { success: true, alwaysOnTop };
  }
  return { success: false };
});

// ==================== END PHASE 5 ====================

// App event listeners
app.on('ready', () => {
  startPythonBackend();
  createWindow();
  createTray();
  
  // Wait for Python server to start
  setTimeout(() => {
    if (mainWindow) {
      mainWindow.webContents.send('app-ready');
    }
  }, 2000);
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  } else {
    mainWindow.show();
    mainWindow.focus();
  }
});

app.on('before-quit', () => {
  isQuitting = true;
  if (pythonProcess) {
    pythonProcess.kill();
  }
});

app.on('window-all-closed', () => {
  // On macOS, keep app running until explicitly quit
  if (process.platform !== 'darwin') {
    isQuitting = true;
    app.quit();
  }
});

// Single instance lock
const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}
