# Stage 5 Quick Start Guide

**Status:** 🚀 Phase 0 - Foundation Complete  
**Date:** February 6, 2026  
**Version:** 0.1

---

## What is Stage 5?

Stage 5 transforms ELIXI into a **world-class Jarvis-level AI assistant** with advanced capabilities:
- 👁️ Screen Understanding (Computer Vision)
- 💻 Coding Assistant (Code Generation & Debugging)
- 📰 News & Weather Updates (Real-time Information)
- 🤖 Multiple AI Models (Ollama Support)
- 🎚️ Floating Interface (Window-less Overlay)
- 🔄 Always-On Background Mode (Persistent Operation)

---

## Current Status: Phase 0 ✅

**Completed:**
- ✅ Full implementation plan in STAGE5_IMPLEMENTATION.md
- ✅ Utility functions module (stage5_utils.py)
- ✅ Base analyzer classes (stage5_base.py)
- ✅ Configuration loader
- ✅ Cache manager system
- ✅ Logging framework
- ✅ Performance monitoring

**What You Get:**
- Reusable utility classes for all Stage 5 modules
- CacheManager with TTL and MongoDB persistence
- ResourceMonitor for system resource tracking
- TextProcessor for code/text analysis
- APIResponseFormatter for consistent responses
- BaseAnalyzer and BaseDataProcessor abstract classes
- PerformanceMonitor for tracking analysis performance

---

## Key Files Created

| File | Purpose | Lines |
|------|---------|-------|
| `STAGE5_IMPLEMENTATION.md` | Complete implementation roadmap | 350+ |
| `python-core/stage5_utils.py` | Shared utility functions | 380+ |
| `python-core/stage5_base.py` | Base classes for analyzers | 280+ |

---

## Next Steps: Phase 1 (Screen Understanding)

**Goal:** Build computer vision capabilities for screen analysis

**What Will Be Built:**
1. **screen_analyzer.py** - Main screen analysis engine
   - Screenshot capture
   - OCR text extraction
   - Window detection
   - AI-powered interpretation
   
2. **API Endpoints** (4 new)
   - `POST /vision/analyze-screen` - Analyze current screen
   - `POST /vision/get-screen-text` - Extract screen text
   - `POST /vision/identify-window` - Get window info
   - `GET /vision/screen-cache` - Get cached analysis

3. **Integration**
   - Add to main.py
   - MongoDB collection for cache
   - Tests and documentation

**Estimated Time:** 2-3 days

---

## Architecture Overview

```
┌─────────────────────────────────────────┐
│         Stage 5 Components              │
├─────────────────────────────────────────┤
│                                         │
│  Screen Analyzer     Coding Assistant   │
│       ↓                   ↓             │
│  ┌──────────────────────────────┐      │
│  │    Base Analyzer Classes     │      │
│  │    (stage5_base.py)          │      │
│  └──────────────────────────────┘      │
│             ↓                          │
│  ┌──────────────────────────────┐      │
│  │   Utility Functions          │      │
│  │   (stage5_utils.py)          │      │
│  │   - Caching                  │      │
│  │   - Logging                  │      │
│  │   - Config Loading           │      │
│  └──────────────────────────────┘      │
│             ↓                          │
│  ┌──────────────────────────────┐      │
│  │     MongoDB + Ollama         │      │
│  │   (Data & AI Models)         │      │
│  └──────────────────────────────┘      │
└─────────────────────────────────────────┘
```

---

## How to Use the Foundation Classes

### Using CacheManager

```python
from stage5_utils import get_cache_manager

cache = get_cache_manager(mongodb=db_connection)

# Set cache value (5-minute TTL, persistent)
cache.set('screen_analysis_1', {'text': 'Hello'}, ttl_minutes=5, persistent=True)

# Get cached value
result = cache.get('screen_analysis_1')

# Clear specific key
cache.clear('screen_analysis_1')
```

### Using BaseAnalyzer

```python
from stage5_base import BaseAnalyzer

class ScreenAnalyzer(BaseAnalyzer):
    def __init__(self, mongodb=None):
        super().__init__('ScreenAnalyzer', mongodb)
    
    def analyze(self, screenshot_path):
        # Validate input
        if not self.validate_input({'path': screenshot_path}):
            return self.format_error("Invalid input")
        
        # Check cache
        cache_key = self.get_cache_key(path=screenshot_path)
        cached = self.get_cached_result(cache_key)
        if cached:
            return self.format_success(cached, "From cache")
        
        # Perform analysis
        result = {'text': 'Extracted text'}
        
        # Cache result
        self.cache_result(cache_key, result, ttl_minutes=5)
        
        return self.format_success(result)

# Usage
analyzer = ScreenAnalyzer(mongodb=db_connection)
result = analyzer.analyze('screenshot.png')
```

### Using Logger

```python
from stage5_utils import Logger

Logger.info('ScreenAnalyzer', 'Analysis started')
Logger.debug('ScreenAnalyzer', 'Debug info', {'key': 'value'})
Logger.warning('ScreenAnalyzer', 'Low confidence')
Logger.error('ScreenAnalyzer', 'Analysis failed', {'code': 'OCR_ERROR'})
```

### Using ConfigLoader

```python
from stage5_utils import ConfigLoader

config = ConfigLoader.load()
ocr_engine = config['ocr_engine']  # 'easyocr' or 'pytesseract'

# Or get specific value
enabled = ConfigLoader.get('screen_analysis_enabled', default=True)
```

---

## Configuration

Create a `.env` file in the project root with these variables:

```env
# Screen Analysis
SCREEN_ANALYSIS_ENABLED=true
SCREEN_CACHE_TTL=5
OCR_ENGINE=easyocr

# Coding Assistant
CODING_ASSISTANT_ENABLED=true
CODE_ANALYSIS_CACHE_TTL=30

# News & Weather
NEWS_WEATHER_ENABLED=true
NEWS_API_KEY=your_newsapi_key
WEATHER_API_KEY=your_openweather_key

# Ollama
OLLAMA_ENABLED=true
OLLAMA_API_URL=http://localhost:11434
DEFAULT_MODEL=mistral

# Background Mode
BACKGROUND_MODE_ENABLED=false
MAX_CPU_USAGE=5.0
MAX_MEMORY_USAGE=150.0
```

---

## Dependencies to Install

Before Phase 1 starts, ensure these are installed:

```bash
# Screen Analysis
pip install pillow pytesseract easyocr pyautogui pygetwindow

# Code Analysis
pip install ast linter

# News/Weather
pip install requests pytz

# System Control
pip install pystray psutil

# Optional but recommended
pip install redis
```

---

## Testing the Foundation

To verify the foundation is working correctly:

```python
# test_stage5_foundation.py
from stage5_utils import (
    CacheManager, Logger, ConfigLoader, TextProcessor,
    APIResponseFormatter, ResourceMonitor
)
from stage5_base import BaseAnalyzer, AnalysisResult

def test_cache():
    cache = CacheManager()
    cache.set('test', {'data': 'value'})
    assert cache.get('test') == {'data': 'value'}
    print("✅ Cache manager working")

def test_config():
    config = ConfigLoader.load()
    assert 'ollama_api_url' in config
    print("✅ Config loader working")

def test_logger():
    Logger.info('Test', 'Testing logger')
    print("✅ Logger working")

def test_response_formatter():
    success = APIResponseFormatter.success({'result': 123})
    assert success['status'] == 'success'
    print("✅ Response formatter working")

if __name__ == '__main__':
    test_cache()
    test_config()
    test_logger()
    test_response_formatter()
    print("\n🎉 All foundation tests passed!")
```

---

## Phase Timeline

| Phase | Duration | Status | Features |
|-------|----------|--------|----------|
| Phase 0 | ✅ Complete | ✅ | Foundation & utilities |
| Phase 1 | 2-3 days | ⏳ | Screen Understanding |
| Phase 2 | 2-3 days | ⏳ | Coding Assistant |
| Phase 3 | 1-2 days | ⏳ | News & Weather |
| Phase 4 | 1 day | ⏳ | Model Management |
| Phase 5 | 2 days | ⏳ | UI & Background Mode |
| **Total** | **~10 days** | **In Progress** | **Complete Stage 5** |

---

## Getting Started with Phase 1

1. Read [STAGE5_IMPLEMENTATION.md](STAGE5_IMPLEMENTATION.md) Phase 1 section
2. Create `screen_analyzer.py` in `python-core/`
3. Implement `ScreenAnalyzer` class extending `BaseAnalyzer`
4. Add API endpoints to `main.py`
5. Write tests in `test_screen_analyzer.py`
6. Update requirements with new OCR dependencies

---

## Key Concepts

### Analyzer Pattern
All Stage 5 analysis modules follow the same pattern:
1. Extend `BaseAnalyzer`
2. Implement `analyze()` method
3. Use caching for performance
4. Return `AnalysisResult` or formatted response

### Caching Strategy
- **Memory Cache**: Fast, in-process (TTL-based expiration)
- **MongoDB Cache**: Persistent, survives restarts
- **Strategy**: Always check cache first before expensive operations

### Error Handling
- Use `format_error()` for consistent error responses
- Log errors with `Logger.error()`
- Gracefully degrade when external APIs fail

### Configuration
- All options load from `.env` file
- Defaults are sensible (offline-first approach)
- Use `ConfigLoader` for type-safe access

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'stage5_utils'"
- Ensure you're running from `python-core/` directory
- Files must be in same directory as `main.py`

### Cache not persisting
- Verify MongoDB connection is initialized
- Check that `persistent=True` when calling `cache.set()`

### Performance issues
- Use `get_performance_monitor()` to check analyzer speeds
- Increase TTL for cache to reduce re-analysis

---

## Documentation Structure

```
STAGE5_IMPLEMENTATION.md  - Full technical design (350+ lines)
STAGE5_QUICKSTART.md      - This file, quick reference
STAGE5_API_REFERENCE.md   - API documentation (coming Phase 1)
STAGE5_PHASE_REPORTS/     - Per-phase completion reports
```

---

## Questions?

Refer to:
- [STAGE5_IMPLEMENTATION.md](STAGE5_IMPLEMENTATION.md) - Design decisions & architecture
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - How to add new features
- [STAGE4_API_REFERENCE.md](STAGE4_API_REFERENCE.md) - API patterns (same patterns used in Stage 5)

---

## Next Milestone

**Ready to Start Phase 1?**
- ✅ Foundation complete (stage5_utils.py, stage5_base.py)
- ✅ Infrastructure ready (CacheManager, Logger, Config)
- ✅ Architecture documented
- **⏳ Next: Screen Understanding module**

**Estimated Start:** Phase 1 begins as soon as Phase 0 testing is complete!
