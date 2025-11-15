from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import uuid
from datetime import datetime

class Voter(AbstractUser):
    """
    Extended User model for voter information
    """
    voter_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    fingerprint_template = models.BinaryField(max_length=534, null=True, blank=True)  # R307 template size
    firebase_template_id = models.CharField(max_length=100, blank=True, null=True)
    aadhar_number = models.CharField(
        max_length=12,
        validators=[RegexValidator(r'^\d{12}$', 'Aadhar number must be 12 digits')],
        unique=True,
        null=True,
        blank=True
    )
    phone_number = models.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', 'Phone number must be 10 digits')],
        null=True,
        blank=True
    )
    address = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_eligible = models.BooleanField(default=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    last_vote_date = models.DateTimeField(null=True, blank=True)
    
    # Blockchain fields
    blockchain_address = models.CharField(max_length=42, blank=True, null=True)
    registration_tx_hash = models.CharField(max_length=66, blank=True, null=True)
    
    class Meta:
        db_table = 'voting_voter'
        verbose_name = 'Voter'
        verbose_name_plural = 'Voters'
    
    def __str__(self):
        return f"{self.username} ({self.aadhar_number})"
    
    def can_vote(self, election):
        """Check if voter is eligible to vote in specific election"""
        if not self.is_eligible or not self.is_active:
            return False
        
        # Check if already voted in this election
        existing_vote = Vote.objects.filter(
            voter=self,
            election=election
        ).exists()
        
        return not existing_vote

class Election(models.Model):
    """
    Election configuration and management
    """
    ELECTION_TYPES = [
        ('GENERAL', 'General Election'),
        ('LOCAL', 'Local Election'),
        ('SPECIAL', 'Special Election'),
    ]
    
    ELECTION_STATUS = [
        ('UPCOMING', 'Upcoming'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    election_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    election_type = models.CharField(max_length=20, choices=ELECTION_TYPES)
    status = models.CharField(max_length=20, choices=ELECTION_STATUS, default='UPCOMING')
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Blockchain configuration
    smart_contract_address = models.CharField(max_length=42, blank=True, null=True)
    deployment_tx_hash = models.CharField(max_length=66, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'voting_election'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.election_type})"
    
    def is_active(self):
        """Check if election is currently active"""
        now = datetime.now()
        return (
            self.status == 'ACTIVE' and
            self.start_date <= now <= self.end_date
        )

class Candidate(models.Model):
    """
    Candidate information for elections
    """
    candidate_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='candidates')
    name = models.CharField(max_length=200)
    party = models.CharField(max_length=100)
    symbol = models.CharField(max_length=50)
    position = models.IntegerField()  # Position on ballot
    
    # Additional information
    age = models.IntegerField()
    qualification = models.CharField(max_length=200)
    previous_experience = models.TextField(blank=True)
    
    # Blockchain fields
    blockchain_candidate_id = models.IntegerField(null=True, blank=True)
    registration_tx_hash = models.CharField(max_length=66, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'voting_candidate'
        unique_together = ['election', 'position']
        ordering = ['position']
    
    def __str__(self):
        return f"{self.name} ({self.party}) - {self.election.name}"
    
    def get_vote_count(self):
        """Get total votes for this candidate"""
        return Vote.objects.filter(candidate=self).count()

class Vote(models.Model):
    """
    Individual vote records
    """
    VOTE_STATUS = [
        ('PENDING', 'Pending Blockchain Confirmation'),
        ('CONFIRMED', 'Blockchain Confirmed'),
        ('FAILED', 'Transaction Failed'),
    ]
    
    vote_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    
    # Voting session information
    esp32_device_id = models.CharField(max_length=100)
    fingerprint_match_score = models.FloatField()
    voting_timestamp = models.DateTimeField(auto_now_add=True)
    
    # Blockchain tracking
    blockchain_tx_hash = models.CharField(max_length=66, null=True, blank=True)
    blockchain_block_number = models.IntegerField(null=True, blank=True)
    vote_status = models.CharField(max_length=20, choices=VOTE_STATUS, default='PENDING')
    gas_used = models.IntegerField(null=True, blank=True)
    
    # Security and verification
    vote_hash = models.CharField(max_length=64)  # SHA256 hash for verification
    fingerprint_template_hash = models.CharField(max_length=64)  # Template verification
    
    class Meta:
        db_table = 'voting_vote'
        unique_together = ['voter', 'election']  # One vote per voter per election
        indexes = [
            models.Index(fields=['election', 'candidate']),
            models.Index(fields=['blockchain_tx_hash']),
            models.Index(fields=['voting_timestamp']),
        ]
    
    def __str__(self):
        return f"Vote by {self.voter.username} for {self.candidate.name}"

class AuditLog(models.Model):
    """
    Comprehensive audit trail for all system activities
    """
    LOG_TYPES = [
        ('VOTER_REGISTRATION', 'Voter Registration'),
        ('VOTE_CAST', 'Vote Cast'),
        ('BLOCKCHAIN_TX', 'Blockchain Transaction'),
        ('AUTHENTICATION', 'Authentication'),
        ('SYSTEM_ACCESS', 'System Access'),
        ('ERROR', 'System Error'),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    log_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    log_type = models.CharField(max_length=50, choices=LOG_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='LOW')
    
    # Related objects
    voter = models.ForeignKey(Voter, on_delete=models.SET_NULL, null=True, blank=True)
    election = models.ForeignKey(Election, on_delete=models.SET_NULL, null=True, blank=True)
    vote = models.ForeignKey(Vote, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Log details
    action = models.CharField(max_length=200)
    description = models.TextField()
    metadata = models.JSONField(default=dict)  # Additional data
    
    # Source information
    esp32_device_id = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True, null=True)
    
    # Blockchain reference
    blockchain_tx_hash = models.CharField(max_length=66, blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'voting_audit_log'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['log_type', 'timestamp']),
            models.Index(fields=['voter', 'timestamp']),
            models.Index(fields=['blockchain_tx_hash']),
        ]
    
    def __str__(self):
        return f"{self.log_type}: {self.action} at {self.timestamp}"

class BlockchainSync(models.Model):
    """
    Track blockchain synchronization status
    """
    SYNC_STATUS = [
        ('PENDING', 'Pending'),
        ('SYNCING', 'Syncing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    sync_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    block_number = models.IntegerField()
    transaction_count = models.IntegerField(default=0)
    vote_count = models.IntegerField(default=0)
    
    sync_status = models.CharField(max_length=20, choices=SYNC_STATUS, default='PENDING')
    error_message = models.TextField(blank=True, null=True)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'voting_blockchain_sync'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Sync Block {self.block_number} - {self.sync_status}"
