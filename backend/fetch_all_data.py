"""
Fetch complete Firebase database structure to understand the data
"""
import os
import sys
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from firebase_service import FirebaseService

# Initialize Firebase
FirebaseService.initialize()

if not FirebaseService._initialized:
    print("❌ Firebase not initialized")
    sys.exit(1)

print("=" * 70)
print("FIREBASE REALTIME DATABASE - COMPLETE DATA STRUCTURE")
print("=" * 70)
print()

# Get the root reference
db_ref = FirebaseService._db_ref

# Fetch all data from root
print("📥 Fetching all data from Firebase...")
all_data = db_ref.get()

if all_data is None:
    print("⚠️  Database is empty")
else:
    print("✅ Data retrieved successfully!")
    print()
    print("=" * 70)
    print("DATABASE STRUCTURE:")
    print("=" * 70)
    print()
    
    # Pretty print the entire structure
    print(json.dumps(all_data, indent=2, default=str))
    
    print()
    print("=" * 70)
    print("SUMMARY:")
    print("=" * 70)
    
    # Analyze the structure
    if isinstance(all_data, dict):
        print(f"\n📊 Top-level keys in database: {list(all_data.keys())}")
        print()
        
        for key, value in all_data.items():
            print(f"\n🔑 Key: '{key}'")
            print(f"   Type: {type(value).__name__}")
            
            if isinstance(value, dict):
                print(f"   Number of items: {len(value)}")
                print(f"   Sub-keys: {list(value.keys())[:5]}")  # Show first 5 keys
                
                # Show a sample item
                if value:
                    sample_key = list(value.keys())[0]
                    sample_value = value[sample_key]
                    print(f"\n   📄 Sample item (key: '{sample_key}'):")
                    print(f"   {json.dumps(sample_value, indent=6, default=str)}")
            
            elif isinstance(value, list):
                print(f"   List length: {len(value)}")
                if value:
                    print(f"   First item: {value[0]}")
            else:
                print(f"   Value: {value}")
    
    print()
    print("=" * 70)
