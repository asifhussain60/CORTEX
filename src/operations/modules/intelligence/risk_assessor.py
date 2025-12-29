"""
Risk Assessor - Pre-execution impact analysis.

Analyzes proposed changes to identify potential breaking changes,
data loss risks, and security vulnerabilities before execution.

Copyright © 2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

from .domain_classifier import Criticality

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class RiskAssessment:
    """Risk assessment result."""
    risk_level: RiskLevel
    category: str  # "breaking_change", "data_loss", "security", "performance"
    description: str
    affected_components: List[str]
    mitigation_steps: List[str]
    requires_manual_review: bool


class RiskAssessor:
    """Assess execution risks before changes are applied."""
    
    def __init__(self, ast_engine, domain_classifier=None):
        """
        Initialize risk assessor.
        
        Args:
            ast_engine: AST engine for code analysis
            domain_classifier: Optional domain classifier for domain-specific risks
        """
        self.ast_engine = ast_engine
        self.domain_classifier = domain_classifier
        
    def assess_risk(
        self,
        operation: str,
        context: Dict[str, Any]
    ) -> List[RiskAssessment]:
        """
        Assess risks of proposed operation.
        
        Args:
            operation: Operation description
            context: Operation context (files, changes, etc.)
            
        Returns:
            List of identified risks
        """
        logger.info(f"Assessing risk for operation: {operation}")
        
        risks = []
        
        # Assess breaking change risk
        breaking_risks = self._assess_breaking_changes(context)
        risks.extend(breaking_risks)
        
        # Assess data loss risk
        data_risks = self._assess_data_loss(context)
        risks.extend(data_risks)
        
        # Assess security risk
        security_risks = self._assess_security_impact(context)
        risks.extend(security_risks)
        
        # Assess domain-specific risks
        if self.domain_classifier:
            domain_risks = self._assess_domain_risks(context)
            risks.extend(domain_risks)
        
        # Sort by severity
        severity_order = {
            RiskLevel.CRITICAL: 0,
            RiskLevel.HIGH: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.LOW: 3
        }
        risks.sort(key=lambda r: severity_order[r.risk_level])
        
        return risks
        
    def _assess_breaking_changes(self, context: Dict[str, Any]) -> List[RiskAssessment]:
        """Assess breaking change risk."""
        risks = []
        
        affected_files = context.get('affected_files', [])
        
        if not affected_files:
            return risks
            
        try:
            # Analyze dependencies
            arch = self.ast_engine.analyze_architecture()
            
            for file in affected_files:
                # Find modules that depend on this file
                dependents = self._find_dependents(file, arch)
                
                if len(dependents) > 10:
                    risks.append(RiskAssessment(
                        risk_level=RiskLevel.HIGH,
                        category="breaking_change",
                        description=(
                            f"Modifying {Path(file).name} affects {len(dependents)} "
                            f"downstream modules"
                        ),
                        affected_components=dependents[:10],
                        mitigation_steps=[
                            "Run full test suite before committing",
                            "Update dependent modules if interface changes",
                            "Consider deprecation path for major changes",
                            "Create feature flag for gradual rollout"
                        ],
                        requires_manual_review=True
                    ))
        except Exception as e:
            logger.warning(f"Breaking change assessment failed: {e}")
                
        return risks
        
    def _assess_data_loss(self, context: Dict[str, Any]) -> List[RiskAssessment]:
        """Assess data loss risk."""
        risks = []
        
        operation_type = context.get('operation_type', '')
        
        # Check for destructive operations
        destructive_keywords = ['delete', 'drop', 'truncate', 'remove', 'clear']
        
        if any(kw in operation_type.lower() for kw in destructive_keywords):
            risks.append(RiskAssessment(
                risk_level=RiskLevel.CRITICAL,
                category="data_loss",
                description="Operation involves data deletion or modification",
                affected_components=context.get('affected_data', ['Unknown']),
                mitigation_steps=[
                    "⚠️ CREATE BACKUP BEFORE PROCEEDING",
                    "Verify backup restoration procedure",
                    "Test on non-production data first",
                    "Implement soft-delete if possible"
                ],
                requires_manual_review=True
            ))
                
        return risks
        
    def _assess_security_impact(self, context: Dict[str, Any]) -> List[RiskAssessment]:
        """Assess security risk."""
        risks = []
        
        operation = context.get('operation', '')
        
        # Check for security-sensitive operations
        security_keywords = [
            'auth', 'password', 'token', 'secret', 'credential', 
            'permission', 'role', 'access', 'security'
        ]
        
        if any(kw in operation.lower() for kw in security_keywords):
            risks.append(RiskAssessment(
                risk_level=RiskLevel.HIGH,
                category="security",
                description="Operation affects security-sensitive components",
                affected_components=context.get('affected_files', ['Unknown']),
                mitigation_steps=[
                    "Review security implications carefully",
                    "Ensure proper authentication/authorization",
                    "Validate input sanitization",
                    "Consider security testing before deployment"
                ],
                requires_manual_review=True
            ))
                
        return risks
        
    def _assess_domain_risks(self, context: Dict[str, Any]) -> List[RiskAssessment]:
        """Assess domain-specific risks."""
        risks = []
        
        if not self.domain_classifier:
            return risks
            
        affected_files = context.get('affected_files', [])
        
        for file in affected_files:
            try:
                domain = self.domain_classifier.classify(Path(file))
                
                if domain.criticality == Criticality.CRITICAL:
                    risks.append(RiskAssessment(
                        risk_level=RiskLevel.HIGH,
                        category="domain_criticality",
                        description=f"Modifying critical domain: {domain.domain_type}",
                        affected_components=[file],
                        mitigation_steps=[
                            f"Extra caution: {domain.domain_type} is critical",
                            "Require peer review before changes",
                            "Ensure comprehensive test coverage",
                            "Monitor changes closely in production"
                        ],
                        requires_manual_review=True
                    ))
            except Exception as e:
                logger.warning(f"Domain classification failed for {file}: {e}")
                
        return risks
        
    def _find_dependents(self, file: str, architecture: Dict[str, Any]) -> List[str]:
        """Find modules that depend on given file."""
        dependents = []
        
        file_path = Path(file)
        
        # Get dependency graph from architecture analysis
        dependencies = architecture.get('dependencies', {})
        
        for module, deps in dependencies.items():
            if any(str(file_path) in dep for dep in deps):
                dependents.append(module)
                
        return dependents
        
    def should_block_execution(self, risks: List[RiskAssessment]) -> bool:
        """
        Determine if execution should be blocked based on risks.
        
        Args:
            risks: List of risk assessments
            
        Returns:
            True if execution should be blocked
        """
        # Block if any CRITICAL risks found
        critical_risks = [r for r in risks if r.risk_level == RiskLevel.CRITICAL]
        
        return len(critical_risks) > 0
        
    def format_risk_report(self, risks: List[RiskAssessment]) -> str:
        """
        Format risk assessments as markdown report.
        
        Args:
            risks: List of risk assessments
            
        Returns:
            Formatted markdown string
        """
        if not risks:
            return "✅ No significant risks identified"
            
        output = []
        output.append("## ⚠️ Risk Assessment Report\n")
        
        # Group by risk level
        by_level = {}
        for risk in risks:
            by_level.setdefault(risk.risk_level, []).append(risk)
            
        for level in [RiskLevel.CRITICAL, RiskLevel.HIGH, RiskLevel.MEDIUM, RiskLevel.LOW]:
            if level not in by_level:
                continue
                
            level_icon = {
                RiskLevel.CRITICAL: '🔴 CRITICAL',
                RiskLevel.HIGH: '🟠 HIGH',
                RiskLevel.MEDIUM: '🟡 MEDIUM',
                RiskLevel.LOW: '🟢 LOW'
            }[level]
            
            output.append(f"### {level_icon}\n")
            
            for risk in by_level[level]:
                output.append(f"**{risk.category.upper()}: {risk.description}**")
                output.append(f"- Affected: {', '.join(risk.affected_components[:5])}")
                output.append("\n**Mitigation Steps:**")
                for step in risk.mitigation_steps:
                    output.append(f"  - {step}")
                if risk.requires_manual_review:
                    output.append("  - ⚠️ **Manual review required**")
                output.append("")
                
        return '\n'.join(output)
