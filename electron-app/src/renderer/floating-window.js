/**
 * Stage 5 Phase 5: Floating Assistant Window
 * File: electron-app/src/renderer/floating-window.js
 * Purpose: Frameless floating overlay window for ELIXI AI assistant
 * Size: 400+ lines
 */

const { ipcRenderer, shell, contextBridge } = require('electron');
const path = require('path');

class FloatingWindowManager {
  constructor() {
    this.isMaximized = false;
    this.isDragging = false;
    this.isResizing = false;
    this.dragStartPos = { x: 0, y: 0 };
    this.windowStartPos = { x: 0, y: 0 };
    this.resizeStartPos = { x: 0, y: 0 };
    this.windowStartSize = { width: 0, height: 0 };
    this.resizeDirection = null;
    
    this.RESIZE_THRESHOLD = 10; // pixels
    this.MIN_WIDTH = 300;
    this.MIN_HEIGHT = 250;
    this.MAX_WIDTH = 1200;
    this.MAX_HEIGHT = 900;
    
    this.init();
  }

  /**
   * Initialize floating window DOM and event listeners
   */
  init() {
    this.createWindowStructure();
    this.setupEventListeners();
    this.setupIPCListeners();
    this.loadStyles();
    this.positionWindow();
    this.setupContextMenu();
  }

  /**
   * Create the floating window DOM structure
   */
  createWindowStructure() {
    // Remove default body styles
    document.body.style.margin = '0';
    document.body.style.padding = '0';
    document.body.style.overflow = 'hidden';
    document.body.style.background = 'transparent';

    // Create main floating window container
    const floatingWindow = document.createElement('div');
    floatingWindow.id = 'floating-window';
    floatingWindow.className = 'floating-window';
    
    // Title bar (draggable)
    const titleBar = document.createElement('div');
    titleBar.className = 'floating-title-bar';
    titleBar.innerHTML = `
      <div class="floating-title-content">
        <svg class="floating-icon" viewBox="0 0 24 24" width="20" height="20">
          <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
        </svg>
        <span class="floating-title-text">ELIXI Assistant</span>
      </div>
      <div class="floating-title-buttons">
        <button class="floating-btn floating-minimize-btn" title="Minimize">
          <svg viewBox="0 0 24 24" width="18" height="18">
            <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
          </svg>
        </button>
        <button class="floating-btn floating-close-btn" title="Close">
          <svg viewBox="0 0 24 24" width="18" height="18">
            <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </button>
      </div>
    `;

    // Content area
    const contentArea = document.createElement('div');
    contentArea.className = 'floating-content';
    contentArea.id = 'floating-content';
    contentArea.innerHTML = `
      <div class="floating-input-section">
        <input 
          type="text" 
          id="floating-input" 
          class="floating-input" 
          placeholder="Ask me anything..."
          autocomplete="off"
        />
        <button class="floating-send-btn" title="Send (Enter)">
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M16.6915026,12.4744748 L3.50612381,13.2599618 C3.19218622,13.2599618 3.03521743,13.4170592 3.03521743,13.5741566 L1.15159189,20.0151496 C0.8376543,20.8006365 0.99,21.89 1.77946707,22.52 C2.41,22.99 3.50612381,23.1 4.13399899,22.8429026 L21.714504,14.0454487 C22.6563168,13.5741566 23.1272231,12.6315722 22.9702544,11.6889879 L4.13399899,1.16109852 C3.34915502,0.9 2.40734225,0.9 1.77946707,1.4430663 C0.994623095,2.0788181 0.837654326,3.16346751 1.15159189,3.94894657 L3.03521743,10.3899396 C3.03521743,10.5470369 3.19218622,10.7041343 3.50612381,10.7041343 L16.6915026,11.4896235 C16.6915026,11.4896235 17.1624089,11.4896235 17.1624089,12.0327201 C17.1624089,12.5758054 16.6915026,12.4744748 16.6915026,12.4744748 Z"/>
          </svg>
        </button>
      </div>
      
      <div class="floating-response-section">
        <div class="floating-response" id="floating-response">
          <div class="floating-welcome">
            <h3>Welcome to ELIXI</h3>
            <p>Your AI assistant is ready. Try asking me something!</p>
          </div>
        </div>
      </div>
      
      <div class="floating-status-bar">
        <span class="floating-status" id="floating-status">Ready</span>
        <span class="floating-memory" id="floating-memory">~145 MB</span>
      </div>
    `;

    // Resize handles
    const resizeHandles = document.createElement('div');
    resizeHandles.className = 'floating-resize-handles';
    resizeHandles.innerHTML = `
      <div class="floating-resize-handle floating-resize-top-left" data-direction="top-left"></div>
      <div class="floating-resize-handle floating-resize-top" data-direction="top"></div>
      <div class="floating-resize-handle floating-resize-top-right" data-direction="top-right"></div>
      <div class="floating-resize-handle floating-resize-right" data-direction="right"></div>
      <div class="floating-resize-handle floating-resize-bottom-right" data-direction="bottom-right"></div>
      <div class="floating-resize-handle floating-resize-bottom" data-direction="bottom"></div>
      <div class="floating-resize-handle floating-resize-bottom-left" data-direction="bottom-left"></div>
      <div class="floating-resize-handle floating-resize-left" data-direction="left"></div>
    `;

    floatingWindow.appendChild(titleBar);
    floatingWindow.appendChild(contentArea);
    floatingWindow.appendChild(resizeHandles);

    document.body.appendChild(floatingWindow);
  }

  /**
   * Setup event listeners for window interactions
   */
  setupEventListeners() {
    // Title bar dragging
    const titleBar = document.querySelector('.floating-title-bar');
    titleBar.addEventListener('mousedown', (e) => this.onTitleBarMouseDown(e));

    // Input handling
    const input = document.getElementById('floating-input');
    input.addEventListener('keypress', (e) => this.onInputKeyPress(e));
    
    // Buttons
    document.querySelector('.floating-minimize-btn').addEventListener('click', () => this.minimize());
    document.querySelector('.floating-close-btn').addEventListener('click', () => this.close());
    document.querySelector('.floating-send-btn').addEventListener('click', () => this.sendMessage());

    // Resize handles
    document.querySelectorAll('.floating-resize-handle').forEach(handle => {
      handle.addEventListener('mousedown', (e) => this.onResizeMouseDown(e));
    });

    // Prevent text selection while dragging
    document.addEventListener('selectstart', () => !this.isDragging);
  }

  /**
   * Title bar mouse down - start dragging
   */
  onTitleBarMouseDown(e) {
    if (e.target.closest('.floating-title-buttons')) return;

    this.isDragging = true;
    this.dragStartPos = { x: e.clientX, y: e.clientY };

    ipcRenderer.invoke('get-window-bounds').then(bounds => {
      this.windowStartPos = { x: bounds.x, y: bounds.y };
    });

    document.addEventListener('mousemove', (e) => this.onMouseMove(e));
    document.addEventListener('mouseup', () => this.onMouseUp());
  }

  /**
   * Mouse move - handle dragging and resizing
   */
  onMouseMove(e) {
    if (this.isDragging) {
      const deltaX = e.clientX - this.dragStartPos.x;
      const deltaY = e.clientY - this.dragStartPos.y;

      ipcRenderer.send('move-window', {
        x: this.windowStartPos.x + deltaX,
        y: this.windowStartPos.y + deltaY
      });
    }

    if (this.isResizing) {
      const deltaX = e.clientX - this.resizeStartPos.x;
      const deltaY = e.clientY - this.resizeStartPos.y;

      this.handleResize(deltaX, deltaY);
    }
  }

  /**
   * Mouse up - stop dragging/resizing
   */
  onMouseUp() {
    this.isDragging = false;
    this.isResizing = false;
    this.resizeDirection = null;

    document.removeEventListener('mousemove', (e) => this.onMouseMove(e));
    document.removeEventListener('mouseup', () => this.onMouseUp());
  }

  /**
   * Resize handle mouse down
   */
  onResizeMouseDown(e) {
    this.isResizing = true;
    this.resizeDirection = e.target.dataset.direction;
    this.resizeStartPos = { x: e.clientX, y: e.clientY };

    ipcRenderer.invoke('get-window-bounds').then(bounds => {
      this.windowStartSize = { width: bounds.width, height: bounds.height };
    });

    document.addEventListener('mousemove', (e) => this.onMouseMove(e));
    document.addEventListener('mouseup', () => this.onMouseUp());

    e.preventDefault();
  }

  /**
   * Handle window resize based on direction
   */
  handleResize(deltaX, deltaY) {
    let newWidth = this.windowStartSize.width;
    let newHeight = this.windowStartSize.height;

    if (['right', 'top-right', 'bottom-right'].includes(this.resizeDirection)) {
      newWidth = Math.max(this.MIN_WIDTH, Math.min(this.MAX_WIDTH, this.windowStartSize.width + deltaX));
    }

    if (['bottom', 'bottom-right', 'bottom-left'].includes(this.resizeDirection)) {
      newHeight = Math.max(this.MIN_HEIGHT, Math.min(this.MAX_HEIGHT, this.windowStartSize.height + deltaY));
    }

    ipcRenderer.send('resize-window', { width: newWidth, height: newHeight });
  }

  /**
   * Input key press handler
   */
  onInputKeyPress(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      this.sendMessage();
    }
  }

  /**
   * Send message to backend
   */
  async sendMessage() {
    const input = document.getElementById('floating-input');
    const message = input.value.trim();

    if (!message) return;

    // Clear input
    input.value = '';
    input.focus();

    // Show loading state
    this.setStatus('Processing...');
    this.displayMessage(message, 'user');

    try {
      const response = await ipcRenderer.invoke('send-message', message);
      this.displayMessage(response.text, 'assistant');
      this.setStatus('Ready');
    } catch (error) {
      this.displayMessage(`Error: ${error.message}`, 'error');
      this.setStatus('Error occurred');
    }
  }

  /**
   * Display message in response area
   */
  displayMessage(text, role) {
    const responseArea = document.getElementById('floating-response');
    
    // Remove welcome message if it exists
    const welcome = responseArea.querySelector('.floating-welcome');
    if (welcome) welcome.remove();

    const messageDiv = document.createElement('div');
    messageDiv.className = `floating-message floating-message-${role}`;
    messageDiv.innerHTML = `
      <div class="floating-message-content">
        ${text}
      </div>
    `;

    responseArea.appendChild(messageDiv);
    responseArea.scrollTop = responseArea.scrollHeight;
  }

  /**
   * Set status
   */
  setStatus(status) {
    const statusEl = document.getElementById('floating-status');
    if (statusEl) {
      statusEl.textContent = status;
    }
  }

  /**
   * Minimize window
   */
  minimize() {
    ipcRenderer.send('minimize-window');
  }

  /**
   * Close window
   */
  close() {
    ipcRenderer.send('hide-window');
  }

  /**
   * Position window on screen
   */
  async positionWindow() {
    try {
      const bounds = await ipcRenderer.invoke('get-primary-display-bounds');
      ipcRenderer.send('position-window', {
        x: bounds.width - 650,
        y: bounds.height - 600
      });
    } catch (error) {
      console.error('Failed to position window:', error);
    }
  }

  /**
   * Setup IPC listeners
   */
  setupIPCListeners() {
    // Update memory usage
    ipcRenderer.on('update-memory', (event, memoryMB) => {
      const memoryEl = document.getElementById('floating-memory');
      if (memoryEl) {
        memoryEl.textContent = `~${Math.round(memoryMB)} MB`;
      }
    });

    // Show notification
    ipcRenderer.on('show-notification', (event, message) => {
      this.displayMessage(message, 'notification');
    });

    // Focus window
    ipcRenderer.on('focus-window', () => {
      ipcRenderer.send('show-window');
      document.getElementById('floating-input').focus();
    });
  }

  /**
   * Setup context menu
   */
  setupContextMenu() {
    document.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      ipcRenderer.send('show-context-menu', {
        x: e.clientX,
        y: e.clientY
      });
    });
  }

  /**
   * Load external styles
   */
  loadStyles() {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = './styles/floating-window.css';
    document.head.appendChild(link);
  }

  /**
   * Toggle always on top
   */
  toggleAlwaysOnTop() {
    ipcRenderer.send('toggle-always-on-top');
  }

  /**
   * Get window state
   */
  async getWindowState() {
    return await ipcRenderer.invoke('get-window-state');
  }

  /**
   * Update UI based on background mode status
   */
  updateBackgroundModeStatus(isRunning) {
    const titleEl = document.querySelector('.floating-title-text');
    if (titleEl) {
      titleEl.textContent = isRunning ? 'ELIXI (Background)' : 'ELIXI Assistant';
    }
  }

  /**
   * Show settings dialog
   */
  showSettings() {
    ipcRenderer.send('show-settings-dialog');
  }

  /**
   * Enable/disable input
   */
  setInputEnabled(enabled) {
    const input = document.getElementById('floating-input');
    const btn = document.querySelector('.floating-send-btn');
    if (input) input.disabled = !enabled;
    if (btn) btn.disabled = !enabled;
  }
}

// Initialize when DOM is ready
let floatingWindow;

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    floatingWindow = new FloatingWindowManager();
    window.floatingWindow = floatingWindow;
  });
} else {
  floatingWindow = new FloatingWindowManager();
  window.floatingWindow = floatingWindow;
}

// Expose to global scope for debugging
window.FloatingWindowManager = FloatingWindowManager;
