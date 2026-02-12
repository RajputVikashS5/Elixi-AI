# ELIXI AI Assistant - Complete Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Backend System (Python)](#backend-system-python)
4. [Frontend Application (Electron)](#frontend-application-electron)
5. [Voice System](#voice-system)
6. [AI Brain (Ollama Integration)](#ai-brain-ollama-integration)
7. [Database Management](#database-management)
8. [API Endpoints](#api-endpoints)
9. [Configuration & Environment](#configuration--environment)
10. [Setup & Installation](#setup--installation)
11. [Development Guide](#development-guide)

---

## Project Overview

**ELIXI** is a Jarvis-like personal AI system assistant that combines:
- Local offline AI capabilities via Ollama
- Advanced voice processing with ElevenLabs TTS and Google Cloud Speech-to-Text
- Cross-platform desktop application (Electron)
- MongoDB for memory and event storage
- Wake word detection for hands-free interaction

### Key Features
- 🎤 **Voice Interface**: Microphone input with wake word detection
- 🧠 **Local AI Brain**: Runs Ollama (Mistral model) for intelligent responses
- 🔊 **Premium Text-to-Speech**: ElevenLabs integration for natural voice output
- 💾 **Persistent Memory**: MongoDB stores conversation memories and events
- 🖥️ **Cross-Platform UI**: Electron-based desktop application
- ⚡ **Modular Architecture**: Independently manageable components

---

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    ELIXI AI Assistant                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │   Frontend (Electron)                                │  │
│  │   - index.html (UI Structure)                        │  │
│  │   - renderer.js (Client Logic)                       │  │
│  │   - main.css (Styling)                               │  │
│  └──────────────────────────────────────────────────────┘  │
│           ↓ HTTP/IPC Communication ↓                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │   Backend HTTP Server (Python - main.py)            │  │
│  │   - Port: 5000                                       │  │
│  │   - REST API Endpoints                               │  │
│  │   - Request Handler Classes                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                ↓        ↓        ↓        ↓                 │
│  ┌───────────┴────────┬────────┬────────┬──────────────┐  │
│  │                    │        │        │              │  │
│  ▼                    ▼        ▼        ▼              ▼  │
│ Voice System      AI Brain   Database  Memory          │  │
│ ├─ Wake Word      ├─ Ollama  ├─Query  └─ Management   │  │
│ ├─ Google Cloud   └─ Prompt  └─Store                  │  │
│ └─ ElevenLabs        Engine                            │  │
│                                                         │  │
│  External Services:                                    │  │
│  - MongoDB Atlas (Cloud)                              │  │
│  - ElevenLabs API (TTS)                               │  │
│  - Ollama Local (AI)                                  │  │
│  - Google Cloud (Optional STT)                        │  │
└─────────────────────────────────────────────────────────────┘
```

### Component Hierarchy
- **Electron App** (UI Layer)
  - renderer.js: Client-side logic
  - index.html: UI structure
  - main.css: Styling
  
- **Python Backend** (Business Logic Layer)
  - main.py: HTTP server & request handling
  - voice_system/: Voice processing modules
  - ai_brain/: AI integration
  - automation/: Future automation engine
  - system_control/: System control modules

- **External Services** (Integration Layer)
  - MongoDB: Memory & event storage
  - ElevenLabs: Text-to-speech
  - Ollama: Local AI inference
  - Google Cloud: Optional voice services

---

## Backend System (Python)

### Main Server (`main.py`)

The backend is an HTTP server written in Python that handles all business logic.

#### Key Components

**1. Global Module Initialization**
```python
MONGODB_URI = os.environ.get("MONGODB_URI")
MONGODB_DB = os.environ.get("MONGODB_DB", "ELIXIDB")
MONGODB_COLLECTION_MEMORIES = os.environ.get("MONGODB_COLLECTION_MEMORIES", "memories")
MONGODB_COLLECTION_EVENTS = os.environ.get("MONGODB_COLLECTION_EVENTS", "events")

# Lazy-loaded singletons
_mongo_client = None
_wake_word_detector = None
_google_voice = None
_elevenlabs_voice = None
_ollama_brain = None
```

The server uses lazy initialization for all modules to reduce startup time and memory footprint.

**2. Database Connection Management**

```python
def get_db():
    """Lazy-initialize MongoDB connection"""
    global _mongo_client
    if not MONGODB_URI:
        return None
    if _mongo_client is None:
        _mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
    return _mongo_client[MONGODB_DB]

def get_collection(name):
    """Retrieve a specific collection from the database"""
    db = get_db()
    if db is None:
        return None
    return db[name]
```

**3. Module Getter Functions**

Similar getters exist for all major components:
- `get_wake_word_detector()`: Wake word detection module
- `get_google_voice()`: Google Cloud voice service
- `get_elevenlabs_voice()`: ElevenLabs TTS service
- `get_ollama_brain()`: Ollama AI model

**4. Reply Generation Engine**

```python
def generate_reply(prompt):
    """
    Generate a reply using AI brain or fallback rules.
    
    Process:
    1. Try Ollama (local AI) first if available
    2. Fall back to rule-based responses
    3. Return helpful assistant responses
    """
```

The `generate_reply()` function implements a fallback system:
- Primary: Ollama AI-generated responses
- Secondary: Rule-based pattern matching for common queries

#### HTTP Request Handler Class

**`ElixiHandler(BaseHTTPRequestHandler)`**

Extends Python's HTTP request handler to process client requests.

##### GET Endpoints

**`GET /system-status`**
Returns system information and health status:
- Platform information
- Python version
- Uptime (seconds)
- MongoDB connection status
- Response format: `{"success": bool, "platform": str, "python_version": str, "uptime_sec": int, "db_connected": bool}`

**`GET /memory/load`**
Retrieves the last 100 memory entries from MongoDB (sorted by newest first):
- Returns: `{"success": bool, "items": [...]}`
- Error handling: Returns 500 if MongoDB not configured

##### POST Endpoints

**`POST /execute`**
Executes commands with flexible argument passing:

Supported commands:
- `command: "chat"` - Process user input and generate response
  - Required args: `prompt` (string)
  - Returns: `{"success": bool, "reply": str}`
  - Side effect: Logs to events collection

- Other commands queue for future automation engine

**`POST /memory/save`**
Stores data in the memories collection:
- Automatically timestamps entries
- Returns: `{"success": bool}`
- Error handling: 500 if MongoDB not configured

#### Helper Methods

```python
def _send_json(self, payload, status=200)
```
Sends JSON response with proper headers and encoding.

```python
def _read_json(self)
```
Reads and parses JSON from request body with error handling.

---

## Voice System

### Wake Word Detection (`voice_system/wake_word.py`)

```python
class WakeWordDetector:
    """Simple wake word detector using text matching."""
```

**Initialization**
```python
def __init__(self):
    self.wake_word = os.getenv("WAKE_WORD", "hey elixi").lower()
    self.sensitivity = float(os.getenv("WAKE_WORD_SENSITIVITY", "0.7"))
```

**Main Methods**

1. **`detect(text: str) -> bool`**
   - Detects if text contains the wake word
   - Uses fuzzy string matching (SequenceMatcher)
   - Cleaning: removes punctuation before matching
   - Returns True if similarity ratio >= sensitivity threshold

   Example:
   ```python
   detector = WakeWordDetector()
   is_wake = detector.detect("Hey elixi, what time is it?")  # True
   ```

2. **`extract_command(text: str) -> str`**
   - Extracts the actual command from text after wake word
   - Returns text following the wake word
   - If no wake word found, returns original text

   Example:
   ```python
   command = detector.extract_command("Hey elixi, what time is it?")
   # Returns: "what time is it?"
   ```

### ElevenLabs Voice Integration (`voice_system/elevenlabs_voice.py`)

```python
class ElevenLabsVoice:
    """ElevenLabs Speech-to-Text and Text-to-Speech integration."""
```

**Configuration**
- API Key: Read from `ELEVENLABS_API_KEY` environment variable
- Voice ID: Configurable, default is "Rachel" voice (21m00Tcm4TlvDq8ikWAM)
- Model ID: Default is "eleven_turbo_v2_5" (latest high-quality model)

**Main Methods**

1. **`is_configured() -> bool`**
   - Checks if ElevenLabs client is properly initialized
   - Returns False if API key missing or client initialization failed

2. **`text_to_speech(text: str, voice_id=None, model_id=None) -> str`**
   - Converts text to speech using ElevenLabs API
   - Returns Base64-encoded MP3 audio data
   - Supports voice customization via parameters
   
   Voice settings applied:
   - Stability: 0.5 (balanced between naturalness and consistency)
   - Similarity Boost: 0.7 (high similarity to voice sample)
   - Speaker Boost: True (enhanced speaker clarity)

   Example:
   ```python
   voice = ElevenLabsVoice()
   audio_b64 = voice.text_to_speech("Hello, I'm ELIXI")
   # Returns: "SUQzBAAAI1IVQVNFADAwMDAwMDAwMDAwMDAw..." (base64 MP3)
   ```

### Google Cloud Voice (`voice_system/google_cloud.py`)
*Optional speech-to-text service. ElevenLabs is preferred for TTS.*

---

## AI Brain (Ollama Integration)

### Ollama AI Brain (`ai_brain/ollama.py`)

```python
class OllamaAIBrain:
    """Ollama integration for offline AI brain."""
```

**Purpose**: Provides local, offline AI capabilities without external API dependencies.

**Initialization**
```python
def __init__(self):
    self.api_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
    self.model = os.getenv("OLLAMA_MODEL", "mistral")
    self.timeout = 30  # seconds
```

**Configuration**
- API URL: Local Ollama server (default: http://localhost:11434)
- Model: Mistral (60B context window, fast inference)
- Timeout: 30 seconds for response generation

**Main Methods**

1. **`is_available() -> bool`**
   - Checks if Ollama service is running
   - Verifies if configured model is loaded
   - Returns False gracefully if service unavailable (no error thrown)

   Process:
   1. Sends GET request to `/api/tags` endpoint
   2. Checks if response status is 200
   3. Verifies model name in available models list
   4. Returns False on any exception (network error, timeout, etc.)

2. **`generate_reply(prompt: str, context: str = "") -> Optional[str]`**
   - Generates text response from user input
   - Supports optional context (from memories)
   - Returns generated text or None on error

   Process:
   ```
   Input Format: "{context}\n\nUser: {prompt}\nAssistant:"
   ↓
   API Call: POST /api/generate
   ↓
   Output: "Assistant response text here..."
   ```

   Request parameters:
   - `model`: Configured model name (e.g., "mistral")
   - `prompt`: Full prompt with context
   - `stream`: False (return full response at once)
   - `temperature`: 0.7 (balanced creativity vs. consistency)

   Example:
   ```python
   ollama = OllamaAIBrain()
   if ollama.is_available():
       reply = ollama.generate_reply("What time is it?")
       # Returns: "I don't have real-time information, but..."
   ```

**Fallback Behavior**

If Ollama is unavailable or offline, the system in main.py handles fallback:
```python
def generate_reply(prompt):
    ollama = get_ollama_brain()
    if ollama.is_available():  # ← Falls through if False
        return ollama.generate_reply(prompt)
    
    # Rule-based replies
    text = prompt.lower()
    if "hello" in text:
        return "Hello. ELIXI is online and ready."
    # ... more patterns
```

---

## Database Management

### MongoDB Integration

**Setup**: MongoDB Atlas (Cloud)
- URI: `mongodb+srv://vikashrajput935843_db_user:password@cluster0.hctrhus.mongodb.net/`
- Database: `ELIXIDB`

**Collections**

1. **`memories`** - Persistent conversation history
   - Stores user inputs, responses, and context
   - Fields: `timestamp`, `data`
   - Usage: Loaded up to last 100 entries for context

2. **`events`** - System event log
   - Tracks all interactions and state changes
   - Fields: `timestamp`, `type`, `prompt`, `reply`
   - Event types: "chat" (and future types)

**Connection Management**

Lazy-loaded singleton pattern:
```python
_mongo_client = None  # Global connection cache

def get_db():
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
    return _mongo_client[MONGODB_DB]
```

Benefits:
- Single database connection reused
- Graceful fallback if MongoDB unavailable
- Timeout after 3 seconds if service unreachable

---

## Frontend Application (Electron)

### Application Structure

**Entry Points**
- Main: `electron-app/src/main/main.js` - Application initialization
- Preload: `electron-app/src/preload/preload.js` - Security bridge
- Renderer: `electron-app/src/renderer/js/renderer.js` - UI logic
- HTML: `electron-app/src/renderer/index.html` - UI structure
- Styles: `electron-app/src/renderer/styles/main.css` - Styling

### UI Components (`index.html`)

**1. Application Header**
```html
<header class="app-header">
  <div class="brand">ELIXI</div>
  <div class="status-pill" id="statusPill">Booting</div>
</header>
```
- Brand/title display
- Live status indicator (colors: ok, busy, warn, info)

**2. Chat Panel**
```html
<main class="chat-panel">
  <div class="chat-feed" id="chatFeed"></div>
</main>
```
- Message display area
- Auto-scrolls to latest message
- Shows both user inputs and ELIXI responses

**3. Input Panel**
```html
<footer class="input-panel">
  <button class="icon-button" id="micButton">🎤</button>
  <input id="userInput" placeholder="Ask ELIXI anything..." />
  <button class="send-button" id="sendButton">Send</button>
</footer>
```
- Microphone button for voice input
- Text input for direct typing
- Send button for manual submission

### Renderer Logic (`renderer.js`)

**Global State**
```javascript
let mediaRecorder = null;      // Audio recording device
let audioChunks = [];           // Accumulated audio chunks
let isListening = false;        // Listening state flag
let hasWoken = false;           // Wake word detection flag
```

**Core Functions**

1. **`addMessage(role, text)`**
   - Adds a message bubble to chat
   - Role: "user" or "assistant"
   - Auto-scrolls chat panel to bottom

2. **`setStatus(text, variant)`**
   - Updates status pill display
   - Variants: "ok", "busy", "warn", "info"
   - Provides visual feedback to user

3. **`sendChat()`**
   - Gets text from input field
   - Calls `/execute` endpoint with "chat" command
   - Displays response and updates status
   - Handles errors gracefully

   Process:
   ```
   User Input → addMessage('user') → POST /execute 
   ↓
   Response → addMessage('assistant') → setStatus('Ready')
   ```

4. **`toggleMic()`**
   - Switches between listening and stopped states
   - Entry point for voice input

5. **`startListening()`**
   - Requests microphone permission
   - Creates MediaRecorder for audio capture
   - Sets status to "Listening"
   - On stop: transcribes audio and checks for wake word

   Flow:
   ```
   Request Audio Permission
   ↓
   Create MediaRecorder
   ↓
   Collect audio chunks
   ↓
   On Stop: POST /voice/transcribe
   ↓
   Check for wake word
   ↓
   Process if command follows wake word
   ```

**Event Listeners**
- Send button: `click` → `sendChat()`
- Microphone button: `click` → `toggleMic()`
- User input: `keydown` (Enter) → `sendChat()`

---

## API Endpoints

### Base URL
**Development**: `http://localhost:5000`
**Production**: Configured via environment

### Endpoints Summary

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| GET | `/system-status` | System health check | ✅ Active |
| GET | `/memory/load` | Retrieve conversation history | ✅ Active |
| POST | `/execute` | Execute commands | ✅ Active |
| POST | `/memory/save` | Store memories | ✅ Active |
| POST | `/voice/transcribe` | Convert speech to text | 🔜 Planned |
| POST | `/voice/wake-word-check` | Detect wake word | 🔜 Planned |

### Detailed Endpoint Reference

#### `GET /system-status`
Returns system health and uptime information.

**Response** (200 OK):
```json
{
  "success": true,
  "platform": "Windows-10-10.0.19045-SP1",
  "python_version": "3.11.4",
  "uptime_sec": 3600,
  "db_connected": true
}
```

**Error Handling**: Always succeeds; `db_connected` indicates MongoDB status.

---

#### `GET /memory/load`
Retrieves stored memories/conversation history.

**Response** (200 OK):
```json
{
  "success": true,
  "items": [
    {
      "timestamp": 1707164000,
      "data": {
        "user_input": "What time is it?",
        "response": "Current time is..."
      }
    }
  ]
}
```

**Response** (500 Server Error):
```json
{
  "success": false,
  "error": "MongoDB not configured"
}
```

**Note**: Returns last 100 memories sorted by newest first.

---

#### `POST /execute`
Main command execution endpoint.

**Request Body** (chat command):
```json
{
  "command": "chat",
  "args": {
    "prompt": "What is the weather?"
  }
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "reply": "I don't have real-time weather data, but..."
}
```

**Side Effects**:
- Logs event to `events` collection with timestamp
- Event format: `{timestamp, type: "chat", prompt, reply}`

**Note**: Other commands queue for future automation engine.

---

#### `POST /memory/save`
Stores arbitrary data in memories collection.

**Request Body**:
```json
{
  "user_input": "Remember: I like coffee",
  "context": "user_preference"
}
```

**Response** (200 OK):
```json
{
  "success": true
}
```

**Server Action**: 
- Inserts into `memories` collection
- Auto-adds current timestamp
- Full document: `{timestamp: X, data: {...}}`

---

## Configuration & Environment

### Environment Variables (`.env`)

**MongoDB Configuration**
```bash
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/
MONGODB_DB=ELIXIDB
MONGODB_COLLECTION_MEMORIES=memories
MONGODB_COLLECTION_EVENTS=events
```

**Google Cloud (Optional)**
```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GOOGLE_CLOUD_PROJECT=your-project-id
```

**ElevenLabs Configuration**
```bash
ELEVENLABS_API_KEY=sk_36a6cf52ae7ef422b88d5b0ff522fef5735deffd015def82
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Rachel voice
ELEVENLABS_MODEL_ID=eleven_turbo_v2_5
```

**Ollama Configuration**
```bash
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

**Wake Word Configuration**
```bash
WAKE_WORD=hey elixi
WAKE_WORD_SENSITIVITY=0.5  # 0.0 to 1.0
```

### Sensitivity Tuning

**WAKE_WORD_SENSITIVITY**
- `0.5`: Very permissive (false positives more likely)
- `0.7`: Balanced (recommended)
- `0.9`: Very strict (may miss genuine wake words)

Uses fuzzy string matching (SequenceMatcher ratio).

---

## Setup & Installation

### Prerequisites
- Python 3.11+
- Node.js 16+ (for Electron)
- MongoDB Atlas account (or local MongoDB instance)
- Ollama installed and running locally
- ElevenLabs API key

### Backend Setup

**1. Install Python Dependencies**
```bash
cd python-core
pip install -r requirements.txt
```

Required packages:
- `pymongo` - MongoDB client
- `python-dotenv` - Environment variable loading
- `requests` - HTTP client for Ollama
- `elevenlabs` - ElevenLabs SDK
- `google-cloud-speech` - Google Cloud API (optional)

**2. Configure Environment**
```bash
# Copy and edit .env file
cp .env.example .env
# Edit with your actual credentials
nano .env
```

**3. Start Ollama Service**
```bash
# On Windows (assuming Ollama is installed)
ollama serve

# Or as background service
# Windows: Set Ollama as system service (installer option)
```

**4. Start Python Backend**
```bash
python main.py
# Server runs on http://localhost:5000
```

### Frontend Setup

**1. Install Dependencies**
```bash
cd electron-app
npm install
```

**2. Run Development**
```bash
npm run dev
# Runs Electron in development mode with hot reload
```

**3. Build for Production**
```bash
npm run build:win    # Windows executable
npm run build        # All platforms
```

### Verification

**1. Check Backend Health**
```bash
# Test system status endpoint
curl http://localhost:5000/system-status
```

**2. Check Ollama**
```bash
# Test Ollama availability
curl http://localhost:11434/api/tags
```

**3. Test Chat**
```bash
# Send a chat request
curl -X POST http://localhost:5000/execute \
  -H "Content-Type: application/json" \
  -d '{"command":"chat","args":{"prompt":"Hello"}}'
```

---

## Development Guide

### Project Structure

```
ELIXI AI/
├── python-core/                 # Backend
│   ├── main.py                  # HTTP server
│   ├── .env                      # Environment config
│   ├── ai_brain/                # AI modules
│   │   └── ollama.py            # Ollama integration
│   ├── voice_system/            # Voice processing
│   │   ├── wake_word.py         # Wake word detection
│   │   ├── elevenlabs_voice.py  # TTS service
│   │   └── google_cloud.py      # Optional STT
│   ├── automation/              # Future automation engine
│   └── system_control/          # OS control modules
│
├── electron-app/                # Frontend
│   ├── src/
│   │   ├── main/
│   │   │   └── main.js          # App initialization
│   │   ├── preload/
│   │   │   └── preload.js       # IPC bridge
│   │   └── renderer/
│   │       ├── index.html       # UI structure
│   │       ├── js/
│   │       │   └── renderer.js  # Client logic
│   │       └── styles/
│   │           └── main.css     # Styling
│   ├── package.json
│   └── node_modules/
│
├── database/                    # Database scripts
├── assets/                      # Images, fonts, icons
└── installer/                   # Build/installer configs
```

### Common Development Tasks

**Adding a New Voice Service**

1. Create module in `voice_system/new_service.py`:
```python
class NewVoiceService:
    def __init__(self):
        self.api_key = os.getenv("NEW_SERVICE_API_KEY")
    
    def text_to_speech(self, text):
        # Implementation
        pass
```

2. Add getter in `main.py`:
```python
_new_service = None

def get_new_service():
    global _new_service
    if _new_service is None:
        _new_service = NewVoiceService()
    return _new_service
```

3. Integrate into `generate_reply()` or create new endpoint.

**Adding a New API Endpoint**

1. Add method to `ElixiHandler`:
```python
def do_POST(self):
    if self.path == "/new-endpoint":
        payload = self._read_json()
        # Process request
        self._send_json({"success": True, "data": result})
```

2. Add corresponding frontend code in `renderer.js`:
```javascript
const response = await fetch('http://localhost:5000/new-endpoint', {
    method: 'POST',
    body: JSON.stringify(data)
});
```

**Testing Changes**

```bash
# Backend
python test_suite.py          # Run all tests
python test_db.py            # Database connectivity
python test_elevenlabs.py    # TTS service
python -m pytest             # If using pytest

# Frontend
npm run dev                   # Development server
npm run build                 # Build test
```

**Debugging**

**Backend**:
- Add print statements in `main.py`
- Enable request logging: `logging.basicConfig(level=logging.DEBUG)`
- MongoClient has built-in debugging

**Frontend**:
- DevTools: Press `F12` in Electron app
- Console logs automatically displayed
- Network tab shows HTTP requests

### Performance Tips

1. **Lazy Loading**: Use the getter functions pattern for expensive modules
2. **Connection Pooling**: MongoDB client reuses connection
3. **Timeout Configuration**: Adjust via environment variables
4. **Audio Optimization**: Reduce bitrate for faster transcription

### Security Considerations

⚠️ **Current State**: Development setup with exposed API keys
- Keep `.env` file secret (add to `.gitignore`)
- Use environment-specific configurations
- Implement request authentication before production
- Validate all inputs on backend
- Use HTTPS in production

### Future Enhancements

- [ ] Command scheduling and automation
- [ ] Advanced natural language understanding
- [ ] System control (lights, appliances)
- [ ] Calendar integration
- [ ] Email handling
- [ ] Web search capability
- [ ] Multi-language support
- [ ] User authentication
- [ ] Cloud sync for memories

---

## Troubleshooting

### Common Issues

**1. Ollama Not Connecting**
- Verify Ollama is running: `curl http://localhost:11434/api/tags`
- Check OLLAMA_API_URL in `.env`
- Ensure model is installed: `ollama list`

**2. MongoDB Connection Failed**
- Verify network access from your IP in MongoDB Atlas
- Check MONGODB_URI credentials
- Test connection: `mongosh "your_connection_string"`
- Verify database name: `ELIXIDB`

**3. ElevenLabs API Errors**
- Validate API key is correct
- Check rate limits (plans have per-minute limits)
- Verify voice ID exists
- Test with curl: 
  ```bash
  curl -X POST https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID} \
    -H "xi-api-key: $API_KEY" \
    -d "text=Hello"
  ```

**4. Electron App Won't Start**
- Delete `node_modules`: `rm -r node_modules`
- Reinstall: `npm install`
- Check Node version: `node --version` (should be 16+)
- Clear cache: `npm cache clean --force`

**5. Microphone Permission Denied**
- Check Windows privacy settings
- Restart Electron app
- Reset OS audio permissions
- Try running as administrator

---

## License & Credits

**License**: MIT
**Version**: 1.0.0
**Author**: ELIXI Team

### Technologies Used
- Python 3.11
- Electron 40.1
- MongoDB Atlas
- Ollama
- ElevenLabs API
- Google Cloud APIs (optional)

---

## Contact & Support

For issues, feature requests, or documentation updates:
- Check existing issues in repository
- Review logs: `python-core/logs/`
- Enable debug mode in environment

Last Updated: February 5, 2026
