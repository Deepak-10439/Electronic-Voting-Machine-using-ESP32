"""
Test all API endpoints with the actual fingerprint data from Firebase
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 70)
print("TESTING EVM FINGERPRINT BACKEND API")
print("=" * 70)
print()

def test_endpoint(name, url):
    """Test an API endpoint and display results"""
    print(f"🔍 Testing: {name}")
    print(f"   URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success!")
            print(f"   Response:")
            print(json.dumps(data, indent=6))
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   {response.text}")
    
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    print()
    print("-" * 70)
    print()


# Test 1: Root endpoint
test_endpoint(
    "Root - API Information",
    f"{BASE_URL}/"
)

# Test 2: Get fingerprint count
test_endpoint(
    "Get Fingerprint Count",
    f"{BASE_URL}/api/fingerprints/count/"
)

# Test 3: Get all fingerprint templates
test_endpoint(
    "Get All Fingerprint Templates",
    f"{BASE_URL}/api/fingerprints/"
)

# Test 4: Get specific template by ID
test_endpoint(
    "Get Fingerprint Template by ID (ID=2)",
    f"{BASE_URL}/api/fingerprints/id/2/"
)

# Test 5: Get specific template by key
test_endpoint(
    "Get Fingerprint Template by Key (template_3)",
    f"{BASE_URL}/api/fingerprints/key/template_3/"
)

# Test 6: Get statistics
test_endpoint(
    "Get Database Statistics",
    f"{BASE_URL}/api/statistics/"
)

print("=" * 70)
print("✅ ALL TESTS COMPLETED")
print("=" * 70)
