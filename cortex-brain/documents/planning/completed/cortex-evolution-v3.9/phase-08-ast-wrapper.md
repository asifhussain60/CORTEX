# Phase 08: AST Engine Wrapper

**🔗 Breadcrumb:** [← Back to Master Plan](cortex-3.9-master.md)

**Status:** ⏳ Pending  
**Phase ID:** 08  
**Estimated Time:** 3 hours (180 minutes)  
**Actual Start:** -  
**Actual End:** -  
**Actual Work Time:** -  
**Dependencies:** None (CORTEX Lens already exists)  
**Blocks:** Phase 06 (Maintenance), Phase 09 (Enhanced Analyzers), Phase 12 (Vacuum)

---

## 🎯 Phase Objective

Create non-invasive wrapper around CORTEX Lens to enable programmatic AST analysis integration without modifying Lens codebase, preserving its independence and self-contained architecture.

**Success Criteria:**
- ✅ Zero modifications to CORTEX Lens codebase
- ✅ Programmatic API for AST analysis (deduplication, test gaps, architecture insights)
- ✅ Contract tests validating wrapper compatibility
- ✅ Performance overhead <100ms per analysis
- ✅ Error handling for Lens unavailability
- ✅ 100% test coverage with passing tests

---

## 🏗️ Implementation Plan

### Task 1: AST Engine Wrapper Core (1.5 hours)

**Create `src/operations/modules/analysis/ast_engine.py`:**

```python
"""
AST Engine - Non-invasive wrapper for CORTEX Lens integration.

Provides programmatic interface to CORTEX Lens AST capabilities
without modifying Lens codebase. Maintains Lens independence.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import subprocess
import json
import logging

logger = logging.getLogger(__name__)

class ASTEngine:
    """Non-invasive CORTEX Lens wrapper for AST analysis."""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.lens_path = self.project_root / "src" / "cortex_lens"
        self.lens_cli = self.lens_path / "cli.py"
        
        if not self.lens_cli.exists():
            logger.warning(f"CORTEX Lens not found at {self.lens_cli}")
            self.available = False
        else:
            self.available = True
            
    def find_semantic_duplicates(
        self, 
        similarity_threshold: float = 0.85,
        min_lines: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find semantically similar code blocks using AST comparison.
        
        Args:
            similarity_threshold: Minimum similarity score (0.0-1.0)
            min_lines: Minimum lines for duplicate consideration
            
        Returns:
            List of duplicate groups with file locations and similarity scores
        """
        if not self.available:
            return []
            
        try:
            result = self._call_lens_analyzer(
                analyzer="deduplication",
                options={
                    "threshold": similarity_threshold,
                    "min_lines": min_lines
                }
            )
            return result.get("duplicate_groups", [])
        except Exception as e:
            logger.error(f"Duplicate detection failed: {e}")
            return []
            
    def find_orphaned_tests(
        self, 
        test_patterns: List[str] = None
    ) -> List[Path]:
        """
        Identify test files with no corresponding source files.
        
        Args:
            test_patterns: Glob patterns for test file matching
            
        Returns:
            List of orphaned test file paths
        """
        if not self.available:
            return []
            
        test_patterns = test_patterns or ["test_*.py", "*_test.py"]
        
        try:
            result = self._call_lens_analyzer(
                analyzer="test_coverage",
                options={"patterns": test_patterns}
            )
            return [Path(p) for p in result.get("orphaned_tests", [])]
        except Exception as e:
            logger.error(f"Orphaned test detection failed: {e}")
            return []
            
    def analyze_test_gaps(self, target_file: Path) -> Dict[str, Any]:
        """
        Identify functions/classes without corresponding tests.
        
        Args:
            target_file: Source file to analyze for test coverage
            
        Returns:
            Dict with untested functions, classes, and coverage percentage
        """
        if not self.available:
            return {"coverage": 0.0, "untested": []}
            
        try:
            result = self._call_lens_analyzer(
                analyzer="test_gaps",
                options={"file": str(target_file)}
            )
            return {
                "coverage": result.get("coverage_percent", 0.0),
                "untested_functions": result.get("untested_functions", []),
                "untested_classes": result.get("untested_classes", [])
            }
        except Exception as e:
            logger.error(f"Test gap analysis failed: {e}")
            return {"coverage": 0.0, "untested": []}
            
    def remove_unused_imports(
        self, 
        exclude_patterns: List[str] = None
    ) -> int:
        """
        Remove unused imports across Python files.
        
        Args:
            exclude_patterns: File patterns to exclude from cleanup
            
        Returns:
            Number of imports removed
        """
        if not self.available:
            return 0
            
        exclude_patterns = exclude_patterns or ["__init__.py"]
        
        try:
            result = self._call_lens_analyzer(
                analyzer="import_cleanup",
                options={"exclude": exclude_patterns}
            )
            return result.get("imports_removed", 0)
        except Exception as e:
            logger.error(f"Import cleanup failed: {e}")
            return 0
            
    def analyze_architecture(self) -> Dict[str, Any]:
        """
        Generate architecture insights and dependency graphs.
        
        Returns:
            Dict with module dependencies, layer violations, circular deps
        """
        if not self.available:
            return {"modules": [], "violations": []}
            
        try:
            result = self._call_lens_analyzer(
                analyzer="architecture",
                options={}
            )
            return {
                "module_graph": result.get("dependencies", []),
                "layer_violations": result.get("violations", []),
                "circular_dependencies": result.get("circular_deps", [])
            }
        except Exception as e:
            logger.error(f"Architecture analysis failed: {e}")
            return {"modules": [], "violations": []}
            
    def _call_lens_analyzer(
        self, 
        analyzer: str, 
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call CORTEX Lens analyzer via programmatic interface.
        
        Strategy: Use Lens orchestrator's programmatic API instead of CLI.
        This avoids subprocess overhead and enables direct data exchange.
        """
        try:
            # Import Lens orchestrator dynamically (no hard dependency)
            import sys
            sys.path.insert(0, str(self.lens_path))
            
            from orchestrator import LensOrchestrator
            
            orchestrator = LensOrchestrator(self.project_root)
            result = orchestrator.run_analyzer(analyzer, **options)
            
            return result
            
        except ImportError:
            # Fallback to CLI if programmatic interface unavailable
            logger.warning("Falling back to Lens CLI interface")
            return self._call_lens_cli(analyzer, options)
            
    def _call_lens_cli(
        self, 
        analyzer: str, 
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback CLI interface for CORTEX Lens."""
        cmd = [
            "python", str(self.lens_cli),
            "analyze", analyzer,
            "--output-format", "json"
        ]
        
        for key, value in options.items():
            cmd.extend([f"--{key}", str(value)])
            
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5-minute timeout
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Lens CLI failed: {result.stderr}")
            
        return json.loads(result.stdout)
```

### Task 2: Contract Tests (1 hour)

**Create `tests/test_ast_engine.py`:**

```python
"""
Contract tests for AST Engine wrapper.

Validates compatibility with CORTEX Lens without testing Lens internals.
"""

import pytest
from pathlib import Path
from src.operations.modules.analysis.ast_engine import ASTEngine

@pytest.fixture
def ast_engine():
    """Create AST engine for CORTEX project root."""
    return ASTEngine(Path(__file__).parent.parent)

def test_ast_engine_initialization(ast_engine):
    """Verify AST engine initializes with Lens detection."""
    assert ast_engine.project_root.exists()
    assert isinstance(ast_engine.available, bool)
    
def test_duplicate_detection_interface(ast_engine):
    """Contract test: duplicate detection returns expected structure."""
    if not ast_engine.available:
        pytest.skip("CORTEX Lens not available")
        
    duplicates = ast_engine.find_semantic_duplicates(
        similarity_threshold=0.85,
        min_lines=10
    )
    
    assert isinstance(duplicates, list)
    # Don't assert on content - that's Lens's responsibility
    
def test_orphaned_test_detection_interface(ast_engine):
    """Contract test: orphaned test detection returns paths."""
    if not ast_engine.available:
        pytest.skip("CORTEX Lens not available")
        
    orphaned = ast_engine.find_orphaned_tests()
    
    assert isinstance(orphaned, list)
    for path in orphaned:
        assert isinstance(path, Path)
        
def test_graceful_degradation_when_lens_unavailable():
    """Verify wrapper handles Lens unavailability gracefully."""
    engine = ASTEngine(Path("/nonexistent"))
    
    assert not engine.available
    assert engine.find_semantic_duplicates() == []
    assert engine.find_orphaned_tests() == []
    assert engine.analyze_test_gaps(Path("dummy.py"))["coverage"] == 0.0
```

### Task 3: Integration Documentation (30 min)

**Create usage guide:**

```markdown
# AST Engine Wrapper - Integration Guide

## Purpose
Non-invasive interface to CORTEX Lens AST capabilities for use in
CORTEX orchestrators and workflows.

## Design Principles
1. **Zero Modifications**: CORTEX Lens remains unchanged
2. **Graceful Degradation**: Functions without Lens present
3. **Performance**: <100ms overhead per analysis
4. **Independence**: Lens can operate standalone

## Usage Examples

### Duplicate Detection
```python
from src.operations.modules.analysis.ast_engine import ASTEngine

engine = ASTEngine(project_root)
duplicates = engine.find_semantic_duplicates(
    similarity_threshold=0.85,
    min_lines=10
)

for group in duplicates:
    print(f"Found {len(group['locations'])} duplicates")
    print(f"Similarity: {group['similarity']:.2%}")
```

### Test Gap Analysis
```python
gaps = engine.analyze_test_gaps(Path("src/module.py"))
print(f"Coverage: {gaps['coverage']:.1%}")
print(f"Untested: {gaps['untested_functions']}")
```

## Error Handling
- Lens unavailable: Returns empty results, logs warning
- Lens error: Catches exception, returns safe defaults
- Timeout: 5-minute limit per analysis
```

---

## 📦 Expected Deliverables

### Code Deliverables
- ✅ `src/operations/modules/analysis/ast_engine.py`
- ✅ `src/operations/modules/analysis/__init__.py`
- ✅ Programmatic Lens interface methods
- ✅ CLI fallback implementation

### Test Deliverables
- ✅ `tests/test_ast_engine.py` (contract tests)
- ✅ Lens availability detection tests
- ✅ Graceful degradation tests
- ✅ Interface compatibility tests

### Documentation Deliverables
- ✅ AST Engine integration guide
- ✅ Usage examples for each analyzer
- ✅ Error handling documentation
- ✅ Performance benchmarks

---

## 🔄 Next Steps

1. **Validation:** Verify CORTEX Lens programmatic interface exists
2. **Fallback Testing:** Validate CLI interface works if programmatic unavailable
3. **Performance Benchmarking:** Measure overhead vs. direct Lens usage
4. **Integration:** Connect to Phase 06 (Maintenance), Phase 09 (Analyzers), Phase 12 (Vacuum)

---

## 🔗 Integration Points

### CORTEX Lens Compatibility
- **Lens Version:** 1.0.0+
- **Required Analyzers:** deduplication, test_coverage, import_cleanup, architecture
- **Interface:** Programmatic (preferred) or CLI (fallback)

### Downstream Consumers
- **Maintenance Orchestrator (Phase 06):** AST cleanup intelligence
- **Enhanced Analyzers (Phase 09):** Deduplication, architecture insights
- **Vacuum Orchestrator (Phase 12):** Orphaned code detection
- **Refactor Cycle (Phase 13):** Unused import cleanup

---

## 🚨 Risk Mitigation

### Risk 1: Lens Interface Changes
**Mitigation:**
- Contract tests detect incompatibilities immediately
- Version pinning in requirements (cortex-lens>=1.0.0)
- Graceful degradation if interface unavailable

### Risk 2: Performance Overhead
**Mitigation:**
- Use programmatic interface (no subprocess spawning)
- Implement result caching (5-minute TTL)
- Timeout limits prevent hanging

### Risk 3: Lens Unavailability
**Mitigation:**
- All methods return safe defaults when Lens missing
- Log warnings but don't fail operations
- Document optional vs. required Lens usage

---

## 📊 Success Metrics

- ✅ Zero modifications to CORTEX Lens codebase
- ✅ Performance overhead <100ms per analysis
- ✅ 100% contract test pass rate
- ✅ Graceful degradation verified in CI without Lens
- ✅ All 5 analyzer interfaces functional
- ✅ Documentation complete with examples

---

**Phase Owner:** Asif Hussain  
**Phase Status:** ⏳ Ready to implement (no blockers)  
**Last Updated:** 2024-12-14
