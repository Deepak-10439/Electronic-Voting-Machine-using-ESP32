import json
import os

# Check if file exists
if not os.path.exists('firebase-credentials.json'):
    print("❌ firebase-credentials.json not found")
    exit(1)

# Check file size
size = os.path.getsize('firebase-credentials.json')
print(f"📄 File size: {size} bytes")

if size == 0:
    print("❌ firebase-credentials.json is empty")
    exit(1)

# Try to parse JSON
try:
    with open('firebase-credentials.json', 'r') as f:
        data = json.load(f)
    
    print("✅ Valid JSON file")
    print(f"✅ Project ID: {data.get('project_id', 'Not found')}")
    print(f"✅ Client Email: {data.get('client_email', 'Not found')}")
    
    # Check required fields
    required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
    missing = [field for field in required_fields if field not in data]
    
    if missing:
        print(f"⚠️  Missing fields: {', '.join(missing)}")
    else:
        print("✅ All required fields present")
        
except json.JSONDecodeError as e:
    print(f"❌ Invalid JSON: {e}")
    print("\nFile contents (first 200 chars):")
    with open('firebase-credentials.json', 'r') as f:
        print(f.read(200))
except Exception as e:
    print(f"❌ Error: {e}")
