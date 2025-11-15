"""
URL Configuration for EVM Voting System API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API URL patterns
urlpatterns = [
    # ESP32 endpoints
    path('api/auth/', views.ESP32AuthenticationView.as_view(), name='esp32-auth'),
    path('api/register/', views.VoterRegistrationView.as_view(), name='voter-register'),
    path('api/elections/', views.ActiveElectionsView.as_view(), name='active-elections'),
    path('api/vote/', views.CastVoteView.as_view(), name='cast-vote'),
    path('api/verify/<uuid:vote_id>/', views.VoteVerificationView.as_view(), name='verify-vote'),
    path('api/results/<uuid:election_id>/', views.ElectionResultsView.as_view(), name='election-results'),
    path('api/blockchain/status/', views.BlockchainStatusView.as_view(), name='blockchain-status'),
    
    # Utility endpoints
    path('api/health/', views.health_check, name='health-check'),
    path('api/time/', views.get_system_time, name='system-time'),
]