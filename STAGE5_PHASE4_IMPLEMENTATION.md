# Stage 5 Phase 4 - Model Management Implementation

**Date Started:** February 19, 2026  
**Phase:** Stage 5, Phase 4 of 6  
**Status:** 🚀 IN PROGRESS  
**Estimated Duration:** 1 day  
**Overall Progress:** 66.7% → 83.3% (5/6 phases)

---

## Executive Summary

Stage 5 Phase 4 implements dynamic Ollama model management for the ELIXI AI assistant. This phase enables:

- **Multi-model support** - Switch between different Ollama models at runtime
- **Model discovery** - Automatically detect installed models
- **Model installation** - Download and install new models from registry
- **Performance monitoring** - Track model performance and type
- **Task-based selection** - Automatically select optimal model for task type
- **Resource optimization** - Monitor and optimize model memory usage

---

## Architecture Overview

### Module: `model_manager.py`

```
ModelManager
├── Model Discovery (Ollama API)
├── Model Status Tracking
├── Model Performance Monitor
├── Model Installation Handler
├── Task-to-Model Selector
└── Resource Monitor
```

### Key Features

| Feature | Description | Status |
|---------|-------------|--------|
| List Models | Get all available/installed models | 📋 Planning |
| Switch Model | Change active model at runtime | 📋 Planning |
| Get Status | Monitor current model performance | 📋 Planning |
| Download Model | Install new model from registry | 📋 Planning |
| Benchmarking | Measure model performance | 📋 Planning |
| Auto-select | Choose best model for task | 📋 Planning |

---

## API Endpoints (4 Total)

### 1. Get Available Models
```http
GET /ai/available-models

Response:
{
  "success": true,
  "data": {
    "installed": [
      {
        "name": "neural-chat",
        "size": "4B",
        "format": "gguf",
        "type": "general-purpose",
        "last_used": "2026-02-19T10:30:00Z",
        "performance": {
          "tokens_per_second": 45.3,
          "avg_latency_ms": 22.1,
          "memory_mb": 4096
        }
      },
      {
        "name": "mistral:7b",
        "size": "7B",
        "format": "gguf",
        "type": "code-generation",
        "last_used": "2026-02-19T09:15:00Z",
        "performance": {
          "tokens_per_second": 28.5,
          "avg_latency_ms": 35.2,
          "memory_mb": 7168
        }
      }
    ],
    "available": [
      {
        "name": "llama2",
        "size": "7B",
        "description": "General purpose model",
        "popularity": 5,
        "source": "ollama"
      },
      {
        "name": "codellama",
        "size": "7B",
        "description": "Code generation model",
        "popularity": 4,
        "source": "ollama"
      }
    ],
    "active_model": "neural-chat"
  },
  "timestamp": "2026-02-19T10:45:32Z"
}
```

### 2. Switch Model
```http
POST /ai/switch-model

Request:
{
  "model_name": "mistral:7b",
  "auto_pull": true
}

Response:
{
  "success": true,
  "data": {
    "previous_model": "neural-chat",
    "current_model": "mistral:7b",
    "status": "active",
    "load_time_ms": 234
  },
  "message": "Successfully switched to mistral:7b"
}
```

### 3. Get Model Status
```http
GET /ai/model-status

Response:
{
  "success": true,
  "data": {
    "current_model": "mistral:7b",
    "status": "active",
    "uptime_seconds": 3600,
    "performance": {
      "tokens_per_second": 28.5,
      "avg_latency_ms": 35.2,
      "error_rate": 0.02,
      "total_requests": 1250
    },
    "resource_usage": {
      "memory_mb": 7168,
      "cpu_percent": 35.2,
      "memory_percent": 45.3
    },
    "capabilities": {
      "type": "code-generation",
      "supports": ["python", "javascript", "rust", "go"],
      "max_context": 4096,
      "quantization": "Q4_K_M"
    }
  }
}
```

### 4. Download/Install Model
```http
POST /ai/download-model

Request:
{
  "model_name": "llama2:7b",
  "auto_switch": false
}

Response:
{
  "success": true,
  "data": {
    "model_name": "llama2:7b",
    "status": "downloading",
    "progress": 45,
    "download_size": "3.8 GB",
    "estimated_time_seconds": 120,
    "install_path": "/users/dell/.ollama/models/llama2:7b"
  },
  "message": "Download in progress..."
}
```

---

## Implementation Details

### Model Manager Class Structure

```python
class ModelManager(BaseAnalyzer):
    """Ollama model management and optimization"""
    
    def __init__(self, ollama_brain):
        """Initialize with OllamaAIBrain instance"""
        
    def get_available_models(self):
        """List installed and available models"""
        
    def get_installed_models(self):
        """Get locally installed models"""
        
    def get_model_performance(self, model_name):
        """Get performance metrics for model"""
        
    def switch_model(self, model_name, auto_pull=False):
        """Switch to different model"""
        
    def download_model(self, model_name, auto_switch=False):
        """Download and install model"""
        
    def get_current_status(self):
        """Get current model status & performance"""
        
    def benchmark_model(self, model_name, test_prompts=None):
        """Run performance benchmark"""
        
    def select_best_model(self, task_type):
        """Auto-select best model for task"""
```

### Performance Tracking

Models will be benchmarked on:
- **Tokens per second** - Generation speed
- **Latency** - Response time
- **Accuracy** - Answer quality (via LLM evaluation)
- **Memory efficiency** - RAM/VRAM usage
- **Error rate** - Failures and timeouts

---

## Integration Points

### With OllamaAIBrain
- Use existing Ollama API calls
- Share model list and status endpoints
- Extend with model switching logic

### With Stage5 Cache
- Cache model performance data (24hr TTL)
- Store benchmark results in MongoDB
- Track model usage history

### With Main.py
- Lazy-load ModelManager instance
- Add model management routes
- Integrate with API router

---

## Database Schema

### Models Performance Collection
```json
{
  "_id": "uuid",
  "model_name": "mistral:7b",
  "timestamp": "2026-02-19T10:45:32Z",
  "performance": {
    "tokens_per_second": 28.5,
    "avg_latency_ms": 35.2,
    "error_rate": 0.02,
    "total_requests": 1250
  },
  "resource_usage": {
    "memory_mb": 7168,
    "cpu_percent": 35.2,
    "memory_percent": 45.3
  },
  "benchmarks": {
    "general_purpose": 85,
    "coding": 92,
    "creativity": 78
  },
  "task_suitability": {
    "general": 8.5,
    "coding": 9.2,
    "analysis": 8.1,
    "creative": 7.8
  }
}
```

---

## Testing Strategy

### Unit Tests
- Model list retrieval
- Model switching logic
- Status calculation
- Model selection algorithm
- Error handling

### Integration Tests
- Ollama API communication
- Model download process
- Performance data storage
- Multi-model switching

### Performance Tests
- Benchmark timing
- Memory profiling
- Concurrent model access
- Cache effectiveness

---

## Success Criteria

- ✅ All 4 API endpoints operational
- ✅ Multi-model switching working <1 second
- ✅ Performance tracking accurate
- ✅ 90%+ test coverage
- ✅ Model discovery complete
- ✅ Error handling robust
- ✅ Documentation comprehensive

---

## Dependencies

| Package | Purpose | Status |
|---------|---------|--------|
| ollama | Model management | Already installed |
| psutil | Resource monitoring | Already installed |
| requests | API calls | Already installed |
| pymongo | Data storage | Already installed |
| stage5_utils | Caching/logging | Created Phase 0 |
| stage5_base | Base classes | Created Phase 0 |

---

## Timeline

- **Day 1 (Feb 19)**
  - 09:00 - Documentation & planning
  - 10:00 - Core model_manager.py implementation
  - 12:00 - API endpoint integration
  - 14:00 - Testing & benchmarking
  - 16:00 - Documentation completion

---

## Next Phase (Phase 5)

After Phase 4 completion:
- **Phase 5: UI Enhancements**
  - Floating window component
  - Background mode implementation
  - System tray integration
  - Auto-start configuration

---

## Current Status

**Phase 4 Progress:** 10% (Just started)
- ✅ Documentation created
- ⏳ Implementation pending
- ⏳ Testing pending
- ⏳ Integration pending
