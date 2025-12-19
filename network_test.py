"""
Network Connectivity Diagnostic for Supabase
"""
import os
import socket
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("Supabase Network Diagnostics")
print("=" * 60)

# Check .env values
url = os.getenv('SUPABASE_URL', '')
print(f"\n1. SUPABASE_URL from .env: {url}")

# Extract hostname
if url:
    from urllib.parse import urlparse
    parsed = urlparse(url)
    hostname = parsed.netloc
    print(f"   Hostname: {hostname}")
    
    # Test DNS resolution
    print(f"\n2. Testing DNS resolution for {hostname}...")
    try:
        ip = socket.gethostbyname(hostname)
        print(f"   ✓ DNS resolved to: {ip}")
    except socket.gaierror as e:
        print(f"   ❌ DNS resolution failed: {e}")
        print("\n   Possible solutions:")
        print("   1. Check your internet connection")
        print("   2. Try: ping supabase.co")
        print("   3. Check if you're behind a firewall/proxy")
        print("   4. Try using a different DNS (8.8.8.8)")
        print("   5. Restart your network connection")
    except Exception as e:
        print(f"   ❌ Error: {e}")

# Check general internet connectivity
print("\n3. Testing general internet connectivity...")
try:
    socket.create_connection(("8.8.8.8", 53), timeout=3)
    print("   ✓ Internet connection active")
except Exception as e:
    print(f"   ❌ No internet connection: {e}")
    print("\n   Please check your internet connection!")

# Try alternate DNS test
print("\n4. Testing if we can reach supabase.co...")
try:
    ip = socket.gethostbyname("supabase.co")
    print(f"   ✓ Can reach supabase.co ({ip})")
except Exception as e:
    print(f"   ❌ Cannot reach supabase.co: {e}")
    print("\n   This suggests a DNS or firewall issue")

print("\n" + "=" * 60)
