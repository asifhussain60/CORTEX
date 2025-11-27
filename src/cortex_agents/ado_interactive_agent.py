"""
ADO Interactive Agent

Interactive Q&A workflow for Azure DevOps work item planning.
Replaces template-based workflow with conversational data collection.

Features:
- Interactive question flow for work items (User Story, Feature, Bug, Task, Epic)
- Conditional questions based on work item type
- DoR/DoD validation
- OWASP security review
- File generation in cortex-brain/documents/planning/ado/
"""

from typing import Dict, Any
from datetime import datetime
import os

from src.cortex_agents.base_interactive_agent import (
    BaseInteractiveAgent,
    ConversationState
)
from src.cortex_agents.base_agent import AgentRequest, AgentResponse
from src.cortex_agents.agent_types import IntentType


class ADOInteractiveAgent(BaseInteractiveAgent):
    """
    Interactive agent for ADO work item planning.
    
    Asks questions one-by-one to collect work item details,
    then generates planning document with DoR/DoD validation.
    
    Example Flow:
        User: "plan ado"
        Agent: "What type of work item? (User Story/Feature/Bug/Task/Epic)"
        User: "user story"
        Agent: "Title?"
        User: "Add dark mode to dashboard"
        [continues...]
        Agent: [shows preview]
        User: "approve"
        Agent: ✅ Created ADO work item planning document
    """
    
    def get_schema_name(self) -> str:
        """Return schema name for ADO planning."""
        return "ado-planning"
    
    def can_handle(self, request: AgentRequest) -> bool:
        """Check if request is for ADO planning."""
        intent = request.intent.lower() if isinstance(request.intent, str) else request.intent.value
        
        # Check intent type
        if intent == IntentType.ADO_PLANNING.value:
            return True
        
        # Check message for ADO keywords
        msg = request.user_message.lower()
        ado_triggers = [
            "plan ado", "ado item", "work item", "workitem",
            "pbi", "user story", "create ado"
        ]
        
        return any(trigger in msg for trigger in ado_triggers)
    
    def generate_output(self, state: ConversationState) -> Dict[str, Any]:
        """
        Generate ADO planning document from collected answers.
        
        Args:
            state: Completed conversation state
        
        Returns:
            Dict with file_path, content, and summary
        """
        answers = state.answers
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        work_item_type = answers.get('work_item_type', 'WorkItem').replace(' ', '')
        title_slug = self._slugify(answers.get('title', 'untitled'))
        
        ado_number = answers.get('ado_number')
        if ado_number:
            filename = f"ADO-{ado_number}-{title_slug}.md"
        else:
            filename = f"ADO-{timestamp}-{title_slug}.md"
        
        # Determine status directory
        status = "active"  # Default for new items
        file_path = os.path.join(
            "cortex-brain", "documents", "planning", "ado", status, filename
        )
        
        # Generate content
        content = self._generate_markdown(answers)
        
        # Validate DoR
        dor_validation = self._validate_definition_of_ready(answers)
        
        # Security review (if applicable)
        security_review = self._run_security_review(answers)
        
        # Create file
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "file_path": file_path,
            "content": content,
            "dor_validation": dor_validation,
            "security_review": security_review,
            "summary": self._generate_summary(answers, file_path, dor_validation)
        }
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL-safe slug."""
        import re
        # Remove special characters and replace spaces with hyphens
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:50]  # Limit length
    
    def _generate_markdown(self, answers: Dict[str, Any]) -> str:
        """Generate markdown planning document."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        lines = [
            f"# ADO Work Item Planning",
            f"**Created:** {timestamp}",
            f"**Status:** Active",
            "",
            "---",
            "",
            "## Basic Information",
            "",
            f"**Work Item Type:** {answers.get('work_item_type', 'N/A')}",
        ]
        
        if answers.get('ado_number'):
            lines.append(f"**ADO Number:** {answers.get('ado_number')}")
        
        lines.extend([
            f"**Title:** {answers.get('title', 'N/A')}",
            f"**Priority:** {answers.get('priority', 'N/A')}",
        ])
        
        if answers.get('assigned_to'):
            lines.append(f"**Assigned To:** {answers.get('assigned_to')}")
        
        if answers.get('iteration'):
            lines.append(f"**Iteration:** {answers.get('iteration')}")
        
        if answers.get('area_path'):
            lines.append(f"**Area Path:** {answers.get('area_path')}")
        
        if answers.get('tags'):
            lines.append(f"**Tags:** {answers.get('tags')}")
        
        lines.extend([
            "",
            "---",
            "",
            "## Description",
            "",
            answers.get('description', 'No description provided'),
            "",
            "---",
            "",
            "## Acceptance Criteria",
            "",
        ])
        
        # Parse acceptance criteria (comma-separated or line-separated)
        criteria = answers.get('acceptance_criteria', '')
        if ',' in criteria:
            criteria_list = [c.strip() for c in criteria.split(',')]
        else:
            criteria_list = [c.strip() for c in criteria.split('\n') if c.strip()]
        
        for criterion in criteria_list:
            lines.append(f"- [ ] {criterion}")
        
        lines.extend([
            "",
            "---",
            "",
            "## Technical Notes",
            "",
            answers.get('technical_notes', 'No technical notes provided'),
            "",
            "---",
            "",
            "## Related Work Items",
            "",
        ])
        
        if answers.get('parent_work_item'):
            lines.append(f"**Parent:** {answers.get('parent_work_item')}")
        
        if answers.get('related_work_items'):
            lines.append(f"**Related:** {answers.get('related_work_items')}")
        
        if answers.get('blocks'):
            lines.append(f"**Blocks:** {answers.get('blocks')}")
        
        if answers.get('blocked_by'):
            lines.append(f"**Blocked By:** {answers.get('blocked_by')}")
        
        # Bug-specific fields
        if answers.get('severity'):
            lines.extend([
                "",
                "---",
                "",
                "## Bug Details",
                "",
                f"**Severity:** {answers.get('severity')}",
                "",
                "**Reproduction Steps:**",
                "",
                answers.get('reproduction_steps', 'No steps provided'),
            ])
        
        lines.extend([
            "",
            "---",
            "",
            "## Definition of Ready (DoR)",
            "",
            "- [ ] Requirements documented with zero ambiguity",
            "- [ ] Dependencies identified and validated",
            "- [ ] Technical design approach agreed",
            "- [ ] Test strategy defined",
            "- [ ] Acceptance criteria measurable",
            "- [ ] Security review complete (if applicable)",
            "",
            "---",
            "",
            "## Definition of Done (DoD)",
            "",
            "- [ ] Code reviewed and approved",
            "- [ ] Unit tests written (≥80% coverage)",
            "- [ ] Integration tests passing",
            "- [ ] Documentation updated",
            "- [ ] Security scan passed",
            "- [ ] Performance benchmarks met",
            "- [ ] Deployed to staging",
            "- [ ] Acceptance criteria validated",
            "- [ ] User acceptance testing completed",
        ])
        
        return "\n".join(lines)
    
    def _validate_definition_of_ready(self, answers: Dict[str, Any]) -> Dict[str, Any]:
        """Validate against Definition of Ready checklist."""
        checks = {
            "requirements_documented": bool(answers.get('description')),
            "acceptance_criteria_defined": bool(answers.get('acceptance_criteria')),
            "technical_notes_provided": bool(answers.get('technical_notes')),
            "priority_set": bool(answers.get('priority')),
        }
        
        passing = sum(1 for v in checks.values() if v)
        total = len(checks)
        
        return {
            "passing": passing,
            "total": total,
            "percentage": (passing / total) * 100,
            "checks": checks,
            "ready": passing == total
        }
    
    def _run_security_review(self, answers: Dict[str, Any]) -> Dict[str, Any]:
        """Run OWASP security review if applicable."""
        # Simple keyword-based security check
        security_keywords = [
            'auth', 'password', 'token', 'credential', 'login',
            'api', 'database', 'sql', 'permission', 'access',
            'encrypt', 'secure', 'security'
        ]
        
        description = answers.get('description', '').lower()
        title = answers.get('title', '').lower()
        technical_notes = answers.get('technical_notes', '').lower()
        
        combined_text = f"{title} {description} {technical_notes}"
        
        security_relevant = any(kw in combined_text for kw in security_keywords)
        
        if not security_relevant:
            return {
                "required": False,
                "message": "No security-sensitive keywords detected"
            }
        
        recommendations = []
        
        if 'password' in combined_text or 'credential' in combined_text:
            recommendations.append("Ensure passwords are hashed with bcrypt/argon2")
            recommendations.append("Implement secure password reset flow")
        
        if 'auth' in combined_text or 'login' in combined_text:
            recommendations.append("Implement rate limiting for authentication endpoints")
            recommendations.append("Add multi-factor authentication support")
        
        if 'api' in combined_text:
            recommendations.append("Validate all API inputs")
            recommendations.append("Implement API rate limiting")
        
        if 'sql' in combined_text or 'database' in combined_text:
            recommendations.append("Use parameterized queries to prevent SQL injection")
            recommendations.append("Implement principle of least privilege for DB access")
        
        return {
            "required": True,
            "security_relevant": True,
            "recommendations": recommendations,
            "message": f"Security review recommended ({len(recommendations)} items)"
        }
    
    def _generate_summary(
        self,
        answers: Dict[str, Any],
        file_path: str,
        dor_validation: Dict[str, Any]
    ) -> str:
        """Generate summary message."""
        lines = [
            f"**Work Item:** {answers.get('work_item_type')} - {answers.get('title')}",
            f"**Priority:** {answers.get('priority')}",
            f"**File:** `{file_path}`",
            "",
            f"**DoR Status:** {dor_validation['passing']}/{dor_validation['total']} checks passing",
        ]
        
        if not dor_validation['ready']:
            lines.append("⚠️ **Not ready for work** - Complete DoR checklist first")
        
        return "\n".join(lines)
