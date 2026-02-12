# ELIXI AI - STAGE 4: AUTOMATION & MEMORY
## Implementation Plan & Tracking

**Date Started:** February 6, 2026  
**Status:** Planning & Implementation  
**Deliverable:** Full automation, custom commands, habit learning, and memory system

---

## 📋 Overview

Stage 4 transforms ELIXI from a reactive assistant into an intelligent, proactive system. Users can define custom voice commands, create automated workflows that handle multi-step processes, and ELIXI learns user habits to provide personalized suggestions.

---

## 🎯 Core Features to Implement

### 1. **Custom Command Creation** (`automation/custom_commands.py`)
Allow users to create and manage custom voice commands that execute system actions.

#### Requirements:
- API endpoint to create/update custom commands
- Command parsing with argument support  
- Intent matching for voice recognition
- Database storage in MongoDB (custom_commands collection)
- Ability to delete/list/edit commands

#### Data Model:
```json
{
  "_id": "...",
  "command_id": "custom_001",
  "command_name": "Close everything",
  "trigger_words": ["close everything", "shut down apps", "close all apps"],
  "description": "Closes all open applications",
  "actions": [
    {"action": "close_app", "args": {"app_name": "Chrome"}},
    {"action": "close_app", "args": {"app_name": "Visual Studio Code"}}
  ],
  "created_date": "2026-02-06T...",
  "last_used": "2026-02-06T...",
  "usage_count": 5,
  "enabled": true
}
```

#### API Endpoints:
- `POST /automation/custom-commands/create` - Create new custom command
- `GET /automation/custom-commands/list` - List all custom commands
- `GET /automation/custom-commands/{id}` - Get specific command
- `PUT /automation/custom-commands/{id}` - Update command
- `DELETE /automation/custom-commands/{id}` - Delete command
- `POST /automation/custom-commands/{id}/execute` - Execute command

---

### 2. **Multi-Step Automation Workflows** (`automation/workflows.py`)
Chain multiple actions together to create complex automated sequences.

#### Requirements:
- Visual workflow builder integration (UI component)
- Sequential action execution with error handling
- Conditional logic (if/then/else)
- Delay between actions
- Rollback on failure (optional)
- Logging and history

#### Data Model:
```json
{
  "_id": "...",
  "workflow_id": "workflow_001",
  "workflow_name": "Morning Routine",
  "description": "Opens browser, checks weather, plays playlist",
  "trigger": {
    "type": "voice",
    "keywords": ["start morning", "morning routine"]
  },
  "steps": [
    {
      "step_id": 1,
      "action": "open_app",
      "args": {"app_name": "Chrome"},
      "delay_after": 2,
      "on_error": "continue"
    },
    {
      "step_id": 2,
      "action": "execute",
      "args": {"command": "chat", "prompt": "What's the weather?"},
      "delay_after": 0,
      "on_error": "continue"
    },
    {
      "step_id": 3,
      "action": "system_call",
      "args": {"api": "media_control", "command": "play_playlist", "playlist": "Chill Vibes"},
      "delay_after": 0,
      "on_error": "stop"
    }
  ],
  "execution_history": [
    {
      "timestamp": "2026-02-06T...",
      "status": "completed",
      "duration_ms": 5000
    }
  ],
  "created_date": "2026-02-06T...",
  "enabled": true
}
```

#### API Endpoints:
- `POST /automation/workflows/create` - Create workflow
- `GET /automation/workflows/list` - List workflows
- `GET /automation/workflows/{id}` - Get workflow
- `PUT /automation/workflows/{id}` - Update workflow
- `DELETE /automation/workflows/{id}` - Delete workflow
- `POST /automation/workflows/{id}/execute` - Run workflow
- `GET /automation/workflows/{id}/history` - Execution history

---

### 3. **Habit Learning System** (`automation/habit_learning.py`)
Analyze user behavior to detect patterns and suggest automations.

#### Requirements:
- Event tracking and analysis
- Pattern detection (time-based, frequency-based, sequential)
- Anomaly detection
- Suggestion engine with confidence scores
- User feedback integration
- Privacy-conscious design

#### Data Model:
```json
{
  "_id": "...",
  "event_id": "event_xxx",
  "event_type": "app_opened",
  "event_data": {
    "app_name": "Chrome",
    "timestamp": "2026-02-06T09:00:00Z"
  },
  "user_action_sequence": ["open_chrome", "open_slack", "open_vscode"],
  "time_of_day": "morning",
  "day_of_week": "Monday",
  "context": {
    "day_type": "workday",
    "temperature": 20
  }
}
```

#### Habit Data Structure:
```json
{
  "_id": "...",
  "habit_id": "habit_001",
  "pattern_type": "sequential",
  "pattern_description": "Opens Chrome → Slack → VSCode",
  "detection_date": "2026-02-06T...",
  "occurrences": 5,
  "confidence_score": 0.85,
  "suggested_automation": {
    "name": "Morning Dev Setup",
    "actions": [...]
  },
  "user_feedback": "accepted",
  "automation_created": true,
  "automation_id": "workflow_xxx"
}
```

#### API Endpoints:
- `GET /automation/habits/list` - List detected habits
- `GET /automation/habits/{id}` - Get habit details
- `POST /automation/habits/{id}/accept` - Accept habit suggestion
- `POST /automation/habits/{id}/reject` - Reject suggestion
- `GET /automation/habits/suggestions` - Get pending suggestions
- `POST /automation/analysis/recent-patterns` - Analyze recent events

---

### 4. **Long-Term Memory System Enhancements** (`memory/memory_manager.py`)
Extend MongoDB storage for preferences, context, and history.

#### Requirements:
- Conversation memory with context
- User preferences storage
- Interaction history with metadata
- Memory retrieval with semantic search (future: vector embeddings)
- Memory expiration/archival policies
- Privacy controls

#### New Collections:

**memories collection** (enhanced):
```json
{
  "_id": "...",
  "memory_id": "mem_xxx",
  "type": "conversation|preference|event|fact",
  "content": "User prefers Chrome over Firefox",
  "timestamp": "2026-02-06T...",
  "context": {
    "conversation_id": "conv_xxx",
    "related_memories": ["mem_xxx", "mem_yyy"],
    "tags": ["browser", "preference"]
  },
  "relevance_score": 0.95,
  "expiry_date": null,
  "importance": "high|medium|low"
}
```

**user_preferences collection**:
```json
{
  "_id": "...",
  "preference_id": "pref_xxx",
  "category": "voice|display|automation|behavior",
  "key": "preferred_voice",
  "value": "Rachel",
  "set_date": "2026-02-06T...",
  "modified_date": "2026-02-06T...",
  "source": "auto|manual|inferred"
}
```

**interaction_history collection**:
```json
{
  "_id": "...",
  "interaction_id": "inter_xxx",
  "type": "voice_command|api_call|automation_exec",
  "command": "chat",
  "input": "What's the weather?",
  "response": "It's 20°C and cloudy",
  "execution_time_ms": 450,
  "timestamp": "2026-02-06T...",
  "success": true,
  "metadata": {
    "source": "voice|text",
    "device": "microphone",
    "context": {}
  }
}
```

#### API Endpoints:
- `POST /memory/save` - Save memory
- `GET /memory/search` - Search memories
- `GET /memory/context/{conversation_id}` - Get context
- `GET /preferences/list` - List preferences
- `POST /preferences/set` - Set preference
- `GET /history/interactions` - Get interaction history

---

### 5. **Personalized Suggestions System** (`automation/suggestion_engine.py`)
Provide intelligent, context-aware recommendations based on patterns and history.

#### Requirements:
- Multi-factor suggestion ranking
- Real-time suggestion delivery
- User feedback loop
- Suggestion learning (improve accuracy)
- Smart timing for suggestions
- Non-intrusive UI integration

#### Suggestion Types:
1. **Habit-Based**: "You usually open Slack on Monday mornings"
2. **Time-Based**: "Ready for your morning routine?"
3. **Context-Based**: "Weather changed, you might want to check forecast"
4. **Optimization**: "You could automate this sequence"
5. **Learning**: "You seem to prefer Chrome, shall I set it as default?"

#### Data Model:
```json
{
  "_id": "...",
  "suggestion_id": "sugg_xxx",
  "type": "automation|preference|optimization|learning",
  "title": "Set Up Morning Routine?",
  "description": "I noticed you open Chrome, Slack, and VSCode every Monday at 9 AM. Create an automation?",
  "confidence_score": 0.88,
  "ranking_factors": {
    "frequency": 0.9,
    "recency": 0.85,
    "context_match": 0.88
  },
  "suggested_action": {
    "type": "create_workflow",
    "workflow_template": {...}
  },
  "delivery_method": "notification|on_demand|contextual",
  "status": "pending|accepted|rejected",
  "created_date": "2026-02-06T...",
  "user_feedback": {
    "helpful": true,
    "feedback_date": "2026-02-06T..."
  }
}
```

#### API Endpoints:
- `GET /suggestions/active` - Get active suggestions
- `GET /suggestions/for-context` - Suggestions for current context
- `POST /suggestions/{id}/accept` - Accept suggestion
- `POST /suggestions/{id}/reject` - Reject suggestion
- `POST /suggestions/{id}/feedback` - Provide feedback
- `GET /suggestions/analytics` - Suggestion performance metrics

---

## 🏗️ Implementation Architecture

### New Directory Structure:
```
python-core/
├── automation/
│   ├── __init__.py
│   ├── custom_commands.py      # Custom command management
│   ├── workflows.py             # Workflow execution engine
│   ├── workflow_executor.py      # Async workflow runner
│   ├── habit_learning.py         # Habit detection & analysis
│   ├── suggestion_engine.py      # Suggestion generation
│   └── __pycache__/
├── memory/
│   ├── __init__.py
│   ├── memory_manager.py         # Memory operations
│   ├── preference_manager.py      # User preferences
│   └── __pycache__/
├── analytics/
│   ├── __init__.py
│   ├── pattern_analyzer.py        # Pattern detection
│   ├── event_analyzer.py          # Event analysis
│   └── __pycache__/
├── main.py                        # Updated with Stage 4 endpoints
└── requirements_stage4.txt        # New dependencies
```

### Electron Frontend Updates:
```
electron-app/
└── src/renderer/
    └── components/
        ├── AutomationBuilder.vue    # Workflow creation UI
        ├── CommandCreator.vue        # Custom command UI
        ├── HabitSuggestions.vue      # Habit suggestions panel
        ├── MemoryExplorer.vue        # Memory browsing UI
        └── PreferencesPanel.vue      # Preference management
```

---

## 📦 Dependencies

Add to `requirements_stage4.txt`:
```
# Existing
flask==2.3.3
pymongo==4.5.0
python-dotenv==1.0.0
pyaudio==0.2.13
elevenlabs==0.2.10
requests==2.31.0
beautifulsoup4==4.12.2
psutil==5.9.5
pillow==10.0.1
pydub==0.25.1
google-cloud-speech==2.22.0

# New for Stage 4
scikit-learn==1.3.2          # Pattern analysis, clustering
pandas==2.1.0               # Data analysis
numpy==1.24.3               # Numerical computing
scipy==1.11.3               # Statistical analysis
apscheduler==3.10.4         # Task scheduling
dateutil==2.8.2             # Date utilities
```

---

## 🚀 Implementation Phases

### Phase 1: Custom Commands (Week 1)
- [ ] Create `automation/custom_commands.py`
- [ ] Database schema for custom_commands collection
- [ ] API endpoints for CRUD operations
- [ ] Voice command matching integration
- [ ] Frontend UI components
- [ ] Testing suite

### Phase 2: Workflows (Week 2)
- [ ] Create `automation/workflows.py`
- [ ] Workflow execution engine
- [ ] Action handler system
- [ ] Error handling and rollback
- [ ] Workflow history logging
- [ ] Frontend workflow builder UI
- [ ] Testing suite

### Phase 3: Habit Learning (Week 3)
- [ ] Create `automation/habit_learning.py`
- [ ] Event tracking system
- [ ] Pattern detection algorithms
- [ ] Habit analysis engine
- [ ] Suggestion generation
- [ ] Frontend habit UI
- [ ] Testing suite

### Phase 4: Memory Enhancements & Suggestions (Week 4)
- [ ] Create `memory/` module structure
- [ ] Update MongoDB collections
- [ ] Suggestion engine implementation
- [ ] Memory search and retrieval
- [ ] Preference management
- [ ] Frontend integration
- [ ] Full system testing

---

## 🔧 Quick Start Commands

```bash
# Install Stage 4 dependencies
cd python-core
pip install -r requirements_stage4.txt

# Run with Stage 4 enabled
python main.py

# Test custom commands
curl -X POST http://localhost:5000/automation/custom-commands/create \
  -H "Content-Type: application/json" \
  -d '{
    "command_name": "Close everything",
    "trigger_words": ["close everything", "shut down apps"],
    "actions": [...]
  }'

# View habits
curl http://localhost:5000/automation/habits/list

# Get suggestions
curl http://localhost:5000/suggestions/active
```

---

## 📊 Success Metrics

✅ **Custom Commands:**
- Users can create custom commands via voice/UI
- Commands execute reliably
- Command history tracked

✅ **Workflows:**
- Multi-step automations execute without errors
- Proper error handling and recovery
- Execution history maintained

✅ **Habit Learning:**
- System detects 3+ habit patterns
- Suggestions have >80% confidence
- Users accept >50% of suggestions

✅ **Memory System:**
- System recalls relevant context from history
- Preferences are stored and respected
- Memory search returns relevant results

✅ **Suggestions:**
- Suggestions are timely and relevant
- System learns from user feedback
- Non-intrusive delivery

---

## 📝 Next Steps

1. ✅ Review this document
2. Create custom commands module
3. Implement database schemas
4. Build API endpoints
5. Create frontend components
6. Integration testing
7. Documentation & examples

**Current Status:** Ready to begin Phase 1

---

## 📚 Reference Documents

- [STARTUP_ROADMAP.md](STARTUP_ROADMAP.md) - Overall vision
- [STAGE3_IMPLEMENTATION.md](STAGE3_IMPLEMENTATION.md) - Previous stage
- [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md) - Full architecture
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Development patterns
