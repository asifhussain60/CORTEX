# CORTEX Policy Documents

**Location:** `cortex-brain/documents/policies/`  
**Conversion Date:** November 27, 2025  
**Author:** Asif Hussain  
**Source:** Original .docx files from `docs/policies/`

---

## Overview

This directory contains the official HealthEquity, Inc. policy documents converted to Markdown format for easier review, version control, and integration with CORTEX documentation systems.

---

## Available Policies

### 1. Information Security Policy
**File:** `Information Security Policy.md`  
**Original Effective Date:** August 31, 2014  
**Last Approval:** December 19, 2024 (edited November 6, 2025)  
**Executive Sponsor:** Chief Security Officer (CSO)  
**Total Lines:** 633

**Purpose:**
- Protect company, member, client, and shareholder information
- Manage risks to confidentiality, integrity, and availability
- Reduce disruption and unauthorized access
- Comply with contractual and legal obligations
- Support cybersecurity certifications (SOC 1, SOC 2)
- Follow NIST Cybersecurity Framework

**Key Sections:**
- Purpose and scope
- Definitions (Protected Information, Risk Management, etc.)
- Information security governance
- Access control and authentication
- Incident response procedures
- Security awareness and training
- Physical and environmental security

---

### 2. Information Technology Policy
**File:** `Information Technology Policy.md`  
**Original Effective Date:** May 7, 2018  
**Last Approval:** May 20, 2025  
**Executive Sponsor:** Chief Technology Officer (CTO)  
**Total Lines:** 194

**Purpose:**
- Define IT operations, services, and resource policies
- Ensure secure and efficient use of IT resources
- Protect sensitive and confidential information
- Comply with legal and regulatory requirements
- Define responsibilities of users and IT staff

**Key Sections:**
- Purpose and scope
- Definitions (Asset, Change, Data, etc.)
- IT asset management
- Change management processes
- System maintenance and patching
- Acceptable use policies
- Software licensing and usage

---

### 3. Privacy Policy
**File:** `Privacy Policy.md`  
**Original Effective Date:** April 29, 2011  
**Last Approval:** October 2, 2025  
**Executive Sponsor:** General Counsel  
**Total Lines:** 345

**Purpose:**
- Define requirements for collection, use, transmission, and storage of sensitive information
- Provide high-level view of privacy obligations
- Define governing principles for Protected Information
- Clarify roles and responsibilities
- Create framework for identifying and guarding protected information
- Maximize data value while minimizing privacy risks

**Key Sections:**
- Purpose and scope
- Definitions (Protected Information, PHI, PII, NPI, etc.)
- Privacy governance structure
- Data collection and usage principles
- Protected Information handling
- Privacy breach response
- Employee training requirements
- Third-party vendor requirements

---

### 4. Responsible AI Policy
**File:** `Responsible AI Policy.md`  
**Original Effective Date:** September 14, 2023  
**Last Approval:** November 26, 2025  
**Executive Sponsor:** Chief Security Officer (CSO)  
**Total Lines:** 336

**Purpose:**
- Establish expectations for appropriate use of AI Systems
- Establish AI Governance Council
- Enable collaboration on enterprise AI strategy
- Define acceptable development and use criteria
- Identify limitations on AI System usage
- Document procedures for identifying approved AI Systems
- Provide basis for evaluating alignment with client and government AI principles

**Key Sections:**
- Purpose and scope
- Definitions (AI System, Generative AI, Machine Learning, etc.)
- AI Governance Council structure
- Acceptable use criteria for AI
- Prohibited AI applications
- Risk assessment requirements
- Bias detection and mitigation
- Transparency and explainability
- Human oversight requirements
- Data quality and privacy protection

---

## Document Organization

These policy documents follow CORTEX's mandatory document organization structure:

```
cortex-brain/documents/policies/
├── Information Security Policy.md
├── Information Technology Policy.md
├── Privacy Policy.md
├── Responsible AI Policy.md
└── README.md (this file)
```

**Storage Location:** All policy documents are stored within the CORTEX brain structure at `cortex-brain/documents/policies/` to comply with CORTEX document organization requirements (NO_ROOT_SUMMARY_DOCUMENTS enforcement).

---

## Conversion Details

**Conversion Method:** Python script using `python-docx` library  
**Conversion Script:** Temporary script (removed after conversion)  
**Original Format:** Microsoft Word (.docx)  
**Output Format:** Markdown (.md)  
**Preserved Elements:**
- Headers and headings
- Tables (converted to Markdown table format)
- Text formatting (bold, italic)
- Document structure and sections

---

## Usage Guidelines

**Review:** Open any policy document in Markdown viewer or text editor  
**Search:** Use grep or text search across all policies  
**Version Control:** All policies tracked in git for change history  
**Updates:** When policy documents are updated, re-convert from source .docx files  

---

## Compliance Notes

These policies establish the governance framework for:
- **Information Security:** NIST Cybersecurity Framework, SOC 1/SOC 2 compliance
- **Information Technology:** IT operations, change management, asset management
- **Privacy:** HIPAA, PII protection, data privacy regulations
- **Responsible AI:** AI ethics, bias mitigation, human oversight, transparency

All CORTEX operations should align with these established policies, particularly:
- Data handling and storage practices (Information Security + Privacy)
- AI/ML development and deployment (Responsible AI)
- System changes and updates (Information Technology)

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)  
**Repository:** https://github.com/asifhussain60/CORTEX
