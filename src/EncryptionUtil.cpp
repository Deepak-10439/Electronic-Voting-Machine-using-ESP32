#include "EncryptionUtil.h"
#include <string.h>

EncryptionUtil::EncryptionUtil() {
    mbedtls_aes_init(&aes);
    // Initialize IV with zeros (should be random in production)
    memset(iv, 0, 16);
}

EncryptionUtil::~EncryptionUtil() {
    mbedtls_aes_free(&aes);
}

void EncryptionUtil::begin(const char* encryptionKey) {
    // Convert string key to 256-bit key
    memset(key, 0, 32);
    size_t keyLen = strlen(encryptionKey);
    size_t copyLen = (keyLen > 32) ? 32 : keyLen;
    memcpy(key, encryptionKey, copyLen);
    
    Serial.println("[Encryption] Initialized with AES-256");
}

void EncryptionUtil::generateIV() {
    // Generate random IV (simple version - use better RNG in production)
    for (int i = 0; i < 16; i++) {
        iv[i] = random(0, 256);
    }
}

bool EncryptionUtil::encrypt(uint8_t* input, size_t inputLen, uint8_t* output, size_t* outputLen) {
    // Calculate padded length (AES requires 16-byte blocks)
    size_t paddedLen = ((inputLen + 15) / 16) * 16;
    *outputLen = paddedLen;
    
    // Pad input
    uint8_t paddedInput[paddedLen];
    memcpy(paddedInput, input, inputLen);
    
    // PKCS7 padding
    uint8_t padValue = paddedLen - inputLen;
    for (size_t i = inputLen; i < paddedLen; i++) {
        paddedInput[i] = padValue;
    }
    
    // Set encryption key
    mbedtls_aes_setkey_enc(&aes, key, 256);
    
    // Encrypt
    for (size_t i = 0; i < paddedLen; i += 16) {
        int ret = mbedtls_aes_crypt_cbc(&aes, MBEDTLS_AES_ENCRYPT, 16, iv, 
                                        paddedInput + i, output + i);
        if (ret != 0) {
            Serial.println("[Encryption] Encryption failed!");
            return false;
        }
    }
    
    Serial.println("[Encryption] Data encrypted successfully");
    return true;
}

bool EncryptionUtil::decrypt(uint8_t* input, size_t inputLen, uint8_t* output, size_t* outputLen) {
    if (inputLen % 16 != 0) {
        Serial.println("[Encryption] Invalid encrypted data length");
        return false;
    }
    
    // Set decryption key
    mbedtls_aes_setkey_dec(&aes, key, 256);
    
    // Decrypt
    for (size_t i = 0; i < inputLen; i += 16) {
        int ret = mbedtls_aes_crypt_cbc(&aes, MBEDTLS_AES_DECRYPT, 16, iv,
                                        input + i, output + i);
        if (ret != 0) {
            Serial.println("[Encryption] Decryption failed!");
            return false;
        }
    }
    
    // Remove PKCS7 padding
    uint8_t padValue = output[inputLen - 1];
    if (padValue > 0 && padValue <= 16) {
        *outputLen = inputLen - padValue;
    } else {
        *outputLen = inputLen;
    }
    
    Serial.println("[Encryption] Data decrypted successfully");
    return true;
}

String EncryptionUtil::encryptToBase64(uint8_t* data, size_t dataLen) {
    // Encrypt data
    uint8_t encrypted[dataLen + 32]; // Extra space for padding
    size_t encryptedLen = 0;
    
    if (!encrypt(data, dataLen, encrypted, &encryptedLen)) {
        return "";
    }
    
    // Encode to Base64
    return toBase64(encrypted, encryptedLen);
}

bool EncryptionUtil::decryptFromBase64(String base64Data, uint8_t* output, size_t* outputLen) {
    // Decode from Base64
    uint8_t encrypted[1024];
    size_t encryptedLen = 0;
    
    if (!fromBase64(base64Data, encrypted, &encryptedLen)) {
        return false;
    }
    
    // Decrypt data
    return decrypt(encrypted, encryptedLen, output, outputLen);
}

String EncryptionUtil::toBase64(uint8_t* data, size_t length) {
    return base64::encode(data, length);
}

bool EncryptionUtil::fromBase64(String base64String, uint8_t* output, size_t* outputLen) {
    String decoded = base64::decode(base64String);
    *outputLen = decoded.length();
    memcpy(output, decoded.c_str(), *outputLen);
    return true;
}
