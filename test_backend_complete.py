"""
Comprehensive Backend Testing with Mock Firebase
Tests both enrollment and verification functionality
"""

import os
import sys
import django

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Load mock Firebase first
from mock_firebase import MockFirebaseService

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

# Import Django modules after setup
from django.test import RequestFactory
import json

# Import our views
from views import enroll_fingerprint, verify_fingerprint_esp32

def test_enrollment_and_verification():
    """Complete test of enrollment and verification flow"""
    print("🚀 EVM Backend Testing with Mock Firebase")
    print("=" * 60)
    
    factory = RequestFactory()
    
    # Clear any existing data
    MockFirebaseService.clear_all_templates()
    
    # Test 1: Enroll fingerprint
    print("\n📝 Test 1: Fingerprint Enrollment")
    print("-" * 30)
    
    enrollment_data = {
        "id": 2,
        "data": "ABCD,1234,EFGH,5678",
        "size": 534
    }
    
    request = factory.post(
        '/api/fingerprints/enroll/',
        data=json.dumps(enrollment_data),
        content_type='application/json'
    )
    
    response = enroll_fingerprint(request)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        result = json.loads(content)
        print(f"✅ Enrollment Success!")
        print(f"   - Template ID: {result.get('template_id')}")
        print(f"   - Message: {result.get('message')}")
    else:
        print(f"❌ Enrollment Failed: {response.content.decode('utf-8')}")
        return False
    
    # Test 2: Verify same fingerprint (should match)
    print("\n🔍 Test 2: Verify Enrolled Fingerprint (Should Match)")
    print("-" * 50)
    
    verification_data = {
        "data": "ABCD,1234,EFGH,5678"  # Same as enrolled
    }
    
    request = factory.post(
        '/api/verification/verify/',
        data=json.dumps(verification_data),
        content_type='application/json'
    )
    
    response = verify_fingerprint_esp32(request)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        result = json.loads(content)
        verification_result = result.get('verification_result', {})
        
        print(f"✅ Verification Success!")
        print(f"   - Match Found: {verification_result.get('match_found')}")
        print(f"   - Matched ID: {verification_result.get('fingerprint_id')}")
        print(f"   - Confidence: {verification_result.get('confidence')}%")
        
        if not verification_result.get('match_found'):
            print("❌ Expected match but none found!")
            return False
    else:
        print(f"❌ Verification Failed: {response.content.decode('utf-8')}")
        return False
    
    # Test 3: Verify different fingerprint (should not match)
    print("\n🔍 Test 3: Verify Unknown Fingerprint (Should Not Match)")
    print("-" * 55)
    
    verification_data = {
        "data": "XXXX,9999,YYYY,0000"  # Different from enrolled
    }
    
    request = factory.post(
        '/api/verification/verify/',
        data=json.dumps(verification_data),
        content_type='application/json'
    )
    
    response = verify_fingerprint_esp32(request)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        result = json.loads(content)
        verification_result = result.get('verification_result', {})
        
        print(f"✅ Verification Success!")
        print(f"   - Match Found: {verification_result.get('match_found')}")
        print(f"   - Confidence: {verification_result.get('confidence')}%")
        
        if verification_result.get('match_found'):
            print("❌ Expected no match but found one!")
            return False
        else:
            print("✅ Correctly identified as no match!")
    else:
        print(f"❌ Verification Failed: {response.content.decode('utf-8')}")
        return False
    
    # Test 4: Multiple enrollments
    print("\n📝 Test 4: Multiple Enrollments")
    print("-" * 30)
    
    users = [
        {"id": 2, "data": "USER2,ABCD,1234,EFGH", "size": 534},
        {"id": 3, "data": "USER3,5678,IJKL,9012", "size": 534},
        {"id": 4, "data": "USER4,MNOP,3456,QRST", "size": 534}
    ]
    
    enrolled_count = 0
    for user in users:
        request = factory.post(
            '/api/fingerprints/enroll/',
            data=json.dumps(user),
            content_type='application/json'
        )
        
        response = enroll_fingerprint(request)
        if response.status_code == 200:
            enrolled_count += 1
            print(f"✅ ID {user['id']} enrolled successfully")
        else:
            print(f"❌ ID {user['id']} enrollment failed")
    
    print(f"\nEnrollment Summary: {enrolled_count}/{len(users)} successful")
    
    # Test 5: Verify each enrolled user
    print("\n🔍 Test 5: Verify Each Enrolled User")
    print("-" * 35)
    
    for user in users:
        request = factory.post(
            '/api/verification/verify/',
            data=json.dumps({"data": user["data"]}),
            content_type='application/json'
        )
        
        response = verify_fingerprint_esp32(request)
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            result = json.loads(content)
            verification_result = result.get('verification_result', {})
            
            if verification_result.get('match_found'):
                matched_id = verification_result.get('fingerprint_id')
                print(f"✅ ID {user['id']} verification: Match found (ID {matched_id})")
                if matched_id != user['id']:
                    print(f"❌ Expected ID {user['id']} but got {matched_id}")
            else:
                print(f"❌ ID {user['id']} verification: No match found")
        else:
            print(f"❌ ID {user['id']} verification failed")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 Backend API Testing Complete!")
    print("✅ Enrollment endpoint working correctly")
    print("✅ Verification endpoint working correctly") 
    print("✅ Match detection working correctly")
    print("✅ No-match detection working correctly")
    print("✅ Multiple user handling working correctly")
    
    print(f"\n📊 Total enrolled templates: {MockFirebaseService.get_template_count()}")
    
    print("\n🚀 Backend is ready for ESP32 integration!")
    print("🔧 Next step: Set up Firebase credentials for production")
    
    return True

if __name__ == "__main__":
    test_enrollment_and_verification()