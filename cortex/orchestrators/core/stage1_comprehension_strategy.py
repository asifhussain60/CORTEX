"""
Stage 1: LENS Comprehension Strategy.

Runs LENS analysis as the first stage of the 4-stage pipeline.
Produces lens_context in StageContext.metadata for downstream stages.

Authority: ENH-087 Track 1.1, CORE-008 (TDD), CORE-011, CORE-012
AC_START: AC-P1-STAGE1-COMP-001
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from cortex.core.result import Err, Ok, Result
from cortex.orchestrators.strategies.stage_execution_strategy import (
    StageContext,
    StageExecutionStrategy,
)


class Stage1ComprehensionStrategy(StageExecutionStrategy):
    """
    Stage 1: LENS Comprehension.

    Runs LENSOrchestrator.analyze_file() on the target file
    (or workspace root) and stores results in metadata['lens_context'].

    This ensures every operation has code intelligence context
    before intent classification (Stage 2).
    """

    def __init__(self, dependencies: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize Stage 1 strategy.

        Args:
            dependencies: Optional dict with 'lens_orchestrator', etc.
        """
        self._dependencies = dependencies or {}

    def execute(self, context: StageContext) -> Result[StageContext]:
        """
        Execute LENS comprehension.

        Analyzes target file using LENSOrchestrator and stores
        results in context.metadata['lens_context'].

        Args:
            context: StageContext from pipeline.

        Returns:
            Result[StageContext] with lens_context in metadata.
        """
        try:
            lens_context = self._run_lens(context)

            context.metadata["lens_context"] = lens_context
            context.metadata["stage1_timestamp"] = datetime.now().isoformat()
            context.metadata["stage1_status"] = "complete"

            return Ok(context)

        except Exception as e:
            # Graceful degradation — don't block pipeline on LENS failure
            context.metadata["lens_context"] = {
                "status": "lens_error",
                "error": str(e),
                "degraded": True,
            }
            context.metadata["stage1_status"] = "degraded"
            return Ok(context)

    def _run_lens(self, context: StageContext) -> Dict[str, Any]:
        """
        Run LENS analysis from context parameters.

        Args:
            context: StageContext with parameters.

        Returns:
            LENS analysis results dict.
        """
        # Try to get LENS orchestrator from dependencies
        lens_orch = self._dependencies.get("lens_orchestrator")

        if lens_orch is None:
            try:
                from cortex.lens.lens_orchestrator import LENSOrchestrator

                repo_path = Path(context.parameters.get("repo_path", "."))
                if not repo_path.is_absolute():
                    repo_path = Path.cwd() / repo_path
                lens_orch = LENSOrchestrator(repo_path=repo_path)
            except ImportError:
                return {"status": "lens_unavailable", "degraded": True}

        # Get target file
        target_file = context.parameters.get("target_file")
        if target_file:
            target_path = Path(target_file)
            if target_path.exists():
                return lens_orch.analyze_file(target_path)

        # Fallback: return basic workspace metadata
        return {
            "status": "no_target_file",
            "operation": context.operation_name,
        }


# AC_COMPLETE: AC-P1-STAGE1-COMP-001
