#ifndef BUZZERMANAGER_H
#define BUZZERMANAGER_H

#include <Arduino.h>

class BuzzerManager {
private:
    uint8_t buzzerPin;
    
public:
    BuzzerManager(uint8_t pin);
    void initialize();
    void playSuccess();
    void playError();
    void playBeep();
};

#endif
