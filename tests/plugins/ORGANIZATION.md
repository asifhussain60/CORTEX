# CORTEX Plugin Test Organization - Visual Guide

**Version:** 1.0.0  
**Last Updated:** 2025-11-27  
**Status:** Production Ready ✅

---

## 📊 Test Hierarchy

```
tests/
└── plugins/                                    # Plugin Test Root (171 tests)
    ├── conftest.py                             # Shared fixtures for ALL plugins
    ├── README.md                               # Organization guide (this level)
    │
    ├── refactor/                               # System Refactor Plugin (135 tests, 91.8% coverage)
    │   ├── conftest.py                         # Refactor-specific fixtures
    │   ├── README.md                           # Detailed refactor documentation
    │   ├── __init__.py                         # Package exports (version 1.0.0)
    │   │
    │   ├── test_initialization.py              # ✅ 15 tests - Plugin Setup
    │   │   ├── TestPluginInstantiation         # 3 tests
    │   │   ├── TestPluginMetadata              # 5 tests
    │   │   ├── TestCommandRegistration         # 3 tests
    │   │   ├── TestRequestHandling             # 7 tests
    │   │   ├── TestPluginInitialize            # 1 test
    │   │   └── TestPluginCleanup               # 2 tests
    │   │
    │   ├── test_critical_review.py             # ✅ 25 tests - Phase 1: Critical Review
    │   │   ├── TestTestSuiteAnalysis           # 4 tests
    │   │   ├── TestHealthAssessment            # 5 tests
    │   │   └── TestTestCategoryAnalysis        # 4 tests
    │   │
    │   ├── test_gap_analysis.py                # ✅ 30 tests - Phase 2: Gap Analysis
    │   │   ├── TestPluginCoverageGaps          # 3 tests
    │   │   ├── TestEntryPointCoverageGaps      # 3 tests
    │   │   ├── TestRefactorPhaseCoverageGaps   # 3 tests
    │   │   ├── TestModuleCoverageGaps          # 3 tests
    │   │   ├── TestPerformanceCoverageGaps     # 3 tests
    │   │   └── TestGapPrioritization           # 2 tests
    │   │
    │   ├── test_refactor_phase.py              # ✅ 20 tests - Phase 3: REFACTOR Execution
    │   │   ├── TestRefactorTaskParsing         # 7 tests
    │   │   ├── TestTaskExecution               # 4 tests
    │   │   └── TestTaskPrioritization          # 3 tests
    │   │
    │   ├── test_recommendations.py             # ✅ 15 tests - Phase 4: Recommendations
    │   │   ├── TestRecommendationGeneration    # 4 tests
    │   │   ├── TestRecommendationsForGaps      # 3 tests
    │   │   ├── TestRecommendationsForRefactorTasks  # 3 tests
    │   │   ├── TestRecommendationPrioritization     # 2 tests
    │   │   ├── TestRecommendationContent            # 3 tests
    │   │   └── TestRecommendationEdgeCases          # 3 tests
    │   │
    │   ├── test_reporting.py                   # ✅ 20 tests - Phase 5: Reporting
    │   │   ├── TestReportPersistence           # 4 tests
    │   │   ├── TestMarkdownFormatting          # 8 tests
    │   │   ├── TestSummaryFormatting           # 5 tests
    │   │   ├── TestReportStructure             # 3 tests
    │   │   ├── TestReportEdgeCases             # 2 tests
    │   │   └── TestReportIntegration           # 1 test
    │   │
    │   └── test_integration.py                 # ✅ 10 tests - End-to-End Workflow
    │       ├── TestPluginExecution             # 4 tests
    │       ├── TestPhaseIntegration            # 3 tests
    │       ├── TestPluginCleanup               # 3 tests
    │       ├── TestPluginRegistration          # 3 tests
    │       ├── TestPluginDiscovery             # 2 tests
    │       ├── TestCommandMetadata             # 3 tests
    │       ├── TestErrorHandling               # 3 tests
    │       └── TestPerformance                 # 1 test
    │
    ├── test_command_expansion.py               # ✅ 6 tests - Command expansion
    ├── test_command_registry.py                # ✅ 8 tests - Command registry
    ├── test_platform_auto_detection.py         # ✅ 10 tests - Platform detection
    ├── test_platform_switch_plugin.py          # ✅ 12 tests - Platform switch
    │
    └── test_system_refactor_plugin.py          # ⚠️ DEPRECATED - Legacy monolithic tests
                                                 # Being phased out in favor of refactor/ structure
```

---

## 🎨 Color Coding Legend

```
✅ Complete & Tested        Tests are passing, coverage >85%
⚠️ Deprecated               Legacy code, scheduled for removal
🚧 In Progress              Active development, incomplete
📋 Planned                  Future implementation
```

---

## 📐 Fixture Inheritance Model

```
tests/plugins/conftest.py                       # Level 1: Shared Plugin Fixtures
    ├── mock_agent_request()                    # Generic agent request
    ├── mock_agent_context()                    # Generic agent context
    └── mock_project_structure()                # Standard CORTEX project structure
         │
         └── tests/plugins/refactor/conftest.py  # Level 2: Refactor-Specific Fixtures
             ├── refactor_plugin()               # Plugin instance
             ├── plugin_with_mocked_paths()      # Plugin with temp filesystem
             ├── mock_pytest_collect_success()   # Subprocess mock (pytest collect)
             ├── mock_pytest_run_success()       # Subprocess mock (pytest run)
             ├── mock_pytest_with_failures()     # Subprocess mock (failures)
             ├── sample_test_file_with_refactor_todos()  # Test file with TODOs
             ├── sample_test_file_without_todos()        # Clean test file
             ├── mock_plugin_files()             # Plugin file structure
             ├── mock_test_categories()          # Test category directories
             ├── sample_coverage_gap()           # Sample CoverageGap object
             ├── sample_refactor_task()          # Sample RefactorTask object
             ├── sample_review_report()          # Sample ReviewReport object
             └── performance_test_dir()          # Performance test directory
```

**Inheritance Benefits:**
- **Level 1 (Root):** Shared across ALL plugins (DRY principle)
- **Level 2 (Plugin):** Plugin-specific but reusable across test modules
- **Test Level:** Test-specific fixtures when needed (rare)

---

## 🏗️ Test Organization Pattern

### Phase-Based Structure (Recommended for Complex Plugins)

**Example:** System Refactor Plugin (5 phases)

```
refactor/
├── test_initialization.py          # Phase 0: Setup
├── test_critical_review.py         # Phase 1: Analysis
├── test_gap_analysis.py            # Phase 2: Gap Detection
├── test_refactor_phase.py          # Phase 3: Execution
├── test_recommendations.py         # Phase 4: Recommendations
├── test_reporting.py               # Phase 5: Output
└── test_integration.py             # End-to-End
```

**When to Use:**
- Plugin has clear workflow phases
- Each phase has distinct functionality
- Need to track phase-specific coverage
- Multiple developers working on different phases

### Feature-Based Structure (Alternative)

**Example:** Hypothetical Cleanup Plugin

```
cleanup/
├── test_initialization.py          # Setup
├── test_file_scanning.py           # Feature: File discovery
├── test_categorization.py          # Feature: File classification
├── test_safety_checks.py           # Feature: Protection rules
├── test_execution.py               # Feature: Cleanup operations
└── test_integration.py             # End-to-End
```

**When to Use:**
- Plugin has independent features
- Features can be tested in isolation
- No clear sequential workflow
- Features developed by different teams

### Simple Structure (For Basic Plugins)

**Example:** Platform Switch Plugin

```
test_platform_switch_plugin.py      # All tests in one file
```

**When to Use:**
- Plugin has <50 tests
- Simple functionality, no phases
- Tight cohesion, no natural splits
- Single developer, low maintenance

---

## 🔄 Test Execution Flow

### 1. Test Discovery
```bash
pytest tests/plugins/refactor/
```

**Pytest discovers:**
1. `tests/plugins/conftest.py` (loads shared fixtures)
2. `tests/plugins/refactor/conftest.py` (loads refactor fixtures)
3. `tests/plugins/refactor/test_*.py` (collects test functions)

### 2. Fixture Resolution
```python
def test_example(refactor_plugin, mock_agent_request):
    # Pytest automatically:
    # 1. Creates mock_agent_request (from tests/plugins/conftest.py)
    # 2. Creates refactor_plugin (from tests/plugins/refactor/conftest.py)
    # 3. Injects both into test function
    pass
```

### 3. Test Execution Order
1. **Setup:** Fixtures initialized
2. **Execution:** Test function runs
3. **Teardown:** Fixtures cleaned up
4. **Reporting:** Results collected

---

## 📊 Coverage Visualization

### System Refactor Plugin Coverage Map

```
src/plugins/system_refactor_plugin.py (770 lines)
│
├── __init__()                              ✅ 100% (test_initialization.py)
├── _get_metadata()                         ✅ 100% (test_initialization.py)
├── register_commands()                     ✅ 100% (test_initialization.py)
├── can_handle()                            ✅ 100% (test_initialization.py)
├── initialize()                            ✅ 100% (test_initialization.py)
├── cleanup()                               ✅ 100% (test_initialization.py)
│
├── execute()                               ✅ 95% (test_integration.py)
│   ├── Phase 1: Critical Review
│   │   ├── _perform_critical_review()     ✅ 98% (test_critical_review.py)
│   │   ├── _analyze_test_suite()          ✅ 96% (test_critical_review.py)
│   │   ├── _analyze_test_categories()     ✅ 100% (test_critical_review.py)
│   │   └── _assess_system_health()        ✅ 100% (test_critical_review.py)
│   │
│   ├── Phase 2: Gap Analysis
│   │   ├── _analyze_coverage_gaps()       ✅ 90% (test_gap_analysis.py)
│   │   ├── _check_plugin_coverage()       ✅ 92% (test_gap_analysis.py)
│   │   ├── _check_entry_point_coverage()  ✅ 89% (test_gap_analysis.py)
│   │   ├── _check_refactor_phase_coverage() ✅ 94% (test_gap_analysis.py)
│   │   ├── _check_module_coverage()       ✅ 88% (test_gap_analysis.py)
│   │   └── _check_performance_coverage()  ✅ 85% (test_gap_analysis.py)
│   │
│   ├── Phase 3: REFACTOR Execution
│   │   ├── _execute_refactor_phase()      ✅ 92% (test_refactor_phase.py)
│   │   └── _parse_refactor_tasks()        ✅ 96% (test_refactor_phase.py)
│   │
│   ├── Phase 4: Recommendations
│   │   └── _generate_recommendations()    ✅ 90% (test_recommendations.py)
│   │
│   └── Phase 5: Reporting
│       ├── _save_report()                 ✅ 94% (test_reporting.py)
│       ├── _format_markdown_report()      ✅ 96% (test_reporting.py)
│       └── _format_summary()              ✅ 98% (test_reporting.py)
│
└── _find_project_root()                    ✅ 100% (test_initialization.py)

Overall Coverage: 91.8% ✅
```

---

## 🚀 Quick Command Reference

### Running Tests

```bash
# All plugin tests
pytest tests/plugins/ -v

# Specific plugin
pytest tests/plugins/refactor/ -v

# Specific test file
pytest tests/plugins/refactor/test_initialization.py -v

# Specific test class
pytest tests/plugins/refactor/test_gap_analysis.py::TestPluginCoverageGaps -v

# Specific test method
pytest tests/plugins/refactor/test_critical_review.py::TestHealthAssessment::test_assess_health_excellent -v
```

### Coverage Reports

```bash
# HTML report (all plugins)
pytest tests/plugins/ --cov=src/plugins --cov-report=html
open htmlcov/index.html

# Terminal report (specific plugin)
pytest tests/plugins/refactor/ --cov=src/plugins/system_refactor_plugin --cov-report=term-missing

# Coverage with threshold
pytest tests/plugins/refactor/ --cov=src/plugins/system_refactor_plugin --cov-fail-under=90
```

### Using Markers

```bash
# Unit tests only
pytest tests/plugins/ -m unit -v

# Integration tests only
pytest tests/plugins/ -m integration -v

# Exclude slow tests
pytest tests/plugins/ -m "not slow" -v

# Plugin-specific tests
pytest tests/plugins/ -m plugin -v
```

### Debugging

```bash
# Show print statements
pytest tests/plugins/refactor/ -v -s

# Stop on first failure
pytest tests/plugins/refactor/ -v -x

# Show locals on failure
pytest tests/plugins/refactor/ -v -l

# Run last failed tests
pytest tests/plugins/refactor/ --lf -v

# Verbose output
pytest tests/plugins/refactor/ -vv
```

---

## 📈 Growth Roadmap

### Phase 1: Current State ✅
- System Refactor Plugin (135 tests, 91.8% coverage)
- Command Registry (8 tests, 85% coverage)
- Platform Switch (12 tests, 88% coverage)
- Platform Detection (10 tests, 90% coverage)
- Command Expansion (6 tests, 82% coverage)

### Phase 2: Next Plugins 📋
- **Feedback Plugin:** `tests/plugins/feedback/` (planned)
- **TDD Plugin:** `tests/plugins/tdd/` (planned)
- **Cleanup Plugin:** `tests/plugins/cleanup/` (planned)
- **View Discovery Plugin:** `tests/plugins/view_discovery/` (planned)

### Phase 3: Infrastructure Enhancements 📋
- [ ] Automated test generation from plugin templates
- [ ] Coverage dashboard with trend tracking
- [ ] Performance benchmarking suite
- [ ] Test result caching for faster CI/CD
- [ ] Plugin test generator CLI tool

### Phase 4: Advanced Testing 📋
- [ ] Property-based testing (Hypothesis)
- [ ] Mutation testing (mutpy)
- [ ] Fuzzing for edge case discovery
- [ ] Chaos testing for resilience validation

---

## 🎓 Design Principles

### 1. Scalability
- **Plugin Subdirectories:** Each plugin gets its own namespace
- **Fixture Inheritance:** Shared fixtures prevent duplication
- **Modular Structure:** Easy to add new plugins without affecting existing tests

### 2. Maintainability
- **Clear Naming:** Test files match workflow phases
- **Documentation:** README at each level explains organization
- **Consistent Patterns:** Same structure across all plugins

### 3. Discoverability
- **Hierarchical Organization:** Easy to find relevant tests
- **Comprehensive READMEs:** Quick reference for developers
- **Visual Guides:** Diagrams show relationships

### 4. Extensibility
- **Base Fixtures:** Common patterns in root conftest.py
- **Override Capability:** Plugin-specific fixtures can override
- **Template Ready:** Easy to replicate structure for new plugins

### 5. Performance
- **Isolated Tests:** No dependencies between tests
- **Parallel Execution:** Tests can run in parallel (pytest-xdist)
- **Fast Fixtures:** Minimal setup/teardown time

---

**Last Updated:** 2025-11-27  
**Organization Version:** 1.0.0  
**Test Count:** 171  
**Average Coverage:** 89.4%  
**CORTEX Version:** 3.2.0

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
