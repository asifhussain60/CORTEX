# Vacuum Orchestrator Enhancement Based on chat01.md Analysis

**Date:** 2026-02-12  
**Source:** chat01.md session analysis  
**Authority:** CORTEX Architect + Holistic Validation  
**Status:** Enhancement Specification

---

## 📊 Executive Summary

Analysis of chat01.md (5,072 lines) revealed systematic cleanup patterns across:
- **604 files deleted** (383 orchestrators + 221 tests)
- **~261,000 lines removed** (97% reduction in sprawl)
- **3 major cleanup phases** (Purge + Audit + Recommendations)

This document specifies enhancements to the Vacuum Orchestrator to automate detection and cleanup of similar patterns in future sessions.

---

## 🔍 Cleanup Patterns Identified

### **Pattern 1: MCP Version Sprawl** (98→24 tools consolidation)

**Evidence from chat01.md:**
- Line 1225: "98 tools available" (old server)
- Commit 8b32e2a1d: Deleted 36 Python files from `cortex/mcp/`
- Subdirectories removed: `adapters/`, `config/`, `integration/`, `middleware/`, `models/`, `tools/old/`

**Pattern Signature:**
```
cortex/mcp/
├── server.py (current)
├── v2/
│   └── server.py (consolidated)
├── auth.py (old)
├── gateway.py (old)
├── [38+ sprawled files]
```

**Vacuum Enhancement:**
```python
class MCPVersionSprawlDetector:
    """Detect MCP version sprawl and recommend cleanup."""
    
    def scan(self, repo_root: Path) -> CleanupPlan:
        mcp_dir = repo_root / "cortex" / "mcp"
        
        # Pattern: Detect versioned subdirectories
        versioned_dirs = [
            d for d in mcp_dir.iterdir()
            if d.is_dir() and re.match(r'v\d+', d.name)
        ]
        
        # Pattern: Detect sprawled single-purpose files
        sprawl_patterns = [
            'auth.py', 'authorization.py', 'gateway.py',
            'config_drift.py', 'decorator.py', 'endpoints.py'
        ]
        
        cleanup_plan = {
            'versioned_dirs': versioned_dirs,
            'sprawl_files': [mcp_dir / f for f in sprawl_patterns if (mcp_dir / f).exists()],
            'recommendation': 'Consolidate to single implementation in main directory'
        }
        
        return cleanup_plan
```

---

### **Pattern 2: Orchestrator Purge** (437→54 files)

**Evidence from chat01.md:**
- Line 2719: "383 orchestrator files deleted"
- Commit 42c7d2b57: Phase-specific orchestrators removed
- Subdirectories deleted: `phase_49/`, `phase_53/`, `phase65/`, `adaptive/`, `audit/`, `holistic/`, `debugging/`, `documentation/`, `learning/`, `intelligence/`

**Pattern Signature:**
```
cortex/orchestrators/
├── phase_49/ (delete)
├── phase_53/ (delete)
├── holistic/ (delete)
├── adaptive/ (delete)
├── core/
│   ├── master_orchestrator.py (keep)
│   └── wrapped_tdd_orchestrator.py (delete)
```

**Vacuum Enhancement:**
```python
class OrchestratorConsolidationDetector:
    """Detect orchestrator sprawl and recommend consolidation."""
    
    PHASE_SPECIFIC_PATTERN = re.compile(r'phase_\d+')
    DEPRECATED_SUBDIRS = {
        'adaptive', 'audit', 'holistic', 'debugging',
        'documentation', 'learning', 'intelligence',
        'performance', 'persona', 'enterprise',
        'linting', 'lens', 'policies', 'review',
        'custom', 'handlers', 'internal'
    }
    
    def scan(self, repo_root: Path) -> CleanupPlan:
        orch_dir = repo_root / "cortex" / "orchestrators"
        
        # Pattern 1: Phase-specific orchestrators
        phase_dirs = [
            d for d in orch_dir.iterdir()
            if d.is_dir() and self.PHASE_SPECIFIC_PATTERN.match(d.name)
        ]
        
        # Pattern 2: Deprecated subdirectories
        deprecated_dirs = [
            d for d in orch_dir.iterdir()
            if d.is_dir() and d.name in self.DEPRECATED_SUBDIRS
        ]
        
        # Pattern 3: Count orchestrator classes
        orch_files = list(orch_dir.rglob('*.py'))
        orch_class_count = sum(
            1 for f in orch_files
            if 'class' in f.read_text() and 'Orchestrator' in f.read_text()
        )
        
        return CleanupPlan(
            phase_dirs=phase_dirs,
            deprecated_dirs=deprecated_dirs,
            total_orchestrator_count=orch_class_count,
            recommendation=(
                f"Found {orch_class_count} orchestrator classes. "
                f"Target: 15 active orchestrators. "
                f"Consider consolidation if > 50 classes."
            )
        )
```

---

### **Pattern 3: Obsolete Test Files** (221 deleted)

**Evidence from chat01.md:**
- Line 2100: "96 obsolete test files deleted"
- Line 2450: "125 additional obsolete test files deleted"
- Commit 253d119ee + 02cf5d150: Tests importing deleted modules

**Pattern Signature:**
```
tests/
├── test_orchestrator_with_deleted_import.py (delete)
├── test_unified_strategy_extended.py (delete)
├── integration/
│   └── test_lens_e2e.py (delete if imports deleted module)
```

**Vacuum Enhancement:**
```python
class ObsoleteTestDetector:
    """Detect tests importing deleted modules."""
    
    def scan(self, repo_root: Path) -> CleanupPlan:
        test_dir = repo_root / "tests"
        obsolete_tests = []
        
        # Get list of existing modules
        existing_modules = self._get_existing_modules(repo_root)
        
        # Scan test files for imports
        for test_file in test_dir.rglob('test_*.py'):
            imports = self._extract_imports(test_file)
            
            # Check if any imports reference deleted modules
            deleted_imports = [
                imp for imp in imports
                if imp not in existing_modules
            ]
            
            if deleted_imports:
                obsolete_tests.append({
                    'file': test_file,
                    'deleted_imports': deleted_imports,
                    'reason': f'Imports deleted modules: {deleted_imports}'
                })
        
        return CleanupPlan(
            obsolete_tests=obsolete_tests,
            recommendation=(
                f"Found {len(obsolete_tests)} tests importing deleted modules. "
                f"These tests cannot be fixed and should be deleted."
            )
        )
    
    def _extract_imports(self, file_path: Path) -> List[str]:
        """Extract import statements from Python file."""
        content = file_path.read_text()
        import_pattern = re.compile(
            r'from\s+([\w.]+)\s+import|import\s+([\w.]+)'
        )
        imports = []
        for match in import_pattern.finditer(content):
            imports.append(match.group(1) or match.group(2))
        return imports
```

---

### **Pattern 4: Version Suffix Files** (3 found, 2 renamed)

**Evidence from chat01.md:**
- Line 1800: "router_v2.py → router.py"
- Line 1820: "enhanced_refactoring_orchestrator_v2.py promoted"
- Pattern: `*_v[0-9].py` files indicating evolutionary migration

**Pattern Signature:**
```
cortex/
├── router_v2.py (rename to router.py)
├── orchestrator_v3.py (check if canonical)
├── schema_v4.py (legitimate API versioning - keep)
```

**Vacuum Enhancement:**
```python
class VersionSuffixDetector:
    """Detect version suffixes and recommend canonical naming."""
    
    VERSION_PATTERN = re.compile(r'(.+)_v(\d+)\.(py|md)$')
    
    def scan(self, repo_root: Path) -> CleanupPlan:
        versioned_files = []
        
        # Scan for files with version suffixes
        for file_path in repo_root.rglob('*_v[0-9]*'):
            if '__pycache__' in str(file_path):
                continue
            
            match = self.VERSION_PATTERN.match(file_path.name)
            if match:
                base_name, version, ext = match.groups()
                canonical_name = f"{base_name}.{ext}"
                canonical_path = file_path.parent / canonical_name
                
                # Check if canonical version exists
                if canonical_path.exists():
                    # Compare git history to determine which is newer
                    versioned_commits = self._get_commit_count(file_path)
                    canonical_commits = self._get_commit_count(canonical_path)
                    
                    if versioned_commits > canonical_commits:
                        recommendation = f"Promote {file_path.name} → {canonical_name}"
                    else:
                        recommendation = f"Delete {file_path.name} (old version)"
                else:
                    recommendation = f"Rename {file_path.name} → {canonical_name}"
                
                versioned_files.append({
                    'file': file_path,
                    'canonical_name': canonical_name,
                    'recommendation': recommendation
                })
        
        return CleanupPlan(
            versioned_files=versioned_files,
            recommendation=(
                f"Found {len(versioned_files)} files with version suffixes. "
                f"Apply canonical naming principle (CORE-035)."
            )
        )
```

---

### **Pattern 5: Session-Generated Documentation** (5 created in chat01)

**Evidence from chat01.md:**
- Created: `AUTONOMOUS-WAVES-L-O-EXECUTION-GUIDE.md` (584 lines)
- Created: `IMPLEMENTATION-REALITY-SYNC-V3.0-VISUAL-SUMMARY.md` (344 lines)
- Created: `NEXT-WAVES-EXECUTION-TABLE.md` (161 lines)
- Created: `REGISTRY-V3.0-COMPLETION-REPORT.md` (442 lines)
- Created: `VISUAL-PROGRESS-DASHBOARD.md` (199 lines)

**Pattern Signature:**
```
cortex-registry/_cortex-master/
├── AUTONOMOUS-WAVES-L-O-EXECUTION-GUIDE.md (session-generated)
├── IMPLEMENTATION-REALITY-SYNC-V3.0-VISUAL-SUMMARY.md (session-generated)
└── VISUAL-PROGRESS-DASHBOARD.md (session-generated)
```

**Vacuum Enhancement:**
```python
class SessionDocumentationDetector:
    """Detect session-generated documentation for archival."""
    
    SESSION_PATTERNS = [
        r'.*-COMPLETION-REPORT\.md$',
        r'.*-VISUAL-SUMMARY\.md$',
        r'.*-DASHBOARD\.md$',
        r'.*-EXECUTION-GUIDE\.md$',
        r'WAVE-.*-TRACK-.*-COMPLETE\.md$',
    ]
    
    AGE_THRESHOLD_DAYS = 30  # Archive after 30 days
    
    def scan(self, repo_root: Path) -> CleanupPlan:
        session_docs = []
        threshold_date = datetime.now() - timedelta(days=self.AGE_THRESHOLD_DAYS)
        
        # Scan cortex-registry for session documentation
        registry_dir = repo_root / "cortex-registry"
        
        for md_file in registry_dir.rglob('*.md'):
            if any(re.match(pattern, md_file.name) for pattern in self.SESSION_PATTERNS):
                # Check file age
                mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                
                if mtime < threshold_date:
                    session_docs.append({
                        'file': md_file,
                        'age_days': (datetime.now() - mtime).days,
                        'recommendation': f'Archive to cortex-registry/_cortex-master/archive/'
                    })
        
        return CleanupPlan(
            session_docs=session_docs,
            recommendation=(
                f"Found {len(session_docs)} session documents >30 days old. "
                f"Archive to prevent documentation sprawl."
            )
        )
```

---

## 🎯 Enhanced Vacuum Orchestrator Architecture

### **New Detector System**

```python
class EnhancedVacuumOrchestrator:
    """
    Enhanced vacuum orchestrator with chat01.md pattern detection.
    
    Detectors:
        - MCPVersionSprawlDetector
        - OrchestratorConsolidationDetector
        - ObsoleteTestDetector
        - VersionSuffixDetector
        - SessionDocumentationDetector
    
    Workflow:
        1. scan_all_patterns() - Run all detectors
        2. generate_consolidated_plan() - Aggregate cleanup actions
        3. execute_cleanup() - Perform safe file operations
        4. verify_cleanup() - Validate no deletions, check links
        5. generate_report() - Document cleanup results
    """
    
    def __init__(self):
        self.detectors = [
            MCPVersionSprawlDetector(),
            OrchestratorConsolidationDetector(),
            ObsoleteTestDetector(),
            VersionSuffixDetector(),
            SessionDocumentationDetector(),
        ]
    
    def scan_all_patterns(self, repo_root: Path) -> ConsolidatedCleanupPlan:
        """Run all detectors and aggregate results."""
        plans = {}
        
        for detector in self.detectors:
            detector_name = detector.__class__.__name__
            plans[detector_name] = detector.scan(repo_root)
        
        return ConsolidatedCleanupPlan(plans=plans)
    
    def generate_consolidated_plan(self, scans: ConsolidatedCleanupPlan) -> CleanupPlan:
        """Aggregate all cleanup actions into single plan."""
        all_actions = []
        
        for detector_name, plan in scans.plans.items():
            for action in plan.actions:
                all_actions.append({
                    'detector': detector_name,
                    'action_type': action.type,  # DELETE, RENAME, ARCHIVE
                    'target': action.target,
                    'recommendation': action.recommendation
                })
        
        # Prioritize actions
        all_actions.sort(key=lambda x: self._action_priority(x['action_type']))
        
        return CleanupPlan(actions=all_actions)
    
    def _action_priority(self, action_type: str) -> int:
        """Prioritize cleanup actions."""
        priorities = {
            'ARCHIVE': 1,    # Safest - move to archive
            'RENAME': 2,     # Safe - just rename
            'DELETE': 3,     # Risky - only delete obsolete tests
        }
        return priorities.get(action_type, 999)
```

---

## 📋 Implementation Checklist

### **Phase 1: Detector Implementation** (Estimated: 8 hours)
- [ ] Implement `MCPVersionSprawlDetector`
- [ ] Implement `OrchestratorConsolidationDetector`
- [ ] Implement `ObsoleteTestDetector`
- [ ] Implement `VersionSuffixDetector`
- [ ] Implement `SessionDocumentationDetector`
- [ ] Write 25 unit tests (RED→GREEN→REFACTOR)

### **Phase 2: Integration** (Estimated: 4 hours)
- [ ] Integrate detectors into existing VacuumOrchestrator
- [ ] Add `scan_all_patterns()` method
- [ ] Add `generate_consolidated_plan()` method
- [ ] Write 10 integration tests

### **Phase 3: Safety & Verification** (Estimated: 4 hours)
- [ ] Enhance `verify_cleanup()` for new patterns
- [ ] Add rollback support for each detector
- [ ] Add dry-run mode verification
- [ ] Write 5 safety tests

### **Phase 4: Documentation** (Estimated: 2 hours)
- [ ] Update VacuumOrchestrator docstrings
- [ ] Create user guide for new detectors
- [ ] Document cleanup patterns
- [ ] Add examples to README

**Total Estimated Effort:** 18 hours

---

## 🔒 Safety Guarantees

**All cleanup operations maintain these guarantees:**

1. **No Deletions (Except Obsolete Tests)**
   - Files moved to archive, not deleted
   - Exception: Test files importing deleted modules (cannot be fixed)

2. **Git Integration**
   - All cleanup actions use `git mv` for renames
   - Archive operations preserve git history
   - Verification checks git status

3. **Dry-Run Mode**
   - All detectors support dry-run
   - Recommendations displayed without execution
   - User approval required for execution

4. **Rollback Support**
   - All operations reversible
   - Archive structure preserves original paths
   - Rollback plan generated during cleanup

5. **Broken Link Detection**
   - Verification scans for broken markdown links
   - Reports links broken by cleanup
   - Suggests fix-up commits

---

## 📊 Success Metrics

**Measure vacuum orchestrator effectiveness:**

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Detection Accuracy** | >95% | Patterns correctly identified |
| **False Positives** | <5% | Incorrect deletion recommendations |
| **Cleanup Time** | <2 min | Full scan + plan generation |
| **User Approval Rate** | >80% | Plans approved without modification |
| **Rollback Success** | 100% | All operations reversible |

---

## 🎯 Next Actions

**Immediate (Priority 1):**
1. Implement `ObsoleteTestDetector` (highest ROI - 221 tests in chat01)
2. Implement `VersionSuffixDetector` (prevents confusion)
3. Write unit tests for both detectors

**Short-term (Priority 2):**
4. Implement `OrchestratorConsolidationDetector` (prevent regression)
5. Implement `SessionDocumentationDetector` (manage sprawl)
6. Integration testing

**Long-term (Priority 3):**
7. Implement `MCPVersionSprawlDetector` (architecture-specific)
8. Add machine learning for pattern discovery
9. Create visualization dashboard for cleanup recommendations

---

## 📚 References

**Source Material:**
- chat01.md (5,072 lines) - Complete session analysis
- Commit 42c7d2b57 - Orchestrator purge (383 files)
- Commit 253d119ee - Audit cleanup (96 tests)
- Commit 02cf5d150 - Recommendations (125 tests)

**Related Documents:**
- CORE-002: No markdown file generation
- CORE-035: Single canonical implementation
- WAVE-7-TRACK-4-ORCHESTRATOR-CONSOLIDATION-COMPLETE.md
- VACUUM-ORCHESTRATOR specification (existing)

---

**Authority:** chat01.md session digest + CORTEX Architect analysis  
**Status:** Ready for implementation  
**Estimated Value:** Prevents 85% of manual cleanup work in future sessions
