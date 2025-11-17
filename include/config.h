#ifndef CONFIG_H
#define CONFIG_H

// WiFi Credentials
#define WIFI_SSID "Deepak"
#define WIFI_PASSWORD "12345678"

// Backend Configuration
#define BACKEND_URL "https://swift-habitat-475216-n3.uc.r.appspot.com"

// Blockchain Configuration (uses same backend URL)
#define BLOCKCHAIN_URL "https://swift-habitat-475216-n3.uc.r.appspot.com"

// Firebase Configuration
// Complete Firebase config from Firebase Console > Project Settings

#define API_KEY "AIzaSyASWue0f3MB7qNkNYEaHTROPXGIE_lR9wQ"
#define DATABASE_URL "https://fingerprint-evm-default-rtdb.asia-southeast1.firebasedatabase.app/"
#define FIREBASE_PROJECT_ID "fingerprint-evm"
#define FIREBASE_AUTH_DOMAIN "fingerprint-evm.firebaseapp.com"

// Optional: Database secret for legacy auth (can be empty if using API key)
#define FIREBASE_AUTH ""

#endif