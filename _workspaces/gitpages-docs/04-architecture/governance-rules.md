# Governance Rules Reference

> Auto-generated from cortex-impl-map.yaml on 2026-01-21

**Version:** 1.0.0  
**Last Updated:** 2026-01-21

---

## Overview

CORTEX uses a multi-tier governance system with immutable tier precedence (tier0 > tier1 > tier2). Rules are enforced at global, domain, and environment levels.

---

## File Naming Convention

- **Format:** kebab-case, ≤25 characters
- **Authority:** Filesystem scan + pytest collection + code analysis
- **Update Frequency:** On major implementation changes
- **Archive Policy:** Move old versions to `_archives/` with timestamp

---

## Documented Rules

| Rule ID | Description |
|---------|-------------|
| **CORE-001** | <500 lines per turn |
| **CORE-008** | Tests before code (TDD) |
| **CORE-011** | All functions typed |
| **CORE-012** | Google docstrings |
| **CORE-013** | No bare except |
| **CORE-026** | Git checkpoints |
| **CORE-027** | Audit trail |
| **CORE-028** | Kebab-case ≤25 chars |

---

## Tier Structure

### Tier 0 - Core Rules (Immutable)

- **Location:** `cortex_brain/tier0/governance/core-rules.yaml`
- **Rules:** 29 CORE-* rules
- **Status:** ✅ CREATED (2026-01-20)

### Tier 1 - Domain Rules

- **Location:** `cortex_brain/tier1/governance/domain-rules.yaml`
- **Rules:** Domain customizations
- **Status:** 🔲 Empty (pending Phase J)

### Tier 2 - Context Rules

- **Location:** `cortex_brain/tier2/governance/`
- **Rules:** Safety rules, credential protection, security policies, hallucination prevention
- **Status:** 🔲 Empty (pending Phase J)

---

## Governance Database

- **Location:** `cortex_brain/state/governance.db`
- **Status:** ✅ Active

---

## Rule Application

Rules apply with strict precedence:
- **Tier 0:** Rules are immutable, enforced globally, cannot be overridden
- **Tier 1:** Domain rules must respect tier0 rules
- **Tier 2:** Environment rules must respect tier0+tier1

When conflicts occur, tier0 rules override tier1, which override tier2. This ensures immutable global governance cannot be weakened at domain or environment levels.

---

## Governance Compliance Status

| Requirement | Status | Source |
|-------------|--------|--------|
| Phases tracked with phase_tracker | ✅ IMPLEMENTED | cortex-builder.prompt.md §3 |
| core-rules.yaml exists | ✅ CREATED | cortex_brain/tier0/governance/ |
| Single source of truth | ⏳ PENDING | Per cortex-builder.prompt.md |

---

## Related Documentation

- [Architecture Overview](./1-system-overview.md)
- [Design Principles](./2-design-principles.md)
- [Implementation Phases](./6-implementation-phases.md)
- [Definition of Ready](./definition-of-ready.md)
- [Governance Tiers Diagram](../_diagrams/governance-tiers.mmd)

