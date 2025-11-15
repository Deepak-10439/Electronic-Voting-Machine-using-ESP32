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
                "GET /api/fingerprints/key/<template_key>/": "Get fingerprint template by key (e.g., template_2)",
                "POST /api/fingerprints/enroll/": "Enroll new fingerprint template from ESP32"
            },
            "verification": {
                "GET /api/verification/template/": "Get the captured template for verification",
                "GET /api/verification/verify/": "Verify captured fingerprint against enrolled templates",
                "GET /api/verification/verify/?threshold=85": "Verify with custom threshold (0-100, default: 80)",
                "POST /api/verification/verify/": "Verify fingerprint template sent from ESP32"
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


@require_http_methods(["GET"])
def get_verification_template(request):
    """
    GET /api/verification/template/
    Get the captured fingerprint template for verification
    """
    template = FirebaseService.get_verification_template()
    
    if isinstance(template, dict) and "error" in template:
        return JsonResponse(template, status=404)
    
    return JsonResponse({
        "success": True,
        "data": template
    })


@require_http_methods(["GET", "POST"])
def verify_fingerprint(request):
    """
    GET /api/verification/verify/
    POST /api/verification/verify/
    
    Verify the captured fingerprint against all enrolled templates
    Optional query parameter: threshold (default: 80)
    
    Example: /api/verification/verify/?threshold=85
    """
    # Get threshold from query parameters or use default
    threshold = request.GET.get('threshold', 80)
    try:
        threshold = float(threshold)
        if threshold < 0 or threshold > 100:
            return JsonResponse({
                "success": False,
                "error": "Threshold must be between 0 and 100"
            }, status=400)
    except ValueError:
        return JsonResponse({
            "success": False,
            "error": "Invalid threshold value"
        }, status=400)
    
    # Perform verification
    result = FirebaseService.verify_fingerprint(threshold=threshold)
    
    if isinstance(result, dict) and "error" in result:
        return JsonResponse(result, status=500)
    
    return JsonResponse({
        "success": True,
        "verification_result": result
    })


@csrf_exempt
@require_http_methods(["POST"])
def enroll_fingerprint(request):
    """
    POST /api/fingerprints/enroll/
    Enroll a new fingerprint template sent from ESP32
    
    Expected JSON payload:
    {
        "id": 1,
        "data": "hex,string,comma,separated",
        "size": 534
    }
    """
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['id', 'data', 'size']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }, status=400)
        
        # Enroll fingerprint via Firebase service
        result = FirebaseService.enroll_fingerprint(
            template_id=data['id'],
            template_data=data['data'],
            template_size=data['size']
        )
        
        if isinstance(result, dict) and "error" in result:
            return JsonResponse({
                "success": False,
                "error": result["error"]
            }, status=500)
        
        return JsonResponse({
            "success": True,
            "message": f"Fingerprint ID {data['id']} enrolled successfully",
            "template_id": data['id']
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Invalid JSON in request body"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def verify_fingerprint_esp32(request):
    """
    POST /api/verification/verify/
    Verify fingerprint template sent from ESP32
    
    Expected JSON payload:
    {
        "data": "hex,string,comma,separated",
        "threshold": 80 (optional)
    }
    """
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        if 'data' not in data:
            return JsonResponse({
                "success": False,
                "error": "Missing required field: data"
            }, status=400)
        
        # Get threshold or use default
        threshold = data.get('threshold', 80)
        
        # Verify fingerprint via Firebase service
        result = FirebaseService.verify_fingerprint_esp32(
            template_data=data['data'],
            threshold=threshold
        )
        
        if isinstance(result, dict) and "error" in result:
            return JsonResponse({
                "success": False,
                "error": result["error"]
            }, status=500)
        
        return JsonResponse({
            "success": True,
            "verification_result": result
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Invalid JSON in request body"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)
