# Phase 12: Vacuum Orchestrator

**🔗 Breadcrumb:** [← Back to Master Plan](cortex-3.9-master.md)

**Status:** ⏳ Pending  
**Phase ID:** 12  
**Estimated Time:** 3 hours (180 minutes)  
**Actual Start:** -  
**Actual End:** -  
**Actual Work Time:** -  
**Dependencies:** Phase 08 (AST Engine Wrapper) ⏳, Phase 09 (Enhanced Analyzers) ⏳, Phase 15 (Version Manager) ✅  
**Blocks:** Phase 06 (Maintenance Orchestrator 3.0), Phase 16 (Integration & Validation)

---

## 🎯 Phase Objective

Create standalone Vacuum Orchestrator for deep codebase cleanup using AST-powered similarity detection, orphaned code removal, and automated housekeeping tasks.

**Success Criteria:**
- ✅ Standalone orchestrator with 5-phase workflow
- ✅ AST-powered duplicate code detection and removal
- ✅ Orphaned test file identification and cleanup
- ✅ Unused import removal across codebase
- ✅ Dead code detection and elimination
- ✅ Dry-run mode with detailed preview
- ✅ Version synchronization from cortex.config.json
- ✅ 100% test coverage with passing tests

---

## 🏗️ Implementation Plan

### Task 1: Vacuum Orchestrator Core (1.5 hours)

**Create `src/operations/modules/orchestration/vacuum_orchestrator.py`:**

```python
"""
Vacuum Orchestrator - Deep codebase cleanup with AST intelligence.

Performs comprehensive cleanup operations using semantic analysis
to identify and remove duplicates, orphaned code, and dead code.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

from ..analysis.ast_engine import ASTEngine
from ..analysis.deduplication_analyzer import DeduplicationAnalyzer
from ..version.version_manager import get_version_manager
from ...decorators.progress import track_progress

logger = logging.getLogger(__name__)

@dataclass
class VacuumResult:
    """Results of vacuum operation."""
    phase: str
    items_found: int
    items_removed: int
    dry_run: bool
    details: List[str]

class VacuumOrchestrator:
    """Orchestrate deep codebase cleanup operations."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.ast_engine = ASTEngine(self.project_root)
        self.dedup_analyzer = DeduplicationAnalyzer(self.ast_engine)
        
        # Version management
        self.version_manager = get_version_manager()
        self.version_manager.register_orchestrator_version("vacuum_orchestrator", "1.0")
        self.version = self.version_manager.get_orchestrator_version("vacuum_orchestrator")
        
        # Vacuum phases
        self.phases = [
            "duplicate_detection",
            "orphaned_tests",
            "unused_imports",
            "dead_code",
            "finalization"
        ]
        
        self.metrics = {
            'phases_completed': [],
            'items_found': 0,
            'items_removed': 0,
            'dry_run': True,
            'errors': []
        }
        
    @track_progress("vacuum_operation")
    async def execute(
        self,
        targets: List[str] = None,
        dry_run: bool = True,
        similarity_threshold: float = 0.85
    ) -> Dict[str, Any]:
        """
        Execute vacuum cleanup operation.
        
        Args:
            targets: Specific cleanup targets or None for all
            dry_run: If True, preview changes without applying
            similarity_threshold: Minimum similarity for duplicates
            
        Returns:
            Operation results with metrics
        """
        logger.info(f"🎭 Orchestrator engaged: VacuumOrchestrator v{self.version}")
        logger.info(f"Dry run: {dry_run}, Targets: {targets or 'all'}")
        
        self.metrics['dry_run'] = dry_run
        
        targets = targets or [
            "duplicate_code",
            "orphaned_tests",
            "unused_imports",
            "dead_code"
        ]
        
        results = []
        
        try:
            # Phase 1: Duplicate Detection
            if "duplicate_code" in targets:
                logger.info("🎭 Phase transition: START → duplicate_detection")
                dup_result = await self._run_duplicate_detection_phase(
                    similarity_threshold,
                    dry_run
                )
                results.append(dup_result)
                self.metrics['phases_completed'].append('duplicate_detection')
                
            # Phase 2: Orphaned Tests
            if "orphaned_tests" in targets:
                logger.info("🎭 Phase transition: duplicate_detection → orphaned_tests")
                orphan_result = await self._run_orphaned_tests_phase(dry_run)
                results.append(orphan_result)
                self.metrics['phases_completed'].append('orphaned_tests')
                
            # Phase 3: Unused Imports
            if "unused_imports" in targets:
                logger.info("🎭 Phase transition: orphaned_tests → unused_imports")
                import_result = await self._run_unused_imports_phase(dry_run)
                results.append(import_result)
                self.metrics['phases_completed'].append('unused_imports')
                
            # Phase 4: Dead Code
            if "dead_code" in targets:
                logger.info("🎭 Phase transition: unused_imports → dead_code")
                dead_code_result = await self._run_dead_code_phase(dry_run)
                results.append(dead_code_result)
                self.metrics['phases_completed'].append('dead_code')
                
            # Phase 5: Finalization
            logger.info("🎭 Phase transition: dead_code → finalization")
            self._finalize_vacuum(results, dry_run)
            self.metrics['phases_completed'].append('finalization')
            
            success = True
            is_complete = success and len(self.metrics['errors']) == 0
            
            logger.info(
                f"🎭 Orchestrator completing: "
                f"{'✅ ALL WORK COMPLETE' if is_complete else '⏳ PHASES DONE WITH WARNINGS'}"
            )
            
            return {
                'success': success,
                'results': results,
                'metrics': self.metrics,
                'is_complete': is_complete
            }
            
        except Exception as e:
            logger.error(f"Vacuum operation failed: {e}", exc_info=True)
            self.metrics['errors'].append(str(e))
            return {
                'success': False,
                'error': str(e),
                'metrics': self.metrics,
                'is_complete': False
            }
            
    async def _run_duplicate_detection_phase(
        self,
        threshold: float,
        dry_run: bool
    ) -> VacuumResult:
        """Phase 1: Detect and remove duplicate code."""
        logger.info(f"Detecting duplicates (threshold: {threshold})")
        
        analysis = self.dedup_analyzer.analyze()
        duplicate_groups = analysis['duplicate_groups']
        
        items_removed = 0
        details = []
        
        for group in duplicate_groups:
            locations = group.locations
            details.append(
                f"Duplicate ({group.similarity_score:.2%}): "
                f"{len(locations)} instances, {group.lines_count} lines"
            )
            
            if not dry_run and len(locations) > 1:
                # Keep first instance, remove rest
                for loc in locations[1:]:
                    self._remove_code_block(loc)
                    items_removed += 1
                    
        self.metrics['items_found'] += len(duplicate_groups)
        self.metrics['items_removed'] += items_removed
        
        return VacuumResult(
            phase="duplicate_detection",
            items_found=len(duplicate_groups),
            items_removed=items_removed,
            dry_run=dry_run,
            details=details
        )
        
    async def _run_orphaned_tests_phase(self, dry_run: bool) -> VacuumResult:
        """Phase 2: Detect and remove orphaned test files."""
        logger.info("Detecting orphaned tests")
        
        orphaned_tests = self.ast_engine.find_orphaned_tests()
        
        items_removed = 0
        details = []
        
        for test_path in orphaned_tests:
            details.append(f"Orphaned test: {test_path}")
            
            if not dry_run:
                test_path.unlink()
                items_removed += 1
                
        self.metrics['items_found'] += len(orphaned_tests)
        self.metrics['items_removed'] += items_removed
        
        return VacuumResult(
            phase="orphaned_tests",
            items_found=len(orphaned_tests),
            items_removed=items_removed,
            dry_run=dry_run,
            details=details
        )
        
    async def _run_unused_imports_phase(self, dry_run: bool) -> VacuumResult:
        """Phase 3: Remove unused imports."""
        logger.info("Cleaning unused imports")
        
        if dry_run:
            # AST engine returns count for dry run
            count = self.ast_engine.remove_unused_imports(exclude_patterns=["__init__.py"])
            items_removed = 0
        else:
            items_removed = self.ast_engine.remove_unused_imports(exclude_patterns=["__init__.py"])
            count = items_removed
            
        details = [f"Unused imports: {count} found"]
        
        self.metrics['items_found'] += count
        self.metrics['items_removed'] += items_removed
        
        return VacuumResult(
            phase="unused_imports",
            items_found=count,
            items_removed=items_removed,
            dry_run=dry_run,
            details=details
        )
        
    async def _run_dead_code_phase(self, dry_run: bool) -> VacuumResult:
        """Phase 4: Detect and remove dead code."""
        logger.info("Detecting dead code")
        
        # Identify unreferenced functions/classes
        dead_code_items = self._detect_dead_code()
        
        items_removed = 0
        details = []
        
        for item in dead_code_items:
            details.append(f"Dead code: {item['type']} {item['name']} in {item['file']}")
            
            if not dry_run:
                self._remove_dead_code_item(item)
                items_removed += 1
                
        self.metrics['items_found'] += len(dead_code_items)
        self.metrics['items_removed'] += items_removed
        
        return VacuumResult(
            phase="dead_code",
            items_found=len(dead_code_items),
            items_removed=items_removed,
            dry_run=dry_run,
            details=details
        )
        
    def _detect_dead_code(self) -> List[Dict[str, Any]]:
        """Detect unreferenced functions and classes."""
        # Use AST engine to find definitions with zero references
        arch = self.ast_engine.analyze_architecture()
        
        # Simplified - actual implementation would use reference counting
        return []  # Placeholder
        
    def _finalize_vacuum(self, results: List[VacuumResult], dry_run: bool):
        """Phase 5: Finalize vacuum operation."""
        total_found = sum(r.items_found for r in results)
        total_removed = sum(r.items_removed for r in results)
        
        if dry_run:
            logger.info(
                f"Vacuum preview: {total_found} items identified, "
                f"{total_removed} would be removed"
            )
        else:
            logger.info(
                f"Vacuum complete: {total_removed} items removed from codebase"
            )
```

### Task 2: Similarity Detection Engine (1 hour)

**Enhanced AST similarity comparison:**

```python
def calculate_ast_similarity(tree1: ast.AST, tree2: ast.AST) -> float:
    """
    Calculate structural similarity between two AST trees.
    
    Uses tree edit distance and structural hashing for comparison.
    
    Returns:
        Similarity score (0.0 to 1.0)
    """
    # Normalize ASTs (remove variable names, retain structure)
    norm_tree1 = normalize_ast(tree1)
    norm_tree2 = normalize_ast(tree2)
    
    # Calculate structural hash
    hash1 = structural_hash(norm_tree1)
    hash2 = structural_hash(norm_tree2)
    
    if hash1 == hash2:
        return 1.0
        
    # Calculate tree edit distance for partial matches
    edit_distance = calculate_tree_edit_distance(norm_tree1, norm_tree2)
    max_size = max(ast_node_count(norm_tree1), ast_node_count(norm_tree2))
    
    similarity = 1.0 - (edit_distance / max_size)
    
    return max(0.0, min(1.0, similarity))
```

### Task 3: Dry-Run Preview (30 min)

**Preview changes before applying:**

```python
def generate_preview_report(results: List[VacuumResult]) -> str:
    """Generate detailed preview report for dry-run mode."""
    lines = ["# Vacuum Operation Preview\n"]
    lines.append("## Summary\n")
    
    total_found = sum(r.items_found for r in results)
    total_would_remove = sum(r.items_removed for r in results)
    
    lines.append(f"**Total Items Found:** {total_found}")
    lines.append(f"**Items to Remove:** {total_would_remove}\n")
    
    for result in results:
        lines.append(f"### {result.phase.replace('_', ' ').title()}\n")
        lines.append(f"- Found: {result.items_found}")
        lines.append(f"- Would Remove: {result.items_removed}\n")
        
        if result.details:
            lines.append("**Details:**")
            for detail in result.details[:10]:  # Limit to 10 items
                lines.append(f"- {detail}")
            if len(result.details) > 10:
                lines.append(f"- ... and {len(result.details) - 10} more\n")
                
    lines.append("\n---\n")
    lines.append("**To execute cleanup:** Re-run with `dry_run=False`")
    
    return "\n".join(lines)
```

---

## 📦 Expected Deliverables

### Code Deliverables
- ✅ `src/operations/modules/orchestration/vacuum_orchestrator.py`
- ✅ AST similarity detection engine
- ✅ Dry-run preview generator
- ✅ Version synchronization integration

### Test Deliverables
- ✅ `tests/test_vacuum_orchestrator.py`
  - Duplicate detection tests
  - Orphaned test identification tests
  - Dry-run mode tests
  - Integration tests with real code samples
- ✅ Similarity algorithm validation tests

### Documentation Deliverables
- ✅ Vacuum orchestrator usage guide
- ✅ Similarity threshold tuning guide
- ✅ Dry-run best practices
- ✅ Safe cleanup guidelines

---

## 🔄 Next Steps

1. **Phase 08-09 Completion:** AST Engine and analyzers must be operational
2. **Threshold Tuning:** Calibrate similarity threshold (0.85 default)
3. **Safety Testing:** Validate dry-run prevents unwanted deletions
4. **Integration:** Connect to Phase 06 (Maintenance Orchestrator)

---

## 🔗 Integration Points

### Upstream Dependencies
- **AST Engine (Phase 08):** Semantic analysis capabilities
- **Deduplication Analyzer (Phase 09):** Duplicate detection
- **Version Manager (Phase 15):** Version synchronization

### Downstream Consumers
- **Maintenance Orchestrator (Phase 06):** Automatic vacuum phase
- **Planning Orchestrator (Phase 03):** Tier 3/4 cleanup invocation
- **Refactor Cycle (Phase 13):** Post-refactor cleanup

---

## 🚨 Risk Mitigation

### Risk 1: False Positive Deletions
**Mitigation:**
- MANDATORY dry-run mode by default
- Conservative similarity threshold (0.85)
- Manual review gate before execution
- Git checkpoint creation before cleanup

### Risk 2: Breaking Working Code
**Mitigation:**
- Exclude __init__.py from import cleanup
- Test suite execution before/after cleanup
- Rollback mechanism via git

### Risk 3: Performance on Large Codebases
**Mitigation:**
- Implement timeout limits (10-minute max)
- Progress indicators for long operations
- Incremental cleanup (target specific directories)

---

## 📊 Success Metrics

- ✅ Duplicate detection accuracy ≥90%
- ✅ Zero false positive orphaned test deletions
- ✅ Unused import cleanup reduces files by 5-10%
- ✅ Vacuum operation completes in <10 minutes for CORTEX
- ✅ Dry-run preview shows 100% of planned changes
- ✅ Manual cleanup effort reduced by 80%

---

**Phase Owner:** Asif Hussain  
**Phase Status:** ⏳ Awaiting Phase 08-09 completion  
**Last Updated:** 2024-12-14
