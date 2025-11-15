#!/usr/bin/env python3
"""
Manual Django Test - Direct API Testing
Tests the Django views directly without running server
"""

import os
import sys
import django
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
import json

# Add Django project to path
django_path = r"C:\Users\sdeep\OneDrive\Documents\PlatformIO\Projects\evm\django_backend"
sys.path.append(django_path)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evm_backend.settings')
django.setup()

# Import after Django setup
from voting import views
from voting.models import Voter, Election, Candidate

def test_django_views():
    """Test Django views directly without server"""
    print("🧪 Manual Django View Testing")
    print("=" * 50)
    
    # Create request factory
    factory = RequestFactory()
    
    # Test 1: Health Check View
    print("1. Testing Health Check View...")
    try:
        request = factory.get('/api/health/')
        response = views.health_check(request)
        print(f"   Status: {response.status_code}")
        print(f"   Content: {response.content.decode()}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 2: System Time View  
    print("2. Testing System Time View...")
    try:
        request = factory.get('/api/time/')
        response = views.get_system_time(request)
        print(f"   Status: {response.status_code}")
        print(f"   Content: {response.content.decode()}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 3: ESP32 Authentication View (POST)
    print("3. Testing ESP32 Authentication View...")
    try:
        data = {
            "device_id": "TEST_ESP32_001",
            "fingerprint_template": "00" * 534,
            "aadhar_number": "123456789012"
        }
        request = factory.post('/api/auth/', 
                              json.dumps(data),
                              content_type='application/json')
        request.user = AnonymousUser()
        
        view = views.ESP32AuthenticationView.as_view()
        response = view(request)
        print(f"   Status: {response.status_code}")
        print(f"   Content: {response.content.decode()}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 4: Database Models
    print("4. Testing Database Models...")
    try:
        # Count existing objects
        voter_count = Voter.objects.count()
        election_count = Election.objects.count()
        candidate_count = Candidate.objects.count()
        
        print(f"   Voters: {voter_count}")
        print(f"   Elections: {election_count}")
        print(f"   Candidates: {candidate_count}")
        print(f"   Database: Connected ✅")
    except Exception as e:
        print(f"   Database Error: {e}")
    print()
    
    print("✅ Manual Django testing completed!")

if __name__ == "__main__":
    test_django_views()