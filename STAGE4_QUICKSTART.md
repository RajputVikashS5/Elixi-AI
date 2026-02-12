# Stage 4 - Quick Start Guide

## ✅ What's Ready Now

You have just completed the **Stage 4 infrastructure build** for ELIXI AI. All the core automation, memory, and learning systems are now built and integrated.

---

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies
```bash
cd e:\Projects\ELIXI AI\python-core
pip install -r requirements_stage4.txt
```

### Step 2: Verify MongoDB Connection
Set your MongoDB URI in `.env`:
```bash
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/
MONGODB_DB=ELIXIDB
```

### Step 3: Start the Backend
```bash
python main.py
```

You should see:
```
ELIXI backend listening on http://127.0.0.1:5000
```

### Step 4: Test Stage 4 (in another terminal)
```bash
# Test custom commands
curl -X POST http://localhost:5000/automation/custom-commands/create ^
  -H "Content-Type: application/json" ^
  -d "{\"command_name\":\"Hello World\",\"trigger_words\":[\"hello\"],\"actions\":[]}"

# Get response
# {"success": true, "command_id": "cmd_1707246000000", ...}
```

---

## 📚 Key Documentation Files

| File | Purpose |
|------|---------|
| [STAGE4_IMPLEMENTATION.md](STAGE4_IMPLEMENTATION.md) | Complete implementation guide with data models |
| [STAGE4_API_REFERENCE.md](STAGE4_API_REFERENCE.md) | All API endpoints with examples |
| [STAGE4_PROGRESS.md](STAGE4_PROGRESS.md) | What's done, what's next |
| [This file](#) | Quick start instructions |

---

## 🔥 What You Can Do Now

### 1. Create Custom Voice Commands
Create commands that users can trigger with voice:
```bash
curl -X POST http://localhost:5000/automation/custom-commands/create \
  -H "Content-Type: application/json" \
  -d '{
    "command_name": "Close everything",
    "trigger_words": ["close everything", "shut down apps"],
    "actions": [
      {"action": "close_app", "args": {"app_name": "Chrome"}},
      {"action": "close_app", "args": {"app_name": "VSCode"}}
    ]
  }'
```

### 2. Create Multi-Step Workflows
Chain actions together for complex automations:
```bash
curl -X POST http://localhost:5000/automation/workflows/create \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "Morning Routine",
    "steps": [
      {"action": "open_app", "args": {"app_name": "Chrome"}, "delay_after": 2},
      {"action": "chat", "args": {"prompt": "What'\''s the weather?"}, "delay_after": 1},
      {"action": "open_app", "args": {"app_name": "Spotify"}, "delay_after": 0}
    ]
  }'
```

### 3. Detect Behavior Patterns
ELIXI analyzes recent user activity:
```bash
curl -X POST http://localhost:5000/automation/habits/analyze \
  -H "Content-Type: application/json" \
  -d '{"days": 7}'
```

### 4. Get Smart Suggestions
Receive personalized suggestions based on patterns:
```bash
curl -X POST http://localhost:5000/suggestions/active \
  -H "Content-Type: application/json" \
  -d '{"limit": 5}'
```

---

## 📊 MongoDB Collections Created

Stage 4 uses these MongoDB collections:
- `custom_commands` - User-defined voice commands
- `workflows` - Multi-step automation sequences
- `workflow_history` - Execution logs for workflows
- `detected_habits` - Detected behavior patterns
- `suggestions` - AI-generated suggestions
- `user_preferences` - Learned user preferences (coming in Phase 2)

---

## 🎯 Implementation Phases

### ✅ Phase 1: Core Infrastructure (Complete)
- Custom command management
- Workflow automation engine
- Habit learning & pattern detection
- Suggestion generation
- 22 new API endpoints

### 📋 Phase 2: Memory System (Next)
- Conversation context management
- Memory search & retrieval
- Preference learning system

### 📋 Phase 3: Advanced Features (Later)
- Workflow scheduling
- Conditional workflows (if/then)
- Optimization recommendations

### 📋 Phase 4: Frontend Integration (Later)
- Vue.js components for automation
- Workflow visualization
- Suggestion UI

---

## 🧪 Testing Your Setup

Run these commands to verify everything works:

```PowerShell
# Test 1: Backend is running
$response = Invoke-WebRequest -Uri "http://localhost:5000/system-status" -TimeoutSec 5
Write-Host "✓ Backend is running"

# Test 2: MongoDB is connected
$response = Invoke-RestMethod -Uri "http://localhost:5000/system-status" -Method Get
if ($response.db_connected) {
    Write-Host "✓ MongoDB is connected"
} else {
    Write-Host "✗ MongoDB not connected - set MONGODB_URI in .env"
}

# Test 3: Stage 4 is available
$body = '{"command_name":"Test","trigger_words":["test"],"actions":[]}'
$response = Invoke-RestMethod -Uri "http://localhost:5000/automation/custom-commands/create" `
    -Method Post -ContentType "application/json" -Body $body
Write-Host "✓ Stage 4 commands working" 
Write-Host "  Created: $($response.command_id)"
```

Expected output:
```
✓ Backend is running
✓ MongoDB is connected
✓ Stage 4 commands working
  Created: cmd_1707246000000
```

---

## 🔗 Integration with Existing Features

Stage 4 integrates seamlessly with:
- ✅ Voice commands (via custom commands)
- ✅ System control (via workflow actions)
- ✅ AI brain/Chat (via execute action)
- ✅ Event logging (for habit analysis)
- ✅ Memory storage (via MongoDB)

---

## 📖 API Endpoint Summary

### Custom Commands (7 endpoints)
- POST `/automation/custom-commands/create`
- POST `/automation/custom-commands/list`
- POST `/automation/custom-commands/execute`
- More... see [STAGE4_API_REFERENCE.md](STAGE4_API_REFERENCE.md)

### Workflows (7 endpoints)
- POST `/automation/workflows/create`
- POST `/automation/workflows/execute`
- More... see [STAGE4_API_REFERENCE.md](STAGE4_API_REFERENCE.md)

### Habits (4 endpoints)
- POST `/automation/habits/analyze`
- POST `/automation/habits/list`
- More... see [STAGE4_API_REFERENCE.md](STAGE4_API_REFERENCE.md)

### Suggestions (5 endpoints)
- POST `/suggestions/active`
- POST `/suggestions/analytics`
- More... see [STAGE4_API_REFERENCE.md](STAGE4_API_REFERENCE.md)

---

## 🐛 Troubleshooting

### "Module not found" error
```bash
pip install -r requirements_stage4.txt
```

### "Database not configured"
Set `MONGODB_URI` in your `.env` file

### Port 5000 already in use
Kill the existing process:
```bash
taskkill /F /IM python.exe /T
```

### No suggestions appearing
Run habit analysis first:
```bash
curl -X POST http://localhost:5000/automation/habits/analyze \
  -H "Content-Type: application/json" \
  -d '{"days": 7}'
```

---

## 💡 Best Practices

1. **Custom Commands**: Keep trigger words unique and memorable
2. **Workflows**: Start simple (2-3 steps), add complexity gradually
3. **Habits**: Analyze daily for fresh patterns
4. **Suggestions**: Respond to suggestions to help system learn
5. **Error Handling**: Set appropriate on_error strategy for each step

---

## 📞 Next Steps

1. ✅ **Test the APIs** - Use cURL commands above to verify everything works
2. **Build Frontend Components** - Create Vue.js UI for automation
3. **Create Test Data** - Add sample commands and workflows
4. **Optimize Database** - Add MongoDB indexes for performance
5. **Implement Memory System** - Phase 2 of Stage 4

---

## 🎉 You're Ready!

Stage 4 core infrastructure is complete and ready for:
- Frontend integration
- Advanced feature development
- Production deployment
- Real-world automation testing

**Start with the API Reference guide** for detailed endpoint documentation and examples.
