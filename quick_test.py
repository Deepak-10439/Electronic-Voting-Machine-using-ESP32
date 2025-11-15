#!/usr/bin/env python3
"""
Quick API Test for ESP32 EVM Django Backend
"""

import requests
import json

def main():
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Quick API Test for ESP32 EVM Backend")
    print("=" * 50)
    
    # Test 1: API Root
    print("1. Testing API Root...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 2: Health Check
    print("2. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/api/health/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 3: System Time
    print("3. Testing System Time...")
    try:
        response = requests.get(f"{base_url}/api/time/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 4: Authentication (POST)
    print("4. Testing ESP32 Authentication...")
    try:
        auth_data = {
            "device_id": "TEST_ESP32_001",
            "fingerprint_template": "00" * 534,
            "aadhar_number": "123456789012"
        }
        response = requests.post(f"{base_url}/api/auth/", json=auth_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 5: Admin Interface
    print("5. Testing Admin Interface...")
    try:
        response = requests.get(f"{base_url}/admin/")
        print(f"   Status: {response.status_code}")
        print(f"   Admin accessible: {'Yes' if response.status_code in [200, 302] else 'No'}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    print("✅ Quick test completed!")

if __name__ == "__main__":
    main()