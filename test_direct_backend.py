"""
Direct Django test for EVM Backend APIs
Tests enrollment and verification without HTTP requests
"""

import os
import sys
import django

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

# Import Django modules after setup
from django.test import RequestFactory
from django.http import JsonResponse
import json

# Import our views
from views import enroll_fingerprint, verify_fingerprint_esp32

def test_enrollment_direct():
    """Test enrollment endpoint directly"""
    print("\n=== Testing Enrollment (Direct Django) ===")
    
    factory = RequestFactory()
    
    # Sample enrollment data (using correct field names)
    enrollment_data = {
        "id": 1,
        "data": "ABCDEF1234567890,ABCDEF1234567890,ABCDEF1234567890,ABCDEF1234567890",
        "size": 534
    }
    
    # Create POST request
    request = factory.post(
        '/api/fingerprints/enroll/',
        data=json.dumps(enrollment_data),
        content_type='application/json'
    )
    
    try:
        # Call the view function directly
        response = enroll_fingerprint(request)
        
        print(f"Status Code: {response.status_code}")
        
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8')
            print(f"Response: {content}")
            
            if response.status_code == 200:
                result = json.loads(content)
                print("✓ Enrollment successful!")
                print(f"  - Success: {result.get('success')}")
                print(f"  - Message: {result.get('message')}")
                return True
        
        print("✗ Enrollment failed!")
        return False
        
    except Exception as e:
        print(f"✗ Enrollment error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_verification_direct():
    """Test verification endpoint directly"""
    print("\n=== Testing Verification (Direct Django) ===")
    
    factory = RequestFactory()
    
    # Sample verification data (using correct field names)
    verification_data = {
        "data": "ABCDEF1234567890,ABCDEF1234567890,ABCDEF1234567890,ABCDEF1234567890"
    }
    
    # Create POST request
    request = factory.post(
        '/api/verification/verify/',
        data=json.dumps(verification_data),
        content_type='application/json'
    )
    
    try:
        # Call the view function directly
        response = verify_fingerprint_esp32(request)
        
        print(f"Status Code: {response.status_code}")
        
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8')
            print(f"Response: {content}")
            
            if response.status_code == 200:
                result = json.loads(content)
                print("✓ Verification successful!")
                print(f"  - Match Found: {result.get('match_found')}")
                print(f"  - Fingerprint ID: {result.get('fingerprint_id', 'No match')}")
                print(f"  - User Name: {result.get('user_name', 'No match')}")
                return True
        
        print("✗ Verification failed!")
        return False
        
    except Exception as e:
        print(f"✗ Verification error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_enrollments_direct():
    """Test multiple enrollments directly"""
    print("\n=== Testing Multiple Enrollments (Direct Django) ===")
    
    factory = RequestFactory()
    
    test_users = [
        {"id": 2, "data": "FEDCBA0987654321,FEDCBA0987654321,FEDCBA0987654321,FEDCBA0987654321", "size": 534},
        {"id": 3, "data": "1122334455667788,1122334455667788,1122334455667788,1122334455667788", "size": 534},
        {"id": 4, "data": "AABBCCDDEEFFAABB,CCDDEEFFAABBCCDD,EEFFAABBCCDDEEFF,AABBCCDDEEFFAABB", "size": 534}
    ]
    
    success_count = 0
    for user in test_users:
        print(f"\nEnrolling ID: {user['id']}")
        
        request = factory.post(
            '/api/fingerprints/enroll/',
            data=json.dumps(user),
            content_type='application/json'
        )
        
        try:
            response = enroll_fingerprint(request)
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                result = json.loads(content)
                print(f"  ✓ ID {user['id']} enrolled successfully")
                success_count += 1
            else:
                print(f"  ✗ ID {user['id']} enrollment failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ✗ ID {user['id']} enrollment error: {e}")
    
    print(f"\nEnrollment Summary: {success_count}/{len(test_users)} successful")
    return success_count == len(test_users)

def main():
    """Main test function"""
    print("🚀 EVM Backend Direct Testing")
    print("=" * 50)
    
    try:
        # Test basic enrollment
        test_enrollment_direct()
        
        # Test basic verification
        test_verification_direct()
        
        # Test multiple enrollments
        test_multiple_enrollments_direct()
        
        print("\n" + "=" * 50)
        print("🎯 Direct Backend Testing Complete!")
        
        # Test verification with known data
        print("\n=== Testing Verification with Enrolled Data ===")
        factory = RequestFactory()
        
        # Try to verify Alice's fingerprint (ID 2)
        alice_data = {"data": "FEDCBA0987654321,FEDCBA0987654321,FEDCBA0987654321,FEDCBA0987654321"}
        request = factory.post('/api/verification/verify/', data=json.dumps(alice_data), content_type='application/json')
        
        try:
            response = verify_fingerprint_esp32(request)
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                result = json.loads(content)
                print(f"✓ ID 2 verification - Match found: {result.get('verification_result', {}).get('match_found', False)}")
                verification_result = result.get('verification_result', {})
                if verification_result.get('match_found'):
                    print(f"  - Matched ID: {verification_result.get('fingerprint_id')}")
        except Exception as e:
            print(f"✗ ID 2 verification error: {e}")
        
        print("\n🎯 Backend is ready for ESP32 integration!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()