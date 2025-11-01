#ifndef LCDMANAGER_H
#define LCDMANAGER_H

#include <Arduino.h>
#include <LiquidCrystal_I2C.h>

class LCDManager {
private:
    LiquidCrystal_I2C* lcd;
    
public:
    LCDManager(uint8_t address, uint8_t cols, uint8_t rows);
    void initialize();
    void clear();
    void print(uint8_t row, uint8_t col, String message);
    void showWelcome();
    void showSensorFound();
    void showSensorNotFound();
    void showTemplateCount(uint16_t count);
    void showWaitingForFinger();
    void showFingerMatch(uint8_t id, uint16_t confidence);
    void showNoMatch();
    void showEnrollStart(uint8_t id);
    void showEnrollProgress(String message);
    void showEnrollSuccess();
    void showEnrollFailed();
    void showDeleteStart(uint8_t id);
    void showDeleteSuccess();
    void showDeleteFailed();
};

#endif
