#include <LiquidCrystal_I2C.h>
#include <Adafruit_Fingerprint.h>

#define buzzerPin 25

LiquidCrystal_I2C lcd(0x27, 16, 2);

Adafruit_Fingerprint finger = Adafruit_Fingerprint(&Serial2);

void lcdPrint(uint8_t row, uint8_t position, String message) {
  lcd.setCursor(position, row);
  lcd.print(message);
}

void lcdClear() {
  lcd.clear();
}

void lcdSetup() {
  lcd.init();
  lcd.clear();
  lcd.backlight();
}

void buzzer(String type) {
  if (type == "error") {
    digitalWrite(buzzerPin, HIGH);
    delay(300);
    digitalWrite(buzzerPin, LOW);
    delay(200);
    digitalWrite(buzzerPin, HIGH);
    delay(300);
    digitalWrite(buzzerPin, LOW);
  } else if (type == "success") {
    digitalWrite(buzzerPin, HIGH);
    delay(500);
    digitalWrite(buzzerPin, LOW);
  }
}

void setup() {
  Serial.begin(115200);
  Serial2.begin(57600);
  delay(100);
  
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Welcome to ");
  lcd.setCursor(0, 1);
  lcd.print("Fingerprint");
  delay(2000);
  lcd.clear();
  
  pinMode(buzzerPin, OUTPUT);

  if (finger.verifyPassword()) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Found fingerprint");
    lcd.setCursor(0, 1);
    lcd.print("sensor!");
    delay(2000);
  } else {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Did not find");
    lcd.setCursor(0, 1);
    lcd.print("fingerprint sensor :(");
    while (1) {
      delay(1);
    }
  }

  finger.getTemplateCount();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Sensor contains");
  lcd.setCursor(0, 1);
  lcd.print(finger.templateCount);
  lcd.print(" templates");
  delay(2000);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Waiting for");
  lcd.setCursor(0, 1);
  lcd.print("valid finger...");
}

void loop() {
  uint8_t p = finger.getImage();
  if (p == FINGERPRINT_OK) {
    Serial.println("Image taken");
    
    p = finger.image2Tz();
    if (p == FINGERPRINT_OK) {
      Serial.println("Image converted");
      
      p = finger.fingerFastSearch();
      if (p == FINGERPRINT_OK) {
        Serial.print("Found ID #");
        Serial.print(finger.fingerID);
        Serial.print(" with confidence of ");
        Serial.println(finger.confidence);
        
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("ID: ");
        lcd.print(finger.fingerID);
        lcd.setCursor(0, 1);
        lcd.print("Confidence: ");
        lcd.print(finger.confidence);
        
        buzzer("success");
        delay(2000);
        
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Waiting for");
        lcd.setCursor(0, 1);
        lcd.print("valid finger...");
      } else {
        Serial.println("Did not find a match");
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("No match found");
        buzzer("error");
        delay(2000);
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Waiting for");
        lcd.setCursor(0, 1);
        lcd.print("valid finger...");
      }
    } else {
      Serial.println("Failed to convert image");
    }
  } else if (p != FINGERPRINT_NOFINGER) {
    Serial.println("Failed to get image");
  }

  delay(500);
}