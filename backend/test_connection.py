#!/usr/bin/env python3
import requests
import sys

def test_backend():
    try:
        # Test localhost first
        print("Testing localhost...")
        response = requests.get('http://127.0.0.1:8000/', timeout=5)
        print(f"✅ Localhost: Status {response.status_code}")
        
        # Test network IP
        print("Testing network IP...")
        response = requests.get('http://10.182.86.1:8000/', timeout=5)
        print(f"✅ Network IP: Status {response.status_code}")
        
        if response.status_code == 200:
            print("🎉 Backend is accessible from ESP32!")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_backend()