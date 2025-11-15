#ifndef FIREBASE_MANAGER_H
#define FIREBASE_MANAGER_H

#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Adafruit_Fingerprint.h>
#include "config.h"

class FirebaseManager {
private:
    String backendUrl;
    bool initialized = false;
    
public:
    FirebaseManager() {
        // Set your Django backend URL here
        backendUrl = BACKEND_URL; // Define this in config.h
    }
    
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
        // Test backend connectivity instead of direct Firebase connection
        return testBackendConnection();
    }
    
    bool testBackendConnection() {
        Serial.println("\n=== Testing Backend Connection ===");
        Serial.print("Backend URL: ");
        Serial.println(backendUrl);
        
        HTTPClient http;
        http.begin(backendUrl + "/");
        http.addHeader("Content-Type", "application/json");
        http.setTimeout(10000);
        
        int httpResponseCode = http.GET();
        
        if (httpResponseCode > 0) {
            String response = http.getString();
            Serial.println("✓ Backend connection successful!");
            Serial.print("Response code: ");
            Serial.println(httpResponseCode);
            initialized = true;
            http.end();
            Serial.println("============================\n");
            return true;
        } else {
            Serial.println("✗ Backend connection failed!");
            Serial.print("Error code: ");
            Serial.println(httpResponseCode);
            Serial.println("\n⚠ Troubleshooting:");
            Serial.println("1. Check if Django backend is running");
            Serial.println("2. Verify backend URL in config.h");
            Serial.println("3. Check network connectivity");
            Serial.println("4. Ensure firewall allows connection");
            Serial.println("============================\n");
            initialized = false;
            http.end();
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
        
        // Convert to comma-separated hex string
        String templateData = "";
        for (int i = 0; i < idx; i++) {
            if (i > 0) templateData += ",";
            templateData += String(bytesReceived[i], HEX);
        }
        
        // Send to backend instead of Firebase
        return enrollToBackend(id, templateData, idx);
    }
    
    bool enrollToBackend(uint16_t id, String templateData, int templateSize) {
        Serial.println("\n=== Enrolling to Backend ===");
        Serial.print("Template ID: ");
        Serial.println(id);
        Serial.print("Data size: ");
        Serial.println(templateSize);
        
        HTTPClient http;
        http.begin(backendUrl + "/api/fingerprints/enroll/");
        http.addHeader("Content-Type", "application/json");
        http.setTimeout(30000); // 30 second timeout for large data
        
        // Create JSON payload
        DynamicJsonDocument doc(8192); // Increase size for template data
        doc["id"] = id;
        doc["data"] = templateData;
        doc["size"] = templateSize;
        
        String jsonString;
        serializeJson(doc, jsonString);
        
        Serial.println("Sending enrollment request...");
        int httpResponseCode = http.POST(jsonString);
        
        if (httpResponseCode == 200) {
            String response = http.getString();
            
            // Parse response
            DynamicJsonDocument responseDoc(1024);
            deserializeJson(responseDoc, response);
            
            bool success = responseDoc["success"];
            if (success) {
                Serial.println("✓ Template enrolled successfully via backend!");
                Serial.print("Message: ");
                Serial.println(responseDoc["message"].as<String>());
                http.end();
                return true;
            } else {
                Serial.println("✗ Backend enrollment failed");
                Serial.print("Error: ");
                Serial.println(responseDoc["error"].as<String>());
                http.end();
                return false;
            }
        } else {
            String response = http.getString();
            Serial.println("✗ Failed to enroll template via backend");
            Serial.print("HTTP Code: ");
            Serial.println(httpResponseCode);
            Serial.print("Response: ");
            Serial.println(response);
            http.end();
            return false;
        }
    }
    
    int cloudVerify(Adafruit_Fingerprint* finger, int maxTemplates = 100) {
        Serial.println("\n=== Backend Verification ===");
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
        
        // Get template from sensor
        Serial.println("Downloading template for verification...");
        uint8_t bytesReceived[534];
        memset(bytesReceived, 0xff, 534);
        
        // Store in temporary slot for download
        p = finger->storeModel(199);
        if (p != FINGERPRINT_OK) {
            Serial.println("Failed to store temporary template");
            return -1;
        }
        
        p = finger->loadModel(199);
        if (p != FINGERPRINT_OK) {
            Serial.println("Failed to load temporary template");
            finger->deleteModel(199);
            return -1;
        }
        
        p = finger->getModel();
        if (p != FINGERPRINT_OK) {
            Serial.println("Failed to get template");
            finger->deleteModel(199);
            return -1;
        }
        
        // Read template data
        int idx = 0;
        unsigned long startTime = millis();
        while (idx < 534 && (millis() - startTime) < 5000) {
            if (Serial2.available()) {
                bytesReceived[idx++] = Serial2.read();
            }
        }
        
        // Clean up temporary slot
        finger->deleteModel(199);
        
        if (idx < 100) {
            Serial.println("Failed to read sufficient template data");
            return -1;
        }
        
        Serial.print("Read ");
        Serial.print(idx);
        Serial.println(" bytes for verification");
        
        // Convert to hex string
        String templateData = "";
        for (int i = 0; i < idx; i++) {
            if (i > 0) templateData += ",";
            templateData += String(bytesReceived[i], HEX);
        }
        
        // Send to backend for verification
        return verifyWithBackend(templateData);
    }
    
    int verifyWithBackend(String templateData) {
        Serial.println("Sending verification data to backend...");
        
        HTTPClient http;
        http.begin(backendUrl + "/api/verification/verify/");
        http.addHeader("Content-Type", "application/json");
        http.setTimeout(30000); // 30 second timeout
        
        // Create JSON payload
        DynamicJsonDocument doc(8192);
        doc["data"] = templateData;
        doc["threshold"] = 80; // Set your desired threshold
        
        String jsonString;
        serializeJson(doc, jsonString);
        
        int httpResponseCode = http.POST(jsonString);
        
        if (httpResponseCode == 200) {
            String response = http.getString();
            
            // Parse response
            DynamicJsonDocument responseDoc(1024);
            deserializeJson(responseDoc, response);
            
            bool success = responseDoc["success"];
            if (success) {
                bool matchFound = responseDoc["verification_result"]["match_found"];
                if (matchFound) {
                    int matchedId = responseDoc["verification_result"]["matched_id"];
                    float similarity = responseDoc["verification_result"]["similarity"];
                    
                    Serial.println("✓ Verification successful via backend!");
                    Serial.print("Matched ID: ");
                    Serial.println(matchedId);
                    Serial.print("Similarity: ");
                    Serial.print(similarity);
                    Serial.println("%");
                    
                    http.end();
                    return matchedId;
                } else {
                    Serial.println("✗ No match found via backend");
                    Serial.print("Message: ");
                    Serial.println(responseDoc["verification_result"]["message"].as<String>());
                    http.end();
                    return -1;
                }
            } else {
                Serial.println("✗ Backend verification failed");
                Serial.print("Error: ");
                Serial.println(responseDoc["error"].as<String>());
                http.end();
                return -1;
            }
        } else {
            String response = http.getString();
            Serial.println("✗ Failed to verify with backend");
            Serial.print("HTTP Code: ");
            Serial.println(httpResponseCode);
            Serial.print("Response: ");
            Serial.println(response);
            http.end();
            return -1;
        }
    }
    
    int getTemplateCount() {
        HTTPClient http;
        http.begin(backendUrl + "/api/fingerprints/count/");
        http.setTimeout(10000);
        
        int httpResponseCode = http.GET();
        
        if (httpResponseCode == 200) {
            String response = http.getString();
            
            DynamicJsonDocument doc(1024);
            deserializeJson(doc, response);
            
            if (doc["success"]) {
                int count = doc["fingerprint_count"];
                http.end();
                return count;
            }
        }
        
        http.end();
        return 0;
    }
    
    void updateTemplateCount(int count) {
        // Count is automatically updated by backend during enrollment
        Serial.print("Template count updated: ");
        Serial.println(count);
    }
    
    void setBackendUrl(String url) {
        backendUrl = url;
    }
};

#endif