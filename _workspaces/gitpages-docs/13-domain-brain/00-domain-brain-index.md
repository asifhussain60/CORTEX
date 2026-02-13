# Domain Brain Architecture

> **Summary:** Multi-tier knowledge architecture for business knowledge, query engines, and synthesis  
> **Authority:** cortex_brain/ | **Last Updated:** 2026-01-22

---

## Overview

Domain Brain provides structured knowledge management across TIER 0-3 with specialized query engines and synthesis capabilities for domain-specific orchestration.

**TIER Structure:**
- **TIER 0:** Immutable foundational rules and policies
- **TIER 1:** Domain-specific acceptance criteria and constraints
- **TIER 2:** Engineering standards and best practices
- **TIER 3:** Runtime context and dynamic policies

---

## Architecture

```mermaid
graph TD
  A["Business Knowledge"] -->|TIER 0| T0["Foundational<br/>Rules"]
  T0 -->|TIER 1| T1["Domain<br/>Acceptance Criteria"]
  T1 -->|TIER 2| T2["Engineering<br/>Standards"]
  T2 -->|TIER 3| T3["Runtime<br/>Context"]
  
  T0 & T1 & T2 & T3 -->|query engines| QE["Multi-Modal<br/>Query Engine"]
  QE -->|synthesis| SE["Synthesis<br/>Engine"]
  SE -->|orchestrator input| OR["Domain<br/>Orchestrator"]
  
  style A fill:#4caf50,stroke:#2e7d32,color:#fff
  style T0 fill:#f44336,stroke:#d32f2f,color:#fff,stroke-width:2px
  style T1 fill:#ff9800,stroke:#f57c00,color:#fff
  style T2 fill:#2196f3,stroke:#1565c0,color:#fff
  style T3 fill:#9c27b0,stroke:#7b1fa2,color:#fff
  style QE fill:#00bcd4,stroke:#0097a7,color:#fff
  style SE fill:#00bcd4,stroke:#0097a7,color:#fff
```

---

## Business Knowledge Repository

Centralizes business-facing knowledge:

```python
from cortex.brain.domain_brain.business_knowledge_repository import BusinessKnowledgeRepository

repo = BusinessKnowledgeRepository.instance()

# Query business knowledge
strategy = repo.get_business_strategy("feature_request_handling")
# Returns: {"priority": "HIGH", "approach": "..."}

# Search for relevant knowledge
docs = repo.search("authentication", domain="security")
```

---

## See Also

- [Domain Brain Overview](../01-cortex-brain/00-brain-index.md)
- [TIER 0 Governance](../01-cortex-brain/01-tier0-governance.md)
- [Source: cortex_brain/](../../../cortex_brain/)

---

**Author:** CORTEX Documentation Engine  
**Generated:** 2026-01-22  
