# ELIXI API - Stage 4: Automation & Memory Reference

## Custom Commands API

### Create Command
```bash
POST /automation/custom-commands/create
Content-Type: application/json

{
  "command_name": "Close everything",
  "trigger_words": ["close everything", "shut down apps"],
  "description": "Closes all open applications",
  "actions": [
    {
      "action": "close_app",
      "args": {"app_name": "Chrome"}
    },
    {
      "action": "close_app",
      "args": {"app_name": "Visual Studio Code"}
    }
  ]
}
```

### List Commands
```bash
POST /automation/custom-commands/list
Content-Type: application/json

{
  "enabled_only": false
}
```

### Get Command
```bash
POST /automation/custom-commands/get
Content-Type: application/json

{
  "command_id": "cmd_1707246000000"
}
```

### Update Command
```bash
POST /automation/custom-commands/update
Content-Type: application/json

{
  "command_id": "cmd_1707246000000",
  "command_name": "New Name",
  "trigger_words": ["new trigger"],
  "enabled": true
}
```

### Delete Command
```bash
POST /automation/custom-commands/delete
Content-Type: application/json

{
  "command_id": "cmd_1707246000000"
}
```

### Execute Command
```bash
POST /automation/custom-commands/execute
Content-Type: application/json

{
  "command_id": "cmd_1707246000000"
}
```

### Get Top Commands
```bash
POST /automation/custom-commands/top
Content-Type: application/json

{
  "limit": 10
}
```

---

## Workflows API

### Create Workflow
```bash
POST /automation/workflows/create
Content-Type: application/json

{
  "workflow_name": "Morning Routine",
  "description": "Opens browser, checks weather, plays music",
  "trigger": {
    "type": "voice",
    "keywords": ["start morning", "morning routine"]
  },
  "steps": [
    {
      "action": "open_app",
      "args": {"app_name": "Chrome"},
      "delay_after": 2,
      "on_error": "continue"
    },
    {
      "action": "execute",
      "args": {"command": "chat", "prompt": "What's the weather?"},
      "delay_after": 0,
      "on_error": "continue"
    }
  ]
}
```

### List Workflows
```bash
POST /automation/workflows/list
Content-Type: application/json

{
  "enabled_only": false
}
```

### Get Workflow
```bash
POST /automation/workflows/get
Content-Type: application/json

{
  "workflow_id": "wf_1707246000000"
}
```

### Update Workflow
```bash
POST /automation/workflows/update
Content-Type: application/json

{
  "workflow_id": "wf_1707246000000",
  "workflow_name": "Updated Name",
  "steps": [...]
}
```

### Delete Workflow
```bash
POST /automation/workflows/delete
Content-Type: application/json

{
  "workflow_id": "wf_1707246000000"
}
```

### Execute Workflow
```bash
POST /automation/workflows/execute
Content-Type: application/json

{
  "workflow_id": "wf_1707246000000"
}
```

### Get Workflow History
```bash
POST /automation/workflows/history
Content-Type: application/json

{
  "workflow_id": "wf_1707246000000",
  "limit": 50
}
```

---

## Habit Learning API

### Analyze Recent Events
```bash
POST /automation/habits/analyze
Content-Type: application/json

{
  "days": 7
}
```

Response:
```json
{
  "success": true,
  "patterns": [
    {
      "pattern_type": "sequential",
      "description": "Chrome → Slack",
      "occurrences": 5,
      "confidence_score": 0.88
    }
  ],
  "habits": [
    {
      "habit_id": "hab_xxx",
      "type": "automation",
      "title": "Automate: Chrome → Slack",
      "confidence_score": 0.88
    }
  ]
}
```

### List Detected Habits
```bash
POST /automation/habits/list
Content-Type: application/json

{}
```

### Provide Habit Feedback
```bash
POST /automation/habits/feedback
Content-Type: application/json

{
  "pattern_id": "hab_xxx",
  "feedback": "helpful|not_helpful|skip"
}
```

### Get Habit Analytics
```bash
POST /automation/habits/analytics
Content-Type: application/json

{}
```

---

## Suggestions API

### Get Active Suggestions
```bash
POST /suggestions/active
Content-Type: application/json

{
  "limit": 5
}
```

Response:
```json
{
  "success": true,
  "suggestions": [
    {
      "suggestion_id": "sugg_xxx",
      "type": "automation",
      "title": "Automate: Chrome → Slack?",
      "description": "I noticed you open Chrome then Slack 5 times...",
      "confidence_score": 0.88,
      "status": "pending"
    }
  ]
}
```

### Get Context-Aware Suggestions
```bash
POST /suggestions/for-context
Content-Type: application/json

{
  "context": {
    "time_of_day": "morning",
    "active_apps": ["Chrome", "Slack"]
  }
}
```

### Respond to Suggestion
```bash
POST /suggestions/respond
Content-Type: application/json

{
  "suggestion_id": "sugg_xxx",
  "response": "accepted|rejected|later",
  "helpful": true
}
```

### Get Suggestion Analytics
```bash
POST /suggestions/analytics
Content-Type: application/json

{}
```

Response:
```json
{
  "success": true,
  "total_suggestions": 45,
  "pending": 12,
  "acceptance_rate": 62.5,
  "helpfulness_rate": 78.3,
  "by_type": {
    "automation": {"total": 25, "accepted": 18},
    "learning": {"total": 20, "accepted": 10}
  }
}
```

### Dismiss Suggestion Type
```bash
POST /suggestions/dismiss-type
Content-Type: application/json

{
  "type": "automation"
}
```

---

## Integration with Custom Commands

When a custom command is recognized (via voice or UI), it's executed:

```javascript
// Frontend example
const response = await fetch('http://localhost:5000/automation/custom-commands/execute', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({command_id: 'cmd_xxx'})
});

const result = await response.json();
// result.actions contains array of actions to execute
// result.message contains command name
```

---

## Recording Events for Habit Learning

To record events for analysis, use the existing events collection or create dedicated event records:

```bash
POST /memory/save
Content-Type: application/json

{
  "event_type": "app_opened",
  "event_data": {
    "app_name": "Chrome",
    "timestamp": "2026-02-06T09:00:00Z"
  },
  "source": "system_control"
}
```

---

## MongoDB Collections for Stage 4

### custom_commands
- Stores custom voice commands
- Fields: command_id, command_name, trigger_words, actions, usage_count, enabled

### workflows
- Stores automation workflows
- Fields: workflow_id, workflow_name, steps, trigger, execution_count, enabled

### workflow_history
- Records workflow executions
- Fields: execution_id, workflow_id, status, duration_ms, timestamp

### detected_habits
- Stores detected behavior patterns
- Fields: habit_id, pattern_type, confidence_score, occurrences, user_feedback

### suggestions
- Stores AI suggestions for user
- Fields: suggestion_id, type, title, confidence_score, status, user_response

---

## Best Practices

1. **Custom Commands**: Keep trigger words concise and distinctive
2. **Workflows**: Start with 2-3 steps, test thoroughly before adding more
3. **Habit Analysis**: Run analysis daily to keep patterns fresh
4. **Suggestions**: Review and respond to suggestions to help system learn
5. **Error Handling**: Always check "on_error" strategy for critical steps

---

## Testing with cURL

```bash
# Test custom command creation
curl -X POST http://localhost:5000/automation/custom-commands/create \
  -H "Content-Type: application/json" \
  -d @custom_command.json

# Test habit analysis
curl -X POST http://localhost:5000/automation/habits/analyze \
  -H "Content-Type: application/json" \
  -d '{"days": 7}'

# Test suggestions
curl -X POST http://localhost:5000/suggestions/active \
  -H "Content-Type: application/json" \
  -d '{"limit": 5}'
```
