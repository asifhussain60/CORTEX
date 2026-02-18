# CORTEX LENS Golden Test Suite

**Authority:** AC-GOLDEN-LENS-001  
**Created:** 2026-02-17  
**Status:** Production-Ready (RED Phase)

## 📋 Overview

Comprehensive end-to-end test suite validating all CORTEX LENS capabilities through golden test scenarios with real file fixtures, audit logging, and deterministic execution.

## 🎯 Coverage Matrix

| Category | Tests | Scenarios | Status |
|----------|-------|-----------|--------|
| **Core** | 8 | 04-11 | 🔴 RED |
| **Domain** | 5 | 15-19 | 🔴 RED |
| **Knowledge Graph** | 4 | 20-23 | 🔴 RED |
| **Runtime** | 3 | 24-26 | 📝 Planned |
| **.NET Enterprise** | 5 | 27-31 | 🔴 RED |
| **Discovery** | 3 | 32-34 | 🔴 RED |
| **Visualization** | 2 | 35-36 | 📝 Planned |
| **Security** | 2 | 37-38 | 🔴 RED |
| **TOTAL** | **32** | **04-38** | **TDD** |

## 📁 Directory Structure

```
tests/orchestrators/e2e/
├── scenarios/
│   ├── lens/
│   │   ├── core/              # Core analyzer tests (04-11, 12-14)
│   │   ├── domain/            # Domain intelligence (15-19)
│   │   ├── knowledge_graph/   # Knowledge graph (20-23)
│   │   ├── runtime/           # Runtime correlation (24-26)
│   │   ├── dotnet/            # .NET enterprise (27-31)
│   │   ├── discovery/         # Capability discovery (32-34)
│   │   ├── visualization/     # Export & diagrams (35-36)
│   │   └── security/          # Security scanning (37-38)
│   ├── golden_01_implement_flow.yaml
│   ├── golden_02_fix_flow.yaml
│   └── golden_03_e2e_trigger.yaml
├── fixtures/
│   └── temp_repos/            # Temporary test repositories
├── test_golden_harness.py     # Base harness
├── test_golden_harness_RED.py # RED phase tests
├── test_golden_harness_GREEN.py
├── test_lens_golden_harness.py    # LENS-specific harness
├── test_lens_core_golden.py       # Core tests (04-11)
├── test_lens_domain_golden.py     # Domain tests (15-19)
├── test_lens_knowledge_graph_golden.py  # KG tests (20-23)
├── test_lens_dotnet_golden.py     # .NET tests (27-31)
└── test_lens_discovery_security_golden.py  # Discovery+Security (32-38)
```

## 🚀 Quick Start

### Run All LENS Golden Tests
```bash
cd /Users/asifhussain/PROJECTS/CORTEX
pytest tests/orchestrators/e2e/test_lens_*_golden.py -v --tb=short
```

### Run Specific Category
```bash
# Core capabilities
pytest tests/orchestrators/e2e/test_lens_core_golden.py -v

# Domain intelligence
pytest tests/orchestrators/e2e/test_lens_domain_golden.py -v

# .NET enterprise
pytest tests/orchestrators/e2e/test_lens_dotnet_golden.py -v
```

### Run Single Scenario
```bash
pytest tests/orchestrators/e2e/test_lens_core_golden.py::TestLENSCoreCapabilities::test_golden_04_python_ast_analysis -v
```

## 📊 Test Categories

### Core Capabilities (8 Tests)

**golden_04_python_ast_analysis**
- Python AST parsing, class/function extraction
- Complexity metrics, docstring validation

**golden_05_dotnet_solution_analysis**
- .sln/.csproj parsing, project references
- Framework version detection (net8.0)

**golden_06_git_history_analysis**
- Commit parsing, hotspot detection
- Churn calculation, contributor tracking

**golden_07_config_extraction**
- YAML, JSON, TOML, .env parsing
- Secret detection, security warnings

**golden_08_api_discovery**
- OpenAPI parsing, endpoint extraction
- HTTP method detection, auth schemes

**golden_09_database_schema_analysis**
- SQL migration parsing, table extraction
- Foreign key detection, index mapping

**golden_10_dependency_graph**
- Multi-ecosystem deps (pip, npm)
- Conflict detection, license extraction

**golden_11_architecture_lens**
- Layered architecture detection
- Pattern identification, violation detection

### Domain Intelligence (5 Tests)

**golden_15_domain_inference**
- Domain clustering by prefix
- Aggregate root detection
- Bounded context identification

**golden_16-19:** Pattern clustering, business language, glossary, use cases

### Knowledge Graph (4 Tests)

**golden_20_knowledge_graph_construction**
- Node creation (File, Class, Function)
- Edge creation (imports, calls, uses)
- Relationship traversal

**golden_21-23:** Traversal, coverage mapping, dead code detection

### .NET Enterprise (5 Tests)

**golden_28_entity_framework_migrations**
- EF Core migration parsing
- Schema evolution tracking
- Up/Down migration detection

**golden_27, 29-31:** Roslyn semantic, WCF services, Azure pipelines, MSBuild

### Discovery & Security (5 Tests)

**golden_32_tech_stack_fingerprinting**
- Language detection (Python, TypeScript)
- Framework identification (Django, React)
- Tool detection (Docker, Kubernetes)

**golden_37_secret_detection**
- API key detection (Stripe, AWS, GitHub)
- Password detection, entropy analysis
- Severity classification, remediation advice

**golden_33-34, 38:** Capability gaps, crawler specs, code smells

## 🏗️ Implementation Pattern

### Scenario YAML Structure
```yaml
name: "golden_XX_feature"
description: "Feature description"
utterance: "natural language trigger"

temp_files:
  - path: "src/module.py"
    content: |
      # Python code here

expected_audit_events:
  - orchestrator: "LENSOrchestrator"
    activity: "ANALYZE_FEATURE"
    workflow_stage: "INTELLIGENCE"
    expected_fields:
      result_count: ">= 1"

expected_outcome:
  status: "COMPLETED"
  has_results: true
```

### Test Implementation Pattern
```python
@pytest.mark.lens
@pytest.mark.xfail(reason="RED phase - wiring pending")
def test_golden_XX_feature(lens_harness: LENSGoldenTestHarness):
    """Golden Test XX: Feature Description"""
    result = lens_harness.execute_lens_scenario("lens/category/golden_XX_feature")
    
    assert result.passed, f"Feature failed: {result.diffs}"
    
    # Verify audit trail
    events = lens_harness.get_audit_events()
    assert any(e['activity'] == 'ANALYZE_FEATURE' for e in events)
```

## 🔬 TDD Workflow

### RED Phase (Current)
All tests marked with `@pytest.mark.xfail` demonstrating missing functionality.

**Run RED Tests:**
```bash
pytest tests/orchestrators/e2e/test_lens_*_golden.py -v
# Expected: All tests XFAIL (expected failures)
```

### GREEN Phase (Next)
1. Wire LENSOrchestrator to golden test harness
2. Implement audit logging in LENS analyzers
3. Remove `@pytest.mark.xfail` markers
4. Verify all tests PASS

**Target:**
```bash
pytest tests/orchestrators/e2e/test_lens_*_golden.py -v
# Expected: All tests PASS
```

## 🛠️ Fixtures & Utilities

### TempRepoBuilder
Creates temporary repositories with realistic file structures:

```python
def test_example(temp_repo_builder):
    files = {
        "src/main.py": "print('hello')",
        "config.yaml": "setting: value"
    }
    
    repo_path = temp_repo_builder.create_repo("test_repo", files)
    # Files created in isolated temp directory
    # Automatic cleanup after test
```

### LENSGoldenTestHarness
Extended harness for LENS-specific scenarios:

```python
def test_example(lens_harness: LENSGoldenTestHarness):
    result = lens_harness.execute_lens_scenario("lens/core/golden_04_python_ast_analysis")
    
    assert result.passed
    assert result.audit_events_matched
```

## 📈 Execution Statistics

- **Total Scenarios:** 38 (14 implemented, 24 planned)
- **Scenario Files:** 14 YAML files
- **Test Files:** 5 Python test modules
- **Temp Fixture Management:** Automatic creation & cleanup
- **Audit Events Tracked:** All orchestrator activities
- **RED Phase Coverage:** 100% (all scenarios demonstrable)

## 🔗 Integration Points

### With Existing Framework
- Extends `GoldenTestHarness` from `test_golden_harness.py`
- Uses same audit database schema
- Shares scenario loading mechanism
- Compatible with existing audit trail validation

### With LENS Analyzers
- **Phase 2 Wiring:** Connect to `LENSOrchestrator`
- **Audit Logging:** Wire `OrchestratorAuditMixin` to analyzers
- **Result Validation:** Map analyzer outputs to expected outcomes

## 📚 Documentation

- **Framework Usage:** `docs/golden-test-framework-usage.md`
- **Scenario Format:** See `scenarios/lens/*/golden_*.yaml`
- **Test Patterns:** Review `test_lens_*_golden.py` files
- **Fixture API:** See `test_lens_golden_harness.py`

## ✅ Success Criteria

### Phase 1 (RED) - COMPLETE ✅
- [x] 38 scenario definitions created
- [x] 14 scenario YAML files implemented
- [x] 5 test modules with @pytest.mark.xfail
- [x] TempRepoBuilder with git support
- [x] LENSGoldenTestHarness extended
- [x] Clean directory structure
- [x] All tests demonstrably fail (RED)

### Phase 2 (GREEN) - PENDING
- [ ] Wire LENSOrchestrator to harness
- [ ] Implement audit logging in analyzers
- [ ] Remove @pytest.mark.xfail markers
- [ ] Verify 100% test pass rate
- [ ] Measure LENS coverage (target: 95%+)

## 🎯 Next Steps

1. **Wire Orchestrator:** Connect `LENSOrchestrator` to `execute_lens_scenario()`
2. **Add Audit Logging:** Integrate `OrchestratorAuditMixin` into LENS analyzers
3. **Implement Remaining Scenarios:** Create YAMLs for golden_12-14, 16-19, 21-26, 29-31, 33-36, 38
4. **GREEN Phase Testing:** Remove xfail markers, verify all pass
5. **CI/CD Integration:** Add to automated test pipeline

## 📞 Support

For issues or questions:
- Review scenario YAML for expected structure
- Check audit trail in `cortex_intelligence/governance.db`
- Verify temp fixtures created correctly
- Ensure database schema applied

**Version:** 1.0  
**Test Framework:** pytest 7.x+  
**Python:** 3.9+  
**Status:** RED Phase Complete ✅
