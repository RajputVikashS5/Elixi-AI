# Stage 5 Phase 5 - Quick Start Guide

**Quick Reference for Floating Interface & Background Mode**

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [API Examples](#api-examples)
3. [Configuration](#configuration)
4. [Troubleshooting](#troubleshooting)
5. [Testing](#testing)

---

## Getting Started

### Prerequisites

```bash
# Install dependencies (if not already installed)
pip install pystray pillow psutil pywin32 python-dotenv requests

# For Windows: Register COM objects
python -m pip install --upgrade pywin32
python Scripts/pywin32_postinstall.py -install
```

### Starting Phase 5

```bash
# Start with floating interface
python main.py --mode floating

# Start in background mode
python main.py --mode background

# Start normally (default)
python main.py

# Enable auto-start
python -c "from auto_start_config import AutoStartConfiguration; AutoStartConfiguration().enable_auto_start()"
```

---

## API Examples

### 1. Enable Background Mode

```bash
# Using curl
curl -X POST http://localhost:5000/system/background-mode \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# Using Python
import requests
response = requests.post(
    'http://localhost:5000/system/background-mode',
    json={'enabled': True}
)
print(response.json())
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "status": "active",
    "mode": "background",
    "timestamp": "2026-02-19T12:00:00Z"
  }
}
```

### 2. Check Background Status

```bash
curl http://localhost:5000/system/background-status

# Response:
{
  "status": "success",
  "data": {
    "running": true,
    "memory_mb": 145.3,
    "cpu_percent": 2.1,
    "uptime_seconds": 3600,
    "wake_triggers": {
      "hotkey": "ALT+Shift+J",
      "voice": true,
      "api": true
    }
  }
}
```

### 3. Configure Auto-start

```bash
curl -X POST http://localhost:5000/system/auto-start \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "startup_delay": 5}'

# Response:
{
  "status": "success",
  "data": {
    "enabled": true,
    "startup_delay_seconds": 5,
    "registry_path": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
  }
}
```

### 4. Get System Tray Status

```bash
curl http://localhost:5000/system/tray-menu

# Response:
{
  "status": "success",
  "data": {
    "tray_visible": true,
    "items": [
      {"label": "Show/Hide", "action": "show_hide"},
      {"label": "Settings", "action": "settings"},
      {"label": "Quit", "action": "quit"}
    ]
  }
}
```

### 5. Restart Service

```bash
curl -X POST http://localhost:5000/system/restart-service

# Response:
{
  "status": "success",
  "data": {
    "success": true,
    "message": "Background service restarted successfully",
    "new_pid": 12345
  }
}
```

---

## Configuration

### Environment Variables

Create `.env` in `python-core/`:

```bash
# Background Mode
BACKGROUND_MODE_ENABLED=true
BACKGROUND_AUTO_RESTART=true
BACKGROUND_STARTUP_DELAY=5

# System Tray
SYSTEM_TRAY_ENABLED=true
TRAY_ICON_PATH=./assets/icons/tray.ico

# Auto-start
AUTO_START_ENABLED=false
AUTO_START_DELAY=5

# Monitoring
MEMORY_CHECK_INTERVAL=30
CPU_CHECK_INTERVAL=30
LOG_BACKGROUND_EVENTS=true

# Wake Triggers
WAKE_HOTKEY=ALT+Shift+J
WAKE_ON_VOICE=true
WAKE_ON_API=true
```

### Floating Window Configuration

In `electron-app/src/renderer/config.js`:

```javascript
const floatingWindowConfig = {
  width: 600,
  height: 500,
  minWidth: 400,
  minHeight: 300,
  alwaysOnTop: true,
  transparent: true,
  frame: false,
  resizable: true,
  webPreferences: {
    preload: path.join(__dirname, '../preload/index.js'),
    nodeIntegration: false,
    contextIsolation: true
  }
};

const floatingStylesConfig = {
  theme: 'dark',
  glassmorphism: true,
  animationDuration: 300,
  compactMode: true
};
```

---

## Troubleshooting

### Background Mode Not Starting

**Issue:** Background service fails to start  
**Solution:**
```bash
# Check logs
tail -f logs/background_mode.log

# Check process
Get-Process | grep python

# Restart service
curl -X POST http://localhost:5000/system/restart-service

# Clear stale processes
taskkill /F /IM python.exe  # WARNING: Kills all Python processes
```

### System Tray Not Showing

**Issue:** Tray icon doesn't appear  
**Solution:**
```bash
# Check tray manager is running
curl http://localhost:5000/system/background-status

# Refresh tray
python -c "from system_tray import SystemTrayManager; SystemTrayManager().refresh()"

# Check icon path
ls -la ./assets/icons/tray.ico
```

### High Memory Usage

**Issue:** Background mode using > 250MB  
**Solution:**
```bash
# Check memory usage
curl http://localhost:5000/system/background-status | jq '.data.memory_mb'

# Restart service
curl -X POST http://localhost:5000/system/restart-service

# Check for memory leaks (run 8-hour test)
python test_phase5_background.py -test memory_leak
```

### Auto-start Not Working

**Issue:** App doesn't launch on system startup  
**Solution:**
```bash
# Check registry
Get-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' | Select-Object ELIXI

# Enable auto-start
python -c "from auto_start_config import AutoStartConfiguration; AutoStartConfiguration().enable_auto_start()"

# Verify registry entry created
Get-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name ELIXI
```

### Floating Window Issues

**Issue:** Window appears off-screen  
**Solution:**
```javascript
// In floating-window.js
window.addEventListener('load', () => {
  const bounds = screen.getDisplayNearestToPoint({x: 0, y: 0});
  mainWindow.setBounds({
    x: bounds.x + 50,
    y: bounds.y + 50,
    width: 600,
    height: 500
  });
});
```

---

## Testing

### Unit Tests

```bash
# Run all Phase 5 tests
cd python-core
pytest test_phase5_background.py test_phase5_system.py -v

# Run specific test class
pytest test_phase5_background.py::TestBackgroundModeManager -v

# Run with coverage
pytest test_phase5_*.py --cov=. --cov-report=html
```

### Integration Tests

```bash
# 1. Start background service
curl -X POST http://localhost:5000/system/background-mode \
  -d '{"enabled": true}' -H "Content-Type: application/json"

# 2. Verify status
curl http://localhost:5000/system/background-status

# 3. Test hotkey wake (ALT+Shift+J)
# Manually press the hotkey combination

# 4. Check if woken up
curl http://localhost:5000/system/background-status | jq '.data.running'

# 5. Stop background mode
curl -X POST http://localhost:5000/system/background-mode \
  -d '{"enabled": false}' -H "Content-Type: application/json"
```

### Performance Tests

```bash
# Memory stability test (8 hours)
python test_phase5_background.py -test memory_leak -duration 8h

# CPU monitoring test (1 hour)
python test_phase5_background.py -test cpu_usage -duration 1h

# Response time benchmark
python test_phase5_background.py -test response_time -requests 1000

# Startup/shutdown timing
python test_phase5_background.py -test lifecycle_timing
```

### Manual Testing Checklist

- [ ] Floating window opens and is visible
- [ ] Window can be dragged to new position
- [ ] Window can be resized
- [ ] Right-click context menu appears
- [ ] Minimize button works
- [ ] Close button works
- [ ] Background mode starts without errors
- [ ] System tray icon visible
- [ ] Tray context menu functional
- [ ] Hotkey (ALT+Shift+J) brings window to focus
- [ ] Auto-start registry entry created
- [ ] Auto-start works after reboot
- [ ] Memory usage stable under 200MB
- [ ] CPU usage < 5% at idle
- [ ] All API endpoints responding

---

## Development Workflow

### Starting Development

```bash
# 1. Create feature branch
git checkout -b phase5-feature-name

# 2. Start development server
cd python-core
python main.py --mode floating --debug

# 3. In another terminal, run tests
pytest test_phase5_*.py -v --watch

# 4. In another terminal, monitor logs
tail -f logs/*.log
```

### Running Specific Tests

```bash
# Test floating window
node electron-app/test/floating-window.test.js

# Test background mode
pytest python-core/test_phase5_background.py -v

# Test system tray
pytest python-core/test_phase5_system.py::TestSystemTrayManager -v

# Test auto-start
pytest python-core/test_phase5_system.py::TestAutoStartConfiguration -v
```

### Debugging

```bash
# Enable debug logging
ELIXI_DEBUG=1 python main.py --mode floating

# Debug specific module
python -m pdb background_mode.py

# Electron DevTools
# Press Ctrl+Shift+I in floating window

# Python debugger
python -c "import pdb; pdb.run('import background_mode')"
```

---

## Performance Optimization Tips

### Reducing Memory Usage

1. **Lazy load modules**
   ```python
   # Bad
   import heavy_module
   
   # Good
   def some_function():
       import heavy_module  # Load only when needed
       return heavy_module.do_something()
   ```

2. **Use generators for large data**
   ```python
   # Bad
   data = [process_item(i) for i in range(1000000)]
   
   # Good
   def data_generator():
       for i in range(1000000):
           yield process_item(i)
   ```

3. **Clear caches periodically**
   ```python
   # In background_mode.py
   cache.clear_expired()  # Clear old cache entries
   ```

### Improving Response Times

1. **Use async operations**
   ```python
   import asyncio
   
   async def handle_request():
       result = await async_operation()
       return result
   ```

2. **Implement caching**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=128)
   def expensive_operation(param):
       return result
   ```

---

## Common Commands

| Task | Command |
|------|---------|
| Start normal mode | `python main.py` |
| Start floating mode | `python main.py --mode floating` |
| Start background mode | `python main.py --mode background` |
| Enable auto-start | `python setup_auto_start.py --enable` |
| Disable auto-start | `python setup_auto_start.py --disable` |
| View background logs | `tail -f logs/background.log` |
| Run all tests | `pytest test_phase5_*.py -v` |
| Memory check | `curl http://localhost:5000/system/background-status` |
| Restart service | `curl -X POST http://localhost:5000/system/restart-service` |

---

## Additional Resources

- [Floating Window Implementation Details](STAGE5_PHASE5_IMPLEMENTATION.md)
- [Background Mode Architecture](STAGE5_PHASE5_IMPLEMENTATION.md#2-background-mode-module-python)
- [System Tray Integration Guide](STAGE5_PHASE5_IMPLEMENTATION.md#3-system-tray-integration-win32native)

**For full technical details, see:** [STAGE5_PHASE5_IMPLEMENTATION.md](STAGE5_PHASE5_IMPLEMENTATION.md)

---

**Last Updated:** February 19, 2026  
**Version:** 1.0
