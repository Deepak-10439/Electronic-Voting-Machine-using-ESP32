#include "BuzzerManager.h"

BuzzerManager::BuzzerManager(uint8_t pin) {
    buzzerPin = pin;
}

void BuzzerManager::initialize() {
    pinMode(buzzerPin, OUTPUT);
    digitalWrite(buzzerPin, LOW);
}

void BuzzerManager::playSuccess() {
    digitalWrite(buzzerPin, HIGH);
    delay(500);
    digitalWrite(buzzerPin, LOW);
}

void BuzzerManager::playError() {
    digitalWrite(buzzerPin, HIGH);
    delay(300);
    digitalWrite(buzzerPin, LOW);
    delay(200);
    digitalWrite(buzzerPin, HIGH);
    delay(300);
    digitalWrite(buzzerPin, LOW);
}

void BuzzerManager::playBeep() {
    digitalWrite(buzzerPin, HIGH);
    delay(100);
    digitalWrite(buzzerPin, LOW);
}
