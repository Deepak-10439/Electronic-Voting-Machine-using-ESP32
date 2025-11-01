#include "LCDManager.h"

LCDManager::LCDManager(uint8_t address, uint8_t cols, uint8_t rows) {
    lcd = new LiquidCrystal_I2C(address, cols, rows);
}

void LCDManager::initialize() {
    lcd->init();
    lcd->backlight();
    lcd->clear();
}

void LCDManager::clear() {
    lcd->clear();
}

void LCDManager::print(uint8_t row, uint8_t col, String message) {
    lcd->setCursor(col, row);
    lcd->print(message);
}

void LCDManager::showWelcome() {
    clear();
    print(0, 0, "Welcome to");
    print(1, 0, "EVM System");
    delay(2000);
}

void LCDManager::showSensorFound() {
    clear();
    print(0, 0, "Found fingerprint");
    print(1, 0, "sensor!");
    delay(2000);
}

void LCDManager::showSensorNotFound() {
    clear();
    print(0, 0, "Did not find");
    print(1, 0, "FP sensor :(");
}

void LCDManager::showTemplateCount(uint16_t count) {
    clear();
    print(0, 0, "Sensor contains");
    print(1, 0, String(count) + " templates");
    delay(2000);
}

void LCDManager::showWaitingForFinger() {
    clear();
    print(0, 0, "Waiting for");
    print(1, 0, "valid finger...");
}

void LCDManager::showFingerMatch(uint8_t id, uint16_t confidence) {
    clear();
    print(0, 0, "ID: " + String(id));
    print(1, 0, "Conf: " + String(confidence));
}

void LCDManager::showNoMatch() {
    clear();
    print(0, 0, "No match found");
    print(1, 0, "Try again");
}

void LCDManager::showEnrollStart(uint8_t id) {
    clear();
    print(0, 0, "Enrolling ID #" + String(id));
    print(1, 0, "Place finger...");
}

void LCDManager::showEnrollProgress(String message) {
    clear();
    print(0, 0, "Enrolling...");
    print(1, 0, message);
}

void LCDManager::showEnrollSuccess() {
    clear();
    print(0, 0, "Enrollment");
    print(1, 0, "Successful!");
}

void LCDManager::showEnrollFailed() {
    clear();
    print(0, 0, "Enrollment");
    print(1, 0, "Failed!");
}

void LCDManager::showDeleteStart(uint8_t id) {
    clear();
    print(0, 0, "Deleting ID #" + String(id));
    delay(1000);
}

void LCDManager::showDeleteSuccess() {
    clear();
    print(0, 0, "Fingerprint");
    print(1, 0, "Deleted!");
}

void LCDManager::showDeleteFailed() {
    clear();
    print(0, 0, "Delete");
    print(1, 0, "Failed!");
}
