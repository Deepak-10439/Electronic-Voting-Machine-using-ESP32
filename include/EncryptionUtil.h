#ifndef ENCRYPTIONUTIL_H
#define ENCRYPTIONUTIL_H

#include <Arduino.h>
#include "mbedtls/aes.h"
#include <base64.h>

class EncryptionUtil {
private:
    mbedtls_aes_context aes;
    unsigned char key[32]; // AES-256 key
    unsigned char iv[16];  // Initialization vector
    
public:
    EncryptionUtil();
    ~EncryptionUtil();
    
    // Initialize with encryption key
    void begin(const char* encryptionKey);
    
    // Encrypt data
    bool encrypt(uint8_t* input, size_t inputLen, uint8_t* output, size_t* outputLen);
    
    // Decrypt data
    bool decrypt(uint8_t* input, size_t inputLen, uint8_t* output, size_t* outputLen);
    
    // Encrypt and encode to Base64
    String encryptToBase64(uint8_t* data, size_t dataLen);
    
    // Decode Base64 and decrypt
    bool decryptFromBase64(String base64Data, uint8_t* output, size_t* outputLen);
    
    // Generate random IV
    void generateIV();
    
    // Base64 encoding/decoding
    String toBase64(uint8_t* data, size_t length);
    bool fromBase64(String base64String, uint8_t* output, size_t* outputLen);
};

#endif
