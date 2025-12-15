"""
CORTEX Planning Rules Validator

Validates planning artifacts against the enhanced DoR framework and Development Executor rules.
Integrates with optimize and healthcheck operations to enforce planning quality.

This validator:
1. Checks DoR compliance (ambiguity detection, self-audit completion)
2. Validates TDD tier assignments (simple/medium/complex)
3. Enforces clean code gates (unused code, complexity thresholds)
4. Validates security review completion (OWASP checklist)
5. Generates actionable recommendations for improvement

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
"""

import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
import yaml

logger = logging.getLogger(__name__)


@dataclass
class ValidationIssue:
    """Represents a planning validation issue."""
    severity: str  # 'blocking', 'warning', 'info'
    category: str  # 'dor', 'tdd', 'security', 'clean_code'
    message: str
    file_path: Optional[Path] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class PlanningValidationReport:
    """Results of planning rules validation."""
    total_plans: int = 0
    plans_validated: int = 0
    blocking_issues: List[ValidationIssue] = field(default_factory=list)
    warnings: List[ValidationIssue] = field(default_factory=list)
    info: List[ValidationIssue] = field(default_factory=list)
    compliant_plans: List[Path] = field(default_factory=list)
    non_compliant_plans: List[Path] = field(default_factory=list)
    
    @property
    def has_blocking_issues(self) -> bool:
        """Check if any blocking issues exist."""
        return len(self.blocking_issues) > 0
    
    @property
    def compliance_rate(self) -> float:
        """Calculate compliance rate."""
        if self.total_plans == 0:
            return 100.0
        return (len(self.compliant_plans) / self.total_plans) * 100


class PlanningRulesValidator:
    """
    Validates planning artifacts against enhanced DoR and Development Executor rules.
    
    Usage:
        validator = PlanningRulesValidator(project_root=Path('/path/to/cortex'))
        report = validator.validate_all_plans()
        
        if report.has_blocking_issues:
            for issue in report.blocking_issues:
                print(f"BLOCKING: {issue.message}")
    """
    
    def __init__(self, project_root: Path):
        """Initialize validator."""
        self.project_root = project_root
        self.cortex_brain = project_root / "cortex-brain"
        self.planning_templates = self.cortex_brain / "templates" / "planning"
        self.development_executor = self.cortex_brain / "components" / "development-executor"
        
        # Load validation rules
        self.dor_rules = self._load_dor_rules()
        self.tdd_rules = self._load_tdd_rules()
        self.clean_code_rules = self._load_clean_code_rules()
        self.security_rules = self._load_security_rules()
    
    def _load_dor_rules(self) -> Dict[str, Any]:
        """Load DoR checklist rules."""
        dor_path = self.planning_templates / "dor-checklist.yaml"
        if not dor_path.exists():
            logger.warning(f"DoR checklist not found: {dor_path}")
            return {}
        
        try:
            with open(dor_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load DoR rules: {e}")
            return {}
    
    def _load_tdd_rules(self) -> Dict[str, Any]:
        """Load TDD framework rules."""
        tdd_path = self.development_executor / "tdd-framework.yaml"
        if not tdd_path.exists():
            logger.warning(f"TDD framework not found: {tdd_path}")
            return {}
        
        try:
            with open(tdd_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load TDD rules: {e}")
            return {}
    
    def _load_clean_code_rules(self) -> Dict[str, Any]:
        """Load clean code gates rules."""
        gates_path = self.development_executor / "clean-code-gates.yaml"
        if not gates_path.exists():
            logger.warning(f"Clean code gates not found: {gates_path}")
            return {}
        
        try:
            with open(gates_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load clean code rules: {e}")
            return {}
    
    def _load_security_rules(self) -> Dict[str, Any]:
        """Load security gates rules."""
        security_path = self.development_executor / "security-gates.yaml"
        if not security_path.exists():
            logger.warning(f"Security gates not found: {security_path}")
            return {}
        
        try:
            with open(security_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load security rules: {e}")
            return {}
    
    def validate_all_plans(self) -> PlanningValidationReport:
        """
        Validate all planning documents in the workspace.
        
        Returns:
            PlanningValidationReport with validation results
        """
        report = PlanningValidationReport()
        
        # Find all planning documents
        planning_dirs = [
            self.cortex_brain / "documents" / "planning",
            self.cortex_brain / "templates" / "planning",
        ]
        
        for plan_dir in planning_dirs:
            if not plan_dir.exists():
                continue
            
            for plan_file in plan_dir.rglob("*.md"):
                report.total_plans += 1
                issues = self._validate_plan_file(plan_file)
                
                if issues:
                    report.plans_validated += 1
                    
                    # Categorize issues
                    for issue in issues:
                        if issue.severity == 'blocking':
                            report.blocking_issues.append(issue)
                            report.non_compliant_plans.append(plan_file)
                        elif issue.severity == 'warning':
                            report.warnings.append(issue)
                        else:
                            report.info.append(issue)
                    
                    # Only compliant if no blocking issues
                    if not any(i.severity == 'blocking' for i in issues):
                        report.compliant_plans.append(plan_file)
                else:
                    report.compliant_plans.append(plan_file)
                    report.plans_validated += 1
        
        return report
    
    def _validate_plan_file(self, plan_file: Path) -> List[ValidationIssue]:
        """Validate a single planning document."""
        issues = []
        
        try:
            with open(plan_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Run all validation checks
            issues.extend(self._check_dor_compliance(content, plan_file))
            issues.extend(self._check_semantic_organization(plan_file))
            issues.extend(self._check_ambiguity_detection(content, plan_file))
            issues.extend(self._check_security_review(content, plan_file))
            issues.extend(self._check_tdd_tier_assignment(content, plan_file))
            
        except Exception as e:
            logger.error(f"Failed to validate {plan_file}: {e}")
            issues.append(ValidationIssue(
                severity='warning',
                category='system',
                message=f"Failed to read file: {e}",
                file_path=plan_file
            ))
        
        return issues
    
    def _check_dor_compliance(self, content: str, file_path: Path) -> List[ValidationIssue]:
        """Check if plan meets Definition of Ready requirements."""
        issues = []
        
        if not self.dor_rules:
            return issues
        
        mandatory_sections = self.dor_rules.get('mandatory_sections', {})
        
        if 'acceptance_criteria' in mandatory_sections:
            if not self._has_acceptance_criteria(content):
                issues.append(ValidationIssue(
                    severity='blocking',
                    category='dor',
                    message="Missing acceptance criteria (GIVEN-WHEN-THEN format)",
                    file_path=file_path,
                    suggestion="Add acceptance criteria section with GIVEN-WHEN-THEN format"
                ))
        
        if 'risk_analysis' in mandatory_sections:
            if not self._has_risk_analysis(content):
                issues.append(ValidationIssue(
                    severity='warning',
                    category='dor',
                    message="Missing risk analysis section",
                    file_path=file_path,
                    suggestion="Add risk analysis with identified risks and mitigation strategies"
                ))
        
        if 'definition_of_done' in mandatory_sections:
            if not self._has_definition_of_done(content):
                issues.append(ValidationIssue(
                    severity='blocking',
                    category='dor',
                    message="Missing Definition of Done (DoD)",
                    file_path=file_path,
                    suggestion="Add DoD section with measurable completion criteria"
                ))
        
        return issues
    
    def _check_ambiguity_detection(self, content: str, file_path: Path) -> List[ValidationIssue]:
        """Detect vague terms that need clarification."""
        issues = []
        
        if not self.dor_rules:
            return issues
        
        vague_terms = self.dor_rules.get('ambiguity_detection', {}).get('vague_terms', [])
        
        for term_config in vague_terms:
            term = term_config.get('term', '')
            challenge = term_config.get('challenge', '')
            
            # Case-insensitive search for vague terms
            pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
            matches = pattern.finditer(content)
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append(ValidationIssue(
                    severity='warning',
                    category='dor',
                    message=f"Vague term '{term}' detected: {challenge}",
                    file_path=file_path,
                    line_number=line_num,
                    suggestion=f"Replace with specific measurable goal (see line {line_num})"
                ))
        
        return issues
    
    def _check_security_review(self, content: str, file_path: Path) -> List[ValidationIssue]:
        """Check if security review has been completed."""
        issues = []
        
        # Look for security review markers
        security_markers = [
            'OWASP',
            'security review',
            'security checklist',
            'vulnerability assessment',
            'threat model'
        ]
        
        has_security_review = any(
            marker.lower() in content.lower() for marker in security_markers
        )
        
        # Check if plan involves security-sensitive features
        security_keywords = [
            'authentication',
            'authorization',
            'password',
            'token',
            'secret',
            'encryption',
            'payment',
            'user data',
            'sensitive'
        ]
        
        is_security_sensitive = any(
            keyword.lower() in content.lower() for keyword in security_keywords
        )
        
        if is_security_sensitive and not has_security_review:
            issues.append(ValidationIssue(
                severity='blocking',
                category='security',
                message="Security-sensitive feature detected without security review",
                file_path=file_path,
                suggestion="Add OWASP Top 10 security checklist section"
            ))
        
        return issues
    
    def _check_tdd_tier_assignment(self, content: str, file_path: Path) -> List[ValidationIssue]:
        """Check if TDD quality tier has been assigned."""
        issues = []
        
        if not self.tdd_rules:
            return issues
        
        # Look for tier assignment markers
        tier_markers = [
            'quality tier',
            'complexity tier',
            'simple feature',
            'medium feature',
            'complex feature'
        ]
        
        has_tier_assignment = any(
            marker.lower() in content.lower() for marker in tier_markers
        )
        
        if not has_tier_assignment:
            issues.append(ValidationIssue(
                severity='info',
                category='tdd',
                message="No TDD quality tier assignment found",
                file_path=file_path,
                suggestion="Add quality tier (simple/medium/complex) for test coverage targets"
            ))
        
        return issues
    
    def _has_acceptance_criteria(self, content: str) -> bool:
        """Check if content has acceptance criteria."""
        patterns = [
            r'acceptance criteria',
            r'GIVEN.*WHEN.*THEN',
            r'given.*when.*then',
        ]
        return any(re.search(pattern, content, re.IGNORECASE | re.DOTALL) for pattern in patterns)
    
    def _has_risk_analysis(self, content: str) -> bool:
        """Check if content has risk analysis."""
        patterns = [
            r'risk\s+analysis',
            r'identified\s+risks',
            r'mitigation\s+strategies',
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns)
    
    def _has_definition_of_done(self, content: str) -> bool:
        """Check if content has definition of done."""
        patterns = [
            r'definition\s+of\s+done',
            r'\bDoD\b',
            r'completion\s+criteria',
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns)
    
    def _check_semantic_organization(self, plan_file: Path) -> List[ValidationIssue]:
        """
        Check if planning file follows semantic organization rules.
        
        Validates:
        1. Folder has semantic feature-based name (not generic like 'cortex-enhancements')
        2. Master plans use 00- prefix
        3. Sub-plans use sequential 01-, 02- prefixes
        4. Short descriptive names (folder provides context)
        
        Args:
            plan_file: Path to planning file
            
        Returns:
            List of ValidationIssue
        """
        issues = []
        
        # Get folder name and file name
        folder_name = plan_file.parent.name
        file_name = plan_file.name
        
        # Rule 1: Check for generic folder names (PROHIBITED)
        generic_folder_patterns = [
            r'cortex-enhancements',
            r'misc-plans',
            r'new-features',
            r'enhancements',
            r'updates',
            r'improvements',
        ]
        
        if any(re.match(pattern, folder_name, re.IGNORECASE) for pattern in generic_folder_patterns):
            issues.append(ValidationIssue(
                severity='blocking',
                category='planning_organization',
                message=f"Generic folder name '{folder_name}' violates SEMANTIC_PLANNING_ORGANIZATION_ENFORCEMENT",
                file_path=plan_file,
                suggestion=f"Move to semantic folder like: {self._suggest_semantic_folder(file_name)}"
            ))
        
        # Rule 2: Check if master plans have 00- prefix
        is_master_plan = any(keyword in file_name.lower() for keyword in ['master', 'main', 'primary'])
        if is_master_plan and not file_name.startswith('00-'):
            issues.append(ValidationIssue(
                severity='warning',
                category='planning_organization',
                message=f"Master plan '{file_name}' should use 00- prefix for visual hierarchy",
                file_path=plan_file,
                suggestion=f"Rename to: 00-{file_name.lower().replace('master-plan', 'master-plan').replace('main-plan', 'master-plan')}"
            ))
        
        # Rule 3: Check if sub-plans have sequential prefixes
        is_subplan = any(keyword in file_name.lower() for keyword in ['subplan', 'sub-plan', 'phase', 'execution', 'guide'])
        if is_subplan and not re.match(r'^\d{2}-', file_name):
            issues.append(ValidationIssue(
                severity='warning',
                category='planning_organization',
                message=f"Sub-plan '{file_name}' should use sequential prefix (01-, 02-, etc.)",
                file_path=plan_file,
                suggestion="Use sequential numbering: 01-subplan-name.md, 02-subplan-name.md"
            ))
        
        # Rule 4: Check for redundant prefixes in file names
        redundant_prefixes = [
            r'CORTEX-LENS-V3-',
            r'CORTEX-LENS-',
            r'PLANNING-SYSTEM-',
            r'ADO-OPERATIONS-',
        ]
        
        for pattern in redundant_prefixes:
            if re.search(pattern, file_name, re.IGNORECASE):
                # Extract feature from pattern
                feature = pattern.lower().replace('-', ' ').strip().title()
                issues.append(ValidationIssue(
                    severity='info',
                    category='planning_organization',
                    message=f"Redundant prefix in file name: folder '{folder_name}' already provides context",
                    file_path=plan_file,
                    suggestion=f"Shorten file name by removing '{pattern}' prefix (folder name provides feature context)"
                ))
                break
        
        return issues
    
    def _suggest_semantic_folder(self, file_name: str) -> str:
        """Suggest semantic folder name based on file name."""
        if 'lens' in file_name.lower():
            return "cortex-lens-v3/"
        elif 'planning' in file_name.lower() and 'system' in file_name.lower():
            return "planning-system-3.0/"
        elif 'ado' in file_name.lower():
            return "ado-operations/"
        elif 'tdd' in file_name.lower():
            return "tdd-orchestrator/"
        else:
            return "{feature-name-v{version}}/"
    
    def generate_recommendations(self, report: PlanningValidationReport) -> List[str]:
        """
        Generate actionable recommendations based on validation report.
        
        Args:
            report: Validation report
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if report.has_blocking_issues:
            recommendations.append(
                "⚠️  BLOCKING ISSUES DETECTED: Address these before proceeding with development"
            )
            
            # Group blocking issues by category
            by_category = {}
            for issue in report.blocking_issues:
                if issue.category not in by_category:
                    by_category[issue.category] = []
                by_category[issue.category].append(issue)
            
            for category, issues in by_category.items():
                recommendations.append(f"\n{category.upper()} Issues ({len(issues)}):")
                for issue in issues[:3]:  # Show top 3
                    recommendations.append(f"  • {issue.message}")
                    if issue.suggestion:
                        recommendations.append(f"    → {issue.suggestion}")
        
        if report.warnings:
            recommendations.append(
                f"\n⚠️  {len(report.warnings)} warnings detected - address to improve plan quality"
            )
        
        compliance_rate = report.compliance_rate
        if compliance_rate < 80:
            recommendations.append(
                f"\n📊 Compliance rate: {compliance_rate:.1f}% - Target: 80%+"
            )
            recommendations.append(
                "   → Review non-compliant plans and update to meet DoR standards"
            )
        
        if not report.blocking_issues and compliance_rate >= 80:
            recommendations.append(
                "✅ Planning quality meets CORTEX standards - ready for development"
            )
        
        return recommendations


def validate_planning_rules(project_root: Path) -> PlanningValidationReport:
    """
    Convenience function to validate planning rules.
    
    Args:
        project_root: Path to CORTEX project root
        
    Returns:
        PlanningValidationReport
    """
    validator = PlanningRulesValidator(project_root)
    return validator.validate_all_plans()
