"""
Mock Firebase service for testing backend endpoints without Firebase credentials
"""

class MockFirebaseService:
    """Mock Firebase service that simulates Firebase operations"""
    
    # In-memory storage for testing
    _enrolled_templates = {}
    
    @classmethod
    def enroll_fingerprint(cls, template_id, template_data, template_size):
        """Mock enrollment - stores in memory"""
        try:
            # Simulate successful enrollment
            cls._enrolled_templates[template_id] = {
                'data': template_data,
                'size': template_size,
                'enrolled_at': '2025-11-15T13:20:00Z'
            }
            
            return {
                'success': True,
                'template_id': template_id,
                'firebase_key': f'mock_key_{template_id}'
            }
            
        except Exception as e:
            return {'error': f'Mock enrollment error: {str(e)}'}
    
    @classmethod
    def verify_fingerprint_esp32(cls, template_data, threshold=80):
        """Mock verification - checks against stored templates"""
        try:
            # Simulate fingerprint matching
            for template_id, stored_template in cls._enrolled_templates.items():
                if stored_template['data'] == template_data:
                    return {
                        'match_found': True,
                        'fingerprint_id': template_id,
                        'confidence': 95.5,
                        'threshold_used': threshold
                    }
            
            # No match found
            return {
                'match_found': False,
                'fingerprint_id': None,
                'confidence': 0,
                'threshold_used': threshold
            }
            
        except Exception as e:
            return {'error': f'Mock verification error: {str(e)}'}
    
    @classmethod
    def get_template_count(cls):
        """Mock get count of enrolled templates"""
        return len(cls._enrolled_templates)
    
    @classmethod
    def clear_all_templates(cls):
        """Clear all stored templates (for testing)"""
        cls._enrolled_templates.clear()

# Replace the Firebase service with mock for testing
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Monkey patch the Firebase service
import firebase_service
firebase_service.FirebaseService = MockFirebaseService

print("✓ Mock Firebase service loaded for testing")