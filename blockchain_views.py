# Blockchain API endpoints to add to views.py

# Add these to the end of views.py file

from datetime import datetime

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