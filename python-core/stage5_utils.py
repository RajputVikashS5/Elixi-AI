"""
Stage 5 Utility Functions - Shared across all Stage 5 modules
Provides common functionality for screen analysis, caching, and API integration
"""

import os
import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List


class CacheManager:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, mongodb=None):
        """Initialize cache manager.
        
        Args:
            mongodb: MongoDB connection for persistent cache
        """
        self.memory_cache = {}
        self.mongodb = mongodb
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache (memory first, then MongoDB)."""
        # Check memory cache first
        if key in self.memory_cache:
            cache_item = self.memory_cache[key]
            if cache_item['expires'] > datetime.now():
                return cache_item['value']
            else:
                del self.memory_cache[key]
        
        # Check MongoDB persistent cache
        if self.mongodb:
            try:
                db = self.mongodb.db
                cache_doc = db.cache.find_one({'key': key})
                if cache_doc and cache_doc.get('expires'):
                    if cache_doc['expires'] > datetime.now():
                        return cache_doc['value']
            except Exception as e:
                print(f"[Warning] MongoDB cache query failed: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl_minutes: int = 60, persistent: bool = False):
        """Set cache value with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_minutes: Time to live in minutes
            persistent: Also save to MongoDB
        """
        expires = datetime.now() + timedelta(minutes=ttl_minutes)
        
        # Store in memory
        self.memory_cache[key] = {
            'value': value,
            'expires': expires
        }
        
        # Store in MongoDB if enabled
        if persistent and self.mongodb:
            try:
                db = self.mongodb.db
                db.cache.update_one(
                    {'key': key},
                    {
                        '$set': {
                            'value': value,
                            'expires': expires,
                            'created_at': datetime.now()
                        }
                    },
                    upsert=True
                )
            except Exception as e:
                print(f"[Warning] Failed to save to MongoDB cache: {e}")
    
    def clear(self, key: Optional[str] = None):
        """Clear cache entries."""
        if key:
            self.memory_cache.pop(key, None)
            if self.mongodb:
                try:
                    self.mongodb.db.cache.delete_one({'key': key})
                except Exception as e:
                    print(f"[Warning] Failed to delete from MongoDB cache: {e}")
        else:
            self.memory_cache.clear()
    
    def cleanup_expired(self):
        """Remove expired entries from memory cache."""
        now = datetime.now()
        expired_keys = [k for k, v in self.memory_cache.items() if v['expires'] <= now]
        for key in expired_keys:
            del self.memory_cache[key]


class ResourceMonitor:
    """Monitor system resources for background mode optimization"""
    
    @staticmethod
    def get_memory_usage() -> float:
        """Get current memory usage percentage."""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except:
            return 0.0
    
    @staticmethod
    def get_cpu_usage() -> float:
        """Get current CPU usage percentage."""
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except:
            return 0.0
    
    @staticmethod
    def is_system_idle(idle_threshold_seconds: int = 300) -> bool:
        """Check if system is idle.
        
        Args:
            idle_threshold_seconds: Seconds of no input to consider idle
        """
        try:
            import win32api
            return win32api.GetTickCount() > idle_threshold_seconds * 1000
        except:
            return False
    
    @staticmethod
    def get_active_window_info() -> Dict[str, Any]:
        """Get information about active window."""
        try:
            import pygetwindow
            active_window = pygetwindow.getActiveWindow()
            if active_window:
                return {
                    'title': active_window.title,
                    'x': active_window.left,
                    'y': active_window.top,
                    'width': active_window.width,
                    'height': active_window.height
                }
        except:
            pass
        return {}


class TextProcessor:
    """Process and normalize text content"""
    
    @staticmethod
    def extract_code_blocks(text: str) -> List[str]:
        """Extract code blocks from text."""
        import re
        # Match markdown code blocks
        pattern = r'```(?:[a-z]+)?\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)
        return matches if matches else [text]
    
    @staticmethod
    def detect_language(code_snippet: str) -> str:
        """Detect programming language from code snippet."""
        keywords = {
            'python': ['def ', 'import ', 'from ', 'class ', 'if __name__'],
            'javascript': ['function ', 'const ', 'let ', 'var ', 'import ', 'export'],
            'java': ['public class ', 'public static void', 'new ', 'System.out'],
            'csharp': ['using ', 'public class ', 'public static void', 'namespace'],
            'cpp': ['#include', 'int main', 'std::', 'namespace'],
            'sql': ['SELECT ', 'FROM ', 'WHERE ', 'INSERT ', 'UPDATE'],
        }
        
        snippet_lower = code_snippet.lower()
        scores = {}
        
        for lang, lang_keywords in keywords.items():
            score = sum(1 for kw in lang_keywords if kw.lower() in snippet_lower)
            if score > 0:
                scores[lang] = score
        
        if scores:
            return max(scores, key=scores.get)
        return 'unknown'
    
    @staticmethod
    def sanitize_code(code: str) -> str:
        """Sanitize code for safe execution."""
        dangerous_patterns = [
            'os.system',
            '__import__',
            'eval(',
            'exec(',
            'subprocess',
            'open(',
        ]
        
        result = code
        for pattern in dangerous_patterns:
            if pattern in result:
                result = result.replace(pattern, f'# BLOCKED: {pattern}')
        
        return result


class APIResponseFormatter:
    """Format consistent API responses"""
    
    @staticmethod
    def success(data: Any, message: str = "Success") -> Dict:
        """Format success response."""
        return {
            'status': 'success',
            'message': message,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def error(message: str, error_code: str = "UNKNOWN_ERROR", details: Optional[Dict] = None) -> Dict:
        """Format error response."""
        return {
            'status': 'error',
            'message': message,
            'error_code': error_code,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def partial(data: Any, message: str = "Partial results") -> Dict:
        """Format partial success response."""
        return {
            'status': 'partial',
            'message': message,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }


class ConfigLoader:
    """Load and manage Stage 5 configuration"""
    
    _config = None
    
    @classmethod
    def load(cls) -> Dict:
        """Load configuration from environment and config files."""
        if cls._config:
            return cls._config
        
        config = {
            # Screen Analysis
            'screen_analysis_enabled': os.getenv('SCREEN_ANALYSIS_ENABLED', 'true').lower() == 'true',
            'screen_cache_ttl': int(os.getenv('SCREEN_CACHE_TTL', '5')),  # minutes
            'ocr_engine': os.getenv('OCR_ENGINE', 'easyocr'),  # easyocr or pytesseract
            
            # Coding Assistant
            'coding_assistant_enabled': os.getenv('CODING_ASSISTANT_ENABLED', 'true').lower() == 'true',
            'code_analysis_cache_ttl': int(os.getenv('CODE_ANALYSIS_CACHE_TTL', '30')),
            
            # News & Weather
            'news_weather_enabled': os.getenv('NEWS_WEATHER_ENABLED', 'true').lower() == 'true',
            'news_api_url': os.getenv('NEWS_API_URL', 'https://newsapi.org/v2'),
            'weather_api_url': os.getenv('WEATHER_API_URL', 'https://api.openweathermap.org'),
            'news_api_key': os.getenv('NEWS_API_KEY', ''),
            'weather_api_key': os.getenv('WEATHER_API_KEY', ''),
            
            # Ollama Models
            'ollama_enabled': os.getenv('OLLAMA_ENABLED', 'true').lower() == 'true',
            'ollama_api_url': os.getenv('OLLAMA_API_URL', 'http://localhost:11434'),
            'default_model': os.getenv('DEFAULT_MODEL', 'mistral'),
            
            # Background Mode
            'background_mode_enabled': os.getenv('BACKGROUND_MODE_ENABLED', 'false').lower() == 'true',
            'max_cpu_usage': float(os.getenv('MAX_CPU_USAGE', '5.0')),
            'max_memory_usage': float(os.getenv('MAX_MEMORY_USAGE', '150.0')),  # MB
        }
        
        cls._config = config
        return config
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get a specific config value."""
        config = cls.load()
        return config.get(key, default)


class Logger:
    """Simple logging utility for Stage 5"""
    
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    
    @staticmethod
    def log(level: str, component: str, message: str, details: Optional[Dict] = None):
        """Log a message."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] [{level}] [{component}] {message}"
        
        if level == 'ERROR':
            print(f"\033[91m{log_message}\033[0m")  # Red
        elif level == 'WARNING':
            print(f"\033[93m{log_message}\033[0m")  # Yellow
        elif level == 'DEBUG':
            print(f"\033[94m{log_message}\033[0m")  # Blue
        else:
            print(log_message)
        
        if details:
            print(f"  Details: {json.dumps(details, indent=2)}")
    
    @staticmethod
    def debug(component: str, message: str, details: Optional[Dict] = None):
        Logger.log(Logger.DEBUG, component, message, details)
    
    @staticmethod
    def info(component: str, message: str, details: Optional[Dict] = None):
        Logger.log(Logger.INFO, component, message, details)
    
    @staticmethod
    def warning(component: str, message: str, details: Optional[Dict] = None):
        Logger.log(Logger.WARNING, component, message, details)
    
    @staticmethod
    def error(component: str, message: str, details: Optional[Dict] = None):
        Logger.log(Logger.ERROR, component, message, details)


# Global cache instance
_cache_manager = None

def get_cache_manager(mongodb=None) -> CacheManager:
    """Get singleton cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager(mongodb)
    return _cache_manager
