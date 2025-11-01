#ifndef TEMPLATEMANAGER_H
#define TEMPLATEMANAGER_H

#include <Arduino.h>
#include <Adafruit_Fingerprint.h>

class TemplateManager {
private:
    Adafruit_Fingerprint* finger;
    uint8_t templateBuffer1[512];
    uint8_t templateBuffer2[512];
    
public:
    TemplateManager(Adafruit_Fingerprint* sensor);
    
    // Capture template during enrollment (before storing)
    bool captureTemplateData(uint8_t* buffer, uint16_t* size);
    
    // Extract template from sensor (if supported)
    bool extractTemplate(uint16_t id, uint8_t* templateBuffer, uint16_t* templateSize);
    
    // Upload template to sensor
    bool uploadTemplate(uint16_t id, uint8_t* templateData, uint16_t templateSize);
    
    // Download template from sensor to buffer
    bool downloadModel(uint16_t id);
    
    // Upload model to sensor from buffer
    bool uploadModel(uint16_t id);
    
    // Convert template to Base64 string for cloud storage
    String templateToBase64(uint8_t* templateData, uint16_t size);
    
    // Convert Base64 string back to template
    bool base64ToTemplate(String base64Data, uint8_t* buffer, uint16_t* size);
    
    // Get template data from last enrollment
    bool getLastTemplateData(uint8_t* buffer, uint16_t* size);
    
    // Check if ID exists on sensor
    bool templateExists(uint16_t id);
    
    // Get number of stored templates
    uint16_t getTemplateCount();
    
    // Clear specific template
    bool clearTemplate(uint16_t id);
    
    // Clear all templates
    bool clearAllTemplates();
};

#endif
