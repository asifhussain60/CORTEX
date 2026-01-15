# PHASE-16: How Business Domain Knowledge Works with Tier 1 YAML

**Status**: Integration Architecture Explanation  
**Date**: January 15, 2026  
**Question**: "How will company business domain knowledge work with the YAML for business tier?"

---

## QUICK ANSWER

The company's business domain knowledge will **mirror CORTEX's Tier 1 YAML structure** exactly:

```
CORTEX Tier 1                          Company Domain Tier 1
─────────────────────────────────────────────────────────────
ac-domain-mappings.yaml         domain-ac-mappings.yaml
├─ Maps CORTEX ACs              ├─ Maps Business ACs
├─ To CORTEX domains            ├─ To Business domains
├─ (TDD, PLANNING, ADO)         ├─ (Finance, Healthcare, etc)
└─ YAML + SQLite indexed        └─ YAML + SQLite indexed

Integration: Query both when domain endpoint is available
Result: Business domain governance merged with CORTEX governance
```

---

## TIER 1 STRUCTURE PRIMER

### What CORTEX Tier 1 Does (Current)

**File**: `cortex-brain/tier1/acceptance-criteria/ac-domain-mappings.yaml`

```yaml
metadata:
  tier: 1
  title: "Acceptance Criteria to Domain Mappings"
  ac_count: 87
  domain_count: 4
  domains:
    - TDD (Test-Driven Development)
    - PLANNING (Phase Management)
    - ADO (Work Item Management)
    - INTERACTION (Communication)

domains:
  tdd:
    domain_id: "tdd"
    domain_name: "Test-Driven Development"
    ac_count: 28
    acceptance_criteria:
      - ac_id: "AC-AR-006-01"
        title: "pytest plugin architecture"
        categories: ["test_execution", "code_coverage"]
        severity: "HIGH"
      
      - ac_id: "AC-AR-006-02"
        title: "Test scaffolding & fixtures"
        categories: ["fixtures", "test_isolation"]
        severity: "HIGH"
```

### Purpose of Tier 1

1. **Maps ACs to Domains**: Answers "Which domain owns this AC?"
2. **Maps Domains to ACs**: Answers "What ACs belong to this domain?"
3. **Categorization**: Groups similar concerns together
4. **Severity Tracking**: Marks critical vs optional
5. **Governance**: Controls which domains have authority over which ACs

---

## HOW COMPANY DOMAIN KNOWLEDGE INTEGRATES

### Pattern 1: Same YAML Structure (Company Domain Brain)

**File**: `domain-brain/tier1/acceptance-criteria/domain-ac-mappings.yaml`

```yaml
metadata:
  tier: 1
  title: "Business Domain to AC Mappings"
  ac_count: 50  # Company's ACs
  domain_count: 3
  domains:
    - FINANCIAL (Financial Services)
    - HEALTHCARE (Healthcare & HIPAA)
    - COMPLIANCE (Regulatory & Audit)

domains:
  financial:
    domain_id: "financial"
    domain_name: "Financial Services"
    orchestrator: "FinancialOrchestrator"
    tier_access: [0, 1, 2]
    primary_rules: [
      "FINANCIAL-RULE-001: Settlement rules",
      "FINANCIAL-RULE-002: Audit trails",
      "FINANCIAL-RULE-003: Reconciliation"
    ]
    ac_count: 20
    acceptance_criteria:
      - ac_id: "AC-FIN-001-01"
        title: "Transaction Settlement"
        description: "Ensure T+2 settlement compliance"
        categories: ["settlement", "compliance"]
        severity: "CRITICAL"
      
      - ac_id: "AC-FIN-001-02"
        title: "Audit Trail Recording"
        description: "Immutable audit trail for all transactions"
        categories: ["audit", "compliance"]
        severity: "CRITICAL"
      
      - ac_id: "AC-FIN-001-03"
        title: "Reconciliation Process"
        description: "Daily reconciliation against settlement"
        categories: ["reconciliation", "validation"]
        severity: "HIGH"

  healthcare:
    domain_id: "healthcare"
    domain_name: "Healthcare & HIPAA"
    ac_count: 18
    acceptance_criteria:
      - ac_id: "AC-HEALTH-001-01"
        title: "HIPAA Compliance"
        description: "Patient data encryption (AES-256)"
        categories: ["encryption", "compliance"]
        severity: "CRITICAL"
      
      - ac_id: "AC-HEALTH-001-02"
        title: "Audit Logging"
        description: "Log all PHI access events"
        categories: ["audit", "logging"]
        severity: "CRITICAL"

  compliance:
    domain_id: "compliance"
    domain_name: "Regulatory Compliance"
    ac_count: 12
    acceptance_criteria:
      - ac_id: "AC-COMP-001-01"
        title: "GDPR Data Rights"
        description: "Support data export/deletion requests"
        categories: ["gdpr", "data_rights"]
        severity: "CRITICAL"
```

### Pattern 2: Same Bidirectional Queries

**CORTEX Query** (Existing):
```python
# Query: "Get all ACs for TDD domain"
query = "domains.tdd.acceptance_criteria[*].ac_id"
result = [
  "AC-AR-006-01",  # pytest plugin architecture
  "AC-AR-006-02",  # Test scaffolding
  "AC-AR-006-03",  # Coverage reporting
  # ... 25 more
]

# Query: "Get severity of AC-AR-006-01"
query = "domains.tdd.acceptance_criteria[0].severity"
result = "HIGH"

# Query: "Get domain for AC-AR-006-01"
query = "ac_id: AC-AR-006-01 → domain: tdd"
result = "tdd"
```

**Company Domain Query** (Same Pattern):
```python
# Query: "Get all ACs for FINANCIAL domain"
query = "domains.financial.acceptance_criteria[*].ac_id"
result = [
  "AC-FIN-001-01",  # Transaction Settlement
  "AC-FIN-001-02",  # Audit Trail Recording
  "AC-FIN-001-03",  # Reconciliation Process
  # ... 17 more
]

# Query: "Get severity of AC-FIN-001-01"
query = "domains.financial.acceptance_criteria[0].severity"
result = "CRITICAL"

# Query: "Get domain for AC-FIN-001-01"
query = "ac_id: AC-FIN-001-01 → domain: financial"
result = "financial"
```

---

## INTEGRATION POINT: Tier 1 Query Layer

### How CORTEX Queries Tier 1 (Current)

```python
# src/core/tier1_query.py

class Tier1QueryEngine:
    def __init__(self, cortex_tier1_path, domain_tier1_path=None):
        self.cortex_mappings = load_yaml(cortex_tier1_path)
        self.domain_mappings = load_yaml(domain_tier1_path) if domain_tier1_path else None
    
    def get_domain_for_ac(self, ac_id):
        """Query: Which domain owns this AC?"""
        # Check CORTEX first
        for domain_name, domain_data in self.cortex_mappings['domains'].items():
            for ac in domain_data['acceptance_criteria']:
                if ac['ac_id'] == ac_id:
                    return {
                        'source': 'cortex',
                        'domain': domain_name,
                        'ac': ac
                    }
        
        # Check Domain Brain if available
        if self.domain_mappings:
            for domain_name, domain_data in self.domain_mappings['domains'].items():
                for ac in domain_data['acceptance_criteria']:
                    if ac['ac_id'] == ac_id:
                        return {
                            'source': 'domain',
                            'domain': domain_name,
                            'ac': ac
                        }
        
        return None

    def get_ac_severity_with_domain(self, ac_id):
        """Get severity + domain context"""
        cortex_result = self.get_domain_for_ac(ac_id)  # CORTEX ACs
        
        if self.domain_mappings:
            domain_result = query_domain_brain(ac_id)  # Domain ACs
            
            # Merge results
            return {
                'cortex_severity': cortex_result['ac']['severity'] if cortex_result else None,
                'domain_severity': domain_result['ac']['severity'] if domain_result else None,
                'effective_severity': max(severities)  # Use higher severity
            }
        else:
            # Graceful: works without domain
            return {
                'cortex_severity': cortex_result['ac']['severity'] if cortex_result else None,
                'domain_severity': None,
                'effective_severity': cortex_result['ac']['severity'] if cortex_result else None
            }
```

### How Queries Merge (With Domain Brain)

```python
def get_all_domain_mappings_merged():
    """Get CORTEX domains + business domains combined"""
    
    cortex_domains = load_yaml('cortex-brain/tier1/acceptance-criteria/ac-domain-mappings.yaml')
    
    # Graceful: works without domain brain
    domain_domains = load_yaml(config.DOMAIN_BRAIN_PATH) if config.DOMAIN_BRAIN_AVAILABLE else {}
    
    merged = {
        'cortex_domains': cortex_domains['domains'],  # TDD, PLANNING, ADO, INTERACTION
        'business_domains': domain_domains['domains'] if domain_domains else {},  # FINANCIAL, HEALTHCARE, COMPLIANCE
        'metadata': {
            'cortex_ac_count': cortex_domains['metadata']['ac_count'],
            'business_ac_count': domain_domains['metadata']['ac_count'] if domain_domains else 0,
            'total_ac_count': cortex_domains['metadata']['ac_count'] + (domain_domains['metadata']['ac_count'] if domain_domains else 0),
        }
    }
    
    return merged
```

---

## REAL-WORLD EXAMPLE: Financial AC Workflow

### Scenario: CORTEX Gets Request for Financial Feature

```python
# Request comes in: "Generate financial settlement code"

# Step 1: Query CORTEX Tier 1
cortex_domains = query_tier1("domains")
# Result:
# - TDD domain: AC-AR-006-01 (pytest), AC-AR-006-02 (fixtures), ...
# - PLANNING domain: Phase governance
# - ADO domain: Work item tracking
# - INTERACTION domain: Audit logging

# Step 2: Query Domain Brain Tier 1 (if available)
domain_domains = query_domain_brain_tier1("domains")
# Result:
# - FINANCIAL domain: AC-FIN-001-01 (settlement), AC-FIN-001-02 (audit), AC-FIN-001-03 (reconciliation)
# - HEALTHCARE domain: (not relevant here)
# - COMPLIANCE domain: AC-COMP-001-01 (GDPR)

# Step 3: Merge and Apply Rules
# CORTEX Rules (mandatory):
# ├─ TDD: Must have 100% test coverage
# ├─ PLANNING: Must follow phase-12 governance
# ├─ ADO: Must link to work items
# └─ INTERACTION: Must audit all decisions

# Domain Rules (if available):
# ├─ FINANCIAL: Must follow T+2 settlement
# ├─ FINANCIAL: Must maintain immutable audit trail
# ├─ FINANCIAL: Must reconcile daily
# └─ COMPLIANCE: Must log all access

# Step 4: Generate Code with Merged Context
generated_code = generate_code(
    request="financial settlement",
    cortex_rules=cortex_domains,
    domain_rules=domain_domains if available else None
)

# Result: Code that satisfies BOTH CORTEX AND FINANCIAL domain rules
```

---

## TIER 1 YAML STRUCTURE: Side-by-Side

### CORTEX (Technical Domains)

```yaml
domains:
  tdd:
    domain_name: "Test-Driven Development"
    ac_count: 28
    acceptance_criteria:
      - ac_id: "AC-AR-006-01"
        title: "pytest plugin architecture"
        severity: "HIGH"
  
  planning:
    domain_name: "Phase Management"
    ac_count: 15
    acceptance_criteria:
      - ac_id: "AC-AR-001-01"
        title: "Phase enforcement"
        severity: "CRITICAL"
  
  ado:
    domain_name: "Work Item Management"
    ac_count: 20
    acceptance_criteria:
      - ac_id: "AC-FR-003-01"
        title: "Work item linking"
        severity: "HIGH"
  
  interaction:
    domain_name: "Communication & Audit"
    ac_count: 12
    acceptance_criteria:
      - ac_id: "AC-FR-001-01"
        title: "Audit logging"
        severity: "CRITICAL"
```

### Company Domain (Business Domains)

```yaml
domains:
  financial:
    domain_name: "Financial Services"
    ac_count: 20
    acceptance_criteria:
      - ac_id: "AC-FIN-001-01"
        title: "Transaction Settlement (T+2)"
        severity: "CRITICAL"
  
  healthcare:
    domain_name: "Healthcare & HIPAA"
    ac_count: 18
    acceptance_criteria:
      - ac_id: "AC-HEALTH-001-01"
        title: "HIPAA Compliance (AES-256 encryption)"
        severity: "CRITICAL"
  
  compliance:
    domain_name: "Regulatory Compliance"
    ac_count: 12
    acceptance_criteria:
      - ac_id: "AC-COMP-001-01"
        title: "GDPR Data Rights"
        severity: "CRITICAL"
```

---

## UNIFIED QUERY RESPONSE

### Before (CORTEX-Only)

```json
{
  "ac_id": "AC-AR-006-01",
  "title": "pytest plugin architecture",
  "domain": "tdd",
  "domain_name": "Test-Driven Development",
  "severity": "HIGH",
  "categories": ["test_execution", "code_coverage"]
}
```

### After (CORTEX + Domain Brain)

```json
{
  "ac_id": "AC-AR-006-01",
  "title": "pytest plugin architecture",
  "cortex_context": {
    "domain": "tdd",
    "domain_name": "Test-Driven Development",
    "severity": "HIGH",
    "categories": ["test_execution", "code_coverage"]
  },
  "domain_context": {
    "applicable_business_domains": [
      {
        "domain": "financial",
        "reason": "Financial services need audit-grade test coverage",
        "applicable_rules": [
          "AC-FIN-001-02: Immutable audit trail",
          "AC-COMP-001-01: GDPR compliance logging"
        ]
      }
    ]
  }
}
```

---

## IMPLEMENTATION: Adding Domain Tier 1 (Company Project)

### What Company Needs to Create

```
domain-brain/
└─ tier1/
   ├─ README.md
   ├─ acceptance-criteria/
   │  └─ domain-ac-mappings.yaml (same structure as CORTEX)
   ├─ governance/
   │  ├─ domain-mutability-rules.yaml
   │  └─ business-rules.yaml
   └─ tracking/
      └─ progress-tracker.json
```

### Step 1: Create YAML Structure (Same as CORTEX)

**Company creates**: `domain-brain/tier1/acceptance-criteria/domain-ac-mappings.yaml`

```yaml
metadata:
  tier: 1
  title: "Business Domain to AC Mappings"
  description: "Maps company business ACs to domains (Financial, Healthcare, etc)"
  created_at: "2026-01-XX"
  ac_count: 50
  domain_count: 3

domains:
  financial:
    domain_id: "financial"
    domain_name: "Financial Services"
    orchestrator: "FinancialOrchestrator"  # Company builds this
    tier_access: [0, 1, 2]
    ac_count: 20
    acceptance_criteria:
      - ac_id: "AC-FIN-001-01"
        title: "T+2 Settlement Compliance"
        description: "Transactions settle within 2 business days"
        categories: ["settlement", "compliance"]
        severity: "CRITICAL"
      - ac_id: "AC-FIN-001-02"
        title: "Audit Trail (Immutable)"
        description: "All transactions logged immutably for audit"
        categories: ["audit", "logging"]
        severity: "CRITICAL"
      # ... 18 more ACs
```

### Step 2: CORTEX Auto-Queries (No Code Changes Needed)

```python
# CORTEX's existing Tier1QueryEngine automatically handles both:

# Query works the same way:
result = tier1_query.get_domain_for_ac("AC-FIN-001-01")

# If domain brain endpoint is configured:
# → Queries domain-brain/tier1/ (company's YAML)
# Otherwise:
# → Uses only CORTEX tier1/ (graceful degradation)

# Both return same structure → No CORTEX code changes needed
```

---

## BENEFITS OF YAML-BASED TIER 1 INTEGRATION

### 1. **Consistency**
- Company Tier 1 has **exact same structure** as CORTEX Tier 1
- Same field names: `domain_id`, `ac_id`, `severity`, `categories`
- Same query patterns work for both

### 2. **No Code Duplication**
- Company uses same YAML format
- CORTEX query engine works unchanged
- Graceful degradation (works without Domain Brain)

### 3. **Clear Separation**
- CORTEX controls: TDD, PLANNING, ADO, INTERACTION domains
- Company controls: FINANCIAL, HEALTHCARE, COMPLIANCE domains
- No overlap, no conflicts

### 4. **Extensibility**
- Company can add new domains without touching CORTEX
- CORTEX remains focused on orchestration
- Company adds business governance as needed

### 5. **Audit Trail**
- Both systems track which AC came from which domain
- Compliance audits can show "CORTEX + Financial rules applied"
- Immutable trail of governance decisions

---

## QUERY EXAMPLES: Tier 1 In Action

### Example 1: "What severity is this AC?"

```python
# CORTEX-only:
severity = tier1.get_severity("AC-AR-006-01")
# → "HIGH" (from CORTEX TDD domain)

# With Domain Brain:
severity = tier1.get_severity_merged("AC-AR-006-01")
# → {"cortex": "HIGH", "domain": "CRITICAL" (if also in financial), "effective": "CRITICAL"}
```

### Example 2: "Which domains cover this AC?"

```python
# CORTEX-only:
domains = tier1.get_domains_for_ac("AC-AR-006-01")
# → ["tdd"]

# With Domain Brain:
domains = tier1.get_domains_for_ac_merged("AC-AR-006-01")
# → ["tdd"] from CORTEX + ["financial"] from Domain (if applicable)
```

### Example 3: "What are all ACs for a domain?"

```python
# CORTEX query:
cortex_ac_list = tier1.get_acs_for_domain("tdd")
# → [AC-AR-006-01, AC-AR-006-02, ..., AC-AR-006-28]

# Company Domain query:
company_ac_list = tier1.get_acs_for_domain("financial")
# → [AC-FIN-001-01, AC-FIN-001-02, ..., AC-FIN-001-20]

# Combined:
all_acs = tier1.get_all_acs_merged()
# → All CORTEX ACs + All Company ACs (87 + 50 = 137 total)
```

---

## CONCLUSION

**The company's business domain knowledge works with Tier 1 YAML by mirroring the exact structure:**

1. **Same YAML Format**: `domain-ac-mappings.yaml` (same as `ac-domain-mappings.yaml`)
2. **Same Fields**: `domain_id`, `ac_id`, `severity`, `categories`, `acceptance_criteria`
3. **Same Query Pattern**: CORTEX's Tier1QueryEngine works unchanged
4. **Graceful Integration**: Domain queries optional, CORTEX always works
5. **No Code Changes**: CORTEX Tier 1 doesn't need modification
6. **Clear Separation**: Each system (CORTEX and Company) owns its domains

**Result**: Company can build their Domain Brain tier independently, and CORTEX automatically merges queries when the endpoint is configured. Perfect separation of concerns with seamless integration.
