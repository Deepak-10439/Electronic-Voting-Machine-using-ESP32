"""
Blockchain Manager for EVM Voting System
Handles all blockchain interactions using Web3.py
"""

import json
import hashlib
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime
from web3 import Web3
from web3.exceptions import ContractLogicError, TransactionNotFound
from django.conf import settings
from .models import Vote, AuditLog, BlockchainSync

logger = logging.getLogger('voting')

class BlockchainManager:
    """
    Manages all blockchain operations for the voting system
    """
    
    def __init__(self):
        """Initialize Web3 connection and smart contract"""
        self.w3 = None
        self.contract = None
        self.account = None
        self._initialize_web3()
    
    def _initialize_web3(self):
        """Initialize Web3 connection"""
        try:
            blockchain_config = settings.BLOCKCHAIN_CONFIG
            provider_uri = blockchain_config.get('WEB3_PROVIDER_URI', 'http://localhost:8545')
            
            # Connect to Ethereum node
            self.w3 = Web3(Web3.HTTPProvider(provider_uri))
            
            if not self.w3.is_connected():
                raise ConnectionError("Failed to connect to blockchain network")
            
            # Set up account from private key
            private_key = blockchain_config.get('PRIVATE_KEY')
            if private_key:
                self.account = self.w3.eth.account.from_key(private_key)
                self.w3.eth.default_account = self.account.address
            
            # Load smart contract if address is configured
            contract_address = blockchain_config.get('CONTRACT_ADDRESS')
            if contract_address:
                self._load_contract(contract_address)
            
            logger.info(f"Blockchain connected successfully. Network ID: {self.w3.net.version}")
            
        except Exception as e:
            logger.error(f"Failed to initialize blockchain connection: {str(e)}")
            raise
    
    def _load_contract(self, contract_address: str):
        """Load the voting smart contract"""
        try:
            # Smart contract ABI - simplified version
            contract_abi = [
                {
                    "name": "registerVoter",
                    "type": "function",
                    "inputs": [
                        {"name": "_voterAddress", "type": "address"},
                        {"name": "_aadharHash", "type": "bytes32"},
                        {"name": "_fingerprintHash", "type": "bytes32"}
                    ],
                    "outputs": [{"name": "", "type": "bool"}]
                },
                {
                    "name": "castVote",
                    "type": "function",
                    "inputs": [
                        {"name": "_electionId", "type": "uint256"},
                        {"name": "_candidateId", "type": "uint256"},
                        {"name": "_voterHash", "type": "bytes32"},
                        {"name": "_timestamp", "type": "uint256"}
                    ],
                    "outputs": [{"name": "", "type": "bool"}]
                },
                {
                    "name": "getVoteCount",
                    "type": "function",
                    "inputs": [
                        {"name": "_electionId", "type": "uint256"},
                        {"name": "_candidateId", "type": "uint256"}
                    ],
                    "outputs": [{"name": "", "type": "uint256"}]
                },
                {
                    "name": "hasVoted",
                    "type": "function",
                    "inputs": [
                        {"name": "_voterAddress", "type": "address"},
                        {"name": "_electionId", "type": "uint256"}
                    ],
                    "outputs": [{"name": "", "type": "bool"}]
                },
                {
                    "name": "VoteCase",
                    "type": "event",
                    "inputs": [
                        {"indexed": True, "name": "electionId", "type": "uint256"},
                        {"indexed": True, "name": "candidateId", "type": "uint256"},
                        {"indexed": True, "name": "voter", "type": "address"},
                        {"indexed": False, "name": "timestamp", "type": "uint256"}
                    ]
                }
            ]
            
            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(contract_address),
                abi=contract_abi
            )
            
            logger.info(f"Smart contract loaded: {contract_address}")
            
        except Exception as e:
            logger.error(f"Failed to load smart contract: {str(e)}")
            raise
    
    def get_balance(self, address: str = None) -> float:
        """Get ETH balance for an address"""
        try:
            if not address:
                address = self.account.address if self.account else None
            
            if not address:
                raise ValueError("No address provided and no default account set")
            
            balance_wei = self.w3.eth.get_balance(Web3.to_checksum_address(address))
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            return float(balance_eth)
            
        except Exception as e:
            logger.error(f"Failed to get balance: {str(e)}")
            return 0.0
    
    def register_voter_on_blockchain(self, voter) -> Tuple[bool, Optional[str]]:
        """
        Register voter on blockchain
        Returns (success, transaction_hash)
        """
        try:
            if not self.contract or not self.account:
                raise ValueError("Blockchain not properly initialized")
            
            # Generate hashes for privacy
            aadhar_hash = self._generate_hash(voter.aadhar_number)
            fingerprint_hash = self._generate_hash(bytes(voter.fingerprint_template))
            
            # Prepare transaction
            function = self.contract.functions.registerVoter(
                Web3.to_checksum_address(voter.blockchain_address or self.account.address),
                Web3.keccak(text=aadhar_hash)[:32],
                Web3.keccak(text=fingerprint_hash)[:32]
            )
            
            # Build transaction
            transaction = function.build_transaction({
                'from': self.account.address,
                'gas': settings.BLOCKCHAIN_CONFIG.get('GAS_LIMIT', 300000),
                'gasPrice': self.w3.to_wei(settings.BLOCKCHAIN_CONFIG.get('GAS_PRICE', 20), 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt.status == 1:
                logger.info(f"Voter registration successful: {receipt.transactionHash.hex()}")
                return True, receipt.transactionHash.hex()
            else:
                logger.error(f"Voter registration failed: {receipt}")
                return False, None
                
        except Exception as e:
            logger.error(f"Blockchain voter registration error: {str(e)}")
            return False, None
    
    def cast_vote_on_blockchain(self, vote) -> Tuple[bool, Optional[str]]:
        """
        Cast vote on blockchain
        Returns (success, transaction_hash)
        """
        try:
            if not self.contract or not self.account:
                raise ValueError("Blockchain not properly initialized")
            
            # Generate voter hash for privacy
            voter_data = f"{vote.voter.aadhar_number}_{vote.fingerprint_match_score}"
            voter_hash = self._generate_hash(voter_data)
            
            # Prepare transaction
            function = self.contract.functions.castVote(
                int(vote.election.election_id.int),
                int(vote.candidate.candidate_id.int),
                Web3.keccak(text=voter_hash)[:32],
                int(vote.voting_timestamp.timestamp())
            )
            
            # Build transaction
            transaction = function.build_transaction({
                'from': self.account.address,
                'gas': settings.BLOCKCHAIN_CONFIG.get('GAS_LIMIT', 300000),
                'gasPrice': self.w3.to_wei(settings.BLOCKCHAIN_CONFIG.get('GAS_PRICE', 20), 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt.status == 1:
                # Update vote record
                vote.blockchain_tx_hash = receipt.transactionHash.hex()
                vote.blockchain_block_number = receipt.blockNumber
                vote.vote_status = 'CONFIRMED'
                vote.gas_used = receipt.gasUsed
                vote.save()
                
                # Create audit log
                AuditLog.objects.create(
                    log_type='BLOCKCHAIN_TX',
                    severity='MEDIUM',
                    voter=vote.voter,
                    election=vote.election,
                    vote=vote,
                    action='Vote Cast on Blockchain',
                    description=f'Vote successfully recorded on blockchain',
                    metadata={
                        'tx_hash': receipt.transactionHash.hex(),
                        'block_number': receipt.blockNumber,
                        'gas_used': receipt.gasUsed
                    },
                    blockchain_tx_hash=receipt.transactionHash.hex()
                )
                
                logger.info(f"Vote cast successful: {receipt.transactionHash.hex()}")
                return True, receipt.transactionHash.hex()
            else:
                vote.vote_status = 'FAILED'
                vote.save()
                logger.error(f"Vote cast failed: {receipt}")
                return False, None
                
        except Exception as e:
            vote.vote_status = 'FAILED'
            vote.save()
            logger.error(f"Blockchain vote casting error: {str(e)}")
            return False, None
    
    def verify_vote(self, tx_hash: str) -> Dict:
        """
        Verify a vote transaction on blockchain
        """
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            transaction = self.w3.eth.get_transaction(tx_hash)
            
            # Decode transaction logs if available
            logs = []
            if self.contract and receipt.logs:
                for log in receipt.logs:
                    try:
                        decoded_log = self.contract.events.VoteCast().processLog(log)
                        logs.append({
                            'election_id': decoded_log['args']['electionId'],
                            'candidate_id': decoded_log['args']['candidateId'],
                            'voter': decoded_log['args']['voter'],
                            'timestamp': decoded_log['args']['timestamp']
                        })
                    except:
                        continue
            
            return {
                'success': True,
                'transaction_hash': tx_hash,
                'block_number': receipt.blockNumber,
                'status': 'confirmed' if receipt.status == 1 else 'failed',
                'gas_used': receipt.gasUsed,
                'from_address': transaction['from'],
                'to_address': transaction['to'],
                'logs': logs,
                'timestamp': self.w3.eth.get_block(receipt.blockNumber)['timestamp']
            }
            
        except TransactionNotFound:
            return {
                'success': False,
                'error': 'Transaction not found',
                'transaction_hash': tx_hash
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'transaction_hash': tx_hash
            }
    
    def get_candidate_votes(self, election_id: int, candidate_id: int) -> int:
        """
        Get vote count for a candidate from blockchain
        """
        try:
            if not self.contract:
                raise ValueError("Smart contract not loaded")
            
            vote_count = self.contract.functions.getVoteCount(
                election_id,
                candidate_id
            ).call()
            
            return vote_count
            
        except Exception as e:
            logger.error(f"Failed to get candidate votes: {str(e)}")
            return 0
    
    def has_voter_voted(self, voter_address: str, election_id: int) -> bool:
        """
        Check if voter has already voted in an election
        """
        try:
            if not self.contract:
                raise ValueError("Smart contract not loaded")
            
            has_voted = self.contract.functions.hasVoted(
                Web3.to_checksum_address(voter_address),
                election_id
            ).call()
            
            return has_voted
            
        except Exception as e:
            logger.error(f"Failed to check voter status: {str(e)}")
            return False
    
    def sync_blockchain_data(self, from_block: int = 0, to_block: str = 'latest') -> Dict:
        """
        Sync blockchain data with local database
        """
        try:
            if not self.contract:
                raise ValueError("Smart contract not loaded")
            
            sync_record = BlockchainSync.objects.create(
                block_number=0,
                sync_status='SYNCING'
            )
            
            # Get events from blockchain
            vote_filter = self.contract.events.VoteCast.create_filter(
                fromBlock=from_block,
                toBlock=to_block
            )
            
            vote_events = vote_filter.get_all_entries()
            synced_votes = 0
            
            for event in vote_events:
                try:
                    # Process each vote event
                    election_id = event['args']['electionId']
                    candidate_id = event['args']['candidateId']
                    voter_address = event['args']['voter']
                    timestamp = event['args']['timestamp']
                    tx_hash = event['transactionHash'].hex()
                    
                    # Update local vote record if exists
                    try:
                        vote = Vote.objects.get(blockchain_tx_hash=tx_hash)
                        vote.vote_status = 'CONFIRMED'
                        vote.blockchain_block_number = event['blockNumber']
                        vote.save()
                        synced_votes += 1
                    except Vote.DoesNotExist:
                        # Log unmatched blockchain vote
                        AuditLog.objects.create(
                            log_type='BLOCKCHAIN_TX',
                            severity='MEDIUM',
                            action='Blockchain Vote Found',
                            description=f'Vote found on blockchain without local record',
                            metadata={
                                'tx_hash': tx_hash,
                                'election_id': election_id,
                                'candidate_id': candidate_id,
                                'voter_address': voter_address
                            },
                            blockchain_tx_hash=tx_hash
                        )
                
                except Exception as e:
                    logger.error(f"Failed to process vote event: {str(e)}")
                    continue
            
            # Update sync record
            sync_record.sync_status = 'COMPLETED'
            sync_record.vote_count = synced_votes
            sync_record.block_number = self.w3.eth.block_number
            sync_record.completed_at = datetime.now()
            sync_record.save()
            
            logger.info(f"Blockchain sync completed. Synced {synced_votes} votes.")
            
            return {
                'success': True,
                'synced_votes': synced_votes,
                'current_block': self.w3.eth.block_number,
                'sync_id': str(sync_record.sync_id)
            }
            
        except Exception as e:
            sync_record.sync_status = 'FAILED'
            sync_record.error_message = str(e)
            sync_record.save()
            
            logger.error(f"Blockchain sync failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_hash(self, data: any) -> str:
        """Generate SHA256 hash of data"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        elif isinstance(data, int):
            data = str(data).encode('utf-8')
        
        return hashlib.sha256(data).hexdigest()
    
    def get_network_info(self) -> Dict:
        """Get blockchain network information"""
        try:
            return {
                'connected': self.w3.is_connected(),
                'network_id': self.w3.net.version,
                'latest_block': self.w3.eth.block_number,
                'gas_price': self.w3.eth.gas_price,
                'account_address': self.account.address if self.account else None,
                'account_balance': self.get_balance() if self.account else 0,
                'contract_address': self.contract.address if self.contract else None
            }
        except Exception as e:
            logger.error(f"Failed to get network info: {str(e)}")
            return {
                'connected': False,
                'error': str(e)
            }

# Global instance
blockchain_manager = BlockchainManager()