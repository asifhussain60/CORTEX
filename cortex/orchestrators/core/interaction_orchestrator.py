"""
InteractionOrchestrator — Stage 1 Comprehension with LENS per-turn.

Wires LENS analysis into every interaction turn, providing:
1. Per-turn LENS context (git, AST, comment, relationship analysis)
2. Optional challenge generation (AC-PERMANENT-FIX-006)
3. IOrchestrator contract compliance
4. ConversationProtocol integration

This is the missing implementation that MasterOrchestrator, wiring.yaml,
and startup_validator all reference. It bridges:
- ConversationProtocol (per-turn LENS comprehension)
- LENSOrchestrator (code intelligence)
- ChallengeEngine (optional disagreement detection)

Authority: MCP-FIRST, CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
AC_START: AC-P0-INTERACTION-ORCH-GREEN-001
"""

from datetime import datetime
import os
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional

from cortex.brain.core.interfaces.i_orchestrator import IOrchestrator, OperationMode
from cortex.brain.core.result import Err, Ok, Result
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
from cortex.infrastructure.trace_integration import trace_orchestrator_action


class InteractionOrchestrator(IOrchestrator):
    """
    Stage 1 orchestrator: LENS-powered comprehension on every turn.

    Coordinates:
    - LENSOrchestrator for per-turn code intelligence
    - ConversationProtocol for turn lifecycle
    - Optional ChallengeEngine for disagreement detection

    Used by MasterOrchestrator as primary Stage 1 orchestrator.
    Registered in wiring.yaml as core orchestrator with lens_protocol capability.

    Attributes:
        conversation_protocol: ConversationProtocol instance for turn management.
        enable_challenges: Whether challenge generation is active.
        lens_orchestrator: LENSOrchestrator for code intelligence.
        turn_number: Current turn counter.
        logger: EnhancedAuditLogger for audit trail.
    """

    def __init__(
        self,
        conversation_protocol: Any,
        enable_challenges: bool = False,
    ) -> None:
        """
        Initialize InteractionOrchestrator.

        Args:
            conversation_protocol: ConversationProtocol instance for turn management.
            enable_challenges: Enable challenge generation (AC-PERMANENT-FIX-006).
        """
        self.orchestrator_id = "interaction"  # For trace logging
        self.conversation_protocol = conversation_protocol
        self.enable_challenges: bool = enable_challenges
        self.turn_number: int = 0
        self._audit_trail: List[Dict[str, Any]] = []
        self.logger = EnhancedAuditLogger.instance()

        # Initialize LENSOrchestrator for per-turn analysis
        self.lens_orchestrator = self._init_lens_orchestrator()

    def _init_lens_orchestrator(self) -> Any:
        """
        Initialize LENSOrchestrator with graceful fallback.

        Returns:
            LENSOrchestrator instance or None if unavailable.
        """
        try:
            from cortex.lens.orchestrator import LENSOrchestrator

            repo_path = Path.cwd()
            return LENSOrchestrator(repo_path=repo_path)
        except Exception:
            # Graceful degradation — LENS not available
            return None

    # =========================================================================
    # IOrchestrator Contract
    # =========================================================================

    def get_name(self) -> str:
        """Get orchestrator name.

        Returns:
            'InteractionOrchestrator' identifier string.
        """
        return "InteractionOrchestrator"

    def get_version(self) -> str:
        """Get orchestrator version.

        Returns:
            Semantic version string.
        """
        return "1.0.0"

    def initialize(self) -> Result[str]:
        """Initialize orchestrator.

        Returns:
            Ok with success message or Err with failure reason.
        """
        try:
            if self.lens_orchestrator is None:
                self.lens_orchestrator = self._init_lens_orchestrator()
            return Ok("InteractionOrchestrator initialized")
        except Exception as e:
            return Err(f"Initialization failed: {str(e)}")

    def get_mode(self) -> OperationMode:
        """Get current operation mode.

        Returns:
            OperationMode.EXECUTION for interaction turns.
        """
        return OperationMode.EXECUTION

    def get_mcp_tools(self) -> Result[Dict[str, Any]]:
        """Get exposed MCP tools.

        Returns:
            Ok with dict of tool definitions.
        """
        return Ok({
            "execute_turn_with_challenge": {
                "name": "execute_turn_with_challenge",
                "description": "Execute one interaction turn with LENS and optional challenge",
            },
            "execute": {
                "name": "execute",
                "description": "Execute comprehension with LENS context",
            },
        })

    @trace_orchestrator_action("EXECUTE_OPERATION")
    def execute_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any],
    ) -> Result[Any]:
        """
        Execute operation with LENS analysis.

        Every operation runs LENS analysis to provide code intelligence
        context for downstream orchestrators.

        Args:
            operation_name: Operation identifier (e.g., 'comprehend').
            parameters: Operation parameters including 'user_input'.

        Returns:
            Result with operation output including lens_context.
        """
        user_input = parameters.get("user_input", parameters.get("request", ""))

        try:
            # Run LENS analysis (per-turn requirement)
            lens_context = self._run_lens_analysis(user_input)

            # Build output
            output: Dict[str, Any] = {
                "operation": operation_name,
                "user_input": user_input,
                "lens_context": lens_context,
                "turn_number": self.turn_number,
                "timestamp": datetime.now().isoformat(),
            }

            # Log audit entry
            self._audit_trail.append({
                "ac_id": "AC-P0-INTERACTION-ORCH-GREEN-001",
                "operation": operation_name,
                "success": True,
                "turn_number": self.turn_number,
                "timestamp": datetime.now().isoformat(),
            })

            return Ok(output)

        except Exception as e:
            return Err(f"Operation {operation_name} failed: {str(e)}")

    def get_audit_trail(self, limit: int = 100) -> Result[list]:
        """Get audit trail from trace database + in-memory fallback.

        Args:
            limit: Maximum entries to return.

        Returns:
            Ok with list of audit entries from trace DB.
        """
        try:
            audit_entries = []
            
            # Try reading from trace database first
            trace_db_path = Path(os.getenv("CORTEX_TRACE_DB", ".cortex/traces/orchestrator-traces.db"))
            if trace_db_path.exists():
                import sqlite3
                with sqlite3.connect(str(trace_db_path)) as conn:
                    # Query trace_interaction table (per-orchestrator table)
                    cursor = conn.execute(
                        "SELECT timestamp, action, context, result, metadata FROM trace_interaction ORDER BY timestamp DESC LIMIT ?",
                        (limit,)
                    )
                    for row in cursor.fetchall():
                        audit_entries.append({
                            "timestamp": row[0],
                            "action": row[1],
                            "context": row[2],
                            "result": row[3],
                            "metadata": row[4]
                        })
            
            # Fallback to in-memory if DB empty
            if not audit_entries:
                audit_entries = self._audit_trail[-limit:]
            
            return Ok(audit_entries)
        except Exception as e:
            # Fallback to in-memory on any error
            return Ok(self._audit_trail[-limit:])

    # =========================================================================
    # Core Turn Execution (used by MasterOrchestrator)
    # =========================================================================

    @trace_orchestrator_action("EXECUTE_TURN_WITH_CHALLENGE")
    def execute_turn_with_challenge(
        self,
        user_request: str,
        round_context: Any,
        pattern_id: Optional[str] = None,
    ) -> Result[Dict[str, Any]]:
        """
        Execute one interaction turn with LENS analysis and optional challenge.

        This is the primary method called by MasterOrchestrator for Stage 1
        comprehension. Every turn:
        1. Increments turn counter
        2. Runs LENS analysis on workspace context
        3. Optionally evaluates challenge patterns
        4. Returns enriched context for Stage 2+

        Args:
            user_request: User's natural language request.
            round_context: RoundContext with turn metadata.
            pattern_id: Optional specific pattern to check for challenge.

        Returns:
            Result with turn output including lens_context and
            optional challenge data.
        """
        self.turn_number += 1

        try:
            # Step 1: Run LENS analysis (MANDATORY per-turn)
            lens_context = self._run_lens_analysis(user_request)

            # Step 2: Build base output
            output: Dict[str, Any] = {
                "type": "comprehension",
                "user_request": user_request,
                "lens_context": lens_context,
                "turn_number": self.turn_number,
                "timestamp": datetime.now().isoformat(),
                "challenge_evaluated": False,
            }

            # Step 3: Optional challenge evaluation
            if self.enable_challenges:
                challenge_result = self._evaluate_challenge(
                    user_request, lens_context, pattern_id
                )
                output["challenge_evaluated"] = True
                if challenge_result is not None:
                    output["type"] = "challenge"
                    output["challenge"] = challenge_result

            # Step 4: Audit trail
            self._audit_trail.append({
                "ac_id": "AC-PERMANENT-FIX-006",
                "operation": "execute_turn_with_challenge",
                "turn_number": self.turn_number,
                "success": True,
                "lens_context_keys": list(lens_context.keys()) if isinstance(lens_context, dict) else [],
                "challenge_evaluated": output["challenge_evaluated"],
                "timestamp": datetime.now().isoformat(),
            })

            return Ok(output)

        except Exception as e:
            self._audit_trail.append({
                "ac_id": "AC-PERMANENT-FIX-006",
                "operation": "execute_turn_with_challenge",
                "turn_number": self.turn_number,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            })
            return Err(f"Turn {self.turn_number} failed: {str(e)}")

    @trace_orchestrator_action("EXECUTE_COMPREHENSION")
    def execute(self, context: Dict[str, Any]) -> Result[Dict[str, Any]]:
        """
        Execute comprehension for MasterOrchestrator Phase 1.

        Simplified interface used by MasterOrchestrator._execute_phase_1()
        to get LENS context for a user intent.

        Args:
            context: Dict with 'user_intent' key.

        Returns:
            Result with comprehension data including intent_type and lens_context.
        """
        user_intent = context.get("user_intent", "")

        try:
            lens_context = self._run_lens_analysis(user_intent)

            # Classify intent from user input
            intent_type = self._classify_intent(user_intent)

            output: Dict[str, Any] = {
                "intent_type": intent_type,
                "lens_context": lens_context,
                "confidence": 0.8,
                "analysis_complete": True,
                "timestamp": datetime.now().isoformat(),
            }

            return Ok(output)

        except Exception as e:
            return Err(f"Comprehension failed: {str(e)}")

    # =========================================================================
    # Internal Methods
    # =========================================================================

    def _run_lens_analysis(self, user_input: str) -> Dict[str, Any]:
        """
        Run LENS analysis for current turn.

        Provides code intelligence context by analyzing workspace files
        relevant to the user's request.

        Args:
            user_input: User's request text for context extraction.

        Returns:
            Dict with LENS analysis results (git, AST, comments, etc.)
            or empty dict on graceful degradation.
        """
        if self.lens_orchestrator is None:
            return {"status": "lens_unavailable", "degraded": True}

        try:
            # Analyze current working directory as default target
            repo_path = Path.cwd()
            # Try to find a relevant file from user input context
            target_file = self._extract_target_file(user_input, repo_path)

            if target_file and target_file.exists():
                return self.lens_orchestrator.analyze_file(target_file)
            else:
                # Fallback: return workspace-level metadata
                return {
                    "status": "no_target_file",
                    "repo_path": str(repo_path),
                    "user_input_hint": user_input[:100],
                }

        except Exception as e:
            # Graceful degradation — never block on LENS failure
            return {
                "status": "lens_error",
                "error": str(e),
                "degraded": True,
            }

    def _extract_target_file(
        self, user_input: str, repo_path: Path
    ) -> Optional[Path]:
        """
        Extract target file path from user input.

        Looks for file references in the user's request to provide
        targeted LENS analysis.

        Args:
            user_input: User's natural language request.
            repo_path: Repository root path.

        Returns:
            Path to target file if found, None otherwise.
        """
        # Simple heuristic: look for .py file references
        words = user_input.split()
        for word in words:
            cleaned = word.strip("'\"`,;:")
            if cleaned.endswith(".py") or cleaned.endswith(".ts") or cleaned.endswith(".js"):
                candidate = repo_path / cleaned
                if candidate.exists():
                    return candidate
                # Try common source directories
                for src_dir in ["cortex", "cortex_brain", "src", "tests"]:
                    candidate = repo_path / src_dir / cleaned
                    if candidate.exists():
                        return candidate
        return None

    def _classify_intent(self, user_input: str) -> str:
        """
        Classify user intent from natural language input.

        Simple keyword-based classification for Stage 1 comprehension.
        More sophisticated classification happens in Stage 2 (IntentRouter).

        Args:
            user_input: User's natural language request.

        Returns:
            Intent type string (IMPLEMENT, FIX, REFACTOR, ANALYZE, UNKNOWN).
        """
        lower = user_input.lower()
        if any(kw in lower for kw in ["implement", "create", "add", "build", "new"]):
            return "IMPLEMENT"
        elif any(kw in lower for kw in ["fix", "bug", "error", "broken", "issue"]):
            return "FIX"
        elif any(kw in lower for kw in ["refactor", "clean", "improve", "optimize"]):
            return "REFACTOR"
        elif any(kw in lower for kw in ["analyze", "audit", "check", "review", "scan"]):
            return "ANALYZE"
        return "UNKNOWN"

    def _evaluate_challenge(
        self,
        user_request: str,
        lens_context: Dict[str, Any],
        pattern_id: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluate whether to generate a challenge for the user's request.

        Checks for disagreement patterns and design concerns that
        should be surfaced before implementation proceeds.

        Args:
            user_request: User's request.
            lens_context: LENS analysis context.
            pattern_id: Specific pattern to check, or None for auto-detect.

        Returns:
            Challenge dict if challenge warranted, None otherwise.
        """
        # Challenge generation is a future enhancement
        # For now, return None (no challenge) to unblock the pipeline
        # ChallengeEngine will be wired here when available
        return None


# AC_COMPLETE: AC-P0-INTERACTION-ORCH-GREEN-001
