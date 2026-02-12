"""
Power Management Module
Handles system power operations: shutdown, restart, sleep, lock
"""

import subprocess
import platform
from typing import Dict, Optional


class PowerManager:
    """Manages system power operations"""

    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self.is_mac = platform.system() == "Darwin"
        self.is_linux = platform.system() == "Linux"

    def shutdown(self, delay_seconds: int = 0, force: bool = False) -> Dict:
        """
        Shutdown the computer
        
        Args:
            delay_seconds: Delay before shutdown (default: immediate)
            force: Force applications to close without warning
            
        Returns:
            Dict with success status
        """
        try:
            if self.is_windows:
                command = ['shutdown', '/s']
                
                if delay_seconds > 0:
                    command.extend(['/t', str(delay_seconds)])
                else:
                    command.extend(['/t', '0'])
                
                if force:
                    command.append('/f')
                
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    message = f"System will shutdown in {delay_seconds} seconds" if delay_seconds > 0 else "System is shutting down"
                    return {
                        "success": True,
                        "message": message,
                        "action": "shutdown",
                        "delay": delay_seconds
                    }
                else:
                    return {
                        "success": False,
                        "error": result.stderr or "Shutdown command failed"
                    }
            
            elif self.is_mac:
                command = ['sudo', 'shutdown', '-h']
                if delay_seconds > 0:
                    command.append(f'+{delay_seconds // 60}')  # macOS uses minutes
                else:
                    command.append('now')
                
                result = subprocess.run(command, capture_output=True, text=True)
                return {
                    "success": result.returncode == 0,
                    "message": "System is shutting down" if result.returncode == 0 else "Shutdown failed"
                }
            
            elif self.is_linux:
                command = ['shutdown', '-h']
                if delay_seconds > 0:
                    command.append(f'+{delay_seconds // 60}')
                else:
                    command.append('now')
                
                result = subprocess.run(command, capture_output=True, text=True)
                return {
                    "success": result.returncode == 0,
                    "message": "System is shutting down" if result.returncode == 0 else "Shutdown failed"
                }
            
            else:
                return {
                    "success": False,
                    "error": "Unsupported platform"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def restart(self, delay_seconds: int = 0, force: bool = False) -> Dict:
        """
        Restart the computer
        
        Args:
            delay_seconds: Delay before restart (default: immediate)
            force: Force applications to close without warning
            
        Returns:
            Dict with success status
        """
        try:
            if self.is_windows:
                command = ['shutdown', '/r']
                
                if delay_seconds > 0:
                    command.extend(['/t', str(delay_seconds)])
                else:
                    command.extend(['/t', '0'])
                
                if force:
                    command.append('/f')
                
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    message = f"System will restart in {delay_seconds} seconds" if delay_seconds > 0 else "System is restarting"
                    return {
                        "success": True,
                        "message": message,
                        "action": "restart",
                        "delay": delay_seconds
                    }
                else:
                    return {
                        "success": False,
                        "error": result.stderr or "Restart command failed"
                    }
            
            elif self.is_mac:
                command = ['sudo', 'shutdown', '-r']
                if delay_seconds > 0:
                    command.append(f'+{delay_seconds // 60}')
                else:
                    command.append('now')
                
                result = subprocess.run(command, capture_output=True, text=True)
                return {
                    "success": result.returncode == 0,
                    "message": "System is restarting" if result.returncode == 0 else "Restart failed"
                }
            
            elif self.is_linux:
                command = ['shutdown', '-r']
                if delay_seconds > 0:
                    command.append(f'+{delay_seconds // 60}')
                else:
                    command.append('now')
                
                result = subprocess.run(command, capture_output=True, text=True)
                return {
                    "success": result.returncode == 0,
                    "message": "System is restarting" if result.returncode == 0 else "Restart failed"
                }
            
            else:
                return {
                    "success": False,
                    "error": "Unsupported platform"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def sleep(self) -> Dict:
        """
        Put the computer to sleep
        
        Returns:
            Dict with success status
        """
        try:
            if self.is_windows:
                # Use rundll32 to trigger sleep
                result = subprocess.run(
                    ['rundll32.exe', 'powrprof.dll,SetSuspendState', '0', '1', '0'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                return {
                    "success": True,
                    "message": "System is going to sleep",
                    "action": "sleep"
                }
            
            elif self.is_mac:
                result = subprocess.run(
                    ['pmset', 'sleepnow'],
                    capture_output=True,
                    text=True
                )
                return {
                    "success": result.returncode == 0,
                    "message": "System is going to sleep" if result.returncode == 0 else "Sleep failed"
                }
            
            elif self.is_linux:
                result = subprocess.run(
                    ['systemctl', 'suspend'],
                    capture_output=True,
                    text=True
                )
                return {
                    "success": result.returncode == 0,
                    "message": "System is going to sleep" if result.returncode == 0 else "Sleep failed"
                }
            
            else:
                return {
                    "success": False,
                    "error": "Unsupported platform"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def hibernate(self) -> Dict:
        """
        Hibernate the computer
        
        Returns:
            Dict with success status
        """
        try:
            if self.is_windows:
                # Use rundll32 to trigger hibernate
                result = subprocess.run(
                    ['shutdown', '/h'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "message": "System is hibernating",
                        "action": "hibernate"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Hibernate failed. Hibernation may not be enabled on this system."
                    }
            
            elif self.is_mac:
                return {
                    "success": False,
                    "error": "Hibernation not supported on macOS"
                }
            
            elif self.is_linux:
                result = subprocess.run(
                    ['systemctl', 'hibernate'],
                    capture_output=True,
                    text=True
                )
                return {
                    "success": result.returncode == 0,
                    "message": "System is hibernating" if result.returncode == 0 else "Hibernate failed"
                }
            
            else:
                return {
                    "success": False,
                    "error": "Unsupported platform"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def lock_screen(self) -> Dict:
        """
        Lock the computer screen
        
        Returns:
            Dict with success status
        """
        try:
            if self.is_windows:
                result = subprocess.run(
                    ['rundll32.exe', 'user32.dll,LockWorkStation'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                return {
                    "success": True,
                    "message": "Screen locked",
                    "action": "lock"
                }
            
            elif self.is_mac:
                result = subprocess.run(
                    ['/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession', '-suspend'],
                    capture_output=True,
                    text=True
                )
                return {
                    "success": result.returncode == 0,
                    "message": "Screen locked" if result.returncode == 0 else "Lock failed"
                }
            
            elif self.is_linux:
                # Try multiple lock commands (depends on desktop environment)
                for cmd in [['gnome-screensaver-command', '-l'], ['xdg-screensaver', 'lock'], ['loginctl', 'lock-session']]:
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            return {
                                "success": True,
                                "message": "Screen locked"
                            }
                    except:
                        continue
                
                return {
                    "success": False,
                    "error": "Could not find a compatible lock command"
                }
            
            else:
                return {
                    "success": False,
                    "error": "Unsupported platform"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def cancel_shutdown(self) -> Dict:
        """
        Cancel a scheduled shutdown or restart
        
        Returns:
            Dict with success status
        """
        try:
            if self.is_windows:
                result = subprocess.run(
                    ['shutdown', '/a'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "message": "Shutdown/restart cancelled"
                    }
                else:
                    return {
                        "success": False,
                        "error": "No shutdown/restart to cancel or cancellation failed"
                    }
            
            elif self.is_mac or self.is_linux:
                result = subprocess.run(
                    ['sudo', 'shutdown', '-c'],
                    capture_output=True,
                    text=True
                )
                return {
                    "success": result.returncode == 0,
                    "message": "Shutdown cancelled" if result.returncode == 0 else "Cancellation failed"
                }
            
            else:
                return {
                    "success": False,
                    "error": "Unsupported platform"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def log_off(self) -> Dict:
        """
        Log off the current user
        
        Returns:
            Dict with success status
        """
        try:
            if self.is_windows:
                result = subprocess.run(
                    ['shutdown', '/l'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                return {
                    "success": True,
                    "message": "User is being logged off",
                    "action": "logoff"
                }
            
            elif self.is_mac:
                result = subprocess.run(
                    ['osascript', '-e', 'tell application "System Events" to log out'],
                    capture_output=True,
                    text=True
                )
                return {
                    "success": result.returncode == 0,
                    "message": "User logged off" if result.returncode == 0 else "Logoff failed"
                }
            
            elif self.is_linux:
                result = subprocess.run(
                    ['loginctl', 'terminate-user', '$USER'],
                    capture_output=True,
                    text=True
                )
                return {
                    "success": result.returncode == 0,
                    "message": "User logged off" if result.returncode == 0 else "Logoff failed"
                }
            
            else:
                return {
                    "success": False,
                    "error": "Unsupported platform"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
