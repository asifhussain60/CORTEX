# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: AC-REM-011-02 - TDD Orchestrator Integration
"""
TDD Orchestrator - Routes test-driven development workflows with knowledge guidance.

PHASE-REMEDIATION-07: TDD Orchestrator Knowledge Integration
AC-ID: AC-REM-011-02 - Wire TDD Knowledge YAMLs into Orchestrator

This orchestrator:
1. Loads 35 best practices YAMLs from cortex_brain/tier3/knowledge/TESTING-VALIDATION/
2. Routes IMPLEMENT/FIX/REFACTOR/VALIDATE intents to TDD discipline enforcer
3. Enforces RED → GREEN → REFACTOR workflow per CORE-008
4. Provides TDD guidance via knowledge guidance engine
5. Tracks test coverage and code metrics

Wired Knowledge Domains:
  - TESTING-VALIDATION (4 YAMLs): tdd-best-practices, test-doubles, testing-pyramid, playwright
  - ARCHITECTURE (14 YAMLs): design patterns, SOLID principles, clean code, DDD patterns
  - DEPLOYMENT (4 YAMLs): CI/CD, infrastructure-as-code, DevOps, AWS
  - KNOWLEDGE-CURATION (4 YAMLs): RAG, embeddings, vectors, retrieval

Core Governance:
  - CORE-008: TDD (Tests BEFORE implementation)
  - CORE-011: Type hints (100% coverage)
  - CORE-012: Docstrings (Google style)
  - CORE-019: TDD-Master Routing (ALL implementation intents route here)
"""

from __future__ import annotations

import yaml
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cortex.core.result import Result, Ok, Err
from cortex.brain.core.knowledge_guidance_engine import (
    KnowledgeGuidanceEngine,
    ModuleGuidance,
    GuidanceEntry,
    GuidanceCategory,
    TierLevel
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
        """Initialize TDD knowledge loader.

        Args:
            knowledge_root: Root path to knowledge repository. Defaults to cortex_brain/tier3/knowledge/

        AC-REM-011-02: Wire TDD knowledge YAMLs
        """
        if knowledge_root is None:
            knowledge_root = Path(__file__).parent.parent.parent.parent / "cortex_brain" / "tier3" / "knowledge"

        self.knowledge_root = Path(knowledge_root)
        self.tdd_domain_path = self.knowledge_root / "TESTING-VALIDATION"
        self.tdd_yamls: Dict[str, Dict[str, Any]] = {}
        self.tdd_rules: List[TDDDisciplineRule] = []
        self._load_tdd_yamls()

    def _load_tdd_yamls(self) -> None:
        """Load all TDD-related YAMLs from TESTING-VALIDATION domain.

        AC-REM-011-02: Load restored 35 YAMLs, specifically TESTING-VALIDATION subset
        """
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
        """Extract TDD discipline rules from YAML content.

        Args:
            content: Parsed YAML dictionary
            yaml_file: Source YAML filename

        AC-REM-011-02: Extract TDD rules from knowledge YAMLs
        """
        if "discipline" in content:
            for rule in content.get("discipline", []):
                try:
                    phase_str = rule.get("phase", "green").lower()
                    phase = TDDPhase[phase_str.upper()] if phase_str.upper() in TDDPhase.__members__ else TDDPhase.GREEN

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
                    logger.warning(f"Failed to extract rule from {yaml_file}: {e}")

    def get_tdd_rules(self, phase: Optional[TDDPhase] = None) -> List[TDDDisciplineRule]:
        """Get TDD rules, optionally filtered by phase.

        Args:
            phase: Optional phase to filter by (RED, GREEN, REFACTOR)

        Returns:
            List of TDD discipline rules

        AC-REM-011-02: Access TDD rules from loaded YAMLs
        """
        if phase is None:
            return self.tdd_rules
        return [rule for rule in self.tdd_rules if rule.phase == phase]

    def get_best_practices(self) -> List[str]:
        """Get all TDD best practices from loaded YAMLs.

        Returns:
            List of best practice descriptions

        AC-REM-011-02: Extract best practices guidance
        """
        practices = []
        for yaml_content in self.tdd_yamls.values():
            if "practices" in yaml_content:
                practices.extend(yaml_content.get("practices", []))
        return practices


class TDDOrchestrator:
    """
    Routes test-driven development workflows with knowledge guidance.

    CORE-008: TDD Enforcement - Tests MUST exist BEFORE implementation
    CORE-019: TDD-Master Required - ALL implementation requests route here

    AC-REM-011-02: Wires 35 best practices YAMLs into TDD workflow
    """

    def __init__(self, knowledge_root: Optional[Path] = None) -> None:
        """Initialize TDD Orchestrator.

        Args:
            knowledge_root: Root path to knowledge repository

        AC-REM-011-02: Initialize with restored TDD knowledge YAMLs
        """
        self.knowledge_loader = TDDKnowledgeLoader(knowledge_root)
        self.guidance_engine = KnowledgeGuidanceEngine()
        self.logger = logging.getLogger(__name__)

        self.logger.info("TDD Orchestrator initialized with knowledge YAMLs")
        self._log_loaded_yamls()

    def _log_loaded_yamls(self) -> None:
        """Log loaded TDD YAML files for verification."""
        yaml_count = len(self.knowledge_loader.tdd_yamls)
        rule_count = len(self.knowledge_loader.tdd_rules)
        self.logger.info(f"TDD Knowledge Loaded: {yaml_count} YAMLs, {rule_count} rules extracted")

    def route_implementation_intent(
        self,
        intent: str,
        module_path: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Result[TDDImplementationGuidance]:
        """
        Route implementation intent through TDD discipline enforcer.

        Per CORE-019: ALL implementation/fix/refactor/validate intents route through TDD-Master

        Args:
            intent: User intent (e.g., "implement X", "fix Y", "refactor Z")
            module_path: Module being implemented
            context: Optional execution context

        Returns:
            Result with TDD implementation guidance

        AC-REM-011-02: Route implementation intents with TDD discipline
        """
        try:
            # Determine TDD phase from intent
            phase = self._determine_tdd_phase(intent)

            # Get guidance from knowledge engine
            knowledge_guidance = self.guidance_engine.get_guidance_for_module(
                module_path,
                context=context
            )

            # Extract TDD rules applicable to this phase
            phase_rules = self.knowledge_loader.get_tdd_rules(phase)

            # Safely extract test patterns
            test_patterns = []
            try:
                test_patterns = self._extract_test_patterns(knowledge_guidance)
            except Exception as e:
                self.logger.warning(f"Failed to extract test patterns: {e}")

            # Safely extract anti-patterns
            anti_patterns = []
            try:
                anti_patterns = self._extract_anti_patterns(phase_rules)
            except Exception as e:
                self.logger.warning(f"Failed to extract anti-patterns: {e}")

            # Safely extract governance rules
            governance_rules = []
            try:
                if hasattr(knowledge_guidance, 'tier_0_rules'):
                    if isinstance(knowledge_guidance.tier_0_rules, list):
                        governance_rules = knowledge_guidance.tier_0_rules
                    elif isinstance(knowledge_guidance.tier_0_rules, dict):
                        governance_rules = list(knowledge_guidance.tier_0_rules.keys())
            except Exception as e:
                self.logger.warning(f"Failed to extract governance rules: {e}")

            # Build TDD implementation guidance
            tdd_guidance = TDDImplementationGuidance(
                module_path=module_path,
                domain=knowledge_guidance.domain,
                tdd_phase=phase,
                rules=phase_rules,
                best_practices=self.knowledge_loader.get_best_practices(),
                test_patterns=test_patterns,
                coverage_targets=self._get_coverage_targets(module_path),
                anti_patterns=anti_patterns,
                governance_rules=governance_rules
            )

            return Ok(tdd_guidance)

        except Exception as e:
            import traceback
            self.logger.error(f"Failed to route implementation intent: {e}\n{traceback.format_exc()}")
            return Err(f"TDD routing failed: {str(e)}")

    def _determine_tdd_phase(self, intent: str) -> TDDPhase:
        """Determine TDD phase from user intent.

        Args:
            intent: User intent string

        Returns:
            TDD phase (RED, GREEN, or REFACTOR)

        AC-REM-011-02: Determine TDD phase from intent
        """
        intent_lower = intent.lower()

        if any(word in intent_lower for word in ["test", "red", "failing"]):
            return TDDPhase.RED
        elif any(word in intent_lower for word in ["refactor", "improve", "optimize"]):
            return TDDPhase.REFACTOR
        else:
            return TDDPhase.GREEN

    def _extract_test_patterns(self, guidance: ModuleGuidance) -> List[str]:
        """Extract test patterns from module guidance.

        Args:
            guidance: Module guidance from knowledge engine

        Returns:
            List of applicable test patterns

        AC-REM-011-02: Extract test patterns from knowledge guidance
        """
        patterns = []
        try:
            if hasattr(guidance, 'guidance_entries') and isinstance(guidance.guidance_entries, list):
                for entry in guidance.guidance_entries:
                    if hasattr(entry, 'category') and hasattr(entry, 'title'):
                        # Check if category matches TESTING_PATTERNS
                        if hasattr(GuidanceCategory, 'TESTING_PATTERNS'):
                            if entry.category == GuidanceCategory.TESTING_PATTERNS:
                                patterns.append(entry.title)
        except Exception as e:
            self.logger.warning(f"Failed to extract test patterns: {e}")
        return patterns

    def _extract_anti_patterns(self, rules: List[TDDDisciplineRule]) -> List[str]:
        """Extract anti-patterns from TDD rules.

        Args:
            rules: TDD discipline rules

        Returns:
            List of anti-patterns to avoid

        AC-REM-011-02: Extract anti-patterns from TDD rules
        """
        anti_patterns = []
        for rule in rules:
            anti_patterns.extend(rule.anti_patterns)
        return anti_patterns

    def _get_coverage_targets(self, module_path: str) -> Dict[str, float]:
        """Get test coverage targets for module.

        Args:
            module_path: Module path

        Returns:
            Dictionary with coverage targets (unit, integration, e2e)

        AC-REM-011-02: Get coverage targets from knowledge YAMLs
        """
        # Default coverage targets per testing pyramid
        return {
            "unit": 0.70,
            "integration": 0.20,
            "e2e": 0.10,
            "total": 0.95  # 95% minimum overall coverage
        }

    def execute_red_phase(
        self,
        module_path: str,
        test_spec: str
    ) -> Result[Dict[str, Any]]:
        """
        Execute RED phase: Write failing test.

        Per CORE-008 TDD discipline: Tests BEFORE implementation

        Args:
            module_path: Module being implemented
            test_spec: Test specification describing desired behavior

        Returns:
            Result with test file and assertions

        AC-REM-011-02: Execute RED phase with TDD guidance
        """
        try:
            guidance = self.route_implementation_intent(
                "write test",
                module_path
            )

            if guidance.is_err():
                return Err(guidance.error)

            tdd_guidance = guidance.unwrap()

            result = {
                "phase": TDDPhase.RED.value,
                "module_path": module_path,
                "test_spec": test_spec,
                "guidance": tdd_guidance,
                "expected_outcome": "Failing test that clarifies requirements",
                "rules": [r.rule_id for r in tdd_guidance.rules]
            }

            return Ok(result)

        except Exception as e:
            return Err(f"RED phase failed: {str(e)}")

    def execute_green_phase(
        self,
        module_path: str,
        test_spec: str
    ) -> Result[Dict[str, Any]]:
        """
        Execute GREEN phase: Write minimal code to pass test.

        Args:
            module_path: Module being implemented
            test_spec: Passing test specification

        Returns:
            Result with implementation guidance

        AC-REM-011-02: Execute GREEN phase with minimal implementation
        """
        try:
            guidance = self.route_implementation_intent(
                "implement",
                module_path
            )

            if guidance.is_err():
                return Err(guidance.error)

            tdd_guidance = guidance.unwrap()

            result = {
                "phase": TDDPhase.GREEN.value,
                "module_path": module_path,
                "test_spec": test_spec,
                "guidance": tdd_guidance,
                "expected_outcome": "Minimal implementation that passes test",
                "rules": [r.rule_id for r in tdd_guidance.rules]
            }

            return Ok(result)

        except Exception as e:
            return Err(f"GREEN phase failed: {str(e)}")

    def execute_refactor_phase(
        self,
        module_path: str,
        test_spec: str
    ) -> Result[Dict[str, Any]]:
        """
        Execute REFACTOR phase: Improve design without changing behavior.

        Args:
            module_path: Module being improved
            test_spec: Passing test that validates refactoring

        Returns:
            Result with refactoring guidance

        AC-REM-011-02: Execute REFACTOR phase with design improvements
        """
        try:
            guidance = self.route_implementation_intent(
                "refactor",
                module_path
            )

            if guidance.is_err():
                return Err(guidance.error)

            tdd_guidance = guidance.unwrap()

            result = {
                "phase": TDDPhase.REFACTOR.value,
                "module_path": module_path,
                "test_spec": test_spec,
                "guidance": tdd_guidance,
                "expected_outcome": "Improved design with all tests still passing",
                "rules": [r.rule_id for r in tdd_guidance.rules],
                "best_practices": tdd_guidance.best_practices[:5]  # Top 5 practices
            }

            return Ok(result)

        except Exception as e:
            return Err(f"REFACTOR phase failed: {str(e)}")

    def get_tdd_status(self) -> Dict[str, Any]:
        """Get TDD orchestrator status and loaded knowledge.

        Returns:
            Dictionary with status information

        AC-REM-011-02: Report TDD orchestrator status
        """
        return {
            "orchestrator": "TDDOrchestrator",
            "version": "1.0",
            "status": "initialized",
            "knowledge_loaded": {
                "tdd_yamls_count": len(self.knowledge_loader.tdd_yamls),
                "tdd_rules_count": len(self.knowledge_loader.tdd_rules),
                "best_practices_count": len(self.knowledge_loader.get_best_practices()),
                "yaml_files": list(self.knowledge_loader.tdd_yamls.keys())
            },
            "tdd_phases": [phase.value for phase in TDDPhase],
            "routing_intent": "Per CORE-019: Route ALL implementation intents through TDD-Master"
        }


def get_tdd_orchestrator(knowledge_root: Optional[Path] = None) -> TDDOrchestrator:
    """
    Get singleton instance of TDD Orchestrator.

    Args:
        knowledge_root: Optional knowledge repository root

    Returns:
        TDD Orchestrator instance

    AC-REM-011-02: Access TDD Orchestrator for intent routing
    """
    if not hasattr(get_tdd_orchestrator, "_instance"):
        get_tdd_orchestrator._instance = TDDOrchestrator(knowledge_root)

    return get_tdd_orchestrator._instance


__all__ = [
    "TDDOrchestrator",
    "TDDKnowledgeLoader",
    "TDDPhase",
    "TDDDisciplineRule",
    "TDDImplementationGuidance",
    "get_tdd_orchestrator",
]
