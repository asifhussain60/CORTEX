# AC-ID: AC-TDD-INCREMENTAL-01 - IncrementalTaskDecomposer Implementation
"""
IncrementalTaskDecomposer - Evidence-based task decomposition for TDD.

Decomposes large implementation tasks into token-budget-constrained subtasks
using Phase 12 CAP framework (EvidenceCollector, PERT estimation).

Key Features:
- Token budget enforcement (default: 10K per subtask)
- Evidence-based complexity assessment
- PERT estimation for subtask sizing
- Dependency tracking between subtasks
- MCP tool integration ready

Governance:
- CORE-008: TDD (tests in test_incremental_task_decomposer.py)
- CORE-011: Type hints on all functions
- CORE-012: Google-style docstrings
- CORE-013: Specific exception handling

Author: Asif Hussain
Date: 2026-02-02
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from cortex.core.result import Result, Ok, Err
from cortex.capacity.evidence_collector import EvidenceCollector

logger = logging.getLogger(__name__)


@dataclass
class SubTask:
    """Single subtask from decomposition."""
    
    subtask_id: str
    parent_task_id: str
    sequence_number: int
    description: str
    module_path: str
    domain: str
    acceptance_criteria: List[str] = field(default_factory=list)
    estimated_tokens: int = 0
    confidence_score: float = 0.0
    depends_on: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskDecompositionResult:
    """Result of task decomposition."""
    
    task_id: str
    subtasks: List[SubTask] = field(default_factory=list)
    total_estimated_tokens: int = 0
    evidence_used: Optional[Dict[str, Any]] = None
    decomposition_strategy: str = "token_budget"
    metadata: Dict[str, Any] = field(default_factory=dict)


class IncrementalTaskDecomposer:
    """
    Decomposes tasks into subtasks with token budget constraints.
    
    Uses Phase 12 CAP framework for evidence-based estimation:
    - EvidenceCollector: Complexity assessment from LENS, Git, Domain
    - PERT estimation: Three-point estimation (optimistic, likely, pessimistic)
    - Token budget: Ensures subtasks fit within LLM context limits
    
    Example:
        >>> decomposer = IncrementalTaskDecomposer(max_tokens_per_subtask=10000)
        >>> result = decomposer.decompose_into_subtasks({
        ...     "task_id": "TASK-001",
        ...     "description": "Implement REST API",
        ...     "module_path": "cortex.api.service",
        ...     "domain": "backend"
        ... })
        >>> subtasks = result.unwrap().subtasks
    
    AC-TDD-INCREMENTAL-01: Task decomposition with token budgets
    """

    def __init__(
        self,
        max_tokens_per_subtask: int = 10000,
        evidence_collector: Optional[EvidenceCollector] = None
    ) -> None:
        """
        Initialize IncrementalTaskDecomposer.
        
        Args:
            max_tokens_per_subtask: Maximum tokens allowed per subtask
            evidence_collector: Evidence collector for complexity assessment
            
        AC-TDD-INCREMENTAL-01-01: Initialization with token budget
        """
        self.max_tokens_per_subtask = max_tokens_per_subtask
        self.evidence_collector = evidence_collector or EvidenceCollector()
        
        logger.info(
            f"IncrementalTaskDecomposer initialized with "
            f"max_tokens_per_subtask={max_tokens_per_subtask}"
        )

    def decompose_into_subtasks(
        self,
        task: Dict[str, Any]
    ) -> Result[TaskDecompositionResult]:
        """
        Decompose task into subtasks with token budget constraints.
        
        Args:
            task: Task specification with task_id, description, module_path, domain
            
        Returns:
            Result with TaskDecompositionResult or error
            
        AC-TDD-INCREMENTAL-01-02: Task decomposition logic
        """
        try:
            # Validate task structure
            validation_result = self._validate_task(task)
            if validation_result.is_err():
                return validation_result

            task_id = task["task_id"]
            description = task["description"]
            module_path = task.get("module_path", "unknown")
            domain = task.get("domain", "unknown")
            acceptance_criteria = task.get("acceptance_criteria", [])

            # Estimate total token budget for task
            token_result = self.estimate_token_budget_per_task(task)
            if token_result.is_err():
                return Err(f"Token estimation failed: {token_result.error}")

            total_tokens = token_result.unwrap()

            # Collect evidence for complexity assessment
            try:
                evidence = self.evidence_collector.collect_evidence(
                    task_id=task_id,
                    task_description=description
                )
            except Exception as e:
                logger.warning(f"Evidence collection failed: {e}, using defaults")
                evidence = None

            # Decompose based on token budget
            if total_tokens <= self.max_tokens_per_subtask:
                # Simple task - single subtask
                subtasks = [self._create_single_subtask(
                    task_id=task_id,
                    description=description,
                    module_path=module_path,
                    domain=domain,
                    acceptance_criteria=acceptance_criteria,
                    estimated_tokens=total_tokens
                )]
            else:
                # Complex task - multiple subtasks
                subtasks = self._decompose_complex_task(
                    task_id=task_id,
                    description=description,
                    module_path=module_path,
                    domain=domain,
                    acceptance_criteria=acceptance_criteria,
                    total_tokens=total_tokens
                )

            result = TaskDecompositionResult(
                task_id=task_id,
                subtasks=subtasks,
                total_estimated_tokens=total_tokens,
                evidence_used=self._evidence_to_dict(evidence) if evidence else None,
                decomposition_strategy="token_budget"
            )

            logger.info(
                f"Task {task_id} decomposed into {len(subtasks)} subtasks "
                f"(total_tokens={total_tokens})"
            )

            return Ok(result)

        except KeyError as e:
            return Err(f"Missing required field in task: {e}")
        except Exception as e:
            logger.error(f"Task decomposition failed: {e}", exc_info=True)
            return Err(f"Task decomposition failed: {e}")

    def estimate_token_budget_per_task(
        self,
        task: Dict[str, Any]
    ) -> Result[int]:
        """
        Estimate token budget for task using PERT and evidence.
        
        Args:
            task: Task specification
            
        Returns:
            Result with estimated token count or error
            
        AC-TDD-INCREMENTAL-01-03: Token budget estimation
        """
        try:
            description = task.get("description", "")
            acceptance_criteria = task.get("acceptance_criteria", [])
            
            # Base estimation on description length and complexity
            base_tokens = len(description.split()) * 50  # ~50 tokens per word average
            
            # Add tokens for acceptance criteria
            ac_tokens = len(acceptance_criteria) * 500  # ~500 tokens per AC
            
            # Collect evidence for complexity multiplier
            task_id = task.get("task_id", "unknown")
            try:
                evidence = self.evidence_collector.collect_evidence(
                    task_id=task_id,
                    task_description=description
                )
                
                # Apply complexity multiplier
                complexity_score = evidence.lens_complexity.get("score", 1.0) if evidence.lens_complexity else 1.0
                complexity_multiplier = 1.0 + (complexity_score / 10.0)  # 1.0 to 2.0 range
                
            except Exception as e:
                logger.warning(f"Evidence collection failed: {e}, using default multiplier")
                complexity_multiplier = 1.5  # Default moderate complexity

            # PERT estimation: (Optimistic + 4*Likely + Pessimistic) / 6
            optimistic = base_tokens + ac_tokens
            likely = int((base_tokens + ac_tokens) * complexity_multiplier)
            pessimistic = int((base_tokens + ac_tokens) * complexity_multiplier * 1.5)
            
            pert_estimate = int((optimistic + 4 * likely + pessimistic) / 6)
            
            # Ensure minimum 1K tokens
            final_estimate = max(1000, pert_estimate)
            
            logger.debug(
                f"Token estimate for {task_id}: {final_estimate} "
                f"(complexity_multiplier={complexity_multiplier:.2f})"
            )
            
            return Ok(final_estimate)

        except Exception as e:
            logger.error(f"Token estimation failed: {e}", exc_info=True)
            return Err(f"Token estimation failed: {e}")

    def _validate_task(self, task: Dict[str, Any]) -> Result[None]:
        """Validate task structure has required fields."""
        required_fields = ["task_id", "description"]
        
        missing = [field for field in required_fields if field not in task]
        
        if missing:
            return Err(f"Missing required fields: {', '.join(missing)}")
        
        return Ok(None)

    def _create_single_subtask(
        self,
        task_id: str,
        description: str,
        module_path: str,
        domain: str,
        acceptance_criteria: List[str],
        estimated_tokens: int
    ) -> SubTask:
        """Create single subtask for simple task."""
        return SubTask(
            subtask_id=f"{task_id}-SUB-01",
            parent_task_id=task_id,
            sequence_number=1,
            description=description,
            module_path=module_path,
            domain=domain,
            acceptance_criteria=acceptance_criteria,
            estimated_tokens=estimated_tokens,
            confidence_score=0.9,  # High confidence for single subtask
            depends_on=[],
            metadata={"is_single": True}
        )

    def _decompose_complex_task(
        self,
        task_id: str,
        description: str,
        module_path: str,
        domain: str,
        acceptance_criteria: List[str],
        total_tokens: int
    ) -> List[SubTask]:
        """Decompose complex task into multiple subtasks."""
        # Calculate number of subtasks needed
        num_subtasks = math.ceil(total_tokens / self.max_tokens_per_subtask)
        tokens_per_subtask = total_tokens // num_subtasks
        
        subtasks = []
        
        # Distribute acceptance criteria across subtasks
        ac_per_subtask = max(1, len(acceptance_criteria) // num_subtasks)
        
        for i in range(num_subtasks):
            start_ac = i * ac_per_subtask
            end_ac = start_ac + ac_per_subtask if i < num_subtasks - 1 else len(acceptance_criteria)
            
            subtask_ac = acceptance_criteria[start_ac:end_ac] if acceptance_criteria else []
            
            # Build subtask description
            subtask_desc = f"{description} (Part {i+1}/{num_subtasks})"
            if subtask_ac:
                subtask_desc += f": {', '.join(subtask_ac[:2])}"  # Show first 2 ACs
            
            # Previous subtask as dependency (except for first)
            depends_on = [f"{task_id}-SUB-{i:02d}"] if i > 0 else []
            
            subtask = SubTask(
                subtask_id=f"{task_id}-SUB-{i+1:02d}",
                parent_task_id=task_id,
                sequence_number=i + 1,
                description=subtask_desc,
                module_path=module_path,
                domain=domain,
                acceptance_criteria=subtask_ac,
                estimated_tokens=tokens_per_subtask,
                confidence_score=0.7,  # Lower confidence for decomposed tasks
                depends_on=depends_on,
                metadata={"part": i+1, "total_parts": num_subtasks}
            )
            
            subtasks.append(subtask)
        
        return subtasks

    def _evidence_to_dict(self, evidence: Any) -> Dict[str, Any]:
        """Convert evidence object to dictionary."""
        try:
            return {
                "lens_complexity": evidence.lens_complexity if hasattr(evidence, 'lens_complexity') else None,
                "git_churn": evidence.git_churn if hasattr(evidence, 'git_churn') else None,
                "evidence_sources": list(evidence.evidence_sources) if hasattr(evidence, 'evidence_sources') else []
            }
        except Exception as e:
            logger.warning(f"Evidence conversion failed: {e}")
            return {}


__all__ = [
    "IncrementalTaskDecomposer",
    "SubTask",
    "TaskDecompositionResult",
]
