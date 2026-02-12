"""
Application Management Module
Handles opening, closing, and managing applications
"""

import os
import subprocess
import psutil
import platform
from typing import List, Dict, Optional


class ApplicationManager:
    """Manages system applications - opening, closing, and listing"""

    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self.is_mac = platform.system() == "Darwin"
        self.is_linux = platform.system() == "Linux"

        # Common application mappings (expandable)
        self.app_paths = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
            "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "vscode": r"C:\Program Files\Microsoft VS Code\Code.exe",
            "explorer": "explorer.exe",
            "cmd": "cmd.exe",
            "powershell": "powershell.exe",
            "task manager": "taskmgr.exe",
            "control panel": "control.exe",
            "settings": "ms-settings:",
        }

    def open_application(self, app_name: str, args: Optional[List[str]] = None) -> Dict:
        """
        Open an application by name or path
        
        Args:
            app_name: Name of the application or full path
            args: Optional list of arguments to pass to the application
            
        Returns:
            Dict with success status and process info
        """
        try:
            app_name_lower = app_name.lower()
            
            # Check if it's a known application
            if app_name_lower in self.app_paths:
                app_path = self.app_paths[app_name_lower]
            else:
                app_path = app_name

            # Build command
            if args:
                command = [app_path] + args
            else:
                command = [app_path]

            # Special handling for Windows settings and protocol URLs
            if app_path.startswith("ms-"):
                if self.is_windows:
                    os.startfile(app_path)
                    return {
                        "success": True,
                        "message": f"Opened {app_name}",
                        "app": app_name
                    }
            
            # Launch the process
            if self.is_windows:
                # Use shell=True for Windows to handle paths properly
                if os.path.exists(app_path) or app_path.endswith('.exe'):
                    process = subprocess.Popen(
                        command,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        shell=False
                    )
                else:
                    # Try as a shell command
                    process = subprocess.Popen(
                        app_path,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        shell=True
                    )
            else:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

            return {
                "success": True,
                "message": f"Successfully opened {app_name}",
                "pid": process.pid,
                "app": app_name
            }

        except FileNotFoundError:
            return {
                "success": False,
                "error": f"Application '{app_name}' not found",
                "app": app_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "app": app_name
            }

    def close_application(self, app_name: str, force: bool = False) -> Dict:
        """
        Close an application by name
        
        Args:
            app_name: Name of the application process
            force: Force kill if normal termination fails
            
        Returns:
            Dict with success status and closed process count
        """
        try:
            app_name_lower = app_name.lower()
            closed_count = 0
            closed_pids = []

            # Iterate through all running processes
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    proc_exe = proc.info.get('exe', '').lower() if proc.info.get('exe') else ''
                    
                    # Check if process matches the app name
                    if (app_name_lower in proc_name or 
                        app_name_lower in proc_exe or
                        proc_name.startswith(app_name_lower)):
                        
                        if force:
                            proc.kill()  # Force kill
                        else:
                            proc.terminate()  # Graceful termination
                        
                        closed_count += 1
                        closed_pids.append(proc.info['pid'])
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if closed_count > 0:
                return {
                    "success": True,
                    "message": f"Closed {closed_count} instance(s) of {app_name}",
                    "closed_count": closed_count,
                    "pids": closed_pids,
                    "app": app_name
                }
            else:
                return {
                    "success": False,
                    "error": f"No running instances of '{app_name}' found",
                    "app": app_name
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "app": app_name
            }

    def list_running_applications(self) -> Dict:
        """
        List all running applications
        
        Returns:
            Dict with list of running applications
        """
        try:
            apps = []
            seen_names = set()

            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    name = proc.info['name']
                    
                    # Filter out system processes and duplicates
                    if name and name not in seen_names:
                        # Only include processes with windows (rough heuristic)
                        if not name.endswith('.exe') or name.lower() in [
                            'svchost.exe', 'system', 'registry', 'smss.exe',
                            'csrss.exe', 'wininit.exe', 'services.exe'
                        ]:
                            continue
                            
                        seen_names.add(name)
                        apps.append({
                            "pid": proc.info['pid'],
                            "name": name,
                            "cpu_percent": proc.info.get('cpu_percent', 0),
                            "memory_mb": proc.info['memory_info'].rss / (1024 * 1024) if proc.info.get('memory_info') else 0
                        })
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Sort by memory usage
            apps.sort(key=lambda x: x['memory_mb'], reverse=True)

            return {
                "success": True,
                "count": len(apps),
                "applications": apps[:50]  # Limit to top 50
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_application_info(self, app_name: str) -> Dict:
        """
        Get detailed information about a running application
        
        Args:
            app_name: Name of the application
            
        Returns:
            Dict with application details
        """
        try:
            app_name_lower = app_name.lower()
            instances = []

            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cpu_percent', 'memory_info', 'create_time']):
                try:
                    proc_name = proc.info['name'].lower()
                    
                    if app_name_lower in proc_name:
                        instances.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "exe": proc.info.get('exe', 'N/A'),
                            "cpu_percent": proc.cpu_percent(interval=0.1),
                            "memory_mb": proc.info['memory_info'].rss / (1024 * 1024),
                            "create_time": proc.info['create_time']
                        })
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if instances:
                return {
                    "success": True,
                    "app": app_name,
                    "running": True,
                    "instance_count": len(instances),
                    "instances": instances
                }
            else:
                return {
                    "success": True,
                    "app": app_name,
                    "running": False,
                    "instance_count": 0
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "app": app_name
            }
