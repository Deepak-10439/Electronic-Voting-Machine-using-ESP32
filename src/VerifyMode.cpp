#include <Arduino.h>
#include <Adafruit_Fingerprint.h>
#include "Config.h"
#include "FingerPrintManager.h"
#include "LCDManager.h"
#include "BuzzerManager.h"

// Initialize hardware
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&FINGERPRINT_SERIAL);
LCDManager lcdManager(LCD_ADDRESS, LCD_COLS, LCD_ROWS);
BuzzerManager buzzerManager(BUZZER_PIN);
FingerPrintManager fpManager(&finger);

void verifyMode_setup() {
    Serial.println("\n=== VERIFY MODE ===");
    Serial.println("Fingerprint Verification System Ready");
    
    lcdManager.showWelcome();
    lcdManager.showSensorFound();
    
    uint16_t templateCount = fpManager.getTemplateCount();
    lcdManager.showTemplateCount(templateCount);
    Serial.print("Sensor contains ");
    Serial.print(templateCount);
    Serial.println(" templates");
    
    lcdManager.showWaitingForFinger();
}

void verifyMode_loop() {
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
            buzzerManager.playSuccess();
            
            Serial.println("✓ Vote Registered!");
            delay(2000);
        } else {
            Serial.println("✗ Low confidence, try again");
            lcdManager.showNoMatch();
            buzzerManager.playError();
            delay(2000);
        }
        
        lcdManager.showWaitingForFinger();
    } else if (result == FINGERPRINT_NOTFOUND) {
        Serial.println("Did not find a match");
        lcdManager.showNoMatch();
        buzzerManager.playError();
        delay(2000);
        lcdManager.showWaitingForFinger();
    }
    
    delay(500);
}
