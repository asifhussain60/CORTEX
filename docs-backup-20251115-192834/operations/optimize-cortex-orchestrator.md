# CORTEX Optimization Orchestrator

**Version:** 1.0  
**Status:** ✅ PRODUCTION READY  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.

---

## Overview

The CORTEX Optimization Orchestrator is an automated system that performs holistic architecture reviews, runs SKULL tests, identifies improvement opportunities, and executes optimizations with full git tracking.

### Key Features

- **🧪 SKULL Test Execution** - Validates all brain protection rules
- **🔍 Architecture Analysis** - Reviews knowledge graph, operations, brain protection, code quality
- **📋 Optimization Planning** - Generates prioritized action plans
- **⚙️ Automated Execution** - Applies improvements with rollback capability
- **📊 Metrics Collection** - Tracks all changes and improvements
- **🔄 Git Tracking** - Commits each optimization for metrics analysis

---

## Quick Start

### Command Line

```bash
# Standard optimization (recommended)
python optimize_cortex.py

# Quick optimization (tests + analysis only)
python optimize_cortex.py --profile quick

# Full optimization (all improvements)
python optimize_cortex.py --profile comprehensive

# Dry run (see what would be done)
python optimize_cortex.py --dry-run
```

### Natural Language

```
optimize cortex
run optimization
improve cortex
architecture review
holistic review
```

### Python API

```python
from src.operations.modules.optimization import OptimizeCortexOrchestrator

# Create orchestrator
orchestrator = OptimizeCortexOrchestrator(project_root=Path('./'))

# Execute optimization
result = orchestrator.execute(context={})

# Check results
if result.success:
    metrics = result.data['metrics']
    print(f"Optimizations applied: {metrics['optimizations_succeeded']}")
    print(f"Git commits: {len(metrics['git_commits'])}")
```

---

## Architecture

### Workflow Phases

```
┌─────────────────────────────────────────────────────────────┐
│                CORTEX OPTIMIZATION WORKFLOW                 │
└─────────────────────────────────────────────────────────────┘

Phase 1: SKULL Tests
├── Run tier0 brain protection tests
├── Validate test-before-claim enforcement
├── Check integration verification
└── Result: Pass/Fail (blocks if fail)

Phase 2: Architecture Analysis
├── Analyze knowledge graph (patterns learned)
├── Review operation modules (structure)
├── Check brain protection rules (integrity)
├── Assess code quality metrics
├── Evaluate test coverage
└── Check documentation completeness

Phase 3: Optimization Planning
├── Categorize issues by severity
│   ├── CRITICAL - Security/stability
│   ├── HIGH - Performance improvements
│   ├── MEDIUM - Code quality
│   └── LOW - Documentation/cosmetic
├── Identify high-frequency patterns
└── Generate prioritized action plan

Phase 4: Optimization Execution
├── Execute in priority order
├── Apply each optimization
├── Git commit with descriptive message
├── Collect metrics
└── Rollback on failure

Phase 5: Metrics & Reporting
├── Calculate duration
├── Count improvements applied
├── List git commits
├── Generate optimization report
└── Return comprehensive results
```

### Component Architecture

```
OptimizeCortexOrchestrator
├── Prerequisites Validator
│   ├── Check project root
│   ├── Validate git repository
│   ├── Verify test suite
│   └── Confirm knowledge graph exists
│
├── SKULL Test Runner
│   ├── Execute pytest on tier0/
│   ├── Parse test results
│   └── Collect pass/fail metrics
│
├── Architecture Analyzer
│   ├── Knowledge Graph Analyzer
│   │   ├── Count validation insights
│   │   ├── Identify high-frequency patterns
│   │   └── Check pattern quality
│   │
│   ├── Operations Analyzer
│   │   ├── Count operation categories
│   │   ├── Check for empty modules
│   │   └── Validate structure
│   │
│   ├── Brain Protection Analyzer
│   │   ├── Count protection layers
│   │   ├── Validate SKULL rules
│   │   └── Check enforcement
│   │
│   ├── Code Quality Analyzer
│   │   ├── Count Python files
│   │   ├── Check package structure
│   │   └── Assess maintainability
│   │
│   ├── Test Coverage Analyzer
│   │   └── Count test files
│   │
│   └── Documentation Analyzer
│       ├── Count docs files
│       └── Check completeness
│
├── Optimization Planner
│   ├── Issue categorizer (CRITICAL/HIGH/MEDIUM/LOW)
│   ├── Pattern identifier
│   └── Action plan generator
│
├── Optimization Executor
│   ├── Priority-based execution
│   ├── Git commit wrapper
│   └── Metrics collector
│
└── Report Generator
    ├── Metrics formatter
    ├── Git commits list
    └── Markdown report builder
```

---

## Optimization Profiles

### Quick Profile

**Use When:** Time-constrained, need validation only

**What It Does:**
- Runs SKULL tests
- Analyzes architecture
- Identifies issues
- **Does NOT** apply optimizations

**Duration:** ~2-3 minutes

```bash
python optimize_cortex.py --profile quick
```

### Standard Profile (Recommended)

**Use When:** Regular maintenance, weekly/monthly optimization

**What It Does:**
- Runs SKULL tests
- Analyzes architecture
- Generates optimization plan
- Applies safe optimizations
- Commits changes to git

**Duration:** ~5-10 minutes

```bash
python optimize_cortex.py --profile standard
```

### Comprehensive Profile

**Use When:** Major release prep, quarterly review, pre-production

**What It Does:**
- Everything in Standard profile
- Applies aggressive optimizations
- Deep analysis of all components
- Comprehensive metrics collection
- Detailed reporting

**Duration:** ~15-20 minutes

```bash
python optimize_cortex.py --profile comprehensive
```

---

## Optimization Categories

### CRITICAL (Blocking)

Issues that impact security, stability, or data integrity.

**Examples:**
- Missing knowledge graph file
- Corrupted brain protection rules
- Git repository not found
- Required operation modules missing

**Action:** Immediate fix required, blocks other optimizations

### HIGH (Important)

Performance improvements and high-frequency patterns.

**Examples:**
- High-frequency pattern detected (5+ occurrences)
- Significant code duplication
- Inefficient database queries
- Missing test coverage for critical paths

**Action:** Applied in standard profile

### MEDIUM (Recommended)

Code quality and maintainability improvements.

**Examples:**
- Empty operation categories
- Missing docstrings
- Inconsistent naming conventions
- Outdated dependencies

**Action:** Applied when safe, skipped if risky

### LOW (Optional)

Documentation and cosmetic updates.

**Examples:**
- Outdated README
- Missing examples
- Formatting inconsistencies
- Typos in comments

**Action:** Only applied in comprehensive profile

---

## Metrics Collected

### Test Metrics

```python
metrics.tests_run          # Total tests executed
metrics.tests_passed       # Tests that passed
metrics.tests_failed       # Tests that failed
```

### Optimization Metrics

```python
metrics.issues_identified       # Total issues found
metrics.optimizations_applied   # Total optimizations attempted
metrics.optimizations_succeeded # Optimizations applied successfully
metrics.optimizations_failed    # Optimizations that failed
```

### Git Tracking

```python
metrics.git_commits        # List of commit hashes
metrics.duration_seconds   # Total execution time
```

### Example Metrics Output

```
Duration: 487.32s
Issues identified: 12
Optimizations applied: 8/10
Git commits: 8

Git commits:
  abc123de
  def456gh
  789ijklm
  ...
```

---

## Git Commit Strategy

Each optimization is committed separately for tracking:

### Commit Message Format

```
[OPTIMIZATION/{PRIORITY}] {Action Description}
```

### Examples

```bash
# Critical optimizations
[OPTIMIZATION/CRITICAL] Create missing knowledge graph file
[OPTIMIZATION/CRITICAL] Restore brain protection rules

# High priority optimizations
[OPTIMIZATION/HIGH] Document high-frequency pattern: powershell_regex
[OPTIMIZATION/HIGH] Optimize database query in tier1 manager

# Medium priority optimizations
[OPTIMIZATION/MEDIUM] Implement empty operation category: refactoring
[OPTIMIZATION/MEDIUM] Add docstrings to public APIs

# Low priority optimizations
[OPTIMIZATION/LOW] Update README with new examples
[OPTIMIZATION/LOW] Fix typos in documentation
```

### Benefits

1. **Metrics Tracking** - Each commit represents measurable improvement
2. **Rollback Capability** - Easy to revert specific optimizations
3. **History Analysis** - Review optimization trends over time
4. **Attribution** - Clear ownership of improvements
5. **CI/CD Integration** - Automated testing per optimization

---

## Error Handling

### SKULL Tests Failed

```
🛡️ SKULL tests failed - cannot proceed with optimization

Tests run: 25
Tests passed: 23
Tests failed: 2

Errors:
  - test_skull_001_test_before_claim FAILED
  - test_skull_002_integration_verification FAILED

Action: Fix failing tests before optimizing
```

### Git Repository Not Found

```
Prerequisites not met:
  - Not a git repository - optimization requires git tracking

Action: Initialize git repository or run from correct directory
```

### Knowledge Graph Corrupted

```
Issues identified: 1 CRITICAL

CRITICAL: Knowledge graph corrupted
  Category: knowledge_graph
  Action: Restore knowledge graph from backup

Optimization blocked until critical issues resolved
```

---

## Integration with CORTEX Operations

### Natural Language Integration

The orchestrator integrates with CORTEX's natural language system:

```yaml
# cortex-operations.yaml
operations:
  optimize_cortex:
    name: CORTEX Optimization
    natural_language:
      - optimize
      - optimize cortex
      - run optimization
      - improve cortex
      - holistic review
      - architecture review
```

### Operation Factory Integration

```python
# Automatically registered via operation factory
from src.operations import execute_operation

# Execute via natural language
report = execute_operation('optimize cortex')

# Or via operation ID
report = execute_operation('optimize_cortex', profile='standard')
```

---

## Best Practices

### When to Run Optimization

**Daily:**
- Quick profile during morning standup
- Validates brain protection intact

**Weekly:**
- Standard profile after significant changes
- Applies safe improvements automatically

**Monthly:**
- Comprehensive profile for deep review
- Generates metrics for reporting

**Pre-Release:**
- Comprehensive profile before production deployment
- Ensures all optimizations applied

### What to Review

After optimization, review:

1. **Git commits** - Understand what changed
2. **Metrics** - Track improvement trends
3. **Errors** - Address failed optimizations
4. **Knowledge graph** - Check new patterns learned

### Troubleshooting

**Optimization takes too long:**
```bash
# Use quick profile for validation only
python optimize_cortex.py --profile quick
```

**Optimizations fail:**
```bash
# Run in dry-run mode first
python optimize_cortex.py --dry-run

# Check logs
tail -f cortex-optimization.log
```

**SKULL tests fail:**
```bash
# Run tests directly to debug
pytest tests/tier0/ -v

# Fix issues, then retry
python optimize_cortex.py
```

---

## Testing

### Run Orchestrator Tests

```bash
# Run all optimization tests
pytest tests/operations/test_optimize_cortex_orchestrator.py -v

# Run specific test category
pytest tests/operations/test_optimize_cortex_orchestrator.py::TestSKULLTests -v

# Run with coverage
pytest tests/operations/test_optimize_cortex_orchestrator.py --cov=src/operations/modules/optimization
```

### Test Coverage

The test suite covers:

- ✅ Prerequisites validation (4 tests)
- ✅ SKULL test execution (3 tests)
- ✅ Architecture analysis (3 tests)
- ✅ Optimization planning (2 tests)
- ✅ Optimization execution (2 tests)
- ✅ Git operations (2 tests)
- ✅ Integration workflow (1 test)
- ✅ Metrics collection (2 tests)

**Total: 19 comprehensive tests**

---

## Future Enhancements

### Phase 2.1 (Planned)

- **AI-powered optimization suggestions** - Use LLM to suggest improvements
- **Automated refactoring** - Safe code transformations
- **Performance profiling** - Identify bottlenecks
- **Security scanning** - Detect vulnerabilities

### Phase 2.2 (Planned)

- **Optimization scheduling** - Cron-based automated runs
- **Slack/email notifications** - Alert on critical issues
- **Dashboard** - Real-time optimization metrics
- **Optimization marketplace** - Share custom optimizations

---

## Related Documentation

- [SKULL Protection Layer](../cortex-brain/SKULL-PROTECTION-LAYER.md)
- [Knowledge Graph](../cortex-brain/knowledge-graph.yaml)
- [Brain Protection Rules](../cortex-brain/brain-protection-rules.yaml)
- [Operations Architecture](../docs/architecture/operations.md)

---

**Last Updated:** 2025-11-11  
**Status:** ✅ PRODUCTION READY  
**Tests:** 19 passing
