# Company Domain Synthesis

---
title: Company Domain Synthesis — LENS Company Domain Layer
type: explanation
audience: [Software Developers, Product Owners]
last_verified: 2026-02-28
source_of_truth: cortex/intelligence/provider.py + cortex/intelligence/knowledge/company_domain_loader.py
order: 5
---

> **Brain analogy:** Company Domain Synthesis is the **hippocampus** — it provides the long-term organisational memory that shapes how LENS interprets what it sees. Without it, every scan is context-free; with it, LENS understands that "auth" means OAuth 2.0 with PKCE and "payment" triggers PCI-DSS rules.

---

## Overview

Company Domain Synthesis connects organisation-specific knowledge stored in `company/domains/*.yaml` to the `UnifiedIntelligenceProvider` pipeline. When LENS analyses a repository, company domain profiles inject:

- **Domain-specific governance rules** (e.g., PCI-DSS for payment domains)
- **Architecture patterns** expected for the domain (microservices, event-driven)
- **Key technologies** the organisation uses in that domain
- **Priority signals** that change how LENS ranks findings

This layer sits **above** the registry tier-0 and tier-1 knowledge, ensuring company context always takes precedence.

---

## Architecture

```
cortex-registry/company/domains/
  ├── ecommerce.yaml        # E-commerce domain profile
  ├── fintech.yaml          # Financial technology profile
  ├── healthcare.yaml       # Healthcare compliance profile
  └── devops.yaml           # Internal platform team profile

         ↓  loaded by

cortex/intelligence/knowledge/company_domain_loader.py
  └── CompanyDomainLoader.load() → List[CompanyKnowledge]
         ↓  5-minute TTL cache

cortex/intelligence/provider.py
  └── UnifiedIntelligenceProvider.targeted() / .full()
         └── injects CompanyKnowledge into synthesis context
```

---

## Domain Profile Schema

Each `company/domains/*.yaml` file follows a standard schema:

```yaml
id: ecommerce                          # Unique domain identifier
name: E-Commerce Platform              # Human-readable name
description: >
  Core shopping and checkout services
  for the consumer-facing store.

# Governance rules activated for this domain
governance_rules:
  - PCI-DSS-3.2                        # Payment card data handling
  - OWASP-TOP10                        # Security baseline
  - CORE-008                           # TDD mandatory

# Architecture patterns expected
architecture_patterns:
  - microservices
  - event-driven
  - api-gateway

# Technologies this domain uses
key_technologies:
  - python
  - postgresql
  - redis
  - stripe-sdk

# Priority boosts for LENS signals
priorities:
  security: high
  performance: high
  documentation: medium
```

---

## Knowledge Precedence

Company domain knowledge sits at the top of the tier hierarchy:

| Precedence | Tier | Source | Mutability |
|-----------|------|--------|------------|
| **1 (highest)** | Company | `company/domains/*.yaml` | Organisation managed |
| **2** | Tier 1 | Registry best practices | Curated |
| **3** | Tier 0 | CORTEX core rules | Immutable |
| **4** | Tier 3 | AI-discovered patterns | AI-managed |

When a governance rule appears in both company profile and tier-0, the **company profile annotation takes precedence** for priority/severity but cannot _override_ a CORE rule's enforcement status.

---

## API Usage

### Targeted Synthesis (with company domain)

```python
from cortex.intelligence.provider import UnifiedIntelligenceProvider

provider = UnifiedIntelligenceProvider()

# targeted() loads company domain profiles (5-min TTL cache)
context = await provider.targeted(repo_path="/path/to/service")

# Company knowledge is available in context
for domain in context.company_knowledge:
    print(domain.id)                  # "ecommerce"
    print(domain.governance_rules)    # ["PCI-DSS-3.2", ...]
    print(domain.key_technologies)    # ["python", "postgresql", ...]
```

### Full Synthesis (with ADO sprint context + KG indexing)

```python
# full() additionally fetches ADO work items and indexes the KG
context = await provider.full(repo_path="/path/to/service")

# Sprint context from ADO
sprint = context.sprint_context
print(sprint["sprint_name"])         # "Sprint 42"
print(sprint["open_count"])          # 7
```

### Loading Profiles Directly

```python
from cortex.intelligence.knowledge.company_domain_loader import CompanyDomainLoader
from pathlib import Path

loader = CompanyDomainLoader(
    domains_dir=Path("cortex-registry/company/domains")
)
domains = loader.load()   # Returns List[CompanyKnowledge], cached for 5 minutes
```

---

## Adding a New Domain Profile

1. Create `cortex-registry/company/domains/<domain-id>.yaml` following the schema above
2. The `CompanyDomainLoader` discovers all `.yaml` files automatically — no code changes required
3. Verify the profile loads correctly:

```bash
python3 -c "
from cortex.intelligence.knowledge.company_domain_loader import CompanyDomainLoader
from pathlib import Path
loader = CompanyDomainLoader(Path('cortex-registry/company/domains'))
for d in loader.load():
    print(d.id, d.name)
"
```

4. Run the company domain test suite:

```bash
make test-batch  # runs all tests including intelligence/test_company_domain_loader.py
```

---

## Integration with ADO Sprint Context

When `provider.full()` runs, ADO sprint data flows through `ADOContextMapper`:

```
ADOWorkItemProvider.fetch_stories()
      ↓
ADOContextMapper.map(stories) → {
    "sprint_name": "Sprint 42",
    "stories": [...],
    "open_count": 7,
    "in_progress_count": 3
}
      ↓
UnifiedIntelligenceProvider.full() → context.sprint_context
```

The combined company domain + sprint context allows orchestrators to answer questions like:

- *"Is this service in the ecommerce domain and does it have open security work items?"*
- *"Which PCI-DSS rules apply to the payment service in the current sprint?"*

---

## Related Documents

- [LENS Overview](01-overview.md) — 15-analyzer-component pipeline
- [Context Synthesis](04-synthesis.md) — UnifiedIntelligenceProvider tier model
- [ADO Integration](../05-infrastructure/07-ado-integration.md) — Work item provider setup
- [Brain Tier Architecture](../00-getting-started/04-brain-tier-architecture.md) — Full intelligence flow

---

*Verified against `cortex/intelligence/knowledge/company_domain_loader.py`*
