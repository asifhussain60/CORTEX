# Multi-Tier Governance Architecture

**Audience:** Architects, governance teams  
**Version:** 1.0.0

---

## Tier System Overview

CORTEX uses 3-level governance hierarchy with immutable tier precedence:

```
Tier 0 (Immutable Global Rules)
    ↓ Always takes precedence
Tier 1 (Domain-Specific Rules)
    ↓ Domain customizations
Tier 2 (Environment-Specific Rules)
    ↑ Lowest priority, easiest to override
```

---

## Tier 0: Global Governance

**Location:** `cortex_brain/tier0/governance/core-rules.yaml`  
**Rules:** 29 SKULL rules (CORE-001 through CORE-029)  
**Properties:** Immutable, enforced globally

| Rule ID | Category | Example |
|---------|----------|---------|
| CORE-001 | Circuit Breaker | Automatic failure detection |
| CORE-002 | Retry Strategy | Exponential backoff patterns |
| CORE-003 | State Consistency | Transactional semantics |
| ... | ... | ... |

**Cannot be overridden at tier1 or tier2.**

---

## Tier 1: Domain Rules

**Location:** `cortex_brain/tier1/governance/domain-rules.yaml`  
**Properties:** Domain-specific customizations, subject to tier0

**Examples:**
- PlanningOrchestrator domain rules
- SearchOrchestrator domain rules
- Custom orchestrator overrides

**Constraints:** Cannot contradict tier0 rules.

---

## Tier 2: Environment Rules

**Location:** `cortex_brain/tier2/governance/`  
**Subdirectories:**
- `safety-rules.yaml` - Hallucination prevention, input validation
- `credential-protection/` - Secret handling, encryption
- `security/` - Audit, compliance requirements
- `coherence/` - Response coherence rules

**Properties:** Environment-specific (dev/staging/prod), easiest to modify.

**Constraints:** Cannot contradict tier0 or tier1 rules.

---

## Rule Resolution Algorithm

When conflicts occur between tiers:
1. Check tier0 rules first (immutable)
2. If no match, check tier1 rules (domain)
3. If no match, check tier2 rules (environment)
4. If still no match, use default behavior

**Example:** If tier1 domain rule conflicts with tier0 global rule → tier0 wins

---

## Related Documentation

- [System Overview](0-overview.md)
- [Governance Rules Reference](governance-rules.md)
- [Orchestration Engine](3-orchestration-engine.md)

