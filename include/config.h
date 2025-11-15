#ifndef CONFIG_H
#define CONFIG_H

// WiFi Credentials
#define WIFI_SSID "Deepak"
#define WIFI_PASSWORD "12345678"

// Django Backend Configuration
#define BACKEND_URL "http://192.168.1.100:8000"  // Change to your server IP
#define ESP32_DEVICE_ID "ESP32_EVM_001"

// Legacy Firebase Configuration (for backup/migration)
// Complete Firebase config from Firebase Console > Project Settings
#define API_KEY "AIzaSyASWue0f3MB7qNkNYEaHTROPXGIE_lR9wQ"
#define DATABASE_URL "https://fingerprint-evm-default-rtdb.asia-southeast1.firebasedatabase.app/"
#define FIREBASE_PROJECT_ID "fingerprint-evm"
#define FIREBASE_AUTH_DOMAIN "fingerprint-evm.firebaseapp.com"

// Optional: Database secret for legacy auth (can be empty if using API key)
#define FIREBASE_AUTH ""

#endif