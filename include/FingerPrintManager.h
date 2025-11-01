#ifndef FINGERPRINTMANAGER_H
#define FINGERPRINTMANAGER_H

#include <Arduino.h>
#include <Adafruit_Fingerprint.h>

class FingerPrintManager {
private:
    Adafruit_Fingerprint* finger;
    
public:
    FingerPrintManager(Adafruit_Fingerprint* sensor);
    bool initialize();
    uint8_t enrollFingerprint(uint8_t id);
    uint8_t deleteFingerprint(uint8_t id);
    uint8_t verifyFingerprint(uint8_t* foundID, uint16_t* confidence);
    uint16_t getTemplateCount();
    uint8_t getFingerprintImage();
    uint8_t convertImage();
    uint8_t searchFingerprint();
    uint8_t createModel();
    uint8_t storeModel(uint8_t id);
    
    // Getters for fingerprint data
    uint8_t getFingerID();
    uint16_t getConfidence();
};

#endif
