# Phase 09: Enhanced Analyzers

**🔗 Breadcrumb:** [← Back to Master Plan](cortex-3.9-master.md)

**Status:** ⏳ Pending  
**Phase ID:** 09  
**Estimated Time:** 4 hours (240 minutes)  
**Actual Start:** -  
**Actual End:** -  
**Actual Work Time:** -  
**Dependencies:** Phase 08 (AST Engine Wrapper) ⏳  
**Blocks:** Phase 17 (Proactive Intelligence)

---

## 🎯 Phase Objective

Enhance CORTEX analysis capabilities with AST-powered deduplication detection, architectural debt analysis, and code smell identification for proactive code quality improvements.

**Success Criteria:**
- ✅ Deduplication analyzer using AST semantic comparison (≥90% accuracy)
- ✅ Architectural debt analyzer detecting layer violations and circular dependencies
- ✅ Code smell analyzer identifying anti-patterns and technical debt
- ✅ Integration with AST Engine for semantic analysis
- ✅ Actionable recommendations for each detected issue
- ✅ 100% test coverage with passing tests

---

## 🏗️ Implementation Plan

### Task 1: Deduplication Analyzer (1.5 hours)

**Create `src/operations/modules/analysis/deduplication_analyzer.py`:**

```python
"""
Deduplication Analyzer - AST-powered semantic duplicate detection.

Identifies functionally similar code blocks that could be refactored
into shared utilities or modules.
"""

from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class DuplicateGroup:
    """Group of semantically similar code blocks."""
    similarity_score: float
    locations: List[Dict[str, Any]]  # file, start_line, end_line
    lines_count: int
    recommendation: str

class DeduplicationAnalyzer:
    """Detect semantic code duplicates using AST analysis."""
    
    def __init__(self, ast_engine):
        self.ast_engine = ast_engine
        self.min_similarity = 0.85
        self.min_lines = 10
        
    def analyze(self, target_path: Path = None) -> Dict[str, Any]:
        """
        Analyze codebase for semantic duplicates.
        
        Args:
            target_path: Specific directory/file or None for full project
            
        Returns:
            Analysis results with duplicate groups and recommendations
        """
        logger.info(f"Analyzing duplicates in {target_path or 'full project'}")
        
        # Use AST engine for semantic comparison
        duplicate_groups = self.ast_engine.find_semantic_duplicates(
            similarity_threshold=self.min_similarity,
            min_lines=self.min_lines
        )
        
        # Enrich with recommendations
        enriched_groups = []
        for group in duplicate_groups:
            enriched_groups.append(DuplicateGroup(
                similarity_score=group['similarity'],
                locations=group['locations'],
                lines_count=group['lines'],
                recommendation=self._generate_recommendation(group)
            ))
            
        return {
            'duplicate_groups': enriched_groups,
            'total_duplicates': len(enriched_groups),
            'total_duplicate_lines': sum(g.lines_count for g in enriched_groups),
            'estimated_cleanup_hours': self._estimate_cleanup_effort(enriched_groups)
        }
        
    def _generate_recommendation(self, group: Dict[str, Any]) -> str:
        """Generate actionable refactoring recommendation."""
        locations = group['locations']
        
        if len(locations) == 2:
            return (
                f"Extract shared logic into utility function. "
                f"Found in {locations[0]['file']} and {locations[1]['file']}."
            )
        elif len(locations) > 2:
            return (
                f"Consider creating shared module. "
                f"Duplicate appears in {len(locations)} files."
            )
        else:
            return "Review for refactoring opportunity."
            
    def _estimate_cleanup_effort(self, groups: List[DuplicateGroup]) -> float:
        """Estimate cleanup effort in hours."""
        # 15 minutes per duplicate group (conservative)
        return len(groups) * 0.25
```

### Task 2: Architectural Debt Analyzer (1.5 hours)

**Create `src/operations/modules/analysis/architecture_debt_analyzer.py`:**

```python
"""
Architectural Debt Analyzer - Layer violations and circular dependencies.

Detects architectural anti-patterns that increase maintenance cost
and reduce code modularity.
"""

from pathlib import Path
from typing import Dict, Any, List, Set
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ArchitectureViolation:
    """Architectural rule violation."""
    violation_type: str  # "layer_violation", "circular_dependency", "tight_coupling"
    severity: str  # "high", "medium", "low"
    description: str
    affected_modules: List[str]
    recommendation: str

class ArchitectureDebtAnalyzer:
    """Analyze architectural quality and identify debt."""
    
    def __init__(self, ast_engine):
        self.ast_engine = ast_engine
        
        # Define expected architecture layers
        self.layer_hierarchy = [
            "presentation",  # UI/API
            "application",   # Orchestrators
            "domain",        # Business logic
            "infrastructure" # Data access
        ]
        
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze codebase architecture for violations and debt.
        
        Returns:
            Architecture analysis with violations and recommendations
        """
        logger.info("Analyzing architectural debt")
        
        # Use AST engine for dependency graph
        arch_data = self.ast_engine.analyze_architecture()
        
        violations = []
        
        # Detect layer violations
        layer_violations = self._detect_layer_violations(arch_data['module_graph'])
        violations.extend(layer_violations)
        
        # Detect circular dependencies
        circular_deps = self._detect_circular_dependencies(arch_data['circular_dependencies'])
        violations.extend(circular_deps)
        
        # Detect tight coupling
        tight_coupling = self._detect_tight_coupling(arch_data['module_graph'])
        violations.extend(tight_coupling)
        
        return {
            'violations': violations,
            'total_violations': len(violations),
            'high_severity_count': len([v for v in violations if v.severity == 'high']),
            'debt_score': self._calculate_debt_score(violations),
            'recommended_actions': self._prioritize_actions(violations)
        }
        
    def _detect_layer_violations(self, module_graph: List[Dict]) -> List[ArchitectureViolation]:
        """Detect dependencies that violate layer hierarchy."""
        violations = []
        
        for edge in module_graph:
            from_module = edge['from']
            to_module = edge['to']
            
            from_layer = self._identify_layer(from_module)
            to_layer = self._identify_layer(to_module)
            
            if from_layer and to_layer:
                from_idx = self.layer_hierarchy.index(from_layer)
                to_idx = self.layer_hierarchy.index(to_layer)
                
                # Lower layers should not depend on higher layers
                if from_idx > to_idx:
                    violations.append(ArchitectureViolation(
                        violation_type="layer_violation",
                        severity="high",
                        description=f"{from_layer} layer depends on {to_layer} layer",
                        affected_modules=[from_module, to_module],
                        recommendation=(
                            f"Introduce abstraction in {to_layer} layer "
                            f"or move {from_module} to appropriate layer"
                        )
                    ))
                    
        return violations
        
    def _detect_circular_dependencies(self, circular_deps: List[List[str]]) -> List[ArchitectureViolation]:
        """Detect circular dependency cycles."""
        violations = []
        
        for cycle in circular_deps:
            violations.append(ArchitectureViolation(
                violation_type="circular_dependency",
                severity="high",
                description=f"Circular dependency: {' → '.join(cycle + [cycle[0]])}",
                affected_modules=cycle,
                recommendation=(
                    "Break cycle by introducing interface/abstraction "
                    "or inverting dependency direction"
                )
            ))
            
        return violations
        
    def _detect_tight_coupling(self, module_graph: List[Dict]) -> List[ArchitectureViolation]:
        """Detect modules with excessive dependencies."""
        violations = []
        
        # Count incoming dependencies per module
        dependency_counts = {}
        for edge in module_graph:
            to_module = edge['to']
            dependency_counts[to_module] = dependency_counts.get(to_module, 0) + 1
            
        # Flag modules with >10 incoming dependencies
        for module, count in dependency_counts.items():
            if count > 10:
                violations.append(ArchitectureViolation(
                    violation_type="tight_coupling",
                    severity="medium",
                    description=f"{module} has {count} incoming dependencies",
                    affected_modules=[module],
                    recommendation=(
                        "Consider splitting module into smaller, focused components "
                        "or introducing facade pattern"
                    )
                ))
                
        return violations
        
    def _calculate_debt_score(self, violations: List[ArchitectureViolation]) -> float:
        """Calculate overall architectural debt score (0-100)."""
        if not violations:
            return 0.0
            
        severity_weights = {"high": 3, "medium": 2, "low": 1}
        total_weight = sum(severity_weights[v.severity] for v in violations)
        
        # Normalize to 0-100 scale (10+ violations = 100)
        return min(100.0, (total_weight / 30.0) * 100)
```

### Task 3: Code Smell Analyzer (1 hour)

**Create `src/operations/modules/analysis/code_smell_analyzer.py`:**

```python
"""
Code Smell Analyzer - Identify common anti-patterns and technical debt.

Detects code quality issues that increase maintenance burden and
reduce code readability.
"""

from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass
import ast
import logging

logger = logging.getLogger(__name__)

@dataclass
class CodeSmell:
    """Individual code smell detection."""
    smell_type: str
    file_path: str
    line_number: int
    description: str
    severity: str
    recommendation: str

class CodeSmellAnalyzer:
    """Detect code smells and anti-patterns."""
    
    def __init__(self):
        self.smell_detectors = [
            self._detect_long_methods,
            self._detect_large_classes,
            self._detect_god_objects,
            self._detect_magic_numbers,
            self._detect_deep_nesting,
            self._detect_duplicate_code
        ]
        
    def analyze(self, target_path: Path) -> Dict[str, Any]:
        """
        Analyze code for smells and anti-patterns.
        
        Args:
            target_path: Directory or file to analyze
            
        Returns:
            Code smell analysis with recommendations
        """
        logger.info(f"Analyzing code smells in {target_path}")
        
        smells = []
        
        if target_path.is_file():
            files = [target_path]
        else:
            files = list(target_path.rglob("*.py"))
            
        for file_path in files:
            file_smells = self._analyze_file(file_path)
            smells.extend(file_smells)
            
        return {
            'smells': smells,
            'total_smells': len(smells),
            'by_type': self._group_by_type(smells),
            'by_severity': self._group_by_severity(smells),
            'priority_fixes': self._prioritize_fixes(smells)
        }
        
    def _analyze_file(self, file_path: Path) -> List[CodeSmell]:
        """Analyze single file for code smells."""
        smells = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
                
            for detector in self.smell_detectors:
                file_smells = detector(tree, file_path, content)
                smells.extend(file_smells)
                
        except Exception as e:
            logger.error(f"Failed to analyze {file_path}: {e}")
            
        return smells
        
    def _detect_long_methods(self, tree: ast.AST, file_path: Path, content: str) -> List[CodeSmell]:
        """Detect methods exceeding 50 lines."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                start_line = node.lineno
                end_line = node.end_lineno or start_line
                lines = end_line - start_line
                
                if lines > 50:
                    smells.append(CodeSmell(
                        smell_type="long_method",
                        file_path=str(file_path),
                        line_number=start_line,
                        description=f"Method '{node.name}' has {lines} lines",
                        severity="medium",
                        recommendation="Consider breaking into smaller, focused methods"
                    ))
                    
        return smells
        
    def _detect_large_classes(self, tree: ast.AST, file_path: Path, content: str) -> List[CodeSmell]:
        """Detect classes exceeding 300 lines or 15 methods."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                start_line = node.lineno
                end_line = node.end_lineno or start_line
                lines = end_line - start_line
                
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                
                if lines > 300 or len(methods) > 15:
                    smells.append(CodeSmell(
                        smell_type="large_class",
                        file_path=str(file_path),
                        line_number=start_line,
                        description=f"Class '{node.name}' has {lines} lines and {len(methods)} methods",
                        severity="high",
                        recommendation="Consider splitting into multiple classes with single responsibilities"
                    ))
                    
        return smells
        
    def _detect_magic_numbers(self, tree: ast.AST, file_path: Path, content: str) -> List[CodeSmell]:
        """Detect magic numbers (unexplained numeric literals)."""
        smells = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Num) and not isinstance(node.n, (bool, type(None))):
                # Ignore common values (0, 1, -1)
                if node.n not in [0, 1, -1]:
                    smells.append(CodeSmell(
                        smell_type="magic_number",
                        file_path=str(file_path),
                        line_number=node.lineno,
                        description=f"Magic number {node.n} without explanation",
                        severity="low",
                        recommendation="Extract to named constant with descriptive name"
                    ))
                    
        return smells
```

---

## 📦 Expected Deliverables

### Code Deliverables
- ✅ `src/operations/modules/analysis/deduplication_analyzer.py`
- ✅ `src/operations/modules/analysis/architecture_debt_analyzer.py`
- ✅ `src/operations/modules/analysis/code_smell_analyzer.py`
- ✅ Integration with AST Engine wrapper

### Test Deliverables
- ✅ `tests/test_deduplication_analyzer.py`
- ✅ `tests/test_architecture_debt_analyzer.py`
- ✅ `tests/test_code_smell_analyzer.py`
- ✅ Integration tests with real code samples

### Documentation Deliverables
- ✅ Analyzer usage guide
- ✅ Code smell catalog with examples
- ✅ Architecture violation patterns
- ✅ Remediation recommendations

---

## 🔄 Next Steps

1. **Phase 08 Completion:** AST Engine wrapper must be operational
2. **Testing:** Validate analyzers on CORTEX codebase
3. **Calibration:** Tune thresholds based on false positive rates
4. **Integration:** Connect to Phase 17 (Proactive Intelligence)

---

## 🔗 Integration Points

### Upstream Dependencies
- **AST Engine (Phase 08):** Core AST analysis capabilities

### Downstream Consumers
- **Proactive Intelligence (Phase 17):** Uses analyzer insights for recommendations
- **Vacuum Orchestrator (Phase 12):** Deduplication for cleanup
- **Refactor Cycle (Phase 13):** Code smell fixes

---

## 🚨 Risk Mitigation

### Risk 1: False Positives
**Mitigation:**
- Conservative thresholds (0.85 similarity, 50+ line methods)
- Manual review gate for high-impact changes
- User feedback loop for threshold calibration

### Risk 2: Performance on Large Codebases
**Mitigation:**
- Incremental analysis (target specific directories)
- Result caching with 1-hour TTL
- Parallel file processing

---

## 📊 Success Metrics

- ✅ Deduplication accuracy ≥90% (validated against manual review)
- ✅ Architecture violations detected with ≥95% precision
- ✅ Code smell false positive rate <10%
- ✅ Analysis completes in <2 minutes for typical project
- ✅ Actionable recommendations generated for 100% of issues

---

**Phase Owner:** Asif Hussain  
**Phase Status:** ⏳ Awaiting Phase 08 completion  
**Last Updated:** 2024-12-14
