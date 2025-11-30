"""
ESP32 Verification and Testing Guide
Real ESP32 with Blockchain Backend Integration
"""

# ESP32 Serial Commands for Testing
print("🔧 ESP32 TESTING COMMANDS")
print("=" * 50)
print("After uploading code to ESP32, open Serial Monitor and:")
print("")
print("1. 📡 Check Connection:")
print("   Command: S")
print("   Expected: WiFi Connected, Firebase Ready, Next Enroll ID")
print("")
print("2. 👆 Enroll Fingerprint:")
print("   Command: E")
print("   Process: Place finger → Remove → Place again → Upload to blockchain")
print("   Expected: 'Enrolled! ID: X' + blockchain transaction")
print("")
print("3. 🔍 Verify Fingerprint:")
print("   Command: V") 
print("   Process: Place enrolled finger → Cloud verification")
print("   Expected: 'VERIFIED! ID: X' + blockchain audit")
print("")
print("4. 🔄 Test Multiple Operations:")
print("   - Enroll several fingerprints (E)")
print("   - Verify each one (V)")
print("   - Check status between operations (S)")
print("")
print("🌐 BACKEND VERIFICATION")
print("=" * 50)

import requests
import json

def check_backend_status():
    """Verify backend is ready for ESP32"""
    backend_url = "https://swift-habitat-475216-n3.uc.r.appspot.com"
    
    print(f"Backend URL: {backend_url}")
    
    try:
        # Test root endpoint
        response = requests.get(f"{backend_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Online: {data.get('message')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Blockchain: {data.get('blockchain')}")
        else:
            print(f"❌ Backend Error: HTTP {response.status_code}")
            return False
        
        # Test fingerprint count endpoint
        response = requests.get(f"{backend_url}/api/fingerprints/count/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Current Fingerprints: {data.get('fingerprint_count', 0)}")
        
        # Test blockchain info
        response = requests.get(f"{backend_url}/api/blockchain/info/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                info = data['blockchain_info']
                print(f"✅ Blockchain: {info.get('total_blocks')} blocks, Valid: {info.get('is_valid')}")
        
        print("")
        print("🎯 READY FOR ESP32 TESTING!")
        return True
        
    except Exception as e:
        print(f"❌ Backend Check Failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ESP32 BLOCKCHAIN INTEGRATION - READY TO TEST")
    print("")
    
    # Check backend
    backend_ready = check_backend_status()
    
    if backend_ready:
        print("")
        print("📋 TESTING CHECKLIST:")
        print("=" * 50)
        print("□ ESP32 connected via USB")
        print("□ Serial Monitor open (115200 baud)")
        print("□ Fingerprint sensor wired correctly")
        print("□ LCD display connected")
        print("□ WiFi credentials configured")
        print("□ Code uploaded successfully")
        print("")
        print("🔄 TESTING SEQUENCE:")
        print("1. Power on ESP32 → Watch Serial Monitor")
        print("2. Verify 'WiFi Connected!' message")
        print("3. Verify 'Firebase Ready!' message")
        print("4. Send 'S' → Check system status")
        print("5. Send 'E' → Enroll a fingerprint")
        print("6. Send 'V' → Verify the fingerprint")
        print("7. Check blockchain transactions in monitor")
        print("")
        print("🎉 Each enrollment and verification will:")
        print("   • Store template in Firebase")
        print("   • Create blockchain transaction")
        print("   • Update immutable audit trail")
        print("   • Display on LCD and Serial Monitor")
        
    else:
        print("")
        print("❌ Backend not ready. Please check:")
        print("1. Internet connection")
        print("2. Backend URL accessibility")
        print("3. GCP App Engine status")

print("")
print("📱 EXPECTED ESP32 BEHAVIOR:")
print("=" * 50)
print("Serial Monitor Output:")
print("=== Fingerprint System Ready ===")
print("Commands:")
print("  E - Enroll new fingerprint")
print("  V - Verify fingerprint")
print("  S - Show status")
print("================================")
print("")
print("LCD Display:")
print("Welcome to")
print("Fingerprint EVM")
print("↓")
print("Mode: IDLE")
print("Ready...")