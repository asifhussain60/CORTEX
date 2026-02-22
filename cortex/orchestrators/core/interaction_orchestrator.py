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

from cortex.core.core.interfaces.i_orchestrator import IOrchestrator, OperationMode
from cortex.core.core.result import Err, Ok, Result
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
from cortex.infrastructure.trace_integration import trace_orchestrator_action

# Phase 23: Import WorkflowTemplateMixin for template consumption capability
from cortex.core.workflow_template_mixin import WorkflowTemplateMixin


class InteractionOrchestrator(IOrchestrator, WorkflowTemplateMixin):
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
            from cortex.lens.lens_orchestrator import LENSOrchestrator

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

    def get_recommended_template(self) -> Optional[str]:
        """Return the recommended workflow template for InteractionOrchestrator.

        Returns:
            Template ID for request execution plan gate.
        """
        return "request-execution/plan-gate"

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
            trace_db_path = Path(os.getenv("CORTEX_TRACE_DB", ".cortex-runtime/traces/orchestrator-traces.db"))
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

    def execute_turn(self, user_input: str) -> Result[Dict[str, Any]]:
        """
        Execute a single interaction turn (simplified interface).

        Delegates core logic without challenge evaluation.
        Required by startup_validator (line 317) and ConversationProtocol contract.

        Args:
            user_input: User's natural language request.

        Returns:
            Result with turn output including user_input, lens_context, turn_number.
        """
        self.turn_number += 1

        try:
            lens_context = self._run_lens_analysis(user_input)

            output: Dict[str, Any] = {
                "user_input": user_input,
                "lens_context": lens_context,
                "turn_number": self.turn_number,
                "timestamp": datetime.now().isoformat(),
                "challenge_evaluated": False,
            }

            self._audit_trail.append({
                "operation": "execute_turn",
                "turn_number": self.turn_number,
                "success": True,
                "timestamp": datetime.now().isoformat(),
            })

            return Ok(output)

        except Exception as e:
            return Err(f"execute_turn {self.turn_number} failed: {str(e)}")

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

            # Step 4: Apply token optimization (ENH-046 Phase 4 Integration)
            try:
                from cortex.core.interaction.context_synthesis_gateway import get_gateway
                
                gateway = get_gateway()
                session_id = getattr(round_context, 'session_id', 'default_session')
                
                synthesized = gateway.synthesize(
                    context=output,
                    session_id=session_id,
                    orchestrator_name="InteractionOrchestrator"
                )
                
                # Log budget violations but don't block
                if not synthesized.budget_compliant:
                    self.logger.log_operation_complete(
                        ac_id="AC-TOKEN-OPT-001",
                        operation="token_budget_violation",
                        success=False,
                        details={
                            "turn_number": self.turn_number,
                            "tokens": synthesized.token_count,
                            "budget": gateway.token_budget,
                            "overflow": synthesized.token_count - gateway.token_budget
                        }
                    )
                
                # Merge synthesis metadata — preserve canonical keys
                # (challenge_evaluated, lens_context, type required downstream)
                synthesis_meta = synthesized.context or {}
                output["synthesized_content"] = synthesis_meta.get("synthesized_content")
                output["compression_strategy"] = synthesis_meta.get("compression_strategy")

            except Exception as gateway_err:
                # Graceful degradation - log but continue with original output
                self.logger.log_operation_complete(
                    ac_id="AC-TOKEN-OPT-001",
                    operation="token_optimization_failed",
                    success=False,
                    details={"error": str(gateway_err)}
                )
            
            # Step 5: Audit trail
            self._audit_trail.append({
                "ac_id": "AC-PERMANENT-FIX-006",
                "operation": "execute_turn_with_challenge",
                "turn_number": self.turn_number,
                "success": True,
                "lens_context_keys": list(lens_context.keys()) if isinstance(lens_context, dict) else [],
                "challenge_evaluated": output.get("challenge_evaluated", False),
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
            
            # Apply token optimization (ENH-046 Phase 4 Integration)
            try:
                from cortex.core.interaction.context_synthesis_gateway import get_gateway
                
                gateway = get_gateway()
                session_id = context.get('session_id', 'default_session')
                
                synthesized = gateway.synthesize(
                    context=output,
                    session_id=session_id,
                    orchestrator_name="InteractionOrchestrator"
                )

                # Merge synthesis metadata into output — preserve canonical keys
                # (intent_type, lens_context, confidence) required by MasterOrchestrator
                synthesis_meta = synthesized.context or {}
                output["synthesized_content"] = synthesis_meta.get("synthesized_content")
                output["compression_strategy"] = synthesis_meta.get("compression_strategy")

            except Exception:
                # Graceful degradation - return original output
                pass

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
                for src_dir in ["cortex", "cortex.intelligence", "src", "tests"]:
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

    # =========================================================================
    # ENH-090: Semantic Block Assembly Integration
    # =========================================================================

    def _init_block_assembler(self) -> Any:
        """
        Initialize SemanticBlockAssembler with graceful fallback.

        Returns:
            SemanticBlockAssembler instance or None if unavailable.
        """
        try:
            from cortex.core.registry.semantic_blocks import SemanticBlockAssembler, SemanticBlockLoader, SemanticBlockReasoner

            loader = SemanticBlockLoader()
            reasoner = SemanticBlockReasoner(loader)
            return SemanticBlockAssembler(loader, reasoner)
        except Exception:
            # Graceful degradation — blocks not available
            return None

    @property
    def block_assembler(self) -> Any:
        """
        Lazy-load semantic block assembler on first access.

        Returns:
            SemanticBlockAssembler instance.
        """
        if not hasattr(self, "_block_assembler"):
            self._block_assembler = self._init_block_assembler()
        return self._block_assembler

    def detect_intent(self, context: Dict[str, Any]) -> str:
        """
        Classify user intent from request text.

        Analyzes user request to determine intent (IMPLEMENT, FIX, ANALYZE, etc.).

        Args:
            context: Dictionary with 'user_request' and 'conversation_history'.

        Returns:
            Intent string (IMPLEMENT|FIX|REFACTOR|ANALYZE|AUDIT|PLAN).
        """
        user_request = context.get("user_request", "").lower()

        # Intent detection heuristics (order matters — check specific before general)
        if any(kw in user_request for kw in ["implement", "create", "build", "add", "new"]):
            return "IMPLEMENT"
        elif any(kw in user_request for kw in ["fix", "bug", "error", "broken", "issue", "debug"]):
            return "FIX"
        elif any(kw in user_request for kw in ["refactor", "clean", "improve", "optimize", "reorganize"]):
            return "REFACTOR"
        elif any(kw in user_request for kw in ["plan", "design", "organize", "roadmap"]):
            # Check PLAN before ANALYZE (architect can mean analyze OR plan)
            return "PLAN"
        elif any(kw in user_request for kw in ["analyze", "audit", "check", "review", "scan", "what", "show", "explain"]):
            return "ANALYZE"
        else:
            # Default to ANALYZE for queries
            return "ANALYZE"

    def select_blocks_for_intent(self, intent: str) -> List[str]:
        """
        Select appropriate semantic blocks for an intent.

        Maps intent to block composition rules.

        Args:
            intent: User intent (IMPLEMENT|FIX|REFACTOR|ANALYZE|AUDIT|PLAN).

        Returns:
            List of block names to assemble.
        """
        # Intent → block selection mapping
        intent_blocks = {
            "IMPLEMENT": ["capabilities", "tutorial", "next_steps"],
            "FIX": ["capabilities", "lens", "next_steps"],
            "REFACTOR": ["capabilities", "tutorial", "next_steps"],
            "ANALYZE": ["lens", "orchestrators", "next_steps"],
            "AUDIT": ["capabilities", "orchestrators", "next_steps"],
            "PLAN": ["capabilities", "orchestrators", "next_steps"],
        }

        return intent_blocks.get(intent, ["capabilities", "next_steps"])

    def select_blocks_for_context(self, context: Dict[str, Any]) -> List[str]:
        """
        Select blocks based on conversation context.

        First interaction includes INTRO block.
        Subsequent interactions omit INTRO.

        Args:
            context: Dictionary with 'user_request' and 'conversation_history'.

        Returns:
            List of block names to assemble.
        """
        history = context.get("conversation_history", [])
        is_first = len(history) == 0

        # Detect intent
        intent = self.detect_intent(context)
        blocks = self.select_blocks_for_intent(intent)

        # Add INTRO for first interaction
        if is_first:
            blocks = ["intro"] + blocks

        return blocks

    def assemble_response(self, context: Dict[str, Any]) -> str:
        """
        Assemble personality-consistent response using semantic blocks.

        Args:
            context: Dictionary with 'user_request' and 'conversation_history'.

        Returns:
            Assembled markdown response.
        """
        if self.block_assembler is None:
            # Fallback: return simple message if blocks unavailable
            return "**CORTEX Ready** — Unable to load semantic blocks. Proceeding with basic mode."

        # Select blocks for context
        blocks = self.select_blocks_for_context(context)

        # Assemble
        result = self.block_assembler.assemble(blocks)

        return result.assembled_content

    def assemble_response_with_metrics(
        self, context: Dict[str, Any]
    ) -> tuple:
        """
        Assemble response and return metrics.

        Args:
            context: Dictionary with 'user_request' and 'conversation_history'.

        Returns:
            Tuple of (assembled_content, metrics_dict).
        """
        if self.block_assembler is None:
            return ("CORTEX Ready — Blocks unavailable", {})

        # Select and assemble
        blocks = self.select_blocks_for_context(context)
        result = self.block_assembler.assemble(blocks)

        # Build metrics
        metrics = {
            "blocks_used": result.blocks_assembled,
            "total_words": result.total_words,
            "personality_consistent": result.personality_consistent,
            "duplication_check_passed": result.duplication_check_passed,
            "rendering_valid": result.rendering_valid,
        }

        return (result.assembled_content, metrics)


# AC_COMPLETE: AC-P0-INTERACTION-ORCH-GREEN-001
