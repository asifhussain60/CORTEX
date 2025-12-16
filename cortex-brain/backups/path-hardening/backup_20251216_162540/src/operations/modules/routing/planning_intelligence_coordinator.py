"""
Planning Intelligence Coordinator
Combines complexity analysis with test value scoring for intelligent planning decisions.

Purpose:
    Coordinates ComplexityAnalyzer (planning tier routing) with TestValueScorer
    (test necessity) to provide comprehensive planning recommendations.

Decision Matrix:
    HIGH Complexity + CRITICAL Test Value → Incremental + Full TDD
    HIGH Complexity + LOW Test Value → Incremental + Skip Tests
    LOW Complexity + CRITICAL Test Value → Skeleton + Targeted Tests
    LOW Complexity + LOW Test Value → Direct Execution + No Tests

Author: Asif Hussain
Date: December 2024
Version: 1.0.0
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.operations.modules.routing.complexity_analyzer import ComplexityAnalyzer, ComplexityScore, ComplexityTier
from src.operations.modules.testing.test_value_scorer import TestValueScorer, TestValueScore, TestValue

logger = logging.getLogger(__name__)


class PlanningMode(Enum):
    """Recommended planning execution mode"""
    INCREMENTAL_FULL_TDD = "incremental_full_tdd"          # High complexity + critical tests
    INCREMENTAL_TARGETED_TDD = "incremental_targeted_tdd"  # High complexity + some tests
    INCREMENTAL_NO_TDD = "incremental_no_tdd"              # High complexity + skip tests
    SKELETON_TARGETED_TDD = "skeleton_targeted_tdd"        # Low complexity + critical tests
    SKELETON_NO_TDD = "skeleton_no_tdd"                    # Low complexity + skip tests
    DIRECT_EXECUTION = "direct_execution"                  # Trivial - no planning needed


class TestStrategy(Enum):
    """Test generation strategy"""
    FULL_SUITE = "full_suite"          # RED→GREEN→REFACTOR with comprehensive tests
    TARGETED_TESTS = "targeted_tests"  # Tests for critical paths only
    SKIP_TESTS = "skip_tests"          # No test generation
    NO_TESTS_NEEDED = "no_tests_needed"  # Trivial code, tests add no value


@dataclass
class PlanningDecision:
    """Comprehensive planning recommendation"""
    planning_mode: PlanningMode
    test_strategy: TestStrategy
    complexity_score: ComplexityScore
    test_value_score: Optional[TestValueScore]  # None if no code to analyze yet
    rationale: List[str]
    recommendation: str
    estimated_hours: Tuple[float, float]  # (min, max)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "planning_mode": self.planning_mode.value,
            "test_strategy": self.test_strategy.value,
            "complexity_score": self.complexity_score.to_dict(),
            "test_value_score": self.test_value_score.to_dict() if self.test_value_score else None,
            "rationale": self.rationale,
            "recommendation": self.recommendation,
            "estimated_hours": {
                "min": self.estimated_hours[0],
                "max": self.estimated_hours[1]
            }
        }


class PlanningIntelligenceCoordinator:
    """
    Coordinates complexity analysis and test value scoring for planning decisions.
    
    Workflow:
        1. User provides feature request
        2. Analyze planning complexity (ComplexityAnalyzer)
        3. If code exists, analyze test value (TestValueScorer)
        4. Combine scores to recommend planning mode + test strategy
        5. Provide time estimates based on combined analysis
    
    Decision Matrix:
        ┌─────────────────┬──────────────────┬──────────────────┬──────────────────┐
        │ Complexity      │ CRITICAL Tests   │ HIGH/MEDIUM Tests│ LOW/TRIVIAL Tests│
        ├─────────────────┼──────────────────┼──────────────────┼──────────────────┤
        │ CRITICAL/HIGH   │ Incremental+Full │ Incremental+Some │ Incremental+Skip │
        │ MEDIUM          │ Skeleton+Targeted│ Skeleton+Targeted│ Skeleton+Skip    │
        │ LOW/TRIVIAL     │ Skeleton+Targeted│ Direct+Skip      │ Direct+Skip      │
        └─────────────────┴──────────────────┴──────────────────┴──────────────────┘
    
    Integration:
        - Called by Planning Orchestrator before execution
        - Informs TDD Orchestrator whether to generate tests
        - Used by response templates to explain decisions
    """
    
    def __init__(self):
        """Initialize coordinator with analyzers"""
        self.complexity_analyzer = ComplexityAnalyzer()
        self.test_value_scorer = TestValueScorer()
        
        logger.info("PlanningIntelligenceCoordinator initialized")
    
    def analyze_request(
        self,
        user_request: str,
        codebase_context: Optional[Dict] = None,
        target_files: Optional[List[Path]] = None
    ) -> PlanningDecision:
        """
        Analyze user request and determine optimal planning approach.
        
        Args:
            user_request: User's feature request or task description
            codebase_context: Optional AST analysis results (file count, dependencies, etc.)
            target_files: Optional list of files to be modified (for test value scoring)
        
        Returns:
            PlanningDecision with mode, test strategy, and rationale
        
        Example:
            >>> coordinator = PlanningIntelligenceCoordinator()
            >>> decision = coordinator.analyze_request(
            ...     "Add JWT authentication to API",
            ...     target_files=[Path("src/auth/jwt_handler.py")]
            ... )
            >>> print(decision.planning_mode)  # INCREMENTAL_FULL_TDD
            >>> print(decision.test_strategy)  # FULL_SUITE
        """
        logger.info(f"Analyzing request: {user_request[:100]}...")
        
        # Step 1: Analyze planning complexity
        complexity_score = self.complexity_analyzer.analyze(user_request, codebase_context)
        logger.info(f"Complexity: {complexity_score.tier.value} ({complexity_score.total_score}/100)")
        
        # Step 2: Analyze test value (if target files provided)
        test_value_score = None
        if target_files:
            test_value_score = self._analyze_test_value(target_files)
            if test_value_score:
                logger.info(f"Test Value: {test_value_score.value_tier.value} ({test_value_score.total_score}/100)")
        
        # Step 3: Determine planning mode
        planning_mode = self._determine_planning_mode(complexity_score, test_value_score)
        
        # Step 4: Determine test strategy
        test_strategy = self._determine_test_strategy(complexity_score, test_value_score)
        
        # Step 5: Generate rationale
        rationale = self._generate_rationale(complexity_score, test_value_score, planning_mode, test_strategy)
        
        # Step 6: Generate recommendation
        recommendation = self._generate_recommendation(planning_mode, test_strategy, complexity_score)
        
        # Step 7: Estimate timeframe
        estimated_hours = self._estimate_timeframe(complexity_score, test_strategy)
        
        return PlanningDecision(
            planning_mode=planning_mode,
            test_strategy=test_strategy,
            complexity_score=complexity_score,
            test_value_score=test_value_score,
            rationale=rationale,
            recommendation=recommendation,
            estimated_hours=estimated_hours
        )
    
    def _analyze_test_value(self, target_files: List[Path]) -> Optional[TestValueScore]:
        """
        Analyze test value for target files.
        Returns highest test value score if multiple files.
        """
        if not target_files:
            return None
        
        scores = []
        for file_path in target_files:
            if not file_path.exists():
                logger.warning(f"File does not exist: {file_path}")
                continue
            
            try:
                code_content = file_path.read_text(encoding='utf-8')
                score = self.test_value_scorer.score_file(file_path, code_content)
                scores.append(score)
            except Exception as e:
                logger.error(f"Error analyzing {file_path}: {e}")
        
        if not scores:
            return None
        
        # Return highest test value score (most critical file determines strategy)
        return max(scores, key=lambda s: s.total_score)
    
    def _determine_planning_mode(
        self,
        complexity_score: ComplexityScore,
        test_value_score: Optional[TestValueScore]
    ) -> PlanningMode:
        """
        Determine planning mode based on complexity and test value.
        
        Decision Matrix:
            CRITICAL/HIGH complexity → Incremental (always)
            MEDIUM complexity → Skeleton or Incremental (depends on test value)
            LOW/TRIVIAL complexity → Direct execution (usually)
        """
        complexity_tier = complexity_score.tier
        test_tier = test_value_score.value_tier if test_value_score else TestValue.MEDIUM
        
        # CRITICAL/HIGH complexity → Always incremental
        if complexity_tier in [ComplexityTier.CRITICAL, ComplexityTier.HIGH]:
            if test_tier in [TestValue.CRITICAL, TestValue.HIGH]:
                return PlanningMode.INCREMENTAL_FULL_TDD
            elif test_tier == TestValue.MEDIUM:
                return PlanningMode.INCREMENTAL_TARGETED_TDD
            else:  # LOW/TRIVIAL test value
                return PlanningMode.INCREMENTAL_NO_TDD
        
        # MEDIUM complexity → Conditional
        elif complexity_tier == ComplexityTier.MEDIUM:
            if test_tier in [TestValue.CRITICAL, TestValue.HIGH]:
                return PlanningMode.SKELETON_TARGETED_TDD
            else:
                return PlanningMode.SKELETON_NO_TDD
        
        # LOW/TRIVIAL complexity → Direct execution
        else:
            if test_tier in [TestValue.CRITICAL, TestValue.HIGH]:
                # Edge case: Trivial complexity but critical code (e.g., simple auth check)
                return PlanningMode.SKELETON_TARGETED_TDD
            else:
                return PlanningMode.DIRECT_EXECUTION
    
    def _determine_test_strategy(
        self,
        complexity_score: ComplexityScore,
        test_value_score: Optional[TestValueScore]
    ) -> TestStrategy:
        """
        Determine test generation strategy.
        
        Rules:
            - CRITICAL test value → Always generate tests
            - HIGH test value + HIGH complexity → Full suite
            - MEDIUM test value → Targeted tests only
            - LOW/TRIVIAL test value → Skip tests
        """
        test_tier = test_value_score.value_tier if test_value_score else TestValue.MEDIUM
        complexity_tier = complexity_score.tier
        
        if test_tier == TestValue.CRITICAL:
            return TestStrategy.FULL_SUITE
        elif test_tier == TestValue.HIGH:
            if complexity_tier in [ComplexityTier.CRITICAL, ComplexityTier.HIGH]:
                return TestStrategy.FULL_SUITE
            else:
                return TestStrategy.TARGETED_TESTS
        elif test_tier == TestValue.MEDIUM:
            return TestStrategy.TARGETED_TESTS
        elif test_tier == TestValue.LOW:
            return TestStrategy.SKIP_TESTS
        else:  # TRIVIAL
            return TestStrategy.NO_TESTS_NEEDED
    
    def _generate_rationale(
        self,
        complexity_score: ComplexityScore,
        test_value_score: Optional[TestValueScore],
        planning_mode: PlanningMode,
        test_strategy: TestStrategy
    ) -> List[str]:
        """Generate explanation for the planning decision"""
        rationale = []
        
        # Complexity rationale
        rationale.append(
            f"**Planning Complexity:** {complexity_score.tier.value.upper()} "
            f"({complexity_score.total_score}/100)"
        )
        rationale.extend(f"  • {item}" for item in complexity_score.rationale)
        
        # Test value rationale
        if test_value_score:
            rationale.append(
                f"\n**Test Value:** {test_value_score.value_tier.value.upper()} "
                f"({test_value_score.total_score}/100)"
            )
            rationale.extend(f"  • {item}" for item in test_value_score.rationale)
        else:
            rationale.append("\n**Test Value:** Not analyzed (no target files provided)")
        
        # Decision rationale
        rationale.append(f"\n**Decision:** {planning_mode.value.replace('_', ' ').title()}")
        rationale.append(f"**Test Strategy:** {test_strategy.value.replace('_', ' ').title()}")
        
        return rationale
    
    def _generate_recommendation(
        self,
        planning_mode: PlanningMode,
        test_strategy: TestStrategy,
        complexity_score: ComplexityScore
    ) -> str:
        """Generate actionable recommendation"""
        mode_recommendations = {
            PlanningMode.INCREMENTAL_FULL_TDD: (
                "Use incremental planning with full TDD cycle (RED→GREEN→REFACTOR). "
                "Break into 2-4 phases with intermediate validation. Generate comprehensive "
                "test suite covering all paths, edge cases, and security scenarios."
            ),
            PlanningMode.INCREMENTAL_TARGETED_TDD: (
                "Use incremental planning with targeted TDD. Break into 2-3 phases. "
                "Generate tests for public API surface and critical paths only. "
                "Skip tests for internal utilities and trivial code."
            ),
            PlanningMode.INCREMENTAL_NO_TDD: (
                "Use incremental planning without TDD. Break into 2-3 phases for structure "
                "and risk management, but skip test generation. Focus on implementation quality "
                "and code review instead of automated testing."
            ),
            PlanningMode.SKELETON_TARGETED_TDD: (
                "Use skeleton planning with targeted tests. Create lightweight structure, "
                "then generate tests for critical code paths only. Suitable for moderate "
                "complexity with focused testing needs."
            ),
            PlanningMode.SKELETON_NO_TDD: (
                "Use skeleton planning without TDD. Create basic structure and implement "
                "directly. Skip test generation - inline validation and code review sufficient."
            ),
            PlanningMode.DIRECT_EXECUTION: (
                "Skip formal planning - execute directly. No test generation needed. "
                "Use inline validation or quick manual check instead of automated tests."
            )
        }
        
        base_recommendation = mode_recommendations[planning_mode]
        
        # Add trigger-specific guidance
        if complexity_score.triggers:
            trigger_guidance = (
                f"\n\n⚠️ **Critical Triggers Detected:** "
                f"{', '.join([t.split(':')[0] for t in complexity_score.triggers])}. "
                f"Mandatory security/compliance review before deployment."
            )
            return base_recommendation + trigger_guidance
        
        return base_recommendation
    
    def _estimate_timeframe(
        self,
        complexity_score: ComplexityScore,
        test_strategy: TestStrategy
    ) -> Tuple[float, float]:
        """
        Estimate development timeframe based on complexity and test strategy.
        
        Returns:
            (min_hours, max_hours) tuple
        """
        # Base estimate from complexity
        complexity_base = {
            ComplexityTier.CRITICAL: (8, 16),
            ComplexityTier.HIGH: (4, 8),
            ComplexityTier.MEDIUM: (2, 4),
            ComplexityTier.LOW: (1, 2),
            ComplexityTier.TRIVIAL: (0.25, 0.5)
        }
        
        min_hours, max_hours = complexity_base[complexity_score.tier]
        
        # Add test overhead
        test_overhead = {
            TestStrategy.FULL_SUITE: 1.5,          # 50% overhead
            TestStrategy.TARGETED_TESTS: 1.25,     # 25% overhead
            TestStrategy.SKIP_TESTS: 1.0,          # No overhead
            TestStrategy.NO_TESTS_NEEDED: 1.0
        }
        
        multiplier = test_overhead[test_strategy]
        
        return (min_hours * multiplier, max_hours * multiplier)


# ============================================================================
# CLI Interface for Standalone Testing
# ============================================================================

if __name__ == "__main__":
    import sys
    import json
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) < 2:
        print("Usage: python planning_intelligence_coordinator.py '<user_request>' [file1.py file2.py ...]")
        print("\nExamples:")
        print('  python planning_intelligence_coordinator.py "Add JWT auth to API"')
        print('  python planning_intelligence_coordinator.py "Add auth" src/auth/handler.py')
        print('  python planning_intelligence_coordinator.py "Fix typo in README"')
        sys.exit(1)
    
    user_request = sys.argv[1]
    target_files = [Path(f) for f in sys.argv[2:]] if len(sys.argv) > 2 else None
    
    print("=" * 80)
    print("CORTEX Planning Intelligence Coordinator v1.0.0")
    print("=" * 80)
    print(f"\nUser Request: {user_request}")
    if target_files:
        print(f"Target Files: {', '.join(str(f) for f in target_files)}\n")
    else:
        print("Target Files: None (complexity analysis only)\n")
    
    coordinator = PlanningIntelligenceCoordinator()
    decision = coordinator.analyze_request(user_request, target_files=target_files)
    
    print("=" * 80)
    print("PLANNING DECISION")
    print("=" * 80)
    print(f"\n**Planning Mode:** {decision.planning_mode.value.replace('_', ' ').title()}")
    print(f"**Test Strategy:** {decision.test_strategy.value.replace('_', ' ').title()}")
    print(f"**Estimated Time:** {decision.estimated_hours[0]:.1f}-{decision.estimated_hours[1]:.1f} hours\n")
    
    print("=" * 80)
    print("RATIONALE")
    print("=" * 80)
    for item in decision.rationale:
        print(item)
    
    print("\n" + "=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    print(f"\n{decision.recommendation}\n")
    
    # Verbose JSON output
    if '--json' in sys.argv:
        print("=" * 80)
        print("JSON OUTPUT")
        print("=" * 80)
        print(json.dumps(decision.to_dict(), indent=2))
