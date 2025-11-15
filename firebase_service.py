"""
Firebase Service Module
Handles all Firebase Realtime Database operations
"""

import firebase_admin
from firebase_admin import credentials, db
import os
from django.conf import settings


class FirebaseService:
    """Service class to interact with Firebase Realtime Database"""
    
    _initialized = False
    _db_ref = None
    
    @classmethod
    def initialize(cls):
        """Initialize Firebase Admin SDK"""
        if cls._initialized:
            return
        
        try:
            # Check if credentials file exists
            cred_path = settings.FIREBASE_CREDENTIALS_PATH
            database_url = settings.FIREBASE_DATABASE_URL
            
            if not os.path.exists(cred_path):
                print(f"Warning: Firebase credentials file not found at {cred_path}")
                print("Please add your firebase-credentials.json file")
                return
            
            if not database_url:
                print("Warning: FIREBASE_DATABASE_URL not set in environment variables")
                return
            
            # Initialize the app
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })
            
            cls._db_ref = db.reference()
            cls._initialized = True
            print("Firebase initialized successfully!")
            
        except Exception as e:
            print(f"Error initializing Firebase: {str(e)}")
            cls._initialized = False
    
    @classmethod
    def get_fingerprint_count(cls):
        """Get the count of enrolled fingerprints"""
        cls.initialize()
        
        if not cls._initialized:
            return {"error": "Firebase not initialized"}
        
        try:
            count_ref = cls._db_ref.child('fingerprints/count')
            count = count_ref.get()
            
            if count is None:
                return 0
            
            return count
        
        except Exception as e:
            return {"error": str(e)}
    
    @classmethod
    def get_all_fingerprint_templates(cls):
        """Retrieve all fingerprint templates from Firebase"""
        cls.initialize()
        
        if not cls._initialized:
            return {"error": "Firebase not initialized"}
        
        try:
            fingerprints_ref = cls._db_ref.child('fingerprints')
            fingerprints = fingerprints_ref.get()
            
            if fingerprints is None:
                return []
            
            # Convert to list format
            templates_list = []
            for key, value in fingerprints.items():
                if key == 'count':
                    continue  # Skip the count field
                
                if isinstance(value, dict):
                    template_data = {
                        'template_key': key,
                        'id': value.get('id'),
                        'size': value.get('size'),
                        'data': value.get('data'),
                        'data_length': len(value.get('data', '').split(',')) if value.get('data') else 0
                    }
                    templates_list.append(template_data)
            
            return templates_list
        
        except Exception as e:
            return {"error": str(e)}
    
    @classmethod
    def get_fingerprint_template_by_id(cls, template_id):
        """Retrieve a specific fingerprint template by ID"""
        cls.initialize()
        
        if not cls._initialized:
            return {"error": "Firebase not initialized"}
        
        try:
            # Search for template with matching ID
            fingerprints_ref = cls._db_ref.child('fingerprints')
            fingerprints = fingerprints_ref.get()
            
            if not fingerprints:
                return {"error": "Template not found"}
            
            for key, value in fingerprints.items():
                if key == 'count':
                    continue
                
                if isinstance(value, dict) and value.get('id') == template_id:
                    template_data = {
                        'template_key': key,
                        'id': value.get('id'),
                        'size': value.get('size'),
                        'data': value.get('data'),
                        'data_length': len(value.get('data', '').split(',')) if value.get('data') else 0
                    }
                    return template_data
            
            return {"error": "Template not found"}
        
        except Exception as e:
            return {"error": str(e)}
    
    @classmethod
    def get_fingerprint_template_by_key(cls, template_key):
        """Retrieve a specific fingerprint template by its key (e.g., 'template_2')"""
        cls.initialize()
        
        if not cls._initialized:
            return {"error": "Firebase not initialized"}
        
        try:
            template_ref = cls._db_ref.child(f'fingerprints/{template_key}')
            template = template_ref.get()
            
            if template and isinstance(template, dict):
                template_data = {
                    'template_key': template_key,
                    'id': template.get('id'),
                    'size': template.get('size'),
                    'data': template.get('data'),
                    'data_length': len(template.get('data', '').split(',')) if template.get('data') else 0
                }
                return template_data
            else:
                return {"error": "Template not found"}
        
        except Exception as e:
            return {"error": str(e)}
    
    @classmethod
    def get_database_statistics(cls):
        """Get statistics about fingerprint templates"""
        cls.initialize()
        
        if not cls._initialized:
            return {"error": "Firebase not initialized"}
        
        try:
            count = cls.get_fingerprint_count()
            templates = cls.get_all_fingerprint_templates()
            
            if isinstance(count, dict) and "error" in count:
                return count
            
            if isinstance(templates, dict) and "error" in templates:
                return templates
            
            # Calculate statistics
            total_templates = len(templates) if isinstance(templates, list) else 0
            
            # Get template IDs
            template_ids = []
            total_data_size = 0
            
            for template in templates if isinstance(templates, list) else []:
                template_ids.append(template.get('id'))
                total_data_size += template.get('size', 0)
            
            return {
                "fingerprint_count": count,
                "total_templates_stored": total_templates,
                "template_ids": sorted(template_ids),
                "total_data_size_bytes": total_data_size,
                "average_template_size_bytes": total_data_size // total_templates if total_templates > 0 else 0
            }
        
        except Exception as e:
            return {"error": str(e)}
