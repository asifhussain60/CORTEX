# Architecture Decision Record: cortex/ as Canonical Package

**Status:** ACCEPTED  
**Date:** 2026-01-20  
**Decision ID:** ADR-001-CORTEX-CANONICAL-PACKAGE

---

## Context

During CORTEX development, there was a discrepancy between deployment design documentation (cortex-deploy.prompt.md) and the actual implementation structure:

- **Design Documentation** specified `cortex_toolkit/` as the "central implementation hub exposed via MCP"
- **Actual Implementation** evolved with `cortex/` as the main package containing 388 Python files
- **Ghost Folder** `cortex_toolkit/` existed but only contained `cortex_toolkit/core/__init__.py` (empty placeholder)

This created confusion about:
1. Where to add new functionality
2. Which package is authoritative
3. Whether MCP tools should be in cortex/ or cortex_toolkit/

## Decision

**cortex/ is the ONLY canonical implementation package for CORTEX.**

The empty `cortex_toolkit/` folder has been deleted, and all documentation updated to reflect cortex/ as the authoritative location.

## Rationale

### Why cortex/ (Not cortex_toolkit/)

1. **Proven Implementation** 
   - 388 Python files already in cortex/
   - 400+ tests importing from cortex.*
   - All MCP functionality complete in cortex/mcp/
   - Working system with 23+ MCP tools exposed

2. **Risk vs Benefit**
   - Renaming cortex/ → cortex_toolkit/ would require:
     - Updating 388 implementation files
     - Updating 400+ test imports
     - Potential test breakage during migration
     - Hours of refactoring work
   - For zero functional benefit (system already works)

3. **Documentation Follows Code**
   - Design docs (cortex-deploy.prompt.md) written after implementation
   - cortex_toolkit/ was aspirational placeholder never populated
   - Better to align docs with proven working code
   - Than to refactor working code to match outdated design docs

4. **Clear Separation of Concerns**
   - `cortex/` = Implementation (orchestrators, MCP, tools, API)
   - `cortex_brain/` = Governance (tier0/1/2 rules, state management)
   - Clean, logical boundary

## Consequences

### Positive

- ✅ Single source of truth: cortex/ is canonical
- ✅ No confusion about where to add new code
- ✅ Documentation matches implementation reality
- ✅ No risk of breaking working system
- ✅ Clear import pattern: `from cortex.mcp import ...`

### Negative

- ⚠️ Design documents needed updating (completed in PHASE-ARCH-ALIGNMENT-001)
- ⚠️ cortex_toolkit/ references in historical docs (archived, not removed)

### Neutral

- Package name is `cortex` not `cortex_toolkit` (both are semantically valid)
- Import pattern `cortex.*` is concise and clear

## Alternatives Considered

### Alternative 1: Rename cortex/ → cortex_toolkit/

**Pros:**
- Would align with original design documentation
- "toolkit" name emphasizes MCP exposure

**Cons:**
- 12+ hours of refactoring work
- Risk breaking 400+ tests
- Changes working, proven implementation
- No functional benefit

**Decision:** REJECTED (too much risk for no gain)

### Alternative 2: Populate cortex_toolkit/ as MCP Facade

**Pros:**
- Maintains existing cortex/ imports
- Could provide MCP-specific export layer

**Cons:**
- Creates dual structure (cortex/ AND cortex_toolkit/)
- Adds complexity (two entry points for same functionality)
- Doesn't solve the core issue (documentation gap)
- Maintenance burden (keeping two packages in sync)

**Decision:** REJECTED (adds complexity without solving root cause)

### Alternative 3: Update Documentation to Match Reality (SELECTED)

**Pros:**
- No code changes required
- Zero risk to working system
- Fast execution (2 hours)
- Documents proven implementation
- Eliminates confusion permanently

**Cons:**
- Design documentation becomes "as-built" not "as-designed"

**Decision:** ACCEPTED ✅

## Implementation

Executed in **PHASE-ARCH-ALIGNMENT-001** (2 hours):

1. ✅ Deleted `cortex_toolkit/` folder
2. ✅ Updated `.github/prompts/cortex-deploy.prompt.md`
3. ✅ Created this ADR
4. ✅ Updated cortex-master.yaml governance rules
5. ✅ Validated no cortex_toolkit references remain

## Governance

Added to `cortex-master.yaml` governance rules:

```yaml
canonical_package:
  status: ENFORCED
  rule: "cortex/ is the ONLY canonical implementation package"
  forbidden:
    - "cortex_toolkit/ (deleted 2026-01-20)"
    - "Multiple parallel implementation folders"
  required:
    - "All Python implementation in cortex/"
    - "cortex_brain/ for tier0/1/2 governance only"
  rationale: "ADR: docs/ARCH-DECISION-RECORD-CORTEX-CANONICAL-PACKAGE.md"
```

## Current Structure

```
CORTEX/
├── cortex/                      # CANONICAL IMPLEMENTATION (388 files)
│   ├── api/                     # API layer
│   ├── brain/                   # Brain integration (269 files)
│   ├── core/                    # Core utilities
│   ├── infrastructure/          # Infrastructure
│   ├── mcp/                     # MCP server (23+ tools)
│   ├── orchestrators/           # Orchestrators (41 files)
│   └── tools/                   # Tools
├── cortex_brain/                # GOVERNANCE & STATE
│   ├── tier0/                   # Core rules (28 immutable)
│   ├── tier1/                   # Orchestrator rules
│   ├── tier2/                   # Domain rules
│   └── state/                   # Runtime state
├── tests/                       # Test suite (400+ files)
└── docs/                        # Documentation
```

## MCP Exposure

All MCP tools are correctly implemented in **cortex/mcp/**:

- `cortex/mcp/server.py` - MCP server
- `cortex/mcp/decorators.py` - @mcp_tool decorator
- `cortex/mcp/endpoints.py` - Discovery endpoints
- `cortex/mcp/domain_operations.py` - MCP-exposed operations
- `cortex/mcp/protocol.py` - JSON-RPC 2.0 protocol

**Evidence:**
- 23+ MCP tools registered and exposed
- 50+ MCP tests passing
- Full MCP audit: `docs/MCP-EXPOSURE-AUDIT-REPORT-20260119.md`

## References

- **Gap Analysis:** `_workspaces/roadmap/reports/ARCHITECTURAL-GAP-ANALYSIS-20260120.yaml`
- **Remediation Phase:** `_workspaces/roadmap/phases/phase-arch-alignment-001.yaml`
- **Complete Report:** `_workspaces/roadmap/reports/CORTEX-STRUCTURAL-ANALYSIS-COMPLETE-20260120.md`
- **Master Roadmap:** `_workspaces/roadmap/cortex-master.yaml`

## Status

**ACCEPTED and ENFORCED**

cortex/ is the canonical implementation package. cortex_toolkit/ is deleted and forbidden from resurrection by governance rules.

---

**Last Updated:** 2026-01-20  
**Phase:** PHASE-ARCH-ALIGNMENT-001  
**Authority:** cortex-builder.prompt.md governance
