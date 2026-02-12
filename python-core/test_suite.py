#!/usr/bin/env python3
"""Comprehensive test suite for ELIXI backend"""

import requests
import json
import time
import base64

BASE_URL = "http://127.0.0.1:5000"
TIMEOUT = 5

def test_system_status():
    """Test /system-status endpoint"""
    print("\n[1] Testing /system-status...")
    try:
        response = requests.get(f"{BASE_URL}/system-status", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Status: {response.status_code}")
            print(f"  ✓ Platform: {data.get('platform', 'N/A')}")
            print(f"  ✓ Python: {data.get('python_version', 'N/A')}")
            print(f"  ✓ Uptime: {data.get('uptime_sec', 0)}s")
            print(f"  ✓ DB Connected: {data.get('db_connected', False)}")
            return True
        else:
            print(f"  ✗ Failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_chat():
    """Test /execute with chat command"""
    print("\n[2] Testing /execute (chat)...")
    prompts = ["hello", "what time is it", "status", "help"]
    
    for prompt in prompts:
        try:
            response = requests.post(
                f"{BASE_URL}/execute",
                json={"command": "chat", "args": {"prompt": prompt}},
                timeout=TIMEOUT
            )
            if response.status_code == 200:
                data = response.json()
                reply = data.get("reply", "N/A")
                print(f"  ✓ '{prompt}' → '{reply[:50]}...'")
            else:
                print(f"  ✗ Chat failed: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Error: {e}")

def test_memory():
    """Test /memory/save and /memory/load"""
    print("\n[3] Testing /memory/save and /memory/load...")
    
    # Save memory
    try:
        test_data = {"user_name": "Vikash", "preference": "dark_mode"}
        response = requests.post(
            f"{BASE_URL}/memory/save",
            json=test_data,
            timeout=TIMEOUT
        )
        if response.status_code == 200 and response.json().get("success"):
            print(f"  ✓ Memory saved: {test_data}")
        else:
            print(f"  ✗ Save failed: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Save error: {e}")
    
    # Load memory
    time.sleep(0.5)
    try:
        response = requests.get(f"{BASE_URL}/memory/load", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            print(f"  ✓ Memory loaded: {len(items)} items")
            if items:
                print(f"  ✓ Latest: {items[0].get('data', {})}")
        else:
            print(f"  ✗ Load failed: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Load error: {e}")

def test_wake_word():
    """Test /voice/wake-word-check endpoint"""
    print("\n[4] Testing /voice/wake-word-check...")
    test_phrases = [
        "hey elixi what time is it",
        "Hey Elixi turn on the lights",
        "hey elixi",
        "hello elixi",
        "just a regular message"
    ]
    
    for phrase in test_phrases:
        try:
            response = requests.post(
                f"{BASE_URL}/voice/wake-word-check",
                json={"text": phrase},
                timeout=TIMEOUT
            )
            if response.status_code == 200:
                data = response.json()
                detected = data.get("is_wake_word", False)
                command = data.get("command", "")
                status = "✓ DETECTED" if detected else "✗ not detected"
                cmd_text = f" → '{command}'" if command else ""
                print(f"  {status}: '{phrase}'{cmd_text}")
        except Exception as e:
            print(f"  ✗ Error: {e}")

def test_ollama():
    """Test Ollama availability"""
    print("\n[5] Testing Ollama availability...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"  ✓ Ollama is running")
            print(f"  ✓ Available models: {len(models)}")
            for model in models[:3]:
                print(f"    - {model.get('name', 'unknown')}")
        else:
            print(f"  ✗ Ollama returned {response.status_code}")
    except Exception as e:
        print(f"  ✗ Ollama not available: {e}")

def test_google_cloud():
    """Test Google Cloud configuration"""
    print("\n[6] Testing Google Cloud configuration...")
    import os
    creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    
    if creds:
        print(f"  ✓ Credentials path set: {creds[:30]}...")
        if os.path.exists(creds):
            print(f"  ✓ Credentials file exists")
        else:
            print(f"  ✗ Credentials file not found")
    else:
        print(f"  ✗ GOOGLE_APPLICATION_CREDENTIALS not set")
    
    if project:
        print(f"  ✓ Project ID: {project}")
    else:
        print(f"  ✗ GOOGLE_CLOUD_PROJECT not set")

def main():
    print("=" * 60)
    print("ELIXI BACKEND TEST SUITE")
    print("=" * 60)
    
    # Wait for backend to be ready
    print("\nWaiting for backend to be ready...")
    for i in range(5):
        try:
            requests.get(f"{BASE_URL}/system-status", timeout=2)
            print("✓ Backend is ready!\n")
            break
        except:
            if i < 4:
                time.sleep(1)
    
    # Run tests
    test_system_status()
    test_chat()
    test_memory()
    test_wake_word()
    test_ollama()
    test_google_cloud()
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
