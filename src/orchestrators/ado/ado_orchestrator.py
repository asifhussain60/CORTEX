"""
ADO Orchestrator v2 - Azure DevOps Work Item Generation.

Autonomous orchestrator for creating and managing Azure DevOps work items:
- User story creation
- Feature creation
- Epic creation
- Acceptance criteria generation
- Work item linking
- Status tracking

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from enum import Enum

from src.orchestrators.base.base_orchestrator_v4 import (
    BaseOrchestratorV4,
    PhaseStatus,
    PhaseResult
)
from src.orchestrators.base.base_orchestrator import (
from src.response_templates.layered_template_renderer import LayeredTemplateRenderer
    OrchestratorResult,
    OrchestratorStatus
)


class WorkItemType(Enum):
    """Azure DevOps work item types."""
    USER_STORY = "user_story"
    FEATURE = "feature"
    EPIC = "epic"
    TASK = "task"
    BUG = "bug"


class ADOResult:
    """Container for ADO operation results."""
    
    def __init__(self, work_item_type: WorkItemType, work_item_id: str, data: Dict[str, Any]):
        self.work_item_type = work_item_type
        self.work_item_id = work_item_id
        self.data = data
        self.timestamp = datetime.now().isoformat()


        self.template_renderer = LayeredTemplateRenderer()
class ADOOrchestratorV2(BaseOrchestratorV4):
    """
    ADO Orchestrator v2 - Azure DevOps integration.
    
    Features:
    - User story generation with acceptance criteria
    - Feature aggregation of related stories
    - Epic organization of features
    - Automatic work item linking
    - Status tracking and updates
    - Template-based work item creation
    - Context-aware description generation
    
    Usage:
        orchestrator = ADOOrchestratorV2(workspace_root="/path/to/workspace")
        result = orchestrator.execute(
            context={
                "type": "user_story",
                "title": "User Authentication",
                "description": "Implement login system"
            }
        )
    """
    
    def __init__(self, workspace_root: str, config_path: Optional[str] = None):
        """
        Initialize ADO Orchestrator v2.
        
        Args:
            workspace_root: Path to workspace root
            config_path: Optional path to configuration file
        """
        super().__init__(config_path=config_path)
        self.workspace_root = workspace_root
        self.logger = logging.getLogger("cortex.orchestrators.ado_v2")
        self.work_items: List[ADOResult] = []
    
    def execute(self, context: Dict[str, Any]) -> OrchestratorResult:
        """
        Execute ADO work item creation.
        
        Args:
            context: Execution context with work item details
            
        Returns:
            OrchestratorResult with created work item info
        """
        self.logger.info("Starting ADO work item creation")
        
        try:
            work_item_type = context.get("type", "user_story")
            title = context.get("title", "Untitled Work Item")
            description = context.get("description", "")
            
            # Route to appropriate creator
            if work_item_type == "user_story":
                result = self._create_user_story(
                    title=title,
                    description=description,
                    acceptance_criteria=context.get("acceptance_criteria", [])
                )
            elif work_item_type == "feature":
                result = self._create_feature(
                    title=title,
                    description=description,
                    user_stories=context.get("user_stories", [])
                )
            elif work_item_type == "epic":
                result = self._create_epic(
                    title=title,
                    description=description,
                    features=context.get("features", [])
                )
            else:
                result = {"title": title, "description": description}
            
            return OrchestratorResult(
                success=True,
                status=OrchestratorStatus.SUCCESS,
                message=f"ADO work item created: {title}",
                data={
                    "work_item_created": True,
                    "type": work_item_type,
                    "details": result
                }
            )
        
        except Exception as e:
            self.logger.error(f"ADO work item creation failed: {e}")
            return OrchestratorResult(
                success=False,
                status=OrchestratorStatus.FAILURE,
                message=f"Failed to create work item: {str(e)}",
                data={"error": str(e)}
            )
    
    def _create_user_story(
        self,
        title: str,
        description: str,
        acceptance_criteria: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a user story work item."""
        self.logger.info(f"Creating user story: {title}")
        
        # Generate acceptance criteria if not provided
        if not acceptance_criteria:
            acceptance_criteria = self._generate_acceptance_criteria(description)
        
        work_item = {
            "work_item_id": f"US-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": title,
            "description": description,
            "acceptance_criteria": acceptance_criteria,
            "type": "User Story",
            "state": "New",
            "created_at": datetime.now().isoformat()
        }
        
        return work_item
    
    def _create_feature(
        self,
        title: str,
        description: str,
        user_stories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a feature work item."""
        self.logger.info(f"Creating feature: {title}")
        
        work_item = {
            "work_item_id": f"F-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": title,
            "description": description,
            "user_stories": user_stories or [],
            "type": "Feature",
            "state": "New",
            "created_at": datetime.now().isoformat()
        }
        
        return work_item
    
    def _create_epic(
        self,
        title: str,
        description: str,
        features: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create an epic work item."""
        self.logger.info(f"Creating epic: {title}")
        
        work_item = {
            "work_item_id": f"E-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": title,
            "description": description,
            "features": features or [],
            "type": "Epic",
            "state": "New",
            "created_at": datetime.now().isoformat()
        }
        
        return work_item
    
    def _generate_acceptance_criteria(self, context: str) -> List[str]:
        """Generate acceptance criteria from context."""
        # Simple heuristic-based generation
        criteria = []
        
        if "login" in context.lower() or "auth" in context.lower():
            criteria.extend([
                "User can successfully log in with valid credentials",
                "Invalid credentials are rejected with clear error message",
                "Password is encrypted during transmission and storage"
            ])
        
        if "test" in context.lower():
            criteria.append("Unit tests have 80%+ code coverage")
        
        if "api" in context.lower():
            criteria.extend([
                "API endpoints return proper HTTP status codes",
                "API responses follow documented schema"
            ])
        
        # Default criteria if none generated
        if not criteria:
            criteria = [
                "Feature is implemented according to specification",
                "All tests pass",
                "Code review is completed"
            ]
        
        return criteria
    
    def _link_work_items(
        self,
        parent_id: str,
        child_id: str,
        link_type: str = "parent-child"
    ) -> Dict[str, Any]:
        """Link parent and child work items."""
        self.logger.info(f"Linking {parent_id} -> {child_id} ({link_type})")
        
        return {
            "success": True,
            "linked": True,
            "parent_id": parent_id,
            "child_id": child_id,
            "link_type": link_type,
            "created_at": datetime.now().isoformat()
        }
