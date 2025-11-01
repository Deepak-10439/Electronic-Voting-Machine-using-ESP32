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

bool deletionComplete = false;

uint8_t readNumberFromSerial() {
    uint8_t num = 0;
    while (num == 0) {
        while (!Serial.available());
        num = Serial.parseInt();
    }
    return num;
}

void deleteMode_setup() {
    Serial.println("\n=== DELETE MODE ===");
    Serial.println("Fingerprint Deletion System Ready");
    
    lcdManager.showWelcome();
    lcdManager.showSensorFound();
    
    uint16_t templateCount = fpManager.getTemplateCount();
    lcdManager.showTemplateCount(templateCount);
    Serial.print("Sensor contains ");
    Serial.print(templateCount);
    Serial.println(" templates");
    
    if (DELETE_ALL) {
        Serial.println("\nWARNING: DELETE ALL mode enabled!");
        lcdManager.clear();
        lcdManager.print(0, 0, "Delete All Mode");
        lcdManager.print(1, 0, "Starting...");
        delay(2000);
    } else if (DELETE_MANUAL) {
        Serial.println("\nManual delete mode");
        Serial.println("Enter ID to delete via Serial Monitor");
        lcdManager.clear();
        lcdManager.print(0, 0, "Manual Delete");
        lcdManager.print(1, 0, "Enter ID...");
    } else {
        Serial.print("Will delete ID #");
        Serial.println(DELETE_ID);
        lcdManager.showDeleteStart(DELETE_ID);
    }
}

void deleteMode_loop() {
    if (deletionComplete) {
        delay(100);
        return;
    }
    
    if (DELETE_ALL) {
        Serial.println("\n--- Deleting all fingerprints ---");
        lcdManager.clear();
        lcdManager.print(0, 0, "Deleting All...");
        
        uint16_t count = 0;
        for (uint8_t id = 1; id <= 127; id++) {
            uint8_t result = fpManager.deleteFingerprint(id);
            if (result == FINGERPRINT_OK) {
                count++;
                Serial.print("Deleted ID #");
                Serial.println(id);
                lcdManager.print(1, 0, "Deleted: " + String(count));
            }
            delay(50);
        }
        
        Serial.print("Deleted ");
        Serial.print(count);
        Serial.println(" fingerprints");
        
        lcdManager.clear();
        lcdManager.print(0, 0, "All Deleted!");
        lcdManager.print(1, 0, String(count) + " removed");
        buzzerManager.playSuccess();
        deletionComplete = true;
        delay(3000);
        return;
    }
    
    uint8_t idToDelete = DELETE_ID;
    
    if (DELETE_MANUAL) {
        Serial.println("\nEnter ID to delete (1-127):");
        lcdManager.clear();
        lcdManager.print(0, 0, "Enter ID:");
        lcdManager.print(1, 0, "Via Serial...");
        
        idToDelete = readNumberFromSerial();
        
        if (idToDelete == 0 || idToDelete > 127) {
            Serial.println("Invalid ID! Use 1-127");
            buzzerManager.playError();
            return;
        }
    }
    
    Serial.print("Deleting ID #");
    Serial.println(idToDelete);
    lcdManager.showDeleteStart(idToDelete);
    
    uint8_t result = fpManager.deleteFingerprint(idToDelete);
    
    if (result == FINGERPRINT_OK) {
        Serial.println("Successfully deleted!");
        lcdManager.showDeleteSuccess();
        buzzerManager.playSuccess();
    } else if (result == FINGERPRINT_PACKETRECIEVEERR) {
        Serial.println("Communication error");
        lcdManager.showDeleteFailed();
        buzzerManager.playError();
    } else if (result == FINGERPRINT_BADLOCATION) {
        Serial.println("Could not delete in that location");
        lcdManager.showDeleteFailed();
        buzzerManager.playError();
    } else if (result == FINGERPRINT_FLASHERR) {
        Serial.println("Error writing to flash");
        lcdManager.showDeleteFailed();
        buzzerManager.playError();
    } else {
        Serial.print("Unknown error: 0x");
        Serial.println(result, HEX);
        lcdManager.showDeleteFailed();
        buzzerManager.playError();
    }
    
    delay(2000);
    
    if (!DELETE_MANUAL) {
        deletionComplete = true;
    }
}
