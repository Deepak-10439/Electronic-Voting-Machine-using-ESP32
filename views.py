"""
API Views for EVM Backend
Handles HTTP requests and returns JSON responses
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from firebase_service import FirebaseService
from datetime import datetime
import json


def index(request):
    """Root endpoint - API information"""
    return JsonResponse({
        "message": "EVM Fingerprint Backend API with Blockchain",
        "version": "2.0.0",
        "database": "Firebase Realtime Database",
        "blockchain": "Enabled - Proof of Work",
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
            "blockchain": {
                "GET /api/blockchain/info/": "Get blockchain statistics and information",
                "GET /api/blockchain/audit/": "Get complete audit trail of transactions",
                "GET /api/blockchain/audit/?type=ENROLLMENT": "Filter audit trail by transaction type",
                "GET /api/blockchain/audit/?limit=10": "Limit number of audit results",
                "GET /api/blockchain/validate/": "Validate blockchain integrity",
                "POST /api/blockchain/vote/": "Record a vote in the blockchain"
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


# Blockchain API Endpoints

@require_http_methods(["GET"])
def get_blockchain_info(request):
    """
    GET /api/blockchain/info/
    Get blockchain statistics and information
    """
    try:
        from blockchain import get_blockchain_instance
        blockchain = get_blockchain_instance()
        
        info = blockchain.get_chain_info()
        return JsonResponse({
            "success": True,
            "blockchain_info": info
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_audit_trail(request):
    """
    GET /api/blockchain/audit/
    Get complete audit trail of all transactions
    Optional query parameters:
    - type: Filter by transaction type (ENROLLMENT, VERIFICATION, VOTE)
    - limit: Limit number of results
    """
    try:
        from blockchain import get_blockchain_instance
        blockchain = get_blockchain_instance()
        
        transaction_type = request.GET.get('type')
        limit = request.GET.get('limit')
        
        transactions = blockchain.get_transaction_history(transaction_type)
        
        # Apply limit if specified
        if limit:
            try:
                limit = int(limit)
                transactions = transactions[-limit:]  # Get latest transactions
            except ValueError:
                pass
        
        return JsonResponse({
            "success": True,
            "transactions": transactions,
            "total_count": len(transactions)
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@require_http_methods(["GET"])
def validate_blockchain(request):
    """
    GET /api/blockchain/validate/
    Validate the integrity of the entire blockchain
    """
    try:
        from blockchain import get_blockchain_instance
        blockchain = get_blockchain_instance()
        
        is_valid = blockchain.validate_chain()
        chain_info = blockchain.get_chain_info()
        
        return JsonResponse({
            "success": True,
            "blockchain_valid": is_valid,
            "chain_info": chain_info
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def submit_vote(request):
    """
    POST /api/vote/
    Submit a vote to the backend database
    
    Expected JSON payload:
    {
        "voterId": 2,
        "candidate": "USAR"
    }
    """
    if request.method != 'POST':
        return JsonResponse({
            "success": False,
            "error": "Method not allowed"
        }, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['voterId', 'candidate']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }, status=400)
        
        voter_id = data['voterId']
        candidate = data['candidate']
        
        # Validate candidate
        valid_candidates = ['USAR', 'USAP', 'USDI']
        if candidate not in valid_candidates:
            return JsonResponse({
                "success": False,
                "error": f"Invalid candidate. Must be one of: {valid_candidates}"
            }, status=400)
        
        # Here you would typically save to your database
        # For now, we'll just log and return success
        print(f"Vote recorded: Voter ID {voter_id} voted for {candidate}")
        
        return JsonResponse({
            "success": True,
            "message": "Vote recorded successfully",
            "voterId": voter_id,
            "candidate": candidate,
            "timestamp": datetime.now().isoformat()
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
def record_vote(request):
    """
    POST /api/blockchain/vote/
    Record a vote in the blockchain (for future voting functionality)
    
    Expected JSON payload:
    {
        "user_id": "user_123",
        "vote_choice": "candidate_a",
        "election_id": "election_2024"
    }
    """
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['user_id', 'vote_choice', 'election_id']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }, status=400)
        
        from blockchain import get_blockchain_instance
        blockchain = get_blockchain_instance()
        
        tx_id = blockchain.record_voting_event(
            user_id=data['user_id'],
            vote_choice=data['vote_choice'],
            election_id=data['election_id']
        )
        
        return JsonResponse({
            "success": True,
            "message": "Vote recorded in blockchain",
            "transaction_id": tx_id
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
