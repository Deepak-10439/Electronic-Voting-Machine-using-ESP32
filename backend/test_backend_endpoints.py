#!/usr/bin/env python3
"""
Test script for EVM Backend APIs
Tests enrollment and verification endpoints
"""

import requests
import json
import time

# Backend configuration
BACKEND_URL = "http://127.0.0.1:8000"
ENROLLMENT_ENDPOINT = f"{BACKEND_URL}/api/fingerprints/enroll/"
VERIFICATION_ENDPOINT = f"{BACKEND_URL}/api/verification/verify/"

def test_server_status():
    """Test if the Django server is responding"""
    try:
        response = requests.get(BACKEND_URL, timeout=5)
        print(f"✓ Server Status: {response.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ Server unreachable: {e}")
        return False

def test_enrollment():
    """Test fingerprint enrollment endpoint"""
    print("\n=== Testing Enrollment Endpoint ===")
    
    # Sample fingerprint template data (simulating ESP32 data)
    enrollment_data = {
        "fingerprint_id": 1,
        "user_name": "Test User 1",
        "template_data": "ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890"
    }
    
    try:
        response = requests.post(
            ENROLLMENT_ENDPOINT, 
            json=enrollment_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Enrollment successful!")
            print(f"  - Success: {result.get('success')}")
            print(f"  - Message: {result.get('message')}")
            print(f"  - Firebase Key: {result.get('firebase_key', 'N/A')}")
            return True
        else:
            print("✗ Enrollment failed!")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Enrollment request failed: {e}")
        return False

def test_verification():
    """Test fingerprint verification endpoint"""
    print("\n=== Testing Verification Endpoint ===")
    
    # Sample verification data (simulating ESP32 verification request)
    verification_data = {
        "template_data": "ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890"
    }
    
    try:
        response = requests.post(
            VERIFICATION_ENDPOINT,
            json=verification_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Verification successful!")
            print(f"  - Match Found: {result.get('match_found')}")
            print(f"  - Fingerprint ID: {result.get('fingerprint_id', 'No match')}")
            print(f"  - User Name: {result.get('user_name', 'No match')}")
            print(f"  - Message: {result.get('message')}")
            return True
        else:
            print("✗ Verification failed!")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Verification request failed: {e}")
        return False

def test_multiple_enrollments():
    """Test multiple fingerprint enrollments"""
    print("\n=== Testing Multiple Enrollments ===")
    
    test_users = [
        {"fingerprint_id": 2, "user_name": "Alice Smith", "template_data": "FEDCBA0987654321FEDCBA0987654321FEDCBA0987654321FEDCBA0987654321"},
        {"fingerprint_id": 3, "user_name": "Bob Johnson", "template_data": "1122334455667788112233445566778811223344556677881122334455667788"},
        {"fingerprint_id": 4, "user_name": "Carol Davis", "template_data": "AABBCCDDEEFFAABBCCDDEEFFAABBCCDDEEFFAABBCCDDEEFFAABBCCDDEEFF"}
    ]
    
    success_count = 0
    for user in test_users:
        print(f"\nEnrolling: {user['user_name']}")
        try:
            response = requests.post(
                ENROLLMENT_ENDPOINT,
                json=user,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✓ {user['user_name']} enrolled successfully")
                success_count += 1
            else:
                print(f"  ✗ {user['user_name']} enrollment failed: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"  ✗ {user['user_name']} enrollment error: {e}")
    
    print(f"\nEnrollment Summary: {success_count}/{len(test_users)} successful")
    return success_count == len(test_users)

def test_verification_scenarios():
    """Test different verification scenarios"""
    print("\n=== Testing Verification Scenarios ===")
    
    # Test with known template (should match)
    print("\n1. Testing with known template (Alice):")
    known_template = {"template_data": "FEDCBA0987654321FEDCBA0987654321FEDCBA0987654321FEDCBA0987654321"}
    
    try:
        response = requests.post(VERIFICATION_ENDPOINT, json=known_template, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✓ Match result: {result.get('match_found')}")
            if result.get('match_found'):
                print(f"   ✓ Matched User: {result.get('user_name')}")
        else:
            print(f"   ✗ Verification failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test with unknown template (should not match)
    print("\n2. Testing with unknown template:")
    unknown_template = {"template_data": "UNKNOWN123456789UNKNOWN123456789UNKNOWN123456789UNKNOWN123456789"}
    
    try:
        response = requests.post(VERIFICATION_ENDPOINT, json=unknown_template, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✓ Match result: {result.get('match_found')}")
            if not result.get('match_found'):
                print("   ✓ Correctly identified as no match")
        else:
            print(f"   ✗ Verification failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

def main():
    """Main test function"""
    print("🚀 EVM Backend API Testing")
    print("=" * 50)
    
    # Check server status
    if not test_server_status():
        print("❌ Server is not running. Please start the Django backend first.")
        return
    
    # Test basic enrollment
    test_enrollment()
    
    # Wait a moment for Firebase to process
    time.sleep(2)
    
    # Test basic verification
    test_verification()
    
    # Test multiple enrollments
    test_multiple_enrollments()
    
    # Wait for processing
    time.sleep(2)
    
    # Test verification scenarios
    test_verification_scenarios()
    
    print("\n" + "=" * 50)
    print("🎯 Backend API Testing Complete!")
    print("\nBackend is ready for ESP32 integration!")

if __name__ == "__main__":
    main()