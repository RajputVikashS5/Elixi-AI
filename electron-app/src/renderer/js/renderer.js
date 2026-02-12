// ============================================================================
// ELIXI AI - Integrated Renderer with Tab Navigation and Feature Modules
// ============================================================================

// ============================================================================
// UI ELEMENTS - Cache DOM references
// ============================================================================
const chatFeed = document.getElementById('chatFeed');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const micButton = document.getElementById('micButton');
const statusPill = document.getElementById('statusPill');
const assistantResponse = document.getElementById('assistantResponse');
const windowMinimize = document.getElementById('windowMinimize');
const windowMaximize = document.getElementById('windowMaximize');
const windowClose = document.getElementById('windowClose');

// Tab Navigation
const navTabs = document.querySelectorAll('.nav-tab');
const tabContents = document.querySelectorAll('.tab-content');

// Control Lists
const appList = document.getElementById('appList');
const commandList = document.getElementById('commandList');
const workflowList = document.getElementById('workflowList');
const habitsList = document.getElementById('habitsList');
const memoryList = document.getElementById('memoryList');
const preferencesList = document.getElementById('preferencesList');
const suggestionsList = document.getElementById('suggestionsList');
const topProcesses = document.getElementById('topProcesses');

// Monitor Cards
const monitorCPU = document.getElementById('monitorCPU');
const monitorMemory = document.getElementById('monitorMemory');
const monitorDisk = document.getElementById('monitorDisk');
const monitorNetwork = document.getElementById('monitorNetwork');
const monitorCPUInfo = document.getElementById('monitorCPUInfo');
const monitorMemoryInfo = document.getElementById('monitorMemoryInfo');
const monitorDiskInfo = document.getElementById('monitorDiskInfo');
const monitorNetworkInfo = document.getElementById('monitorNetworkInfo');

// Controls
const volumeSlider = document.getElementById('volumeSlider');
const brightnessSlider = document.getElementById('brightnessSlider');

// ============================================================================
// STATE MANAGEMENT
// ============================================================================
let mediaRecorder = null;
let audioChunks = [];
let isListening = false;
let hasWoken = false;
let currentTab = 'chat';
let monitoringInterval = null;

// ============================================================================
// TAB NAVIGATION SYSTEM
// ============================================================================
function switchTab(tabName) {
  currentTab = tabName;
  
  // Update nav tabs
  navTabs.forEach(tab => {
    tab.classList.toggle('active', tab.getAttribute('data-tab') === tabName);
  });
  
  // Update content
  tabContents.forEach(content => {
    content.classList.toggle('active', content.id === `content-${tabName}`);
  });
  
  // Load data for specific tabs
  if (tabName === 'system') {
    loadSystemControl();
  } else if (tabName === 'automation') {
    loadAutomation();
  } else if (tabName === 'memory') {
    loadMemory();
  } else if (tabName === 'monitor') {
    loadSystemMonitor();
    if (!monitoringInterval) {
      monitoringInterval = setInterval(loadSystemMonitor, 2000);
    }
  }
}

navTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    switchTab(tab.getAttribute('data-tab'));
  });
});

// ============================================================================
// CHAT INTERFACE
// ============================================================================
const updateAssistantResponse = (text) => {
  if (assistantResponse) {
    assistantResponse.textContent = text;
  }
};

const typeMessage = (element, text, speed = 16) => new Promise((resolve) => {
  let index = 0;
  const timer = setInterval(() => {
    element.textContent += text[index];
    index += 1;
    chatFeed.scrollTop = chatFeed.scrollHeight;
    if (index >= text.length) {
      clearInterval(timer);
      resolve();
    }
  }, speed);
});

const addMessage = async (role, text) => {
  const bubble = document.createElement('div');
  bubble.className = `message ${role}`;
  chatFeed.appendChild(bubble);
  chatFeed.scrollTop = chatFeed.scrollHeight;

  if (role === 'assistant') {
    bubble.classList.add('typing');
    updateAssistantResponse(text);
    await typeMessage(bubble, text);
    bubble.classList.remove('typing');
  } else {
    bubble.textContent = text;
  }
};

const setStatus = (text, variant) => {
  statusPill.textContent = text;
  statusPill.dataset.variant = variant || 'info';
};

const sendChat = async () => {
  const prompt = userInput.value.trim();
  if (!prompt) return;

  addMessage('user', prompt);
  userInput.value = '';
  setStatus('Thinking', 'busy');

  try {
    const response = await window.elixi.sendCommand('chat', { prompt });
    if (response && response.success) {
      await addMessage('assistant', response.reply || 'Online.');
      setStatus('Ready', 'ok');
    } else {
      await addMessage('assistant', response.error || 'I ran into an issue.');
      setStatus('Issue', 'warn');
    }
  } catch (error) {
    await addMessage('assistant', 'Backend unreachable. Is the Python service running?');
    setStatus('Offline', 'warn');
  }
};

// ============================================================================
// VOICE INTERFACE
// ============================================================================
const toggleMic = async () => {
  if (!isListening) {
    startListening();
  } else {
    stopListening();
  }
};

const startListening = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];
    isListening = true;
    hasWoken = false;

    micButton.classList.add('listening');
    setStatus('Listening', 'busy');

    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
      const arrayBuffer = await audioBlob.arrayBuffer();
      const audioBase64 = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));

      try {
        const transcribeResponse = await fetch('http://localhost:5000/voice/transcribe', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ audio: audioBase64 })
        });
        
        if (transcribeResponse.ok) {
          const data = await transcribeResponse.json();
          if (data.success && data.transcript) {
            const transcript = data.transcript.trim();
            addMessage('user', `(heard: "${transcript}")`);

            const wakeResponse = await fetch('http://localhost:5000/voice/wake-word-check', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ text: transcript })
            });

            if (wakeResponse.ok) {
              const wakeData = await wakeResponse.json();
              if (wakeData.is_wake_word) {
                hasWoken = true;
                await addMessage('assistant', 'Hey there! I\'m listening.');
                setStatus('Awake', 'ok');

                if (wakeData.command) {
                  await sendChatCommand(wakeData.command);
                }
              }
            }
          }
        }
      } catch (error) {
        await addMessage('assistant', 'Transcription failed. Try again?');
        setStatus('Offline', 'warn');
      }
    };

    mediaRecorder.start();
  } catch (error) {
    await addMessage('assistant', 'Microphone access denied.');
    setStatus('Error', 'warn');
  }
};

const stopListening = () => {
  if (mediaRecorder && isListening) {
    mediaRecorder.stop();
    mediaRecorder.stream.getTracks().forEach(track => track.stop());
    micButton.classList.remove('listening');
    isListening = false;
    setStatus('Ready', 'ok');
  }
};

const sendChatCommand = async (prompt) => {
  setStatus('Thinking', 'busy');
  try {
    const response = await window.elixi.sendCommand('chat', { prompt });
    if (response && response.success) {
      await addMessage('assistant', response.reply || 'Done.');
      setStatus('Ready', 'ok');
    } else {
      await addMessage('assistant', 'Command failed.');
      setStatus('Error', 'warn');
    }
  } catch (error) {
    await addMessage('assistant', 'Backend unreachable.');
    setStatus('Offline', 'warn');
  }
};

// ============================================================================
// SYSTEM CONTROL MODULE
// ============================================================================
async function loadSystemControl() {
  // Load applications
  try {
    const appData = await window.elixi.systemAppList?.() || { apps: [] };
    renderAppList(appData.apps || []);
  } catch (error) {
    console.error('Failed to load apps:', error);
  }

  // Load hardware control state
  try {
    const volume = await window.elixi.hardwareVolumeGet?.() || { volume: 50 };
    if (volumeSlider) volumeSlider.value = volume.volume || 50;
  } catch (error) {
    console.error('Failed to load volume:', error);
  }

  try {
    const brightness = await window.elixi.hardwareBrightnessGet?.() || { brightness: 75 };
    if (brightnessSlider) brightnessSlider.value = brightness.brightness || 75;
  } catch (error) {
    console.error('Failed to load brightness:', error);
  }
}

function renderAppList(apps) {
  if (!appList) return;
  appList.innerHTML = '';
  
  if (!apps || apps.length === 0) {
    appList.innerHTML = '<div class="loading">No applications found.</div>';
    return;
  }

  apps.slice(0, 12).forEach(app => {
    const appItem = document.createElement('div');
    appItem.className = 'app-item';
    appItem.innerHTML = `
      <div class="app-item-icon">📱</div>
      <div class="app-item-name">${app.name || 'App'}</div>
    `;
    appItem.addEventListener('click', async () => {
      await openApplication(app.name);
    });
    appList.appendChild(appItem);
  });
}

async function openApplication(appName) {
  try {
    const result = await window.elixi.systemAppOpen?.(appName) || {};
    if (result.success) {
      await addMessage('assistant', `Opened ${appName}.`);
    } else {
      await addMessage('assistant', `Failed to open ${appName}.`);
    }
  } catch (error) {
    console.error('Error opening app:', error);
  }
}

// ============================================================================
// AUTOMATION MODULE
// ============================================================================
async function loadAutomation() {
  try {
    const commands = await window.elixi.automationCommandsList?.() || { commands: [] };
    renderCommandList(commands.commands || []);
  } catch (error) {
    console.error('Failed to load commands:', error);
  }

  try {
    const workflows = await window.elixi.automationWorkflowsList?.() || { workflows: [] };
    renderWorkflowList(workflows.workflows || []);
  } catch (error) {
    console.error('Failed to load workflows:', error);
  }

  try {
    const habits = await window.elixi.automationHabitsList?.() || { habits: [] };
    renderHabitsList(habits.habits || []);
  } catch (error) {
    console.error('Failed to load habits:', error);
  }
}

function renderCommandList(commands) {
  if (!commandList) return;
  commandList.innerHTML = '';
  
  if (!commands || commands.length === 0) {
    commandList.innerHTML = '<div class="loading">No commands yet. Create one to get started!</div>';
    return;
  }

  commands.forEach(cmd => {
    const item = document.createElement('div');
    item.className = 'command-item';
    item.innerHTML = `
      <div class="item-info">
        <div class="item-title">${cmd.command_name || 'Unnamed'}</div>
        <div class="item-subtitle">${cmd.trigger_words?.join(', ') || 'No triggers'}</div>
      </div>
      <div class="item-actions">
        <button class="item-btn">Execute</button>
      </div>
    `;
    item.querySelector('.item-btn').addEventListener('click', async () => {
      await executeCommand(cmd._id || cmd.id);
    });
    commandList.appendChild(item);
  });
}

function renderWorkflowList(workflows) {
  if (!workflowList) return;
  workflowList.innerHTML = '';
  
  if (!workflows || workflows.length === 0) {
    workflowList.innerHTML = '<div class="loading">No workflows yet. Create one to automate!</div>';
    return;
  }

  workflows.forEach(wf => {
    const item = document.createElement('div');
    item.className = 'workflow-item';
    item.innerHTML = `
      <div class="item-info">
        <div class="item-title">${wf.name || 'Unnamed'}</div>
        <div class="item-subtitle">${wf.description || 'No description'}</div>
      </div>
      <div class="item-actions">
        <button class="item-btn">Run</button>
      </div>
    `;
    item.querySelector('.item-btn').addEventListener('click', async () => {
      await executeWorkflow(wf._id || wf.id);
    });
    workflowList.appendChild(item);
  });
}

function renderHabitsList(habits) {
  if (!habitsList) return;
  habitsList.innerHTML = '';
  
  if (!habits || habits.length === 0) {
    habitsList.innerHTML = '<div class="loading">No learned habits yet.</div>';
    return;
  }

  habits.forEach(habit => {
    const item = document.createElement('div');
    item.className = 'habit-item';
    item.innerHTML = `
      <div class="item-info">
        <div class="item-title">${habit.pattern || 'Pattern'}</div>
        <div class="item-subtitle">Confidence: ${Math.round((habit.confidence || 0) * 100)}%</div>
      </div>
    `;
    habitsList.appendChild(item);
  });
}

async function executeCommand(commandId) {
  try {
    const result = await window.elixi.automationCommandsExecute?.(commandId) || {};
    if (result.success) {
      await addMessage('assistant', 'Command executed successfully.');
    }
  } catch (error) {
    console.error('Error executing command:', error);
  }
}

async function executeWorkflow(workflowId) {
  try {
    const result = await window.elixi.automationWorkflowsExecute?.(workflowId) || {};
    if (result.success) {
      await addMessage('assistant', 'Workflow started.');
    }
  } catch (error) {
    console.error('Error executing workflow:', error);
  }
}

// ============================================================================
// MEMORY MODULE
// ============================================================================
async function loadMemory() {
  try {
    const memories = await window.elixi.memoryRecent?.() || { memories: [] };
    renderMemoryList(memories.memories || []);
  } catch (error) {
    console.error('Failed to load memories:', error);
  }

  try {
    const preferences = await window.elixi.preferencesGetAll?.() || { preferences: [] };
    renderPreferencesList(preferences.preferences || []);
  } catch (error) {
    console.error('Failed to load preferences:', error);
  }

  try {
    const suggestions = await window.elixi.automationSuggestionsActive?.() || { suggestions: [] };
    renderSuggestionsList(suggestions.suggestions || []);
  } catch (error) {
    console.error('Failed to load suggestions:', error);
  }
}

function renderMemoryList(memories) {
  if (!memoryList) return;
  memoryList.innerHTML = '';
  
  if (!memories || memories.length === 0) {
    memoryList.innerHTML = '<div class="loading">No memories stored yet.</div>';
    return;
  }

  memories.slice(0, 20).forEach(mem => {
    const item = document.createElement('div');
    item.className = 'memory-item';
    item.innerHTML = `
      <div class="item-info">
        <div class="item-title">${mem.title || mem.content?.substring(0, 40) || 'Memory'}</div>
        <div class="item-subtitle">${mem.type || 'general'} • ${new Date(mem.timestamp).toLocaleDateString()}</div>
      </div>
    `;
    memoryList.appendChild(item);
  });
}

function renderPreferencesList(preferences) {
  if (!preferencesList) return;
  preferencesList.innerHTML = '';
  
  if (!preferences || Object.keys(preferences).length === 0) {
    preferencesList.innerHTML = '<div class="loading">No preferences configured yet.</div>';
    return;
  }

  Object.entries(preferences).slice(0, 20).forEach(([key, value]) => {
    const item = document.createElement('div');
    item.className = 'preference-item';
    item.innerHTML = `
      <div class="item-info">
        <div class="item-title">${key}</div>
        <div class="item-subtitle">${JSON.stringify(value).substring(0, 50)}</div>
      </div>
    `;
    preferencesList.appendChild(item);
  });
}

function renderSuggestionsList(suggestions) {
  if (!suggestionsList) return;
  suggestionsList.innerHTML = '';
  
  if (!suggestions || suggestions.length === 0) {
    suggestionsList.innerHTML = '<div class="loading">No active suggestions.</div>';
    return;
  }

  suggestions.slice(0, 10).forEach(sugg => {
    const item = document.createElement('div');
    item.className = 'suggestion-item';
    item.innerHTML = `
      <div class="item-info">
        <div class="item-title">${sugg.suggestion || 'Suggestion'}</div>
        <div class="item-subtitle">${sugg.reason || 'Context-based'}</div>
      </div>
      <div class="item-actions">
        <button class="item-btn">Apply</button>
      </div>
    `;
    suggestionsList.appendChild(item);
  });
}

// ============================================================================
// SYSTEM MONITORING MODULE
// ============================================================================
async function loadSystemMonitor() {
  try {
    const cpu = await window.elixi.systemMonitorCpu?.() || { usage: 0 };
    if (monitorCPU) monitorCPU.textContent = `${Math.round(cpu.usage || 0)}%`;
  } catch (error) {
    console.error('Failed to load CPU:', error);
  }

  try {
    const memory = await window.elixi.systemMonitorMemory?.() || { usage: 0 };
    if (monitorMemory) monitorMemory.textContent = `${Math.round(memory.usage || 0)}%`;
  } catch (error) {
    console.error('Failed to load memory:', error);
  }

  try {
    const disk = await window.elixi.systemMonitorDisk?.() || { usage: 0 };
    if (monitorDisk) monitorDisk.textContent = `${Math.round(disk.usage || 0)}%`;
  } catch (error) {
    console.error('Failed to load disk:', error);
  }

  try {
    const network = await window.elixi.systemMonitorNetwork?.() || { stats: {} };
    const stats = network.stats || {};
    const totalBytes = (stats.bytes_sent || 0) + (stats.bytes_recv || 0);
    if (monitorNetwork) monitorNetwork.textContent = `${totalBytes} B`;
  } catch (error) {
    console.error('Failed to load network:', error);
  }

  try {
    const processes = await window.elixi.systemMonitorMemoryProcesses?.() || { processes: [] };
    renderProcessList(processes.processes || []);
  } catch (error) {
    console.error('Failed to load processes:', error);
  }
}

function renderProcessList(processes) {
  if (!topProcesses) return;
  topProcesses.innerHTML = '';
  
  if (!processes || processes.length === 0) {
    topProcesses.innerHTML = '<div class="loading">Loading processes...</div>';
    return;
  }

  processes.slice(0, 10).forEach(proc => {
    const item = document.createElement('div');
    item.className = 'process-item';
    item.innerHTML = `
      <span class="process-name">${proc.name || 'Process'}</span>
      <span class="process-usage">${Math.round(proc.memory_percent || 0)}%</span>
    `;
    topProcesses.appendChild(item);
  });
}

// ============================================================================
// HARDWARE CONTROLS
// ============================================================================
function setupHardwareControls() {
  if (volumeSlider) {
    volumeSlider.addEventListener('change', async (e) => {
      const volume = parseInt(e.target.value);
      try {
        await window.elixi.hardwareVolumeSet?.(volume);
        await addMessage('assistant', `Volume set to ${volume}%.`);
      } catch (error) {
        console.error('Error setting volume:', error);
      }
    });
  }

  if (brightnessSlider) {
    brightnessSlider.addEventListener('change', async (e) => {
      const brightness = parseInt(e.target.value);
      try {
        await window.elixi.hardwareBrightnessSet?.(brightness);
        await addMessage('assistant', `Brightness set to ${brightness}%.`);
      } catch (error) {
        console.error('Error setting brightness:', error);
      }
    });
  }

  // Power options
  document.getElementById('btnSleep')?.addEventListener('click', async () => {
    await window.elixi.systemPowerSleep?.();
  });

  document.getElementById('btnRestart')?.addEventListener('click', async () => {
    await window.elixi.systemPowerRestart?.();
  });

  document.getElementById('btnShutdown')?.addEventListener('click', async () => {
    const confirmed = confirm('Are you sure you want to shut down?');
    if (confirmed) {
      await window.elixi.systemPowerShutdown?.();
    }
  });
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================
sendButton?.addEventListener('click', sendChat);
userInput?.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    sendChat();
  }
});

micButton?.addEventListener('click', toggleMic);

if (windowMinimize) {
  windowMinimize.addEventListener('click', () => {
    window.elixi.windowControl('minimize');
  });
}

if (windowMaximize) {
  windowMaximize.addEventListener('click', () => {
    window.elixi.windowControl('toggle-maximize');
  });
}

if (windowClose) {
  windowClose.addEventListener('click', () => {
    window.elixi.windowControl('close');
  });
}

// ============================================================================
// INITIALIZATION
// ============================================================================
window.elixi.onAppReady(async () => {
  setStatus('Ready', 'ok');
  await addMessage('assistant', 'ELIXI online. Say "Hey Elixi" or type a message.');

  const status = await window.elixi.getSystemStatus();
  if (status && status.success) {
    const dbStatus = status.db_connected ? '✓' : '✗';
    await addMessage('assistant', `System: ${status.platform} | DB ${dbStatus}`);
  }

  // Setup hardware controls
  setupHardwareControls();

  // Load initial data for current tab
  loadSystemControl();
});

window.elixi.onOpenSettings(async () => {
  switchTab('memory');
});

