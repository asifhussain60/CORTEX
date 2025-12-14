# Phase 13: Refactor Cycle Engine

**🔗 Breadcrumb:** [← Back to Master Plan](cortex-3.9-master.md)

**Status:** ⏳ Pending  
**Phase ID:** 13  
**Estimated Time:** 4 hours (240 minutes)  
**Actual Start:** -  
**Actual End:** -  
**Actual Work Time:** -  
**Dependencies:** Phase 08 (AST Engine Wrapper) ⏳, Phase 15 (Version Manager) ✅  
**Blocks:** Phase 03 (Planning Orchestrator 3.0), Phase 16 (Integration & Validation)

---

## 🎯 Phase Objective

Create automatic refactor cycle engine for code cleanup integrated into all Tier 3/4 planning operations, including comment synchronization, debug code removal, dead code elimination, and lint enforcement.

**Success Criteria:**
- ✅ Standalone refactor cycle orchestrator with 6-phase workflow
- ✅ Automatic comment update and synchronization
- ✅ Debug code removal (console.log, print, debugger statements)
- ✅ Dead code elimination using AST analysis
- ✅ Lint and format enforcement
- ✅ Multi-threaded Python utilities for performance
- ✅ Integration with Planning Orchestrator 3.0
- ✅ Version synchronization from cortex.config.json
- ✅ 100% test coverage with passing tests

---

## 🏗️ Implementation Plan

### Task 1: Refactor Cycle Orchestrator Core (2 hours)

**Create `src/operations/modules/orchestration/refactor_cycle_orchestrator.py`:**

```python
"""
Refactor Cycle Engine - Automatic code cleanup and quality enforcement.

Integrated into Planning System 3.0 for automatic code cleanup
during Tier 3/4 operations.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import ast
import re
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..analysis.ast_engine import ASTEngine
from ..version.version_manager import get_version_manager
from ...decorators.progress import track_progress

logger = logging.getLogger(__name__)

@dataclass
class RefactorResult:
    """Results of refactor operation."""
    phase: str
    files_processed: int
    changes_made: int
    issues_found: List[str]

class RefactorCycleOrchestrator:
    """Orchestrate automatic code cleanup and refactoring."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.ast_engine = ASTEngine(self.project_root)
        
        # Version management
        self.version_manager = get_version_manager()
        self.version_manager.register_orchestrator_version("refactor_cycle_orchestrator", "1.0")
        self.version = self.version_manager.get_orchestrator_version("refactor_cycle_orchestrator")
        
        # Refactor phases
        self.phases = [
            "comment_sync",
            "debug_removal",
            "dead_code",
            "lint_enforcement",
            "format_enforcement",
            "finalization"
        ]
        
        self.metrics = {
            'phases_completed': [],
            'files_processed': 0,
            'changes_made': 0,
            'errors': []
        }
        
        # Multi-threading config
        self.max_workers = 4
        
    @track_progress("refactor_cycle")
    async def execute(
        self,
        target_files: List[Path] = None,
        phases: List[str] = None
    ) -> Dict[str, Any]:
        """
        Execute refactor cycle.
        
        Args:
            target_files: Specific files to refactor or None for all
            phases: Specific phases to run or None for all
            
        Returns:
            Operation results with metrics
        """
        logger.info(f"🎭 Orchestrator engaged: RefactorCycleOrchestrator v{self.version}")
        
        phases = phases or self.phases
        target_files = target_files or list(self.project_root.rglob("*.py"))
        
        results = []
        
        try:
            # Phase 1: Comment Synchronization
            if "comment_sync" in phases:
                logger.info("🎭 Phase transition: START → comment_sync")
                comment_result = await self._run_comment_sync_phase(target_files)
                results.append(comment_result)
                self.metrics['phases_completed'].append('comment_sync')
                
            # Phase 2: Debug Code Removal
            if "debug_removal" in phases:
                logger.info("🎭 Phase transition: comment_sync → debug_removal")
                debug_result = await self._run_debug_removal_phase(target_files)
                results.append(debug_result)
                self.metrics['phases_completed'].append('debug_removal')
                
            # Phase 3: Dead Code Elimination
            if "dead_code" in phases:
                logger.info("🎭 Phase transition: debug_removal → dead_code")
                dead_code_result = await self._run_dead_code_phase(target_files)
                results.append(dead_code_result)
                self.metrics['phases_completed'].append('dead_code')
                
            # Phase 4: Lint Enforcement
            if "lint_enforcement" in phases:
                logger.info("🎭 Phase transition: dead_code → lint_enforcement")
                lint_result = await self._run_lint_phase(target_files)
                results.append(lint_result)
                self.metrics['phases_completed'].append('lint_enforcement')
                
            # Phase 5: Format Enforcement
            if "format_enforcement" in phases:
                logger.info("🎭 Phase transition: lint_enforcement → format_enforcement")
                format_result = await self._run_format_phase(target_files)
                results.append(format_result)
                self.metrics['phases_completed'].append('format_enforcement')
                
            # Phase 6: Finalization
            logger.info("🎭 Phase transition: format_enforcement → finalization")
            self._finalize_refactor(results)
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
            logger.error(f"Refactor cycle failed: {e}", exc_info=True)
            self.metrics['errors'].append(str(e))
            return {
                'success': False,
                'error': str(e),
                'metrics': self.metrics,
                'is_complete': False
            }
            
    async def _run_comment_sync_phase(self, files: List[Path]) -> RefactorResult:
        """Phase 1: Synchronize comments with code."""
        logger.info(f"Synchronizing comments in {len(files)} files")
        
        changes = 0
        issues = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._sync_file_comments, file): file
                for file in files
            }
            
            for future in as_completed(futures):
                file = futures[future]
                try:
                    file_changes = future.result()
                    changes += file_changes
                except Exception as e:
                    issues.append(f"Comment sync failed for {file}: {e}")
                    
        self.metrics['files_processed'] += len(files)
        self.metrics['changes_made'] += changes
        
        return RefactorResult(
            phase="comment_sync",
            files_processed=len(files),
            changes_made=changes,
            issues_found=issues
        )
        
    def _sync_file_comments(self, file_path: Path) -> int:
        """Synchronize comments in single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            # Check if docstrings match function signatures
            changes = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    docstring = ast.get_docstring(node)
                    if docstring:
                        # Validate docstring matches current signature
                        if not self._validate_docstring(node, docstring):
                            # Update docstring (simplified - actual implementation more complex)
                            changes += 1
                            
            return changes
            
        except Exception as e:
            logger.error(f"Failed to sync comments in {file_path}: {e}")
            return 0
            
    async def _run_debug_removal_phase(self, files: List[Path]) -> RefactorResult:
        """Phase 2: Remove debug statements."""
        logger.info(f"Removing debug code from {len(files)} files")
        
        debug_patterns = [
            r'print\s*\(',           # Python print
            r'console\.log\s*\(',    # JavaScript console.log
            r'debugger;',            # JavaScript debugger
            r'import pdb.*pdb\.set_trace\(\)',  # Python debugger
            r'breakpoint\(\)'        # Python breakpoint
        ]
        
        changes = 0
        issues = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._remove_debug_statements, file, debug_patterns): file
                for file in files
            }
            
            for future in as_completed(futures):
                file = futures[future]
                try:
                    file_changes = future.result()
                    changes += file_changes
                except Exception as e:
                    issues.append(f"Debug removal failed for {file}: {e}")
                    
        self.metrics['changes_made'] += changes
        
        return RefactorResult(
            phase="debug_removal",
            files_processed=len(files),
            changes_made=changes,
            issues_found=issues
        )
        
    def _remove_debug_statements(
        self, 
        file_path: Path,
        patterns: List[str]
    ) -> int:
        """Remove debug statements from single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_lines = content.split('\n')
            filtered_lines = []
            changes = 0
            
            for line in original_lines:
                # Check if line matches debug pattern
                is_debug = any(re.search(pattern, line) for pattern in patterns)
                
                if not is_debug:
                    filtered_lines.append(line)
                else:
                    changes += 1
                    
            if changes > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(filtered_lines))
                    
            return changes
            
        except Exception as e:
            logger.error(f"Failed to remove debug statements from {file_path}: {e}")
            return 0
            
    async def _run_dead_code_phase(self, files: List[Path]) -> RefactorResult:
        """Phase 3: Eliminate dead code."""
        logger.info(f"Eliminating dead code from {len(files)} files")
        
        # Use AST engine to find unreferenced functions/classes
        changes = 0
        issues = []
        
        for file in files:
            try:
                file_changes = self._remove_dead_code_from_file(file)
                changes += file_changes
            except Exception as e:
                issues.append(f"Dead code removal failed for {file}: {e}")
                
        self.metrics['changes_made'] += changes
        
        return RefactorResult(
            phase="dead_code",
            files_processed=len(files),
            changes_made=changes,
            issues_found=issues
        )
        
    def _remove_dead_code_from_file(self, file_path: Path) -> int:
        """Remove dead code from single file."""
        # Simplified - actual implementation would use reference counting
        return 0
        
    async def _run_lint_phase(self, files: List[Path]) -> RefactorResult:
        """Phase 4: Enforce linting rules."""
        logger.info(f"Enforcing lint rules on {len(files)} files")
        
        # Run pylint/flake8 on files
        import subprocess
        
        changes = 0
        issues = []
        
        for file in files:
            try:
                result = subprocess.run(
                    ["pylint", str(file), "--output-format=json"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    issues.append(f"Lint issues in {file}")
                    
            except Exception as e:
                issues.append(f"Lint failed for {file}: {e}")
                
        return RefactorResult(
            phase="lint_enforcement",
            files_processed=len(files),
            changes_made=changes,
            issues_found=issues
        )
        
    async def _run_format_phase(self, files: List[Path]) -> RefactorResult:
        """Phase 5: Enforce code formatting."""
        logger.info(f"Enforcing formatting on {len(files)} files")
        
        # Run black/autopep8 on files
        import subprocess
        
        changes = 0
        issues = []
        
        for file in files:
            try:
                result = subprocess.run(
                    ["black", str(file), "--quiet"],
                    capture_output=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    changes += 1
                    
            except Exception as e:
                issues.append(f"Formatting failed for {file}: {e}")
                
        self.metrics['changes_made'] += changes
        
        return RefactorResult(
            phase="format_enforcement",
            files_processed=len(files),
            changes_made=changes,
            issues_found=issues
        )
        
    def _finalize_refactor(self, results: List[RefactorResult]):
        """Phase 6: Finalize refactor cycle."""
        total_changes = sum(r.changes_made for r in results)
        total_issues = sum(len(r.issues_found) for r in results)
        
        logger.info(
            f"Refactor cycle complete: {total_changes} changes, "
            f"{total_issues} issues found"
        )
```

### Task 2: Multi-threaded File Scanner (1 hour)

**Create `src/operations/utils/multithreaded_file_scanner.py`:**

```python
"""Multi-threaded file scanning utilities for performance."""

from pathlib import Path
from typing import List, Callable, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)

def scan_files_parallel(
    files: List[Path],
    processor: Callable[[Path], Any],
    max_workers: int = 4
) -> List[Any]:
    """
    Scan files in parallel using thread pool.
    
    Args:
        files: List of file paths to process
        processor: Function to process each file
        max_workers: Maximum number of worker threads
        
    Returns:
        List of processing results
    """
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(processor, file): file for file in files}
        
        for future in as_completed(futures):
            file = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Processing failed for {file}: {e}")
                
    return results
```

### Task 3: Integration with Planning Orchestrator (1 hour)

**Update Planning Orchestrator 3.0:**

```python
# In planning_orchestrator.py

async def _run_refactor_cycle(self, plan_data: Dict[str, Any]):
    """Execute automatic refactor cycle for Tier 3/4."""
    from .refactor_cycle_orchestrator import RefactorCycleOrchestrator
    
    refactor = RefactorCycleOrchestrator(self.project_root)
    
    # Get files affected by plan
    affected_files = plan_data.get('affected_files', [])
    
    result = await refactor.execute(target_files=affected_files)
    
    return {
        'refactor_complete': result['success'],
        'changes_made': result['metrics']['changes_made'],
        'issues': result['metrics']['errors']
    }
```

---

## 📦 Expected Deliverables

### Code Deliverables
- ✅ `src/operations/modules/orchestration/refactor_cycle_orchestrator.py`
- ✅ `src/operations/utils/multithreaded_file_scanner.py`
- ✅ Integration with Planning Orchestrator 3.0
- ✅ Version synchronization logic

### Test Deliverables
- ✅ `tests/test_refactor_cycle_orchestrator.py`
- ✅ `tests/test_multithreaded_file_scanner.py`
- ✅ Integration tests with sample code
- ✅ Performance benchmarks

### Documentation Deliverables
- ✅ Refactor cycle usage guide
- ✅ Debug pattern configuration
- ✅ Multi-threading best practices
- ✅ Integration guide for orchestrators

---

## 🔄 Next Steps

1. **Phase 08 Completion:** AST Engine wrapper must be operational
2. **Phase 15 Completion:** Version Manager must be available
3. **Testing:** Validate refactor cycle on CORTEX codebase
4. **Performance Tuning:** Optimize multi-threading workers
5. **Integration:** Connect to Phase 03 (Planning Orchestrator 3.0)

---

## 🔗 Integration Points

### Upstream Dependencies
- **AST Engine (Phase 08):** Dead code detection
- **Version Manager (Phase 15):** Version synchronization

### Downstream Consumers
- **Planning Orchestrator (Phase 03):** Automatic refactor for Tier 3/4
- **Vacuum Orchestrator (Phase 12):** Post-vacuum refactor
- **Integration Tests (Phase 16):** End-to-end validation

---

## 🚨 Risk Mitigation

### Risk 1: Breaking Working Code
**Mitigation:**
- Git checkpoint before refactor cycle
- Test suite execution validation
- Conservative pattern matching
- Manual review gate for large changes

### Risk 2: Performance Overhead
**Mitigation:**
- Multi-threaded processing (4 workers default)
- Timeout limits (30s per file)
- Incremental processing for large codebases

### Risk 3: False Positive Debug Removal
**Mitigation:**
- Conservative regex patterns
- Exclude legitimate logging (logger.debug)
- Manual review of removed statements

---

## 📊 Success Metrics

- ✅ Refactor cycle completes in <30 seconds for typical phase
- ✅ 100% of debug statements removed
- ✅ Zero false positives in dead code detection
- ✅ Comment sync accuracy ≥95%
- ✅ Multi-threading provides 3x speedup vs. sequential
- ✅ Integration with Planning Orchestrator seamless

---

**Phase Owner:** Asif Hussain  
**Phase Status:** ⏳ Awaiting Phase 08, 15 completion  
**Last Updated:** 2024-12-14
