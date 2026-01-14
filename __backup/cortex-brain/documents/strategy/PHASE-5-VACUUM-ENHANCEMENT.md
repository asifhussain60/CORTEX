🧠 # Phase 5: Vacuum Orchestrator Enhancement & Scaffolding Removal

**Version:** 1.0.0  
**Date:** 2026-01-12  
**Author:** GitHub Copilot + Asif Hussain  
**Status:** SPECIFICATION - Ready for Implementation  
**Scope:** AC-CLEAN-301-328 (28 AC-IDs)

---

## Executive Summary

Phase 5 decommissions the temporary construction scaffolding for CORTEX 6.0. The Vacuum Orchestrator is enhanced from basic filesystem cleanup to comprehensive **Scaffolding Removal Orchestrator** that identifies, tracks, and removes:

- ✅ Hardcoded phase references (1-5, 3.5)
- ✅ Embedded planning artifacts (master-plan.yaml, cx6-plan/)
- ✅ Phase-gating logic in permanent orchestrators
- ✅ Configuration files with temporary patterns
- ✅ Archive and isolation of historical artifacts

**Key Principle:** Permanent CORTEX operates with ZERO references to construction phases or planning files.

---

## 1. Vacuum Orchestrator Enhancements

### Current State (v2)
```python
VacuumOrchestratorV2:
  - 6 cleanup categories (filesystem only)
  - Safe deletion patterns
  - Dry-run + confirmation
  - Checkpoint/rollback
  - Focused on: temp files, build artifacts, duplicates
```

### Enhanced State (Phase 5)
```python
ScaffoldingRemovalOrchestrator(VacuumOrchestratorV2):
  - EXTENDS VacuumOrchestratorV2 with scaffolding awareness
  - 5 NEW cleanup categories (code-based removal)
  - Reference analysis + AST parsing
  - Configuration mutation
  - Archive creation + isolation
  - Housekeeping enforcement integration
```

### Architecture

```
ScaffoldingRemovalOrchestrator
├── Inherits: VacuumOrchestratorV2 (filesystem ops)
├── New Methods:
│   ├── scan_hardcoded_references()      [AC-CLEAN-301]
│   ├── extract_phase_logic()            [AC-CLEAN-302]
│   ├── archive_planning_artifacts()     [AC-CLEAN-307]
│   ├── update_configuration()           [AC-CLEAN-313]
│   ├── create_feature_flags()           [AC-CLEAN-319]
│   └── verify_scaffolding_free()        [AC-CLEAN-325]
└── Integration:
    ├── HousekeepingOrchestrator (continuous enforcement)
    ├── GovernanceMerger (rule updates)
    └── MasterOrchestrator (cleanup phase gates)
```

---

## 2. Implementation Strategy

### Phase 5A: Reference Removal (AC-CLEAN-301-306)

#### Objective
Identify and remove all hardcoded phase references from production code.

#### Implementation Steps

**Step 1: Comprehensive Reference Scan (AC-CLEAN-301)**

```python
class ScaffoldingRemovalOrchestrator(VacuumOrchestratorV2):
    def scan_hardcoded_references(self) -> Dict[str, List[str]]:
        """
        Scan codebase for hardcoded phase references.
        
        Returns dict mapping file paths to line numbers with phase refs.
        """
        patterns = {
            'phase_numbers': [
                r'\bphase[_\s]*[1-5](?:\.\d)?(?![0-9])',  # phase 1-5, 3.5
                r'\bcomplete_phase\(',
                r'phase_number.*[1-5]',
                r'blocked_by_phase_[1-5]',
            ],
            'cx6_plan_refs': [
                r"cx6-plan|cx6_plan",
                r"master-plan\.yaml|master_plan_path",
                r"snowball_strategy|snowball-strategy",
            ],
            'phase_gating': [
                r'if.*phase.*==|phase.*>|phase.*<',
                r'phase_gate|wait_for_phase',
                r'current_phase|next_phase',
            ]
        }
        
        results = {}
        for py_file in Path("src").rglob("*.py"):
            with open(py_file, 'r') as f:
                for i, line in enumerate(f, 1):
                    for category, regexes in patterns.items():
                        for regex in regexes:
                            if re.search(regex, line, re.IGNORECASE):
                                results.setdefault(str(py_file), []).append({
                                    'line': i,
                                    'content': line.strip(),
                                    'category': category
                                })
        
        return results

    def extract_phase_logic(self) -> Dict[str, Any]:
        """
        Extract phase-based orchestrator methods into optional module.
        
        Returns mapping of extracted methods and their dependencies.
        """
        extraction_map = {
            'master_orchestrator.py': {
                'method': 'complete_phase',
                'new_location': 'planning_modules/lifecycle_phase_manager.py',
                'args': ['phase_number'],
                'description': 'Move to optional PlanningModule'
            },
            'state_synchronizer.py': {
                'methods': ['_validate_plan'],
                'new_location': 'planning_modules/planning_state_validator.py',
                'condition': 'if INCLUDE_PLANNING_SCAFFOLDING'
            },
            'planning_state_db.py': {
                'schema_change': 'phase_numbers → module_ids',
                'migration': 'Create migration_001_phase_to_module.sql'
            }
        }
        
        return extraction_map
```

**Step 2: Automated Refactoring (AC-CLEAN-302-306)**

Each AC-ID targets specific files:
- AC-CLEAN-302: Extract to PlanningModule
- AC-CLEAN-303: Update state_synchronizer
- AC-CLEAN-304: Migrate database schema
- AC-CLEAN-305: Update atomic_state_manager
- AC-CLEAN-306: Final verification

---

### Phase 5B: Artifact Decommission (AC-CLEAN-307-312)

#### Objective
Archive and remove all planning artifacts safely.

#### Implementation

```python
def archive_planning_artifacts(self) -> Dict[str, Any]:
    """
    Archive cx6-plan/ to historical location before deletion.
    
    Process:
    1. Create archive directory: cortex-brain/documents/archives/CORTEX-6.0-construction/
    2. Tar + compress cx6-plan/
    3. Generate manifest (files, checksums, metadata)
    4. Verify archive integrity
    5. Delete cx6-plan/
    """
    
    archive_dir = Path("cortex-brain/documents/archives/CORTEX-6.0-construction")
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Create tarball with metadata
    archive_date = datetime.now().isoformat()
    archive_file = archive_dir / f"cx6-plan-{archive_date}.tar.gz"
    
    # Tar cx6-plan/ directory
    import tarfile
    import hashlib
    
    checksums = {}
    with tarfile.open(archive_file, "w:gz") as tar:
        for file_path in Path("cortex-brain/cx6-plan").rglob("*"):
            if file_path.is_file():
                # Calculate checksum
                with open(file_path, 'rb') as f:
                    checksums[str(file_path)] = hashlib.sha256(f.read()).hexdigest()
                
                # Add to archive
                tar.add(file_path, arcname=file_path.relative_to("cortex-brain"))
    
    # Create manifest
    manifest = {
        'archive_date': archive_date,
        'version': 'CORTEX-6.0',
        'files_archived': len(checksums),
        'total_size': archive_file.stat().st_size,
        'checksums': checksums,
        'access_level': 'read-only',
        'purpose': 'Historical reference - construction scaffolding'
    }
    
    manifest_path = archive_dir / f"manifest-{archive_date}.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Verify integrity
    self._verify_archive_integrity(archive_file, manifest_path)
    
    # Delete cx6-plan/ after verification
    shutil.rmtree("cortex-brain/cx6-plan")
    
    return {
        'status': 'archived',
        'archive_file': str(archive_file),
        'manifest': str(manifest_path),
        'files_archived': len(checksums)
    }
```

**Archive Structure:**
```
cortex-brain/documents/archives/CORTEX-6.0-construction/
├── cx6-plan-2026-04-07T14:30:00.tar.gz
├── manifest-2026-04-07T14:30:00.json
├── cx6-plan-2026-04-07T14:35:00.tar.gz  (if re-run)
└── manifest-2026-04-07T14:35:00.json    (versioning)
```

---

### Phase 5C: Configuration Cleanup (AC-CLEAN-313-318)

#### Objective
Update governance rules and config files to reflect permanent architecture.

#### Implementation

```python
def update_configuration(self) -> Dict[str, Any]:
    """
    Update YAML config files to remove temporary patterns.
    
    Files to update:
    1. brittleness-ambiguity-tests.yaml - Remove plan validation
    2. file-organization-policy.yaml - Remove cx6-plan folder
    3. operational-efficiency-rules.yaml - Remove phase patterns
    4. AC-INDEX.yaml - Remove design_source cx6-plan refs
    """
    
    updates = {}
    
    # 1. Remove plan validation from brittleness tests
    brittleness_file = Path("cortex-brain/tier0/governance/brittleness-ambiguity-tests.yaml")
    with open(brittleness_file, 'r') as f:
        brittleness = yaml.safe_load(f)
    
    # Remove master-plan.yaml references
    brittleness['tests'] = [
        t for t in brittleness.get('tests', [])
        if 'master-plan' not in str(t)
    ]
    
    with open(brittleness_file, 'w') as f:
        yaml.dump(brittleness, f)
    
    updates['brittleness_tests'] = 'Plan validation removed'
    
    # 2. Update AC-INDEX.yaml design_source
    ac_index_file = Path("cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml")
    with open(ac_index_file, 'r') as f:
        ac_index = yaml.safe_load(f)
    
    for ac_category in ac_index.get('ac_categories', []):
        for ac_id_data in ac_category.get('ac_ids', []):
            if 'design_source' in ac_id_data:
                source = ac_id_data['design_source']
                if 'cx6-plan' in source:
                    # Move to permanent doc location or remove
                    ac_id_data['design_source'] = source.replace(
                        'cx6-plan/validation/',
                        'cortex-brain/documents/architecture/'
                    )
    
    with open(ac_index_file, 'w') as f:
        yaml.dump(ac_index, f)
    
    updates['ac_index'] = 'cx6-plan references updated'
    
    return updates
```

---

### Phase 5D: Housekeeping Enhancement (AC-CLEAN-319-324)

#### Objective
Ensure housekeeping continuously enforces scaffolding-free requirements.

#### Implementation

```python
class HousekeepingOrchestratorEnhanced:
    """
    Enhanced housekeeping with scaffolding alignment verification.
    
    Runs on every MasterOrchestrator turn to ensure:
    - No phase references re-introduced
    - Archive stays isolated
    - Feature flags used correctly
    - Governance rules aligned
    """
    
    def alignment_check(self) -> Dict[str, bool]:
        """
        Comprehensive alignment check (runs every turn).
        
        Returns dict of all alignment checks with pass/fail.
        """
        checks = {
            'zero_phase_references': self._check_no_phase_refs(),
            'zero_cx6plan_imports': self._check_no_plan_imports(),
            'archive_not_loaded': self._check_archive_isolated(),
            'feature_flags_used': self._check_feature_flag_usage(),
            'governance_aligned': self._check_governance_rules(),
            'config_aligned': self._check_config_alignment(),
        }
        
        # Calculate alignment score
        passed = sum(1 for v in checks.values() if v)
        score = (passed / len(checks)) * 100
        
        # Log to audit
        self.logger.info(
            category=AuditCategory.GOVERNANCE,
            component='housekeeping',
            operation='alignment_check',
            message=f'Alignment check: {score}%',
            context={'checks': checks, 'score': score}
        )
        
        # Alert if misaligned
        if score < 100:
            self.logger.warning(
                category=AuditCategory.GOVERNANCE,
                component='housekeeping',
                operation='alignment_drift',
                message=f'Scaffolding alignment drift detected: {score}%',
                context={'failed_checks': [k for k, v in checks.items() if not v]}
            )
        
        return checks
    
    def _check_no_phase_refs(self) -> bool:
        """Grep for phase 1-5 hardcodes in src/"""
        result = subprocess.run(
            ['grep', '-r', r'\bphase[_\s]*[1-5](?:\.\d)?', 'src/', '--include=*.py'],
            capture_output=True,
            text=True
        )
        # Whitelist: tests, comments, strings
        return result.returncode != 0  # No matches
    
    def _check_no_plan_imports(self) -> bool:
        """Grep for cx6-plan imports in permanent code"""
        result = subprocess.run(
            ['grep', '-r', 'from.*cx6.plan|import.*cx6.plan', 'src/', '--include=*.py'],
            capture_output=True,
            text=True
        )
        return result.returncode != 0  # No matches
    
    def _check_archive_isolated(self) -> bool:
        """Verify archive directory exists and is read-only"""
        archive_dir = Path("cortex-brain/documents/archives/CORTEX-6.0-construction")
        
        if not archive_dir.exists():
            return False
        
        # Check no imports from archive
        result = subprocess.run(
            ['grep', '-r', 'from.*archives.*CORTEX-6.0', 'src/', '--include=*.py'],
            capture_output=True,
            text=True
        )
        
        return result.returncode != 0  # No imports from archive
    
    def _check_feature_flag_usage(self) -> bool:
        """Verify feature flags control planning modules"""
        # Search for INCLUDE_PLANNING_SCAFFOLDING flag usage
        result = subprocess.run(
            ['grep', '-r', 'INCLUDE_PLANNING_SCAFFOLDING', 'src/', '--include=*.py'],
            capture_output=True,
            text=True
        )
        
        # Flag should be used in planning module imports
        return 'INCLUDE_PLANNING_SCAFFOLDING' in result.stdout
    
    def _check_governance_rules(self) -> bool:
        """Verify governance rules don't reference phases"""
        rules_dir = Path("cortex-brain/tier0/governance")
        
        for rule_file in rules_dir.glob("*.yaml"):
            with open(rule_file, 'r') as f:
                content = f.read()
                if re.search(r'\bphase[_\s]*[1-5]', content, re.IGNORECASE):
                    return False
        
        return True
    
    def _check_config_alignment(self) -> bool:
        """Verify config files don't reference planning artifacts"""
        config_dir = Path("cortex-brain")
        
        for yaml_file in config_dir.rglob("*.yaml"):
            with open(yaml_file, 'r') as f:
                content = f.read()
                if 'cx6-plan' in content:
                    return False
        
        return True
```

**Integration with HousekeepingOrchestrator:**

```python
class HousekeepingOrchestratorV3(HousekeepingOrchestrator):
    """Enhanced housekeeping with Phase 5 alignment enforcement"""
    
    def execute(self) -> OrchestratorResult:
        """Run housekeeping + alignment check"""
        
        # Existing housekeeping tasks
        result = super().execute()
        
        # NEW: Post-Phase-5 alignment check
        if self.is_post_phase_5():
            alignment = self.alignment_check()
            
            # Fail if misaligned
            if alignment['alignment_score'] < 100:
                result.status = OrchestratorStatus.FAILED
                result.message = f"Scaffolding alignment drift: {alignment['alignment_score']}%"
                result.recommendations = alignment['failed_checks']
        
        return result
```

---

### Phase 5E: Verification Suite (AC-CLEAN-325-328)

#### Objective
Comprehensive validation that CORTEX is permanently scaffolding-free.

#### Implementation

```python
class Phase5VerificationSuite:
    """
    Final verification that Phase 5 cleanup succeeded.
    
    Comprehensive test suite ensuring:
    1. All references removed
    2. Archive created + isolated
    3. Features flags working
    4. Performance baseline met
    5. Documentation updated
    """
    
    def verify_scaffolding_free(self) -> VerificationReport:
        """
        Execute all Phase 5 verification checks.
        
        Returns comprehensive report with:
        - Reference audit (grep results)
        - Archive integrity (checksums, size)
        - Feature flag verification
        - Performance baseline
        - Documentation audit
        """
        
        report = VerificationReport(
            phase='5',
            timestamp=datetime.now(),
            checks=[]
        )
        
        # Check 1: Zero phase references
        check_1 = self._verify_zero_references()
        report.checks.append(check_1)
        
        # Check 2: Archive integrity
        check_2 = self._verify_archive_integrity()
        report.checks.append(check_2)
        
        # Check 3: Feature flags
        check_3 = self._verify_feature_flags()
        report.checks.append(check_3)
        
        # Check 4: Performance
        check_4 = self._verify_performance_baseline()
        report.checks.append(check_4)
        
        # Check 5: Documentation
        check_5 = self._verify_documentation()
        report.checks.append(check_5)
        
        # Overall status
        report.overall_status = 'PASS' if all(c.passed for c in report.checks) else 'FAIL'
        report.certification = (
            'CORTEX 6.0 Cleanup Phase certified complete' 
            if report.overall_status == 'PASS'
            else 'Phase 5 verification failed - review checks'
        )
        
        return report
```

---

## 3. Continuous Alignment: Housekeeping Integration

### The Enforcement Loop

```
Every GitHub Copilot Turn:
  ├─ MasterOrchestrator executes user intent
  ├─ Updates progress-tracker.json
  └─ TRIGGERS HousekeepingOrchestrator (auto)
      ├─ [NEW] Phase 5 alignment_check() runs
      │   ├─ Scan: zero phase refs?
      │   ├─ Verify: archive isolated?
      │   ├─ Check: feature flags correct?
      │   ├─ Validate: config aligned?
      │   └─ Report: alignment score (0-100%)
      ├─ If alignment < 100%:
      │   ├─ LOG WARNING to audit
      │   ├─ SUGGEST FIXES in output
      │   └─ Block high-risk operations until fixed
      └─ Continue normal housekeeping
```

### Key Features

**1. Automatic Detection (AC-CLEAN-319)**
- Runs on every turn (no manual invocation)
- Detects re-introduction of phase logic
- Flags drift immediately

**2. Pre-Commit Hooks (AC-CLEAN-320)**
```bash
# .git/hooks/pre-commit
if grep -r '\bphase[_\s]*[1-5]' src/ --include='*.py'; then
    echo "❌ Phase references detected - commit blocked"
    echo "   Override with: git commit --no-verify (logs to audit)"
    exit 1
fi
```

**3. Continuous Validation (AC-CLEAN-321)**
- Every `python3 -m src.main` call triggers alignment check
- Alignment score logged to audit trail
- Serves as historical record of scaffolding removal success

**4. Archive Protection (AC-CLEAN-322)**
```python
# Archive directory never imported at runtime
archive_dir = Path("cortex-brain/documents/archives/CORTEX-6.0-construction")

# Read-only enforcement
for file_path in archive_dir.rglob("*"):
    if file_path.is_file():
        os.chmod(file_path, 0o444)  # Read-only
```

---

## 4. Implementation Timeline

| Week | Task | AC-IDs | Owner |
|------|------|--------|-------|
| W1 | Reference removal + extraction | AC-CLEAN-301-306 | TDD-Master |
| W1-W2 | Artifact decommission + archiving | AC-CLEAN-307-312 | Vacuum Orch |
| W2 | Configuration cleanup | AC-CLEAN-313-318 | GovernanceMerger |
| W2 | Housekeeping enhancement | AC-CLEAN-319-324 | Housekeeping |
| W2 | Verification suite | AC-CLEAN-325-328 | Validation |

---

## 5. Success Criteria

✅ **Reference Removal:** 100% of phase 1-5 hardcodes removed from src/

✅ **Artifact Decommission:** cx6-plan/ fully archived + deleted

✅ **Configuration Cleanup:** Zero cx6-plan references in YAML configs

✅ **Housekeeping Enforcement:** Alignment checks running + 100% passing

✅ **Verification:** All 4 verification checks passing (references, archive, flags, perf)

✅ **Certification:** Phase 5 completion certified

---

## 6. Risk Mitigation

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Breaking phase-dependent code | HIGH | Feature flags maintain compatibility |
| Archive corruption | MEDIUM | Checksum validation + versioning |
| Configuration conflicts | MEDIUM | Pre-cleanup config backup |
| Performance regression | LOW | Baseline comparison (target: <1%) |
| Incomplete reference removal | HIGH | Multiple grep passes + manual audit |

---

## 7. Deliverables

| Deliverable | Location | Owner |
|-------------|----------|-------|
| ScaffoldingRemovalOrchestrator | src/orchestrators/vacuum/ | TDD-Master |
| HousekeepingOrchestratorV3 | src/orchestrators/housekeeping/ | Enhancement |
| Phase5VerificationSuite | tests/phase5/ | QA |
| Archive (cx6-plan) | cortex-brain/documents/archives/ | Vacuum |
| Alignment Report | cortex-brain/documents/ | Housekeeping |
| Certification Document | cortex-brain/documents/ | Lead |

---

## Appendix: Feature Flag Pattern

```python
# src/config/feature_flags.py

class FeatureFlags:
    """Feature flags for backward compatibility during Phase 5 transition"""
    
    # Post-Phase-5: Planning scaffolding optional
    INCLUDE_PLANNING_SCAFFOLDING = os.getenv(
        'CORTEX_INCLUDE_PLANNING_SCAFFOLDING',
        'false'  # Default: disabled (permanent ops only)
    ).lower() == 'true'

# Usage in code:
if FeatureFlags.INCLUDE_PLANNING_SCAFFOLDING:
    # Only import planning modules if flag enabled
    from src.planning_modules import LifecyclePhaseManager, PlanningValidator
else:
    # Permanent operations use module-based architecture
    pass
```

---

**Ready for Phase 5 implementation!** 🚀

All 28 AC-IDs (AC-CLEAN-301-328) defined with full specifications, success criteria, and integration points.

