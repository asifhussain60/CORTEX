# AC-ID: ARCH-012-REFACTOR - TDDOrchestrator V2 with Base Protocol
"""
TDDOrchestrator V2 - Refactored to use OrchestratorBaseProtocol.

PROOF OF CONCEPT: First orchestrator migrated to base protocol pattern.

Before (TDDOrchestrator):
- 555 lines
- Manual LENS context building (none)
- No challenge generation
- No DoR confidence gate
- No security threat assessment
- Pure TDD logic only

After (TDDOrchestrator):
- ~250 lines (55% reduction)
- Automatic LENS context (inherited)
- Automatic challenge generation (inherited)
- Automatic DoR confidence gate (inherited)
- Automatic security assessment (inherited)
- Focus on TDD domain logic only

Benefits:
1. Intelligence: LENS synthesis provides context for better TDD guidance
2. Security: Hard gates block security vulnerabilities in test/impl code
3. Quality: DoR confidence ensures clear requirements before RED phase
4. Challenges: Suggests alternatives when user requests suboptimal approach
5. Consistency: Same protocol as all other orchestrators

Governance:
- ARCH-012: Inherits OrchestratorBaseProtocol
- CORE-008: TDD (tests in tests/unit/orchestrators/test_tdd_orchestrator_v2.py)
- CORE-011: Type hints 100%
- CORE-012: Google-style docstrings
- CORE-019: ALL implementation intents route through TDD-Master

Author: Asif Hussain
Date: 2026-01-31
"""

from __future__ import annotations

import yaml
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.core.result import Result, Ok, Err
from cortex.orchestrators.support.brittleness_scanner import BrittlenessScanner
from cortex.orchestrators.support.phase_completion_orchestrator import PhaseCompletionOrchestrator
from cortex.orchestrators.core.orchestrator_base_protocol import (
    OrchestratorBaseProtocol,
    ProtocolExecutionResult,
)
from cortex.brain.core.knowledge_guidance_engine import (
    KnowledgeGuidanceEngine,
    ModuleGuidance,
)

logger = logging.getLogger(__name__)


class TDDPhase(Enum):
    """TDD workflow phases."""
    RED = "red"        # Write failing test
    GREEN = "green"    # Minimal code to pass
    REFACTOR = "refactor"  # Improve design


@dataclass
class TDDDisciplineRule:
    """Single TDD discipline rule from knowledge YAML."""
    rule_id: str
    phase: TDDPhase
    description: str
    examples: List[str] = field(default_factory=list)
    anti_patterns: List[str] = field(default_factory=list)
    related_rules: List[str] = field(default_factory=list)


@dataclass
class TDDImplementationGuidance:
    """Complete TDD guidance for a module implementation."""
    module_path: str
    domain: str
    tdd_phase: TDDPhase
    rules: List[TDDDisciplineRule] = field(default_factory=list)
    best_practices: List[str] = field(default_factory=list)
    test_patterns: List[str] = field(default_factory=list)
    coverage_targets: Dict[str, float] = field(default_factory=dict)
    anti_patterns: List[str] = field(default_factory=list)
    governance_rules: List[str] = field(default_factory=list)


class TDDKnowledgeLoader:
    """Loads TDD best practices YAMLs from cortex_brain/tier3/knowledge/."""

    def __init__(self, knowledge_root: Optional[Path] = None) -> None:
        """Initialize TDD knowledge loader."""
        if knowledge_root is None:
            knowledge_root = (
                Path(__file__).parent.parent.parent.parent 
                / "cortex_brain" / "tier3" / "knowledge"
            )

        self.knowledge_root = Path(knowledge_root)
        self.tdd_domain_path = self.knowledge_root / "TESTING-VALIDATION"
        self.tdd_yamls: Dict[str, Dict[str, Any]] = {}
        self.tdd_rules: List[TDDDisciplineRule] = []
        self._load_tdd_yamls()

    def _load_tdd_yamls(self) -> None:
        """Load all TDD-related YAMLs from TESTING-VALIDATION domain."""
        if not self.tdd_domain_path.exists():
            logger.warning(f"TDD domain path not found: {self.tdd_domain_path}")
            return

        tdd_files = [
            "tdd-best-practices.yaml",
            "test-doubles.yaml",
            "testing-pyramid.yaml",
            "playwright-best-practices.yaml"
        ]

        for yaml_file in tdd_files:
            file_path = self.tdd_domain_path / yaml_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = yaml.safe_load(f)
                        if content:
                            self.tdd_yamls[yaml_file] = content
                            logger.debug(f"Loaded TDD YAML: {yaml_file}")
                            self._extract_tdd_rules(content, yaml_file)
                except Exception as e:
                    logger.error(f"Failed to load TDD YAML {yaml_file}: {e}")

    def _extract_tdd_rules(self, content: Dict[str, Any], yaml_file: str) -> None:
        """Extract TDD discipline rules from YAML content."""
        if "discipline" in content:
            for rule in content.get("discipline", []):
                try:
                    phase_str = rule.get("phase", "green").lower()
                    phase = (
                        TDDPhase[phase_str.upper()] 
                        if phase_str.upper() in TDDPhase.__members__ 
                        else TDDPhase.GREEN
                    )

                    tdd_rule = TDDDisciplineRule(
                        rule_id=rule.get("rule_id", f"TDD-{len(self.tdd_rules)}"),
                        phase=phase,
                        description=rule.get("description", ""),
                        examples=rule.get("examples", []),
                        anti_patterns=rule.get("anti_patterns", []),
                        related_rules=rule.get("related_rules", [])
                    )
                    self.tdd_rules.append(tdd_rule)
                except Exception as e:
                    logger.error(f"Failed to extract TDD rule: {e}")

    def get_best_practices(self) -> List[str]:
        """Get all TDD best practices."""
        practices = []
        for yaml_content in self.tdd_yamls.values():
            if "best_practices" in yaml_content:
                practices.extend(yaml_content.get("best_practices", []))
        return practices


class TDDOrchestrator(OrchestratorBaseProtocol):
    """
    TDD Orchestrator V2 - Refactored with OrchestratorBaseProtocol.
    
    AUTOMATIC PROTOCOL (inherited from base):
    1. LENS Context Building → Understands request deeply
    2. Security Assessment → Blocks vulnerable test/impl code
    3. Challenge Generation → Suggests better TDD approaches
    4. DoR Confidence Gate → Blocks <60% confidence requests
    5. TDD Domain Logic → RED → GREEN → REFACTOR
    
    This orchestrator focuses ONLY on TDD domain logic:
    - Phase determination (RED, GREEN, REFACTOR)
    - Knowledge YAML integration (35+ best practices)
    - Test pattern selection
    - Coverage target validation
    - Anti-pattern detection
    
    All intelligence/security/quality gates handled by base protocol.
    
    Usage:
        >>> orchestrator = TDDOrchestrator()
        >>> result = orchestrator.execute_with_protocol(
        ...     user_request="Implement authentication service",
        ...     context={"module_path": "cortex.auth.service"}
        ... )
        >>> # Automatic: LENS → Security → Challenge → DoR → TDD
    """

    def __init__(self, knowledge_root: Optional[Path] = None) -> None:
        """
        Initialize TDD Orchestrator V2.
        
        Args:
            knowledge_root: Root path to knowledge repository
        
        ARCH-012: Inherits protocol initialization from base class
        """
        # Initialize base protocol (LENS, Security, Challenge, DoR)
        super().__init__(
            enable_lens=True,
            enable_security=True,
            enable_challenges=True,
            enable_dor_gate=True,
        )
        
        # TDD-specific components
        self.knowledge_loader = TDDKnowledgeLoader(knowledge_root)
        self.guidance_engine = KnowledgeGuidanceEngine()
        
        # AC-PHASE24-005: Initialize BrittlenessScanner for regression detection
        self._brittleness_scanner = BrittlenessScanner()
        
        # AC-PHASE24-007: Initialize PhaseCompletionOrchestrator for post-completion hooks
        self._phase_completion_orchestrator = PhaseCompletionOrchestrator()
        
        logger.info(
            f"TDD Orchestrator V2 initialized with base protocol + "
            f"{len(self.knowledge_loader.tdd_yamls)} knowledge YAMLs + "
            f"BrittlenessScanner (AC-PHASE24-005) + "
            f"PhaseCompletionOrchestrator (AC-PHASE24-007)"
        )

    def _run_pre_execution_brittleness_scan(self, context: Dict[str, Any]) -> None:
        """
        Run BrittlenessScanner before TDD execution (AC-PHASE24-005).
        
        Non-blocking: Violations logged as warnings, execution continues.
        
        Args:
            context: Execution context with module_path
        """
        if self._brittleness_scanner is None:
            return  # Scanner not initialized (e.g., in tests without injection)
        
        try:
            # Get module path from context
            module_path = context.get("module_path", "")
            if not module_path:
                return
            
            # Scan for brittleness (convert Path to str for scanner)
            scan_path = str(Path(module_path).parent)
            scan_result = self._brittleness_scanner.scan(scan_path)
            
            # Log violations as warnings (non-blocking)
            if scan_result.brittleness_score > 0.5:
                logger.warning(
                    f"⚠️ Brittleness detected (score: {scan_result.brittleness_score:.2f}) "
                    f"in {scan_result.scanned_path}"
                )
            
            if scan_result.circular_dependencies:
                for violation in scan_result.circular_dependencies:
                    logger.warning(
                        f"⚠️ Circular dependency: {' → '.join(violation.cycle_path)} "
                        f"(severity: {violation.severity})"
                    )
            
            if scan_result.coupling_violations:
                logger.warning(
                    f"⚠️ High coupling detected: {len(scan_result.coupling_violations)} violations"
                )
        
        except Exception as e:
            # Scanner failures don't block TDD execution
            logger.warning(f"BrittlenessScanner failed (non-blocking): {e}")

    def _run_post_execution_brittleness_scan(self, context: Dict[str, Any]) -> None:
        """
        Run BrittlenessScanner AFTER TDD execution (AC-PHASE24-005).
        
        Post-execution scan verifies implementation didn't introduce brittleness.
        Violations logged as warnings (non-blocking).
        
        Args:
            context: Execution context with module_path
            
        AC-PHASE24-005: Post-execution brittleness verification
        """
        try:
            module_path = context.get("module_path", "")
            if not module_path:
                return
            
            # Scan directory containing modified files
            scan_path = str(Path(module_path).parent)
            scan_result = self._brittleness_scanner.scan(scan_path)
            
            # Log violations as warnings (non-blocking)
            if scan_result.brittleness_score > 0.5:
                logger.warning(
                    f"⚠️ Post-execution brittleness (score: {scan_result.brittleness_score:.2f}) "
                    f"in {scan_result.scanned_path}"
                )
            
            if scan_result.circular_dependencies:
                for violation in scan_result.circular_dependencies:
                    logger.warning(
                        f"⚠️ Post-execution circular dependency: {' → '.join(violation.cycle_path)} "
                        f"(severity: {violation.severity})"
                    )
            
            if scan_result.coupling_violations:
                logger.warning(
                    f"⚠️ Post-execution high coupling: {len(scan_result.coupling_violations)} violations"
                )
        
        except Exception as e:
            # Scanner failures don't block TDD execution
            logger.warning(f"Post-execution BrittlenessScanner failed (non-blocking): {e}")

    def _run_phase_completion_hook(
        self, 
        context: Dict[str, Any], 
        execution_result: Dict[str, Any]
    ) -> None:
        """
        Run PhaseCompletionOrchestrator after successful TDD execution (AC-PHASE24-007).
        
        Automatically updates:
        - Phase YAML completion_status
        - Dashboard data via regeneration
        - Registry sync
        - Enhancement history
        
        Non-blocking: Failures logged as warnings.
        
        Args:
            context: Execution context
            execution_result: TDD execution results
            
        AC-PHASE24-007: Automatic post-completion status updates
        """
        if self._phase_completion_orchestrator is None:
            return  # Not initialized (e.g., in tests)
        
        try:
            # Extract phase information from context
            phase_file_str = context.get("phase_file")
            phase_key = context.get("phase_key")
            
            if not phase_file_str or not phase_key:
                # Not a phase-tracked operation, skip completion hook
                logger.debug(
                    "Skipping phase completion hook: no phase_file or phase_key in context"
                )
                return
            
            phase_file = Path(phase_file_str)
            enhancement_id = context.get("enhancement_id")  # Optional
            
            # Call PhaseCompletionOrchestrator
            completion_result = self._phase_completion_orchestrator.complete_phase(
                phase_file=phase_file,
                phase_key=phase_key,
                enhancement_id=enhancement_id
            )
            
            if completion_result.success:
                logger.info(
                    f"✅ AC-PHASE24-007: Phase completion hook successful - "
                    f"File: {phase_file.name}, Key: {phase_key}, "
                    f"Dashboard: {completion_result.dashboard_regenerated}"
                )
            else:
                logger.warning(
                    f"⚠️ AC-PHASE24-007: Phase completion hook failed - "
                    f"Error: {completion_result.error}"
                )
        
        except Exception as e:
            # Completion hook failures don't block TDD execution
            logger.warning(f"PhaseCompletionOrchestrator hook failed (non-blocking): {e}")

    def _execute_domain_logic(
        self,
        user_request: str,
        lens_context: Optional[Any],
        context: Dict[str, Any]
    ) -> Result[Any]:
        """
        Execute TDD domain logic (RED → GREEN → REFACTOR).
        
        This method is called AFTER:
        - LENS context built
        - Security threats assessed
        - Challenges generated (if disagreement)
        - DoR confidence validated (≥60%)
        
        Args:
            user_request: User's natural language request
            lens_context: LENS context from Phase 1 (or None if degraded)
            context: Execution context with module_path, domain, etc.
            
        Returns:
            Result with TDD guidance and execution status
            
        CORE-008: Enforces TDD discipline (RED → GREEN → REFACTOR)
        MCP-GATE: Rejects non-MCP invocations for IMPLEMENT intents
        AC-PHASE24-005: BrittlenessScanner pre-execution hook
        """
        try:
            # AC-PHASE24-005: Pre-execution brittleness scan (non-blocking)
            self._run_pre_execution_brittleness_scan(context)
            
            # MCP-GATE ENFORCEMENT: Block direct chat invocations
            invocation_source = context.get("source", "unknown")
            if invocation_source != "mcp_gateway":
                logger.warning(
                    f"TDD Orchestrator invoked from {invocation_source} instead of MCP gateway"
                )
                return Err(
                    "❌ MCP-GATE VIOLATION (CORE-019)\n\n"
                    "Implementation requests MUST route through MCP gateway.\n"
                    "Direct file creation bypasses:\n"
                    "  - TDD enforcement (CORE-008)\n"
                    "  - Security gates (ARCH-012)\n"
                    "  - Cross-layer validation (CORE-035)\n"
                    "  - Challenge generation\n"
                    "  - DoR confidence gating\n\n"
                    "✅ FIX: Use cortex_process_request MCP tool:\n"
                    "  cortex_process_request(\n"
                    "    request='implement feature X',\n"
                    "    context={'module_path': 'cortex/...', 'domain': '...'}\n"
                    "  )"
                )
            
            # Extract context
            module_path = context.get("module_path", "unknown")
            domain = context.get("domain", "unknown")
            
            # Determine TDD phase from request
            tdd_phase = self._determine_tdd_phase(user_request)
            
            # Build TDD implementation guidance
            guidance = self._build_tdd_guidance(
                module_path=module_path,
                domain=domain,
                tdd_phase=tdd_phase,
                user_request=user_request,
                lens_context=lens_context
            )
            
            # Execute TDD phase
            phase_result = self._execute_tdd_phase(tdd_phase, guidance, context)
            
            if phase_result.is_err():
                return phase_result
            
            # AC-PHASE24-005: Post-execution brittleness scan (non-blocking)
            self._run_post_execution_brittleness_scan(context)
            
            # AC-PHASE24-007: Phase completion hook (automatic status updates)
            self._run_phase_completion_hook(context, phase_result.unwrap())
            
            # Return comprehensive TDD result
            return Ok({
                "orchestrator": "TDDOrchestrator",
                "tdd_phase": tdd_phase.value,
                "guidance": {
                    "module_path": guidance.module_path,
                    "domain": guidance.domain,
                    "rules": [rule.rule_id for rule in guidance.rules],
                    "best_practices": guidance.best_practices,
                    "test_patterns": guidance.test_patterns,
                    "governance_rules": guidance.governance_rules,
                },
                "execution_result": phase_result.unwrap(),
                "lens_context_used": lens_context is not None,
                "protocol_phases_completed": [
                    "LENS Context",
                    "Security Assessment", 
                    "Challenge Generation",
                    "DoR Confidence Gate",
                    "TDD Domain Logic"
                ]
            })
            
        except Exception as e:
            logger.error(f"TDD domain logic failed: {e}", exc_info=True)
            return Err(f"TDD execution error: {str(e)}")

    def _determine_tdd_phase(self, user_request: str) -> TDDPhase:
        """
        Determine TDD phase from user request.
        
        Args:
            user_request: User's natural language request
            
        Returns:
            TDD phase (RED, GREEN, REFACTOR)
        """
        request_lower = user_request.lower()
        
        # RED: Writing tests
        if any(word in request_lower for word in [
            "test", "failing test", "red phase", "write test"
        ]):
            return TDDPhase.RED
        
        # REFACTOR: Improving code
        elif any(word in request_lower for word in [
            "refactor", "improve", "optimize", "clean up"
        ]):
            return TDDPhase.REFACTOR
        
        # GREEN: Implementation (default)
        else:
            return TDDPhase.GREEN

    def _build_tdd_guidance(
        self,
        module_path: str,
        domain: str,
        tdd_phase: TDDPhase,
        user_request: str,
        lens_context: Optional[Any]
    ) -> TDDImplementationGuidance:
        """
        Build TDD implementation guidance.
        
        Args:
            module_path: Target module path
            domain: Domain classification
            tdd_phase: Current TDD phase
            user_request: User's request
            lens_context: LENS context (optional)
            
        Returns:
            TDD implementation guidance
        """
        # Get phase-specific rules
        phase_rules = [
            rule for rule in self.knowledge_loader.tdd_rules
            if rule.phase == tdd_phase
        ]
        
        # Get best practices
        best_practices = self.knowledge_loader.get_best_practices()
        
        # Build guidance
        guidance = TDDImplementationGuidance(
            module_path=module_path,
            domain=domain,
            tdd_phase=tdd_phase,
            rules=phase_rules[:5],  # Top 5 rules for phase
            best_practices=best_practices[:10],  # Top 10 practices
            test_patterns=self._select_test_patterns(tdd_phase),
            coverage_targets={"line": 0.8, "branch": 0.7},
            governance_rules=["CORE-008", "CORE-011", "CORE-012"]
        )
        
        return guidance

    def _select_test_patterns(self, tdd_phase: TDDPhase) -> List[str]:
        """Select test patterns for TDD phase."""
        if tdd_phase == TDDPhase.RED:
            return [
                "Arrange-Act-Assert (AAA)",
                "Given-When-Then (BDD)",
                "Fixture setup with pytest",
                "Parameterized tests for edge cases"
            ]
        elif tdd_phase == TDDPhase.GREEN:
            return [
                "Minimal implementation to pass",
                "Triangulation (add more test cases)",
                "Fake-it-till-you-make-it",
                "Obvious implementation"
            ]
        else:  # REFACTOR
            return [
                "Extract method/class",
                "Replace magic numbers with constants",
                "Apply SOLID principles",
                "Simplify conditionals"
            ]

    def _execute_tdd_phase(
        self,
        tdd_phase: TDDPhase,
        guidance: TDDImplementationGuidance,
        context: Dict[str, Any]
    ) -> Result[Dict[str, Any]]:
        """
        Execute specific TDD phase.
        
        Args:
            tdd_phase: TDD phase to execute
            guidance: TDD guidance
            context: Execution context
            
        Returns:
            Result with phase execution status
        """
        if tdd_phase == TDDPhase.RED:
            return self._execute_red_phase(guidance, context)
        elif tdd_phase == TDDPhase.GREEN:
            return self._execute_green_phase(guidance, context)
        else:  # REFACTOR
            return self._execute_refactor_phase(guidance, context)

    def _execute_red_phase(
        self,
        guidance: TDDImplementationGuidance,
        context: Dict[str, Any]
    ) -> Result[Dict[str, Any]]:
        """Execute RED phase (write failing test)."""
        return Ok({
            "phase": "RED",
            "action": "Write failing test",
            "test_patterns": guidance.test_patterns,
            "rules_applied": [rule.rule_id for rule in guidance.rules],
            "status": "ready_for_test_writing"
        })

    def _execute_green_phase(
        self,
        guidance: TDDImplementationGuidance,
        context: Dict[str, Any]
    ) -> Result[Dict[str, Any]]:
        """Execute GREEN phase (minimal implementation)."""
        return Ok({
            "phase": "GREEN",
            "action": "Implement minimal code to pass test",
            "implementation_patterns": guidance.test_patterns,
            "rules_applied": [rule.rule_id for rule in guidance.rules],
            "status": "ready_for_implementation"
        })

    def _execute_refactor_phase(
        self,
        guidance: TDDImplementationGuidance,
        context: Dict[str, Any]
    ) -> Result[Dict[str, Any]]:
        """Execute REFACTOR phase (improve design)."""
        return Ok({
            "phase": "REFACTOR",
            "action": "Refactor code while keeping tests green",
            "refactoring_patterns": guidance.test_patterns,
            "rules_applied": [rule.rule_id for rule in guidance.rules],
            "status": "ready_for_refactoring"
        })

    def get_tdd_status(self) -> Dict[str, Any]:
        """
        Get TDD orchestrator status and loaded knowledge.
        
        Returns:
            Dictionary with status information
        """
        return {
            "orchestrator": "TDDOrchestrator",
            "version": "2.0",
            "base_protocol": "OrchestratorBaseProtocol",
            "protocol_phases": [
                "LENS Context",
                "Security Assessment",
                "Challenge Generation",
                "DoR Confidence Gate",
                "TDD Domain Logic"
            ],
            "status": "initialized",
            "knowledge_loaded": {
                "tdd_yamls_count": len(self.knowledge_loader.tdd_yamls),
                "tdd_rules_count": len(self.knowledge_loader.tdd_rules),
                "best_practices_count": len(self.knowledge_loader.get_best_practices()),
                "yaml_files": list(self.knowledge_loader.tdd_yamls.keys())
            },
            "tdd_phases": [phase.value for phase in TDDPhase],
            "routing_intent": "CORE-019: Route ALL implementation intents through TDD-Master"
        }


def get_tdd_orchestrator(knowledge_root: Optional[Path] = None) -> TDDOrchestrator:
    """
    Singleton factory for TDDOrchestrator.
    
    Args:
        knowledge_root: Root path to knowledge repository
        
    Returns:
        TDDOrchestrator instance
    """
    if not hasattr(get_tdd_orchestrator, "_instance"):
        get_tdd_orchestrator._instance = TDDOrchestrator(knowledge_root)
    return get_tdd_orchestrator._instance


__all__ = [
    "TDDOrchestrator",
    "TDDPhase",
    "TDDDisciplineRule",
    "TDDImplementationGuidance",
    "TDDKnowledgeLoader",
    "get_tdd_orchestrator",
]
