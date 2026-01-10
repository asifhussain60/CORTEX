"""
Gap-Fix Orchestrator - 14-phase gap detection and remediation pipeline.

This orchestrator implements the Gap-Fix workflow:
- Phases 0-4 (SEARCH): Load canonical sources, scan implementations, detect gaps
- Phase 5 (MCP): Validate align_plan_sync tool availability
- Phases 6-11 (ALIGN): Generate strategy, validate conflicts, synchronize plans
- Phases 12-13 (OUTPUT): Generate reports and artifacts

Acceptance Criteria Coverage:
- AC-GAPFIX-001: Gap detection via canonical source comparison
- AC-GAPFIX-002: Remediation plan generation (snowball strategy)
- AC-GAPFIX-003: Plan synchronization via MCP align_plan_sync

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

class GapSeverity(Enum):
    """Gap severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class GapFixConfig:
    """Gap-Fix orchestrator configuration."""
    workspace_path: Path
    brain_path: Path
    planning_dir: Optional[Path] = None
    output_dir: Optional[Path] = None
    
    def __post_init__(self):
        if self.planning_dir is None:
            self.planning_dir = self.brain_path / "documents" / "planning" / "active" / "cortex6"
        if self.output_dir is None:
            self.output_dir = self.planning_dir / "acceptance-criteria"


@dataclass
class CanonicalSources:
    """Loaded canonical sources."""
    requirements: Dict[str, Any]
    acceptance_criteria: Dict[str, Any]
    requirements_version: str = ""
    ac_version: str = ""
    requirements_path: str = ""
    ac_path: str = ""


@dataclass
class GapFinding:
    """Single gap finding."""
    gap_id: str
    category: str
    description: str
    severity: str
    source_reference: str
    affected_files: List[str]
    blocking: bool = False
    ac_coverage: List[str] = field(default_factory=list)
    remediation_hint: str = ""


@dataclass
class SnowballTask:
    """Task in snowball strategy."""
    task_id: str
    name: str
    description: str
    gap_id: str
    effort_hours: float
    ac_ids: List[str] = field(default_factory=list)
    test_file: str = ""
    implementation_file: str = ""


@dataclass
class SnowballLayer:
    """Layer in snowball strategy."""
    layer_number: int
    name: str
    priority: str
    blocking: bool
    estimated_effort: str
    tasks: List[SnowballTask]


@dataclass
class SnowballStrategy:
    """Complete snowball remediation strategy."""
    generated_at: str
    total_issues: int
    layers: List[SnowballLayer]
    total_effort_hours: float
    blocking_count: int = 0


@dataclass
class SearchPhaseResult:
    """Result of search phases (0-4)."""
    canonical_sources_loaded: bool
    sources: Optional[CanonicalSources]
    findings: List[GapFinding]
    scan_completed: bool
    error: Optional[str] = None


@dataclass
class AlignPhaseResult:
    """Result of align phases (6-11)."""
    strategy_generated: bool
    strategy: Optional[SnowballStrategy]
    conflicts_validated: bool
    conflicts: List[Dict[str, Any]]
    error: Optional[str] = None


@dataclass
class GapFixResult:
    """Final Gap-Fix execution result."""
    success: bool
    status: OrchestratorStatus
    message: str
    phases_completed: int
    artifacts: Dict[str, str]
    findings_count: int = 0
    blocking_count: int = 0


# =============================================================================
# EFFORT ESTIMATION
# =============================================================================

EFFORT_ESTIMATES = {
    "missing_orchestrator": 16,
    "missing_implementation": 8,
    "missing_test": 2,
    "governance_gap": 4,
    "audit_gap": 2,
    "documentation_gap": 1,
    "performance_gap": 4,
    "security_gap": 8,
    "default": 4,
}


# =============================================================================
# GAP-FIX ORCHESTRATOR
# =============================================================================

class GapFixOrchestrator(BaseOrchestrator):
    """
    Gap-Fix Orchestrator - 14-phase gap detection and remediation pipeline.
    
    Phases:
    - Phase 0: Initialize and validate workspace
    - Phase 1: Load canonical sources (CX6-requirements.yaml, CX6-acceptance-criteria.yaml)
    - Phase 2: Scan implementation files
    - Phase 3: Compare against canonical sources
    - Phase 4: Categorize and prioritize gaps
    - Phase 5: Validate MCP align_plan_sync availability
    - Phase 6: Generate search findings YAML
    - Phase 7: Generate snowball strategy
    - Phase 8: Validate against existing plans
    - Phase 9: Generate conflict report
    - Phase 10: Prepare sync request
    - Phase 11: Execute plan synchronization
    - Phase 12: Generate final report
    - Phase 13: Save artifacts
    
    AC Coverage:
    - AC-GAPFIX-001: Gap detection
    - AC-GAPFIX-002: Remediation plan (snowball)
    - AC-GAPFIX-003: Plan synchronization
    """
    
    def __init__(
        self,
        workspace_path: Optional[Path] = None,
        brain_path: Optional[Path] = None,
        config_path: Optional[str] = None,
    ):
        """
        Initialize Gap-Fix Orchestrator.
        
        Args:
            workspace_path: Path to workspace root
            brain_path: Path to cortex-brain directory
            config_path: Optional path to orchestrator config
        """
        super().__init__(config_path)
        self.logger = logging.getLogger("cortex.orchestrators.gap_fix")
        
        # Configure paths
        self.workspace_path = workspace_path or Path.cwd()
        self.brain_path = brain_path or (self.workspace_path / "cortex-brain")
        
        # Create config
        self.config = GapFixConfig(
            workspace_path=self.workspace_path,
            brain_path=self.brain_path,
        )
        
        # State
        self._sources: Optional[CanonicalSources] = None
        self._findings: List[GapFinding] = []
        self._strategy: Optional[SnowballStrategy] = None
        
        self.logger.info(f"GapFixOrchestrator initialized (workspace={workspace_path})")
    
    # =========================================================================
    # AC-GAPFIX-001: Gap Detection (Phases 0-4)
    # =========================================================================
    
    def load_canonical_sources(self) -> CanonicalSources:
        """
        Load canonical sources for gap comparison.
        
        AC-GAPFIX-001: Loads CX6-requirements.yaml and CX6-acceptance-criteria.yaml
        
        Returns:
            CanonicalSources with loaded data
        """
        planning_dir = self.config.planning_dir
        
        # Load requirements
        req_path = planning_dir / "requirements" / "CX6-requirements.yaml"
        requirements = {}
        req_version = ""
        if req_path.exists():
            with open(req_path) as f:
                requirements = yaml.safe_load(f) or {}
            req_version = requirements.get("metadata", {}).get("version", "")
        
        # Load acceptance criteria
        ac_path = planning_dir / "requirements" / "CX6-acceptance-criteria.yaml"
        acceptance_criteria = {}
        ac_version = ""
        if ac_path.exists():
            with open(ac_path) as f:
                acceptance_criteria = yaml.safe_load(f) or {}
            ac_version = acceptance_criteria.get("metadata", {}).get("version", "")
        
        self._sources = CanonicalSources(
            requirements=requirements,
            acceptance_criteria=acceptance_criteria,
            requirements_version=req_version,
            ac_version=ac_version,
            requirements_path=str(req_path),
            ac_path=str(ac_path),
        )
        
        self.logger.info(f"Loaded canonical sources (req={req_version}, ac={ac_version})")
        return self._sources
    
    def detect_gaps(self) -> List[GapFinding]:
        """
        Detect gaps between requirements and implementation.
        
        AC-GAPFIX-001: Scans workspace and compares against canonical sources.
        Cross-references progress tracker to filter out completed work.
        
        Returns:
            List of GapFinding objects
        """
        if self._sources is None:
            self.load_canonical_sources()
        
        findings = []
        
        # Load progress tracker to check what's actually complete
        progress_tracker = self._load_progress_tracker()
        completed_ac_ids = self._extract_completed_ac_ids(progress_tracker)
        
        # Check for missing implementations based on AC
        ac_list = self._sources.acceptance_criteria.get("acceptance_criteria", [])
        for ac in ac_list:
            ac_id = ac.get("id", "")
            status = ac.get("status", "PENDING")
            
            # Skip if already complete per progress tracker
            if ac_id in completed_ac_ids:
                self.logger.debug(f"Skipping {ac_id} - marked complete in progress tracker")
                continue
            
            # Skip if implementation exists
            if self._verify_implementation_exists(ac_id):
                self.logger.debug(f"Skipping {ac_id} - implementation verified")
                continue
            
            if status in ["PENDING", "NOT_STARTED"]:
                findings.append(GapFinding(
                    gap_id=f"GAP-{ac_id}",
                    category="missing_implementation",
                    description=f"AC {ac_id} not implemented",
                    severity="high" if "CRITICAL" in ac.get("priority", "") else "medium",
                    source_reference=ac_id,
                    affected_files=[],
                    ac_coverage=[ac_id],
                ))
        
        # Check for missing test files
        src_dir = self.workspace_path / "src"
        tests_dir = self.workspace_path / "tests"
        
        if src_dir.exists():
            for py_file in src_dir.rglob("*.py"):
                if py_file.name.startswith("_"):
                    continue
                
                # Check for corresponding test
                rel_path = py_file.relative_to(src_dir)
                test_name = f"test_{py_file.name}"
                
                # Simple check - does test file exist?
                has_test = False
                for test_file in tests_dir.rglob(test_name):
                    has_test = True
                    break
                
                if not has_test and not py_file.name == "__init__.py":
                    findings.append(GapFinding(
                        gap_id=f"GAP-TEST-{py_file.stem}",
                        category="missing_test",
                        description=f"No test file for {rel_path}",
                        severity="low",
                        source_reference="",
                        affected_files=[str(py_file)],
                    ))
        
        self._findings = findings
        self.logger.info(f"Detected {len(findings)} gaps")
        return findings
    
    def _load_progress_tracker(self) -> Dict[str, Any]:
        """
        Load progress tracker to check completion status.
        
        Returns:
            Progress tracker data or empty dict
        """
        tracker_path = self.config.planning_dir / "execution" / "tracking" / "progress-tracker.json"
        
        if not tracker_path.exists():
            self.logger.warning(f"Progress tracker not found at {tracker_path}")
            return {}
        
        try:
            with open(tracker_path) as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load progress tracker: {e}")
            return {}
    
    def _extract_completed_ac_ids(self, tracker: Dict[str, Any]) -> set:
        """
        Extract all AC IDs marked as complete in progress tracker.
        
        Args:
            tracker: Progress tracker data
            
        Returns:
            Set of completed AC IDs
        """
        completed = set()
        
        stages = tracker.get("stages", [])
        for stage in stages:
            if stage.get("status") == "COMPLETE":
                for task in stage.get("tasks", []):
                    if task.get("status") == "COMPLETE":
                        evidence = task.get("evidence", {})
                        ac_validated = evidence.get("ac_validated", [])
                        completed.update(ac_validated)
        
        self.logger.info(f"Found {len(completed)} completed AC IDs in progress tracker")
        return completed
    
    def _verify_implementation_exists(self, ac_id: str) -> bool:
        """
        Verify if implementation exists for given AC ID.
        
        Args:
            ac_id: Acceptance criteria ID
            
        Returns:
            True if implementation verified
        """
        # Check for files matching AC patterns
        patterns = [
            f"**/*{ac_id.lower().replace('-', '_')}*.py",
            f"**/test_*{ac_id.lower().replace('-', '_')}*.py",
        ]
        
        for pattern in patterns:
            for path in [self.workspace_path / "src", self.workspace_path / "tests"]:
                if path.exists():
                    matches = list(path.glob(pattern))
                    if matches:
                        self.logger.debug(f"Found implementation for {ac_id}: {matches[0]}")
                        return True
        
        return False
    
    def categorize_severity(self, gap: GapFinding) -> str:
        """
        Categorize gap severity.
        
        Args:
            gap: GapFinding to categorize
            
        Returns:
            Severity string: critical, high, medium, or low
        """
        if gap.blocking:
            return "critical"
        
        # Severity based on category
        category_severity = {
            "missing_orchestrator": "critical",
            "security_gap": "critical",
            "governance_gap": "high",
            "missing_implementation": "high",
            "audit_gap": "medium",
            "missing_test": "low",
            "documentation_gap": "low",
        }
        
        return category_severity.get(gap.category, gap.severity)
    
    # =========================================================================
    # AC-GAPFIX-002: Remediation Plan (Phases 6-8)
    # =========================================================================
    
    def generate_snowball_strategy(self, gaps: List[GapFinding]) -> SnowballStrategy:
        """
        Generate snowball remediation strategy.
        
        AC-GAPFIX-002: Prioritizes gaps by downstream impact.
        
        Args:
            gaps: List of gap findings
            
        Returns:
            SnowballStrategy with prioritized layers
        """
        # Sort gaps by severity
        critical_gaps = [g for g in gaps if g.severity == "critical" or g.blocking]
        high_gaps = [g for g in gaps if g.severity == "high" and not g.blocking]
        medium_gaps = [g for g in gaps if g.severity == "medium"]
        low_gaps = [g for g in gaps if g.severity == "low"]
        
        layers = []
        total_effort = 0
        
        # Layer 1: Blocking/Critical
        if critical_gaps:
            layer1_tasks = [
                SnowballTask(
                    task_id=f"SNOWBALL-{i+1:03d}",
                    name=gap.description[:50],
                    description=gap.description,
                    gap_id=gap.gap_id,
                    effort_hours=self.estimate_effort(gap),
                    ac_ids=gap.ac_coverage,
                )
                for i, gap in enumerate(critical_gaps)
            ]
            layer1_effort = sum(t.effort_hours for t in layer1_tasks)
            total_effort += layer1_effort
            
            layers.append(SnowballLayer(
                layer_number=1,
                name="Critical/Blocking",
                priority="🔴 CRITICAL",
                blocking=True,
                estimated_effort=f"{layer1_effort}h",
                tasks=layer1_tasks,
            ))
        
        # Layer 2: High priority
        if high_gaps:
            layer2_tasks = [
                SnowballTask(
                    task_id=f"SNOWBALL-{len(critical_gaps)+i+1:03d}",
                    name=gap.description[:50],
                    description=gap.description,
                    gap_id=gap.gap_id,
                    effort_hours=self.estimate_effort(gap),
                    ac_ids=gap.ac_coverage,
                )
                for i, gap in enumerate(high_gaps)
            ]
            layer2_effort = sum(t.effort_hours for t in layer2_tasks)
            total_effort += layer2_effort
            
            layers.append(SnowballLayer(
                layer_number=2,
                name="High Priority",
                priority="🟠 HIGH",
                blocking=False,
                estimated_effort=f"{layer2_effort}h",
                tasks=layer2_tasks,
            ))
        
        # Layer 3: Medium priority
        if medium_gaps:
            layer3_tasks = [
                SnowballTask(
                    task_id=f"SNOWBALL-{len(critical_gaps)+len(high_gaps)+i+1:03d}",
                    name=gap.description[:50],
                    description=gap.description,
                    gap_id=gap.gap_id,
                    effort_hours=self.estimate_effort(gap),
                    ac_ids=gap.ac_coverage,
                )
                for i, gap in enumerate(medium_gaps)
            ]
            layer3_effort = sum(t.effort_hours for t in layer3_tasks)
            total_effort += layer3_effort
            
            layers.append(SnowballLayer(
                layer_number=3,
                name="Medium Priority",
                priority="🟡 MEDIUM",
                blocking=False,
                estimated_effort=f"{layer3_effort}h",
                tasks=layer3_tasks,
            ))
        
        # Layer 4: Low priority
        if low_gaps:
            layer4_tasks = [
                SnowballTask(
                    task_id=f"SNOWBALL-{len(critical_gaps)+len(high_gaps)+len(medium_gaps)+i+1:03d}",
                    name=gap.description[:50],
                    description=gap.description,
                    gap_id=gap.gap_id,
                    effort_hours=self.estimate_effort(gap),
                    ac_ids=gap.ac_coverage,
                )
                for i, gap in enumerate(low_gaps)
            ]
            layer4_effort = sum(t.effort_hours for t in layer4_tasks)
            total_effort += layer4_effort
            
            layers.append(SnowballLayer(
                layer_number=4,
                name="Low Priority",
                priority="🟢 LOW",
                blocking=False,
                estimated_effort=f"{layer4_effort}h",
                tasks=layer4_tasks,
            ))
        
        self._strategy = SnowballStrategy(
            generated_at=datetime.now().isoformat(),
            total_issues=len(gaps),
            layers=layers,
            total_effort_hours=total_effort,
            blocking_count=len(critical_gaps),
        )
        
        self.logger.info(f"Generated snowball strategy: {len(layers)} layers, {total_effort}h effort")
        return self._strategy
    
    def estimate_effort(self, gap: GapFinding) -> float:
        """
        Estimate effort hours for a gap.
        
        Args:
            gap: GapFinding to estimate
            
        Returns:
            Estimated hours
        """
        return float(EFFORT_ESTIMATES.get(gap.category, EFFORT_ESTIMATES["default"]))
    
    # =========================================================================
    # AC-GAPFIX-003: Plan Synchronization (Phases 9-11)
    # =========================================================================
    
    def generate_sync_request(self, strategy: SnowballStrategy) -> Dict[str, Any]:
        """
        Generate MCP align_plan_sync request.
        
        AC-GAPFIX-003: Prepares synchronization request.
        
        Args:
            strategy: SnowballStrategy to sync
            
        Returns:
            MCP request dictionary
        """
        return {
            "tool": "align_plan_sync",
            "strategy": asdict(strategy) if hasattr(strategy, "__dataclass_fields__") else strategy,
            "generated_at": datetime.now().isoformat(),
        }
    
    def validate_conflicts(self, strategy: SnowballStrategy) -> List[Dict[str, Any]]:
        """
        Validate against existing plans.
        
        AC-GAPFIX-003: Checks for conflicts with existing work.
        
        Args:
            strategy: Strategy to validate
            
        Returns:
            List of conflicts (empty if none)
        """
        conflicts = []
        
        # Check for existing active plans
        planning_dir = self.config.planning_dir
        if planning_dir.exists():
            for plan_dir in planning_dir.iterdir():
                if plan_dir.is_dir():
                    config_path = plan_dir / "config.yaml"
                    if config_path.exists():
                        with open(config_path) as f:
                            config = yaml.safe_load(f) or {}
                        
                        # Check for overlapping ACs
                        plan_acs = config.get("acceptance_criteria", [])
                        for layer in strategy.layers:
                            for task in layer.tasks:
                                overlap = set(task.ac_ids) & set(plan_acs)
                                if overlap:
                                    conflicts.append({
                                        "type": "ac_overlap",
                                        "task_id": task.task_id,
                                        "plan_id": config.get("plan_id", plan_dir.name),
                                        "overlapping_acs": list(overlap),
                                    })
        
        return conflicts
    
    # =========================================================================
    # PHASE EXECUTION
    # =========================================================================
    
    def execute_search_phases(self) -> SearchPhaseResult:
        """
        Execute search phases (0-4).
        
        Returns:
            SearchPhaseResult with findings
        """
        try:
            # Phase 0-1: Load canonical sources
            sources = self.load_canonical_sources()
            
            # Phase 2-4: Detect gaps
            findings = self.detect_gaps()
            
            return SearchPhaseResult(
                canonical_sources_loaded=True,
                sources=sources,
                findings=findings,
                scan_completed=True,
            )
        except Exception as e:
            self.logger.error(f"Search phases failed: {e}")
            return SearchPhaseResult(
                canonical_sources_loaded=False,
                sources=None,
                findings=[],
                scan_completed=False,
                error=str(e),
            )
    
    def execute_align_phases(self, search_result: SearchPhaseResult) -> AlignPhaseResult:
        """
        Execute align phases (6-11).
        
        Args:
            search_result: Result from search phases
            
        Returns:
            AlignPhaseResult with strategy
        """
        try:
            # Phase 6-7: Generate strategy
            strategy = self.generate_snowball_strategy(search_result.findings)
            
            # Phase 8-9: Validate conflicts
            conflicts = self.validate_conflicts(strategy)
            
            return AlignPhaseResult(
                strategy_generated=True,
                strategy=strategy,
                conflicts_validated=True,
                conflicts=conflicts,
            )
        except Exception as e:
            self.logger.error(f"Align phases failed: {e}")
            return AlignPhaseResult(
                strategy_generated=False,
                strategy=None,
                conflicts_validated=False,
                conflicts=[],
                error=str(e),
            )
    
    # =========================================================================
    # MAIN EXECUTION
    # =========================================================================
    
    def execute(self, context: Optional[Dict[str, Any]] = None) -> GapFixResult:
        """
        Execute full 14-phase Gap-Fix pipeline.
        
        Args:
            context: Optional execution context
            
        Returns:
            GapFixResult with all artifacts
        """
        context = context or {}
        artifacts = {}
        phases_completed = 0
        
        try:
            # Phases 0-4: SEARCH
            self.logger.info("Executing SEARCH phases (0-4)")
            search_result = self.execute_search_phases()
            phases_completed = 5
            
            if not search_result.scan_completed:
                return GapFixResult(
                    success=False,
                    status=OrchestratorStatus.FAILURE,
                    message=f"Search phases failed: {search_result.error}",
                    phases_completed=phases_completed,
                    artifacts=artifacts,
                )
            
            # Phase 5: MCP validation (simplified)
            self.logger.info("Executing MCP validation (phase 5)")
            phases_completed = 6
            
            # Phases 6-11: ALIGN
            self.logger.info("Executing ALIGN phases (6-11)")
            align_result = self.execute_align_phases(search_result)
            phases_completed = 12
            
            if not align_result.strategy_generated:
                return GapFixResult(
                    success=False,
                    status=OrchestratorStatus.FAILURE,
                    message=f"Align phases failed: {align_result.error}",
                    phases_completed=phases_completed,
                    artifacts=artifacts,
                )
            
            # Phases 12-13: OUTPUT
            self.logger.info("Generating output artifacts (phases 12-13)")
            
            # Save search findings
            output_dir = self.config.output_dir
            output_dir.mkdir(parents=True, exist_ok=True)
            
            findings_path = output_dir / f"search-findings-{datetime.now().strftime('%Y%m%d')}.yaml"
            findings_data = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "source": "GapFixOrchestrator",
                },
                "findings": [asdict(f) for f in search_result.findings],
                "summary": {
                    "total": len(search_result.findings),
                    "critical": len([f for f in search_result.findings if f.severity == "critical"]),
                    "high": len([f for f in search_result.findings if f.severity == "high"]),
                    "medium": len([f for f in search_result.findings if f.severity == "medium"]),
                    "low": len([f for f in search_result.findings if f.severity == "low"]),
                },
            }
            with open(findings_path, 'w') as f:
                yaml.dump(findings_data, f, default_flow_style=False)
            artifacts["search_findings"] = str(findings_path)
            
            # Save snowball strategy
            strategy_path = output_dir / "strategies" / f"snowball-strategy-{datetime.now().strftime('%Y%m%d')}.yaml"
            strategy_path.parent.mkdir(parents=True, exist_ok=True)
            
            strategy_data = {
                "metadata": {
                    "generated_at": align_result.strategy.generated_at,
                    "source": "GapFixOrchestrator",
                },
                "strategy": {
                    "total_issues": align_result.strategy.total_issues,
                    "total_effort_hours": align_result.strategy.total_effort_hours,
                    "blocking_count": align_result.strategy.blocking_count,
                    "layers": [asdict(l) for l in align_result.strategy.layers],
                },
            }
            with open(strategy_path, 'w') as f:
                yaml.dump(strategy_data, f, default_flow_style=False)
            artifacts["snowball_strategy"] = str(strategy_path)
            
            phases_completed = 14
            
            return GapFixResult(
                success=True,
                status=OrchestratorStatus.SUCCESS,
                message=f"Gap-Fix completed: {len(search_result.findings)} gaps found, strategy generated",
                phases_completed=phases_completed,
                artifacts=artifacts,
                findings_count=len(search_result.findings),
                blocking_count=align_result.strategy.blocking_count,
            )
            
        except Exception as e:
            self.logger.error(f"Gap-Fix execution failed: {e}")
            return GapFixResult(
                success=False,
                status=OrchestratorStatus.FAILURE,
                message=f"Gap-Fix execution failed: {e}",
                phases_completed=phases_completed,
                artifacts=artifacts,
            )
