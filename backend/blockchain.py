"""
Simple Blockchain Implementation for EVM
Provides immutable audit trail for fingerprint enrollment and verification
"""

import hashlib
import json
import time
import os
from datetime import datetime
from typing import List, Dict, Optional


class Block:
    """
    A simple block in the blockchain
    """
    def __init__(self, index: int, timestamp: float, data: Dict, previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the block"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int = 2):
        """Simple proof-of-work mining (very lightweight)"""
        target = "0" * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()
    
    def to_dict(self) -> Dict:
        """Convert block to dictionary for storage"""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }


class EVMBlockchain:
    """
    Simple blockchain for EVM fingerprint operations
    """
    def __init__(self, data_file: str = "blockchain_data.json"):
        self.difficulty = 2  # Very low difficulty for minimal computation
        self.pending_transactions: List[Dict] = []
        self.data_file = data_file
        
        # Try to load existing blockchain, create new if doesn't exist
        if os.path.exists(data_file) and os.path.getsize(data_file) > 0:
            self.load_from_file()
        else:
            self.chain: List[Block] = [self.create_genesis_block()]
            self.save_to_file()
    
    def create_genesis_block(self) -> Block:
        """Create the first block in the chain"""
        genesis_data = {
            "type": "GENESIS",
            "message": "EVM Blockchain Genesis Block",
            "system": "Fingerprint EVM v1.0",
            "created": datetime.now().isoformat()
        }
        block = Block(0, time.time(), genesis_data, "0")
        block.mine_block(self.difficulty)
        return block
    
    def get_latest_block(self) -> Block:
        """Get the most recent block"""
        return self.chain[-1]
    
    def add_transaction(self, transaction: Dict):
        """Add a transaction to pending transactions"""
        # Add timestamp and unique ID
        transaction["timestamp"] = time.time()
        transaction["datetime"] = datetime.now().isoformat()
        transaction["tx_id"] = self.generate_transaction_id(transaction)
        self.pending_transactions.append(transaction)
    
    def generate_transaction_id(self, transaction: Dict) -> str:
        """Generate unique transaction ID"""
        tx_string = json.dumps(transaction, sort_keys=True)
        return hashlib.sha256(tx_string.encode()).hexdigest()[:16]
    
    def mine_pending_transactions(self) -> Optional[Block]:
        """Mine all pending transactions into a new block"""
        if not self.pending_transactions:
            return None
        
        # Create new block
        latest_block = self.get_latest_block()
        new_block = Block(
            index=latest_block.index + 1,
            timestamp=time.time(),
            data={
                "transactions": self.pending_transactions.copy(),
                "transaction_count": len(self.pending_transactions)
            },
            previous_hash=latest_block.hash
        )
        
        # Mine the block (lightweight proof-of-work)
        new_block.mine_block(self.difficulty)
        
        # Add to chain and clear pending
        self.chain.append(new_block)
        self.pending_transactions.clear()
        
        # Auto-save after mining
        self.save_to_file()
        
        return new_block
    
    def validate_chain(self) -> bool:
        """Validate the entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if current block's hash is valid
            if current_block.hash != current_block.calculate_hash():
                return False
            
            # Check if current block points to previous block
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True
    
    def get_chain_info(self) -> Dict:
        """Get blockchain statistics"""
        return {
            "total_blocks": len(self.chain),
            "pending_transactions": len(self.pending_transactions),
            "latest_block_hash": self.get_latest_block().hash,
            "is_valid": self.validate_chain(),
            "chain_size_kb": len(json.dumps([block.to_dict() for block in self.chain])) / 1024
        }
    
    def get_transaction_history(self, transaction_type: str = None) -> List[Dict]:
        """Get all transactions of a specific type"""
        transactions = []
        for block in self.chain[1:]:  # Skip genesis block
            if "transactions" in block.data:
                for tx in block.data["transactions"]:
                    if transaction_type is None or tx.get("type") == transaction_type:
                        tx["block_index"] = block.index
                        tx["block_hash"] = block.hash
                        transactions.append(tx)
        return transactions
    
    def record_enrollment(self, user_id: str, fingerprint_id: int, template_hash: str, 
                         esp32_ip: str = None) -> str:
        """Record fingerprint enrollment in blockchain"""
        transaction = {
            "type": "ENROLLMENT",
            "user_id": user_id,
            "fingerprint_id": fingerprint_id,
            "template_hash": template_hash,  # Hash of template for privacy
            "esp32_ip": esp32_ip,
            "action": "fingerprint_enrolled"
        }
        self.add_transaction(transaction)
        
        # Auto-mine single transactions for real-time recording
        block = self.mine_pending_transactions()
        return transaction["tx_id"] if block else None
    
    def record_verification(self, fingerprint_id: int, result: bool, 
                          similarity: float, esp32_ip: str = None) -> str:
        """Record fingerprint verification in blockchain"""
        transaction = {
            "type": "VERIFICATION",
            "fingerprint_id": fingerprint_id,
            "verification_result": "SUCCESS" if result else "FAILED",
            "similarity_score": similarity,
            "esp32_ip": esp32_ip,
            "action": "fingerprint_verified"
        }
        self.add_transaction(transaction)
        
        # Auto-mine single transactions for real-time recording
        block = self.mine_pending_transactions()
        return transaction["tx_id"] if block else None
    
    def record_voting_event(self, user_id: str, vote_choice: str, election_id: str) -> str:
        """Record voting event in blockchain"""
        transaction = {
            "type": "VOTE",
            "user_id": user_id,
            "vote_choice": vote_choice,  # This would be encrypted in real system
            "election_id": election_id,
            "action": "vote_cast"
        }
        self.add_transaction(transaction)
        
        block = self.mine_pending_transactions()
        return transaction["tx_id"] if block else None
    
    def export_chain(self) -> List[Dict]:
        """Export entire blockchain for backup/analysis"""
        return [block.to_dict() for block in self.chain]
    
    def import_chain(self, chain_data: List[Dict]) -> bool:
        """Import blockchain from backup"""
        try:
            new_chain = []
            for block_data in chain_data:
                block = Block(
                    block_data["index"],
                    block_data["timestamp"],
                    block_data["data"],
                    block_data["previous_hash"]
                )
                block.nonce = block_data["nonce"]
                block.hash = block_data["hash"]
                new_chain.append(block)
            
            # Simple validation - check chain continuity
            for i in range(1, len(new_chain)):
                current_block = new_chain[i]
                previous_block = new_chain[i - 1]
                
                # Check if current block points to previous block
                if current_block.previous_hash != previous_block.hash:
                    return False
            
            # If validation passes, update the chain
            self.chain = new_chain
            return True
        except Exception:
            return False
    
    def save_to_file(self) -> bool:
        """Save blockchain to file"""
        try:
            data = {
                "chain": self.export_chain(),
                "pending_transactions": self.pending_transactions,
                "saved_at": datetime.now().isoformat()
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving blockchain: {e}")
            return False
    
    def load_from_file(self) -> bool:
        """Load blockchain from file"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            if "chain" in data:
                if self.import_chain(data["chain"]):
                    if "pending_transactions" in data:
                        self.pending_transactions = data["pending_transactions"]
                    print(f"Blockchain loaded from {self.data_file}")
                    return True
            return False
        except Exception as e:
            print(f"Error loading blockchain: {e}")
            # Create new blockchain if loading fails
            self.chain = [self.create_genesis_block()]
            return False


# Global blockchain instance
evm_blockchain = EVMBlockchain()


def get_blockchain_instance() -> EVMBlockchain:
    """Get the global blockchain instance"""
    return evm_blockchain


def hash_template(template_data: str) -> str:
    """Create hash of fingerprint template for privacy"""
    return hashlib.sha256(template_data.encode()).hexdigest()[:32]