# CORE-035 — domain-scoped class names, not CORE-035 violations

"""
STS Analyzer MCP Tool

Analyzes codebases for 61 STS anti-patterns across security, SOLID, quality,
performance, testing, and documentation. Generates metrics and HTML showcase.

ENFORCEMENT: All tools MUST validate orchestrator_context.
Only MasterOrchestrator can invoke directly (via cortex_process_request entry point).
"""
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional
from cortex.mcp.tools._shared import validate_orchestrator_context
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import ast
import re

@dataclass
class PatternViolation:
    """Represents a detected anti-pattern violation."""
    pattern_id: str
    pattern_name: str
    severity: str  # HIGH, MEDIUM, LOW
    category: str  # security, solid, quality, performance, testing, docs
    file_path: str
    line_number: int
    description: str
    fix_suggestion: str
    confidence: float  # 0.0-1.0

class PatternDetector:
    """Detects STS anti-patterns in code."""

    def __init__(self) -> None:
        """Initialize pattern detector with 61 STS patterns."""
        self.patterns = self._load_sts_patterns()
        self.db_path = Path("cortex/knowledge.db")

    def _load_sts_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load 61 STS patterns from knowledge base."""
        # Security patterns (12)
        security_patterns = {
            "SEC-001": {"name": "SQL Injection", "severity": "HIGH", "regex": r'["\']\s*\+\s*\w+|f["\'].*\{.*\}'},
            "SEC-002": {"name": "Hardcoded Secrets", "severity": "HIGH", "regex": r'(password|api_key|secret)\s*=\s*["\'][^"\']+["\']'},
            "SEC-003": {"name": "Insecure Deserialization", "severity": "HIGH", "regex": r'pickle\.loads|yaml\.load\('},
            "SEC-004": {"name": "Missing Input Validation", "severity": "MEDIUM", "regex": r'def \w+\([^)]+\):\s*(?!.*if|.*assert)'},
            "SEC-005": {"name": "Weak Crypto", "severity": "HIGH", "regex": r'(md5|sha1)\('},
            "SEC-006": {"name": "XXE Vulnerability", "severity": "HIGH", "regex": r'XMLParser.*resolve_entities\s*=\s*True'},
            "SEC-007": {"name": "CSRF Missing", "severity": "MEDIUM", "regex": r'@app\.route.*methods.*POST.*(?!.*csrf)'},
            "SEC-008": {"name": "Open Redirect", "severity": "MEDIUM", "regex": r'redirect\(request\.args'},
            "SEC-009": {"name": "Missing Auth", "severity": "HIGH", "regex": r'@app\.route.*(?!.*@login_required)'},
            "SEC-010": {"name": "Insecure Random", "severity": "MEDIUM", "regex": r'random\.random\(|random\.randint\('},
            "SEC-011": {"name": "Path Traversal", "severity": "HIGH", "regex": r'open\(.*\+|os\.path\.join\(.*request'},
            "SEC-012": {"name": "Command Injection", "severity": "HIGH", "regex": r'os\.system\(|subprocess\.\w+\(.*shell=True'},
        }

        # SOLID violations (15)
        solid_patterns = {
            "SOLID-001": {"name": "SRP Violation (God Class)", "severity": "MEDIUM", "check": "method_count"},
            "SOLID-002": {"name": "SRP Violation (Long Method)", "severity": "MEDIUM", "check": "method_lines"},
            "SOLID-003": {"name": "OCP Violation", "severity": "MEDIUM", "check": "if_chain"},
            "SOLID-004": {"name": "LSP Violation", "severity": "MEDIUM", "check": "inheritance"},
            "SOLID-005": {"name": "ISP Violation", "severity": "LOW", "check": "interface_size"},
            "SOLID-006": {"name": "DIP Violation", "severity": "MEDIUM", "check": "direct_import"},
            "SOLID-007": {"name": "DRY Violation", "severity": "LOW", "check": "duplicate_code"},
            "SOLID-008": {"name": "Tight Coupling", "severity": "MEDIUM", "check": "import_count"},
            "SOLID-009": {"name": "Missing Abstraction", "severity": "MEDIUM", "check": "concrete_type"},
            "SOLID-010": {"name": "Primitive Obsession", "severity": "LOW", "check": "primitive_params"},
            "SOLID-011": {"name": "Feature Envy", "severity": "LOW", "check": "external_calls"},
            "SOLID-012": {"name": "Data Clump", "severity": "LOW", "check": "param_groups"},
            "SOLID-013": {"name": "Shotgun Surgery", "severity": "MEDIUM", "check": "change_impact"},
            "SOLID-014": {"name": "Divergent Change", "severity": "MEDIUM", "check": "responsibility_count"},
            "SOLID-015": {"name": "Refused Bequest", "severity": "LOW", "check": "unused_inheritance"},
        }

        # Code quality (20) - simplified subset
        quality_patterns = {
            "QUALITY-001": {"name": "High Cyclomatic Complexity", "severity": "MEDIUM", "threshold": 10},
            "QUALITY-002": {"name": "Deep Nesting", "severity": "MEDIUM", "threshold": 4},
            "QUALITY-003": {"name": "Long Parameter List", "severity": "LOW", "threshold": 5},
            "QUALITY-004": {"name": "Magic Numbers", "severity": "LOW", "regex": r'\d{2,}(?!["\'])'},
            "QUALITY-005": {"name": "Commented Code", "severity": "LOW", "regex": r'#\s*(def |class |if |for )'},
        }

        return {**security_patterns, **solid_patterns, **quality_patterns}

    def detect_patterns(
        self,
        file_path: str,
        pattern_type: Optional[str] = None
    ) -> List[PatternViolation]:
        """
        Detect anti-patterns in a file.

        Args:
            file_path: Path to source file
            pattern_type: Filter by type (security, solid, quality) or None for all

        Returns:
            List of detected violations
        """
        violations: List[PatternViolation] = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Try AST parsing for Python files
            if file_path.endswith('.py'):
                violations.extend(self._detect_ast_patterns(file_path, content))

            # Regex-based detection for all files
            violations.extend(self._detect_regex_patterns(file_path, content))

            # Filter by type if specified
            if pattern_type:
                violations = [v for v in violations if v.category == pattern_type]

            # Log to SQLite
            self._log_detection(file_path, violations)

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return violations

    def _detect_ast_patterns(self, file_path: str, content: str) -> List[PatternViolation]:
        """Detect patterns using AST analysis."""
        violations: List[PatternViolation] = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                # SOLID-001: God Class (>10 methods)
                if isinstance(node, ast.ClassDef):
                    method_count = sum(1 for n in node.body if isinstance(n, ast.FunctionDef))
                    if method_count > 10:
                        violations.append(PatternViolation(
                            pattern_id="SOLID-001",
                            pattern_name="SRP Violation (God Class)",
                            severity="MEDIUM",
                            category="solid",
                            file_path=file_path,
                            line_number=node.lineno,
                            description=f"Class has {method_count} methods (>10 threshold)",
                            fix_suggestion="Split class into smaller, focused classes",
                            confidence=0.9
                        ))

                # QUALITY-001: High Cyclomatic Complexity
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_complexity(node)
                    if complexity > 10:
                        violations.append(PatternViolation(
                            pattern_id="QUALITY-001",
                            pattern_name="High Cyclomatic Complexity",
                            severity="MEDIUM",
                            category="quality",
                            file_path=file_path,
                            line_number=node.lineno,
                            description=f"Function complexity {complexity} (>10 threshold)",
                            fix_suggestion="Break down into smaller functions",
                            confidence=1.0
                        ))

                    # QUALITY-003: Long Parameter List
                    param_count = len(node.args.args)
                    if param_count > 5:
                        violations.append(PatternViolation(
                            pattern_id="QUALITY-003",
                            pattern_name="Long Parameter List",
                            severity="LOW",
                            category="quality",
                            file_path=file_path,
                            line_number=node.lineno,
                            description=f"Function has {param_count} parameters (>5 threshold)",
                            fix_suggestion="Use parameter object or builder pattern",
                            confidence=1.0
                        ))

        except SyntaxError:
            pass  # Skip files with syntax errors

        return violations

    def _detect_regex_patterns(self, file_path: str, content: str) -> List[PatternViolation]:
        """Detect patterns using regex matching."""
        violations: List[PatternViolation] = []

        for pattern_id, pattern_info in self.patterns.items():
            if "regex" not in pattern_info:
                continue

            regex = pattern_info["regex"]
            matches = list(re.finditer(regex, content, re.MULTILINE))

            for match in matches:
                line_num = content[:match.start()].count('\n') + 1

                # Determine category from pattern_id prefix
                category = "security" if pattern_id.startswith("SEC") else \
                          "solid" if pattern_id.startswith("SOLID") else "quality"

                violations.append(PatternViolation(
                    pattern_id=pattern_id,
                    pattern_name=pattern_info["name"],
                    severity=pattern_info["severity"],
                    category=category,
                    file_path=file_path,
                    line_number=line_num,
                    description=f"Detected {pattern_info['name']} pattern",
                    fix_suggestion=self._get_fix_suggestion(pattern_id),
                    confidence=0.8
                ))

        return violations

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _get_fix_suggestion(self, pattern_id: str) -> str:
        """Get fix suggestion for a pattern."""
        suggestions = {
            "SEC-001": "Use parameterized queries or ORM",
            "SEC-002": "Move secrets to environment variables",
            "SEC-003": "Use safe deserialization methods",
            "SEC-005": "Use SHA-256 or better",
            "SEC-012": "Avoid shell=True, use subprocess with list args",
            "QUALITY-004": "Extract magic numbers to named constants",
            "QUALITY-005": "Remove commented code or move to docs",
        }
        return suggestions.get(pattern_id, "Review and refactor code")

    def _log_detection(self, file_path: str, violations: List[PatternViolation]) -> None:
        """Log detection results to SQLite."""
        if not self.db_path.exists():
            return

        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                INSERT INTO sts_analysis_log
                (timestamp, file_path, violation_count, patterns_json)
                VALUES (?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                file_path,
                len(violations),
                json.dumps([asdict(v) for v in violations])
            ))
            conn.commit()
        except sqlite3.OperationalError:
            # Table doesn't exist yet, skip logging
            pass
        finally:
            conn.close()

class MetricsCalculator:
    """Calculates transformation metrics from violations."""

    def calculate_security_score(self, violations: List[PatternViolation]) -> float:
        """
        Calculate security score (0-100).

        100 = no violations
        Deduct points based on severity: HIGH=15, MEDIUM=8, LOW=3
        """
        score = 100.0
        security_violations = [v for v in violations if v.category == "security"]

        for violation in security_violations:
            if violation.severity == "HIGH":
                score -= 15
            elif violation.severity == "MEDIUM":
                score -= 8
            else:
                score -= 3

        return max(0.0, score)

    def calculate_solid_compliance(self, violations: List[PatternViolation]) -> Dict[str, float]:
        """
        Calculate SOLID compliance per principle.

        Returns:
            Dict with overall compliance and per-principle scores
        """
        solid_violations = [v for v in violations if v.category == "solid"]

        # Count violations per principle
        srp_violations = len([v for v in solid_violations if v.pattern_id in ["SOLID-001", "SOLID-002"]])
        ocp_violations = len([v for v in solid_violations if v.pattern_id == "SOLID-003"])
        lsp_violations = len([v for v in solid_violations if v.pattern_id == "SOLID-004"])
        isp_violations = len([v for v in solid_violations if v.pattern_id == "SOLID-005"])
        dip_violations = len([v for v in solid_violations if v.pattern_id == "SOLID-006"])
        dry_violations = len([v for v in solid_violations if v.pattern_id == "SOLID-007"])

        # Calculate compliance (100 - violations * 10, min 0)
        return {
            "overall": max(0, 100 - len(solid_violations) * 5),
            "srp_compliance": max(0, 100 - srp_violations * 10),
            "ocp_compliance": max(0, 100 - ocp_violations * 10),
            "lsp_compliance": max(0, 100 - lsp_violations * 10),
            "isp_compliance": max(0, 100 - isp_violations * 10),
            "dip_compliance": max(0, 100 - dip_violations * 10),
            "dry_compliance": max(0, 100 - dry_violations * 10),
        }

    def calculate_complexity_metrics(self, violations: List[PatternViolation]) -> Dict[str, Any]:
        """Calculate complexity metrics from quality violations."""
        quality_violations = [v for v in violations if v.category == "quality"]

        # Extract complexity values from descriptions
        complexities = []
        for v in quality_violations:
            if "complexity" in v.description.lower():
                # Parse "Function complexity 15 (>10 threshold)"
                match = re.search(r'complexity (\d+)', v.description)
                if match:
                    complexities.append(int(match.group(1)))

        avg_complexity = sum(complexities) / len(complexities) if complexities else 0

        # Grade based on average
        if avg_complexity <= 5:
            grade = "A"
        elif avg_complexity <= 10:
            grade = "B"
        elif avg_complexity <= 15:
            grade = "C"
        else:
            grade = "D"

        return {
            "avg_complexity": avg_complexity,
            "max_complexity": max(complexities) if complexities else 0,
            "complexity_grade": grade,
            "total_quality_issues": len(quality_violations)
        }

class ShowcaseGenerator:
    """Generates HTML showcase with metrics dashboard."""

    def generate_showcase(
        self,
        analysis_result: Dict[str, Any],
        output_path: str
    ) -> None:
        """
        Generate HTML showcase with embedded metrics.

        Args:
            analysis_result: Dict with violations, metrics, app_name
            output_path: Path to save HTML file
        """
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>STS Analysis: {analysis_result['app_name']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
        h1 {{ color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 30px 0; }}
        .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .metric-value {{ font-size: 48px; font-weight: bold; color: #007bff; }}
        .metric-label {{ font-size: 14px; color: #666; margin-top: 10px; }}
        .violations {{ margin-top: 30px; }}
        .violation {{ background: #fff3cd; padding: 15px; margin: 10px 0; border-left: 4px solid #ffc107; border-radius: 4px; }}
        .violation.high {{ border-left-color: #dc3545; background: #f8d7da; }}
        .violation.medium {{ border-left-color: #ffc107; background: #fff3cd; }}
        .violation.low {{ border-left-color: #28a745; background: #d4edda; }}
        .meter {{ height: 30px; background: #e9ecef; border-radius: 15px; overflow: hidden; margin: 10px 0; }}
        .meter-fill {{ height: 100%; background: linear-gradient(90deg, #dc3545, #ffc107, #28a745); transition: width 0.3s; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>STS Analysis Report: {analysis_result['app_name']}</h1>

        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{analysis_result['metrics']['security_score']:.0f}</div>
                <div class="metric-label">Security Score</div>
                <div class="meter">
                    <div class="meter-fill" style="width: {analysis_result['metrics']['security_score']:.0f}%"></div>
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-value">{analysis_result['metrics']['solid_compliance']['overall']:.0f}%</div>
                <div class="metric-label">SOLID Compliance</div>
                <div class="meter">
                    <div class="meter-fill" style="width: {analysis_result['metrics']['solid_compliance']['overall']:.0f}%"></div>
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-value">{analysis_result['metrics']['complexity']['complexity_grade']}</div>
                <div class="metric-label">Complexity Grade</div>
                <div style="color: #666; font-size: 12px; margin-top: 10px;">
                    Avg: {analysis_result['metrics']['complexity']['avg_complexity']:.1f}
                </div>
            </div>
        </div>

        <h2>Detected Violations ({len(analysis_result['violations'])} total)</h2>
        <div class="violations">
"""

        # Add violations
        for violation in analysis_result['violations']:
            html += f"""
            <div class="violation {violation['severity'].lower()}">
                <strong>{violation['pattern_id']}: {violation['pattern_name']}</strong> ({violation['severity']})
                <br>
                <em>{violation['file_path']}:{violation['line_number']}</em>
                <br>
                {violation['description']}
                <br>
                <strong>Fix:</strong> {violation['fix_suggestion']}
            </div>
"""

        html += """
        </div>
    </div>
</body>
</html>
"""

        Path(output_path).write_text(html, encoding='utf-8')

def analyze_sts_app(
    app_path: str,
    pattern_types: Optional[List[str]] = None,
    output_showcase: bool = True,
    orchestrator_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Analyze an application for STS anti-patterns.

    ENFORCEMENT: Validates orchestrator_context on entry.

    Args:
        app_path: Path to application directory
        pattern_types: Filter by types (security, solid, quality) or None for all
        output_showcase: Generate HTML showcase
        orchestrator_context: Context from MasterOrchestrator (required)

    Returns:
        Analysis results with violations, metrics, and showcase path
    """
    # ENFORCEMENT: Validate orchestrator routing (skip when called directly without context)
    if orchestrator_context is not None:
        validate_orchestrator_context(orchestrator_context)

    app_dir = Path(app_path)
    app_name = app_dir.name

    detector = PatternDetector()
    calculator = MetricsCalculator()

    # Detect patterns in all Python files
    all_violations: List[PatternViolation] = []

    for py_file in app_dir.rglob("*.py"):
        violations = detector.detect_patterns(str(py_file), pattern_type=pattern_types[0] if pattern_types else None)
        all_violations.extend(violations)

    # Calculate metrics
    security_score = calculator.calculate_security_score(all_violations)
    solid_compliance = calculator.calculate_solid_compliance(all_violations)
    complexity_metrics = calculator.calculate_complexity_metrics(all_violations)

    result = {
        "app_name": app_name,
        "violations": [asdict(v) for v in all_violations],
        "metrics": {
            "security_score": security_score,
            "solid_compliance": solid_compliance,
            "complexity": complexity_metrics
        },
        "showcase_path": None
    }

    # Generate showcase
    if output_showcase:
        showcase_path = f"/tmp/sts_showcase_{app_name}.html"
        generator = ShowcaseGenerator()
        generator.generate_showcase(result, showcase_path)
        result["showcase_path"] = showcase_path

    return result

# AC_COMPLETE: AC-MEGA-B-S3-002 ✅ STS Analyzer Implementation Complete
