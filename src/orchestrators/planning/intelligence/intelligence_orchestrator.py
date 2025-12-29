"""
Intelligence Orchestrator - Central Coordination for Planning Intelligence

Purpose: Coordinates all 4 intelligence adapters (Test, TDD, Validation, Manifest)
and provides unified intelligence API for Planning System workflows.

Version: 1.0.0
Author: CORTEX Development Team
Created: 2025-12-24 (Week 9 Day 4)

Responsibilities:
- Coordinate test intelligence (coverage analysis)
- Coordinate TDD intelligence (workflow enforcement)
- Coordinate validation intelligence (multi-layer validation)
- Coordinate manifest compliance (DoR/DoD validation)
- Aggregate intelligence reports
- Provide unified intelligence API
- Enable/disable intelligence features selectively

Integration Points:
- Planning System: Enhanced validation and recommendations
- plan_validator.py: Multi-layer validation before execution
- plan_generator.py: Intelligent test strategies and TDD guidance
- Brain Protection (Tier 0): Enforce governance rules

Week 9 Target: 500 LOC
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .test_intelligence_adapter import TestIntelligenceAdapter
from .tdd_intelligence_adapter import TDDIntelligenceAdapter
from .validation_framework_adapter import (
    ValidationFrameworkAdapter,
    ValidationReport,
    ValidationLevel
)
from .manifest_compliance_validator import (
    ManifestComplianceValidator,
    ComplianceReport,
    ComplianceLevel
)

logger = logging.getLogger(__name__)


class IntelligenceMode(Enum):
    """Intelligence operation modes."""
    FULL = "full"  # All intelligence features enabled
    VALIDATION_ONLY = "validation_only"  # Only validation (no test/TDD)
    ADVISORY_ONLY = "advisory_only"  # Only test/TDD guidance (no validation)
    MINIMAL = "minimal"  # Only critical validations


@dataclass
class IntelligenceReport:
    """Aggregated intelligence report."""
    timestamp: datetime = field(default_factory=datetime.now)
    mode: IntelligenceMode = IntelligenceMode.FULL
    
    # Test Intelligence
    test_coverage_analysis: Optional[Any] = None
    test_gaps: List[Any] = field(default_factory=list)
    test_strategy: Optional[Dict[str, Any]] = None
    
    # TDD Intelligence
    tdd_workflow_status: Optional[Dict[str, Any]] = None
    tdd_quality_score: float = 0.0
    tdd_recommendations: List[str] = field(default_factory=list)
    
    # Validation Intelligence
    validation_report: Optional[ValidationReport] = None
    validation_passed: bool = False
    
    # Manifest Compliance
    compliance_report: Optional[ComplianceReport] = None
    compliance_level: Optional[ComplianceLevel] = None
    
    # Overall Assessment
    overall_score: float = 0.0
    execution_approved: bool = False
    blocking_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def is_ready_for_execution(self) -> bool:
        """Check if plan is ready for execution."""
        return self.execution_approved and len(self.blocking_issues) == 0
    
    def get_summary(self) -> str:
        """Get human-readable summary."""
        if self.is_ready_for_execution():
            return f"✅ Ready for execution (Score: {self.overall_score:.1f}%, {len(self.warnings)} warnings)"
        else:
            return f"❌ Not ready ({len(self.blocking_issues)} blocking issues, {len(self.warnings)} warnings)"


class IntelligenceOrchestrator:
    """
    Central orchestrator for Planning System intelligence.
    
    Coordinates all intelligence adapters and provides unified API
    for intelligent plan validation, generation, and execution.
    
    Usage:
        orchestrator = IntelligenceOrchestrator(
            project_root=Path.cwd(),
            mode=IntelligenceMode.FULL
        )
        
        # Analyze plan
        report = await orchestrator.analyze_plan(plan_data, feature_description)
        
        if report.is_ready_for_execution():
            # Proceed with execution
        else:
            # Handle blocking issues
            for issue in report.blocking_issues:
                print(f"Blocking: {issue}")
    """
    
    def __init__(
        self,
        project_root: Path,
        mode: IntelligenceMode = IntelligenceMode.FULL,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize intelligence orchestrator.
        
        Args:
            project_root: Project root directory
            mode: Intelligence operation mode
            config: Optional configuration overrides
        """
        self.project_root = project_root
        self.mode = mode
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize adapters based on mode
        self._initialize_adapters()
    
    # ========== Initialization ==========
    
    def _initialize_adapters(self):
        """Initialize intelligence adapters based on mode."""
        # Test Intelligence
        if self.mode in [IntelligenceMode.FULL, IntelligenceMode.ADVISORY_ONLY]:
            self.test_intelligence = TestIntelligenceAdapter(
                project_root=self.project_root
            )
            self.logger.info("✓ Test Intelligence enabled")
        else:
            self.test_intelligence = None
        
        # TDD Intelligence
        if self.mode in [IntelligenceMode.FULL, IntelligenceMode.ADVISORY_ONLY]:
            self.tdd_intelligence = TDDIntelligenceAdapter(
                project_root=self.project_root,
                enforce_strict=self.config.get("tdd_strict_mode", True)
            )
            self.logger.info("✓ TDD Intelligence enabled")
        else:
            self.tdd_intelligence = None
        
        # Validation Framework
        if self.mode in [IntelligenceMode.FULL, IntelligenceMode.VALIDATION_ONLY, IntelligenceMode.MINIMAL]:
            self.validation_framework = ValidationFrameworkAdapter(
                strict_mode=self.config.get("validation_strict_mode", True)
            )
            self.logger.info("✓ Validation Framework enabled")
        else:
            self.validation_framework = None
        
        # Manifest Compliance
        if self.mode in [IntelligenceMode.FULL, IntelligenceMode.VALIDATION_ONLY, IntelligenceMode.MINIMAL]:
            self.manifest_validator = ManifestComplianceValidator(
                manifest_path=self.config.get("manifest_path")
            )
            self.logger.info("✓ Manifest Compliance enabled")
        else:
            self.manifest_validator = None
    
    # ========== Main Intelligence API ==========
    
    async def analyze_plan(
        self,
        plan_data: Dict[str, Any],
        feature_description: Optional[str] = None,
        validate_tdd_workflow: bool = True
    ) -> IntelligenceReport:
        """
        Perform comprehensive intelligence analysis on plan.
        
        Args:
            plan_data: Plan data to analyze
            feature_description: Optional feature description
            validate_tdd_workflow: Validate TDD workflow compliance
            
        Returns:
            Aggregated intelligence report
        """
        self.logger.info(f"🧠 Starting intelligence analysis (mode: {self.mode.value})")
        
        report = IntelligenceReport(mode=self.mode)
        
        # Run intelligence adapters in parallel where possible
        tasks = []
        
        # Test Intelligence
        if self.test_intelligence:
            tasks.append(self._run_test_intelligence(report, feature_description))
        
        # TDD Intelligence
        if self.tdd_intelligence and validate_tdd_workflow:
            tasks.append(self._run_tdd_intelligence(report, plan_data))
        
        # Validation Framework
        if self.validation_framework:
            tasks.append(self._run_validation_framework(report, plan_data))
        
        # Manifest Compliance
        if self.manifest_validator:
            tasks.append(self._run_manifest_compliance(report, plan_data))
        
        # Execute all intelligence tasks
        if tasks:
            await asyncio.gather(*tasks)
        
        # Aggregate results
        self._aggregate_intelligence(report)
        
        self.logger.info(f"🧠 Intelligence analysis complete: {report.get_summary()}")
        return report
    
    # ========== Individual Intelligence Runners ==========
    
    async def _run_test_intelligence(
        self,
        report: IntelligenceReport,
        feature_description: Optional[str]
    ):
        """Run test intelligence analysis."""
        try:
            # Analyze project coverage
            coverage = self.test_intelligence.analyze_project_coverage()
            report.test_coverage_analysis = coverage
            
            # Identify critical gaps
            gaps = self.test_intelligence.identify_critical_gaps(target_modules=None)
            report.test_gaps = gaps
            
            # Generate test strategy
            feature_scope = {
                "description": feature_description or "Feature implementation",
                "files_affected": []
            }
            strategy_dict = self.test_intelligence.generate_test_strategy(
                feature_scope,
                target_coverage=85.0
            )
            report.test_strategy = strategy_dict
            
            # Add recommendations
            if coverage.overall_coverage < 85:
                report.recommendations.append(
                    f"📊 Test coverage at {coverage.overall_coverage:.1f}% (target: 85%+)"
                )
            
            for gap in gaps[:3]:  # Top 3 gaps
                if gap.severity == "critical":
                    report.blocking_issues.append(
                        f"Critical test gap: {gap.module_name} ({gap.reason})"
                    )
                elif gap.severity == "high":
                    report.warnings.append(
                        f"High priority test gap: {gap.module_name}"
                    )
            
        except Exception as e:
            self.logger.error(f"Test intelligence failed: {e}")
            report.warnings.append(f"Test intelligence unavailable: {e}")
    
    async def _run_tdd_intelligence(
        self,
        report: IntelligenceReport,
        plan_data: Dict[str, Any]
    ):
        """Run TDD intelligence analysis."""
        try:
            # Check if TDD workflow exists
            if "tdd_workflow" in plan_data:
                tdd_workflow = plan_data["tdd_workflow"]
                
                # Validate workflow
                is_valid, errors = self.tdd_intelligence.validate_tdd_workflow(tdd_workflow)
                report.tdd_workflow_status = {
                    "valid": is_valid,
                    "errors": errors
                }
                
                # Calculate quality score
                if is_valid:
                    report.tdd_quality_score = 10.0  # Perfect score
                else:
                    report.tdd_quality_score = max(0, 10 - len(errors) * 2)
                
                # Add errors as blocking issues
                for error in errors:
                    report.blocking_issues.append(f"TDD workflow: {error}")
            else:
                # Check if TDD is required
                complexity = plan_data.get("metadata", {}).get("complexity", "low")
                if complexity in ["medium", "high", "complex"]:
                    report.blocking_issues.append(
                        f"TDD workflow required for {complexity} complexity"
                    )
            
            # Generate TDD strategy
            feature_scope = {
                "feature_type": plan_data.get("metadata", {}).get("feature_type", "feature"),
                "description": plan_data.get("metadata", {}).get("plan_name", "")
            }
            strategy = self.tdd_intelligence.generate_tdd_strategy(
                feature_scope=feature_scope,
                complexity=plan_data.get("metadata", {}).get("complexity", "low")
            )
            report.tdd_recommendations = strategy.reasoning
            
        except Exception as e:
            self.logger.error(f"TDD intelligence failed: {e}")
            report.warnings.append(f"TDD intelligence unavailable: {e}")
    
    async def _run_validation_framework(
        self,
        report: IntelligenceReport,
        plan_data: Dict[str, Any]
    ):
        """Run validation framework analysis."""
        try:
            # Validate plan
            validation_report = await self.validation_framework.validate_plan(
                plan_data,
                validation_levels=["schema", "business_rule", "cross_field"]
            )
            
            report.validation_report = validation_report
            report.validation_passed = validation_report.is_valid
            
            # Add blocking errors
            for error in validation_report.get_blocking_errors():
                report.blocking_issues.append(f"Validation: {error.message}")
            
            # Add warnings
            for result in validation_report.results:
                if result.level == ValidationLevel.WARNING:
                    report.warnings.append(f"Validation: {result.message}")
            
        except Exception as e:
            self.logger.error(f"Validation framework failed: {e}")
            report.blocking_issues.append(f"Validation failed: {e}")
    
    async def _run_manifest_compliance(
        self,
        report: IntelligenceReport,
        plan_data: Dict[str, Any]
    ):
        """Run manifest compliance analysis."""
        try:
            # Validate compliance
            compliance_report = self.manifest_validator.validate_plan_compliance(plan_data)
            
            report.compliance_report = compliance_report
            report.compliance_level = compliance_report.compliance_level
            
            # Add critical violations as blocking issues
            for violation in compliance_report.get_critical_violations():
                report.blocking_issues.append(f"Manifest: {violation.message}")
            
            # Add major violations as warnings
            for violation in compliance_report.violations:
                if violation.severity == "major":
                    report.warnings.append(f"Manifest: {violation.message}")
            
            # Add DoR/DoD scores to recommendations
            if compliance_report.dor_compliance < 100:
                report.recommendations.append(
                    f"📋 DoR compliance: {compliance_report.dor_compliance:.0f}%"
                )
            if compliance_report.dod_compliance < 100:
                report.recommendations.append(
                    f"📋 DoD compliance: {compliance_report.dod_compliance:.0f}%"
                )
            
        except Exception as e:
            self.logger.error(f"Manifest compliance failed: {e}")
            report.warnings.append(f"Manifest compliance unavailable: {e}")
    
    # ========== Aggregation ==========
    
    def _aggregate_intelligence(self, report: IntelligenceReport):
        """Aggregate intelligence results into overall assessment."""
        scores = []
        
        # Test coverage score (0-100)
        if report.test_coverage_analysis:
            scores.append(report.test_coverage_analysis.overall_coverage)
        
        # TDD quality score (0-10 → 0-100)
        if report.tdd_quality_score > 0:
            scores.append(report.tdd_quality_score * 10)
        
        # Validation score (0-100)
        if report.validation_passed:
            scores.append(100.0)
        elif report.validation_report:
            # Penalty based on errors
            penalty = report.validation_report.errors * 10
            scores.append(max(0, 100 - penalty))
        
        # Compliance score (0-100)
        if report.compliance_report:
            scores.append(report.compliance_report.overall_score)
        
        # Calculate overall score
        if scores:
            report.overall_score = sum(scores) / len(scores)
        else:
            report.overall_score = 0.0
        
        # Determine execution approval
        report.execution_approved = (
            len(report.blocking_issues) == 0 and
            report.overall_score >= 70.0  # Minimum threshold
        )
    
    # ========== Public API Methods ==========
    
    async def validate_plan(
        self,
        plan_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate plan (blocking validation only).
        
        Returns:
            (is_valid, error_messages)
        """
        report = await self.analyze_plan(plan_data, validate_tdd_workflow=True)
        return (len(report.blocking_issues) == 0, report.blocking_issues)
    
    async def get_test_strategy(
        self,
        feature_description: str
    ) -> Dict[str, Any]:
        """Get intelligent test strategy for feature."""
        if not self.test_intelligence:
            return {"error": "Test intelligence not enabled"}
        
        feature_scope = {
            "description": feature_description,
            "files_affected": []
        }
        return self.test_intelligence.generate_test_strategy(
            feature_scope,
            target_coverage=85.0
        )
    
    async def get_tdd_recommendations(
        self,
        feature_scope: Dict[str, Any],
        complexity: str = "medium"
    ) -> Dict[str, Any]:
        """Get TDD recommendations for feature."""
        if not self.tdd_intelligence:
            return {"error": "TDD intelligence not enabled"}
        
        strategy = self.tdd_intelligence.generate_tdd_strategy(
            feature_scope=feature_scope,
            complexity=complexity
        )
        return {
            "recommendations": strategy.reasoning,
            "recommended": strategy.recommended,
            "estimated_cycles": strategy.estimated_cycles,
            "test_first_modules": strategy.test_first_modules,
            "implementation_order": strategy.implementation_order
        }
    
    def get_coverage_gaps(self) -> List[Any]:
        """Get current test coverage gaps."""
        if not self.test_intelligence:
            return []
        
        return self.test_intelligence.identify_critical_gaps(target_modules=None)
    
    # ========== Configuration ==========
    
    def set_mode(self, mode: IntelligenceMode):
        """Change intelligence mode."""
        self.mode = mode
        self._initialize_adapters()
        self.logger.info(f"Intelligence mode changed to: {mode.value}")
    
    def enable_adapter(self, adapter_name: str):
        """Enable specific adapter."""
        if adapter_name == "test" and not self.test_intelligence:
            self.test_intelligence = TestIntelligenceAdapter(self.project_root)
        elif adapter_name == "tdd" and not self.tdd_intelligence:
            self.tdd_intelligence = TDDIntelligenceAdapter(self.project_root)
        elif adapter_name == "validation" and not self.validation_framework:
            self.validation_framework = ValidationFrameworkAdapter()
        elif adapter_name == "manifest" and not self.manifest_validator:
            self.manifest_validator = ManifestComplianceValidator()
    
    def disable_adapter(self, adapter_name: str):
        """Disable specific adapter."""
        if adapter_name == "test":
            self.test_intelligence = None
        elif adapter_name == "tdd":
            self.tdd_intelligence = None
        elif adapter_name == "validation":
            self.validation_framework = None
        elif adapter_name == "manifest":
            self.manifest_validator = None
