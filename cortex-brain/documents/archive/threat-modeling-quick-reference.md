# Threat Modeling Integration - Quick Reference

**Version:** 1.0  
**Last Updated:** 2025-12-01  
**Author:** Asif Hussain

---

## 🎯 Quick Start

```
User: "plan authentication feature"
CORTEX:
  ✅ DoR validation passed
  🔒 Running threat analysis...
  ✅ Identified 8 threats (2 Critical, 3 High, 3 Medium)
  ✅ Plan created with security section
```

---

## 📋 Commands

### Basic Commands
```bash
# Analyze threats for any feature
"analyze threats for [feature description]"

# Show quick threat summary
"show threats"

# Show detailed threat report
"detailed threat report"

# Show security DoD checklist
"security checklist"

# Validate security DoD items
"validate security"
```

### Planning Commands
```bash
# Plan with automatic threat modeling
"plan [feature name]"

# Plan from ADO work item (includes threats)
"plan ado [work item ID]"

# Resume plan (threats preserved)
"resume plan [plan name]"
```

---

## 🛡️ STRIDE Framework

| Category | Focus | Example Threat |
|----------|-------|---------------|
| **S**poofing | Identity verification | Weak password storage |
| **T**ampering | Data integrity | SQL injection |
| **R**epudiation | Audit trails | Missing logging |
| **I**nformation Disclosure | Data confidentiality | Sensitive data exposure |
| **D**enial of Service | Availability | Rate limiting bypass |
| **E**levation of Privilege | Authorization | Broken access control |

---

## 🎨 Feature Types & Templates

### Authentication Features
**Keywords:** login, signup, password, session, authentication, OAuth, SSO, JWT

**Common Threats:**
- Weak password storage (CRITICAL)
- Session hijacking (HIGH)
- Brute force attacks (HIGH)
- Missing MFA (CRITICAL)

**Mitigations:**
- Argon2id/bcrypt password hashing
- TOTP-based multi-factor authentication
- Secure session management (15-min timeout)
- Account lockout after 5 failed attempts

---

### API Features
**Keywords:** API, REST, endpoint, GraphQL, service, microservice

**Common Threats:**
- Broken authentication (CRITICAL)
- Excessive data exposure (HIGH)
- Missing rate limiting (MEDIUM)
- SQL injection (CRITICAL)

**Mitigations:**
- JWT with short expiration (15 minutes)
- Field-level authorization checks
- Rate limiting (100 requests/min per IP)
- Parameterized queries with ORM

---

### Data Storage Features
**Keywords:** database, storage, SQL, NoSQL, schema, persistence

**Common Threats:**
- SQL injection (CRITICAL)
- Insecure data at rest (HIGH)
- Missing encryption (HIGH)
- Sensitive data exposure (CRITICAL)

**Mitigations:**
- ORM with parameterized queries
- AES-256 encryption for sensitive data
- Column-level encryption for PII
- Secure key management (Azure Key Vault)

---

### File Upload Features
**Keywords:** upload, file, attachment, image, document, media

**Common Threats:**
- Malicious file upload (CRITICAL)
- Path traversal (HIGH)
- Unrestricted file types (HIGH)
- DoS via large files (MEDIUM)

**Mitigations:**
- File type whitelist (validation)
- Antivirus scanning on upload
- Content type verification
- File size limits (10MB max)
- Secure storage with random filenames

---

### Payment Processing
**Keywords:** payment, checkout, billing, credit card, subscription, transaction

**Common Threats:**
- PCI-DSS compliance gaps (CRITICAL)
- Payment data exposure (CRITICAL)
- Transaction tampering (HIGH)
- Insecure gateway integration (HIGH)

**Mitigations:**
- Use PCI-compliant payment gateway (Stripe, PayPal)
- Never store credit card data locally
- HTTPS for all payment operations
- Transaction integrity checks

---

## 🔴 Risk Ratings

| Rating | Criteria | Action Required |
|--------|----------|-----------------|
| **CRITICAL** | High impact + High likelihood | Must fix before release |
| **HIGH** | High impact OR High likelihood | Must fix before release |
| **MEDIUM** | Medium impact/likelihood | Should fix (not blocking) |
| **LOW** | Low impact + Low likelihood | Nice to have |

---

## 📊 OWASP Top 10 2021 Mapping

| Code | Category | Example Threat |
|------|----------|---------------|
| A01 | Broken Access Control | Missing authorization checks |
| A02 | Cryptographic Failures | Weak password hashing |
| A03 | Injection | SQL injection |
| A04 | Insecure Design | Missing threat modeling |
| A05 | Security Misconfiguration | Default credentials |
| A06 | Vulnerable Components | Outdated dependencies |
| A07 | Authentication Failures | Weak password policy |
| A08 | Data Integrity Failures | Unsigned code execution |
| A09 | Logging Failures | Missing audit logs |
| A10 | SSRF | Unvalidated URL redirects |

---

## 📁 Output Locations

### Planning Document
```
Location: cortex-brain/documents/planning/active/[plan-name].md
Section: ## Security Threat Analysis
Includes: All threats, mitigations, risk ratings, OWASP mapping
```

### Threat Report
```
Location: cortex-brain/documents/reports/threat-analysis-[feature-name].md
Format: Standalone detailed report
Includes: Full STRIDE breakdown, code examples, test recommendations
```

### DoD Checklist
```
Location: Integrated into plan document
Section: ## Definition of Done - Security
Includes: Critical/High threat checklists, security testing requirements
```

---

## 🧪 Testing Integration

### Auto-Generated Security Tests

For each identified threat, CORTEX recommends:

**Input Validation Tests:**
```csharp
[Fact]
public void Login_RejectsEmptyPassword()
{
    // Test validates against weak password threat
    var result = authService.Login("user@test.com", "");
    Assert.False(result.Success);
}
```

**Authentication Tests:**
```csharp
[Fact]
public void ProtectedEndpoint_RequiresAuthentication()
{
    // Test validates against broken access control
    var response = client.GetAsync("/api/protected").Result;
    Assert.Equal(HttpStatusCode.Unauthorized, response.StatusCode);
}
```

**Injection Prevention Tests:**
```csharp
[Fact]
public void Search_PreventsSQLInjection()
{
    // Test validates against SQL injection
    var result = repository.Search("'; DROP TABLE Users--");
    Assert.NotNull(result); // Should not throw or execute malicious SQL
}
```

---

## ⚡ Performance

- **Analysis Time:** <3 seconds for typical feature (requirement met)
- **Threat Detection:** 100+ security keywords, 5 feature templates
- **Mitigation Database:** 8+ strategies with code examples
- **OWASP Coverage:** All Top 10 2021 categories

---

## 🔄 Workflow Integration

### Planning Workflow with Threats
```
1. User: "plan authentication"
2. CORTEX: DoR validation
3. CORTEX: Generate plan skeleton (user approves)
4. CORTEX: Run threat analysis (STRIDE)
5. CORTEX: Fill Phase 1 sections (user approves)
6. CORTEX: Integrate threats into plan
7. CORTEX: Fill Phase 2 & 3 sections
8. CORTEX: Update DoD with threat mitigations
9. CORTEX: Generate standalone threat report
10. CORTEX: Validate DoD (including security)
11. User: "approve plan"
```

**Checkpoints:**
- Skeleton approval
- Phase 1 approval
- Phase 2 approval
- Phase 3 approval
- DoD validation

---

## 💡 Examples

### Example 1: Authentication Feature

**Input:**
```
"plan user authentication with JWT tokens"
```

**Output:**
```markdown
## Security Threat Analysis

**Total Threats:** 8
**Risk Distribution:** 2 Critical, 3 High, 3 Medium

### Critical Threats
1. Weak Password Storage (Spoofing)
   - Risk: CRITICAL
   - OWASP: A02:2021
   - Mitigation: Argon2id with salt
   
2. Missing MFA (Spoofing)
   - Risk: CRITICAL
   - OWASP: A07:2021
   - Mitigation: TOTP-based MFA

### Definition of Done - Security
☐ Argon2id password hashing implemented
☐ TOTP MFA enabled for all accounts
☐ Session timeout 15 minutes
☐ Account lockout after 5 attempts
☐ All security tests passing (12/12)
```

---

### Example 2: API Feature

**Input:**
```
"plan REST API for customer data"
```

**Output:**
```markdown
## Security Threat Analysis

**Total Threats:** 6
**Risk Distribution:** 2 Critical, 2 High, 2 Medium

### Critical Threats
1. Broken Authentication (Spoofing)
   - Risk: CRITICAL
   - OWASP: A07:2021
   - Mitigation: JWT with 15-min expiration
   
2. SQL Injection (Injection)
   - Risk: CRITICAL
   - OWASP: A03:2021
   - Mitigation: Parameterized queries with EF Core

### Definition of Done - Security
☐ JWT authentication implemented
☐ Rate limiting (100 req/min per IP)
☐ Input validation for all endpoints
☐ SQL injection tests passing
☐ Authorization tests passing
```

---

## 🎯 Best Practices

### 1. Address Critical Threats First
Always fix CRITICAL threats before release. No exceptions.

### 2. Include Security in DoR
Add "Security requirements identified" to Definition of Ready.

### 3. Write Security Tests
For each threat, write at least one test validating the mitigation.

### 4. Review OWASP Mapping
Use OWASP categories to ensure comprehensive coverage.

### 5. Update Threat Model
Re-run threat analysis when:
- Feature scope changes significantly
- New attack vectors emerge
- Security incidents occur

### 6. Document Mitigations
In planning document, include:
- Mitigation strategy
- Implementation code
- Test coverage
- Deployment notes

---

## 🆘 Troubleshooting

### No Threats Identified
**Cause:** Generic feature description  
**Fix:** Add more details (e.g., "API" instead of "service")

### Wrong Feature Type Detected
**Cause:** Ambiguous keywords  
**Fix:** Use explicit feature type keywords (authentication, API, etc.)

### Missing Mitigations
**Cause:** Threat not in database  
**Fix:** Manually add mitigation in planning document

### Performance Slow (>3 seconds)
**Cause:** Very long feature description  
**Fix:** Break into smaller features or summarize description

---

## 📚 Related Documentation

- **Planning System Guide:** `.github/prompts/modules/planning-orchestrator-guide.md`
- **TDD Mastery Guide:** `.github/prompts/modules/tdd-mastery-guide.md`
- **Workflow Definition:** `workflows/planning_with_threats.yaml`
- **Response Templates:** `cortex-brain/response-templates.yaml` (search "threat")

---

**Questions?** Say "help threat modeling" in Copilot Chat

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**GitHub:** github.com/asifhussain60/CORTEX
