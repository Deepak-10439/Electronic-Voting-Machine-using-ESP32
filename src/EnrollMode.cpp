#include <Arduino.h>
#include <Adafruit_Fingerprint.h>
#include "Config.h"
#include "FingerPrintManager.h"
#include "LCDManager.h"
#include "BuzzerManager.h"

// Initialize hardware
extern Adafruit_Fingerprint finger;
extern LCDManager lcdManager;
extern BuzzerManager buzzerManager;
extern FingerPrintManager fpManager;

uint8_t currentEnrollID = ENROLL_START_ID;
bool enrollmentComplete = false;

uint8_t readNumberFromSerial() {
    uint8_t num = 0;
    while (num == 0) {
        while (!Serial.available());
        num = Serial.parseInt();
    }
    return num;
}

void enrollMode_setup() {
    Serial.println("\n=== ENROLL MODE ===");
    Serial.println("Fingerprint Enrollment System Ready");
    
    lcdManager.showWelcome();
    lcdManager.showSensorFound();
    
    uint16_t templateCount = fpManager.getTemplateCount();
    lcdManager.showTemplateCount(templateCount);
    Serial.print("Sensor contains ");
    Serial.print(templateCount);
    Serial.println(" templates");
    
    if (ENROLL_MANUAL) {
        Serial.println("\nReady for manual enrollment");
        Serial.println("Type ID number (1-127) in Serial Monitor to start");
        lcdManager.clear();
        lcdManager.print(0, 0, "Manual Enroll");
        lcdManager.print(1, 0, "Enter ID...");
    } else {
        Serial.print("Auto-enrollment mode: ID ");
        Serial.print(ENROLL_START_ID);
        Serial.print(" to ");
        Serial.println(ENROLL_START_ID + ENROLL_COUNT - 1);
        lcdManager.showEnrollStart(currentEnrollID);
    }
}

void enrollMode_loop() {
    if (enrollmentComplete) {
        delay(100);
        return;
    }
    
    uint8_t idToEnroll = currentEnrollID;
    
    if (ENROLL_MANUAL) {
        Serial.println("\nEnter ID to enroll (1-127):");
        lcdManager.clear();
        lcdManager.print(0, 0, "Enter ID:");
        lcdManager.print(1, 0, "Via Serial...");
        
        idToEnroll = readNumberFromSerial();
        
        if (idToEnroll == 0 || idToEnroll > 127) {
            Serial.println("Invalid ID! Use 1-127");
            buzzerManager.playError();
            return;
        }
    }
    
    Serial.println("\n--- Starting Enrollment ---");
    lcdManager.showEnrollStart(idToEnroll);
    delay(1000);
    
    // First finger scan
    lcdManager.showEnrollProgress("Place finger");
    uint8_t result = fpManager.enrollFingerprint(idToEnroll);
    
    if (result == FINGERPRINT_OK) {
        Serial.print("Successfully enrolled ID #");
        Serial.println(idToEnroll);
        lcdManager.showEnrollSuccess();
        buzzerManager.playSuccess();
        delay(2000);
        
        if (!ENROLL_MANUAL) {
            currentEnrollID++;
            if (currentEnrollID >= ENROLL_START_ID + ENROLL_COUNT) {
                Serial.println("\n*** All enrollments complete! ***");
                lcdManager.clear();
                lcdManager.print(0, 0, "All Complete!");
                lcdManager.print(1, 0, String(ENROLL_COUNT) + " enrolled");
                enrollmentComplete = true;
                buzzerManager.playSuccess();
                delay(1000);
                buzzerManager.playSuccess();
                return;
            }
            lcdManager.showEnrollStart(currentEnrollID);
        }
    } else {
        Serial.print("Enrollment failed with error code: ");
        Serial.println(result);
        lcdManager.showEnrollFailed();
        buzzerManager.playError();
        delay(2000);
        
        if (!ENROLL_MANUAL) {
            lcdManager.showEnrollStart(currentEnrollID);
        }
    }
    
    delay(1000);
}
