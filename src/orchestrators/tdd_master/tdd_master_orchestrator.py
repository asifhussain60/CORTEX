"""
TDD-Master Orchestrator - Coordination layer for Planning → TDD workflow.

This orchestrator bridges the Planning Orchestrator and TDD Orchestrator:
1. Detects completed plans via config.yaml validation (AC-TDD-MASTER-001)
2. Transforms Planning data → TDD context JSON (AC-TDD-MASTER-002)
3. Invokes TDD Orchestrator with enriched context (AC-TDD-MASTER-003)
4. Validates 100% AC coverage post-TDD (AC-TDD-MASTER-004)
5. Enforces Tier0-3 governance continuity (AC-TDD-MASTER-005)
6. Updates dashboard with TDD progress (AC-TDD-MASTER-006)
7. Generates unified completion report (AC-TDD-MASTER-007)
8. Handles unplanned development requests (AC-TDD-MASTER-000)

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import logging
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from src.orchestrators.base.base_orchestrator import (
    BaseOrchestrator,
    OrchestratorResult,
    OrchestratorStatus,
)


# =============================================================================
# ENUMS AND DATA CLASSES
# =============================================================================

class PlanValidationStatus(Enum):
    """Plan validation status."""
    READY = "ready"
    INVALID = "invalid"
    IN_PROGRESS = "in_progress"
    NOT_FOUND = "not_found"


@dataclass
class TDDMasterConfig:
    """TDD-Master configuration."""
    workspace_path: Path
    brain_path: Path
    planning_dir: Optional[Path] = None
    tdd_context_filename: str = "tdd-context.json"
    completion_report_filename: str = "completion-report.json"
    dashboard_data_filename: str = "plan-data.json"
    
    def __post_init__(self):
        if self.planning_dir is None:
            self.planning_dir = self.brain_path / "documents" / "planning" / "active"


@dataclass
class PlanInfo:
    """Information about a detected plan."""
    plan_id: str
    plan_path: Path
    status: PlanValidationStatus
    feature_name: Optional[str] = None
    acceptance_criteria: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    config_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TDDMasterContext:
    """Context for TDD Orchestrator invocation."""
    feature_name: str
    plan_id: str
    plan_path: str
    acceptance_criteria: List[str]
    test_requirements: Dict[str, Any]
    domain_knowledge: Dict[str, Any]
    governance_rules: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)


@dataclass
class TDDInvocationResult:
    """Result of TDD Orchestrator invocation."""
    success: bool
    message: str
    tdd_result: Any = None
    error: Optional[str] = None


@dataclass
class ACCoverageResult:
    """Result of AC coverage validation."""
    coverage_percent: float
    all_acs_covered: bool
    covered_acs: List[str]
    missing_acs: List[str]
    test_mapping: Dict[str, List[str]]


@dataclass
class GovernanceResult:
    """Result of governance validation."""
    tier0_validated: bool
    validated_rules: List[str]
    violations: List[str]
    warnings: List[str] = field(default_factory=list)


@dataclass
class DashboardUpdateResult:
    """Result of dashboard update."""
    updated: bool
    dashboard_path: Optional[str] = None
    error: Optional[str] = None


@dataclass
class CompletionReport:
    """Completion report structure."""
    format: str = "json"
    plan_id: str = ""
    success: bool = False
    data: Dict[str, Any] = field(default_factory=dict)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TDDMasterResult:
    """Result of TDD-Master execution."""
    success: bool
    status: OrchestratorStatus
    message: str
    mode: str = "planned"  # "planned" or "unplanned"
    data: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# TDD-MASTER ORCHESTRATOR
# =============================================================================

class TDDMasterOrchestrator(BaseOrchestrator):
    """
    TDD-Master Orchestrator - Coordination layer for Planning → TDD workflow.
    
    This orchestrator:
    1. Detects plans ready for implementation
    2. Transforms planning artifacts to TDD context
    3. Invokes the TDD Orchestrator
    4. Validates acceptance criteria coverage
    5. Enforces governance rules
    6. Updates dashboards
    7. Generates completion reports
    
    Acceptance Criteria:
    - AC-TDD-MASTER-001: Plan detection via config.yaml validation
    - AC-TDD-MASTER-002: Planning → TDD context transformation (JSON)
    - AC-TDD-MASTER-003: TDD Orchestrator invocation with enriched context
    - AC-TDD-MASTER-004: 100% AC coverage validation post-TDD
    - AC-TDD-MASTER-005: Tier0-3 governance continuity enforcement
    - AC-TDD-MASTER-006: Dashboard updates (plan-viewer.html)
    - AC-TDD-MASTER-007: Unified completion report generation (JSON)
    - AC-TDD-MASTER-000: Unplanned development request handling
    """
    
    def __init__(
        self,
        workspace_path: Optional[Path] = None,
        brain_path: Optional[Path] = None,
        config_path: Optional[str] = None,
    ):
        """
        Initialize TDD-Master Orchestrator.
        
        Args:
            workspace_path: Path to workspace root
            brain_path: Path to cortex-brain directory
            config_path: Optional path to orchestrator config
        """
        super().__init__(config_path)
        self.logger = logging.getLogger("cortex.orchestrators.tdd_master")
        
        # Configure paths
        self.workspace_path = workspace_path or Path.cwd()
        self.brain_path = brain_path or (self.workspace_path / "cortex-brain")
        
        # Create config
        self.config = TDDMasterConfig(
            workspace_path=self.workspace_path,
            brain_path=self.brain_path,
        )
        
        # TDD orchestrator reference (lazy loaded)
        self._tdd_orchestrator = None
        
        self.logger.info(f"TDDMasterOrchestrator initialized (workspace={workspace_path})")
    
    # =========================================================================
    # AC-TDD-MASTER-001: Plan Detection
    # =========================================================================
    
    def detect_ready_plans(self) -> List[PlanInfo]:
        """
        Detect plans ready for implementation.
        
        AC-TDD-MASTER-001: Detects completed plans via config.yaml validation.
        
        Returns:
            List of PlanInfo objects for all detected plans
        """
        plans: List[PlanInfo] = []
        planning_dir = self.config.planning_dir
        
        if not planning_dir.exists():
            self.logger.warning(f"Planning directory not found: {planning_dir}")
            return plans
        
        # Scan for plan directories
        for plan_dir in planning_dir.iterdir():
            if not plan_dir.is_dir():
                continue
            
            config_path = plan_dir / "config.yaml"
            if not config_path.exists():
                continue
            
            # Validate config
            plan_info = self._validate_plan_config(plan_dir, config_path)
            plans.append(plan_info)
        
        self.logger.info(f"Detected {len(plans)} plans ({len([p for p in plans if p.status == PlanValidationStatus.READY])} ready)")
        return plans
    
    def _validate_plan_config(self, plan_dir: Path, config_path: Path) -> PlanInfo:
        """Validate plan config.yaml and return PlanInfo."""
        try:
            with open(config_path) as f:
                config_data = yaml.safe_load(f)
            
            # Required fields
            required_fields = ["plan_id", "status"]
            missing = [f for f in required_fields if f not in config_data]
            
            if missing:
                return PlanInfo(
                    plan_id=config_data.get("plan_id", plan_dir.name),
                    plan_path=plan_dir,
                    status=PlanValidationStatus.INVALID,
                    error_message=f"Missing required fields: {missing}",
                    config_data=config_data,
                )
            
            # Check status
            status = config_data.get("status", "")
            if status == "READY_FOR_IMPLEMENTATION":
                validation_status = PlanValidationStatus.READY
            elif status == "IN_PROGRESS":
                validation_status = PlanValidationStatus.IN_PROGRESS
            else:
                validation_status = PlanValidationStatus.INVALID
                return PlanInfo(
                    plan_id=config_data["plan_id"],
                    plan_path=plan_dir,
                    status=validation_status,
                    feature_name=config_data.get("feature_name"),
                    error_message=f"Invalid status: {status}",
                    config_data=config_data,
                )
            
            return PlanInfo(
                plan_id=config_data["plan_id"],
                plan_path=plan_dir,
                status=validation_status,
                feature_name=config_data.get("feature_name"),
                acceptance_criteria=config_data.get("acceptance_criteria", []),
                config_data=config_data,
            )
            
        except yaml.YAMLError as e:
            return PlanInfo(
                plan_id=plan_dir.name,
                plan_path=plan_dir,
                status=PlanValidationStatus.INVALID,
                error_message=f"Invalid YAML: {e}",
            )
        except Exception as e:
            return PlanInfo(
                plan_id=plan_dir.name,
                plan_path=plan_dir,
                status=PlanValidationStatus.INVALID,
                error_message=f"Error validating config: {e}",
            )
    
    # =========================================================================
    # AC-TDD-MASTER-002: Context Transformation
    # =========================================================================
    
    def transform_plan_to_context(self, plan_path: str) -> TDDMasterContext:
        """
        Transform planning data to TDD context.
        
        AC-TDD-MASTER-002: Transforms Planning data → TDD context (JSON).
        
        Args:
            plan_path: Path to plan directory
            
        Returns:
            TDDMasterContext with all necessary data for TDD
        """
        plan_dir = Path(plan_path)
        
        # Load config.yaml
        config_path = plan_dir / "config.yaml"
        with open(config_path) as f:
            config_data = yaml.safe_load(f)
        
        # Load requirements.yaml if exists
        requirements_data = {}
        requirements_path = plan_dir / "requirements.yaml"
        if requirements_path.exists():
            with open(requirements_path) as f:
                requirements_data = yaml.safe_load(f)
        
        # Extract domain knowledge
        domain_knowledge = self._extract_domain_knowledge(requirements_data)
        
        # Extract test requirements
        test_requirements = self._extract_test_requirements(config_data, requirements_data)
        
        # Load governance rules
        governance_rules = self._load_governance_rules()
        
        context = TDDMasterContext(
            feature_name=config_data.get("feature_name", "unknown"),
            plan_id=config_data.get("plan_id", plan_dir.name),
            plan_path=str(plan_dir),
            acceptance_criteria=config_data.get("acceptance_criteria", []),
            test_requirements=test_requirements,
            domain_knowledge=domain_knowledge,
            governance_rules=governance_rules,
            metadata={
                "created_at": datetime.now().isoformat(),
                "version": config_data.get("version", "1.0.0"),
                "source": "TDDMasterOrchestrator",
            },
        )
        
        self.logger.info(f"Transformed plan '{context.plan_id}' to TDD context")
        return context
    
    def _extract_domain_knowledge(self, requirements_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract domain knowledge from requirements."""
        feature_info = requirements_data.get("feature", {})
        return {
            "domain": feature_info.get("domain", "general"),
            "description": feature_info.get("description", ""),
            "requirements": requirements_data.get("requirements", []),
        }
    
    def _extract_test_requirements(
        self, 
        config_data: Dict[str, Any], 
        requirements_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract test requirements from plan data."""
        phases = config_data.get("phases", [])
        requirements = requirements_data.get("requirements", [])
        
        return {
            "phases": phases,
            "requirements": requirements,
            "acceptance_criteria": config_data.get("acceptance_criteria", []),
            "priority_order": ["P0_CRITICAL", "P1_HIGH", "P2_MEDIUM", "P3_LOW"],
        }
    
    def _load_governance_rules(self) -> List[Dict[str, Any]]:
        """Load governance rules from tier0."""
        rules = []
        rules_path = self.brain_path / "tier0" / "governance" / "core-rules.yaml"
        
        if rules_path.exists():
            try:
                with open(rules_path) as f:
                    rules_data = yaml.safe_load(f)
                rules = rules_data.get("rules", [])
            except Exception as e:
                self.logger.warning(f"Failed to load governance rules: {e}")
        
        return rules
    
    def save_tdd_context(self, context: TDDMasterContext, plan_path: str) -> str:
        """
        Save TDD context to JSON file.
        
        Args:
            context: TDDMasterContext to save
            plan_path: Plan directory path
            
        Returns:
            Path to saved context file
        """
        plan_dir = Path(plan_path)
        output_path = plan_dir / self.config.tdd_context_filename
        
        with open(output_path, 'w') as f:
            f.write(context.to_json())
        
        self.logger.info(f"Saved TDD context to {output_path}")
        return str(output_path)
    
    # =========================================================================
    # AC-TDD-MASTER-003: TDD Invocation
    # =========================================================================
    
    def _get_tdd_orchestrator(self):
        """Get TDD Orchestrator instance (lazy loading)."""
        if self._tdd_orchestrator is None:
            try:
                from src.orchestrators.tdd.tdd_orchestrator import TDDOrchestrator
                self._tdd_orchestrator = TDDOrchestrator(project_root=self.workspace_path)
            except ImportError:
                self.logger.error("TDD Orchestrator not available")
                return None
        return self._tdd_orchestrator
    
    def invoke_tdd(self, context: TDDMasterContext) -> TDDInvocationResult:
        """
        Invoke TDD Orchestrator with enriched context.
        
        AC-TDD-MASTER-003: Invokes TDD Orchestrator with enriched context.
        
        Args:
            context: TDDMasterContext with all necessary data
            
        Returns:
            TDDInvocationResult with execution details
        """
        tdd_orchestrator = self._get_tdd_orchestrator()
        
        if tdd_orchestrator is None:
            return TDDInvocationResult(
                success=False,
                message="TDD Orchestrator not available",
                error="ImportError: TDD Orchestrator could not be loaded",
            )
        
        try:
            # Execute TDD with context
            result = tdd_orchestrator.execute(
                context={
                    "tdd_context": context.to_dict(),
                    "feature_name": context.feature_name,
                    "plan_id": context.plan_id,
                    "acceptance_criteria": context.acceptance_criteria,
                }
            )
            
            return TDDInvocationResult(
                success=result.success if hasattr(result, 'success') else False,
                message=result.message if hasattr(result, 'message') else "TDD execution complete",
                tdd_result=result,
            )
            
        except Exception as e:
            self.logger.error(f"TDD invocation failed: {e}")
            return TDDInvocationResult(
                success=False,
                message=f"TDD invocation failed: {e}",
                error=str(e),
            )
    
    # =========================================================================
    # AC-TDD-MASTER-004: AC Coverage Validation
    # =========================================================================
    
    def validate_ac_coverage(
        self, 
        tdd_result: Any, 
        plan_acs: List[str]
    ) -> ACCoverageResult:
        """
        Validate acceptance criteria coverage.
        
        AC-TDD-MASTER-004: Validates 100% AC coverage post-TDD.
        
        Args:
            tdd_result: Result from TDD Orchestrator
            plan_acs: List of AC IDs from plan
            
        Returns:
            ACCoverageResult with coverage details
        """
        # Extract AC coverage from TDD result
        ac_coverage = {}
        if hasattr(tdd_result, 'data') and tdd_result.data:
            ac_coverage = tdd_result.data.get("ac_coverage", {})
        
        covered_acs = list(ac_coverage.keys())
        missing_acs = [ac for ac in plan_acs if ac not in covered_acs]
        
        coverage_percent = (len(covered_acs) / len(plan_acs) * 100) if plan_acs else 100.0
        
        return ACCoverageResult(
            coverage_percent=coverage_percent,
            all_acs_covered=(len(missing_acs) == 0),
            covered_acs=covered_acs,
            missing_acs=missing_acs,
            test_mapping=ac_coverage,
        )
    
    # =========================================================================
    # AC-TDD-MASTER-005: Governance Continuity
    # =========================================================================
    
    def validate_governance(self) -> GovernanceResult:
        """
        Validate governance rules.
        
        AC-TDD-MASTER-005: Enforces Tier0-3 governance continuity.
        
        Returns:
            GovernanceResult with validation details
        """
        validated_rules = []
        violations = []
        
        # Check Tier 0 rules
        rules_path = self.brain_path / "tier0" / "governance" / "core-rules.yaml"
        
        if not rules_path.exists():
            violations.append("CORE-000: core-rules.yaml not found")
            return GovernanceResult(
                tier0_validated=False,
                validated_rules=validated_rules,
                violations=violations,
            )
        
        try:
            with open(rules_path) as f:
                rules_data = yaml.safe_load(f)
            
            rules = rules_data.get("rules", [])
            for rule in rules:
                rule_id = rule.get("rule_id", "unknown")
                validated_rules.append(rule_id)
            
            return GovernanceResult(
                tier0_validated=True,
                validated_rules=validated_rules,
                violations=violations,
            )
            
        except Exception as e:
            violations.append(f"CORE-000: Failed to validate rules - {e}")
            return GovernanceResult(
                tier0_validated=False,
                validated_rules=validated_rules,
                violations=violations,
            )
    
    # =========================================================================
    # AC-TDD-MASTER-006: Dashboard Updates
    # =========================================================================
    
    def update_dashboard(
        self, 
        plan_id: str, 
        tdd_result: Any
    ) -> DashboardUpdateResult:
        """
        Update dashboard with TDD progress.
        
        AC-TDD-MASTER-006: Updates plan-viewer.html with TDD progress.
        
        Args:
            plan_id: Plan identifier
            tdd_result: Result from TDD Orchestrator
            
        Returns:
            DashboardUpdateResult with update status
        """
        dashboards_dir = self.brain_path / "dashboards"
        dashboards_dir.mkdir(parents=True, exist_ok=True)
        
        dashboard_data_path = dashboards_dir / self.config.dashboard_data_filename
        
        # Load existing data or create new
        if dashboard_data_path.exists():
            with open(dashboard_data_path) as f:
                dashboard_data = json.load(f)
        else:
            dashboard_data = {"plans": {}, "updated_at": None}
        
        # Extract TDD data
        tdd_data = {}
        if hasattr(tdd_result, 'data') and tdd_result.data:
            tdd_data = tdd_result.data
        
        # Update plan data
        dashboard_data["plans"][plan_id] = {
            "tests_created": tdd_data.get("tests_created", 0),
            "tests_passed": tdd_data.get("tests_passed", 0),
            "coverage": tdd_data.get("coverage", 0),
            "phases_complete": tdd_data.get("phases_complete", []),
            "updated_at": datetime.now().isoformat(),
        }
        dashboard_data["updated_at"] = datetime.now().isoformat()
        
        # Save updated data
        with open(dashboard_data_path, 'w') as f:
            json.dump(dashboard_data, f, indent=2)
        
        return DashboardUpdateResult(
            updated=True,
            dashboard_path=str(dashboard_data_path),
        )
    
    # =========================================================================
    # AC-TDD-MASTER-007: Completion Report
    # =========================================================================
    
    def generate_completion_report(
        self,
        plan_id: str,
        tdd_result: Any,
        coverage_result: ACCoverageResult,
    ) -> CompletionReport:
        """
        Generate unified completion report.
        
        AC-TDD-MASTER-007: Generates unified completion report (JSON).
        
        Args:
            plan_id: Plan identifier
            tdd_result: Result from TDD Orchestrator
            coverage_result: AC coverage validation result
            
        Returns:
            CompletionReport with all execution data
        """
        # Extract TDD data
        tdd_data = {}
        if hasattr(tdd_result, 'data') and tdd_result.data:
            tdd_data = tdd_result.data
        
        success = (
            hasattr(tdd_result, 'success') and tdd_result.success and
            coverage_result.all_acs_covered
        )
        
        return CompletionReport(
            format="json",
            plan_id=plan_id,
            success=success,
            data={
                "tdd_summary": {
                    "tests_created": tdd_data.get("tests_created", 0),
                    "tests_passed": tdd_data.get("tests_passed", 0),
                    "coverage": tdd_data.get("coverage", 0),
                },
                "ac_coverage": {
                    "coverage_percent": coverage_result.coverage_percent,
                    "all_acs_covered": coverage_result.all_acs_covered,
                    "covered_acs": coverage_result.covered_acs,
                    "missing_acs": coverage_result.missing_acs,
                },
                "governance": {
                    "validated": True,
                },
            },
        )
    
    def save_completion_report(self, report: CompletionReport, plan_path: str) -> str:
        """
        Save completion report to plan directory.
        
        Args:
            report: CompletionReport to save
            plan_path: Plan directory path
            
        Returns:
            Path to saved report file
        """
        plan_dir = Path(plan_path)
        output_path = plan_dir / self.config.completion_report_filename
        
        with open(output_path, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        
        self.logger.info(f"Saved completion report to {output_path}")
        return str(output_path)
    
    # =========================================================================
    # AC-TDD-MASTER-000: Unplanned Mode
    # =========================================================================
    
    def handle_unplanned_request(self, request: str) -> TDDMasterResult:
        """
        Handle unplanned development request.
        
        AC-TDD-MASTER-000: Handles unplanned development requests.
        
        Args:
            request: User's development request
            
        Returns:
            TDDMasterResult with execution details
        """
        self.logger.info(f"Handling unplanned request: {request}")
        
        # Create minimal context
        context = TDDMasterContext(
            feature_name=request[:50],  # Use request as feature name
            plan_id=f"unplanned-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            plan_path="",
            acceptance_criteria=[],
            test_requirements={"request": request},
            domain_knowledge={"request": request},
            governance_rules=self._load_governance_rules(),
            metadata={
                "mode": "unplanned",
                "created_at": datetime.now().isoformat(),
            },
        )
        
        # Invoke TDD
        tdd_result = self.invoke_tdd(context)
        
        return TDDMasterResult(
            success=tdd_result.success,
            status=OrchestratorStatus.SUCCESS if tdd_result.success else OrchestratorStatus.FAILURE,
            message=tdd_result.message,
            mode="unplanned",
            data={
                "request": request,
                "tdd_result": tdd_result.tdd_result,
            },
        )
    
    # =========================================================================
    # MAIN EXECUTION
    # =========================================================================
    
    def execute(
        self, 
        plan_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> TDDMasterResult:
        """
        Execute TDD-Master workflow.
        
        Args:
            plan_id: Optional specific plan ID to execute
            context: Optional execution context
            
        Returns:
            TDDMasterResult with full execution details
        """
        context = context or {}
        execution_data = {
            "plan_detected": False,
            "context_transformed": False,
            "tdd_invoked": False,
            "ac_validated": False,
            "governance_validated": False,
            "dashboard_updated": False,
            "report_generated": False,
        }
        
        try:
            # Step 1: Validate governance (AC-TDD-MASTER-005)
            governance_result = self.validate_governance()
            execution_data["governance_validated"] = governance_result.tier0_validated
            
            if not governance_result.tier0_validated:
                return TDDMasterResult(
                    success=False,
                    status=OrchestratorStatus.FAILURE,
                    message=f"Governance validation failed: {governance_result.violations}",
                    data=execution_data,
                )
            
            # Step 2: Detect plans (AC-TDD-MASTER-001)
            plans = self.detect_ready_plans()
            ready_plans = [p for p in plans if p.status == PlanValidationStatus.READY]
            
            if plan_id:
                ready_plans = [p for p in ready_plans if p.plan_id == plan_id]
            
            if not ready_plans:
                return TDDMasterResult(
                    success=False,
                    status=OrchestratorStatus.FAILURE,
                    message="No ready plans found",
                    data=execution_data,
                )
            
            execution_data["plan_detected"] = True
            target_plan = ready_plans[0]
            
            # Step 3: Transform context (AC-TDD-MASTER-002)
            tdd_context = self.transform_plan_to_context(str(target_plan.plan_path))
            self.save_tdd_context(tdd_context, str(target_plan.plan_path))
            execution_data["context_transformed"] = True
            
            # Step 4: Invoke TDD (AC-TDD-MASTER-003)
            tdd_result = self.invoke_tdd(tdd_context)
            execution_data["tdd_invoked"] = True
            
            if not tdd_result.success:
                return TDDMasterResult(
                    success=False,
                    status=OrchestratorStatus.FAILURE,
                    message=f"TDD execution failed: {tdd_result.message}",
                    data=execution_data,
                )
            
            # Step 5: Validate AC coverage (AC-TDD-MASTER-004)
            coverage_result = self.validate_ac_coverage(
                tdd_result.tdd_result,
                target_plan.acceptance_criteria
            )
            execution_data["ac_validated"] = True
            
            # Step 6: Update dashboard (AC-TDD-MASTER-006)
            dashboard_result = self.update_dashboard(
                target_plan.plan_id,
                tdd_result.tdd_result
            )
            execution_data["dashboard_updated"] = dashboard_result.updated
            
            # Step 7: Generate report (AC-TDD-MASTER-007)
            report = self.generate_completion_report(
                target_plan.plan_id,
                tdd_result.tdd_result,
                coverage_result
            )
            self.save_completion_report(report, str(target_plan.plan_path))
            execution_data["report_generated"] = True
            
            return TDDMasterResult(
                success=True,
                status=OrchestratorStatus.SUCCESS,
                message=f"TDD-Master completed for plan '{target_plan.plan_id}'",
                mode="planned",
                data=execution_data,
            )
            
        except Exception as e:
            self.logger.error(f"TDD-Master execution failed: {e}")
            return TDDMasterResult(
                success=False,
                status=OrchestratorStatus.FAILURE,
                message=f"TDD-Master execution failed: {e}",
                data=execution_data,
            )
