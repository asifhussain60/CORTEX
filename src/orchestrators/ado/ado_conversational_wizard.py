"""
ADO Conversational Wizard - Multi-turn Interactive Work Item Creation

Provides guided conversational flow for complex ADO work items requiring
iterative refinement. Complements existing auto-generation with interactive mode.

Architecture:
    - 7-stage wizard flow (basic_info → acceptance_criteria → dor → dod → estimation → dependencies → review)
    - Session state management via in-memory dictionary
    - Vision API integration for screenshot-based acceptance criteria
    - Natural language processing for conversational responses
    - Skip/default support for optional stages
    - Approval loop for final review

Usage:
    >>> wizard = ADOConversationalWizard()
    >>> response = wizard.start_wizard("Authentication feature with SSO")
    >>> print(response.prompt)
    >>> # User responds: "Feature, High priority, Large effort"
    >>> response = wizard.process_response(
    ...     session_id=response.session_id,
    ...     user_input="Feature, High priority, Large effort"
    ... )

Version: 1.0.0
Author: Asif Hussain
Copyright: © 2025-2026 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import logging
import re
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field


# Configure module logger
logger = logging.getLogger(__name__)


class WizardStage(Enum):
    """Wizard progression stages for ADO work item creation."""
    BASIC_INFO = "basic_info"              # Feature name, type, priority
    ACCEPTANCE_CRITERIA = "acceptance_criteria"  # Vision API or manual entry
    DEFINITION_OF_READY = "dor"           # Assumptions, constraints
    DEFINITION_OF_DONE = "dod"            # Completion criteria
    ESTIMATION = "estimation"              # Story points, effort
    DEPENDENCIES = "dependencies"          # Related work items
    REVIEW = "review"                      # Final approval
    COMPLETE = "complete"


@dataclass
class WizardResponse:
    """Response object for wizard interactions."""
    session_id: str
    stage: WizardStage
    prompt: str
    context: Dict[str, Any]
    can_skip: bool = False
    validation_errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkItemData:
    """Structured work item data collected through wizard."""
    feature_name: str
    work_item_type: str = "Story"
    priority: str = "Medium"
    effort: str = "M"
    acceptance_criteria: List[str] = field(default_factory=list)
    definition_of_ready: Dict[str, List[str]] = field(default_factory=dict)
    definition_of_done: List[str] = field(default_factory=list)
    story_points: Optional[int] = None
    dependencies: List[str] = field(default_factory=list)
    vision_context: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ADOConversationalWizard:
    """
    Multi-turn conversational wizard for ADO work item creation.
    
    Provides guided conversation flow for complex work items with:
    - Natural language interaction
    - Vision API integration
    - Iterative refinement
    - Skip/default handling
    - Session persistence
    
    Attributes:
        sessions: In-memory session storage {session_id: session_data}
        state_db: Optional database for session persistence
        vision_api: Optional Vision API for screenshot analysis
    
    Example:
        >>> wizard = ADOConversationalWizard()
        >>> response = wizard.start_wizard("User authentication system")
        >>> # Process user responses
        >>> response = wizard.process_response(
        ...     session_id=response.session_id,
        ...     user_input="Feature, High, XL"
        ... )
    """
    
    def __init__(self, state_db: Optional[Any] = None, vision_api: Optional[Any] = None):
        """
        Initialize ADO Conversational Wizard.
        
        Args:
            state_db: Optional database for session persistence
            vision_api: Optional Vision API for screenshot analysis
        """
        self.state_db = state_db
        self.vision_api = vision_api
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        logger.info("ADO Conversational Wizard initialized")
    
    def start_wizard(self, initial_input: str) -> WizardResponse:
        """
        Initiate wizard with feature description.
        
        Args:
            initial_input: User's initial feature description
            
        Returns:
            WizardResponse with first stage prompt
        """
        session_id = str(uuid.uuid4())
        
        # Parse initial feature info
        feature_name = self._extract_feature_name(initial_input)
        
        # Initialize session state
        self.sessions[session_id] = {
            "stage": WizardStage.BASIC_INFO,
            "data": WorkItemData(
                feature_name=feature_name,
                metadata={
                    "initial_input": initial_input,
                    "created_at": datetime.utcnow().isoformat(),
                    "session_id": session_id
                }
            ),
            "history": []
        }
        
        # Generate first prompt
        prompt = self._generate_basic_info_prompt(feature_name)
        
        logger.info(f"Wizard session started: {session_id}, feature: {feature_name}")
        
        return WizardResponse(
            session_id=session_id,
            stage=WizardStage.BASIC_INFO,
            prompt=prompt,
            context={"feature_name": feature_name}
        )
    
    def process_response(
        self,
        session_id: str,
        user_input: str,
        vision_context: Optional[Dict[str, Any]] = None
    ) -> WizardResponse:
        """
        Process user response and advance wizard stage.
        
        Args:
            session_id: Active wizard session ID
            user_input: User's conversational response
            vision_context: Optional Vision API analysis (screenshot)
            
        Returns:
            WizardResponse for next stage or completion
            
        Raises:
            ValueError: If session ID is invalid
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Invalid session ID: {session_id}")
        
        current_stage = session["stage"]
        
        # Add to history
        session["history"].append({
            "stage": current_stage.value,
            "input": user_input,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Process current stage response
        validation_errors = self._process_stage_data(
            session, current_stage, user_input, vision_context
        )
        
        if validation_errors:
            # Re-prompt with errors
            return WizardResponse(
                session_id=session_id,
                stage=current_stage,
                prompt=self._generate_stage_prompt(current_stage, session["data"]),
                context=self._get_session_context(session),
                validation_errors=validation_errors
            )
        
        # Advance to next stage
        next_stage = self._get_next_stage(current_stage)
        session["stage"] = next_stage
        
        if next_stage == WizardStage.COMPLETE:
            # Generate final ADO work item
            ado_item = self._generate_ado_from_session(session)
            return self._finalize_wizard(session_id, ado_item)
        
        # Generate prompt for next stage
        prompt = self._generate_stage_prompt(next_stage, session["data"])
        
        logger.info(f"Session {session_id}: Advanced to stage {next_stage.value}")
        
        return WizardResponse(
            session_id=session_id,
            stage=next_stage,
            prompt=prompt,
            context=self._get_session_context(session),
            can_skip=self._is_optional_stage(next_stage)
        )
    
    def _extract_feature_name(self, input_text: str) -> str:
        """
        Extract feature name from initial input.
        
        Args:
            input_text: Raw user input
            
        Returns:
            Cleaned feature name
        """
        # Remove common prefixes
        cleaned = re.sub(r'^(create|implement|build|add|develop)\s+', '', input_text, flags=re.IGNORECASE)
        
        # Capitalize first letter
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]
        
        return cleaned.strip() or "Untitled Feature"
    
    def _generate_basic_info_prompt(self, feature_name: str) -> str:
        """Generate interactive prompt for basic work item info."""
        return f"""📋 **ADO Work Item Wizard - Basic Information**

Feature: **{feature_name}**

Please provide the following (or say 'continue' for defaults):

1. **Work Item Type:** Story / Feature / Epic / Task / Bug (default: Story)
2. **Priority:** High / Medium / Low (default: Medium)
3. **Estimated Effort:** XS / S / M / L / XL (default: M)

**Example:** "Feature, High priority, Large effort"
**Example:** "Story, Medium, XL" 
**Example:** "continue" (uses defaults)

Your response:"""
    
    def _generate_acceptance_criteria_prompt(self, data: WorkItemData) -> str:
        """Generate prompt for acceptance criteria stage."""
        return f"""✅ **Acceptance Criteria for {data.feature_name}**

Define what "done" looks like for this {data.work_item_type}.

**Options:**
1. **Screenshot:** Attach a UI mockup/screenshot and I'll extract criteria using Vision API
2. **List:** Provide numbered list (e.g., "1. User can login, 2. Session persists")
3. **Skip:** Say "skip" for auto-generation during final review

**Vision API Available:** Yes (attach screenshot to your next message)

Your response:"""
    
    def _generate_dor_prompt(self, data: WorkItemData) -> str:
        """Generate prompt for Definition of Ready."""
        return f"""📝 **Definition of Ready (DoR) - Prerequisites**

What needs to be in place **before** work begins on "{data.feature_name}"?

**Categories:**
- **Assumptions:** What are we assuming? (e.g., "Users have email addresses")
- **Constraints:** Technical limitations? (e.g., "Must use existing auth library")
- **Dependencies:** External blockers? (e.g., "API endpoint must be deployed")

**Example:** "Assumptions: Users have valid email. Constraints: Use OAuth 2.0. Dependencies: None"
**Or say "skip"** to use standard DoR template

Your response:"""
    
    def _generate_dod_prompt(self, data: WorkItemData) -> str:
        """Generate prompt for Definition of Done."""
        return f"""✔️ **Definition of Done (DoD) - Completion Criteria**

What must be completed before "{data.feature_name}" is considered done?

**Common criteria:**
- Code complete with tests
- Documentation updated
- Security review passed
- Deployed to staging

**Example:** "Code complete, unit tests pass, docs updated, deployed to staging"
**Or say "skip"** to use standard DoD checklist

Your response:"""
    
    def _generate_estimation_prompt(self, data: WorkItemData) -> str:
        """Generate prompt for story point estimation."""
        return f"""🎯 **Estimation - Story Points**

How complex is "{data.feature_name}"?

**Effort Level:** {data.effort}

**Story Point Suggestions:**
- XS: 1-2 points (trivial change)
- S: 3 points (simple feature)
- M: 5 points (standard feature)
- L: 8 points (complex feature)
- XL: 13 points (very complex/multiple sprints)

**Provide story points:** "5 points" or "8" or "skip" for auto-calculation

Your response:"""
    
    def _generate_dependencies_prompt(self, data: WorkItemData) -> str:
        """Generate prompt for dependencies."""
        return f"""🔗 **Dependencies - Related Work**

Does "{data.feature_name}" depend on other work items or external factors?

**Examples:**
- "Depends on work item #12345"
- "Blocked by API deployment"
- "Requires database migration first"

**Or say "none"** if no dependencies exist

Your response:"""
    
    def _generate_review_prompt(self, data: WorkItemData) -> str:
        """Generate final review prompt with preview."""
        preview = self._format_work_item_preview(data)
        
        return f"""📋 **Final Review - ADO Work Item Preview**

{preview}

**Actions:**
- **approve** - Create this work item
- **refine [stage]** - Go back to edit (e.g., "refine acceptance criteria")
- **cancel** - Abandon wizard

Your response:"""
    
    def _generate_stage_prompt(self, stage: WizardStage, data: WorkItemData) -> str:
        """Generate prompt for given stage."""
        prompt_generators = {
            WizardStage.BASIC_INFO: self._generate_basic_info_prompt,
            WizardStage.ACCEPTANCE_CRITERIA: self._generate_acceptance_criteria_prompt,
            WizardStage.DEFINITION_OF_READY: self._generate_dor_prompt,
            WizardStage.DEFINITION_OF_DONE: self._generate_dod_prompt,
            WizardStage.ESTIMATION: self._generate_estimation_prompt,
            WizardStage.DEPENDENCIES: self._generate_dependencies_prompt,
            WizardStage.REVIEW: self._generate_review_prompt
        }
        
        generator = prompt_generators.get(stage)
        if generator:
            if stage == WizardStage.BASIC_INFO:
                return generator(data.feature_name)
            else:
                return generator(data)
        
        return f"Stage {stage.value} prompt generation not implemented"
    
    def _process_stage_data(
        self,
        session: Dict[str, Any],
        stage: WizardStage,
        user_input: str,
        vision_context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """
        Process user input for current stage and update session data.
        
        Returns:
            List of validation errors (empty if valid)
        """
        data: WorkItemData = session["data"]
        errors = []
        
        if stage == WizardStage.BASIC_INFO:
            errors = self._process_basic_info(data, user_input)
        
        elif stage == WizardStage.ACCEPTANCE_CRITERIA:
            errors = self._process_acceptance_criteria(data, user_input, vision_context)
        
        elif stage == WizardStage.DEFINITION_OF_READY:
            errors = self._process_dor(data, user_input)
        
        elif stage == WizardStage.DEFINITION_OF_DONE:
            errors = self._process_dod(data, user_input)
        
        elif stage == WizardStage.ESTIMATION:
            errors = self._process_estimation(data, user_input)
        
        elif stage == WizardStage.DEPENDENCIES:
            errors = self._process_dependencies(data, user_input)
        
        elif stage == WizardStage.REVIEW:
            errors = self._process_review(data, user_input, session)
        
        return errors
    
    def _process_basic_info(self, data: WorkItemData, user_input: str) -> List[str]:
        """Process basic info stage input."""
        input_lower = user_input.lower()
        
        # Check for continue/skip
        if input_lower in ['continue', 'skip', 'default', 'defaults']:
            return []  # Keep defaults
        
        # Parse input
        parts = [p.strip() for p in user_input.split(',')]
        
        # Work item type (first part)
        if len(parts) >= 1:
            wi_type = parts[0].title()
            if wi_type in ['Story', 'Feature', 'Epic', 'Task', 'Bug']:
                data.work_item_type = wi_type
        
        # Priority (second part or keyword)
        for part in parts:
            part_lower = part.lower()
            if any(pri in part_lower for pri in ['high', 'medium', 'low']):
                if 'high' in part_lower:
                    data.priority = 'High'
                elif 'medium' in part_lower:
                    data.priority = 'Medium'
                elif 'low' in part_lower:
                    data.priority = 'Low'
                break
        
        # Effort (look for size keywords)
        for part in parts:
            part_upper = part.upper()
            if any(size in part_upper for size in ['XS', 'S', 'M', 'L', 'XL']):
                for size in ['XS', 'S', 'M', 'L', 'XL']:
                    if size in part_upper:
                        data.effort = size
                        break
                break
        
        logger.debug(f"Basic info processed: type={data.work_item_type}, priority={data.priority}, effort={data.effort}")
        return []
    
    def _process_acceptance_criteria(
        self,
        data: WorkItemData,
        user_input: str,
        vision_context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Process acceptance criteria input."""
        input_lower = user_input.lower()
        
        if input_lower in ['skip', 'auto']:
            data.acceptance_criteria = ["[Auto-generated during review]"]
            return []
        
        # Vision context provided
        if vision_context:
            data.vision_context = vision_context
            # Extract UI elements as acceptance criteria
            ui_elements = vision_context.get('ui_elements', [])
            if ui_elements:
                data.acceptance_criteria = [
                    f"UI Element: {elem}" for elem in ui_elements[:5]
                ]
            else:
                data.acceptance_criteria = ["[Vision analysis: See attached screenshot]"]
            return []
        
        # Manual list (numbered or bulleted)
        lines = user_input.strip().split('\n')
        criteria = []
        for line in lines:
            # Remove numbering/bullets
            cleaned = re.sub(r'^\s*[\d\-\*\•]+[\.\)]\s*', '', line).strip()
            if cleaned:
                criteria.append(cleaned)
        
        if criteria:
            data.acceptance_criteria = criteria
            return []
        
        # Single line
        if user_input.strip():
            data.acceptance_criteria = [user_input.strip()]
            return []
        
        return ["Please provide at least one acceptance criterion or say 'skip'"]
    
    def _process_dor(self, data: WorkItemData, user_input: str) -> List[str]:
        """Process Definition of Ready input."""
        input_lower = user_input.lower()
        
        if input_lower in ['skip', 'none', 'standard']:
            data.definition_of_ready = {
                "assumptions": ["Standard assumptions apply"],
                "constraints": ["No specific constraints"],
                "dependencies": []
            }
            return []
        
        # Parse categories
        dor = {"assumptions": [], "constraints": [], "dependencies": []}
        
        # Simple keyword-based parsing
        if 'assumption' in input_lower:
            # Extract assumptions
            match = re.search(r'assumption[s]?:\s*(.+?)(?=constraint|dependenc|$)', user_input, re.IGNORECASE | re.DOTALL)
            if match:
                dor["assumptions"] = [match.group(1).strip()]
        
        if 'constraint' in input_lower:
            match = re.search(r'constraint[s]?:\s*(.+?)(?=assumption|dependenc|$)', user_input, re.IGNORECASE | re.DOTALL)
            if match:
                dor["constraints"] = [match.group(1).strip()]
        
        if 'depend' in input_lower:
            match = re.search(r'dependenc[y|ies]+:\s*(.+?)(?=assumption|constraint|$)', user_input, re.IGNORECASE | re.DOTALL)
            if match:
                dep_text = match.group(1).strip()
                if dep_text.lower() != 'none':
                    dor["dependencies"] = [dep_text]
        
        # Fallback: treat entire input as assumptions
        if not any(dor.values()):
            dor["assumptions"] = [user_input.strip()]
        
        data.definition_of_ready = dor
        return []
    
    def _process_dod(self, data: WorkItemData, user_input: str) -> List[str]:
        """Process Definition of Done input."""
        input_lower = user_input.lower()
        
        if input_lower in ['skip', 'standard']:
            data.definition_of_done = [
                "Code complete",
                "Tests passing",
                "Documentation updated",
                "Code review completed"
            ]
            return []
        
        # Parse list
        lines = user_input.strip().split('\n')
        dod = []
        for line in lines:
            cleaned = re.sub(r'^\s*[\d\-\*\•]+[\.\)]\s*', '', line).strip()
            if cleaned:
                dod.append(cleaned)
        
        # Single line with commas
        if not dod and ',' in user_input:
            dod = [item.strip() for item in user_input.split(',') if item.strip()]
        
        # Single item
        if not dod and user_input.strip():
            dod = [user_input.strip()]
        
        if dod:
            data.definition_of_done = dod
            return []
        
        return ["Please provide at least one DoD criterion or say 'skip'"]
    
    def _process_estimation(self, data: WorkItemData, user_input: str) -> List[str]:
        """Process story point estimation."""
        input_lower = user_input.lower()
        
        if input_lower in ['skip', 'auto']:
            # Auto-calculate from effort
            effort_map = {'XS': 1, 'S': 3, 'M': 5, 'L': 8, 'XL': 13}
            data.story_points = effort_map.get(data.effort, 5)
            return []
        
        # Extract number
        match = re.search(r'(\d+)', user_input)
        if match:
            points = int(match.group(1))
            if 1 <= points <= 21:
                data.story_points = points
                return []
            else:
                return ["Story points must be between 1 and 21"]
        
        return ["Please provide story points (1-21) or say 'skip'"]
    
    def _process_dependencies(self, data: WorkItemData, user_input: str) -> List[str]:
        """Process dependencies."""
        input_lower = user_input.lower()
        
        if input_lower in ['none', 'skip', 'no']:
            data.dependencies = []
            return []
        
        # Parse list
        lines = user_input.strip().split('\n')
        deps = []
        for line in lines:
            cleaned = re.sub(r'^\s*[\d\-\*\•]+[\.\)]\s*', '', line).strip()
            if cleaned:
                deps.append(cleaned)
        
        # Single line with commas
        if not deps and ',' in user_input:
            deps = [item.strip() for item in user_input.split(',') if item.strip()]
        
        # Single item
        if not deps and user_input.strip():
            deps = [user_input.strip()]
        
        data.dependencies = deps
        return []
    
    def _process_review(
        self,
        data: WorkItemData,
        user_input: str,
        session: Dict[str, Any]
    ) -> List[str]:
        """Process final review actions."""
        input_lower = user_input.lower()
        
        if input_lower in ['approve', 'yes', 'confirm', 'create']:
            # Mark for creation
            session["approved"] = True
            return []
        
        elif input_lower in ['cancel', 'abort', 'stop']:
            session["cancelled"] = True
            return []
        
        elif 'refine' in input_lower:
            # Extract stage to refine
            for stage in WizardStage:
                if stage.value in input_lower or stage.name.lower() in input_lower:
                    session["stage"] = stage
                    return []
            return ["Please specify which stage to refine (e.g., 'refine acceptance criteria')"]
        
        return ["Please respond with 'approve', 'refine [stage]', or 'cancel'"]
    
    def _get_next_stage(self, current_stage: WizardStage) -> WizardStage:
        """Get next wizard stage."""
        stage_order = [
            WizardStage.BASIC_INFO,
            WizardStage.ACCEPTANCE_CRITERIA,
            WizardStage.DEFINITION_OF_READY,
            WizardStage.DEFINITION_OF_DONE,
            WizardStage.ESTIMATION,
            WizardStage.DEPENDENCIES,
            WizardStage.REVIEW,
            WizardStage.COMPLETE
        ]
        
        try:
            current_idx = stage_order.index(current_stage)
            return stage_order[current_idx + 1]
        except (ValueError, IndexError):
            return WizardStage.COMPLETE
    
    def _is_optional_stage(self, stage: WizardStage) -> bool:
        """Check if stage can be skipped."""
        optional_stages = [
            WizardStage.DEPENDENCIES,
            WizardStage.ESTIMATION
        ]
        return stage in optional_stages
    
    def _format_work_item_preview(self, data: WorkItemData) -> str:
        """Format work item data as markdown preview."""
        preview = f"""## {data.feature_name}

**Type:** {data.work_item_type}  
**Priority:** {data.priority}  
**Effort:** {data.effort}  
**Story Points:** {data.story_points or 'TBD'}

### Acceptance Criteria
"""
        for i, criterion in enumerate(data.acceptance_criteria, 1):
            preview += f"{i}. {criterion}\n"
        
        preview += "\n### Definition of Ready\n"
        dor = data.definition_of_ready
        if dor:
            if dor.get("assumptions"):
                preview += f"**Assumptions:** {', '.join(dor['assumptions'])}\n"
            if dor.get("constraints"):
                preview += f"**Constraints:** {', '.join(dor['constraints'])}\n"
            if dor.get("dependencies"):
                preview += f"**Dependencies:** {', '.join(dor['dependencies'])}\n"
        
        preview += "\n### Definition of Done\n"
        for i, item in enumerate(data.definition_of_done, 1):
            preview += f"{i}. {item}\n"
        
        if data.dependencies:
            preview += "\n### Dependencies\n"
            for dep in data.dependencies:
                preview += f"- {dep}\n"
        
        return preview
    
    def _generate_ado_from_session(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ADO work item structure from session data."""
        data: WorkItemData = session["data"]
        
        return {
            "title": data.feature_name,
            "type": data.work_item_type,
            "priority": data.priority,
            "effort": data.effort,
            "story_points": data.story_points,
            "acceptance_criteria": data.acceptance_criteria,
            "definition_of_ready": data.definition_of_ready,
            "definition_of_done": data.definition_of_done,
            "dependencies": data.dependencies,
            "vision_context": data.vision_context,
            "metadata": {
                "created_via": "conversational_wizard",
                "session_id": data.metadata.get("session_id"),
                "created_at": datetime.utcnow().isoformat()
            }
        }
    
    def _finalize_wizard(self, session_id: str, ado_item: Dict[str, Any]) -> WizardResponse:
        """Generate final completion response."""
        prompt = f"""🎉 **Wizard Complete!**

Work item created successfully:

**Title:** {ado_item['title']}
**Type:** {ado_item['type']}
**Priority:** {ado_item['priority']}

Next steps:
1. Work item will be created in ADO
2. All artifacts saved
3. Session complete

Session ID: {session_id}
"""
        
        logger.info(f"Wizard completed: {session_id}")
        
        return WizardResponse(
            session_id=session_id,
            stage=WizardStage.COMPLETE,
            prompt=prompt,
            context={"ado_item": ado_item},
            metadata={"completed": True}
        )
    
    def _get_session_context(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Extract context dictionary from session."""
        data: WorkItemData = session["data"]
        return {
            "feature_name": data.feature_name,
            "work_item_type": data.work_item_type,
            "priority": data.priority,
            "effort": data.effort,
            "story_points": data.story_points,
            "acceptance_criteria_count": len(data.acceptance_criteria),
            "dependencies_count": len(data.dependencies)
        }
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of wizard session state."""
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        data: WorkItemData = session["data"]
        return {
            "session_id": session_id,
            "stage": session["stage"].value,
            "feature_name": data.feature_name,
            "progress": f"{list(WizardStage).index(session['stage'])}/{len(WizardStage)-1}",
            "created_at": data.metadata.get("created_at"),
            "interaction_count": len(session["history"])
        }
    
    def cancel_wizard(self, session_id: str) -> bool:
        """Cancel active wizard session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Wizard cancelled: {session_id}")
            return True
        return False
