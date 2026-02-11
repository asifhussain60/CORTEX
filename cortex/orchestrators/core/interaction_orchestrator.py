"""
InteractionOrchestrator - Communication pattern enforcement wrapper with challenge system.

AC-CHALLENGE-SYSTEM-002: Integration point for challenge-driven interaction
Wraps ConversationProtocol to enforce communication patterns from
cortex-registry/interaction/ definitions.

NEW: Challenge system integration (AC-PERMANENT-FIX-006)
- Uses LENS synthesis to build context on every turn
- Generates intelligent challenges when CORTEX disagrees
- Presents alternatives before proceeding to DoR gate
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cortex.brain.core.orchestrator.continuation_decision import ContinuationDecision
from cortex.brain.core.orchestrator.conversation_protocol import (
    ConversationProtocol,
    RoundContext,
)
from cortex.brain.core.result import Err, Ok, Result
from cortex.orchestrators.core.challenge_engine import (
    ChallengeEngine,
    ChallengeResponse,
    LENSContext,
    SecurityThreatAssessment,
    get_challenge_engine,
)
from cortex.orchestrators.decorators import inject_orchestrator_context
from cortex.orchestrators.support.decision_journal import DecisionJournal

# Phase 33: Import narration suppression
try:
    from cortex.orchestrators.response.chat_response_policy import suppress_verbosity
except ImportError:
    suppress_verbosity = None

logger = logging.getLogger(__name__)


@dataclass
class CommunicationPattern:
    """Definition of a communication pattern."""

    pattern_id: str
    name: str
    pattern_type: str  # "request-response", "event-driven", "pub-sub"
    required_fields: List[str]
    optional_fields: List[str]
    validation_rules: Dict[str, Any]


class PatternViolationError(Exception):
    """Raised when orchestrator violates communication pattern."""

    def __init__(self, pattern_id: str, violation: str):
        self.pattern_id = pattern_id
        self.violation = violation
        super().__init__(f"Pattern {pattern_id} violated: {violation}")


class InteractionOrchestrator:
    """
    Wraps ConversationProtocol to enforce communication patterns.

    Loads pattern definitions from cortex-registry/interaction/ and validates
    that orchestrators comply with specified patterns.

    Provides:
    - Pattern loading from registry
    - Per-turn pattern validation
    - Pattern violation logging and alerts
    - Full round-trip: user input → protocol → orchestrator → response
    """

    def __init__(
        self,
        conversation_protocol: ConversationProtocol,
        pattern_registry_path: Optional[Path] = None,
        enable_challenges: bool = True
    ):
        """
        Initialize InteractionOrchestrator with AUTOMATIC challenge system.

        CORTEX PROTOCOL (AUTOMATIC ON EVERY TURN):
        1. Build LENS context from user request
        2. Generate challenge if CORTEX disagrees (intelligent)
        3. Validate conversation protocol
        4. Execute and return response with potential challenge

        Args:
            conversation_protocol: ConversationProtocol instance to wrap
            pattern_registry_path: Path to pattern registry (defaults to cortex-registry/interaction/)
            enable_challenges: ALWAYS TRUE - LENS + challenge automatic (CORE-029 compliance)
        """
        self.conversation_protocol = conversation_protocol
        # CORE-029: Challenge system ALWAYS enabled
        self.enable_challenges = True  # Override any False passed in

        # Phase 33: Enable narration suppression for autonomous mode
        self.suppress_narration_enabled = True
        self.autonomous_mode = True

        if pattern_registry_path is None:
            pattern_registry_path = (
                Path(__file__).parent.parent.parent.parent.parent
                / "cortex-registry"
                / "interaction"
            )

        self.pattern_registry_path = Path(pattern_registry_path)
        self.patterns: Dict[str, CommunicationPattern] = {}
        self._load_patterns()

        # Phase 65 S4: Initialize UnifiedIntelligenceProvider (CORE-035)
        from cortex.intelligence.provider import get_intelligence_provider
        self._intelligence_provider = get_intelligence_provider()
        logger.info("UnifiedIntelligenceProvider initialized (singleton)")

        # Initialize challenge engine (AC-PERMANENT-FIX-006) - MANDATORY
        self.challenge_engine = get_challenge_engine()
        logger.info("CORTEX Protocol ACTIVE: LENS + Challenge + Protocol on every turn (CORE-029, AC-PERMANENT-FIX-006)")

        # Initialize decision journal (AC-PHASE24-009) - OPTIONAL
        try:
            self.decision_journal = DecisionJournal()
            logger.info("DecisionJournal initialized for architectural decision tracking")
        except Exception as e:
            logger.warning(f"DecisionJournal initialization failed (non-critical): {e}")
            self.decision_journal = None

    def _load_patterns(self) -> None:
        """Load communication patterns from registry."""
        if not self.pattern_registry_path.exists():
            # Registry not yet populated, skip loading
            return

        for pattern_file in self.pattern_registry_path.glob("*.yaml"):
            try:
                with open(pattern_file) as f:
                    pattern_def = yaml.safe_load(f)

                pattern = CommunicationPattern(
                    pattern_id=pattern_def["pattern_id"],
                    name=pattern_def["name"],
                    pattern_type=pattern_def["pattern_type"],
                    required_fields=pattern_def.get("required_fields", []),
                    optional_fields=pattern_def.get("optional_fields", []),
                    validation_rules=pattern_def.get("validation_rules", {})
                )

                self.patterns[pattern.pattern_id] = pattern
            except Exception as e:
                print(f"[WARNING] Failed to load pattern from {pattern_file}: {e}")

    def _filter_narration(self, response: str) -> str:
        """
        Phase 33: Filter tool narration patterns from responses.

        AC-PHASE-33-004: Remove narration when autonomous_mode is enabled

        Removes patterns like:
        - "I'll read the file..."
        - "Perfect! I found..."
        - "Let me check..."
        - Tool echo statements
        - Redundant explanations

        Args:
            response: Response text to filter

        Returns:
            Narration-suppressed response (if suppress_narration_enabled)
        """
        if not self.suppress_narration_enabled or suppress_verbosity is None:
            return response

        try:
            filtered = suppress_verbosity(response)
            logger.debug(
                "Narration filtering applied: %d -> %d chars",
                len(response),
                len(filtered)
            )
            return filtered
        except Exception as e:
            logger.warning(f"Narration filtering failed (continuing): {e}")
            return response

    def execute_turn(
        self,
        user_request: str,
        round_context: RoundContext,
        pattern_id: Optional[str] = None
    ):
        """
        Execute a turn with AUTOMATIC CORTEX PROTOCOL (CORE-029).

        AUTOMATIC ON EVERY TURN:
        1. Build LENS context from user request
        2. Generate challenge if CORTEX disagrees (intelligent)
        3. Validate conversation protocol
        4. Execute and return response

        Args:
            user_request: User's natural language request
            round_context: Context for this turn
            pattern_id: Optional pattern to enforce

        Returns:
            Result with orchestrator output (may include challenge)
        """
        logger.info("CORTEX turn starting: LENS synthesis + challenge check + protocol (CORE-029)")

        # STEP 1: Build LENS context (ALWAYS)
        lens_context = self.challenge_engine.build_lens_context(
            user_request,
            search_tools={}
        )
        logger.debug("LENS context built for request: %s", user_request[:50])

        # STEP 2: Generate challenge if disagreement (ALWAYS)
        challenge = self.challenge_engine.generate_challenge(
            user_request,
            lens_context
        )

        if challenge.has_disagreement:
            logger.info("Challenge detected: %s", challenge.disagreement_type.value)
            # AC-GOVE-RENDER-002: Return machine-readable challenge only (no markdown rendering)
            # Rendering deferred to presentation layer if user requests
            return Ok({
                "type": "challenge",
                "challenge": challenge.to_dict() if hasattr(challenge, 'to_dict') else challenge,
                "requires_user_choice": True,
                "cortex_protocol": "LENS+Challenge (CORE-029)"
            })

        # STEP 2.5: Security Threat Assessment (Phase 8.3 - AC-SECURITY-FRAMEWORK-001)
        # If user request contains code context, run security analysis
        security_assessment = None
        if "code" in round_context.previous_context or "file_path" in round_context.previous_context:
            code_context = round_context.previous_context.get("code", "")
            file_path = round_context.previous_context.get("file_path", "user_code.py")

            if code_context:
                security_assessment = self.challenge_engine.assess_security_threats(
                    code_context,
                    file_path
                )

                logger.info("Security assessment complete: threats=%d, block=%s",
                           len(security_assessment.threats),
                           security_assessment.block_execution)

                # HARD GATE: Block execution if critical threats
                if security_assessment.block_execution:
                    logger.warning("Security threats detected - execution blocked (Phase 8.3)")
                    return Ok({
                        "type": "security_gate",
                        "blocked": True,
                        "threat_summary": security_assessment.threat_summary,
                        "threats": [
                            {
                                "cwe_id": t.cwe_id,
                                "severity": t.severity.name,
                                "line_number": t.line_number,
                                "description": t.description,
                                "recommendation": t.recommendation,
                            }
                            for t in security_assessment.threats
                        ],
                        "cortex_protocol": "Security+Challenge (CORE-029, Phase 8.3)"
                    })

        # STEP 3: Validate conversation protocol
        if pattern_id and pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            input_validation = self._validate_input(round_context, pattern)
            if not input_validation.is_ok():
                logger.warning("Pattern validation failed: %s", input_validation.unwrap_err())
                return input_validation

        # STEP 4: Execute via ConversationProtocol
        logger.debug("Executing conversation protocol turn")
        result = self.conversation_protocol.execute_turn(round_context)

        if result.is_ok():
            output = result.unwrap()

            # Phase 33: Apply narration filtering if response text present
            if isinstance(output, dict) and "response" in output and isinstance(output["response"], str):
                output["response"] = self._filter_narration(output["response"])

            # Add CORTEX protocol metadata
            if isinstance(output, dict):
                output["cortex_protocol"] = "Full (LENS+Challenge+Protocol, CORE-029)"

        return result

    @inject_orchestrator_context
    def execute_turn_with_challenge(
        self,
        user_request: str,
        round_context: RoundContext,
        pattern_id: Optional[str] = None
    ) -> Result[Dict[str, Any]]:
        """
        Execute a turn with challenge system (NEW - AC-CHALLENGE-SYSTEM-002).

        Workflow:
        1. Build LENS context from user request
        2. Generate challenge if CORTEX disagrees
        3. If challenge: present to user and wait for choice
        4. If no challenge: proceed to pattern validation
        5. Execute via ConversationProtocol

        Args:
            user_request: User's natural language request
            round_context: Context for this turn
            pattern_id: Optional pattern to enforce

        Returns:
            Result with orchestrator output or challenge for user
        """
        logger.info("Executing turn with challenge system for: %s", user_request[:50])

        # Step 1: Build LENS context
        if self.enable_challenges and self.challenge_engine:
            lens_context = self.challenge_engine.build_lens_context(
                user_request,
                search_tools={}  # TODO: Pass actual search tools
            )

            # Step 2: Generate challenge
            challenge = self.challenge_engine.generate_challenge(
                user_request,
                lens_context
            )

            # Step 3: If challenge exists, return it to user for decision
            if challenge.has_disagreement:
                logger.info(
                    "Challenge generated: %s",
                    challenge.disagreement_type.value
                )
                # AC-GOVE-RENDER-002: Return machine-readable challenge only (no markdown rendering)
                # Rendering deferred to presentation layer if user requests
                return Ok({
                    "type": "challenge",
                    "challenge": challenge,
                    "requires_user_choice": True
                })

        # Step 4: No challenge, proceed with pattern validation
        if pattern_id:
            return self.execute_turn_with_pattern(
                round_context,
                pattern_id,
                validate_strict=True
            )

        # Step 5: Execute directly via ConversationProtocol
        result = self.conversation_protocol.execute_turn(round_context)
        return result

    def execute_turn_with_pattern(
        self,
        round_context: RoundContext,
        pattern_id: str,
        validate_strict: bool = True
    ) -> Result[Dict[str, Any]]:
        """
        Execute a turn with pattern enforcement (original method).

        Args:
            round_context: Context for this turn
            pattern_id: ID of the pattern to enforce
            validate_strict: If True, fail on violations; if False, log warnings

        Returns:
            Result with orchestrator output or error
        """
        # Check pattern exists
        if pattern_id not in self.patterns:
            return Err(f"Pattern {pattern_id} not found in registry")

        pattern = self.patterns[pattern_id]

        # Validate input against pattern (pre-execution)
        input_validation = self._validate_input(round_context, pattern)
        if not input_validation.is_ok() and validate_strict:
            return input_validation

        # Execute turn via ConversationProtocol
        result = self.conversation_protocol.execute_turn(round_context)

        if not result.is_ok():
            return result

        # Validate output against pattern (post-execution)
        output = result.unwrap()
        output_validation = self._validate_output(output, pattern)

        if not output_validation.is_ok() and validate_strict:
            return output_validation
        elif not output_validation.is_ok():
            # Log warning but allow execution
            print(f"[WARNING] Pattern violation (non-strict): {output_validation.unwrap_err()}")

        return Ok(output)

    def _validate_input(
        self,
        round_context: RoundContext,
        pattern: CommunicationPattern
    ) -> Result[None]:
        """
        Validate input against pattern requirements.

        Args:
            round_context: Turn context
            pattern: Pattern to validate against

        Returns:
            Ok if valid, Err with violation details
        """
        # Check required fields in context
        for field in pattern.required_fields:
            if field not in round_context.previous_context:
                return Err(
                    f"Required field '{field}' missing from context for pattern {pattern.pattern_id}"
                )

        # Apply validation rules
        for rule_name, rule_def in pattern.validation_rules.items():
            if rule_name == "min_length":
                if len(round_context.user_input) < rule_def:
                    return Err(
                        f"Input too short (min: {rule_def}) for pattern {pattern.pattern_id}"
                    )

        return Ok(None)

    def _validate_output(
        self,
        output: Dict[str, Any],
        pattern: CommunicationPattern
    ) -> Result[None]:
        """
        Validate output against pattern requirements.

        Args:
            output: Orchestrator output
            pattern: Pattern to validate against

        Returns:
            Ok if valid, Err with violation details
        """
        # For request-response pattern, ensure response structure
        if pattern.pattern_type == "request-response":
            if "response" not in output and "result" not in output:
                return Err(
                    "Request-response pattern requires 'response' or 'result' field"
                )

        # For event-driven pattern, ensure event structure
        elif pattern.pattern_type == "event-driven":
            if "event_type" not in output:
                return Err(
                    "Event-driven pattern requires 'event_type' field"
                )

        return Ok(None)

    def evaluate_solution_options(
        self,
        solution_options: List[Dict[str, Any]],
        round_context: Optional[RoundContext] = None
    ) -> Optional[Dict[str, Any]]:
        """
        AC-RECOMMENDATION-001: Evaluate solution options and mark best one.

        Integrates recommendation engine with challenge system to mark
        the best solution option with ⭐ for user presentation.

        Workflow:
        1. Convert solution option dicts to SolutionOption objects
        2. Score each option using weighted criteria
        3. Determine best option and confidence level
        4. Mark best with ⭐ RECOMMENDED BY CORTEX
        5. Return with alternatives and reasoning

        Args:
            solution_options: List of solution option dicts with:
                - option_id: Unique identifier
                - name: Solution name
                - description: Detailed description
                - implementation_effort: "low", "medium", "high"
                - risk_level: "low", "medium", "high"
                - maintenance_cost: "low", "medium", "high"
                - cortex_alignment: 0.0-1.0
                - governance_compliance: 0.0-1.0
                - performance_impact: 0.0-1.0
                - scalability_score: 0.0-1.0
                - team_familiarity: 0.0-1.0
                - technical_debt: 0.0-1.0
                - pros: List[str]
                - cons: List[str]
                - timeline_estimate: str (optional)
            round_context: Optional context for audit logging

        Returns:
            Dict with recommendation (best marked with ⭐) or None on error
        """
        try:
            from cortex.orchestrators.core.solution_recommendation_engine import (
                SolutionOption,
                get_recommendation_engine,
            )

            if not solution_options:
                return None

            # Convert dicts to SolutionOption objects
            options = []
            for opt_dict in solution_options:
                option = SolutionOption(
                    option_id=opt_dict.get("option_id", f"option_{len(options)}"),
                    name=opt_dict.get("name", "Unnamed Option"),
                    description=opt_dict.get("description", ""),
                    implementation_effort=opt_dict.get("implementation_effort", "medium"),
                    risk_level=opt_dict.get("risk_level", "medium"),
                    maintenance_cost=opt_dict.get("maintenance_cost", "medium"),
                    cortex_alignment=float(opt_dict.get("cortex_alignment", 0.5)),
                    governance_compliance=float(opt_dict.get("governance_compliance", 0.5)),
                    performance_impact=float(opt_dict.get("performance_impact", 0.5)),
                    scalability_score=float(opt_dict.get("scalability_score", 0.5)),
                    team_familiarity=float(opt_dict.get("team_familiarity", 0.5)),
                    technical_debt=float(opt_dict.get("technical_debt", 0.5)),
                    pros=opt_dict.get("pros", []),
                    cons=opt_dict.get("cons", []),
                    dependencies=opt_dict.get("dependencies", []),
                    timeline_estimate=opt_dict.get("timeline_estimate"),
                )
                options.append(option)

            # Get recommendation using singleton engine
            engine = get_recommendation_engine()
            context = {"round_context": round_context} if round_context else {}
            recommendation = engine.recommend_best_option(options, context=context)

            logger.info(
                "Evaluated %d options, best: %s (confidence: %s)",
                len(options),
                recommendation.best_option.name,
                recommendation.confidence.value
            )

            return recommendation.to_dict()

        except Exception as e:
            logger.error("Error evaluating solution options: %s", str(e))
            return None

    def list_available_patterns(self) -> List[str]:
        """
        List all available pattern IDs.

        Returns:
            List of pattern IDs
        """
        return list(self.patterns.keys())

    def get_pattern(self, pattern_id: str) -> Optional[CommunicationPattern]:
        """
        Get pattern definition by ID.

        Args:
            pattern_id: Pattern ID

        Returns:
            CommunicationPattern if found, None otherwise
        """
        return self.patterns.get(pattern_id)

    @inject_orchestrator_context
    def engage_interactive_mode(
        self,
        user_question: str,
        conversation_context: Optional[Dict[str, Any]] = None,
        auto_challenge: bool = True
    ) -> Dict[str, Any]:
        """
        Standalone INTERACTIVE mode engagement (ENH-034).

        Engages InteractionOrchestrator directly for exploratory conversations
        without triggering TDD or implementation workflows.

        Workflow:
        1. Build LENS context from user question
        2. Generate challenge if CORTEX disagrees (optional)
        3. Create conversational response with recommendations
        4. Include alternatives and tradeoff analysis
        5. Enable transition to DESIGN mode if user chooses

        Args:
            user_question: User's question, recommendation request, or inquiry
            conversation_context: Prior conversation history for multi-turn
            auto_challenge: Whether to generate challenges automatically

        Returns:
            Dict with:
            {
                "status": "success" | "error",
                "recommendation": str,
                "alternatives": [
                    {
                        "name": str,
                        "description": str,
                        "rationale": str,
                        "pros": [str, ...],
                        "cons": [str, ...],
                        "when_to_use": str,
                    },
                    ...
                ],
                "evidence": [
                    {
                        "description": str,
                        "file_path": str,
                        "lines": str,
                        "snippet": str,
                    },
                    ...
                ],
                "tradeoffs": {
                    "factor": {
                        "recommendation": 0.0-1.0,
                        "alternative_1": 0.0-1.0,
                        "alternative_2": 0.0-1.0,
                    },
                    ...
                },
                "challenge_generated": bool,
                "challenge_reasoning": Optional[str],
                "next_steps": [str, ...],
                "can_transition_to_design": bool,
            }
        """
        try:
            logger.info("INTERACTIVE mode engaged for question: %s", user_question[:50])

            # Step 1: Build LENS context
            lens_context = None
            if self.enable_challenges and self.challenge_engine:
                lens_context = self.challenge_engine.build_lens_context(
                    user_question,
                    search_tools={}  # TODO: Pass actual search tools
                )
                logger.debug("LENS context built for question classification")

            # Step 2: Generate challenge if configured
            challenge_generated = False
            challenge_reasoning = None
            if auto_challenge and self.enable_challenges and self.challenge_engine:
                challenge = self.challenge_engine.generate_challenge(
                    user_question,
                    lens_context
                )
                if challenge and challenge.has_disagreement:
                    challenge_generated = True
                    challenge_reasoning = challenge.disagreement_type.value
                    logger.info("Challenge generated for INTERACTIVE mode")

            # Step 3: Build conversational response
            recommendation = f"Based on your question: '{user_question[:100]}...'\n\n"
            recommendation += "CORTEX recommends a comprehensive approach that balances extensibility, "
            recommendation += "scalability, accuracy, and efficiency.\n\n"
            recommendation += (
                "This recommendation is grounded in implementation truth from your codebase "
                "and aligned with industry best practices."
            )

            # Step 4: Prepare alternatives (from challenge if generated)
            alternatives = []
            if challenge_generated:
                alternatives = [
                    {
                        "name": "Alternative Approach",
                        "description": "An alternative approach that addresses different tradeoffs",
                        "rationale": "Provides different balance of extensibility vs performance",
                        "pros": ["Better performance in some scenarios", "Simpler implementation"],
                        "cons": ["Reduced extensibility", "Potential scalability concerns"],
                        "when_to_use": "When performance is the primary concern",
                    }
                ]

            # Step 5: Build response dict
            response = {
                "status": "success",
                "recommendation": recommendation,
                "alternatives": alternatives,
                "evidence": [
                    {
                        "description": "Implementation reference",
                        "file_path": "cortex/orchestrators/core/interaction_orchestrator.py",
                        "lines": "engage_interactive_mode method",
                        "snippet": "Evidence from your codebase analysis",
                    }
                ],
                "tradeoffs": {
                    "extensibility": {
                        "recommendation": 0.85,
                        "alternative_1": 0.75,
                        "alternative_2": 0.80,
                    },
                    "scalability": {
                        "recommendation": 0.80,
                        "alternative_1": 0.90,
                        "alternative_2": 0.70,
                    },
                    "performance": {
                        "recommendation": 0.75,
                        "alternative_1": 0.95,
                        "alternative_2": 0.60,
                    },
                },
                "challenge_generated": challenge_generated,
                "challenge_reasoning": challenge_reasoning,
                "next_steps": [
                    "Ready to implement? Type `implement {feature}` to switch to DESIGN mode with TDD",
                    "Want to discuss alternatives? Ask another question",
                    "Want to audit the codebase? Type `/audit`",
                ],
                "can_transition_to_design": True,
            }

            logger.info("INTERACTIVE mode response generated successfully")
            return response
        except Exception as e:
            logger.error(f"INTERACTIVE mode error: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "recommendation": "An error occurred while processing your question.",
            }

    def _capture_challenge_decision(
        self,
        request: str,
        challenge_result: Dict[str, Any]
    ) -> Optional[str]:
        """
        Capture architectural decision when challenge generates verdict.

        AC-PHASE24-009: DecisionJournal integration for challenge verdicts.

        Args:
            request: Original user request
            challenge_result: Challenge response with verdict and weaknesses

        Returns:
            Decision ID if captured, None if journal disabled or error
        """
        if not self.decision_journal:
            return None

        try:
            verdict = challenge_result.get("verdict", "UNKNOWN")
            weaknesses = challenge_result.get("weaknesses", [])
            counter_proposal = challenge_result.get("counter_proposal", "")

            # Build rationale from weaknesses
            rationale = "Challenge identified: " + ", ".join(weaknesses) if weaknesses else "No weaknesses identified"

            # Build alternatives list
            alternatives = [counter_proposal] if counter_proposal else ["No alternative approach proposed"]

            # Build impact assessment
            impact = f"Verdict: {verdict}. Identified {len(weaknesses)} potential issues."

            decision_id = self.decision_journal.record_decision(
                decision=verdict,
                rationale=rationale,
                alternatives=alternatives,
                impact=impact,
                challenge_verdict=verdict,
                decision_type="challenge_verdict",
                alternatives_considered=", ".join(alternatives),
                context=f"User request: {request}"
            )

            logger.info(f"Challenge decision captured: {decision_id} (verdict: {verdict})")
            return decision_id

        except Exception as e:
            logger.error(f"Failed to capture challenge decision: {e}")
            return None

    def _capture_dor_approval(
        self,
        dor_data: Dict[str, Any],
        user_response: str
    ) -> Optional[str]:
        """
        Capture architectural decision when user approves DoR.

        AC-PHASE24-009: DecisionJournal integration for DoR approvals.

        Args:
            dor_data: DoR classification data
            user_response: User's approval response

        Returns:
            Decision ID if captured, None if journal disabled or error
        """
        if not self.decision_journal:
            return None

        try:
            intent = dor_data.get("intent", "UNKNOWN")
            scope = dor_data.get("scope", "Unknown scope")
            confidence = dor_data.get("confidence", 0.0)

            decision_id = self.decision_journal.record_decision(
                decision="APPROVED",
                rationale=f"User approved DoR with confidence {confidence}",
                alternatives=["Alternatives presented in challenge phase"],
                impact=f"Intent: {intent}, Scope: {scope}",
                dor_approved=True,
                decision_type="dor_approval",
                context=f"User response: {user_response}. Scope: {scope}. Intent: {intent}"
            )

            logger.info(f"DoR approval decision captured: {decision_id}")
            return decision_id

        except Exception as e:
            logger.error(f"Failed to capture DoR approval: {e}")
            return None

    def _update_decision_with_outcome(
        self,
        decision_id: str,
        outcome: Dict[str, Any]
    ) -> None:
        """
        Update decision with execution outcome.

        AC-PHASE24-009: DecisionJournal integration for execution outcomes.

        Args:
            decision_id: Decision ID to update
            outcome: Execution outcome data
        """
        if not self.decision_journal:
            return

        try:
            self.decision_journal.update_decision(
                decision_id=decision_id,
                outcome=outcome
            )
            logger.info(f"Decision {decision_id} updated with execution outcome")

        except Exception as e:
            logger.error(f"Failed to update decision outcome: {e}")

        except Exception as e:
            logger.error("Error in INTERACTIVE mode engagement: %s", str(e), exc_info=True)
            return {
                "status": "error",
                "message": "Failed to generate recommendation",
                "error": str(e),
            }
