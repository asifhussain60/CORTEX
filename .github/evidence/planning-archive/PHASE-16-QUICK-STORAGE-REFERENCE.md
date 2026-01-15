# PHASE-16: Quick Visual Guide - What Gets Stored Where

**Status**: Quick Reference  
**Purpose**: One-page visual showing information storage across all tiers

---

## THE CORE DISTINCTION

```
                    TIER 0                          TIER 3
                 (Brain Rules)              (Knowledge Library)
─────────────────────────────────────────────────────────────────
      Rules Decided                    Knowledge Shared
         "MUST"                          "SHOULD"
       Immutable                        Mutable
      Enforced                          Advisory
   ~28-50 entries               Hundreds/thousands entries
```

---

## CORTEX SYSTEM: What's Stored

### TIER 0: CORTEX Governance (28 SKULL Rules)

```
File: cortex-brain/tier0/governance/core-rules.yaml

RULE FORMAT:
  rule_id: CORE-001
  name: "Incremental Execution"
  rule: "ALL work MUST be <500 lines per execution"
  severity: "BLOCKED"

28 RULES COVERING:
├─ Process (TDD, incremental execution, no summaries)
├─ Technical (no hardcoded paths, portability)
├─ Quality (testing, coverage, performance)
├─ Security (encryption, audit trails)
├─ Architecture (immutability, phase lock)
└─ Operational (verification, teardown)

ENFORCEMENT:
  ✅ BLOCKED = Violation = Code fails
  Precedence = HIGHEST (unbreakable)
```

### TIER 3: CORTEX Knowledge (16 Domains)

```
File: cortex-brain/tier3/knowledge/

16 DOMAINS CONTAINING:
├─ GOVERNANCE → Policy frameworks, compliance
├─ INTENT-ROUTING → Intent classification
├─ HALLUCINATION-PREVENTION → Validation
├─ EXECUTION-ORCHESTRATION → Coordination patterns
├─ DATA-MANAGEMENT → Data handling
├─ OBSERVABILITY → Monitoring & logging
├─ SECURITY → Security patterns
├─ API-DESIGN → REST/async patterns
├─ ML-MODELS → ML deployment
├─ KNOWLEDGE-CURATION → Knowledge management
├─ TESTING-VALIDATION → Testing strategies
├─ DEPLOYMENT → Rollout procedures
├─ DOCUMENTATION → Documentation practices
├─ PERFORMANCE → Optimization techniques
├─ ARCHITECTURE → Design patterns
└─ ERROR-HANDLING → Recovery strategies

ENFORCEMENT:
  🔍 SUGGESTED = Violation = Warning
  Precedence = LOWEST (advisory)
```

---

## COMPANY DOMAIN SYSTEM: What Will Be Stored

### TIER 0: Company Domain Governance (~50 Business Rules)

```
File: domain-brain/tier0/governance/business-rules.yaml

RULE FORMAT:
  rule_id: FINANCIAL-RULE-001
  name: "T+2 Settlement"
  rule: "ALL transactions MUST settle within 2 business days"
  severity: "BLOCKED"
  source: "SEC regulations"

~50 RULES ACROSS 3 DOMAINS:

FINANCIAL (20 rules):
├─ T+2 settlement requirement
├─ Audit trail immutability
├─ Daily reconciliation
├─ Audit trail calculation
└─ Transaction validation

HEALTHCARE (18 rules):
├─ HIPAA encryption (AES-256)
├─ PHI access logging
├─ Data retention (6+ years)
├─ Consent requirements
└─ Patient data validation

COMPLIANCE (12 rules):
├─ GDPR data export rights
├─ Consent management
├─ Data access logs (90 days)
├─ Vendor contract review
└─ Privacy by design

ENFORCEMENT:
  ✅ BLOCKED = Violation = Code fails
  Precedence = HIGH (enforceable like CORTEX)
```

### TIER 3: Company Domain Knowledge (20+ Business Domains)

```
File: domain-brain/tier3/knowledge/

20+ DOMAINS CONTAINING:

FINANCIAL-SERVICES:
├─ Settlement workflow patterns
├─ Reconciliation procedures
├─ Audit trail design patterns
├─ Risk management strategies
└─ Compliance checklists

HEALTHCARE:
├─ HIPAA compliance patterns
├─ Patient workflow templates
├─ Medical terminology standards
├─ Treatment protocols
└─ Privacy-preserving analytics

RETAIL:
├─ Inventory management patterns
├─ Pricing algorithms
├─ Customer loyalty programs
├─ Supply chain workflows
└─ POS integration

LEGAL:
├─ Contract management
├─ Compliance documentation
├─ Audit trail requirements
└─ Regulatory reporting

MANUFACTURING:
├─ Quality control
├─ Supply chain optimization
├─ Production scheduling
└─ Defect tracking

... (15+ more domains)

ENFORCEMENT:
  🔍 SUGGESTED = Violation = Warning
  Precedence = LOW (advisory)
```

---

## SIDE-BY-SIDE STORAGE COMPARISON

```
TIER 0: Rules (Immutable, Enforced)
┌──────────────────────────────────────────────────────────┐
│  CORTEX                    │    COMPANY DOMAIN           │
├────────────────────────────┼─────────────────────────────┤
│ 28 core technical rules    │ ~50 business/compliance     │
│ "No hardcoded paths"       │ "T+2 settlement required"   │
│ "TDD enforcement"          │ "HIPAA encryption"          │
│ "Incremental execution"    │ "Audit trail immutable"     │
│ "All tests must pass"      │ "GDPR rights required"      │
│ "Phase lock immutable"     │ "Daily reconciliation"      │
│ Severity: BLOCKED          │ Severity: BLOCKED           │
│ Enforcement: STRICT ✅     │ Enforcement: STRICT ✅      │
└────────────────────────────┴─────────────────────────────┘

TIER 3: Knowledge (Mutable, Advisory)
┌──────────────────────────────────────────────────────────┐
│  CORTEX                    │    COMPANY DOMAIN           │
├────────────────────────────┼─────────────────────────────┤
│ 16 technical domains       │ 20+ business domains        │
│ Hundreds of entries        │ Thousands of entries        │
│ "Testing best practices"   │ "Settlement workflows"      │
│ "Error handling patterns"  │ "Healthcare processes"      │
│ "Security implementations" │ "Compliance procedures"     │
│ "Architecture patterns"    │ "Financial reconciliation"  │
│ "Performance tips"         │ "Industry standards"        │
│ Severity: SUGGESTED        │ Severity: SUGGESTED         │
│ Enforcement: ADVISORY 🔍   │ Enforcement: ADVISORY 🔍    │
└────────────────────────────┴─────────────────────────────┘
```

---

## INFORMATION TYPES BY TIER

### TIER 0: The Constraints

```
What's Stored:
├─ Unbreakable rules
├─ Governance boundaries
├─ Compliance requirements
├─ Risk constraints
├─ Audit requirements
└─ Operational boundaries

Format: YAML rules with:
  ├─ rule_id
  ├─ category
  ├─ severity
  ├─ name
  ├─ description
  ├─ validation criteria
  └─ precedence level

Characteristics:
  • Small (fits in YAML)
  • Precise (binary: applies or not)
  • Immutable (rarely change)
  • Strictly enforced
  • Phase-locked
```

### TIER 3: The Patterns

```
What's Stored:
├─ Best practices
├─ Implementation patterns
├─ Common workflows
├─ Industry standards
├─ Lessons learned
└─ Expert recommendations

Format: Markdown documents with:
  ├─ Pattern description
  ├─ When to use
  ├─ When NOT to use
  ├─ Example implementations
  ├─ Anti-patterns to avoid
  ├─ Performance implications
  └─ Related patterns

Characteristics:
  • Large (detailed documentation)
  • Nuanced (contextual: sometimes applies)
  • Mutable (evolve over time)
  • Loosely suggested
  • Updated frequently
```

---

## CODE GENERATION FLOW

### How Information Gets Used

```
Request: "Generate financial settlement code"

┌─────────────────────────────────────────┐
│ 1. CHECK CORTEX TIER 0 (Strict)         │
├─────────────────────────────────────────┤
│ ✅ Must have tests? → YES (TDD)         │
│ ✅ Incremental? → YES (<500 lines)      │
│ ✅ No hardcoded paths? → YES            │
│ ✅ Portable? → YES                      │
├─────────────────────────────────────────┤
│ Result: Passes CORTEX governance ✅     │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ 2. CHECK DOMAIN TIER 0 (Strict)         │
├─────────────────────────────────────────┤
│ ✅ T+2 settlement? → YES                │
│ ✅ Audit trail immutable? → YES         │
│ ✅ Daily reconciliation? → YES          │
│ ✅ Valid transaction? → YES             │
├─────────────────────────────────────────┤
│ Result: Passes domain governance ✅     │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ 3. CONSULT CORTEX TIER 3 (Advisory)     │
├─────────────────────────────────────────┤
│ 🔍 "Error handling best practice"       │
│ 🔍 "Testing patterns library"           │
│ 🔍 "Performance optimization tips"      │
├─────────────────────────────────────────┤
│ Result: Get suggestions 🔍              │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ 4. CONSULT DOMAIN TIER 3 (Advisory)     │
├─────────────────────────────────────────┤
│ 🔍 "Settlement workflow pattern"        │
│ 🔍 "Reconciliation best practices"      │
│ 🔍 "Financial validation rules"         │
├─────────────────────────────────────────┤
│ Result: Get domain suggestions 🔍       │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ GENERATE CODE                           │
├─────────────────────────────────────────┤
│ • Compliant with Tier 0 rules ✅        │
│ • Domain compliant ✅                   │
│ • Following Tier 3 patterns 🔍          │
│ • Using Tier 3 domain patterns 🔍       │
└─────────────────────────────────────────┘
```

---

## REAL NUMBERS

### CORTEX Tier 0: 28 Rules

```
Core Rules (CORE-001 to CORE-028):
├─ Orchestration: 5 rules
├─ Response Formatting: 4 rules
├─ Portability: 3 rules
├─ Development Workflow: 6 rules
├─ Architecture Integrity: 5 rules
├─ Quality Gates: 3 rules
└─ Security & Privacy: 2 rules
```

### CORTEX Tier 3: 16 Domains

```
Knowledge Domains:
├─ GOVERNANCE
├─ INTENT-ROUTING
├─ HALLUCINATION-PREVENTION
├─ EXECUTION-ORCHESTRATION
├─ DATA-MANAGEMENT
├─ OBSERVABILITY
├─ SECURITY
├─ API-DESIGN
├─ ML-MODELS
├─ KNOWLEDGE-CURATION
├─ TESTING-VALIDATION
├─ DEPLOYMENT
├─ DOCUMENTATION
├─ PERFORMANCE
├─ ARCHITECTURE
└─ ERROR-HANDLING
(Each has 10-50+ indexed knowledge entries)
```

### Company Domain Tier 0: ~50 Rules

```
By Domain:
├─ Financial: 20 rules
├─ Healthcare: 18 rules
└─ Compliance: 12 rules
```

### Company Domain Tier 3: 20+ Domains

```
FINANCIAL-SERVICES, HEALTHCARE, RETAIL, LEGAL,
MANUFACTURING, SUPPLY-CHAIN, QUALITY-ASSURANCE,
REAL-ESTATE, INSURANCE, TELECOMMUNICATIONS,
ENERGY, UTILITIES, LOGISTICS, BANKING, FINTECH,
REGULATORY, PRIVACY, SECURITY, INTEGRATION,
REPORTING, ... (and more as needed)
```

---

## KEY TAKEAWAYS

```
1. TIER 0 = Rules (What MUST happen)
   CORTEX: Technical governance
   Domain: Business governance
   Both: BLOCKED if violated

2. TIER 3 = Knowledge (What SHOULD happen)
   CORTEX: Technical patterns
   Domain: Business patterns
   Both: SUGGESTED (flexible)

3. Different Information Types
   T0: Binary decisions (applies or not)
   T3: Contextual recommendations (consider)

4. Different Update Cycles
   T0: Rarely changes (phase-locked)
   T3: Frequently updates (as knowledge grows)

5. Combined Effect
   Code generation respects BOTH systems
   Technical + Business governance together
   Technical + Business knowledge together
```

---

## QUICK REFERENCE TABLE

| Question | Tier 0 | Tier 3 |
|----------|--------|---------|
| Where is it? | `governance/` | `knowledge/` |
| Is it mutable? | ❌ No (immutable) | ✅ Yes (evolves) |
| How enforced? | ✅ BLOCKED | 🔍 WARNED |
| How many? | ~28-50 entries | Hundreds/thousands |
| What format? | YAML rules | Markdown patterns |
| Updated how often? | Rarely | Frequently |
| Business or tech? | Both | Both |
| For CORTEX? | 28 rules | 16 domains |
| For Company? | ~50 rules | 20+ domains |

