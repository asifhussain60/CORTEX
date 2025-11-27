"""
Code Executor Agent - Tactical implementation specialist

Executes code changes based on planned tasks with TDD enforcement.
"""

from typing import Dict, Any
import logging

from src.cortex_agents.base_agent import BaseAgent, AgentRequest, AgentResponse
from src.core.context_management.context_injector import ContextInjector


class CodeExecutor(BaseAgent):
    """
    Executes code implementations following TDD principles.
    
    This agent:
    - Implements planned features
    - Enforces RED → GREEN → REFACTOR cycle
    - Validates syntax and structure
    - Tracks implementation progress
    """
    
    def __init__(self, name: str = "CodeExecutor", tier1_api=None, tier2_kg=None, tier3_context=None):
        """Initialize CodeExecutor agent."""
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        self.logger = logging.getLogger(__name__)
        
        # Initialize context injector (Phase 2: Context Management)
        self.context_injector = ContextInjector(format_style='compact')
    
    def can_handle(self, request: AgentRequest) -> bool:
        """
        Check if this agent can handle the request.
        
        Args:
            request: Agent request to evaluate
            
        Returns:
            True if agent can handle this request
        """
        execution_intents = [
            'execute', 'implement', 'code', 'create', 'add',
            'modify', 'update', 'build', 'develop'
        ]
        
        intent_lower = request.intent.lower()
        return any(keyword in intent_lower for keyword in execution_intents)
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute code implementation request.
        
        Args:
            request: Agent request containing implementation details
            
        Returns:
            AgentResponse with execution results
        """
        try:
            self.logger.info(f"Executing code implementation: {request.user_message}")
            
            # Extract context
            context = request.context
            task_description = request.user_message
            rule_context = context.get('rule_context', {})
            
            # Phase 2: Intelligent test determination
            requires_tests = self._determine_if_tests_needed(
                task_description=task_description,
                context=context,
                rule_context=rule_context
            )
            
            # Phase 3: Summary generation control
            skip_summary = rule_context.get('skip_summary_generation', False)
            
            # Build result
            result = {
                'status': 'acknowledged',
                'task': task_description,
                'message': 'CodeExecutor is ready to implement this task',
                'requires_tests': requires_tests,
                'skip_summary': skip_summary,
                'tdd_cycle': 'RED → GREEN → REFACTOR enforced' if requires_tests else 'Direct implementation',
                'next_step': 'Test generation required before implementation' if requires_tests else 'Direct implementation'
            }
            
            # Determine next actions based on test requirement
            next_actions = []
            if requires_tests:
                next_actions = [
                    "Generate failing tests (RED)",
                    "Implement minimal code to pass tests (GREEN)",
                    "Refactor for quality (REFACTOR)"
                ]
            else:
                next_actions = [
                    "Implement change directly",
                    "Verify syntax and structure",
                    "Track implementation progress"
                ]
            
            # Add summary note if suppressed
            if skip_summary:
                result['summary_note'] = 'Summary generation suppressed (execution-focused intent)'
            
            # Build response message
            response_message = f"Code execution request acknowledged: {task_description}"
            
            # Inject context summary (Phase 2: Context Management)
            context_data = request.context.get('unified_context', {})
            if context_data:
                response_message = self.context_injector.format_for_agent(
                    agent_name="Code Executor",
                    response_text=response_message,
                    context_data=context_data
                )
            
            return AgentResponse(
                success=True,
                result=result,
                message=response_message,
                agent_name=self.name,
                next_actions=next_actions
            )
            
        except Exception as e:
            self.logger.error(f"Code execution failed: {str(e)}")
            return AgentResponse(
                success=False,
                result={},
                message=f"Code execution failed: {str(e)}",
                agent_name=self.name,
                error=str(e)
            )
    
    def _determine_if_tests_needed(
        self, 
        task_description: str, 
        context: Dict[str, Any],
        rule_context: Dict[str, Any]
    ) -> bool:
        """
        Intelligently determine if tests are required for this change.
        
        Phase 2 Implementation: Analyzes change type to decide if TDD is needed.
        
        Strategy: 
        1. Check for compound tasks (AND, multiple verbs) - require tests
        2. Check for strong trivial patterns - skip tests
        3. Check for documentation-only changes - skip tests
        4. Check for significant changes - require tests
        5. Default to requiring tests (safety)
        
        Args:
            task_description: Description of the task
            context: Request context with additional information
            rule_context: Rule context from IntentRouter
            
        Returns:
            True if tests should be written, False otherwise
        """
        # Check if intelligent determination is enabled
        if not rule_context.get('intelligent_test_determination', False):
            # If not enabled, default to requiring tests
            return True
        
        # Analyze task description for change type
        task_lower = task_description.lower()
        
        # Step 1: Detect compound tasks (multiple actions)
        # If task has "and" or multiple verbs, it's compound -> requires tests
        has_and = ' and ' in task_lower
        action_verbs = ['add', 'create', 'implement', 'fix', 'update', 'modify']
        verb_count = sum(1 for verb in action_verbs if verb in task_lower)
        
        if has_and and verb_count > 1:
            self.logger.info(
                f"Test determination: TESTS REQUIRED "
                f"(compound task with multiple actions)"
            )
            return True
        
        # Step 2: Strong trivial patterns (explicit trivial changes)
        strong_trivial_patterns = [
            'fix typo', 'fix spelling', 'update comment', 'add comment',
            'fix whitespace', 'fix formatting', 'fix indent',
            'rename variable', 'rename file'
        ]
        
        # Check strong trivial patterns - but only if not compound
        if not has_and:
            for pattern in strong_trivial_patterns:
                if pattern in task_lower:
                    self.logger.info(
                        f"Test determination: NO TESTS NEEDED "
                        f"(detected strong trivial pattern '{pattern}')"
                    )
                    return False
        
        # Step 3: Documentation-only changes
        doc_patterns = ['add documentation', 'update documentation', 'write documentation']
        for pattern in doc_patterns:
            if pattern in task_lower:
                self.logger.info(
                    f"Test determination: NO TESTS NEEDED "
                    f"(documentation-only change)"
                )
                return False
        
        # Step 4: Significant changes that require tests
        test_required_indicators = [
            'add feature', 'implement', 'create class', 'create method',
            'business logic', 'algorithm', 'calculation', 'validation',
            'api endpoint', 'database', 'authentication', 'authorization',
            'payment', 'integration', 'state change', 'workflow'
        ]
        
        # Check for test-required indicators
        for indicator in test_required_indicators:
            if indicator in task_lower:
                self.logger.info(
                    f"Test determination: TESTS REQUIRED "
                    f"(detected '{indicator}' - significant change)"
                )
                return True
        
        # Step 5: Weak trivial indicators (standalone keywords)
        weak_trivial_indicators = [
            'typo', 'spelling', 'comment', 'readme',
            'whitespace', 'formatting'
        ]
        
        for indicator in weak_trivial_indicators:
            if indicator in task_lower:
                self.logger.info(
                    f"Test determination: NO TESTS NEEDED "
                    f"(trivial change: '{indicator}')"
                )
                return False
        
        # Default: require tests for safety
        self.logger.info(
            "Test determination: TESTS REQUIRED "
            "(default - change type unclear)"
        )
        return True


__all__ = ["CodeExecutor"]
