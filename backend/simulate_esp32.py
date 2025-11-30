# Simulate ESP32 Enrollment and Verification
import requests
import json
import time

# Backend URL
BASE_URL = "https://swift-habitat-475216-n3.uc.r.appspot.com"

def simulate_esp32_enrollment():
    """Simulate ESP32 enrolling a new fingerprint"""
    print("🔄 SIMULATING ESP32 ENROLLMENT...")
    print("=" * 50)
    
    # Simulate fingerprint template data (this would come from the actual sensor)
    enrollment_data = {
        "id": 101,  # New fingerprint ID
        "data": "FF,01,A2,B3,C4,D5,E6,F7,08,19,2A,3B,4C,5D,6E,7F,80,91,A2,B3,C4,D5,E6,F7,08,19",
        "size": 26
    }
    
    print(f"📤 Sending enrollment request for ID: {enrollment_data['id']}")
    print(f"🔢 Template size: {enrollment_data['size']} bytes")
    print(f"📡 Backend URL: {BASE_URL}/api/fingerprints/enroll/")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/fingerprints/enroll/", 
            json=enrollment_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📨 Response Status: HTTP {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ ENROLLMENT SUCCESSFUL!")
            print(f"   Message: {result.get('message', 'No message')}")
            print(f"   Template ID: {result.get('template_id', 'N/A')}")
            
            # Check if blockchain transaction was created
            if 'blockchain_tx' in result:
                print(f"🔗 Blockchain TX: {result['blockchain_tx']}")
            else:
                print("🔍 Checking blockchain for new transaction...")
                
            return True
        else:
            print(f"❌ ENROLLMENT FAILED!")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ENROLLMENT ERROR: {e}")
        return False

def simulate_esp32_verification():
    """Simulate ESP32 verifying a fingerprint"""
    print("\n🔄 SIMULATING ESP32 VERIFICATION...")
    print("=" * 50)
    
    # Simulate verification with slight variation in template
    verification_data = {
        "data": "FF,01,A2,B3,C4,D5,E6,F7,08,19,2A,3B,4C,5D,6E,7F,81,91,A2,B3,C4,D5,E6,F7,09,1A",
        "threshold": 65  # Use the improved threshold
    }
    
    print(f"📤 Sending verification request")
    print(f"🎯 Threshold: {verification_data['threshold']}%")
    print(f"📡 Backend URL: {BASE_URL}/api/verification/verify/")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/verification/verify/", 
            json=verification_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📨 Response Status: HTTP {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                verification_result = result['verification_result']
                
                if verification_result.get('match_found'):
                    print("✅ VERIFICATION SUCCESSFUL!")
                    print(f"   Matched ID: {verification_result.get('matched_id', 'N/A')}")
                    print(f"   Similarity: {verification_result.get('similarity', 0):.1f}%")
                    print(f"   Message: {verification_result.get('message', 'No message')}")
                    
                    # Check blockchain transaction
                    if 'blockchain_tx' in verification_result:
                        print(f"🔗 Blockchain TX: {verification_result['blockchain_tx']}")
                    
                    return True
                else:
                    print("❌ VERIFICATION FAILED - No Match")
                    print(f"   Message: {verification_result.get('message', 'No message')}")
                    
                    # Still check for blockchain transaction (failed attempts are also recorded)
                    if 'blockchain_tx' in verification_result:
                        print(f"🔗 Blockchain TX: {verification_result['blockchain_tx']}")
                    
                    return False
            else:
                print(f"❌ VERIFICATION ERROR: {result.get('error', 'Unknown error')}")
                return False
                
        else:
            print(f"❌ VERIFICATION FAILED!")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ VERIFICATION ERROR: {e}")
        return False

def check_blockchain_updates():
    """Check for recent blockchain updates"""
    print("\n🔍 CHECKING BLOCKCHAIN UPDATES...")
    print("=" * 50)
    
    try:
        # Get recent transactions
        response = requests.get(f"{BASE_URL}/api/blockchain/audit/?limit=3", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                transactions = result.get('transactions', [])
                total_count = result.get('total_count', 0)
                
                print(f"📊 Total Blockchain Transactions: {total_count}")
                print("📋 Recent Transactions:")
                
                if transactions:
                    for i, tx in enumerate(transactions[-3:], 1):
                        tx_type = tx.get('type', 'UNKNOWN')
                        tx_id = tx.get('tx_id', 'N/A')
                        timestamp = tx.get('datetime', 'N/A')
                        block_index = tx.get('block_index', 'N/A')
                        
                        print(f"   {i}. {tx_type} | Block #{block_index} | TX: {tx_id}")
                        print(f"      Time: {timestamp}")
                        
                        if 'fingerprint_id' in tx:
                            print(f"      Fingerprint ID: {tx['fingerprint_id']}")
                        if 'similarity_score' in tx:
                            print(f"      Similarity: {tx['similarity_score']:.1f}%")
                        print("")
                else:
                    print("   No transactions found")
                    
        else:
            print(f"❌ Failed to get blockchain data: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Blockchain check error: {e}")

if __name__ == "__main__":
    print("🚀 ESP32 SIMULATION - Blockchain Integration Test")
    print("This simulates what your ESP32 will do when connected")
    print("Watch the monitor_blockchain.py output for real-time updates!")
    print("")
    
    # Test enrollment
    enrollment_success = simulate_esp32_enrollment()
    
    if enrollment_success:
        print("\n⏳ Waiting 3 seconds for blockchain processing...")
        time.sleep(3)
        
        # Test verification
        verification_success = simulate_esp32_verification()
        
        print("\n⏳ Waiting 3 seconds for blockchain processing...")
        time.sleep(3)
        
        # Check blockchain status
        check_blockchain_updates()
        
        print("\n🎉 SIMULATION COMPLETE!")
        print("=" * 50)
        print("✅ Results Summary:")
        print(f"   Enrollment: {'✅ Success' if enrollment_success else '❌ Failed'}")
        print(f"   Verification: {'✅ Success' if verification_success else '❌ Failed'}")
        print("")
        print("🔍 Check the monitor_blockchain.py output to see:")
        print("   • New blockchain blocks created")
        print("   • Transaction details recorded")
        print("   • Real-time audit trail updates")
        print("")
        print("🎯 This demonstrates the ESP32 + Blockchain integration!")
        
    else:
        print("\n❌ Enrollment failed - skipping verification test")
        
    print("\n📋 Next Steps:")
    print("1. Upload this code to your ESP32 hardware")
    print("2. Connect fingerprint sensor and LCD")
    print("3. Use Serial Monitor commands (E/V/S)")
    print("4. Watch blockchain monitor for real-time updates")