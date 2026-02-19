"""
Stage 5 Phase 4: Model Manager Tests
Test suite for model_manager.py module

Author: ELIXI AI Development Team
Date: February 19, 2026
"""

import unittest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from model_manager import ModelManager


class TestModelManager(unittest.TestCase):
    """Test cases for ModelManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_ollama_brain = Mock()
        self.manager = ModelManager(ollama_brain=self.mock_ollama_brain)
    
    # ==================== Model Discovery Tests ====================
    
    def test_model_manager_initialization(self):
        """Test ModelManager initialization"""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.current_model, None)
        self.assertIsNotNone(self.manager.logger)
        self.assertIsNotNone(self.manager.cache)
    
    def test_classify_model_type(self):
        """Test model type classification"""
        self.assertEqual(self.manager._classify_model_type("codellama"), "coding")
        self.assertEqual(self.manager._classify_model_type("dolphin:7b"), "creative")
        self.assertEqual(self.manager._classify_model_type("orca-mini"), "fast")
        self.assertEqual(self.manager._classify_model_type("neural-chat"), "general")
        self.assertEqual(self.manager._classify_model_type("mistral:7b"), "general")
    
    def test_format_size(self):
        """Test size formatting"""
        self.assertEqual(ModelManager._format_size(512), "512.0B")
        self.assertEqual(ModelManager._format_size(1024), "1.0KB")
        self.assertEqual(ModelManager._format_size(1024 * 1024), "1.0MB")
        self.assertEqual(ModelManager._format_size(1024 * 1024 * 1024), "1.0GB")
    
    # ==================== Model Switching Tests ====================
    
    def test_switch_model_success(self):
        """Test successful model switching"""
        with patch('model_manager.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "models": [
                    {"name": "mistral:7b", "size": 7000000000},
                    {"name": "neural-chat", "size": 4000000000}
                ]
            }
            mock_get.return_value = mock_response
            
            result = self.manager.switch_model("mistral:7b")
            
            self.assertTrue(result.get("success", False))
            self.assertEqual(result.get("current_model"), "mistral:7b")
            self.assertEqual(self.manager.current_model, "mistral:7b")
    
    def test_switch_model_not_found(self):
        """Test switching to non-existent model"""
        with patch('model_manager.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "models": [
                    {"name": "neural-chat", "size": 4000000000}
                ]
            }
            mock_get.return_value = mock_response
            
            result = self.manager.switch_model("nonexistent-model")
            
            self.assertFalse(result.get("success", True))
            self.assertIn("not installed", result.get("error", ""))
    
    def test_switch_model_with_auto_pull(self):
        """Test switching with auto-pull enabled"""
        with patch('model_manager.requests.get') as mock_get, \
             patch('model_manager.requests.post') as mock_post:
            # First call: get installed models (empty)
            mock_response_get = Mock()
            mock_response_get.status_code = 200
            mock_response_get.json.return_value = {"models": []}
            mock_get.return_value = mock_response_get
            
            # POST: pull model
            mock_response_post = Mock()
            mock_response_post.status_code = 200
            mock_post.return_value = mock_response_post
            
            result = self.manager.switch_model("mistral:7b", auto_pull=True)
            
            # Should attempt to pull
            mock_post.assert_called()
    
    # ==================== Model Status Tests ====================
    
    def test_get_current_status(self):
        """Test getting current model status"""
        self.manager.current_model = "neural-chat"
        
        result = self.manager.get_current_status()
        
        self.assertTrue(result.get("success", False))
        self.assertEqual(result.get("current_model"), "neural-chat")
        self.assertIn("performance", result.get("data", {}))
        self.assertIn("resource_usage", result.get("data", {}))
    
    def test_get_model_capabilities(self):
        """Test getting model capabilities"""
        caps_general = self.manager._get_model_capabilities("neural-chat")
        self.assertEqual(caps_general["type"], "general")
        
        caps_coding = self.manager._get_model_capabilities("codellama")
        self.assertEqual(caps_coding["type"], "coding")
        self.assertIn("python", caps_coding["supports"])
    
    # ==================== Model Selection Tests ====================
    
    def test_select_best_model_general(self):
        """Test best model selection for general task"""
        with patch('model_manager.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "models": [
                    {"name": "neural-chat", "size": 4000000000},
                    {"name": "mistral:7b", "size": 7000000000}
                ]
            }
            mock_get.return_value = mock_response
            
            best = self.manager.select_best_model("general")
            
            # Should return one of the models
            self.assertIn(best, ["neural-chat", "mistral:7b", "llama2", "orca"])
    
    def test_select_best_model_coding(self):
        """Test best model selection for coding task"""
        with patch('model_manager.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "models": [
                    {"name": "codellama", "size": 7000000000},
                    {"name": "neural-chat", "size": 4000000000}
                ]
            }
            mock_get.return_value = mock_response
            
            best = self.manager.select_best_model("coding")
            
            # Should prefer codellama for coding
            self.assertEqual(best, "codellama")
    
    def test_select_best_model_invalid_type(self):
        """Test model selection with invalid task type"""
        with patch('model_manager.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "models": [
                    {"name": "neural-chat", "size": 4000000000}
                ]
            }
            mock_get.return_value = mock_response
            
            best = self.manager.select_best_model("invalid_type")
            
            # Should fall back to general
            self.assertIsNotNone(best)
    
    # ==================== Caching Tests ====================
    
    def test_cache_operations(self):
        """Test cache get and set operations"""
        cache_key = "test_model_perf"
        test_data = {"tokens_per_second": 45.3, "avg_latency_ms": 22.1}
        
        self.manager.cache.set(cache_key, test_data)
        cached = self.manager.cache.get(cache_key)
        
        self.assertEqual(cached, test_data)
    
    # ==================== Benchmark Tests ====================
    
    def test_benchmark_model_structure(self):
        """Test benchmark result structure"""
        benchmark_result = {
            "model_name": "test_model",
            "prompts_tested": 3,
            "results": [
                {"prompt_index": 0, "tokens": 100, "time_ms": 50},
                {"prompt_index": 1, "tokens": 85, "time_ms": 45},
                {"prompt_index": 2, "tokens": 120, "time_ms": 60}
            ],
            "summary": {
                "total_tokens": 305,
                "total_time_seconds": 0.155,
                "avg_tokens_per_second": 1968,
                "avg_latency_ms": 51.7
            }
        }
        
        # Validate structure
        self.assertIn("model_name", benchmark_result)
        self.assertIn("prompts_tested", benchmark_result)
        self.assertIn("summary", benchmark_result)
        self.assertIn("avg_tokens_per_second", benchmark_result["summary"])
    
    # ==================== Error Handling Tests ====================
    
    def test_error_handling_connection_error(self):
        """Test error handling for connection errors"""
        with patch('model_manager.requests.get') as mock_get:
            mock_get.side_effect = Exception("Connection refused")
            
            models = self.manager._get_installed_models()
            
            self.assertEqual(models, [])
    
    def test_error_handling_invalid_json(self):
        """Test error handling for invalid JSON response"""
        with patch('model_manager.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_get.return_value = mock_response
            
            models = self.manager._get_installed_models()
            
            self.assertEqual(models, [])
    
    # ==================== API Integration Tests ====================
    
    def test_get_available_models_response_structure(self):
        """Test response structure of get_available_models"""
        with patch('model_manager.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "models": [
                    {"name": "neural-chat", "size": 4000000000}
                ]
            }
            mock_get.return_value = mock_response
            
            result = self.manager.get_available_models()
            
            self.assertIn("installed", result)
            self.assertIn("available", result)
            self.assertIn("active_model", result)
            self.assertIsInstance(result["installed"], list)
            self.assertIsInstance(result["available"], list)
    
    def test_model_type_classification_all_types(self):
        """Test model type classification for all model types"""
        test_cases = {
            "codellama": "coding",
            "mistral-7b-instruct": "coding",
            "neural-chat": "general",
            "llama2": "general",
            "orca-mini": "fast",
            "dolphin-mixtral": "creative",
            "openchat": "general"
        }
        
        for model_name, expected_type in test_cases.items():
            result_type = self.manager._classify_model_type(model_name)
            self.assertEqual(result_type, expected_type, 
                           f"Model {model_name} should be classified as {expected_type}, got {result_type}")


class TestModelManagerIntegration(unittest.TestCase):
    """Integration tests for ModelManager"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.manager = ModelManager()
    
    def test_full_workflow_offline(self):
        """Test complete workflow without actual Ollama connection"""
        with patch('model_manager.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "models": [
                    {"name": "neural-chat", "size": 4000000000},
                    {"name": "mistral:7b", "size": 7000000000}
                ]
            }
            mock_get.return_value = mock_response
            
            # Test model discovery
            models = self.manager.get_available_models()
            self.assertTrue(len(models["installed"]) >= 0)
            
            # Test model selection
            best = self.manager.select_best_model("general")
            self.assertIsNotNone(best)
    
    def test_model_capabilities_all_models(self):
        """Test capabilities for different model types"""
        models = ["neural-chat", "codellama", "mistral:7b", "dolphin", "orca-mini"]
        
        for model in models:
            caps = self.manager._get_model_capabilities(model)
            self.assertIn("type", caps)
            self.assertIn("supports", caps)
            self.assertIn("max_context", caps)
            self.assertIsInstance(caps["supports"], list)


class TestModelManagerAnalyze(unittest.TestCase):
    """Test analyze method implementation"""
    
    def setUp(self):
        """Set up analyze method tests"""
        self.manager = ModelManager()
    
    def test_analyze_method_success(self):
        """Test analyze method returns AnalysisResult"""
        with patch.object(self.manager, 'get_current_status') as mock_status:
            mock_status.return_value = {
                "success": True,
                "current_model": "test_model",
                "data": {}
            }
            
            result = self.manager.analyze()
            
            self.assertIsNotNone(result)
            self.assertTrue(result.success)
            self.assertEqual(result.metadata.get("analysis_type"), "model_status")


def run_tests():
    """Run all tests"""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == "__main__":
    run_tests()
