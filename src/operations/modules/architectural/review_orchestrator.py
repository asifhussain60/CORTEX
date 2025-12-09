"""
Comprehensive Architectural Review Orchestrator

Performs holistic code and architecture analysis from a senior architect perspective.
Examines structure, patterns, SOLID principles, API design, security, scalability,
and maintainability.

Author: Asif Hussain
Version: 3.8.1
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationResult,
    OperationStatus,
    OperationModuleMetadata
)
from src.utils.progress_decorator import with_progress, yield_progress
from src.operations.modules.git_protection.alignment_state_tracker import AlignmentStateTracker


@dataclass
class ReviewFinding:
    """Represents a single review finding."""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # Architecture, Code Quality, Security, Performance, etc.
    title: str
    description: str
    location: Optional[str] = None
    recommendation: Optional[str] = None
    root_cause: Optional[str] = None


@dataclass
class ReviewSection:
    """Represents a section of the review."""
    name: str
    score: int  # 0-100
    findings: List[ReviewFinding]
    summary: str
    recommendations: List[str]


class ReviewOrchestrator(BaseOperationModule):
    """
    Comprehensive architectural and code quality review orchestrator.
    
    Performs multi-phase analysis:
    1. Architecture & Structure
    2. Code Quality & Patterns
    3. Security & Risk Assessment
    4. Performance & Scalability
    5. Maintainability & Technical Debt
    """
    
    def __init__(self):
        super().__init__()
        self.workspace_path = self._detect_workspace_path()
        self.findings: List[ReviewFinding] = []
        self.sections: List[ReviewSection] = []
        self.alignment_tracker = AlignmentStateTracker(self.workspace_path)
        
        # Context-aware review support (added 2025-12-09)
        self.scope_filter: List[str] = []
        self.request_context: str = ""
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            name="review",
            description="Comprehensive architectural and code quality review",
            version="1.0.0",
            author="Asif Hussain"
        )
    
    def _detect_workspace_path(self) -> Path:
        """Detect workspace path from context or environment."""
        # Try to get from environment or use current directory
        workspace = os.environ.get('CORTEX_WORKSPACE', os.getcwd())
        return Path(workspace)
    
    @with_progress(operation_name="Architectural Review", threshold_seconds=3.0)
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute comprehensive architectural review.
        
        Args:
            context: Operation context with optional keys:
                - 'path': Workspace path override
                - 'scope_filter': List of scope keywords (e.g., ['auth', 'api'])
                - 'request_context': User's feature request for contextual analysis
            
        Returns:
            OperationResult with review findings and report path
        """
        try:
            # Override workspace path if provided in context
            if 'path' in context:
                self.workspace_path = Path(context['path'])
            
            # Store scope context for filtering
            self.scope_filter = context.get('scope_filter', [])
            self.request_context = context.get('request_context', '')
            
            if self.scope_filter:
                logger.info(f"🎯 Scoped review: {', '.join(self.scope_filter)}")
            
            # Phase 1: Architecture & Structure Analysis
            yield_progress(1, 6, "Phase 1: Analyzing architecture and structure")
            arch_section = self._analyze_architecture()
            self.sections.append(arch_section)
            
            # Phase 2: Code Quality & Patterns
            yield_progress(2, 6, "Phase 2: Analyzing code quality and patterns")
            quality_section = self._analyze_code_quality()
            self.sections.append(quality_section)
            
            # Phase 3: SOLID Principles & Design Patterns
            yield_progress(3, 6, "Phase 3: Evaluating SOLID principles")
            solid_section = self._analyze_solid_principles()
            self.sections.append(solid_section)
            
            # Phase 4: Security & Risk Assessment
            yield_progress(4, 6, "Phase 4: Assessing security and risks")
            security_section = self._analyze_security()
            self.sections.append(security_section)
            
            # Phase 5: Performance & Scalability
            yield_progress(5, 6, "Phase 5: Evaluating performance and scalability")
            performance_section = self._analyze_performance()
            self.sections.append(performance_section)
            
            # Phase 6: Generate Report
            yield_progress(6, 6, "Phase 6: Generating comprehensive report")
            report_path = self._generate_report()
            
            # Calculate overall score
            overall_score = sum(s.score for s in self.sections) // len(self.sections)
            
            # Mark reviewed files in alignment tracker
            self._mark_reviewed_files(overall_score)
            
            # Convert sections to dicts for serialization (include findings)
            sections_data = []
            for section in self.sections:
                findings_data = []
                for finding in section.findings:
                    findings_data.append({
                        'severity': finding.severity,
                        'category': finding.category,
                        'title': finding.title,
                        'description': finding.description,
                        'location': finding.location,
                        'recommendation': finding.recommendation,
                        'root_cause': finding.root_cause
                    })
                
                sections_data.append({
                    'name': section.name,
                    'score': section.score,
                    'findings': findings_data,
                    'summary': section.summary,
                    'recommendations': section.recommendations
                })
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Architectural review completed. Overall score: {overall_score}/100",
                data={
                    'overall_score': overall_score,
                    'sections': sections_data,
                    'total_findings': sum(len(s.findings) for s in self.sections),
                    'critical_findings': sum(1 for s in self.sections for f in s.findings if f.severity == 'CRITICAL'),
                    'high_findings': sum(1 for s in self.sections for f in s.findings if f.severity == 'HIGH'),
                    'report_path': str(report_path),
                    'workspace': str(self.workspace_path),
                    'scope_filter': self.scope_filter,
                    'request_context': self.request_context,
                    'alignment_protected': True
                }
            )
            
        except Exception as e:
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Review failed: {str(e)}",
                data={'error': str(e)}
            )
    
    def _analyze_architecture(self) -> ReviewSection:
        """Analyze architecture and structure."""
        findings = []
        
        # Check for common architectural patterns
        src_path = self.workspace_path / "src"
        if src_path.exists():
            # Analyze directory structure
            subdirs = [d for d in src_path.iterdir() if d.is_dir()]
            
            # Check for layered architecture
            has_layers = any(d.name in ['controllers', 'services', 'repositories', 'models', 'entities'] 
                           for d in subdirs)
            
            if not has_layers:
                findings.append(ReviewFinding(
                    severity="MEDIUM",
                    category="Architecture",
                    title="No clear layered architecture detected",
                    description="Code does not appear to follow a clear layered architecture (MVC, Clean Architecture, etc.)",
                    location=str(src_path),
                    recommendation="Consider organizing code into clear layers: presentation, business logic, data access",
                    root_cause="Lack of architectural planning or gradual architectural drift"
                ))
            
            # Check for separation of concerns
            file_count = sum(1 for _ in src_path.rglob("*.py"))
            if file_count > 50:
                avg_lines = self._calculate_avg_file_size(src_path)
                if avg_lines > 300:
                    findings.append(ReviewFinding(
                        severity="HIGH",
                        category="Architecture",
                        title="Large average file size indicates poor separation of concerns",
                        description=f"Average file size: {avg_lines} lines. Files should be smaller and more focused.",
                        location=str(src_path),
                        recommendation="Break down large files into smaller, single-responsibility modules",
                        root_cause="Lack of refactoring discipline, unclear module boundaries"
                    ))
        
        # Calculate score (100 - 10 per finding, weighted by severity)
        severity_weights = {'CRITICAL': 20, 'HIGH': 15, 'MEDIUM': 10, 'LOW': 5}
        deductions = sum(severity_weights.get(f.severity, 10) for f in findings)
        score = max(0, 100 - deductions)
        
        return ReviewSection(
            name="Architecture & Structure",
            score=score,
            findings=findings,
            summary=f"Analyzed {len(subdirs) if src_path.exists() else 0} architectural components. Found {len(findings)} issues.",
            recommendations=[
                "Establish clear architectural layers",
                "Document architectural decisions (ADRs)",
                "Implement dependency injection for better testability"
            ]
        )
    
    def _analyze_code_quality(self) -> ReviewSection:
        """Analyze code quality and patterns."""
        findings = []
        
        src_path = self.workspace_path / "src"
        if src_path.exists():
            # Check for naming conventions
            py_files = list(src_path.rglob("*.py"))
            
            # Check for magic numbers
            magic_numbers_count = 0
            long_functions_count = 0
            
            for py_file in py_files[:20]:  # Sample first 20 files
                try:
                    content = py_file.read_text(encoding='utf-8')
                    lines = content.split('\n')
                    
                    # Detect magic numbers (simple heuristic)
                    import re
                    numbers = re.findall(r'\b\d{3,}\b', content)
                    if len(numbers) > 5:
                        magic_numbers_count += 1
                    
                    # Detect long functions (>50 lines)
                    in_function = False
                    function_lines = 0
                    for line in lines:
                        if line.strip().startswith('def '):
                            if function_lines > 50:
                                long_functions_count += 1
                            in_function = True
                            function_lines = 0
                        elif in_function:
                            function_lines += 1
                    
                except Exception:
                    pass
            
            if magic_numbers_count > 5:
                findings.append(ReviewFinding(
                    severity="MEDIUM",
                    category="Code Quality",
                    title="Excessive use of magic numbers",
                    description=f"Found magic numbers in {magic_numbers_count} files. Use named constants instead.",
                    location=str(src_path),
                    recommendation="Extract magic numbers into named constants or configuration",
                    root_cause="Lack of constant extraction during development"
                ))
            
            if long_functions_count > 10:
                findings.append(ReviewFinding(
                    severity="HIGH",
                    category="Code Quality",
                    title="Multiple long functions detected",
                    description=f"Found {long_functions_count} functions exceeding 50 lines. Functions should be smaller and focused.",
                    location=str(src_path),
                    recommendation="Apply Extract Method refactoring to break down long functions",
                    root_cause="Insufficient refactoring, violation of Single Responsibility Principle"
                ))
        
        severity_weights = {'CRITICAL': 20, 'HIGH': 15, 'MEDIUM': 10, 'LOW': 5}
        deductions = sum(severity_weights.get(f.severity, 10) for f in findings)
        score = max(0, 100 - deductions)
        
        return ReviewSection(
            name="Code Quality & Patterns",
            score=score,
            findings=findings,
            summary=f"Analyzed code quality patterns. Found {len(findings)} issues.",
            recommendations=[
                "Establish code review practices",
                "Use linters and formatters (pylint, black, flake8)",
                "Implement automated code quality gates in CI/CD"
            ]
        )
    
    def _analyze_solid_principles(self) -> ReviewSection:
        """Analyze SOLID principles adherence."""
        findings = []
        
        src_path = self.workspace_path / "src"
        if src_path.exists():
            py_files = list(src_path.rglob("*.py"))
            
            # Check for large classes (SRP violation)
            large_classes = 0
            for py_file in py_files[:20]:
                try:
                    content = py_file.read_text(encoding='utf-8')
                    lines = content.split('\n')
                    
                    in_class = False
                    class_lines = 0
                    class_methods = 0
                    
                    for line in lines:
                        if line.strip().startswith('class '):
                            if class_lines > 300 or class_methods > 15:
                                large_classes += 1
                            in_class = True
                            class_lines = 0
                            class_methods = 0
                        elif in_class:
                            class_lines += 1
                            if line.strip().startswith('def '):
                                class_methods += 1
                except Exception:
                    pass
            
            if large_classes > 5:
                findings.append(ReviewFinding(
                    severity="HIGH",
                    category="SOLID Principles",
                    title="Single Responsibility Principle violations detected",
                    description=f"Found {large_classes} large classes (>300 lines or >15 methods). Classes should have single responsibility.",
                    location=str(src_path),
                    recommendation="Break down large classes using Extract Class refactoring",
                    root_cause="Lack of responsibility segregation, God Object anti-pattern"
                ))
        
        severity_weights = {'CRITICAL': 20, 'HIGH': 15, 'MEDIUM': 10, 'LOW': 5}
        deductions = sum(severity_weights.get(f.severity, 10) for f in findings)
        score = max(0, 100 - deductions)
        
        return ReviewSection(
            name="SOLID Principles",
            score=score,
            findings=findings,
            summary=f"Evaluated SOLID principles adherence. Found {len(findings)} violations.",
            recommendations=[
                "Review classes with >300 lines or >15 methods",
                "Apply Single Responsibility Principle systematically",
                "Use interfaces/abstract classes for dependency inversion"
            ]
        )
    
    def _analyze_security(self) -> ReviewSection:
        """Analyze security and risk factors."""
        findings = []
        
        # Check for common security issues
        src_path = self.workspace_path / "src"
        if src_path.exists():
            py_files = list(src_path.rglob("*.py"))
            
            security_issues = {
                'hardcoded_secrets': 0,
                'sql_injection_risk': 0,
                'unsafe_eval': 0
            }
            
            for py_file in py_files[:30]:
                try:
                    content = py_file.read_text(encoding='utf-8')
                    
                    # Check for hardcoded secrets (simple patterns)
                    import re
                    if re.search(r'(password|secret|api_key|token)\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE):
                        security_issues['hardcoded_secrets'] += 1
                    
                    # Check for SQL injection risks
                    if 'execute(' in content and 'f"' in content:
                        security_issues['sql_injection_risk'] += 1
                    
                    # Check for unsafe eval
                    if 'eval(' in content or 'exec(' in content:
                        security_issues['unsafe_eval'] += 1
                        
                except Exception:
                    pass
            
            if security_issues['hardcoded_secrets'] > 0:
                findings.append(ReviewFinding(
                    severity="CRITICAL",
                    category="Security",
                    title="Hardcoded secrets detected",
                    description=f"Found potential hardcoded secrets in {security_issues['hardcoded_secrets']} files.",
                    location=str(src_path),
                    recommendation="Move secrets to environment variables or secure vaults (Azure Key Vault, AWS Secrets Manager)",
                    root_cause="Lack of secrets management strategy"
                ))
            
            if security_issues['sql_injection_risk'] > 0:
                findings.append(ReviewFinding(
                    severity="CRITICAL",
                    category="Security",
                    title="SQL injection risk detected",
                    description=f"Found potential SQL injection vulnerabilities in {security_issues['sql_injection_risk']} files.",
                    location=str(src_path),
                    recommendation="Use parameterized queries or ORM instead of string concatenation",
                    root_cause="Improper input sanitization and query construction"
                ))
            
            if security_issues['unsafe_eval'] > 0:
                findings.append(ReviewFinding(
                    severity="HIGH",
                    category="Security",
                    title="Unsafe eval/exec usage detected",
                    description=f"Found eval/exec in {security_issues['unsafe_eval']} files. This poses code injection risks.",
                    location=str(src_path),
                    recommendation="Avoid eval/exec. Use safer alternatives like ast.literal_eval or proper parsers",
                    root_cause="Dangerous code patterns, lack of security awareness"
                ))
        
        severity_weights = {'CRITICAL': 20, 'HIGH': 15, 'MEDIUM': 10, 'LOW': 5}
        deductions = sum(severity_weights.get(f.severity, 10) for f in findings)
        score = max(0, 100 - deductions)
        
        return ReviewSection(
            name="Security & Risk Assessment",
            score=score,
            findings=findings,
            summary=f"Assessed security posture. Found {len(findings)} security issues.",
            recommendations=[
                "Implement security scanning in CI/CD pipeline",
                "Use secrets management solution",
                "Conduct regular security audits",
                "Follow OWASP Top 10 guidelines"
            ]
        )
    
    def _analyze_performance(self) -> ReviewSection:
        """Analyze performance and scalability concerns."""
        findings = []
        
        src_path = self.workspace_path / "src"
        if src_path.exists():
            py_files = list(src_path.rglob("*.py"))
            
            perf_issues = {
                'nested_loops': 0,
                'missing_indexes': 0,
                'inefficient_queries': 0
            }
            
            for py_file in py_files[:20]:
                try:
                    content = py_file.read_text(encoding='utf-8')
                    lines = content.split('\n')
                    
                    # Check for nested loops (O(n²) or worse)
                    loop_depth = 0
                    for line in lines:
                        if 'for ' in line or 'while ' in line:
                            loop_depth += 1
                            if loop_depth >= 3:
                                perf_issues['nested_loops'] += 1
                                break
                        elif line.strip() and not line.strip().startswith('#'):
                            if loop_depth > 0 and line[0] not in ' \t':
                                loop_depth = 0
                    
                    # Check for N+1 query patterns
                    if 'for ' in content and '.get(' in content:
                        perf_issues['inefficient_queries'] += 1
                        
                except Exception:
                    pass
            
            if perf_issues['nested_loops'] > 3:
                findings.append(ReviewFinding(
                    severity="MEDIUM",
                    category="Performance",
                    title="Multiple nested loops detected",
                    description=f"Found {perf_issues['nested_loops']} instances of deeply nested loops (O(n²) or worse).",
                    location=str(src_path),
                    recommendation="Consider using hash maps, sets, or optimized algorithms to reduce complexity",
                    root_cause="Algorithmic inefficiency, lack of performance analysis"
                ))
            
            if perf_issues['inefficient_queries'] > 5:
                findings.append(ReviewFinding(
                    severity="HIGH",
                    category="Performance",
                    title="Potential N+1 query problem",
                    description=f"Found {perf_issues['inefficient_queries']} instances of potential N+1 query patterns.",
                    location=str(src_path),
                    recommendation="Use eager loading, batch queries, or caching to avoid N+1 problems",
                    root_cause="Lack of query optimization, ORM misuse"
                ))
        
        severity_weights = {'CRITICAL': 20, 'HIGH': 15, 'MEDIUM': 10, 'LOW': 5}
        deductions = sum(severity_weights.get(f.severity, 10) for f in findings)
        score = max(0, 100 - deductions)
        
        return ReviewSection(
            name="Performance & Scalability",
            score=score,
            findings=findings,
            summary=f"Analyzed performance characteristics. Found {len(findings)} concerns.",
            recommendations=[
                "Implement performance testing and benchmarking",
                "Profile critical code paths",
                "Add caching layers where appropriate",
                "Design for horizontal scalability"
            ]
        )
    
    def _calculate_avg_file_size(self, path: Path) -> int:
        """Calculate average file size in lines."""
        py_files = list(path.rglob("*.py"))
        if not py_files:
            return 0
        
        total_lines = 0
        file_count = 0
        
        for py_file in py_files[:50]:  # Sample up to 50 files
            try:
                lines = len(py_file.read_text(encoding='utf-8').split('\n'))
                total_lines += lines
                file_count += 1
            except Exception:
                pass
        
        return total_lines // file_count if file_count > 0 else 0
    
    def _generate_report(self) -> Path:
        """Generate comprehensive review report."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        report_name = f"architectural-review-{timestamp}.md"
        
        # Ensure reports directory exists
        reports_dir = Path("cortex-brain/documents/reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = reports_dir / report_name
        
        # Calculate overall score
        overall_score = sum(s.score for s in self.sections) // len(self.sections)
        
        # Generate markdown report
        report_lines = [
            "# Architectural Review Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Workspace:** {self.workspace_path}",
            f"**Overall Score:** {overall_score}/100",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            self._generate_executive_summary(overall_score),
            "",
            "---",
            ""
        ]
        
        # Add each section
        for section in self.sections:
            report_lines.extend([
                f"## {section.name}",
                "",
                f"**Score:** {section.score}/100",
                "",
                f"**Summary:** {section.summary}",
                "",
                "### Findings",
                ""
            ])
            
            if section.findings:
                for i, finding in enumerate(section.findings, 1):
                    severity_emoji = {
                        'CRITICAL': '🔴',
                        'HIGH': '🟠',
                        'MEDIUM': '🟡',
                        'LOW': '🟢'
                    }.get(finding.severity, '⚪')
                    
                    report_lines.extend([
                        f"#### {severity_emoji} Finding {i}: {finding.title}",
                        "",
                        f"**Severity:** {finding.severity}",
                        f"**Category:** {finding.category}",
                        "",
                        f"**Description:** {finding.description}",
                        ""
                    ])
                    
                    if finding.location:
                        report_lines.append(f"**Location:** `{finding.location}`")
                        report_lines.append("")
                    
                    if finding.root_cause:
                        report_lines.append(f"**Root Cause:** {finding.root_cause}")
                        report_lines.append("")
                    
                    if finding.recommendation:
                        report_lines.append(f"**Recommendation:** {finding.recommendation}")
                        report_lines.append("")
            else:
                report_lines.extend([
                    "✅ No issues found in this category.",
                    ""
                ])
            
            report_lines.extend([
                "### Recommendations",
                ""
            ])
            
            for rec in section.recommendations:
                report_lines.append(f"- {rec}")
            
            report_lines.extend(["", "---", ""])
        
        # Add action items
        report_lines.extend([
            "## Recommended Action Items",
            "",
            "### Immediate Actions (Critical/High Priority)",
            ""
        ])
        
        critical_high = [f for s in self.sections for f in s.findings 
                        if f.severity in ['CRITICAL', 'HIGH']]
        
        if critical_high:
            for i, finding in enumerate(critical_high, 1):
                report_lines.append(f"{i}. **{finding.title}** - {finding.recommendation}")
        else:
            report_lines.append("✅ No critical or high priority issues found.")
        
        report_lines.extend([
            "",
            "### Medium-Term Improvements",
            ""
        ])
        
        medium = [f for s in self.sections for f in s.findings if f.severity == 'MEDIUM']
        
        if medium:
            for i, finding in enumerate(medium, 1):
                report_lines.append(f"{i}. **{finding.title}** - {finding.recommendation}")
        else:
            report_lines.append("✅ No medium priority issues found.")
        
        report_lines.extend([
            "",
            "---",
            "",
            "**Reviewer:** CORTEX Architectural Review System",
            f"**Version:** 3.8.1",
            f"**Report ID:** {timestamp}"
        ])
        
        # Write report
        report_path.write_text('\n'.join(report_lines), encoding='utf-8')
        
        # Also generate JSON version for programmatic access
        json_report_path = reports_dir / f"architectural-review-{timestamp}.json"
        json_data = {
            'timestamp': datetime.now().isoformat(),
            'workspace': str(self.workspace_path),
            'overall_score': overall_score,
            'sections': [
                {
                    'name': s.name,
                    'score': s.score,
                    'summary': s.summary,
                    'findings': [asdict(f) for f in s.findings],
                    'recommendations': s.recommendations
                }
                for s in self.sections
            ]
        }
        
        json_report_path.write_text(json.dumps(json_data, indent=2), encoding='utf-8')
        
        return report_path
    
    def _generate_executive_summary(self, overall_score: int) -> str:
        """Generate executive summary based on score and findings."""
        critical_count = sum(1 for s in self.sections for f in s.findings if f.severity == 'CRITICAL')
        high_count = sum(1 for s in self.sections for f in s.findings if f.severity == 'HIGH')
        
        if overall_score >= 90:
            assessment = "**Excellent** - This codebase demonstrates high quality with minimal issues."
        elif overall_score >= 75:
            assessment = "**Good** - This codebase is generally well-structured with some areas for improvement."
        elif overall_score >= 60:
            assessment = "**Fair** - This codebase has moderate issues that should be addressed."
        else:
            assessment = "**Needs Improvement** - This codebase has significant issues requiring immediate attention."
        
        summary = f"{assessment}\n\n"
        
        if critical_count > 0:
            summary += f"⚠️ **{critical_count} CRITICAL** issues require immediate attention.\n\n"
        
        if high_count > 0:
            summary += f"🟠 **{high_count} HIGH** priority issues should be addressed soon.\n\n"
        
        summary += "This review examined architecture, code quality, SOLID principles, security, and performance. "
        summary += "Detailed findings and recommendations are provided in the sections below."
        
        return summary
    
    def _mark_reviewed_files(self, overall_score: int) -> None:
        """Mark all analyzed files in alignment tracker."""
        src_path = self.workspace_path / "src"
        
        if not src_path.exists():
            return
        
        # Get all Python files that were analyzed
        py_files = list(src_path.rglob("*.py"))[:50]  # Same sample as analysis
        
        total_findings = sum(len(s.findings) for s in self.sections)
        
        for py_file in py_files:
            try:
                # Mark file as reviewed with score
                self.alignment_tracker.mark_aligned(
                    file_path=py_file,
                    operation='review',
                    issues_fixed=0,  # Review doesn't fix, just reports
                    score=overall_score
                )
            except Exception:
                pass  # Continue marking other files
