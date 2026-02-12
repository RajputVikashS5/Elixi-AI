# Stage 5 API Reference

**Status:** 🚀 Phase 0 Complete - Phase 1 APIs Starting  
**Last Updated:** February 6, 2026  
**Version:** 0.1

---

## Overview

This document will contain all Stage 5 REST API endpoints. Currently populated with placeholders for all planned endpoints across all 5 phases.

---

## API Structure

All Stage 5 APIs follow REST principles:
- **Base URL:** `http://localhost:5000`
- **Content-Type:** `application/json`
- **Authentication:** None (local development)

---

## Phase 1: Screen Understanding APIs

### 1. Analyze Screen
**Endpoint:** `POST /vision/analyze-screen`  
**Status:** 📋 Phase 1 - Planned  
**Purpose:** Analyze current screen and extract context

**Request:**
```json
{
  "include_text": true,
  "include_elements": true,
  "ai_interpretation": true
}
```

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "timestamp": "2026-02-06T10:30:00Z",
    "window_info": {
      "title": "Visual Studio Code",
      "app_name": "Code",
      "dimensions": {"width": 1920, "height": 1080}
    },
    "text_content": "Extracted text from screen",
    "elements": [
      {"type": "button", "text": "Save", "position": [100, 200]},
      {"type": "textbox", "placeholder": "Search"}
    ],
    "ai_analysis": "User is editing Python code",
    "confidence": 0.92
  },
  "timestamp": "2026-02-06T10:30:00Z"
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid parameters
- `500` - Analysis failed

---

### 2. Get Screen Text
**Endpoint:** `POST /vision/get-screen-text`  
**Status:** 📋 Phase 1 - Planned  
**Purpose:** Extract only text from screen (OCR)

**Request:**
```json
{
  "ocr_confidence_threshold": 0.7
}
```

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "text": "Full screen text content",
    "languages_detected": ["en"],
    "ocr_confidence": 0.89,
    "num_characters": 1234
  },
  "timestamp": "2026-02-06T10:30:00Z"
}
```

---

### 3. Identify Window
**Endpoint:** `GET /vision/identify-window`  
**Status:** 📋 Phase 1 - Planned  
**Purpose:** Get information about currently active window

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "window_handle": "0x0010010a",
    "title": "Visual Studio Code",
    "app_name": "Code",
    "app_path": "C:\\Users\\{user}\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
    "process_id": 12345,
    "position": {"x": 0, "y": 0},
    "size": {"width": 1920, "height": 1080},
    "is_maximized": true
  },
  "timestamp": "2026-02-06T10:30:00Z"
}
```

---

### 4. Get Screen Cache
**Endpoint:** `GET /vision/screen-cache`  
**Status:** 📋 Phase 1 - Planned  
**Purpose:** Get cached screen analysis (no recompute)

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "analysis": {
      "timestamp": "2026-02-06T10:25:00Z",
      "window_info": {...},
      "text_content": "...",
      "ai_analysis": "..."
    },
    "cache_age_seconds": 300,
    "cache_ttl_seconds": 300,
    "is_expired": false
  },
  "timestamp": "2026-02-06T10:30:00Z"
}
```

---

## Phase 2: Coding Assistant APIs

### 1. Generate Code
**Endpoint:** `POST /coding/generate-code`  
**Status:** 📋 Phase 2 - Planned  
**Purpose:** Generate code from natural language description

**Request:**
```json
{
  "description": "Create a function that sorts a list of numbers",
  "language": "python",
  "context": "I need this for data processing"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "code": "def sort_numbers(numbers):\n    return sorted(numbers)",
    "language": "python",
    "explanation": "This function uses Python's built-in sorted() function",
    "alternative_approaches": [
      "Using collections.Counter for frequency",
      "Using heapq.nsmallest() for top N numbers"
    ]
  },
  "timestamp": "2026-02-06T10:30:00Z"
}
```

---

### 2. Debug Code
**Endpoint:** `POST /coding/debug-code`  
**Status:** 📋 Phase 2 - Planned  
**Purpose:** Analyze code for errors and suggest fixes

**Request:**
```json
{
  "code": "def add(a, b)\n    return a + b",
  "language": "python"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "errors": [
      {
        "type": "syntax_error",
        "line": 1,
        "message": "Missing colon after function definition",
        "fix": "Add ':' after closing parenthesis",
        "corrected_line": "def add(a, b):"
      }
    ],
    "warnings": [
      {
        "type": "style_warning",
        "message": "Add docstring to function",
        "suggestion": "Add '''Function description''' at start of function"
      }
    ],
    "severity_score": 1.0
  },
  "timestamp": "2026-02-06T10:30:00Z"
}
```

---

### 3. Explain Code
**Endpoint:** `POST /coding/explain-code`  
**Status:** 📋 Phase 2 - Planned  
**Purpose:** Generate explanation for code snippet

**Request:**
```json
{
  "code": "sum(x*x for x in range(10))",
  "language": "python",
  "detail_level": "comprehensive"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "summary": "Calculates sum of squares from 0 to 9",
    "detailed_explanation": "Uses generator expression to compute squares...",
    "components": [
      {"part": "sum(...)", "explanation": "Built-in sum function"},
      {"part": "x*x for x in range(10)", "explanation": "Generator expression"}
    ]
  },
  "timestamp": "2026-02-06T10:30:00Z"
}
```

---

### 4. Refactor Code
**Endpoint:** `POST /coding/refactor-code`  
**Status:** 📋 Phase 2 - Planned  
**Purpose:** Suggest code improvements

**Request:**
```json
{
  "code": "...",
  "language": "python",
  "focus": ["performance", "readability"]
}
```

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "refactored_code": "...",
    "improvements": [
      {"type": "performance", "impact": "2x faster", "explanation": "..."},
      {"type": "readability", "impact": "improved", "explanation": "..."}
    ]
  },
  "timestamp": "2026-02-06T10:30:00Z"
}
```

---

### 5. Generate Documentation
**Endpoint:** `POST /coding/documentation`  
**Status:** 📋 Phase 2 - Planned  
**Purpose:** Generate documentation for code

**Request:**
```json
{
  "code": "...",
  "language": "python",
  "format": "docstring"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "documentation": "...",
    "format": "docstring",
    "includes": ["summary", "parameters", "returns", "examples"]
  },
  "timestamp": "2026-02-06T10:30:00Z"
}
```

---

## Phase 3: News & Weather APIs

### 1. Get Weather
**Endpoint:** `POST /info/weather`  
**Status:** 📋 Phase 3 - Planned  
**Purpose:** Get current weather for location

**Request:**
```json
{
  "location": "New York, USA",
  "units": "imperial"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "location": "New York, USA",
    "temperature": 72,
    "condition": "Partly Cloudy",
    "humidity": 65,
    "wind_speed": 12,
    "pressure": 1013,
    "units": "imperial",
    "updated_at": "2026-02-06T10:30:00Z"
  },
  "timestamp": "2026-02-06T10:30:00Z"
}
```

---

### 2. Get News
**Endpoint:** `POST /info/news`  
**Status:** 📋 Phase 3 - Planned  
**Purpose:** Get latest news headlines

**Request:**
```json
{
  "category": "technology",
  "country": "us",
  "limit": 5
}
```

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "articles": [
      {
        "title": "AI Breakthrough in 2026",
        "source": "TechNews",
        "url": "https://example.com/article",
        "published_at": "2026-02-06T08:00:00Z",
        "summary": "..."
      }
    ],
    "total_articles": 50,
    "category": "technology"
  },
  "timestamp": "2026-02-06T10:30:00Z"
}
```

---

### 3. Get Weather Forecast
**Endpoint:** `POST /info/weather-forecast`  
**Status:** 📋 Phase 3 - Planned  
**Purpose:** Get extended weather forecast

**Request:**
```json
{
  "location": "New York, USA",
  "days": 7,
  "units": "imperial"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "location": "New York, USA",
    "forecast": [
      {
        "date": "2026-02-06",
        "high": 74,
        "low": 52,
        "condition": "Partly Cloudy",
        "precipitation_chance": 20
      }
    ],
    "units": "imperial"
  },
  "timestamp": "2026-02-06T10:30:00Z"
}
```

---

## Phase 4: Model Management APIs

### 1. Get Available Models
**Endpoint:** `GET /ai/available-models`  
**Status:** 📋 Phase 4 - Planned  
**Purpose:** List all installed Ollama models

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "models": [
      {
        "name": "mistral",
        "size": "7.4 GB",
        "parameters": "7B",
        "quantization": "4-bit"
      },
      {
        "name": "neural-chat",
        "size": "4.1 GB",
        "parameters": "7B",
        "quantization": "4-bit"
      }
    ],
    "total_models": 2
  },
  "timestamp": "2026-02-06T10:30:00Z"
}
```

---

### 2. Switch Model
**Endpoint:** `POST /ai/switch-model`  
**Status:** 📋 Phase 4 - Planned  
**Purpose:** Change active AI model

**Request:**
```json
{
  "model_name": "neural-chat"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "previous_model": "mistral",
    "current_model": "neural-chat",
    "switch_time_ms": 230
  },
  "timestamp": "2026-02-06T10:30:00Z"
}
```

---

### 3. Get Model Status
**Endpoint:** `GET /ai/model-status`  
**Status:** 📋 Phase 4 - Planned  
**Purpose:** Get information about current model

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "current_model": "mistral",
    "memory_used_mb": 4096,
    "tokens_processed": 12345,
    "average_response_time_ms": 450,
    "uptime_seconds": 3600
  },
  "timestamp": "2026-02-06T10:30:00Z"
}
```

---

### 4. Download Model
**Endpoint:** `POST /ai/download-model`  
**Status:** 📋 Phase 4 - Planned  
**Purpose:** Install new Ollama model

**Request:**
```json
{
  "model_name": "llama2"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "model": "llama2",
    "download_size": "3.8 GB",
    "status": "downloading",
    "progress_percent": 45
  },
  "timestamp": "2026-02-06T10:30:00Z"
}
```

---

## Phase 5: System & Background Mode APIs

### 1. Enable/Disable Background Mode
**Endpoint:** `POST /system/background-mode`  
**Status:** 📋 Phase 5 - Planned  
**Purpose:** Enable always-running background operation

**Request:**
```json
{
  "enable": true,
  "system_tray": true,
  "auto_start": true
}
```

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "background_mode": true,
    "system_tray_enabled": true,
    "auto_start_configured": true
  },
  "timestamp": "2026-02-06T10:30:00Z"
}
```

---

### 2. Get Background Status
**Endpoint:** `GET /system/background-status`  
**Status:** 📋 Phase 5 - Planned  
**Purpose:** Check background mode status

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "background_mode_active": true,
    "system_tray_visible": true,
    "cpu_usage_percent": 2.3,
    "memory_usage_mb": 145,
    "uptime_seconds": 7200
  },
  "timestamp": "2026-02-06T10:30:00Z"
}
```

---

### 3. Configure Auto-Start
**Endpoint:** `POST /system/auto-start`  
**Status:** 📋 Phase 5 - Planned  
**Purpose:** Configure Windows auto-start

**Request:**
```json
{
  "enable": true,
  "startup_mode": "minimized"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "auto_start_enabled": true,
    "startup_mode": "minimized",
    "registry_configured": true
  },
  "timestamp": "2026-02-06T10:30:00Z"
}
```

---

## Error Response Format

All endpoints return this format on error:

```json
{
  "status": "error",
  "message": "Descriptive error message",
  "error_code": "ERROR_CODE",
  "details": {
    "field": "specific error details"
  },
  "timestamp": "2026-02-06T10:30:00Z"
}
```

---

## Response Status Codes

| Code | Meaning | When Returned |
|------|---------|---------------|
| 200 | Success | Operation completed successfully |
| 400 | Bad Request | Invalid parameters or missing fields |
| 401 | Unauthorized | Authentication required (future) |
| 403 | Forbidden | Permission denied (future) |
| 404 | Not Found | Endpoint doesn't exist |
| 500 | Server Error | Unexpected error during processing |
| 503 | Service Unavailable | Service (Ollama, API) not available |

---

## Rate Limiting

- **Premium:** 100 requests/minute
- **Standard:** 50 requests/minute
- **Free:** 10 requests/minute

(To be implemented in Phase 5)

---

## Caching Behavior

All Stage 5 endpoints implement intelligent caching:

| Endpoint | Default TTL | Persistent |
|----------|------------|-----------|
| Vision APIs | 5 minutes | Yes |
| Coding APIs | 30 minutes | Yes |
| News/Weather | 2 hours | Yes |
| Model Status | 1 minute | No |

---

## Implementation Timeline

| Phase | APIs | Status | ETA |
|-------|------|--------|-----|
| Phase 1 | Vision (4) | 📋 Planned | Feb 7-9 |
| Phase 2 | Coding (5) | 📋 Planned | Feb 10-12 |
| Phase 3 | News/Weather (3) | 📋 Planned | Feb 12-13 |
| Phase 4 | Models (4) | 📋 Planned | Feb 13 |
| Phase 5 | System (3) | 📋 Planned | Feb 14-15 |
| **Total** | **19 APIs** | **In Progress** | **Feb 15** |

---

## Testing

Test all endpoints with cURL:

```bash
# Example Phase 1 (when implemented)
curl -X POST http://localhost:5000/vision/analyze-screen \
  -H "Content-Type: application/json" \
  -d '{"include_text": true}'
```

---

## Notes

- All timestamps are in ISO 8601 format
- All durations are in seconds unless otherwise specified
- All sizes are in bytes unless otherwise specified
- Percentage values are 0-100

---

**Last Updated:** February 6, 2026  
**Document Version:** 0.1  
**Status:** Planning Phase - Ready for Phase 1
