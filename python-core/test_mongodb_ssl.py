#!/usr/bin/env python3
"""
MongoDB SSL/TLS Handshake Diagnostic Test
Tests various SSL configurations and certificate validation
"""

import os
import ssl
import socket
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import certifi

load_dotenv()

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_basic_tcp_connection():
    """Test basic TCP connection without SSL"""
    print_header("TEST 1: Basic TCP Connection (No SSL)")
    
    host = "ac-dj55aef-shard-00-00.hctrhus.mongodb.net"
    port = 27017
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ TCP Connection successful to {host}:{port}")
            return True
        else:
            print(f"❌ TCP Connection failed (error code: {result})")
            return False
    except Exception as e:
        print(f"❌ TCP Connection error: {e}")
        return False

def test_ssl_certificate_info():
    """Get SSL certificate information"""
    print_header("TEST 2: SSL Certificate Information")
    
    host = "ac-dj55aef-shard-00-00.hctrhus.mongodb.net"
    port = 27017
    
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                print(f"✅ SSL Certificate retrieved:")
                print(f"   Subject: {cert.get('subject')}")
                print(f"   Issuer: {cert.get('issuer')}")
                print(f"   Version: {cert.get('version')}")
                print(f"   Serial Number: {cert.get('serialNumber')}")
                print(f"   Not Before: {cert.get('notBefore')}")
                print(f"   Not After: {cert.get('notAfter')}")
                print(f"   Alt Names: {cert.get('subjectAltName')}")
                return True
    except ssl.SSLCertVerificationError as e:
        print(f"⚠️  SSL Certificate Verification Error: {e}")
        return False
    except ssl.SSLError as e:
        print(f"❌ SSL Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ssl_with_certifi():
    """Test SSL with certifi CA bundle"""
    print_header("TEST 3: SSL Connection with Certifi CA Bundle")
    
    host = "ac-dj55aef-shard-00-00.hctrhus.mongodb.net"
    port = 27017
    
    print(f"Using CA Bundle: {certifi.where()}")
    
    try:
        context = ssl.create_default_context(cafile=certifi.where())
        with socket.create_connection((host, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                print(f"✅ SSL Connection successful with certifi CA bundle")
                print(f"   Protocol: {ssock.version()}")
                print(f"   Cipher: {ssock.cipher()}")
                return True
    except ssl.SSLError as e:
        print(f"❌ SSL Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ssl_without_verification():
    """Test SSL without certificate verification (NOT RECOMMENDED)"""
    print_header("TEST 4: SSL Without Verification (Testing Only)")
    
    host = "ac-dj55aef-shard-00-00.hctrhus.mongodb.net"
    port = 27017
    
    print("⚠️  This test disables certificate verification - FOR TESTING ONLY")
    
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection((host, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                print(f"✅ SSL Connection successful without verification")
                print(f"   Protocol: {ssock.version()}")
                print(f"   Cipher: {ssock.cipher()}")
                return True
    except ssl.SSLError as e:
        print(f"❌ SSL Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_mongodb_connection_default():
    """Test MongoDB connection with default settings"""
    print_header("TEST 5: MongoDB Connection (Default SSL)")
    
    uri = os.getenv('MONGODB_URI')
    db_name = os.getenv('MONGODB_DB', 'ELIXIDB')
    
    if not uri:
        print("❌ MONGODB_URI not set in environment")
        return False
    
    print(f"URI: {uri[:50]}...")
    print(f"Database: {db_name}")
    
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        print(f"   Server info: {client.server_info()}")
        client.close()
        return True
    except ServerSelectionTimeoutError as e:
        print(f"❌ Server Selection Timeout: {str(e)[:200]}")
        return False
    except Exception as e:
        print(f"❌ MongoDB Error: {str(e)[:200]}")
        return False

def test_mongodb_connection_no_ssl_verify():
    """Test MongoDB connection without SSL verification"""
    print_header("TEST 6: MongoDB Connection (SSL Verification Disabled)")
    
    uri = os.getenv('MONGODB_URI')
    
    if not uri:
        print("❌ MONGODB_URI not set")
        return False
    
    print("⚠️  Note: This test disables SSL verification")
    
    try:
        client = MongoClient(
            uri,
            serverSelectionTimeoutMS=5000,
            ssl_cert_reqs='CERT_NONE',
            ssl_match_hostname=False
        )
        client.admin.command('ping')
        print("✅ MongoDB connection successful without SSL verification!")
        client.close()
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)[:200]}")
        return False

def test_tls_versions():
    """Test different TLS versions"""
    print_header("TEST 7: TLS Version Support")
    
    host = "ac-dj55aef-shard-00-00.hctrhus.mongodb.net"
    port = 27017
    
    tls_versions = {
        'TLSv1.0': ssl.TLSVersion.TLSv1,
        'TLSv1.1': ssl.TLSVersion.TLSv1_1,
        'TLSv1.2': ssl.TLSVersion.TLSv1_2,
    }
    
    # TLSv1.3 might not be available on all systems
    try:
        tls_versions['TLSv1.3'] = ssl.TLSVersion.TLSv1_3
    except AttributeError:
        pass
    
    for version_name, version in tls_versions.items():
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.minimum_version = version
            context.maximum_version = version
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((host, port), timeout=3) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    print(f"✅ {version_name} - Connection successful")
        except Exception as e:
            print(f"❌ {version_name} - Failed: {str(e)[:100]}")

def test_ssl_error_analysis():
    """Analyze SSL errors in detail"""
    print_header("TEST 8: SSL Error Analysis")
    
    uri = os.getenv('MONGODB_URI')
    
    if not uri:
        print("❌ MONGODB_URI not set")
        return
    
    print("Attempting connection and capturing detailed error...")
    
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
    except Exception as e:
        error_str = str(e)
        print(f"\n📋 Full Error Message:")
        print(f"{error_str}")
        
        print(f"\n🔍 Error Analysis:")
        if "SSL" in error_str:
            print(f"   • SSL/TLS related error detected")
        if "TLSV1_ALERT" in error_str:
            print(f"   • TLS Alert: Protocol error during handshake")
        if "INTERNAL_ERROR" in error_str:
            print(f"   • Internal error: Server-side SSL issue")
        if "certificate" in error_str.lower():
            print(f"   • Certificate validation issue")
        if "handshake" in error_str.lower():
            print(f"   • Handshake failure detected")
        
        print(f"\n💡 Recommendations:")
        print(f"   1. Check MongoDB Atlas cluster status")
        print(f"   2. Verify certificate expiration")
        print(f"   3. Check firewall/proxy settings")
        print(f"   4. Try updating pymongo: pip install --upgrade pymongo")
        print(f"   5. Try updating cryptography: pip install --upgrade cryptography")

def main():
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "MongoDB SSL/TLS Handshake Diagnostic" + " " * 17 + "║")
    print("║" + " " * 20 + "February 13, 2026" + " " * 32 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Run all tests
    results = {}
    
    results["TCP Connection"] = test_basic_tcp_connection()
    results["SSL Certificate Info"] = test_ssl_certificate_info()
    results["SSL with Certifi"] = test_ssl_with_certifi()
    results["SSL Without Verification"] = test_ssl_without_verification()
    results["MongoDB Default"] = test_mongodb_connection_default()
    results["MongoDB No SSL Verify"] = test_mongodb_connection_no_ssl_verify()
    
    test_tls_versions()
    test_ssl_error_analysis()
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed")
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n{'=' * 70}")
    
    if not results["MongoDB Default"]:
        if results["MongoDB No SSL Verify"]:
            print("\n🔍 DIAGNOSIS:")
            print("  • Basic TCP connection: Working")
            print("  • SSL handshake: Failing")
            print("  • Connection without SSL verification: Working")
            print("\n  → The issue is SSL certificate validation")
            print("\n💡 SOLUTION:")
            print("  Option 1 (Recommended): Contact MongoDB Atlas support")
            print("  Option 2 (Temporary): Update MongoDB URI with ssl=true&retryWrites=true")
            print("  Option 3 (Testing): Set ssl_cert_reqs=CERT_NONE (NOT FOR PRODUCTION)")
        else:
            print("\n⚠️  CRITICAL: Cannot connect with or without SSL verification")
            print("   This suggests network connectivity issues")
    else:
        print("\n✅ MongoDB connection is working!")
    
    print(f"\n{'=' * 70}\n")

if __name__ == "__main__":
    main()
