"""
Stage 5 Phase 5: Background Mode Manager
File: python-core/background_mode.py
Purpose: Manage always-on persistent background operation
Size: 400+ lines
"""

import os
import sys
import psutil
import threading
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

from stage5_base import BaseAnalyzer, AnalysisResult
from stage5_utils import Logger, ConfigLoader

# Load environment variables
load_dotenv()

class BackgroundModeManager(BaseAnalyzer):
    """
    Manages ELIXI's background operation mode.
    
    Features:
    - Lifecycle management (start/stop/restart)
    - Memory and CPU monitoring
    - Wake triggers (hotkey, voice, API)
    - Graceful shutdown
    - Auto-recovery on crash
    - Event logging
    """

    def __init__(self):
        """Initialize Background Mode Manager"""
        super().__init__(name="BackgroundModeManager")
        
        self.component_name = "BACKGROUND MODE"
        self.config = ConfigLoader()
        
        # State management
        self._is_running = False
        self._process_id = os.getpid()
        self._startup_time = None
        self._last_activity = None
        self._crash_count = 0
        
        # Configuration
        self.auto_restart_on_crash = self.config.get('BACKGROUND_AUTO_RESTART', True)
        self.startup_delay_seconds = self.config.get('BACKGROUND_STARTUP_DELAY', 5)
        
        # Monitoring
        self.memory_check_interval = self.config.get('MEMORY_CHECK_INTERVAL', 30)
        self.cpu_check_interval = self.config.get('CPU_CHECK_INTERVAL', 30)
        self.max_memory_mb = self.config.get('MAX_MEMORY_MB', 250)
        
        # Wake triggers
        self.wake_triggers = {
            'hotkey': self.config.get('WAKE_HOTKEY', 'ALT+Shift+J'),
            'voice': self.config.get('WAKE_ON_VOICE', True),
            'api': self.config.get('WAKE_ON_API', True)
        }
        
        # Monitoring threads
        self._monitor_thread = None
        self._stop_event = threading.Event()
        
        Logger.info(self.component_name, "Background Mode Manager initialized")

    # ===== Required Abstract Method =====
    
    def analyze(self, input_data):
        """
        Implement required analyze method from BaseAnalyzer
        
        Args:
            input_data: Analysis input
            
        Returns:
            Analysis result as dict
        """
        return self.get_background_status().to_dict()

    # ===== Lifecycle Management =====

    def start_background_mode(self) -> AnalysisResult:
        """
        Start background mode operation
        
        Returns:
            AnalysisResult with status and details
        """
        try:
            if self._is_running:
                Logger.warning(self.component_name, "Background mode already running")
                return AnalysisResult(
                    success=False,
                    data={'status': 'already_running', 'message': 'Background mode is already active'},
                    metadata={'process_id': self._process_id}
                )
            
            # Record startup
            self._startup_time = datetime.now()
            self._is_running = True
            self._process_id = os.getpid()
            self._crash_count = 0
            self._stop_event.clear()
            
            # Start monitoring thread
            self._monitor_thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True,
                name="BackgroundMonitor"
            )
            self._monitor_thread.start()
            
            Logger.info(self.component_name, f"Background mode started (PID: {self._process_id})")
            
            return AnalysisResult(
                success=True,
                data={
                    'status': 'started',
                    'mode': 'background',
                    'process_id': self._process_id,
                    'timestamp': self._startup_time.isoformat()
                },
                metadata=self._get_performance_metrics()
            )
            
        except Exception as e:
            Logger.error(self.component_name, f"Failed to start background mode: {str(e)}")
            self._is_running = False
            return AnalysisResult(
                success=False,
                error_code=str(e),
                data={'status': 'failed'}
            )

    def stop_background_mode(self) -> AnalysisResult:
        """
        Gracefully stop background mode
        
        Returns:
            AnalysisResult with shutdown details
        """
        try:
            if not self._is_running:
                return AnalysisResult(
                    success=False,
                    data={'status': 'not_running', 'message': 'Background mode is not active'},
                )
            
            # Signal stop
            self._stop_event.set()
            
            # Wait for monitor thread to finish
            if self._monitor_thread and self._monitor_thread.is_alive():
                self._monitor_thread.join(timeout=5)
            
            uptime = (datetime.now() - self._startup_time).total_seconds()
            self._is_running = False
            
            Logger.info(self.component_name, f"Background mode stopped (uptime: {uptime:.1f}s)")
            
            return AnalysisResult(
                success=True,
                data={
                    'status': 'stopped',
                    'uptime_seconds': uptime,
                    'timestamp': datetime.now().isoformat()
                },
                metadata=self._get_performance_metrics()
            )
            
        except Exception as e:
            Logger.error(self.component_name, f"Error stopping background mode: {str(e)}")
            return AnalysisResult(
                success=False,
                error_code=str(e),
                data={'status': 'error'}
            )

    def restart_background_mode(self) -> AnalysisResult:
        """
        Restart background mode (stop and start)
        
        Returns:
            AnalysisResult with restart details
        """
        try:
            # Stop current instance
            stop_result = self.stop_background_mode()
            if not stop_result.success:
                return stop_result
            
            # Brief delay
            time.sleep(1)
            
            # Start new instance
            start_result = self.start_background_mode()
            
            if start_result.success:
                Logger.info(self.component_name, "Background mode restarted successfully")
            
            return start_result
            
        except Exception as e:
            Logger.error(self.component_name, f"Failed to restart background mode: {str(e)}")
            return AnalysisResult(
                success=False,
                error_code=str(e),
                data={'status': 'restart_failed'}
            )

    # ===== Status & Monitoring =====

    def get_background_status(self) -> AnalysisResult:
        """
        Get current background mode status
        
        Returns:
            AnalysisResult with detailed status
        """
        try:
            metrics = self._get_performance_metrics()
            uptime = None
            
            if self._startup_time:
                uptime = (datetime.now() - self._startup_time).total_seconds()
            
            return AnalysisResult(
                success=True,
                data={
                    'running': self._is_running,
                    'process_id': self._process_id,
                    'uptime_seconds': uptime,
                    'crash_count': self._crash_count,
                    'last_activity': self._last_activity.isoformat() if self._last_activity else None,
                    'wake_triggers': self.wake_triggers,
                    'auto_restart': self.auto_restart_on_crash
                },
                metadata=metrics
            )
            
        except Exception as e:
            Logger.error(self.component_name, f"Error getting background status: {str(e)}")
            return AnalysisResult(
                success=False,
                error_code=str(e),
                data={'running': self._is_running}
            )

    def is_running(self) -> bool:
        """Check if background mode is running"""
        return self._is_running

    # ===== Performance Monitoring =====

    def _get_performance_metrics(self) -> Dict:
        """
        Get current system performance metrics
        
        Returns:
            Dictionary with memory, CPU, and resource usage
        """
        try:
            process = psutil.Process(self._process_id)
            
            # Memory usage
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            memory_percent = process.memory_percent()
            
            # CPU usage
            cpu_percent = process.cpu_percent(interval=0.1)
            
            # Thread count
            num_threads = process.num_threads()
            
            # Network connections (if available)
            num_connections = 0
            try:
                if hasattr(process, 'connections'):
                    num_connections = len(process.connections())
            except (psutil.AccessDenied, psutil.NoSuchProcess, AttributeError):
                num_connections = 0
            
            return {
                'memory_mb': round(memory_mb, 2),
                'memory_percent': round(memory_percent, 2),
                'cpu_percent': round(cpu_percent, 2),
                'num_threads': num_threads,
                'num_connections': num_connections,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            Logger.warning(self.component_name, f"Error getting performance metrics: {str(e)}")
            return {}

    def _monitor_loop(self):
        """
        Main monitoring loop running in separate thread
        Checks memory, CPU, and health
        """
        Logger.debug(self.component_name, "Monitor loop started")
        
        while not self._stop_event.is_set():
            try:
                metrics = self._get_performance_metrics()
                
                # Check memory usage
                if metrics.get('memory_mb', 0) > self.max_memory_mb:
                    Logger.warning(self.component_name, 
                        f"Memory usage high: {metrics['memory_mb']:.1f} MB "
                        f"(max: {self.max_memory_mb} MB)"
                    )
                
                # Check CPU usage
                if metrics.get('cpu_percent', 0) > 80:
                    Logger.warning(self.component_name, 
                        f"CPU usage high: {metrics['cpu_percent']:.1f}%"
                    )
                
                # Update last activity
                self._last_activity = datetime.now()
                
                # Sleep before next check
                self._stop_event.wait(self.memory_check_interval)
                
            except Exception as e:
                Logger.error(self.component_name, f"Error in monitor loop: {str(e)}")
                if self.auto_restart_on_crash:
                    self._handle_crash()
        
        Logger.debug(self.component_name, "Monitor loop stopped")

    def _handle_crash(self):
        """Handle unexpected crash or error"""
        self._crash_count += 1
        Logger.error(self.component_name, f"Crash detected (count: {self._crash_count})")
        
        if self._crash_count >= 3:
            Logger.error(self.component_name, "Too many crashes, disabling auto-restart")
            self.auto_restart_on_crash = False
            self.stop_background_mode()

    # ===== Wake Configuration =====

    def set_wake_triggers(self, hotkey: Optional[str] = None, 
                         voice: Optional[bool] = None, 
                         api: Optional[bool] = None) -> AnalysisResult:
        """
        Configure wake trigger settings
        
        Args:
            hotkey: Hotkey combination (e.g., 'ALT+Shift+J')
            voice: Enable voice activation
            api: Enable API-based wake
            
        Returns:
            AnalysisResult with new configuration
        """
        try:
            if hotkey:
                self.wake_triggers['hotkey'] = hotkey
                self.config.set('WAKE_HOTKEY', hotkey)
            
            if voice is not None:
                self.wake_triggers['voice'] = voice
                self.config.set('WAKE_ON_VOICE', voice)
            
            if api is not None:
                self.wake_triggers['api'] = api
                self.config.set('WAKE_ON_API', api)
            
            Logger.info(self.component_name, f"Wake triggers updated: {self.wake_triggers}")
            
            return AnalysisResult(
                success=True,
                data={'wake_triggers': self.wake_triggers}
            )
            
        except Exception as e:
            Logger.error(self.component_name, f"Error setting wake triggers: {str(e)}")
            return AnalysisResult(
                success=False,
                error_code=str(e),
                data={'wake_triggers': self.wake_triggers}
            )

    def get_wake_triggers(self) -> Dict:
        """Get current wake trigger configuration"""
        return self.wake_triggers.copy()

    # ===== Auto-Start Configuration =====

    def enable_auto_restart(self) -> AnalysisResult:
        """Enable auto-restart on crash"""
        try:
            self.auto_restart_on_crash = True
            self.config.set('BACKGROUND_AUTO_RESTART', True)
            self._crash_count = 0  # Reset crash count
            
            Logger.info(self.component_name, "Auto-restart enabled")
            
            return AnalysisResult(
                success=True,
                data={'auto_restart': self.auto_restart_on_crash}
            )
            
        except Exception as e:
            Logger.error(self.component_name, f"Error enabling auto-restart: {str(e)}")
            return AnalysisResult(
                success=False,
                error_code=str(e)
            )

    def disable_auto_restart(self) -> AnalysisResult:
        """Disable auto-restart on crash"""
        try:
            self.auto_restart_on_crash = False
            self.config.set('BACKGROUND_AUTO_RESTART', False)
            
            Logger.info(self.component_name, "Auto-restart disabled")
            
            return AnalysisResult(
                success=True,
                data={'auto_restart': self.auto_restart_on_crash}
            )
            
        except Exception as e:
            Logger.error(self.component_name, f"Error disabling auto-restart: {str(e)}")
            return AnalysisResult(
                success=False,
                error_code=str(e)
            )

    def is_auto_restart_enabled(self) -> bool:
        """Check if auto-restart is enabled"""
        return self.auto_restart_on_crash

    # ===== Memory Management =====

    def get_memory_usage(self) -> Dict:
        """
        Get detailed memory usage information
        
        Returns:
            Dictionary with memory statistics
        """
        try:
            process = psutil.Process(self._process_id)
            memory_info = process.memory_info()
            
            return {
                'rss_mb': round(memory_info.rss / (1024 * 1024), 2),
                'vms_mb': round(memory_info.vms / (1024 * 1024), 2),
                'percent': round(process.memory_percent(), 2),
                'available_mb': round(psutil.virtual_memory().available / (1024 * 1024), 2),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            Logger.error(self.component_name, f"Error getting memory usage: {str(e)}")
            return {}

    def cleanup_memory(self) -> AnalysisResult:
        """
        Trigger memory cleanup (garbage collection)
        
        Returns:
            AnalysisResult with cleanup status
        """
        try:
            import gc
            
            before = self.get_memory_usage()
            collected = gc.collect()
            after = self.get_memory_usage()
            
            freed_mb = before.get('rss_mb', 0) - after.get('rss_mb', 0)
            
            Logger.info(self.component_name, f"Memory cleanup: freed {freed_mb:.2f} MB, collected {collected} objects")
            
            return AnalysisResult(
                success=True,
                data={
                    'objects_collected': collected,
                    'memory_freed_mb': max(0, freed_mb),
                    'before_mb': before.get('rss_mb', 0),
                    'after_mb': after.get('rss_mb', 0)
                }
            )
            
        except Exception as e:
            Logger.error(self.component_name, f"Error during memory cleanup: {str(e)}")
            return AnalysisResult(
                success=False,
                error_code=str(e)
            )

    # ===== Event Recording =====

    def log_event(self, event_type: str, details: Dict) -> None:
        """
        Log a background mode event
        
        Args:
            event_type: Type of event (startup, shutdown, crash, etc.)
            details: Event details dictionary
        """
        try:
            event = {
                'timestamp': datetime.now().isoformat(),
                'type': event_type,
                'details': details,
                'process_id': self._process_id
            }
            
            # Log to file
            event_log_path = 'logs/background_events.json'
            os.makedirs('logs', exist_ok=True)
            
            with open(event_log_path, 'a') as f:
                f.write(json.dumps(event) + '\n')
            
            Logger.debug(self.component_name, f"Event logged: {event_type}")
            
        except Exception as e:
            Logger.error(self.component_name, f"Error logging event: {str(e)}")

    # ===== Utility Methods =====

    def get_uptime(self) -> Optional[float]:
        """Get uptime in seconds"""
        if self._startup_time:
            return (datetime.now() - self._startup_time).total_seconds()
        return None

    def get_process_info(self) -> Dict:
        """Get detailed process information"""
        try:
            process = psutil.Process(self._process_id)
            
            return {
                'pid': self._process_id,
                'name': process.name(),
                'status': process.status(),
                'create_time': datetime.fromtimestamp(process.create_time()).isoformat(),
                'exe': process.exe() if hasattr(process, 'exe') else None,
                'cwd': process.cwd() if hasattr(process, 'cwd') else None,
            }
            
        except Exception as e:
            Logger.error(self.component_name, f"Error getting process info: {str(e)}")
            return {'pid': self._process_id}

    def __enter__(self):
        """Context manager entry"""
        self.start_background_mode()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_background_mode()
        return False


# ===== Module-level convenience functions =====

_background_manager = None

def init_background_mode() -> BackgroundModeManager:
    """Initialize and return background mode manager"""
    global _background_manager
    if _background_manager is None:
        _background_manager = BackgroundModeManager()
    return _background_manager

def start_background():
    """Start background mode"""
    manager = init_background_mode()
    return manager.start_background_mode()

def stop_background():
    """Stop background mode"""
    manager = init_background_mode()
    return manager.stop_background_mode()

def get_background_status():
    """Get background mode status"""
    manager = init_background_mode()
    return manager.get_background_status()

if __name__ == '__main__':
    # Example usage
    manager = BackgroundModeManager()
    
    # Start background mode
    result = manager.start_background_mode()
    print(f"Started: {result.success}")
    
    # Run for 10 seconds
    time.sleep(10)
    
    # Get status
    status = manager.get_background_status()
    print(f"Status: {status.data}")
    
    # Stop
    result = manager.stop_background_mode()
    print(f"Stopped: {result.success}")
