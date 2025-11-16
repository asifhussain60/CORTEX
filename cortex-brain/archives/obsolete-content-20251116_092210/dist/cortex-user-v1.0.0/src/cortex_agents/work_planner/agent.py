"""
WorkPlanner Agent - Modular Version

Breaks down complex requests into actionable tasks with time estimates.
Uses Tier 2 Knowledge Graph to find similar workflow patterns and Tier 3 Context
Intelligence to inform velocity-aware time estimates.
"""

import os
from typing import List, Dict, Any
from datetime import datetime

from ..base_agent import BaseAgent, AgentRequest, AgentResponse
from ..agent_types import IntentType, Priority
from ..utils import extract_file_paths, safe_get

from .complexity_analyzer import ComplexityAnalyzer
from .workflow_finder import WorkflowFinder
from .velocity_tracker import VelocityTracker
from .strategies.task_generator import TaskGenerator
from .estimator import Estimator
from .dependency_manager import DependencyManager
from .risk_assessor import RiskAssessor
from .priority_calculator import PriorityCalculator
from .pattern_storage import PatternStorage


class WorkPlanner(BaseAgent):
    """
    Breaks down complex requests into actionable tasks.
    
    Features:
    - Task decomposition based on complexity analysis
    - Pattern-based task templates from Tier 2
    - Velocity-aware time estimation using Tier 3
    - Dependency identification and ordering
    - Risk assessment for task execution
    """
    
    def __init__(self, name: str, tier1_api=None, tier2_kg=None, tier3_context=None):
        """Initialize WorkPlanner with tier APIs."""
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        
        # Initialize components
        self.complexity_analyzer = ComplexityAnalyzer()
        self.workflow_finder = WorkflowFinder(tier2_kg)
        self.velocity_tracker = VelocityTracker(tier3_context)
        self.task_generator = TaskGenerator()
        self.estimator = Estimator()
        self.dependency_manager = DependencyManager()
        self.risk_assessor = RiskAssessor()
        self.priority_calculator = PriorityCalculator()
        self.pattern_storage = PatternStorage(tier2_kg)
    
    def can_handle(self, request: AgentRequest) -> bool:
        """Check if this agent can handle the request."""
        valid_intents = [
            IntentType.FEATURE.value,
            IntentType.BUG.value,
            IntentType.REFACTOR.value,
            "plan",
            "breakdown",
            "estimate",
            "tasks"
        ]
        return request.intent.lower() in valid_intents
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """Generate task breakdown with time estimates."""
        try:
            self.log_request(request)
            self.logger.info("Starting work planning")
            
            # Analyze complexity
            complexity = self.complexity_analyzer.analyze(request)
            self.logger.info(f"Detected complexity: {complexity}")
            
            # Find similar workflows from Tier 2
            similar_workflows = self.workflow_finder.find_similar(request)
            
            # Get velocity metrics from Tier 3
            velocity_data = self.velocity_tracker.get_metrics()
            
            # Generate task breakdown
            tasks = self._generate_task_breakdown(
                request,
                complexity,
                similar_workflows,
                velocity_data
            )
            
            # Identify dependencies
            tasks = self.dependency_manager.identify(tasks)
            
            # Assess risks
            file_paths = extract_file_paths(request.user_message)
            tasks, risk_factors = self.risk_assessor.assess(
                tasks,
                complexity,
                len(file_paths)
            )
            
            # Calculate total hours
            total_hours = sum(t.get("estimated_hours", 0) for t in tasks)
            
            # Log to Tier 1 if available
            if self.tier1 and request.conversation_id:
                self.tier1.process_message(
                    request.conversation_id,
                    "agent",
                    f"WorkPlanner: Generated {len(tasks)} tasks ({total_hours} hours)"
                )
            
            # Store workflow pattern in Tier 2
            self.pattern_storage.store(
                request.context,
                tasks,
                complexity,
                total_hours
            )
            
            result = {
                "success": True,
                "tasks": tasks,
                "task_count": len(tasks),
                "total_hours": total_hours,
                "complexity": complexity,
                "risks": risk_factors,
                "velocity_used": velocity_data is not None,
                "timestamp": datetime.now().isoformat()
            }
            
            response = AgentResponse(
                success=True,
                result=result,
                message=f"Created {len(tasks)} tasks with {total_hours} hour estimate (complexity: {complexity})",
                agent_name=self.name,
                metadata={
                    "task_count": len(tasks),
                    "total_hours": total_hours,
                    "complexity": complexity
                },
                next_actions=self._suggest_next_actions(result)
            )
            
            self.log_response(response)
            return response
            
        except Exception as e:
            self.logger.error(f"Work planning failed: {str(e)}")
            return AgentResponse(
                success=False,
                result=None,
                message=f"Work planning failed: {str(e)}",
                agent_name=self.name
            )
    
    def _generate_task_breakdown(
        self,
        request: AgentRequest,
        complexity: str,
        similar_workflows: List[Dict[str, Any]],
        velocity_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate task breakdown with time estimates."""
        tasks = []
        
        # Try to use similar workflow as template
        if similar_workflows:
            template_tasks = self.workflow_finder.extract_tasks(similar_workflows[0])
            if template_tasks:
                tasks = template_tasks
                self.logger.info(f"Using workflow template with {len(tasks)} tasks")
        
        # If no template found, use pattern matching
        if not tasks:
            tasks = self.task_generator.match_template(request)
        
        # If still no tasks, create generic breakdown
        if not tasks:
            tasks = self.task_generator.create_generic_breakdown(request, complexity)
        
        # Adjust estimates based on complexity and velocity
        tasks = self.estimator.adjust_estimates(tasks, complexity, velocity_data)
        
        # Add task metadata
        for i, task in enumerate(tasks):
            task["id"] = i + 1
            task["status"] = "not_started"
            task["priority"] = self.priority_calculator.calculate(task, i, len(tasks))
        
        return tasks
    
    def _suggest_next_actions(self, result: Dict[str, Any]) -> List[str]:
        """Suggest next actions based on planning result."""
        actions = []
        
        if result.get("success"):
            actions.append("Review task breakdown for accuracy")
            actions.append("Begin with highest priority tasks")
            
            if result.get("total_hours", 0) > 10:
                actions.append("Consider breaking into multiple work sessions")
            
            if result.get("risks"):
                actions.append("Review identified risks before starting")
            
            actions.append("Update task status as you progress")
        else:
            actions.append("Clarify requirements and try planning again")
        
        return actions
