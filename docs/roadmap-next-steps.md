# Next Steps: Complete Phase YAML Creation
# Date: 2026-01-20

## Status

**Completed**: 4/25 phase files created
**Remaining**: 19 phase files to create

## Template Pattern

Each phase file should be ~100-150 lines following this structure:

```yaml
# [Title] - IMPLEMENTED/STUB/NOT_STARTED
# Phase ID: [id]
# Status: [status]
# Tests: [count] passing

metadata:
  id: "[kebab-case-id]"
  title: "[Full Title]"
  status: "COMPLETED|STUB|NOT_STARTED"
  locked: true|false
  completed_at: "[ISO timestamp]"
  tests_passing: [number]
  ac_count: [number]

description: |
  Brief description of what the phase implements.

acceptance_criteria:
  AC-XXX-01:
    title: "[AC title]"
    status: "IMPLEMENTED|STUB|NOT_STARTED"
    tests: [count]
    files:
      - "[implementation files]"
    test_files:
      - "[test files]"

implementation:
  modules:
    - "[module paths]"
  key_classes:
    - "[class names]"

test_summary:
  total_tests: [count]
  categories:
    [category]: [count]
  pass_rate: "[percentage]"
  coverage: "[percentage]"

governance:
  rules_enforced:
    - "CORE-*: [rule description]"
  audit_entries: [count]
  hash_chain_valid: true|false

gaps:
  - gap: "[description]"
    impact: "[impact]"
    resolution: "[resolution]"

notes: |
  Additional context.
```

## Remaining Phases to Document

### Priority 1: Core Infrastructure (8 phases)
1. **arch-008-orchestrators** (Core Orchestrators)
   - AC count: 6
   - Tests: 161
   - Files: cortex/orchestrators/

2. **arch-009-governance** (Governance Tools)
   - AC count: 8
   - Tests: 133
   - Files: cortex/core/governance/

3. **arch-010-adaptive** (Adaptive Execution)
   - AC count: 5
   - Tests: 106
   - Files: cortex/orchestrators/adaptive/

4. **arch-011-hallucination** (Hallucination Prevention)
   - AC count: 6
   - Tests: 160
   - Files: cortex/core/hallucination/

5. **arch-012-knowledge** (Knowledge Ecosystem)
   - AC count: 7
   - Tests: 243
   - Files: cortex/brain/knowledge/

6. **arch-013-observability** (Observability)
   - AC count: 9
   - Tests: 141
   - Files: cortex/infrastructure/observability/

7. **arch-005-hardening** (Production Hardening)
   - AC count: 12
   - Tests: 45
   - Files: cortex/core/security/

8. **arch-006-brittleness** (Brittleness Fixes)
   - AC count: 17
   - Tests: ~100
   - Files: Multiple locations

### Priority 2: Advanced Features (8 phases)
9. **arch-015-dashboard** (Dashboard)
   - AC count: 16
   - Tests: 48
   - Status: CLAIMED_COMPLETE (no dashboard files found)

10. **arch-016-continuation** (Orchestrator Continuation)
    - AC count: 9
    - Tests: 155
    - Files: cortex/orchestrators/continuation/

11. **arch-017-domain-brain** (Domain Brain)
    - AC count: 12
    - Tests: 353
    - Files: cortex/brain/domain/

12. **arch-018-devx** (Developer Experience)
    - AC count: 4
    - Tests: 135
    - Files: cortex/devx/

13. **arch-019-template-tool** (Template Tools)
    - AC count: 6
    - Tests: 89
    - Files: cortex/tools/template/

14. **arch-020-template-content** (Template Content)
    - AC count: 6
    - Tests: 68
    - Files: cortex_brain/tier2/templates/

15. **arch-023-complexity** (Complexity Gate)
    - AC count: 4
    - Tests: ~30
    - Files: cortex/core/complexity/

16. **arch-024-response** (Response Composition)
    - AC count: 4
    - Tests: 172
    - Files: cortex/orchestrators/response/

### Priority 3: Specialized (3 phases)
17. **arch-022-mcp-compliance** (MCP Protocol)
    - AC count: 8
    - Tests: ~50
    - Status: STUB_ONLY
    - Files: cortex/mcp/

18. **arch-025-governance-comp** (Governance Composite)
    - AC count: 8
    - Tests: 183
    - Files: cortex/core/governance/composite/

19. **remed-008-init-files** (Package Init Files)
    - AC count: 6
    - Tests: 42
    - Files: cortex/__init__.py, cortex_brain/__init__.py, etc.

## File Naming Convention

All phase files must follow **CORE-028**:
- Format: `impl-[phase-id].yaml`
- Kebab-case
- ≤25 chars (excluding .yaml extension)

Examples:
- `impl-arch-008-orch.yaml` (21 chars) ✓
- `impl-arch-009-gov.yaml` (19 chars) ✓
- `impl-arch-010-adapt.yaml` (21 chars) ✓
- `impl-arch-011-halluc.yaml` (22 chars) ✓
- `impl-remed-008-init.yaml` (21 chars) ✓

## Validation Checklist

For each phase file:
- [ ] File name follows CORE-028 (kebab-case, ≤25 chars)
- [ ] Located in `_workspaces/roadmap/phases/`
- [ ] AC count matches test file references
- [ ] Test counts are actual (from pytest collection)
- [ ] Implementation files exist on filesystem
- [ ] Status reflects reality (IMPLEMENTED/STUB/NOT_STARTED)
- [ ] Gaps section documents missing pieces
- [ ] No aspirational claims

## How to Generate

### Automated Approach (Recommended)
Use subagent to scan each phase's test files and implementation:

```
For phase [id]:
1. Find all test files with AC-ID pattern matching phase
2. Count tests per AC-ID
3. Find implementation files referenced in tests
4. Generate phase YAML following template
5. Validate against filesystem
```

### Manual Approach
1. Identify phase AC-IDs from tests/
2. Count tests: `grep -r "AC-[ID]" tests/ | wc -l`
3. Find implementation files: `grep -r "class|def" cortex/[module]/`
4. Fill template
5. Validate

## Authority

- **Test counts**: From pytest collection, not roadmap claims
- **AC-IDs**: From test file headers, not assumptions
- **Implementation status**: From filesystem scan, not documentation
- **Gaps**: From comparison of claimed vs actual

## Output Location

All phase files go to:
```
_workspaces/roadmap/phases/impl-[phase-id].yaml
```

No files in root, no `.md` files, no duplication.
