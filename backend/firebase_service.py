"""
Firebase Service Module with Blockchain Integration
Handles all Firebase Realtime Database operations and blockchain recording
"""

import firebase_admin
from firebase_admin import credentials, db
import os
from datetime import datetime
from django.conf import settings
from blockchain import get_blockchain_instance, hash_template


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
    def compare_templates(cls, template1_data, template2_data, threshold=70):
        """
        Compare two fingerprint templates using fuzzy matching
        Returns similarity percentage (0-100)
        
        Args:
            template1_data: Comma-separated hex string
            template2_data: Comma-separated hex string
            threshold: Minimum similarity percentage to consider a match (default 70%)
        """
        try:
            # Convert comma-separated strings to lists
            bytes1 = template1_data.split(',')
            bytes2 = template2_data.split(',')
            
            # If lengths are different, they can't match
            if len(bytes1) != len(bytes2):
                return 0.0
            
            # Count matching bytes and similar bytes (within tolerance)
            exact_matches = 0
            similar_matches = 0
            total_bytes = len(bytes1)
            
            for b1, b2 in zip(bytes1, bytes2):
                try:
                    val1 = int(b1.strip(), 16) if b1.strip() else 0
                    val2 = int(b2.strip(), 16) if b2.strip() else 0
                    
                    if val1 == val2:
                        exact_matches += 1
                        similar_matches += 1
                    elif abs(val1 - val2) <= 15:  # Allow small variations (within ~6% of 255)
                        similar_matches += 1
                except ValueError:
                    # If conversion fails, treat as non-match
                    continue
            
            # Calculate weighted similarity (exact matches weight more)
            exact_weight = 0.7
            similar_weight = 0.3
            
            exact_similarity = (exact_matches / total_bytes) * 100
            similar_similarity = (similar_matches / total_bytes) * 100
            
            # Weighted final similarity
            final_similarity = (exact_similarity * exact_weight) + (similar_similarity * similar_weight)
            
            return round(final_similarity, 2)
            
        except Exception as e:
            print(f"Template comparison error: {e}")
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
    
    @classmethod
    def enroll_fingerprint(cls, template_id, template_data, template_size):
        """
        Enroll a new fingerprint template to Firebase
        
        Args:
            template_id: ID for the fingerprint template
            template_data: Comma-separated hex string
            template_size: Size of the template data
        
        Returns:
            Success status or error information
        """
        cls.initialize()
        
        if not cls._initialized:
            return {"error": "Firebase not initialized"}
        
        try:
            # Store template data
            template_key = f"template_{template_id}"
            template_ref = cls._db_ref.child(f'fingerprints/{template_key}')
            
            template_ref.set({
                'id': template_id,
                'data': template_data,
                'size': template_size,
                'enrolled_at': datetime.now().isoformat(),
                'status': 'active'
            })
            
            # Update count
            count_ref = cls._db_ref.child('fingerprints/count')
            current_count = count_ref.get() or 0
            count_ref.set(max(current_count, template_id))
            
            # Record enrollment in blockchain
            blockchain = get_blockchain_instance()
            template_hash = hash_template(template_data)
            tx_id = blockchain.record_enrollment(
                user_id=f"user_{template_id}",
                fingerprint_id=template_id,
                template_hash=template_hash,
                esp32_ip="unknown"  # Can be enhanced to capture actual IP
            )
            
            return {
                "success": True, 
                "template_id": template_id,
                "blockchain_tx": tx_id,
                "template_hash": template_hash
            }
        
        except Exception as e:
            return {"error": str(e)}
    
    @classmethod
    def verify_fingerprint_esp32(cls, template_data, threshold=65):
        """
        Verify fingerprint template sent from ESP32 against all enrolled templates
        
        Args:
            template_data: Comma-separated hex string from ESP32
            threshold: Minimum similarity percentage to consider a match (default 65%)
        
        Returns:
            Dictionary with match result and matched template ID
        """
        cls.initialize()
        
        if not cls._initialized:
            return {"error": "Firebase not initialized"}
        
        try:
            # Get all enrolled templates
            templates = cls.get_all_fingerprint_templates()
            if isinstance(templates, dict) and "error" in templates:
                return templates
            
            if not templates:
                return {
                    "match_found": False,
                    "message": "No enrolled templates to compare",
                    "matched_id": None
                }
            
            # Compare with each template
            best_match_id = None
            best_similarity = 0.0
            
            print(f"Comparing against {len(templates)} enrolled templates...")
            
            for template in templates:
                template_id = template.get('id')
                stored_data = template.get('data')
                similarity = cls.compare_templates(template_data, stored_data, threshold)
                
                print(f"Template ID {template_id}: {similarity}% similarity")
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match_id = template_id
            
            print(f"Best match: ID {best_match_id} with {best_similarity}% similarity")
            print(f"Threshold: {threshold}%")
            
            # Determine if match found
            match_found = best_similarity >= threshold
            
            # Record verification in blockchain
            blockchain = get_blockchain_instance()
            tx_id = blockchain.record_verification(
                fingerprint_id=best_match_id if match_found else 0,
                result=match_found,
                similarity=best_similarity,
                esp32_ip="unknown"  # Can be enhanced to capture actual IP
            )
            
            return {
                "match_found": match_found,
                "matched_id": best_match_id if match_found else None,
                "similarity": best_similarity,
                "threshold": threshold,
                "message": f"Match found! ID: {best_match_id}" if match_found else "No match found",
                "blockchain_tx": tx_id
            }
        
        except Exception as e:
            return {"error": str(e)}
