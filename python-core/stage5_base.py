"""
Base Analyzer Class - Foundation for all Stage 5 analysis modules
Provides common functionality for screen, code, and data analysis
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from datetime import datetime
from stage5_utils import Logger, CacheManager, APIResponseFormatter, ConfigLoader


class BaseAnalyzer(ABC):
    """Abstract base class for all Stage 5 analyzers"""
    
    def __init__(self, name: str, mongodb=None, enable_cache: bool = True):
        """Initialize base analyzer.
        
        Args:
            name: Name of analyzer (for logging)
            mongodb: MongoDB connection
            enable_cache: Whether to use caching
        """
        self.name = name
        self.mongodb = mongodb
        self.enable_cache = enable_cache
        self.cache = None
        self.config = ConfigLoader.load()
        
        if enable_cache:
            self.cache = CacheManager(mongodb)
        
        Logger.info(self.name, "Initialized")
    
    @abstractmethod
    def analyze(self, input_data: Any) -> Dict[str, Any]:
        """Analyze input data. Must be implemented by subclass.
        
        Args:
            input_data: Data to analyze
            
        Returns:
            Analysis results
        """
        pass
    
    def get_cache_key(self, **kwargs) -> str:
        """Generate cache key from parameters."""
        import hashlib
        import json
        key_string = json.dumps(kwargs, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def cache_result(self, cache_key: str, result: Dict, ttl_minutes: int = 60):
        """Cache analysis result."""
        if self.enable_cache and self.cache:
            self.cache.set(
                cache_key,
                result,
                ttl_minutes=ttl_minutes,
                persistent=True
            )
    
    def get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Retrieve cached result."""
        if self.enable_cache and self.cache:
            return self.cache.get(cache_key)
        return None
    
    def validate_input(self, input_data: Any, required_fields: List[str] = None) -> bool:
        """Validate input data."""
        if input_data is None:
            Logger.warning(self.name, "Input data is None")
            return False
        
        if not isinstance(input_data, dict) and required_fields:
            Logger.warning(self.name, "Input is not a dictionary")
            return False
        
        if required_fields:
            missing = [f for f in required_fields if f not in input_data]
            if missing:
                Logger.warning(self.name, f"Missing fields: {missing}")
                return False
        
        return True
    
    def format_success(self, data: Any, message: str = "Analysis successful") -> Dict:
        """Format successful analysis response."""
        return APIResponseFormatter.success(data, message)
    
    def format_error(self, message: str, error_code: str = "ANALYSIS_ERROR") -> Dict:
        """Format error response."""
        Logger.error(self.name, message)
        return APIResponseFormatter.error(message, error_code)
    
    def log_analysis(self, input_summary: str, result_summary: str, duration_ms: float):
        """Log analysis completion."""
        Logger.info(
            self.name,
            f"Analysis complete",
            {
                'input': input_summary,
                'result': result_summary,
                'duration_ms': duration_ms
            }
        )


class BaseDataProcessor(ABC):
    """Abstract base class for data processing in Stage 5"""
    
    def __init__(self, name: str, mongodb=None):
        """Initialize data processor.
        
        Args:
            name: Name of processor
            mongodb: MongoDB connection
        """
        self.name = name
        self.mongodb = mongodb
        self.config = ConfigLoader.load()
        Logger.info(self.name, "Initialized")
    
    @abstractmethod
    def process(self, data: Any) -> Any:
        """Process data. Must be implemented by subclass."""
        pass
    
    def validate_data(self, data: Any) -> bool:
        """Validate data before processing."""
        if data is None:
            Logger.warning(self.name, "Data is None")
            return False
        return True
    
    def save_to_db(self, collection_name: str, data: Dict) -> bool:
        """Save processed data to MongoDB."""
        if not self.mongodb:
            Logger.warning(self.name, "MongoDB not initialized")
            return False
        
        try:
            db = self.mongodb.db
            collection = db[collection_name]
            result = collection.insert_one(data)
            Logger.debug(self.name, f"Saved to {collection_name}", {'id': str(result.inserted_id)})
            return True
        except Exception as e:
            Logger.error(self.name, f"Failed to save to MongoDB: {e}")
            return False
    
    def update_db(self, collection_name: str, query: Dict, data: Dict) -> bool:
        """Update data in MongoDB."""
        if not self.mongodb:
            Logger.warning(self.name, "MongoDB not initialized")
            return False
        
        try:
            db = self.mongodb.db
            collection = db[collection_name]
            result = collection.update_one(query, {'$set': data}, upsert=True)
            Logger.debug(self.name, f"Updated {collection_name}")
            return True
        except Exception as e:
            Logger.error(self.name, f"Failed to update MongoDB: {e}")
            return False


class AnalysisResult:
    """Standard result object for all analyses"""
    
    def __init__(
        self,
        success: bool,
        data: Any = None,
        message: str = "",
        error_code: str = "",
        metadata: Dict = None
    ):
        """Initialize analysis result.
        
        Args:
            success: Whether analysis succeeded
            data: Result data
            message: Status message
            error_code: Error code if failed
            metadata: Additional metadata
        """
        self.success = success
        self.data = data
        self.message = message
        self.error_code = error_code
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'success': self.success,
            'data': self.data,
            'message': self.message,
            'error_code': self.error_code,
            'metadata': self.metadata,
            'timestamp': self.timestamp
        }
    
    def to_json_response(self) -> Dict:
        """Convert to API JSON response."""
        if self.success:
            return APIResponseFormatter.success(self.data, self.message)
        else:
            return APIResponseFormatter.error(self.message, self.error_code, self.metadata)


class PerformanceMonitor:
    """Monitor performance of analyzers"""
    
    def __init__(self):
        self.metrics = {}
    
    def record(self, analyzer_name: str, duration_ms: float, success: bool = True):
        """Record analyzer performance."""
        if analyzer_name not in self.metrics:
            self.metrics[analyzer_name] = {
                'count': 0,
                'total_time': 0,
                'avg_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'errors': 0
            }
        
        m = self.metrics[analyzer_name]
        m['count'] += 1
        m['total_time'] += duration_ms
        m['avg_time'] = m['total_time'] / m['count']
        m['min_time'] = min(m['min_time'], duration_ms)
        m['max_time'] = max(m['max_time'], duration_ms)
        
        if not success:
            m['errors'] += 1
    
    def get_metrics(self, analyzer_name: str = None) -> Dict:
        """Get performance metrics."""
        if analyzer_name:
            return self.metrics.get(analyzer_name, {})
        return self.metrics
    
    def reset(self):
        """Reset all metrics."""
        self.metrics = {}


# Global performance monitor
_monitor = PerformanceMonitor()

def get_performance_monitor() -> PerformanceMonitor:
    """Get singleton performance monitor."""
    return _monitor
