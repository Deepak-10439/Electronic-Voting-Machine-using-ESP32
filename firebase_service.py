"""
Firebase Service Module
Provides Firebase integration for fingerprint template storage and management
"""

import firebase_admin
from firebase_admin import credentials, db
import os
import json
from django.conf import settings


class FirebaseService:
    """Firebase service for fingerprint template management"""
    
    _initialized = False
    _db_ref = None
    
    @classmethod
    def _initialize_firebase(cls):
        """Initialize Firebase Admin SDK"""
        if cls._initialized:
            return
        
        try:
            # Check if Firebase app already exists
            firebase_admin.get_app()
        except ValueError:
            # Initialize Firebase with service account key
            cred_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
            
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': getattr(settings, 'FIREBASE_DATABASE_URL', '')
                })
            else:
                # For development, return mock data
                print(f"Warning: Firebase credentials not found at {cred_path}")
                return
        
        cls._db_ref = db.reference()
        cls._initialized = True
    
    @classmethod
    def get_all_fingerprint_templates(cls):
        """Get all fingerprint templates from Firebase"""
        cls._initialize_firebase()
        
        if not cls._initialized:
            return []
        
        try:
            templates_ref = cls._db_ref.child('fingerprints')
            templates = templates_ref.get()
            
            if templates:
                result = []
                for key, value in templates.items():
                    if key != 'count' and isinstance(value, dict):
                        result.append({
                            'key': key,
                            'id': value.get('id', 0),
                            'data': value.get('data', ''),
                            'size': value.get('size', 0)
                        })
                return result
            return []
        except Exception as e:
            return {"error": f"Failed to get templates: {str(e)}"}
    
    @classmethod
    def get_fingerprint_count(cls):
        """Get count of enrolled fingerprints"""
        cls._initialize_firebase()
        
        if not cls._initialized:
            return 0
        
        try:
            count_ref = cls._db_ref.child('fingerprints/count')
            count = count_ref.get()
            return count if count else 0
        except Exception as e:
            return {"error": f"Failed to get count: {str(e)}"}
    
    @classmethod
    def get_fingerprint_template_by_id(cls, template_id):
        """Get fingerprint template by ID"""
        cls._initialize_firebase()
        
        if not cls._initialized:
            return {"error": "Firebase not initialized"}
        
        try:
            templates = cls.get_all_fingerprint_templates()
            if isinstance(templates, dict) and "error" in templates:
                return templates
            
            for template in templates:
                if template.get('id') == template_id:
                    return template
            
            return {"error": f"Template with ID {template_id} not found"}
        except Exception as e:
            return {"error": f"Failed to get template: {str(e)}"}
    
    @classmethod
    def get_fingerprint_template_by_key(cls, template_key):
        """Get fingerprint template by key"""
        cls._initialize_firebase()
        
        if not cls._initialized:
            return {"error": "Firebase not initialized"}
        
        try:
            template_ref = cls._db_ref.child(f'fingerprints/{template_key}')
            template = template_ref.get()
            
            if template:
                return {
                    'key': template_key,
                    'id': template.get('id', 0),
                    'data': template.get('data', ''),
                    'size': template.get('size', 0)
                }
            
            return {"error": f"Template with key {template_key} not found"}
        except Exception as e:
            return {"error": f"Failed to get template: {str(e)}"}
    
    @classmethod
    def get_database_statistics(cls):
        """Get database statistics"""
        cls._initialize_firebase()
        
        if not cls._initialized:
            return {"error": "Firebase not initialized"}
        
        try:
            templates = cls.get_all_fingerprint_templates()
            if isinstance(templates, dict) and "error" in templates:
                return templates
            
            return {
                "total_templates": len(templates),
                "template_count": cls.get_fingerprint_count(),
                "templates": templates
            }
        except Exception as e:
            return {"error": f"Failed to get statistics: {str(e)}"}
    
    @classmethod
    def get_verification_template(cls):
        """Get verification template"""
        cls._initialize_firebase()
        
        if not cls._initialized:
            return {"error": "Firebase not initialized"}
        
        try:
            verify_ref = cls._db_ref.child('verification/captured_template')
            template = verify_ref.get()
            
            if template:
                return {"data": template}
            
            return {"error": "No verification template found"}
        except Exception as e:
            return {"error": f"Failed to get verification template: {str(e)}"}
    
    @classmethod
    def verify_fingerprint(cls, threshold=80):
        """Verify fingerprint against stored templates"""
        # This is a placeholder implementation
        # In a real scenario, you would implement fingerprint matching logic
        return {
            "matched": False,
            "template_id": None,
            "confidence": 0,
            "threshold": threshold
        }
    
    @classmethod
    def enroll_fingerprint(cls, template_id, template_data, template_size):
        """Enroll a new fingerprint template"""
        cls._initialize_firebase()
        
        if not cls._initialized:
            return {"error": "Firebase not initialized"}
        
        try:
            template_ref = cls._db_ref.child(f'fingerprints/template_{template_id}')
            template_ref.set({
                'id': template_id,
                'data': template_data,
                'size': template_size
            })
            
            # Update count
            count = cls.get_fingerprint_count()
            if not isinstance(count, dict):
                count_ref = cls._db_ref.child('fingerprints/count')
                count_ref.set(count + 1)
            
            return {"success": True, "template_id": template_id}
        except Exception as e:
            return {"error": f"Failed to enroll fingerprint: {str(e)}"}
    
    @classmethod
    def verify_fingerprint_esp32(cls, template_data, threshold=80):
        """Verify fingerprint template sent from ESP32"""
        # This is a placeholder implementation
        # In a real scenario, you would implement fingerprint matching logic
        return {
            "matched": False,
            "template_id": None,
            "confidence": 0,
            "threshold": threshold,
            "template_data_length": len(template_data) if template_data else 0
        }