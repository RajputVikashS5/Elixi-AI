# ELIXI AI - Quick Reference Guide

> **📖 For the complete project roadmap and vision, see [STARTUP_ROADMAP.md](STARTUP_ROADMAP.md)**

---

## 🚀 Quick Start

### Backend (Python)
```bash
cd python-core
python main.py
# Server: http://localhost:5000
```

### Frontend (Electron)
```bash
cd electron-app
npm install          # First time only
npm run dev         # Development
npm run build:win   # Build Windows app
```

### Verify Setup
```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Check Python backend
curl http://localhost:5000/system-status

# Test chat
curl -X POST http://localhost:5000/execute \
  -H "Content-Type: application/json" \
  -d '{"command":"chat","args":{"prompt":"Hello"}}'
```

---

## 📋 Environment Variables

Save this as `.env` in `python-core/` directory:

```bash
# Database
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DB=ELIXIDB
MONGODB_COLLECTION_MEMORIES=memories
MONGODB_COLLECTION_EVENTS=events

# Text-to-Speech (Required)
ELEVENLABS_API_KEY=your_api_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
ELEVENLABS_MODEL_ID=eleven_turbo_v2_5

# AI Brain (Required)
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# Voice Detection
WAKE_WORD=hey elixi
WAKE_WORD_SENSITIVITY=0.5

# Google Cloud (Optional)
GOOGLE_APPLICATION_CREDENTIALS=
GOOGLE_CLOUD_PROJECT=
```

---

## 🔌 API Quick Reference

### `/system-status` (GET)
```bash
curl http://localhost:5000/system-status
```
Response:
```json
{
  "success": true,
  "platform": "Windows-10...",
  "python_version": "3.11.4",
  "uptime_sec": 3600,
  "db_connected": true
}
```

### `/memory/load` (GET)
```bash
curl http://localhost:5000/memory/load
```
Returns last 100 stored memories.

### `/execute` (POST)
**Chat command**:
```bash
curl -X POST http://localhost:5000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "chat",
    "args": {"prompt": "What time is it?"}
  }'
```

Response:
```json
{
  "success": true,
  "reply": "I don't have real-time information, but..."
}
```

### `/memory/save` (POST)
```bash
curl -X POST http://localhost:5000/memory/save \
  -H "Content-Type: application/json" \
  -d '{"note": "User prefers coffee", "type": "preference"}'
```

---

## 🧠 AI Brain (Ollama)

### Installation & Setup
```bash
# Windows: Download from https://ollama.ai
# Run: just double-click ollama installer
# Then in terminal:
ollama pull mistral  # Download model

# To run:
ollama serve  # Starts on http://localhost:11434
```

### Check Status
```bash
# List installed models
curl http://localhost:11434/api/tags

# Output:
# {
#   "models": [
#     {"name": "mistral:latest", ...}
#   ]
# }
```

### Generate Response (Manual Test)
```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral",
    "prompt": "What time is it?",
    "stream": false
  }'
```

---

## 🎤 Voice System

### Wake Word Detection
Located in: `python-core/voice_system/wake_word.py`

```python
from voice_system.wake_word import WakeWordDetector

detector = WakeWordDetector()

# Check if wake word is in text
is_wake = detector.detect("Hey elixi, what time is it?")  # True

# Extract command after wake word
cmd = detector.extract_command("Hey elixi, what time is it?")
# Returns: "what time is it?"
```

### ElevenLabs TTS
Located in: `python-core/voice_system/elevenlabs_voice.py`

```python
from voice_system.elevenlabs_voice import ElevenLabsVoice

voice = ElevenLabsVoice()

# Check configuration
if voice.is_configured():
    # Convert text to speech
    audio_base64 = voice.text_to_speech("Hello, I'm ELIXI")
    # Returns: base64-encoded MP3
```

**Available Voices**:
- 21m00Tcm4TlvDq8ikWAM - Rachel (default)
- Get more from: https://api.elevenlabs.io/docs

---

## 🗄️ Database (MongoDB)

### View Data via MongoDB Atlas
1. Go to: https://www.mongodb.com/cloud/atlas
2. Login with your credentials
3. Browse collections in ELIXIDB

### Command Line Access
```bash
# Install mongosh: https://www.mongodb.com/try/download/shell

# Connect
mongosh "your_mongodb_uri_here"

# Switch to database
use ELIXIDB

# View collections
show collections

# Query memories
db.memories.find().limit(10)

# Query events
db.events.find({type: "chat"}).limit(5)

# Clear old events (careful!)
db.events.deleteMany({timestamp: {$lt: Date.now() - 30*24*60*60*1000}})
```

---

## 🖥️ Frontend Development

### Electron Project Structure
```
electron-app/
├── src/
│   ├── main/main.js           # Main process
│   ├── preload/preload.js     # Security bridge
│   └── renderer/
│       ├── index.html         # UI
│       ├── js/renderer.js     # Client logic
│       └── styles/main.css    # CSS
├── package.json
└── node_modules/
```

### Useful npm Commands
```bash
npm run dev         # Run with developer tools
npm run start       # Run production build
npm run build       # Create installer
npm run pack        # Dry-run build
npm install         # Install dependencies
npm audit fix       # Fix security issues
```

### Debugging
- Press `F12` to open DevTools in dev mode
- Console errors show in terminal
- View network requests in Network tab
- Check local storage via Application tab

### Key UI Elements (HTML IDs)
- `#chatFeed` - Message display area
- `#userInput` - Text input field
- `#sendButton` - Send button
- `#micButton` - Microphone button
- `#statusPill` - Status indicator

---

## 🧪 Testing

### Test Files
```bash
cd python-core

# Full test suite
python test_suite.py

# Database connectivity
python test_db.py

# ElevenLabs TTS
python test_elevenlabs.py
```

### Manual Testing
```bash
# Start backend
python main.py

# In another terminal, test endpoint
curl http://localhost:5000/system-status

# Test chat
curl -X POST http://localhost:5000/execute \
  -H "Content-Type: application/json" \
  -d '{"command":"chat","args":{"prompt":"hello"}}'
```

---

## ⚙️ Configuration Examples

### Change Wake Word
Edit `.env`:
```bash
WAKE_WORD=hello assistent
WAKE_WORD_SENSITIVITY=0.6  # More strict (0.9) or loose (0.3)
```

### Change AI Model
Edit `.env`:
```bash
OLLAMA_MODEL=neural-chat  # or other Ollama models
```

### Pull Additional Models
```bash
ollama pull llama2
ollama pull neural-chat
ollama pull orca-mini

# Use in .env
OLLAMA_MODEL=llama2
```

### Change Voice Character
Edit `.env`:
```bash
ELEVENLABS_VOICE_ID=EXAVITQu4vr4xnSDxMaL  # Different voice
```

Get more voices at: https://elevenlabs.io/docs/voice-library

---

## 🐛 Troubleshooting

### Python Backend Issues
```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip list | grep -E "pymongo|requests|elevenlabs|dotenv"

# Full import check
python -c "import pymongo; import requests; import elevenlabs; print('OK')"

# Test with debug
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('MONGODB_URI:', )
print('OLLAMA_API_URL:', os.getenv('OLLAMA_API_URL'))
"
```

### Ollama Won't Start
```bash
# Check if running
curl http://localhost:11434/api/tags

# Restart
# Kill existing processes
tasklist | findstr ollama
taskkill /IM ollama.exe

# Start fresh
ollama serve
```

### Electron App Issues
```bash
# Clear cache and reinstall
rm -r electron-app/node_modules
rm electron-app/package-lock.json
npm install

# If still issues, update Electron
npm update electron
```

### MongoDB Connection Failed
```bash
# Test connection string
mongosh "your_uri_here"

# Common issues:
# 1. IP whitelist - add your IP in MongoDB Atlas
# 2. Wrong username/password
# 3. Network blocked - check firewall
# 4. Cluster paused - resume in MongoDB Atlas
```

---

## 📊 Performance Tuning

### Reduce Ollama Response Time
```bash
# Use faster model
ollama pull orca-mini  # Faster than mistral

# In .env
OLLAMA_MODEL=orca-mini
```

### Reduce TTS Latency
```bash
# Use turbo model (already default)
ELEVENLABS_MODEL_ID=eleven_turbo_v2_5
```

### Database Optimization
```bash
# In MongoDB Atlas:
# 1. Create index on collections:
db.memories.createIndex({"timestamp": -1})
db.events.createIndex({"type": 1, "timestamp": -1})

# 2. Enable connection pooling (done automatically)
# 3. Set write concern: majority
```

---

## 📚 Key File Reference

| File | Purpose |
|------|---------|
| `main.py` | HTTP server, request handling |
| `ollama.py` | AI brain integration |
| `elevenlabs_voice.py` | Text-to-speech |
| `wake_word.py` | Wake word detection |
| `renderer.js` | Frontend UI logic |
| `index.html` | UI structure |
| `.env` | Configuration |

---

## 🔐 Security Notes

⚠️ **Before Production**:
- [ ] Generate new API keys (current ones exposed)
- [ ] Add request authentication
- [ ] Use HTTPS/TLS
- [ ] Validate all inputs
- [ ] Rate limit API endpoints
- [ ] Add user authentication
- [ ] Encrypt sensitive data at rest
- [ ] Use private MongoDB instance
- [ ] Remove credentials from code

---

## 📞 Support

**Quick Fixes**:
1. Restart Python backend: `Ctrl+C` then `python main.py`
2. Restart Ollama: Kill process and `ollama serve`
3. Restart Electron: Close and `npm run dev`
4. Check `.env` file is in `python-core/` directory
5. Verify all services running on correct ports

**Debug Mode**:
```bash
# Run backend with logging
python -u main.py  # Flush output immediately

# Run Electron with DevTools open
npm run dev
# Then File → DevTools or F12
```

---

## 🎯 Next Steps

1. ✅ Get Ollama running locally
2. ✅ Set up MongoDB Atlas account
3. ✅ Get ElevenLabs API key
4. ✅ Configure `.env` file
5. ✅ Start backend: `python main.py`
6. ✅ Start frontend: `npm run dev`
7. ✅ Test in browser: Open http://localhost:5000/system-status
8. ✅ Test chat in UI: Click in input and type message
9. ✅ Test voice: Click microphone button

Happy coding! 🚀
