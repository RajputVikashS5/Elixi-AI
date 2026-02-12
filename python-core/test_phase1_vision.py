"""
Test Suite for Stage 5 Phase 1 - Screen Understanding
Tests ScreenAnalyzer and Vision API endpoints
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_screen_analyzer_import():
    """Test if ScreenAnalyzer can be imported."""
    print("\n=== Test 1: Import ScreenAnalyzer ===")
    try:
        from vision.screen_analyzer import ScreenAnalyzer, get_screen_analyzer
        print("✓ ScreenAnalyzer imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import ScreenAnalyzer: {e}")
        return False


def test_screen_analyzer_initialization():
    """Test ScreenAnalyzer initialization."""
    print("\n=== Test 2: Initialize ScreenAnalyzer ===")
    try:
        from vision.screen_analyzer import ScreenAnalyzer
        
        analyzer = ScreenAnalyzer(mongodb=None, enable_cache=False)
        print(f"✓ ScreenAnalyzer initialized: {analyzer.name}")
        print(f"  - Tesseract available: {analyzer.tesseract_available}")
        return True
    except Exception as e:
        print(f"✗ ScreenAnalyzer initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_window_identification():
    """Test window identification functionality."""
    print("\n=== Test 3: Window Identification ===")
    try:
        from vision.screen_analyzer import get_screen_analyzer
        
        analyzer = get_screen_analyzer()
        result = analyzer.identify_window()
        
        if result.get('status') == 'success':
            data = result.get('data', {})
            print(f"✓ Window identified:")
            print(f"  - Title: {data.get('title', 'Unknown')}")
            print(f"  - App: {data.get('app_name', 'Unknown')}")
            print(f"  - Size: {data.get('size', {})}")
            return True
        else:
            print(f"✗ Window identification failed: {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ Window identification test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_screenshot_capture():
    """Test screenshot capture."""
    print("\n=== Test 4: Screenshot Capture ===")
    try:
        from vision.screen_analyzer import get_screen_analyzer
        
        analyzer = get_screen_analyzer()
        screenshot = analyzer._capture_screenshot()
        
        if screenshot:
            print(f"✓ Screenshot captured:")
            print(f"  - Size: {screenshot.size}")
            print(f"  - Mode: {screenshot.mode}")
            return True
        else:
            print("✗ Screenshot capture failed")
            return False
    except Exception as e:
        print(f"✗ Screenshot capture test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_text_extraction():
    """Test OCR text extraction."""
    print("\n=== Test 5: Text Extraction (OCR) ===")
    try:
        from vision.screen_analyzer import get_screen_analyzer
        
        analyzer = get_screen_analyzer()
        
        if not analyzer.tesseract_available:
            print("⚠ Tesseract OCR not available - skipping test")
            print("  Install from: https://github.com/UB-Mannheim/tesseract/wiki")
            return None  # Skip, not a failure
        
        result = analyzer.get_screen_text(ocr_confidence_threshold=0.5)
        
        if result.get('status') == 'success':
            data = result.get('data', {})
            text = data.get('text', '')
            print(f"✓ Text extracted:")
            print(f"  - Characters: {data.get('num_characters', 0)}")
            print(f"  - Confidence: {data.get('ocr_confidence', 0):.2f}")
            print(f"  - Preview: {text[:100]}..." if len(text) > 100 else f"  - Text: {text}")
            return True
        else:
            print(f"✗ Text extraction failed: {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ Text extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_analysis():
    """Test full screen analysis."""
    print("\n=== Test 6: Full Screen Analysis ===")
    try:
        from vision.screen_analyzer import get_screen_analyzer
        
        analyzer = get_screen_analyzer()
        
        # Test with minimal options
        input_data = {
            'include_text': analyzer.tesseract_available,  # Only if available
            'include_elements': False,
            'ai_interpretation': False
        }
        
        result = analyzer.analyze(input_data)
        
        if result.get('status') == 'success':
            data = result.get('data', {})
            print(f"✓ Full analysis completed:")
            print(f"  - Window: {data.get('window_info', {}).get('title', 'Unknown')}")
            print(f"  - Text length: {data.get('full_text_length', 0)}")
            print(f"  - OCR confidence: {data.get('ocr_confidence', 0):.2f}")
            print(f"  - From cache: {data.get('from_cache', False)}")
            return True
        else:
            print(f"✗ Full analysis failed: {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ Full analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_functionality():
    """Test caching functionality."""
    print("\n=== Test 7: Cache Functionality ===")
    try:
        from vision.screen_analyzer import get_screen_analyzer
        
        analyzer = get_screen_analyzer()
        
        # Clear cache first
        if analyzer.cache:
            analyzer.cache.clear()
        
        # First call - should not be cached
        input_data = {
            'include_text': False,
            'include_elements': False,
            'ai_interpretation': False
        }
        
        result1 = analyzer.analyze(input_data)
        is_cached_1 = result1.get('data', {}).get('from_cache', False)
        
        # Second call - should be cached
        result2 = analyzer.analyze(input_data)
        is_cached_2 = result2.get('data', {}).get('from_cache', False)
        
        print(f"  - First call cached: {is_cached_1}")
        print(f"  - Second call cached: {is_cached_2}")
        
        if not is_cached_1 and is_cached_2:
            print("✓ Cache working correctly")
            return True
        elif not analyzer.enable_cache:
            print("⚠ Cache disabled - skipping test")
            return None
        else:
            print("✗ Cache not working as expected")
            return False
    except Exception as e:
        print(f"✗ Cache test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoint():
    """Test vision API endpoint (requires server running)."""
    print("\n=== Test 8: API Endpoint Test ===")
    try:
        import requests
        
        # Test /vision/identify-window endpoint
        response = requests.get("http://127.0.0.1:5000/vision/identify-window", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                window_data = data.get('data', {})
                print("✓ API endpoint working:")
                print(f"  - Window: {window_data.get('title', 'Unknown')}")
                return True
            else:
                print(f"✗ API returned error: {data.get('error', 'Unknown')}")
                return False
        else:
            print(f"✗ API request failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠ Server not running - skipping API test")
        print("  Start server with: python main.py")
        return None
    except Exception as e:
        print(f"✗ API test failed: {e}")
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "="*60)
    print("Stage 5 Phase 1 - Screen Understanding Test Suite")
    print("="*60)
    
    tests = [
        ("Import Test", test_screen_analyzer_import),
        ("Initialization Test", test_screen_analyzer_initialization),
        ("Window Identification", test_window_identification),
        ("Screenshot Capture", test_screenshot_capture),
        ("Text Extraction", test_text_extraction),
        ("Full Analysis", test_full_analysis),
        ("Cache Functionality", test_cache_functionality),
        ("API Endpoint", test_api_endpoint),
    ]
    
    results = {}
    for test_name, test_func in tests:
        result = test_func()
        results[test_name] = result
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    total = len(tests)
    
    for test_name, result in results.items():
        if result is True:
            status = "✓ PASS"
        elif result is False:
            status = "✗ FAIL"
        else:
            status = "⚠ SKIP"
        print(f"{status:10} {test_name}")
    
    print(f"\nResults: {passed} passed, {failed} failed, {skipped} skipped (total: {total})")
    
    if failed == 0:
        print("\n✓ All tests passed!")
        return True
    else:
        print(f"\n✗ {failed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
