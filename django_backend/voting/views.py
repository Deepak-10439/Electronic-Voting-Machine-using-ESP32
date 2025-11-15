"""
REST API Views for EVM Voting System
Provides secure endpoints for ESP32 devices and admin interface
"""

import json
import hashlib
import logging
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .models import Voter, Election, Candidate, Vote, AuditLog

logger = logging.getLogger('voting')

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# Health check endpoint for ESP32 devices
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Simple health check endpoint"""
    return Response({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# ESP32 system time sync
@api_view(['GET'])
@permission_classes([AllowAny])
def get_system_time(request):
    """Get current system time for ESP32 synchronization"""
    return Response({
        'success': True,
        'timestamp': int(datetime.now().timestamp()),
        'iso_time': datetime.now().isoformat()
    })

class ESP32AuthenticationView(APIView):
    """
    Authentication endpoint for ESP32 devices
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        return Response({
            'success': True,
            'message': 'Authentication endpoint ready'
        })

class VoterRegistrationView(APIView):
    """
    Voter registration endpoint
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        return Response({
            'success': True,
            'message': 'Registration endpoint ready'
        })

class ActiveElectionsView(APIView):
    """
    Get active elections for voting
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({
            'success': True,
            'elections': []
        })

class CastVoteView(APIView):
    """
    Cast vote endpoint for ESP32 devices
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response({
            'success': True,
            'message': 'Vote casting endpoint ready'
        })

class VoteVerificationView(APIView):
    """
    Verify vote on blockchain
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, vote_id):
        return Response({
            'success': True,
            'vote_id': vote_id
        })

class ElectionResultsView(APIView):
    """
    Get election results
    """
    permission_classes = [AllowAny]
    
    def get(self, request, election_id):
        return Response({
            'success': True,
            'election_id': election_id
        })

class BlockchainStatusView(APIView):
    """
    Get blockchain network status
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({
            'success': True,
            'blockchain_status': {
                'connected': False,
                'message': 'Blockchain integration ready for setup'
            }
        })
