"""
CORTEX Entry Point Integration with Workflow Pipeline

Shows how to integrate the Workflow Pipeline System with the existing
CORTEX entry point and router.

Author: CORTEX Development Team
Version: 1.0
"""

from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime

from src.entry_point.cortex_entry import CortexEntry
from src.workflows.workflow_pipeline import (
    WorkflowDefinition,
    WorkflowOrchestrator
)


class CortexEntryWithWorkflows(CortexEntry):
    """
    Extended CORTEX entry point with workflow pipeline support
    
    Backwards compatible - falls back to original routing if no workflow specified
    """
    
    def __init__(self, brain_path: Optional[str] = None, enable_logging: bool = True):
        super().__init__(brain_path, enable_logging)
        
        # Load available workflows
        self.workflows_dir = Path(__file__).parent.parent / "workflows" / "definitions"
        self.available_workflows = self._discover_workflows()
        
        self.logger.info(f"Discovered {len(self.available_workflows)} workflows")
    
    def process(
        self,
        user_message: str,
        resume_session: bool = True,
        format_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None,
        workflow_id: Optional[str] = None  # NEW: Optional workflow specification
    ) -> str:
        """
        Process user request (with optional workflow)
        
        Args:
            user_message: User's natural language request
            resume_session: Whether to resume previous session
            format_type: Output format ("text", "json", "markdown")
            metadata: Optional metadata
            workflow_id: Optional workflow to use (e.g., "secure_feature_creation")
        
        Returns:
            Formatted response
        """
        conversation_id = self._get_conversation_id(resume_session)
        
        # Check if workflow specified or should be auto-selected
        if workflow_id or self._should_use_workflow(user_message):
            return self._process_with_workflow(
                user_message,
                conversation_id,
                workflow_id,
                format_type
            )
        else:
            # Fallback to original routing
            return super().process(
                user_message,
                resume_session=resume_session,
                format_type=format_type,
                metadata=metadata
            )
    
    def _should_use_workflow(self, user_message: str) -> bool:
        """
        Determine if request should use workflow pipeline
        
        Criteria:
        - Request mentions "security", "threat", "authentication"
        - Request is for new feature (PLAN intent)
        - Request mentions "DoD", "DoR", "definition"
        - User explicitly says "WORKFLOW:"
        
        Args:
            user_message: User's request
        
        Returns:
            True if workflow recommended
        """
        message_lower = user_message.lower()
        
        # Explicit workflow request
        if "workflow:" in message_lower:
            return True
        
        # Security-related keywords
        security_keywords = [
            "security", "threat", "authentication", "auth",
            "login", "password", "token", "permission"
        ]
        if any(keyword in message_lower for keyword in security_keywords):
            return True
        
        # DoD/DoR keywords
        dod_keywords = ["dod", "dor", "definition of done", "definition of ready"]
        if any(keyword in message_lower for keyword in dod_keywords):
            return True
        
        # Large feature keywords
        feature_keywords = ["add feature", "new feature", "implement feature"]
        if any(keyword in message_lower for keyword in feature_keywords):
            return True
        
        return False
    
    def _select_workflow(self, user_message: str, workflow_id: Optional[str]) -> str:
        """
        Select appropriate workflow
        
        Priority:
        1. User-specified workflow_id
        2. Workflow mentioned in message ("WORKFLOW: secure_feature_creation")
        3. Auto-select based on keywords
        4. Default to "quick_feature"
        
        Args:
            user_message: User's request
            workflow_id: Optionally provided workflow ID
        
        Returns:
            Workflow ID to use
        """
        # Priority 1: Explicit workflow_id parameter
        if workflow_id:
            return workflow_id
        
        # Priority 2: Workflow specified in message
        if "workflow:" in user_message.lower():
            # Extract: "WORKFLOW: secure_feature_creation"
            parts = user_message.lower().split("workflow:")
            if len(parts) > 1:
                extracted = parts[1].strip().split()[0]
                if extracted in self.available_workflows:
                    return extracted
        
        # Priority 3: Auto-select based on keywords
        message_lower = user_message.lower()
        
        # Security-related → secure_feature_creation
        security_keywords = ["security", "threat", "authentication", "auth"]
        if any(kw in message_lower for kw in security_keywords):
            return "secure_feature_creation"
        
        # DoD/DoR mentioned → secure_feature_creation (includes clarification)
        if any(kw in message_lower for kw in ["dod", "dor", "definition"]):
            return "secure_feature_creation"
        
        # Default → quick_feature
        return "quick_feature"
    
    def _process_with_workflow(
        self,
        user_message: str,
        conversation_id: str,
        workflow_id: Optional[str],
        format_type: str
    ) -> str:
        """
        Process request using workflow pipeline
        
        Args:
            user_message: User's request
            conversation_id: Conversation UUID
            workflow_id: Optional workflow ID
            format_type: Output format
        
        Returns:
            Formatted response
        """
        try:
            # Select workflow
            selected_workflow = self._select_workflow(user_message, workflow_id)
            
            self.logger.info(f"Using workflow: {selected_workflow}")
            
            # Log to Tier 1
            self.tier1.process_message(
                conversation_id,
                role="user",
                content=user_message
            )
            
            self.tier1.process_message(
                conversation_id,
                role="system",
                content=f"Using workflow: {selected_workflow}"
            )
            
            # Load workflow definition
            workflow_path = self.workflows_dir / f"{selected_workflow}.yaml"
            workflow_def = WorkflowDefinition.from_yaml(workflow_path)
            
            # Create orchestrator
            orchestrator = WorkflowOrchestrator(
                workflow_def=workflow_def,
                context_injector=self.context_injector,
                tier1_api=self.tier1
            )
            
            # Register stages (dynamic import)
            self._register_workflow_stages(orchestrator, workflow_def)
            
            # Execute workflow
            start_time = datetime.now()
            
            workflow_state = orchestrator.execute(
                user_request=user_message,
                conversation_id=conversation_id
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Log completion
            self.tier1.process_message(
                conversation_id,
                role="assistant",
                content=self._format_workflow_response(workflow_state, duration)
            )
            
            # Format response
            return self._format_workflow_response(
                workflow_state,
                duration,
                format_type
            )
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}", exc_info=True)
            
            # Log error to Tier 1
            self.tier1.process_message(
                conversation_id,
                role="system",
                content=f"Workflow failed: {str(e)}"
            )
            
            return self.formatter.format_error(
                e,
                context={"workflow": selected_workflow}
            )
    
    def _register_workflow_stages(
        self,
        orchestrator: WorkflowOrchestrator,
        workflow_def: WorkflowDefinition
    ):
        """
        Register all stages for workflow
        
        Dynamically imports stage modules and registers them.
        
        Args:
            orchestrator: Workflow orchestrator
            workflow_def: Workflow definition
        """
        from importlib import import_module
        
        for stage_def in workflow_def.stages:
            try:
                # Import stage module
                # Example: "threat_modeler" → src.workflows.stages.threat_modeler
                module = import_module(f"src.workflows.stages.{stage_def.script}")
                
                # Get stage instance via factory function
                stage_instance = module.create_stage()
                
                # Register with orchestrator
                orchestrator.register_stage(stage_def.id, stage_instance)
                
                self.logger.debug(f"Registered stage: {stage_def.id}")
                
            except ImportError as e:
                self.logger.error(
                    f"Failed to import stage '{stage_def.script}': {e}"
                )
                raise
    
    def _format_workflow_response(
        self,
        workflow_state,
        duration: float,
        format_type: str = "text"
    ) -> str:
        """
        Format workflow execution result
        
        Args:
            workflow_state: Final workflow state
            duration: Execution duration in seconds
            format_type: Output format
        
        Returns:
            Formatted response string
        """
        if format_type == "json":
            import json
            return json.dumps({
                "workflow_id": workflow_state.workflow_id,
                "duration_seconds": duration,
                "stages_completed": len(workflow_state.stage_outputs),
                "stage_statuses": {
                    k: v.value for k, v in workflow_state.stage_statuses.items()
                },
                "outputs": workflow_state.stage_outputs
            }, indent=2)
        
        elif format_type == "markdown":
            lines = [
                f"# Workflow Execution Summary",
                f"",
                f"**Workflow ID:** `{workflow_state.workflow_id}`  ",
                f"**Duration:** {duration:.1f}s  ",
                f"**Stages Completed:** {len(workflow_state.stage_outputs)}",
                f"",
                f"## Stage Results",
                f""
            ]
            
            for stage_id, status in workflow_state.stage_statuses.items():
                status_emoji = {
                    "success": "✅",
                    "failed": "❌",
                    "skipped": "⏭️"
                }.get(status.value, "❓")
                
                lines.append(f"- {status_emoji} **{stage_id}**: {status.value}")
            
            return "\n".join(lines)
        
        else:  # text
            success_count = len([
                s for s in workflow_state.stage_statuses.values()
                if s.value == "success"
            ])
            
            return (
                f"✅ Workflow completed successfully\n"
                f"\n"
                f"Duration: {duration:.1f}s\n"
                f"Stages: {success_count}/{len(workflow_state.stage_statuses)} succeeded\n"
                f"Files modified: {self._count_modified_files(workflow_state)}\n"
                f"Tests created: {self._count_tests_created(workflow_state)}\n"
            )
    
    def _count_modified_files(self, workflow_state) -> int:
        """Count files modified across all stages"""
        files = set()
        for outputs in workflow_state.stage_outputs.values():
            if isinstance(outputs, dict):
                if "files_modified" in outputs:
                    files.update(outputs["files_modified"])
        return len(files)
    
    def _count_tests_created(self, workflow_state) -> int:
        """Count tests created across all stages"""
        tests = set()
        for outputs in workflow_state.stage_outputs.values():
            if isinstance(outputs, dict):
                if "tests_created" in outputs:
                    tests.update(outputs["tests_created"])
        return len(tests)
    
    def _discover_workflows(self) -> Dict[str, str]:
        """
        Discover available workflow definitions
        
        Returns:
            Dict mapping workflow_id to file path
        """
        workflows = {}
        
        if not self.workflows_dir.exists():
            self.logger.warning(f"Workflows directory not found: {self.workflows_dir}")
            return workflows
        
        for yaml_file in self.workflows_dir.glob("*.yaml"):
            workflow_id = yaml_file.stem
            workflows[workflow_id] = str(yaml_file)
            self.logger.debug(f"Discovered workflow: {workflow_id}")
        
        return workflows


# Convenience function for quick usage
def process_with_workflow(
    user_message: str,
    workflow_id: Optional[str] = None
) -> str:
    """
    Quick helper to process request with workflow
    
    Args:
        user_message: User's request
        workflow_id: Optional workflow to use
    
    Returns:
        Response string
    
    Example:
        >>> result = process_with_workflow(
        ...     "Add authentication to login page",
        ...     workflow_id="secure_feature_creation"
        ... )
        >>> print(result)
        ✅ Workflow completed successfully
        Duration: 5.8s
        Stages: 8/8 succeeded
        ...
    """
    entry = CortexEntryWithWorkflows()
    return entry.process(
        user_message=user_message,
        workflow_id=workflow_id
    )


if __name__ == "__main__":
    # Example usage
    print("CORTEX Workflow Pipeline Integration Demo")
    print("=" * 50)
    
    # Example 1: Auto-select workflow based on keywords
    print("\n1. Auto-select workflow (security keyword):")
    result = process_with_workflow(
        "Add authentication to the login page"
    )
    print(result)
    
    # Example 2: Explicit workflow specification
    print("\n2. Explicit workflow:")
    result = process_with_workflow(
        "Add user profile page",
        workflow_id="quick_feature"
    )
    print(result)
    
    # Example 3: Workflow specified in message
    print("\n3. Workflow in message:")
    result = process_with_workflow(
        "Add dashboard. WORKFLOW: secure_feature_creation"
    )
    print(result)
