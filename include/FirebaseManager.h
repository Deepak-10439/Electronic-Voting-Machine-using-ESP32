#ifndef FIREBASE_MANAGER_H
#define FIREBASE_MANAGER_H

#include <Arduino.h>
#include <WiFi.h>
#include <Firebase.h>
#include <Adafruit_Fingerprint.h>
#include "config.h"

// Define Firebase Data object
FirebaseData firebaseData;

class FirebaseManager {
private:
    FirebaseAuth auth;
    FirebaseConfig config;
    bool initialized = false;
    
public:
    FirebaseManager() {}
    
    bool initWiFi() {
        Serial.print("Connecting to WiFi");
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
        
        int attempts = 0;
        while (WiFi.status() != WL_CONNECTED && attempts < 20) {
            delay(500);
            Serial.print(".");
            attempts++;
        }
        
        if (WiFi.status() == WL_CONNECTED) {
            Serial.println("\nWiFi Connected!");
            Serial.print("IP Address: ");
            Serial.println(WiFi.localIP());
            return true;
        }
        Serial.println("\nWiFi Connection Failed!");
        return false;
    }
    
    bool initFirebase() {
        Serial.println("\n=== Initializing Firebase ===");
        
        // Configure API Key (required for new Firebase SDK)
        config.api_key = API_KEY;
        Serial.print("API Key: ");
        Serial.println(API_KEY);
        
        // Configure the database URL
        config.database_url = DATABASE_URL;
        Serial.print("Database URL: ");
        Serial.println(DATABASE_URL);
        
        // Configure authentication
        if (strlen(FIREBASE_AUTH) > 0) {
            config.signer.tokens.legacy_token = FIREBASE_AUTH;
            Serial.println("Auth: Using database secret");
        } else {
            Serial.println("Auth: Anonymous sign-in");
            Serial.println("⚠ Ensure Firebase Authentication has Anonymous enabled");
            Serial.println("⚠ And Realtime Database rules allow access:");
            Serial.println("   {\"rules\": {\".read\": true, \".write\": true}}");
            
            // Sign in anonymously
            auth.user.email = "";
            auth.user.password = "";
        }
        
        // Set timeouts
        config.timeout.serverResponse = 10 * 1000;
        config.timeout.rtdbKeepAlive = 45 * 1000;
        config.timeout.rtdbStreamReconnect = 1 * 1000;
        config.timeout.rtdbStreamError = 3 * 1000;
        
        // Assign the callback function for token generation
        config.token_status_callback = nullptr;
        
        // Initialize Firebase with config
        Serial.println("Calling Firebase.begin()...");
        Firebase.begin(&config, &auth);
        Firebase.reconnectWiFi(true);
        
        // Sign up anonymously if no auth token
        if (strlen(FIREBASE_AUTH) == 0) {
            Serial.println("Signing in anonymously...");
            if (Firebase.signUp(&config, &auth, "", "")) {
                Serial.println("✓ Anonymous sign-in successful");
            } else {
                Serial.print("✗ Anonymous sign-in failed: ");
                Serial.println(config.signer.signupError.message.c_str());
            }
        }
        
        // Wait for Firebase to be ready
        Serial.println("Waiting for token generation...");
        unsigned long startWait = millis();
        while (!Firebase.ready() && (millis() - startWait) < 10000) {
            delay(100);
        }
        
        if (Firebase.ready()) {
            Serial.println("✓ Firebase is ready!");
        } else {
            Serial.println("⚠ Firebase not ready after timeout");
        }
        
        delay(1000);
        Serial.println("Testing Firebase connection...");
        
        // Test with a simple write
        String testPath = "/test/connection";
        if (Firebase.RTDB.setInt(&firebaseData, testPath.c_str(), 1)) {
            Serial.println("✓ Firebase connection successful!");
            Firebase.RTDB.deleteNode(&firebaseData, "/test");
            initialized = true;
            Serial.println("============================\n");
            return true;
        } else {
            Serial.println("✗ Firebase connection failed!");
            Serial.print("Error: ");
            Serial.println(firebaseData.errorReason());
            Serial.println("\n⚠ Troubleshooting:");
            Serial.println("1. Check API Key in config.h");
            Serial.println("2. Go to Firebase Console > Realtime Database");
            Serial.println("3. Click on 'Rules' tab");
            Serial.println("4. Set rules to:");
            Serial.println("   {");
            Serial.println("     \"rules\": {");
            Serial.println("       \".read\": true,");
            Serial.println("       \".write\": true");
            Serial.println("     }");
            Serial.println("   }");
            Serial.println("5. Click 'Publish'");
            Serial.println("============================\n");
            initialized = false;
            return false;
        }
    }
    
    bool isInitialized() {
        return initialized;
    }
    
    bool uploadTemplate(uint16_t id, Adafruit_Fingerprint* finger) {
        Serial.println("Getting template from sensor...");
        
        uint8_t p = finger->loadModel(id);
        if (p != FINGERPRINT_OK) {
            Serial.println("Failed to load model");
            return false;
        }
        
        // Get the template - this downloads it to the serial connection
        Serial.println("Downloading template...");
        uint8_t bytesReceived[534]; // Template packet is 534 bytes
        memset(bytesReceived, 0xff, 534);
        
        p = finger->getModel();
        if (p == FINGERPRINT_OK) {
            Serial.println("Template received");
        } else {
            Serial.println("Failed to transfer template");
            return false;
        }
        
        // Read the template data from Serial2
        int idx = 0;
        unsigned long startTime = millis();
        while (idx < 534 && (millis() - startTime) < 5000) {
            if (Serial2.available()) {
                bytesReceived[idx++] = Serial2.read();
            }
        }
        
        Serial.print("Received ");
        Serial.print(idx);
        Serial.println(" bytes");
        
        // Convert to comma-separated hex string for Firebase
        String templateData = "";
        for (int i = 0; i < idx; i++) {
            if (i > 0) templateData += ",";
            templateData += String(bytesReceived[i], HEX);
        }
        
        // Upload to Firebase
        String path = "/fingerprints/template_" + String(id);
        
        if (Firebase.RTDB.setString(&firebaseData, path + "/data", templateData)) {
            Serial.println("Template uploaded to Firebase!");
            Firebase.RTDB.setInt(&firebaseData, path + "/id", id);
            Firebase.RTDB.setInt(&firebaseData, path + "/size", idx);
            return true;
        } else {
            Serial.println("Failed to upload template");
            Serial.println(firebaseData.errorReason());
            return false;
        }
    }
    
    int cloudVerify(Adafruit_Fingerprint* finger, int maxTemplates = 100) {
        Serial.println("\n=== Fast Local Verification ===");
        Serial.println("Converting captured image to template...");
        
        // Convert the captured image to a template in slot 1
        uint8_t p = finger->image2Tz(1);
        if (p != FINGERPRINT_OK) {
            Serial.println("✗ Failed to convert image");
            Serial.print("Error code: ");
            Serial.println(p);
            return -1;
        }
        Serial.println("✓ Template created in slot 1");
        
        // Download templates from Firebase and verify locally using sensor's matching
        Serial.println("\nDownloading templates from Firebase for local matching...");
        int matchedID = -1;
        int templatesChecked = 0;
        
        for (int id = 1; id <= maxTemplates; id++) {
            String pathData = "/fingerprints/template_" + String(id) + "/data";
            String pathSize = "/fingerprints/template_" + String(id) + "/size";
            
            // Check if template exists
            if (Firebase.RTDB.getString(&firebaseData, pathData)) {
                String templateData = firebaseData.stringData();
                
                if (templateData.length() > 10) {
                    templatesChecked++;
                    Serial.print("  [");
                    Serial.print(templatesChecked);
                    Serial.print("] Checking ID #");
                    Serial.print(id);
                    Serial.print("... ");
                    
                    // Get template size
                    int templateSize = 534;
                    if (Firebase.RTDB.getInt(&firebaseData, pathSize)) {
                        templateSize = firebaseData.intData();
                    }
                    
                    // Convert hex string back to bytes
                    uint8_t templateBuffer[534];
                    int bufferIndex = 0;
                    int startIndex = 0;
                    
                    for (int i = 0; i <= templateData.length() && bufferIndex < templateSize; i++) {
                        if (i == templateData.length() || templateData[i] == ',') {
                            String hexByte = templateData.substring(startIndex, i);
                            templateBuffer[bufferIndex++] = (uint8_t)strtol(hexByte.c_str(), NULL, 16);
                            startIndex = i + 1;
                        }
                    }
                    
                    // Load template into temporary slot 200
                    Serial2.write(templateBuffer, bufferIndex);
                    delay(100);
                    
                    // Store in slot 200
                    p = finger->storeModel(200);
                    if (p == FINGERPRINT_OK) {
                        // Load from slot 200
                        p = finger->loadModel(200);
                        if (p == FINGERPRINT_OK) {
                            // Convert to CharBuffer2
                            p = finger->image2Tz(2);
                            
                            if (p == FINGERPRINT_OK) {
                                // Create model and compare with slot 1
                                p = finger->createModel();
                                
                                if (p == FINGERPRINT_OK) {
                                    // Match found
                                    matchedID = id;
                                    Serial.println("✓ MATCH!");
                                    Serial.println("\n╔═══════════════════════════╗");
                                    Serial.println("║    ✓ MATCH FOUND!         ║");
                                    Serial.println("╠═══════════════════════════╣");
                                    Serial.print("║    ID: #");
                                    Serial.print(id);
                                    if (id < 10) Serial.print(" ");
                                    Serial.println("                  ║");
                                    Serial.println("╚═══════════════════════════╝\n");
                                    finger->deleteModel(200);
                                    break;
                                } else {
                                    Serial.println("No match");
                                }
                            }
                        }
                        finger->deleteModel(200);
                    } else {
                        Serial.println("Failed to store");
                    }
                }
            }
            
            delay(50);
        }
        
        if (matchedID == -1) {
            Serial.println("\n╔═══════════════════════════╗");
            Serial.println("║    ✗ NO MATCH FOUND       ║");
            Serial.println("╠═══════════════════════════╣");
            Serial.print("║    Templates checked: ");
            Serial.print(templatesChecked);
            if (templatesChecked < 10) Serial.print(" ");
            Serial.println("  ║");
            Serial.println("╚═══════════════════════════╝\n");
        }
        
        Serial.println("================================\n");
        return matchedID;
    }
    
    // Helper function to compare two template strings
    int compareTemplates(String template1, String template2) {
        if (template1.length() == 0 || template2.length() == 0) return 0;
        
        // Count matching bytes
        int matches = 0;
        int total = 0;
        
        int idx1 = 0, idx2 = 0;
        String byte1 = "", byte2 = "";
        
        while (idx1 < template1.length() && idx2 < template2.length()) {
            // Extract hex bytes
            int comma1 = template1.indexOf(',', idx1);
            int comma2 = template2.indexOf(',', idx2);
            
            if (comma1 == -1) comma1 = template1.length();
            if (comma2 == -1) comma2 = template2.length();
            
            byte1 = template1.substring(idx1, comma1);
            byte2 = template2.substring(idx2, comma2);
            
            if (byte1.equals(byte2)) {
                matches++;
            }
            total++;
            
            idx1 = comma1 + 1;
            idx2 = comma2 + 1;
        }
        
        if (total == 0) return 0;
        return (matches * 100) / total;
    }
    
    int getTemplateCount() {
        if (Firebase.RTDB.getInt(&firebaseData, "/fingerprints/count")) {
            return firebaseData.intData();
        }
        return 0;
    }
    
    void updateTemplateCount(int count) {
        Firebase.RTDB.setInt(&firebaseData, "/fingerprints/count", count);
    }
};

#endif
