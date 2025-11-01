#include "FingerPrintManager.h"

FingerPrintManager::FingerPrintManager(Adafruit_Fingerprint* sensor) {
    finger = sensor;
}

bool FingerPrintManager::initialize() {
    finger->begin(FINGERPRINT_BAUDRATE);
    return finger->verifyPassword();
}

uint16_t FingerPrintManager::getTemplateCount() {
    finger->getTemplateCount();
    return finger->templateCount;
}

uint8_t FingerPrintManager::getFingerprintImage() {
    return finger->getImage();
}

uint8_t FingerPrintManager::convertImage() {
    return finger->image2Tz();
}

uint8_t FingerPrintManager::searchFingerprint() {
    return finger->fingerFastSearch();
}

uint8_t FingerPrintManager::createModel() {
    return finger->createModel();
}

uint8_t FingerPrintManager::storeModel(uint8_t id) {
    return finger->storeModel(id);
}

uint8_t FingerPrintManager::getFingerID() {
    return finger->fingerID;
}

uint16_t FingerPrintManager::getConfidence() {
    return finger->confidence;
}

uint8_t FingerPrintManager::verifyFingerprint(uint8_t* foundID, uint16_t* confidence) {
    uint8_t p = getFingerprintImage();
    if (p != FINGERPRINT_OK) {
        return p;
    }

    p = finger->image2Tz();
    if (p != FINGERPRINT_OK) {
        return p;
    }

    p = searchFingerprint();
    if (p == FINGERPRINT_OK) {
        *foundID = finger->fingerID;
        *confidence = finger->confidence;
    }
    
    return p;
}

uint8_t FingerPrintManager::enrollFingerprint(uint8_t id) {
    Serial.print("Waiting for finger to enroll as ID #");
    Serial.println(id);
    
    uint8_t p = -1;
    
    // Wait for finger
    while (p != FINGERPRINT_OK) {
        p = getFingerprintImage();
        if (p == FINGERPRINT_NOFINGER) {
            continue;
        } else if (p != FINGERPRINT_OK) {
            return p;
        }
    }
    
    // Image taken, convert it
    p = finger->image2Tz(1);
    if (p != FINGERPRINT_OK) {
        return p;
    }
    
    Serial.println("Remove finger");
    delay(2000);
    
    // Wait for finger to be removed
    p = 0;
    while (p != FINGERPRINT_NOFINGER) {
        p = getFingerprintImage();
    }
    
    Serial.println("Place same finger again");
    
    // Wait for same finger again
    p = -1;
    while (p != FINGERPRINT_OK) {
        p = getFingerprintImage();
        if (p == FINGERPRINT_NOFINGER) {
            continue;
        } else if (p != FINGERPRINT_OK) {
            return p;
        }
    }
    
    // Image taken, convert it
    p = finger->image2Tz(2);
    if (p != FINGERPRINT_OK) {
        return p;
    }
    
    // Create model
    p = createModel();
    if (p != FINGERPRINT_OK) {
        return p;
    }
    
    // Store model
    p = storeModel(id);
    return p;
}

uint8_t FingerPrintManager::deleteFingerprint(uint8_t id) {
    return finger->deleteModel(id);
}
