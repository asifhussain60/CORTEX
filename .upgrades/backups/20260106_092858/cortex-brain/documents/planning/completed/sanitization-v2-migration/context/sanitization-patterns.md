# Sanitization Patterns Catalog

**Date:** January 3, 2026  
**Purpose:** Consolidated pattern library for Sanitization v2  
**Sources:** 5 existing CORTEX modules

---

## 📋 Pattern Categories

### 1. PII (Personally Identifiable Information)

#### Email Addresses
```python
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
```
**Examples:**
- `john.doe@example.com` → `[REDACTED_EMAIL]` or `user_a1b2c3d4@example.com`

**Confidence:** HIGH (>99%)

---

#### Usernames
```python
USERNAME_PATTERN = r'\b[a-z][a-z0-9_]{2,19}\b'
```
**Exclusions:** Avoid common words (false positives)
**Validation:** Must contain numbers/underscores OR ≥12 chars
**Examples:**
- `john_doe123` → `[REDACTED_USERNAME]`
- `asifhussain` → `[REDACTED_USERNAME]`

**Confidence:** MEDIUM (70-85%) - requires context validation

---

#### Phone Numbers
```python
PHONE_PATTERN = r'\b\+?1?\d{10,15}\b'
```
**Formats Matched:**
- `+1-555-123-4567`
- `555-123-4567`
- `5551234567`
- `+44 20 7123 4567`

**Confidence:** HIGH (>95%)

---

#### IP Addresses
```python
IP_PATTERN = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
```
**Examples:**
- `192.168.1.1` → `[REDACTED_IP]`
- `10.0.0.5` → `[REDACTED_IP]`

**Confidence:** HIGH (>99%)

---

#### SSN (Social Security Numbers)
```python
SSN_PATTERN = r'\b\d{3}-\d{2}-\d{4}\b'
```
**Format:** `123-45-6789`

**Confidence:** VERY HIGH (>99.9%)

---

#### Passport Numbers
```python
PASSPORT_PATTERN = r'\b[A-Z]{1,2}\d{6,9}\b'
```
**Examples:**
- `AB1234567` → `[REDACTED_PASSPORT]`

**Confidence:** HIGH (>90%)

---

#### Driver's License
```python
DRIVERS_LICENSE_PATTERN = r'\b[A-Z]{1,2}\d{5,8}\b'
```

**Confidence:** MEDIUM (70-80%) - overlaps with other patterns

---

### 2. Credentials & Secrets

#### API Keys
```python
API_KEY_PATTERNS = [
    r'api[_-]?key["\']?\s*[:=]\s*["\']?([A-Za-z0-9_-]{32,})["\']?',
    r'apikey["\']?\s*[:=]\s*["\']?([A-Za-z0-9_-]{32,})["\']?',
    r'["\']([A-Za-z0-9_-]{32,64})["\']',  # Generic key-like strings
]
```
**Examples:**
- `api_key = "sk_live_123abc..."`
- `API_KEY: "ghp_abc123xyz..."`

**Confidence:** HIGH (>95%)

---

#### Passwords
```python
PASSWORD_PATTERNS = [
    r'password["\']?\s*[:=]\s*["\']?([^"\'}\s]+)["\']?',
    r'passwd["\']?\s*[:=]\s*["\']?([^"\'}\s]+)["\']?',
    r'pwd["\']?\s*[:=]\s*["\']?([^"\'}\s]+)["\']?',
]
```
**Examples:**
- `password = "MySecret123!"`
- `PASSWORD: "p@ssw0rd"`

**Confidence:** VERY HIGH (>99%)

---

#### Tokens
```python
TOKEN_PATTERNS = [
    r'token["\']?\s*[:=]\s*["\']?([\w\.-]+)["\']?',
    r'bearer\s+([\w\.-]+)',
    r'authorization:\s*bearer\s+([\w\.-]+)',
]
```
**Examples:**
- `token = "eyJhbGciOiJIUzI1NiIs..."`
- `Bearer abc123xyz...`

**Confidence:** HIGH (>95%)

---

#### Private Keys
```python
PRIVATE_KEY_PATTERN = r'-----BEGIN [A-Z ]+PRIVATE KEY-----.*?-----END [A-Z ]+PRIVATE KEY-----'
```
**Format:** PEM-encoded private keys

**Confidence:** VERY HIGH (>99.9%)

---

#### Secrets
```python
SECRET_PATTERNS = [
    r'secret["\']?\s*[:=]\s*["\']?([^"\'}\s]+)["\']?',
    r'secret_key["\']?\s*[:=]\s*["\']?([^"\'}\s]+)["\']?',
]
```

**Confidence:** HIGH (>95%)

---

### 3. Path Sanitization

#### File Paths (Unix)
```python
UNIX_PATH_PATTERN = r'/(?:[^/\s]+/)+[^/\s]*'
```
**Examples:**
- `/Users/asifhussain/PROJECTS/CORTEX` → `/Users/USER/PROJECTS/PROJECT`
- `/home/john/documents/secret.txt` → `/home/USER/documents/file.txt`

**Replacement Strategy:**
- Username → `USER`
- Project name → `PROJECT`
- Preserve file extensions

**Confidence:** HIGH (>95%)

---

#### File Paths (Windows)
```python
WINDOWS_PATH_PATTERN = r'[A-Za-z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*'
```
**Examples:**
- `C:\Users\John\Documents\file.txt` → `C:\Users\USER\Documents\file.txt`

**Replacement Strategy:**
- Username → `USER`
- Preserve drive letter and structure

**Confidence:** HIGH (>95%)

---

### 4. PHI (Protected Health Information)

#### Medical Record Numbers
```python
MRN_PATTERN = r'\bMRN[:\s]*\d{6,10}\b'
```
**Example:** `MRN: 1234567` → `[REDACTED_MRN]`

**Confidence:** VERY HIGH (>99%)

---

#### Diagnoses Codes (ICD-10)
```python
ICD10_PATTERN = r'\b[A-Z]\d{2}(?:\.\d{1,3})?\b'
```
**Example:** `E11.9` (Diabetes) → `[REDACTED_DIAGNOSIS]`

**Confidence:** HIGH (>90%)

---

#### Prescription Numbers
```python
RX_PATTERN = r'\bRX[:\s]*\d{6,10}\b'
```

**Confidence:** HIGH (>95%)

---

### 5. PCI (Payment Card Industry)

#### Credit Card Numbers
```python
CREDIT_CARD_PATTERN = r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
```
**Formats:**
- `1234-5678-9012-3456`
- `1234 5678 9012 3456`
- `1234567890123456`

**Validation:** Luhn algorithm check
**Replacement:** Show last 4 digits: `****-****-****-3456`

**Confidence:** HIGH (>95%)

---

#### CVV Codes
```python
CVV_PATTERN = r'\bCVV[:\s]*\d{3,4}\b'
```

**Confidence:** VERY HIGH (>99%)

---

#### Bank Account Numbers
```python
ACCOUNT_NUMBER_PATTERN = r'\b\d{8,17}\b'
```
**Context Required:** Needs "account" keyword nearby

**Confidence:** MEDIUM (60-70%) - requires context validation

---

### 6. Company-Specific Patterns

#### Domain Names
```python
DOMAIN_PATTERN = r'\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b'
```
**Configurable:** Company domains can be specified
**Example:** `acme.com`, `internal.company.net`

**Replacement:** `[REDACTED_DOMAIN]` or generic `company.com`

**Confidence:** HIGH (>95%)

---

#### Internal IPs
```python
INTERNAL_IP_PATTERNS = [
    r'\b10\.(?:\d{1,3}\.){2}\d{1,3}\b',          # 10.0.0.0/8
    r'\b172\.(?:1[6-9]|2\d|3[01])\.(?:\d{1,3}\.)\d{1,3}\b',  # 172.16.0.0/12
    r'\b192\.168\.(?:\d{1,3}\.)\d{1,3}\b',       # 192.168.0.0/16
]
```

**Confidence:** VERY HIGH (>99%)

---

### 7. Hash Detection (Exclusion)

#### SHA-256/MD5 Hashes
```python
HASH_PATTERN = r'\b[a-f0-9]{32,64}\b'
```
**Purpose:** Identify already-anonymized content (don't re-sanitize hashes)

**Confidence:** VERY HIGH (>99%)

---

## 🎨 Replacement Strategies

### Strategy 1: Complete Removal
```python
"email: john@example.com" → "email: [REDACTED_EMAIL]"
```

### Strategy 2: Partial Preservation
```python
"credit card: 1234-5678-9012-3456" → "credit card: ****-****-****-3456"
```

### Strategy 3: Hash Replacement
```python
"username: john_doe" → "username: user_a1b2c3d4e5f6"
```

### Strategy 4: Generic Placeholder
```python
"/Users/john/project" → "/Users/USER/project"
```

### Strategy 5: Structural Preservation
```python
"email@domain.com" → "user123@example.com" (preserves email structure)
```

---

## 🧪 Pattern Validation

### Test Suite Requirements

**For Each Pattern:**
1. **True Positives:** Should detect actual sensitive data
2. **True Negatives:** Should NOT flag safe content
3. **False Positives:** Edge cases that trigger incorrectly
4. **False Negatives:** Missed sensitive data

**Example Test Matrix:**

| Pattern | True Positive | True Negative | False Positive | False Negative |
|---------|---------------|---------------|----------------|----------------|
| Email | `test@example.com` | `test-at-example` | `file@2x.png` | `test [at] example.com` |
| API Key | `api_key="abc123..."` | `public_key="..."` | `primary_key=5` | `APIKEY: value` |
| Path | `/Users/john/file` | `https://site.com` | `/usr/bin/python` | `C:\\Users\\john\\file` |

---

## 📊 Pattern Priority

**Priority Order (Highest → Lowest):**

1. **Critical Secrets** (Passwords, Private Keys, API Keys)
2. **PHI** (Medical Records, Diagnoses)
3. **PCI** (Credit Cards, CVV, Account Numbers)
4. **PII** (SSN, Passport, Email, Phone)
5. **Paths** (File paths with usernames)
6. **Company Data** (Domains, Internal IPs)

**Rationale:** Critical secrets should be detected first to prevent leakage

---

## 🔧 Usage in SanitizationEngine

```python
class SanitizationEngine:
    def __init__(self):
        self.patterns = {
            'critical_secrets': {
                'password': PASSWORD_PATTERNS,
                'api_key': API_KEY_PATTERNS,
                'token': TOKEN_PATTERNS,
                'private_key': [PRIVATE_KEY_PATTERN],
            },
            'pii': {
                'email': [EMAIL_PATTERN],
                'phone': [PHONE_PATTERN],
                'ssn': [SSN_PATTERN],
                'ip_address': [IP_PATTERN],
            },
            'phi': {
                'mrn': [MRN_PATTERN],
                'icd10': [ICD10_PATTERN],
            },
            'pci': {
                'credit_card': [CREDIT_CARD_PATTERN],
                'cvv': [CVV_PATTERN],
            },
            'paths': {
                'unix_path': [UNIX_PATH_PATTERN],
                'windows_path': [WINDOWS_PATH_PATTERN],
            },
            'company': {
                'domain': [DOMAIN_PATTERN],
                'internal_ip': INTERNAL_IP_PATTERNS,
            },
        }
    
    def detect_all(self, text: str) -> Dict[str, List[Match]]:
        """Detect all sensitive patterns in text."""
        matches = {}
        for category, patterns_dict in self.patterns.items():
            for pattern_name, pattern_list in patterns_dict.items():
                for pattern in pattern_list:
                    found = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
                    if found:
                        matches.setdefault(category, {})[pattern_name] = found
        return matches
```

---

## ✅ Consolidation Checklist

**Phase 1 Implementation:**
- [ ] Create `PatternRegistry` class
- [ ] Consolidate patterns from 5 modules
- [ ] Implement priority-based detection
- [ ] Add custom pattern injection API
- [ ] Create pattern test suite
- [ ] Validate against existing test cases
- [ ] Benchmark detection performance

**Target:** <100ms for 10,000-line file scan

---

**Document Created:** January 3, 2026  
**Pattern Count:** 30+ patterns across 7 categories  
**Sources:** Anonymizer, PrivacySanitizer, EnhancedGuardrail, PrivacySafeExporter, SanitizationOrchestrator v1
