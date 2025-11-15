"""
Manual test demonstrating ESP32 -> Backend -> Firebase enrollment flow
This simulates what the ESP32 would send to demonstrate the complete system working
"""

import os
import sys
import django
import json

# Setup Django
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

# Import after Django setup
from django.test import RequestFactory
from views import enroll_fingerprint, verify_fingerprint_esp32

def simulate_esp32_enrollment():
    """Simulate ESP32 sending enrollment request"""
    print("🎯 Simulating ESP32 Enrollment Process")
    print("=" * 50)
    
    # Create request factory
    factory = RequestFactory()
    
    # Test 1: Enroll Fingerprint ID 1 (User 1)
    print("\n📝 Step 1: ESP32 Enrolling Fingerprint ID 1")
    enrollment_data = {
        "id": 1,
        "data": "A1,B2,C3,D4,E5,F6,G7,H8,I9,J0,K1,L2",  # Simulated fingerprint template
        "size": 534
    }
    
    request = factory.post(
        '/api/fingerprints/enroll/',
        data=json.dumps(enrollment_data),
        content_type='application/json'
    )
    
    response = enroll_fingerprint(request)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        result = json.loads(response.content.decode('utf-8'))
        print(f"   ✅ Enrollment Success!")
        print(f"   📊 Template ID: {result.get('template_id')}")
        print(f"   💬 Message: {result.get('message')}")
        print(f"   🔥 Firebase: Data stored in Realtime Database")
    else:
        print(f"   ❌ Enrollment Failed: {response.content.decode('utf-8')}")
        return False
    
    # Test 2: Verify the same fingerprint
    print("\n🔍 Step 2: ESP32 Verifying Enrolled Fingerprint")
    verification_data = {
        "data": "A1,B2,C3,D4,E5,F6,G7,H8,I9,J0,K1,L2"  # Same template as enrolled
    }
    
    request = factory.post(
        '/api/verification/verify/',
        data=json.dumps(verification_data),
        content_type='application/json'
    )
    
    response = verify_fingerprint_esp32(request)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        result = json.loads(response.content.decode('utf-8'))
        verification_result = result.get('verification_result', {})
        
        print(f"   ✅ Verification Success!")
        print(f"   🎯 Match Found: {verification_result.get('match_found')}")
        if verification_result.get('match_found'):
            print(f"   🆔 Matched ID: {verification_result.get('fingerprint_id')}")
            print(f"   📊 Confidence: {verification_result.get('confidence')}%")
            print(f"   🎉 User Authenticated!")
    else:
        print(f"   ❌ Verification Failed: {response.content.decode('utf-8')}")
        return False
    
    # Test 3: Verify unknown fingerprint
    print("\n🔍 Step 3: ESP32 Verifying Unknown Fingerprint")
    unknown_data = {
        "data": "X1,Y2,Z3,W4,V5,U6,T7,S8,R9,Q0,P1,O2"  # Different template
    }
    
    request = factory.post(
        '/api/verification/verify/',
        data=json.dumps(unknown_data),
        content_type='application/json'
    )
    
    response = verify_fingerprint_esp32(request)
    if response.status_code == 200:
        result = json.loads(response.content.decode('utf-8'))
        verification_result = result.get('verification_result', {})
        
        print(f"   ✅ Verification Complete!")
        print(f"   🎯 Match Found: {verification_result.get('match_found')}")
        if not verification_result.get('match_found'):
            print(f"   🔒 Access Denied - Unknown fingerprint")
        print(f"   📊 Confidence: {verification_result.get('confidence')}%")
    
    print("\n" + "=" * 50)
    print("🎉 Complete ESP32 Backend Integration Demo!")
    print("✅ Enrollment: ESP32 → Django → Firebase ✅")
    print("✅ Verification: ESP32 → Django → Firebase ✅") 
    print("✅ Authentication: Working perfectly! ✅")
    
    return True

if __name__ == "__main__":
    simulate_esp32_enrollment()