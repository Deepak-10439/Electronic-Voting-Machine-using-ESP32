"""
Django REST Framework Serializers for EVM Voting System
"""

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Voter, Election, Candidate, Vote, AuditLog

class VoterSerializer(serializers.ModelSerializer):
    """Serializer for Voter model"""
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    fingerprint_template = serializers.CharField(max_length=1068)  # Hex string representation
    
    class Meta:
        model = Voter
        fields = [
            'username', 'email', 'first_name', 'last_name', 'password', 
            'confirm_password', 'aadhar_number', 'phone_number', 'address',
            'date_of_birth', 'fingerprint_template'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'aadhar_number': {'write_only': True}
        }
    
    def validate(self, data):
        """Validate voter registration data"""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        
        # Validate fingerprint template format
        fingerprint_hex = data['fingerprint_template']
        if len(fingerprint_hex) != 1068:  # 534 bytes * 2 hex chars
            raise serializers.ValidationError("Invalid fingerprint template format")
        
        try:
            # Validate hex format
            bytes.fromhex(fingerprint_hex)
        except ValueError:
            raise serializers.ValidationError("Invalid fingerprint template hex format")
        
        return data
    
    def create(self, validated_data):
        """Create new voter"""
        # Remove confirm_password and convert fingerprint
        validated_data.pop('confirm_password')
        fingerprint_hex = validated_data.pop('fingerprint_template')
        fingerprint_bytes = bytes.fromhex(fingerprint_hex)
        
        # Hash password
        validated_data['password'] = make_password(validated_data['password'])
        
        # Create voter
        voter = Voter.objects.create(**validated_data)
        voter.fingerprint_template = fingerprint_bytes
        voter.save()
        
        return voter

class ElectionSerializer(serializers.ModelSerializer):
    """Serializer for Election model"""
    candidates_count = serializers.SerializerMethodField()
    total_votes = serializers.SerializerMethodField()
    is_currently_active = serializers.SerializerMethodField()
    
    class Meta:
        model = Election
        fields = [
            'election_id', 'name', 'description', 'election_type', 'status',
            'start_date', 'end_date', 'smart_contract_address', 
            'candidates_count', 'total_votes', 'is_currently_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['election_id', 'created_at', 'updated_at']
    
    def get_candidates_count(self, obj):
        """Get number of candidates in election"""
        return obj.candidates.count()
    
    def get_total_votes(self, obj):
        """Get total votes cast in election"""
        return Vote.objects.filter(election=obj, vote_status='CONFIRMED').count()
    
    def get_is_currently_active(self, obj):
        """Check if election is currently active"""
        return obj.is_active()

class CandidateSerializer(serializers.ModelSerializer):
    """Serializer for Candidate model"""
    vote_count = serializers.SerializerMethodField()
    vote_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Candidate
        fields = [
            'candidate_id', 'name', 'party', 'symbol', 'position',
            'age', 'qualification', 'previous_experience',
            'vote_count', 'vote_percentage', 'created_at'
        ]
        read_only_fields = ['candidate_id', 'vote_count', 'vote_percentage', 'created_at']
    
    def get_vote_count(self, obj):
        """Get vote count for candidate"""
        return Vote.objects.filter(candidate=obj, vote_status='CONFIRMED').count()
    
    def get_vote_percentage(self, obj):
        """Get vote percentage for candidate"""
        total_votes = Vote.objects.filter(
            election=obj.election, 
            vote_status='CONFIRMED'
        ).count()
        
        if total_votes == 0:
            return 0.0
        
        candidate_votes = self.get_vote_count(obj)
        return round((candidate_votes / total_votes) * 100, 2)

class VoteSerializer(serializers.ModelSerializer):
    """Serializer for Vote model"""
    voter_name = serializers.CharField(source='voter.get_full_name', read_only=True)
    election_name = serializers.CharField(source='election.name', read_only=True)
    candidate_name = serializers.CharField(source='candidate.name', read_only=True)
    candidate_party = serializers.CharField(source='candidate.party', read_only=True)
    
    class Meta:
        model = Vote
        fields = [
            'vote_id', 'voter_name', 'election_name', 'candidate_name',
            'candidate_party', 'esp32_device_id', 'fingerprint_match_score',
            'voting_timestamp', 'blockchain_tx_hash', 'blockchain_block_number',
            'vote_status', 'gas_used', 'vote_hash'
        ]
        read_only_fields = [
            'vote_id', 'voting_timestamp', 'blockchain_tx_hash', 
            'blockchain_block_number', 'vote_status', 'gas_used', 'vote_hash'
        ]

class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog model"""
    voter_name = serializers.CharField(source='voter.get_full_name', read_only=True)
    election_name = serializers.CharField(source='election.name', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'log_id', 'log_type', 'severity', 'voter_name', 'election_name',
            'action', 'description', 'metadata', 'esp32_device_id',
            'ip_address', 'blockchain_tx_hash', 'timestamp'
        ]
        read_only_fields = ['log_id', 'timestamp']

class VoteCastRequestSerializer(serializers.Serializer):
    """Serializer for vote casting request from ESP32"""
    election_id = serializers.UUIDField()
    candidate_id = serializers.UUIDField()
    device_id = serializers.CharField(max_length=100)
    fingerprint_match_score = serializers.FloatField(min_value=0.0, max_value=1.0)
    
    def validate_fingerprint_match_score(self, value):
        """Validate fingerprint match score"""
        if value < 0.8:  # Minimum 80% match required
            raise serializers.ValidationError("Fingerprint match score too low")
        return value

class ESP32AuthRequestSerializer(serializers.Serializer):
    """Serializer for ESP32 authentication request"""
    device_id = serializers.CharField(max_length=100)
    aadhar_number = serializers.CharField(max_length=12)
    fingerprint_template = serializers.CharField(max_length=1068)  # Hex string
    
    def validate_aadhar_number(self, value):
        """Validate Aadhar number format"""
        if not value.isdigit() or len(value) != 12:
            raise serializers.ValidationError("Invalid Aadhar number format")
        return value
    
    def validate_fingerprint_template(self, value):
        """Validate fingerprint template format"""
        if len(value) != 1068:
            raise serializers.ValidationError("Invalid fingerprint template length")
        
        try:
            bytes.fromhex(value)
        except ValueError:
            raise serializers.ValidationError("Invalid fingerprint template hex format")
        
        return value

class ElectionResultSerializer(serializers.Serializer):
    """Serializer for election results"""
    candidate_id = serializers.UUIDField()
    name = serializers.CharField()
    party = serializers.CharField()
    symbol = serializers.CharField()
    local_votes = serializers.IntegerField()
    blockchain_votes = serializers.IntegerField()
    percentage = serializers.FloatField()
    position = serializers.IntegerField()

class BlockchainStatusSerializer(serializers.Serializer):
    """Serializer for blockchain status"""
    connected = serializers.BooleanField()
    network_id = serializers.CharField()
    latest_block = serializers.IntegerField()
    gas_price = serializers.IntegerField()
    account_address = serializers.CharField()
    account_balance = serializers.FloatField()
    contract_address = serializers.CharField()