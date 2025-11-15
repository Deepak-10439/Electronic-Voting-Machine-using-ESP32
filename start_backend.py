#!/usr/bin/env python
"""
Django Backend Server Starter
Run this script to start the EVM Backend server
"""

import os
import sys
import subprocess

def start_server():
    """Start the Django development server"""
    print("🚀 Starting EVM Backend Server...")
    print("=" * 50)
    
    # Check if virtual environment exists
    if not os.path.exists('venv'):
        print("❌ Virtual environment not found!")
        print("Please run setup.ps1 first to install dependencies")
        return
    
    # Check if Firebase credentials exist
    if not os.path.exists('firebase-credentials.json'):
        print("⚠️  Warning: firebase-credentials.json not found")
        print("Please add your Firebase credentials file")
        print("See FIREBASE_CREDENTIALS_HELP.md for instructions")
        print()
    
    try:
        # Activate virtual environment and start server
        if os.name == 'nt':  # Windows
            python_path = os.path.join('venv', 'Scripts', 'python.exe')
        else:  # Unix/Linux/MacOS
            python_path = os.path.join('venv', 'bin', 'python')
        
        print("🔥 Starting Django server on http://0.0.0.0:8000")
        print("📱 ESP32 can connect from any device on the network")
        print("🛑 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Start Django server accessible from network
        subprocess.run([
            python_path, 'manage.py', 'runserver', '0.0.0.0:8000'
        ])
        
    except KeyboardInterrupt:
        print("\n✅ Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    start_server()