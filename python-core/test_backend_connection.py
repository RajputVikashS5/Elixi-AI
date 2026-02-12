#!/usr/bin/env python3
import urllib.request
import json
import time

print("Testing backend connection...")
time.sleep(1)

try:
    response = urllib.request.urlopen('http://127.0.0.1:5000/system-status', timeout=5)
    print(f"✓ Status: {response.status}")
    data = json.loads(response.read().decode())
    print("✓ Response from /system-status:")
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"✗ Error: {e}")

print("\nTesting /execute endpoint...")
try:
    req = urllib.request.Request(
        'http://127.0.0.1:5000/execute',
        data=json.dumps({'command': 'chat', 'args': {'prompt': 'hello'}}).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    response = urllib.request.urlopen(req, timeout=5)
    print(f"✓ Status: {response.status}")
    data = json.loads(response.read().decode())
    print("✓ Response from /execute:")
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"✗ Error: {e}")
