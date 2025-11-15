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
    
    @classmethod
    def get_verification_template(cls):
        """Get the captured template for verification"""
        cls.initialize()
        
        if not cls._initialized:
            return {"error": "Firebase not initialized"}
        
        try:
            verify_ref = cls._db_ref.child('verification/captured_template')
            template = verify_ref.get()
            
            if template:
                return {
                    "data": template,
                    "data_length": len(template.split(',')) if template else 0
                }
            else:
                return {"error": "No verification template found"}
        
        except Exception as e:
            return {"error": str(e)}
    
    @classmethod
    def compare_templates(cls, template1_data, template2_data, threshold=80):
        """
        Compare two fingerprint templates
        Returns similarity percentage (0-100)
        
        Args:
            template1_data: Comma-separated hex string
            template2_data: Comma-separated hex string
            threshold: Minimum similarity percentage to consider a match (default 80%)
        """
        try:
            # Convert comma-separated strings to lists
            bytes1 = template1_data.split(',')
            bytes2 = template2_data.split(',')
            
            # If lengths are different, they can't match
            if len(bytes1) != len(bytes2):
                return 0.0
            
            # Count matching bytes
            matches = sum(1 for b1, b2 in zip(bytes1, bytes2) if b1.strip() == b2.strip())
            
            # Calculate similarity percentage
            similarity = (matches / len(bytes1)) * 100
            
            return round(similarity, 2)
        
        except Exception as e:
            return 0.0
    
    @classmethod
    def verify_fingerprint(cls, threshold=80):
        """
        Verify the captured template against all enrolled templates
        
        Args:
            threshold: Minimum similarity percentage to consider a match (default 80%)
        
        Returns:
            Dictionary with match result, matched template info, and similarity scores
        """
        cls.initialize()
        
        if not cls._initialized:
            return {"error": "Firebase not initialized"}
        
        try:
            # Get verification template
            verify_template = cls.get_verification_template()
            if isinstance(verify_template, dict) and "error" in verify_template:
                return verify_template
            
            verify_data = verify_template.get('data')
            
            # Get all enrolled templates
            templates = cls.get_all_fingerprint_templates()
            if isinstance(templates, dict) and "error" in templates:
                return templates
            
            if not templates:
                return {
                    "match_found": False,
                    "message": "No enrolled templates to compare",
                    "comparisons": []
                }
            
            # Compare with each template
            comparisons = []
            best_match = None
            best_similarity = 0.0
            
            for template in templates:
                template_data = template.get('data')
                similarity = cls.compare_templates(verify_data, template_data, threshold)
                
                comparison = {
                    "template_id": template.get('id'),
                    "template_key": template.get('template_key'),
                    "similarity_percentage": similarity,
                    "is_match": similarity >= threshold
                }
                comparisons.append(comparison)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = template
            
            # Determine if any match found
            match_found = best_similarity >= threshold
            
            result = {
                "match_found": match_found,
                "threshold_used": threshold,
                "best_match": {
                    "template_id": best_match.get('id') if best_match else None,
                    "template_key": best_match.get('template_key') if best_match else None,
                    "similarity_percentage": best_similarity
                } if match_found else None,
                "message": f"Match found! ID: {best_match.get('id')}" if match_found else "No match found",
                "all_comparisons": sorted(comparisons, key=lambda x: x['similarity_percentage'], reverse=True)
            }
            
            return result
        
        except Exception as e:
            return {"error": str(e)}
