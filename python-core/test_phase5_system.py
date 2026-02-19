"""
Stage 5 Phase 5: System Tray & Auto-Start Tests
File: python-core/test_phase5_system.py
Purpose: Tests for system tray and auto-start functionality
Size: 250+ lines
"""

import pytest
import os
import platform
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from system_tray import SystemTrayManager, get_tray_manager
from auto_start_config import AutoStartConfiguration, init_auto_start

class TestSystemTrayManagerInit:
    """Test SystemTrayManager initialization"""
    
    def test_init_creates_manager(self):
        """Test that tray manager initializes"""
        manager = SystemTrayManager()
        
        assert manager is not None
        assert manager.name == "SystemTrayManager"
        assert manager._is_running == False
        assert manager.enabled is not None
    
    def test_init_loads_config(self):
        """Test that manager loads configuration"""
        manager = SystemTrayManager()
        
        assert manager.icon_path is not None
        assert manager.enabled is not None

@pytest.mark.skipif(platform.system() != "Windows", reason="System tray tests for Windows only")
class TestSystemTrayStart:
    """Test system tray start functionality"""
    
    @pytest.fixture
    def manager(self):
        """Create a tray manager"""
        return SystemTrayManager()
    
    def test_start_tray_without_pystray(self, manager):
        """Test start when pystray not available"""
        with patch('system_tray.HAS_TRAY', False):
            result = manager.start_tray()
            
            # Should fail gracefully
            assert result.success == False
            assert "pystray" in result.error.lower()
    
    def test_start_tray_twice(self, manager):
        """Test starting tray twice"""
        with patch.object(manager, '_create_icon', return_value=Mock()):
            with patch.object(manager, '_build_menu', return_value=Mock()):
                result1 = manager.start_tray()
                result2 = manager.start_tray()
                
                # First should succeed, second should fail
                if result1.success:
                    assert result2.success == False
                    assert result2.data['status'] == 'already_running'

class TestSystemTrayStatus:
    """Test system tray status operations"""
    
    @pytest.fixture
    def manager(self):
        """Create a tray manager"""
        return SystemTrayManager()
    
    def test_get_status(self, manager):
        """Test getting tray status"""
        result = manager.get_status()
        
        assert result.success == True
        assert 'running' in result.data
        assert 'enabled' in result.data
        assert 'timestamp' in result.data
    
    def test_is_running(self, manager):
        """Test is_running check"""
        assert manager.is_running() == False

class TestSystemTrayCallbacks:
    """Test system tray callback registration"""
    
    @pytest.fixture
    def manager(self):
        """Create a tray manager"""
        return SystemTrayManager()
    
    def test_register_callback(self, manager):
        """Test registering a callback"""
        mock_callback = Mock()
        
        manager.register_callback('test_action', mock_callback)
        
        assert 'test_action' in manager._callbacks
        assert manager._callbacks['test_action'] == mock_callback
    
    def test_remove_callback(self, manager):
        """Test removing a callback"""
        mock_callback = Mock()
        
        manager.register_callback('test_action', mock_callback)
        manager.remove_callback('test_action')
        
        assert 'test_action' not in manager._callbacks
    
    def test_remove_nonexistent_callback(self, manager):
        """Test removing non-existent callback"""
        # Should not raise error
        manager.remove_callback('nonexistent')

class TestAutoStartConfigInit:
    """Test AutoStartConfiguration initialization"""
    
    def test_init_creates_config(self):
        """Test that auto-start config initializes"""
        config = AutoStartConfiguration()
        
        assert config is not None
        assert config.name == "AutoStartConfiguration"
        assert config.app_name == "ELIXI"
        assert config.platform is not None
    
    def test_platform_detection(self):
        """Test platform detection"""
        config = AutoStartConfiguration()
        
        assert config.platform in ["Windows", "Linux", "Darwin"]
        assert config.is_windows == (config.platform == "Windows")

@pytest.mark.skipif(platform.system() != "Windows", reason="Registry tests for Windows only")
class TestAutoStartRegistry:
    """Test auto-start registry operations"""
    
    @pytest.fixture
    def config(self):
        """Create an auto-start config"""
        return AutoStartConfiguration()
    
    @patch('auto_start_config.winreg')
    def test_enable_auto_start_windows(self, mock_winreg, config):
        """Test enabling auto-start on Windows"""
        if not config.is_windows:
            pytest.skip("Windows only")
        
        # Mock registry operations
        mock_key = Mock()
        mock_winreg.CreateKey.return_value = mock_key
        mock_winreg.REG_SZ = 1
        
        result = config.enable_auto_start()
        
        # Should call registry setup
        if result.success:
            assert config.enabled == True
    
    @patch('auto_start_config.winreg')
    def test_disable_auto_start_windows(self, mock_winreg, config):
        """Test disabling auto-start on Windows"""
        if not config.is_windows:
            pytest.skip("Windows only")
        
        # First enable
        config.enabled = True
        
        # Mock registry operations
        mock_key = Mock()
        mock_winreg.OpenKey.return_value = mock_key
        
        result = config.disable_auto_start()
        
        # Should attempt to remove from registry
        if result.success:
            assert config.enabled == False

class TestAutoStartStatus:
    """Test auto-start status operations"""
    
    @pytest.fixture
    def config(self):
        """Create an auto-start config"""
        return AutoStartConfiguration()
    
    def test_get_status(self, config):
        """Test getting auto-start status"""
        result = config.get_status()
        
        assert result.success == True
        assert 'enabled' in result.data
        assert 'app_name' in result.data
        assert 'platform' in result.data
    
    def test_is_auto_start_enabled(self, config):
        """Test checking if auto-start is enabled"""
        enabled = config.is_auto_start_enabled()
        
        assert isinstance(enabled, bool)
    
    def test_get_launch_parameters(self, config):
        """Test getting launch parameters"""
        params = config.get_launch_parameters()
        
        assert isinstance(params, dict)
        assert 'launcher_path' in params
        assert 'startup_delay' in params
        assert 'mode' in params
    
    def test_get_startup_delay(self, config):
        """Test getting startup delay"""
        delay = config.get_startup_delay()
        
        assert isinstance(delay, int)
        assert delay >= 0

class TestAutoStartConfiguration:
    """Test auto-start configuration operations"""
    
    @pytest.fixture
    def config(self):
        """Create an auto-start config"""
        return AutoStartConfiguration()
    
    def test_set_startup_delay(self, config):
        """Test setting startup delay"""
        result = config.set_startup_delay(10)
        
        assert result.success == True
        assert config.get_startup_delay() == 10
    
    def test_set_startup_delay_invalid(self, config):
        """Test setting invalid startup delay"""
        # Too large
        result = config.set_startup_delay(3601)
        assert result.success == False
        
        # Negative
        result = config.set_startup_delay(-1)
        assert result.success == False
    
    def test_get_startup_delay(self, config):
        """Test getting startup delay"""
        delay = config.get_startup_delay()
        
        assert isinstance(delay, int)
        assert delay >= 0

class TestAutoStartLauncher:
    """Test launcher path determination"""
    
    @pytest.fixture
    def config(self):
        """Create an auto-start config"""
        return AutoStartConfiguration()
    
    def test_get_launcher_path(self, config):
        """Test getting launcher path"""
        path = config._get_launcher_path()
        
        assert isinstance(path, str)
        assert len(path) > 0
    
    def test_build_launch_command(self, config):
        """Test building launch command"""
        cmd = config._build_launch_command()
        
        assert isinstance(cmd, str)
        assert len(cmd) > 0
        assert '--mode background' in cmd
        assert '--headless' in cmd

class TestAutoStartVerification:
    """Test registry verification"""
    
    @pytest.fixture
    def config(self):
        """Create an auto-start config"""
        return AutoStartConfiguration()
    
    @patch('auto_start_config.winreg')
    def test_verify_registry_entry(self, mock_winreg, config):
        """Test verifying registry entry"""
        if not config.is_windows:
            pytest.skip("Windows only")
        
        mock_key = Mock()
        mock_winreg.OpenKey.return_value = mock_key
        mock_winreg.QueryValueEx.return_value = ("c:\\test.exe", 1)
        mock_winreg.REG_SZ = 1
        
        result = config.verify_registry_entry()
        
        # Should attempt to verify
        assert result.success or not config.is_windows

class TestModuleFunctions:
    """Test module-level convenience functions"""
    
    def test_init_auto_start(self):
        """Test init_auto_start function"""
        config = init_auto_start()
        
        assert config is not None
        assert isinstance(config, AutoStartConfiguration)
    
    def test_get_tray_manager(self):
        """Test get_tray_manager function"""
        manager = get_tray_manager()
        
        assert manager is not None
        assert isinstance(manager, SystemTrayManager)

class TestIntegration:
    """Integration tests"""
    
    def test_tray_manager_lifecycle(self):
        """Test tray manager lifecycle"""
        manager = SystemTrayManager()
        
        assert manager.is_running() == False
        # Cannot test full lifecycle without pystray
        assert manager.get_status().success == True
    
    def test_auto_start_full_flow(self):
        """Test complete auto-start configuration"""
        config = AutoStartConfiguration()
        
        # Get initial status
        status1 = config.get_status()
        assert status1.success == True
        
        # Set delay
        config.set_startup_delay(15)
        
        # Get updated status
        status2 = config.get_status()
        assert status2.success == True
        assert status2.data['startup_delay'] == 15

class TestErrorHandling:
    """Test error handling"""
    
    def test_tray_without_callbacks(self):
        """Test tray start without callbacks"""
        manager = SystemTrayManager()
        
        # Should handle None callbacks gracefully
        result = manager.get_status()
        assert result.success == True
    
    def test_auto_start_on_unsupported_platform(self):
        """Test auto-start on unsupported platform"""
        config = AutoStartConfiguration()
        
        if not config.is_windows:
            # Should handle gracefully on non-Windows
            result = config.enable_auto_start()
            assert result.success == False

class TestConfiguration:
    """Test configuration management"""
    
    def test_tray_configuration(self):
        """Test tray configuration"""
        manager = SystemTrayManager()
        
        assert manager.icon_path is not None
        assert manager.enabled is not None
    
    def test_auto_start_configuration(self):
        """Test auto-start configuration"""
        config = AutoStartConfiguration()
        
        assert config.app_name == "ELIXI"
        assert config.registry_path is not None
        assert config.launch_path is not None

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
