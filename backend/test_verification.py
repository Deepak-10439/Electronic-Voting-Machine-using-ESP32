"""
Test fingerprint verification API
"""
import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from firebase_service import FirebaseService

print("=" * 70)
print("FINGERPRINT VERIFICATION TEST")
print("=" * 70)
print()

# Initialize Firebase
FirebaseService.initialize()

if not FirebaseService._initialized:
    print("❌ Firebase not initialized")
    sys.exit(1)

# Test 1: Get verification template
print("📥 Test 1: Getting verification template...")
verify_template = FirebaseService.get_verification_template()
if "error" in verify_template:
    print(f"   ❌ Error: {verify_template['error']}")
else:
    print(f"   ✅ Verification template found")
    print(f"   Data length: {verify_template['data_length']} bytes")
print()

# Test 2: Get all enrolled templates
print("📥 Test 2: Getting enrolled templates...")
templates = FirebaseService.get_all_fingerprint_templates()
if isinstance(templates, dict) and "error" in templates:
    print(f"   ❌ Error: {templates['error']}")
else:
    print(f"   ✅ Found {len(templates)} enrolled templates")
    for t in templates:
        print(f"      - ID {t['id']}: {t['template_key']}")
print()

# Test 3: Verify fingerprint (default threshold 80%)
print("🔍 Test 3: Verifying fingerprint (threshold: 80%)...")
result = FirebaseService.verify_fingerprint(threshold=80)

if "error" in result:
    print(f"   ❌ Error: {result['error']}")
else:
    print(f"   ✅ Verification complete!")
    print(f"   Match found: {result['match_found']}")
    print(f"   Message: {result['message']}")
    
    if result['match_found']:
        print(f"\n   🎯 Best Match:")
        print(f"      Template ID: {result['best_match']['template_id']}")
        print(f"      Template Key: {result['best_match']['template_key']}")
        print(f"      Similarity: {result['best_match']['similarity_percentage']}%")
    
    print(f"\n   📊 All Comparisons:")
    for comp in result['all_comparisons']:
        match_icon = "✅" if comp['is_match'] else "❌"
        print(f"      {match_icon} ID {comp['template_id']} ({comp['template_key']}): {comp['similarity_percentage']}%")

print()
print("=" * 70)
print("✅ TEST COMPLETED")
print("=" * 70)
