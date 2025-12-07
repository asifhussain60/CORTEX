# Security Collector Enhancement Plan

**Purpose:** Document comprehensive security scan improvements based on test-driven findings  
**Author:** Asif Hussain  
**Date:** 2025-12-07

---

## Test Results Baseline (RED Phase)

**Total Tests:** 22  
**Passing:** 6 (27%)  
**Failing:** 16 (73%)

### ✅ Passing Tests (Already Working)
1. SQL Injection: String concatenation detection
2. SQL Injection: String interpolation detection  
3. SQL Injection: String.Format detection
4. XSS: Response.Write without HtmlEncode (partial)
5. Hardcoded Secrets: JWT token detection
6. Insecure Deserialization: BinaryFormatter detection

### ❌ Failing Tests (Need Implementation)

**XSS Scans (5 failures):**
- `innerHTML` assignments in JavaScript
- `document.write()` with user input
- jQuery `.html()` method usage
- `eval()` / `Function()` constructor
- ASPX `<%= %>` without encoding

**Hardcoded Secrets (4 failures):**
- Basic Auth headers (`Authorization: Basic ...`)
- AWS access keys (AKIAIOSFODNN...)
- Azure connection strings (AccountKey=...)
- Private keys in PEM files

**Weak Cryptography (4 failures):**
- MD5 usage (detected but wrong key in findings)
- SHA1 usage (detected but wrong key in findings)
- DES/3DES usage (not detected)
- ECB mode configuration (not detected)

**Insecure Deserialization (1 failure):**
- TypeNameHandling.All in JSON.NET

**Input Validation (2 failures):**
- Unvalidated redirects (`Response.Redirect(Request.QueryString[...])`)
- Path traversal (`Path.Combine` with user input)

---

## Pattern Additions Required

### 1. XSS Scan Enhancements

**Current Issues:**
- Only scans `.cs` and `.aspx` files (misses `.js`, `.cshtml`, `.html`)
- File-level HtmlEncode check (false negatives if HtmlEncode exists anywhere)
- Line 267: Redundant `for file in [file]:` loop

**New Patterns to Add:**
```python
# JavaScript file patterns (.js, .cshtml, .html)
js_xss_patterns = [
    (r'\.innerHTML\s*=', "innerHTML Assignment", "high"),
    (r'document\.write\(', "document.write Usage", "high"),
    (r'\$\(.+?\)\.html\(', "jQuery html() Method", "high"),
    (r'eval\(', "eval() Usage", "critical"),
    (r'new\s+Function\(', "Function Constructor", "critical"),
    (r'\.outerHTML\s*=', "outerHTML Assignment", "high"),
    (r'insertAdjacentHTML\(', "insertAdjacentHTML Usage", "medium"),
]

# ASPX/Razor patterns (.aspx, .cshtml)
aspx_xss_patterns = [
    (r'<%=\s*Request\.(QueryString|Form|Params)', "ASPX Output Without Encoding", "high"),
    (r'@Html\.Raw\(', "Razor Html.Raw Without Sanitization", "high"),
    (r'Response\.Output\.Write\(', "Response.Output.Write Without Encoding", "high"),
]

# .NET code patterns (.cs)
cs_xss_patterns = [
    (r'Response\.Write\([^)]*Request\.(QueryString|Form|Params)', "Response.Write with User Input", "high"),
    (r'Response\.Write\([^)]*\w+\)', "Response.Write Without HtmlEncode", "medium"),  # Context-aware
]
```

**File Extension Mapping:**
- `.js` → JavaScript patterns
- `.cshtml` → JavaScript + ASPX/Razor patterns
- `.html` → JavaScript patterns
- `.aspx` → ASPX/Razor patterns
- `.cs` → .NET code patterns

### 2. Hardcoded Secrets Enhancements

**Current Patterns (working):**
```regex
password|pwd|api_key|secret|token|connectionString
```

**New Patterns to Add:**
```python
secret_patterns = [
    # Existing (working)
    (r'(password|pwd)\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded Password", "high"),
    (r'(api_key|apiKey)\s*=\s*["\'][^"\']+["\']', "API Key", "high"),
    (r'(secret|Secret)\s*=\s*["\'][^"\']+["\']', "Hardcoded Secret", "high"),
    (r'token\s*=\s*["\'][^"\']+["\']', "Hardcoded Token", "medium"),
    (r'connectionString\s*=\s*["\'][^"\']+["\']', "Connection String", "medium"),
    
    # New patterns
    (r'Authorization["\']?\s*:\s*["\']?Basic\s+[A-Za-z0-9+/=]{20,}', "Basic Auth Header", "critical"),
    (r'AKIA[0-9A-Z]{16}', "AWS Access Key", "critical"),
    (r'AccountKey\s*=\s*[A-Za-z0-9+/=]{40,}', "Azure Storage Key", "critical"),
    (r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----', "Private Key in PEM", "critical"),
    (r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}', "JWT Token", "high"),  # Already working
    (r'sk_live_[0-9a-zA-Z]{24,}', "Stripe Secret Key", "critical"),
    (r'ghp_[0-9a-zA-Z]{36}', "GitHub Personal Access Token", "critical"),
]
```

**File Extensions to Scan:**
- `.cs`, `.config`, `.xml`, `.json`, `.yml`, `.yaml`, `.env`, `.pem`, `.key`

### 3. Weak Cryptography Enhancements

**Current Issues:**
- MD5/SHA1 detected but findings dict has wrong keys (`"type"` instead of `"description"`)
- Weak regex: `SHA1(?!256)` misses `SHA1Managed`, `HMACSHA1`
- Missing DES/3DES detection
- Missing ECB mode detection

**Fixed Patterns:**
```python
crypto_patterns = [
    # Hashing
    (r'\bMD5\b|MD5CryptoServiceProvider|MD5\.Create', "MD5 Weak Hashing", "high"),
    (r'\bSHA1\b|SHA1Managed|HMACSHA1|SHA1CryptoServiceProvider', "SHA1 Weak Hashing", "high"),
    
    # Encryption
    (r'\bDES\b|DESCryptoServiceProvider|DES\.Create', "DES Weak Encryption", "critical"),
    (r'TripleDES|3DES|TripleDESCryptoServiceProvider', "3DES Weak Encryption", "high"),
    (r'RC2|RC4', "RC2/RC4 Weak Encryption", "high"),
    
    # Cipher Mode
    (r'CipherMode\.ECB', "ECB Mode Insecure", "high"),
    
    # Random
    (r'new\s+Random\(\)', "Weak Random Number Generator", "medium"),
]
```

**Assertion Fix:**
```python
# Test checks for "cryptography" in type OR "MD5" in description
# Current code sets: findings.append({"type": "Weak Hashing Algorithm", ...})
# Tests expect: "cryptography" in f['type'].lower() OR "MD5" in f.get('description', '')
# Solution: Add "Cryptography" to type field
{"type": "Weak Cryptography - MD5 Hashing", ...}
```

### 4. Insecure Deserialization Enhancements

**Current Patterns (working):**
```regex
BinaryFormatter|SoapFormatter|NetDataContractSerializer
```

**New Patterns to Add:**
```python
deser_patterns = [
    # Existing
    (r'BinaryFormatter|SoapFormatter|NetDataContractSerializer', "Insecure Binary Deserialization", "critical"),
    
    # New
    (r'TypeNameHandling\s*=\s*TypeNameHandling\.(All|Auto)', "JSON.NET TypeNameHandling Insecure", "high"),
    (r'JavaScriptSerializer|__type', ".NET JavaScriptSerializer Type Handling", "high"),
    (r'ObjectStateFormatter', "ObjectStateFormatter Insecure", "high"),
]
```

### 5. Input Validation Enhancements

**Current Patterns (working):**
```regex
Request.(QueryString|Form|Params)\[ without validation in context
```

**New Patterns to Add:**
```python
validation_patterns = [
    # Unvalidated Redirects
    (r'Response\.Redirect\([^)]*Request\.(QueryString|Form|Params)\[', "Unvalidated Open Redirect", "high"),
    (r'Response\.Redirect\([^)]*\)', "Potential Open Redirect", "medium"),  # Needs context
    
    # Path Traversal
    (r'Path\.Combine\([^)]*Request\.(QueryString|Form|Params)\[', "Path Traversal Vulnerability", "high"),
    (r'File\.(Read|Write|Open|Delete)\([^)]*Request\.', "File Operation with User Input", "high"),
    (r'Directory\.(Create|Delete|Move)\([^)]*Request\.', "Directory Operation with User Input", "high"),
    
    # Command Injection
    (r'Process\.Start\([^)]*Request\.', "Command Injection Risk", "critical"),
    (r'cmd\.exe|powershell\.exe.*Request\.', "Shell Command with User Input", "critical"),
]
```

---

## Implementation Plan

### Phase 1: Fix XSS Scanner (5 tests)
1. Add file extension detection (`.js`, `.cshtml`, `.html`, `.aspx`)
2. Remove redundant loop (line 267)
3. Add JavaScript-specific patterns
4. Add ASPX/Razor-specific patterns
5. Fix Response.Write context-aware detection

### Phase 2: Fix Hardcoded Secrets (4 tests)
1. Add AWS key regex pattern
2. Add Azure key regex pattern  
3. Add Basic Auth header pattern
4. Expand file extensions to `.pem`, `.key`, `.env`

### Phase 3: Fix Weak Cryptography (4 tests)
1. Fix MD5/SHA1 regex (word boundaries, Managed variants)
2. Add DES/3DES patterns
3. Add ECB mode pattern
4. Fix findings dict keys (add "Cryptography" to type field)

### Phase 4: Fix Deserialization (1 test)
1. Add TypeNameHandling.All/Auto pattern

### Phase 5: Fix Input Validation (2 tests)
1. Add unvalidated redirect pattern
2. Add path traversal pattern
3. Add command injection patterns

---

## Expected Outcome

**After Fixes:**
- ✅ 22/22 tests passing (100%)
- ✅ Comprehensive vulnerability detection for .NET projects
- ✅ Reduced false negatives (luum-fresh XSS should be detected)
- ✅ Ready for production collection on luum-fresh

**Performance Impact:**
- JavaScript file scanning adds ~5-10% overhead
- PEM/key file scanning minimal (few files)
- Overall: <15% increase in scan time (acceptable for accuracy gain)

---

## Next Steps

1. Implement Phase 1-5 fixes in `security_collector.py`
2. Run `pytest tests/test_security_collector_comprehensive.py`
3. Verify 22/22 passing
4. Run luum-fresh collection with `--skip-consolidation`
5. Validate XSS vulnerabilities detected
6. Document findings in dashboard
