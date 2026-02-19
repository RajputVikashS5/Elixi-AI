import ssl
import socket
import certifi
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

print("\n" + "=" * 70)
print("  MongoDB SSL/TLS Handshake Diagnostic Test")
print("=" * 70)

host = 'ac-dj55aef-shard-00-00.hctrhus.mongodb.net'
port = 27017

# TEST 1: Basic TCP Connection
print("\n[TEST 1] Basic TCP Connection")
print("-" * 70)
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    result = sock.connect_ex((host, port))
    sock.close()
    if result == 0:
        print("✓ TCP Connection successful")
    else:
        print(f"✗ TCP Connection failed (error code: {result})")
except Exception as e:
    print(f"✗ Error: {e}")

# TEST 2: SSL Certificate Info (with verification)
print("\n[TEST 2] SSL Certificate Retrieval (with verification)")
print("-" * 70)
try:
    context = ssl.create_default_context()
    sock = socket.create_connection((host, port), timeout=3)
    ssock = context.wrap_socket(sock, server_hostname=host)
    cert = ssock.getpeercert()
    print("✓ SSL Certificate retrieved successfully!")
    print(f"  Subject: {cert.get('subject')}")
    print(f"  Issuer: {cert.get('issuer')}")
    print(f"  Not Before: {cert.get('notBefore')}")
    print(f"  Not After: {cert.get('notAfter')}")
    ssock.close()
except ssl.SSLCertVerificationError as e:
    print(f"⚠ Certificate Verification Error:")
    print(f"  {str(e)[:150]}...")
except ssl.SSLError as e:
    print(f"✗ SSL Error during handshake:")
    print(f"  {str(e)[:150]}...")
except socket.timeout:
    print("✗ Connection timeout")
except Exception as e:
    print(f"✗ Error: {e}")

# TEST 3: SSL Details
print("\n[TEST 3] SSL/TLS Protocol Details")
print("-" * 70)
try:
    context = ssl.create_default_context()
    sock = socket.create_connection((host, port), timeout=3)
    ssock = context.wrap_socket(sock, server_hostname=host)
    print(f"✓ SSL Connection established")
    print(f"  TLS Version: {ssock.version()}")
    cipher = ssock.cipher()
    print(f"  Cipher Suite: {cipher[0]}")
    print(f"  Protocol Version: {cipher[1]}")
    ssock.close()
except Exception as e:
    print(f"✗ Error: {str(e)[:100]}")

# TEST 4: SSL without verification (for testing)
print("\n[TEST 4] SSL Without Verification (Testing Only)")
print("-" * 70)
try:
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    sock = socket.create_connection((host, port), timeout=3)
    ssock = context.wrap_socket(sock, server_hostname=host)
    print("✓ SSL Connection successful (no verification)")
    print(f"  TLS Version: {ssock.version()}")
    print(f"  Cipher: {ssock.cipher()[0]}")
    ssock.close()
except Exception as e:
    print(f"✗ Error: {e}")

# TEST 5: MongoDB Connection (default)
print("\n[TEST 5] MongoDB Connection (Default Settings)")
print("-" * 70)
uri = os.getenv('MONGODB_URI')
if not uri:
    print("✗ MONGODB_URI not configured in environment")
else:
    print(f"URI: {uri[:60]}...")
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=3000)
        client.admin.command('ping')
        print("✓ MongoDB connection successful!")
        print(f"  Server version: {client.server_info().get('version')}")
        client.close()
    except Exception as e:
        error_msg = str(e)
        print(f"✗ MongoDB connection failed:")
        print(f"  {error_msg[:150]}...")
        
        # Analyze error
        print(f"\n  Error Analysis:")
        if "SSL" in error_msg:
            print(f"    • SSL/TLS related error")
        if "INTERNAL_ERROR" in error_msg:
            print(f"    • Server-side SSL error (certificate issue)")
        if "handshake" in error_msg.lower():
            print(f"    • Handshake failure during SSL negotiation")

# TEST 6: MongoDB without SSL verification
print("\n[TEST 6] MongoDB Connection (SSL Verification Disabled)")
print("-" * 70)
if not uri:
    print("✗ MONGODB_URI not configured")
else:
    print("⚠ Testing with SSL verification disabled (NOT FOR PRODUCTION)")
    try:
        client = MongoClient(
            uri,
            serverSelectionTimeoutMS=3000,
            ssl_cert_reqs='CERT_NONE',
            ssl_match_hostname=False
        )
        client.admin.command('ping')
        print("✓ MongoDB connection successful (without SSL verification)")
        client.close()
    except Exception as e:
        print(f"✗ Still failed: {str(e)[:100]}")

# Summary
print("\n" + "=" * 70)
print("DIAGNOSIS SUMMARY")
print("=" * 70)
print("\nIf Test 5 failed but Test 6 succeeded:")
print("  → Issue is with SSL certificate validation")
print("  → Possible causes:")
print("     1. Certificate expiration")
print("     2. Certificate chain broken")
print("     3. Hostname mismatch")
print("     4. Server-side certificate issue")
print("\nIf both Test 5 and Test 6 failed:")
print("  → Issue is with server connectivity")
print("  → Check network/firewall settings")
print("\nRecommendations:")
print("  1. Update cryptography: pip install --upgrade cryptography")
print("  2. Update pymongo: pip install --upgrade pymongo")
print("  3. Check MongoDB Atlas cluster status")
print("  4. Contact MongoDB support if certificate is expired")
print("\n" + "=" * 70 + "\n")
