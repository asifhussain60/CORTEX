"""
Plan Pause Manager - Pause/Resume State Management with LENS-Driven Replanning

Handles pause/resume operations:
- Checkpoint creation (phase artifacts, test results, code state)
- User-correction detection and integration
- LENS re-analysis of user corrections
- Adaptive replanning when user modifies plan mid-execution

AC-PAUSE-MANAGER-001: Pause State Management
AC-PAUSE-MANAGER-002: Checkpoint Creation & Restoration
AC-PAUSE-MANAGER-003: LENS-Driven Adaptive Replanning

Author: GitHub Copilot (CORTEX Plan Pause Manager)
Date: 2026-01-26
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.core.result import Result, Ok, Err

logger = logging.getLogger(__name__)


@dataclass
class PauseCheckpoint:
    """Checkpoint at pause point"""

    pause_id: str
    plan_id: str
    phase_num: int
    phase_name: str
    pause_time: str
    pause_reason: str
    code_checkpoint_sha: Optional[str] = None
    test_results: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    execution_state: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class UserCorrection:
    """User correction during pause"""

    correction_type: str  # code_fix, plan_update, phase_skip, etc.
    original_content: str
    corrected_content: str
    explanation: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class LENSAnalysisResult:
    """LENS analysis of user correction"""

    correction_category: str  # MINIMAL, MODERATE, SIGNIFICANT
    affected_phases: List[int] = field(default_factory=list)
    impact_summary: str = ""
    requires_replanning: bool = False
    new_dependencies: List[int] = field(default_factory=list)
    suggested_actions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class ResumeContext:
    """Context for resuming execution"""

    checkpoint: PauseCheckpoint
    user_correction: Optional[UserCorrection] = None
    lens_analysis: Optional[LENSAnalysisResult] = None
    updated_plan: Optional[Dict[str, Any]] = None
    resume_phase: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "checkpoint": self.checkpoint.to_dict(),
            "user_correction": self.user_correction.to_dict() if self.user_correction else None,
            "lens_analysis": self.lens_analysis.to_dict() if self.lens_analysis else None,
            "updated_plan": self.updated_plan,
            "resume_phase": self.resume_phase,
        }


class PlanPauseManager:
    """
    Manages pause/resume with checkpoint and LENS-driven replanning.

    AC-PAUSE-MANAGER-001 through 003
    """

    def __init__(self, checkpoint_path: Optional[Path] = None):
        """
        Initialize pause manager.

        Args:
            checkpoint_path: Path to store pause checkpoints (.cortex/pause_checkpoints/)
        """
        if checkpoint_path is None:
            checkpoint_path = Path.home() / ".cortex" / "pause_checkpoints"

        self.checkpoint_path = checkpoint_path
        self.logger = logging.getLogger(__name__)
        self._current_checkpoint: Optional[PauseCheckpoint] = None

    async def pause(
        self,
        phase_num: int,
        phase_name: str,
        plan_id: str,
        reason: str,
        artifacts: List[str] = None,
        execution_state: Dict[str, Any] = None,
        code_checkpoint_sha: Optional[str] = None,
    ) -> Result:
        """
        Create pause checkpoint.

        AC-PAUSE-MANAGER-001: Pause State Management

        Args:
            phase_num: Phase number
            phase_name: Phase name
            plan_id: Plan ID
            reason: Reason for pause
            artifacts: List of artifact paths
            execution_state: Current execution state
            code_checkpoint_sha: Git SHA of code checkpoint

        Returns:
            Result with pause checkpoint
        """
        try:
            from uuid import uuid4

            pause_id = str(uuid4())[:8]

            checkpoint = PauseCheckpoint(
                pause_id=pause_id,
                plan_id=plan_id,
                phase_num=phase_num,
                phase_name=phase_name,
                pause_time=datetime.now().isoformat(),
                pause_reason=reason,
                code_checkpoint_sha=code_checkpoint_sha,
                artifacts=artifacts or [],
                execution_state=execution_state or {},
            )

            self._current_checkpoint = checkpoint

            # Save checkpoint
            await self._save_checkpoint(checkpoint)

            self.logger.info(f"Pause checkpoint created: {pause_id}")
            return Ok(checkpoint.to_dict())

        except Exception as e:
            self.logger.exception(f"Pause error: {e}")
            return Err(str(e))

    async def resume(
        self,
        checkpoint_id: str,
        user_correction: Optional[UserCorrection] = None,
    ) -> Result:
        """
        Resume execution from pause.

        AC-PAUSE-MANAGER-002: Checkpoint Creation & Restoration

        Args:
            checkpoint_id: ID of pause checkpoint
            user_correction: Optional user correction

        Returns:
            Result with resume context
        """
        try:
            # Load checkpoint
            checkpoint_result = await self._load_checkpoint(checkpoint_id)
            if checkpoint_result.is_err():
                return checkpoint_result

            checkpoint = checkpoint_result.unwrap()

            # Analyze user correction if provided
            lens_analysis = None
            if user_correction:
                lens_result = await self.analyze_user_corrections(
                    checkpoint,
                    user_correction,
                )

                if lens_result.is_ok():
                    lens_analysis = lens_result.unwrap()

            # Determine resume phase
            resume_phase = checkpoint.phase_num
            if lens_analysis and lens_analysis.requires_replanning:
                # Start from affected phase if replanning needed
                if lens_analysis.affected_phases:
                    resume_phase = min(lens_analysis.affected_phases)

            resume_context = ResumeContext(
                checkpoint=checkpoint,
                user_correction=user_correction,
                lens_analysis=lens_analysis,
                resume_phase=resume_phase,
            )

            self.logger.info(f"Resume context created from checkpoint {checkpoint_id}")
            return Ok(resume_context.to_dict())

        except Exception as e:
            self.logger.exception(f"Resume error: {e}")
            return Err(str(e))

    async def analyze_user_corrections(
        self,
        checkpoint: PauseCheckpoint,
        user_correction: UserCorrection,
    ) -> Result:
        """
        Analyze user correction using LENS protocol.

        AC-PAUSE-MANAGER-003: LENS-Driven Adaptive Replanning

        Args:
            checkpoint: Pause checkpoint
            user_correction: User correction

        Returns:
            Result with LENS analysis
        """
        try:
            # LENS Analysis: Language → Examination → Navigation → Synthesis
            # Language: Parse correction type
            correction_type = user_correction.correction_type

            # Examination: Determine scope
            if correction_type == "code_fix":
                # Minimal change - small scope
                category = "MINIMAL"
                affected_phases = [checkpoint.phase_num]
                impact_text = f"Code fix in phase {checkpoint.phase_num} ({user_correction.explanation})"

            elif correction_type == "plan_update":
                # Moderate change - affects dependent phases
                category = "MODERATE"
                affected_phases = list(range(checkpoint.phase_num, checkpoint.phase_num + 2))
                impact_text = f"Plan update affects phases {affected_phases}"

            elif correction_type == "phase_skip":
                # Significant change - skip remaining phases
                category = "SIGNIFICANT"
                affected_phases = []
                impact_text = "Phase skipped - remaining phases unaffected"

            else:
                category = "MODERATE"
                affected_phases = [checkpoint.phase_num]
                impact_text = user_correction.explanation

            # Navigation: Determine replanning needs
            requires_replanning = category in ["MODERATE", "SIGNIFICANT"]

            # Synthesis: Create analysis result
            analysis = LENSAnalysisResult(
                correction_category=category,
                affected_phases=affected_phases,
                impact_summary=impact_text,
                requires_replanning=requires_replanning,
                suggested_actions=self._suggest_actions(category, checkpoint.phase_num),
            )

            self.logger.info(
                f"LENS analysis: {category} impact, replanning={requires_replanning}"
            )
            return Ok(analysis)

        except Exception as e:
            self.logger.exception(f"LENS analysis error: {e}")
            return Err(str(e))

    async def replan_affected_phases(
        self,
        original_plan: Dict[str, Any],
        updated_plan: Dict[str, Any],
        from_phase: int,
    ) -> Result:
        """
        Replan affected phases after user correction.

        AC-PAUSE-MANAGER-003: LENS-Driven Adaptive Replanning

        Args:
            original_plan: Original plan before correction
            updated_plan: Updated plan after correction
            from_phase: Starting phase for replan

        Returns:
            Result with updated plan
        """
        try:
            # Compare plans to find differences
            differences = self._compare_plans(original_plan, updated_plan)

            # Update affected phases
            if "phases" in updated_plan:
                for phase in updated_plan["phases"]:
                    if phase.get("phase_num", 0) >= from_phase:
                        # Mark phase as requiring re-execution
                        phase["status"] = "replanned"
                        phase["replanned_at"] = datetime.now().isoformat()

            self.logger.info(f"Replanning phases from {from_phase}: {len(differences)} changes")
            return Ok(updated_plan)

        except Exception as e:
            self.logger.exception(f"Replan error: {e}")
            return Err(str(e))

    async def _save_checkpoint(self, checkpoint: PauseCheckpoint) -> Result:
        """Save checkpoint to disk."""
        try:
            self.checkpoint_path.mkdir(parents=True, exist_ok=True)
            checkpoint_file = self.checkpoint_path / f"{checkpoint.pause_id}.json"

            with open(checkpoint_file, "w") as f:
                json.dump(checkpoint.to_dict(), f, indent=2)

            self.logger.debug(f"Checkpoint saved: {checkpoint_file}")
            return Ok(checkpoint_file)

        except Exception as e:
            self.logger.exception(f"Checkpoint save error: {e}")
            return Err(str(e))

    async def _load_checkpoint(self, checkpoint_id: str) -> Result:
        """Load checkpoint from disk."""
        try:
            checkpoint_file = self.checkpoint_path / f"{checkpoint_id}.json"

            if not checkpoint_file.exists():
                return Err(f"Checkpoint not found: {checkpoint_id}")

            with open(checkpoint_file, "r") as f:
                data = json.load(f)

            # Reconstruct checkpoint object
            checkpoint = PauseCheckpoint(**data)

            self.logger.debug(f"Checkpoint loaded: {checkpoint_id}")
            return Ok(checkpoint)

        except Exception as e:
            self.logger.exception(f"Checkpoint load error: {e}")
            return Err(str(e))

    @staticmethod
    def _suggest_actions(category: str, phase_num: int) -> List[str]:
        """Generate suggested actions based on correction category."""
        base_actions = [
            "Review changes carefully",
            "Run affected tests",
            "Validate governance compliance",
        ]

        if category == "MINIMAL":
            return base_actions + [f"Resume phase {phase_num}"]

        elif category == "MODERATE":
            return base_actions + [
                f"Re-execute phase {phase_num}",
                f"Validate phase {phase_num + 1}",
            ]

        else:  # SIGNIFICANT
            return base_actions + [
                "Re-evaluate plan timeline",
                "Check all downstream dependencies",
                "Conduct full regression test",
            ]

    @staticmethod
    def _compare_plans(original: Dict[str, Any], updated: Dict[str, Any]) -> List[str]:
        """Compare plans and identify differences."""
        differences = []

        # Simple comparison - in production, use deep diff
        if json.dumps(original) != json.dumps(updated):
            differences.append("Plan structure changed")

        return differences
