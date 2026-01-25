"""
PlannerOrchestrator - Holistic YAML-Based Planning with LENS, Challenges, and Approval Flow

AC-PLANNER-001: Two-Phase Workflow (Temp → Active)
AC-PLANNER-002: Challenge System Integration  
AC-PLANNER-003: Git Analysis (Lightweight)
AC-PLANNER-004: Autonomous Execution Gates

Architecture:
- Singleton wrapper around InteractionOrchestrator + ChallengeEngine
- YAML-first workflow: temp → approval → active → execution
- Strategic challenges (4 types: governance, alternative, scope, risk)
- Lightweight git analysis (branch, status, recent commits)
- Hybrid execution gates (low/medium/high impact + confidence matrix)
- Autonomous execution with confirmation gates

Authority: AC-PLANNER-001 through AC-PLANNER-004
Author: GitHub Copilot (TDD Orchestrator)
Date: 2026-01-25
"""

from __future__ import annotations

import hashlib
import json
import logging
import subprocess
import threading
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import yaml

from cortex.core.interfaces import IOrchestrator
from cortex.core.result import Result, Ok, Err
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & TYPES
# ============================================================================


class PlanYamlState(Enum):
    """YAML plan state machine"""

    TEMP = "temp"  # Initial creation, pending approval
    PENDING_APPROVAL = "pending_approval"  # Awaiting user review
    ACTIVE = "active"  # Approved, ready for execution
    EXECUTING = "executing"  # Currently running
    EXECUTED = "executed"  # Completed successfully
    REJECTED = "rejected"  # Rejected by user
    FAILED = "failed"  # Execution failed
    ARCHIVED = "archived"  # Archived after completion


class PlanApprovalStatus(Enum):
    """Approval status tracking"""

    PENDING = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"  # User modified and resubmitted


class ChallengeType(Enum):
    """Types of strategic challenges"""

    GOVERNANCE = "governance"  # Violates CORE rules
    ALTERNATIVE_PATH = "alternative_path"  # Better solution exists
    SCOPE_CREEP = "scope_creep"  # Scope expanded unexpectedly
    RISK_MISMATCH = "risk_mismatch"  # High impact + low confidence


class ExecutionGateType(Enum):
    """Execution gate types based on impact/confidence"""

    AUTO_EXECUTE = "auto_execute"  # Execute immediately
    NOTIFY_AND_EXECUTE = "notify_and_execute"  # Execute, notify user
    CONFIRM_BEFORE_EXECUTE = "confirm_before_execute"  # Require confirmation
    NOTIFY_USER = "notify_user"  # Notify before, wait for permission
    BLOCKED = "blocked"  # Block execution, require design review


class GitContextType(Enum):
    """Git context information"""

    BRANCH = "branch"
    UNCOMMITTED_CHANGES = "uncommitted_changes"
    RECENT_COMMITS = "recent_commits"
    STATUS = "status"


# ============================================================================
# DATACLASSES
# ============================================================================


@dataclass
class Challenge:
    """Strategic challenge presented to user"""

    id: str = field(default_factory=lambda: str(uuid4())[:8])
    type: ChallengeType = ChallengeType.GOVERNANCE
    title: str = ""
    description: str = ""
    severity: str = "medium"  # low, medium, high
    recommendation: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization"""
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "recommendation": self.recommendation,
            "created_at": self.created_at,
        }


@dataclass
class ExecutionGate:
    """Execution gate constraints"""

    gate_type: ExecutionGateType = ExecutionGateType.AUTO_EXECUTE
    requires_confirmation: bool = False
    requires_design_review: bool = False
    confidence_threshold: float = 0.75
    impact_level: str = "low"  # low, medium, high
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization"""
        return {
            "gate_type": self.gate_type.value,
            "requires_confirmation": self.requires_confirmation,
            "requires_design_review": self.requires_design_review,
            "confidence_threshold": self.confidence_threshold,
            "impact_level": self.impact_level,
            "reason": self.reason,
        }


@dataclass
class GitContext:
    """Lightweight git analysis"""

    branch: str = ""
    uncommitted_changes: List[str] = field(default_factory=list)
    recent_commits: List[Dict[str, str]] = field(default_factory=list)
    status: str = ""  # clean, dirty, detached, etc.

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "branch": self.branch,
            "uncommitted_changes": self.uncommitted_changes,
            "recent_commits": self.recent_commits,
            "status": self.status,
        }


# ============================================================================
# PLANNER ORCHESTRATOR
# ============================================================================


class PlannerOrchestrator(IOrchestrator):
    """
    Holistic YAML-based planner with:
    - LENS-powered intent classification
    - Strategic challenge system
    - Two-phase approval workflow (temp → active)
    - Autonomous execution with hybrid gates
    - Lightweight git analysis

    AC-PLANNER-001 through 004
    """

    _instance: Optional[PlannerOrchestrator] = None
    _lock = threading.Lock()

    def __init__(self):
        """Initialize PlannerOrchestrator"""
        self.audit_logger = EnhancedAuditLogger.instance()
        self.logger = logging.getLogger(__name__)
        self.temp_plans_path: Optional[Path] = None
        self.active_plans_path: Optional[Path] = None
        self.executed_plans_path: Optional[Path] = None
        self.interaction_orchestrator: Optional[Any] = None
        self.git_context: Optional[GitContext] = None
        self._plan_cache: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def instance(cls) -> PlannerOrchestrator:
        """Get singleton instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = PlannerOrchestrator()
        return cls._instance

    def initialize(self) -> Result:  # type: ignore[type-arg]
        """Initialize PlannerOrchestrator and setup paths"""
        try:
            # Setup registry paths
            repo_root = Path(__file__).parent.parent.parent.parent.parent
            registry_path = repo_root / "cortex-registry" / "planning"

            self.temp_plans_path = registry_path / "temp"
            self.active_plans_path = registry_path / "active"
            self.executed_plans_path = registry_path / "executed"

            # Create directories
            for path in [self.temp_plans_path, self.active_plans_path, self.executed_plans_path]:
                path.mkdir(parents=True, exist_ok=True)

            # Load InteractionOrchestrator
            try:
                from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator

                self.interaction_orchestrator = InteractionOrchestrator
            except ImportError:
                self.logger.warning("InteractionOrchestrator not available, challenges disabled")

            # Initialize git context
            self._initialize_git_context()

            # Register with DatabaseBackedRegistry
            try:
                from cortex.orchestrators.core.database_registry import (
                    get_database_registry,
                    OrchestratorConfig,
                    OrchestratorCategory,
                )

                registry = get_database_registry()
                config = OrchestratorConfig(
                    name="PlannerOrchestrator",
                    module_path="cortex.orchestrators.core.planner_orchestrator",
                    class_name="PlannerOrchestrator",
                    category=OrchestratorCategory.CORE,
                    version="1.0.0",
                    dependencies=[],
                    capabilities=["planning", "yaml_workflow", "challenges"],
                    routing_keywords=["plan", "workflow", "yaml"],
                )
                registry.register(config, "PlannerOrchestrator.initialize()")
            except Exception as e:
                self.logger.warning(f"Failed to register with DatabaseBackedRegistry: {str(e)}")

            self.logger.info("PlannerOrchestrator initialized successfully")
            return Ok("PlannerOrchestrator initialized successfully")

        except Exception as e:
            error_msg = f"Initialization failed: {str(e)}"
            self.logger.error(error_msg)
            return Err(error_msg)

    def _initialize_git_context(self) -> None:
        """Initialize lightweight git analysis"""
        try:
            # Get current branch
            branch_output = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()

            # Get uncommitted changes
            status_output = subprocess.check_output(
                ["git", "status", "--porcelain"],
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()

            uncommitted = [line.strip() for line in status_output.split("\n") if line.strip()]

            # Get recent commits (last 5)
            log_output = subprocess.check_output(
                ["git", "log", "--oneline", "-5"],
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()

            recent_commits = []
            for line in log_output.split("\n"):
                if line.strip():
                    parts = line.split(" ", 1)
                    if len(parts) == 2:
                        recent_commits.append({"hash": parts[0], "message": parts[1]})

            # Get status
            status = "clean" if not uncommitted else "dirty"

            self.git_context = GitContext(
                branch=branch_output,
                uncommitted_changes=uncommitted,
                recent_commits=recent_commits,
                status=status,
            )

        except Exception as e:
            self.logger.warning(f"Git context initialization failed: {str(e)}")
            self.git_context = GitContext(branch="unknown", status="error")

    def create_temp_plan(self, user_request: Dict[str, Any]) -> Result:  # type: ignore[type-arg]
        """
        Create a TEMP YAML plan from user request.

        Flow:
        1. Validate request
        2. Run LENS classification
        3. Generate strategic challenges
        4. Compute execution gates
        5. Write TEMP YAML
        """
        try:
            # Validate request
            if not user_request or not isinstance(user_request, dict):
                return Err("Invalid user request: must be non-empty dictionary")

            if "description" not in user_request:
                return Err("User request must include 'description' field")

            # Generate plan ID
            plan_id = str(uuid4())[:12]

            # Build TEMP plan structure
            temp_plan: Dict[str, Any] = {
                "plan_id": plan_id,
                "status": PlanYamlState.TEMP.value,
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "created_by": "user",
                    "version": "1.0",
                },
                "request": user_request,
                "classification": self._classify_intent(user_request),
                "challenges": self._generate_challenges(user_request),
                "approval_status": {
                    "status": PlanApprovalStatus.PENDING.value,
                    "approved_at": None,
                    "approved_by": None,
                },
                "execution_gates": {
                    **(self._compute_execution_gates(user_request).to_dict() 
                       if self._compute_execution_gates(user_request) else {})
                },
                "git_context": self.git_context.to_dict() if self.git_context else {},
            }

            # Write to disk
            temp_file = self.temp_plans_path / f"{plan_id}.yaml"
            with open(temp_file, "w") as f:
                yaml.dump(temp_plan, f, default_flow_style=False, sort_keys=False)

            # Cache in memory
            self._plan_cache[plan_id] = temp_plan

            self.logger.info(f"Created TEMP plan: {plan_id}")
            return Ok(temp_plan)

        except Exception as e:
            error_msg = f"Failed to create temp plan: {str(e)}"
            self.logger.error(error_msg)
            return Err(error_msg)

    def _classify_intent(self, user_request: Dict[str, Any]) -> Dict[str, Any]:
        """Run LENS classification on user request"""
        try:
            description = user_request.get("description", "").lower()

            # LENS: Language → Examination → Navigation → Synthesis
            intent = "ANALYZE"  # Default
            confidence = 0.7

            # Detect intent keywords (Language phase)
            if any(
                keyword in description
                for keyword in [
                    "implement",
                    "create",
                    "build",
                    "add",
                    "new",
                ]
            ):
                intent = "IMPLEMENT"
                confidence = 0.85
            elif any(
                keyword in description
                for keyword in ["fix", "bug", "issue", "broken", "error"]
            ):
                intent = "FIX"
                confidence = 0.90
            elif any(
                keyword in description
                for keyword in ["refactor", "improve", "clean", "optimize"]
            ):
                intent = "REFACTOR"
                confidence = 0.85
            elif any(
                keyword in description
                for keyword in ["document", "doc", "explain", "describe"]
            ):
                intent = "DOCUMENT"
                confidence = 0.80
            elif any(
                keyword in description
                for keyword in ["test", "verify", "validate"]
            ):
                intent = "TEST"
                confidence = 0.85

            scope = user_request.get("scope", "file")
            impact = user_request.get("impact", "medium")

            return {
                "intent": intent,
                "confidence": confidence,
                "scope": scope,
                "impact": impact,
                "handler": self._get_handler_for_intent(intent),
            }

        except Exception as e:
            self.logger.warning(f"Intent classification failed: {str(e)}")
            return {
                "intent": "ANALYZE",
                "confidence": 0.5,
                "scope": "file",
                "impact": "unknown",
                "handler": "MasterOrchestrator",
            }

    def _get_handler_for_intent(self, intent: str) -> str:
        """Get orchestrator handler for intent"""
        mapping = {
            "IMPLEMENT": "TDDOrchestrator",
            "FIX": "IntentRouter",
            "REFACTOR": "RefactoringOrchestrator",
            "DOCUMENT": "DocumentationOrchestrator",
            "TEST": "TDDOrchestrator",
            "ANALYZE": "MasterOrchestrator",
        }
        return mapping.get(intent, "MasterOrchestrator")

    def _generate_challenges(self, user_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate strategic challenges based on request analysis"""
        challenges: List[Challenge] = []
        description = user_request.get("description", "").lower()

        # Challenge 1: Governance violations
        if "bare except" in description or "except:" in description:
            challenges.append(
                Challenge(
                    type=ChallengeType.GOVERNANCE,
                    title="CORE-013: Bare except clauses forbidden",
                    description="Your request mentions bare except clauses, which violate CORE-013",
                    severity="high",
                    recommendation="Use specific exception types instead",
                )
            )

        # Challenge 2: Alternative path suggestions
        description_lower = description.lower()
        intent_value = user_request.get("intent", "").lower()
        
        # Detect copy/paste or duplication patterns
        if any(keyword in description_lower for keyword in ["copy", "duplicate", "paste", "clone"]):
            challenges.append(
                Challenge(
                    type=ChallengeType.ALTERNATIVE_PATH,
                    title="Consider refactoring instead of copying",
                    description="Copying code violates CORE-035 (Single Canonical Implementation)",
                    severity="high",
                    recommendation="Extract to shared module or use composition",
                )
            )
        # Detect implementation requests that could be refactored
        elif intent_value == "implement" and any(kw in description_lower for kw in ["similar", "like", "same", "as before", "twice"]):
            challenges.append(
                Challenge(
                    type=ChallengeType.ALTERNATIVE_PATH,
                    title="Consider if this should be refactored into generic solution",
                    description="Similar requests suggest a more general pattern might be better",
                    severity="medium",
                    recommendation="Extract commonality into reusable component",
                )
            )

        # Challenge 3: Scope creep detection
        # Check for explicit scope creep patterns (multiple "AND" clauses)
        if " and " in description_lower and len(description_lower.split(" and ")) > 2:
            challenges.append(
                Challenge(
                    type=ChallengeType.SCOPE_CREEP,
                    title="Scope creep detected",
                    description=f"Request mentions multiple independent tasks (separated by 'AND')",
                    severity="medium",
                    recommendation="Break into smaller, focused requests",
                )
            )
        else:
            # Also check word count per scope
            word_count = len(description.split())
            scope = user_request.get("scope", "file").lower()
            
            # Calculate expected word count per scope
            scope_expectations = {
                "line": (5, 20),      # 5-20 words for single line changes
                "function": (20, 100), # 20-100 words for function changes
                "file": (50, 200),     # 50-200 words for file changes
                "module": (100, 400),  # 100-400 words for module changes
                "system": (200, 1000), # 200+ words for system changes
            }
            
            min_words, max_words = scope_expectations.get(scope, (50, 200))
            
            # Detect scope creep: word count exceeds what's typical for stated scope
            if word_count > max_words:
                challenges.append(
                    Challenge(
                        type=ChallengeType.SCOPE_CREEP,
                        title="Scope creep detected",
                        description=f"Request is {word_count} words but scope is '{scope}' (typical max: {max_words})",
                        severity="medium",
                        recommendation="Break into smaller, focused requests or increase stated scope",
                    )
                )

        # Challenge 4: Risk mismatch
        impact = user_request.get("impact", "medium")
        confidence_val = user_request.get("confidence", 0.75)
        
        # Convert confidence to float if it's a string
        if isinstance(confidence_val, str):
            confidence_map = {"low": 0.3, "medium": 0.7, "high": 0.9}
            confidence = confidence_map.get(confidence_val.lower(), 0.75)
        else:
            confidence = float(confidence_val)
        
        if impact == "high" and confidence < 0.7:
            challenges.append(
                Challenge(
                    type=ChallengeType.RISK_MISMATCH,
                    title="High impact with low confidence",
                    description="High-impact changes require higher confidence",
                    severity="high",
                    recommendation="Increase confidence through research/design",
                )
            )

        # Return as dictionaries for YAML
        return [c.to_dict() for c in challenges]

    def _compute_execution_gates(self, user_request: Dict[str, Any]) -> Optional[ExecutionGate]:
        """Compute execution gate based on impact/confidence matrix"""
        try:
            impact = user_request.get("impact", "medium")
            # Ensure confidence is a float
            confidence_val = user_request.get("confidence", None)
            
            # If confidence is not specified, infer it from impact
            if confidence_val is None:
                # Unspecified confidence: default to 0.9 for LOW/MEDIUM, 0.7 for HIGH
                if impact == "low":
                    confidence = 0.9
                elif impact == "medium":
                    confidence = 0.75
                else:  # HIGH
                    confidence = 0.7
            elif isinstance(confidence_val, str):
                try:
                    confidence = float(confidence_val)
                except ValueError:
                    confidence = 0.75
            else:
                confidence = float(confidence_val)
            
            # Normalize percentage values (0-100) to decimal (0-1)
            if confidence > 1.0:
                confidence = confidence / 100.0

            # Decision matrix
            if impact == "low":
                if confidence >= 0.85:
                    return ExecutionGate(
                        gate_type=ExecutionGateType.AUTO_EXECUTE,
                        requires_confirmation=False,
                        impact_level="low",
                        reason="Low impact + high confidence",
                    )
                elif confidence >= 0.70:
                    return ExecutionGate(
                        gate_type=ExecutionGateType.NOTIFY_AND_EXECUTE,
                        requires_confirmation=False,
                        impact_level="low",
                        reason="Low impact + medium confidence",
                    )
                else:
                    return ExecutionGate(
                        gate_type=ExecutionGateType.CONFIRM_BEFORE_EXECUTE,
                        requires_confirmation=True,
                        impact_level="low",
                        reason="Low impact + low confidence",
                    )

            elif impact == "medium":
                if confidence >= 0.90:
                    return ExecutionGate(
                        gate_type=ExecutionGateType.AUTO_EXECUTE,
                        requires_confirmation=False,
                        impact_level="medium",
                        reason="Medium impact + very high confidence",
                    )
                elif confidence >= 0.75:
                    return ExecutionGate(
                        gate_type=ExecutionGateType.CONFIRM_BEFORE_EXECUTE,
                        requires_confirmation=True,
                        impact_level="medium",
                        reason="Medium impact + medium confidence",
                    )
                else:
                    return ExecutionGate(
                        gate_type=ExecutionGateType.BLOCKED,
                        requires_confirmation=True,
                        requires_design_review=True,
                        impact_level="medium",
                        reason="Medium impact + low confidence",
                    )

            else:  # HIGH impact
                if confidence >= 0.95:
                    return ExecutionGate(
                        gate_type=ExecutionGateType.NOTIFY_USER,
                        requires_confirmation=False,
                        impact_level="high",
                        reason="High impact + very high confidence",
                    )
                elif confidence >= 0.80:
                    return ExecutionGate(
                        gate_type=ExecutionGateType.CONFIRM_BEFORE_EXECUTE,
                        requires_confirmation=True,
                        impact_level="high",
                        reason="High impact + high confidence",
                    )
                else:
                    return ExecutionGate(
                        gate_type=ExecutionGateType.BLOCKED,
                        requires_confirmation=True,
                        requires_design_review=True,
                        impact_level="high",
                        reason="High impact + low confidence",
                    )

        except Exception as e:
            self.logger.warning(f"Execution gate computation failed: {str(e)}")
            return None

    def approve_plan(self, plan_id: str) -> Result:  # type: ignore[type-arg]
        """Move TEMP plan to ACTIVE state after user approval"""
        try:
            # Get TEMP plan
            temp_plan = self.get_temp_plan(plan_id)
            if temp_plan.is_err():
                return Err(f"Plan not found: {plan_id}")

            plan = temp_plan.unwrap()

            # Transition state
            plan["status"] = PlanYamlState.ACTIVE.value
            plan["approval_status"]["status"] = PlanApprovalStatus.APPROVED.value
            plan["approval_status"]["approved_at"] = datetime.now().isoformat()

            # Write to active directory
            temp_file = self.temp_plans_path / f"{plan_id}.yaml"
            active_file = self.active_plans_path / f"{plan_id}.yaml"

            with open(active_file, "w") as f:
                yaml.dump(plan, f, default_flow_style=False, sort_keys=False)

            # Remove from temp
            if temp_file.exists():
                temp_file.unlink()

            # Update cache
            self._plan_cache[plan_id] = plan

            self.logger.info(f"Plan approved: {plan_id}")
            return Ok(plan)

        except Exception as e:
            error_msg = f"Approval failed: {str(e)}"
            self.logger.error(error_msg)
            return Err(error_msg)

    def reject_plan(self, plan_id: str, reason: str = "") -> Result:  # type: ignore[type-arg]
        """Reject TEMP plan"""
        try:
            temp_plan = self.get_temp_plan(plan_id)
            if temp_plan.is_err():
                return Err(f"Plan not found: {plan_id}")

            plan = temp_plan.unwrap()
            plan["status"] = PlanYamlState.REJECTED.value
            plan["approval_status"]["status"] = PlanApprovalStatus.REJECTED.value
            plan["rejection_reason"] = reason

            # Write to temp (mark as rejected)
            temp_file = self.temp_plans_path / f"{plan_id}.yaml"
            with open(temp_file, "w") as f:
                yaml.dump(plan, f, default_flow_style=False, sort_keys=False)

            self._plan_cache[plan_id] = plan

            self.logger.info(f"Plan rejected: {plan_id}")
            return Ok(plan)

        except Exception as e:
            error_msg = f"Rejection failed: {str(e)}"
            self.logger.error(error_msg)
            return Err(error_msg)

    def modify_temp_plan(
        self, plan_id: str, modifications: Dict[str, Any]
    ) -> Result:  # type: ignore[type-arg]
        """Modify TEMP plan before approval"""
        try:
            temp_plan = self.get_temp_plan(plan_id)
            if temp_plan.is_err():
                return Err(f"Plan not found: {plan_id}")

            plan = temp_plan.unwrap()

            # Only temp plans can be modified
            if plan["status"] != PlanYamlState.TEMP.value:
                return Err(f"Cannot modify plan in state: {plan['status']}")

            # Apply modifications to request
            plan["request"].update(modifications)

            # Recompute classification and challenges
            plan["classification"] = self._classify_intent(plan["request"])
            plan["challenges"] = self._generate_challenges(plan["request"])
            gate = self._compute_execution_gates(plan["request"])
            plan["execution_gates"] = gate.to_dict() if gate else {}
            plan["approval_status"]["status"] = PlanApprovalStatus.MODIFIED.value

            # Write to disk
            temp_file = self.temp_plans_path / f"{plan_id}.yaml"
            with open(temp_file, "w") as f:
                yaml.dump(plan, f, default_flow_style=False, sort_keys=False)

            self._plan_cache[plan_id] = plan

            self.logger.info(f"Plan modified: {plan_id}")
            return Ok(plan)

        except Exception as e:
            error_msg = f"Modification failed: {str(e)}"
            self.logger.error(error_msg)
            return Err(error_msg)

    def execute_plan(self, plan_id: str, confirmed: bool = False) -> Result:  # type: ignore[type-arg]
        """Execute an ACTIVE plan
        
        Args:
            plan_id: ID of the plan to execute
            confirmed: Whether confirmation has been provided for gates that require it.
                      Defaults to False (gates are enforced).
                      Set to True to bypass confirmation gates.
        """
        try:
            active_plan = self.get_active_plan(plan_id)
            if active_plan.is_err():
                return Err(f"Plan not found in active: {plan_id}")

            plan = active_plan.unwrap()

            # Check execution gate
            gate = ExecutionGate(**plan.get("execution_gates", {}))
            if gate.gate_type == ExecutionGateType.BLOCKED:
                return Err(f"Execution blocked: {gate.reason}")

            # If confirmation is required and not provided, ask for it
            if gate.requires_confirmation and not confirmed:
                return Ok({"awaiting_confirmation": True, "plan_id": plan_id})

            # Mark as executing
            plan["status"] = PlanYamlState.EXECUTING.value

            # Write update
            active_file = self.active_plans_path / f"{plan_id}.yaml"
            with open(active_file, "w") as f:
                yaml.dump(plan, f, default_flow_style=False, sort_keys=False)

            # TODO: Actually execute the plan via appropriate orchestrator
            # For now, just mark as executed

            plan["status"] = PlanYamlState.EXECUTED.value
            executed_file = self.executed_plans_path / f"{plan_id}.yaml"
            with open(executed_file, "w") as f:
                yaml.dump(plan, f, default_flow_style=False, sort_keys=False)

            # Remove from active
            if active_file.exists():
                active_file.unlink()

            self._plan_cache[plan_id] = plan
            self.logger.info(f"Plan executed: {plan_id}")
            return Ok(plan)

        except Exception as e:
            error_msg = f"Execution failed: {str(e)}"
            self.logger.error(error_msg)
            return Err(error_msg)

    def get_temp_plan(self, plan_id: str) -> Result:  # type: ignore[type-arg]
        """Get TEMP plan by ID"""
        try:
            # Check cache first
            if plan_id in self._plan_cache:
                return Ok(self._plan_cache[plan_id])

            # Load from disk
            temp_file = self.temp_plans_path / f"{plan_id}.yaml"
            if not temp_file.exists():
                return Err(f"TEMP plan not found: {plan_id}")

            with open(temp_file, "r") as f:
                plan = yaml.safe_load(f)

            self._plan_cache[plan_id] = plan
            return Ok(plan)

        except Exception as e:
            return Err(f"Failed to load TEMP plan: {str(e)}")

    def get_active_plan(self, plan_id: str) -> Result:  # type: ignore[type-arg]
        """Get ACTIVE plan by ID"""
        try:
            active_file = self.active_plans_path / f"{plan_id}.yaml"
            if not active_file.exists():
                return Err(f"ACTIVE plan not found: {plan_id}")

            with open(active_file, "r") as f:
                plan = yaml.safe_load(f)

            return Ok(plan)

        except Exception as e:
            return Err(f"Failed to load ACTIVE plan: {str(e)}")

    def get_plan_status(self, plan_id: str) -> Result:  # type: ignore[type-arg]
        """Get plan status (works for any state)"""
        try:
            # Try temp
            temp_result = self.get_temp_plan(plan_id)
            if temp_result.is_ok():
                return temp_result

            # Try active
            active_result = self.get_active_plan(plan_id)
            if active_result.is_ok():
                return active_result

            # Try executed
            executed_file = self.executed_plans_path / f"{plan_id}.yaml"
            if executed_file.exists():
                with open(executed_file, "r") as f:
                    plan = yaml.safe_load(f)
                return Ok(plan)

            return Err(f"Plan not found in any state: {plan_id}")

        except Exception as e:
            return Err(f"Failed to get plan status: {str(e)}")

    def list_temp_plans(self) -> Result:  # type: ignore[type-arg]
        """List all TEMP plans"""
        try:
            plans = []
            if self.temp_plans_path.exists():
                for plan_file in self.temp_plans_path.glob("*.yaml"):
                    try:
                        with open(plan_file, "r") as f:
                            plan = yaml.safe_load(f)
                        plans.append(plan)
                    except Exception as e:
                        self.logger.warning(f"Failed to load plan {plan_file.name}: {str(e)}")

            return Ok(plans)

        except Exception as e:
            return Err(f"Failed to list temp plans: {str(e)}")

    def list_active_plans(self) -> Result:  # type: ignore[type-arg]
        """List all ACTIVE plans"""
        try:
            plans = []
            if self.active_plans_path.exists():
                for plan_file in self.active_plans_path.glob("*.yaml"):
                    try:
                        with open(plan_file, "r") as f:
                            plan = yaml.safe_load(f)
                        plans.append(plan)
                    except Exception as e:
                        self.logger.warning(f"Failed to load plan {plan_file.name}: {str(e)}")

            return Ok(plans)

        except Exception as e:
            return Err(f"Failed to list active plans: {str(e)}")

    # ========================================================================
    # IOrchestrator Implementation
    # ========================================================================

    def get_name(self) -> str:
        """Get orchestrator name"""
        return "PlannerOrchestrator"

    def get_version(self) -> str:
        """Get orchestrator version"""
        return "1.0.0"

    def get_mode(self) -> str:
        """Get operating mode"""
        return "PLANNING"

    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status information"""
        return {
            "name": self.get_name(),
            "version": self.get_version(),
            "mode": self.get_mode(),
            "ready": self.temp_plans_path is not None,
            "state": "OPERATIONAL" if self.temp_plans_path else "INITIALIZING",
            "temp_plans_path": str(self.temp_plans_path) if self.temp_plans_path else None,
            "active_plans_path": str(self.active_plans_path) if self.active_plans_path else None,
        }

    def execute(self, *args: Any, **kwargs: Any) -> Result:  # type: ignore[type-arg]
        """Execute operation (delegates to appropriate handler)"""
        try:
            # Primary entry point for MasterOrchestrator
            if "plan_request" in kwargs:
                return self.create_temp_plan(kwargs["plan_request"])

            return Err("Invalid operation for PlannerOrchestrator")

        except Exception as e:
            return Err(f"Execution failed: {str(e)}")

    def execute_operation(self, operation: str, context: Optional[Dict[str, Any]] = None) -> Result:  # type: ignore[type-arg]
        """Execute operation - required by IOrchestrator"""
        try:
            if operation == "create_plan" and context:
                return self.create_temp_plan(context)
            elif operation == "approve_plan" and context and "plan_id" in context:
                return self.approve_plan(context["plan_id"])
            elif operation == "execute_plan" and context and "plan_id" in context:
                return self.execute_plan(context["plan_id"])
            
            return Err(f"Unknown operation: {operation}")
        except Exception as e:
            return Err(f"Operation {operation} failed: {str(e)}")

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Get audit trail - required by IOrchestrator"""
        try:
            return self.logger.get_audit_trail() if hasattr(self.logger, 'get_audit_trail') else []
        except Exception:
            return []

    def get_mcp_tools(self) -> Result:  # type: ignore[type-arg]
        """Get MCP tools - required by IOrchestrator"""
        try:
            tools = {
                "create_plan": {
                    "description": "Create a new TEMP plan from user request",
                    "parameters": {"user_request": "dict"},
                },
                "approve_plan": {
                    "description": "Approve and activate a TEMP plan",
                    "parameters": {"plan_id": "str"},
                },
                "reject_plan": {
                    "description": "Reject a TEMP plan",
                    "parameters": {"plan_id": "str", "reason": "str"},
                },
                "execute_plan": {
                    "description": "Execute an ACTIVE plan",
                    "parameters": {"plan_id": "str"},
                },
                "get_plan_status": {
                    "description": "Get plan status",
                    "parameters": {"plan_id": "str"},
                },
                "list_temp_plans": {
                    "description": "List all TEMP plans",
                    "parameters": {},
                },
                "list_active_plans": {
                    "description": "List all ACTIVE plans",
                    "parameters": {},
                },
            }
            return Ok(tools)
        except Exception as e:
            return Err(f"Failed to get MCP tools: {str(e)}")


# Module-level getter function for external access
def get_planner_orchestrator() -> PlannerOrchestrator:
    """Get singleton PlannerOrchestrator instance, initializing if needed.
    
    Returns:
        PlannerOrchestrator: Initialized singleton instance
    """
    planner = PlannerOrchestrator.instance()
    if not planner.temp_plans_path:
        # Initialize if not already done
        planner.initialize()
    return planner

