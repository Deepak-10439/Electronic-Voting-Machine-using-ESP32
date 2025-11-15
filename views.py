"""
API Views for EVM Backend
Handles HTTP requests and returns JSON responses
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from firebase_service import FirebaseService
import json


def index(request):
    """Root endpoint - API information"""
    return JsonResponse({
        "message": "EVM Fingerprint Backend API",
        "version": "1.0.0",
        "database": "Firebase Realtime Database",
        "endpoints": {
            "fingerprints": {
                "GET /api/fingerprints/": "Get all fingerprint templates",
                "GET /api/fingerprints/count/": "Get count of enrolled fingerprints",
                "GET /api/fingerprints/id/<template_id>/": "Get fingerprint template by ID",
                "GET /api/fingerprints/key/<template_key>/": "Get fingerprint template by key (e.g., template_2)"
            },
            "statistics": {
                "GET /api/statistics/": "Get database statistics"
            }
        }
    })


@require_http_methods(["GET"])
def get_all_fingerprints(request):
    """
    GET /api/fingerprints/
    Retrieve all fingerprint templates from Firebase
    """
    templates = FirebaseService.get_all_fingerprint_templates()
    
    if isinstance(templates, dict) and "error" in templates:
        return JsonResponse(templates, status=500)
    
    return JsonResponse({
        "success": True,
        "count": len(templates),
        "data": templates
    })


@require_http_methods(["GET"])
def get_fingerprint_count(request):
    """
    GET /api/fingerprints/count/
    Get the count of enrolled fingerprints
    """
    count = FirebaseService.get_fingerprint_count()
    
    if isinstance(count, dict) and "error" in count:
        return JsonResponse(count, status=500)
    
    return JsonResponse({
        "success": True,
        "fingerprint_count": count
    })


@require_http_methods(["GET"])
def get_fingerprint_by_id(request, template_id):
    """
    GET /api/fingerprints/id/<template_id>/
    Retrieve a specific fingerprint template by ID
    """
    template = FirebaseService.get_fingerprint_template_by_id(int(template_id))
    
    if isinstance(template, dict) and "error" in template:
        return JsonResponse(template, status=404)
    
    return JsonResponse({
        "success": True,
        "data": template
    })


@require_http_methods(["GET"])
def get_fingerprint_by_key(request, template_key):
    """
    GET /api/fingerprints/key/<template_key>/
    Retrieve a specific fingerprint template by key (e.g., template_2)
    """
    template = FirebaseService.get_fingerprint_template_by_key(template_key)
    
    if isinstance(template, dict) and "error" in template:
        return JsonResponse(template, status=404)
    
    return JsonResponse({
        "success": True,
        "data": template
    })


@require_http_methods(["GET"])
def get_statistics(request):
    """
    GET /api/statistics/
    Get database statistics including fingerprint count and template information
    """
    stats = FirebaseService.get_database_statistics()
    
    if isinstance(stats, dict) and "error" in stats:
        return JsonResponse(stats, status=500)
    
    return JsonResponse({
        "success": True,
        "data": stats
    })
