# Document Governance & System Alignment Enhancement Plan

**Created:** 2025-11-28  
**Status:** Active  
**Priority:** High  
**Estimated Duration:** 8-10 hours  
**Author:** Asif Hussain

---

## 🎯 Executive Summary

Wire Document Governance into all orchestrators and enhance System Alignment to use the Enhancement Catalog for feature discovery, ensuring comprehensive integration testing and removal of deprecated features.

---

## 📋 Current State Analysis

### ✅ What's Already Implemented

1. **Document Governance System** (`src/governance/document_governance.py`)
   - Duplicate detection with similarity scoring
   - Canonical name enforcement
   - Merge strategy suggestions (update_in_place, append_phases, create_timestamped)
   - Document index caching
   - **Status:** ✅ Implemented but not wired to orchestrators

2. **Enhancement Catalog System** (`src/utils/enhancement_catalog.py`)
   - Centralized feature tracking (Tier 3 SQLite)
   - Temporal awareness ("what's new since X")
   - Hash-based deduplication
   - Multi-source discovery (Git, YAML, codebase, templates, docs)
   - **Status:** ✅ Operational, integrated into 6 orchestrators

3. **System Alignment Orchestrator** (`src/operations/modules/admin/system_alignment_orchestrator.py`)
   - Convention-based feature discovery
   - 7-layer integration scoring (discovered → optimized)
   - Conflict detection and remediation
   - **Status:** ✅ Operational but missing catalog pre-check

4. **Integration Tests**
   - `test_system_alignment_orchestrator.py` (255 lines)
   - Multiple workflow integration tests (TDD, session, lint, etc.)
   - **Status:** ⚠️ Needs expansion for new features + obsolete feature removal

---

## 🚨 Problems to Solve

### Problem 1: Document Duplication
**Issue:** Orchestrators create new documentation files without checking if similar content exists  
**Impact:** Documentation sprawl, inconsistency, maintenance overhead  
**Root Cause:** Document Governance system not integrated into orchestrators

### Problem 2: Stale Feature Discovery
**Issue:** System Alignment discovers features from scratch each run, misses temporal context  
**Impact:** Can't answer "what's new since last alignment?" or "show me recent additions"  
**Root Cause:** Enhancement Catalog not used as first step in alignment

### Problem 3: Obsolete Feature Accumulation
**Issue:** Deprecated/redundant features remain in integration tests  
**Impact:** False positives, maintenance burden, confusion about what's actually used  
**Root Cause:** No automated obsolete feature detection and test cleanup

### Problem 4: Incomplete Integration Testing
**Issue:** New features added without corresponding integration tests  
**Impact:** Integration bugs slip through, regression risk increases  
**Root Cause:** No validation that all catalog features have integration tests

---

## 🎯 Solution Design

### Architecture Changes

```
┌─────────────────────────────────────────────────────────────┐
│                   ENHANCED WORKFLOW                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Enhancement Catalog Discovery (NEW FIRST STEP)          │
│     └─> Discover features since last alignment              │
│         └─> Update catalog with latest features             │
│                                                              │
│  2. Document Governance Check (WIRED INTO ALL ORCHESTRATORS)│
│     └─> Before creating docs: check for duplicates          │
│         └─> Suggest update/merge instead of create          │
│                                                              │
│  3. System Alignment Validation                             │
│     └─> Validate catalog features against integration tests │
│         └─> Flag missing tests for new features             │
│         └─> Flag tests for obsolete features                │
│                                                              │
│  4. Integration Test Suite Update                           │
│     └─> Add tests for new catalog features                  │
│         └─> Remove tests for deprecated features            │
│         └─> Update test documentation                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📐 Implementation Plan

### Phase 1: Wire Document Governance (3 hours)

#### Step 1.1: Create Document Governance Mixin
**File:** `src/governance/document_governance_mixin.py`

```python
class DocumentGovernanceMixin:
    """Mixin for orchestrators to enforce document governance."""
    
    def __init__(self):
        self._doc_governance = DocumentGovernance()
    
    def create_document_safely(
        self, 
        proposed_path: Path, 
        content: str,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Create document with governance checks.
        
        Returns:
            {
                'allowed': bool,
                'action': 'create' | 'update' | 'merge',
                'target_path': Path,
                'duplicates': List[DuplicateMatch],
                'recommendations': List[str]
            }
        """
        # Check for duplicates
        allowed, issues, duplicates = self._doc_governance.validate_document_creation(
            proposed_path, content
        )
        
        if not allowed and not force:
            return {
                'allowed': False,
                'action': None,
                'target_path': proposed_path,
                'duplicates': duplicates,
                'recommendations': issues
            }
        
        # Determine action based on duplicates
        if duplicates and duplicates[0].similarity_score > 0.8:
            return {
                'allowed': True,
                'action': 'update',
                'target_path': duplicates[0].existing_path,
                'duplicates': duplicates,
                'recommendations': [f"Update existing: {duplicates[0].existing_path}"]
            }
        
        return {
            'allowed': True,
            'action': 'create',
            'target_path': proposed_path,
            'duplicates': [],
            'recommendations': []
        }
```

**Integration Points:**
- PlanningOrchestrator
- EnterpriseDocumentationOrchestrator
- FeedbackOrchestrator
- ADOWorkItemOrchestrator
- ArchitectureIntelligenceOrchestrator

#### Step 1.2: Update Orchestrators to Use Mixin
**Files to Modify:**
- `src/orchestrators/planning_orchestrator.py`
- `src/operations/modules/documentation/enterprise_documentation_orchestrator_module.py`
- `src/orchestrators/ado_work_item_orchestrator.py`
- `src/operations/modules/admin/architecture_intelligence_orchestrator.py`

**Change Pattern:**
```python
# BEFORE
def _save_plan(self, plan_content: str):
    plan_path = self.brain_path / "documents" / "planning" / "features" / "active" / filename
    with open(plan_path, 'w') as f:
        f.write(plan_content)

# AFTER
def _save_plan(self, plan_content: str):
    result = self.create_document_safely(plan_path, plan_content)
    
    if not result['allowed']:
        logger.warning(f"Document creation blocked: {result['recommendations']}")
        return result
    
    if result['action'] == 'update':
        logger.info(f"Updating existing document: {result['target_path']}")
        # Merge logic here
    else:
        logger.info(f"Creating new document: {result['target_path']}")
    
    with open(result['target_path'], 'w') as f:
        f.write(plan_content)
```

#### Step 1.3: Add Document Governance Tests
**File:** `tests/governance/test_document_governance_integration.py`

Test scenarios:
- Orchestrator creates new doc (no duplicates) → allowed
- Orchestrator creates duplicate doc → blocked with suggestions
- Orchestrator updates existing doc → allowed
- Force flag bypasses governance → allowed

---

### Phase 2: Enhance System Alignment with Catalog Pre-Check (2.5 hours)

#### Step 2.1: Add Enhancement Catalog Discovery as First Step
**File:** `src/operations/modules/admin/system_alignment_orchestrator.py`

**Location:** Beginning of `run_full_validation()` method

```python
def run_full_validation(self, monitor: ProgressMonitor) -> AlignmentReport:
    """Run comprehensive system validation."""
    
    # ===== NEW PHASE 0: Enhancement Catalog Discovery =====
    monitor.update("Phase 0: Discovering features from Enhancement Catalog")
    catalog_report = self._discover_catalog_features(monitor)
    
    # Continue with existing validation phases...
    monitor.update("Phase 1: Discovering orchestrators and agents")
    # ... existing code ...
```

#### Step 2.2: Implement Catalog Discovery Method
```python
def _discover_catalog_features(self, monitor: ProgressMonitor) -> Dict[str, Any]:
    """
    Phase 0: Discover features from Enhancement Catalog.
    
    Returns:
        {
            'total_features': int,
            'new_since_last': int,
            'features_by_type': Dict[str, int],
            'new_features': List[Dict],
            'days_since_review': int
        }
    """
    catalog = EnhancementCatalog()
    discovery = EnhancementDiscoveryEngine()
    
    # Get last alignment timestamp
    last_review = catalog.get_last_review_timestamp(review_type='alignment')
    
    # Discover features since last alignment (or all if first run)
    if last_review:
        days_since = (datetime.now() - last_review).days
        discovered = discovery.discover_since(since_date=last_review)
    else:
        # First run - scan last 30 days
        discovered = discovery.discover_since(days=30)
        days_since = None
    
    # Add to catalog
    new_features_count = 0
    new_features_details = []
    
    for feature in discovered:
        feature_type = self._map_feature_type(feature.feature_type)
        
        is_new = catalog.add_feature(
            name=feature.name,
            feature_type=feature_type,
            description=feature.description,
            source=feature.source,
            metadata=feature.metadata
        )
        
        if is_new:
            new_features_count += 1
            new_features_details.append({
                'name': feature.name,
                'type': feature_type.value,
                'source': feature.source,
                'description': feature.description
            })
    
    # Log this review
    catalog.log_review(
        review_type='alignment',
        features_reviewed=len(discovered),
        new_features_found=new_features_count,
        notes=f"System Alignment run"
    )
    
    # Get all features grouped by type
    all_features = catalog.get_all_features()
    features_by_type = {}
    for feature in all_features:
        type_key = feature.feature_type.value
        features_by_type[type_key] = features_by_type.get(type_key, 0) + 1
    
    monitor.update(f"Found {new_features_count} new features since last alignment")
    
    return {
        'total_features': len(all_features),
        'new_since_last': new_features_count,
        'features_by_type': features_by_type,
        'new_features': new_features_details,
        'days_since_review': days_since
    }
```

#### Step 2.3: Integrate Catalog Report into Alignment Report
**Modify:** `AlignmentReport` dataclass to include catalog metrics (already exists in lines 148-151)

**Modify:** `run_full_validation()` to populate catalog fields:
```python
report = AlignmentReport(
    timestamp=datetime.now(),
    overall_health=overall_health,
    # ... existing fields ...
    catalog_features_total=catalog_report['total_features'],
    catalog_features_new=catalog_report['new_since_last'],
    catalog_days_since_review=catalog_report['days_since_review'],
    catalog_new_features=catalog_report['new_features']
)
```

#### Step 2.4: Update Alignment Report Template
**File:** `src/reporting/alignment_report_formatter.py`

Add section showing catalog discoveries:
```markdown
## 🆕 Enhancement Catalog Discoveries

**Total Features Tracked:** {total_features}  
**New Since Last Alignment:** {new_since_last} ({days_since_review} days ago)

### New Features Discovered:
{for feature in new_features}
- **{feature.name}** ({feature.type})
  - Source: {feature.source}
  - Description: {feature.description}
{endfor}

### Features by Type:
{for type, count in features_by_type}
- {type}: {count} features
{endfor}
```

---

### Phase 3: Update Integration Test Suite (3 hours)

#### Step 3.1: Create Integration Test Validator
**File:** `tests/validation/test_integration_coverage.py`

```python
"""
Integration Test Coverage Validator

Ensures all catalog features have corresponding integration tests
and removes tests for deprecated features.

Author: Asif Hussain
"""

import pytest
from pathlib import Path
from typing import List, Dict, Set
from src.utils.enhancement_catalog import EnhancementCatalog, FeatureType

class IntegrationTestValidator:
    """Validates integration test coverage against Enhancement Catalog."""
    
    def __init__(self, tests_root: Path):
        self.tests_root = tests_root
        self.catalog = EnhancementCatalog()
    
    def discover_test_files(self) -> List[Path]:
        """Find all integration test files."""
        return list(self.tests_root.rglob("test_*_integration.py"))
    
    def extract_tested_features(self, test_file: Path) -> Set[str]:
        """Extract feature names from test file."""
        with open(test_file, 'r') as f:
            content = f.read()
        
        # Extract class names and test names
        import re
        features = set()
        
        # Find imports like: from src.orchestrators.X import Y
        imports = re.findall(r'from src\.\w+\.(\w+)', content)
        features.update(imports)
        
        # Find test names like: def test_X_integration
        tests = re.findall(r'def test_(\w+)_integration', content)
        features.update(tests)
        
        return features
    
    def validate_coverage(self) -> Dict[str, any]:
        """
        Validate integration test coverage.
        
        Returns:
            {
                'missing_tests': List[str],  # Features without tests
                'obsolete_tests': List[str],  # Tests for non-existent features
                'coverage_percent': float,
                'recommendations': List[str]
            }
        """
        # Get all catalog features
        catalog_features = self.catalog.get_all_features()
        catalog_names = {f.name for f in catalog_features}
        
        # Get all tested features
        test_files = self.discover_test_files()
        tested_features = set()
        for test_file in test_files:
            tested_features.update(self.extract_tested_features(test_file))
        
        # Find gaps
        missing_tests = catalog_names - tested_features
        obsolete_tests = tested_features - catalog_names
        
        coverage_percent = (len(tested_features) / len(catalog_names)) * 100 if catalog_names else 0
        
        recommendations = []
        
        if missing_tests:
            recommendations.append(f"Add integration tests for {len(missing_tests)} features:")
            for feature in sorted(missing_tests)[:10]:  # Top 10
                recommendations.append(f"  - {feature}")
        
        if obsolete_tests:
            recommendations.append(f"Remove integration tests for {len(obsolete_tests)} obsolete features:")
            for feature in sorted(obsolete_tests)[:10]:  # Top 10
                recommendations.append(f"  - {feature}")
        
        return {
            'missing_tests': list(missing_tests),
            'obsolete_tests': list(obsolete_tests),
            'coverage_percent': coverage_percent,
            'recommendations': recommendations
        }


def test_integration_coverage_validation():
    """Test that all catalog features have integration tests."""
    tests_root = Path(__file__).parent.parent
    validator = IntegrationTestValidator(tests_root)
    
    result = validator.validate_coverage()
    
    # Assert minimum coverage threshold
    assert result['coverage_percent'] >= 80.0, \
        f"Integration test coverage is {result['coverage_percent']:.1f}%, below 80% threshold"
    
    # Assert no missing tests for critical features
    critical_missing = [f for f in result['missing_tests'] 
                       if 'Orchestrator' in f or 'Agent' in f]
    
    assert len(critical_missing) == 0, \
        f"Missing integration tests for critical features: {critical_missing}"
    
    # Print recommendations
    if result['recommendations']:
        print("\n⚠️  Integration Test Recommendations:")
        for rec in result['recommendations']:
            print(rec)
```

#### Step 3.2: Add Missing Integration Tests

**Files to Create:**
1. `tests/governance/test_document_governance_integration.py` (new)
2. `tests/operations/modules/admin/test_alignment_catalog_integration.py` (new)
3. `tests/orchestrators/test_planning_governance_integration.py` (new)

**Test Template:**
```python
def test_{feature}_integration():
    """Test {feature} integration with CORTEX ecosystem."""
    # Setup
    orchestrator = {Feature}Orchestrator()
    
    # Execute
    result = orchestrator.execute({'test': True})
    
    # Validate
    assert result.success is True
    assert result.status == OperationStatus.COMPLETED
    
    # Validate integration points
    # - Tier 1/2/3 interactions
    # - Response template wiring
    # - Documentation existence
    # - Error handling
```

#### Step 3.3: Remove Obsolete Integration Tests

**Process:**
1. Run `IntegrationTestValidator.validate_coverage()`
2. Identify obsolete test files (tests for non-existent features)
3. Move to `tests/archive/obsolete-integration-tests-{date}/`
4. Update test documentation

**Obsolete Test Detection Algorithm:**
```python
def identify_obsolete_tests(self) -> List[Path]:
    """Identify test files for features no longer in catalog."""
    catalog_features = {f.name for f in self.catalog.get_all_features()}
    obsolete = []
    
    for test_file in self.discover_test_files():
        tested_features = self.extract_tested_features(test_file)
        
        # If none of the tested features exist in catalog, it's obsolete
        if tested_features and not (tested_features & catalog_features):
            obsolete.append(test_file)
    
    return obsolete
```

---

### Phase 4: Update System Alignment to Validate Test Coverage (1.5 hours)

#### Step 4.1: Add Integration Test Validation Layer
**File:** `src/operations/modules/admin/system_alignment_orchestrator.py`

Add new validation phase after existing 7-layer scoring:

```python
def _validate_integration_test_coverage(
    self, 
    catalog_report: Dict, 
    monitor: ProgressMonitor
) -> Dict[str, Any]:
    """
    Phase 8: Validate integration test coverage.
    
    Ensures all catalog features have integration tests and
    identifies obsolete tests.
    """
    from tests.validation.test_integration_coverage import IntegrationTestValidator
    
    tests_root = self.project_root / "tests"
    validator = IntegrationTestValidator(tests_root)
    
    monitor.update("Validating integration test coverage")
    
    coverage_result = validator.validate_coverage()
    
    return {
        'coverage_percent': coverage_result['coverage_percent'],
        'missing_tests': coverage_result['missing_tests'],
        'obsolete_tests': coverage_result['obsolete_tests'],
        'recommendations': coverage_result['recommendations'],
        'status': 'healthy' if coverage_result['coverage_percent'] >= 80 else 'warning'
    }
```

#### Step 4.2: Integrate into Alignment Report
**Modify:** `run_full_validation()` method

```python
def run_full_validation(self, monitor: ProgressMonitor) -> AlignmentReport:
    # ... existing phases ...
    
    # Phase 8: Integration Test Coverage
    test_coverage = self._validate_integration_test_coverage(catalog_report, monitor)
    
    report = AlignmentReport(
        # ... existing fields ...
        integration_test_coverage=test_coverage['coverage_percent'],
        missing_integration_tests=test_coverage['missing_tests'],
        obsolete_integration_tests=test_coverage['obsolete_tests']
    )
```

#### Step 4.3: Update AlignmentReport Dataclass
```python
@dataclass
class AlignmentReport:
    # ... existing fields ...
    
    # Integration test coverage (NEW)
    integration_test_coverage: float = 100.0  # 0-100%
    missing_integration_tests: List[str] = field(default_factory=list)
    obsolete_integration_tests: List[str] = field(default_factory=list)
```

---

### Phase 5: Documentation & Testing (2 hours)

#### Step 5.1: Create Implementation Guides

**File 1:** `cortex-brain/documents/implementation-guides/document-governance-integration-guide.md`
- How to use Document Governance Mixin in orchestrators
- Merge strategy selection guide
- Force flag usage
- Troubleshooting duplicate detection

**File 2:** `cortex-brain/documents/implementation-guides/integration-test-coverage-guide.md`
- How to write integration tests for new features
- Coverage validation process
- Obsolete test removal workflow
- CI/CD integration recommendations

**File 3:** `cortex-brain/documents/analysis/enhanced-alignment-report-guide.md`
- New catalog discovery section interpretation
- Integration test coverage metrics
- Action items based on report findings

#### Step 5.2: Update Module Documentation

**File:** `.github/prompts/modules/system-alignment-guide.md`

Add sections:
- Enhancement Catalog Pre-Check (Phase 0)
- Document Governance Integration
- Integration Test Coverage Validation
- Obsolete Feature Detection

#### Step 5.3: Update Response Templates

**File:** `cortex-brain/response-templates.yaml`

Update `system_alignment` template to include:
- Catalog discoveries summary
- Document governance violations
- Integration test coverage metrics
- Obsolete test recommendations

---

## 🎯 Definition of Ready (DoR)

- [x] Document Governance system exists and is functional
- [x] Enhancement Catalog system exists and is functional
- [x] System Alignment Orchestrator exists and is functional
- [x] Integration test infrastructure exists
- [x] Git checkpoint system available for safe rollback
- [x] Planning document created and reviewed

---

## ✅ Definition of Done (DoD)

### Technical Completeness
- [ ] Document Governance Mixin created and tested
- [ ] All 5 orchestrators use Document Governance Mixin
- [ ] System Alignment uses Enhancement Catalog as Phase 0
- [ ] Integration Test Validator created and functional
- [ ] Missing integration tests added (100% coverage for critical features)
- [ ] Obsolete integration tests identified and archived
- [ ] AlignmentReport includes catalog and test coverage metrics

### Testing Requirements
- [ ] Unit tests for Document Governance Mixin (>90% coverage)
- [ ] Integration tests for governance-wired orchestrators
- [ ] Integration tests for catalog pre-check in alignment
- [ ] Integration tests for test coverage validator
- [ ] All existing tests still pass (100% pass rate)

### Documentation Requirements
- [ ] Implementation guides created (3 documents)
- [ ] Module documentation updated (system-alignment-guide.md)
- [ ] Response templates updated
- [ ] Inline code documentation complete
- [ ] README updates if needed

### Quality Gates
- [ ] Zero regressions in existing functionality
- [ ] Performance impact <5% on alignment execution time
- [ ] No new linting errors
- [ ] OWASP security review passed (no new vulnerabilities)

### Operational Readiness
- [ ] Admin help updated with new capabilities
- [ ] Rollback procedure documented
- [ ] Git checkpoint created before deployment
- [ ] System health check confirms no degradation

---

## 🔒 OWASP Security Review

### Security Considerations

1. **File System Access**
   - **Risk:** Document Governance reads/writes files, potential path traversal
   - **Mitigation:** Path validation in `DocumentGovernance.__init__()`, restrict to cortex-brain/
   - **Status:** ✅ Existing validation sufficient

2. **SQL Injection**
   - **Risk:** Enhancement Catalog uses SQLite with dynamic queries
   - **Mitigation:** Parameterized queries already used (src/utils/enhancement_catalog.py)
   - **Status:** ✅ No changes needed

3. **Code Execution**
   - **Risk:** Integration test validator imports test files dynamically
   - **Mitigation:** Restrict to tests/ directory only, validate file extensions
   - **Status:** ⚠️ Add path validation in Step 3.1

4. **Sensitive Data Exposure**
   - **Risk:** Alignment reports may contain file paths with usernames
   - **Mitigation:** Sanitize paths in report generation, use relative paths
   - **Status:** ⚠️ Add sanitization in Step 2.4

5. **Denial of Service**
   - **Risk:** Document similarity calculation on large files could hang
   - **Mitigation:** Add timeout and file size limits in Document Governance
   - **Status:** ⚠️ Add limits in Step 1.1 (max 10MB per doc, 30s timeout)

### Security Enhancements Required

```python
# Step 1.1 Enhancement: Add DoS protection
class DocumentGovernanceMixin:
    MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB
    SIMILARITY_TIMEOUT = 30  # seconds
    
    def create_document_safely(self, proposed_path: Path, content: str, force: bool = False):
        # Validate file size
        if len(content.encode('utf-8')) > self.MAX_DOCUMENT_SIZE:
            return {'allowed': False, 'error': 'Document exceeds size limit'}
        
        # Validate path (no traversal)
        if '..' in str(proposed_path):
            return {'allowed': False, 'error': 'Invalid path'}
        
        # Rest of implementation with timeout...
```

---

## 📊 Success Metrics

### Quantitative Metrics
- **Document Duplication Rate:** Reduce from ~15% to <5%
- **Integration Test Coverage:** Increase to 100% for critical features (orchestrators/agents)
- **Obsolete Test Count:** Reduce to 0
- **Alignment Execution Time:** <5% increase from baseline
- **False Positive Rate:** <2% for duplicate detection

### Qualitative Metrics
- Enhanced temporal awareness ("what's new")
- Improved documentation consistency
- Reduced maintenance overhead
- Better developer experience (clear merge suggestions)

---

## 🛡️ Risk Mitigation

### Risk 1: Performance Degradation
**Risk:** Document similarity calculation slows down orchestrators  
**Likelihood:** Medium | **Impact:** Medium  
**Mitigation:** 
- Implement caching for document index
- Add file size limits (max 10MB)
- Add timeout for similarity calculation (30s)
- Run similarity check async if possible

### Risk 2: False Duplicate Detection
**Risk:** Document Governance blocks legitimate new documents  
**Likelihood:** Low | **Impact:** High  
**Mitigation:**
- Tune similarity threshold (default 0.8)
- Add force flag for bypassing governance
- Log all blocked creations for review
- Implement appeal mechanism

### Risk 3: Integration Test Maintenance
**Risk:** 100% coverage requirement becomes maintenance burden  
**Likelihood:** Medium | **Impact:** Low  
**Mitigation:**
- Focus on critical features first (orchestrators, agents)
- Allow 80% threshold for non-critical features
- Automate test generation where possible
- Document exemptions clearly

### Risk 4: Catalog Synchronization Issues
**Risk:** Enhancement Catalog gets out of sync with actual features  
**Likelihood:** Low | **Impact:** Medium  
**Mitigation:**
- Run catalog discovery as first step in alignment
- Implement catalog health check in system health
- Add manual catalog refresh command
- Log all catalog modifications

---

## 🔄 Rollback Plan

### Rollback Triggers
- Integration test pass rate drops below 95%
- Alignment execution time increases >10%
- Document creation blocked for legitimate cases >5 times
- Any critical security vulnerability discovered

### Rollback Procedure
1. Create git checkpoint: `create checkpoint "pre-governance-integration"`
2. Execute implementation phases
3. If rollback needed:
   ```bash
   rollback to "pre-governance-integration"
   ```
4. Restore backup of modified files from `workflow_checkpoints/`
5. Re-run test suite to confirm stability
6. Document rollback reason and lessons learned

---

## 📅 Implementation Timeline

| Phase | Duration | Dependencies | Owner |
|-------|----------|--------------|-------|
| Phase 1: Document Governance Wiring | 3 hours | None | Asif |
| Phase 2: Alignment Catalog Pre-Check | 2.5 hours | Phase 1 complete | Asif |
| Phase 3: Integration Test Suite Update | 3 hours | Phase 2 complete | Asif |
| Phase 4: Test Coverage Validation | 1.5 hours | Phase 3 complete | Asif |
| Phase 5: Documentation & Testing | 2 hours | All phases complete | Asif |
| **Total** | **12 hours** | Sequential | Asif |

**Note:** Original estimate was 8-10 hours, revised to 12 hours after detailed analysis.

---

## 🚀 Next Steps

### Immediate Actions (Today)
1. ✅ Create this planning document
2. ⏳ Create git checkpoint: `create checkpoint "pre-governance-integration"`
3. ⏳ Begin Phase 1, Step 1.1: Create Document Governance Mixin

### Short-Term (This Week)
1. Complete Phase 1 and Phase 2
2. Run system alignment to validate catalog integration
3. Create integration test validator

### Medium-Term (Next Week)
1. Complete Phase 3 and Phase 4
2. Add missing integration tests
3. Archive obsolete tests

### Long-Term (Next Sprint)
1. Complete Phase 5 documentation
2. Update response templates
3. Train on new capabilities via hands-on tutorial

---

## 📝 Open Questions

1. **Q:** Should document governance apply to all document types or just markdown?
   **A:** Start with markdown (.md), expand to YAML (.yaml) in Phase 2

2. **Q:** What similarity threshold should trigger merge suggestion?
   **A:** 0.8 (80%) for blocking, 0.6 (60%) for warning

3. **Q:** Should obsolete tests be deleted or archived?
   **A:** Archive to `tests/archive/obsolete-{date}/` with manifest file

4. **Q:** How to handle manually created tests that don't match catalog features?
   **A:** Flag as "manual" in test metadata, exclude from obsolete detection

---

## 📚 References

- **Document Governance Implementation:** `src/governance/document_governance.py`
- **Enhancement Catalog API:** `src/utils/enhancement_catalog.py`
- **System Alignment Orchestrator:** `src/operations/modules/admin/system_alignment_orchestrator.py`
- **Integration Test Examples:** `tests/workflows/test_tdd_mastery_integration.py`
- **OWASP Top 10:** https://owasp.org/www-project-top-ten/
- **Python Security Best Practices:** https://python.readthedocs.io/en/stable/library/security_warnings.html

---

**Plan Status:** ✅ READY FOR APPROVAL  
**Approval Required From:** System Architect (Asif Hussain)  
**Implementation Start Date:** 2025-11-28  
**Target Completion Date:** 2025-11-30

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
