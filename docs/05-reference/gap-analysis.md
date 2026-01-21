# Gap Analysis

> Auto-generated from cortex-impl-map.yaml on 2026-01-21

**Last Updated:** 2026-01-21  
**Authority:** cortex-impl-map.yaml v3.9-machine-autonomous-tracks

---

## Overview

This document identifies gaps between the current implementation state and production readiness, along with their impact and resolution paths.

---

## Architecture Conflicts

### Gap #1: Tier Structure Duplication

| Attribute | Value |
|-----------|-------|
| **Location** | `cortex_brain/tier*/` (canonical) vs `cortex/brain/core/governance/` (duplicate) |
| **Impact** | BLOCKS 3 phases: impl-arch-011, impl-arch-022, impl-arch-025. Tier precedence broken. BrainPopulator loads wrong location. |
| **Priority** | P0-CRITICAL |
| **Estimated Effort** | 1 day consolidation |
| **Resolution** | Phase A: Delete cortex/brain/core/governance/, move cortex/brain/core/hallucination_prevention/ → cortex_brain/tier2/governance/, repoint BrainPopulator |
| **Blocked Phases** | impl-arch-011-hallucination, impl-arch-022-mcp-compliance, impl-arch-025-governance-comp |

### Gap #2: MCP Tools Not Centralized

| Attribute | Value |
|-----------|-------|
| **Location** | `cortex/mcp/tools/` (14 stubs scattered, no categorization) |
| **Impact** | BLOCKS impl-arch-022-mcp-compliance. No tool discovery mechanism. Governance of tool access undefined. |
| **Priority** | P0-CRITICAL |
| **Estimated Effort** | 2 days (create registry + reorganize) |
| **Resolution** | Phase B: Create cortex/mcp/registry.py, reorganize tools by category, update server.py discovery |
| **Blocked Phases** | impl-arch-022-mcp-compliance |

### Gap #3: Hallucination Prevention in Wrong Tier

| Attribute | Value |
|-----------|-------|
| **Location** | `cortex_brain/tier2/hallucination_prevention/` (Python files, should be YAML rules) |
| **Impact** | Blocks impl-arch-011. Code not loaded by BrainPopulator tier system. Format inconsistency. |
| **Priority** | P0-CRITICAL |
| **Estimated Effort** | 1 day (consolidation part of Phase A) |
| **Resolution** | Phase A: Convert Python files → YAML, consolidate to cortex_brain/tier2/governance/safety-rules.yaml |
| **Blocked Phases** | impl-arch-011-hallucination |

### Gap #4: Cortex/Brain Duplicates Cortex_Brain

| Attribute | Value |
|-----------|-------|
| **Location** | `cortex/brain/core/` (35+ files) duplicates `cortex_brain/` (41 files, canonical) |
| **Impact** | Confusion about governance authority. Hard to maintain consistency. Single source of truth violated. |
| **Priority** | P0-CRITICAL |
| **Estimated Effort** | 1 day (part of Phase A consolidation) |
| **Resolution** | Phase A: Remove cortex/brain/core/governance/, move tier logic to cortex_brain/, repoint all imports |

---

## Critical Gaps

### Gap #5: 125 Modules Have Tests But No Implementations

| Attribute | Value |
|-----------|-------|
| **Location** | Multiple src.* imports in test files |
| **Impact** | 170 test errors on import failures, production not ready |
| **Priority** | P0-NEXT |
| **Estimated Effort** | 8-12 days implementation + 3-4 days validation |
| **Depends On** | Phase A tier consolidation, Phase B MCP registry |
| **Categories** | core: 87, orchestrators: 9, domain: 14, infrastructure: 5, mcp: 1, other: 9 |

### Gap #6: MCP Tools Are Stubs

| Attribute | Value |
|-----------|-------|
| **Location** | `cortex/mcp/*.py` |
| **Impact** | No functional MCP exposure; impl-arch-022 blocked |
| **Priority** | P0-CRITICAL |
| **Resolution** | Phase B: Create registry + reorganize; impl-arch-022: implement tool logic |
| **Depends On** | Phase B MCP centralization |

### Gap #7: Empty Tier1/Tier2 Directories

| Attribute | Value |
|-----------|-------|
| **Location** | `cortex_brain/tier1/`, `cortex_brain/tier2/` |
| **Impact** | Governance architecture incomplete; hallucination_prevention not loaded |
| **Priority** | P0-CRITICAL |
| **Resolution** | Phase A: Consolidate hallucination_prevention to tier2/governance/safety-rules.yaml |
| **Depends On** | Phase A consolidation |

---

## Resolved Gaps

| Gap | Resolution Date | Implementation | Result |
|-----|----------------|----------------|--------|
| Governance rules not enforced | 2026-01-20 | Context-aware governance pipeline (GOV-CTX-001) | 28/29 rules now functional - 75 tests passing |
| Missing core-rules.yaml | 2026-01-20 | Copied to cortex_brain/tier0/governance/core-rules.yaml | 30 rules loading successfully |
| No routing decision outcome tracking | 2026-01-20 | RoutingAnalyzer with SQLite persistence (INT-001) | 12 tests passing |
| No operation duration baselines | 2026-01-20 | DurationAnalyzer with percentile calculations (INT-002) | 15 tests passing |
| Error logs not analyzed for patterns | 2026-01-20 | ErrorAnalyzer with context sanitization (INT-003) | 15 tests passing |

---

## Moderate Gaps

| Gap | Impact | Priority | Resolution |
|-----|--------|----------|------------|
| Test-to-AC mapping unclear | Hard to verify AC completion | P2 | Document test file AC-ID coverage |
| No cross-phase integration tests | Late discovery of integration bugs | P2-HIGH | Create integration test scenarios |
| Phase dependency tracking incomplete | Risk of implementing phases with unmet dependencies | P2 | Ensure all dependencies documented |
| Orchestrator protocol vs concrete mismatch | 5 protocols, 4 implementations - incomplete | P2 | Document missing orchestrators |
| Dashboard files missing | PHASE-15 claimed complete but no dashboard | P3 | Implement or mark as future work |

---

## Related

- [Architecture Overview](../02-architecture/1-system-overview.md)
- [Remediation Status](./remediation-status.md)
- [Implementation Phases](../02-architecture/6-implementation-phases.md)
