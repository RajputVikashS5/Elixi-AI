"""
Stage 5 Phase 4: Model Manager
Ollama model management, switching, and performance monitoring

Author: ELIXI AI Development Team
Date: February 19, 2026
"""

import json
import time
import subprocess
import os
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import requests

from stage5_base import BaseAnalyzer, AnalysisResult
from stage5_utils import CacheManager, Logger, APIResponseFormatter


class LoggerWrapper:
    """Wrapper for Logger to provide instance-like interface"""
    def __init__(self, component: str):
        self.component = component
    
    def info(self, message: str, details=None):
        Logger.info(self.component, message, details)
    
    def warning(self, message: str, details=None):
        Logger.warning(self.component, message, details)
    
    def error(self, message: str, details=None):
        Logger.error(self.component, message, details)
    
    def debug(self, message: str, details=None):
        Logger.debug(self.component, message, details)


class ModelManager(BaseAnalyzer):
    """
    Ollama model management and optimization engine
    
    Handles:
    - Model discovery (installed & available)
    - Model switching at runtime
    - Performance monitoring
    - Benchmarking
    - Task-based model selection
    - Resource monitoring
    """
    
    def __init__(self, ollama_brain=None, ollama_base_url: str = "http://localhost:11434"):
        """
        Initialize ModelManager
        
        Args:
            ollama_brain: Reference to OllamaAIBrain instance (optional)
            ollama_base_url: Base URL for Ollama API
        """
        super().__init__(name="ModelManager")
        
        self.ollama_brain = ollama_brain
        self.ollama_base_url = ollama_base_url
        self.ollama_api = f"{ollama_base_url}/api"
        
        self.logger = LoggerWrapper("ModelManager")
        self.cache = CacheManager()
        self.formatter = APIResponseFormatter()
        
        # Model metadata
        self.model_types = {
            "general": {"models": ["neural-chat", "mistral", "llama2", "orca"], "uses": "General conversation"},
            "coding": {"models": ["codellama", "mistral-7b-instruct"], "uses": "Code generation & debugging"},
            "analysis": {"models": ["neural-chat", "orca-mini"], "uses": "Text analysis & reasoning"},
            "creative": {"models": ["ollama-neural-chat"], "uses": "Creative writing & generation"},
            "fast": {"models": ["orca-mini", "neural-chat:3.8b"], "uses": "Quick responses"},
        }
        
        # Performance tracking
        self.perf_data = {}
        self.current_model = None
        self._session_start = time.time()
        
        self.logger.info("ModelManager initialized")
    
    # ============================================================
    # Model Discovery
    # ============================================================
    
    def get_available_models(self) -> Dict:
        """
        Get all available models (installed + available in registry)
        
        Returns:
            Dict with installed and available models
        """
        try:
            installed = self._get_installed_models()
            available = self._get_available_models_from_registry()
            
            return {
                "installed": installed,
                "available": available,
                "active_model": self.current_model or "unknown"
            }
        except Exception as e:
            self.logger.error(f"Error getting available models: {e}")
            return {
                "installed": [],
                "available": [],
                "active_model": "error",
                "error": str(e)
            }
    
    def _get_installed_models(self) -> List[Dict]:
        """
        Get list of installed models from Ollama
        
        Returns:
            List of installed model info dicts
        """
        try:
            response = requests.get(
                f"{self.ollama_api}/tags",
                timeout=5
            )
            
            if response.status_code != 200:
                self.logger.warning(f"Ollama API returned {response.status_code}")
                return []
            
            data = response.json()
            models = data.get("models", [])
            
            installed = []
            for model in models:
                model_info = {
                    "name": model.get("name", "unknown"),
                    "size": self._format_size(model.get("size", 0)),
                    "modified": model.get("modified_at", ""),
                    "format": model.get("details", {}).get("format", "gguf"),
                    "type": self._classify_model_type(model.get("name", "")),
                }
                
                # Get performance data if available
                perf = self._get_model_performance(model.get("name", ""))
                if perf:
                    model_info["performance"] = perf
                
                installed.append(model_info)
            
            self.logger.info(f"Found {len(installed)} installed models")
            return installed
            
        except requests.exceptions.ConnectionError:
            self.logger.warning("Cannot connect to Ollama API")
            return []
        except Exception as e:
            self.logger.error(f"Error getting installed models: {e}")
            return []
    
    def _get_available_models_from_registry(self) -> List[Dict]:
        """
        Get available models from Ollama registry
        
        Returns:
            List of available model info dicts
        """
        # Common models available in Ollama registry
        registry_models = [
            {
                "name": "llama2",
                "size": "7B",
                "description": "Meta's Llama 2 - General purpose model",
                "popularity": 5,
                "type": "general"
            },
            {
                "name": "mistral",
                "size": "7B",
                "description": "Mistral 7B - Fast and accurate",
                "popularity": 5,
                "type": "general"
            },
            {
                "name": "neural-chat",
                "size": "7B",
                "description": "Intel's Neural Chat - Optimized conversation",
                "popularity": 4,
                "type": "general"
            },
            {
                "name": "codellama",
                "size": "7B",
                "description": "Code Llama - Code generation specialist",
                "popularity": 4,
                "type": "coding"
            },
            {
                "name": "orca-mini",
                "size": "3B",
                "description": "Orca Mini - Fast and lightweight",
                "popularity": 3,
                "type": "fast"
            },
            {
                "name": "dolphin-mixtral",
                "size": "7B",
                "description": "Dolphin Mixtral - Creative and versatile",
                "popularity": 4,
                "type": "creative"
            },
            {
                "name": "openchat",
                "size": "7B",
                "description": "OpenChat - Optimized for chat",
                "popularity": 3,
                "type": "general"
            },
            {
                "name": "starling-lm",
                "size": "7B",
                "description": "Starling - High quality responses",
                "popularity": 3,
                "type": "general"
            }
        ]
        
        return registry_models
    
    # ============================================================
    # Model Switching
    # ============================================================
    
    def switch_model(self, model_name: str, auto_pull: bool = False) -> Dict:
        """
        Switch to a different model
        
        Args:
            model_name: Name of the model to switch to
            auto_pull: Whether to auto-pull if not installed
            
        Returns:
            Dict with switch status
        """
        try:
            start_time = time.time()
            previous_model = self.current_model
            
            # Check if model is installed
            installed = self._get_installed_models()
            model_names = [m["name"] for m in installed]
            
            if model_name not in model_names:
                if auto_pull:
                    self.logger.info(f"Model {model_name} not found, attempting to pull...")
                    pull_result = self._pull_model(model_name)
                    if not pull_result:
                        return {
                            "success": False,
                            "error": f"Failed to pull model {model_name}"
                        }
                else:
                    return {
                        "success": False,
                        "error": f"Model {model_name} not installed. Use auto_pull=True to install."
                    }
            
            # Update current model
            self.current_model = model_name
            
            # Update Ollama brain if available
            if self.ollama_brain:
                self.ollama_brain.model = model_name
            
            load_time = (time.time() - start_time) * 1000  # Convert to ms
            
            self.logger.info(f"Switched from {previous_model} to {model_name} ({load_time:.1f}ms)")
            
            return {
                "success": True,
                "previous_model": previous_model,
                "current_model": model_name,
                "status": "active",
                "load_time_ms": round(load_time, 1)
            }
            
        except Exception as e:
            self.logger.error(f"Error switching model: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ============================================================
    # Model Installation
    # ============================================================
    
    def download_model(self, model_name: str, auto_switch: bool = False) -> Dict:
        """
        Download and install a new model
        
        Args:
            model_name: Name of model to download
            auto_switch: Whether to switch to model after download
            
        Returns:
            Dict with download status
        """
        try:
            self.logger.info(f"Starting download of {model_name}...")
            
            result = self._pull_model(model_name)
            
            if not result:
                return {
                    "success": False,
                    "error": f"Failed to download {model_name}"
                }
            
            if auto_switch:
                switch_result = self.switch_model(model_name)
                if not switch_result["success"]:
                    return switch_result
            
            self.logger.info(f"Successfully downloaded {model_name}")
            
            return {
                "success": True,
                "model_name": model_name,
                "status": "installed",
                "auto_switched": auto_switch
            }
            
        except Exception as e:
            self.logger.error(f"Error downloading model: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _pull_model(self, model_name: str) -> bool:
        """
        Pull model from Ollama registry (blocking)
        
        Args:
            model_name: Name of model to pull
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.ollama_api}/pull",
                json={"name": model_name},
                timeout=3600  # 1 hour timeout for downloads
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Failed to pull model {model_name}: {e}")
            return False
    
    # ============================================================
    # Model Status & Performance
    # ============================================================
    
    def get_current_status(self) -> Dict:
        """
        Get current model status and performance metrics
        
        Returns:
            Dict with model status and performance data
        """
        try:
            if not self.current_model:
                # Detect current model from Ollama
                self._detect_current_model()
            
            model_name = self.current_model or "unknown"
            uptime = time.time() - self._session_start
            
            perf = self._get_model_performance(model_name) or {}
            resource_usage = self._get_resource_usage()
            
            return {
                "success": True,
                "current_model": model_name,
                "data": {
                    "status": "active",
                    "uptime_seconds": int(uptime),
                    "performance": {
                        "tokens_per_second": perf.get("tokens_per_second", 0),
                        "avg_latency_ms": perf.get("avg_latency_ms", 0),
                        "error_rate": perf.get("error_rate", 0),
                        "total_requests": perf.get("total_requests", 0)
                    },
                    "resource_usage": resource_usage,
                    "capabilities": self._get_model_capabilities(model_name)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_model_performance(self, model_name: str) -> Optional[Dict]:
        """
        Get cached performance data for a model
        
        Args:
            model_name: Name of the model
            
        Returns:
            Performance metrics dict or None
        """
        try:
            cache_key = f"model_perf_{model_name}"
            cached = self.cache.get(cache_key)
            if cached:
                return cached
            
            # Return None if not cached (will use defaults)
            return None
            
        except Exception as e:
            self.logger.warning(f"Error getting performance data: {e}")
            return None
    
    def _get_resource_usage(self) -> Dict:
        """
        Get current system resource usage
        
        Returns:
            Dict with CPU and memory metrics
        """
        try:
            process = psutil.Process(os.getpid())
            
            return {
                "memory_mb": int(process.memory_info().rss / 1024 / 1024),
                "cpu_percent": process.cpu_percent(interval=0.1),
                "memory_percent": process.memory_percent()
            }
        except Exception as e:
            self.logger.warning(f"Error getting resource usage: {e}")
            return {
                "memory_mb": 0,
                "cpu_percent": 0,
                "memory_percent": 0
            }
    
    def _get_model_capabilities(self, model_name: str) -> Dict:
        """
        Get model capabilities
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dict with model capabilities
        """
        model_lower = model_name.lower()
        
        # Default capabilities
        capabilities = {
            "type": self._classify_model_type(model_name),
            "supports": ["general"],
            "max_context": 4096,
            "quantization": "Q4_K_M"
        }
        
        # Model-specific capabilities
        if "code" in model_lower:
            capabilities["supports"] = ["python", "javascript", "rust", "go", "java", "cpp"]
        elif "mistral" in model_lower:
            capabilities["supports"] = ["python", "javascript", "general"]
        elif "neural" in model_lower:
            capabilities["supports"] = ["general", "analysis"]
        
        return capabilities
    
    # ============================================================
    # Benchmarking
    # ============================================================
    
    def benchmark_model(self, model_name: str, num_prompts: int = 5) -> Dict:
        """
        Run performance benchmark on a model
        
        Args:
            model_name: Name of the model to benchmark
            num_prompts: Number of test prompts to use
            
        Returns:
            Dict with benchmark results
        """
        try:
            self.logger.info(f"Starting benchmark for {model_name}...")
            
            test_prompts = [
                "What is the capital of France?",
                "Explain quantum computing in simple terms.",
                "Write a Python function to sort a list.",
                "What are the benefits of exercise?",
                "How does photosynthesis work?"
            ][:num_prompts]
            
            results = {
                "model_name": model_name,
                "timestamp": datetime.now().isoformat(),
                "prompts_tested": len(test_prompts),
                "results": []
            }
            
            total_tokens = 0
            total_time = 0
            errors = 0
            
            for i, prompt in enumerate(test_prompts):
                try:
                    start_time = time.time()
                    
                    response = requests.post(
                        f"{self.ollama_api}/generate",
                        json={
                            "model": model_name,
                            "prompt": prompt,
                            "stream": False
                        },
                        timeout=60
                    )
                    
                    elapsed = time.time() - start_time
                    
                    if response.status_code == 200:
                        data = response.json()
                        tokens = data.get("eval_count", 0)
                        total_tokens += tokens
                        total_time += elapsed
                        
                        results["results"].append({
                            "prompt_index": i,
                            "tokens": tokens,
                            "time_ms": round(elapsed * 1000, 1),
                            "tokens_per_sec": round(tokens / elapsed, 2) if elapsed > 0 else 0
                        })
                    else:
                        errors += 1
                        
                except Exception as e:
                    self.logger.warning(f"Benchmark prompt {i} failed: {e}")
                    errors += 1
            
            # Calculate aggregate metrics
            avg_tokens_per_sec = total_tokens / total_time if total_time > 0 else 0
            error_rate = errors / len(test_prompts) if test_prompts else 0
            
            results["summary"] = {
                "total_tokens": total_tokens,
                "total_time_seconds": round(total_time, 2),
                "avg_tokens_per_second": round(avg_tokens_per_sec, 2),
                "avg_latency_ms": round((total_time / len(test_prompts)) * 1000, 1) if test_prompts else 0,
                "error_rate": round(error_rate, 3),
                "successful_prompts": len(test_prompts) - errors
            }
            
            self.logger.info(f"Benchmark complete: {avg_tokens_per_sec:.2f} tokens/sec")
            
            # Cache results
            cache_key = f"model_perf_{model_name}"
            self.cache.set(
                cache_key,
                {
                    "tokens_per_second": results["summary"]["avg_tokens_per_second"],
                    "avg_latency_ms": results["summary"]["avg_latency_ms"],
                    "error_rate": results["summary"]["error_rate"],
                    "total_requests": len(test_prompts)
                }
            )
            
            return {
                "success": True,
                "data": results
            }
            
        except Exception as e:
            self.logger.error(f"Error benchmarking model: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ============================================================
    # Model Selection
    # ============================================================
    
    def select_best_model(self, task_type: str = "general") -> Optional[str]:
        """
        Select the best model for a given task type
        
        Args:
            task_type: Type of task (general, coding, analysis, creative, fast)
            
        Returns:
            Name of best model or None
        """
        try:
            if task_type not in self.model_types:
                self.logger.warning(f"Unknown task type: {task_type}, using 'general'")
                task_type = "general"
            
            # Get installed models
            installed = self._get_installed_models()
            installed_names = [m["name"] for m in installed]
            
            # Get preferred models for this task
            preferred = self.model_types[task_type]["models"]
            
            # Find first installed preferred model
            for model in preferred:
                if any(model in name for name in installed_names):
                    return model
            
            # Fall back to first installed model
            if installed_names:
                return installed_names[0]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error selecting model: {e}")
            return None
    
    # ============================================================
    # Helper Methods
    # ============================================================
    
    def _detect_current_model(self) -> None:
        """Detect current model from Ollama"""
        try:
            installed = self._get_installed_models()
            if installed:
                self.current_model = installed[0]["name"]
        except Exception as e:
            self.logger.warning(f"Error detecting current model: {e}")
    
    def _classify_model_type(self, model_name: str) -> str:
        """
        Classify model type based on name
        
        Args:
            model_name: Name of the model
            
        Returns:
            Type classification
        """
        name_lower = model_name.lower()
        
        if "code" in name_lower or "instruct" in name_lower:
            return "coding"
        elif "creative" in name_lower or "dolphin" in name_lower:
            return "creative"
        elif "mini" in name_lower or "small" in name_lower:
            return "fast"
        elif "orca" in name_lower and "analysis" in name_lower:
            return "analysis"
        else:
            return "general"
    
    @staticmethod
    def _format_size(bytes_size: int) -> str:
        """Format bytes to human-readable size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f}{unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f}PB"
    
    # ============================================================
    # Analysis Result Formatting
    # ============================================================
    
    def analyze(self) -> AnalysisResult:
        """
        Implement abstract analyze method
        
        Returns:
            AnalysisResult with model manager status
        """
        try:
            status = self.get_current_status()
            
            return AnalysisResult(
                success=status.get("success", False),
                data=status,
                message="Model manager status retrieved",
                metadata={
                    "confidence": 0.95,
                    "analysis_type": "model_status"
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error in analyze: {e}")
            return AnalysisResult(
                success=False,
                data={"error": str(e)},
                confidence=0.0,
                analysis_type="model_status"
            )


# ============================================================
# Utility Functions
# ============================================================

def create_model_manager(ollama_brain=None, cache_manager=None) -> ModelManager:
    """Factory function to create ModelManager instance"""
    return ModelManager(ollama_brain=ollama_brain)
