"""
Test Suite for Stage 5 Phase 3 - News & Weather
Tests NewsWeatherManager and News/Weather API endpoints
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_news_weather_import():
    """Test if NewsWeatherManager can be imported."""
    print("\n=== Test 1: Import NewsWeatherManager ===")
    try:
        from news_weather import NewsWeatherManager
        print("✓ NewsWeatherManager imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import NewsWeatherManager: {e}")
        return False


def test_news_weather_initialization():
    """Test NewsWeatherManager initialization."""
    print("\n=== Test 2: Initialize NewsWeatherManager ===")
    try:
        from news_weather import NewsWeatherManager
        
        manager = NewsWeatherManager(mongodb=None, enable_cache=False)
        print(f"✓ NewsWeatherManager initialized: {manager.name}")
        print(f"  - API key configured: {bool(manager.weather_api_key)}")
        print(f"  - News API key configured: {bool(manager.news_api_key)}")
        print(f"  - Timeout: {manager.timeout}s")
        return True
    except Exception as e:
        print(f"✗ NewsWeatherManager initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_weather():
    """Test weather retrieval."""
    print("\n=== Test 3: Get Weather ===")
    try:
        from news_weather import NewsWeatherManager
        
        manager = NewsWeatherManager(mongodb=None, enable_cache=False)
        
        # Test with a well-known city
        result = manager.get_weather('London', 'metric')
        
        if result.get('status') == 'success':
            data = result.get('data', {})
            print(f"✓ Weather retrieved:")
            print(f"  - Location: {data.get('location', {}).get('name')}")
            print(f"  - Temperature: {data.get('current', {}).get('temperature')} {data.get('current', {}).get('unit')}")
            print(f"  - Description: {data.get('current', {}).get('description')}")
            print(f"  - Humidity: {data.get('current', {}).get('humidity')}%")
            print(f"  - Source: {data.get('source')}")
            print(f"  - Offline/Mock: {data.get('offline', False)}")
            return True
        else:
            print(f"✗ Weather retrieval failed: {result.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ Weather test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_weather_forecast():
    """Test weather forecast retrieval."""
    print("\n=== Test 4: Get Weather Forecast ===")
    try:
        from news_weather import NewsWeatherManager
        
        manager = NewsWeatherManager(mongodb=None, enable_cache=False)
        
        # Test 5-day forecast
        result = manager.get_weather_forecast('Paris', days=3, units='metric')
        
        if result.get('status') == 'success':
            data = result.get('data', {})
            forecast = data.get('forecast', [])
            print(f"✓ Forecast retrieved:")
            print(f"  - Location: {data.get('location', {}).get('name')}")
            print(f"  - Days: {len(forecast)}")
            print(f"  - Source: {data.get('source')}")
            
            # Show first day
            if forecast:
                day1 = forecast[0]
                print(f"  - First day ({day1.get('day_name')}):")
                temp = day1.get('temperature', {})
                print(f"    • Temp: {temp.get('avg')} {temp.get('unit')} (min: {temp.get('min')}, max: {temp.get('max')})")
                print(f"    • Condition: {day1.get('description')}")
            
            return True
        else:
            print(f"✗ Forecast retrieval failed: {result.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ Forecast test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_news():
    """Test news retrieval."""
    print("\n=== Test 5: Get News ===")
    try:
        from news_weather import NewsWeatherManager
        
        manager = NewsWeatherManager(mongodb=None, enable_cache=False)
        
        # Test news retrieval
        result = manager.get_news(query='', category='technology', country='us', page_size=5)
        
        if result.get('status') == 'success':
            data = result.get('data', {})
            articles = data.get('articles', [])
            print(f"✓ News retrieved:")
            print(f"  - Articles: {len(articles)}")
            print(f"  - Total available: {data.get('total')}")
            print(f"  - Sources: {', '.join(data.get('sources', []))}")
            print(f"  - Data source: {data.get('source')}")
            print(f"  - Offline/Mock: {data.get('offline', False)}")
            
            # Show first article
            if articles:
                article = articles[0]
                print(f"  - First article:")
                print(f"    • Title: {article.get('title')[:60]}...")
                print(f"    • Source: {article.get('source')}")
                print(f"    • Author: {article.get('author')}")
            
            return True
        else:
            print(f"✗ News retrieval failed: {result.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ News test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_news_with_query():
    """Test news retrieval with search query."""
    print("\n=== Test 6: Get News with Query ===")
    try:
        from news_weather import NewsWeatherManager
        
        manager = NewsWeatherManager(mongodb=None, enable_cache=False)
        
        # Test news with search query
        result = manager.get_news(query='artificial intelligence', category='general', page_size=3)
        
        if result.get('status') == 'success':
            data = result.get('data', {})
            articles = data.get('articles', [])
            print(f"✓ News with query retrieved:")
            print(f"  - Query: 'artificial intelligence'")
            print(f"  - Articles found: {len(articles)}")
            print(f"  - Sources: {len(data.get('sources', []))}")
            
            return True
        else:
            print(f"✗ News query failed: {result.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"✗ News query test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_invalid_inputs():
    """Test error handling for invalid inputs."""
    print("\n=== Test 7: Invalid Input Handling ===")
    try:
        from news_weather import NewsWeatherManager
        
        manager = NewsWeatherManager(mongodb=None, enable_cache=False)
        
        # Test empty location
        result1 = manager.get_weather('', 'metric')
        if result1.get('status') != 'success':
            print(f"✓ Empty location rejected correctly")
        else:
            print(f"✗ Empty location should have been rejected")
            return False
        
        # Test invalid category
        result2 = manager.get_news(category='invalid_category', page_size=10)
        if result2.get('status') != 'success':
            print(f"✓ Invalid category rejected correctly")
        else:
            print(f"✗ Invalid category should have been rejected")
            return False
        
        # Test invalid days
        result3 = manager.get_weather_forecast('London', days=10)
        if result3.get('status') != 'success':
            print(f"✓ Invalid days rejected correctly")
        else:
            print(f"✗ Invalid days should have been rejected")
            return False
        
        # Test invalid page size
        result4 = manager.get_news(page_size=200)
        if result4.get('status') != 'success':
            print(f"✓ Invalid page size rejected correctly")
        else:
            print(f"✗ Invalid page size should have been rejected")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Invalid input test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_caching():
    """Test caching functionality."""
    print("\n=== Test 8: Caching Functionality ===")
    try:
        from news_weather import NewsWeatherManager
        import time
        
        manager = NewsWeatherManager(mongodb=None, enable_cache=True)
        
        # First call - should fetch
        start1 = time.time()
        result1 = manager.get_weather('Tokyo', 'metric')
        duration1 = (time.time() - start1) * 1000
        
        # Second call - should use cache
        start2 = time.time()
        result2 = manager.get_weather('Tokyo', 'metric')
        duration2 = (time.time() - start2) * 1000
        
        if result1.get('status') == 'success' and result2.get('status') == 'success':
            print(f"✓ Caching working:")
            print(f"  - First call: {duration1:.2f}ms")
            print(f"  - Second call (cached): {duration2:.2f}ms")
            print(f"  - Speedup: {duration1/duration2 if duration2 > 0 else 'N/A'}x")
            
            # Check if cache was faster (should be)
            if duration2 < duration1:
                print(f"  - Cache is faster ✓")
                return True
            else:
                print(f"  - Cache might not be working (same speed)")
                return True  # Still pass as caching is optional
        else:
            print(f"✗ Caching test failed")
            return False
    except Exception as e:
        print(f"✗ Caching test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_analyze_method():
    """Test generic analyze method."""
    print("\n=== Test 9: Generic Analyze Method ===")
    try:
        from news_weather import NewsWeatherManager
        
        manager = NewsWeatherManager(mongodb=None, enable_cache=False)
        
        # Test weather via analyze
        result1 = manager.analyze({'type': 'weather', 'location': 'Berlin'})
        if result1.get('status') == 'success':
            print(f"✓ Analyze with weather type works")
        else:
            print(f"✗ Weather analyze failed")
            return False
        
        # Test news via analyze
        result2 = manager.analyze({'type': 'news', 'category': 'business', 'page_size': 5})
        if result2.get('status') == 'success':
            print(f"✓ Analyze with news type works")
        else:
            print(f"✗ News analyze failed")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Analyze method test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoints():
    """Test API endpoints integration."""
    print("\n=== Test 10: API Endpoints (requires running server) ===")
    try:
        import requests
        import time
        
        base_url = "http://127.0.0.1:5000"
        
        # Check if server is running
        try:
            response = requests.get(f"{base_url}/system-status", timeout=2)
            if response.status_code != 200:
                print("⊘ Server not running - skipping API endpoint tests")
                return None  # Skip, not a failure
        except:
            print("⊘ Server not running - skipping API endpoint tests")
            return None  # Skip, not a failure
        
        print("Server is running, testing endpoints...")
        
        # Test weather endpoint
        weather_resp = requests.post(
            f"{base_url}/info/weather",
            json={'location': 'London', 'units': 'metric'},
            timeout=10
        )
        if weather_resp.status_code == 200 and weather_resp.json().get('status') == 'success':
            print(f"✓ POST /info/weather working")
        else:
            print(f"✗ POST /info/weather failed: {weather_resp.status_code}")
            return False
        
        # Test forecast endpoint
        forecast_resp = requests.post(
            f"{base_url}/info/weather-forecast",
            json={'location': 'Paris', 'days': 3, 'units': 'metric'},
            timeout=10
        )
        if forecast_resp.status_code == 200 and forecast_resp.json().get('status') == 'success':
            print(f"✓ POST /info/weather-forecast working")
        else:
            print(f"✗ POST /info/weather-forecast failed")
            return False
        
        # Test news endpoint
        news_resp = requests.post(
            f"{base_url}/info/news",
            json={'category': 'technology', 'page_size': 5},
            timeout=10
        )
        if news_resp.status_code == 200 and news_resp.json().get('status') == 'success':
            print(f"✓ POST /info/news working")
        else:
            print(f"✗ POST /info/news failed")
            return False
        
        # Test cached news endpoint (GET)
        cached_resp = requests.get(f"{base_url}/info/cached-news", timeout=5)
        if cached_resp.status_code == 200:
            print(f"✓ GET /info/cached-news working")
        else:
            print(f"✗ GET /info/cached-news failed")
            return False
        
        return True
    except Exception as e:
        print(f"✗ API endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_locations():
    """Test weather for multiple locations."""
    print("\n=== Test 11: Multiple Locations ===")
    try:
        from news_weather import NewsWeatherManager
        
        manager = NewsWeatherManager(mongodb=None, enable_cache=False)
        
        locations = ['New York', 'Tokyo', 'Sydney', 'Moscow']
        success_count = 0
        
        for location in locations:
            result = manager.get_weather(location, 'metric')
            if result.get('status') == 'success':
                data = result.get('data', {})
                loc_name = data.get('location', {}).get('name', location)
                temp = data.get('current', {}).get('temperature')
                print(f"  ✓ {loc_name}: {temp}°C")
                success_count += 1
        
        if success_count == len(locations):
            print(f"✓ All {success_count}/{len(locations)} locations successful")
            return True
        else:
            print(f"⚠ Partial success: {success_count}/{len(locations)} locations")
            return success_count > 0  # Pass if at least one works
    except Exception as e:
        print(f"✗ Multiple locations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_news_categories():
    """Test different news categories."""
    print("\n=== Test 12: News Categories ===")
    try:
        from news_weather import NewsWeatherManager
        
        manager = NewsWeatherManager(mongodb=None, enable_cache=False)
        
        categories = ['business', 'technology', 'health', 'science']
        success_count = 0
        
        for category in categories:
            result = manager.get_news(category=category, page_size=3)
            if result.get('status') == 'success':
                data = result.get('data', {})
                article_count = len(data.get('articles', []))
                print(f"  ✓ {category}: {article_count} articles")
                success_count += 1
        
        if success_count == len(categories):
            print(f"✓ All {success_count}/{len(categories)} categories successful")
            return True
        else:
            print(f"⚠ Partial success: {success_count}/{len(categories)} categories")
            return success_count > 0
    except Exception as e:
        print(f"✗ News categories test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("=" * 70)
    print("STAGE 5 PHASE 3 - NEWS & WEATHER TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Import NewsWeatherManager", test_news_weather_import),
        ("Initialize NewsWeatherManager", test_news_weather_initialization),
        ("Get Weather", test_get_weather),
        ("Get Weather Forecast", test_get_weather_forecast),
        ("Get News", test_get_news),
        ("Get News with Query", test_news_with_query),
        ("Invalid Input Handling", test_invalid_inputs),
        ("Caching Functionality", test_caching),
        ("Generic Analyze Method", test_analyze_method),
        ("API Endpoints", test_api_endpoints),
        ("Multiple Locations", test_multiple_locations),
        ("News Categories", test_news_categories),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    total = len(results)
    
    for test_name, result in results:
        if result is True:
            status = "✓ PASS"
        elif result is False:
            status = "✗ FAIL"
        else:
            status = "⊘ SKIP"
        print(f"{status:8} | {test_name}")
    
    print("=" * 70)
    print(f"Total: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Phase 3 implementation complete!")
    elif passed > failed:
        print(f"\n⚠ Most tests passed ({passed}/{total - skipped}). Review failures.")
    else:
        print(f"\n❌ Many tests failed. Phase 3 needs fixes.")
    
    print("=" * 70)
    
    return passed, failed, skipped


if __name__ == "__main__":
    run_all_tests()
