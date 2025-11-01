# 🚀 QUICK REFERENCE GUIDE

## How to Switch Between Modes

### ✅ The ONLY file you need to edit: `include/Config.h`

---

## 🔄 Switching Modes

### Want to VERIFY/VOTE? ✓
```cpp
#define MODE_VERIFY     // ✓ Uncomment this
// #define MODE_ENROLL  // ✗ Comment this
// #define MODE_DELETE  // ✗ Comment this
```

### Want to ENROLL new fingerprints? ➕
```cpp
// #define MODE_VERIFY  // ✗ Comment this
#define MODE_ENROLL     // ✓ Uncomment this
// #define MODE_DELETE  // ✗ Comment this
```

### Want to DELETE fingerprints? 🗑️
```cpp
// #define MODE_VERIFY  // ✗ Comment this
// #define MODE_ENROLL  // ✗ Comment this
#define MODE_DELETE     // ✓ Uncomment this
```

---

## 📋 Common Tasks

### Task 1: First-Time Setup (Enroll 10 Users)
**File: `Config.h`**
```cpp
// #define MODE_VERIFY
#define MODE_ENROLL
// #define MODE_DELETE

#define ENROLL_START_ID 1
#define ENROLL_COUNT 10
#define ENROLL_MANUAL false
```
**Then**: Upload → Follow LCD prompts

---

### Task 2: Start Voting
**File: `Config.h`**
```cpp
#define MODE_VERIFY
// #define MODE_ENROLL
// #define MODE_DELETE
```
**Then**: Upload → Place fingers to vote

---

### Task 3: Remove User #5
**File: `Config.h`**
```cpp
// #define MODE_VERIFY
// #define MODE_ENROLL
#define MODE_DELETE

#define DELETE_ID 5
#define DELETE_MANUAL false
```
**Then**: Upload → User deleted automatically

---

### Task 4: Clear All Fingerprints
**File: `Config.h`**
```cpp
// #define MODE_VERIFY
// #define MODE_ENROLL
#define MODE_DELETE

#define DELETE_ALL true
```
**Then**: Upload → All data erased

---

## 🎛️ Configuration Cheat Sheet

| Setting | What It Does | Values |
|---------|-------------|--------|
| `MODE_VERIFY` | Enable voting/verification mode | Uncomment to use |
| `MODE_ENROLL` | Enable enrollment mode | Uncomment to use |
| `MODE_DELETE` | Enable deletion mode | Uncomment to use |
| `ENROLL_START_ID` | First ID to enroll | 1-127 |
| `ENROLL_COUNT` | How many to enroll | 1-127 |
| `ENROLL_MANUAL` | Manual ID entry | true/false |
| `DELETE_ID` | Which ID to delete | 1-127 |
| `DELETE_MANUAL` | Manual ID entry | true/false |
| `DELETE_ALL` | Delete everything | true/false |
| `VERIFY_CONFIDENCE_THRESHOLD` | Match sensitivity | 0-255 (50 recommended) |

---

## ⚡ Workflow

```
┌─────────────────────┐
│  Edit Config.h      │
│  (Select ONE mode)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Upload to ESP32    │
│  (PlatformIO)       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Use the System     │
│  (Follow LCD)       │
└─────────────────────┘
```

---

## 🚫 What NOT to Edit

❌ **DO NOT edit** `src/main.cpp`
❌ **DO NOT edit** `src/VerifyMode.cpp`
❌ **DO NOT edit** `src/EnrollMode.cpp`
❌ **DO NOT edit** `src/DeleteMode.cpp`

✅ **ONLY edit** `include/Config.h`

---

## 📞 Need Help?

1. **Sensor not found?** → Check connections
2. **LCD blank?** → Check I2C address (0x27 or 0x3F)
3. **Mode error?** → Uncomment exactly ONE mode in Config.h
4. **Can't enroll?** → Clean finger, press firmly

---

## 💾 File to Change

```
include/
  └── Config.h  ← ⭐ EDIT THIS FILE ONLY
```

Everything else works automatically! 🎉
