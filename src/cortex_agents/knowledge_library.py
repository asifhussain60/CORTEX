"""
Knowledge Library - Phase -1 Pre-Planning Discovery

Purpose:
    Scan workspace for existing patterns, duplication, and architectural knowledge
    BEFORE planning begins. Prevents planning duplicate implementations.

Key Capabilities:
    1. AST Scanning - Extract classes, functions, imports from codebase
    2. Pattern Detection - Identify duplicates, architectural patterns, refactoring opportunities
    3. Knowledge Graph Integration - Query historical patterns from Tier 2
    4. Risk Analysis - Surface lessons-learned from similar implementations

Usage:
    from cortex_agents.knowledge_library import KnowledgeLibrary

    library = KnowledgeLibrary(workspace_path="/Users/user/project")
    patterns = library.scan_workspace(target_feature="user authentication")

    # Returns:
    # {
    #   "existing_implementations": [...],
    #   "duplicate_code": [...],
    #   "architectural_patterns": [...],
    #   "refactoring_opportunities": [...],
    #   "historical_risks": [...]
    # }

Version: 1.0
Author: CORTEX
Created: 2026-01-04
Sub-Plan: C50-03 (Knowledge Library Phase -1)
"""

import ast
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import yaml
import json
from datetime import datetime


@dataclass
class CodeEntity:
    """Represents a code entity (class, function, variable)"""

    name: str
    type: str  # 'class', 'function', 'import', 'variable'
    file_path: str
    line_number: int
    signature: Optional[str] = None
    docstring: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)


@dataclass
class Pattern:
    """Represents a detected pattern"""

    pattern_type: str  # 'duplicate', 'architectural', 'refactoring_opportunity'
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    locations: List[Tuple[str, int]]  # (file_path, line_number)
    recommendation: str


@dataclass
class InjectionPoint:
    """Represents an optimal code injection location"""

    file_path: str
    line_number: int
    injection_type: str  # 'class', 'function', 'module_level', 'method'
    context: str  # Surrounding code context
    score: float  # Suitability score (0.0-1.0)
    reasoning: str  # Why this is a good injection point
    surrounding_code: Optional[str] = None  # 3 lines before/after


@dataclass
class SecurityIssue:
    """Represents a detected security vulnerability"""

    severity: str  # 'low', 'medium', 'high', 'critical'
    issue_type: str  # Type of security issue
    file_path: str
    line_number: int
    description: str
    recommendation: str
    code_snippet: Optional[str] = None


@dataclass
class PerformanceIssue:
    """Represents a detected performance anti-pattern"""

    severity: str  # 'low', 'medium', 'high'
    issue_type: str  # Type of performance issue
    file_path: str
    line_number: int
    description: str
    recommendation: str
    estimated_impact: str  # 'minor', 'moderate', 'significant'


@dataclass
class KnowledgeDiscovery:
    """Result of knowledge library scan"""

    timestamp: str
    workspace_path: str
    target_feature: str
    existing_implementations: List[CodeEntity]
    duplicate_code: List[Pattern]
    architectural_patterns: List[Pattern]
    refactoring_opportunities: List[Pattern]
    historical_risks: List[Dict]
    scan_statistics: Dict
    injection_points: List[InjectionPoint] = field(default_factory=list)  # NEW
    security_issues: List[SecurityIssue] = field(default_factory=list)  # NEW
    performance_issues: List[PerformanceIssue] = field(default_factory=list)  # NEW


class KnowledgeLibrary:
    """
    Phase -1 Knowledge Library for Pre-Planning Discovery

    Scans workspace for existing code, patterns, and duplication BEFORE
    planning begins. Integrates with Tier 2 knowledge graph for historical context.
    """

    def __init__(self, workspace_path: str, config_path: Optional[str] = None):
        """
        Initialize Knowledge Library

        Args:
            workspace_path: Root directory to scan
            config_path: Optional path to cortex.config.json
        """
        self.workspace_path = Path(workspace_path)
        self.config_path = (
            Path(config_path) if config_path else self.workspace_path / "cortex.config.json"
        )

        # Load configuration
        self.config = self._load_config()

        # Tier 2 paths
        self.knowledge_graph_path = self.workspace_path / "cortex-brain" / "knowledge-graph.yaml"
        self.lessons_learned_path = self.workspace_path / "cortex-brain" / "lessons-learned.yaml"

        # Scanning state
        self.scanned_files: Set[Path] = set()
        self.discovered_entities: List[CodeEntity] = []
        
        # Initialize AST Scanner (C50-04)
        self.ast_scanner = ASTScanner(str(self.workspace_path))

    def _load_config(self) -> Dict:
        """Load cortex.config.json"""
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                return json.load(f)
        return {
            "scanning": {
                "exclude_patterns": [
                    "*/tests/*",
                    "*/node_modules/*",
                    "*/.venv/*",
                    "*/venv/*",
                    "*/__pycache__/*",
                    "*/.git/*",
                ],
                "include_extensions": [".py", ".js", ".ts", ".jsx", ".tsx"],
            }
        }

    def scan_workspace(self, target_feature: Optional[str] = None, enable_ast_scanning: bool = True) -> KnowledgeDiscovery:
        """
        Scan workspace for existing implementations and patterns

        Args:
            target_feature: Optional feature name for focused scanning
            enable_ast_scanning: Enable enhanced AST scanning (C50-04 feature)

        Returns:
            KnowledgeDiscovery with all found patterns
        """
        print(f"🔍 Knowledge Library: Scanning workspace...")
        scan_start = datetime.now()

        # Step 1: AST scan all Python files
        python_files = self._find_python_files()
        print(f"   Found {len(python_files)} Python files to scan")

        for file_path in python_files:
            self._scan_file(file_path)

        # Step 2: Detect patterns
        duplicates = self._detect_duplicates()
        architecture = self._detect_architectural_patterns()
        refactoring = self._detect_refactoring_opportunities()

        # Step 3: Query knowledge graph for historical context
        historical_risks = self._query_historical_risks(target_feature)

        # Step 4: Filter by target feature if provided
        if target_feature:
            relevant_entities = self._filter_by_feature(target_feature)
        else:
            relevant_entities = self.discovered_entities
        
        # Step 5: Enhanced AST scanning (C50-04)
        injection_points = []
        security_issues = []
        performance_issues = []
        
        if enable_ast_scanning:
            print(f"   🔬 Running enhanced AST analysis...")
            for file_path in list(self.scanned_files)[:10]:  # Limit to first 10 files for demo
                try:
                    # Find injection points
                    points = self.ast_scanner.find_injection_points(str(file_path))
                    injection_points.extend(points)
                    
                    # Detect security issues
                    sec_issues = self.ast_scanner.detect_security_vulnerabilities(str(file_path))
                    security_issues.extend(sec_issues)
                    
                    # Analyze performance
                    perf_issues = self.ast_scanner.analyze_performance_patterns(str(file_path))
                    performance_issues.extend(perf_issues)
                except Exception as e:
                    print(f"   ⚠️  AST scan error for {file_path}: {e}")
            
            print(f"   ✅ AST analysis complete: {len(injection_points)} injection points, {len(security_issues)} security issues, {len(performance_issues)} performance issues")

        scan_duration = (datetime.now() - scan_start).total_seconds()

        return KnowledgeDiscovery(
            timestamp=datetime.now().isoformat(),
            workspace_path=str(self.workspace_path),
            target_feature=target_feature or "FULL_SCAN",
            existing_implementations=relevant_entities,
            duplicate_code=duplicates,
            architectural_patterns=architecture,
            refactoring_opportunities=refactoring,
            historical_risks=historical_risks,
            scan_statistics={
                "files_scanned": len(self.scanned_files),
                "entities_discovered": len(self.discovered_entities),
                "duplicates_found": len(duplicates),
                "duration_seconds": scan_duration,
                "injection_points_found": len(injection_points),  # NEW
                "security_issues_found": len(security_issues),  # NEW
                "performance_issues_found": len(performance_issues),  # NEW
            },
            injection_points=injection_points,  # NEW
            security_issues=security_issues,  # NEW
            performance_issues=performance_issues,  # NEW
        )

    def _find_python_files(self) -> List[Path]:
        """Find all Python files in workspace (respecting exclusions)"""
        python_files = []
        exclude_patterns = self.config.get("scanning", {}).get("exclude_patterns", [])

        for py_file in self.workspace_path.rglob("*.py"):
            # Check exclusions
            if any(pattern.replace("*", "") in str(py_file) for pattern in exclude_patterns):
                continue
            python_files.append(py_file)

        return python_files

    def _scan_file(self, file_path: Path):
        """Scan a single Python file with AST"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))
            self.scanned_files.add(file_path)

            # Extract entities
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._extract_class(node, file_path)
                elif isinstance(node, ast.FunctionDef):
                    self._extract_function(node, file_path)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    self._extract_import(node, file_path)

        except SyntaxError:
            # Skip files with syntax errors
            pass
        except Exception as e:
            print(f"⚠️  Error scanning {file_path}: {e}")

    def _extract_class(self, node: ast.ClassDef, file_path: Path):
        """Extract class information"""
        entity = CodeEntity(
            name=node.name,
            type="class",
            file_path=str(file_path),
            line_number=node.lineno,
            docstring=ast.get_docstring(node),
            dependencies=[base.id for base in node.bases if isinstance(base, ast.Name)],
        )
        self.discovered_entities.append(entity)

    def _extract_function(self, node: ast.FunctionDef, file_path: Path):
        """Extract function information"""
        # Build signature
        args = [arg.arg for arg in node.args.args]
        signature = f"{node.name}({', '.join(args)})"

        entity = CodeEntity(
            name=node.name,
            type="function",
            file_path=str(file_path),
            line_number=node.lineno,
            signature=signature,
            docstring=ast.get_docstring(node),
        )
        self.discovered_entities.append(entity)

    def _extract_import(self, node: ast.AST, file_path: Path):
        """Extract import information"""
        if isinstance(node, ast.Import):
            for alias in node.names:
                entity = CodeEntity(
                    name=alias.name,
                    type="import",
                    file_path=str(file_path),
                    line_number=node.lineno,
                )
                self.discovered_entities.append(entity)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                entity = CodeEntity(
                    name=f"{module}.{alias.name}",
                    type="import",
                    file_path=str(file_path),
                    line_number=node.lineno,
                )
                self.discovered_entities.append(entity)

    def _detect_duplicates(self) -> List[Pattern]:
        """Detect duplicate code by class/function names"""
        duplicates = []
        name_locations: Dict[str, List[Tuple[str, int]]] = {}

        # Group by name
        for entity in self.discovered_entities:
            if entity.type in ["class", "function"]:
                if entity.name not in name_locations:
                    name_locations[entity.name] = []
                name_locations[entity.name].append((entity.file_path, entity.line_number))

        # Find duplicates (same name in different files)
        for name, locations in name_locations.items():
            if len(locations) > 1:
                # Check if different files (not just different lines in same file)
                unique_files = set(loc[0] for loc in locations)
                if len(unique_files) > 1:
                    pattern = Pattern(
                        pattern_type="duplicate",
                        severity="high",
                        description=f"Duplicate implementation of '{name}' found in {len(unique_files)} files",
                        locations=locations,
                        recommendation=f"Consolidate '{name}' into a single shared module to reduce duplication",
                    )
                    duplicates.append(pattern)

        return duplicates

    def _detect_architectural_patterns(self) -> List[Pattern]:
        """Detect architectural patterns (orchestrators, agents, etc.)"""
        patterns = []

        # Detect orchestrator pattern
        orchestrator_count = sum(
            1
            for e in self.discovered_entities
            if e.type == "class" and "orchestrator" in e.name.lower()
        )

        if orchestrator_count > 0:
            locations = [
                (e.file_path, e.line_number)
                for e in self.discovered_entities
                if e.type == "class" and "orchestrator" in e.name.lower()
            ]
            pattern = Pattern(
                pattern_type="architectural",
                severity="info",
                description=f"Orchestrator pattern detected ({orchestrator_count} orchestrators)",
                locations=locations,
                recommendation="Ensure new orchestrators follow existing patterns and extend base classes",
            )
            patterns.append(pattern)

        # Detect agent pattern
        agent_count = sum(
            1 for e in self.discovered_entities if e.type == "class" and "agent" in e.name.lower()
        )

        if agent_count > 0:
            locations = [
                (e.file_path, e.line_number)
                for e in self.discovered_entities
                if e.type == "class" and "agent" in e.name.lower()
            ]
            pattern = Pattern(
                pattern_type="architectural",
                severity="info",
                description=f"Agent pattern detected ({agent_count} agents)",
                locations=locations,
                recommendation="Ensure new agents follow existing patterns and specialize appropriately",
            )
            patterns.append(pattern)

        return patterns

    def _detect_refactoring_opportunities(self) -> List[Pattern]:
        """Detect code that needs refactoring"""
        opportunities = []

        # Large classes (>500 LOC) - simplified detection
        # In production, you'd parse line counts from AST
        for entity in self.discovered_entities:
            if entity.type == "class":
                # Placeholder: In real implementation, count LOC from AST
                # For now, flag classes with >10 methods as potentially large
                pass

        return opportunities

    def _query_historical_risks(self, target_feature: Optional[str]) -> List[Dict]:
        """Query Tier 2 knowledge graph for historical risks"""
        risks = []

        if self.lessons_learned_path.exists():
            try:
                with open(self.lessons_learned_path, "r") as f:
                    lessons = yaml.safe_load(f) or {}

                # Extract relevant lessons
                for lesson in lessons.get("lessons", []):
                    if (
                        target_feature
                        and target_feature.lower() in lesson.get("context", "").lower()
                    ):
                        risks.append(
                            {
                                "source": "lessons-learned",
                                "context": lesson.get("context", ""),
                                "problem": lesson.get("problem", ""),
                                "solution": lesson.get("solution", ""),
                                "date": lesson.get("date", "unknown"),
                            }
                        )
            except Exception as e:
                print(f"⚠️  Error reading lessons-learned: {e}")

        return risks

    def _filter_by_feature(self, target_feature: str) -> List[CodeEntity]:
        """Filter entities relevant to target feature"""
        relevant = []
        feature_keywords = target_feature.lower().split()

        for entity in self.discovered_entities:
            # Check if entity name contains feature keywords
            entity_text = f"{entity.name} {entity.docstring or ''}".lower()
            if any(keyword in entity_text for keyword in feature_keywords):
                relevant.append(entity)

        return relevant
    
    def find_injection_points(self, target_files: List[str], code_type: str = 'auto') -> List[InjectionPoint]:
        """
        Convenience method: Find injection points across multiple files
        
        Args:
            target_files: List of file paths to analyze
            code_type: Type of code to inject
            
        Returns:
            Combined list of injection points from all files
        """
        all_points = []
        for file_path in target_files:
            points = self.ast_scanner.find_injection_points(file_path, code_type)
            all_points.extend(points)
        
        # Sort by score
        all_points.sort(key=lambda x: x.score, reverse=True)
        return all_points
    
    def scan_security_risks(self, target_files: List[str]) -> List[SecurityIssue]:
        """
        Convenience method: Scan for security risks across multiple files
        
        Args:
            target_files: List of file paths to analyze
            
        Returns:
            Combined list of security issues from all files
        """
        all_issues = []
        for file_path in target_files:
            issues = self.ast_scanner.detect_security_vulnerabilities(file_path)
            all_issues.extend(issues)
        
        # Sort by severity (critical > high > medium > low)
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_issues.sort(key=lambda x: severity_order.get(x.severity, 4))
        return all_issues
    
    def scan_performance_issues(self, target_files: List[str]) -> List[PerformanceIssue]:
        """
        Convenience method: Scan for performance issues across multiple files
        
        Args:
            target_files: List of file paths to analyze
            
        Returns:
            Combined list of performance issues from all files
        """
        all_issues = []
        for file_path in target_files:
            issues = self.ast_scanner.analyze_performance_patterns(file_path)
            all_issues.extend(issues)
        
        # Sort by severity
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        all_issues.sort(key=lambda x: severity_order.get(x.severity, 3))
        return all_issues

    def generate_report(
        self, discovery: KnowledgeDiscovery, output_path: Optional[Path] = None
    ) -> str:
        """
        Generate markdown report from knowledge discovery

        Args:
            discovery: KnowledgeDiscovery result
            output_path: Optional path to save report

        Returns:
            Markdown report string
        """
        report_lines = [
            "# 🔍 Knowledge Library Discovery Report",
            "",
            f"**Generated:** {discovery.timestamp}",
            f"**Workspace:** {discovery.workspace_path}",
            f"**Target Feature:** {discovery.target_feature}",
            "",
            "---",
            "",
            "## 📊 Scan Statistics",
            "",
            f"- **Files Scanned:** {discovery.scan_statistics['files_scanned']}",
            f"- **Entities Discovered:** {discovery.scan_statistics['entities_discovered']}",
            f"- **Duplicates Found:** {discovery.scan_statistics['duplicates_found']}",
            f"- **Duration:** {discovery.scan_statistics['duration_seconds']:.2f}s",
            "",
            "---",
            "",
            "## 🔁 Duplicate Code Detected",
            "",
        ]

        if discovery.duplicate_code:
            for dup in discovery.duplicate_code:
                report_lines.append(f"### ⚠️ {dup.description}")
                report_lines.append(f"**Severity:** {dup.severity.upper()}")
                report_lines.append(f"**Locations:**")
                for loc in dup.locations:
                    report_lines.append(f"- `{loc[0]}:{loc[1]}`")
                report_lines.append(f"**Recommendation:** {dup.recommendation}")
                report_lines.append("")
        else:
            report_lines.append("✅ No duplicates detected")
            report_lines.append("")

        report_lines.extend(["---", "", "## 🏗️ Architectural Patterns", ""])

        if discovery.architectural_patterns:
            for pattern in discovery.architectural_patterns:
                report_lines.append(f"### ℹ️ {pattern.description}")
                report_lines.append(f"**Recommendation:** {pattern.recommendation}")
                report_lines.append("")
        else:
            report_lines.append("ℹ️  No specific architectural patterns detected")
            report_lines.append("")

        report_lines.extend(["---", "", "## 📚 Historical Risks", ""])

        if discovery.historical_risks:
            for risk in discovery.historical_risks:
                report_lines.append(f"### ⚠️ {risk['context']}")
                report_lines.append(f"**Problem:** {risk['problem']}")
                report_lines.append(f"**Solution:** {risk['solution']}")
                report_lines.append(f"**Date:** {risk['date']}")
                report_lines.append("")
        else:
            report_lines.append("✅ No historical risks found for this feature")
            report_lines.append("")
        
        # NEW: Injection Points Section (C50-04)
        report_lines.extend(["---", "", "## 🎯 Injection Points (C50-04 AST Analysis)", ""])
        
        if discovery.injection_points:
            for point in discovery.injection_points[:5]:  # Show top 5
                report_lines.append(f"### 📍 {point.file_path}:{point.line_number}")
                report_lines.append(f"**Type:** {point.injection_type}")
                report_lines.append(f"**Score:** {point.score:.2f}/1.0")
                report_lines.append(f"**Reasoning:** {point.reasoning}")
                if point.surrounding_code:
                    report_lines.append(f"**Context:**")
                    report_lines.append(f"```python")
                    report_lines.append(point.surrounding_code.strip())
                    report_lines.append(f"```")
                report_lines.append("")
        else:
            report_lines.append("ℹ️  No injection points analyzed (AST scanning disabled)")
            report_lines.append("")
        
        # NEW: Security Issues Section (C50-04)
        report_lines.extend(["---", "", "## 🔒 Security Issues (C50-04 AST Analysis)", ""])
        
        if discovery.security_issues:
            for issue in discovery.security_issues:
                severity_icon = "🔴" if issue.severity == "critical" else "🟠" if issue.severity == "high" else "🟡"
                report_lines.append(f"### {severity_icon} {issue.issue_type.upper()} - {issue.severity.upper()}")
                report_lines.append(f"**File:** `{issue.file_path}:{issue.line_number}`")
                report_lines.append(f"**Description:** {issue.description}")
                report_lines.append(f"**Recommendation:** {issue.recommendation}")
                if issue.code_snippet:
                    report_lines.append(f"**Code:**")
                    report_lines.append(f"```python")
                    report_lines.append(issue.code_snippet)
                    report_lines.append(f"```")
                report_lines.append("")
        else:
            report_lines.append("✅ No security issues detected")
            report_lines.append("")
        
        # NEW: Performance Issues Section (C50-04)
        report_lines.extend(["---", "", "## ⚡ Performance Issues (C50-04 AST Analysis)", ""])
        
        if discovery.performance_issues:
            for issue in discovery.performance_issues:
                severity_icon = "🔴" if issue.severity == "high" else "🟠" if issue.severity == "medium" else "🟡"
                report_lines.append(f"### {severity_icon} {issue.issue_type.upper()} - {issue.severity.upper()}")
                report_lines.append(f"**File:** `{issue.file_path}:{issue.line_number}`")
                report_lines.append(f"**Description:** {issue.description}")
                report_lines.append(f"**Impact:** {issue.estimated_impact}")
                report_lines.append(f"**Recommendation:** {issue.recommendation}")
                report_lines.append("")
        else:
            report_lines.append("✅ No performance issues detected")
            report_lines.append("")

        report_lines.extend(["---", "", f"**Copyright © 2026 Asif Hussain. All rights reserved.**"])

        report = "\n".join(report_lines)

        # Save if path provided
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write(report)
            print(f"📄 Report saved: {output_path}")

        return report


class ASTScanner:
    """
    Enhanced AST Scanner for Injection Point Detection, Security, and Performance Analysis
    
    Extends Knowledge Library with intelligent code structure analysis to find:
    - Optimal injection points for new code
    - Security vulnerabilities and anti-patterns
    - Performance bottlenecks and optimization opportunities
    
    Used by Planning Orchestrator v5 in Phase -1 for informed planning decisions.
    
    Version: 1.0
    Author: CORTEX
    Created: 2026-01-04
    Sub-Plan: C50-04 (AST Scanning Integration)
    """
    
    def __init__(self, workspace_path: str):
        """
        Initialize AST Scanner
        
        Args:
            workspace_path: Root directory to scan
        """
        self.workspace_path = Path(workspace_path)
        
        # Security patterns to detect
        self.security_patterns = {
            'hardcoded_secret': {
                'pattern': ['password', 'api_key', 'secret', 'token', 'credential'],
                'severity': 'high'
            },
            'sql_injection': {
                'pattern': ['execute', 'cursor', 'query'],
                'severity': 'critical'
            },
            'command_injection': {
                'pattern': ['shell=True', 'os.system', 'subprocess.call'],
                'severity': 'critical'
            },
            'unsafe_deserialization': {
                'pattern': ['pickle.loads', 'yaml.load', 'eval', 'exec'],
                'severity': 'high'
            }
        }
        
    def analyze_code_structure(self, file_path: str) -> Dict:
        """
        Analyze code structure of a Python file
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Dict with structure analysis (classes, functions, complexity, etc.)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=file_path)
            
            structure = {
                'file_path': file_path,
                'classes': [],
                'functions': [],
                'imports': [],
                'module_level_code': [],
                'complexity_score': 0,
                'line_count': len(source.split('\n'))
            }
            
            # Walk AST and extract structure
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    structure['classes'].append({
                        'name': node.name,
                        'line_number': node.lineno,
                        'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                        'bases': [self._get_node_name(b) for b in node.bases]
                    })
                elif isinstance(node, ast.FunctionDef):
                    # Only module-level functions (not class methods)
                    if not any(isinstance(p, ast.ClassDef) for p in ast.walk(tree) if hasattr(p, 'body') and node in getattr(p, 'body', [])):
                        structure['functions'].append({
                            'name': node.name,
                            'line_number': node.lineno,
                            'args': [arg.arg for arg in node.args.args]
                        })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    structure['imports'].append({
                        'line_number': node.lineno,
                        'type': 'import' if isinstance(node, ast.Import) else 'import_from'
                    })
            
            # Calculate cyclomatic complexity
            structure['complexity_score'] = self._calculate_complexity(tree)
            
            return structure
            
        except SyntaxError as e:
            return {'error': f'Syntax error: {e}', 'file_path': file_path}
        except Exception as e:
            return {'error': f'Analysis error: {e}', 'file_path': file_path}
    
    def find_injection_points(
        self,
        file_path: str,
        code_type: str = 'auto'
    ) -> List[InjectionPoint]:
        """
        Find optimal injection points for new code
        
        Args:
            file_path: Path to Python file
            code_type: Type of code to inject ('class', 'function', 'method', 'import', 'auto')
            
        Returns:
            List of InjectionPoint objects ranked by suitability
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_lines = f.readlines()
                source = ''.join(source_lines)
            
            tree = ast.parse(source, filename=file_path)
            injection_points = []
            
            # Find class end points (good for adding new methods)
            if code_type in ['method', 'auto']:
                injection_points.extend(self._find_class_injection_points(tree, source_lines, file_path))
            
            # Find module-level injection points (good for new classes/functions)
            if code_type in ['class', 'function', 'auto']:
                injection_points.extend(self._find_module_injection_points(tree, source_lines, file_path))
            
            # Find import section injection points
            if code_type in ['import', 'auto']:
                injection_points.extend(self._find_import_injection_points(tree, source_lines, file_path))
            
            # Sort by score (highest first)
            injection_points.sort(key=lambda x: x.score, reverse=True)
            
            return injection_points[:10]  # Return top 10
            
        except Exception as e:
            print(f"⚠️  Error finding injection points in {file_path}: {e}")
            return []
    
    def _find_class_injection_points(
        self,
        tree: ast.AST,
        source_lines: List[str],
        file_path: str
    ) -> List[InjectionPoint]:
        """Find injection points at end of classes (for new methods)"""
        points = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Find last method in class
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if methods:
                    last_method = methods[-1]
                    injection_line = last_method.end_lineno + 1
                    
                    # Score this injection point
                    score = 0.7  # Base score for end-of-class
                    reasoning = f"End of class '{node.name}' - follows existing method pattern"
                    
                    # Bonus: If class has docstring
                    if ast.get_docstring(node):
                        score += 0.1
                        reasoning += ", documented class"
                    
                    # Context: Get surrounding lines
                    context = self._get_context(source_lines, injection_line, before=2, after=2)
                    
                    points.append(InjectionPoint(
                        file_path=file_path,
                        line_number=injection_line,
                        injection_type='method',
                        context=node.name,
                        score=score,
                        reasoning=reasoning,
                        surrounding_code=context
                    ))
        
        return points
    
    def _find_module_injection_points(
        self,
        tree: ast.AST,
        source_lines: List[str],
        file_path: str
    ) -> List[InjectionPoint]:
        """Find injection points at module level (for new classes/functions)"""
        points = []
        
        # Find last class or function at module level
        module_level_nodes = [n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef))]
        
        if module_level_nodes:
            last_node = module_level_nodes[-1]
            injection_line = last_node.end_lineno + 2  # Add spacing
            
            score = 0.8  # High score for end-of-module
            reasoning = f"End of module - follows existing structure"
            
            # Context
            context = self._get_context(source_lines, injection_line, before=3, after=1)
            
            points.append(InjectionPoint(
                file_path=file_path,
                line_number=injection_line,
                injection_type='class' if 'class' in reasoning else 'function',
                context='module_level',
                score=score,
                reasoning=reasoning,
                surrounding_code=context
            ))
        
        return points
    
    def _find_import_injection_points(
        self,
        tree: ast.AST,
        source_lines: List[str],
        file_path: str
    ) -> List[InjectionPoint]:
        """Find injection points in import section"""
        points = []
        
        # Find last import
        imports = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
        
        if imports:
            last_import = imports[-1]
            injection_line = last_import.end_lineno + 1
            
            score = 0.9  # Very high score for import section
            reasoning = "End of import section - maintains clean structure"
            
            context = self._get_context(source_lines, injection_line, before=2, after=2)
            
            points.append(InjectionPoint(
                file_path=file_path,
                line_number=injection_line,
                injection_type='import',
                context='import_section',
                score=score,
                reasoning=reasoning,
                surrounding_code=context
            ))
        
        return points
    
    def detect_security_vulnerabilities(self, file_path: str) -> List[SecurityIssue]:
        """
        Detect security vulnerabilities in Python code
        
        Args:
            file_path: Path to Python file
            
        Returns:
            List of SecurityIssue objects
        """
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_lines = f.readlines()
                source = ''.join(source_lines)
            
            tree = ast.parse(source, filename=file_path)
            
            # Walk AST and detect patterns
            for node in ast.walk(tree):
                # Detect hardcoded secrets
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            var_name = target.id.lower()
                            if any(pattern in var_name for pattern in ['password', 'secret', 'api_key', 'token']):
                                issues.append(SecurityIssue(
                                    severity='high',
                                    issue_type='hardcoded_secret',
                                    file_path=file_path,
                                    line_number=node.lineno,
                                    description=f"Potential hardcoded secret in variable '{target.id}'",
                                    recommendation="Use environment variables or secrets manager",
                                    code_snippet=source_lines[node.lineno - 1].strip() if node.lineno <= len(source_lines) else None
                                ))
                
                # Detect eval/exec usage
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in ['eval', 'exec']:
                        issues.append(SecurityIssue(
                            severity='critical',
                            issue_type='unsafe_deserialization',
                            file_path=file_path,
                            line_number=node.lineno,
                            description=f"Use of {node.func.id}() - arbitrary code execution risk",
                            recommendation="Avoid eval/exec - use safer alternatives like ast.literal_eval()",
                            code_snippet=source_lines[node.lineno - 1].strip() if node.lineno <= len(source_lines) else None
                        ))
                
                # Detect shell=True in subprocess
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                        if node.func.value.id == 'subprocess':
                            for keyword in node.keywords:
                                if keyword.arg == 'shell' and isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                                    issues.append(SecurityIssue(
                                        severity='critical',
                                        issue_type='command_injection',
                                        file_path=file_path,
                                        line_number=node.lineno,
                                        description="Use of shell=True in subprocess - command injection risk",
                                        recommendation="Use shell=False and pass command as list",
                                        code_snippet=source_lines[node.lineno - 1].strip() if node.lineno <= len(source_lines) else None
                                    ))
            
        except Exception as e:
            print(f"⚠️  Error detecting security issues in {file_path}: {e}")
        
        return issues
    
    def analyze_performance_patterns(self, file_path: str) -> List[PerformanceIssue]:
        """
        Analyze code for performance anti-patterns
        
        Args:
            file_path: Path to Python file
            
        Returns:
            List of PerformanceIssue objects
        """
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_lines = f.readlines()
                source = ''.join(source_lines)
            
            tree = ast.parse(source, filename=file_path)
            
            # Detect nested loops (O(n²) complexity)
            for node in ast.walk(tree):
                if isinstance(node, ast.For):
                    # Check if this for loop contains another for loop
                    for child in ast.walk(node):
                        if child != node and isinstance(child, ast.For):
                            issues.append(PerformanceIssue(
                                severity='medium',
                                issue_type='nested_loops',
                                file_path=file_path,
                                line_number=node.lineno,
                                description="Nested loop detected - potential O(n²) complexity",
                                recommendation="Consider using dictionary lookup, set operations, or list comprehension",
                                estimated_impact='moderate'
                            ))
                            break
                
                # Detect high cyclomatic complexity
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_function_complexity(node)
                    if complexity > 10:
                        issues.append(PerformanceIssue(
                            severity='high' if complexity > 15 else 'medium',
                            issue_type='high_complexity',
                            file_path=file_path,
                            line_number=node.lineno,
                            description=f"Function '{node.name}' has high cyclomatic complexity ({complexity})",
                            recommendation="Refactor into smaller functions - target complexity < 10",
                            estimated_impact='significant' if complexity > 15 else 'moderate'
                        ))
            
        except Exception as e:
            print(f"⚠️  Error analyzing performance in {file_path}: {e}")
        
        return issues
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate overall cyclomatic complexity of AST"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a single function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _get_context(
        self,
        source_lines: List[str],
        line_number: int,
        before: int = 3,
        after: int = 3
    ) -> str:
        """Get context lines around a specific line number"""
        start = max(0, line_number - before - 1)
        end = min(len(source_lines), line_number + after)
        return ''.join(source_lines[start:end])
    
    def _get_node_name(self, node: ast.AST) -> str:
        """Get name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_node_name(node.value)}.{node.attr}"
        return str(node)


# Convenience function for quick scanning
def quick_scan(workspace_path: str, target_feature: Optional[str] = None) -> KnowledgeDiscovery:
    """
    Quick scan of workspace

    Args:
        workspace_path: Root directory to scan
        target_feature: Optional feature name for focused scanning

    Returns:
        KnowledgeDiscovery result
    """
    library = KnowledgeLibrary(workspace_path)
    return library.scan_workspace(target_feature)


if __name__ == "__main__":
    # Demo usage
    import sys

    # Detect project root dynamically
    from pathlib import Path
    import sys
    
    # Try to import project_root utility
    try:
        from src.utils.project_root import get_project_root
        workspace = str(get_project_root())
    except ImportError:
        # Fallback: use current file location to find root
        current = Path(__file__).resolve()
        for parent in [current.parent] + list(current.parents):
            if (parent / "cortex.config.json").exists():
                workspace = str(parent)
                break
        else:
            workspace = str(current.parent.parent.parent)  # src/cortex_agents -> root
    
    workspace = sys.argv[1] if len(sys.argv) > 1 else workspace
    feature = sys.argv[2] if len(sys.argv) > 2 else None

    print("🧠 CORTEX Knowledge Library - Phase -1 Discovery")
    print("=" * 60)

    library = KnowledgeLibrary(workspace)
    discovery = library.scan_workspace(feature)

    # Generate report
    report_path = (
        Path(workspace) / "cortex-brain" / "documents" / "analysis" / "knowledge-discovery.md"
    )
    report = library.generate_report(discovery, report_path)

    print("\n" + "=" * 60)
    print(f"✅ Discovery complete!")
    print(f"📊 {discovery.scan_statistics['entities_discovered']} entities discovered")
    print(f"🔁 {len(discovery.duplicate_code)} duplicates found")
    print(f"📚 {len(discovery.historical_risks)} historical risks surfaced")
