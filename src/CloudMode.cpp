#include <Arduino.h>
#include <Adafruit_Fingerprint.h>
#include "Config.h"
#include "FingerPrintManager.h"
#include "LCDManager.h"
#include "BuzzerManager.h"
#include "FirebaseManager.h"
#include "TemplateManager.h"

// Initialize hardware
extern Adafruit_Fingerprint finger;
extern LCDManager lcdManager;
extern BuzzerManager buzzerManager;
extern FingerPrintManager fpManager;

FirebaseManager firebaseManager;
TemplateManager templateManager(&finger);

bool cloudInitialized = false;
uint8_t currentEnrollID = 1;

void cloudMode_setup() {
    Serial.println("\n=== CLOUD MODE ===");
    Serial.println("Cloud-Synced Electronic Voting Machine");
    
    lcdManager.showWelcome();
    delay(1000);
    
    // Initialize WiFi and Firebase
    lcdManager.clear();
    lcdManager.print(0, 0, "Connecting WiFi");
    lcdManager.print(1, 0, "Please wait...");
    
    cloudInitialized = firebaseManager.initialize(WIFI_SSID, WIFI_PASSWORD, CLOUD_FUNCTION_URL);
    
    if (cloudInitialized) {
        lcdManager.clear();
        lcdManager.print(0, 0, "WiFi Connected!");
        lcdManager.print(1, 0, "Cloud Ready");
        buzzerManager.playSuccess();
        Serial.println("✓ Cloud mode initialized successfully");
        delay(2000);
    } else {
        lcdManager.clear();
        lcdManager.print(0, 0, "WiFi Failed!");
        lcdManager.print(1, 0, "Check config");
        buzzerManager.playError();
        Serial.println("✗ Cloud initialization failed");
        Serial.println("Check WiFi credentials in Config.h");
        delay(3000);
    }
    
    lcdManager.showSensorFound();
    
    uint16_t templateCount = fpManager.getTemplateCount();
    lcdManager.showTemplateCount(templateCount);
    Serial.print("Local sensor contains ");
    Serial.print(templateCount);
    Serial.println(" templates");
    
    if (cloudInitialized && CLOUD_REAL_TIME_COUNT) {
        int cloudVoteCount = firebaseManager.getTotalVoteCount();
        if (cloudVoteCount >= 0) {
            Serial.print("Cloud vote count: ");
            Serial.println(cloudVoteCount);
            lcdManager.clear();
            lcdManager.print(0, 0, "Cloud Votes:");
            lcdManager.print(1, 0, String(cloudVoteCount));
            delay(2000);
        }
    }
    
    // Show menu
    Serial.println("\n--- Cloud Mode Menu ---");
    Serial.println("1. Enroll with Cloud Sync");
    Serial.println("2. Verify with Cloud Sync");
    Serial.println("Enter choice (1 or 2):");
    
    lcdManager.clear();
    lcdManager.print(0, 0, "Cloud Mode");
    lcdManager.print(1, 0, "Serial: 1 or 2");
}

void cloudMode_enrollWithSync() {
    Serial.println("\n--- Cloud Enrollment ---");
    Serial.print("Enter Voter ID (e.g., VTR001): ");
    
    lcdManager.clear();
    lcdManager.print(0, 0, "Enter Voter ID");
    lcdManager.print(1, 0, "via Serial...");
    
    // Wait for Serial input
    while (!Serial.available()) {
        delay(100);
    }
    
    String voterId = Serial.readStringUntil('\n');
    voterId.trim();
    
    if (voterId.length() == 0) {
        Serial.println("Invalid Voter ID");
        return;
    }
    
    Serial.print("Enter Voter Name: ");
    lcdManager.clear();
    lcdManager.print(0, 0, "Enter Name");
    lcdManager.print(1, 0, "via Serial...");
    
    while (!Serial.available()) {
        delay(100);
    }
    
    String voterName = Serial.readStringUntil('\n');
    voterName.trim();
    
    if (voterName.length() == 0) {
        Serial.println("Invalid Name");
        return;
    }
    
    Serial.print("Enrolling: ");
    Serial.print(voterName);
    Serial.print(" (");
    Serial.print(voterId);
    Serial.println(")");
    
    lcdManager.showEnrollStart(currentEnrollID);
    delay(1000);
    
    // Enroll on local sensor
    uint8_t result = fpManager.enrollFingerprint(currentEnrollID);
    
    if (result == FINGERPRINT_OK) {
        Serial.print("✓ Enrolled locally as ID #");
        Serial.println(currentEnrollID);
        
        // Upload to cloud (without template data due to R307 limitations)
        if (cloudInitialized) {
            lcdManager.clear();
            lcdManager.print(0, 0, "Uploading to");
            lcdManager.print(1, 0, "Cloud...");
            
            bool uploaded = firebaseManager.uploadVoterRecord(
                voterId, 
                voterName, 
                currentEnrollID, 
                STATION_LOCATION
            );
            
            if (uploaded) {
                Serial.println("✓ Voter record uploaded to Firestore");
                lcdManager.showEnrollSuccess();
                buzzerManager.playSuccess();
                delay(1000);
                buzzerManager.playSuccess();
            } else {
                Serial.println("⚠️ Local enrollment OK, but cloud upload failed");
                lcdManager.clear();
                lcdManager.print(0, 0, "Local: OK");
                lcdManager.print(1, 0, "Cloud: Failed");
                buzzerManager.playError();
            }
        } else {
            lcdManager.showEnrollSuccess();
            buzzerManager.playSuccess();
        }
        
        currentEnrollID++;
        delay(2000);
    } else {
        Serial.println("✗ Enrollment failed");
        lcdManager.showEnrollFailed();
        buzzerManager.playError();
        delay(2000);
    }
}

void cloudMode_verifyWithSync() {
    lcdManager.showWaitingForFinger();
    
    uint8_t foundID = 0;
    uint16_t confidence = 0;
    
    uint8_t result = fpManager.verifyFingerprint(&foundID, &confidence);
    
    if (result == FINGERPRINT_OK) {
        Serial.print("Found ID #");
        Serial.print(foundID);
        Serial.print(" with confidence of ");
        Serial.println(confidence);
        
        if (confidence >= VERIFY_CONFIDENCE_THRESHOLD) {
            lcdManager.showFingerMatch(foundID, confidence);
            
            // Check cloud for double voting
            if (cloudInitialized && CLOUD_PREVENT_DOUBLE_VOTING) {
                lcdManager.clear();
                lcdManager.print(0, 0, "Checking cloud");
                lcdManager.print(1, 0, "Please wait...");
                
                // For this demo, we construct voter ID from sensor ID
                String voterId = "SENSOR_" + String(foundID);
                
                bool alreadyVoted = firebaseManager.hasVotedAlready(voterId);
                
                if (alreadyVoted) {
                    Serial.println("✗ Already voted!");
                    lcdManager.clear();
                    lcdManager.print(0, 0, "Already Voted!");
                    lcdManager.print(1, 0, "Access Denied");
                    buzzerManager.playError();
                    delay(3000);
                    lcdManager.showWaitingForFinger();
                    return;
                }
            }
            
            // Register vote
            Serial.println("✓ Vote Registered!");
            buzzerManager.playSuccess();
            
            // Update cloud
            if (cloudInitialized && CLOUD_VOTE_TRACKING) {
                lcdManager.clear();
                lcdManager.print(0, 0, "Updating cloud");
                lcdManager.print(1, 0, "Please wait...");
                
                String voterId = "SENSOR_" + String(foundID);
                bool updated = firebaseManager.updateVoteStatus(voterId, true);
                
                if (updated) {
                    Serial.println("✓ Vote recorded in cloud");
                    lcdManager.clear();
                    lcdManager.print(0, 0, "Vote Recorded!");
                    lcdManager.print(1, 0, "Thank you");
                } else {
                    Serial.println("⚠️ Local vote OK, cloud update failed");
                    lcdManager.clear();
                    lcdManager.print(0, 0, "Vote Counted");
                    lcdManager.print(1, 0, "Cloud: Offline");
                }
            } else {
                lcdManager.clear();
                lcdManager.print(0, 0, "Vote Counted!");
                lcdManager.print(1, 0, "Thank you");
            }
            
            delay(3000);
            
            // Show updated count
            if (cloudInitialized && CLOUD_REAL_TIME_COUNT) {
                int voteCount = firebaseManager.getTotalVoteCount();
                if (voteCount >= 0) {
                    lcdManager.clear();
                    lcdManager.print(0, 0, "Total Votes:");
                    lcdManager.print(1, 0, String(voteCount));
                    Serial.print("Total votes: ");
                    Serial.println(voteCount);
                    delay(2000);
                }
            }
            
            lcdManager.showWaitingForFinger();
        } else {
            Serial.println("✗ Low confidence, try again");
            lcdManager.showNoMatch();
            buzzerManager.playError();
            delay(2000);
            lcdManager.showWaitingForFinger();
        }
    } else if (result == FINGERPRINT_NOTFOUND) {
        Serial.println("Did not find a match");
        lcdManager.showNoMatch();
        buzzerManager.playError();
        delay(2000);
        lcdManager.showWaitingForFinger();
    }
}

void cloudMode_loop() {
    // Check for Serial commands
    if (Serial.available()) {
        char cmd = Serial.read();
        
        if (cmd == '1') {
            cloudMode_enrollWithSync();
            Serial.println("\nEnter choice (1 or 2):");
        } else if (cmd == '2') {
            Serial.println("\n--- Verification Mode ---");
            Serial.println("Place finger on sensor...");
            lcdManager.showWaitingForFinger();
            
            // Stay in verification loop until command received
            while (!Serial.available()) {
                cloudMode_verifyWithSync();
                delay(500);
            }
            
            Serial.println("\nEnter choice (1 or 2):");
            lcdManager.clear();
            lcdManager.print(0, 0, "Cloud Mode");
            lcdManager.print(1, 0, "Serial: 1 or 2");
        }
    }
    
    delay(100);
}
