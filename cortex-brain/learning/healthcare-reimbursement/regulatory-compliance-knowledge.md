# Healthcare Reimbursement Regulatory Compliance Knowledge

**Domain:** Healthcare Reimbursement Accounts (FSA/HSA/HRA/Dependent Care FSA)  
**Purpose:** Reusable regulatory knowledge for future healthcare projects  
**Created:** December 11, 2025  
**Sources:** IRS.gov, HHS.gov, PCIsecuritystandards.org (all official/public)

---

## Overview

This document captures regulatory compliance knowledge for healthcare reimbursement account systems (FSA/HSA/HRA). Use this as a reference when designing, developing, or testing healthcare financial applications.

**Compliance Domains:**
1. **IRS Tax Code** - Contribution limits, carryover rules, qualified expenses
2. **HIPAA Security Rule** - Protected Health Information (PHI) data security
3. **PCI-DSS** - Payment card data security (if card transactions supported)

---

## 1. IRS Tax Code Compliance

### 1.1 Contribution Limits (Updated Annually)

**2024 Limits:**
- FSA: $3,200 annually
- HSA Self-Only: $4,150 annually
- HSA Family: $8,300 annually
- HSA Catch-Up (55+): $1,000 additional
- Dependent Care FSA: $5,000 per household (not indexed)

**2025 Limits (inflation-indexed):**
- HSA Self-Only: $4,300 annually (+$150)
- HSA Family: $8,550 annually (+$250)
- FSA: TBD (announced Nov/Dec each year via Revenue Procedure)

**Key Rules:**
- Limits apply to **combined employee + employer contributions**
- Catch-up contributions allowed for age 55+ (HSA only)
- Dependent Care FSA limit is per household (not indexed for inflation)
- Limits change annually - **must update system configuration each November/December**

**Source:** IRS Publication 969, Revenue Procedure (announced annually)

### 1.2 Carryover & Grace Period Rules

**FSA Carryover:**
- Maximum: $640 (2024) - indexed annually
- Employer chooses: Carryover **OR** Grace Period (not both - 26 CFR §125-5)
- Unused funds exceeding carryover limit = forfeited to employer
- **Dependent Care FSA: NO CARRYOVER ALLOWED** (strict use-it-or-lose-it)

**FSA Grace Period:**
- Maximum: 2.5 months (Jan 1 - Mar 15 following plan year end)
- Employer may offer, but cannot offer both grace period and carryover
- Allows claims incurred in grace period to use prior year funds

**HSA Rollover:**
- 100% unlimited rollover year-to-year
- Funds never forfeited (portable - stays with employee)
- No grace period concept (funds always available)

**HRA Carryover:**
- Employer discretion (plan-specific rules)
- Most employers allow 100% carryover
- Not portable (forfeited upon employment termination, unless COBRA/retiree plan)

**Source:** IRS Publication 969, 26 CFR §125-5, IRS Notice 2013-71

### 1.3 Qualified Medical Expenses

**Always Qualified:**
- Prescription drugs and insulin
- Doctor/dentist visits, hospital services
- Medical equipment (wheelchairs, crutches, hearing aids)
- Vision care (eyeglasses, contact lenses, eye surgery)
- Mental health services (psychiatrist, psychologist)

**Qualified as of 2019+ (Rule Changes):**
- Over-the-counter (OTC) medicines (no prescription required)
- Menstrual care products (tampons, pads, cups)
- Condoms (added Notice 2024-71)
- OTC contraceptives (added Notice 2024-75)

**Preventive Care (No HDHP Deductible Required):**
- Annual physicals, well-child care, immunizations
- Cancer screening (all breast cancer screening pre-diagnosis - Notice 2024-75)
- Continuous glucose monitors (CGMs) for diabetes (Notice 2024-75 clarification)
- Insulin products ($0 deductible per Public Law 117-169)
- OTC oral contraceptives, emergency contraceptives, male condoms (Notice 2024-75 NEW 2024)

**NOT Qualified:**
- Cosmetic surgery (unless medically necessary - e.g., post-mastectomy reconstruction)
- Gym memberships, health club dues (general health, not medical treatment)
- Nutritional supplements, vitamins (unless prescribed for specific medical condition)
- Non-prescription drugs (except insulin and OTC medicines per 2019+ rules)

**Source:** IRS Publication 502, IRS Notice 2024-75, IRS Notice 2024-71

### 1.4 HDHP Requirements (for HSA Eligibility)

**2024 HDHP Requirements:**
- Minimum Deductible: $1,600 (self-only) / $3,200 (family)
- Maximum Out-of-Pocket: $8,050 (self-only) / $16,100 (family)

**2025 HDHP Requirements:**
- Minimum Deductible: $1,650 (self-only) / $3,300 (family)
- Maximum Out-of-Pocket: $8,300 (self-only) / $16,600 (family)

**Key Rules:**
- Must have qualifying HDHP to contribute to HSA
- Preventive care can be covered with $0 deductible (safe harbor)
- Last-Month Rule: Eligible on Dec 1 = can contribute full year amount
- Testing Period: Must remain eligible for 12 months or repay excess + 10% penalty

**Source:** IRS Publication 969

---

## 2. HIPAA Security Rule Compliance

### 2.1 Protected Health Information (PHI) Definition

**PHI Includes:**
- Medical record numbers, account numbers
- Health plan beneficiary numbers
- Device identifiers (e.g., serial numbers)
- Biometric identifiers (fingerprints, voice prints)
- Full-face photos and comparable images
- Any other unique identifying number, characteristic, or code
- **In RA Context:** Account balances, claims data, transaction history, participant demographics (SSN, DOB, address)

**ePHI:** Electronic Protected Health Information (PHI in electronic format)

**Source:** HIPAA Privacy Rule, 45 CFR §160.103

### 2.2 Administrative Safeguards (45 CFR §164.308)

**Required:**
- **Security Management Process:** Risk analysis, risk management, sanction policy, information system activity review
- **Assigned Security Responsibility:** Identify security official
- **Workforce Security:** Authorization, workforce clearance, termination procedures
- **Information Access Management:** RBAC, least privilege, access authorization
- **Security Awareness Training:** Security reminders, malware protection, login monitoring, password management
- **Security Incident Procedures:** Response and reporting
- **Contingency Plan:** Data backup, disaster recovery, emergency mode operation
- **Business Associate Contracts:** Written contracts with all vendors accessing PHI

**Source:** HIPAA Security Rule, 45 CFR §164.308

### 2.3 Technical Safeguards (45 CFR §164.312)

**Required:**
- **Access Control:** Unique user ID, emergency access, automatic log-off, encryption/decryption
- **Audit Controls:** Hardware, software, procedural mechanisms to record/examine PHI access
- **Integrity:** Mechanisms to authenticate ePHI not altered/destroyed
- **Person or Entity Authentication:** Verify person/entity is who they claim (MFA recommended)
- **Transmission Security:** Integrity controls, encryption (TLS/HTTPS)

**Implementation Recommendations:**
- Session timeout after 15 minutes inactivity
- Multi-factor authentication (MFA) for PHI access
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.2+)
- Audit trail for all PHI create/read/update/delete operations
- Annual risk analysis

**Source:** HIPAA Security Rule, 45 CFR §164.312

---

## 3. PCI-DSS Compliance (Payment Card Data)

### 3.1 Scope Determination

**Applies to:** Systems that store, process, or transmit cardholder data (CHD)

**Healthcare Context:** If system supports FSA/HSA debit cards, PCI-DSS applies

**Out of Scope:** If no card transactions (ACH/direct deposit only), PCI-DSS not required

### 3.2 Cardholder Data (CHD) vs Sensitive Authentication Data (SAD)

**CHD (Cardholder Data):**
- Primary Account Number (PAN) - 16-digit card number
- Cardholder name
- Expiration date
- Service code

**SAD (Sensitive Authentication Data) - NEVER STORE:**
- CVV/CVV2/CVC2 (3-4 digit security code)
- PIN/PIN block
- Magnetic stripe data (Track 1, Track 2)

**CRITICAL:** SAD must **NEVER** be stored after transaction authorization (even if encrypted)

**Source:** PCI-DSS v4.0.1, PCI SSC Glossary

### 3.3 PAN Protection Requirements

**Requirement 3: Protect Stored CHD**
- **Render PAN unreadable:** Encryption (AES-256), truncation (show last 4 digits only), hashing, tokenization
- **Display:** Show only first 6 + last 4 digits (e.g., 4532-XXXX-XXXX-1234)
- **Tokenization recommended:** Replace PAN with non-sensitive token for card-on-file
- **Key Management:** Encrypt encryption keys, restrict access, rotate keys annually

**Requirement 4: Encrypt Transmission**
- Use strong cryptography (TLS 1.2+) for CHD over public networks
- Never send PAN via end-user messaging (email, SMS, chat)

**Requirement 10: Log and Monitor**
- Audit trail for all CHD access
- Log user ID, date/time, action, data element accessed
- Retain audit logs 90 days minimum (1 year recommended)

**Source:** PCI-DSS v4.0.1 Requirements 3, 4, 10

### 3.4 PCI-DSS 12 Requirements Summary

| Requirement | Description | Priority |
|-------------|-------------|----------|
| **1** | Install/maintain firewall configuration | Infrastructure |
| **2** | Do not use vendor-supplied defaults | P1 |
| **3** | Protect stored CHD (encrypt PAN, NEVER store CVV) | **P0** |
| **4** | Encrypt transmission of CHD over public networks | **P0** |
| **5** | Protect from malware | Infrastructure |
| **6** | Develop secure systems/software (OWASP Top 10) | **P0** |
| **7** | Restrict access by business need-to-know (RBAC) | **P0** |
| **8** | Assign unique ID to each person | **P0** |
| **9** | Restrict physical access to CHD | Infrastructure |
| **10** | Track/monitor all access to CHD | **P0** |
| **11** | Test security systems regularly | P1 |
| **12** | Maintain information security policy | P2 |

**Source:** PCI-DSS v4.0.1

---

## 4. Annual Compliance Calendar

| Month | Compliance Activity | Regulation | Action Required |
|-------|---------------------|------------|-----------------|
| **November/December** | IRS announces next year limits | IRS Revenue Procedure | Update system configuration for FSA/HSA/HDHP limits |
| **January 1** | New IRS limits effective | IRS Publication 969 | Deploy configuration changes, test limit validation |
| **March 15** | FSA grace period ends (if offered) | 26 CFR §125-5 | Process grace period claims, finalize prior year accounts |
| **March 31** | HIPAA breach notification (if >500 records) | HIPAA Breach Notification Rule | Report to HHS if breach occurred |
| **Quarterly** | PCI-DSS ASV scans | PCI-DSS Requirement 11 | Run approved scanning vendor (ASV) vulnerability scans |
| **Annually** | HIPAA risk analysis | HIPAA Security Rule | Conduct enterprise-wide security risk assessment |
| **Annually** | PCI-DSS SAQ/ROC | PCI-DSS Requirement 12 | Complete Self-Assessment Questionnaire or Report on Compliance |

---

## 5. Key Regulatory Concepts

### 5.1 Use-It-Or-Lose-It (FSA)
- Unused FSA funds exceeding carryover limit ($640) are forfeited to employer
- Applies to health FSA and dependent care FSA (no carryover for dependent care)
- Employer retains forfeited funds (not returned to employee)

### 5.2 HSA Portability
- HSA funds belong to employee (not employer)
- Employee keeps HSA upon termination, retirement, or job change
- 100% rollover year-to-year, never forfeited

### 5.3 HIPAA Minimum Necessary
- Use, disclose, or request only minimum PHI necessary to accomplish purpose
- Apply to all PHI except treatment, patient access, or required by law
- Implement role-based access control (RBAC) to enforce

### 5.4 PCI-DSS Tokenization
- Replace PAN with non-sensitive token (e.g., 1234-5678-9012-3456 → TKN_ABC123XYZ)
- Token has no mathematical relationship to PAN (not encryption)
- Reduces PCI-DSS scope (token not considered CHD)
- Recommended for card-on-file scenarios

---

## 6. Common Pitfalls & Best Practices

### 6.1 IRS Tax Code
**Pitfall:** Hardcoding contribution limits in code  
**Best Practice:** Store limits in database configuration table, update annually

**Pitfall:** Offering both carryover AND grace period  
**Best Practice:** Mutual exclusion - employer selects ONE option per plan

**Pitfall:** Allowing HSA contributions for non-HDHP plans  
**Best Practice:** Validate HDHP deductible/OOP limits before allowing contributions

### 6.2 HIPAA Security
**Pitfall:** Shared user accounts for PHI access  
**Best Practice:** Unique user ID for every person (HIPAA §164.312(a)(2)(i))

**Pitfall:** No audit trail for PHI access  
**Best Practice:** Log all PHI create/read/update/delete with user ID, timestamp, action

**Pitfall:** Session timeout >15 minutes  
**Best Practice:** Auto log-off after 10-15 minutes inactivity (HIPAA §164.312(a)(2)(iii))

### 6.3 PCI-DSS
**Pitfall:** Storing CVV/CVV2 "temporarily" or "encrypted"  
**Best Practice:** **NEVER** store CVV, even encrypted (PCI-DSS Requirement 3.2.2)

**Pitfall:** Displaying full PAN in UI/logs/emails  
**Best Practice:** Mask PAN - show only first 6 + last 4 digits (e.g., 4532-XX-XXXX-1234)

**Pitfall:** Using default passwords (admin/admin, root/root)  
**Best Practice:** Remove all default accounts, require strong unique passwords

---

## 7. Regulatory Resources

### 7.1 Official Sources (All Public/Free)

| Regulation | Official Source | URL |
|------------|-----------------|-----|
| **IRS Publication 969** | Internal Revenue Service | https://www.irs.gov/publications/p969 |
| **IRS Publication 502** | Internal Revenue Service | https://www.irs.gov/publications/p502 |
| **26 CFR Part 125** | Electronic Code of Federal Regulations | https://www.ecfr.gov/ (search "26 CFR 125") |
| **HIPAA Privacy Rule** | U.S. Department of Health & Human Services | https://www.hhs.gov/hipaa/for-professionals/privacy/index.html |
| **HIPAA Security Rule** | U.S. Department of Health & Human Services | https://www.hhs.gov/hipaa/for-professionals/security/index.html |
| **PCI-DSS v4.0.1** | PCI Security Standards Council | https://www.pcisecuritystandards.org/standards/pci-dss/ |

### 7.2 Annual Updates to Monitor

- **IRS Revenue Procedure** (published Nov/Dec each year) - FSA/HSA/HDHP limits for next year
- **IRS Notices** - Mid-year rule changes (e.g., Notice 2024-75 preventive care expansions)
- **HIPAA Final Rules** - Privacy/Security Rule modifications (published in Federal Register)
- **PCI-DSS Updates** - Standards council publishes new versions (~every 3 years)

---

## 8. Testing Checklists

### 8.1 IRS Compliance Testing

**Contribution Limits:**
- [ ] Reject FSA contribution >$3,200 (2024)
- [ ] Reject HSA self-only contribution >$4,150 (2024)
- [ ] Reject HSA family contribution >$8,300 (2024)
- [ ] Allow HSA catch-up $1,000 for age 55+
- [ ] Reject dependent care FSA >$5,000 per household

**Carryover & Grace Period:**
- [ ] Forfeit FSA unused funds exceeding $640
- [ ] Prevent both carryover AND grace period enabled
- [ ] Allow claims through Mar 15 if grace period enabled
- [ ] Rollover 100% of HSA balance year-to-year
- [ ] Forfeit 100% of dependent care FSA balance (no carryover)

**Qualified Expenses:**
- [ ] Approve OTC medicine claims (post-2019 rule)
- [ ] Approve menstrual product claims
- [ ] Approve condom claims (post-2024 rule)
- [ ] Reject cosmetic surgery claims (unless medically necessary)
- [ ] Reject gym membership claims

### 8.2 HIPAA Compliance Testing

**Access Control:**
- [ ] Require unique user ID (no shared accounts)
- [ ] Session timeout after 15 minutes inactivity
- [ ] Multi-factor authentication (MFA) for PHI access
- [ ] Encrypt PHI at rest (AES-256)
- [ ] Encrypt PHI in transit (TLS 1.2+)

**Audit Controls:**
- [ ] Log PHI access (user ID, timestamp, action, data element)
- [ ] Audit trail for account balance views
- [ ] Audit trail for claims approvals/denials
- [ ] Audit trail for participant data changes
- [ ] Retain audit logs 1+ years

### 8.3 PCI-DSS Compliance Testing (If Card Transactions)

**PAN Protection:**
- [ ] Verify CVV never stored (not even encrypted)
- [ ] Encrypt PAN at rest (AES-256)
- [ ] Mask PAN in UI (show only last 4 digits: XXXX-XXXX-XXXX-1234)
- [ ] Encrypt PAN transmission (TLS 1.2+)
- [ ] Tokenize PAN for card-on-file

**Access & Audit:**
- [ ] RBAC for cardholder data access
- [ ] No shared accounts with card data access
- [ ] Audit trail for all card data access
- [ ] Retain audit logs 90+ days

---

## 9. Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| Dec 11, 2025 | 1.0 | Initial creation from RA-Domain Batch 2.5 external intelligence gathering | CORTEX AI |

---

**End of Healthcare Reimbursement Regulatory Compliance Knowledge**

**Usage:** Reference this document when:
- Designing healthcare financial applications
- Creating test scenarios for compliance validation
- Performing code reviews for regulatory adherence
- Investigating production issues related to limits/carryover/claims
- Onboarding new team members to healthcare domain

**Next Update:** December 2025 (after IRS announces 2026 contribution limits)
