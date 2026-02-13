# ADR-002: Governance Tier Precedence

> Architecture Decision Record

**Status:** Accepted  
**Date:** 2026-01-20  
**Deciders:** CORTEX Architecture Team  
**Technical Story:** impl-governance-001-context-aware

## Context

CORTEX requires a governance system that enforces rules at different levels of authority. Rules must be immutable at the core level while allowing customization at domain and runtime levels.

## Decision

Implement a four-tier governance hierarchy with strict precedence:

```
tier0 (Core) > tier1 (Domain) > tier2 (Context) > tier3 (Runtime)
```

### Tier Definitions

| Tier | Authority | Mutability | Location |
|------|-----------|------------|----------|
| **tier0** | Core rules (29 CORE-*) | Immutable | `cortex_brain/tier0/governance/` |
| **tier1** | Domain customizations | Admin-mutable | `cortex_brain/tier1/` |
| **tier2** | Context rules (safety, security) | Session-mutable | `cortex_brain/tier2/` |
| **tier3** | Runtime/business rules | Dynamic | Domain Brain |

### Precedence Rules

1. Higher tiers CANNOT override lower tiers
2. tier0 rules are BLOCKED enforcement (operation fails)
3. tier1/tier2 rules are STRICT enforcement (warning + proceed)
4. tier3 rules are ADVISORY (logged only)

## Consequences

### Positive

- Clear authority chain prevents accidental rule bypass
- Immutable core rules ensure security/compliance
- Domain teams can customize within boundaries
- Runtime flexibility for business rules

### Negative

- More complex rule resolution logic
- Potential confusion about which tier applies
- Migration required when promoting rules between tiers

### Risks

- Misconfigured tier1/tier2 could block valid operations
- Performance impact of multi-tier rule checking

## Alternatives Considered

1. **Flat rule system** - Rejected: No clear authority, conflicts possible
2. **Two-tier (core + custom)** - Rejected: Insufficient granularity
3. **Role-based only** - Rejected: Doesn't capture rule type differences

## Related

- [Governance Tiers Diagram](../_diagrams/governance-tiers.mmd)
- [Governance Rules Reference](../../05-reference/governance-rules-reference.md)
- `cortex_brain/tier0/governance/core-rules.yaml`
