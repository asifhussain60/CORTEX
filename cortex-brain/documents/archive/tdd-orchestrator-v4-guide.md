# TDD Orchestrator - User Guide

**Version:** 4.0.0  
**Author:** CORTEX Development Team  
**Date:** December 19, 2025  

---

## 🎯 Overview

TDD Orchestrator is a unified, adaptive system for Test-Driven Development that automatically discovers your technology stack, generates comprehensive tests, implements minimal code, and refactors for quality—all while learning from patterns and enforcing clean code principles.

### Key Features

- ✅ **Adaptive Learning:** Auto-detects 11+ languages and frameworks
- ✅ **AI-Driven:** LLM-powered test generation, implementation, and refactoring
- ✅ **Clean Code:** Enforces SOLID, DRY, KISS, YAGNI principles with 0-10 scoring
- ✅ **Strategy Pattern:** Pluggable RED, GREEN, REFACTOR phases
- ✅ **Brain Integration:** Stores patterns in Tier 2 knowledge graph
- ✅ **Rollback Safety:** Automatic per-phase rollback on failures
- ✅ **Technology Discovery:** Learns best practices for your stack

---

## 🚀 Quick Start

### Basic Usage

```bash
# In Copilot Chat
start tdd User Authentication
```

Or:

```bash
tdd User Authentication
```

The orchestrator will:
1. Discover your tech stack (language, frameworks, test tools)
2. **RED Phase:** Generate comprehensive failing tests
3. **GREEN Phase:** Implement minimal code to pass tests
4. **REFACTOR Phase:** Improve code quality
5. Learn patterns for future use

### With Acceptance Criteria

```bash
# Provide specific criteria
start tdd User Authentication with criteria:
- Users can register with email and password
- Passwords must be hashed
- Email validation required
- Duplicate emails rejected
```

---

## 📋 Commands

| Command | Description |
|---------|-------------|
| `start tdd [feature]` | Begin TDD workflow for feature |
| `tdd [feature]` | Shorthand for start tdd |
| `run tests` | Execute test suite |
| `continue tdd` | Resume interrupted TDD cycle |
| `tdd status` | View current TDD cycle status |

---

## 🔄 TDD Workflow

### Phase 1: RED - Generate Failing Tests

**What Happens:**
1. Analyzes your feature requirements
2. Extracts edge cases (null, empty, boundaries, errors)
3. Queries Tier 2 for domain patterns
4. Generates comprehensive test suite
5. Runs tests (MUST fail - RED validation)
6. Creates git checkpoint
7. Updates documentation

**DoR (Definition of Ready):**
- ✅ Feature name defined
- ✅ Acceptance criteria provided
- ✅ No existing tests for this feature
- ✅ Git working directory clean
- ✅ Test framework detected

**DoD (Definition of Done):**
- ✅ Test file created
- ✅ Tests run successfully (framework works)
- ✅ ALL tests FAIL (RED validation)
- ✅ Git checkpoint created
- ✅ Documentation generated
- ✅ At least 1 edge case covered

**Example Output:**
```
🎭 Orchestrator engaged: TDDOrchestrator
▶️  RED: Generating tests for 'User Authentication'
  1. Analyzing feature requirements...
  2. Extracting edge cases...
  3. Querying Tier 2 patterns...
  4. Generating test suite...
  5. Running tests (expecting failures)...
✅ RED: Generated 8 failing tests
```

### Phase 2: GREEN - Minimal Implementation

**What Happens:**
1. Analyzes failing tests
2. Retrieves best practices for your tech stack
3. Generates minimal implementation (AI-driven)
4. Runs tests continuously until GREEN
5. Detects over-engineering
6. Validates clean code compliance (quality score >= 7.0)
7. Creates git checkpoint
8. Updates documentation

**DoR:**
- ✅ Test file exists
- ✅ Tests are failing
- ✅ No passing tests

**DoD:**
- ✅ Implementation file created
- ✅ 90%+ tests passing
- ✅ No over-engineering detected
- ✅ Quality score >= 7.0
- ✅ Git checkpoint created
- ✅ Documentation updated
- ✅ Test coverage >= 80%

**Example Output:**
```
🎭 Phase transition: RED → GREEN
▶️  GREEN: Implementing 'User Authentication'
  1. Analyzing failing tests...
  2. Loading best practices...
  3. Generating minimal implementation...
  4. Running tests (expecting GREEN)...
  5. Checking for over-engineering...
  6. Validating clean code compliance...
✅ GREEN: 8/8 tests passing
```

### Phase 3: REFACTOR - Code Improvement

**What Happens:**
1. Establishes quality baseline
2. Detects code smells (long functions, complexity, duplicates)
3. Generates AI-driven refactoring suggestions
4. Applies refactorings incrementally (validates tests after each)
5. Validates final quality improvement
6. Creates git checkpoint
7. Updates documentation
8. Feeds refactoring patterns to Tier 2

**DoR:**
- ✅ Implementation file exists
- ✅ Tests are passing
- ✅ No failing tests

**DoD:**
- ✅ All tests still passing
- ✅ Quality score improved or maintained
- ✅ At least one smell eliminated (if any existed)
- ✅ No new code smells introduced
- ✅ Git checkpoint created
- ✅ Documentation updated

**Example Output:**
```
🎭 Phase transition: GREEN → REFACTOR
▶️  REFACTOR: Improving code quality for 'User Authentication'
  1. Establishing quality baseline...
  2. Detecting code smells...
  3. Loading refactoring best practices...
  4. Generating refactoring suggestions...
  5. Applying refactorings incrementally...
✅ REFACTOR: Quality improved by +1.5 (7.5 → 9.0)
🎭 Orchestrator completing: ✅ ALL WORK COMPLETE
```

---

## 🌍 Supported Technologies

### Languages (11+)
- Python
- JavaScript
- TypeScript
- Java
- C#
- Go
- Ruby
- PHP
- Swift
- Kotlin
- Rust

### Test Frameworks (Auto-Detected)
- **Python:** pytest, unittest
- **JavaScript/TypeScript:** jest, mocha, vitest
- **.NET:** xUnit, NUnit, MSTest

### Frameworks (Auto-Detected)
- **Python:** Django, Flask, FastAPI
- **JavaScript/TypeScript:** React, Vue, Angular, Next.js
- **.NET:** ASP.NET Core

---

## 🎓 Best Practices

### 1. Write Clear Acceptance Criteria

**Good:**
```
- Users can register with email and password
- Passwords must be hashed using bcrypt
- Email validation follows RFC 5322
- Duplicate emails return 409 Conflict
```

**Bad:**
```
- User registration works
- Secure passwords
```

### 2. Let the Orchestrator Detect Your Stack

The orchestrator automatically detects:
- Language from file extensions
- Frameworks from `requirements.txt`, `package.json`, etc.
- Test frameworks from dependencies

**No manual configuration needed!**

### 3. Trust the RED Phase

If tests are passing in RED phase, the orchestrator will fail the cycle. This ensures you're not implementing before testing.

### 4. Review Refactoring Suggestions

The orchestrator applies refactorings incrementally and validates tests after each. If a refactoring breaks tests, it automatically rolls back.

### 5. Learn from Patterns

The orchestrator stores successful patterns in Tier 2. Over time, it learns your team's preferred approaches and applies them automatically.

---

## 📊 Quality Scoring

The orchestrator uses a 0-10 quality scoring system:

| Score | Level | Description |
|-------|-------|-------------|
| 9.0-10.0 | Excellent | Clean code, no violations |
| 7.0-8.9 | Good | Minor issues, acceptable |
| 5.0-6.9 | Fair | Multiple violations |
| < 5.0 | Poor | Major refactoring needed |

**Target:** >= 8.0 after REFACTOR phase

**Violations Detected:**
- Long functions (>20 lines)
- High cyclomatic complexity (>10)
- Duplicate code
- Poor naming conventions
- God classes/methods

---

## 🔧 Configuration

### Quality Thresholds

Edit `cortex-brain/manifests/orchestrators/tdd-orchestrator-v4-manifest.yaml`:

```yaml
configuration:
  quality_thresholds:
    green_phase:
      min_pass_rate: 0.9  # 90%
      min_coverage: 80
    refactor_phase:
      target_quality_score: 8.0
```

### Iterations

```yaml
configuration:
  default_settings:
    max_iterations_green: 10  # Max attempts to get tests passing
```

---

## 🐛 Troubleshooting

### Tests Won't Pass (GREEN Phase)

**Symptoms:** After 10 iterations, tests still failing

**Solutions:**
1. Review test requirements - may be too complex
2. Check if acceptance criteria are clear
3. Review generated implementation for errors
4. Manually intervene and resume with `continue tdd`

### Over-Engineering Detected

**Symptoms:** GREEN phase fails with "Over-engineering detected"

**Reason:** Implementation is more complex than needed

**Solutions:**
1. Trust the orchestrator - it wants minimal implementation
2. Review complexity metrics (LOC, cyclomatic complexity)
3. Simplify implementation manually if needed

### Quality Score Too Low

**Symptoms:** REFACTOR phase completes but score < 8.0

**Solutions:**
1. Review violation types in output
2. Apply additional refactorings manually
3. Run `continue tdd` to attempt more refactorings

### Technology Not Detected

**Symptoms:** Warning about unknown tech stack

**Solutions:**
1. Ensure project has standard config files (`requirements.txt`, `package.json`)
2. Manually specify in context if needed
3. File an issue to add support for your stack

---

## 📈 Metrics & Learning

### Orchestrator Metrics

View overall performance:

```bash
# In Python console
from src.orchestrators.tdd import TDDOrchestrator
metrics = orchestrator.get_orchestrator_metrics()
print(f"Success Rate: {metrics['success_rate']:.1%}")
print(f"Patterns Learned: {metrics['patterns_learned']}")
```

**Tracked Metrics:**
- Total cycles executed
- Success rate
- Patterns learned
- Technologies discovered
- Average quality improvement
- Average tests per feature

### Pattern Learning

The orchestrator learns from every successful cycle:

1. **Test Generation Patterns:** Edge cases used, test techniques
2. **Implementation Patterns:** Code structures, framework usage
3. **Refactoring Patterns:** Successful refactorings, quality improvements

These patterns are stored in Tier 2 and retrieved for future cycles.

---

## 🔗 Integration

### With Planning System

TDD is automatically included in all planning system plans:

```bash
plan User Authentication
# Automatically includes RED → GREEN → REFACTOR phases
```

### With CI/CD

Run TDD orchestrator in your CI pipeline:

```yaml
# .github/workflows/tdd.yml
- name: Run TDD Cycle
  run: |
    python -m src.orchestrators.tdd.tdd_orchestrator \
      --feature "New Feature" \
      --project-path "."
```

---

## 📚 Advanced Usage

### Custom Strategies

Add custom phases by implementing `TDDPhaseStrategy`:

```python
from src.orchestrators.tdd import TDDPhaseStrategy

class PERFORMANCEPhaseStrategy(TDDPhaseStrategy):
    async def execute(self, context):
        # Load testing, profiling, benchmarking
        pass

orchestrator.register_strategy('PERFORMANCE', PERFORMANCEPhaseStrategy())
```

### Programmatic Usage

```python
from pathlib import Path
from src.orchestrators.tdd import TDDOrchestrator

orchestrator = TDDOrchestrator(brain, kg, mcp)

result = await orchestrator.execute_tdd_cycle(
    feature_name="User Authentication",
    acceptance_criteria=[
        "Users can login",
        "Passwords hashed"
    ],
    project_path=Path("./my-project")
)

print(f"Success: {result['success']}")
print(f"Tests: {result['metrics']['total_tests']}")
print(f"Quality: {result['metrics']['quality_score']}")
```

---

## 🎯 Examples

See `examples/tdd_orchestrator_example.py` for complete examples:

1. Basic TDD cycle
2. Multi-feature workflow with learning
3. Technology discovery demonstration

---

## 📖 Reference

- **Manifest:** `cortex-brain/manifests/orchestrators/tdd-orchestrator-v4-manifest.yaml`
- **Implementation:** `src/orchestrators/tdd/tdd_orchestrator.py`
- **Strategies:** `src/orchestrators/tdd/strategies/`
- **Tests:** `tests/orchestrators/tdd/`
- **Brain Rules:** `cortex-brain/brain-protection-rules.yaml` (TDD_ENFORCEMENT)

---

## 🆘 Support

**Issues:** File at [GitHub Issues](https://github.com/asifhussain60/CORTEX/issues)  
**Questions:** Ask in Copilot Chat with `tdd help`  

---

**Version:** 4.0.0 | **Status:** ✅ Production Ready
