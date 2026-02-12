"""
Screen Analyzer - Computer Vision for Screen Understanding
Provides screenshot capture, OCR, window detection, and AI-powered analysis
"""

import sys
import os
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from stage5_base import BaseAnalyzer
from stage5_utils import Logger, APIResponseFormatter
import time

# Screen capture and window management
try:
    import pyautogui
    import pygetwindow as gw
    from PIL import Image
    import pytesseract
    SCREEN_LIBS_AVAILABLE = True
except ImportError as e:
    SCREEN_LIBS_AVAILABLE = False
    Logger.warning("ScreenAnalyzer", f"Screen libraries not available: {e}")


class ScreenAnalyzer(BaseAnalyzer):
    """Analyze screen content using OCR and AI interpretation"""
    
    def __init__(self, mongodb=None, enable_cache: bool = True, ai_brain=None):
        """Initialize screen analyzer.
        
        Args:
            mongodb: MongoDB connection for caching
            enable_cache: Whether to use caching
            ai_brain: AI brain instance for interpretation (optional)
        """
        super().__init__("ScreenAnalyzer", mongodb, enable_cache)
        self.ai_brain = ai_brain
        
        # Check if Tesseract is installed
        self.tesseract_available = self._check_tesseract()
        
        if not SCREEN_LIBS_AVAILABLE:
            Logger.error(self.name, "Required screen libraries not available")
        
        Logger.info(self.name, f"Tesseract available: {self.tesseract_available}")
    
    def _check_tesseract(self) -> bool:
        """Check if Tesseract OCR is installed."""
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception as e:
            Logger.warning(self.name, f"Tesseract OCR not found: {e}")
            Logger.info(self.name, "Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")
            return False
    
    def analyze(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main analysis entry point.
        
        Args:
            input_data: Configuration for analysis
                - include_text: Extract text via OCR
                - include_elements: Detect UI elements (future)
                - ai_interpretation: Use AI to interpret screen
                
        Returns:
            Analysis results with screen data
        """
        start_time = time.time()
        
        # Validate input
        if not self.validate_input(input_data, []):
            return self.format_error("Invalid input data")
        
        if not SCREEN_LIBS_AVAILABLE:
            return self.format_error("Screen libraries not available")
        
        try:
            # Get configuration
            include_text = input_data.get('include_text', True)
            include_elements = input_data.get('include_elements', False)
            ai_interpretation = input_data.get('ai_interpretation', False)
            
            # Generate cache key
            cache_key = self.get_cache_key(
                action='analyze_screen',
                include_text=include_text,
                include_elements=include_elements
            )
            
            # Check cache (5 minute TTL for screen analysis)
            cached = self.get_cached_result(cache_key)
            if cached:
                Logger.info(self.name, "Returning cached screen analysis")
                cached['from_cache'] = True
                return self.format_success(cached)
            
            # Capture screen
            screenshot = self._capture_screenshot()
            if not screenshot:
                return self.format_error("Failed to capture screenshot")
            
            # Get window information
            window_info = self._get_window_info()
            
            # Extract text if requested
            text_content = ""
            ocr_confidence = 0.0
            if include_text and self.tesseract_available:
                text_content, ocr_confidence = self._extract_text(screenshot)
            
            # Detect UI elements if requested (placeholder for future)
            elements = []
            if include_elements:
                elements = self._detect_elements(screenshot)
            
            # AI interpretation if requested
            ai_analysis = ""
            confidence = 0.0
            if ai_interpretation and self.ai_brain and text_content:
                ai_analysis, confidence = self._ai_interpret(text_content, window_info)
            
            # Build result
            result = {
                'timestamp': datetime.now().isoformat(),
                'window_info': window_info,
                'text_content': text_content[:500] if text_content else "",  # Limit text
                'full_text_length': len(text_content),
                'ocr_confidence': round(ocr_confidence, 2),
                'elements': elements,
                'ai_analysis': ai_analysis,
                'confidence': round(confidence, 2),
                'from_cache': False
            }
            
            # Cache result (5 minutes)
            self.cache_result(cache_key, result, ttl_minutes=5)
            
            duration_ms = (time.time() - start_time) * 1000
            self.log_analysis(
                f"Screen analysis with OCR={include_text}",
                f"Found {len(text_content)} chars, {len(elements)} elements",
                duration_ms
            )
            
            return self.format_success(result)
            
        except Exception as e:
            Logger.error(self.name, f"Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return self.format_error(f"Analysis failed: {str(e)}")
    
    def _capture_screenshot(self) -> Optional[Image.Image]:
        """Capture current screen as PIL Image."""
        try:
            screenshot = pyautogui.screenshot()
            Logger.info(self.name, f"Screenshot captured: {screenshot.size}")
            return screenshot
        except Exception as e:
            Logger.error(self.name, f"Screenshot capture failed: {e}")
            return None
    
    def _get_window_info(self) -> Dict[str, Any]:
        """Get information about the active window."""
        try:
            active_window = gw.getActiveWindow()
            if active_window:
                return {
                    'title': active_window.title,
                    'app_name': active_window.title.split(' - ')[-1] if ' - ' in active_window.title else active_window.title,
                    'dimensions': {
                        'width': active_window.width,
                        'height': active_window.height
                    },
                    'position': {
                        'x': active_window.left,
                        'y': active_window.top
                    },
                    'is_maximized': active_window.isMaximized
                }
        except Exception as e:
            Logger.warning(self.name, f"Failed to get window info: {e}")
        
        return {
            'title': 'Unknown',
            'app_name': 'Unknown',
            'dimensions': {'width': 0, 'height': 0},
            'position': {'x': 0, 'y': 0},
            'is_maximized': False
        }
    
    def _extract_text(self, image: Image.Image) -> Tuple[str, float]:
        """Extract text from image using Tesseract OCR.
        
        Returns:
            Tuple of (text_content, confidence_score)
        """
        try:
            # Extract text with confidence data
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Get text and calculate average confidence
            text_parts = []
            confidences = []
            
            for i, conf in enumerate(data['conf']):
                if int(conf) > 0:  # Valid confidence
                    text = data['text'][i].strip()
                    if text:
                        text_parts.append(text)
                        confidences.append(int(conf))
            
            text_content = ' '.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            Logger.info(self.name, f"OCR extracted {len(text_content)} chars with {avg_confidence:.1f}% confidence")
            return text_content, avg_confidence / 100.0  # Convert to 0-1 scale
            
        except Exception as e:
            Logger.error(self.name, f"Text extraction failed: {e}")
            return "", 0.0
    
    def _detect_elements(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Detect UI elements in screenshot (placeholder for future implementation)."""
        # This would use computer vision to detect buttons, text boxes, etc.
        # For now, return empty list as placeholder
        Logger.info(self.name, "UI element detection not yet implemented")
        return []
    
    def _ai_interpret(self, text_content: str, window_info: Dict) -> Tuple[str, float]:
        """Use AI to interpret screen content.
        
        Returns:
            Tuple of (interpretation, confidence)
        """
        try:
            if not self.ai_brain:
                return "", 0.0
            
            # Build context-aware prompt
            prompt = f"""Analyze this screen content and provide a brief interpretation:
            
Window: {window_info.get('title', 'Unknown')}
App: {window_info.get('app_name', 'Unknown')}

Text content:
{text_content[:1000]}  # Limit to 1000 chars

Provide a brief 1-2 sentence interpretation of what the user is doing."""
            
            # Query AI brain
            result = self.ai_brain.query(prompt)
            if result and isinstance(result, dict):
                interpretation = result.get('response', '')
                confidence = result.get('confidence', 0.5)
                Logger.info(self.name, f"AI interpretation generated with {confidence:.2f} confidence")
                return interpretation, confidence
            
        except Exception as e:
            Logger.warning(self.name, f"AI interpretation failed: {e}")
        
        return "", 0.0
    
    def get_screen_text(self, ocr_confidence_threshold: float = 0.7) -> Dict[str, Any]:
        """Extract only text from screen (simplified OCR).
        
        Args:
            ocr_confidence_threshold: Minimum confidence to include text
            
        Returns:
            OCR results with text and metadata
        """
        start_time = time.time()
        
        if not SCREEN_LIBS_AVAILABLE or not self.tesseract_available:
            return self.format_error("OCR not available")
        
        try:
            # Capture screenshot
            screenshot = self._capture_screenshot()
            if not screenshot:
                return self.format_error("Failed to capture screenshot")
            
            # Extract text
            text_content, confidence = self._extract_text(screenshot)
            
            # Filter by confidence threshold
            if confidence < ocr_confidence_threshold:
                Logger.warning(self.name, f"OCR confidence {confidence:.2f} below threshold {ocr_confidence_threshold}")
            
            result = {
                'text': text_content,
                'languages_detected': ['en'],  # Placeholder - Tesseract default
                'ocr_confidence': round(confidence, 2),
                'num_characters': len(text_content),
                'timestamp': datetime.now().isoformat()
            }
            
            duration_ms = (time.time() - start_time) * 1000
            Logger.info(self.name, f"Text extraction completed in {duration_ms:.0f}ms")
            
            return self.format_success(result)
            
        except Exception as e:
            Logger.error(self.name, f"Text extraction failed: {e}")
            return self.format_error(f"Text extraction failed: {str(e)}")
    
    def identify_window(self) -> Dict[str, Any]:
        """Get detailed information about the active window.
        
        Returns:
            Window information including title, app, position, size
        """
        if not SCREEN_LIBS_AVAILABLE:
            return self.format_error("Window management not available")
        
        try:
            active_window = gw.getActiveWindow()
            
            if not active_window:
                return self.format_error("No active window found")
            
            result = {
                'window_handle': str(active_window._hWnd) if hasattr(active_window, '_hWnd') else 'unknown',
                'title': active_window.title,
                'app_name': active_window.title.split(' - ')[-1] if ' - ' in active_window.title else active_window.title,
                'app_path': 'unknown',  # Would need psutil for this
                'process_id': 0,  # Would need psutil
                'position': {
                    'x': active_window.left,
                    'y': active_window.top
                },
                'size': {
                    'width': active_window.width,
                    'height': active_window.height
                },
                'is_maximized': active_window.isMaximized,
                'timestamp': datetime.now().isoformat()
            }
            
            Logger.info(self.name, f"Identified window: {result['title']}")
            return self.format_success(result)
            
        except Exception as e:
            Logger.error(self.name, f"Window identification failed: {e}")
            return self.format_error(f"Window identification failed: {str(e)}")
    
    def get_screen_cache(self) -> Dict[str, Any]:
        """Get the most recent cached screen analysis without recomputing.
        
        Returns:
            Cached analysis or error if no cache exists
        """
        try:
            # Try to get cached full analysis
            cache_key = self.get_cache_key(
                action='analyze_screen',
                include_text=True,
                include_elements=False
            )
            
            cached = self.get_cached_result(cache_key)
            
            if cached:
                # Calculate cache age
                timestamp_str = cached.get('timestamp', '')
                cache_age_seconds = 0
                if timestamp_str:
                    try:
                        cached_time = datetime.fromisoformat(timestamp_str)
                        cache_age_seconds = (datetime.now() - cached_time).total_seconds()
                    except:
                        pass
                
                result = {
                    'analysis': cached,
                    'cache_age_seconds': int(cache_age_seconds),
                    'cache_ttl_seconds': 300,  # 5 minutes
                    'is_expired': cache_age_seconds > 300
                }
                
                Logger.info(self.name, f"Retrieved cached analysis (age: {cache_age_seconds:.0f}s)")
                return self.format_success(result)
            else:
                return self.format_error("No cached analysis available", "CACHE_MISS")
                
        except Exception as e:
            Logger.error(self.name, f"Cache retrieval failed: {e}")
            return self.format_error(f"Cache retrieval failed: {str(e)}")


# Singleton instance
_screen_analyzer_instance = None

def get_screen_analyzer(mongodb=None, ai_brain=None) -> ScreenAnalyzer:
    """Get singleton instance of ScreenAnalyzer."""
    global _screen_analyzer_instance
    if _screen_analyzer_instance is None:
        _screen_analyzer_instance = ScreenAnalyzer(mongodb=mongodb, ai_brain=ai_brain)
    return _screen_analyzer_instance
