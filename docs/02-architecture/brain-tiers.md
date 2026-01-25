# Brain Tier Architecture

## Four-Tier Governance Model

CORTEX's intelligence is organized in four tiers:

### Tier 0: Immutable Governance (29 CORE Rules)

**Location:** `cortex_brain/tier0/governance/`

Rules include:
- **CORE-008:** TDD - Tests BEFORE code
- **CORE-011:** Type hints MANDATORY
- **CORE-012:** Google-style docstrings
- **CORE-013:** No bare except clauses
- **CORE-026:** Git checkpoint before major changes
- **CORE-027:** Audit trail enforcement
- **CORE-029:** Response header enforcement

### Tier 1: Acceptance Criteria

**Location:** `cortex_brain/tier1/`

- Phase specifications
- AC-ID definitions
- Quality gates
- Delivery requirements

### Tier 2: Response Templates & Boundaries

**Location:** `cortex_brain/tier2/`

- Response format templates
- Boundary definitions
- Hallucination prevention
- Output validation rules

### Tier 3: Knowledge & Best Practices

**Location:** `cortex_brain/tier3/knowledge/`

Contains 35+ YAML files:
- TDD patterns
- Refactoring techniques
- API design principles
- Security best practices
- Domain-specific knowledge

## Knowledge Repository

The knowledge system supports:

- **Discovery:** Auto-scan codebase for new components
- **Ingestion:** Add new patterns and best practices
- **Querying:** Find relevant guidance
- **Updates:** Version control for knowledge
- **Validation:** Verify consistency

---

Next: [Orchestrator Reference](orchestrators.md)
