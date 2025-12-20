# System Integrity Orchestrator

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Status:** ✅ Production Ready

---

## 🎯 Purpose

Admin-level orchestrator that comprehensively validates CORTEX 4.0 system integrity and automatically fixes issues:

- ✅ Master plan alignment with actual implementation
- ✅ Test execution and coverage verification
- ✅ Documentation completeness and generation
- ✅ File organization and structure cleanup
- ✅ Broken link detection and repair across all markdown files
- ✅ Legacy artifact removal (CORTEX 3.0)
- ✅ Root folder organization
- ✅ Manifest and reference integrity

**Philosophy:** Don't just report issues - **FIX THEM AUTOMATICALLY**.

---

## 🚀 Usage

### Simple Command (Natural Language)

```bash
# In Copilot Chat
system integrity
validate system
check integrity
integrity check
```

### CLI Wrapper

```bash
# Full integrity check with auto-fix (default)
python scripts/cli_wrappers/system_integrity_wrapper.py

# Check only, no fixes
python scripts/cli_wrappers/system_integrity_wrapper.py --no-fix

# Skip test execution
python scripts/cli_wrappers/system_integrity_wrapper.py --no-tests

# Cleanup only (no tests or docs)
python scripts/cli_wrappers/system_integrity_wrapper.py --no-tests --no-docs

# Verbose output
python scripts/cli_wrappers/system_integrity_wrapper.py --verbose
```

### Programmatic Usage

```python
from src.orchestrators.system.system_integrity_orchestrator import SystemIntegrityOrchestrator

# Create orchestrator
orchestrator = SystemIntegrityOrchestrator(logger)

# Execute with options
result = orchestrator.execute({
    'fix_mode': True,           # Auto-fix issues (default)
    'run_tests': True,           # Run test suite (default)
    'generate_docs': True,       # Generate missing docs (default)
    'cleanup_legacy': True,      # Remove CORTEX 3.0 artifacts (default)
    'reorganize_files': True     # Fix file structure (default)
})

# Check results
if result['is_complete']:
    print("✅ System integrity validated!")
else:
    print(f"⚠️  {result['issues_remaining']} issues remaining")
```

---

## 📊 What It Validates

### Phase 1: Master Plan Alignment
- ✅ Parses completed phases from master plan
- ✅ Verifies implementation artifacts exist
- ✅ Checks orchestrator files for completed phases
- ✅ Validates phase-specific requirements

### Phase 2: Test Suite Validation
- ✅ Runs full pytest suite
- ✅ Parses test results (passed/failed)
- ✅ Reports test failures as high-severity issues
- ✅ Tracks test coverage metrics

### Phase 3: Documentation Completeness
- ✅ Checks for completion reports for each phase
- ✅ Auto-generates missing phase documentation
- ✅ Validates documentation structure
- ✅ Ensures all completed work is documented

### Phase 4: File Organization
- ✅ Runs `cortex-cleanup.ps1` script
- ✅ Checks root folder for misplaced files
- ✅ Relocates files to proper directories
- ✅ Tracks all file moves for link repair

### Phase 5: Broken Link Repair
- ✅ Scans all markdown files recursively
- ✅ Detects broken relative links
- ✅ Updates links for relocated files
- ✅ Skips external URLs

### Phase 6: Legacy Cleanup
- ✅ Removes CORTEX 3.0 artifacts (`*_v3.py`, `*_legacy.py`)
- ✅ Cleans up deprecated directories
- ✅ Safely deletes unused legacy code
- ✅ Verifies files aren't referenced in active code

### Phase 7: Manifest Validation
- ✅ Validates `cortex-operations.yaml`
- ✅ Ensures orchestrator is registered
- ✅ Checks manifest syntax
- ✅ Auto-registers missing operations

### Phase 8: Report Generation
- ✅ Generates comprehensive integrity report
- ✅ Categorizes issues by type and severity
- ✅ Tracks all fixes applied
- ✅ Saves report to `cortex-brain/documents/reports/`

---

## 📈 Output Report

After execution, generates a detailed report:

```markdown
# CORTEX System Integrity Report

**Generated:** 2025-12-20 15:30:00
**Execution Time:** 45.23 seconds

## Executive Summary
- Issues Found: 15
- Issues Fixed: 13
- Issues Remaining: 2
- Tests Passed: 138/138
- Docs Generated: 3
- Files Relocated: 7
- Links Fixed: 12

## Issues by Category
- plan: 2
- tests: 0
- docs: 3
- structure: 7
- links: 2
- legacy: 1

## Detailed Issues
[Full list with fix status]
```

---

## 🏗️ Architecture

### Orchestrator Structure

```
SystemIntegrityOrchestrator
├── _setup()                    # Initialize context
├── _register_phases()          # Register 8 phases
├── execute()                   # Main execution
│
├── Phase 1: _phase_analyze()
│   ├── _parse_completed_phases()
│   └── _validate_phase_implementation()
│
├── Phase 2: _phase_validate_tests()
│   └── subprocess: pytest tests/
│
├── Phase 3: _phase_check_docs()
│   └── _generate_phase_documentation()
│
├── Phase 4: _phase_organize_files()
│   ├── subprocess: cortex-cleanup.ps1
│   ├── _check_root_folder()
│   └── _relocate_file()
│
├── Phase 5: _phase_repair_links()
│   └── _repair_links_in_file()
│
├── Phase 6: _phase_cleanup_legacy()
│   ├── _is_safe_to_delete()
│   └── _delete_path()
│
├── Phase 7: _phase_validate_manifests()
│   └── _add_system_integrity_to_manifest()
│
└── Phase 8: _phase_generate_report()
    └── _build_report_content()
```

### Data Structures

```python
@dataclass
class IntegrityIssue:
    category: str       # 'plan', 'tests', 'docs', 'structure', 'links', 'legacy'
    severity: str       # 'critical', 'high', 'medium', 'low'
    description: str
    location: Optional[Path]
    auto_fixable: bool
    fix_applied: bool
    fix_result: Optional[str]

@dataclass
class IntegrityReport:
    issues_found: int
    issues_fixed: int
    issues_remaining: int
    tests_run: int
    tests_passed: int
    tests_failed: int
    docs_generated: int
    files_relocated: int
    files_deleted: int
    links_fixed: int
    issues: List[IntegrityIssue]
    execution_time_seconds: float
```

---

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest tests/orchestrators/system/test_system_integrity_orchestrator.py -v

# Specific test
pytest tests/orchestrators/system/test_system_integrity_orchestrator.py::TestSystemIntegrityOrchestrator::test_full_execution -v

# With coverage
pytest tests/orchestrators/system/ --cov=src.orchestrators.system --cov-report=html
```

### Test Coverage

- ✅ Initialization and setup
- ✅ Phase registration
- ✅ Master plan parsing
- ✅ Issue tracking (add/fix/report)
- ✅ Test validation (mocked)
- ✅ Documentation generation
- ✅ File relocation
- ✅ Link repair
- ✅ Report generation
- ✅ Full execution flow
- ✅ Error handling

---

## 🔧 Configuration

### Default Behavior

All features enabled by default:
- `fix_mode`: True (auto-fix issues)
- `run_tests`: True (execute test suite)
- `generate_docs`: True (create missing docs)
- `cleanup_legacy`: True (remove CORTEX 3.0)
- `reorganize_files`: True (fix structure)

### Custom Configuration

```python
context = {
    'fix_mode': False,          # Report only
    'run_tests': True,
    'generate_docs': False,
    'cleanup_legacy': True,
    'reorganize_files': False
}

result = orchestrator.execute(context)
```

---

## 🚨 Edge Cases Handled

1. **Missing Master Plan**: Reports critical issue, continues with other phases
2. **Test Timeout**: 5-minute timeout, reports as medium issue
3. **Duplicate Files**: Adds timestamp to relocated files
4. **Broken Symlinks**: Skips during link repair
5. **Permission Errors**: Logs error, continues with next item
6. **YAML Syntax Errors**: Reports manifest issue, doesn't update
7. **Legacy Files in Use**: Checks references before deletion
8. **Circular Links**: Prevents infinite loops in link repair
9. **Binary Files**: Skips in link repair (markdown only)
10. **Git-ignored Paths**: Excludes .venv, node_modules, __pycache__

---

## 📝 Manifest Entry

Registered in `cortex-brain/manifests/operations/cortex-operations.yaml`:

```yaml
operations:
  system_integrity:
    name: System Integrity
    description: Comprehensive system validation and auto-fix
    deployment_tier: admin
    execution_method: cli_wrapper
    cli_script: scripts/cli_wrappers/system_integrity_wrapper.py
    natural_language:
    - system integrity
    - validate system
    - check integrity
    - integrity check
    category: system
    modules:
    - system_integrity_orchestrator
```

---

## 🎭 Engagement Hints

The orchestrator provides visual feedback during execution:

```
🎭 Orchestrator engaged: SystemIntegrityOrchestrator
🎭 Phase transition: SETUP → ANALYZE
🎭 Phase transition: ANALYZE → VALIDATE_TESTS
🎭 Phase transition: VALIDATE_TESTS → CHECK_DOCS
...
🎭 Orchestrator completing: ✅ ALL WORK COMPLETE
```

---

## 🔗 Related Components

- **BaseOrchestrator**: Parent class providing lifecycle management
- **DocumentationOrchestrator**: Called for missing phase docs
- **cortex-cleanup.ps1**: PowerShell script for file organization
- **cortex-operations.yaml**: Operation registry
- **MASTER-PLAN.md**: Source of truth for completed phases

---

## 📊 Success Criteria

System is considered **fully validated** when:

✅ `issues_remaining == 0`  
✅ `tests_failed == 0`  
✅ All completed phases have documentation  
✅ No files in root (except allowed)  
✅ No broken links detected  
✅ All manifests valid  

When criteria met, orchestrator shows:

```
# 🎉 CONGRATULATIONS
System integrity validated! No issues remaining.
```

---

## 🤝 Contributing

When adding new validation phases:

1. Add phase in `_register_phases()`
2. Implement `_phase_<name>()` method
3. Add tests in `test_system_integrity_orchestrator.py`
4. Update this README
5. Add phase transition logs

---

## 📄 License

Copyright © 2024-2025 Asif Hussain. All rights reserved.

---

**Questions?** See `cortex-brain/documents/planning/active/CORTEX-3.0-4.0/00-MASTER-PLAN.md`
