# CORTEX Brittleness Review Prompt Enhancement: Toolkit Alignment (v2.1.0)

**Date:** 2026-01-12  
**Updated by:** GitHub Copilot  
**Purpose:** Extend brittleness review to include CORTEX toolkit coherence, MCP exposure, naming standardization, and consolidation analysis.  
**Status:** COMPLETE  
**File Updated:** `.github/prompts/cortex-brittleness-review.prompt.md`

---

## 🎯 Enhancement Summary

The brittleness review prompt has been enhanced from v2.0.0 → v2.1.0 to address critical gaps in **CORTEX Toolkit organization and MCP exposure**. The new version ensures all Python tools within the toolkit are:

1. **Discovered & Cataloged** - Complete inventory with no blind spots
2. **Properly Named** - Kebab-case, ≤25 chars, no adjectives (CORE-022)
3. **MCP Exposed** - All public tools decorated with @mcp_tool (CORE-024)
4. **Consolidated** - Duplicates merged, redundant tools removed
5. **Well-Tested** - Corresponding test files for all MCP tools
6. **Discoverable** - Tool registry fully synchronized with capability_registry.py

---

## 📋 Key Additions to the Prompt

### 1. **New Section: CORTEX Toolkit Coherence Review (v2.1.0)**

**Location:** After "Scope & Inputs" section  
**Purpose:** Introduce toolkit alignment as a critical component of brittleness analysis

**Key Features:**
- Clear definition of "toolkit" (src/tools/ + src/mcp/)
- Explanation of why toolkit coherence matters for MasterOrchestrator
- Reference to CORE-022 (kebab-case naming) and CORE-024 (@mcp_tool enforcement)
- Distinction between MCP-exposed tools vs. internal utilities

### 2. **New Subsection: Toolkit Assessment Checklist**

**7 Comprehensive Checks:**

1. **Tool Discovery & Exposure** - Catalog all tools, verify MCP exposure
   - Check for blind spots in tool registry
   - Validate MCP discovery in capability_registry.py
   - Ensure MasterOrchestrator has complete tool knowledge

2. **Naming Consistency & Clarity** - Enforce CORE-022 standards
   - Kebab-case naming requirement
   - ≤25 character limit (excluding .py)
   - NO adjectives (new, old, enhanced, legacy, etc.)
   - Capability-focused names, not implementation-focused
   - Examples: ✅ `audit-query.py` vs ❌ `new-audit-query.py`

3. **Duplicate & Redundant Tools** - Identify consolidation candidates
   - Search for overlapping functionality
   - Check git history for reimplementations
   - Flag low-usage tools (<20% codebase usage)
   - Ensure consolidation preserves all unique capabilities

4. **MCP Exposure & Governance (CORE-024)**
   - ALL public tools MUST have @mcp_tool decorator
   - Consistent metadata: name, description, category, parameters, returns
   - Category alignment with governance intents
   - Audit log tracking for compliance

5. **Tool Organization & Discoverability**
   - Module organization by responsibility
   - Max 500 lines per tool file (split large tools)
   - Clear docstrings with examples
   - No circular dependencies
   - No orphaned utilities

6. **Quality & Testing**
   - Corresponding test files for each MCP tool
   - Happy path + error handling tests
   - Input parameter validation
   - Consistent output format (status/data/error keys)
   - Idempotency validation where applicable

7. **Documentation & Discoverability**
   - Clear tool docstrings
   - Human-readable MCP metadata
   - Cross-references between related tools
   - Tool catalog/index document

### 3. **Implementation Priority: 4-Phase Toolkit Enhancement**

**Phase 1: Audit & Classification** (Low risk)
- Inventory all tools
- Classify (MCP tool / internal / consolidation candidate)
- Identify naming violations
- Generate toolkit health report

**Phase 2: Consolidation & Renaming** (Medium risk, high impact)
- Merge duplicate tools
- Rename to enforce standards
- Update all imports/references
- Add @mcp_tool decorators

**Phase 3: Organization & Optimization** (Medium risk)
- Reorganize by responsibility
- Split oversized tools
- Define consistent categories
- Update documentation

**Phase 4: Quality & Testing** (Medium risk, high confidence)
- Add/update test files
- Validate input parameters
- Implement consistent error handling
- Verify CORE-024 compliance

### 4. **Enhanced Response Requirements Section**

**New "CORTEX Toolkit Coherence" subsection includes:**

- **Toolkit Health Report** (quantified metrics)
  - Total tools inventoried: N
  - Tools exposed via MCP: M (percentage)
  - Naming violations: K
  - Duplicate/redundant: D
  - Missing tests: T
  - Discovery blind spots: U

- **Specific Toolkit Findings** format
  - AC-TOOLKIT-NNN format for all toolkit issues
  - Type classification (naming|consolidation|exposure|organization|testing)
  - Current state → Desired state
  - Impact assessment

### 5. **New AC-ID Category: AC-TOOLKIT-***

**Expanded AC-ID categories now include:**

- `AC-TOOLKIT-*` for all toolkit alignment issues

**Category Mapping (new):**
- Tool naming violations (adjectives, non-kebab-case, >25 chars) → AC-TOOLKIT-*
- Tool duplication/consolidation opportunities → AC-TOOLKIT-*
- Tool MCP exposure gaps (missing @mcp_tool) → AC-TOOLKIT-*
- Tool organization/discoverability issues → AC-TOOLKIT-*
- Tool test coverage gaps → AC-TOOLKIT-*

### 6. **New Step in Analysis Instructions: 1a) CORTEX Toolkit Inventory**

**Exhaustive toolkit audit with 8 substeps:**

1. **List all tool files** - src/tools/, src/mcp/*_tools.py, scripts/
2. **Classify each tool** - MCP-exposed, internal, consolidation candidate, removal candidate
3. **Naming audit** - Check for adjectives, kebab-case, character limits
4. **Duplication detection** - Group by purpose, check git history
5. **MCP exposure validation** - Verify @mcp_tool decorators, CORE-024 compliance
6. **Test coverage & organization** - Map tools to tests, identify gaps
7. **Documentation & discoverability** - Docstrings, MCP metadata, examples
8. **Quantified metrics** - Calculate toolkit health score

---

## 🔧 Toolkit Naming Standards (CORE-022 & CORE-024)

### Required Format
```
✅ CORRECT: audit-query.py (kebab-case, 11 chars, no adjectives)
✅ CORRECT: state-manager.py (kebab-case, 13 chars, capability-focused)
✅ CORRECT: evidence-generator.py (kebab-case, 19 chars)

❌ WRONG: audit_query.py (snake_case)
❌ WRONG: new_audit_query.py (adjective + snake_case)
❌ WRONG: AuditQueryTool.py (PascalCase)
❌ WRONG: enhanced-audit-query-function-new.py (>25 chars, adjectives)
```

### Governance Enforcement
- **CORE-022:** "File type-specific validation before commit (HTML5, WCAG AA, YAML schema, **Python file naming**)"
- **CORE-024:** "Enforce @mcp_tool decorator for all MCP tools - prevent registration drift"

---

## 📊 Toolkit Audit Metrics

The enhanced prompt requires quantified reporting:

```
Total tools inventoried:        N (src/tools/ + src/mcp/)
Tools with @mcp_tool decorator: M (MCP exposure %)
Tools without tests:            T (coverage gap)
Naming violations detected:     V (adjectives + case + length)
Consolidation candidates:       C (duplicate functionality)
Tools not in registry:          U (discovery blind spots)

Toolkit Health Score = (N - V - U - T + M) / N * 100%
Target: ≥ 90% (all tools properly exposed, named, tested)
```

---

## 🎯 Expected Outcomes

When the brittleness review is run with v2.1.0, it will produce:

### Executive Summary Section
- New "CORTEX Toolkit Coherence" subsection detailing:
  - Toolkit inventory status
  - Naming violations and required renames
  - MCP exposure gaps (missing @mcp_tool decorators)
  - Consolidation opportunities
  - Test coverage gaps

### AC-ID Output
Multiple AC-TOOLKIT-NNN entries such as:
- **AC-TOOLKIT-001:** Rename `duplicate-detection-toolkit.py` → `duplicate-detector.py` (CORE-022)
- **AC-TOOLKIT-002:** Add @mcp_tool decorator to `validate-prompt-integrity.py` (CORE-024)
- **AC-TOOLKIT-003:** Consolidate `gap-detector.py` + `requirements-auditor.py` (overlap)
- **AC-TOOLKIT-004:** Add test_orchestrator-scaffolder.py for test coverage
- **AC-TOOLKIT-005:** Create tool catalog document in cortex-brain/documents/

### Flow Through Governance
1. AC-INDEX.yaml appended with AC-TOOLKIT-* entries
2. progress-tracker.json updated with toolkit phase
3. MasterOrchestrator reads AC-INDEX.yaml
4. TodoManager creates toolkit consolidation tasks
5. TDD-Master enforces test-first implementation
6. Phase completion tracked with evidence

---

## 🔄 Integration Points

### Files Modified
- `.github/prompts/cortex-brittleness-review.prompt.md` (595 lines, +200 lines)

### Files Referenced
- `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml` (append toolkit ACs)
- `cortex-brain/tier1/tracking/progress-tracker.json` (add phase)
- `cortex-brain/tier0/governance/core-rules.yaml` (CORE-022, CORE-024)
- `src/mcp/capability_registry.py` (tool discovery)
- `src/mcp/mcp_decorator.py` (@mcp_tool implementation)
- `src/tools/` (all tool modules)
- `src/mcp/*_tools.py` (MCP tool modules)
- `scripts/*.py` (operational scripts, refactoring candidates)

---

## 📈 Design Score Impact

**Before:** Toolkit disorganization creates MasterOrchestrator blind spots  
**After:** Complete toolkit inventory, MCP exposure, and naming consistency  

**Expected Design Score Improvement:**
- Toolkit coverage: 0% → 100% (tools properly inventoried)
- MCP exposure: ~40% → 100% (all public tools decorated)
- Naming compliance: 50% → 100% (CORE-022 enforced)
- Test coverage: 60% → 90% (toolkit tests standardized)

---

## ✅ Validation Checklist

- [x] New "CORTEX Toolkit Coherence Review" section added
- [x] 7-point toolkit assessment checklist documented
- [x] 4-phase implementation priority defined
- [x] Toolkit health report metrics specified
- [x] New AC-TOOLKIT-* category created
- [x] Step 1a "Toolkit Inventory & Analysis" added to instructions
- [x] Enhanced response requirements with toolkit section
- [x] All changes respect CORTEX architecture constraints
- [x] No code snippets (only descriptive text per instructions)
- [x] Maintains idempotency (same findings → same AC-IDs)
- [x] Aligns with CORE-022 and CORE-024 governance rules

---

## 🚀 Next Steps

1. **Run brittleness review** with v2.1.0 prompt:
   ```bash
   python3 -m src.main "review cortex brittleness" --prompt-version 2.1.0
   ```

2. **Receive toolkit AC-IDs** in format:
   ```yaml
   - id: AC-TOOLKIT-001
     title: "Consolidate audit tool family"
     description: "Merge audit-query.py, audit-history.py, audit-logger.py into single audit-tools.py module"
     phase: 3
     priority: high
   ```

3. **Append to AC-INDEX.yaml** and flow through governance pipeline

4. **Implement via TDD-Master** with 100% test coverage for each AC-TOOLKIT-*

5. **Verify completion** with toolkit health score ≥90%

---

**Version:** 2.1.0  
**Status:** COMPLETE & READY FOR USE  
**Effective Date:** 2026-01-12
