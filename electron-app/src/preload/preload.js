const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('elixi', {
  // Core Commands
  sendCommand: (command, args) => ipcRenderer.invoke('execute-command', command, args),
  sendVoiceCommand: (command) => ipcRenderer.invoke('voice-command', command),
  getSystemStatus: () => ipcRenderer.invoke('get-system-status'),
  
  // Memory Management
  saveMemory: (memoryData) => ipcRenderer.invoke('save-memory', memoryData),
  loadMemory: () => ipcRenderer.invoke('load-memory'),
  memoryRecent: () => ipcRenderer.invoke('memory-recent'),
  memorySearch: (query) => ipcRenderer.invoke('memory-search', query),
  memoryStatistics: () => ipcRenderer.invoke('memory-statistics'),
  
  // System Control - Applications
  systemAppList: () => ipcRenderer.invoke('system-app-list'),
  systemAppOpen: (appName) => ipcRenderer.invoke('system-app-open', appName),
  
  // System Control - Hardware
  hardwareVolumeGet: () => ipcRenderer.invoke('hardware-volume-get'),
  hardwareVolumeSet: (volume) => ipcRenderer.invoke('hardware-volume-set', volume),
  hardwareBrightnessGet: () => ipcRenderer.invoke('hardware-brightness-get'),
  hardwareBrightnessSet: (brightness) => ipcRenderer.invoke('hardware-brightness-set', brightness),
  hardwareWiFiStatus: () => ipcRenderer.invoke('hardware-wifi-status'),
  
  // System Control - Power
  systemPowerSleep: () => ipcRenderer.invoke('system-power-sleep'),
  systemPowerShutdown: () => ipcRenderer.invoke('system-power-shutdown'),
  systemPowerRestart: () => ipcRenderer.invoke('system-power-restart'),
  
  // System Monitoring
  systemMonitorOverview: () => ipcRenderer.invoke('system-monitor-overview'),
  systemMonitorCpu: () => ipcRenderer.invoke('system-monitor-cpu'),
  systemMonitorMemory: () => ipcRenderer.invoke('system-monitor-memory'),
  systemMonitorDisk: () => ipcRenderer.invoke('system-monitor-disk'),
  systemMonitorMemoryProcesses: () => ipcRenderer.invoke('system-monitor-memory-processes'),
  systemMonitorNetwork: () => ipcRenderer.invoke('system-monitor-network'),
  
  // Automation - Custom Commands
  automationCommandsList: () => ipcRenderer.invoke('automation-commands-list'),
  automationCommandsCreate: (command) => ipcRenderer.invoke('automation-commands-create', command),
  automationCommandsExecute: (commandId) => ipcRenderer.invoke('automation-commands-execute', commandId),
  
  // Automation - Workflows
  automationWorkflowsList: () => ipcRenderer.invoke('automation-workflows-list'),
  automationWorkflowsCreate: (workflow) => ipcRenderer.invoke('automation-workflows-create', workflow),
  automationWorkflowsExecute: (workflowId) => ipcRenderer.invoke('automation-workflows-execute', workflowId),
  
  // Automation - Habits & Suggestions
  automationHabitsList: () => ipcRenderer.invoke('automation-habits-list'),
  automationSuggestionsActive: () => ipcRenderer.invoke('automation-suggestions-active'),
  
  // Preferences
  preferencesGetAll: () => ipcRenderer.invoke('preferences-get-all'),
  preferencesSet: (key, value) => ipcRenderer.invoke('preferences-set', key, value),
  
  // Window Control
  windowControl: (action) => ipcRenderer.invoke('window-control', action),
  closeApp: () => ipcRenderer.invoke('close-app'),
  
  // Event Listeners
  onAppReady: (callback) => ipcRenderer.on('app-ready', callback),
  onOpenSettings: (callback) => ipcRenderer.on('open-settings', callback)
});
