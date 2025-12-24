# Code Sanitization Orchestrator - Implementation Guide

**Version:** 1.0.0  
**Author:** CORTEX 4.0  
**Last Updated:** December 20, 2025

---

## Overview

The Sanitization Orchestrator implements a **5-phase workflow** to remove company-specific information from codebases while preserving functionality:

```
ANALYZE → MAPPING → TRANSFORM → VALIDATE → REPORT
```

**Key Features:**
- Automated domain terminology extraction
- Intelligent namespace-aware mappings
- Build validation with test execution
- Comprehensive audit reporting
- Dry-run mode for safe previews

---

## Architecture

### Phase Workflow

| Phase | Utility | Purpose |
|-------|---------|---------|
| **ANALYZE** | CodeAnalyzer | Scan files, extract domain terms & namespaces |
| **MAPPING** | MappingEngine | Generate domain→generic mappings, detect conflicts |
| **TRANSFORM** | CodeTransformer | Apply transformations, create backups |
| **VALIDATE** | BuildValidator | Build system detection, build + test execution |
| **REPORT** | ReportGenerator | Generate audit report with metrics |

### BaseOrchestrator Compliance

- ✅ Inherits from `BaseOrchestrator`
- ✅ Implements 5-phase enum (`SanitizationPhase`)
- ✅ Returns structured result (`SanitizationResult` dataclass)
- ✅ Engagement hints (🎭 pattern) for phase transitions
- ✅ Error handling with phase-specific failures

---

## Usage

### Basic Usage

```python
from src.orchestrators.sanitization import SanitizationOrchestrator

# Initialize orchestrator
orchestrator = SanitizationOrchestrator(
    target_directory="/path/to/project",
    dry_run=False  # Set True for preview
)

# Execute sanitization
result = orchestrator.execute()

# Check results
if result.success:
    print(f"✅ Sanitization complete!")
    print(f"Files analyzed: {result.files_analyzed}")
    print(f"Files transformed: {result.files_transformed}")
    print(f"Report: {result.report_path}")
else:
    print(f"❌ Failed at {result.phase}")
    for error in result.errors:
        print(f"  - {error}")
```

### Dry-Run Mode

Preview changes without modifying files:

```python
orchestrator = SanitizationOrchestrator(
    target_directory="/path/to/project",
    dry_run=True  # No transformations or validation
)

result = orchestrator.execute()
# Shows what WOULD be changed without actual modifications
```

---

## Configuration

### Manifest Structure

Located at: `cortex-brain/manifests/orchestrators/code-sanitization-manifest.yaml`

```yaml
name: "Code Sanitization"
version: "1.0.0"

phases:
  analyze:
    enabled: true
    file_extensions: [".py", ".cs", ".ts", ".js"]
    ignore_patterns: ["**/node_modules/**", "**/.venv/**"]
    
  mapping:
    enabled: true
    terminology_categories:
      business_entity: "Entity"
      business_process: "Process"
      domain_concept: "Concept"
    
  transform:
    enabled: true
    create_backup: true
    backup_location: ".sanitization_backup"
    
  validate:
    enabled: true
    build_systems: ["python", "dotnet", "node"]
    
  report:
    enabled: true
    output_directory: "cortex-brain/documents/reports"
    format: "markdown"
```

---

## Phase Details

### Phase 1: ANALYZE

**Purpose:** Discover files and extract domain-specific terminology

**Implementation:**
```python
def _execute_analyze_phase(self) -> Dict[str, Any]:
    # 1. Scan file structure
    file_inventory = self.analyzer.scan_file_structure()
    
    # 2. Extract domain terms
    domain_terms = self.analyzer.extract_domain_terminology()
    
    # 3. Extract namespaces
    namespaces = self.analyzer.extract_namespaces()
    
    return {
        'success': True,
        'file_inventory': file_inventory,
        'domain_terms': domain_terms,
        'namespaces': namespaces
    }
```

**Outputs:**
- File inventory with counts
- Domain terminology with categories
- Namespace hierarchies

---

### Phase 2: MAPPING

**Purpose:** Generate transformation mappings with conflict detection

**Implementation:**
```python
def _execute_mapping_phase(self, analysis: Dict) -> Dict[str, Any]:
    # 1. Generate mappings
    mappings = self.mapper.generate_mappings(
        domain_terms=analysis['domain_terms'],
        namespaces=analysis['namespaces']
    )
    
    # 2. Detect conflicts
    conflicts = self.mapper.detect_conflicts(mappings)
    if conflicts:
        logger.warning(f"Detected {len(conflicts)} naming conflicts")
    
    return {
        'success': True,
        'mappings': mappings,
        'conflicts': conflicts
    }
```

**Outputs:**
- Domain→Generic mappings
- Conflict warnings (multiple terms mapping to same generic)

---

### Phase 3: TRANSFORM

**Purpose:** Apply transformations with backup creation

**Implementation:**
```python
def _execute_transform_phase(self, mapping: Dict) -> Dict[str, Any]:
    # 1. Create output directory
    output_dir = Path(f"{self.target}_sanitized")
    output_dir.mkdir(exist_ok=True)
    
    # 2. Transform codebase
    result = self.transformer.transform_codebase(
        source_directory=str(self.target),
        output_directory=str(output_dir),
        mappings=mapping['mappings']
    )
    
    return {
        'success': True,
        'files_transformed': result['files_transformed'],
        'output_directory': str(output_dir)
    }
```

**Outputs:**
- Sanitized codebase in `{target}_sanitized/`
- Transformation count

---

### Phase 4: VALIDATE

**Purpose:** Ensure sanitized code builds and tests pass

**Implementation:**
```python
def _execute_validate_phase(self) -> Dict[str, Any]:
    # 1. Detect build system
    build_system = self.validator.detect_build_system(str(self.target))
    
    # 2. Execute build
    build_result = self.validator.execute_build(str(self.target), build_system)
    if not build_result['success']:
        return {'success': False, 'errors': ['Build failed']}
    
    # 3. Run tests
    test_result = self.validator.run_tests(str(self.target), build_system)
    
    return {
        'success': True,
        'passed': test_result['success'],
        'build_system': build_system,
        'test_result': test_result
    }
```

**Outputs:**
- Build success/failure
- Test results with pass/fail counts

---

### Phase 5: REPORT

**Purpose:** Generate comprehensive audit report

**Implementation:**
```python
def _execute_report_phase(self, ..., analysis, mappings, transform, validate) -> Dict:
    results = {
        'status': 'success' if validation_passed else 'failed',
        'phases': {
            'analyze': analysis,
            'mapping': mappings,
            'transform': transform,
            'validate': validate
        }
    }
    
    report_path = self.reporter.generate_audit_report(results)
    
    return {
        'success': True,
        'report_path': report_path
    }
```

**Outputs:**
- Markdown audit report at `cortex-brain/documents/reports/sanitization-audit-report.md`

---

## Error Handling

### Phase-Specific Failures

Each phase can fail independently:

```python
# ANALYZE failure
result = orchestrator.execute()
if not result.success and result.phase == SanitizationPhase.ANALYZE:
    print("Analysis failed - check file permissions")

# MAPPING failure
if not result.success and result.phase == SanitizationPhase.MAPPING:
    print("Mapping failed - check manifest configuration")

# TRANSFORM failure
if not result.success and result.phase == SanitizationPhase.TRANSFORM:
    print("Transform failed - check disk space")

# VALIDATE failure
if not result.success and result.phase == SanitizationPhase.VALIDATE:
    print("Validation failed - code may not compile")
```

### Error Recovery

Orchestrator stops at first failure and returns:
- `success=False`
- `phase=<failed_phase>`
- `errors=[<error_messages>]`

---

## Testing

### Test Coverage

**24 tests across 5 test files:**
- `test_orchestrator_foundation.py` (9 tests) - Core structure
- `test_analyze_phase.py` (3 tests) - File scanning, term extraction
- `test_mapping_phase.py` (3 tests) - Mapping generation, conflicts
- `test_transform_phase.py` (3 tests) - Transformation, backups
- `test_validate_phase.py` (3 tests) - Build, test execution
- `test_report_phase.py` (3 tests) - Report generation, metrics

### Running Tests

```bash
# All tests
pytest src/orchestrators/sanitization/tests/ -v --no-cov

# Specific phase
pytest src/orchestrators/sanitization/tests/test_transform_phase.py -v

# With coverage
pytest src/orchestrators/sanitization/tests/ --cov=src/orchestrators/sanitization
```

---

## Best Practices

### 1. Always Use Dry-Run First

```python
# Preview changes
result = SanitizationOrchestrator(target, dry_run=True).execute()

# If acceptable, run for real
if result.success:
    result = SanitizationOrchestrator(target, dry_run=False).execute()
```

### 2. Review Mapping Conflicts

Check for multiple domain terms mapping to the same generic:

```python
result = orchestrator.execute()
# Review mappings in report before deploying sanitized code
```

### 3. Validate Before Distribution

Always ensure validation passes:

```python
if result.validation_passed:
    print("✅ Safe to distribute")
else:
    print("❌ Fix build/test failures first")
```

### 4. Keep Audit Reports

Reports contain critical provenance information:
- Original→sanitized mappings
- Transformation counts
- Validation results

---

## Troubleshooting

### Issue: "Orchestrator using mock utilities"

**Cause:** Utilities not initialized properly  
**Fix:** Check manifest file exists and is valid YAML

### Issue: "Build validation failed"

**Cause:** Sanitized code doesn't compile  
**Fix:** Review mappings for namespace conflicts, check manual code reviews

### Issue: "No domain terms detected"

**Cause:** Analyzer configuration too restrictive  
**Fix:** Update `file_extensions` and `ignore_patterns` in manifest

---

## Integration with CORTEX

### Planning System 2.0

Can be invoked via:
```bash
# Via Copilot Chat
"Plan code sanitization for [directory]"

# Via orchestrator directly
orchestrator = SanitizationOrchestrator(target, dry_run=False)
result = orchestrator.execute()
```

### Brain Integration

- Manifests: `cortex-brain/manifests/orchestrators/`
- Reports: `cortex-brain/documents/reports/`
- Templates: `cortex-brain/templates/orchestrators/`

---

## API Reference

### SanitizationOrchestrator

**Constructor:**
```python
SanitizationOrchestrator(
    target_directory: str,  # Path to project
    dry_run: bool = False   # Preview mode
)
```

**Methods:**
- `execute() -> SanitizationResult` - Run full 5-phase workflow

### SanitizationResult

**Fields:**
- `success: bool` - Overall success
- `phase: SanitizationPhase` - Last completed phase
- `files_analyzed: int` - Total files scanned
- `mappings_created: int` - Number of term mappings
- `files_transformed: int` - Files modified
- `validation_passed: bool` - Build+test success
- `report_path: Path` - Audit report location
- `duration_seconds: float` - Execution time
- `errors: List[str]` - Error messages

### SanitizationPhase (Enum)

- `ANALYZE` - File scanning and term extraction
- `MAPPING` - Transformation mapping generation
- `TRANSFORM` - Code modification
- `VALIDATE` - Build and test execution
- `REPORT` - Audit report generation

---

## Examples

### Example 1: Sanitize Python Project

```python
from src.orchestrators.sanitization import SanitizationOrchestrator

orchestrator = SanitizationOrchestrator(
    target_directory="/projects/acme-billing-system",
    dry_run=False
)

result = orchestrator.execute()

print(f"""
Sanitization Results:
- Status: {'✅ Success' if result.success else '❌ Failed'}
- Files Analyzed: {result.files_analyzed}
- Mappings Created: {result.mappings_created}
- Files Transformed: {result.files_transformed}
- Validation: {'✅ Pass' if result.validation_passed else '❌ Fail'}
- Duration: {result.duration_seconds:.2f}s
- Report: {result.report_path}
""")
```

### Example 2: Error Handling

```python
orchestrator = SanitizationOrchestrator(target, dry_run=False)

try:
    result = orchestrator.execute()
    
    if not result.success:
        print(f"Failed at {result.phase.name} phase:")
        for error in result.errors:
            print(f"  - {error}")
            
except Exception as e:
    print(f"Orchestrator error: {e}")
```

---

## Related Documentation

- [Code Sanitization Quick Reference](../CODE-SANITIZATION-QUICK-REF.md)
- [Planning System 2.0 Manifest](../../manifests/planning-system-2.0-manifest.yaml)
- [ADO Operations Guide](./ado-operations-guide.md)

---

**End of Implementation Guide**
