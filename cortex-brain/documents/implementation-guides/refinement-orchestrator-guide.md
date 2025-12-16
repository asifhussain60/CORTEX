# Refinement Orchestrator Implementation Guide

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Copyright © 2025 Asif Hussain. All rights reserved.**

---

## Overview

The **Refinement Orchestrator** performs holistic CORTEX system improvement through automated discovery, analysis, and enhancement across code, tests, and documentation.

## 7-Phase Workflow

### Phase 1: Discovery & Analysis
**Duration:** ~10 minutes  
**Blocking:** Yes  

Comprehensive system analysis:
- Code complexity (cyclomatic, cognitive)
- Dead code detection
- Test coverage gaps
- Documentation drift
- Dependency analysis

**Output:** `cortex-brain/documents/reports/refinement-discovery-{timestamp}.md`

### Phase 2: SKULL Test Review
**Duration:** ~15 minutes  
**Blocking:** Yes  
**Requires Confirmation:** Yes  
**Git Checkpoint:** Yes  

Governance test optimization:
- Identify redundant tests
- Find mergeable tests
- Detect unclear test purposes
- Improve weak assertions
- Validate alignment with brain-protection-rules.yaml

**Safeguards:**
- Never remove core governance tests
- Preserve coverage percentage
- Require explicit approval for deletions

**Output:** `cortex-brain/documents/analysis/skull-test-review-{timestamp}.md`

### Phase 3: Documentation Refinement
**Duration:** ~10 minutes  
**Blocking:** Yes  
**Git Checkpoint:** Yes  

Documentation optimization:
- Remove bloat from CORTEX.prompt.md (<600 lines)
- Fix broken references
- Update outdated sections
- Sync copilot-instructions.md with operations
- Validate manifest references

**Targets:**
- `.github/prompts/CORTEX.prompt.md`
- `.github/copilot-instructions.md`
- `cortex-brain/response-templates.yaml`
- `cortex-brain/brain-protection-rules.yaml`

**Output:** `cortex-brain/documents/reports/documentation-refinement-{timestamp}.md`

### Phase 4: Code Quality Enhancement
**Duration:** ~20 minutes  
**Blocking:** Yes  
**Git Checkpoint:** Yes  

Code maintainability improvements:
- Simplify complex functions (>15 cyclomatic)
- Remove duplicate code blocks
- Standardize naming conventions
- Fix inconsistent error handling
- Optimize imports

**Quality Gates:**
- All tests must pass
- No new linting errors
- Complexity scores must improve

**Output:** `cortex-brain/documents/analysis/code-quality-improvements-{timestamp}.md`

### Phase 5: Architecture Review
**Duration:** ~15 minutes  
**Blocking:** No  

System design validation:
- Check for circular dependencies
- Identify missing abstractions
- Find consolidation opportunities
- Review manifest consistency
- Validate execution_method classifications
- Check tier separation

**Output:** `cortex-brain/documents/analysis/architecture-review-{timestamp}.md`

### Phase 6: Performance Optimization
**Duration:** ~10 minutes  
**Blocking:** No  

Bottleneck identification:
- Slow operations (>1s response)
- Memory leaks
- File I/O patterns
- Caching opportunities
- Tier1 memory profiling

**Output:** `cortex-brain/documents/analysis/performance-optimization-{timestamp}.md`

### Phase 7: Validation & Rollback Safety
**Duration:** ~15 minutes  
**Blocking:** Yes  

Comprehensive validation:
- Run full test suite (pytest)
- Validate all SKULL rules
- Check documentation builds
- Verify no broken imports
- Test sample operations
- Generate rollback script

**Success Criteria:**
- 100% test pass rate
- Zero SKULL violations
- No import errors
- Documentation valid

**Outputs:**
- `cortex-brain/documents/reports/refinement-validation-{timestamp}.md`
- `scripts/rollback_refinement_{timestamp}.py`

---

## Usage

### From Copilot Chat

```
refine
refine the system
improve cortex
optimize cortex holistically
```

### From CLI

```bash
# Dry-run (preview changes)
python scripts/cli_wrappers/refine_wrapper.py --dry-run

# Apply changes
python scripts/cli_wrappers/refine_wrapper.py --apply

# Run specific phase
python scripts/cli_wrappers/refine_wrapper.py --phase discovery

# Save results to file
python scripts/cli_wrappers/refine_wrapper.py --output results.json
```

### Direct Python

```python
from pathlib import Path
from src.operations.modules.orchestration.refinement_orchestrator_v1 import RefinementOrchestratorV1

orchestrator = RefinementOrchestratorV1(
    cortex_root=Path("/path/to/cortex"),
    dry_run=True
)

results = orchestrator.execute()
print(results["metrics"])
```

---

## Configuration

Edit `cortex-brain/orchestrator-manifests/refinement-orchestrator-manifest.yaml`:

```yaml
configuration:
  dry_run_default: true              # Safe by default
  auto_approve_safe_changes: false   # Require confirmation
  max_complexity_threshold: 15       # Complexity limit
  min_test_coverage: 80              # Coverage requirement
  token_limit_prompt_md: 600         # Token limit
```

### Change Categories

**Safe** (can auto-apply):
- Import optimization
- Formatting fixes
- Comment updates

**Moderate** (needs review):
- Function simplification
- Duplicate removal
- Documentation updates

**Dangerous** (requires explicit approval):
- SKULL test removal
- Governance rule changes
- Architecture refactoring

---

## Safety Features

### Git Checkpoints

Automatic git checkpoints before destructive phases:
- Phase 2: SKULL changes
- Phase 3: Documentation changes
- Phase 4: Code changes

### Rollback Script

Generated at end of execution:
- Location: `scripts/rollback_refinement_{timestamp}.py`
- Restores all changes via git
- Validates rollback success

**Usage:**
```bash
python scripts/rollback_refinement_20251216_143022.py
```

### Dry-Run Mode

**Default:** Enabled  
**Purpose:** Preview all changes without applying

**Behavior:**
- Analyzes all issues
- Generates reports
- Shows what would change
- Does NOT modify files

**Enable changes:**
```bash
python scripts/cli_wrappers/refine_wrapper.py --apply
```

---

## Metrics Tracked

- **Lines Removed:** Dead code elimination
- **Complexity Delta:** Improvement in cyclomatic complexity
- **Coverage Delta:** Test coverage change
- **Token Reduction:** Documentation optimization
- **Dead Code Removed:** Count of removed functions/classes
- **Duplicates Eliminated:** Consolidated code blocks
- **Tests Improved:** Enhanced test quality
- **Docs Fixed:** Documentation corrections

---

## Integration Points

### Pre-Execution
1. Run healthcheck to establish baseline
2. Create full git backup branch

### Post-Execution
1. Run healthcheck to validate changes
2. Update tier2 knowledge graph with improvements

### Rollback Triggers
- Test failure rate >5%
- SKULL violations detected
- Import errors found
- User abort requested

---

## Common Use Cases

### 1. Quarterly System Cleanup

```bash
# Full refinement with all phases
python scripts/cli_wrappers/refine_wrapper.py --dry-run
# Review reports
python scripts/cli_wrappers/refine_wrapper.py --apply
```

### 2. Documentation Optimization

```bash
# Run only documentation phase
python scripts/cli_wrappers/refine_wrapper.py --phase docs --apply
```

### 3. Code Quality Sprint

```bash
# Run quality and architecture phases
python scripts/cli_wrappers/refine_wrapper.py --phase quality --apply
python scripts/cli_wrappers/refine_wrapper.py --phase architecture
```

### 4. Performance Audit

```bash
# Run performance analysis only
python scripts/cli_wrappers/refine_wrapper.py --phase performance
```

---

## Troubleshooting

### Issue: Phase Times Out

**Cause:** Complex codebase, slow operations  
**Solution:** Increase timeout in manifest:

```yaml
phases:
  - id: "phase_X"
    timeout_minutes: 30  # Increase from 10
```

### Issue: SKULL Tests Incorrectly Flagged

**Cause:** Analyzer doesn't understand test purpose  
**Solution:** Add clear docstrings to tests:

```python
def test_governance_rule():
    """
    SKULL Rule: TDD_ENFORCEMENT
    Validates RED phase before implementation.
    Core governance - DO NOT REMOVE.
    """
```

### Issue: False Positive Complexity

**Cause:** Complex domain logic that can't be simplified  
**Solution:** Add complexity exception comment:

```python
def complex_business_logic():
    """
    Complexity: 18 (APPROVED)
    Reason: Domain complexity, state machine implementation
    """
```

### Issue: Rollback Fails

**Cause:** Git state changed after refinement  
**Solution:** Manual rollback:

```bash
git log --oneline -10
git reset --hard <commit_before_refinement>
pytest tests/  # Validate
```

---

## Best Practices

1. **Always start with dry-run** - Review reports before applying
2. **Run quarterly** - Regular maintenance prevents debt accumulation
3. **Review SKULL changes carefully** - Governance is critical
4. **Keep rollback script** - Archive for 30 days minimum
5. **Update knowledge graph** - Record patterns learned
6. **Validate thoroughly** - Run full test suite after changes
7. **Document exceptions** - Add comments for approved complexity
8. **Incremental application** - Apply one phase at a time for large changes

---

## Future Enhancements

### Planned Features

- **Semantic consistency check** - Validate templates vs behavior
- **User experience analysis** - Learn from tier1 error patterns
- **Knowledge graph optimization** - Remove stale patterns
- **Test quality scoring** - Advanced assertion analysis
- **Manifest validation** - Complete inheritance chain checks
- **Auto-fix capabilities** - Safe changes applied automatically

### Extension Points

- Custom analyzers via plugin system
- Domain-specific complexity rules
- Project-specific naming conventions
- Custom quality gates

---

## Related Documentation

- **Manifest:** `cortex-brain/orchestrator-manifests/refinement-orchestrator-manifest.yaml`
- **Implementation:** `src/operations/modules/orchestration/refinement_orchestrator_v1.py`
- **CLI Wrapper:** `scripts/cli_wrappers/refine_wrapper.py`
- **Tests:** `tests/test_refinement_orchestrator.py`
- **Brain Protection:** `cortex-brain/brain-protection-rules.yaml`

---

**Last Updated:** 2025-12-16  
**Status:** ✅ Production Ready
