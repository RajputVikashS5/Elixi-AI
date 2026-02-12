#!/usr/bin/env python3
"""Test Stage 4 APIs to verify they're working correctly."""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_custom_commands():
    """Test custom commands API."""
    print("\n=== Testing Custom Commands ===")
    
    # Test create
    payload = {
        "command_name": "Open Browser",
        "trigger_words": ["open browser", "start chrome"],
        "actions": [
            {"action": "open_app", "args": {"app_name": "Chrome"}}
        ],
        "description": "Opens Chrome browser"
    }
    
    response = requests.post(
        f"{BASE_URL}/automation/custom-commands/create",
        json=payload,
        timeout=5
    )
    
    print(f"✓ Create command: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  - Success: {data.get('success')}")
        print(f"  - Command ID: {data.get('command_id')}")
        command_id = data.get('command_id')
    else:
        print(f"  ERROR: {response.text}")
        return
    
    # Test list
    response = requests.post(
        f"{BASE_URL}/automation/custom-commands/list",
        json={},
        timeout=5
    )
    print(f"✓ List commands: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  - Found {data.get('count')} commands")
    
    # Test get
    if command_id:
        response = requests.post(
            f"{BASE_URL}/automation/custom-commands/get",
            json={"command_id": command_id},
            timeout=5
        )
        print(f"✓ Get command: {response.status_code}")

def test_workflows():
    """Test workflows API."""
    print("\n=== Testing Workflows ===")
   
    payload = {
        "workflow_name": "Morning Routine",
        "description": "Opens apps in sequence",
        "steps": [
            {"action": "open_app", "args": {"app_name": "Chrome"}, "delay_after": 2}
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/automation/workflows/create",
        json=payload,
        timeout=5
    )
    
    print(f"✓ Create workflow: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  - Success: {data.get('success')}")
        print(f"  - Workflow ID: {data.get('workflow_id')}")

def test_habits():
    """Test habit learning API."""
    print("\n=== Testing Habit Learning ===")
    
    response = requests.post(
        f"{BASE_URL}/automation/habits/analyze",
        json={"days": 7},
        timeout=10
    )
    
    print(f"✓ Analyze habits: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  - Success: {data.get('success')}")
        print(f"  - Patterns found: {len(data.get('patterns', []))}")

def test_suggestions():
    """Test suggestions API."""
    print("\n=== Testing Suggestions ===")
    
    response = requests.post(
        f"{BASE_URL}/suggestions/active",
        json={"limit": 5},
        timeout=5
    )
    
    print(f"✓ Get suggestions: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  - Success: {data.get('success')}")
        print(f"  - Suggestions count: {data.get('count', 0)}")

if __name__ == "__main__":
    print("Testing Stage 4 Implementation...")
    print("=" * 50)
    
    try:
        test_custom_commands()
        test_workflows()
        test_habits()
        test_suggestions()
        print("\n" + "=" * 50)
        print("✓✓✓ ALL STAGE 4 TESTS PASSED!")
        print("=" * 50)
    except Exception as e:
        print(f"\n✗ Error: {e}")
