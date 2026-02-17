# Golden Test Scenarios for Repository Onboarding

## Overview
Comprehensive test suite for repository onboarding orchestrator with SQLite audit trail verification.

**Authority**: CORE-008 (TDD), CORE-011 (Type Hints), CORE-027 (Audit Trails)  
**Created**: 2026-02-17  
**Test File**: `tests/golden/onboarding/test_onboarding_scenarios_with_audit.py`

---

## 🎯 Test Scenario Catalog

### Scenario 01: Python Repository Onboarding
**Test**: `TestOnboardingScenario01_PythonRepo::test_onboard_cortex_python_repo`

- **Target**: CORTEX repository (Python)
- **Purpose**: Verify onboarding of large Python project
- **Verifies**:
  - Profile generation
  - AST graph creation for Python code
  - Audit trail logging in SQLite
  - YAML artifact generation in cortex-registry
- **Audit Checks**:
  - Operations logged in `intelligence_audit` table
  - Timestamp accuracy
  - Metadata capture

---

### Scenario 02: .NET/C# Repository Onboarding
**Test**: `TestOnboardingScenario02_DotNetRepo::test_onboard_ksessions_dotnet_repo`

- **Target**: KSESSIONS repository (.NET/C#)
- **Purpose**: Verify cross-platform language support
- **Verifies**:
  - C# file detection
  - .sln/.csproj parsing
  - Multi-language AST support
  - Governance violations for C# code
- **Audit Checks**:
  - Cross-language operations
  - .NET-specific metadata
  - Governance rule violations (KP-001, KP-002, KP-003)

---

### Scenario 03: Empty Repository
**Test**: `TestOnboardingScenario03_EmptyRepo::test_onboard_empty_repository`

- **Target**: Temporary empty directory with `.git`
- **Purpose**: Verify graceful handling of empty repos
- **Verifies**:
  - Error handling for no code files
  - Warning generation
  - Audit trail on failure
- **Audit Checks**:
  - Error status logged
  - Failure reason captured
  - No false positives in violations

---

### Scenario 04: Polyglot Repository
**Test**: `TestOnboardingScenario04_PolyglotRepo::test_onboard_polyglot_repository`

- **Target**: Temporary repo with Python, TypeScript, and Rust
- **Purpose**: Verify multi-language detection
- **Verifies**:
  - Language detection across Python, TypeScript, Rust
  - AST generation for each language
  - Unified profile with language breakdown
- **Audit Checks**:
  - Multiple language operations
  - Language-specific metadata
  - Tech stack detection

---

### Scenario 05: Documentation-Only Repository
**Test**: `TestOnboardingScenario05_NoCodeFiles::test_onboard_docs_only_repository`

- **Target**: Repository with only Markdown files
- **Purpose**: Verify handling of non-code repositories
- **Verifies**:
  - Graceful handling of docs-only repos
  - No AST generation attempted
  - Warning about missing code
- **Audit Checks**:
  - Documented as "docs-only"
  - No code analysis operations

---

### Scenario 06: Re-Onboarding Existing Repository
**Test**: `TestOnboardingScenario06_ReOnboarding::test_reonboard_existing_repository`

- **Target**: CORTEX (re-onboarded)
- **Purpose**: Verify idempotency and update behavior
- **Verifies**:
  - Existing profile detection
  - Update vs. replace logic
  - Version tracking
  - Timestamp updates
- **Audit Checks**:
  - Multiple onboarding operations logged
  - Incremental updates tracked
  - No duplicate violations

---

### Scenario 07: Missing Dependencies
**Test**: `TestOnboardingScenario07_MissingDependencies::test_onboard_repo_with_missing_deps`

- **Target**: Temporary repo with unresolved dependencies
- **Purpose**: Verify dependency gap detection
- **Verifies**:
  - Dependency scanning
  - Missing package warnings
  - requirements.txt parsing
- **Audit Checks**:
  - Dependency issues logged
  - Resolution suggestions captured

---

### Scenario 08: Repository with Secrets
**Test**: `TestOnboardingScenario08_WithSecrets::test_onboard_repo_with_secrets`

- **Target**: Temporary repo with hardcoded secrets
- **Purpose**: Verify secrets detection
- **Verifies**:
  - Secrets scanning (API keys, passwords, AWS keys)
  - Security violation generation
  - Blocking vs. warning classification
- **Audit Checks**:
  - Security violations in `governance_violations` table
  - Rule IDs (e.g., SEC-001, SEC-002)
  - Severity levels

---

### Scenario 09: Tests-Only Repository
**Test**: `TestOnboardingScenario09_TestsOnly::test_onboard_tests_only_repository`

- **Target**: Repository with only test files
- **Purpose**: Verify test detection without source code
- **Verifies**:
  - Test file detection
  - Warning about missing source code
  - Test coverage metrics (N/A)
- **Audit Checks**:
  - "Tests-only" flag in metadata
  - Test framework detection

---

### Scenario 10: Large Repository
**Test**: `TestOnboardingScenario10_LargeRepo::test_onboard_large_repository`

- **Target**: Temporary repo with 50+ files
- **Purpose**: Verify performance and scalability
- **Verifies**:
  - Handling of many files
  - AST generation performance
  - Memory efficiency
  - Progress tracking
- **Audit Checks**:
  - File count metrics
  - Processing time
  - Performance thresholds

---

### Scenario 11: Monorepo
**Test**: `TestOnboardingScenario11_Monorepo::test_onboard_monorepo`

- **Target**: Temporary monorepo with multiple projects
- **Purpose**: Verify multi-project detection
- **Verifies**:
  - Sub-project discovery
  - Independent module tracking
  - Shared library detection
- **Audit Checks**:
  - Sub-project operations
  - Cross-project dependencies
  - Module boundaries

---

### Scenario 12: Complex AST Structures
**Test**: `TestOnboardingScenario12_ComplexAST::test_onboard_complex_ast_repository`

- **Target**: Repository with advanced Python constructs
- **Purpose**: Verify AST handling of complex code
- **Verifies**:
  - Metaclass parsing
  - Decorator handling
  - Generic types
  - Async functions
  - Abstract base classes
- **Audit Checks**:
  - AST complexity metrics
  - Node count
  - Relationship depth

---

### Scenario 13: Governance Violations
**Test**: `TestOnboardingScenario13_GovernanceViolations::test_onboard_repo_with_violations`

- **Target**: Repository with known violations
- **Purpose**: Verify violation detection
- **Verifies**:
  - Missing docstrings (CORE-012)
  - Missing type hints (CORE-011)
  - Hardcoded secrets (SEC-001)
  - SQL injection patterns (SEC-002)
- **Audit Checks**:
  - Violations in `governance_violations` table
  - Rule ID tracking
  - Blocking vs. warning classification

---

### Scenario 14: Non-Existent Path
**Test**: `TestOnboardingScenario14_NonExistentPath::test_onboard_nonexistent_path`

- **Target**: `/nonexistent/path/to/repo`
- **Purpose**: Verify error handling
- **Verifies**:
  - Graceful failure on missing path
  - Clear error messages
  - No partial state corruption
- **Audit Checks**:
  - Error logged in audit trail
  - Error reason captured
  - No false success

---

### Scenario 15: Custom Domain Knowledge
**Test**: `TestOnboardingScenario15_CustomDomain::test_onboard_repo_with_domain_knowledge`

- **Target**: Repository with financial domain code
- **Purpose**: Verify domain-specific terminology extraction
- **Verifies**:
  - Domain keyword detection (IRR, Sharpe Ratio, Black-Scholes)
  - Specialized function recognition
  - Domain classification
- **Audit Checks**:
  - Domain tags in metadata
  - Terminology extraction

---

## 🔍 Audit Trail Verification Tests

### Test: Audit Database Exists
**Test**: `TestAuditTrailVerification::test_audit_database_exists`

- Verifies `governance.db` exists
- Lists all tables in database
- Validates database accessibility

### Test: Audit Trail Schema
**Test**: `TestAuditTrailVerification::test_audit_trail_schema`

- Verifies expected tables:
  - `audit_log`
  - `intelligence_audit`
  - `governance_violations`
  - `onboarding_audit`
- Validates column schemas
- Checks for required fields (timestamp, operation, target, status)

### Test: Query Onboarding Operations
**Test**: `TestAuditTrailVerification::test_query_all_onboarding_operations`

- Queries all onboarding operations across tables
- Verifies operation counts
- Validates data integrity

---

## 📊 Audit Verification Utilities

### `AuditTraceVerifier` Class

Utility class for SQLite audit trail verification:

```python
class AuditTraceVerifier:
    def __init__(self, db_path: Path)
    
    def get_operations_for_repo(repo_name: str, operation_type: Optional[str]) -> List[Dict]
    def get_governance_violations(repo_name: str, rule_id: Optional[str]) -> List[Dict]
    def verify_audit_trail_exists(repo_name: str) -> bool
    def verify_operation_logged(repo_name: str, operation: str, min_count: int) -> bool
    def get_latest_operation(repo_name: str, operation: Optional[str]) -> Optional[Dict]
    def get_all_tables() -> List[str]
```

**Features**:
- Multi-table query support
- Flexible filtering (by repo, operation, rule ID)
- Timestamp-based ordering
- Schema introspection

---

## 🎯 Expected Behaviors

### Current Known Issues (As of 2026-02-17)

Based on initial test runs, the following issues are documented:

1. **API Signature Mismatches**:
   - `capture_from_operation()` receives unexpected `operation_data` keyword
   - `detect_patterns()` receives unexpected `threshold` keyword

2. **Blocking Violations**:
   - KP-001: "No patterns captured during onboarding"
   - KP-002: "Brain enhancement incomplete"
   - KP-003: "Knowledge artifacts empty"

3. **Missing Artifacts**:
   - ❌ No YAML files generated in `cortex-registry/knowledge-base/repositories/`
   - ❌ No AST graphs generated in `cortex-registry/artifacts/ast-graphs/`
   - ❌ No JSON profiles in `cortex_intelligence/onboarded_repos/` (due to blocking violations)

4. **Audit Trail**:
   - ✅ Violations ARE logged to SQLite
   - ✅ Error messages captured
   - ✅ Timestamps recorded
   - ❌ Success cases not yet working

---

## 📈 Running the Tests

### Run All Scenarios
```bash
python3 -m pytest tests/golden/onboarding/test_onboarding_scenarios_with_audit.py -v
```

### Run Specific Scenario
```bash
python3 -m pytest tests/golden/onboarding/test_onboarding_scenarios_with_audit.py::TestOnboardingScenario02_DotNetRepo -v
```

### Run with Audit Output
```bash
python3 -m pytest tests/golden/onboarding/test_onboarding_scenarios_with_audit.py -v -s
```

### Run Audit Verification Only
```bash
python3 -m pytest tests/golden/onboarding/test_onboarding_scenarios_with_audit.py::TestAuditTrailVerification -v
```

---

## 📝 Test Output Examples

Each test prints audit trail information:

```
📊 Audit Tables: ['audit_log', 'intelligence_audit', 'governance_violations']
📝 Operations logged: 3
  - ONBOARD: 2026-02-17T10:30:45.123456
  - VALIDATE: 2026-02-17T10:30:45.234567
  - ERROR: 2026-02-17T10:30:45.345678

⚠️  Governance Violations: 3
  - KP-001: No patterns captured during onboarding. Learning capture is required for knowledge persistence.
  - KP-002: Brain enhancement incomplete: no patterns or strategies generated
  - KP-003: Knowledge artifacts empty
```

---

## ✅ Success Criteria

For each scenario, verify:

1. **Result Structure**: ✅ `status`, `repository_path`, `artifacts` keys present
2. **Audit Trail**: ✅ Operations logged in SQLite `governance.db`
3. **Timestamps**: ✅ ISO 8601 format
4. **Error Handling**: ✅ Graceful failures with clear messages
5. **Artifacts**: ❌ **TO BE IMPLEMENTED** - YAML/AST graph generation
6. **Idempotency**: ✅ Re-running produces consistent results

---

## 🔧 Future Enhancements

1. **Fix Blocking Violations**: Resolve API signature mismatches in `UniversalLearningLoop`
2. **Implement Artifact Generation**: Wire AST graph builder to onboarding
3. **Add Performance Benchmarks**: Track timing for each scenario
4. **Expand Language Support**: Add Go, Java, Ruby scenarios
5. **Add Compliance Tests**: Verify SOX, PCI-DSS compliance in audit trail
6. **Add Export Tests**: Verify audit trail export to JSON/CSV

---

## 📚 Related Documentation

- `tests/golden/onboarding/test_e2e_onboarding_ksessions.py` - Original E2E tests
- `cortex/mcp/tools/onboard_repository.py` - Onboarding tool implementation
- `cortex_intelligence/governance.db` - SQLite audit database
- `cortex-registry/` - Expected artifact output location

---

**END OF DOCUMENT**
