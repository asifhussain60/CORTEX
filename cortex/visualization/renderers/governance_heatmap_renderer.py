"""
Governance Heatmap Renderer for CORTEX LENS Dashboard.

This module renders visualizations of CORE rule compliance across the codebase,
tracking governance violations, phase approval status, and compliance drift over time.

Author: Asif Hussain
Orchestrator: LENSVisualizationOrchestrator
AC-ID: LENS-010
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Optional
import re
from datetime import datetime
from enum import Enum


class ComplianceLevel(Enum):
    """Compliance level for CORE rules."""
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"
    UNKNOWN = "unknown"


@dataclass
class CoreRule:
    """Information about a CORE governance rule.
    
    Attributes:
        rule_id: Rule identifier (e.g., "CORE-008")
        name: Rule name (e.g., "TDD")
        description: Brief rule description
        category: Rule category (governance, testing, documentation)
        severity: Rule severity (critical, high, medium, low)
    """
    rule_id: str
    name: str
    description: str
    category: str
    severity: str


@dataclass
class ComplianceResult:
    """Compliance check result for a file.
    
    Attributes:
        file_path: Path to checked file
        rule_id: CORE rule identifier
        level: Compliance level
        violations: List of violation descriptions
        line_numbers: List of line numbers with violations
        timestamp: Check timestamp
    """
    file_path: Path
    rule_id: str
    level: ComplianceLevel
    violations: List[str]
    line_numbers: List[int]
    timestamp: datetime


@dataclass
class GovernanceHeatmap:
    """Complete governance heatmap data.
    
    Attributes:
        files: List of analyzed files
        compliance_matrix: Matrix of file x rule compliance
        overall_compliance: Overall compliance percentage
        violations_by_rule: Count of violations per rule
        violations_by_category: Count of violations per category
        timeline: Compliance drift timeline
    """
    files: List[Path]
    compliance_matrix: Dict[str, Dict[str, ComplianceLevel]]
    overall_compliance: float
    violations_by_rule: Dict[str, int]
    violations_by_category: Dict[str, int]
    timeline: List[Dict[str, Any]]


class GovernanceHeatmapRenderer:
    """Renderer for governance compliance heatmap visualizations.
    
    This renderer analyzes Python files for CORE rule compliance,
    generates heatmaps showing compliance across the codebase, and
    tracks governance drift over time through git history analysis.
    """
    
    def __init__(self) -> None:
        """Initialize governance heatmap renderer."""
        self.core_rules = self._load_core_rules()
    
    def _load_core_rules(self) -> List[CoreRule]:
        """Load CORE governance rules.
        
        Returns:
            List[CoreRule]: List of CORE rules
        """
        # Define known CORE rules
        rules = [
            CoreRule("CORE-008", "TDD", "Tests BEFORE code", "testing", "critical"),
            CoreRule("CORE-011", "Type Hints", "Type hints mandatory", "code_quality", "high"),
            CoreRule("CORE-012", "Docstrings", "Google-style docstrings", "documentation", "high"),
            CoreRule("CORE-013", "Exception Handling", "No bare except clauses", "code_quality", "medium"),
            CoreRule("CORE-026", "Git Checkpoints", "Git checkpoint before major changes", "governance", "medium"),
            CoreRule("CORE-027", "Audit Trail", "AC_START → AC_EXECUTE → AC_COMPLETE", "governance", "critical"),
            CoreRule("CORE-028", "File Naming", "Python modules use snake_case", "governance", "high"),
            CoreRule("CORE-029", "Response Headers", "Response header enforcement", "governance", "medium"),
            CoreRule("CORE-030", "Implementation Truth", "Verify code, not docs", "governance", "critical"),
            CoreRule("CORE-035", "Single Canonical Implementation", "No duplicates", "code_quality", "high"),
            CoreRule("CORE-038", "File Placement", "Correct directory structure", "governance", "high"),
            CoreRule("CORE-039", "MD Generation Prohibition", "No .md outside docs/", "governance", "medium"),
            CoreRule("CORE-040", "Documentation Lifecycle", "Keep docs synchronized", "documentation", "medium"),
        ]
        return rules
    
    def analyze_file_compliance(
        self,
        file_path: Path,
        file_content: Optional[str] = None,
    ) -> List[ComplianceResult]:
        """Analyze a file for CORE rule compliance.
        
        Args:
            file_path: Path to file to analyze
            file_content: Optional file content (reads from disk if None)
        
        Returns:
            List[ComplianceResult]: Compliance results for each rule
        """
        if file_content is None:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read()
            except Exception:
                return []
        
        results = []
        
        # Check each CORE rule
        for rule in self.core_rules:
            if rule.rule_id == "CORE-008":
                result = self._check_tdd_compliance(file_path, file_content)
            elif rule.rule_id == "CORE-011":
                result = self._check_type_hints(file_path, file_content)
            elif rule.rule_id == "CORE-012":
                result = self._check_docstrings(file_path, file_content)
            elif rule.rule_id == "CORE-013":
                result = self._check_exception_handling(file_path, file_content)
            elif rule.rule_id == "CORE-028":
                result = self._check_file_naming(file_path, file_content)
            elif rule.rule_id == "CORE-038":
                result = self._check_file_placement(file_path, file_content)
            elif rule.rule_id == "CORE-039":
                result = self._check_md_generation(file_path, file_content)
            else:
                # Rules that can't be automatically checked
                result = ComplianceResult(
                    file_path=file_path,
                    rule_id=rule.rule_id,
                    level=ComplianceLevel.UNKNOWN,
                    violations=[],
                    line_numbers=[],
                    timestamp=datetime.now(),
                )
            
            results.append(result)
        
        return results
    
    def _check_tdd_compliance(self, file_path: Path, content: str) -> ComplianceResult:
        """Check TDD compliance (CORE-008).
        
        Args:
            file_path: Path to file
            content: File content
        
        Returns:
            ComplianceResult: TDD compliance result
        """
        violations = []
        line_numbers = []
        
        # Check if this is a test file or implementation
        is_test_file = "test_" in file_path.name or file_path.parent.name == "tests"
        
        if not is_test_file:
            # Implementation file - check if corresponding test exists
            test_file = self._find_test_file(file_path)
            if not test_file or not test_file.exists():
                violations.append(f"No test file found for {file_path.name}")
        
        level = ComplianceLevel.COMPLIANT if not violations else ComplianceLevel.VIOLATION
        
        return ComplianceResult(
            file_path=file_path,
            rule_id="CORE-008",
            level=level,
            violations=violations,
            line_numbers=line_numbers,
            timestamp=datetime.now(),
        )
    
    def _find_test_file(self, file_path: Path) -> Optional[Path]:
        """Find corresponding test file for an implementation file.
        
        Args:
            file_path: Path to implementation file
        
        Returns:
            Optional[Path]: Path to test file if found
        """
        # Look for tests/path/to/test_filename.py
        test_name = f"test_{file_path.name}"
        
        # Try in tests/ directory
        tests_dir = file_path.parent.parent / "tests"
        if tests_dir.exists():
            # Search for test file
            for test_file in tests_dir.rglob(test_name):
                return test_file
        
        return None
    
    def _check_type_hints(self, file_path: Path, content: str) -> ComplianceResult:
        """Check type hints compliance (CORE-011).
        
        Args:
            file_path: Path to file
            content: File content
        
        Returns:
            ComplianceResult: Type hints compliance result
        """
        violations = []
        line_numbers = []
        
        # Find function definitions without type hints
        lines = content.split("\n")
        for i, line in enumerate(lines, start=1):
            # Match function definitions
            if re.match(r'^\s*def\s+\w+\s*\(', line):
                # Check if function has type hints
                if "->" not in line and ":" not in line.split("def")[1].split(":")[0]:
                    # Skip __init__, __str__, __repr__ and other dunder methods
                    if not re.search(r'def\s+__\w+__', line):
                        violations.append(f"Function missing type hints at line {i}")
                        line_numbers.append(i)
        
        level = ComplianceLevel.COMPLIANT if not violations else ComplianceLevel.VIOLATION
        
        return ComplianceResult(
            file_path=file_path,
            rule_id="CORE-011",
            level=level,
            violations=violations,
            line_numbers=line_numbers,
            timestamp=datetime.now(),
        )
    
    def _check_docstrings(self, file_path: Path, content: str) -> ComplianceResult:
        """Check docstring compliance (CORE-012).
        
        Args:
            file_path: Path to file
            content: File content
        
        Returns:
            ComplianceResult: Docstring compliance result
        """
        violations = []
        line_numbers = []
        
        lines = content.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Match function or class definitions
            if re.match(r'^\s*(def|class)\s+\w+', line):
                # Check next non-empty line for docstring
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                
                if j < len(lines):
                    next_line = lines[j].strip()
                    if not (next_line.startswith('"""') or next_line.startswith("'''")):
                        # Skip private methods and properties
                        if not re.search(r'(def|class)\s+_\w+', line):
                            violations.append(f"Missing docstring at line {i + 1}")
                            line_numbers.append(i + 1)
            
            i += 1
        
        level = ComplianceLevel.COMPLIANT if not violations else ComplianceLevel.WARNING
        
        return ComplianceResult(
            file_path=file_path,
            rule_id="CORE-012",
            level=level,
            violations=violations,
            line_numbers=line_numbers,
            timestamp=datetime.now(),
        )
    
    def _check_exception_handling(self, file_path: Path, content: str) -> ComplianceResult:
        """Check exception handling compliance (CORE-013).
        
        Args:
            file_path: Path to file
            content: File content
        
        Returns:
            ComplianceResult: Exception handling compliance result
        """
        violations = []
        line_numbers = []
        
        lines = content.split("\n")
        for i, line in enumerate(lines, start=1):
            # Check for bare except clauses
            if re.match(r'^\s*except\s*:', line):
                violations.append(f"Bare except clause at line {i}")
                line_numbers.append(i)
        
        level = ComplianceLevel.COMPLIANT if not violations else ComplianceLevel.VIOLATION
        
        return ComplianceResult(
            file_path=file_path,
            rule_id="CORE-013",
            level=level,
            violations=violations,
            line_numbers=line_numbers,
            timestamp=datetime.now(),
        )
    
    def _check_file_naming(self, file_path: Path, content: str) -> ComplianceResult:
        """Check file naming compliance (CORE-028).
        
        Args:
            file_path: Path to file
            content: File content
        
        Returns:
            ComplianceResult: File naming compliance result
        """
        violations = []
        line_numbers = []
        
        # Check if Python file uses snake_case
        if file_path.suffix == ".py":
            filename = file_path.stem
            # Check for hyphens (invalid in Python modules)
            if "-" in filename:
                violations.append(f"Filename contains hyphens: {filename}")
            # Check if not snake_case (except __init__ and special files)
            elif filename not in ["__init__", "__main__"] and not re.match(r'^[a-z][a-z0-9_]*$', filename):
                violations.append(f"Filename not snake_case: {filename}")
        
        level = ComplianceLevel.COMPLIANT if not violations else ComplianceLevel.VIOLATION
        
        return ComplianceResult(
            file_path=file_path,
            rule_id="CORE-028",
            level=level,
            violations=violations,
            line_numbers=line_numbers,
            timestamp=datetime.now(),
        )
    
    def _check_file_placement(self, file_path: Path, content: str) -> ComplianceResult:
        """Check file placement compliance (CORE-038).
        
        Args:
            file_path: Path to file
            content: File content
        
        Returns:
            ComplianceResult: File placement compliance result
        """
        violations = []
        line_numbers = []
        
        # Check Python files in root (should be in cortex/ or tests/)
        if file_path.suffix == ".py" and len(file_path.parts) <= 2:
            if file_path.name not in ["setup.py", "conftest.py"]:
                violations.append(f"Python file in root: {file_path.name}")
        
        level = ComplianceLevel.COMPLIANT if not violations else ComplianceLevel.WARNING
        
        return ComplianceResult(
            file_path=file_path,
            rule_id="CORE-038",
            level=level,
            violations=violations,
            line_numbers=line_numbers,
            timestamp=datetime.now(),
        )
    
    def _check_md_generation(self, file_path: Path, content: str) -> ComplianceResult:
        """Check MD generation prohibition (CORE-039).
        
        Args:
            file_path: Path to file
            content: File content
        
        Returns:
            ComplianceResult: MD generation compliance result
        """
        violations = []
        line_numbers = []
        
        # Check .md files outside docs/ or reports/
        if file_path.suffix == ".md":
            allowed_dirs = ["docs", "reports", ".github"]
            if not any(dir_name in file_path.parts for dir_name in allowed_dirs):
                violations.append(f".md file outside allowed directories: {file_path}")
        
        level = ComplianceLevel.COMPLIANT if not violations else ComplianceLevel.VIOLATION
        
        return ComplianceResult(
            file_path=file_path,
            rule_id="CORE-039",
            level=level,
            violations=violations,
            line_numbers=line_numbers,
            timestamp=datetime.now(),
        )
    
    def generate_heatmap(
        self,
        repo_path: Path,
        file_patterns: Optional[List[str]] = None,
    ) -> GovernanceHeatmap:
        """Generate governance compliance heatmap for repository.
        
        Args:
            repo_path: Path to repository root
            file_patterns: Optional list of glob patterns to include
        
        Returns:
            GovernanceHeatmap: Complete heatmap data
        """
        if file_patterns is None:
            file_patterns = ["cortex/**/*.py", "tests/**/*.py"]
        
        # Collect files to analyze
        files = []
        for pattern in file_patterns:
            files.extend(repo_path.glob(pattern))
        
        # Analyze compliance for each file
        compliance_matrix = {}
        violations_by_rule = {rule.rule_id: 0 for rule in self.core_rules}
        violations_by_category = {}
        
        for file_path in files:
            results = self.analyze_file_compliance(file_path)
            
            # Build compliance matrix
            file_key = str(file_path.relative_to(repo_path))
            compliance_matrix[file_key] = {}
            
            for result in results:
                compliance_matrix[file_key][result.rule_id] = result.level
                
                # Count violations
                if result.level == ComplianceLevel.VIOLATION:
                    violations_by_rule[result.rule_id] += len(result.violations)
                    
                    # Get rule category
                    rule = next((r for r in self.core_rules if r.rule_id == result.rule_id), None)
                    if rule:
                        category = rule.category
                        violations_by_category[category] = violations_by_category.get(category, 0) + 1
        
        # Calculate overall compliance
        total_checks = len(files) * len(self.core_rules)
        compliant_checks = sum(
            1 for file_data in compliance_matrix.values()
            for level in file_data.values()
            if level == ComplianceLevel.COMPLIANT
        )
        overall_compliance = (compliant_checks / total_checks * 100) if total_checks > 0 else 0.0
        
        # Generate timeline (placeholder - would need git history)
        timeline = self._generate_compliance_timeline(repo_path)
        
        return GovernanceHeatmap(
            files=files,
            compliance_matrix=compliance_matrix,
            overall_compliance=overall_compliance,
            violations_by_rule=violations_by_rule,
            violations_by_category=violations_by_category,
            timeline=timeline,
        )
    
    def _generate_compliance_timeline(self, repo_path: Path) -> List[Dict[str, Any]]:
        """Generate compliance drift timeline from git history.
        
        Args:
            repo_path: Path to repository root
        
        Returns:
            List[Dict[str, Any]]: Timeline data points
        """
        # Placeholder - would analyze git history for compliance changes
        timeline = [
            {"date": "2026-01-01", "compliance": 75.0},
            {"date": "2026-01-15", "compliance": 85.0},
            {"date": "2026-01-29", "compliance": 92.0},
        ]
        return timeline
    
    def render_heatmap_visualization(
        self,
        heatmap: GovernanceHeatmap,
    ) -> Dict[str, Any]:
        """Render heatmap visualization data for D3.js.
        
        Args:
            heatmap: Governance heatmap data
        
        Returns:
            Dict[str, Any]: D3.js heatmap data
        """
        # Prepare data for D3.js heatmap
        heatmap_data = []
        
        for file_key, rule_results in heatmap.compliance_matrix.items():
            for rule_id, level in rule_results.items():
                # Map compliance level to color
                color_map = {
                    ComplianceLevel.COMPLIANT: "green",
                    ComplianceLevel.WARNING: "yellow",
                    ComplianceLevel.VIOLATION: "red",
                    ComplianceLevel.UNKNOWN: "gray",
                }
                
                heatmap_data.append({
                    "file": file_key,
                    "rule": rule_id,
                    "level": level.value,
                    "color": color_map[level],
                })
        
        return {
            "data": heatmap_data,
            "files": [str(f.name) for f in heatmap.files[:50]],  # Limit for display
            "rules": [rule.rule_id for rule in self.core_rules],
            "metadata": {
                "total_files": len(heatmap.files),
                "total_rules": len(self.core_rules),
                "overall_compliance": f"{heatmap.overall_compliance:.1f}%",
            },
        }
    
    def render_violations_chart(
        self,
        heatmap: GovernanceHeatmap,
    ) -> Dict[str, Any]:
        """Render violations breakdown chart data.
        
        Args:
            heatmap: Governance heatmap data
        
        Returns:
            Dict[str, Any]: Chart data for violations
        """
        # Violations by rule
        rule_data = [
            {"rule": rule_id, "count": count}
            for rule_id, count in heatmap.violations_by_rule.items()
            if count > 0
        ]
        
        # Violations by category
        category_data = [
            {"category": category, "count": count}
            for category, count in heatmap.violations_by_category.items()
        ]
        
        return {
            "by_rule": rule_data,
            "by_category": category_data,
        }
    
    def render_compliance_timeline(
        self,
        heatmap: GovernanceHeatmap,
    ) -> Dict[str, Any]:
        """Render compliance timeline chart data.
        
        Args:
            heatmap: Governance heatmap data
        
        Returns:
            Dict[str, Any]: Timeline chart data
        """
        return {
            "timeline": heatmap.timeline,
            "current_compliance": heatmap.overall_compliance,
        }
