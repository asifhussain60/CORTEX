# Task 4.2 Design: Encryptor Implementation

**Plan:** A01 - Enterprise Python Audit Logger with Self-Healing  
**Phase:** 4 - Security Layer  
**Task:** 4.2 - Encryptor with AES-256-GCM  
**Status:** 🎨 **DESIGN PHASE**  
**Date:** January 5, 2026  
**Author:** Asif Hussain

---

## 🎯 Objectives

Implement production-grade encryption for audit logs with:
1. **AES-256-GCM:** Primary encryption (NIST-approved, authenticated)
2. **Fernet:** Fallback encryption (symmetric, time-based)
3. **Key Management:** Secure key generation, storage, rotation
4. **Tamper Detection:** MAC verification, integrity checks
5. **Compliance:** GDPR, HIPAA, SOC 2 requirements

---

## 🏗️ Architecture

### Component Hierarchy
```
Encryptor (Main Class)
├── AES-256-GCM Engine (Primary)
│   ├── Key derivation (PBKDF2-HMAC-SHA256)
│   ├── Nonce generation (96-bit random)
│   ├── Authentication tag (128-bit)
│   └── Encryption/Decryption
├── Fernet Engine (Fallback)
│   ├── Key generation (URL-safe base64)
│   ├── Time-based tokens
│   └── Encryption/Decryption
├── Key Manager
│   ├── Master key storage
│   ├── Key rotation
│   ├── Key derivation
│   └── Secure deletion
└── Tamper Detector
    ├── MAC verification
    ├── Integrity checks
    └── Audit trail
```

### Design Patterns
- **Strategy Pattern:** Pluggable encryption algorithms (AES-GCM, Fernet)
- **Factory Pattern:** Create encryptors based on algorithm choice
- **Singleton Pattern:** Key manager (single instance per process)
- **Template Method:** Encrypt/decrypt workflow with hooks
- **Observer Pattern:** Key rotation notifications

---

## 📊 Data Structures

### Encrypted Message Format
```python
{
    "version": "1.0",           # Format version for migration
    "algorithm": "AES-256-GCM", # Encryption algorithm used
    "encrypted_data": "...",    # Base64-encoded ciphertext
    "nonce": "...",             # Base64-encoded nonce (12 bytes)
    "tag": "...",               # Base64-encoded auth tag (16 bytes)
    "key_id": "key-2026-01",    # Key identifier for rotation
    "timestamp": 1704470400,    # Unix timestamp
    "metadata": {               # Optional metadata
        "sanitized": true,      # PII sanitized before encryption
        "log_level": "INFO"
    }
}
```

### Key Storage Format
```python
{
    "key_id": "key-2026-01",
    "algorithm": "AES-256-GCM",
    "key": "...",               # Base64-encoded key (32 bytes)
    "created_at": 1704470400,
    "expires_at": 1735920000,   # Key expiration (1 year)
    "status": "active",         # active, rotating, revoked
    "rotation_count": 0
}
```

---

## 🔐 Encryption Algorithms

### AES-256-GCM (Primary)

**Why AES-256-GCM?**
- ✅ NIST-approved (FIPS 197)
- ✅ Authenticated encryption (prevents tampering)
- ✅ Fast (hardware acceleration on modern CPUs)
- ✅ Industry standard (used by TLS 1.3, SSH)

**Parameters:**
- Key size: 256 bits (32 bytes)
- Nonce size: 96 bits (12 bytes) - unique per encryption
- Tag size: 128 bits (16 bytes) - authentication
- Block size: 128 bits (16 bytes)

**Implementation:**
```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt_aes_gcm(plaintext: bytes, key: bytes) -> dict:
    """Encrypt with AES-256-GCM"""
    aesgcm = AESGCM(key)  # 32-byte key
    nonce = os.urandom(12)  # 96-bit nonce
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    
    # Split ciphertext and tag
    encrypted_data = ciphertext[:-16]
    tag = ciphertext[-16:]
    
    return {
        "encrypted_data": base64.b64encode(encrypted_data).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "tag": base64.b64encode(tag).decode()
    }
```

### Fernet (Fallback)

**Why Fernet?**
- ✅ Simple API (harder to misuse)
- ✅ Time-based tokens (automatic expiration)
- ✅ Built-in versioning
- ✅ Standard library (no external deps)

**Parameters:**
- Key size: 256 bits (32 bytes)
- Uses AES-128-CBC + HMAC-SHA256
- Timestamps for TTL enforcement

**Implementation:**
```python
from cryptography.fernet import Fernet

def encrypt_fernet(plaintext: bytes, key: bytes) -> str:
    """Encrypt with Fernet"""
    f = Fernet(key)  # 32-byte URL-safe base64 key
    token = f.encrypt(plaintext)
    return base64.b64encode(token).decode()
```

---

## 🔑 Key Management

### Key Generation

**Master Key:**
```python
def generate_master_key() -> bytes:
    """Generate 256-bit master key"""
    return os.urandom(32)  # Cryptographically secure random
```

**Derived Keys (PBKDF2):**
```python
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

def derive_key(master_key: bytes, salt: bytes, iterations: int = 100000) -> bytes:
    """Derive key using PBKDF2-HMAC-SHA256"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations
    )
    return kdf.derive(master_key)
```

### Key Storage

**Options:**
1. **Environment Variable:** Simple, not secure (dev only)
2. **File System:** Encrypted file with OS permissions
3. **Key Management Service (KMS):** AWS KMS, Azure Key Vault (production)
4. **Hardware Security Module (HSM):** FIPS 140-2 certified (enterprise)

**Implementation (File System):**
```python
import json
from pathlib import Path

def save_key(key_data: dict, key_file: Path) -> None:
    """Save key to encrypted file"""
    key_file.parent.mkdir(parents=True, exist_ok=True)
    key_file.write_text(json.dumps(key_data), encoding='utf-8')
    key_file.chmod(0o600)  # Read/write owner only

def load_key(key_file: Path) -> dict:
    """Load key from encrypted file"""
    if not key_file.exists():
        raise FileNotFoundError(f"Key file not found: {key_file}")
    return json.loads(key_file.read_text(encoding='utf-8'))
```

### Key Rotation

**Strategy:**
- Rotate keys every 90 days (configurable)
- Keep old keys for decryption (backward compatibility)
- Maximum 5 active keys at once
- Automatic re-encryption of old data (background job)

**Implementation:**
```python
def rotate_key(key_manager: KeyManager) -> str:
    """Rotate encryption key"""
    old_key_id = key_manager.active_key_id
    new_key_id = key_manager.generate_new_key()
    
    # Mark old key as rotating
    key_manager.set_key_status(old_key_id, 'rotating')
    
    # Activate new key
    key_manager.set_active_key(new_key_id)
    
    # Schedule re-encryption (async background job)
    schedule_re_encryption(old_key_id, new_key_id)
    
    return new_key_id
```

---

## 🛡️ Tamper Detection

### MAC Verification

**AES-GCM:**
- Built-in authentication tag (128-bit)
- Verifies both ciphertext and associated data
- Throws exception on tampering

```python
def decrypt_aes_gcm(encrypted: dict, key: bytes) -> bytes:
    """Decrypt with tamper detection"""
    aesgcm = AESGCM(key)
    nonce = base64.b64decode(encrypted['nonce'])
    ciphertext = base64.b64decode(encrypted['encrypted_data'])
    tag = base64.b64decode(encrypted['tag'])
    
    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext + tag, None)
        return plaintext
    except Exception as e:
        raise TamperDetectedError(f"Tamper detected: {e}")
```

### Integrity Checks

**Additional checks:**
1. **Timestamp validation:** Reject old logs (replay attacks)
2. **Key ID validation:** Ensure key exists and not revoked
3. **Format validation:** Verify JSON structure
4. **Checksum validation:** Optional SHA-256 checksum

```python
def verify_integrity(encrypted: dict) -> bool:
    """Verify message integrity"""
    # Check required fields
    required = ['version', 'algorithm', 'encrypted_data', 'nonce', 'tag', 'key_id']
    if not all(field in encrypted for field in required):
        return False
    
    # Check timestamp (reject > 24 hours old)
    age = time.time() - encrypted.get('timestamp', 0)
    if age > 86400:  # 24 hours
        return False
    
    # Check key ID exists
    if not key_manager.has_key(encrypted['key_id']):
        return False
    
    return True
```

---

## 📋 API Design

### Encryptor Class

```python
class Encryptor:
    """Production-grade encryption for audit logs"""
    
    def __init__(self, key_file: Path, algorithm: str = 'AES-256-GCM'):
        """Initialize encryptor with key file and algorithm"""
        self.key_manager = KeyManager(key_file)
        self.algorithm = algorithm
        
    def encrypt(self, plaintext: str) -> dict:
        """Encrypt plaintext string, return encrypted dict"""
        pass
    
    def decrypt(self, encrypted: dict) -> str:
        """Decrypt encrypted dict, return plaintext string"""
        pass
    
    def rotate_keys(self) -> str:
        """Rotate encryption keys, return new key ID"""
        pass
    
    def verify_integrity(self, encrypted: dict) -> bool:
        """Verify message integrity (tamper detection)"""
        pass
```

### KeyManager Class

```python
class KeyManager:
    """Secure key management with rotation"""
    
    def __init__(self, key_file: Path):
        """Initialize key manager with key storage file"""
        self.key_file = key_file
        self.keys = {}
        self.active_key_id = None
        
    def generate_new_key(self) -> str:
        """Generate new encryption key, return key ID"""
        pass
    
    def get_key(self, key_id: str) -> bytes:
        """Get key by ID"""
        pass
    
    def set_active_key(self, key_id: str) -> None:
        """Set active key for encryption"""
        pass
    
    def revoke_key(self, key_id: str) -> None:
        """Revoke key (mark as inactive)"""
        pass
```

---

## 🧪 Test Cases

### Unit Tests (TDD RED Phase)

```python
def test_encrypt_decrypt_aes_gcm():
    """Test AES-256-GCM encryption/decryption"""
    encryptor = Encryptor(algorithm='AES-256-GCM')
    plaintext = "Sensitive audit log data"
    encrypted = encryptor.encrypt(plaintext)
    decrypted = encryptor.decrypt(encrypted)
    assert decrypted == plaintext

def test_tamper_detection():
    """Test tamper detection with modified ciphertext"""
    encryptor = Encryptor()
    plaintext = "Original data"
    encrypted = encryptor.encrypt(plaintext)
    
    # Tamper with ciphertext
    encrypted['encrypted_data'] = 'TAMPERED'
    
    with pytest.raises(TamperDetectedError):
        encryptor.decrypt(encrypted)

def test_key_rotation():
    """Test key rotation and backward compatibility"""
    encryptor = Encryptor()
    plaintext = "Test data"
    
    # Encrypt with old key
    encrypted_old = encryptor.encrypt(plaintext)
    old_key_id = encrypted_old['key_id']
    
    # Rotate key
    new_key_id = encryptor.rotate_keys()
    assert new_key_id != old_key_id
    
    # Decrypt with old key should still work
    decrypted = encryptor.decrypt(encrypted_old)
    assert decrypted == plaintext
    
    # New encryptions use new key
    encrypted_new = encryptor.encrypt(plaintext)
    assert encrypted_new['key_id'] == new_key_id

def test_multiple_algorithms():
    """Test switching between AES-GCM and Fernet"""
    encryptor_aes = Encryptor(algorithm='AES-256-GCM')
    encryptor_fernet = Encryptor(algorithm='Fernet')
    
    plaintext = "Test data"
    
    encrypted_aes = encryptor_aes.encrypt(plaintext)
    assert encrypted_aes['algorithm'] == 'AES-256-GCM'
    
    encrypted_fernet = encryptor_fernet.encrypt(plaintext)
    assert encrypted_fernet['algorithm'] == 'Fernet'

def test_encryption_format():
    """Test encrypted message format compliance"""
    encryptor = Encryptor()
    encrypted = encryptor.encrypt("Test data")
    
    # Check required fields
    assert 'version' in encrypted
    assert 'algorithm' in encrypted
    assert 'encrypted_data' in encrypted
    assert 'nonce' in encrypted
    assert 'tag' in encrypted
    assert 'key_id' in encrypted
    assert 'timestamp' in encrypted

def test_empty_string():
    """Test encryption of empty string"""
    encryptor = Encryptor()
    encrypted = encryptor.encrypt("")
    decrypted = encryptor.decrypt(encrypted)
    assert decrypted == ""

def test_large_data():
    """Test encryption of large data (1 MB)"""
    encryptor = Encryptor()
    plaintext = "A" * (1024 * 1024)  # 1 MB
    encrypted = encryptor.encrypt(plaintext)
    decrypted = encryptor.decrypt(encrypted)
    assert decrypted == plaintext

def test_unicode_data():
    """Test encryption of Unicode data"""
    encryptor = Encryptor()
    plaintext = "Unicode: 你好世界 🌍 Émojis 🎉"
    encrypted = encryptor.encrypt(plaintext)
    decrypted = encryptor.decrypt(encrypted)
    assert decrypted == plaintext

def test_key_not_found():
    """Test decryption with missing key"""
    encryptor = Encryptor()
    encrypted = encryptor.encrypt("Test data")
    
    # Modify key_id to non-existent key
    encrypted['key_id'] = 'non-existent-key'
    
    with pytest.raises(KeyNotFoundError):
        encryptor.decrypt(encrypted)

def test_invalid_algorithm():
    """Test initialization with invalid algorithm"""
    with pytest.raises(ValueError):
        Encryptor(algorithm='INVALID')
```

---

## 🔒 Security Considerations

### Best Practices
- ✅ Use cryptographically secure random (os.urandom)
- ✅ Never reuse nonces with same key
- ✅ Validate all inputs (prevent injection)
- ✅ Secure key storage (file permissions 0o600)
- ✅ Key rotation every 90 days
- ✅ Audit all encryption/decryption operations
- ✅ Use constant-time comparison for MACs
- ✅ Zeroize keys in memory after use

### Threat Model
- **Attacker Goals:** Read logs, modify logs, impersonate user
- **Attack Vectors:** File system access, memory dumps, network sniffing
- **Mitigations:** Encryption at rest, tamper detection, access control

---

## 📊 Performance Targets

| Operation | Target | Method |
|-----------|--------|--------|
| **Encryption** | <1ms per log | Hardware-accelerated AES |
| **Decryption** | <1ms per log | Hardware-accelerated AES |
| **Key Rotation** | <100ms | Async background job |
| **Tamper Check** | <0.1ms | Built-in MAC verification |

---

## 📚 Dependencies

```python
# requirements.txt
cryptography>=41.0.0  # AES-GCM, Fernet, PBKDF2
```

---

## ✅ Completion Criteria

- [ ] Encryptor class implemented
- [ ] AES-256-GCM encryption/decryption
- [ ] Fernet fallback encryption
- [ ] KeyManager with rotation
- [ ] Tamper detection (MAC verification)
- [ ] 15+ unit tests (100% coverage)
- [ ] Integration with PII Sanitizer (Task 4.1)
- [ ] Performance benchmarks (<1ms per operation)
- [ ] Documentation (API docs, security guide)

---

## 🎯 Next Steps

1. ✅ **Design Complete** (this document)
2. ➡️ **Write Tests (RED):** Create test_encryptor.py with failing tests
3. ➡️ **Implement (GREEN):** Create encryptor.py to pass all tests
4. ➡️ **Refactor (REFACTOR):** Apply SKULL rules, optimize performance
5. ➡️ **Integration:** Test with PII Sanitizer
6. ➡️ **Documentation:** Update completion report

---

**Generated:** 2026-01-05T11:30:00Z  
**Author:** Asif Hussain  
**Review:** GitHub Copilot (CORTEX)
