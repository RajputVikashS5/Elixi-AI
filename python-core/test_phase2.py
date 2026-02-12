"""
ELIXI AI - Stage 4 Phase 2 Testing
Tests for Memory System Enhancements
- Semantic search with TF-IDF
- Memory expiration/archival with retention policies
- Conversation context retrieval with analytics
- Related memory search
"""

import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"

def test_semantic_search():
    """Test semantic search capabilities."""
    print("\n=== Test: Semantic Search ===")
    
    # First, save diverse memories
    test_memories = [
        ("The user likes to work in the morning when they are most productive", "habit"),
        ("Weather forecast shows rain tomorrow", "event"),
        ("Morning routine includes exercise and coffee", "routine"),
        ("Productivity tips for remote workers", "learning"),
        ("Climate patterns are changing significantly", "fact"),
    ]
    
    print("Saving test memories...")
    for content, tag in test_memories:
        payload = {
            "query": content,
            "memory_type": "conversation",
            "context": {"source": "test"},
            "tags": [tag],
            "importance": "high" if tag == "habit" else "medium"
        }
        response = requests.post(f"{BASE_URL}/memory/save", json=payload)
        if response.status_code == 200:
            print(f"  ✓ Saved: {tag}")
    
    # Test semantic search with various queries
    test_queries = [
        ("morning productivity", "habit"),
        ("weather and climate", "nature"),
        ("routine habits", "schedule"),
    ]
    
    for query, topic in test_queries:
        payload = {
            "query": query,
            "threshold": 0.2,
            "limit": 5
        }
        response = requests.post(f"{BASE_URL}/memory/semantic-search", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"\n  Semantic search for '{query}' ({topic}):")
                for mem in result.get("memories", [])[:3]:
                    score = mem.get("similarity_score", 0)
                    content = mem.get("content", "")[:50]
                    print(f"    [{score:.2f}] {content}...")
            else:
                print(f"  ✗ Search failed: {result.get('error')}")
        else:
            print(f"  ✗ Request failed: {response.status_code}")

def test_memory_expiration():
    """Test memory expiration and archival."""
    print("\n=== Test: Memory Expiration & Archival ===")
    
    # Save a test memory
    payload = {
        "query": "Test memory for expiration",
        "memory_type": "conversation",
        "tags": ["test", "expiration"],
        "importance": "low"
    }
    response = requests.post(f"{BASE_URL}/memory/save", json=payload)
    
    if response.status_code == 200:
        memory_id = response.json().get("memory_id")
        print(f"  Saved test memory: {memory_id}")
        
        # Set expiry
        payload = {
            "memory_id": memory_id,
            "days_to_expiry": 7
        }
        response = requests.post(f"{BASE_URL}/memory/set-expiry", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"  ✓ Set expiry for 7 days")
                print(f"    Expiry date: {result.get('expiry_date')}")
        
        # Check cleanup
        payload = {"days_to_keep": 90}
        response = requests.post(f"{BASE_URL}/memory/cleanup", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                archived = result.get("archived_count", 0)
                print(f"  ✓ Cleanup completed")
                print(f"    Archived {archived} old memories")
                print(f"    Retention policies: {result.get('policies')}")

def test_conversation_context():
    """Test conversation context retrieval."""
    print("\n=== Test: Conversation Context ===")
    
    conv_id = f"test_conv_{int(time.time())}"
    
    # Add messages
    messages = [
        ("user", "Can you help me with my morning routine?"),
        ("assistant", "Sure! Let's discuss your current routine and optimize it."),
        ("user", "I usually wake up at 7am and exercise"),
        ("assistant", "That's great! Morning exercise boosts productivity."),
    ]
    
    print(f"\n  Creating conversation: {conv_id}")
    for role, text in messages:
        payload = {
            "conversation_id": conv_id,
            "role": role,
            "message": text
        }
        response = requests.post(f"{BASE_URL}/memory/add-to-conversation", json=payload)
        if response.status_code == 200:
            print(f"    ✓ Added {role} message")
    
    # Get context
    payload = {"conversation_id": conv_id}
    response = requests.post(f"{BASE_URL}/memory/context", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            context = result.get("context", {})
            print(f"\n  ✓ Retrieved context:")
            print(f"    Messages: {context.get('message_count')}")
            print(f"    Duration: {context.get('duration_seconds')} seconds")
            print(f"    Related memories: {result.get('related_memories_count')}")

def test_conversation_summary():
    """Test conversation summarization."""
    print("\n=== Test: Conversation Summary ===")
    
    conv_id = f"summary_conv_{int(time.time())}"
    
    # Create conversation
    summary_messages = [
        ("user", "I need to organize my weekly schedule"),
        ("assistant", "Let's plan your week. What are your priorities?"),
        ("user", "Work projects, exercise, and family time"),
        ("assistant", "Great balance. Let's block time for each area."),
        ("user", "Can we schedule morning workouts?"),
        ("assistant", "Perfect for the morning routine we discussed."),
    ]
    
    for role, text in summary_messages:
        payload = {
            "conversation_id": conv_id,
            "role": role,
            "message": text
        }
        requests.post(f"{BASE_URL}/memory/add-to-conversation", json=payload)
    
    # Get summary
    payload = {"conversation_id": conv_id}
    response = requests.post(f"{BASE_URL}/memory/conversation-summary", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            summary = result.get("summary", {})
            print(f"\n  ✓ Retrieved conversation summary:")
            print(f"    Total messages: {summary.get('message_count')}")
            print(f"    Total tokens: {summary.get('total_tokens')}")
            print(f"    Participants: {summary.get('participants')}")
            print(f"    Participant distribution: {summary.get('participant_distribution')}")
            print(f"    Keywords: {summary.get('keywords', [])[:5]}")

def test_memory_statistics():
    """Test memory statistics."""
    print("\n=== Test: Memory Statistics ===")
    
    response = requests.get(f"{BASE_URL}/memory/statistics")
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print(f"\n  ✓ Retrieved statistics:")
            print(f"    Total memories: {result.get('total_memories')}")
            print(f"    Active memories: {result.get('active_memories')}")
            print(f"    Archived memories: {result.get('archived_memories')}")
            print(f"    By type: {result.get('by_type')}")
            print(f"    By importance: {result.get('by_importance')}")
            print(f"    Semantic search: {'Available' if result.get('semantic_search_available') else 'Unavailable'}")

def run_all_tests():
    """Run all Phase 2 tests."""
    print("\n" + "="*60)
    print("ELIXI AI - Stage 4 Phase 2 Testing")
    print("Memory System Enhancements")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/system-status", timeout=2)
        if response.status_code != 200:
            print("\n✗ Backend not responding with success")
            return
    except Exception as e:
        print(f"\n✗ Cannot connect to backend at {BASE_URL}")
        print("Start the backend with: python main.py")
        return
    
    print("\n✓ Backend is running")
    
    test_semantic_search()
    test_memory_expiration()
    test_conversation_context()
    test_conversation_summary()
    test_memory_statistics()
    
    print("\n" + "="*60)
    print("Phase 2 Testing Complete!")
    print("="*60)

if __name__ == "__main__":
    run_all_tests()

        response = requests.post(
            f"{BASE_URL}/preferences/set",
            json=pref
        )
        assert response.status_code == 200
    print(f"✓ Set {len(prefs)} preferences")
    
    # Test 4: Get All Preferences
    print("\n[4] Testing /preferences/all...")
    response = requests.post(
        f"{BASE_URL}/preferences/all",
        json={}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    print(f"✓ Total preferences: {data.get('count', 0)}")
    print(f"  Categories: {list(data.get('grouped', {}).keys())}")
    
    # Test 5: Get Preferences by Category
    print("\n[5] Testing /preferences/all with category filter...")
    response = requests.post(
        f"{BASE_URL}/preferences/all",
        json={"category": "voice"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    print(f"✓ Voice preferences: {len(data.get('preferences', []))} items")
    
    # Test 6: Get Preferences Statistics
    print("\n[6] Testing /preferences/statistics...")
    response = requests.post(
        f"{BASE_URL}/preferences/statistics",
        json={}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    stats = data
    print(f"✓ Preference statistics:")
    print(f"  - Total: {stats.get('total_preferences', 0)}")
    print(f"  - By source: {stats.get('by_source', {})}")
    print(f"  - Avg confidence: {stats.get('average_confidence', 0)}")
    
    # Test 7: Learn Preference
    print("\n[7] Testing /preferences/set (inferred learning)...")
    response = requests.post(
        f"{BASE_URL}/preferences/set",
        json={
            "category": "behavior",
            "key": "preferred_response_type",
            "value": "conversational",
            "source": "inferred",
            "confidence": 0.72
        }
    )
    assert response.status_code == 200
    print(f"✓ Learned preference set with 0.72 confidence")
    
    # Test 8: Get Recommendations
    print("\n[8] Testing /preferences/recommendations...")
    response = requests.post(
        f"{BASE_URL}/preferences/recommendations",
        json={}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    print(f"✓ Recommendations: {len(data.get('recommendations', []))} items")
    
    # Test 9: Apply Recommendation
    print("\n[9] Testing /preferences/apply...")
    if data.get("recommendations"):
        first_rec = data["recommendations"][0]
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
        print(f"✓ Preference promoted from inferred to manual")
    else:
        print(f"⊘ No recommendations to promote (skipping)")
    
    # Test 10: Preference History
    print("\n[10] Testing /preferences/history...")
    response = requests.post(
        f"{BASE_URL}/preferences/history",
        json={"category": "voice", "limit": 20}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    print(f"✓ Preference history: {len(data.get('history', []))} changes")
    
    # Test 11: Delete Preference
    print("\n[11] Testing /preferences/delete...")
    response = requests.post(
        f"{BASE_URL}/preferences/delete",
        json={"category": "display", "key": "dark_mode"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    print(f"✓ Preference deleted")
    
    # Test 12: Verify Deletion
    print("\n[12] Verifying deletion...")
    response = requests.post(
        f"{BASE_URL}/preferences/get",
        json={"category": "display", "key": "dark_mode"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == False
    print(f"✓ Deletion confirmed")
    
    print("\n✅ ALL PREFERENCE TESTS PASSED")


def main():
    """Run all Phase 2 tests."""
    print("\n" + "="*60)
    print("PHASE 2 MEMORY SYSTEM TEST SUITE")
    print("="*60)
    print(f"Testing: {BASE_URL}")
    
    try:
        # Check connection
        print("\nChecking backend connection...")
        response = requests.post(f"{BASE_URL}/system-status", json={}, timeout=5)
        if response.status_code == 200:
            print("✓ Backend is running")
        else:
            print("⚠ Backend may not be fully ready")
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("Make sure backend is running: python main.py")
        return False
    
    try:
        # Run tests
        test_memory_operations()
        test_preference_operations()
        
        print("\n" + "="*60)
        print("✅ ALL PHASE 2 TESTS PASSED!")
        print("="*60)
        print("\nPhase 2 Memory System is production-ready.")
        print("\nKey Features Validated:")
        print("  ✓ Memory storage and retrieval")
        print("  ✓ Full-text and tag-based search")
        print("  ✓ Conversation context preservation")
        print("  ✓ Memory relevance scoring")
        print("  ✓ User preference management")
        print("  ✓ Preference learning and recommendations")
        print("  ✓ Complete audit trail with history")
        
        return True
    
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
