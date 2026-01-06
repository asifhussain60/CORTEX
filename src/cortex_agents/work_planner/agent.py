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

# Import learning system
try:
    from src.learning.event_collector import get_global_collector
    from src.learning.event_taxonomy import LearningEvent, EventType
except ImportError:
    get_global_collector = None
    LearningEvent = None
    EventType = None

# Import Planning Orchestrator for enhanced planning features
try:
    from src.orchestrators.planning_orchestrator import PlanningOrchestrator
    PLANNING_ORCHESTRATOR_AVAILABLE = True
except ImportError:
    PLANNING_ORCHESTRATOR_AVAILABLE = False
    PlanningOrchestrator = None


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
        
        self.complexity_analyzer = ComplexityAnalyzer()
        self.workflow_finder = WorkflowFinder(tier2_kg)
        self.velocity_tracker = VelocityTracker(tier3_context)
        self.task_generator = TaskGenerator()
        self.estimator = Estimator()
        self.dependency_manager = DependencyManager()
        self.risk_assessor = RiskAssessor()
        self.priority_calculator = PriorityCalculator()
        self.pattern_storage = PatternStorage(tier2_kg)
        
        # Initialize Planning Orchestrator for enhanced features
        # DISABLED: P01 Fix - Planning intents should route directly to orchestrator, not through agent
        # Architecture violation: Orchestrators expect autonomous terminal execution, not nested agent calls
        self._planning_orchestrator = None
        # if PLANNING_ORCHESTRATOR_AVAILABLE:
        #     try:
        #         from src.config import config
        #         self._planning_orchestrator = PlanningOrchestrator(cortex_root=str(config.root_path))
        #         self.logger.info("✅ Planning Orchestrator initialized for enhanced planning")
        #     except Exception as e:
        #         self.logger.warning(f"Planning Orchestrator initialization failed: {e}")
        #         self._planning_orchestrator = None
    
    def can_handle(self, request: AgentRequest) -> bool:
        """
        Check if this agent can handle the request.
        
        P01 FIX: WorkPlanner now handles ONLY task breakdown/estimation.
        Planning intents should route to Planning Orchestrator via MasterOrchestrator.
        
        Valid intents:
        - TASK_BREAKDOWN: "estimate", "breakdown", "how long"
        - Simple decomposition requests (no architecture review, no threat modeling)
        
        Invalid intents (route to Planning Orchestrator instead):
        - "plan feature", "create plan", "plan for" (comprehensive planning)
        - Requests mentioning architecture/security/threat model
        """
        # P01 FIX: Explicitly reject "plan" intents (should route to orchestrator)
        message_lower = request.user_message.lower()
        
        # If message contains "plan" + planning keywords, reject (orchestrator handles it)
        planning_keywords = ['plan feature', 'create plan', 'plan for', 'planning', 
                            'architecture', 'threat model', 'security', 'proceed with', 'epic']
        if any(keyword in message_lower for keyword in planning_keywords):
            return False
        
        # Accept only task breakdown intents
        valid_intents = [
            IntentType.FEATURE.value,
            IntentType.BUG.value,
            IntentType.REFACTOR.value,
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
            
            # Emit PLANNING_REQUEST event
            if get_global_collector and LearningEvent and EventType:
                try:
                    event = LearningEvent(
                        event_type=EventType.PLANNING_REQUEST,
                        component="WorkPlanner",
                        metadata={"intent": request.intent, "context_size": len(request.context)}
                    )
                    get_global_collector().capture_event(event)
                except Exception as e:
                    self.logger.debug(f"Learning event capture failed: {e}")
            
            # Detect if this is a full feature planning request (use orchestrator)
            # vs simple task breakdown (use internal logic)
            if self._should_use_orchestrator(request):
                return self._execute_with_orchestrator(request)
            
            # Analyze complexity
            complexity = self.complexity_analyzer.analyze(request)
            self.logger.info(f"Detected complexity: {complexity}")
            
            # Find similar workflows from Tier 2
            similar_workflows = self.workflow_finder.find_similar(request)
            
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
            
            # Emit PLAN_VALIDATED event
            if get_global_collector and LearningEvent and EventType:
                try:
                    event = LearningEvent(
                        event_type=EventType.PLAN_VALIDATED,
                        component="WorkPlanner",
                        metadata={
                            "task_count": len(tasks),
                            "total_hours": total_hours,
                            "complexity": complexity
                        }
                    )
                    get_global_collector().capture_event(event)
                except Exception as e:
                    self.logger.debug(f"Learning event capture failed: {e}")
            
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
    
    def _should_use_orchestrator(self, request: AgentRequest) -> bool:
        """
        Determine if request should use Planning Orchestrator (enhanced features).
        
        Criteria for orchestrator:
        - Orchestrator is available
        - Request mentions "plan feature" or "create plan"
        - Request includes feature/security/auth/api keywords
        - NOT a simple "estimate" or "breakdown" request
        
        Args:
            request: Agent request
            
        Returns:
            True if should use orchestrator, False for simple breakdown
        """
        if not self._planning_orchestrator:
            return False
        
        message_lower = request.user_message.lower()
        
        # Keywords that trigger orchestrator (complex planning)
        orchestrator_keywords = [
            'plan feature', 'create plan', 'plan for',
            'authentication', 'security', 'migration',
            'api', 'integration', 'deployment',
            'threat model', 'architecture',
            'user story', 'feature request'
        ]
        
        # Keywords that stay in simple mode (quick breakdowns)
        simple_keywords = [
            'estimate', 'breakdown', 'how long',
            'time estimate', 'effort'
        ]
        
        # If explicitly asking for simple estimate, don't use orchestrator
        if any(keyword in message_lower for keyword in simple_keywords):
            return False
        
        # If request matches orchestrator criteria, use enhanced planning
        if any(keyword in message_lower for keyword in orchestrator_keywords):
            return True
        
        # Default: use orchestrator if request intent is "plan" or "feature"
        return request.intent.lower() in ['plan', 'feature']
    
    def _execute_with_orchestrator(self, request: AgentRequest) -> AgentResponse:
        """
        Execute planning request using Planning Orchestrator for enhanced features.
        
        This provides:
        - Contextual architectural review (REQ-003)
        - Interactive DoR refinement (REQ-002)
        - Threat modeling integration (REQ-007)
        - Visual progress bars
        - Git checkpoints
        - TDD integration
        
        Args:
            request: Agent request
            
        Returns:
            AgentResponse from orchestrator
        """
        try:
            self.logger.info("🚀 Using Planning Orchestrator for enhanced features")
            
            # Extract feature requirements from request
            feature_requirements = request.user_message
            
            # Execute with orchestrator
            success, output_path, message = self._planning_orchestrator.generate_incremental_plan(
                feature_requirements=feature_requirements,
                checkpoint_callback=None  # Auto-approve for agent mode
            )
            
            if success and output_path:
                # Load generated plan to extract details
                plan_success, plan_data, errors = self._planning_orchestrator.load_plan(output_path)
                
                if plan_success and plan_data:
                    metadata = plan_data.get('metadata', {})
                    phases = plan_data.get('phases', [])
                    total_tasks = sum(len(phase.get('tasks', [])) for phase in phases)
                    
                    return AgentResponse(
                        success=True,
                        result={
                            'plan_path': str(output_path),
                            'plan_data': plan_data,
                            'phases': len(phases),
                            'total_tasks': total_tasks,
                            'estimated_hours': metadata.get('estimated_hours', 0),
                            'enhanced_features': {
                                'review_orchestrator': True,
                                'threat_modeling': True,
                                'progress_monitoring': True,
                                'tdd_integration': True
                            }
                        },
                        message=f"✅ {message}\n\n📊 Enhanced Planning Features Used:\n"
                                f"   🔍 Architectural Review\n"
                                f"   🔒 Threat Modeling\n"
                                f"   📈 Visual Progress Tracking\n"
                                f"   🧪 TDD Integration\n\n"
                                f"📋 Plan saved: {output_path.name}",
                        agent_name=self.name,
                        metadata={
                            'orchestrator_used': True,
                            'plan_path': str(output_path),
                            'phases': len(phases),
                            'total_tasks': total_tasks
                        }
                    )
            
            # Orchestrator returned but no plan generated
            return AgentResponse(
                success=False,
                result={'message': message},
                message=f"⚠️  Planning incomplete: {message}",
                agent_name=self.name
            )
            
        except Exception as e:
            self.logger.error(f"Orchestrator execution failed: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
            # Fallback to simple planning
            self.logger.warning("Falling back to simple task breakdown")
            return self._execute_simple_breakdown(request)
    
    def _execute_simple_breakdown(self, request: AgentRequest) -> AgentResponse:
        """
        Execute simple task breakdown without orchestrator.
        
        This is the original WorkPlanner logic for quick estimates.
        
        Args:
            request: Agent request
            
        Returns:
            AgentResponse with task breakdown
        """
        # Original logic continues here
        complexity = self.complexity_analyzer.analyze(request)
        similar_workflows = self.workflow_finder.find_similar(request)
        velocity_data = self.velocity_tracker.get_metrics()
        
        tasks = self._generate_task_breakdown(
            request, complexity, similar_workflows, velocity_data
        )
        
        tasks = self.dependency_manager.identify(tasks)
        file_paths = extract_file_paths(request.user_message)
        tasks, risk_factors = self.risk_assessor.assess(
            tasks, complexity, len(file_paths)
        )
        
        total_hours = sum(t.get("estimated_hours", 0) for t in tasks)
        
        return AgentResponse(
            success=True,
            result={
                "tasks": tasks,
                "task_count": len(tasks),
                "total_hours": total_hours,
                "complexity": complexity,
                "risks": risk_factors
            },
            message=f"Created {len(tasks)} tasks with {total_hours} hour estimate (complexity: {complexity})",
            agent_name=self.name,
            metadata={
                "task_count": len(tasks),
                "total_hours": total_hours,
                "complexity": complexity
            }
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
