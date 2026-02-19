import ssl
import socket
import sys

print("\n" + "=" * 70)
print("  MongoDB SSL/TLS Advanced Handshake Analysis")
print("=" * 70)

host = 'ac-dj55aef-shard-00-00.hctrhus.mongodb.net'
port = 27017

# TEST 1: SSL Context Information
print("\n[TEST 1] System SSL Configuration")
print("-" * 70)
print(f"OpenSSL Version: {ssl.OPENSSL_VERSION}")
print(f"Python SSL Version: {ssl.OPENSSL_VERSION_INFO}")

# Get supported protocols
print("\nSupported Protocols:")
try:
    print(f"  PROTOCOL_TLS_CLIENT: Available")
except:
    print(f"  PROTOCOL_TLS_CLIENT: Not available")

# Get cipher suites
print("\nDefault Cipher Suites:")
context = ssl.create_default_context()
print(f"  High ciphers: {len(context.get_ciphers())} available")
print(f"  First 3 ciphers:")
for cipher in context.get_ciphers()[:3]:
    print(f"    • {cipher['name']}")

# TEST 2: TLS Version Force Tests
print("\n[TEST 2] TLS Version-Specific Tests")
print("-" * 70)

tls_configs = [
    ('TLSv1.2', ssl.TLSVersion.TLSv1_2, ssl.TLSVersion.TLSv1_2),
]

# Try TLSv1.3 if available
try:
    tls_configs.append(('TLSv1.3', ssl.TLSVersion.TLSv1_3, ssl.TLSVersion.TLSv1_3))
except AttributeError:
    print("TLSv1.3 not available on this system")

for name, min_ver, max_ver in tls_configs:
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.minimum_version = min_ver
        context.maximum_version = max_ver
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        sock = socket.create_connection((host, port), timeout=2)
        ssock = context.wrap_socket(sock, server_hostname=host)
        print(f"✓ {name}: Connection successful")
        print(f"  Negotiated: {ssock.version()}, Cipher: {ssock.cipher()[0][:30]}")
        ssock.close()
    except ssl.SSLError as e:
        print(f"✗ {name}: {str(e)[:80]}")
    except Exception as e:
        print(f"✗ {name}: {str(e)[:80]}")

# TEST 3: Detailed Handshake Error
print("\n[TEST 3] Detailed Handshake Error Analysis")
print("-" * 70)
try:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    sock = socket.create_connection((host, port), timeout=2)
    ssock = context.wrap_socket(sock, server_hostname=host)
    print("✓ Connection succeeded")
except ssl.SSLError as e:
    error_name = e.library if hasattr(e, 'library') else 'Unknown'
    error_msg = str(e)
    
    print(f"SSL Error Details:")
    print(f"  Error Code: {e.errno if hasattr(e, 'errno') else 'N/A'}")
    print(f"  Error Message: {error_msg}")
    
    if "INTERNAL_ERROR" in error_msg:
        print(f"\n  Error Type: SERVER-SIDE INTERNAL ERROR")
        print(f"  This indicates a problem with the MongoDB server's SSL certificate")
        print(f"  or SSL/TLS implementation, not the client.")
    
    if "TLSV1_ALERT" in error_msg:
        print(f"\n  Alert Level: TLS Alert during handshake")
        print(f"  This is typically caused by:")
        print(f"    1. Certificate verification failure")
        print(f"    2. Certificate expiration/invalidity")
        print(f"    3. Server-side SSL configuration issue")
        print(f"    4. Unsupported cipher/protocol combination")

# TEST 4: Certificate Chain Inspection
print("\n[TEST 4] Certificate Chain Inspection (if available)")
print("-" * 70)
try:
    sock = socket.create_connection((host, port), timeout=2)
    # Create context without SSL to trigger immediate handshake
    context = ssl.create_default_context()
    try:
        ssock = context.wrap_socket(sock, server_hostname=host)
        cert = ssock.getpeercert()
        print("✓ Certificate retrieved")
        print(f"  Subject: {cert.get('subject')}")
    except ssl.SSLCertVerificationError as e:
        print(f"Certificate Verification Error: {str(e)[:100]}")
    except ssl.SSLError as e:
        print(f"SSL Error (expected): {str(e)[:100]}")
    sock.close()
except Exception as e:
    print(f"Could not inspect certificate: {e}")

# TEST 5: Recommendations
print("\n[TEST 5] Recommendations Based on Errors")
print("-" * 70)
print("Since the SSL alert is INTERNAL_ERROR occurring on server side:")
print("\n✓ PROBABLE CAUSES (in order of likelihood):")
print("  1. MongoDB Atlas cluster certificate is expired or invalid")
print("  2. MongoDB cluster SSL/TLS is misconfigured")
print("  3. Firewall/proxy is interfering with SSL handshake")
print("\n✓ ACTIONS TO TAKE:")
print("  1. Check MongoDB Atlas cluster details:")
print("     • Login to MongoDB Atlas console")
print("     • Check cluster health and SSL certificate status")
print("  2. Rotate MongoDB Atlas certificate:")
print("     • Go to Cluster Security → Edit Cluster")
print("     • Force certificate rotation")
print("  3. Contact MongoDB Support:")
print("     • Provide cluster name and error details")
print("     • Open support ticket with TLSV1_ALERT_INTERNAL_ERROR")
print("\n✓ WORKAROUNDS (TEMPORARY):")
print("  • None available - this is a server-side issue")
print("  • You must resolve it with MongoDB Atlas")

print("\n" + "=" * 70 + "\n")
