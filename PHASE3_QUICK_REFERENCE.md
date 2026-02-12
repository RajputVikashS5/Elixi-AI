# Stage 4 Phase 3 - Quick Reference Guide

**Feature:** User Preferences with Behavioral Learning  
**Status:** ✅ Complete  
**Date:** February 6, 2026

---

## Quick Start

### Test Phase 3
```bash
cd python-core
python test_phase3.py
```

---

## New API Endpoints (5 Total)

### 1. Analyze Behavior
```bash
curl -X POST http://localhost:5000/preferences/analyze-behavior \
  -H "Content-Type: application/json" \
  -d '{"days": 14}'
```

**What it does:** Analyzes user behavior patterns and automatically learns preferences

**Response:**
```json
{
  "success": true,
  "patterns_detected": 8,
  "preferences_learned": 5,
  "patterns": [...]
}
```

---

### 2. Detect Patterns
```bash
curl -X POST http://localhost:5000/preferences/patterns \
  -H "Content-Type: application/json" \
  -d '{}'
```

**What it does:** Finds meta-patterns in existing preferences

**Response:**
```json
{
  "success": true,
  "patterns": [
    {
      "pattern_type": "category_preference",
      "description": "Strong preferences in behavior category",
      "confidence": 0.8
    }
  ]
}
```

---

### 3. Auto-Learning Control
```bash
# Enable
curl -X POST http://localhost:5000/preferences/auto-learn \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# Disable
curl -X POST http://localhost:5000/preferences/auto-learn \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

**What it does:** Enable or disable automatic preference learning

---

### 4. Habit-Based Suggestions
```bash
curl -X POST http://localhost:5000/preferences/suggest-from-habits \
  -H "Content-Type: application/json" \
  -d '{}'
```

**What it does:** Generates preference suggestions based on detected habits

**Response:**
```json
{
  "success": true,
  "suggestions": [
    {
      "category": "automation",
      "key": "workflow_automation_enabled",
      "value": true,
      "confidence": 0.9,
      "reason": "Detected habit: Opens Chrome → Slack → VSCode"
    }
  ]
}
```

---

### 5. Learning Analytics
```bash
curl -X POST http://localhost:5000/preferences/learning-analytics \
  -H "Content-Type: application/json" \
  -d '{}'
```

**What it does:** Shows learning performance metrics

**Response:**
```json
{
  "success": true,
  "total_preferences": 25,
  "by_source": {
    "manual": 10,
    "inferred": 12,
    "auto": 3
  },
  "learning_metrics": {
    "learning_score": 60.0,
    "accepted_suggestions": 8
  }
}
```

---

## Behavioral Analysis Types

### 1. Application Usage
- Tracks which apps are used most frequently
- Detects preferred applications (>30% usage)
- **Confidence:** Based on usage ratio

**Example:**
```json
{
  "category": "behavior",
  "key": "preferred_app",
  "value": "Chrome",
  "confidence": 0.85,
  "evidence": "Used 45 times (72% of sessions)"
}
```

---

### 2. Time-Based Patterns
- Analyzes activity by time of day
- Detects peak activity periods (>35%)
- **Times:** morning, afternoon, evening, night

**Example:**
```json
{
  "category": "behavior",
  "key": "peak_activity_time",
  "value": "morning",
  "confidence": 0.78,
  "evidence": "120 events (43% of activity)"
}
```

---

### 3. Interaction Style
- Analyzes conversation message lengths
- Determines response preference
- **Styles:** brief (<100 chars), moderate (<300), detailed (300+)

**Example:**
```json
{
  "category": "interaction",
  "key": "response_style",
  "value": "brief",
  "confidence": 0.75,
  "evidence": "Average response: 85 characters"
}
```

---

### 4. Command Usage
- Tracks command execution patterns
- Identifies preferred command types (>25% usage)
- Helps optimize command availability

**Example:**
```json
{
  "category": "automation",
  "key": "preferred_command_type",
  "value": "system_control",
  "confidence": 0.82,
  "evidence": "Used 30 times (45%)"
}
```

---

## Complete Workflow Example

### Step 1: Analyze Behavior
```bash
curl -X POST http://localhost:5000/preferences/analyze-behavior \
  -H "Content-Type: application/json" \
  -d '{"days": 7}'
```

### Step 2: Review Learned Preferences
```bash
curl -X POST http://localhost:5000/preferences/recommendations \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Step 3: Apply or Reject
```bash
# Apply (accept)
curl -X POST http://localhost:5000/preferences/apply \
  -H "Content-Type: application/json" \
  -d '{"category": "behavior", "key": "preferred_app"}'

# Reject
curl -X POST http://localhost:5000/preferences/reject \
  -H "Content-Type: application/json" \
  -d '{"category": "behavior", "key": "preferred_app"}'
```

### Step 4: Check Analytics
```bash
curl -X POST http://localhost:5000/preferences/learning-analytics \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## Integration with Existing Features

### Works With Phase 1 (Habits)
```bash
# 1. Detect habits
curl -X POST http://localhost:5000/automation/habits/analyze \
  -H "Content-Type: application/json" \
  -d '{"days": 7}'

# 2. Generate preferences from habits
curl -X POST http://localhost:5000/preferences/suggest-from-habits \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Works With Phase 2 (Memory)
```bash
# Phase 3 analyzes conversation memories
# for interaction style preferences automatically
```

---

## Configuration

### Enable Auto-Learning
```bash
curl -X POST http://localhost:5000/preferences/auto-learn \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

When enabled, system automatically:
- Analyzes behavior daily
- Learns new preferences
- Updates existing preferences
- Maintains confidence scores

---

## Confidence Score Guide

| Score | Meaning | Action |
|-------|---------|--------|
| 0.9-1.0 | Very high confidence | Auto-stored, highly reliable |
| 0.7-0.9 | High confidence | Auto-stored, reliable |
| 0.6-0.7 | Moderate confidence | Auto-stored, review recommended |
| 0.3-0.6 | Low confidence | Not auto-stored, manual review |
| <0.3 | Too low | Rejected, insufficient data |

---

## Data Requirements

For accurate analysis, minimum requirements:

| Analysis Type | Minimum Data |
|---------------|--------------|
| App preferences | 5+ app open events |
| Time patterns | 10+ events |
| Interaction style | 5+ conversations |
| Command preferences | 5+ command executions |

---

## Preference Categories

### behavior
- preferred_app
- peak_activity_time
- preferred_command_type

### interaction
- response_style
- communication_preference

### automation
- workflow_automation_enabled
- automation_suggestions_enabled
- preferred_work_time

### voice
- (from Phase 2)

### display
- (from Phase 2)

### system
- (from Phase 2)

---

## Troubleshooting

### No Patterns Detected
- **Cause:** Insufficient data
- **Solution:** Use system for 3-5 days, then re-analyze

### Low Confidence Scores
- **Cause:** Inconsistent behavior
- **Solution:** Normal for new users, will improve over time

### Too Many Inferred Preferences
- **Cause:** Auto-learning too aggressive
- **Solution:** Disable auto-learn, review manually

### Learning Score Low
- **Cause:** Few inferred preferences accepted
- **Solution:** Normal initially, will improve with feedback

---

## PowerShell Examples (Windows)

### Analyze Behavior
```powershell
$body = @{days=14} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5000/preferences/analyze-behavior" `
  -Method Post -ContentType "application/json" -Body $body
```

### Get Analytics
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/preferences/learning-analytics" `
  -Method Post -ContentType "application/json" -Body "{}"
```

### Enable Auto-Learning
```powershell
$body = @{enabled=$true} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5000/preferences/auto-learn" `
  -Method Post -ContentType "application/json" -Body $body
```

---

## Key Statistics

| Metric | Value |
|--------|-------|
| New Endpoints | 5 |
| Analysis Types | 4 |
| New Methods | 9 |
| Minimum Confidence | 0.6 (for auto-store) |
| Default Analysis Window | 14 days |
| Test Functions | 7 |

---

## What's Next?

### Phase 4: Database Optimization
- MongoDB indexes for performance
- Compound indexes for queries
- Data retention policies
- Performance profiling

### Phase 5: UI Integration
- Preference management UI
- Learning analytics dashboard
- Auto-learning toggle
- Recommendation notifications

---

## Complete Endpoint List

### Phase 3 (New)
1. POST `/preferences/analyze-behavior`
2. POST `/preferences/patterns`
3. POST `/preferences/auto-learn`
4. POST `/preferences/suggest-from-habits`
5. POST `/preferences/learning-analytics`

### Phase 2 (Existing)
6. POST `/preferences/set`
7. POST `/preferences/get`
8. POST `/preferences/all`
9. POST `/preferences/delete`
10. POST `/preferences/recommendations`
11. POST `/preferences/apply`
12. POST `/preferences/reject`
13. POST `/preferences/statistics`
14. POST `/preferences/history`

**Total:** 14 preference endpoints

---

## Documentation Files

- [STAGE4_PHASE3_SUMMARY.md](STAGE4_PHASE3_SUMMARY.md) - Complete implementation details
- [STAGE4_PHASE2_SUMMARY.md](STAGE4_PHASE2_SUMMARY.md) - Phase 2 memory features
- [STAGE4_PROGRESS.md](STAGE4_PROGRESS.md) - Overall progress tracking
- [STAGE4_API_REFERENCE.md](STAGE4_API_REFERENCE.md) - Full API reference

---

**Status:** ✅ Ready to use  
**Version:** 1.0  
**Date:** February 6, 2026
