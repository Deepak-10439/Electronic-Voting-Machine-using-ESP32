# Test blockchain integration with enrollment and verification
import requests
import json

# Test URLs
BASE_URL = "https://swift-habitat-475216-n3.uc.r.appspot.com"

def test_enrollment():
    """Test fingerprint enrollment with blockchain recording"""
    enrollment_data = {
        "id": 99,
        "data": "01,02,03,04,05,06,07,08,09,0A,0B,0C,0D,0E,0F,10",
        "size": 16
    }
    
    print("Testing fingerprint enrollment with blockchain...")
    response = requests.post(f"{BASE_URL}/api/fingerprints/enroll/", 
                           json=enrollment_data,
                           headers={'Content-Type': 'application/json'})
    
    print(f"Enrollment Response: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json().get('success', False)

def test_verification():
    """Test fingerprint verification with blockchain recording"""
    verification_data = {
        "data": "01,02,03,04,05,06,07,08,09,0A,0B,0C,0D,0E,0F,10",
        "threshold": 65
    }
    
    print("\nTesting fingerprint verification with blockchain...")
    response = requests.post(f"{BASE_URL}/api/verification/verify/", 
                           json=verification_data,
                           headers={'Content-Type': 'application/json'})
    
    print(f"Verification Response: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json().get('success', False)

def check_blockchain_audit():
    """Check blockchain audit trail"""
    print("\nChecking blockchain audit trail...")
    response = requests.get(f"{BASE_URL}/api/blockchain/audit/")
    
    print(f"Audit Response: {response.status_code}")
    audit_data = response.json()
    print(f"Total transactions: {audit_data.get('total_count', 0)}")
    
    for i, tx in enumerate(audit_data.get('transactions', [])):
        print(f"\nTransaction {i+1}:")
        print(f"  Type: {tx.get('type')}")
        print(f"  Action: {tx.get('action')}")
        print(f"  TX ID: {tx.get('tx_id')}")
        print(f"  Time: {tx.get('datetime')}")
        print(f"  Block: {tx.get('block_index')}")

def check_blockchain_info():
    """Check blockchain information"""
    print("\nChecking blockchain information...")
    response = requests.get(f"{BASE_URL}/api/blockchain/info/")
    
    print(f"Info Response: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("=== EVM Blockchain Integration Test ===")
    
    # Test enrollment
    enrollment_success = test_enrollment()
    
    # Test verification
    verification_success = test_verification()
    
    # Check audit trail
    check_blockchain_audit()
    
    # Check blockchain info
    check_blockchain_info()
    
    print(f"\n=== Test Results ===")
    print(f"Enrollment: {'✅ Success' if enrollment_success else '❌ Failed'}")
    print(f"Verification: {'✅ Success' if verification_success else '❌ Failed'}")