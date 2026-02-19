"""
Complexity-Gated Workflow Router - Core Implementation

Routes tasks to workflow templates or direct orchestrators based on complexity scoring.
Prevents golden hammer anti-pattern through intelligent threshold-based routing.

Authority: WORKFLOW-COMPLEXITY-GATE-001
Date: 2026-02-17
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime


class ComplexityThreshold(Enum):
    """Complexity thresholds aligned with CONF-GATE (CORE-046)."""
    TRIVIAL = 0.15      # Direct orchestrator (auto-approve)
    SIMPLE = 0.35       # Direct orchestrator (minimal validation)
    MODERATE = 0.60     # Workflow template (structured approach)
    COMPLEX = 0.75      # Workflow template (mandatory gates)


class RoutingStrategy(Enum):
    """Routing strategies for task execution."""
    DIRECT_ORCHESTRATOR = "direct_orchestrator"
    WORKFLOW_TEMPLATE = "workflow_template"


@dataclass
class Intent:
    """Parsed user intent for complexity analysis."""
    operation_type: str
    target_files: List[str]
    dependencies: List[str]
    risk_level: str
    metadata: Dict[str, Any]


@dataclass
class RoutingDecision:
    """Decision output from complexity router."""
    route: RoutingStrategy
    complexity: float
    rationale: str
    orchestrator: Optional[str] = None
    template_id: Optional[str] = None
    requires_confirmation: bool = False
    governance_gate: Optional[str] = None


class WorkflowComplexityRouter:
    """
    Routes tasks to workflow templates or direct orchestrators based on complexity.
    
    Scoring dimensions (aligned with CONF-GATE-001):
    - File count (30%): min(files/10, 1.0)
    - Operation type (40%): Predefined scores
    - Dependencies (20%): min(deps/5, 1.0)
    - Risk level (10%): {LOW:0.2, MEDIUM:0.5, HIGH:0.8, CRITICAL:1.0}
    
    Authority: WORKFLOW-COMPLEXITY-GATE-001
    """
    
    # Thresholds aligned with CONF-GATE rules (CORE-046)
    TRIVIAL_THRESHOLD = ComplexityThreshold.TRIVIAL.value
    SIMPLE_THRESHOLD = ComplexityThreshold.SIMPLE.value
    MODERATE_THRESHOLD = ComplexityThreshold.MODERATE.value
    COMPLEX_THRESHOLD = ComplexityThreshold.COMPLEX.value
    
    # Operation type complexity scores (40% weight)
    OPERATION_SCORES = {
        "create": 0.4,
        "refactor": 0.6,
        "migrate": 0.8,
        "test": 0.5,
        "security": 0.7,
        "document": 0.2,
        "fix": 0.3,
        "update": 0.2,
        "delete": 0.4,
        "deploy": 0.7,
    }
    
    # Risk level scores (10% weight)
    RISK_SCORES = {
        "LOW": 0.2,
        "MEDIUM": 0.5,
        "HIGH": 0.8,
        "CRITICAL": 1.0,
    }
    
    def score_task_complexity(self, intent: Intent) -> float:
        """
        Score task complexity (0.0-1.0) based on dimensions.
        
        Args:
            intent: Parsed user intent with task details
        
        Returns:
            Complexity score (0.0 = trivial, 1.0 = highly complex)
        """
        score = 0.0
        
        # Dimension 1: File count (30% weight)
        file_count = len(intent.target_files)
        file_score = min(file_count / 10, 1.0) * 0.30
        
        # Dimension 2: Operation type (40% weight)
        operation_score = self.OPERATION_SCORES.get(
            intent.operation_type.lower(), 0.5
        ) * 0.40
        
        # Dimension 3: Dependency depth (20% weight)
        dep_count = len(intent.dependencies)
        dep_score = min(dep_count / 5, 1.0) * 0.20
        
        # Dimension 4: Risk level (10% weight)
        risk_score = self.RISK_SCORES.get(intent.risk_level.upper(), 0.5) * 0.10
        
        # Total score
        score = file_score + operation_score + dep_score + risk_score
        
        return min(score, 1.0)
    
    def route(self, intent: Intent) -> RoutingDecision:
        """
        Route to workflow template or direct orchestrator.
        
        Args:
            intent: Parsed user intent
        
        Returns:
            RoutingDecision with route, complexity, and rationale
        """
        complexity = self.score_task_complexity(intent)
        
        if complexity < self.TRIVIAL_THRESHOLD:
            return RoutingDecision(
                route=RoutingStrategy.DIRECT_ORCHESTRATOR,
                complexity=complexity,
                rationale="Trivial operation, no workflow overhead",
                orchestrator=self._select_orchestrator(intent),
                requires_confirmation=False
            )
        
        elif complexity < self.SIMPLE_THRESHOLD:
            return RoutingDecision(
                route=RoutingStrategy.DIRECT_ORCHESTRATOR,
                complexity=complexity,
                rationale="Simple operation, direct orchestration sufficient",
                orchestrator=self._select_orchestrator(intent),
                requires_confirmation=False
            )
        
        elif complexity < self.MODERATE_THRESHOLD:
            return RoutingDecision(
                route=RoutingStrategy.WORKFLOW_TEMPLATE,
                complexity=complexity,
                rationale="Moderate complexity, structured workflow recommended",
                template_id=self._select_template(intent),
                requires_confirmation=True
            )
        
        else:  # >= COMPLEX_THRESHOLD
            return RoutingDecision(
                route=RoutingStrategy.WORKFLOW_TEMPLATE,
                complexity=complexity,
                rationale="High complexity, mandatory workflow template",
                template_id=self._select_template(intent),
                requires_confirmation=True,
                governance_gate="MANDATORY"
            )
    
    def _select_orchestrator(self, intent: Intent) -> str:
        """Select appropriate orchestrator for direct execution."""
        operation_type = intent.operation_type.lower()
        
        orchestrator_map = {
            "fix": "RefactoringOrchestrator",
            "update": "RefactoringOrchestrator",
            "document": "DocumentationOrchestrator",
            "test": "TDDOrchestrator",
            "security": "SecurityOrchestrator",
            "deploy": "DeploymentOrchestrator",
        }
        
        return orchestrator_map.get(operation_type, "MasterOrchestrator")
    
    def _select_template(self, intent: Intent) -> str:
        """Select appropriate workflow template."""
        operation_type = intent.operation_type.lower()
        
        template_map = {
            "create": "tdd/feature-implementation",
            "test": "tdd/feature-implementation",
            "refactor": "quality/refactoring",
            "migrate": "migration/legacy-modernization",
            "security": "security/audit-remediation",
            "deploy": "deployment/production-release",
        }
        
        return template_map.get(operation_type, "tdd/feature-implementation")
