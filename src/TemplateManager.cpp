#include "TemplateManager.h"
#include <base64.hpp>

TemplateManager::TemplateManager(Adafruit_Fingerprint* sensor) {
    finger = sensor;
    memset(templateBuffer1, 0, 512);
    memset(templateBuffer2, 0, 512);
}

uint16_t TemplateManager::getTemplateCount() {
    finger->getTemplateCount();
    return finger->templateCount;
}

bool TemplateManager::templateExists(uint16_t id) {
    uint8_t p = finger->loadModel(id);
    return (p == FINGERPRINT_OK);
}

bool TemplateManager::clearTemplate(uint16_t id) {
    uint8_t p = finger->deleteModel(id);
    return (p == FINGERPRINT_OK);
}

bool TemplateManager::clearAllTemplates() {
    uint8_t p = finger->emptyDatabase();
    return (p == FINGERPRINT_OK);
}

bool TemplateManager::extractTemplate(uint16_t id, uint8_t* templateBuffer, uint16_t* templateSize) {
    // Load model from flash to buffer
    uint8_t p = finger->loadModel(id);
    if (p != FINGERPRINT_OK) {
        Serial.println("Failed to load model from flash");
        return false;
    }
    
    // Download the model
    p = finger->getModel();
    if (p != FINGERPRINT_OK) {
        Serial.println("Failed to get model");
        return false;
    }
    
    // Read the template data from the packet
    // Note: This is sensor-specific and may not work on all R307 variants
    // The Adafruit library stores this in finger->fingerTemplate
    
    // Copy template data
    // WARNING: This is implementation-specific
    // Check your sensor's datasheet for actual method
    
    Serial.println("⚠️ Template extraction may not be supported on all R307 variants");
    Serial.println("Alternative: Store template during enrollment before writing to sensor");
    
    return false;  // Return false as direct extraction is often not supported
}

bool TemplateManager::downloadModel(uint16_t id) {
    uint8_t p = finger->loadModel(id);
    if (p != FINGERPRINT_OK) return false;
    
    p = finger->getModel();
    return (p == FINGERPRINT_OK);
}

bool TemplateManager::uploadTemplate(uint16_t id, uint8_t* templateData, uint16_t templateSize) {
    // This functionality is rarely supported on R307
    // Alternative approach: Store raw template during enrollment
    
    Serial.println("⚠️ Direct template upload not supported on most R307 variants");
    Serial.println("Solution: Capture template data during enrollment process");
    
    return false;
}

bool TemplateManager::uploadModel(uint16_t id) {
    // Store the model in specified location
    uint8_t p = finger->storeModel(id);
    return (p == FINGERPRINT_OK);
}

bool TemplateManager::captureTemplateData(uint8_t* buffer, uint16_t* size) {
    // After creating model, try to get the template data
    uint8_t p = finger->getModel();
    if (p != FINGERPRINT_OK) {
        Serial.println("Failed to get model for template capture");
        return false;
    }
    
    // Note: Direct template extraction is limited on R307
    // This is a placeholder - actual implementation depends on sensor capabilities
    Serial.println("⚠️ Template capture: Limited by R307 hardware");
    *size = 0;
    return false;
}

bool TemplateManager::getLastTemplateData(uint8_t* buffer, uint16_t* size) {
    // Return the last captured template data
    // Note: This would need to be captured during enrollment
    *size = 0;
    return false;
}

String TemplateManager::templateToBase64(uint8_t* templateData, uint16_t size) {
    // Convert binary template to Base64 string for storage
    if (size == 0 || templateData == nullptr) {
        return "";
    }
    
    // Use base64 encoding
    unsigned int base64_length = encode_base64_length(size);
    unsigned char* base64_output = (unsigned char*)malloc(base64_length);
    
    if (base64_output == nullptr) {
        return "";
    }
    
    encode_base64(templateData, size, base64_output);
    String result = String((char*)base64_output);
    free(base64_output);
    
    return result;
}

bool TemplateManager::base64ToTemplate(String base64Data, uint8_t* buffer, uint16_t* size) {
    // Convert Base64 string back to binary template
    if (base64Data.length() == 0) {
        *size = 0;
        return false;
    }
    
    unsigned int decoded_length = decode_base64_length((unsigned char*)base64Data.c_str());
    
    if (decoded_length > 512) {  // Safety check
        *size = 0;
        return false;
    }
    
    decode_base64((unsigned char*)base64Data.c_str(), buffer);
    *size = decoded_length;
    
    return true;
}
