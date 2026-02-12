# ELIXI AI - Developer's Implementation Guide

## 1. Adding New Voice Services

### Example: Adding a New TTS Service

**File**: `python-core/voice_system/new_tts_service.py`

```python
import os
from typing import Optional

class NewTTSService:
    """Integration with custom TTS service."""
    
    def __init__(self):
        """Initialize with API credentials."""
        self.api_key = os.getenv("NEW_TTS_API_KEY")
        self.api_url = os.getenv("NEW_TTS_API_URL", "https://api.example.com")
        self.model = os.getenv("NEW_TTS_MODEL", "model-v1")
        self.timeout = 30
        
        self.is_ready = self.api_key is not None
        if not self.is_ready:
            print("[Warning] NewTTSService not configured")
    
    def is_configured(self) -> bool:
        """Check if service is properly configured."""
        return self.is_ready and self.api_key is not None
    
    def text_to_speech(self, text: str, voice_id: str = None) -> Optional[str]:
        """
        Convert text to speech.
        
        Args:
            text: Text to convert
            voice_id: Optional voice identifier
            
        Returns:
            Base64-encoded audio data or None on error
        """
        if not self.is_configured():
            print("[Error] NewTTSService not configured")
            return None
        
        if not text or len(text) == 0:
            return None
        
        try:
            import requests
            import base64
            
            # Make API request
            response = requests.post(
                f"{self.api_url}/synthesize",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "text": text,
                    "model": self.model,
                    "voice": voice_id or "default"
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                audio_bytes = response.content
                return base64.b64encode(audio_bytes).decode("utf-8")
            else:
                print(f"[Error] API returned {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[Error] TTS generation failed: {e}")
            return None
    
    def get_available_voices(self) -> list:
        """Get list of available voices."""
        try:
            import requests
            response = requests.get(
                f"{self.api_url}/voices",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=5
            )
            if response.status_code == 200:
                return response.json().get("voices", [])
        except Exception as e:
            print(f"[Warning] Could not fetch voices: {e}")
        return []
```

### Integration in main.py

**Step 1**: Add import and global
```python
from voice_system.new_tts_service import NewTTSService

_new_tts_service = None
```

**Step 2**: Add getter function
```python
def get_new_tts_service():
    global _new_tts_service
    if _new_tts_service is None:
        _new_tts_service = NewTTSService()
    return _new_tts_service
```

**Step 3**: Create API endpoint (optional)
```python
def do_POST(self):
    # ... existing code ...
    
    if self.path == "/voice/synthesize":
        payload = self._read_json()
        text = payload.get("text", "")
        
        # Try new service
        service = get_new_tts_service()
        if service.is_configured():
            audio = service.text_to_speech(text)
            if audio:
                self._send_json({"success": True, "audio": audio})
                return
        
        # Fallback to ElevenLabs
        elevenlabs = get_elevenlabs_voice()
        if elevenlabs.is_configured():
            audio = elevenlabs.text_to_speech(text)
            self._send_json({"success": True, "audio": audio})
        else:
            self._send_json(
                {"success": False, "error": "No TTS service available"},
                status=503
            )
        return
```

**Step 4**: Update .env
```bash
NEW_TTS_API_KEY=your_api_key_here
NEW_TTS_API_URL=https://api.example.com
NEW_TTS_MODEL=model-v1
```

---

## 2. Adding New AI Models

### Example: Adding LLaMA 2 Support

**File**: `python-core/ai_brain/llama2.py`

```python
import os
import requests
from typing import Optional

class Llama2Brain:
    """Local LLaMA 2 integration via Ollama."""
    
    def __init__(self):
        self.api_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
        self.model = "llama2"
        self.timeout = 60  # LLaMA can be slower
        self.context_window = 4096
        self.temperature = 0.7
    
    def is_available(self) -> bool:
        """Check if LLaMA 2 is available."""
        try:
            response = requests.get(
                f"{self.api_url}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(m.get("name", "").startswith("llama2") 
                          for m in models)
            return False
        except Exception as e:
            print(f"[Warning] LLaMA 2 check failed: {e}")
            return False
    
    def generate_reply(
        self,
        prompt: str,
        context: str = "",
        temperature: float = None
    ) -> Optional[str]:
        """Generate reply with LLaMA 2."""
        try:
            temp = temperature or self.temperature
            
            full_prompt = f"{context}\n\n{prompt}"
            
            response = requests.post(
                f"{self.api_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "temperature": temp,
                    "num_ctx": self.context_window
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            return None
            
        except Exception as e:
            print(f"[Error] LLaMA 2 generation failed: {e}")
            return None
    
    def set_temperature(self, temp: float):
        """Adjust model creativity (0.0-1.0)."""
        if 0.0 <= temp <= 1.0:
            self.temperature = temp
```

### Setup

```bash
# Install model
ollama pull llama2

# Update .env to use it
# OLLAMA_MODEL=llama2

# Or use in config
LLAMA2_MODEL_NAME=llama2
LLAMA2_CONTEXT_WINDOW=4096
LLAMA2_TEMPERATURE=0.7
```

---

## 3. Adding Custom Automation Commands

### Example: System Control Command

**File**: `python-core/automation/system_control.py`

```python
import os
import platform
import subprocess
from typing import Dict, Any

class SystemController:
    """Handle OS-level system commands."""
    
    def __init__(self):
        self.os_type = platform.system()  # "Windows", "Linux", "Darwin"
        self.available_commands = self._get_available_commands()
    
    def _get_available_commands(self) -> list:
        """Get list of safe commands."""
        commands = [
            "shutdown",
            "restart",
            "sleep",
            "volume",
            "brightness"
        ]
        return commands
    
    def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute system command safely.
        
        Args:
            command: Command name
            **kwargs: Command-specific arguments
            
        Returns:
            Result dictionary with status and output
        """
        if command not in self.available_commands:
            return {
                "success": False,
                "error": f"Unknown command: {command}"
            }
        
        if command == "shutdown":
            return self._shutdown(kwargs.get("delay", 0))
        elif command == "restart":
            return self._restart(kwargs.get("delay", 0))
        elif command == "sleep":
            return self._sleep()
        elif command == "volume":
            return self._set_volume(kwargs.get("level", 50))
        elif command == "brightness":
            return self._set_brightness(kwargs.get("level", 50))
    
    def _shutdown(self, delay: int = 0) -> Dict[str, Any]:
        """Shutdown system with optional delay."""
        try:
            if self.os_type == "Windows":
                cmd = f"shutdown /s /t {delay}"
            else:
                cmd = f"shutdown -h +{delay//60}"
            
            subprocess.run(cmd, shell=True, check=True)
            return {
                "success": True,
                "message": f"System shutdown in {delay} seconds"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _restart(self, delay: int = 0) -> Dict[str, Any]:
        """Restart system with optional delay."""
        try:
            if self.os_type == "Windows":
                cmd = f"shutdown /r /t {delay}"
            else:
                cmd = f"shutdown -r +{delay//60}"
            
            subprocess.run(cmd, shell=True, check=True)
            return {
                "success": True,
                "message": f"System restart in {delay} seconds"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _sleep(self) -> Dict[str, Any]:
        """Put system to sleep."""
        try:
            if self.os_type == "Windows":
                subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
                              shell=True, check=True)
            else:
                subprocess.run("pmset sleepnow", shell=True, check=True)
            
            return {"success": True, "message": "System sleeping"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _set_volume(self, level: int) -> Dict[str, Any]:
        """Set system volume level (0-100)."""
        level = max(0, min(100, level))
        try:
            if self.os_type == "Windows":
                # Using nircmd (download from nirsoft)
                cmd = f"nircmd.exe setsysvolume {int(level * 655.36)}"
                subprocess.run(cmd, shell=True)
            return {"success": True, "volume": level}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _set_brightness(self, level: int) -> Dict[str, Any]:
        """Set screen brightness (0-100)."""
        level = max(0, min(100, level))
        try:
            if self.os_type == "Windows":
                # Using WMI
                import ctypes
                cmd = f'powershell -Command "Get-WmiObject -Namespace \\"root\\cimv2\\" -Class WmiMonitorBrightnessMethods | foreach-object {{$_.WmiSetBrightness(1,{level})}}"'
                subprocess.run(cmd, shell=True)
            return {"success": True, "brightness": level}
        except Exception as e:
            return {"success": False, "error": str(e)}
```

### Integration in main.py

```python
from automation.system_control import SystemController

_system_controller = None

def get_system_controller():
    global _system_controller
    if _system_controller is None:
        _system_controller = SystemController()
    return _system_controller

# In do_POST
if self.path == "/execute":
    payload = self._read_json()
    command = payload.get("command")
    args = payload.get("args") or {}
    
    if command == "chat":
        # ... existing chat code ...
        pass
    
    elif command == "system":
        controller = get_system_controller()
        result = controller.execute(
            args.get("action"),
            **args.get("params", {})
        )
        self._send_json(result)
        return
```

---

## 4. Database Schema Management

### Creating Indexes for Performance

```python
# Add this to a database setup function
def setup_database_indexes():
    """Create indexes for optimal query performance."""
    db = get_db()
    
    if db is None:
        print("[Error] Database not connected")
        return
    
    try:
        # Memories collection
        memories = db[MONGODB_COLLECTION_MEMORIES]
        memories.create_index([("timestamp", -1)])
        
        # Events collection
        events = db[MONGODB_COLLECTION_EVENTS]
        events.create_index([("type", 1), ("timestamp", -1)])
        events.create_index([("timestamp", -1)])
        
        print("[Info] Database indexes created successfully")
    except PyMongoError as e:
        print(f"[Error] Index creation failed: {e}")
```

### Data Models (Schemas)

```python
# Suggested schemas for collections

# memories collection
memories_schema = {
    "timestamp": float,      # Unix timestamp
    "data": {
        "user_input": str,
        "ai_response": str,
        "context_tags": [str],
        "sentiment": str,    # "positive", "neutral", "negative"
        "user_id": str,      # For future multi-user support
        "session_id": str    # For grouping conversations
    }
}

# events collection
events_schema = {
    "timestamp": float,
    "type": str,            # "chat", "wake_word", "voice_input", etc.
    "prompt": str,
    "reply": str,
    "metadata": {
        "response_time_ms": int,
        "model_used": str,
        "confidence": float
    }
}

# users collection (future)
users_schema = {
    "_id": str,             # Username or UUID
    "created_at": float,
    "preferences": {
        "voice_id": str,
        "language": str,
        "wake_word": str
    },
    "settings": {
        "auto_archive_after_days": int,
        "max_memories": int
    }
}
```

---

## 5. Frontend Component Extension

### Adding New Chat Commands

**File**: `electron-app/src/renderer/js/commands.js`

```javascript
/**
 * Command handlers for ELIXI actions
 */

const commands = {
  // Execute chat command
  chat: async (input) => {
    try {
      const response = await window.elixi.sendCommand('chat', {
        prompt: input
      });
      return response;
    } catch (error) {
      console.error('Chat command error:', error);
      return { success: false, error: error.message };
    }
  },
  
  // Execute system command
  system: async (action, params = {}) => {
    try {
      const response = await window.elixi.sendCommand('system', {
        action,
        params
      });
      return response;
    } catch (error) {
      console.error('System command error:', error);
      return { success: false, error: error.message };
    }
  },
  
  // Control lights example
  lights: async (action, params = {}) => {
    return await commands.system('lights', { action, ...params });
  },
  
  // Get weather (future integration)
  weather: async (location = 'current') => {
    try {
      const response = await fetch('http://localhost:5000/weather', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ location })
      });
      return await response.json();
    } catch (error) {
      return { success: false, error: error.message };
    }
  }
};

export default commands;
```

### Adding New UI Components

```javascript
/**
 * Add custom UI component
 */

class NotificationBubble {
  constructor(message, type = 'info', duration = 3000) {
    this.message = message;
    this.type = type;  // 'info', 'success', 'warning', 'error'
    this.duration = duration;
    this.element = null;
  }
  
  show() {
    // Create bubble element
    this.element = document.createElement('div');
    this.element.className = `notification notification-${this.type}`;
    this.element.textContent = this.message;
    
    // Add to page
    document.body.appendChild(this.element);
    
    // Auto-remove
    if (this.duration > 0) {
      setTimeout(() => this.hide(), this.duration);
    }
  }
  
  hide() {
    if (this.element && this.element.parentNode) {
      this.element.parentNode.removeChild(this.element);
    }
  }
}

// Usage
const notif = new NotificationBubble('Command executed!', 'success', 2000);
notif.show();
```

---

## 6. Adding a New API Endpoint

### Complete Example: Get Weather

**Backend** (`main.py`):

```python
def do_GET(self):
    # ... existing code ...
    
    if self.path == "/weather":
        # Get current weather simulation
        self._send_json({
            "success": True,
            "temperature": 72,
            "condition": "sunny",
            "humidity": 65
        })
        return

def do_POST(self):
    # ... existing code ...
    
    if self.path == "/weather":
        payload = self._read_json()
        location = payload.get("location", "current")
        
        # In real scenario, call weather API
        # For now: return mock data
        self._send_json({
            "success": True,
            "location": location,
            "temperature": 72,
            "condition": "sunny",
            "forecast": [
                {"day": "Tomorrow", "high": 75, "low": 62},
                {"day": "Friday", "high": 78, "low": 65}
            ]
        })
        return
```

**Frontend** (`renderer.js`):

```javascript
const getWeather = async (location = 'current') => {
  try {
    const response = await fetch('http://localhost:5000/weather', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ location })
    });
    
    const data = await response.json();
    
    if (data.success) {
      const message = `Weather in ${data.location}: ${data.temperature}°F and ${data.condition}`;
      addMessage('assistant', message);
    } else {
      addMessage('assistant', 'Could not fetch weather information');
    }
  } catch (error) {
    console.error('Weather request failed:', error);
  }
};

// Hook into command parsing
if (userPrompt.includes('weather')) {
  await getWeather();
}
```

---

## 7. Testing Your Extensions

### Unit Test Template

```python
# python-core/test_new_feature.py

import unittest
from unittest.mock import patch, MagicMock
from voice_system.new_tts_service import NewTTSService

class TestNewTTSService(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = NewTTSService()
    
    def test_initialization(self):
        """Test service initializes correctly."""
        self.assertIsNotNone(self.service)
        self.assertEqual(self.service.model, "model-v1")
    
    def test_is_configured_without_key(self):
        """Test returns False when API key missing."""
        with patch.dict('os.environ', {'NEW_TTS_API_KEY': ''}):
            service = NewTTSService()
            self.assertFalse(service.is_configured())
    
    @patch('requests.post')
    def test_text_to_speech_success(self, mock_post):
        """Test successful TTS conversion."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'audio_data'
        mock_post.return_value = mock_response
        
        # Set API key
        with patch.dict('os.environ', {'NEW_TTS_API_KEY': 'test_key'}):
            service = NewTTSService()
            result = service.text_to_speech("Hello")
            
            self.assertIsNotNone(result)
            self.assertTrue(result.startswith('YXVkaW8'))  # base64 "audio"
    
    @patch('requests.post')
    def test_text_to_speech_failure(self, mock_post):
        """Test TTS failure handling."""
        mock_post.side_effect = Exception("API down")
        
        with patch.dict('os.environ', {'NEW_TTS_API_KEY': 'test_key'}):
            service = NewTTSService()
            result = service.text_to_speech("Hello")
            
            self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
```

### Integration Test

```bash
# Test your new endpoint
curl -X POST http://localhost:5000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "system",
    "args": {
      "action": "brightness",
      "params": {"level": 75}
    }
  }'
```

---

## 8. Debugging Guide

### Python Debugging

```python
# Add to main.py for detailed logging
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('elixi_debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Use in your code
logger.debug("User input: %s", prompt)
logger.info("Generated reply: %s", reply)
logger.error("API error: %s", error)
```

### Frontend Debugging

```javascript
// Add debugging utilities
const DEBUG = true;

const log = (level, message, data = null) => {
  if (DEBUG) {
    const timestamp = new Date().toLocaleTimeString();
    console.log(`[${timestamp}] ${level}: ${message}`, data || '');
  }
};

// Usage
log('DEBUG', 'User sent prompt', prompt);
log('INFO', 'Received response', response);
log('ERROR', 'API request failed', error);
```

### Database Debugging

```python
# Quick MongoDB inspection
def inspect_db():
    """Print database stats."""
    db = get_db()
    collections = db.list_collection_names()
    
    print("Database: ELIXIDB")
    for coll_name in collections:
        coll = db[coll_name]
        count = coll.count_documents({})
        print(f"  {coll_name}: {count} documents")
        
        # Show recent entries
        recent = coll.find_one(sort=[("timestamp", -1)])
        if recent:
            print(f"    Latest: {recent.get('timestamp', 'N/A')}")
```

---

## 9. Performance Optimization Tips

### Caching Responses

```python
from functools import lru_cache
from time import time

class CachedOllamaBrain:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def generate_reply(self, prompt, use_cache=True):
        """Generate reply with optional caching."""
        cache_key = hash(prompt)
        
        if use_cache and cache_key in self.cache:
            cached_result, timestamp = self.cache[cache_key]
            if time() - timestamp < self.cache_ttl:
                return cached_result
        
        # Generate new response
        result = self._call_api(prompt)
        
        # Cache it
        self.cache[cache_key] = (result, time())
        
        return result
    
    def _call_api(self, prompt):
        # Actual API call
        pass
```

### Connection Pooling

```python
from pymongo import MongoClient
from pymongo.errors import PyMongoError

class DatabasePool:
    def __init__(self, uri, max_pool_size=50):
        self.client = MongoClient(
            uri,
            maxPoolSize=max_pool_size,
            minPoolSize=10,
            maxIdleTimeMS=45000
        )
    
    def get_db(self):
        return self.client['ELIXIDB']
```

---

## 10. Deployment Checklist

Before going to production:

- [ ] Remove debug logging
- [ ] Rotate API keys
- [ ] Add input validation
- [ ] Implement rate limiting
- [ ] Add authentication
- [ ] Enable HTTPS
- [ ] Set up monitoring/alerts
- [ ] Database backups enabled
- [ ] Error tracking (Sentry, etc.)
- [ ] Performance testing
- [ ] Load testing
- [ ] Security audit
- [ ] Documentation complete
- [ ] User acceptance testing

---

Good luck with your ELIXI extensions! 🚀
