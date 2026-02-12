"""
Screenshot and File Search Module
Captures screenshots and searches for files in the system
"""

import os
import base64
import io
import time
import platform
from typing import Dict, List, Optional
from pathlib import Path
from PIL import ImageGrab, Image


class ScreenshotManager:
    """Manages screenshot capture and file search operations"""

    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self.is_mac = platform.system() == "Darwin"
        self.is_linux = platform.system() == "Linux"
        
        # Common search directories
        self.common_dirs = []
        if self.is_windows:
            home = Path.home()
            self.common_dirs = [
                home / "Desktop",
                home / "Documents",
                home / "Downloads",
                home / "Pictures",
                home / "Videos",
                home / "Music",
            ]
        elif self.is_mac:
            home = Path.home()
            self.common_dirs = [
                home / "Desktop",
                home / "Documents",
                home / "Downloads",
                home / "Pictures",
                home / "Movies",
                home / "Music",
            ]
        elif self.is_linux:
            home = Path.home()
            self.common_dirs = [
                home / "Desktop",
                home / "Documents",
                home / "Downloads",
                home / "Pictures",
                home / "Videos",
                home / "Music",
            ]

    # ========== SCREENSHOT OPERATIONS ==========

    def capture_screenshot(self, save_path: Optional[str] = None) -> Dict:
        """
        Capture a screenshot of the entire screen
        
        Args:
            save_path: Optional path to save the screenshot file
            
        Returns:
            Dict with base64 encoded image and file path (if saved)
        """
        try:
            # Capture screenshot
            screenshot = ImageGrab.grab()
            
            # Convert to base64
            buffer = io.BytesIO()
            screenshot.save(buffer, format='PNG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            result = {
                "success": True,
                "image": img_base64,
                "width": screenshot.width,
                "height": screenshot.height,
                "format": "PNG",
                "timestamp": time.time()
            }
            
            # Save to file if path provided
            if save_path:
                screenshot.save(save_path)
                result["file_path"] = save_path
                result["message"] = f"Screenshot saved to {save_path}"
            else:
                result["message"] = "Screenshot captured"
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def capture_region(self, x: int, y: int, width: int, height: int, save_path: Optional[str] = None) -> Dict:
        """
        Capture a screenshot of a specific region
        
        Args:
            x: X coordinate of top-left corner
            y: Y coordinate of top-left corner
            width: Width of region to capture
            height: Height of region to capture
            save_path: Optional path to save the screenshot
            
        Returns:
            Dict with base64 encoded image
        """
        try:
            # Calculate bounding box
            bbox = (x, y, x + width, y + height)
            
            # Capture region
            screenshot = ImageGrab.grab(bbox=bbox)
            
            # Convert to base64
            buffer = io.BytesIO()
            screenshot.save(buffer, format='PNG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            result = {
                "success": True,
                "image": img_base64,
                "region": {"x": x, "y": y, "width": width, "height": height},
                "format": "PNG",
                "timestamp": time.time()
            }
            
            # Save to file if path provided
            if save_path:
                screenshot.save(save_path)
                result["file_path"] = save_path
                result["message"] = f"Screenshot saved to {save_path}"
            else:
                result["message"] = "Region screenshot captured"
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def capture_window(self, window_title: Optional[str] = None) -> Dict:
        """
        Capture a screenshot of a specific window
        
        Args:
            window_title: Title of the window to capture (None for active window)
            
        Returns:
            Dict with base64 encoded image
        """
        try:
            if self.is_windows:
                import win32gui
                import win32ui
                import win32con
                
                # Get window handle
                if window_title:
                    hwnd = win32gui.FindWindow(None, window_title)
                    if not hwnd:
                        return {
                            "success": False,
                            "error": f"Window '{window_title}' not found"
                        }
                else:
                    hwnd = win32gui.GetForegroundWindow()
                
                # Get window dimensions
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                width = right - left
                height = bottom - top
                
                # Capture window
                screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
                
                # Convert to base64
                buffer = io.BytesIO()
                screenshot.save(buffer, format='PNG')
                img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                return {
                    "success": True,
                    "image": img_base64,
                    "window": window_title or "Active Window",
                    "dimensions": {"width": width, "height": height},
                    "format": "PNG",
                    "timestamp": time.time(),
                    "message": "Window screenshot captured"
                }
            else:
                return {
                    "success": False,
                    "error": "Window capture only supported on Windows"
                }
                
        except ImportError:
            return {
                "success": False,
                "error": "pywin32 package required for window capture"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def auto_save_screenshot(self, filename_prefix: str = "screenshot") -> Dict:
        """
        Capture screenshot and auto-save with timestamp
        
        Args:
            filename_prefix: Prefix for the filename
            
        Returns:
            Dict with file path and image data
        """
        try:
            # Create screenshots directory in user's Pictures folder
            if self.is_windows:
                screenshots_dir = Path.home() / "Pictures" / "ELIXI Screenshots"
            else:
                screenshots_dir = Path.home() / "Pictures" / "ELIXI_Screenshots"
            
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}.png"
            filepath = screenshots_dir / filename
            
            # Capture and save
            return self.capture_screenshot(save_path=str(filepath))
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # ========== FILE SEARCH OPERATIONS ==========

    def search_files(self, query: str, search_dirs: Optional[List[str]] = None, 
                    max_results: int = 50, file_types: Optional[List[str]] = None) -> Dict:
        """
        Search for files by name
        
        Args:
            query: Search query (filename or pattern)
            search_dirs: List of directories to search (defaults to common user folders)
            max_results: Maximum number of results to return
            file_types: Optional list of file extensions to filter (e.g., ['.txt', '.pdf'])
            
        Returns:
            Dict with list of matching files
        """
        try:
            query_lower = query.lower()
            results = []
            
            # Use provided directories or default to common directories
            dirs_to_search = []
            if search_dirs:
                dirs_to_search = [Path(d) for d in search_dirs if os.path.exists(d)]
            else:
                dirs_to_search = [d for d in self.common_dirs if d.exists()]
            
            # Search each directory
            for search_dir in dirs_to_search:
                try:
                    for root, dirs, files in os.walk(search_dir):
                        for filename in files:
                            # Check if we've reached max results
                            if len(results) >= max_results:
                                break
                            
                            # Check if filename matches query
                            if query_lower in filename.lower():
                                filepath = Path(root) / filename
                                
                                # Filter by file type if specified
                                if file_types and filepath.suffix.lower() not in file_types:
                                    continue
                                
                                try:
                                    stat = filepath.stat()
                                    results.append({
                                        "name": filename,
                                        "path": str(filepath),
                                        "size": stat.st_size,
                                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                                        "modified": stat.st_mtime,
                                        "extension": filepath.suffix
                                    })
                                except:
                                    continue
                        
                        if len(results) >= max_results:
                            break
                except PermissionError:
                    continue
                except Exception:
                    continue
            
            return {
                "success": True,
                "query": query,
                "count": len(results),
                "results": results,
                "searched_dirs": [str(d) for d in dirs_to_search]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def find_file_by_extension(self, extension: str, search_dirs: Optional[List[str]] = None, 
                               max_results: int = 50) -> Dict:
        """
        Find all files with a specific extension
        
        Args:
            extension: File extension (e.g., '.pdf', '.docx')
            search_dirs: List of directories to search
            max_results: Maximum number of results
            
        Returns:
            Dict with list of matching files
        """
        try:
            if not extension.startswith('.'):
                extension = '.' + extension
            
            return self.search_files(
                query="",
                search_dirs=search_dirs,
                max_results=max_results,
                file_types=[extension]
            )
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_recent_files(self, days: int = 7, search_dirs: Optional[List[str]] = None, 
                        max_results: int = 50) -> Dict:
        """
        Get recently modified files
        
        Args:
            days: Number of days to look back
            search_dirs: List of directories to search
            max_results: Maximum number of results
            
        Returns:
            Dict with list of recent files
        """
        try:
            cutoff_time = time.time() - (days * 24 * 60 * 60)
            results = []
            
            # Use provided directories or default to common directories
            dirs_to_search = []
            if search_dirs:
                dirs_to_search = [Path(d) for d in search_dirs if os.path.exists(d)]
            else:
                dirs_to_search = [d for d in self.common_dirs if d.exists()]
            
            # Search each directory
            for search_dir in dirs_to_search:
                try:
                    for root, dirs, files in os.walk(search_dir):
                        for filename in files:
                            if len(results) >= max_results:
                                break
                            
                            filepath = Path(root) / filename
                            
                            try:
                                stat = filepath.stat()
                                if stat.st_mtime >= cutoff_time:
                                    results.append({
                                        "name": filename,
                                        "path": str(filepath),
                                        "size": stat.st_size,
                                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                                        "modified": stat.st_mtime,
                                        "extension": filepath.suffix
                                    })
                            except:
                                continue
                        
                        if len(results) >= max_results:
                            break
                except PermissionError:
                    continue
                except Exception:
                    continue
            
            # Sort by modification time (newest first)
            results.sort(key=lambda x: x['modified'], reverse=True)
            
            return {
                "success": True,
                "days": days,
                "count": len(results),
                "results": results,
                "searched_dirs": [str(d) for d in dirs_to_search]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def open_file_location(self, filepath: str) -> Dict:
        """
        Open file explorer at the file's location
        
        Args:
            filepath: Path to the file
            
        Returns:
            Dict with success status
        """
        try:
            filepath = Path(filepath)
            
            if not filepath.exists():
                return {
                    "success": False,
                    "error": "File does not exist"
                }
            
            if self.is_windows:
                os.startfile(filepath.parent)
            elif self.is_mac:
                os.system(f'open "{filepath.parent}"')
            elif self.is_linux:
                os.system(f'xdg-open "{filepath.parent}"')
            
            return {
                "success": True,
                "message": f"Opened location: {filepath.parent}",
                "path": str(filepath.parent)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
