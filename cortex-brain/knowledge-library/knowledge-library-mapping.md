# Knowledge Library Domain Mapping

**Version:** 1.0.0  
**Created:** 2025-12-31  
**Governance Rule:** `KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT`  
**Purpose:** Domain-to-library file mapping for automatic best practices integration

---

## 📚 Overview

This document defines the mapping between detected domains/keywords and applicable knowledge library files. Used by Planning System and ADO Operations orchestrators to automatically inject best practices into plans and work items.

---

## 🔍 Domain Classification

### Architecture Domain

**Triggers:**
- `ai`, `ml`, `machine learning`
- `microservice`, `microservices`
- `architecture`, `system design`
- `scalability`, `distributed`
- `reactive`, `event-driven`

**Applicable Library Files:**

| File | Focus | When to Use |
|------|-------|-------------|
| `architecture/ai-architecture.yaml` | AI/ML production patterns | AI features, LLM integration, model deployment |
| `architecture/microservices-transition.yaml` | Microservices migration | Monolith decomposition, service boundaries |
| `architecture/reactive-systems.yaml` | Reactive architecture | Event-driven systems, message queues, streaming |

**Key Sections:**
- Production patterns (sequential, batch, stream)
- Build vs buy vs rent decisions
- Failure handling strategies
- Scalability considerations

---

### Security Domain

**Triggers:**
- `auth`, `authentication`, `authorization`
- `login`, `password`, `token`
- `permission`, `access control`, `role`
- `api endpoint`, `security`
- `encryption`, `jwt`, `oauth`

**Applicable Library Files:**

| File | Focus | When to Use |
|------|-------|-------------|
| `security/threat-modeling-framework.md` | Threat analysis | New features, API design, data flows |
| `security/owasp-top-10-guide.md` | OWASP Top 10 | All web/API features |
| `security/api-security-foundations.md` | API security patterns | REST/GraphQL endpoints, authentication |
| `security/access-control-patterns.md` | Authorization patterns | RBAC, ABAC, permissions |
| `security/data-protection-framework.md` | Data security | PII handling, encryption, storage |
| `security/audit-logging-standards.md` | Audit trails | Compliance features, security events |
| `security/incident-response-playbook.md` | Security incidents | Security features, monitoring |

**Key Sections:**
- OWASP A01: Broken Access Control
- OWASP A02: Cryptographic Failures
- OWASP A03: Injection
- OWASP A07: Identification and Authentication Failures
- Authentication patterns
- Rate limiting
- Input validation

---

### Compliance Domain

**Triggers:**
- `gdpr`, `data protection`, `privacy`
- `hipaa`, `healthcare`, `phi`
- `pci`, `pci-dss`, `payment`
- `compliance`, `regulation`, `audit`
- `sox`, `soc2`

**Applicable Library Files:**

| File | Focus | When to Use |
|------|-------|-------------|
| `compliance/gdpr-compliance-checklist.md` | GDPR requirements | User data handling, EU operations |
| `compliance/hipaa-compliance-checklist.md` | HIPAA requirements | Healthcare data, PHI handling |
| `compliance/pci-dss-compliance-checklist.md` | PCI-DSS requirements | Payment processing, card data |
| `compliance/soc2-compliance-checklist.md` | SOC2 requirements | Enterprise features, security controls |

**Key Sections:**
- Data collection and consent (GDPR Art. 6, 7)
- Data subject rights (GDPR Art. 15-22)
- Data protection by design (GDPR Art. 25)
- Access controls (PCI-DSS 7.0)
- Encryption requirements (PCI-DSS 3.0, HIPAA §164.312)
- Audit logging (SOC2 CC6.2)

---

### Design Patterns Domain

**Triggers:**
- `design pattern`, `pattern`
- `csharp`, `c#`, `.net`
- `refactoring`, `code quality`
- `solid`, `dependency injection`

**Applicable Library Files:**

| File | Focus | When to Use |
|------|-------|-------------|
| `design-patterns/csharp-patterns.yaml` | C# patterns | C# development, refactoring |

**Key Sections:**
- Creational patterns (Factory, Builder, Singleton)
- Structural patterns (Adapter, Decorator, Facade)
- Behavioral patterns (Strategy, Observer, Command)
- SOLID principles implementation

---

### Design & UX/UI Domain

**Triggers:**
- `ui`, `ux`, `user interface`, `user experience`
- `design system`, `glassmorphism`, `visual design`
- `documentation site`, `documentation website`
- `accessibility`, `wcag`, `a11y`
- `responsive design`, `mobile`, `layout`
- `interaction`, `animation`, `hover state`
- `usability`, `user-centered`

**Applicable Library Files:**

| File | Focus | When to Use |
|------|-------|-------------|
| `design/ui-ux-documentation-best-practices.yaml` | Documentation UI/UX | Documentation sites, web interfaces, user-facing pages |

**Key Sections:**
- Progressive disclosure patterns
- Visual hierarchy and spacing systems
- Glassmorphism implementation (v4.0 compatible)
- Animation tier system (T1/T2/T3)
- Accessibility (WCAG 2.1 AA)
- Responsive design (mobile-first)
- Data visualization best practices
- Multi-visual approach for documentation
- Hub-and-spoke navigation pattern
- Performance optimization

---

### Standards Domain

**Triggers:**
- `diagram`, `architecture diagram`
- `visualization`, `flowchart`
- `documentation`, `technical spec`
- `uml`, `c4 model`

**Applicable Library Files:**

| File | Focus | When to Use |
|------|-------|-------------|
| `standards/diagram-guidelines.md` | Diagram standards | Architecture docs, technical specs |

**Key Sections:**
- C4 model levels (Context, Container, Component, Code)
- Diagram types and when to use
- Tool recommendations
- Style guidelines

---

## 🎯 Integration Examples

### Example 1: User Authentication Feature

**Detected Domains:** Security, Design Patterns  
**Triggered By:** "authentication", "login", "csharp"

**Auto-Injected References:**
```yaml
knowledge_library_references:
  - file: "security/owasp-top-10-guide.md"
    domain: "security"
    relevant_sections:
      - "A01:2021 - Broken Access Control"
      - "A02:2021 - Cryptographic Failures"
      - "A07:2021 - Identification and Authentication Failures"
    application: "User authentication and session management"
    key_patterns:
      - "Password hashing (bcrypt, Argon2)"
      - "JWT token validation"
      - "Rate limiting on login attempts"
  
  - file: "security/api-security-foundations.md"
    domain: "security"
    relevant_sections:
      - "Authentication Patterns"
      - "Session Management"
      - "Rate Limiting"
    application: "API authentication endpoints"
    key_patterns:
      - "Bearer token authentication"
      - "OAuth 2.0 flows"
      - "API key management"
  
  - file: "design-patterns/csharp-patterns.yaml"
    domain: "design_patterns"
    relevant_sections:
      - "Strategy Pattern (authentication providers)"
      - "Factory Pattern (token generation)"
    application: "Authentication service implementation"
```

**Phase Task Examples:**
- `[ ] 2.3 Review OWASP A07 guidelines (owasp-top-10-guide.md)`
- `[ ] 3.1 Implement password hashing per api-security-foundations.md`
- `[ ] 4.2 Apply Strategy pattern for auth providers (csharp-patterns.yaml)`

---

### Example 2: Healthcare Patient Portal

**Detected Domains:** Compliance (HIPAA), Security  
**Triggered By:** "healthcare", "patient data", "phi"

**Auto-Injected References:**
```yaml
knowledge_library_references:
  - file: "compliance/hipaa-compliance-checklist.md"
    domain: "compliance"
    relevant_sections:
      - "§164.312(a)(1) - Access Control"
      - "§164.312(c) - Integrity Controls"
      - "§164.312(d) - Person or Entity Authentication"
      - "§164.312(e)(1) - Transmission Security"
    application: "Patient data handling and access"
    checklist_items:
      - "Unique user identification"
      - "Emergency access procedures"
      - "Automatic logoff"
      - "Encryption of PHI in transit and at rest"
  
  - file: "security/access-control-patterns.md"
    domain: "security"
    relevant_sections:
      - "Role-Based Access Control (RBAC)"
      - "Attribute-Based Access Control (ABAC)"
    application: "Patient record access permissions"
  
  - file: "security/audit-logging-standards.md"
    domain: "security"
    relevant_sections:
      - "Access Log Requirements"
      - "Retention Policies"
    application: "HIPAA audit trail requirements"
```

**ADO Work Item Enhancements:**
- **Linked Task:** "HIPAA Compliance Validation"
- **Custom Field:** `Compliance.Requirements = "HIPAA §164.312"`
- **Acceptance Criteria:**
  - `[ ] HIPAA §164.312(a)(1): User access controls implemented`
  - `[ ] HIPAA §164.312(e)(1): PHI encrypted in transit (TLS 1.2+)`
  - `[ ] Audit logging per audit-logging-standards.md`

---

### Example 3: Payment Processing Integration

**Detected Domains:** Compliance (PCI-DSS), Security  
**Triggered By:** "payment", "credit card", "pci"

**Auto-Injected References:**
```yaml
knowledge_library_references:
  - file: "compliance/pci-dss-compliance-checklist.md"
    domain: "compliance"
    relevant_sections:
      - "Requirement 3: Protect stored cardholder data"
      - "Requirement 4: Encrypt transmission of cardholder data"
      - "Requirement 7: Restrict access to cardholder data"
      - "Requirement 8: Identify and authenticate access"
    application: "Payment processing and card data handling"
    checklist_items:
      - "Never store CVV/CVV2"
      - "Encrypt PAN if stored"
      - "Use TLS 1.2+ for transmission"
      - "Implement MFA for admin access"
  
  - file: "security/data-protection-framework.md"
    domain: "security"
    relevant_sections:
      - "Encryption Standards"
      - "Key Management"
    application: "Cardholder data encryption"
```

---

## 🔧 Implementation Guidelines

### For Planning System

1. **Domain Detection Phase:**
   - Parse feature description, user story, acceptance criteria
   - Match keywords against domain classifiers
   - Rank domains by keyword frequency

2. **Library File Loading:**
   - Load YAML/MD files for detected domains
   - Extract relevant sections based on keyword context
   - Generate references list

3. **Plan Integration:**
   - Add `### 📚 Knowledge Library References` section to plan context
   - Include library reminders in phase tasks
   - Add validation checklist at end

4. **Template:**
   ```yaml
   context:
     knowledge_library_references:
       - file: "{path}"
         domain: "{domain}"
         relevant_sections: ["{section1}", "{section2}"]
         application: "{how it applies}"
         key_patterns: ["{pattern1}", "{pattern2}"]
   
   phases:
     - phase: 1
       tasks:
         - "[ ] Review {library_file} - {specific_section}"
   ```

### For ADO Operations

1. **Work Item Enhancement:**
   - Inject library checklist into acceptance criteria
   - Add "📚 Knowledge Library References" section to description
   - Create linked tasks for security/compliance validation

2. **Custom Fields:**
   - `Custom.KnowledgeLibraryReferences`: HTML bulleted list
   - `Custom.ComplianceRequirements`: Comma-separated string
   - `Custom.SecurityConsiderations`: HTML checklist

3. **Validation:**
   - Block work item creation if security/compliance detected without library references
   - Warn if no libraries referenced for applicable domain

---

## 📊 Validation Rules

| Rule | Enforcement | Action |
|------|-------------|--------|
| Security feature without security library | **BLOCK** | Require at least one security library reference |
| Compliance keyword without compliance library | **BLOCK** | Require compliance checklist reference |
| Architecture feature without library | **WARN** | Suggest applicable architecture library |
| Design pattern without library | **INFO** | Recommend design pattern library |

---

## 🗂️ Library File Inventory

### Current Files (17 total)

**Architecture (3):**
- `ai-architecture.yaml`
- `microservices-transition.yaml`
- `reactive-systems.yaml`

**Security (13):**
- `access-control-patterns.md`
- `ai-security-operations.md`
- `api-security-foundations.md`
- `audit-logging-standards.md`
- `data-protection-framework.md`
- `incident-response-playbook.md`
- `microservices-security.yaml`
- `penetration-testing-methodology.md`
- `risk-assessment-methodology.md`
- `security-awareness-training.md`
- `security-documentation-standards.md`
- `threat-modeling-framework.md`
- `vulnerability-assessment-framework.md`

**Compliance (4):**
- `gdpr-compliance-checklist.md`
- `hipaa-compliance-checklist.md`
- `pci-dss-compliance-checklist.md`
- `soc2-compliance-checklist.md`

**Design Patterns (1):**
- `csharp-patterns.yaml`

**Standards (1):**
- `diagram-guidelines.md`

---

## 🔄 Maintenance

### Adding New Library Files

1. Create file in appropriate `cortex-brain/knowledge-library/{domain}/` directory
2. Add entry to this mapping document
3. Update `brain-protection-rules.yaml` knowledge_library_mapping section
4. Update orchestrator manifests (planning, ADO) with new domain classifier
5. Test domain detection with sample features

### Updating Existing Mappings

1. Update this document first (source of truth)
2. Sync changes to `brain-protection-rules.yaml`
3. Sync changes to orchestrator manifests
4. Run validation: `python cortex-toolkit/validate_knowledge_library_mappings.py`

---

**Governance:** This mapping is enforced by `KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT` brain protection rule.

**Validation:** Run system maintenance to verify mapping integrity.
