"""
Test script to verify Django backend setup and Firebase connection
Run this after setting up the backend to check if everything is working
"""

import os
import sys

def test_imports():
    """Test if all required packages are installed"""
    print("Testing package imports...")
    try:
        import django
        print(f"✓ Django {django.get_version()} installed")
    except ImportError:
        print("✗ Django not installed")
        return False
    
    try:
        import rest_framework
        print(f"✓ Django REST Framework installed")
    except ImportError:
        print("✗ Django REST Framework not installed")
        return False
    
    try:
        import firebase_admin
        print(f"✓ Firebase Admin SDK installed")
    except ImportError:
        print("✗ Firebase Admin SDK not installed")
        return False
    
    try:
        from dotenv import load_dotenv
        print(f"✓ python-dotenv installed")
    except ImportError:
        print("✗ python-dotenv not installed")
        return False
    
    return True


def test_env_file():
    """Check if .env file exists"""
    print("\nTesting environment configuration...")
    if os.path.exists('.env'):
        print("✓ .env file exists")
        return True
    else:
        print("✗ .env file not found. Copy .env.example to .env")
        return False


def test_firebase_credentials():
    """Check if Firebase credentials file exists"""
    print("\nTesting Firebase credentials...")
    if os.path.exists('firebase-credentials.json'):
        print("✓ firebase-credentials.json exists")
        return True
    else:
        print("✗ firebase-credentials.json not found")
        print("  Download it from Firebase Console → Project Settings → Service Accounts")
        return False


def test_django_settings():
    """Test if Django settings can be loaded"""
    print("\nTesting Django settings...")
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
        import django
        django.setup()
        print("✓ Django settings loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Error loading Django settings: {str(e)}")
        return False


def test_firebase_connection():
    """Test Firebase connection"""
    print("\nTesting Firebase connection...")
    try:
        from firebase_service import FirebaseService
        FirebaseService.initialize()
        
        if FirebaseService._initialized:
            print("✓ Firebase initialized successfully")
            print("\nTrying to fetch data...")
            
            # Try to get votes
            votes = FirebaseService.get_all_votes()
            if isinstance(votes, list):
                print(f"✓ Successfully retrieved {len(votes)} votes")
            elif isinstance(votes, dict) and "error" not in votes:
                print("✓ Firebase connection working (no votes yet)")
            else:
                print(f"⚠ Warning: {votes}")
            
            return True
        else:
            print("✗ Firebase initialization failed")
            print("  Check your FIREBASE_DATABASE_URL in .env")
            return False
    except Exception as e:
        print(f"✗ Error testing Firebase: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("EVM Django Backend - Setup Verification")
    print("=" * 60)
    print()
    
    tests = [
        ("Package Imports", test_imports),
        ("Environment File", test_env_file),
        ("Firebase Credentials", test_firebase_credentials),
        ("Django Settings", test_django_settings),
        ("Firebase Connection", test_firebase_connection),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Unexpected error in {name}: {str(e)}")
            results.append((name, False))
        print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print()
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Your backend is ready to use.")
        print("\nStart the server with: python manage.py runserver")
    else:
        print("\n⚠ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Create .env file: copy .env.example .env")
        print("3. Add firebase-credentials.json from Firebase Console")
        print("4. Set FIREBASE_DATABASE_URL in .env")
    
    return passed == total


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
