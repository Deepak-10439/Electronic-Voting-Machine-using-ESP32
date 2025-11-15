import requests
import json

def test_api_endpoints():
    """Test the Django API endpoints"""
    base_url = "http://127.0.0.1:8000"
    
    print("Testing Django API Endpoints...")
    print("=" * 50)
    
    # Test health check endpoint
    try:
        response = requests.get(f"{base_url}/api/health/")
        print(f"Health Check: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
    except Exception as e:
        print(f"Health Check Error: {e}")
    
    # Test system time endpoint
    try:
        response = requests.get(f"{base_url}/api/time/")
        print(f"System Time: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
    except Exception as e:
        print(f"System Time Error: {e}")
    
    # Test API root
    try:
        response = requests.get(f"{base_url}/")
        print(f"API Root: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
    except Exception as e:
        print(f"API Root Error: {e}")
    
    # Test authentication endpoint (POST)
    try:
        data = {
            "device_id": "TEST_ESP32_001",
            "fingerprint_template": "00" * 534,  # Mock fingerprint data
            "aadhar_number": "123456789012"
        }
        response = requests.post(f"{base_url}/api/auth/", json=data)
        print(f"Authentication: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
    except Exception as e:
        print(f"Authentication Error: {e}")

if __name__ == "__main__":
    test_api_endpoints()