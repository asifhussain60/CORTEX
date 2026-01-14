"""
CORTEX Review Orchestrator v2.0.0

Validates epic plans against implementation and design goals using a 7-phase pipeline:
1. Epic Structure Analysis
2. Architecture Coherence Review
3. Knowledge Integration Analysis
4. Orchestrator Registry Audit
5. Edge Case & Failure Mode Analysis
6. Implementation Fidelity Check
7. Best Practices & Governance Validation

Author: Asif Hussain
Version: 2.0.0
Created: 2026-01-07
"""

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import logging
import json
import yaml

from src.orchestrators.base.base_orchestrator import BaseOrchestrator
from src.infrastructure.state_manager import StateManager

# Import analyzers
from .analyzers.epic_structure_analyzer import EpicStructureAnalyzer
from .analyzers.architecture_analyzer import ArchitectureAnalyzer
from .analyzers.knowledge_analyzer import KnowledgeAnalyzer
from .analyzers.registry_analyzer import RegistryAnalyzer
from .analyzers.edge_case_analyzer import EdgeCaseAnalyzer
from .analyzers.fidelity_analyzer import FidelityAnalyzer
from .analyzers.governance_analyzer import GovernanceAnalyzer

# Import validators
from .validators.python_validator import PythonValidator
from .validators.audit_log_validator import AuditLogValidator
from .validators.phase_progression_validator import PhaseProgressionValidator

# Import reporters
from .reporters.yaml_reporter import YAMLReporter
from .reporters.markdown_reporter import MarkdownReporter


class ReviewOrchestratorV2(BaseOrchestrator):
    """
    Comprehensive epic plan and implementation review orchestrator.
    
    This orchestrator validates epic plans against CORTEX design goals,
    architecture integrity, autonomous execution capabilities, and
    governance compliance.
    
    Attributes:
        state_db: Planning state database
        epic_path: Path to epic folder
        review_type: Type of review (baseline, progress, phase, final, etc.)
        phase_id: Specific phase to review (if review_type=phase)
        output_format: Output format (yaml, markdown, json)
        include_static_analysis: Run static analysis tools
        include_audit_validation: Cross-check audit logs
    
    Example:
        >>> orchestrator = ReviewOrchestratorV2(
        ...     config_path="config.yaml",
        ...     state_db=state_db,
        ...     epic_path="active/cortex5-epic",
        ...     review_type="comprehensive"
        ... )
        >>> results = orchestrator.execute("review epic")
    """
    
    def __init__(
        self,
        config_path: str,
        state_db: PlanningStateDB,
        epic_path: str,
        review_type: str = "comprehensive",
        phase_id: Optional[str] = None,
        output_format: str = "yaml",
        include_static_analysis: bool = True,
        include_audit_validation: bool = True
    ):
        """
        Initialize review orchestrator.
        
        Args:
            config_path: Path to configuration file
            state_db: Planning state database instance
            epic_path: Path to epic folder (active/archived)
            review_type: Type of review to perform
            phase_id: Specific phase to review (optional)
            output_format: Output format (yaml/markdown/json)
            include_static_analysis: Run static analysis tools
            include_audit_validation: Cross-check audit logs
        
        Raises:
            FileNotFoundError: If epic_path doesn't exist
            ValueError: If review_type invalid or phase_id required but missing
        """
        super().__init__(config_path)
        self.state_db = state_db
        self.epic_path = Path(epic_path)
        self.review_type = review_type
        self.phase_id = phase_id
        self.output_format = output_format
        self.include_static_analysis = include_static_analysis
        self.include_audit_validation = include_audit_validation
        self.logger = logging.getLogger(__name__)
        
        # Validate inputs
        self._validate_inputs()
        
        # Initialize analyzers
        self._init_analyzers()
        
        # Initialize validators
        self._init_validators()
        
        # Initialize reporters
        self._init_reporters()
    
    def _validate_inputs(self) -> None:
        """Validate input parameters."""
        # Check epic path exists
        if not self.epic_path.exists():
            raise FileNotFoundError(f"Epic path not found: {self.epic_path}")
        
        # Check required files exist
        required_files = ["progress-tracker.json", "CONTINUATION-PROMPT.md"]
        for file in required_files:
            if not (self.epic_path / file).exists():
                raise FileNotFoundError(
                    f"Required file missing in epic: {file}"
                )
        
        # Validate review_type
        valid_types = [
            "baseline", "progress", "phase", "final",
            "retrospective", "comprehensive"
        ]
        if self.review_type not in valid_types:
            raise ValueError(
                f"Invalid review_type: {self.review_type}. "
                f"Must be one of: {', '.join(valid_types)}"
            )
        
        # Check phase_id if review_type is phase
        if self.review_type == "phase" and not self.phase_id:
            raise ValueError(
                "phase_id required when review_type='phase'"
            )
    
    def _init_analyzers(self) -> None:
        """Initialize all analyzer modules."""
        self.logger.info("Initializing analyzers...")
        
        self.analyzers: Dict[str, Any] = {
            "structure": EpicStructureAnalyzer(
                self.epic_path,
                self.state_db
            ),
            "architecture": ArchitectureAnalyzer(
                self.epic_path,
                self.state_db
            ),
            "knowledge": KnowledgeAnalyzer(
                self.epic_path,
                self.state_db
            ),
            "registry": RegistryAnalyzer(
                self.epic_path,
                self.state_db
            ),
            "edge_cases": EdgeCaseAnalyzer(
                self.epic_path,
                self.state_db
            ),
            "fidelity": FidelityAnalyzer(
                self.epic_path,
                self.state_db
            ),
            "governance": GovernanceAnalyzer(
                self.epic_path,
                self.state_db
            )
        }
        
        self.logger.info(f"Initialized {len(self.analyzers)} analyzers")
    
    def _init_validators(self) -> None:
        """Initialize validator modules."""
        self.logger.info("Initializing validators...")
        
        self.validators: Dict[str, Any] = {}
        
        if self.include_static_analysis:
            self.validators["python"] = PythonValidator(
                self.epic_path
            )
        
        if self.include_audit_validation:
            self.validators["audit"] = AuditLogValidator(
                self.epic_path,
                self.state_db
            )
        
        self.validators["progression"] = PhaseProgressionValidator(
            self.epic_path,
            self.state_db
        )
        
        self.logger.info(f"Initialized {len(self.validators)} validators")
    
    def _init_reporters(self) -> None:
        """Initialize reporter modules."""
        self.logger.info("Initializing reporters...")
        
        self.reporters: Dict[str, Any] = {
            "yaml": YAMLReporter(self.epic_path),
            "markdown": MarkdownReporter(self.epic_path),
            "json": YAMLReporter(self.epic_path)  # Reuse YAML for JSON
        }
        
        self.logger.info(f"Initialized {len(self.reporters)} reporters")
    
    def execute(self, request: str, **kwargs) -> Dict[str, Any]:
        """
        Execute review based on review type.
        
        Args:
            request: User request string
            **kwargs: Additional parameters
        
        Returns:
            Review results with scores, blocking issues, and recommendations
        
        Raises:
            FileNotFoundError: If epic path doesn't exist
            ValidationError: If critical violations found
        """
        self.logger.info(
            f"Starting {self.review_type} review for {self.epic_path}"
        )
        
        start_time = datetime.now()
        
        # Log review start to state DB
        review_id = self._log_review_start()
        
        # Execute all analyzers
        self.logger.info("Running 7-phase analysis pipeline...")
        analyzer_results = self._run_analyzers()
        
        # Run validators
        self.logger.info("Running validators...")
        validator_results = self._run_validators()
        
        # Calculate overall scores
        self.logger.info("Calculating scores...")
        overall_score = self._calculate_overall_score(analyzer_results)
        
        # Check blocking conditions
        self.logger.info("Checking blocking conditions...")
        blocking_issues = self._check_blocking_conditions(
            analyzer_results,
            validator_results
        )
        
        # Generate recommendations
        self.logger.info("Generating recommendations...")
        recommendations = self._generate_recommendations(
            analyzer_results,
            validator_results,
            blocking_issues
        )
        
        # Generate report
        self.logger.info("Generating review report...")
        report = self._generate_report(
            analyzer_results,
            validator_results,
            overall_score,
            blocking_issues,
            recommendations,
            start_time
        )
        
        # Save report
        output_path = self._save_report(report)
        
        # Log review completion
        self._log_review_complete(review_id, overall_score, blocking_issues)
        
        elapsed_time = (datetime.now() - start_time).total_seconds()
        self.logger.info(
            f"Review complete in {elapsed_time:.2f}s: "
            f"Score={overall_score}, Blocking={len(blocking_issues)}"
        )
        
        return {
            "status": "complete" if not blocking_issues else "blocked",
            "review_id": review_id,
            "overall_score": overall_score,
            "blocking_issues": blocking_issues,
            "recommendations": recommendations,
            "report_path": str(output_path),
            "elapsed_time": elapsed_time,
            "analyzer_results": analyzer_results,
            "validator_results": validator_results
        }
    
    def _run_analyzers(self) -> Dict[str, Any]:
        """Run all analyzers and collect results."""
        results = {}
        
        for analyzer_name, analyzer in self.analyzers.items():
            self.logger.info(f"Running {analyzer_name} analyzer...")
            try:
                results[analyzer_name] = analyzer.analyze()
                score = results[analyzer_name].get("score", 0)
                issues = len(results[analyzer_name].get("issues", []))
                self.logger.info(
                    f"  {analyzer_name}: score={score}, issues={issues}"
                )
            except Exception as e:
                self.logger.error(f"Analyzer {analyzer_name} failed: {e}")
                results[analyzer_name] = {
                    "status": "error",
                    "error": str(e),
                    "score": 0,
                    "issues": []
                }
        
        return results
    
    def _run_validators(self) -> Dict[str, Any]:
        """Run all validators and collect results."""
        results = {}
        
        for validator_name, validator in self.validators.items():
            self.logger.info(f"Running {validator_name} validator...")
            try:
                results[validator_name] = validator.validate()
                status = results[validator_name].get("status", "unknown")
                self.logger.info(f"  {validator_name}: status={status}")
            except Exception as e:
                self.logger.error(f"Validator {validator_name} failed: {e}")
                results[validator_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results
    
    def _calculate_overall_score(self, results: Dict[str, Any]) -> float:
        """
        Calculate weighted overall score.
        
        Weights based on criticality to CORTEX design goals:
        - Architecture: 20% (most critical)
        - Fidelity: 15%
        - Governance: 15%
        - Structure: 15%
        - Edge Cases: 15%
        - Knowledge: 10%
        - Registry: 10%
        """
        weights = {
            "structure": 0.15,
            "architecture": 0.20,
            "knowledge": 0.10,
            "registry": 0.10,
            "edge_cases": 0.15,
            "fidelity": 0.15,
            "governance": 0.15
        }
        
        score = 0.0
        for name, weight in weights.items():
            analyzer_score = results.get(name, {}).get("score", 0)
            score += analyzer_score * weight
        
        return round(score, 2)
    
    def _check_blocking_conditions(
        self,
        analyzer_results: Dict[str, Any],
        validator_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Check if any blocking conditions exist.
        
        Blocking conditions from manifest:
        1. Overall score < 70
        2. Any BLOCKED severity violations in audit log
        3. Architecture coherence < 65
        4. Implementation fidelity < 60
        5. Governance compliance < 70
        6. Static analysis failures
        7. Test coverage below thresholds
        """
        blocking: List[Dict[str, Any]] = []
        
        # Check overall score
        overall_score = self._calculate_overall_score(analyzer_results)
        if overall_score < 70:
            blocking.append({
                "condition": "critical_overall_score",
                "severity": "critical",
                "message": f"Overall score ({overall_score}) below threshold (70)",
                "current_value": overall_score,
                "required_value": 70
            })
        
        # Check governance violations (BLOCKED severity)
        gov_violations = analyzer_results.get("governance", {}).get(
            "blocked_violations", []
        )
        if gov_violations:
            blocking.append({
                "condition": "blocked_violations",
                "severity": "critical",
                "message": f"Found {len(gov_violations)} BLOCKED violations",
                "violations": gov_violations
            })
        
        # Check architecture coherence
        arch_score = analyzer_results.get("architecture", {}).get("score", 0)
        if arch_score < 65:
            blocking.append({
                "condition": "architecture_coherence",
                "severity": "critical",
                "message": f"Architecture coherence ({arch_score}) below threshold (65)",
                "current_value": arch_score,
                "required_value": 65
            })
        
        # Check implementation fidelity
        fidelity_score = analyzer_results.get("fidelity", {}).get("score", 0)
        if fidelity_score < 60:
            blocking.append({
                "condition": "implementation_fidelity",
                "severity": "critical",
                "message": f"Implementation fidelity ({fidelity_score}) below threshold (60)",
                "current_value": fidelity_score,
                "required_value": 60
            })
        
        # Check governance compliance
        gov_score = analyzer_results.get("governance", {}).get("score", 0)
        if gov_score < 70:
            blocking.append({
                "condition": "governance_compliance",
                "severity": "critical",
                "message": f"Governance compliance ({gov_score}) below threshold (70)",
                "current_value": gov_score,
                "required_value": 70
            })
        
        # Check static analysis (if enabled)
        if "python" in validator_results:
            python_result = validator_results["python"]
            if python_result.get("status") == "failed":
                blocking.append({
                    "condition": "static_analysis_failures",
                    "severity": "warning",
                    "message": "Static analysis failures detected",
                    "details": python_result.get("failures", [])
                })
        
        # Check phase progression validator
        if "progression" in validator_results:
            progression_result = validator_results["progression"]
            if not progression_result.get("can_progress", False):
                blocking.extend(progression_result.get("blocking_reasons", []))
        
        return blocking
    
    def _generate_recommendations(
        self,
        analyzer_results: Dict[str, Any],
        validator_results: Dict[str, Any],
        blocking_issues: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on analysis results."""
        recommendations = []
        
        # Critical recommendations from blocking issues
        for issue in blocking_issues:
            if issue["severity"] == "critical":
                recommendations.append({
                    "priority": "critical",
                    "category": issue["condition"],
                    "recommendation": issue["message"],
                    "action": self._get_remediation_action(issue),
                    "estimated_effort": "high"
                })
        
        # Recommendations from each analyzer
        for analyzer_name, result in analyzer_results.items():
            analyzer_recommendations = result.get("recommendations", [])
            for rec in analyzer_recommendations:
                recommendations.append({
                    "priority": rec.get("priority", "medium"),
                    "category": analyzer_name,
                    "recommendation": rec.get("message", ""),
                    "action": rec.get("action", ""),
                    "estimated_effort": rec.get("effort", "medium")
                })
        
        # Sort by priority (critical > high > medium > low)
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        recommendations.sort(
            key=lambda x: priority_order.get(x["priority"], 99)
        )
        
        return recommendations
    
    def _get_remediation_action(self, issue: Dict[str, Any]) -> str:
        """Get specific remediation action for blocking issue."""
        condition = issue["condition"]
        
        remediation_map = {
            "critical_overall_score": "Address critical findings in all phases to improve overall score",
            "blocked_violations": "Resolve all BLOCKED severity violations in audit log",
            "architecture_coherence": "Refactor architecture to improve coherence and reduce coupling",
            "implementation_fidelity": "Implement missing features and align code with plan",
            "governance_compliance": "Enforce SKULL rules and best practices",
            "static_analysis_failures": "Fix all mypy, pylint, and pydocstyle errors"
        }
        
        return remediation_map.get(
            condition,
            f"Address {condition} violation"
        )
    
    def _generate_report(
        self,
        analyzer_results: Dict[str, Any],
        validator_results: Dict[str, Any],
        overall_score: float,
        blocking_issues: List[Dict[str, Any]],
        recommendations: List[Dict[str, Any]],
        start_time: datetime
    ) -> Dict[str, Any]:
        """Generate comprehensive review report."""
        elapsed_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "review_metadata": {
                "timestamp": datetime.now().isoformat(),
                "epic_path": str(self.epic_path),
                "review_type": self.review_type,
                "phase_id": self.phase_id,
                "orchestrator_version": "2.0.0",
                "elapsed_time_seconds": round(elapsed_time, 2)
            },
            "overall_assessment": {
                "score": overall_score,
                "status": "PASS" if overall_score >= 70 else "FAIL",
                "severity": self._calculate_severity(
                    overall_score,
                    blocking_issues
                ),
                "can_progress": len(blocking_issues) == 0
            },
            "blocking_issues": blocking_issues,
            "phase_scores": {
                name: result.get("score", 0)
                for name, result in analyzer_results.items()
            },
            "analyzer_results": analyzer_results,
            "validator_results": validator_results,
            "recommendations": recommendations,
            "summary": self._generate_summary(
                analyzer_results,
                overall_score,
                blocking_issues,
                recommendations
            )
        }
    
    def _calculate_severity(
        self,
        overall_score: float,
        blocking_issues: List[Dict[str, Any]]
    ) -> str:
        """Calculate severity level based on score and blocking issues."""
        if overall_score < 50:
            return "critical"
        elif overall_score < 70 or any(
            issue["severity"] == "critical" for issue in blocking_issues
        ):
            return "warning"
        elif overall_score < 85:
            return "acceptable"
        else:
            return "excellent"
    
    def _generate_summary(
        self,
        analyzer_results: Dict[str, Any],
        overall_score: float,
        blocking_issues: List[Dict[str, Any]],
        recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate executive summary."""
        total_issues = sum(
            len(result.get("issues", []))
            for result in analyzer_results.values()
        )
        
        critical_recs = [
            r for r in recommendations if r["priority"] == "critical"
        ]
        
        return {
            "overall_score": overall_score,
            "total_issues": total_issues,
            "blocking_issues": len(blocking_issues),
            "critical_recommendations": len(critical_recs),
            "phases_analyzed": len(analyzer_results),
            "validation_status": "BLOCKED" if blocking_issues else "CLEAR",
            "next_action": (
                "Address blocking issues before phase progression"
                if blocking_issues
                else "Continue with next phase"
            )
        }
    
    def _save_report(self, report: Dict[str, Any]) -> Path:
        """Save report to file based on output format."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = self.epic_path / "reports" / "cortex-review"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{timestamp}_{self.review_type}_review"
        
        # Use appropriate reporter
        reporter = self.reporters.get(self.output_format)
        if not reporter:
            self.logger.warning(
                f"Unknown output format: {self.output_format}, using YAML"
            )
            reporter = self.reporters["yaml"]
        
        output_path = reporter.save_report(report, filename)
        
        self.logger.info(f"Report saved to {output_path}")
        return output_path
    
    def _log_review_start(self) -> str:
        """Log review start to state DB and return review ID."""
        review_id = f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # TODO: Log to state DB
        # self.state_db.log_review_start(
        #     review_id=review_id,
        #     epic_path=str(self.epic_path),
        #     review_type=self.review_type,
        #     phase_id=self.phase_id
        # )
        
        return review_id
    
    def _log_review_complete(
        self,
        review_id: str,
        overall_score: float,
        blocking_issues: List[Dict[str, Any]]
    ) -> None:
        """Log review completion to state DB."""
        # TODO: Log to state DB
        # self.state_db.log_review_complete(
        #     review_id=review_id,
        #     overall_score=overall_score,
        #     blocking_issues=len(blocking_issues),
        #     status="blocked" if blocking_issues else "complete"
        # )
        pass
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
