"""
Test Quality Evaluator for TDD Orchestrator v4.0

Package 3: LLM-as-judge test quality evaluation
Evaluates test generation reasoning using agent evaluation framework.

Author: CORTEX Development Team
Version: 1.0.0
Created: 2025-12-21
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from src.orchestration_4_0.frameworks.agent_evaluator import AgentEvaluator, EvaluationResult

logger = logging.getLogger(__name__)


@dataclass
class TestQualityScore:
    """Test quality assessment result"""
    coverage_completeness: float  # 1-10
    edge_case_handling: float     # 1-10
    assertion_quality: float      # 1-10
    maintainability: float        # 1-10
    independence: float           # 1-10
    overall: float                # Average
    reasoning: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'coverage_completeness': self.coverage_completeness,
            'edge_case_handling': self.edge_case_handling,
            'assertion_quality': self.assertion_quality,
            'maintainability': self.maintainability,
            'independence': self.independence,
            'overall': self.overall,
            'reasoning': self.reasoning,
        }


class TestQualityEvaluator:
    """
    Evaluate test generation quality using LLM-as-judge.
    
    Integrates with Phase 5 Agent Evaluation Framework to assess:
    - Coverage completeness
    - Edge case handling
    - Assertion quality
    - Maintainability
    - Test independence
    """
    
    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize test quality evaluator.
        
        Args:
            llm_client: LLM client for evaluation (optional)
        """
        self.agent_evaluator = AgentEvaluator(llm_client)
        self.criteria = {
            'coverage_completeness': 'Tests cover all requirements and acceptance criteria',
            'edge_case_handling': 'Edge cases, error scenarios, and boundary conditions tested',
            'assertion_quality': 'Assertions are specific, meaningful, and verify expected behavior',
            'maintainability': 'Tests are readable, well-structured, and follow conventions',
            'independence': 'Tests are isolated, repeatable, and don\'t depend on execution order'
        }
        logger.info("🎭 Test Quality Evaluator initialized")
    
    async def evaluate_test_quality(
        self,
        test_code: str,
        implementation: str,
        acceptance_criteria: List[str],
        language: str = "Python"
    ) -> TestQualityScore:
        """
        Use LLM to judge test quality across multiple criteria.
        
        Args:
            test_code: Generated test code
            implementation: Implementation code being tested
            acceptance_criteria: List of acceptance criteria
            language: Programming language
            
        Returns:
            TestQualityScore with individual scores and overall
        """
        logger.info("📊 Evaluating test quality with LLM-as-judge")
        
        # Build evaluation context
        context = self._build_evaluation_context(
            test_code,
            implementation,
            acceptance_criteria,
            language
        )
        
        # Use agent evaluator for reasoning quality
        reasoning_result = await self.agent_evaluator.evaluate_reasoning(
            agent_name="TestGenerator",
            input_context=context['input_context'],
            agent_output=test_code,
            expected_output=None
        )
        
        # Evaluate individual criteria
        scores = {}
        
        # Coverage completeness
        scores['coverage_completeness'] = self._evaluate_coverage(
            test_code,
            acceptance_criteria
        )
        
        # Edge case handling
        scores['edge_case_handling'] = self._evaluate_edge_cases(
            test_code,
            language
        )
        
        # Assertion quality
        scores['assertion_quality'] = self._evaluate_assertions(
            test_code,
            language
        )
        
        # Maintainability
        scores['maintainability'] = self._evaluate_maintainability(
            test_code,
            language
        )
        
        # Independence
        scores['independence'] = self._evaluate_independence(
            test_code,
            language
        )
        
        # Calculate overall score (weighted average)
        overall = sum(scores.values()) / len(scores)
        
        # Build reasoning summary
        reasoning = self._build_reasoning(scores, reasoning_result)
        
        result = TestQualityScore(
            coverage_completeness=scores['coverage_completeness'],
            edge_case_handling=scores['edge_case_handling'],
            assertion_quality=scores['assertion_quality'],
            maintainability=scores['maintainability'],
            independence=scores['independence'],
            overall=overall,
            reasoning=reasoning
        )
        
        logger.info(f"✅ Test quality: {overall:.1f}/10")
        
        return result
    
    def _build_evaluation_context(
        self,
        test_code: str,
        implementation: str,
        acceptance_criteria: List[str],
        language: str
    ) -> Dict[str, str]:
        """Build context for evaluation"""
        input_context = f"""
Language: {language}

Implementation:
```{language.lower()}
{implementation}
```

Acceptance Criteria:
{chr(10).join(f'- {c}' for c in acceptance_criteria)}
"""
        return {'input_context': input_context}
    
    def _evaluate_coverage(
        self,
        test_code: str,
        acceptance_criteria: List[str]
    ) -> float:
        """Evaluate coverage completeness (heuristic)"""
        score = 5.0  # Start neutral
        
        # Check if test mentions each acceptance criterion
        test_lower = test_code.lower()
        criteria_covered = sum(
            1 for criterion in acceptance_criteria
            if any(word.lower() in test_lower for word in criterion.split() if len(word) > 4)
        )
        
        if criteria_covered == len(acceptance_criteria):
            score = 10.0
        elif criteria_covered >= len(acceptance_criteria) * 0.8:
            score = 8.0
        elif criteria_covered >= len(acceptance_criteria) * 0.5:
            score = 6.0
        else:
            score = 4.0
        
        return score
    
    def _evaluate_edge_cases(self, test_code: str, language: str) -> float:
        """Evaluate edge case handling (heuristic)"""
        score = 5.0
        test_lower = test_code.lower()
        
        # Look for edge case indicators
        edge_case_keywords = [
            'edge', 'boundary', 'empty', 'null', 'none', 'zero',
            'negative', 'maximum', 'minimum', 'invalid', 'error'
        ]
        
        edge_cases_found = sum(
            1 for keyword in edge_case_keywords
            if keyword in test_lower
        )
        
        if edge_cases_found >= 5:
            score = 10.0
        elif edge_cases_found >= 3:
            score = 8.0
        elif edge_cases_found >= 1:
            score = 6.0
        else:
            score = 4.0
        
        return score
    
    def _evaluate_assertions(self, test_code: str, language: str) -> float:
        """Evaluate assertion quality (heuristic)"""
        score = 5.0
        
        # Count assertions
        if language == "Python":
            assertion_count = test_code.count('assert')
        elif language in ["JavaScript", "TypeScript"]:
            assertion_count = test_code.count('expect(')
        elif language == "C#":
            assertion_count = test_code.count('Assert.')
        else:
            assertion_count = test_code.lower().count('assert')
        
        # Score based on assertion count
        if 3 <= assertion_count <= 10:
            score = 10.0
        elif 1 <= assertion_count <= 2:
            score = 7.0
        elif assertion_count > 10:
            score = 6.0  # Too many assertions may indicate poor test structure
        else:
            score = 3.0  # No assertions is bad
        
        return score
    
    def _evaluate_maintainability(self, test_code: str, language: str) -> float:
        """Evaluate test maintainability (heuristic)"""
        score = 5.0
        
        # Check for docstrings/comments
        has_documentation = '"""' in test_code or "'''" in test_code or '//' in test_code or '/*' in test_code
        if has_documentation:
            score += 2
        
        # Check for descriptive test names
        if 'test_' in test_code or 'it(' in test_code or 'should' in test_code.lower():
            score += 1
        
        # Check test length (not too long)
        lines = len(test_code.split('\n'))
        if 10 <= lines <= 50:
            score += 1
        elif lines > 100:
            score -= 2  # Too long
        
        # Check for setup/teardown patterns
        if 'setup' in test_code.lower() or 'teardown' in test_code.lower() or 'fixture' in test_code.lower():
            score += 1
        
        return min(score, 10.0)
    
    def _evaluate_independence(self, test_code: str, language: str) -> float:
        """Evaluate test independence (heuristic)"""
        score = 8.0  # Assume independent unless proven otherwise
        
        test_lower = test_code.lower()
        
        # Red flags for test dependencies
        if 'global' in test_lower:
            score -= 2
        
        if 'shared' in test_lower and 'state' in test_lower:
            score -= 2
        
        if 'depends on' in test_lower or 'requires' in test_lower:
            score -= 1
        
        # Good patterns for independence
        if 'setup' in test_lower or 'fixture' in test_lower:
            score += 1
        
        if 'mock' in test_lower or 'stub' in test_lower:
            score += 1
        
        return max(1.0, min(score, 10.0))
    
    def _build_reasoning(
        self,
        scores: Dict[str, float],
        reasoning_result: EvaluationResult
    ) -> str:
        """Build reasoning summary"""
        parts = []
        
        for criterion, score in scores.items():
            criterion_display = criterion.replace('_', ' ').title()
            if score >= 8:
                parts.append(f"{criterion_display}: Excellent ({score:.1f}/10)")
            elif score >= 6:
                parts.append(f"{criterion_display}: Good ({score:.1f}/10)")
            elif score >= 4:
                parts.append(f"{criterion_display}: Fair ({score:.1f}/10)")
            else:
                parts.append(f"{criterion_display}: Needs Improvement ({score:.1f}/10)")
        
        parts.append(f"LLM Reasoning: {reasoning_result.reasoning}")
        
        return "; ".join(parts)
