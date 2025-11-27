"""
Feedback Interactive Agent

Interactive Q&A workflow for feedback submission (bugs/features/improvements).
Replaces template-based workflow with conversational feedback collection.

Features:
- Interactive question flow for feedback
- Conditional questions based on feedback type
- Auto-context capture (environment, version, etc.)
- Privacy protection (auto-redacts sensitive data)
- GitHub Gist upload option
"""

from typing import Dict, Any
from datetime import datetime
import os
import re

from src.cortex_agents.base_interactive_agent import (
    BaseInteractiveAgent,
    ConversationState
)
from src.cortex_agents.base_agent import AgentRequest, AgentResponse
from src.cortex_agents.agent_types import IntentType


class FeedbackInteractiveAgent(BaseInteractiveAgent):
    """
    Interactive agent for feedback submission.
    
    Asks questions to collect feedback details with type-specific
    conditional questions, then generates feedback report.
    
    Example Flow:
        User: "feedback"
        Agent: "What type of feedback? (Bug Report/Feature Request/Improvement Suggestion)"
        User: "bug report"
        Agent: "Title?"
        User: "Vision API fails with screenshots"
        [continues...]
        Agent: [shows preview]
        User: "approve"
        Agent: ✅ Feedback submitted and saved
    """
    
    def get_schema_name(self) -> str:
        """Return schema name for feedback."""
        return "feedback"
    
    def can_handle(self, request: AgentRequest) -> bool:
        """Check if request is for feedback."""
        intent = request.intent.lower() if isinstance(request.intent, str) else request.intent.value
        
        # Check intent type
        if intent in [IntentType.FEEDBACK.value, IntentType.REPORT_ISSUE.value]:
            return True
        
        # Check message for feedback keywords
        msg = request.user_message.lower()
        feedback_triggers = [
            "feedback", "report bug", "report issue",
            "suggest feature", "feature request",
            "improvement", "report problem"
        ]
        
        return any(trigger in msg for trigger in feedback_triggers)
    
    def generate_output(self, state: ConversationState) -> Dict[str, Any]:
        """
        Generate feedback report from collected answers.
        
        Args:
            state: Completed conversation state
        
        Returns:
            Dict with file_path, content, and summary
        """
        answers = state.answers
        
        # Auto-capture context
        context_data = self._capture_context()
        
        # Redact sensitive data
        sanitized_answers = self._sanitize_data(answers)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        feedback_type = answers.get('feedback_type', 'feedback').replace(' ', '-').lower()
        title_slug = self._slugify(answers.get('title', 'untitled'))
        
        filename = f"FEEDBACK-{timestamp}-{feedback_type}-{title_slug}.md"
        file_path = os.path.join(
            "cortex-brain", "feedback", filename
        )
        
        # Generate content
        content = self._generate_markdown(sanitized_answers, context_data)
        
        # Create file
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # GitHub Issues formatted version (optional)
        github_content = self._generate_github_format(sanitized_answers, context_data)
        
        return {
            "file_path": file_path,
            "content": content,
            "github_content": github_content,
            "context": context_data,
            "summary": self._generate_summary(sanitized_answers, file_path)
        }
    
    def _capture_context(self) -> Dict[str, Any]:
        """Auto-capture environment context."""
        import platform
        import sys
        
        context = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": sys.version.split()[0],
            "timestamp": datetime.now().isoformat(),
        }
        
        # Try to get CORTEX version
        try:
            version_file = os.path.join(
                os.path.dirname(__file__),
                "../../VERSION"
            )
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    context["cortex_version"] = f.readline().strip()
        except:
            context["cortex_version"] = "unknown"
        
        return context
    
    def _sanitize_data(self, answers: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive data from answers."""
        sanitized = answers.copy()
        
        # Patterns to redact
        sensitive_patterns = [
            (r'password["\']?\s*[:=]\s*["\']?[\w\d]+', 'password: [REDACTED]'),
            (r'token["\']?\s*[:=]\s*["\']?[\w\d]+', 'token: [REDACTED]'),
            (r'api[_-]?key["\']?\s*[:=]\s*["\']?[\w\d]+', 'api_key: [REDACTED]'),
            (r'secret["\']?\s*[:=]\s*["\']?[\w\d]+', 'secret: [REDACTED]'),
            (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN-REDACTED]'),  # SSN
            (r'\b\d{16}\b', '[CARD-REDACTED]'),  # Credit card
        ]
        
        for key, value in sanitized.items():
            if isinstance(value, str):
                for pattern, replacement in sensitive_patterns:
                    value = re.sub(pattern, replacement, value, flags=re.IGNORECASE)
                sanitized[key] = value
        
        return sanitized
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL-safe slug."""
        import re
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:50]
    
    def _generate_markdown(self, answers: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate markdown feedback report."""
        lines = [
            f"# Feedback: {answers.get('feedback_type')}",
            f"**Created:** {context['timestamp']}",
            f"**Priority:** {answers.get('priority')}",
            "",
            "---",
            "",
            "## Title",
            "",
            answers.get('title', 'No title provided'),
            "",
            "---",
            "",
            "## Description",
            "",
            answers.get('description', 'No description provided'),
            "",
        ]
        
        # Type-specific sections
        feedback_type = answers.get('feedback_type')
        
        if feedback_type == 'Bug Report':
            lines.extend([
                "---",
                "",
                "## Steps to Reproduce",
                "",
                answers.get('reproduction_steps', 'No steps provided'),
                "",
                "## Expected Behavior",
                "",
                answers.get('expected_behavior', 'Not specified'),
                "",
                "## Actual Behavior",
                "",
                answers.get('actual_behavior', 'Not specified'),
                "",
            ])
        
        if feedback_type == 'Feature Request':
            lines.extend([
                "---",
                "",
                "## Use Case",
                "",
                answers.get('use_case', 'No use case provided'),
                "",
            ])
        
        if answers.get('current_workaround'):
            lines.extend([
                "---",
                "",
                "## Current Workaround",
                "",
                answers.get('current_workaround'),
                "",
            ])
        
        if answers.get('additional_context'):
            lines.extend([
                "---",
                "",
                "## Additional Context",
                "",
                answers.get('additional_context'),
                "",
            ])
        
        lines.extend([
            "---",
            "",
            "## Environment",
            "",
            f"- **Platform:** {context['platform']} {context['platform_version']}",
            f"- **Python:** {context['python_version']}",
            f"- **CORTEX:** {context['cortex_version']}",
            f"- **Timestamp:** {context['timestamp']}",
        ])
        
        return "\n".join(lines)
    
    def _generate_github_format(self, answers: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate GitHub Issues formatted content."""
        feedback_type = answers.get('feedback_type')
        
        if feedback_type == 'Bug Report':
            label = 'bug'
        elif feedback_type == 'Feature Request':
            label = 'enhancement'
        else:
            label = 'question'
        
        lines = [
            f"**Type:** {feedback_type}",
            f"**Priority:** {answers.get('priority')}",
            f"**Labels:** {label}",
            "",
            "## Description",
            "",
            answers.get('description', 'No description provided'),
            "",
        ]
        
        if feedback_type == 'Bug Report':
            lines.extend([
                "## Steps to Reproduce",
                "",
                answers.get('reproduction_steps', 'No steps provided'),
                "",
                "## Expected Behavior",
                "",
                answers.get('expected_behavior', 'Not specified'),
                "",
                "## Actual Behavior",
                "",
                answers.get('actual_behavior', 'Not specified'),
                "",
            ])
        
        if feedback_type == 'Feature Request':
            lines.extend([
                "## Use Case",
                "",
                answers.get('use_case', 'No use case provided'),
                "",
            ])
        
        lines.extend([
            "## Environment",
            "",
            f"- Platform: {context['platform']}",
            f"- Python: {context['python_version']}",
            f"- CORTEX: {context['cortex_version']}",
        ])
        
        return "\n".join(lines)
    
    def _generate_summary(self, answers: Dict[str, Any], file_path: str) -> str:
        """Generate summary message."""
        lines = [
            f"**Type:** {answers.get('feedback_type')}",
            f"**Priority:** {answers.get('priority')}",
            f"**Title:** {answers.get('title')}",
            f"**File:** `{file_path}`",
            "",
            "✅ **Feedback submitted successfully!**",
            "",
            "Your feedback has been saved locally and is ready to share.",
        ]
        
        return "\n".join(lines)
