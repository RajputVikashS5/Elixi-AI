"""
Hardware Control Module
Manages hardware settings: volume, brightness, WiFi, Bluetooth
"""

import subprocess
import platform
from typing import Dict, Optional
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


class HardwareController:
    """Controls system hardware settings"""

    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self.is_mac = platform.system() == "Darwin"
        self.is_linux = platform.system() == "Linux"
        
        # Initialize audio interface for Windows
        self._audio_interface = None
        if self.is_windows:
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self._audio_interface = interface.QueryInterface(IAudioEndpointVolume)
            except Exception:
                self._audio_interface = None

    # ========== VOLUME CONTROL ==========
    
    def get_volume(self) -> Dict:
        """
        Get current system volume level
        
        Returns:
            Dict with volume level (0-100)
        """
        try:
            if self.is_windows and self._audio_interface:
                volume = self._audio_interface.GetMasterVolumeLevelScalar()
                volume_percent = int(volume * 100)
                muted = self._audio_interface.GetMute()
                
                return {
                    "success": True,
                    "volume": volume_percent,
                    "muted": bool(muted)
                }
            else:
                return {
                    "success": False,
                    "error": "Volume control not available on this platform"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def set_volume(self, level: int) -> Dict:
        """
        Set system volume level
        
        Args:
            level: Volume level (0-100)
            
        Returns:
            Dict with success status
        """
        try:
            if not 0 <= level <= 100:
                return {
                    "success": False,
                    "error": "Volume level must be between 0 and 100"
                }

            if self.is_windows and self._audio_interface:
                volume_scalar = level / 100.0
                self._audio_interface.SetMasterVolumeLevelScalar(volume_scalar, None)
                
                return {
                    "success": True,
                    "message": f"Volume set to {level}%",
                    "volume": level
                }
            else:
                return {
                    "success": False,
                    "error": "Volume control not available on this platform"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def mute_volume(self) -> Dict:
        """Mute system volume"""
        try:
            if self.is_windows and self._audio_interface:
                self._audio_interface.SetMute(1, None)
                return {
                    "success": True,
                    "message": "Audio muted",
                    "muted": True
                }
            else:
                return {
                    "success": False,
                    "error": "Mute control not available on this platform"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def unmute_volume(self) -> Dict:
        """Unmute system volume"""
        try:
            if self.is_windows and self._audio_interface:
                self._audio_interface.SetMute(0, None)
                return {
                    "success": True,
                    "message": "Audio unmuted",
                    "muted": False
                }
            else:
                return {
                    "success": False,
                    "error": "Unmute control not available on this platform"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def volume_up(self, increment: int = 10) -> Dict:
        """Increase volume by increment"""
        try:
            current = self.get_volume()
            if current["success"]:
                new_volume = min(100, current["volume"] + increment)
                return self.set_volume(new_volume)
            return current
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def volume_down(self, decrement: int = 10) -> Dict:
        """Decrease volume by decrement"""
        try:
            current = self.get_volume()
            if current["success"]:
                new_volume = max(0, current["volume"] - decrement)
                return self.set_volume(new_volume)
            return current
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # ========== BRIGHTNESS CONTROL ==========
    
    def get_brightness(self) -> Dict:
        """
        Get current screen brightness
        
        Returns:
            Dict with brightness level (0-100)
        """
        try:
            if self.is_windows:
                # Use WMI to get brightness
                result = subprocess.run(
                    ['powershell', '-Command',
                     '(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    brightness = int(result.stdout.strip())
                    return {
                        "success": True,
                        "brightness": brightness
                    }
                else:
                    return {
                        "success": False,
                        "error": "Could not retrieve brightness level"
                    }
            else:
                return {
                    "success": False,
                    "error": "Brightness control not implemented for this platform"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def set_brightness(self, level: int) -> Dict:
        """
        Set screen brightness
        
        Args:
            level: Brightness level (0-100)
            
        Returns:
            Dict with success status
        """
        try:
            if not 0 <= level <= 100:
                return {
                    "success": False,
                    "error": "Brightness level must be between 0 and 100"
                }

            if self.is_windows:
                # Use WMI to set brightness
                result = subprocess.run(
                    ['powershell', '-Command',
                     f'(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "message": f"Brightness set to {level}%",
                        "brightness": level
                    }
                else:
                    return {
                        "success": False,
                        "error": "Could not set brightness level"
                    }
            else:
                return {
                    "success": False,
                    "error": "Brightness control not implemented for this platform"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def brightness_up(self, increment: int = 10) -> Dict:
        """Increase brightness by increment"""
        try:
            current = self.get_brightness()
            if current["success"]:
                new_brightness = min(100, current["brightness"] + increment)
                return self.set_brightness(new_brightness)
            return current
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def brightness_down(self, decrement: int = 10) -> Dict:
        """Decrease brightness by decrement"""
        try:
            current = self.get_brightness()
            if current["success"]:
                new_brightness = max(0, current["brightness"] - decrement)
                return self.set_brightness(new_brightness)
            return current
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # ========== WIFI CONTROL ==========
    
    def get_wifi_status(self) -> Dict:
        """
        Get WiFi adapter status
        
        Returns:
            Dict with WiFi status and connected network
        """
        try:
            if self.is_windows:
                # Check WiFi adapter status
                result = subprocess.run(
                    ['netsh', 'interface', 'show', 'interface'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    output = result.stdout
                    wifi_enabled = "Wi-Fi" in output or "WiFi" in output or "Wireless" in output
                    
                    # Get connected network name
                    network_result = subprocess.run(
                        ['netsh', 'wlan', 'show', 'interfaces'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    connected_network = None
                    if network_result.returncode == 0:
                        for line in network_result.stdout.split('\n'):
                            if 'SSID' in line and 'BSSID' not in line:
                                parts = line.split(':', 1)
                                if len(parts) == 2:
                                    connected_network = parts[1].strip()
                                    break
                    
                    return {
                        "success": True,
                        "enabled": wifi_enabled,
                        "connected": connected_network is not None,
                        "network": connected_network
                    }
                else:
                    return {
                        "success": False,
                        "error": "Could not retrieve WiFi status"
                    }
            else:
                return {
                    "success": False,
                    "error": "WiFi control not implemented for this platform"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def enable_wifi(self) -> Dict:
        """Enable WiFi adapter"""
        try:
            if self.is_windows:
                result = subprocess.run(
                    ['netsh', 'interface', 'set', 'interface', 'Wi-Fi', 'enabled'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "message": "WiFi enabled"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Could not enable WiFi"
                    }
            else:
                return {
                    "success": False,
                    "error": "WiFi control not implemented for this platform"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def disable_wifi(self) -> Dict:
        """Disable WiFi adapter"""
        try:
            if self.is_windows:
                result = subprocess.run(
                    ['netsh', 'interface', 'set', 'interface', 'Wi-Fi', 'disabled'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "message": "WiFi disabled"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Could not disable WiFi"
                    }
            else:
                return {
                    "success": False,
                    "error": "WiFi control not implemented for this platform"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def list_wifi_networks(self) -> Dict:
        """
        List available WiFi networks
        
        Returns:
            Dict with list of available networks
        """
        try:
            if self.is_windows:
                result = subprocess.run(
                    ['netsh', 'wlan', 'show', 'networks'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    networks = []
                    lines = result.stdout.split('\n')
                    
                    current_network = {}
                    for line in lines:
                        line = line.strip()
                        if line.startswith('SSID'):
                            if current_network and 'ssid' in current_network:
                                networks.append(current_network)
                            parts = line.split(':', 1)
                            if len(parts) == 2:
                                ssid = parts[1].strip()
                                if ssid:
                                    current_network = {'ssid': ssid}
                        elif 'Signal' in line and current_network:
                            parts = line.split(':', 1)
                            if len(parts) == 2:
                                current_network['signal'] = parts[1].strip()
                        elif 'Authentication' in line and current_network:
                            parts = line.split(':', 1)
                            if len(parts) == 2:
                                current_network['security'] = parts[1].strip()
                    
                    if current_network and 'ssid' in current_network:
                        networks.append(current_network)
                    
                    return {
                        "success": True,
                        "count": len(networks),
                        "networks": networks
                    }
                else:
                    return {
                        "success": False,
                        "error": "Could not scan WiFi networks"
                    }
            else:
                return {
                    "success": False,
                    "error": "WiFi scanning not implemented for this platform"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
