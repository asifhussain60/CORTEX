# System Alignment Guide

**Version:** 2.0 (Align 2.0)  
**Status:** Production Ready  
**Audience:** CORTEX Administrators

---

## What's New in Align 2.0

**Enhanced Capabilities:**
- ✅ **Conflict Detection:** Detects duplicate modules, orphaned wiring, architectural drift, missing dependencies
- ✅ **Smart Remediation:** Generates fix templates with before/after previews, user confirmation, git checkpoint safety
- ✅ **Visual Dashboard:** Integration health trends, priority matrices, actionable recommendations
- ✅ **Interactive Fixes:** Apply corrections one-by-one with rollback capability
- ✅ **Historical Tracking:** Trend analysis showing health evolution over time

---

## Overview

System Alignment is CORTEX's self-validation framework that automatically discovers, validates, and reports on the integration depth of all features. It uses convention-based discovery to eliminate manual feature tracking and provides actionable remediation with user consent.

**Align 2.0 Enhancements:**
- Passive observation with smart recommendations (respects brain protection consent rules)
- Auto-detects internal conflicts (module inconsistencies, wiring issues, architectural drift)
- User-guided fixes with preview and confirmation
- Git checkpoint safety with instant rollback
- Visual health dashboard with emoji indicators and trend analysis

---

## Core Concepts

### Convention-Based Discovery

**No Hardcoded Lists:** System alignment discovers features by scanning the filesystem and using naming conventions.

**Discovery Paths:**
- `src/operations/modules/` - Operation orchestrators
- `src/workflows/` - Workflow orchestrators
- `src/agents/` - Specialized agents

**Naming Conventions:**
- Classes ending in `Orchestrator` are discovered as orchestrators
- Classes ending in `Agent` are discovered as agents
- Inheritance from `BaseOperationModule` is validated

### Integration Depth Scoring

**7-Layer Validation (0-100%):**

| Score | Layer | Validation | Points |
|-------|-------|------------|--------|
| 20% | Discovery | File exists in correct location | 20 |
| 40% | Import | Can be imported without errors | +20 |
| 60% | Instantiation | Class can be instantiated | +20 |
| 70% | Documentation | Has docstring + module documentation | +10 |
| 80% | Testing | Test file exists with >70% coverage | +10 |
| 90% | Wiring | Entry point trigger configured | +10 |
| 100% | Optimization | Performance benchmarks pass | +10 |

**Status Thresholds:**
- **<70%:** ❌ Critical - Not production ready
- **70-89%:** ⚠️ Warning - Needs improvement
- **90-100%:** ✅ Healthy - Production ready

---

## Configuration

### Performance Optimization

**Default Configuration** (`cortex.config.json`):
```json
"system_alignment": {
  "skip_duplicate_detection": true,
  "comment": "Duplicate detection skipped by default to prevent O(n²) performance issue"
}
```

**Why Skip Duplicate Detection by Default:**
- With 575+ documents, duplicate detection becomes O(n²) operation
- Results in 330,625 file operations (575 × 575)
- Can take hours to complete, appearing as infinite loop
- Primary system alignment purpose is integration depth validation, not duplicate detection
- Document duplicates better handled by dedicated cleanup operations

**Enable Duplicate Detection (if needed):**
```json
"system_alignment": {
  "skip_duplicate_detection": false
}
```

**When to Enable:**
- Deep documentation governance audit required
- After major documentation refactoring
- Preparing for release (one-time validation)
- Never enable for regular development workflow

**Performance Characteristics:**
- **Skip enabled (default):** <5 seconds for full alignment
- **Skip disabled:** 10-15 seconds with optimized keyword cache (575 one-time file reads)
- **Legacy (pre-fix):** Hours/infinite loop (330,625 file reads)

---

## Commands

### Basic Commands (Enhanced in v2.0)

```bash
# Run full alignment validation with dashboard
align

# Generate detailed report with remediation
align report

# Check system alignment status
system alignment

# Validate current alignment
validate alignment
```

### Align 2.0 Commands (NEW)

```bash
# Run alignment with visual dashboard and automatic fix prompt
align

# Apply fixes interactively with confirmation (direct access)
align fix

# View full dashboard in terminal
align report

# Show detected conflicts only
align conflicts

# Generate fix templates without applying
align fix --preview
```

**Unified Workflow (NEW in v2.0):**
When you run `align`, it automatically:
1. Validates system integration depth
2. Detects conflicts and generates fix templates
3. **Prompts you** if fixes are available:
   - Option 1: Apply fixes interactively (recommended)
   - Option 2: View report only
   - Option 3: Exit

This eliminates the need to run `align` then `align fix` separately.

### Integration with Optimize

```bash
# Optimize includes alignment check
optimize

# If healthy (>80%): Silent, no output
# If issues detected: Shows warning with issue count
```

---

## Usage Scenarios

### Scenario 1: Add New Feature

**Developer adds:** `src/operations/modules/payments/payment_orchestrator.py`

**Alignment auto-detects:**
1. ✅ Discovered (20%)
2. ✅ Importable (40%)
3. ✅ Instantiable (60%)
4. ❌ Not documented (stays at 60%)
5. ❌ No tests (stays at 60%)
6. ❌ Not wired (stays at 60%)

**Alignment reports:**
```
⚠️ PaymentOrchestrator: 60% integration
   - Missing documentation
   - No test coverage
   - Not wired to entry point
```

**Auto-remediation generates:**
- YAML entry point template
- Pytest test skeleton
- Documentation template

### Scenario 2: Monitor System Health

**Run during development:**
```bash
align
```

**Output:**
```
✅ System alignment healthy
   Overall Health: 85%
   15 features validated
   13 fully integrated (>90%)
   2 warnings (70-89%)
```

### Scenario 3: Pre-Deployment Validation

**Run before release:**
```bash
align report
```

**Checks:**
- ✅ Overall health >80%
- ✅ No critical issues (<70%)
- ✅ All user-facing features wired
- ✅ Test coverage >70% on critical paths
- ✅ No admin code in user packages

---

## Validation Layers

### Layer 1: Discovery (20%)

**Validates:**
- File exists in expected location
- Filename follows conventions
- Directory structure matches patterns

**Failure Causes:**
- File in wrong directory
- Incorrect naming convention

### Layer 2: Import Validation (40%)

**Validates:**
- Python imports succeed
- No syntax errors
- No missing dependencies

**Failure Causes:**
- Import errors
- Missing dependencies
- Syntax errors in file

### Layer 3: Instantiation (60%)

**Validates:**
- Class can be instantiated
- Required methods exist
- Inheritance is valid

**Failure Causes:**
- Abstract methods not implemented
- Missing required methods
- Constructor errors

### Layer 4: Documentation (70%)

**Validates:**
- Class has docstring
- Module documentation exists in `prompts/modules/`
- Usage examples provided

**Locations Checked:**
- Class docstring
- `.github/prompts/CORTEX.prompt.md`
- `.github/prompts/modules/*.md`

### Layer 5: Testing (80%)

**Validates:**
- Test file exists in `tests/`
- Test coverage >70%
- Tests actually run (not skipped)

**Test File Patterns:**
- `tests/operations/modules/test_*.py`
- `tests/agents/test_*.py`
- `tests/workflows/test_*.py`

### Layer 6: Wiring (90%)

**Validates:**
- Entry point trigger exists in `response-templates.yaml`
- Trigger maps to orchestrator via naming convention
- Routing configuration present

**Entry Point Discovery:**
```yaml
# response-templates.yaml
templates:
  payment_operation:
    triggers:
    - payment
    - process payment
    
routing:
  payment_triggers:
  - payment
  - process payment
```

**Wiring Validator checks:**
- Trigger → Orchestrator mapping
- Naming convention match
- No orphaned triggers
- No ghost features

### Layer 7: Optimization (100%)

**Validates:**
- Performance benchmarks exist
- Response time <500ms typical
- Memory usage reasonable
- No performance regressions

**Note:** Currently placeholder - full implementation planned

---

## Auto-Remediation

### Wiring Template Generation

**Input:** Unwired orchestrator `PaymentOrchestrator`

**Generates:**
```yaml
# Add to response-templates.yaml
templates:
  payment_operation:
    name: "Payment Operation"
    triggers:
    - payment
    - process payment
    - handle payment
    response_type: "detailed"
    content: "🧠 **CORTEX Payment Operation**..."

routing:
  payment_triggers:
  - payment
  - process payment
  - handle payment
```

### Test Skeleton Generation

**Input:** Untested orchestrator `PaymentOrchestrator`

**Generates:** `tests/operations/modules/test_payment_orchestrator.py`
```python
import pytest
from src.operations.modules.payment_orchestrator import PaymentOrchestrator

@pytest.fixture
def orchestrator():
    return PaymentOrchestrator()

def test_execute_success(orchestrator):
    context = {"amount": 100}
    result = orchestrator.execute(context)
    assert result.success is True

def test_validate_prerequisites(orchestrator):
    context = {}
    valid, errors = orchestrator.validate_prerequisites(context)
    assert isinstance(valid, bool)
```

### Documentation Template Generation

**Input:** Undocumented orchestrator `PaymentOrchestrator`

**Generates:** `.github/prompts/modules/payment-guide.md`
```markdown
# Payment Processing Guide

**Purpose:** Process payment transactions

**Commands:**
- `payment` - Process payment
- `process payment [amount]` - Process specific amount

**How It Works:**
1. Validates payment details
2. Processes transaction
3. Returns confirmation

**Examples:**
- "process payment for $100"
- "handle payment transaction"
```

---

## Deployment Gates

### Quality Gates Checked

1. **Integration Score Gate**
   - All features >70% integration
   - Critical features >80% integration
   - Overall health >80%

2. **Test Coverage Gate**
   - Overall coverage >70%
   - No mocked critical paths in production code
   - All tests passing

3. **Package Purity Gate**
   - No admin code in user packages
   - No development dependencies in production
   - Clean package boundaries

4. **Documentation Gate**
   - All user-facing features documented
   - API documentation current
   - Examples provided for all commands

### Gate Failure Handling

**If gates fail:**
- Deployment blocked
- Detailed failure report generated
- Remediation suggestions provided
- Re-validation required

---

## Architecture

### Component Overview

```
SystemAlignmentOrchestrator
├── OrchestratorScanner (Convention-based discovery)
├── AgentScanner (Convention-based discovery)
├── EntryPointScanner (Template parsing)
├── DocumentationScanner (Doc validation)
├── IntegrationScorer (7-layer validation)
├── WiringValidator (Entry point validation)
├── TestCoverageValidator (Test validation)
├── DeploymentGates (Quality gates)
├── PackagePurityChecker (Admin leak detection)
└── RemediationGenerators (Auto-fix templates)
    ├── WiringGenerator
    ├── TestSkeletonGenerator
    └── DocumentationGenerator
```

### Data Flow

```
1. User: "align"
   ↓
2. SystemAlignmentOrchestrator.execute()
   ↓
3. Parallel Discovery
   ├── OrchestratorScanner.discover()
   ├── AgentScanner.discover()
   └── EntryPointScanner.discover()
   ↓
4. Integration Scoring
   └── For each feature:
       ├── Check import
       ├── Check instantiation
       ├── Check documentation
       ├── Check tests
       ├── Check wiring
       └── Check optimization
   ↓
5. Validation
   ├── Deployment gates
   ├── Package purity
   └── Entry point wiring
   ↓
6. Remediation Generation
   ├── Generate wiring templates
   ├── Generate test skeletons
   └── Generate documentation
   ↓
7. Report Generation
   └── AlignmentReport with recommendations
```

---

## Best Practices

### For Feature Developers

1. **Follow Naming Conventions**
   - Use `*Orchestrator` for orchestrators
   - Use `*Agent` for agents
   - Place in correct directories

2. **Add Documentation Early**
   - Write class docstrings
   - Add usage examples
   - Document in CORTEX.prompt.md

3. **Write Tests Before Wiring**
   - Create test file in `tests/`
   - Achieve >70% coverage
   - Include integration tests

4. **Wire to Entry Points**
   - Add template to `response-templates.yaml`
   - Configure routing triggers
   - Test natural language commands

5. **Run Alignment Before PR**
   ```bash
   align report
   ```
   - Fix all critical issues
   - Address warnings
   - Verify >80% health

### For System Administrators

1. **Monitor Continuously**
   - Run `align` weekly
   - Check health trends
   - Address degradation early

2. **Enforce Quality Gates**
   - Block deployment if <80% health
   - Require tests for all features
   - Validate documentation completeness

3. **Review Remediation Suggestions**
   - Apply auto-generated templates
   - Validate suggested fixes
   - Update conventions as needed

---

## Troubleshooting

### Issue: Feature Not Discovered

**Symptoms:** Feature exists but not in alignment report

**Causes:**
- File in wrong directory
- Incorrect naming convention
- Excluded by scanner patterns

**Fix:**
1. Check file location matches expected paths
2. Verify class name ends in `Orchestrator` or `Agent`
3. Check scanner exclusion patterns

### Issue: Wiring Validation Fails

**Symptoms:** Feature shows "Not wired" but template exists

**Causes:**
- Trigger doesn't match naming convention
- Entry point scanner mapping missing
- Template in wrong format

**Fix:**
1. Check `response-templates.yaml` syntax
2. Add mapping to `EntryPointScanner._infer_orchestrator()`
3. Verify routing triggers exist

### Issue: Low Test Coverage Score

**Symptoms:** Tests exist but coverage reported as 0%

**Causes:**
- Test file not in expected location
- Tests are skipped
- Coverage calculation error

**Fix:**
1. Move test file to `tests/` hierarchy
2. Remove `@pytest.mark.skip` decorators
3. Run tests manually to verify they execute

---

## Future Enhancements

### Planned Features

1. **Performance Benchmarking (Layer 7)**
   - Automated performance testing
   - Regression detection
   - Optimization recommendations

2. **Dependency Analysis**
   - Track feature dependencies
   - Detect circular dependencies
   - Suggest decoupling

3. **Historical Trending**
   - Track health over time
   - Identify degradation patterns
   - Predict maintenance needs

4. **Auto-Fix Capabilities**
   - Apply remediation automatically
   - Generate PRs for fixes
   - Self-healing system

---

## Reference

### Files

- **Orchestrator:** `src/operations/modules/admin/system_alignment_orchestrator.py`
- **Scanners:** `src/discovery/*.py`
- **Validators:** `src/validation/*.py`
- **Templates:** `cortex-brain/response-templates.yaml`
- **Tests:** `tests/operations/admin/test_system_alignment_orchestrator.py`

### Related Documentation

- CORTEX.prompt.md - System Alignment section
- optimization-principles.yaml - Quality standards
- test-strategy.yaml - Testing guidelines

---

**Last Updated:** November 25, 2025  
**Version:** 1.0  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
