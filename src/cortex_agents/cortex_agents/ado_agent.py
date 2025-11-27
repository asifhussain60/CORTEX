"""
ADO Agent

Wrapper agent for ADO orchestrators (unified entry point, work items, code review).
Routes ADO-related intents to appropriate orchestrators.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Optional
from pathlib import Path

from .base_agent import BaseAgent, AgentRequest, AgentResponse
from .agent_types import IntentType, AgentType


class ADOAgent(BaseAgent):
    """
    Agent for handling ADO (Azure DevOps) operations.
    
    Routes requests to appropriate orchestrators:
    - Story creation: UnifiedEntryPointOrchestrator.execute_ado_story()
    - Feature creation: UnifiedEntryPointOrchestrator.execute_ado_feature()
    - Work summary: UnifiedEntryPointOrchestrator.generate_work_summary()
    - Code review: UnifiedEntryPointOrchestrator.execute_code_review()
    
    Features:
    - ADO-formatted markdown output for direct copy-paste
    - Complete work tracking (files, decisions, criteria)
    - Integration with planning and code review systems
    
    Example:
        agent = ADOAgent("ADOAgent", tier1_api, tier2_kg, tier3_context)
        
        # Create user story
        request = AgentRequest(
            intent=IntentType.ADO_STORY,
            context={"title": "User Login", "description": "..."},
            user_message="plan ado story"
        )
        response = agent.execute(request)
    """
    
    def __init__(self, name: str, tier1_api=None, tier2_kg=None, tier3_context=None):
        """Initialize ADO Agent with tier APIs."""
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        
        # Initialize orchestrators lazily (on first use)
        self._unified_orchestrator = None
    
    def _get_unified_orchestrator(self):
        """Get or create unified orchestrator instance."""
        if self._unified_orchestrator is None:
            from src.orchestrators.unified_entry_point_orchestrator import UnifiedEntryPointOrchestrator
            self._unified_orchestrator = UnifiedEntryPointOrchestrator()
            self.logger.info("Initialized UnifiedEntryPointOrchestrator")
        return self._unified_orchestrator
    
    def can_handle(self, request: AgentRequest) -> bool:
        """
        Check if this agent can handle the request.
        
        Args:
            request: The agent request
        
        Returns:
            True if intent is ADO-related
        """
        ado_intents = [
            IntentType.ADO_STORY,
            IntentType.ADO_FEATURE,
            IntentType.ADO_SUMMARY,
            IntentType.ADO_WORKITEM,
            IntentType.CODE_REVIEW
        ]
        
        try:
            # Check if intent matches ADO operations
            from .agent_types import IntentType
            if isinstance(request.intent, IntentType):
                return request.intent in ado_intents
            
            # String comparison fallback
            intent_str = str(request.intent).lower()
            return any(intent_str == ado_intent.value for ado_intent in ado_intents)
        except:
            return False
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute ADO operation based on intent.
        
        Args:
            request: The agent request
        
        Returns:
            AgentResponse with operation result and ADO-formatted summary
        """
        self.log_request(request)
        start_time = self.logger.info("Executing ADO operation")
        
        try:
            orchestrator = self._get_unified_orchestrator()
            
            # Extract parameters from request
            context = request.context or {}
            intent_str = str(request.intent).lower() if hasattr(request.intent, 'value') else str(request.intent)
            
            # Route based on intent
            if intent_str == IntentType.ADO_STORY.value:
                result = self._handle_story_creation(orchestrator, request, context)
            
            elif intent_str == IntentType.ADO_FEATURE.value:
                result = self._handle_feature_creation(orchestrator, request, context)
            
            elif intent_str == IntentType.ADO_SUMMARY.value:
                result = self._handle_summary_generation(orchestrator, request, context)
            
            elif intent_str == IntentType.CODE_REVIEW.value:
                result = self._handle_code_review(orchestrator, request, context)
            
            else:
                return AgentResponse(
                    success=False,
                    result=None,
                    message=f"Unknown ADO intent: {intent_str}"
                )
            
            # Log completion
            duration_ms = self.log_completion(start_time)
            
            # Return response with formatted message
            return AgentResponse(
                success=result.get("success", False),
                result=result,
                message=self._format_response_message(result, intent_str),
                duration_ms=duration_ms
            )
        
        except Exception as e:
            self.logger.error(f"ADO operation failed: {e}", exc_info=True)
            return AgentResponse(
                success=False,
                result=None,
                message=f"ADO operation failed: {str(e)}"
            )
    
    def _handle_story_creation(self, orchestrator, request: AgentRequest, context: dict) -> dict:
        """Handle user story creation."""
        # Extract story parameters
        title = context.get("title") or self._extract_title_from_message(request.user_message)
        description = context.get("description", "")
        acceptance_criteria = context.get("acceptance_criteria", [])
        priority = context.get("priority", "Medium")
        tags = context.get("tags", [])
        
        # Create story via orchestrator
        workflow_result = orchestrator.execute_ado_story(
            title=title,
            description=description,
            acceptance_criteria=acceptance_criteria,
            priority=priority,
            tags=tags
        )
        
        return {
            "success": True,
            "work_item_id": workflow_result.work_item_id,
            "work_item_path": workflow_result.work_item_path,
            "ado_summary": workflow_result.ado_summary,
            "operation": "create_story"
        }
    
    def _handle_feature_creation(self, orchestrator, request: AgentRequest, context: dict) -> dict:
        """Handle feature creation."""
        # Extract feature parameters
        title = context.get("title") or self._extract_title_from_message(request.user_message)
        description = context.get("description", "")
        related_stories = context.get("related_stories", [])
        priority = context.get("priority", "High")
        tags = context.get("tags", [])
        estimated_duration = context.get("estimated_duration")
        
        # Create feature via orchestrator
        workflow_result = orchestrator.execute_ado_feature(
            title=title,
            description=description,
            related_stories=related_stories,
            priority=priority,
            tags=tags,
            estimated_duration=estimated_duration
        )
        
        return {
            "success": True,
            "work_item_id": workflow_result.work_item_id,
            "work_item_path": workflow_result.work_item_path,
            "ado_summary": workflow_result.ado_summary,
            "operation": "create_feature"
        }
    
    def _handle_summary_generation(self, orchestrator, request: AgentRequest, context: dict) -> dict:
        """Handle work summary generation."""
        # Extract work item ID from context or message
        work_item_id = context.get("work_item_id") or self._extract_work_item_id(request.user_message)
        
        if not work_item_id:
            return {
                "success": False,
                "error": "Work item ID required for summary generation. Provide as parameter or in message."
            }
        
        # Generate summary via orchestrator
        success, message, summary_path = orchestrator.generate_work_summary(work_item_id)
        
        return {
            "success": success,
            "work_item_id": work_item_id,
            "summary_path": summary_path,
            "message": message,
            "operation": "generate_summary"
        }
    
    def _handle_code_review(self, orchestrator, request: AgentRequest, context: dict) -> dict:
        """Handle code review operation."""
        # Extract PR info
        pr_info = context.get("pr_info") or context.get("pr_url") or request.user_message
        depth = context.get("depth", "standard")
        focus_areas = context.get("focus_areas")
        
        # Execute code review via orchestrator
        workflow_result = orchestrator.execute_code_review(
            pr_info=pr_info,
            depth=depth,
            focus_areas=focus_areas
        )
        
        return {
            "success": True,
            "issues_found": len(workflow_result.issues_found),
            "recommendations": len(workflow_result.recommendations),
            "risk_score": workflow_result.risk_score,
            "ado_summary": workflow_result.ado_summary,
            "summary_path": workflow_result.summary_path,
            "operation": "code_review"
        }
    
    def _extract_title_from_message(self, message: str) -> str:
        """Extract title from user message (basic extraction)."""
        # Remove trigger phrases
        triggers = ["plan ado story", "create ado story", "plan ado feature", "create ado feature"]
        clean_message = message.lower()
        for trigger in triggers:
            clean_message = clean_message.replace(trigger, "").strip()
        
        # Take first sentence or first 50 chars as title
        if "." in clean_message:
            clean_message = clean_message.split(".")[0]
        
        return clean_message[:50].strip().title() or "Untitled Work Item"
    
    def _extract_work_item_id(self, message: str) -> Optional[str]:
        """Extract work item ID from message."""
        import re
        # Look for patterns like: UserStory-20251126143025, Feature-20251126143130
        pattern = r'(UserStory|Feature|Bug|Task|Epic)-(\d{14})-'
        match = re.search(pattern, message)
        if match:
            return match.group(0).rstrip('-')
        return None
    
    def _format_response_message(self, result: dict, intent: str) -> str:
        """Format user-facing response message."""
        if not result.get("success"):
            error = result.get("error", "Operation failed")
            return f"❌ ADO operation failed: {error}"
        
        operation = result.get("operation", intent)
        
        if operation == "create_story":
            work_item_id = result.get("work_item_id", "unknown")
            return (
                f"✅ User Story Created: {work_item_id}\n\n"
                f"Work item file opened in VS Code.\n"
                f"Update with implementation details as you work.\n\n"
                f"Use `generate ado summary {work_item_id}` when complete."
            )
        
        elif operation == "create_feature":
            work_item_id = result.get("work_item_id", "unknown")
            return (
                f"✅ Feature Created: {work_item_id}\n\n"
                f"Work item file opened in VS Code.\n"
                f"Link related stories and track progress.\n\n"
                f"Use `generate ado summary {work_item_id}` when complete."
            )
        
        elif operation == "generate_summary":
            summary_path = result.get("summary_path", "unknown")
            return (
                f"✅ Work Summary Generated\n\n"
                f"Summary saved to: {summary_path}\n\n"
                f"📋 Copy-Paste Instructions:\n"
                f"1. Open summary file in VS Code\n"
                f"2. Copy content from 'Summary of Work Completed' section\n"
                f"3. Open ADO work item\n"
                f"4. Paste into Description or Comments\n"
                f"5. Update status to Done/Resolved"
            )
        
        elif operation == "code_review":
            issues = result.get("issues_found", 0)
            risk = result.get("risk_score", 0)
            return (
                f"✅ Code Review Complete\n\n"
                f"Issues Found: {issues}\n"
                f"Risk Score: {risk}\n\n"
                f"ADO-formatted summary available for copy-paste."
            )
        
        return "✅ ADO operation completed successfully."
