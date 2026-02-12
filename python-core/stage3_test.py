"""
ELIXI AI - Stage 3 Test Suite
Full System Control Testing

Tests all Stage 3 features:
- Application Management
- Hardware Control (Volume, Brightness, WiFi)
- Power Management
- Screenshot & File Search
- System Monitoring
"""

import requests
import time
import json

BASE_URL = "http://127.0.0.1:5000"

def print_test_header(title):
    """Print formatted test section header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")

def print_result(test_name, result, success_key="success"):
    """Print test result"""
    status = "✅ PASS" if result.get(success_key) else "❌ FAIL"
    print(f"{status} | {test_name}")
    if not result.get(success_key):
        print(f"      Error: {result.get('error', 'Unknown error')}")
    return result.get(success_key, False)

def print_json(data, indent=2):
    """Print formatted JSON"""
    print(json.dumps(data, indent=indent))

# ========== SYSTEM STATUS ==========

def test_system_status():
    """Test that backend is running"""
    print_test_header("SYSTEM STATUS CHECK")
    try:
        response = requests.get(f"{BASE_URL}/system-status", timeout=3)
        result = response.json()
        print_result("Backend Connection", result)
        print(f"   Platform: {result.get('platform', 'Unknown')}")
        print(f"   Python: {result.get('python_version', 'Unknown')}")
        print(f"   Uptime: {result.get('uptime_sec', 0)}s")
        print(f"   DB Connected: {result.get('db_connected', False)}")
        return True
    except Exception as e:
        print(f"❌ FAIL | Backend Connection")
        print(f"      Error: {e}")
        return False

# ========== APPLICATION MANAGEMENT TESTS ==========

def test_application_management():
    """Test application control features"""
    print_test_header("APPLICATION MANAGEMENT TESTS")
    
    passed = 0
    total = 0
    
    # Test 1: List running applications
    print("Test 1: List Running Applications")
    try:
        response = requests.post(f"{BASE_URL}/system/app/list", json={}, timeout=5)
        result = response.json()
        total += 1
        if print_result("List Applications", result):
            passed += 1
            print(f"   Found {result.get('count', 0)} running applications")
            if result.get('applications'):
                for app in result['applications'][:5]:  # Show first 5
                    print(f"      - {app['name']} (PID: {app['pid']}, Memory: {app['memory_mb']:.1f} MB)")
    except Exception as e:
        print(f"❌ FAIL | List Applications: {e}")
        total += 1
    
    # Test 2: Open Notepad
    print("\nTest 2: Open Application (Notepad)")
    try:
        response = requests.post(
            f"{BASE_URL}/system/app/open",
            json={"app_name": "notepad"},
            timeout=5
        )
        result = response.json()
        total += 1
        if print_result("Open Notepad", result):
            passed += 1
            print(f"   PID: {result.get('pid', 'N/A')}")
            time.sleep(1)  # Give app time to open
    except Exception as e:
        print(f"❌ FAIL | Open Notepad: {e}")
        total += 1
    
    # Test 3: Get application info
    print("\nTest 3: Get Application Info (Notepad)")
    try:
        response = requests.post(
            f"{BASE_URL}/system/app/info",
            json={"app_name": "notepad"},
            timeout=5
        )
        result = response.json()
        total += 1
        if print_result("Get App Info", result):
            passed += 1
            print(f"   Running: {result.get('running', False)}")
            print(f"   Instances: {result.get('instance_count', 0)}")
    except Exception as e:
        print(f"❌ FAIL | Get App Info: {e}")
        total += 1
    
    # Test 4: Close Notepad
    print("\nTest 4: Close Application (Notepad)")
    try:
        response = requests.post(
            f"{BASE_URL}/system/app/close",
            json={"app_name": "notepad", "force": False},
            timeout=5
        )
        result = response.json()
        total += 1
        if print_result("Close Notepad", result):
            passed += 1
            print(f"   Closed {result.get('closed_count', 0)} instance(s)")
    except Exception as e:
        print(f"❌ FAIL | Close Notepad: {e}")
        total += 1
    
    print(f"\n📊 Application Management: {passed}/{total} tests passed")
    return passed, total

# ========== HARDWARE CONTROL TESTS ==========

def test_hardware_control():
    """Test hardware control features"""
    print_test_header("HARDWARE CONTROL TESTS")
    
    passed = 0
    total = 0
    
    # Volume Tests
    print("Volume Control Tests:")
    
    # Test 1: Get current volume
    try:
        response = requests.post(f"{BASE_URL}/system/hardware/volume/get", json={}, timeout=5)
        result = response.json()
        total += 1
        if print_result("  Get Volume", result):
            passed += 1
            original_volume = result.get('volume', 50)
            print(f"     Current: {original_volume}%, Muted: {result.get('muted', False)}")
        else:
            original_volume = 50
    except Exception as e:
        print(f"  ❌ FAIL | Get Volume: {e}")
        total += 1
        original_volume = 50
    
    # Test 2: Set volume
    try:
        response = requests.post(
            f"{BASE_URL}/system/hardware/volume/set",
            json={"level": 30},
            timeout=5
        )
        result = response.json()
        total += 1
        if print_result("  Set Volume to 30%", result):
            passed += 1
            time.sleep(0.5)
    except Exception as e:
        print(f"  ❌ FAIL | Set Volume: {e}")
        total += 1
    
    # Test 3: Restore original volume
    try:
        response = requests.post(
            f"{BASE_URL}/system/hardware/volume/set",
            json={"level": original_volume},
            timeout=5
        )
        result = response.json()
        total += 1
        if print_result(f"  Restore Volume to {original_volume}%", result):
            passed += 1
    except Exception as e:
        print(f"  ❌ FAIL | Restore Volume: {e}")
        total += 1
    
    # Brightness Tests
    print("\nBrightness Control Tests:")
    
    # Test 4: Get brightness
    try:
        response = requests.post(f"{BASE_URL}/system/hardware/brightness/get", json={}, timeout=5)
        result = response.json()
        total += 1
        if print_result("  Get Brightness", result):
            passed += 1
            print(f"     Current: {result.get('brightness', 'N/A')}%")
    except Exception as e:
        print(f"  ❌ FAIL | Get Brightness: {e}")
        total += 1
    
    # WiFi Tests
    print("\nWiFi Control Tests:")
    
    # Test 5: Get WiFi status
    try:
        response = requests.post(f"{BASE_URL}/system/hardware/wifi/status", json={}, timeout=5)
        result = response.json()
        total += 1
        if print_result("  Get WiFi Status", result):
            passed += 1
            print(f"     Enabled: {result.get('enabled', False)}")
            print(f"     Connected: {result.get('connected', False)}")
            print(f"     Network: {result.get('network', 'N/A')}")
    except Exception as e:
        print(f"  ❌ FAIL | Get WiFi Status: {e}")
        total += 1
    
    print(f"\n📊 Hardware Control: {passed}/{total} tests passed")
    return passed, total

# ========== SYSTEM MONITORING TESTS ==========

def test_system_monitoring():
    """Test system monitoring features"""
    print_test_header("SYSTEM MONITORING TESTS")
    
    passed = 0
    total = 0
    
    # Test 1: System Overview
    print("Test 1: System Overview")
    try:
        response = requests.post(f"{BASE_URL}/system/monitor/overview", json={}, timeout=5)
        result = response.json()
        total += 1
        if print_result("System Overview", result):
            passed += 1
            system = result.get('system', {})
            cpu = result.get('cpu', {})
            memory = result.get('memory', {})
            print(f"   Platform: {system.get('platform', 'Unknown')}")
            print(f"   Uptime: {system.get('uptime_hours', 0):.1f} hours")
            print(f"   CPU Usage: {cpu.get('usage_percent', 0):.1f}%")
            print(f"   Memory Used: {memory.get('used_gb', 0):.1f}/{memory.get('total_gb', 0):.1f} GB")
    except Exception as e:
        print(f"❌ FAIL | System Overview: {e}")
        total += 1
    
    # Test 2: CPU Info
    print("\nTest 2: CPU Information")
    try:
        response = requests.post(f"{BASE_URL}/system/monitor/cpu/info", json={}, timeout=5)
        result = response.json()
        total += 1
        if print_result("CPU Info", result):
            passed += 1
            print(f"   Physical Cores: {result.get('physical_cores', 'N/A')}")
            print(f"   Logical Cores: {result.get('logical_cores', 'N/A')}")
            freq = result.get('frequency', {})
            if freq and freq.get('current'):
                print(f"   Frequency: {freq['current']:.0f} MHz")
    except Exception as e:
        print(f"❌ FAIL | CPU Info: {e}")
        total += 1
    
    # Test 3: Memory Usage
    print("\nTest 3: Memory Usage")
    try:
        response = requests.post(f"{BASE_URL}/system/monitor/memory", json={}, timeout=5)
        result = response.json()
        total += 1
        if print_result("Memory Usage", result):
            passed += 1
            ram = result.get('ram', {})
            print(f"   Total: {ram.get('total_gb', 0):.2f} GB")
            print(f"   Used: {ram.get('used_gb', 0):.2f} GB ({ram.get('percent', 0):.1f}%)")
            print(f"   Available: {ram.get('available_gb', 0):.2f} GB")
    except Exception as e:
        print(f"❌ FAIL | Memory Usage: {e}")
        total += 1
    
    # Test 4: Top Memory Processes
    print("\nTest 4: Top Memory Processes")
    try:
        response = requests.post(
            f"{BASE_URL}/system/monitor/memory/top-processes",
            json={"count": 5},
            timeout=5
        )
        result = response.json()
        total += 1
        if print_result("Top Processes", result):
            passed += 1
            for proc in result.get('processes', [])[:5]:
                print(f"   - {proc['name']}: {proc['memory_mb']:.1f} MB")
    except Exception as e:
        print(f"❌ FAIL | Top Processes: {e}")
        total += 1
    
    # Test 5: Disk Usage
    print("\nTest 5: Disk Usage")
    try:
        response = requests.post(f"{BASE_URL}/system/monitor/disk", json={}, timeout=5)
        result = response.json()
        total += 1
        if print_result("Disk Usage", result):
            passed += 1
            for partition in result.get('partitions', [])[:3]:  # Show first 3 drives
                print(f"   {partition['device']}: {partition['used_gb']:.1f}/{partition['total_gb']:.1f} GB ({partition['percent']:.1f}%)")
    except Exception as e:
        print(f"❌ FAIL | Disk Usage: {e}")
        total += 1
    
    # Test 6: Network Usage
    print("\nTest 6: Network Usage")
    try:
        response = requests.post(f"{BASE_URL}/system/monitor/network", json={}, timeout=5)
        result = response.json()
        total += 1
        if print_result("Network Usage", result):
            passed += 1
            print(f"   Sent: {result.get('sent_gb', 0):.2f} GB")
            print(f"   Received: {result.get('recv_gb', 0):.2f} GB")
    except Exception as e:
        print(f"❌ FAIL | Network Usage: {e}")
        total += 1
    
    # Test 7: Battery Status (if available)
    print("\nTest 7: Battery Status")
    try:
        response = requests.post(f"{BASE_URL}/system/monitor/battery", json={}, timeout=5)
        result = response.json()
        total += 1
        # Battery may not be available on desktop
        if result.get('success'):
            print_result("Battery Status", result)
            passed += 1
            print(f"   Charge: {result.get('percent', 0)}%")
            print(f"   Plugged In: {result.get('power_plugged', False)}")
            if result.get('minutes_left'):
                print(f"   Time Left: {result['minutes_left']:.0f} minutes")
        else:
            print("  ⚠️  SKIP | Battery Status (Desktop system)")
            # Don't count as pass or fail
            total -= 1
    except Exception as e:
        print(f"  ⚠️  SKIP | Battery Status: {e}")
        # Don't count as fail if battery not available
        total -= 1
    
    print(f"\n📊 System Monitoring: {passed}/{total} tests passed")
    return passed, total

# ========== SCREENSHOT & FILE SEARCH TESTS ==========

def test_screenshot_and_files():
    """Test screenshot and file search features"""
    print_test_header("SCREENSHOT & FILE SEARCH TESTS")
    
    passed = 0
    total = 0
    
    # Test 1: Auto-save screenshot
    print("Test 1: Capture and Auto-Save Screenshot")
    try:
        response = requests.post(
            f"{BASE_URL}/system/screenshot/auto-save",
            json={"prefix": "elixi_test"},
            timeout=10
        )
        result = response.json()
        total += 1
        if print_result("Screenshot Capture", result):
            passed += 1
            print(f"   Saved to: {result.get('file_path', 'N/A')}")
            print(f"   Size: {result.get('width', 0)}x{result.get('height', 0)}")
    except Exception as e:
        print(f"❌ FAIL | Screenshot Capture: {e}")
        total += 1
    
    # Test 2: Search for files
    print("\nTest 2: File Search")
    try:
        response = requests.post(
            f"{BASE_URL}/system/files/search",
            json={"query": "test", "max_results": 10},
            timeout=10
        )
        result = response.json()
        total += 1
        if print_result("File Search", result):
            passed += 1
            print(f"   Found {result.get('count', 0)} files")
            for file in result.get('results', [])[:3]:  # Show first 3
                print(f"      - {file['name']} ({file['size_mb']} MB)")
    except Exception as e:
        print(f"❌ FAIL | File Search: {e}")
        total += 1
    
    # Test 3: Get recent files
    print("\nTest 3: Recent Files")
    try:
        response = requests.post(
            f"{BASE_URL}/system/files/recent",
            json={"days": 7, "max_results": 10},
            timeout=10
        )
        result = response.json()
        total += 1
        if print_result("Recent Files", result):
            passed += 1
            print(f"   Found {result.get('count', 0)} recent files")
            for file in result.get('results', [])[:3]:  # Show first 3
                print(f"      - {file['name']}")
    except Exception as e:
        print(f"❌ FAIL | Recent Files: {e}")
        total += 1
    
    print(f"\n📊 Screenshot & Files: {passed}/{total} tests passed")
    return passed, total

# ========== POWER MANAGEMENT TESTS ==========

def test_power_management():
    """Test power management features (safe operations only)"""
    print_test_header("POWER MANAGEMENT TESTS (Safe Operations Only)")
    
    passed = 0
    total = 0
    
    print("⚠️  Note: Only testing lock screen. Shutdown/restart tests are skipped for safety.\n")
    
    # Test 1: Lock screen (will actually lock, so ask first)
    print("Test 1: Lock Screen")
    print("⚠️  This will lock your screen. Press Enter to continue or Ctrl+C to skip...")
    try:
        input()
        response = requests.post(f"{BASE_URL}/system/power/lock", json={}, timeout=5)
        result = response.json()
        total += 1
        if print_result("Lock Screen", result):
            passed += 1
    except KeyboardInterrupt:
        print("  ⚠️  SKIP | Lock Screen (User skipped)")
        total += 1
    except Exception as e:
        print(f"❌ FAIL | Lock Screen: {e}")
        total += 1
    
    print(f"\n📊 Power Management: {passed}/{total} tests passed")
    return passed, total

# ========== MAIN TEST RUNNER ==========

def main():
    """Run all Stage 3 tests"""
    print("\n" + "=" * 60)
    print("  ELIXI AI - STAGE 3 TEST SUITE")
    print("  Full System Control Testing")
    print("=" * 60)
    
    # Check backend connection first
    if not test_system_status():
        print("\n❌ Backend is not running. Please start main.py first.")
        print("   Run: python main.py")
        return
    
    total_passed = 0
    total_tests = 0
    
    # Run all test suites
    test_suites = [
        ("Application Management", test_application_management),
        ("Hardware Control", test_hardware_control),
        ("System Monitoring", test_system_monitoring),
        ("Screenshot & Files", test_screenshot_and_files),
        ("Power Management", test_power_management),
    ]
    
    for suite_name, test_func in test_suites:
        try:
            passed, total = test_func()
            total_passed += passed
            total_tests += total
        except Exception as e:
            print(f"\n❌ Error running {suite_name} tests: {e}")
    
    # Print final results
    print("\n" + "=" * 60)
    print("  FINAL RESULTS")
    print("=" * 60)
    
    percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"\n✅ Passed: {total_passed}/{total_tests} ({percentage:.1f}%)")
    
    if percentage == 100:
        print("\n🎉 ALL TESTS PASSED! Stage 3 implementation is complete!")
    elif percentage >= 80:
        print("\n✅ Most tests passed! Stage 3 is mostly functional.")
    elif percentage >= 50:
        print("\n⚠️  Some tests failed. Review the errors above.")
    else:
        print("\n❌ Many tests failed. Please review the implementation.")
    
    print("\n" + "=" * 60)
    print("  Stage 3: Full System Control - Testing Complete")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing cancelled by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
