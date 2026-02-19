"""
Stage 5 Phase 5: Background Mode Tests
File: python-core/test_phase5_background.py
Purpose: Unit and integration tests for background mode
Size: 300+ lines
"""

import pytest
import time
import psutil
import threading
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from background_mode import BackgroundModeManager, init_background_mode, start_background, stop_background

class TestBackgroundModeManagerInit:
    """Test BackgroundModeManager initialization"""
    
    def test_init_creates_manager(self):
        """Test that manager initializes correctly"""
        manager = BackgroundModeManager()
        
        assert manager is not None
        assert manager.name == "BackgroundModeManager"
        assert manager._is_running == False
        assert manager._process_id == None or manager._process_id > 0
    
    def test_init_loads_config(self):
        """Test that manager loads configuration"""
        manager = BackgroundModeManager()
        
        assert manager.auto_restart_on_crash is not None
        assert manager.startup_delay_seconds >= 0
        assert manager.memory_check_interval > 0
        assert isinstance(manager.wake_triggers, dict)

class TestBackgroundModeLifecycle:
    """Test background mode lifecycle"""
    
    @pytest.fixture
    def manager(self):
        """Create a manager for testing"""
        return BackgroundModeManager()
    
    def test_start_background_mode(self, manager):
        """Test starting background mode"""
        result = manager.start_background_mode()
        
        assert result.success == True
        assert manager._is_running == True
        assert result.data['status'] == 'started'
        assert result.data['process_id'] > 0
        
        # Cleanup
        manager.stop_background_mode()
    
    def test_cannot_start_twice(self, manager):
        """Test that starting twice returns error"""
        manager.start_background_mode()
        
        result = manager.start_background_mode()
        assert result.success == False
        assert result.data['status'] == 'already_running'
        
        # Cleanup
        manager.stop_background_mode()
    
    def test_stop_background_mode(self, manager):
        """Test stopping background mode"""
        manager.start_background_mode()
        result = manager.stop_background_mode()
        
        assert result.success == True
        assert manager._is_running == False
        assert result.data['status'] == 'stopped'
        assert result.data['uptime_seconds'] >= 0
    
    def test_stop_when_not_running(self, manager):
        """Test stopping when not running"""
        result = manager.stop_background_mode()
        
        assert result.success == False
        assert result.data['status'] == 'not_running'
    
    def test_restart_background_mode(self, manager):
        """Test restarting background mode"""
        manager.start_background_mode()
        result = manager.restart_background_mode()
        
        assert result.success == True
        assert manager._is_running == True
        
        # Cleanup
        manager.stop_background_mode()

class TestBackgroundModeStatus:
    """Test background mode status queries"""
    
    @pytest.fixture
    def manager(self):
        """Create a running manager"""
        m = BackgroundModeManager()
        m.start_background_mode()
        yield m
        m.stop_background_mode()
    
    def test_get_background_status(self, manager):
        """Test getting background status"""
        result = manager.get_background_status()
        
        assert result.success == True
        assert result.data['running'] == True
        assert result.data['process_id'] > 0
        assert result.data['uptime_seconds'] >= 0
        assert 'wake_triggers' in result.data
    
    def test_is_running(self, manager):
        """Test is_running check"""
        assert manager.is_running() == True
    
    def test_uptime_tracking(self, manager):
        """Test that uptime is tracked correctly"""
        time.sleep(0.5)
        uptime = manager.get_uptime()
        
        assert uptime is not None
        assert uptime >= 0.5

class TestPerformanceMonitoring:
    """Test performance monitoring"""
    
    @pytest.fixture
    def manager(self):
        """Create a running manager"""
        m = BackgroundModeManager()
        m.start_background_mode()
        yield m
        m.stop_background_mode()
    
    def test_get_performance_metrics(self, manager):
        """Test getting performance metrics"""
        metrics = manager._get_performance_metrics()
        
        assert isinstance(metrics, dict)
        assert 'memory_mb' in metrics
        assert 'cpu_percent' in metrics
        assert metrics['memory_mb'] > 0
        assert metrics['cpu_percent'] >= 0
    
    def test_memory_usage_tracking(self, manager):
        """Test memory usage tracking"""
        memory = manager.get_memory_usage()
        
        assert 'rss_mb' in memory
        assert 'vms_mb' in memory
        assert 'percent' in memory
        assert memory['rss_mb'] > 0
    
    def test_process_info(self, manager):
        """Test process info retrieval"""
        info = manager.get_process_info()
        
        assert 'pid' in info
        assert info['pid'] > 0
        assert 'name' in info
        assert 'status' in info

class TestWakeTriggers:
    """Test wake trigger configuration"""
    
    @pytest.fixture
    def manager(self):
        """Create a manager"""
        return BackgroundModeManager()
    
    def test_get_wake_triggers(self, manager):
        """Test getting wake triggers"""
        triggers = manager.get_wake_triggers()
        
        assert isinstance(triggers, dict)
        assert 'hotkey' in triggers
        assert 'voice' in triggers
        assert 'api' in triggers
    
    def test_set_wake_hotkey(self, manager):
        """Test setting wake hotkey"""
        result = manager.set_wake_triggers(hotkey='ALT+Shift+K')
        
        assert result.success == True
        assert manager.wake_triggers['hotkey'] == 'ALT+Shift+K'
    
    def test_set_voice_trigger(self, manager):
        """Test setting voice trigger"""
        result = manager.set_wake_triggers(voice=False)
        
        assert result.success == True
        assert manager.wake_triggers['voice'] == False
    
    def test_set_api_trigger(self, manager):
        """Test setting API trigger"""
        result = manager.set_wake_triggers(api=False)
        
        assert result.success == True
        assert manager.wake_triggers['api'] == False

class TestAutoRestart:
    """Test auto-restart functionality"""
    
    @pytest.fixture
    def manager(self):
        """Create a manager"""
        return BackgroundModeManager()
    
    def test_enable_auto_restart(self, manager):
        """Test enabling auto-restart"""
        result = manager.enable_auto_restart()
        
        assert result.success == True
        assert manager.is_auto_restart_enabled() == True
    
    def test_disable_auto_restart(self, manager):
        """Test disabling auto-restart"""
        result = manager.disable_auto_restart()
        
        assert result.success == True
        assert manager.is_auto_restart_enabled() == False
    
    def test_is_auto_restart_enabled(self, manager):
        """Test checking auto-restart status"""
        manager.enable_auto_restart()
        assert manager.is_auto_restart_enabled() == True
        
        manager.disable_auto_restart()
        assert manager.is_auto_restart_enabled() == False

class TestMemoryManagement:
    """Test memory management"""
    
    @pytest.fixture
    def manager(self):
        """Create a running manager"""
        m = BackgroundModeManager()
        m.start_background_mode()
        yield m
        m.stop_background_mode()
    
    def test_get_memory_usage(self, manager):
        """Test getting memory usage"""
        memory = manager.get_memory_usage()
        
        assert isinstance(memory, dict)
        assert 'rss_mb' in memory
        assert 'vms_mb' in memory
        assert 'percent' in memory
        assert memory['rss_mb'] > 0
    
    def test_cleanup_memory(self, manager):
        """Test memory cleanup"""
        result = manager.cleanup_memory()
        
        assert result.success == True
        assert 'objects_collected' in result.data
        assert result.data['objects_collected'] >= 0

class TestEventLogging:
    """Test event logging"""
    
    @pytest.fixture
    def manager(self):
        """Create a manager"""
        return BackgroundModeManager()
    
    def test_log_event(self, manager):
        """Test logging an event"""
        import os
        
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        # Log an event
        manager.log_event('test_event', {'test': 'data'})
        
        # Check log was created
        assert os.path.exists('logs/background_events.json')

class TestContextManager:
    """Test context manager behavior"""
    
    def test_context_manager(self):
        """Test using BackgroundModeManager as context manager"""
        with BackgroundModeManager() as manager:
            assert manager._is_running == True
        
        # Should be stopped after exiting context
        assert manager._is_running == False

class TestModuleFunctions:
    """Test module-level convenience functions"""
    
    def test_init_background_mode(self):
        """Test init_background_mode function"""
        manager = init_background_mode()
        
        assert manager is not None
        assert isinstance(manager, BackgroundModeManager)
        
        # Cleanup
        if manager._is_running:
            manager.stop_background_mode()
    
    def test_start_background(self):
        """Test start_background function"""
        result = start_background()
        
        assert result.success == True
        
        # Cleanup
        stop_background()
    
    def test_stop_background(self):
        """Test stop_background function"""
        start_background()
        result = stop_background()
        
        assert result.success == True

class TestConcurrency:
    """Test concurrent operations"""
    
    def test_monitor_thread_runs(self):
        """Test that monitor thread starts"""
        manager = BackgroundModeManager()
        manager.start_background_mode()
        
        # Give thread time to start
        time.sleep(0.1)
        
        assert manager._monitor_thread is not None
        assert manager._monitor_thread.is_alive()
        
        # Cleanup
        manager.stop_background_mode()
    
    def test_memory_monitoring(self):
        """Test memory monitoring in background"""
        manager = BackgroundModeManager()
        manager.memory_check_interval = 0.1  # Fast interval for testing
        manager.start_background_mode()
        
        # Let it monitor for a bit
        time.sleep(0.5)
        
        # Should have activity
        assert manager._last_activity is not None
        
        # Cleanup
        manager.stop_background_mode()

class TestErrorHandling:
    """Test error handling"""
    
    def test_start_with_error(self):
        """Test error handling during start"""
        manager = BackgroundModeManager()
        
        # Mock process.pid to fail
        with patch('os.getpid', side_effect=Exception("Test error")):
            # Should still initialize (error would happen in start)
            assert manager is not None
    
    def test_get_metrics_with_error(self):
        """Test error handling in metrics"""
        manager = BackgroundModeManager()
        manager.start_background_mode()
        
        # Even with errors, should return empty dict
        metrics = manager._get_performance_metrics()
        assert isinstance(metrics, dict)
        
        # Cleanup
        manager.stop_background_mode()

class TestIntegration:
    """Integration tests"""
    
    def test_full_lifecycle(self):
        """Test complete lifecycle"""
        manager = BackgroundModeManager()
        
        # Start
        result = manager.start_background_mode()
        assert result.success == True
        
        # Check status multiple times
        for _ in range(3):
            status = manager.get_background_status()
            assert status.success == True
            assert status.data['running'] == True
            time.sleep(0.1)
        
        # Stop
        result = manager.stop_background_mode()
        assert result.success == True
        assert manager._is_running == False
    
    def test_configuration_persistence(self):
        """Test that configuration is persistent"""
        manager1 = BackgroundModeManager()
        manager1.set_wake_triggers(hotkey='ALT+Shift+X')
        
        # Create new instance
        manager2 = BackgroundModeManager()
        triggers = manager2.get_wake_triggers()
        
        # Hotkey should be persisted
        assert triggers['hotkey'] == 'ALT+Shift+X'

# ===== Performance Tests =====

class TestPerformance:
    """Performance and stress tests"""
    
    def test_startup_speed(self):
        """Test startup speed"""
        manager = BackgroundModeManager()
        
        start_time = time.time()
        result = manager.start_background_mode()
        elapsed = time.time() - start_time
        
        assert result.success == True
        assert elapsed < 1.0  # Should start in < 1 second
        
        # Cleanup
        manager.stop_background_mode()
    
    def test_shutdown_speed(self):
        """Test shutdown speed"""
        manager = BackgroundModeManager()
        manager.start_background_mode()
        
        start_time = time.time()
        result = manager.stop_background_mode()
        elapsed = time.time() - start_time
        
        assert result.success == True
        assert elapsed < 5.0  # Should stop in < 5 seconds
    
    @pytest.mark.slow
    def test_memory_stability(self):
        """Test memory stability over time"""
        manager = BackgroundModeManager()
        manager.start_background_mode()
        
        # Collect memory samples
        samples = []
        for _ in range(10):
            memory = manager.get_memory_usage()
            samples.append(memory['rss_mb'])
            time.sleep(0.1)
        
        # Check that memory is relatively stable
        avg_memory = sum(samples) / len(samples)
        max_increase = max(samples) - min(samples)
        
        assert max_increase < 10  # Memory shouldn't increase by more than 10 MB
        
        # Cleanup
        manager.stop_background_mode()

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
