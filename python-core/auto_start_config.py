"""
Stage 5 Phase 5: Auto-Start Configuration
File: python-core/auto_start_config.py
Purpose: Configure ELIXI to launch on system startup
Size: 150+ lines
"""

import os
import sys
import platform
from typing import Dict, Optional
from datetime import datetime

try:
    import winreg
    HAS_WINREG = True
except ImportError:
    HAS_WINREG = False
    winreg = None

from stage5_base import BaseAnalyzer, AnalysisResult
from stage5_utils import Logger, ConfigLoader

class AutoStartConfiguration(BaseAnalyzer):
    """
    Manages auto-start configuration for ELIXI.
    
    Supports Windows Registry modification for auto-launch on startup.
    
    Features:
    - Enable/disable auto-start
    - Configure launch parameters
    - Set startup delay
    - Windows Registry integration
    """

    def __init__(self):
        """Initialize Auto-Start Configuration"""
        super().__init__(name="AutoStartConfiguration")
        
        self.logger_component = "AUTO-START"
        self.config = ConfigLoader()
        
        # Platform detection
        self.platform = platform.system()
        self.is_windows = self.platform == "Windows"
        
        if not self.is_windows:
            Logger.warning(self.logger_component, f"Auto-start may not work on {self.platform}")
        
        # Configuration
        self.app_name = "ELIXI"
        self.registry_path = r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
        self.launch_path = self._get_launcher_path()
        self.startup_delay = self.config.get('AUTO_START_DELAY', 5)
        self.enabled = False
        
        # Load current status
        self._load_status()
        
        Logger.info(self.logger_component, f"Auto-Start Configuration initialized ({self.platform})")

    # ===== Required Abstract Method =====
    
    def analyze(self, input_data):
        """
        Implement required analyze method from BaseAnalyzer
        
        Args:
            input_data: Analysis input
            
        Returns:
            Analysis result as dict
        """
        return self.get_status().to_dict()

    # ===== Status Management =====

    def _load_status(self) -> None:
        """Load current auto-start status from registry"""
        if not self.is_windows or not HAS_WINREG:
            return
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run"
            )
            
            try:
                value, regtype = winreg.QueryValueEx(key, self.app_name)
                self.enabled = True
                Logger.debug(self.logger_component, f"Found existing registry entry: {value}")
            except OSError:
                self.enabled = False
            finally:
                winreg.CloseKey(key)
                
        except Exception as e:
            Logger.warning(self.logger_component, f"Error loading status: {str(e)}")

    # ===== Enable/Disable Auto-Start =====

    def enable_auto_start(self) -> AnalysisResult:
        """
        Enable auto-start for ELIXI
        
        Returns:
            AnalysisResult with status
        """
        if not self.is_windows:
            return AnalysisResult(
                success=False,
                error_code=f"Auto-start not supported on {self.platform}",
                data={'platform': self.platform}
            )
        
        if not HAS_WINREG:
            return AnalysisResult(
                success=False,
                error_code="winreg module not available",
                data={'available': False}
            )
        
        try:
            # Build launch command with parameters
            launch_cmd = self._build_launch_command()
            
            # Write to registry
            key = winreg.CreateKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run"
            )
            
            try:
                winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, launch_cmd)
                self.enabled = True
                
                Logger.info(self.logger_component, f"Auto-start enabled: {launch_cmd}")
                self.config.set('AUTO_START_ENABLED', True)
                
                return AnalysisResult(
                    success=True,
                    data={
                        'enabled': True,
                        'app_name': self.app_name,
                        'registry_path': self.registry_path,
                        'command': launch_cmd,
                        'startup_delay': self.startup_delay,
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
            finally:
                winreg.CloseKey(key)
                
        except Exception as e:
            Logger.error(self.logger_component, f"Failed to enable auto-start: {str(e)}")
            return AnalysisResult(
                success=False,
                error_code=str(e),
                data={'enabled': self.enabled}
            )

    def disable_auto_start(self) -> AnalysisResult:
        """
        Disable auto-start for ELIXI
        
        Returns:
            AnalysisResult with status
        """
        if not self.is_windows or not HAS_WINREG:
            return AnalysisResult(
                success=False,
                error_code="Auto-start not supported on this platform"
            )
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            
            try:
                winreg.DeleteValue(key, self.app_name)
                self.enabled = False
                
                Logger.info(self.logger_component, "Auto-start disabled")
                self.config.set('AUTO_START_ENABLED', False)
                
                return AnalysisResult(
                    success=True,
                    data={
                        'enabled': False,
                        'removed': self.app_name,
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
            finally:
                winreg.CloseKey(key)
                
        except FileNotFoundError:
            # Entry doesn't exist
            self.enabled = False
            return AnalysisResult(
                success=True,
                data={'enabled': False, 'message': 'Entry not found'}
            )
            
        except Exception as e:
            Logger.error(self.logger_component, f"Failed to disable auto-start: {str(e)}")
            return AnalysisResult(
                success=False,
                error_code=str(e),
                data={'enabled': self.enabled}
            )

    def is_auto_start_enabled(self) -> bool:
        """Check if auto-start is enabled"""
        return self.enabled

    def get_status(self) -> AnalysisResult:
        """
        Get current auto-start status
        
        Returns:
            AnalysisResult with detailed status
        """
        try:
            self._load_status()  # Refresh from registry
            
            return AnalysisResult(
                success=True,
                data={
                    'enabled': self.enabled,
                    'app_name': self.app_name,
                    'platform': self.platform,
                    'registry_path': self.registry_path if self.is_windows else None,
                    'launcher_path': self.launch_path,
                    'startup_delay': self.startup_delay,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            Logger.error(self.logger_component, f"Error getting status: {str(e)}")
            return AnalysisResult(
                success=False,
                error_code=str(e),
                data={'enabled': self.enabled}
            )

    # ===== Configuration =====

    def set_startup_delay(self, seconds: int) -> AnalysisResult:
        """
        Set startup delay in seconds
        
        Args:
            seconds: Delay in seconds before launching
            
        Returns:
            AnalysisResult
        """
        try:
            if seconds < 0 or seconds > 3600:
                return AnalysisResult(
                    success=False,
                    error_code="Delay must be between 0 and 3600 seconds"
                )
            
            self.startup_delay = seconds
            self.config.set('AUTO_START_DELAY', seconds)
            
            # Update registry if enabled
            if self.enabled:
                self.enable_auto_start()
            
            Logger.info(self.logger_component, f"Startup delay set to {seconds}s")
            
            return AnalysisResult(
                success=True,
                data={'startup_delay': seconds}
            )
            
        except Exception as e:
            Logger.error(self.logger_component, f"Error setting startup delay: {str(e)}")
            return AnalysisResult(
                success=False,
                error_code=str(e)
            )

    def get_startup_delay(self) -> int:
        """Get current startup delay in seconds"""
        return self.startup_delay

    # ===== Launcher Management =====

    def _get_launcher_path(self) -> str:
        """
        Get the launcher executable path
        
        Returns:
            Path to launcher executable
        """
        # Get main.py path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        main_py = os.path.join(current_dir, "main.py")
        
        # Get Python executable
        python_exe = sys.executable
        
        # On Windows, could also use launcher.exe if it exists
        launcher_exe = os.path.join(
            os.path.dirname(current_dir),
            "launcher.exe"
        )
        
        if os.path.exists(launcher_exe):
            return launcher_exe
        
        return python_exe

    def _build_launch_command(self) -> str:
        """
        Build the launch command with parameters
        
        Returns:
            Full command string for registry
        """
        launcher = self._get_launcher_path()
        
        # Build command
        if launcher.endswith('.py'):
            # Python script
            python_exe = sys.executable
            cmd = f'"{python_exe}" "{launcher}"'
        else:
            # Executable
            cmd = f'"{launcher}"'
        
        # Add parameters
        cmd += ' --mode background --headless'
        
        # Add startup delay (use scheduled task or internal delay)
        if self.startup_delay > 0:
            cmd += f' --startup-delay {self.startup_delay}'
        
        return cmd

    # ===== Utility Methods =====

    def verify_registry_entry(self) -> AnalysisResult:
        """
        Verify registry entry is correctly set
        
        Returns:
            AnalysisResult with verification status
        """
        if not self.is_windows or not HAS_WINREG:
            return AnalysisResult(
                success=False,
                error_code="Registry verification not available on this platform"
            )
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run"
            )
            
            try:
                value, regtype = winreg.QueryValueEx(key, self.app_name)
                
                if value and regtype == winreg.REG_SZ:
                    Logger.info(self.logger_component, f"Registry entry verified: {value}")
                    return AnalysisResult(
                        success=True,
                        data={
                            'verified': True,
                            'value': value,
                            'type': 'REG_SZ'
                        }
                    )
                else:
                    return AnalysisResult(
                        success=False,
                        error_code="Invalid registry entry type"
                    )
                    
            except OSError:
                return AnalysisResult(
                    success=False,
                    error_code="Registry entry not found",
                    data={'verified': False}
                )
            finally:
                winreg.CloseKey(key)
                
        except Exception as e:
            Logger.error(self.logger_component, f"Error verifying registry: {str(e)}")
            return AnalysisResult(
                success=False,
                error_code=str(e)
            )

    def get_launch_parameters(self) -> Dict:
        """Get current launch parameters"""
        return {
            'launcher_path': self.launch_path,
            'startup_delay': self.startup_delay,
            'mode': 'background',
            'headless': True,
            'command': self._build_launch_command()
        }


# ===== Module-level convenience functions =====

_auto_start_config = None

def init_auto_start() -> AutoStartConfiguration:
    """Initialize and return auto-start configuration"""
    global _auto_start_config
    if _auto_start_config is None:
        _auto_start_config = AutoStartConfiguration()
    return _auto_start_config

def enable_auto_start():
    """Enable auto-start"""
    config = init_auto_start()
    return config.enable_auto_start()

def disable_auto_start():
    """Disable auto-start"""
    config = init_auto_start()
    return config.disable_auto_start()

def is_auto_start_enabled() -> bool:
    """Check if auto-start is enabled"""
    config = init_auto_start()
    return config.is_auto_start_enabled()

def get_auto_start_status():
    """Get auto-start status"""
    config = init_auto_start()
    return config.get_status()

if __name__ == '__main__':
    # Example usage
    config = AutoStartConfiguration()
    
    # Check status
    status = config.get_status()
    print(f"Status: {status.data}")
    
    # Enable auto-start
    result = config.enable_auto_start()
    print(f"Enabled: {result.success}")
    
    # Verify
    verify = config.verify_registry_entry()
    print(f"Verified: {verify.success}")
