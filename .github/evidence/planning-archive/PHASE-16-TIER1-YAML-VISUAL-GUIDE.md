# PHASE-16: Tier 1 YAML Integration - Visual Guide

**Status**: Architecture Documentation  
**Date**: January 15, 2026

---

## THE ANSWER IN ONE DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CORTEX Tier 1 YAML                              │
│          ac-domain-mappings.yaml (87 ACs, 4 domains)                    │
│                                                                          │
│  domains:                                                               │
│    tdd:                    → 28 ACs (testing, coverage)                │
│    planning:               → 15 ACs (phase governance)                 │
│    ado:                    → 20 ACs (work tracking)                    │
│    interaction:            → 12 ACs (audit, communication)             │
│                                                                          │
│  Format: { domain_id, domain_name, ac_count, acceptance_criteria[] }   │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
                        (Query via config endpoint)
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    Company Domain Brain Tier 1 YAML                      │
│        domain-ac-mappings.yaml (50 ACs, 3 domains)                      │
│                      [Company's Project]                                │
│                                                                          │
│  domains:                                                               │
│    financial:              → 20 ACs (settlement, audit)                │
│    healthcare:             → 18 ACs (HIPAA, encryption)               │
│    compliance:             → 12 ACs (GDPR, regulations)               │
│                                                                          │
│  Format: { domain_id, domain_name, ac_count, acceptance_criteria[] }   │
│  (EXACT SAME STRUCTURE)                                                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## TIER 1 YAML STRUCTURE: CORTEX vs COMPANY

### CORTEX Tier 1 (Current)

```yaml
# File: cortex-brain/tier1/acceptance-criteria/ac-domain-mappings.yaml

metadata:
  tier: 1
  title: "Acceptance Criteria to Domain Mappings"
  ac_count: 87
  domain_count: 4

domains:
  tdd:
    domain_id: "tdd"
    domain_name: "Test-Driven Development"
    orchestrator: "TDDOrchestrator"
    ac_count: 28
    acceptance_criteria:
      - ac_id: "AC-AR-006-01"
        title: "pytest plugin architecture"
        description: "Test execution framework with plugin discovery"
        categories: ["test_execution", "code_coverage"]
        severity: "HIGH"
      
      - ac_id: "AC-AR-006-02"
        title: "Test scaffolding & fixtures"
        categories: ["fixtures", "test_isolation"]
        severity: "HIGH"
      
      # ... 26 more TDD ACs

  planning:
    domain_id: "planning"
    domain_name: "Phase Management"
    ac_count: 15
    acceptance_criteria:
      - ac_id: "AC-AR-001-01"
        title: "Phase enforcement"
        severity: "CRITICAL"
      # ... 14 more PLANNING ACs

  ado:
    domain_id: "ado"
    domain_name: "Work Item Management"
    ac_count: 20
    acceptance_criteria:
      # ... 20 ADO ACs

  interaction:
    domain_id: "interaction"
    domain_name: "Communication & Audit"
    ac_count: 12
    acceptance_criteria:
      # ... 12 INTERACTION ACs
```

### Company Domain Brain Tier 1 (What They'll Build)

```yaml
# File: domain-brain/tier1/acceptance-criteria/domain-ac-mappings.yaml
# (EXACT SAME STRUCTURE)

metadata:
  tier: 1
  title: "Business Domain to AC Mappings"
  ac_count: 50
  domain_count: 3

domains:
  financial:
    domain_id: "financial"
    domain_name: "Financial Services"
    orchestrator: "FinancialOrchestrator"  # Company builds
    ac_count: 20
    acceptance_criteria:
      - ac_id: "AC-FIN-001-01"
        title: "Transaction Settlement (T+2)"
        description: "Transactions settle within 2 business days"
        categories: ["settlement", "compliance"]
        severity: "CRITICAL"
      
      - ac_id: "AC-FIN-001-02"
        title: "Audit Trail (Immutable)"
        description: "All transactions logged immutably"
        categories: ["audit", "logging"]
        severity: "CRITICAL"
      
      - ac_id: "AC-FIN-001-03"
        title: "Daily Reconciliation"
        description: "Verify settlement against records"
        categories: ["reconciliation", "validation"]
        severity: "HIGH"
      
      # ... 17 more Financial ACs

  healthcare:
    domain_id: "healthcare"
    domain_name: "Healthcare & HIPAA"
    orchestrator: "HealthcareOrchestrator"
    ac_count: 18
    acceptance_criteria:
      - ac_id: "AC-HEALTH-001-01"
        title: "HIPAA Compliance"
        description: "Patient data encrypted with AES-256"
        categories: ["encryption", "compliance"]
        severity: "CRITICAL"
      
      - ac_id: "AC-HEALTH-001-02"
        title: "Access Logging"
        description: "Log all PHI access events"
        categories: ["audit", "logging"]
        severity: "CRITICAL"
      
      # ... 16 more Healthcare ACs

  compliance:
    domain_id: "compliance"
    domain_name: "Regulatory Compliance"
    orchestrator: "ComplianceOrchestrator"
    ac_count: 12
    acceptance_criteria:
      - ac_id: "AC-COMP-001-01"
        title: "GDPR Data Rights"
        description: "Support data export/deletion requests"
        categories: ["gdpr", "data_rights"]
        severity: "CRITICAL"
      
      - ac_id: "AC-COMP-001-02"
        title: "Consent Management"
        description: "Track and enforce user consent"
        categories: ["consent", "privacy"]
        severity: "HIGH"
      
      # ... 10 more Compliance ACs
```

---

## KEY INSIGHT: SAME FORMAT, DIFFERENT CONTENT

### CORTEX Tier 1: Maps CORTEX ACs to Technical Domains
```
AC-AR-006-01 (pytest plugin)
    ↓ belongs to domain ↓
TDD (Test-Driven Development)
```

### Company Tier 1: Maps Company ACs to Business Domains
```
AC-FIN-001-01 (T+2 Settlement)
    ↓ belongs to domain ↓
FINANCIAL (Financial Services)
```

### Both Use Same YAML Structure
- Same field names: `domain_id`, `ac_id`, `severity`, `categories`
- Same hierarchy: domains → acceptance_criteria[]
- Same query patterns work for both

---

## HOW QUERIES WORK

### Single Query Engine, Two Sources

```python
# src/core/tier1_query.py

class Tier1QueryEngine:
    def __init__(self, cortex_tier1_path, domain_tier1_path=None):
        self.cortex = load_yaml(cortex_tier1_path)
        self.domain = load_yaml(domain_tier1_path) if domain_tier1_path else None
    
    def query_ac_domain(self, ac_id):
        """Find domain for an AC"""
        
        # Check CORTEX first
        for domain, data in self.cortex['domains'].items():
            for ac in data['acceptance_criteria']:
                if ac['ac_id'] == ac_id:
                    return {'source': 'cortex', 'domain': domain}
        
        # Check Domain Brain if available
        if self.domain:
            for domain, data in self.domain['domains'].items():
                for ac in data['acceptance_criteria']:
                    if ac['ac_id'] == ac_id:
                        return {'source': 'domain', 'domain': domain}
        
        return None
```

### Query Examples

#### Query 1: "Get domain for AC-AR-006-01"
```python
result = tier1.query_ac_domain("AC-AR-006-01")
# → {'source': 'cortex', 'domain': 'tdd'}
```

#### Query 2: "Get domain for AC-FIN-001-01"
```python
result = tier1.query_ac_domain("AC-FIN-001-01")
# Without Domain Brain:
# → None (unknown AC)

# With Domain Brain:
# → {'source': 'domain', 'domain': 'financial'}
```

#### Query 3: "Get all ACs for financial domain"
```python
result = tier1.query_domain_acs("financial")
# Without Domain Brain:
# → None (domain not found)

# With Domain Brain:
# → [AC-FIN-001-01, AC-FIN-001-02, ..., AC-FIN-001-20]
```

#### Query 4: "Get all ACs across all domains (merged)"
```python
result = tier1.query_all_acs_merged()
# → CORTEX ACs (87) + Domain ACs (50) = 137 total
# Organized by source and domain
```

---

## INTEGRATION WORKFLOW

### Step 1: CORTEX Tier 1 (Already Exists)
```
✅ CORTEX has: ac-domain-mappings.yaml
✅ 87 ACs in 4 technical domains (TDD, PLANNING, ADO, INTERACTION)
✅ Queries work perfectly
```

### Step 2: Company Builds Domain Tier 1 (Future)
```
⏳ Company creates: domain-ac-mappings.yaml
⏳ 50 ACs in 3 business domains (FINANCIAL, HEALTHCARE, COMPLIANCE)
⏳ Same YAML structure as CORTEX
```

### Step 3: Configure Endpoint (One Config Change)
```
# .env or config.yaml

DOMAIN_BRAIN_ENDPOINT=https://domain-brain.local/tier1
# or
DOMAIN_BRAIN_PATH=/path/to/domain-brain/tier1/
```

### Step 4: CORTEX Auto-Detects (No Code Changes)
```python
# CORTEX Tier1QueryEngine automatically:
# 1. Loads CORTEX Tier 1 YAML ✅
# 2. Loads Domain Brain Tier 1 YAML (if available) ✅
# 3. Queries both seamlessly ✅
# 4. Falls back gracefully if domain unavailable ✅
```

---

## TIER 1 IN ACTION: Real Scenario

### Scenario: Generate Financial Settlement Code

#### Step 1: CORTEX Queries Its Tier 1
```python
cortex_acs = tier1.query_domain_acs("tdd")
# → AC-AR-006-01 (pytest), AC-AR-006-02 (fixtures), ...

cortex_acs = tier1.query_domain_acs("planning")
# → AC-AR-001-01 (phase enforcement), ...

cortex_acs = tier1.query_domain_acs("ado")
# → AC-FR-003-01 (work item linking), ...
```

#### Step 2: CORTEX Queries Domain Tier 1
```python
domain_acs = tier1.query_domain_acs("financial")
# → AC-FIN-001-01 (T+2 settlement)
#   AC-FIN-001-02 (audit trail)
#   AC-FIN-001-03 (reconciliation)

domain_acs = tier1.query_domain_acs("compliance")
# → AC-COMP-001-01 (GDPR data rights)
```

#### Step 3: Merged Governance
```
Applied Rules:
├─ CORTEX Rules (mandatory):
│  ├─ TDD: 100% test coverage required
│  ├─ PLANNING: Phase governance enforced
│  ├─ ADO: Work items linked
│  └─ INTERACTION: Audit all decisions
│
└─ Domain Rules (if available):
   ├─ FINANCIAL: T+2 settlement compliance
   ├─ FINANCIAL: Immutable audit trail
   ├─ FINANCIAL: Daily reconciliation
   └─ COMPLIANCE: GDPR data rights
```

#### Step 4: Generate Code
```python
generated_code = cortex.generate(
    request="financial settlement code",
    tier0_rules=tier0_rules,
    tier1_domains=tier1_merged,  # CORTEX + Domain
    tier2_templates=tier2_templates,
    tier3_knowledge=tier3_knowledge
)

# Result: Code that satisfies ALL rules (CORTEX + Financial)
```

---

## YAML FIELDS REFERENCE

### Metadata Section
```yaml
metadata:
  tier: 1                          # Always tier 1
  title: "..."                     # Descriptive title
  description: "..."               # Long description
  created_at: "ISO 8601"          # Creation timestamp
  ac_count: <number>              # Total ACs in this tier
  domain_count: <number>          # Total domains
```

### Domain Section
```yaml
domains:
  <domain_id>:
    domain_id: "<string>"         # Unique identifier
    domain_name: "<string>"       # Human-readable name
    orchestrator: "<string>"      # Associated orchestrator class
    tier_access: [0, 1, 2]        # Which tiers can access
    primary_rules: ["..."]        # Governance rules for this domain
    ac_count: <number>            # Number of ACs in this domain
    acceptance_criteria:
      - ac_id: "<string>"         # Unique AC identifier
        title: "<string>"         # Short title
        description: "<string>"   # Detailed description
        categories: ["..."]       # Categorization tags
        severity: "<string>"      # CRITICAL, HIGH, MEDIUM, LOW
```

### Acceptance Criteria Section
```yaml
acceptance_criteria:
  - ac_id: "AC-XXX-001-01"
    title: "..."
    description: "..."
    categories: [...]              # Multiple categories possible
    severity: "CRITICAL"           # Importance level
    # Additional fields possible:
    # - priority: "P0" | "P1" | ...
    # - owner: "team_name"
    # - due_date: "ISO 8601"
```

---

## GRACEFUL DEGRADATION

### Without Domain Brain (Today)
```
CORTEX Tier 1
├─ Load: ac-domain-mappings.yaml ✅
├─ Query: TDD, PLANNING, ADO, INTERACTION domains ✅
└─ Result: Works perfectly (CORTEX governance only)
```

### With Domain Brain (When Company Builds It)
```
CORTEX Tier 1              Domain Brain Tier 1
├─ Load: CORTEX YAML ✅    ├─ Load: Domain YAML ✅
├─ Query: CORTEX domains ✅ ├─ Query: Domain domains ✅
└─ Merge results ✅        └─ Return merged ✅

Result: CORTEX + Domain governance applied
```

### If Domain Brain Becomes Unavailable
```
CORTEX Tier 1
├─ Load: ac-domain-mappings.yaml ✅
├─ Try: Query domain-brain (timeout/error) ⚠️
├─ Catch: Exception gracefully
└─ Fall back to CORTEX only ✅

Result: Works with CORTEX governance (domain ignored temporarily)
```

---

## IMPLEMENTATION CHECKLIST

### For CORTEX (Already Done ✅)
- ✅ Create cortex-brain/tier1/acceptance-criteria/ac-domain-mappings.yaml
- ✅ Implement Tier1QueryEngine
- ✅ Add graceful degradation for missing domain brain

### For Company (To Do)
- ⏳ Design business domains (FINANCIAL, HEALTHCARE, COMPLIANCE, etc)
- ⏳ Create domain-brain/tier1/acceptance-criteria/domain-ac-mappings.yaml
- ⏳ Define acceptance criteria for each business domain
- ⏳ Implement domain orchestrators (FinancialOrchestrator, etc)
- ⏳ Deploy domain-brain and set DOMAIN_BRAIN_ENDPOINT config

### For CORTEX (Future Enhancement - 1 Hour, PHASE-13)
- ⏳ Add domain registry to tier3 (signals where domain will integrate)
- ⏳ Design dashboard extensibility (show domain context if available)
- ⏳ Document API for company Domain Brain project

---

## BENEFITS OF YAML-BASED TIER 1

| Benefit | How |
|---------|-----|
| **Consistency** | Same YAML structure for CORTEX and Company |
| **Extensibility** | Company adds new domains without touching CORTEX |
| **Querying** | Single query engine handles both sources |
| **Separation** | Clear domain boundaries (no overlap) |
| **Auditability** | Track which domain governed which decision |
| **Flexibility** | Easy to add/remove domains |
| **Version Control** | YAML files in git for history tracking |

---

## CONCLUSION

**Business domain knowledge integrates with Tier 1 YAML through perfect structural mirroring:**

1. **CORTEX Tier 1**: Maps technical ACs to technical domains (87 ACs, 4 domains)
2. **Company Tier 1**: Maps business ACs to business domains (50 ACs, 3 domains)
3. **Same Format**: Identical YAML structure enables seamless queries
4. **Single Query Engine**: Works for both CORTEX and Company domains
5. **Graceful Integration**: Optional, falls back to CORTEX-only if unavailable
6. **No Code Changes**: Tier1QueryEngine handles both automatically

**Result**: Clean separation of concerns with elegant, transparent integration via YAML.
