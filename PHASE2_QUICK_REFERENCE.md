# Stage 4 Phase 2 - Quick Reference Guide

## New API Endpoints Overview

### 1. Semantic Search
**Endpoint:** `POST /memory/semantic-search`

Find memories by semantic similarity using TF-IDF vectorization.

**Request:**
```json
{
  "query": "morning routine habits",
  "threshold": 0.3,
  "type": "conversation",
  "limit": 10
}
```

**Response:**
```json
{
  "success": true,
  "memories": [
    {
      "memory_id": "mem_123456",
      "content": "User likes to exercise in the morning",
      "similarity_score": 0.85,
      "importance": "high"
    }
  ],
  "count": 1
}
```

### 2. Search Related Memories
**Endpoint:** `POST /memory/search-related`

Find memories related to a specific conversation.

**Request:**
```json
{
  "conversation_id": "conv_123456",
  "query": "productivity",
  "limit": 5
}
```

**Response:**
```json
{
  "success": true,
  "memories": [...],
  "count": 3
}
```

### 3. Set Memory Expiry
**Endpoint:** `POST /memory/set-expiry`

Set custom expiration date for a memory.

**Request:**
```json
{
  "memory_id": "mem_123456",
  "days_to_expiry": 30
}
```

**Response:**
```json
{
  "success": true,
  "expiry_date": "2026-03-08T10:30:45.123456"
}
```

### 4. Archive Expired Memories
**Endpoint:** `POST /memory/archive-expired`

Automatically archive all memories past their expiry date.

**Request:**
```json
{}
```

**Response:**
```json
{
  "success": true,
  "archived_count": 5
}
```

### 5. Conversation Summary
**Endpoint:** `POST /memory/conversation-summary`

Get automated analysis of a conversation.

**Request:**
```json
{
  "conversation_id": "conv_123456"
}
```

**Response:**
```json
{
  "success": true,
  "summary": {
    "conversation_id": "conv_123456",
    "message_count": 6,
    "total_tokens": 156,
    "participants": ["user", "assistant"],
    "participant_distribution": {
      "user": 84,
      "assistant": 72
    },
    "duration_seconds": 120,
    "created_at": "2026-02-06T10:00:00Z",
    "keywords": ["productivity", "morning", "routine", "workflow"]
  }
}
```

### 6. Enhanced Memory Statistics
**Endpoint:** `GET /memory/statistics`

Get detailed memory system statistics.

**Request:**
```
(no body)
```

**Response:**
```json
{
  "success": true,
  "total_memories": 245,
  "active_memories": 210,
  "archived_memories": 35,
  "by_type": {
    "conversation": 150,
    "learning": 45,
    "event": 15
  },
  "by_importance": {
    "high": 75,
    "medium": 95,
    "low": 40
  },
  "semantic_search_available": true
}
```

---

## Usage Examples

### Example 1: Search for Related Information
```python
import requests

# Find memories about a conversation
response = requests.post(
    "http://localhost:5000/memory/semantic-search",
    json={
        "query": "automation setup",
        "limit": 5
    }
)

results = response.json()
for memory in results['memories']:
    print(f"[{memory['similarity_score']:.2f}] {memory['content']}")
```

### Example 2: Conversation Analysis
```python
import requests

# Get conversation summary
response = requests.post(
    "http://localhost:5000/memory/conversation-summary",
    json={
        "conversation_id": "conv_morning_chat"
    }
)

summary = response.json()['summary']
print(f"Duration: {summary['duration_seconds']} seconds")
print(f"Participants: {summary['participants']}")
print(f"Keywords: {', '.join(summary['keywords'][:5])}")
```

### Example 3: Memory Cleanup
```python
import requests

# Set expiry for a memory
requests.post(
    "http://localhost:5000/memory/set-expiry",
    json={
        "memory_id": "mem_old_data",
        "days_to_expiry": 30
    }
)

# Archive all expired
response = requests.post(
    "http://localhost:5000/memory/archive-expired",
    json={}
)

print(f"Archived: {response.json()['archived_count']} memories")
```

---

## Memory Retention Policies

Automatic retention based on memory type (when cleanup is run):

| Type | Duration | Reason |
|------|----------|--------|
| Conversation | 90 days | Conversation history |
| Event | 180 days | Important events |
| Learning | 450 days | Learning experiences |
| Preference | 270 days | User preferences |
| Fact | 900 days | Static facts |

**Note:** Only low-importance memories auto-delete. High and medium importance memories are preserved.

---

## Semantic Search Parameters

### Threshold
- **Range:** 0 to 1
- **Default:** 0.3
- **Usage:** Filter results by minimum similarity score
  - 0.9+: Exact match-like results
  - 0.5-0.9: Highly relevant
  - 0.3-0.5: Moderately relevant
  - <0.3: Weakly related

### Limit
- **Default:** 20
- **Usage:** Maximum number of results to return

### Type Filter
- Optional: Filter by memory type
- Values: `conversation`, `preference`, `event`, `fact`, `learning`

---

## Best Practices

1. **Semantic Search**
   - Use lower threshold (0.2-0.3) for broader searches
   - Use higher threshold (0.7+) for precise matches
   - Provide clear, specific queries for better results

2. **Memory Expiration**
   - Set custom expiry for temporary memories
   - Run cleanup periodically (weekly/monthly)
   - Important memories won't auto-delete (set importance level)

3. **Conversation Context**
   - Summarize long conversations periodically
   - Extract keywords for indexing
   - Track conversation metadata

4. **Statistics**
   - Monitor memory growth rate
   - Track importance distribution
   - Identify over-archival issues

---

## Integration with Phase 1 Features

Phase 2 builds on Phase 1:
- Works with existing memory endpoints
- Compatible with all memory types
- Enhances existing search capabilities
- No breaking changes to existing APIs

Example combined flow:
```python
# Save a memory (Phase 1)
requests.post("http://localhost:5000/memory/save", json={
    "memory_type": "conversation",
    "content": "User wants morning productivity tips"
})

# Search semantically (Phase 2)
requests.post("http://localhost:5000/memory/semantic-search", json={
    "query": "productivity routines"
})
```

---

## Troubleshooting

### Semantic Search Returns No Results
- Lower the `threshold` parameter
- Check if memories exist using `/memory/statistics`
- Verify query is relevant to stored content

### Memories Not Archived
- Check memory importance level (high/medium preserved)
- Run `/memory/archive-expired` manually
- Verify memory has `expiry_date` set

### Conversation Summary Missing Keywords
- Conversation needs >3 messages
- Keywords extracted from message content
- Check message content is descriptive

---

## Next Steps

Phase 3 will add:
- Preference learning from user behavior
- Automated preference recommendations
- Preference-based suggestions

These will leverage Phase 2's memory system for analysis.

---

**Status:** Ready to use | **Version:** 1.0 | **Date:** February 6, 2026
