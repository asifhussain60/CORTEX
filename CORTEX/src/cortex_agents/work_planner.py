"""
WorkPlanner Agent

Breaks down complex requests into actionable tasks with time estimates.
Uses Tier 2 Knowledge Graph to find similar workflow patterns and Tier 3 Context
Intelligence to inform velocity-aware time estimates.

The WorkPlanner is essential for converting high-level feature requests into
concrete, executable task lists.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from CORTEX.src.cortex_agents.base_agent import BaseAgent, AgentRequest, AgentResponse
from CORTEX.src.cortex_agents.agent_types import IntentType, Priority
from CORTEX.src.cortex_agents.utils import (
    extract_file_paths,
    safe_get,
    format_duration
)


class WorkPlanner(BaseAgent):
    """
    Breaks down complex requests into actionable tasks.
    
    The WorkPlanner analyzes user requests to decompose them into concrete tasks,
    leveraging historical patterns from Tier 2 and velocity metrics from Tier 3
    to provide realistic time estimates.
    
    Features:
    - Task decomposition based on complexity analysis
    - Pattern-based task templates from Tier 2
    - Velocity-aware time estimation using Tier 3
    - Dependency identification and ordering
    - Risk assessment for task execution
    
    Example:
        planner = WorkPlanner(name="Planner", tier1_api, tier2_kg, tier3_context)
        
        request = AgentRequest(
            intent="feature",
            context={"type": "authentication"},
            user_message="Add user authentication with email/password"
        )
        
        response = planner.execute(request)
        # Returns: {
        #   "tasks": [
        #     {"name": "Create User model", "estimated_hours": 1.5},
        #     {"name": "Add login endpoint", "estimated_hours": 2.0},
        #     {"name": "Create tests", "estimated_hours": 1.0}
        #   ],
        #   "total_hours": 4.5,
        #   "complexity": "medium"
        # }
    """
    
    def __init__(self, name: str, tier1_api=None, tier2_kg=None, tier3_context=None):
        """Initialize WorkPlanner with tier APIs."""
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        
        # Task complexity indicators
        self.COMPLEXITY_KEYWORDS = {
            "simple": ["add", "create", "simple", "basic", "quick"],
            "medium": ["modify", "update", "refactor", "enhance", "improve"],
            "complex": ["redesign", "migrate", "overhaul", "architecture", "system"]
        }
        
        # Default task templates for common patterns
        self.TASK_TEMPLATES = {
            "api_endpoint": [
                {"name": "Define route/endpoint", "base_hours": 0.5},
                {"name": "Implement handler logic", "base_hours": 1.5},
                {"name": "Add validation", "base_hours": 1.0},
                {"name": "Create tests", "base_hours": 1.0},
                {"name": "Update documentation", "base_hours": 0.5}
            ],
            "model_creation": [
                {"name": "Define model schema", "base_hours": 1.0},
                {"name": "Add model methods", "base_hours": 1.5},
                {"name": "Create migrations", "base_hours": 0.5},
                {"name": "Write model tests", "base_hours": 1.0}
            ],
            "authentication": [
                {"name": "Create User model", "base_hours": 1.5},
                {"name": "Implement login/logout", "base_hours": 2.0},
                {"name": "Add password hashing", "base_hours": 1.0},
                {"name": "Create session management", "base_hours": 1.5},
                {"name": "Add authentication tests", "base_hours": 2.0}
            ],
            "ui_component": [
                {"name": "Create component structure", "base_hours": 1.0},
                {"name": "Implement component logic", "base_hours": 2.0},
                {"name": "Add styling", "base_hours": 1.0},
                {"name": "Create component tests", "base_hours": 1.5}
            ]
        }
    
    def can_handle(self, request: AgentRequest) -> bool:
        """
        Check if this agent can handle the request.
        
        Args:
            request: The agent request
        
        Returns:
            True if intent is plan, feature, or task_breakdown
        """
        valid_intents = [
            IntentType.PLAN.value,
            IntentType.FEATURE.value,
            IntentType.TASK_BREAKDOWN.value
        ]
        return request.intent.lower() in valid_intents
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Break down the request into actionable tasks.
        
        Args:
            request: The agent request
        
        Returns:
            AgentResponse with task breakdown and estimates
        """
        try:
            self.log_request(request)
            self.logger.info("Starting work planning")
            
            # Step 1: Analyze request complexity
            complexity = self._analyze_complexity(request)
            self.logger.info(f"Request complexity: {complexity}")
            
            # Step 2: Query Tier 2 for similar workflows
            similar_workflows = self._find_similar_workflows(request)
            
            # Step 3: Get velocity metrics from Tier 3
            velocity_data = self._get_velocity_metrics()
            
            # Step 4: Generate task breakdown
            tasks = self._generate_task_breakdown(
                request,
                complexity,
                similar_workflows,
                velocity_data
            )
            
            # Step 5: Calculate total estimate
            total_hours = sum(task["estimated_hours"] for task in tasks)
            
            # Step 6: Identify dependencies and risks
            dependencies = self._identify_dependencies(tasks)
            risks = self._assess_risks(request, complexity, tasks)
            
            # Step 7: Store workflow pattern in Tier 2 for future learning
            if self.tier2:
                self._store_workflow_pattern(request, tasks, complexity)
            
            # Step 8: Log to Tier 1 conversation
            if self.tier1 and request.conversation_id:
                self.tier1.process_message(
                    request.conversation_id,
                    "agent",
                    f"WorkPlanner: Created {len(tasks)} tasks, estimated {total_hours:.1f} hours"
                )
            
            response = AgentResponse(
                success=True,
                result={
                    "tasks": tasks,
                    "total_hours": total_hours,
                    "complexity": complexity,
                    "dependencies": dependencies,
                    "risks": risks,
                    "velocity_adjusted": velocity_data is not None
                },
                message=f"Breakdown: {len(tasks)} tasks, {total_hours:.1f} hours ({complexity} complexity)",
                agent_name=self.name,
                metadata={
                    "pattern_matches": len(similar_workflows),
                    "velocity_available": velocity_data is not None
                },
                next_actions=[
                    "Review task breakdown",
                    "Adjust estimates if needed",
                    "Proceed with execution"
                ]
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
    
    def _analyze_complexity(self, request: AgentRequest) -> str:
        """
        Analyze request complexity based on keywords and context.
        
        Args:
            request: The agent request
        
        Returns:
            Complexity level: "simple", "medium", or "complex"
        """
        message_lower = request.user_message.lower()
        
        # Count complexity indicators
        complexity_scores = {
            "simple": 0,
            "medium": 0,
            "complex": 0
        }
        
        for level, keywords in self.COMPLEXITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in message_lower:
                    complexity_scores[level] += 1
        
        # Check context hints
        context_complexity = safe_get(request.context, "complexity", default="")
        if context_complexity and context_complexity.lower() in complexity_scores:
            complexity_scores[context_complexity.lower()] += 3  # Weight context heavily
        
        # Check for multi-file operations (increases complexity)
        if len(extract_file_paths(request.user_message)) > 3:
            complexity_scores["complex"] += 2
        
        # Return highest scoring complexity
        if complexity_scores["complex"] >= complexity_scores["medium"]:
            if complexity_scores["complex"] >= complexity_scores["simple"]:
                return "complex"
        
        if complexity_scores["medium"] >= complexity_scores["simple"]:
            return "medium"
        
        return "simple"
    
    def _find_similar_workflows(
        self,
        request: AgentRequest,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar workflow patterns from Tier 2.
        
        Args:
            request: The agent request
            limit: Maximum number of patterns to return
        
        Returns:
            List of similar workflow patterns
        """
        if not self.tier2:
            return []
        
        try:
            # Search for workflow patterns
            results = self.tier2.search(
                f"workflow {request.user_message}",
                limit=limit
            )
            
            # Filter to workflow-type patterns
            workflows = [
                r for r in results
                if r.get("type") == "workflow"
            ]
            
            return workflows
        except Exception as e:
            self.logger.warning(f"Tier 2 workflow search failed: {str(e)}")
            return []
    
    def _get_velocity_metrics(self) -> Optional[Dict[str, Any]]:
        """
        Get velocity/capacity metrics from Tier 3.
        
        Returns:
            Velocity metrics dictionary or None if unavailable
        """
        if not self.tier3:
            return None
        
        try:
            # Get context summary with velocity data
            summary = self.tier3.get_context_summary()
            
            velocity_data = {
                "average_velocity": safe_get(summary, "average_velocity", default=15.0),
                "recent_commits": safe_get(summary, "total_commits", default=0),
                "active_developers": 1  # Default assumption
            }
            
            return velocity_data
        except Exception as e:
            self.logger.warning(f"Tier 3 velocity query failed: {str(e)}")
            return None
    
    def _generate_task_breakdown(
        self,
        request: AgentRequest,
        complexity: str,
        similar_workflows: List[Dict[str, Any]],
        velocity_data: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate task breakdown with time estimates.
        
        Args:
            request: The agent request
            complexity: Request complexity level
            similar_workflows: Similar historical workflows
            velocity_data: Velocity metrics from Tier 3
        
        Returns:
            List of tasks with estimates
        """
        tasks = []
        
        # Try to use similar workflow as template
        if similar_workflows:
            template_tasks = self._extract_tasks_from_workflow(similar_workflows[0])
            if template_tasks:
                tasks = template_tasks
                self.logger.info(f"Using workflow template with {len(tasks)} tasks")
        
        # If no template found, use pattern matching
        if not tasks:
            tasks = self._match_task_template(request)
        
        # If still no tasks, create generic breakdown
        if not tasks:
            tasks = self._create_generic_breakdown(request, complexity)
        
        # Adjust estimates based on complexity and velocity
        tasks = self._adjust_estimates(tasks, complexity, velocity_data)
        
        # Add task metadata
        for i, task in enumerate(tasks):
            task["id"] = i + 1
            task["status"] = "not_started"
            task["priority"] = self._calculate_task_priority(task, i, len(tasks))
        
        return tasks
    
    def _extract_tasks_from_workflow(
        self,
        workflow: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract tasks from a historical workflow pattern.
        
        Args:
            workflow: Workflow pattern from Tier 2
        
        Returns:
            List of tasks
        """
        # Workflow content should contain task list
        content = workflow.get("content", "")
        
        # Simple extraction - in real implementation, this would be more sophisticated
        tasks = []
        
        # Check if workflow has embedded task data
        if isinstance(content, dict) and "tasks" in content:
            tasks = content["tasks"]
        
        return tasks
    
    def _match_task_template(self, request: AgentRequest) -> List[Dict[str, Any]]:
        """
        Match request to a task template.
        
        Args:
            request: The agent request
        
        Returns:
            List of tasks from matching template
        """
        message_lower = request.user_message.lower()
        
        # Check for template keywords
        if any(word in message_lower for word in ["api", "endpoint", "route"]):
            return [dict(task) for task in self.TASK_TEMPLATES["api_endpoint"]]
        
        if any(word in message_lower for word in ["model", "schema", "database"]):
            return [dict(task) for task in self.TASK_TEMPLATES["model_creation"]]
        
        if any(word in message_lower for word in ["auth", "login", "user", "password"]):
            return [dict(task) for task in self.TASK_TEMPLATES["authentication"]]
        
        if any(word in message_lower for word in ["component", "ui", "interface", "view"]):
            return [dict(task) for task in self.TASK_TEMPLATES["ui_component"]]
        
        return []
    
    def _create_generic_breakdown(
        self,
        request: AgentRequest,
        complexity: str
    ) -> List[Dict[str, Any]]:
        """
        Create a generic task breakdown when no template matches.
        
        Args:
            request: The agent request
            complexity: Request complexity level
        
        Returns:
            List of generic tasks
        """
        # Base hours by complexity
        complexity_hours = {
            "simple": 2.0,
            "medium": 5.0,
            "complex": 10.0
        }
        
        total_hours = complexity_hours.get(complexity, 5.0)
        
        # Generic task structure
        tasks = [
            {
                "name": "Analyze requirements",
                "base_hours": total_hours * 0.1,
                "description": "Review and understand the requirements"
            },
            {
                "name": "Design solution",
                "base_hours": total_hours * 0.15,
                "description": "Design the implementation approach"
            },
            {
                "name": "Implement core functionality",
                "base_hours": total_hours * 0.5,
                "description": "Write the main implementation"
            },
            {
                "name": "Create tests",
                "base_hours": total_hours * 0.15,
                "description": "Write comprehensive tests"
            },
            {
                "name": "Review and refine",
                "base_hours": total_hours * 0.1,
                "description": "Review code and make improvements"
            }
        ]
        
        return tasks
    
    def _adjust_estimates(
        self,
        tasks: List[Dict[str, Any]],
        complexity: str,
        velocity_data: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Adjust time estimates based on complexity and velocity.
        
        Args:
            tasks: List of tasks with base_hours
            complexity: Request complexity level
            velocity_data: Velocity metrics from Tier 3
        
        Returns:
            Tasks with adjusted estimated_hours
        """
        # Complexity multipliers
        complexity_multipliers = {
            "simple": 0.8,
            "medium": 1.0,
            "complex": 1.5
        }
        
        complexity_mult = complexity_multipliers.get(complexity, 1.0)
        
        # Velocity adjustment (if available)
        velocity_mult = 1.0
        if velocity_data:
            avg_velocity = velocity_data.get("average_velocity", 15.0)
            # Adjust based on team velocity (higher velocity = can do more faster)
            if avg_velocity > 20:
                velocity_mult = 0.9
            elif avg_velocity < 10:
                velocity_mult = 1.1
        
        # Apply adjustments
        for task in tasks:
            base = task.get("base_hours", 1.0)
            task["estimated_hours"] = round(base * complexity_mult * velocity_mult, 1)
        
        return tasks
    
    def _identify_dependencies(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify task dependencies.
        
        Args:
            tasks: List of tasks
        
        Returns:
            List of dependency relationships
        """
        dependencies = []
        
        # Simple heuristic: tasks must be done in order
        for i in range(1, len(tasks)):
            dependencies.append({
                "task_id": tasks[i]["id"],
                "depends_on": tasks[i-1]["id"],
                "type": "sequential"
            })
        
        return dependencies
    
    def _assess_risks(
        self,
        request: AgentRequest,
        complexity: str,
        tasks: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Assess risks in the work plan.
        
        Args:
            request: The agent request
            complexity: Request complexity level
            tasks: List of tasks
        
        Returns:
            List of risk descriptions
        """
        risks = []
        
        # Complexity risk
        if complexity == "complex":
            risks.append("High complexity - may require additional time or resources")
        
        # Scope risk
        if len(tasks) > 10:
            risks.append("Large number of tasks - consider breaking into smaller features")
        
        # Time risk
        total_hours = sum(t.get("estimated_hours", 0) for t in tasks)
        if total_hours > 20:
            risks.append("Extended timeline - consider phased delivery")
        
        return risks
    
    def _calculate_task_priority(
        self,
        task: Dict[str, Any],
        index: int,
        total: int
    ) -> str:
        """
        Calculate task priority.
        
        Args:
            task: Task dictionary
            index: Task index in list
            total: Total number of tasks
        
        Returns:
            Priority level string
        """
        # First tasks are higher priority
        if index < total * 0.3:
            return "high"
        elif index < total * 0.7:
            return "medium"
        else:
            return "low"
    
    def _store_workflow_pattern(
        self,
        request: AgentRequest,
        tasks: List[Dict[str, Any]],
        complexity: str
    ) -> None:
        """
        Store workflow pattern in Tier 2 for future learning.
        
        Args:
            request: The agent request
            tasks: Generated tasks
            complexity: Request complexity
        """
        if not self.tier2:
            return
        
        try:
            pattern_content = {
                "tasks": tasks,
                "complexity": complexity,
                "total_hours": sum(t.get("estimated_hours", 0) for t in tasks)
            }
            
            self.tier2.add_pattern(
                pattern_type="workflow",
                title=f"Workflow: {request.user_message[:50]}",
                content=str(pattern_content)
            )
            
            self.logger.info("Stored workflow pattern in Tier 2")
        except Exception as e:
            self.logger.warning(f"Failed to store workflow pattern: {str(e)}")
