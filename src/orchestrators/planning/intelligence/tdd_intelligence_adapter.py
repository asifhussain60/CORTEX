"""
TDD Intelligence Adapter - TDD Workflow Enforcement for Planning System

Purpose: Enforces TDD workflow (RED→GREEN→REFACTOR), validates phase transitions,
and provides intelligent TDD recommendations for feature plans.

Version: 1.0.0
Author: CORTEX Development Team
Created: 2025-12-24 (Week 9 Day 1)

Responsibilities:
- TDD phase detection and validation (RED, GREEN, REFACTOR)
- Phase transition enforcement (must pass DoR/DoD)
- TDD workflow pattern learning
- TDD strategy recommendations
- Integration with TDD Orchestrator

Integration Points:
- Planning System: Injects TDD workflow into plans
- TDD Orchestrator: Validates phase completeness
- Brain Protection (Tier 0): Enforces TDD_ENFORCEMENT rule
- Knowledge Graph (Tier 2): Learns TDD patterns

Week 9 Target: 300 LOC
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class TDDPhase(Enum):
    """TDD workflow phases."""
    RED = "RED"  # Write failing tests
    GREEN = "GREEN"  # Implement minimal code to pass
    REFACTOR = "REFACTOR"  # Clean up while keeping tests green
    COMPLETE = "COMPLETE"  # Full cycle complete


@dataclass
class TDDPhaseStatus:
    """Status of a TDD phase."""
    phase: TDDPhase
    status: str  # not_started, in_progress, complete, failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_minutes: float = 0.0
    
    # Phase-specific metrics
    tests_written: int = 0
    tests_passing: int = 0
    tests_failing: int = 0
    code_complexity: int = 0
    
    # DoR/DoD validation
    dor_passed: bool = False
    dod_passed: bool = False
    validation_errors: List[str] = field(default_factory=list)


@dataclass
class TDDWorkflowValidation:
    """Results of TDD workflow validation."""
    is_valid: bool
    current_phase: TDDPhase
    phase_statuses: Dict[TDDPhase, TDDPhaseStatus]
    violations: List[str]
    recommendations: List[str]
    
    # Metrics
    total_duration_minutes: float = 0.0
    cycle_count: int = 0
    quality_score: float = 0.0  # 0-10


@dataclass
class TDDStrategy:
    """TDD strategy for feature implementation."""
    recommended: bool
    reasoning: List[str]
    estimated_cycles: int
    estimated_duration_minutes: float
    test_first_modules: List[str]
    implementation_order: List[str]


class TDDIntelligenceAdapter:
    """
    Adapter for TDD workflow intelligence within Planning System.
    
    Enforces TDD best practices, validates phase transitions, and provides
    intelligent recommendations for TDD workflow in feature plans.
    
    Usage:
        adapter = TDDIntelligenceAdapter(project_root)
        validation = adapter.validate_tdd_workflow(feature_context)
        strategy = adapter.generate_tdd_strategy(feature_scope)
        can_transition = adapter.can_transition_to_green(red_phase_status)
    """
    
    def __init__(self, project_root: Path, enforce_strict: bool = True):
        """
        Initialize TDD intelligence adapter.
        
        Args:
            project_root: Root of project
            enforce_strict: Enforce strict TDD rules (default: True)
        """
        self.project_root = Path(project_root)
        self.enforce_strict = enforce_strict
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Workflow state tracking
        self._current_workflow: Optional[Dict[str, Any]] = None
        self._phase_history: List[TDDPhaseStatus] = []
    
    # ========== Workflow Validation ==========
    
    def validate_tdd_workflow(
        self,
        feature_context: Dict[str, Any],
        current_phase: Optional[TDDPhase] = None
    ) -> TDDWorkflowValidation:
        """
        Validate TDD workflow compliance.
        
        Args:
            feature_context: Feature implementation context
            current_phase: Current TDD phase (None = detect automatically)
            
        Returns:
            Validation results with violations and recommendations
        """
        self.logger.info("Validating TDD workflow compliance")
        
        violations = []
        recommendations = []
        phase_statuses = {}
        
        # Detect current phase if not provided
        if current_phase is None:
            current_phase = self._detect_current_phase(feature_context)
        
        # Validate RED phase
        red_status = self._validate_red_phase(feature_context)
        phase_statuses[TDDPhase.RED] = red_status
        
        if not red_status.dod_passed:
            violations.extend(red_status.validation_errors)
            recommendations.append("Complete RED phase: All tests must fail before proceeding to GREEN")
        
        # Validate GREEN phase (if applicable)
        if current_phase in [TDDPhase.GREEN, TDDPhase.REFACTOR, TDDPhase.COMPLETE]:
            green_status = self._validate_green_phase(feature_context)
            phase_statuses[TDDPhase.GREEN] = green_status
            
            if not green_status.dod_passed:
                violations.extend(green_status.validation_errors)
                recommendations.append("Complete GREEN phase: Minimal code to pass all tests")
        
        # Validate REFACTOR phase (if applicable)
        if current_phase in [TDDPhase.REFACTOR, TDDPhase.COMPLETE]:
            refactor_status = self._validate_refactor_phase(feature_context)
            phase_statuses[TDDPhase.REFACTOR] = refactor_status
            
            if not refactor_status.dod_passed:
                violations.extend(refactor_status.validation_errors)
                recommendations.append("Complete REFACTOR phase: Clean code while keeping tests green")
        
        # Calculate metrics
        total_duration = sum(
            status.duration_minutes
            for status in phase_statuses.values()
            if status.duration_minutes > 0
        )
        
        cycle_count = len([s for s in phase_statuses.values() if s.status == "complete"])
        quality_score = self._calculate_quality_score(phase_statuses)
        
        is_valid = len(violations) == 0
        
        return TDDWorkflowValidation(
            is_valid=is_valid,
            current_phase=current_phase,
            phase_statuses=phase_statuses,
            violations=violations,
            recommendations=recommendations,
            total_duration_minutes=total_duration,
            cycle_count=cycle_count,
            quality_score=quality_score
        )
    
    def can_transition_to_phase(
        self,
        target_phase: TDDPhase,
        current_phase_status: TDDPhaseStatus
    ) -> Tuple[bool, List[str]]:
        """
        Check if can transition to next TDD phase.
        
        Args:
            target_phase: Phase to transition to
            current_phase_status: Status of current phase
            
        Returns:
            Tuple of (can_transition, blocking_issues)
        """
        blocking_issues = []
        
        # Check DoD for current phase
        if not current_phase_status.dod_passed:
            blocking_issues.extend(current_phase_status.validation_errors)
            blocking_issues.append(f"{current_phase_status.phase.value} phase DoD not satisfied")
        
        # Phase-specific transition rules
        if target_phase == TDDPhase.GREEN:
            # RED → GREEN: All tests must be failing
            if current_phase_status.tests_passing > 0:
                blocking_issues.append("Cannot transition to GREEN: Some tests already passing (violates RED phase)")
            
            if current_phase_status.tests_failing == 0:
                blocking_issues.append("Cannot transition to GREEN: No failing tests written")
        
        elif target_phase == TDDPhase.REFACTOR:
            # GREEN → REFACTOR: All tests must be passing
            if current_phase_status.tests_failing > 0:
                blocking_issues.append("Cannot transition to REFACTOR: Tests still failing")
            
            if current_phase_status.code_complexity > 20 and self.enforce_strict:
                blocking_issues.append("High complexity detected - refactor before proceeding")
        
        elif target_phase == TDDPhase.COMPLETE:
            # REFACTOR → COMPLETE: Tests still passing, complexity reduced
            if current_phase_status.tests_failing > 0:
                blocking_issues.append("Cannot complete: Tests failing after refactor")
            
            if current_phase_status.code_complexity > current_phase_status.tests_written * 3:
                blocking_issues.append("Code complexity too high relative to test coverage")
        
        can_transition = len(blocking_issues) == 0
        return can_transition, blocking_issues
    
    def generate_tdd_strategy(
        self,
        feature_scope: Dict[str, Any],
        complexity: str = "medium"
    ) -> TDDStrategy:
        """
        Generate intelligent TDD strategy for feature.
        
        Args:
            feature_scope: Feature information
            complexity: Feature complexity (low, medium, high)
            
        Returns:
            TDD strategy with recommendations
        """
        reasoning = []
        test_first_modules = []
        implementation_order = []
        
        files_affected = feature_scope.get("files_affected", [])
        has_api_changes = any("api" in str(f).lower() for f in files_affected)
        has_data_model_changes = any("model" in str(f).lower() for f in files_affected)
        
        # Determine if TDD is recommended
        tdd_recommended = True
        
        if complexity == "low" and len(files_affected) == 1:
            tdd_recommended = False
            reasoning.append("Simple single-file change - TDD optional")
        else:
            reasoning.append("TDD recommended for multi-file or complex changes")
        
        if has_api_changes:
            reasoning.append("API changes detected - TDD ensures contract compliance")
            test_first_modules.extend([f for f in files_affected if "api" in str(f).lower()])
        
        if has_data_model_changes:
            reasoning.append("Data model changes - TDD prevents data corruption")
            test_first_modules.extend([f for f in files_affected if "model" in str(f).lower()])
        
        # Determine implementation order (inside-out: models → services → API)
        for file_path in files_affected:
            file_str = str(file_path).lower()
            if "model" in file_str or "entity" in file_str:
                implementation_order.insert(0, str(file_path))  # First
            elif "service" in file_str or "logic" in file_str:
                implementation_order.insert(len(implementation_order) // 2, str(file_path))  # Middle
            elif "api" in file_str or "view" in file_str or "controller" in file_str:
                implementation_order.append(str(file_path))  # Last
            else:
                implementation_order.append(str(file_path))
        
        # Estimate cycles and duration
        estimated_cycles = max(1, len(files_affected))
        estimated_duration = estimated_cycles * self._estimate_cycle_duration(complexity)
        
        return TDDStrategy(
            recommended=tdd_recommended,
            reasoning=reasoning,
            estimated_cycles=estimated_cycles,
            estimated_duration_minutes=estimated_duration,
            test_first_modules=list(set(test_first_modules)),
            implementation_order=implementation_order
        )
    
    # ========== Phase Validation ==========
    
    def _validate_red_phase(self, context: Dict[str, Any]) -> TDDPhaseStatus:
        """Validate RED phase (write failing tests)."""
        status = TDDPhaseStatus(phase=TDDPhase.RED, status="not_started")
        
        test_files = context.get("test_files", [])
        test_results = context.get("test_results", {})
        
        if not test_files:
            status.validation_errors.append("No test files created")
            return status
        
        status.tests_written = test_results.get("total", 0)
        status.tests_failing = test_results.get("failed", 0)
        status.tests_passing = test_results.get("passed", 0)
        
        # RED phase DoD: Tests exist and ALL are failing
        if status.tests_written > 0:
            status.dor_passed = True
            status.status = "in_progress"
            
            if status.tests_failing == status.tests_written and status.tests_passing == 0:
                status.dod_passed = True
                status.status = "complete"
            else:
                status.validation_errors.append(
                    f"RED phase violation: {status.tests_passing} tests passing (expected: 0)"
                )
        else:
            status.validation_errors.append("No tests written in RED phase")
        
        return status
    
    def _validate_green_phase(self, context: Dict[str, Any]) -> TDDPhaseStatus:
        """Validate GREEN phase (minimal code to pass tests)."""
        status = TDDPhaseStatus(phase=TDDPhase.GREEN, status="not_started")
        
        implementation_files = context.get("implementation_files", [])
        test_results = context.get("test_results", {})
        
        if not implementation_files:
            status.validation_errors.append("No implementation files created")
            return status
        
        status.tests_written = test_results.get("total", 0)
        status.tests_passing = test_results.get("passed", 0)
        status.tests_failing = test_results.get("failed", 0)
        
        # GREEN phase DoD: All tests passing
        status.dor_passed = status.tests_failing > 0  # Must start with failing tests
        
        if status.tests_written > 0:
            status.status = "in_progress"
            
            if status.tests_passing == status.tests_written and status.tests_failing == 0:
                status.dod_passed = True
                status.status = "complete"
            else:
                status.validation_errors.append(
                    f"GREEN phase incomplete: {status.tests_failing} tests still failing"
                )
        
        return status
    
    def _validate_refactor_phase(self, context: Dict[str, Any]) -> TDDPhaseStatus:
        """Validate REFACTOR phase (clean code, keep tests green)."""
        status = TDDPhaseStatus(phase=TDDPhase.REFACTOR, status="not_started")
        
        test_results = context.get("test_results", {})
        code_quality = context.get("code_quality", {})
        
        status.tests_written = test_results.get("total", 0)
        status.tests_passing = test_results.get("passed", 0)
        status.tests_failing = test_results.get("failed", 0)
        status.code_complexity = code_quality.get("complexity", 0)
        
        # REFACTOR phase DoR: All tests passing from GREEN
        status.dor_passed = status.tests_passing == status.tests_written
        
        if status.dor_passed:
            status.status = "in_progress"
            
            # REFACTOR phase DoD: Tests still passing, complexity reduced
            if status.tests_failing == 0:
                if status.code_complexity < 15:  # Good complexity
                    status.dod_passed = True
                    status.status = "complete"
                else:
                    status.validation_errors.append(
                        f"REFACTOR incomplete: Complexity ({status.code_complexity}) still high"
                    )
            else:
                status.validation_errors.append("REFACTOR broke tests - tests now failing")
        
        return status
    
    # ========== Helpers ==========
    
    def _detect_current_phase(self, context: Dict[str, Any]) -> TDDPhase:
        """Detect current TDD phase from context."""
        test_results = context.get("test_results", {})
        implementation_files = context.get("implementation_files", [])
        
        tests_total = test_results.get("total", 0)
        tests_passing = test_results.get("passed", 0)
        tests_failing = test_results.get("failed", 0)
        
        if tests_total == 0:
            return TDDPhase.RED  # Need to write tests
        
        if tests_failing > 0 and not implementation_files:
            return TDDPhase.RED  # Tests exist and failing, no implementation
        
        if tests_failing > 0 and implementation_files:
            return TDDPhase.GREEN  # Working on implementation
        
        if tests_passing == tests_total:
            return TDDPhase.REFACTOR  # All tests passing, can refactor
        
        return TDDPhase.RED  # Default
    
    def _calculate_quality_score(self, phase_statuses: Dict[TDDPhase, TDDPhaseStatus]) -> float:
        """Calculate TDD workflow quality score (0-10)."""
        score = 10.0
        
        for phase, status in phase_statuses.items():
            # Deduct points for incomplete phases
            if not status.dod_passed:
                score -= 3.0
            
            # Deduct points for validation errors
            score -= len(status.validation_errors) * 0.5
            
            # Bonus for complete phases
            if status.status == "complete":
                score += 0.5
        
        return max(0.0, min(10.0, score))
    
    def _estimate_cycle_duration(self, complexity: str) -> float:
        """Estimate duration of one TDD cycle in minutes."""
        durations = {
            "low": 30.0,
            "medium": 60.0,
            "high": 120.0,
            "complex": 180.0
        }
        return durations.get(complexity, 60.0)
