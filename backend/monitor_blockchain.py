# Real-time ESP32 and Blockchain Monitoring Script
import requests
import json
import time
import threading
from datetime import datetime

# Backend configuration
BASE_URL = "https://swift-habitat-475216-n3.uc.r.appspot.com"

class EVMMonitor:
    def __init__(self):
        self.monitoring = True
        self.last_block_count = 0
        self.last_transaction_count = 0
        self.enrollment_count = 0
        self.verification_count = 0
        
    def print_header(self):
        print("="*80)
        print("🔗 EVM BLOCKCHAIN MONITORING - Real-time ESP32 Integration Test")
        print("="*80)
        print(f"Backend URL: {BASE_URL}")
        print(f"Monitoring started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*80)
        
    def get_blockchain_info(self):
        """Get current blockchain statistics"""
        try:
            response = requests.get(f"{BASE_URL}/api/blockchain/info/", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_audit_trail(self, limit=5):
        """Get recent transactions from blockchain"""
        try:
            response = requests.get(f"{BASE_URL}/api/blockchain/audit/?limit={limit}", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_fingerprint_count(self):
        """Get enrolled fingerprint count"""
        try:
            response = requests.get(f"{BASE_URL}/api/fingerprints/count/", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def validate_blockchain(self):
        """Validate blockchain integrity"""
        try:
            response = requests.get(f"{BASE_URL}/api/blockchain/validate/", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def print_blockchain_status(self):
        """Print current blockchain status"""
        blockchain_info = self.get_blockchain_info()
        
        if "error" not in blockchain_info and blockchain_info.get("success"):
            info = blockchain_info["blockchain_info"]
            print(f"📊 BLOCKCHAIN STATUS:")
            print(f"   Total Blocks: {info.get('total_blocks', 'N/A')}")
            print(f"   Pending Transactions: {info.get('pending_transactions', 'N/A')}")
            print(f"   Chain Valid: {'✅' if info.get('is_valid') else '❌'}")
            print(f"   Chain Size: {info.get('chain_size_kb', 0):.2f} KB")
            print(f"   Latest Hash: {info.get('latest_block_hash', 'N/A')[:16]}...")
            
            # Check for new blocks
            current_blocks = info.get('total_blocks', 0)
            if current_blocks > self.last_block_count:
                if self.last_block_count > 0:  # Skip first run
                    print(f"🆕 NEW BLOCK DETECTED! Block #{current_blocks}")
                self.last_block_count = current_blocks
                
        else:
            print(f"❌ Blockchain Status Error: {blockchain_info.get('error', 'Unknown error')}")
    
    def print_recent_transactions(self):
        """Print recent blockchain transactions"""
        audit = self.get_audit_trail(limit=3)
        
        if "error" not in audit and audit.get("success"):
            transactions = audit.get("transactions", [])
            total_count = audit.get("total_count", 0)
            
            print(f"📋 RECENT TRANSACTIONS (Total: {total_count}):")
            
            if transactions:
                for tx in transactions[-3:]:  # Last 3 transactions
                    tx_type = tx.get('type', 'UNKNOWN')
                    action = tx.get('action', 'unknown')
                    tx_id = tx.get('tx_id', 'N/A')
                    timestamp = tx.get('datetime', 'N/A')
                    block_index = tx.get('block_index', 'N/A')
                    
                    # Count transaction types
                    if tx_type == 'ENROLLMENT':
                        self.enrollment_count += 1
                    elif tx_type == 'VERIFICATION':
                        self.verification_count += 1
                    
                    print(f"   🔗 {tx_type} | Block #{block_index} | TX: {tx_id}")
                    print(f"      Time: {timestamp}")
                    if 'fingerprint_id' in tx:
                        print(f"      Fingerprint ID: {tx['fingerprint_id']}")
                    if 'similarity_score' in tx:
                        print(f"      Similarity: {tx['similarity_score']:.1f}%")
                    print("")
            else:
                print("   No transactions found")
            
            # Check for new transactions
            if total_count > self.last_transaction_count:
                if self.last_transaction_count > 0:  # Skip first run
                    new_tx_count = total_count - self.last_transaction_count
                    print(f"🆕 {new_tx_count} NEW TRANSACTION(S) DETECTED!")
                self.last_transaction_count = total_count
                
        else:
            print(f"❌ Transaction Error: {audit.get('error', 'Unknown error')}")
    
    def print_fingerprint_stats(self):
        """Print fingerprint enrollment statistics"""
        fp_data = self.get_fingerprint_count()
        
        if "error" not in fp_data and fp_data.get("success"):
            count = fp_data.get("fingerprint_count", 0)
            print(f"👆 FINGERPRINT DATABASE:")
            print(f"   Enrolled Templates: {count}")
            print(f"   Total Enrollments: {self.enrollment_count}")
            print(f"   Total Verifications: {self.verification_count}")
        else:
            print(f"❌ Fingerprint Count Error: {fp_data.get('error', 'Unknown error')}")
    
    def print_validation_status(self):
        """Print blockchain validation status"""
        validation = self.validate_blockchain()
        
        if "error" not in validation and validation.get("success"):
            is_valid = validation.get("blockchain_valid", False)
            print(f"🔒 BLOCKCHAIN INTEGRITY: {'✅ VALID' if is_valid else '❌ INVALID'}")
        else:
            print(f"❌ Validation Error: {validation.get('error', 'Unknown error')}")
    
    def monitor_loop(self):
        """Main monitoring loop"""
        self.print_header()
        
        while self.monitoring:
            try:
                print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Monitoring Update")
                print("-" * 50)
                
                # Get all status information
                self.print_blockchain_status()
                print("")
                self.print_recent_transactions()
                print("")
                self.print_fingerprint_stats()
                print("")
                self.print_validation_status()
                
                print("-" * 50)
                print("💡 ESP32 Instructions:")
                print("   Send 'E' via Serial Monitor to enroll fingerprint")
                print("   Send 'V' via Serial Monitor to verify fingerprint")
                print("   Watch this monitor for real-time blockchain updates!")
                
                # Wait for next update
                for i in range(10, 0, -1):
                    print(f"\r⏳ Next update in {i} seconds...", end="", flush=True)
                    time.sleep(1)
                print("\r" + " " * 30 + "\r", end="", flush=True)
                
            except KeyboardInterrupt:
                print("\n\n🛑 Monitoring stopped by user")
                self.monitoring = False
                break
            except Exception as e:
                print(f"\n❌ Monitor Error: {e}")
                time.sleep(5)
        
        print("👋 Monitoring session ended")
    
    def start_monitoring(self):
        """Start the monitoring in a separate thread"""
        monitor_thread = threading.Thread(target=self.monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        return monitor_thread

def test_backend_connectivity():
    """Test initial backend connectivity"""
    print("🔍 Testing backend connectivity...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is online!")
            print(f"   Message: {data.get('message', 'N/A')}")
            print(f"   Version: {data.get('version', 'N/A')}")
            print(f"   Blockchain: {data.get('blockchain', 'N/A')}")
            return True
        else:
            print(f"❌ Backend returned HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connectivity failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting EVM Blockchain Monitor...")
    
    # Test connectivity first
    if test_backend_connectivity():
        print("\n🎯 Backend is ready! Starting real-time monitoring...\n")
        
        # Start monitoring
        monitor = EVMMonitor()
        try:
            monitor.monitor_loop()
        except KeyboardInterrupt:
            print("\n\n👋 Monitor stopped. Thank you!")
    else:
        print("\n❌ Cannot start monitoring - backend not accessible")
        print("Please check:")
        print("1. Internet connection")
        print("2. Backend URL configuration") 
        print("3. GCP App Engine status")