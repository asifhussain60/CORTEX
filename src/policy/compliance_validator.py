"""
Compliance Validator - 3-Act WOW Workflow

Purpose: Validate code compliance against policy rules using intelligent
         Recognition → Gap Analysis → Enforcement workflow.

The WOW Framework:
- Act 1 (Recognition): Detect policy violations in codebase
- Act 2 (Gap Analysis): Compare current state vs required state
- Act 3 (Enforcement): Generate actionable remediation recommendations

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Repository: https://github.com/asifhussain60/CORTEX
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime

from .policy_analyzer import PolicyDocument, PolicyRule, PolicyLevel, PolicyCategory


class ViolationSeverity:
    """Violation severity levels"""
    CRITICAL = "critical"  # MUST/MUST NOT violations
    HIGH = "high"          # SHOULD violations
    MEDIUM = "medium"      # SHOULD NOT violations
    LOW = "low"            # MAY violations
    INFO = "info"          # Recommendations


@dataclass
class PolicyViolation:
    """Detected policy violation"""
    rule_id: str
    rule_text: str
    severity: str
    file_path: str
    line_number: Optional[int] = None
    column: Optional[int] = None
    code_snippet: Optional[str] = None
    violation_details: Optional[str] = None
    current_value: Optional[Any] = None
    required_value: Optional[Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class GapAnalysis:
    """Gap analysis between current and required state"""
    rule_id: str
    category: str
    current_state: Dict[str, Any]
    required_state: Dict[str, Any]
    gaps: List[str]
    impact: str  # HIGH, MEDIUM, LOW
    effort: str  # HIGH, MEDIUM, LOW
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class RemediationAction:
    """Actionable remediation recommendation"""
    rule_id: str
    action_type: str  # FIX, REFACTOR, ADD, REMOVE, UPDATE
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggested_fix: Optional[str] = None
    estimated_effort: Optional[str] = None  # minutes/hours/days
    priority: int = 1  # 1=highest, 5=lowest
    automation_available: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class ComplianceReport:
    """Complete compliance validation report"""
    timestamp: datetime
    policy_file: str
    policy_version: Optional[str]
    codebase_path: str
    total_rules: int
    violations: List[PolicyViolation] = field(default_factory=list)
    gap_analyses: List[GapAnalysis] = field(default_factory=list)
    remediation_actions: List[RemediationAction] = field(default_factory=list)
    compliance_score: float = 0.0
    summary: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['violations'] = [v.to_dict() for v in self.violations]
        result['gap_analyses'] = [g.to_dict() for g in self.gap_analyses]
        result['remediation_actions'] = [r.to_dict() for r in self.remediation_actions]
        return result


class ComplianceValidator:
    """
    Validate code compliance using 3-act WOW workflow:
    
    Act 1 - Recognition: Detect violations
    Act 2 - Gap Analysis: Compare current vs required
    Act 3 - Enforcement: Generate remediation actions
    
    Supports:
    - Python code analysis (AST parsing)
    - Test coverage validation
    - Security rule checking
    - Performance threshold validation
    - Architecture pattern detection
    """
    
    def __init__(self):
        """Initialize compliance validator"""
        self.violation_patterns = self._build_violation_patterns()
    
    def validate(
        self,
        policy_doc: PolicyDocument,
        codebase_path: str
    ) -> ComplianceReport:
        """
        Validate codebase against policy document.
        
        3-Act WOW Workflow:
        1. Recognition: Scan codebase for violations
        2. Gap Analysis: Analyze current vs required state
        3. Enforcement: Generate remediation actions
        
        Args:
            policy_doc: Parsed policy document
            codebase_path: Path to codebase to validate
        
        Returns:
            ComplianceReport with violations, gaps, and actions
        """
        print(f"\n🔍 Starting Compliance Validation (3-Act WOW Workflow)")
        print(f"Policy: {policy_doc.title or 'Untitled'} v{policy_doc.version or '?'}")
        print(f"Codebase: {codebase_path}\n")
        
        # Act 1: Recognition - Detect violations
        print("⚡ Act 1: Recognition (Detecting Violations)")
        violations = self._recognize_violations(policy_doc, codebase_path)
        print(f"   Found {len(violations)} violations\n")
        
        # Act 2: Gap Analysis - Compare current vs required
        print("📊 Act 2: Gap Analysis (Comparing State)")
        gap_analyses = self._analyze_gaps(policy_doc, violations, codebase_path)
        print(f"   Identified {len(gap_analyses)} gaps\n")
        
        # Act 3: Enforcement - Generate remediation actions
        print("🎯 Act 3: Enforcement (Generating Actions)")
        remediation_actions = self._generate_remediation(violations, gap_analyses)
        print(f"   Created {len(remediation_actions)} actionable recommendations\n")
        
        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(policy_doc, violations)
        
        # Build summary
        summary = self._build_summary(violations, gap_analyses, remediation_actions)
        
        # Create report
        report = ComplianceReport(
            timestamp=datetime.now(),
            policy_file=policy_doc.file_path,
            policy_version=policy_doc.version,
            codebase_path=codebase_path,
            total_rules=len(policy_doc.rules),
            violations=violations,
            gap_analyses=gap_analyses,
            remediation_actions=remediation_actions,
            compliance_score=compliance_score,
            summary=summary
        )
        
        return report
    
    def _recognize_violations(
        self,
        policy_doc: PolicyDocument,
        codebase_path: str
    ) -> List[PolicyViolation]:
        """
        Act 1: Recognition - Detect policy violations in codebase.
        
        Uses pattern matching, AST analysis, and rule-specific validators.
        """
        violations = []
        
        # Get all Python files
        python_files = list(Path(codebase_path).rglob("*.py"))
        
        for rule in policy_doc.rules:
            # Check each file for this rule
            for py_file in python_files:
                rule_violations = self._check_rule(rule, py_file)
                violations.extend(rule_violations)
        
        return violations
    
    def _check_rule(self, rule: PolicyRule, file_path: Path) -> List[PolicyViolation]:
        """Check a specific rule against a file"""
        violations = []
        
        # Determine severity from policy level
        severity_map = {
            PolicyLevel.MUST: ViolationSeverity.CRITICAL,
            PolicyLevel.MUST_NOT: ViolationSeverity.CRITICAL,
            PolicyLevel.SHOULD: ViolationSeverity.HIGH,
            PolicyLevel.SHOULD_NOT: ViolationSeverity.MEDIUM,
            PolicyLevel.MAY: ViolationSeverity.LOW,
        }
        severity = severity_map.get(rule.level, ViolationSeverity.INFO)
        
        # Category-specific validation
        if rule.category == PolicyCategory.TESTING:
            violations.extend(self._check_testing_rule(rule, file_path, severity))
        elif rule.category == PolicyCategory.SECURITY:
            violations.extend(self._check_security_rule(rule, file_path, severity))
        elif rule.category == PolicyCategory.PERFORMANCE:
            violations.extend(self._check_performance_rule(rule, file_path, severity))
        elif rule.category == PolicyCategory.DOCUMENTATION:
            violations.extend(self._check_documentation_rule(rule, file_path, severity))
        
        return violations
    
    def _check_testing_rule(
        self,
        rule: PolicyRule,
        file_path: Path,
        severity: str
    ) -> List[PolicyViolation]:
        """Check testing-related rules"""
        violations = []
        
        # Example: Check for test coverage threshold
        if 'coverage' in rule.text.lower() and rule.threshold:
            # This would integrate with actual coverage tools
            # For now, create a placeholder violation
            if 'test' not in str(file_path).lower():
                violation = PolicyViolation(
                    rule_id=rule.id,
                    rule_text=rule.text,
                    severity=severity,
                    file_path=str(file_path),
                    violation_details=f"File may lack test coverage (threshold: {rule.threshold}{rule.unit})",
                    required_value=f"{rule.threshold}{rule.unit}"
                )
                violations.append(violation)
        
        return violations
    
    def _check_security_rule(
        self,
        rule: PolicyRule,
        file_path: Path,
        severity: str
    ) -> List[PolicyViolation]:
        """Check security-related rules"""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for common security issues
            if 'password' in rule.text.lower() and 'plain text' in rule.text.lower():
                # Check for hardcoded passwords
                password_patterns = [
                    r'password\s*=\s*["\'][\w]+["\']',
                    r'PASSWORD\s*=\s*["\'][\w]+["\']',
                ]
                
                for pattern in password_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        violation = PolicyViolation(
                            rule_id=rule.id,
                            rule_text=rule.text,
                            severity=severity,
                            file_path=str(file_path),
                            line_number=line_num,
                            code_snippet=match.group(0),
                            violation_details="Hardcoded password detected"
                        )
                        violations.append(violation)
            
            # Check for input validation
            if 'input' in rule.text.lower() and 'validat' in rule.text.lower():
                # Look for input() or request.args without validation
                if 'input(' in content or 'request.args' in content or 'request.form' in content:
                    # Check if validation is present (simplified)
                    if not any(keyword in content for keyword in ['validate', 'sanitize', 'clean', 'escape']):
                        violation = PolicyViolation(
                            rule_id=rule.id,
                            rule_text=rule.text,
                            severity=severity,
                            file_path=str(file_path),
                            violation_details="User input without visible validation"
                        )
                        violations.append(violation)
        
        except Exception as e:
            pass  # Skip files that can't be read
        
        return violations
    
    def _check_performance_rule(
        self,
        rule: PolicyRule,
        file_path: Path,
        severity: str
    ) -> List[PolicyViolation]:
        """Check performance-related rules"""
        violations = []
        
        # This would integrate with profiling tools
        # For now, check for known performance anti-patterns
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for inefficient patterns
            if '+=' in content and 'for' in content:
                # String concatenation in loop (inefficient)
                if re.search(r'for\s+\w+\s+in.*:\s*\n\s*\w+\s*\+=\s*["\']', content):
                    violation = PolicyViolation(
                        rule_id=rule.id,
                        rule_text=rule.text,
                        severity=severity,
                        file_path=str(file_path),
                        violation_details="String concatenation in loop detected (use join() instead)"
                    )
                    violations.append(violation)
        
        except Exception:
            pass
        
        return violations
    
    def _check_documentation_rule(
        self,
        rule: PolicyRule,
        file_path: Path,
        severity: str
    ) -> List[PolicyViolation]:
        """Check documentation-related rules"""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST to check for docstrings
            try:
                tree = ast.parse(content)
                
                # Check functions without docstrings
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        if not ast.get_docstring(node):
                            violation = PolicyViolation(
                                rule_id=rule.id,
                                rule_text=rule.text,
                                severity=severity,
                                file_path=str(file_path),
                                line_number=node.lineno,
                                violation_details=f"{node.__class__.__name__} '{node.name}' missing docstring"
                            )
                            violations.append(violation)
            
            except SyntaxError:
                pass  # Skip files with syntax errors
        
        except Exception:
            pass
        
        return violations
    
    def _analyze_gaps(
        self,
        policy_doc: PolicyDocument,
        violations: List[PolicyViolation],
        codebase_path: str
    ) -> List[GapAnalysis]:
        """
        Act 2: Gap Analysis - Compare current vs required state.
        
        Analyzes what needs to change to achieve compliance.
        """
        gap_analyses = []
        
        # Group violations by rule
        violations_by_rule: Dict[str, List[PolicyViolation]] = {}
        for violation in violations:
            if violation.rule_id not in violations_by_rule:
                violations_by_rule[violation.rule_id] = []
            violations_by_rule[violation.rule_id].append(violation)
        
        # Analyze gap for each rule with violations
        for rule_id, rule_violations in violations_by_rule.items():
            # Find the rule
            rule = next((r for r in policy_doc.rules if r.id == rule_id), None)
            if not rule:
                continue
            
            # Build gap analysis
            current_state = {
                "violations_count": len(rule_violations),
                "affected_files": list(set(v.file_path for v in rule_violations)),
                "compliance": False
            }
            
            required_state = {
                "violations_count": 0,
                "compliance": True,
                "threshold": rule.threshold,
                "unit": rule.unit
            }
            
            gaps = [
                f"{len(rule_violations)} violations detected",
                f"{len(current_state['affected_files'])} files affected",
                f"Requires {rule.level.value} compliance"
            ]
            
            # Determine impact and effort
            impact = self._determine_impact(rule, rule_violations)
            effort = self._determine_effort(rule, rule_violations)
            
            gap = GapAnalysis(
                rule_id=rule_id,
                category=rule.category.value,
                current_state=current_state,
                required_state=required_state,
                gaps=gaps,
                impact=impact,
                effort=effort
            )
            
            gap_analyses.append(gap)
        
        return gap_analyses
    
    def _determine_impact(self, rule: PolicyRule, violations: List[PolicyViolation]) -> str:
        """Determine business impact of violations"""
        # Critical rules = HIGH impact
        if rule.level in [PolicyLevel.MUST, PolicyLevel.MUST_NOT]:
            return "HIGH"
        
        # Many violations = HIGH impact
        if len(violations) > 10:
            return "HIGH"
        
        # Security = HIGH impact
        if rule.category == PolicyCategory.SECURITY:
            return "HIGH"
        
        # Few violations of SHOULD rules = MEDIUM
        if rule.level in [PolicyLevel.SHOULD, PolicyLevel.SHOULD_NOT]:
            return "MEDIUM"
        
        return "LOW"
    
    def _determine_effort(self, rule: PolicyRule, violations: List[PolicyViolation]) -> str:
        """Determine effort required to fix violations"""
        # Many files affected = HIGH effort
        affected_files = set(v.file_path for v in violations)
        if len(affected_files) > 20:
            return "HIGH"
        
        # Architecture changes = HIGH effort
        if rule.category == PolicyCategory.ARCHITECTURE:
            return "HIGH"
        
        # Medium number of violations = MEDIUM effort
        if len(violations) > 5:
            return "MEDIUM"
        
        return "LOW"
    
    def _generate_remediation(
        self,
        violations: List[PolicyViolation],
        gap_analyses: List[GapAnalysis]
    ) -> List[RemediationAction]:
        """
        Act 3: Enforcement - Generate actionable remediation recommendations.
        
        Creates prioritized list of actions to achieve compliance.
        """
        actions = []
        
        for gap in gap_analyses:
            # Find violations for this rule
            rule_violations = [v for v in violations if v.rule_id == gap.rule_id]
            
            # Generate actions based on category and violations
            if gap.category == "security":
                actions.extend(self._generate_security_actions(gap, rule_violations))
            elif gap.category == "testing":
                actions.extend(self._generate_testing_actions(gap, rule_violations))
            elif gap.category == "performance":
                actions.extend(self._generate_performance_actions(gap, rule_violations))
            elif gap.category == "documentation":
                actions.extend(self._generate_documentation_actions(gap, rule_violations))
            else:
                actions.extend(self._generate_general_actions(gap, rule_violations))
        
        # Sort by priority (1=highest)
        actions.sort(key=lambda a: a.priority)
        
        return actions
    
    def _generate_security_actions(
        self,
        gap: GapAnalysis,
        violations: List[PolicyViolation]
    ) -> List[RemediationAction]:
        """Generate security remediation actions"""
        actions = []
        
        for violation in violations:
            if 'password' in violation.violation_details.lower():
                action = RemediationAction(
                    rule_id=gap.rule_id,
                    action_type="FIX",
                    description="Replace hardcoded password with environment variable or secrets manager",
                    file_path=violation.file_path,
                    line_number=violation.line_number,
                    suggested_fix="password = os.environ.get('PASSWORD')",
                    estimated_effort="15 minutes",
                    priority=1,  # Critical
                    automation_available=True
                )
                actions.append(action)
            
            elif 'input' in violation.violation_details.lower():
                action = RemediationAction(
                    rule_id=gap.rule_id,
                    action_type="ADD",
                    description="Add input validation and sanitization",
                    file_path=violation.file_path,
                    suggested_fix="Use validation library (e.g., marshmallow, pydantic)",
                    estimated_effort="30 minutes",
                    priority=1,
                    automation_available=False
                )
                actions.append(action)
        
        return actions
    
    def _generate_testing_actions(
        self,
        gap: GapAnalysis,
        violations: List[PolicyViolation]
    ) -> List[RemediationAction]:
        """Generate testing remediation actions"""
        actions = []
        
        # Group by file
        files = set(v.file_path for v in violations)
        
        for file_path in files:
            action = RemediationAction(
                rule_id=gap.rule_id,
                action_type="ADD",
                description=f"Add tests for {Path(file_path).name}",
                file_path=file_path,
                suggested_fix="Create corresponding test file with pytest",
                estimated_effort="2 hours",
                priority=2,
                automation_available=True
            )
            actions.append(action)
        
        return actions
    
    def _generate_performance_actions(
        self,
        gap: GapAnalysis,
        violations: List[PolicyViolation]
    ) -> List[RemediationAction]:
        """Generate performance remediation actions"""
        actions = []
        
        for violation in violations:
            if 'string concatenation' in violation.violation_details.lower():
                action = RemediationAction(
                    rule_id=gap.rule_id,
                    action_type="REFACTOR",
                    description="Replace string concatenation with join()",
                    file_path=violation.file_path,
                    suggested_fix="Use ''.join(list) instead of += in loop",
                    estimated_effort="10 minutes",
                    priority=3,
                    automation_available=True
                )
                actions.append(action)
        
        return actions
    
    def _generate_documentation_actions(
        self,
        gap: GapAnalysis,
        violations: List[PolicyViolation]
    ) -> List[RemediationAction]:
        """Generate documentation remediation actions"""
        actions = []
        
        for violation in violations:
            action = RemediationAction(
                rule_id=gap.rule_id,
                action_type="ADD",
                description=f"Add docstring: {violation.violation_details}",
                file_path=violation.file_path,
                line_number=violation.line_number,
                suggested_fix="Add Google-style or NumPy-style docstring",
                estimated_effort="5 minutes",
                priority=4,
                automation_available=True
            )
            actions.append(action)
        
        return actions
    
    def _generate_general_actions(
        self,
        gap: GapAnalysis,
        violations: List[PolicyViolation]
    ) -> List[RemediationAction]:
        """Generate general remediation actions"""
        actions = []
        
        action = RemediationAction(
            rule_id=gap.rule_id,
            action_type="REVIEW",
            description=f"Review and address {len(violations)} violations",
            estimated_effort=f"{len(violations) * 15} minutes",
            priority=5,
            automation_available=False
        )
        actions.append(action)
        
        return actions
    
    def _calculate_compliance_score(
        self,
        policy_doc: PolicyDocument,
        violations: List[PolicyViolation]
    ) -> float:
        """Calculate overall compliance score (0-100)"""
        if not policy_doc.rules:
            return 100.0
        
        # Weight violations by severity
        severity_weights = {
            ViolationSeverity.CRITICAL: 10,
            ViolationSeverity.HIGH: 5,
            ViolationSeverity.MEDIUM: 3,
            ViolationSeverity.LOW: 1,
            ViolationSeverity.INFO: 0.5
        }
        
        # Calculate weighted violation score
        weighted_violations = sum(
            severity_weights.get(v.severity, 1) for v in violations
        )
        
        # Max possible violations (all rules violated at highest severity)
        max_violations = len(policy_doc.rules) * severity_weights[ViolationSeverity.CRITICAL]
        
        # Calculate score
        if max_violations == 0:
            return 100.0
        
        score = max(0.0, 100.0 - (weighted_violations / max_violations * 100))
        
        return round(score, 2)
    
    def _build_summary(
        self,
        violations: List[PolicyViolation],
        gap_analyses: List[GapAnalysis],
        remediation_actions: List[RemediationAction]
    ) -> Dict[str, Any]:
        """Build compliance summary"""
        # Count by severity
        severity_counts = {}
        for violation in violations:
            severity_counts[violation.severity] = severity_counts.get(violation.severity, 0) + 1
        
        # Count by category
        category_counts = {}
        for gap in gap_analyses:
            category_counts[gap.category] = category_counts.get(gap.category, 0) + 1
        
        # Estimate total effort
        total_effort_minutes = 0
        for action in remediation_actions:
            if action.estimated_effort and 'minute' in action.estimated_effort:
                try:
                    minutes = int(re.search(r'(\d+)', action.estimated_effort).group(1))
                    total_effort_minutes += minutes
                except (AttributeError, ValueError):
                    pass
            elif action.estimated_effort and 'hour' in action.estimated_effort:
                try:
                    hours = int(re.search(r'(\d+)', action.estimated_effort).group(1))
                    total_effort_minutes += hours * 60
                except (AttributeError, ValueError):
                    pass
        
        return {
            "total_violations": len(violations),
            "by_severity": severity_counts,
            "by_category": category_counts,
            "total_gaps": len(gap_analyses),
            "total_actions": len(remediation_actions),
            "estimated_effort_hours": round(total_effort_minutes / 60, 1),
            "automated_actions": sum(1 for a in remediation_actions if a.automation_available)
        }
    
    def _build_violation_patterns(self) -> Dict[str, Any]:
        """Build violation detection patterns"""
        # This would be expanded with more sophisticated patterns
        return {}


def main():
    """Test compliance validator"""
    from .policy_analyzer import PolicyAnalyzer
    
    # Create sample policy
    sample_policy = """# Security Policy
Version: 1.0

## Security Rules

- Passwords MUST NOT be stored in plain text.
- All user input MUST be validated and sanitized.
- API keys SHOULD NOT be hardcoded in source files.

## Testing Rules

- Test coverage MUST be greater than 80%.
"""
    
    # Write to temp file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(sample_policy)
        policy_path = f.name
    
    try:
        # Parse policy
        analyzer = PolicyAnalyzer()
        policy_doc = analyzer.analyze_file(policy_path)
        
        # Validate against current directory
        validator = ComplianceValidator()
        report = validator.validate(policy_doc, ".")
        
        print(f"✅ Compliance Validation Complete!")
        print(f"\nCompliance Score: {report.compliance_score}%")
        print(f"\nViolations: {len(report.violations)}")
        print(f"Gap Analyses: {len(report.gap_analyses)}")
        print(f"Remediation Actions: {len(report.remediation_actions)}")
        print(f"\nEstimated Effort: {report.summary['estimated_effort_hours']} hours")
        print(f"Automated Actions: {report.summary['automated_actions']}/{report.summary['total_actions']}")
    
    finally:
        os.unlink(policy_path)


if __name__ == "__main__":
    main()
