"""
ELIXI AI - System Control Module
Stage 3: Full System Control Implementation

This module provides complete PC control capabilities including:
- Application Management
- Hardware Control (Volume, Brightness, WiFi)
- Power Management (Shutdown, Restart, Sleep)
- Screenshot & File Search
- System Monitoring (CPU, RAM, Disk, Temperature)
"""

from .applications import ApplicationManager
from .hardware import HardwareController
from .power import PowerManager
from .screenshot import ScreenshotManager
from .monitoring import SystemMonitor

__all__ = [
    "ApplicationManager",
    "HardwareController",
    "PowerManager",
    "ScreenshotManager",
    "SystemMonitor",
]

__version__ = "1.0.0"
