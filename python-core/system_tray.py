"""
Stage 5 Phase 5: System Tray Manager
File: python-core/system_tray.py
Purpose: Manage system tray integration and context menus
Size: 250+ lines
"""

import os
import threading
from typing import Dict, List, Optional, Callable
from datetime import datetime

try:
    import pystray
    from PIL import Image, ImageDraw
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False
    pystray = None
    Image = None

from stage5_base import BaseAnalyzer, AnalysisResult
from stage5_utils import Logger, ConfigLoader

class SystemTrayManager(BaseAnalyzer):
    """
    Manages system tray integration for ELIXI AI.
    
    Features:
    - Tray icon display
    - Context menu handling
    - Status indicators
    - Quick actions
    - Click handling
    """

    def __init__(self):
        """Initialize System Tray Manager"""
        super().__init__(name="SystemTrayManager")
        
        self.logger = Logger("SYSTEM TRAY")
        self.config = ConfigLoader()
        
        # Check dependencies
        if not HAS_TRAY:
            self.logger.warning("pystray/PIL not installed, some features disabled")
        
        # State
        self._icon = None
        self._menu = None
        self._tray_thread = None
        self._is_running = False
        self._callbacks = {}
        
        # Configuration
        self.icon_path = self.config.get('TRAY_ICON_PATH', './assets/icons/tray.ico')
        self.enabled = self.config.get('SYSTEM_TRAY_ENABLED', True)
        
        self.logger.info("System Tray Manager initialized")

    # ===== Tray Management =====

    def start_tray(self, callbacks: Optional[Dict[str, Callable]] = None) -> AnalysisResult:
        """
        Start system tray with menu
        
        Args:
            callbacks: Dictionary of action callbacks {'action': callable, ...}
            
        Returns:
            AnalysisResult with tray status
        """
        try:
            if not HAS_TRAY:
                return AnalysisResult(
                    success=False,
                    error="pystray/PIL not installed",
                    data={'status': 'not_available'}
                )
            
            if self._is_running:
                self.logger.warning("Tray already running")
                return AnalysisResult(
                    success=False,
                    data={'status': 'already_running'}
                )
            
            # Store callbacks
            if callbacks:
                self._callbacks.update(callbacks)
            
            # Create icon
            self._icon = self._create_icon()
            
            # Build menu
            self._menu = self._build_menu()
            
            # Start in separate thread
            self._is_running = True
            self._tray_thread = threading.Thread(
                target=self._run_tray,
                daemon=True,
                name="SystemTray"
            )
            self._tray_thread.start()
            
            self.logger.info("System tray started")
            
            return AnalysisResult(
                success=True,
                data={
                    'status': 'started',
                    'timestamp': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to start tray: {str(e)}")
            self._is_running = False
            return AnalysisResult(
                success=False,
                error=str(e),
                data={'status': 'failed'}
            )

    def stop_tray(self) -> AnalysisResult:
        """
        Stop system tray
        
        Returns:
            AnalysisResult with stop status
        """
        try:
            if not self._is_running:
                return AnalysisResult(
                    success=False,
                    data={'status': 'not_running'}
                )
            
            if self._icon:
                self._icon.stop()
            
            self._is_running = False
            
            self.logger.info("System tray stopped")
            
            return AnalysisResult(
                success=True,
                data={'status': 'stopped'}
            )
            
        except Exception as e:
            self.logger.error(f"Error stopping tray: {str(e)}")
            return AnalysisResult(
                success=False,
                error=str(e)
            )

    def is_running(self) -> bool:
        """Check if tray is running"""
        return self._is_running

    # ===== Icon Management =====

    def _create_icon(self) -> 'pystray.Icon':
        """
        Create system tray icon
        
        Returns:
            pystray Icon object
        """
        # Try to load icon from file
        if os.path.exists(self.icon_path):
            image = Image.open(self.icon_path)
        else:
            # Generate default icon
            image = self._generate_default_icon()
        
        icon = pystray.Icon(
            "ELIXI",
            image,
            "ELIXI AI Assistant",
            menu=None  # Will be set later
        )
        
        return icon

    def _generate_default_icon(self) -> Image.Image:
        """
        Generate default icon if file not found
        
        Returns:
            PIL Image object
        """
        size = (64, 64)
        
        # Create image with gradient background
        image = Image.new('RGBA', size, color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw circle
        margin = 4
        draw.ellipse(
            [(margin, margin), (size[0] - margin, size[1] - margin)],
            fill=(99, 102, 241, 255),  # Indigo
            outline=(139, 92, 246, 255)  # Purple
        )
        
        # Draw dot (indicator)
        dot_size = 8
        draw.ellipse(
            [(size[0] - dot_size - 4, size[1] - dot_size - 4),
             (size[0] - 4, size[1] - 4)],
            fill=(16, 185, 129, 255)  # Green
        )
        
        return image

    def _build_menu(self) -> 'pystray.Menu':
        """
        Build context menu
        
        Returns:
            pystray Menu object
        """
        items = []
        
        # Show/Hide
        items.append(pystray.MenuItem(
            'Show Window',
            self._callback_show,
            default=True
        ))
        
        # Separator
        items.append(pystray.MenuItem.SEPARATOR)
        
        # Status
        items.append(pystray.MenuItem(
            'Status: Active',
            None,
            enabled=False
        ))
        
        # Separator
        items.append(pystray.MenuItem.SEPARATOR)
        
        # Settings
        items.append(pystray.MenuItem(
            'Settings',
            self._callback_settings
        ))
        
        # Background Mode
        items.append(pystray.MenuItem(
            'Background Mode',
            self._callback_background_mode
        ))
        
        # Separator
        items.append(pystray.MenuItem.SEPARATOR)
        
        # Exit
        items.append(pystray.MenuItem(
            'Exit',
            self._callback_quit
        ))
        
        return pystray.Menu(*items)

    # ===== Callbacks =====

    def _callback_show(self, icon, item):
        """Show window callback"""
        if 'show_window' in self._callbacks:
            self._callbacks['show_window']()
        self.logger.debug("Show window clicked")

    def _callback_settings(self, icon, item):
        """Settings callback"""
        if 'show_settings' in self._callbacks:
            self._callbacks['show_settings']()
        self.logger.debug("Settings clicked")

    def _callback_background_mode(self, icon, item):
        """Background mode callback"""
        if 'toggle_background' in self._callbacks:
            self._callbacks['toggle_background']()
        self.logger.debug("Background mode clicked")

    def _callback_quit(self, icon, item):
        """Quit callback"""
        if 'quit' in self._callbacks:
            self._callbacks['quit']()
        icon.stop()
        self.logger.info("Quit requested")

    # ===== Status Updates =====

    def set_status(self, status: str, color: tuple = (16, 185, 129, 255)) -> AnalysisResult:
        """
        Update tray icon status
        
        Args:
            status: Status text
            color: RGB color tuple
            
        Returns:
            AnalysisResult
        """
        try:
            if not self._icon:
                return AnalysisResult(
                    success=False,
                    error="Tray not initialized"
                )
            
            # Update tooltip
            self._icon.title = f"ELIXI: {status}"
            
            # Update menu
            items = list(self._menu)
            items[2] = pystray.MenuItem(f'Status: {status}', None, enabled=False)
            self._menu = pystray.Menu(*items)
            self._icon.menu = self._menu
            
            self.logger.debug(f"Status updated: {status}")
            
            return AnalysisResult(
                success=True,
                data={'status': status}
            )
            
        except Exception as e:
            self.logger.error(f"Error updating status: {str(e)}")
            return AnalysisResult(
                success=False,
                error=str(e)
            )

    def notify(self, title: str, message: str) -> AnalysisResult:
        """
        Show notification from tray
        
        Args:
            title: Notification title
            message: Notification message
            
        Returns:
            AnalysisResult
        """
        try:
            if not self._icon:
                return AnalysisResult(
                    success=False,
                    error="Tray not initialized"
                )
            
            # Use platform-specific notification if available
            try:
                # Try Windows notification
                import ctypes
                ctypes.windll.user32.SetForegroundWindow(0)
            except Exception:
                pass
            
            self.logger.info(f"Notification: {title} - {message}")
            
            return AnalysisResult(
                success=True,
                data={'notification': f"{title}: {message}"}
            )
            
        except Exception as e:
            self.logger.error(f"Error showing notification: {str(e)}")
            return AnalysisResult(
                success=False,
                error=str(e)
            )

    # ===== Tray Operations =====

    def _run_tray(self):
        """Run tray (blocking, called in separate thread)"""
        try:
            if self._icon:
                self._icon.run()
        except Exception as e:
            self.logger.error(f"Error in tray loop: {str(e)}")
            self._is_running = False

    def refresh(self) -> AnalysisResult:
        """Refresh tray display"""
        try:
            if self._icon:
                # Recreate icon
                old_icon = self._icon
                self._icon = self._create_icon()
                if old_icon:
                    old_icon.stop()
            
            return AnalysisResult(
                success=True,
                data={'status': 'refreshed'}
            )
            
        except Exception as e:
            self.logger.error(f"Error refreshing tray: {str(e)}")
            return AnalysisResult(
                success=False,
                error=str(e)
            )

    def get_status(self) -> AnalysisResult:
        """Get tray status"""
        return AnalysisResult(
            success=True,
            data={
                'running': self._is_running,
                'enabled': self.enabled,
                'menu_items': 7 if self._menu else 0,
                'timestamp': datetime.now().isoformat()
            }
        )

    def register_callback(self, action: str, callback: Callable) -> None:
        """
        Register a callback for an action
        
        Args:
            action: Action name
            callback: Callable to execute
        """
        self._callbacks[action] = callback
        self.logger.debug(f"Callback registered: {action}")

    def remove_callback(self, action: str) -> None:
        """
        Remove a callback
        
        Args:
            action: Action name
        """
        if action in self._callbacks:
            del self._callbacks[action]
            self.logger.debug(f"Callback removed: {action}")


# ===== Module-level convenience functions =====

_tray_manager = None

def init_system_tray(callbacks: Optional[Dict[str, Callable]] = None) -> SystemTrayManager:
    """Initialize and return system tray manager"""
    global _tray_manager
    if _tray_manager is None:
        _tray_manager = SystemTrayManager()
        if callbacks:
            _tray_manager.start_tray(callbacks)
    return _tray_manager

def start_system_tray(callbacks: Optional[Dict[str, Callable]] = None):
    """Start system tray"""
    manager = init_system_tray(callbacks)
    return manager.start_tray(callbacks)

def stop_system_tray():
    """Stop system tray"""
    global _tray_manager
    if _tray_manager:
        return _tray_manager.stop_tray()

def get_tray_manager() -> SystemTrayManager:
    """Get system tray manager instance"""
    global _tray_manager
    if _tray_manager is None:
        _tray_manager = SystemTrayManager()
    return _tray_manager

if __name__ == '__main__':
    # Example usage
    if not HAS_TRAY:
        print("pystray and Pillow required: pip install pystray pillow")
    else:
        manager = SystemTrayManager()
        
        # Define callbacks
        callbacks = {
            'show_window': lambda: print("Show window"),
            'show_settings': lambda: print("Show settings"),
            'toggle_background': lambda: print("Toggle background"),
            'quit': lambda: print("Quit")
        }
        
        # Start tray
        result = manager.start_tray(callbacks)
        print(f"Started: {result.success}")
        
        # Keep running
        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            manager.stop_tray()
            print("Stopped")
