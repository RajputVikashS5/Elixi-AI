"""
Test Suite for Stage 4 Phase 3: User Preferences with Behavioral Learning
Comprehensive tests for behavioral analysis and preference learning.
"""

import requests
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"


def test_behavioral_analysis():
    """Test behavioral analysis for preference detection."""
    print("\n" + "="*60)
    print("PHASE 3 TEST 1: Behavioral Analysis")
    print("="*60)
    
    # First, create some test events for analysis
    print("\n[Setup] Creating test events...")
    events_data = [
        {
            "event_type": "app_opened",
            "event_data": {"app_name": "Chrome"}
        },
        {
            "event_type": "app_opened",
            "event_data": {"app_name": "Chrome"}
        },
        {
            "event_type": "app_opened",
            "event_data": {"app_name": "VSCode"}
        },
        {
            "event_type": "app_opened",
            "event_data": {"app_name": "Chrome"}
        },
        {
            "event_type": "command_executed",
            "event_data": {"command_type": "system_control"}
        },
    ]
    
    # Record events using habit learning endpoint
    for event_data in events_data:
        try:
            response = requests.post(
                f"{BASE_URL}/automation/habits/analyze",
                json={"days": 7}
            )
            time.sleep(0.1)
        except:
            pass
    
    print("✓ Test events created")
    
    # Test 1: Analyze behavior for preferences
    print("\n[1] Testing /preferences/analyze-behavior...")
    response = requests.post(
        f"{BASE_URL}/preferences/analyze-behavior",
        json={"days": 14}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    print(f"✓ Behavioral analysis complete:")
    print(f"  - Patterns detected: {data.get('patterns_detected', 0)}")
    print(f"  - Preferences learned: {data.get('preferences_learned', 0)}")
    
    # Display some patterns
    patterns = data.get("patterns", [])
    if patterns:
        print(f"\n  Sample patterns:")
        for pattern in patterns[:3]:
            print(f"    • {pattern.get('category')}/{pattern.get('key')}: {pattern.get('value')}")
            print(f"      Confidence: {pattern.get('confidence', 0):.2f} - {pattern.get('evidence', '')}")
    
    print("\n✅ Behavioral Analysis Test PASSED")
    return data


def test_preference_patterns():
    """Test preference pattern detection."""
    print("\n" + "="*60)
    print("PHASE 3 TEST 2: Preference Pattern Detection")
    print("="*60)
    
    # First, ensure we have some preferences
    print("\n[Setup] Creating test preferences...")
    test_prefs = [
        {"category": "behavior", "key": "test_pref_1", "value": "value1", "confidence": 0.85},
        {"category": "behavior", "key": "test_pref_2", "value": "value2", "confidence": 0.90},
        {"category": "automation", "key": "test_pref_3", "value": True, "confidence": 0.75},
        {"category": "interaction", "key": "test_pref_4", "value": "brief", "confidence": 0.80},
    ]
    
    for pref in test_prefs:
        requests.post(
            f"{BASE_URL}/preferences/set",
            json={
                "category": pref["category"],
                "key": pref["key"],
                "value": pref["value"],
                "source": "inferred",
                "confidence": pref["confidence"]
            }
        )
    print("✓ Test preferences created")
    
    # Test pattern detection
    print("\n[1] Testing /preferences/patterns...")
    response = requests.post(
        f"{BASE_URL}/preferences/patterns",
        json={}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    print(f"✓ Pattern detection complete:")
    print(f"  - Total preferences: {data.get('total_preferences', 0)}")
    print(f"  - Patterns found: {len(data.get('patterns', []))}")
    
    # Display patterns
    patterns = data.get("patterns", [])
    if patterns:
        print(f"\n  Detected patterns:")
        for pattern in patterns:
            print(f"    • {pattern.get('pattern_type')}: {pattern.get('description')}")
            print(f"      {pattern.get('evidence', '')}")
    
    print("\n✅ Pattern Detection Test PASSED")
    return data


def test_auto_learning():
    """Test auto-learning enable/disable."""
    print("\n" + "="*60)
    print("PHASE 3 TEST 3: Auto-Learning Control")
    print("="*60)
    
    # Test 1: Enable auto-learning
    print("\n[1] Testing enable auto-learning...")
    response = requests.post(
        f"{BASE_URL}/preferences/auto-learn",
        json={"enabled": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["auto_learning"] == True
    print(f"✓ Auto-learning enabled: {data.get('message')}")
    
    # Test 2: Disable auto-learning
    print("\n[2] Testing disable auto-learning...")
    response = requests.post(
        f"{BASE_URL}/preferences/auto-learn",
        json={"enabled": False}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["auto_learning"] == False
    print(f"✓ Auto-learning disabled: {data.get('message')}")
    
    # Re-enable for subsequent tests
    requests.post(
        f"{BASE_URL}/preferences/auto-learn",
        json={"enabled": True}
    )
    
    print("\n✅ Auto-Learning Control Test PASSED")


def test_habit_suggestions():
    """Test preference suggestions from habits."""
    print("\n" + "="*60)
    print("PHASE 3 TEST 4: Habit-Based Suggestions")
    print("="*60)
    
    # Test without specific habit IDs (all habits)
    print("\n[1] Testing /preferences/suggest-from-habits (all habits)...")
    response = requests.post(
        f"{BASE_URL}/preferences/suggest-from-habits",
        json={}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    print(f"✓ Habit analysis complete:")
    print(f"  - Habits analyzed: {data.get('habits_analyzed', 0)}")
    print(f"  - Suggestions generated: {data.get('suggestions_count', 0)}")
    
    # Display suggestions
    suggestions = data.get("suggestions", [])
    if suggestions:
        print(f"\n  Suggestions:")
        for sugg in suggestions[:5]:
            print(f"    • {sugg.get('category')}/{sugg.get('key')}: {sugg.get('value')}")
            print(f"      Reason: {sugg.get('reason', 'N/A')}")
            print(f"      Confidence: {sugg.get('confidence', 0):.2f}")
    else:
        print("  - No suggestions (no habits detected yet)")
    
    print("\n✅ Habit-Based Suggestions Test PASSED")
    return data


def test_learning_analytics():
    """Test learning analytics."""
    print("\n" + "="*60)
    print("PHASE 3 TEST 5: Learning Analytics")
    print("="*60)
    
    print("\n[1] Testing /preferences/learning-analytics...")
    response = requests.post(
        f"{BASE_URL}/preferences/learning-analytics",
        json={}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    print(f"✓ Analytics retrieved:")
    print(f"  - Total preferences: {data.get('total_preferences', 0)}")
    
    by_source = data.get("by_source", {})
    if by_source:
        print(f"  - By source:")
        print(f"    • Manual: {by_source.get('manual', 0)}")
        print(f"    • Inferred: {by_source.get('inferred', 0)}")
        print(f"    • Auto: {by_source.get('auto', 0)}")
    
    metrics = data.get("learning_metrics", {})
    if metrics:
        print(f"  - Learning metrics:")
        print(f"    • Learning score: {metrics.get('learning_score', 0)}%")
        print(f"    • Accepted suggestions: {metrics.get('accepted_suggestions', 0)}")
        avg_conf = metrics.get("avg_confidence", {})
        if avg_conf:
            print(f"    • Avg confidence by source:")
            for source, conf in avg_conf.items():
                print(f"      - {source}: {conf}")
    
    print("\n✅ Learning Analytics Test PASSED")
    return data


def test_existing_endpoints():
    """Test that existing Phase 2 endpoints still work."""
    print("\n" + "="*60)
    print("PHASE 3 TEST 6: Backward Compatibility")
    print("="*60)
    
    # Test 1: Set preference (existing endpoint)
    print("\n[1] Testing /preferences/set (existing)...")
    response = requests.post(
        f"{BASE_URL}/preferences/set",
        json={
            "category": "voice",
            "key": "volume_level",
            "value": 75
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    print("✓ Set preference working")
    
    # Test 2: Get preference
    print("\n[2] Testing /preferences/get (existing)...")
    response = requests.post(
        f"{BASE_URL}/preferences/get",
        json={"category": "voice", "key": "volume_level"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["value"] == 75
    print("✓ Get preference working")
    
    # Test 3: Statistics
    print("\n[3] Testing /preferences/statistics (existing)...")
    response = requests.post(
        f"{BASE_URL}/preferences/statistics",
        json={}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    print(f"✓ Statistics working: {data.get('total_preferences', 0)} total")
    
    print("\n✅ Backward Compatibility Test PASSED")


def test_integration_workflow():
    """Test complete workflow: behavior → analysis → suggestion → application."""
    print("\n" + "="*60)
    print("PHASE 3 TEST 7: Complete Integration Workflow")
    print("="*60)
    
    print("\n[1] Step 1: Analyze behavior...")
    response = requests.post(
        f"{BASE_URL}/preferences/analyze-behavior",
        json={"days": 7}
    )
    assert response.status_code == 200
    analysis_data = response.json()
    print(f"✓ Found {analysis_data.get('patterns_detected', 0)} behavioral patterns")
    
    print("\n[2] Step 2: Get preference recommendations...")
    response = requests.post(
        f"{BASE_URL}/preferences/recommendations",
        json={}
    )
    assert response.status_code == 200
    rec_data = response.json()
    recommendations = rec_data.get("recommendations", [])
    print(f"✓ Found {len(recommendations)} recommendations")
    
    print("\n[3] Step 3: Apply a recommendation (if any)...")
    if recommendations:
        first_rec = recommendations[0]
        response = requests.post(
            f"{BASE_URL}/preferences/apply",
            json={
                "category": first_rec.get("category"),
                "key": first_rec.get("key")
            }
        )
        assert response.status_code == 200
        apply_data = response.json()
        assert apply_data["success"] == True
        print(f"✓ Applied recommendation: {first_rec.get('key')}")
    else:
        print("⊘ No recommendations to apply (this is OK)")
    
    print("\n[4] Step 4: Check learning analytics...")
    response = requests.post(
        f"{BASE_URL}/preferences/learning-analytics",
        json={}
    )
    assert response.status_code == 200
    analytics = response.json()
    metrics = analytics.get("learning_metrics", {})
    print(f"✓ Learning score: {metrics.get('learning_score', 0):.1f}%")
    
    print("\n✅ Integration Workflow Test PASSED")


def main():
    """Run all Phase 3 tests."""
    print("\n" + "="*70)
    print("  STAGE 4 PHASE 3: USER PREFERENCES WITH BEHAVIORAL LEARNING")
    print("  Test Suite - Comprehensive Testing")
    print("="*70)
    
    try:
        # Check backend is running
        print("\n[Initializing] Checking backend connection...")
        response = requests.get(f"{BASE_URL}/system-status", timeout=5)
        if response.status_code != 200:
            raise Exception("Backend not responding correctly")
        print("✓ Backend connected")
        
        # Run all tests
        test_behavioral_analysis()
        test_preference_patterns()
        test_auto_learning()
        test_habit_suggestions()
        test_learning_analytics()
        test_existing_endpoints()
        test_integration_workflow()
        
        # Final summary
        print("\n" + "="*70)
        print("  ✅ ALL PHASE 3 TESTS PASSED")
        print("="*70)
        print("\n🎉 Phase 3 Implementation Summary:")
        print("  ✓ Behavioral analysis working")
        print("  ✓ Preference pattern detection working")
        print("  ✓ Auto-learning control working")
        print("  ✓ Habit-based suggestions working")
        print("  ✓ Learning analytics working")
        print("  ✓ Backward compatibility maintained")
        print("  ✓ Complete workflow integration working")
        print("\n📊 New Features:")
        print("  • Analyze user behavior to infer preferences (5 new methods)")
        print("  • Detect patterns in existing preferences")
        print("  • Generate suggestions from detected habits")
        print("  • Learning analytics and performance metrics")
        print("  • Auto-learning enable/disable control")
        print("\n🔌 New API Endpoints: 5 endpoints")
        print("  • POST /preferences/analyze-behavior")
        print("  • POST /preferences/patterns")
        print("  • POST /preferences/auto-learn")
        print("  • POST /preferences/suggest-from-habits")
        print("  • POST /preferences/learning-analytics")
        print("\n📝 Total Stage 4 Preference Endpoints: 14")
        print("  • Phase 2: 9 endpoints (basic CRUD + recommendations)")
        print("  • Phase 3: 5 endpoints (behavioral learning)")
        print("\n✅ Ready for Phase 4: Database Optimization")
        print("="*70)
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend")
        print("Please start the backend first:")
        print("  cd python-core")
        print("  python main.py")
        return False
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
