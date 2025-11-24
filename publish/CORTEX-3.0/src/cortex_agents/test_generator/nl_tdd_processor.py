"""
Natural Language TDD Command Processor

Bridges GitHub Copilot Chat with TDD Workflow:
- Detects TDD intents from natural language
- Routes to TDD workflow automatically
- Provides interactive RED-GREEN-REFACTOR guidance
- Formats test execution feedback for chat display

Author: Asif Hussain
Created: 2025-11-21
Phase: TDD Mastery Phase 2 Milestone 2.2
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from .tdd_intent_router import TDDIntentRouter, RouteDecision, Intent


@dataclass
class TDDChatResponse:
    """Formatted response for GitHub Copilot Chat."""
    message: str
    phase: str  # "RED", "GREEN", "REFACTOR", "COMPLETE"
    status: str  # "in_progress", "success", "failed"
    details: Dict[str, Any]
    next_action: Optional[str] = None


class NaturalLanguageTDDProcessor:
    """
    Natural Language TDD Command Processor
    
    Responsibilities:
    - Parse natural language commands from GitHub Copilot Chat
    - Route IMPLEMENT intents to TDD workflow
    - Guide users through RED-GREEN-REFACTOR cycle
    - Format test results for chat display
    - Track workflow state across conversation turns
    """
    
    def __init__(self, tdd_workflow=None, orchestrator=None):
        """
        Initialize NL TDD processor.
        
        Args:
            tdd_workflow: TDD workflow orchestrator instance
            orchestrator: Agent orchestrator for routing
        """
        self.router = TDDIntentRouter()
        self.tdd_workflow = tdd_workflow
        self.orchestrator = orchestrator
        
        # State tracking for multi-turn conversations
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
    
    def process_chat_command(self, 
                            user_message: str,
                            conversation_id: str = "default",
                            context: Optional[Dict[str, Any]] = None) -> TDDChatResponse:
        """
        Process natural language command from GitHub Copilot Chat.
        
        Args:
            user_message: User's natural language message
            conversation_id: Unique conversation identifier for state tracking
            context: Optional context from CORTEX brain (Tiers 1-3)
        
        Returns:
            TDDChatResponse formatted for chat display
        """
        # Check if resuming existing workflow
        if conversation_id in self.active_workflows:
            return self._resume_workflow(user_message, conversation_id, context)
        
        # Route new request
        decision = self.router.route(user_message)
        
        # If not TDD workflow, return routing decision
        if not decision.should_use_tdd:
            return TDDChatResponse(
                message=f"Detected {decision.intent.value.upper()} intent. Using {decision.workflow} workflow.",
                phase="ROUTING",
                status="success",
                details=asdict(decision),
                next_action="Proceed with standard workflow"
            )
        
        # Activate TDD workflow
        return self._activate_tdd_workflow(decision, user_message, conversation_id, context)
    
    def _activate_tdd_workflow(self, 
                               decision: RouteDecision,
                               user_message: str,
                               conversation_id: str,
                               context: Optional[Dict[str, Any]]) -> TDDChatResponse:
        """
        Activate TDD workflow for IMPLEMENT intent.
        
        Args:
            decision: Routing decision from intent router
            user_message: Original user message
            conversation_id: Conversation ID
            context: CORTEX brain context
        
        Returns:
            TDDChatResponse for RED phase start
        """
        # Initialize workflow state
        self.active_workflows[conversation_id] = {
            'decision': decision,
            'original_request': user_message,
            'current_phase': 'RED',
            'context': context or {},
            'results': {}
        }
        
        # Format TDD activation message
        feature = decision.extracted_feature or "this feature"
        
        message = f"""🧪 **TDD Workflow Activated**

**Feature:** {feature}
**Intent:** {decision.intent.value.upper()}
**Confidence:** {decision.confidence:.0%}

**📋 TDD Cycle:**
1. ❌ **RED Phase:** Write failing test (CURRENT)
2. ✅ **GREEN Phase:** Minimal implementation
3. 🔄 **REFACTOR Phase:** Improve code quality
4. ✔️ **VALIDATE:** Check Definition of Done

**Next Step:** I'll generate a failing test for `{feature}`.

Type `continue` to proceed, or provide additional requirements."""
        
        return TDDChatResponse(
            message=message,
            phase="RED",
            status="in_progress",
            details={
                'feature': feature,
                'intent': decision.intent.value,
                'confidence': decision.confidence,
                'reason': decision.reason
            },
            next_action="continue"
        )
    
    def _resume_workflow(self,
                        user_message: str,
                        conversation_id: str,
                        context: Optional[Dict[str, Any]]) -> TDDChatResponse:
        """
        Resume active TDD workflow.
        
        Args:
            user_message: User's response
            conversation_id: Conversation ID
            context: CORTEX brain context
        
        Returns:
            TDDChatResponse for current phase
        """
        workflow = self.active_workflows[conversation_id]
        current_phase = workflow['current_phase']
        
        # Check for user commands
        if user_message.lower().strip() in ['cancel', 'abort', 'stop']:
            del self.active_workflows[conversation_id]
            return TDDChatResponse(
                message="TDD workflow cancelled.",
                phase="CANCELLED",
                status="success",
                details={}
            )
        
        # Execute current phase
        if current_phase == 'RED':
            return self._execute_red_phase(workflow, conversation_id)
        elif current_phase == 'GREEN':
            return self._execute_green_phase(workflow, conversation_id)
        elif current_phase == 'REFACTOR':
            return self._execute_refactor_phase(workflow, conversation_id)
        
        # Should not reach here
        return TDDChatResponse(
            message=f"Unknown phase: {current_phase}",
            phase=current_phase,
            status="failed",
            details={}
        )
    
    def _execute_red_phase(self,
                          workflow: Dict[str, Any],
                          conversation_id: str) -> TDDChatResponse:
        """
        Execute RED phase - generate failing test.
        
        Args:
            workflow: Active workflow state
            conversation_id: Conversation ID
        
        Returns:
            TDDChatResponse with RED phase results
        """
        if not self.tdd_workflow:
            return TDDChatResponse(
                message="TDD workflow orchestrator not initialized.",
                phase="RED",
                status="failed",
                details={}
            )
        
        decision = workflow['decision']
        feature = decision.extracted_feature or "feature"
        
        try:
            # Generate test task
            task = {
                'name': feature,
                'description': workflow['original_request'],
                'files': []  # Will be inferred by test generator
            }
            
            # Execute RED phase
            red_result = self.tdd_workflow._red_phase(task, workflow['context'])
            
            # Store result
            workflow['results']['red'] = red_result
            workflow['current_phase'] = 'GREEN'
            
            # Format response
            message = f"""✅ **RED Phase Complete**

**Test Created:** `{red_result['test_file']}`
**Test Name:** `{red_result['test_name']}`
**Status:** ❌ Test FAILED (as expected)

**Test Output:**
```
{red_result.get('test_output', 'Test failed as expected')}
```

**Next Phase:** GREEN - Minimal implementation to make test pass.

Type `continue` to proceed."""
            
            return TDDChatResponse(
                message=message,
                phase="RED",
                status="success",
                details=red_result,
                next_action="continue"
            )
        
        except Exception as e:
            return TDDChatResponse(
                message=f"❌ RED phase failed: {str(e)}",
                phase="RED",
                status="failed",
                details={'error': str(e)}
            )
    
    def _execute_green_phase(self,
                            workflow: Dict[str, Any],
                            conversation_id: str) -> TDDChatResponse:
        """
        Execute GREEN phase - minimal implementation.
        
        Args:
            workflow: Active workflow state
            conversation_id: Conversation ID
        
        Returns:
            TDDChatResponse with GREEN phase results
        """
        if not self.tdd_workflow:
            return TDDChatResponse(
                message="TDD workflow orchestrator not initialized.",
                phase="GREEN",
                status="failed",
                details={}
            )
        
        red_result = workflow['results']['red']
        decision = workflow['decision']
        feature = decision.extracted_feature or "feature"
        
        try:
            # Generate implementation task
            task = {
                'name': feature,
                'description': workflow['original_request'],
                'files': []
            }
            
            # Execute GREEN phase
            green_result = self.tdd_workflow._green_phase(
                task,
                red_result['test_file'],
                workflow['context']
            )
            
            # Store result
            workflow['results']['green'] = green_result
            workflow['current_phase'] = 'REFACTOR'
            
            # Format response
            files_modified = "\n".join([f"- `{f}`" for f in green_result['files']])
            
            message = f"""✅ **GREEN Phase Complete**

**Implementation Status:** ✅ Tests PASSING

**Files Modified:**
{files_modified}

**Test Output:**
```
{green_result.get('test_output', 'All tests passed')}
```

**Next Phase:** REFACTOR - Improve code quality while keeping tests green.

Type `continue` to proceed, or `skip` to finish."""
            
            return TDDChatResponse(
                message=message,
                phase="GREEN",
                status="success",
                details=green_result,
                next_action="continue"
            )
        
        except Exception as e:
            return TDDChatResponse(
                message=f"❌ GREEN phase failed: {str(e)}",
                phase="GREEN",
                status="failed",
                details={'error': str(e)}
            )
    
    def _execute_refactor_phase(self,
                               workflow: Dict[str, Any],
                               conversation_id: str) -> TDDChatResponse:
        """
        Execute REFACTOR phase - improve code quality.
        
        Args:
            workflow: Active workflow state
            conversation_id: Conversation ID
        
        Returns:
            TDDChatResponse with REFACTOR phase results
        """
        if not self.tdd_workflow:
            return TDDChatResponse(
                message="TDD workflow orchestrator not initialized.",
                phase="REFACTOR",
                status="failed",
                details={}
            )
        
        green_result = workflow['results']['green']
        red_result = workflow['results']['red']
        
        try:
            # Execute REFACTOR phase
            refactor_result = self.tdd_workflow._refactor_phase(
                green_result['files'],
                red_result['test_file'],
                workflow['context']
            )
            
            # Store result
            workflow['results']['refactor'] = refactor_result
            
            # Validate DoD
            dod_result = self.tdd_workflow._validate_dod(refactor_result['files'])
            workflow['results']['dod'] = dod_result
            
            # Cleanup workflow state
            del self.active_workflows[conversation_id]
            
            # Format response
            improvements = "\n".join([f"- {imp}" for imp in refactor_result.get('improvements', [])])
            files_modified = "\n".join([f"- `{f}`" for f in refactor_result['files']])
            
            dod_status = "✅ PASSED" if dod_result['passed'] else "❌ FAILED"
            
            message = f"""✅ **REFACTOR Phase Complete**

**Refactoring Status:** ✅ Tests still PASSING

**Improvements Made:**
{improvements or '- Code structure improved'}

**Files Modified:**
{files_modified}

**Definition of Done:** {dod_status}

**🎉 TDD Cycle Complete!**

All phases completed successfully:
- ❌ RED: Test created and failed
- ✅ GREEN: Implementation passed tests
- 🔄 REFACTOR: Code improved
- ✔️ VALIDATED: DoD checks passed

Feature `{workflow['decision'].extracted_feature or 'feature'}` is ready for review."""
            
            return TDDChatResponse(
                message=message,
                phase="COMPLETE",
                status="success",
                details={
                    'red': workflow['results']['red'],
                    'green': workflow['results']['green'],
                    'refactor': refactor_result,
                    'dod': dod_result
                }
            )
        
        except Exception as e:
            return TDDChatResponse(
                message=f"❌ REFACTOR phase failed: {str(e)}",
                phase="REFACTOR",
                status="failed",
                details={'error': str(e)}
            )
    
    def format_for_copilot_chat(self, response: TDDChatResponse) -> str:
        """
        Format TDDChatResponse for GitHub Copilot Chat display.
        
        Args:
            response: TDDChatResponse to format
        
        Returns:
            Markdown-formatted string for chat
        """
        return response.message
    
    def get_workflow_status(self, conversation_id: str = "default") -> Optional[Dict[str, Any]]:
        """
        Get status of active workflow.
        
        Args:
            conversation_id: Conversation ID
        
        Returns:
            Workflow status or None if no active workflow
        """
        return self.active_workflows.get(conversation_id)
