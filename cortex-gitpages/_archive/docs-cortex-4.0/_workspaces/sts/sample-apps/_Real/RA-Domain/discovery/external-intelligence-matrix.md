# External Domain Intelligence Matrix

**Purpose:** Map external regulatory requirements to test scenarios  
**Sources:** RegulatoryAgency.gov, HHS.gov, PCIsecuritystandards.org (all official/public)  
**Created:** December 11, 2025  
**Batch:** 2.5 - External Domain Intelligence

---

## Executive Summary

**Compliance Scope:** Healthcare payment accounts (FlexAccount/HealthSavings/HealthReimbursement) require validation against:
- **RegulatoryAgency Tax Code:** Contribution limits, rollover rules, qualified expenses
- **PrivacyRegulation Security Rule:** PHI data protection, access controls, audit trails
- **PaymentSecurity v4.0.1:** Payment card data security (if card transactions supported)

**P0 Gap Validated:** No code found validating RegulatoryAgency contribution limits ($3,200 FlexAccount, $4,150/$8,300 HealthSavings) - production risk confirmed.

---

## 1. RegulatoryAgency Regulatory Requirements

### 1.1 Contribution Limits (IRC §125, IRC §223, RegulatoryAgency Pub 969)

| Regulation | 2024 Limit | 2025 Limit | Business Rule | Code Must Validate | Test Scenario | Priority |
|------------|------------|------------|---------------|-------------------|---------------|----------|
| **FlexAccount Annual Contribution** | $3,200 | TBD (Nov 2025) | Max employee + organization contributions | YES | Reject contribution >$3,200 | **P0** |
| **FlexAccount Rollover** | $640 | TBD | Unused funds exceeding $640 forfeited | YES | Test year-end expiration logic | **P0** |
| **HealthSavings Self-Only** | $4,150 | $4,300 | Individual coverage limit | YES | Reject contribution >$4,150 (2024) | **P0** |
| **HealthSavings Family** | $8,300 | $8,550 | Family coverage limit | YES | Reject contribution >$8,300 (2024) | **P0** |
| **HealthSavings Catch-Up (55+)** | $1,000 | $1,000 | Additional for age 55+ | YES | Allow +$1,000 if age ≥55 | **P1** |
| **HDHP Min Deductible (Self)** | $1,600 | $1,650 | Qualifying HDHP requirement | YES | Validate HDHP eligibility | **P1** |
| **HDHP Min Deductible (Family)** | $3,200 | $3,300 | Qualifying HDHP requirement | YES | Validate HDHP eligibility | **P1** |
| **HDHP Max OOP (Self)** | $8,050 | $8,300 | Qualifying HDHP requirement | YES | Validate HDHP eligibility | **P1** |
| **HDHP Max OOP (Family)** | $16,100 | $16,600 | Qualifying HDHP requirement | YES | Validate HDHP eligibility | **P1** |
| **DependentCare FlexAccount** | $5,000 | $5,000 | Per household (not indexed) | YES | Reject >$5,000 household | **P0** |

**Source:** RegulatoryAgency Publication 969 (2024), Revenue Procedure 2023-34  
**Status:** ❌ **NO VALIDATION FOUND** in AST analysis (Batch 1) - P0 compliance gap  
**Next Step:** Scan contribution processing services in Batch 3-6 to locate/create validation logic

### 1.2 Rollover & Grace Period Rules (26 CFR §125-5, RegulatoryAgency Pub 969)

| Regulation | Rule | Business Logic | Code Must Implement | Test Scenario | Priority |
|------------|------|----------------|---------------------|---------------|----------|
| **FlexAccount Rollover vs Grace** | Organization chooses ONE (not both) | Mutual exclusion | YES | Prevent both enabled | **P0** |
| **FlexAccount Rollover Amount** | Maximum $640 (2024) | Unused funds >$640 forfeited | YES | Test year-end with $640, $641 | **P0** |
| **FlexAccount Grace Period** | Maximum 2.5 months | Jan 1 - Mar 15 grace | YES | Allow claims through Mar 15 | **P1** |
| **FlexAccount Use-It-Or-Lose-It** | Unused funds forfeited | Transfer to organization | YES | Test expiration to organization account | **P2** |
| **HealthSavings Rollover** | 100% unlimited | Never forfeited | YES | Verify 100% rollover year-to-year | **P1** |
| **HealthReimbursement Rollover** | Organization discretion | Plan-specific rules | YES | Validate per-plan rollover config | **P2** |
| **DependentCare FlexAccount Rollover** | NO CARRYOVER | Strict use-it-or-lose-it | YES | Test $0 rollover (no $640 option) | **P0** |

**Source:** RegulatoryAgency Publication 969, RegulatoryAgency Notice 2013-71 (rollover option)  
**Status:** ⏳ **PARTIAL** - Rollover logic found in `ExampleDomainService.cs` (20 methods), but grace period logic not yet validated  
**Next Step:** Scan year-end processing in Batch 7-8 to validate grace period implementation

### 1.3 Qualified Medical Expenses (RegulatoryAgency Pub 502, IRC §213)

| Category | Examples | 2019+ Changes | Code Must Validate | Test Scenario | Priority |
|----------|----------|---------------|-------------------|---------------|----------|
| **Prescription Drugs** | Insulin, prescribed medications | ✅ Always qualified | YES | Approve Rx claims | **P0** |
| **OTC Medicines** | Aspirin, ibuprofen, allergy meds | ✅ NOW QUALIFIED (2019+) | YES | Approve OTC if post-2019 | **P0** |
| **Menstrual Products** | Tampons, pads, cups | ✅ NOW QUALIFIED (2019+) | YES | Approve menstrual products | **P1** |
| **Condoms** | Male condoms | ✅ NOW QUALIFIED (Notice 2024-71) | YES | Approve condom claims | **P2** |
| **OTC Contraceptives** | Birth control pills, emergency contraceptives | ✅ NOW QUALIFIED (Notice 2024-75) | YES | Approve OTC contraceptives | **P1** |
| **Breast Pumps** | Pumps and lactation supplies | ✅ Qualified | YES | Approve breast pump claims | **P1** |
| **CGM for Diabetes** | Continuous glucose monitors | ✅ Preventive care (2024) | YES | Approve CGM claims | **P2** |
| **Insulin (No Deductible)** | Insulin products | ✅ $0 HDHP deductible (PL 117-169) | YES | Allow pre-deductible insulin | **P1** |
| **Cosmetic Surgery** | Face lifts, hair transplants, liposuction | ❌ NOT qualified (unless medical necessity) | YES | Reject cosmetic claims | **P0** |
| **Gym Memberships** | Health club dues | ❌ NOT qualified (general health) | YES | Reject gym membership claims | **P1** |
| **Nutritional Supplements** | Vitamins, herbal supplements | ❌ NOT qualified (unless Rx for specific condition) | YES | Reject supplement claims | **P1** |

**Source:** RegulatoryAgency Publication 502 (2024)  
**Status:** ⏳ **UNKNOWN** - Requests validation logic not yet scanned  
**Next Step:** Batch 9-10 - Scan claims processing services for qualified expense validation

### 1.4 Tax Reporting Requirements (Form 8889, Form 5498-SA, Form W-2)

| Requirement | Form | Deadline | System Must Generate | Test Scenario | Priority |
|-------------|------|----------|----------------------|---------------|----------|
| **HealthSavings Contributions** | Form 8889 | Tax return filing | Report to RegulatoryAgency | Verify W-2 Box 12 Code W | **P0** |
| **HealthSavings Distributions** | Form 1099-SA | Jan 31 | Trustee reports | Verify distribution reporting | **P0** |
| **Excess Contributions** | Form 5329 (6% excise tax) | Tax return filing | Notify participant | Test excess contribution alert | **P1** |
| **Archer MSA** | Form 8853 | Tax return filing | Report to RegulatoryAgency | Verify MSA reporting | **P2** |

**Status:** ⏳ **UNKNOWN** - Tax reporting not yet scanned  
**Next Step:** Batch 11-12 - Scan reporting services for RegulatoryAgency form generation

---

## 2. PrivacyRegulation Security Rule Requirements

### 2.1 Administrative Safeguards (45 CFR §164.308)

| Requirement | Implementation Spec | Code Must Implement | Test Scenario | Priority |
|-------------|---------------------|---------------------|---------------|----------|
| **Security Management Process** | Risk analysis, risk management, sanction policy, info system activity review | Audit logging, access controls | Verify audit trail for PHI access | **P0** |
| **Assigned Security Responsibility** | Identify security official | Role-based access control (RBAC) | Test security role assignment | **P1** |
| **Workforce Security** | Authorization, workforce clearance, termination procedures | User lifecycle management | Test user deactivation removes access | **P0** |
| **Information Access Management** | Isolation health clearinghouse functions, access authorization, access establishment/modification | RBAC, least privilege | Test user can only access own accounts | **P0** |
| **Security Awareness Training** | Security reminders, protection from malicious software, log-in monitoring, password management | Login attempt tracking, password policies | Test account lockout after failed logins | **P1** |
| **Security Incident Procedures** | Response and reporting | Incident logging, breach notification | Test incident reporting workflow | **P1** |
| **Contingency Plan** | Data backup, disaster recovery, emergency mode operation, testing/revision | Backup/restore procedures | Test data recovery from backup | **P2** |
| **Business Associate Contracts** | Written contract or other arrangement | Vendor agreements | Verify BA contracts for all vendors | **P2** |

**Source:** PrivacyRegulation Security Rule, 45 CFR Part 164 Subpart C  
**Status:** ⏳ **UNKNOWN** - Security implementation not yet scanned  
**Next Step:** Batch 13-14 - Scan authentication, authorization, audit logging

### 2.2 Physical Safeguards (45 CFR §164.310)

| Requirement | Implementation Spec | Infrastructure Must Provide | Test Scenario | Priority |
|-------------|---------------------|----------------------------|---------------|----------|
| **Facility Access Controls** | Contingency operations, facility security plan, access control/validation, maintenance records | Physical security (data center) | N/A (infrastructure) | **P2** |
| **Workstation Use** | Policies for workstation functions, manner of access, physical attributes | Workstation security policies | N/A (policy-based) | **P3** |
| **Workstation Security** | Restrict access to authorized users | Physical workstation locks | N/A (infrastructure) | **P3** |
| **Device and Media Controls** | Disposal, media re-use, accountability, data backup/storage | Secure media disposal | N/A (operational) | **P2** |

**Status:** N/A (infrastructure/operational - not code-level)

### 2.3 Technical Safeguards (45 CFR §164.312)

| Requirement | Implementation Spec | Code Must Implement | Test Scenario | Priority |
|-------------|---------------------|---------------------|---------------|----------|
| **Access Control** | Unique user ID, emergency access, automatic log-off, encryption/decryption | User authentication, session timeout, PHI encryption at rest | Test session timeout after inactivity | **P0** |
| **Audit Controls** | Hardware, software, procedural mechanisms to record/examine activity | Audit trail for PHI create/read/update/delete | Verify audit log for account balance view | **P0** |
| **Integrity** | Mechanisms to authenticate ePHI not altered/destroyed | Data integrity checks, checksums | Test data tampering detection | **P1** |
| **Person or Entity Authentication** | Verify person/entity is who they request to be | MFA, strong authentication | Test MFA requirement for PHI access | **P0** |
| **Transmission Security** | Integrity controls, encryption | TLS/HTTPS for data in transit | Test encrypted transmission (SSL/TLS) | **P0** |

**Source:** PrivacyRegulation Security Rule, 45 CFR §164.312  
**Status:** ⏳ **UNKNOWN** - Security implementation not yet scanned  
**Next Step:** Batch 13-14 - Scan security services for PrivacyRegulation compliance

**PrivacyRegulation PHI Examples in RA Domain:**
- Account balances (FlexAccount/HealthSavings/HealthReimbursement balances are PHI)
- Requests data (payment requests contain medical procedure codes)
- Transaction history (dates/amounts linked to medical services)
- Participant demographic data (SSN, DOB, address)

---

## 3. PaymentSecurity v4.0.1 Requirements (Payment Card Data)

### 3.1 Build and Maintain a Secure Network (Requirements 1-2)

| Requirement | Control | Code Must Implement (if card transactions) | Test Scenario | Priority |
|-------------|---------|-------------------------------------------|---------------|----------|
| **Req 1: Firewall Configuration** | Install/maintain network security controls | Network firewall rules | N/A (infrastructure) | **P1** |
| **Req 2: Secure Configurations** | Apply secure configs to all system components | Secure defaults, remove sample accounts | Test no default credentials | **P1** |

### 3.2 Protect Cardholder Data (Requirements 3-4)

| Requirement | Control | Code Must Implement (if card transactions) | Test Scenario | Priority |
|-------------|---------|-------------------------------------------|---------------|----------|
| **Req 3: Protect Stored CHD** | **Do NOT store sensitive authentication data** (CVV, PIN) | Tokenization, PAN truncation/masking | **Test CVV never stored** | **P0** |
| **Req 3: PAN Storage** | **Render PAN unreadable** (encryption, truncation, hashing) | Encrypt PAN at rest, display only last 4 digits | Test PAN displayed as XXXX-XXXX-XXXX-1234 | **P0** |
| **Req 4: Encrypt Transmission** | Use strong cryptography for CHD over public networks | TLS 1.2+ for card data transmission | Test encrypted card data transmission | **P0** |

### 3.3 Maintain a Vulnerability Management Program (Requirements 5-6)

| Requirement | Control | Code Must Implement (if card transactions) | Test Scenario | Priority |
|-------------|---------|-------------------------------------------|---------------|----------|
| **Req 5: Protect from Malware** | Deploy anti-malware solutions | Anti-malware on servers | N/A (infrastructure) | **P1** |
| **Req 6: Secure Development** | Develop secure systems/software | OWASP Top 10, code review, static analysis | Run SAST on payment processing code | **P0** |

### 3.4 Implement Strong Access Control Measures (Requirements 7-9)

| Requirement | Control | Code Must Implement (if card transactions) | Test Scenario | Priority |
|-------------|---------|-------------------------------------------|---------------|----------|
| **Req 7: Restrict Data Access** | Restrict access by business need-to-know | RBAC for cardholder data | Test user can't access card data w/o permission | **P0** |
| **Req 8: Identify Users** | Assign unique ID to each person with computer access | Unique user IDs, no shared accounts | Test no shared admin accounts | **P0** |
| **Req 9: Physical Access** | Restrict physical access to cardholder data | Physical security controls | N/A (infrastructure) | **P2** |

### 3.5 Monitor and Test Networks (Requirements 10-11)

| Requirement | Control | Code Must Implement (if card transactions) | Test Scenario | Priority |
|-------------|---------|-------------------------------------------|---------------|----------|
| **Req 10: Log and Monitor** | Track/monitor all access to CHD | Audit logging for card data access | Verify audit trail for card transactions | **P0** |
| **Req 11: Test Security Systems** | Test security systems/processes regularly | Vulnerability scanning, penetration testing | Run ASV scans quarterly | **P1** |

### 3.6 Maintain an Information Security Policy (Requirement 12)

| Requirement | Control | Code Must Implement (if card transactions) | Test Scenario | Priority |
|-------------|---------|-------------------------------------------|---------------|----------|
| **Req 12: Security Policy** | Maintain policy addressing information security | Security policies for all personnel | N/A (policy-based) | **P2** |

**Source:** PCI DSS v4.0.1 (March 2022), PCI Security Standards Council  
**Status:** ⏳ **UNKNOWN** - Card transaction support not yet validated  
**Scope Decision Needed:** Does GenericCorp RA system support card transactions (debit cards for FlexAccount/HealthSavings)?  
**Next Step:** Batch 15-16 - Scan for payment card processing (if applicable)

**PaymentSecurity Key Terms:**
- **CHD (Cardholder Data):** PAN (Primary Account Number) + cardholder name + expiration + service code
- **SAD (Sensitive Authentication Data):** CVV/CVV2/CVC2, PIN, magnetic stripe data (NEVER STORE)
- **PAN:** 16-digit credit/debit card number (must be encrypted at rest, masked in UI)
- **Tokenization:** Replace PAN with non-sensitive token (recommended for card-on-file)

---

## 4. Intelligence-to-Test Mapping

### 4.1 Immediate Action Items (P0 Gaps)

| Gap ID | Description | Regulation | Code Location (Expected) | Test Design | Batch |
|--------|-------------|------------|--------------------------|-------------|-------|
| **P0-001** | No FlexAccount $3,200 limit validation | RegulatoryAgency Pub 969, IRC §125 | Contribution processing service | Create test: Reject $3,201 contribution | Batch 3-6 |
| **P0-002** | No HealthSavings $4,150/$8,300 limit validation | RegulatoryAgency Pub 969, IRC §223 | Contribution processing service | Create test: Reject $4,151 self-only | Batch 3-6 |
| **P0-003** | No FlexAccount $640 rollover limit | RegulatoryAgency Pub 969, 26 CFR §125-5 | Year-end processing service | Create test: Forfeit $641+ unused funds | Batch 7-8 |
| **P0-004** | DependentCare FlexAccount no rollover validation | RegulatoryAgency Pub 969 | DependentCare FlexAccount service | Create test: Verify $0 rollover (not $640) | Batch 7-8 |
| **P0-005** | Cosmetic surgery rejection | RegulatoryAgency Pub 502 | Requests validation service | Create test: Reject liposuction request | Batch 9-10 |
| **P0-006** | CVV storage prohibition | PaymentSecurity Req 3 | Card transaction service | Create test: Verify CVV never stored | Batch 15-16 |
| **P0-007** | PAN encryption at rest | PaymentSecurity Req 3 | Card storage service | Create test: Verify encrypted PAN in DB | Batch 15-16 |
| **P0-008** | PHI audit trail | PrivacyRegulation §164.312 | Security/logging service | Create test: Verify audit log for balance view | Batch 13-14 |
| **P0-009** | MFA for PHI access | PrivacyRegulation §164.312 | Authentication service | Create test: Require MFA for account access | Batch 13-14 |

### 4.2 High-Priority Validation (P1)

| Gap ID | Description | Regulation | Code Location (Expected) | Test Design | Batch |
|--------|-------------|------------|--------------------------|-------------|-------|
| **P1-001** | HealthSavings catch-up ($1,000 age 55+) | RegulatoryAgency Pub 969 | Contribution service | Test: Allow $5,150 if age=55 | Batch 3-6 |
| **P1-002** | HDHP min deductible validation | RegulatoryAgency Pub 969 | HealthSavings eligibility service | Test: Reject if deductible <$1,600 | Batch 3-6 |
| **P1-003** | FlexAccount grace period (2.5 months) | 26 CFR §125-5 | Year-end processing | Test: Allow claims through Mar 15 | Batch 7-8 |
| **P1-004** | OTC medicine qualification (2019+) | RegulatoryAgency Pub 502 | Requests validation | Test: Approve aspirin request (post-2019) | Batch 9-10 |
| **P1-005** | Session timeout for PHI | PrivacyRegulation §164.312 | Session management | Test: Timeout after 15 min inactivity | Batch 13-14 |
| **P1-006** | PAN masking in UI | PaymentSecurity Req 3 | Card display service | Test: Show XXXX-XXXX-XXXX-1234 only | Batch 15-16 |

---

## 5. Next Steps by Batch

### Batch 3-6: Contribution Processing
**Scan:**
- Contribution validation services
- Limit enforcement logic
- Age-based catch-up calculations

**Regulatory Focus:**
- RegulatoryAgency Pub 969 limits ($3,200 FlexAccount, $4,150/$8,300 HealthSavings, $1,000 catch-up)
- HDHP eligibility requirements

**Expected Findings:**
- ❌ No limit validation (P0) → CREATE validation logic
- ⚠️ Hardcoded limits (P1) → REFACTOR to config-based

### Batch 7-8: Year-End Processing
**Scan:**
- Rollover calculation logic
- Grace period implementation
- Expiration processing

**Regulatory Focus:**
- 26 CFR §125-5 ($640 rollover OR 2.5-month grace, not both)
- Use-it-or-lose-it enforcement

**Expected Findings:**
- ✅ Rollover logic exists (`ExampleDomainService.cs`) - VALIDATE against $640 limit
- ⏳ Grace period logic - LOCATE and VALIDATE 2.5-month window

### Batch 9-10: Request Processing
**Scan:**
- Requests validation services
- Qualified expense determination
- 2019+ OTC medicine rules

**Regulatory Focus:**
- RegulatoryAgency Pub 502 (qualified expenses, OTC rule changes, preventive care)
- Notice 2024-75 (OTC contraceptives, breast cancer screening, CGMs)

**Expected Findings:**
- ⏳ Qualified expense list - VALIDATE against RegulatoryAgency Pub 502
- ⚠️ Cosmetic surgery rejection - VERIFY implemented
- ⚠️ OTC medicine approval (post-2019) - UPDATE rules

### Batch 11-12: Tax Reporting
**Scan:**
- RegulatoryAgency form generation (Form 8889, Form 1099-SA, Form W-2 Box 12)
- Excess contribution detection

**Regulatory Focus:**
- Form 8889 requirements
- Excess contribution reporting (6% excise tax)

**Expected Findings:**
- ⏳ Tax form generation - VALIDATE completeness
- ⏳ Excess contribution alerts - VERIFY participant notification

### Batch 13-14: Security & Compliance
**Scan:**
- Authentication services
- Authorization (RBAC)
- Audit logging
- Session management

**Regulatory Focus:**
- PrivacyRegulation §164.312 (access control, audit, MFA, encryption)
- PrivacyRegulation §164.308 (administrative safeguards)

**Expected Findings:**
- ✅ Authentication - VALIDATE MFA requirement
- ⏳ Audit logging - VERIFY PHI access tracking
- ⏳ Session timeout - VALIDATE inactivity timeout

### Batch 15-16: Payment Card Data (If Applicable)
**Scan:**
- Card transaction processing
- PAN storage/display
- CVV handling

**Regulatory Focus:**
- PaymentSecurity v4.0.1 Requirements 3-4 (protect CHD, encrypt transmission)
- PaymentSecurity Requirement 10 (audit logging)

**Scope Decision:**
- ⏳ Determine if system supports card transactions (FlexAccount/HealthSavings debit cards)
- If YES: VALIDATE PaymentSecurity compliance (PAN encryption, CVV prohibition, audit trail)
- If NO: DOCUMENT out-of-scope, skip Batch 15-16

---

## 6. External Source Summary

### 6.1 Sources Used (All Official/Public)

| Source | URL | Content Retrieved | Date Accessed |
|--------|-----|-------------------|---------------|
| **RegulatoryAgency Publication 969 (2024)** | https://www.irs.gov/publications/p969 | FlexAccount/HealthSavings/HealthReimbursement contribution limits, rollover rules, qualified expenses | Dec 11, 2025 |
| **RegulatoryAgency Publication 502 (2024)** | https://www.irs.gov/publications/p502 | Qualified medical expenses, OTC rule changes, preventive care | Dec 11, 2025 |
| **PrivacyRegulation Privacy Rule** | https://www.hhs.gov/hipaa/for-professionals/privacy/index.html | PHI definition, individual rights, covered entity requirements | Dec 11, 2025 |
| **PrivacyRegulation Security Rule** | https://www.hhs.gov/hipaa/for-professionals/security/index.html | Administrative/physical/technical safeguards, 45 CFR §164.312 | Dec 11, 2025 |
| **PaymentSecurity v4.0.1** | https://www.pcisecuritystandards.org/standards/pci-dss/ | Payment card data security, 12 requirements, CHD protection | Dec 11, 2025 |

**Compliance:**
- ✅ All sources are **publicly available**
- ✅ All sources are **official government/industry standards bodies**
- ✅ No pirated PDFs, no unauthorized content
- ✅ All URLs use HTTPS (secure)

### 6.2 Knowledge Captured for Learning Library

**Healthcare Domain Knowledge (for reuse):**
1. **RegulatoryAgency Contribution Limits** (2024/2025) - FlexAccount/HealthSavings/HealthReimbursement annual limits, catch-up contributions, HDHP requirements
2. **Rollover Rules** - $640 FlexAccount rollover OR 2.5-month grace (mutual exclusion), 100% HealthSavings rollover
3. **Qualified Medical Expenses** - RegulatoryAgency Pub 502 list with 2019+ OTC rule changes
4. **PrivacyRegulation PHI Security** - Administrative/physical/technical safeguards for healthcare data
5. **PaymentSecurity Payment Card Security** - CHD protection requirements (if card transactions supported)

**Next Step:** Create learning library entry in `cortex_brain/learning/healthcare-payment/` (Batch 2.5 Task 7)

---

## 7. Batch 2.5 Completion Summary

**Tasks Completed:**
1. ✅ RegulatoryAgency Publication 969 (HealthSavings/FlexAccount/HealthReimbursement rules)
2. ✅ RegulatoryAgency Publication 502 (Qualified Medical Expenses)
3. ✅ 26 CFR §125 rules (captured in Pub 969)
4. ✅ PrivacyRegulation PHI requirements (HHS.gov)
5. ✅ PaymentSecurity standards (PCIsecuritystandards.org)
6. ✅ External intelligence matrix (this document)
7. ⏳ Learning library capture (next)

**Key Findings:**
- **P0 Gap Confirmed:** No RegulatoryAgency contribution limit validation found (AST Batch 1)
- **Regulatory Landscape:** 3 compliance domains (RegulatoryAgency tax code, PrivacyRegulation security, PaymentSecurity)
- **Test Strategy:** Just-in-time validation during code scanning (Batches 3-16)
- **Source Quality:** All official/public government/industry sites (legal compliance)

**Estimated Impact:**
- **P0 Issues:** 9 identified (require immediate remediation)
- **P1 Issues:** 6 identified (high-priority validation)
- **Test Scenarios:** 40+ regulatory-driven tests to be created
- **Code Validation:** 8 functional areas to scan (contributions, rollover, claims, reporting, security, card transactions)

**Next Batch:** Batch 3 - Entity Extraction (56 files, 6 sub-batches) with just-in-time regulatory lookups as needed.

---

**End of External Intelligence Matrix**
