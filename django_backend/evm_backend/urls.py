"""
URL configuration for evm_backend project.
EVM Blockchain Voting System - Main URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def api_root(request):
    """API root endpoint"""
    return JsonResponse({
        'message': 'EVM Blockchain Voting System API',
        'version': '1.0.0',
        'endpoints': {
            'authentication': '/api/auth/',
            'voter_registration': '/api/register/',
            'active_elections': '/api/elections/',
            'cast_vote': '/api/vote/',
            'verify_vote': '/api/verify/<vote_id>/',
            'election_results': '/api/results/<election_id>/',
            'blockchain_status': '/api/blockchain/status/',
            'health_check': '/api/health/',
            'system_time': '/api/time/',
            'admin': '/admin/'
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_root, name='api-root'),
    path('', include('voting.urls')),
]
