#ifndef CONFIG_H
#define CONFIG_H

// ====================================
// OPERATION MODE CONFIGURATION
// ====================================
// Uncomment ONLY ONE mode at a time
// ====================================

#define MODE_VERIFY     // Fingerprint verification/voting mode
// #define MODE_ENROLL  // Fingerprint enrollment mode
// #define MODE_DELETE  // Fingerprint deletion mode
// #define MODE_CLOUD   // Cloud-synced voting with Firebase

// ====================================
// HARDWARE CONFIGURATION
// ====================================

// LCD Configuration
#define LCD_ADDRESS 0x27
#define LCD_COLS 16
#define LCD_ROWS 2

// Buzzer Configuration
#define BUZZER_PIN 25

// Fingerprint Sensor Configuration
#define FINGERPRINT_SERIAL Serial2
#define FINGERPRINT_BAUDRATE 57600

// ====================================
// ENROLLMENT CONFIGURATION (for MODE_ENROLL)
// ====================================
#define ENROLL_START_ID 1    // Starting ID for enrollment
#define ENROLL_COUNT 10      // Number of fingerprints to enroll in sequence
// Or set ENROLL_MANUAL to true to enter ID via Serial Monitor
#define ENROLL_MANUAL false  // Set to true for manual ID entry

// ====================================
// DELETION CONFIGURATION (for MODE_DELETE)
// ====================================
#define DELETE_ID 1          // Specific ID to delete
// Or set DELETE_MANUAL to true to enter ID via Serial Monitor
#define DELETE_MANUAL true   // Set to true for manual ID entry
#define DELETE_ALL false     // Set to true to delete all fingerprints

// ====================================
// VERIFICATION CONFIGURATION (for MODE_VERIFY)
// ====================================
#define VERIFY_CONFIDENCE_THRESHOLD 50  // Minimum confidence score

// ====================================
// CLOUD/FIREBASE CONFIGURATION (for MODE_CLOUD)
// ====================================
#define WIFI_SSID "YOUR_WIFI_SSID"           // Your WiFi network name
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"   // Your WiFi password

// Firebase Cloud Function URL (replace with your actual URL)
#define CLOUD_FUNCTION_URL "https://YOUR_REGION-YOUR_PROJECT.cloudfunctions.net/evmHandler"

// Cloud features
#define CLOUD_UPLOAD_TEMPLATES false         // Upload templates to cloud (limited by R307)
#define CLOUD_VOTE_TRACKING true             // Track votes in Firestore
#define CLOUD_PREVENT_DOUBLE_VOTING true     // Check cloud for existing votes
#define CLOUD_REAL_TIME_COUNT true           // Show real-time vote count

// Station configuration for cloud mode
#define STATION_LOCATION "Station_A"         // This station's identifier

#endif
