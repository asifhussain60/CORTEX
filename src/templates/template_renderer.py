"""
Template Renderer - Generates markdown output from sections and content

Responsibilities:
- Format headers with emojis
- Assemble sections in correct order
- Apply markdown formatting
- Handle success template special case
"""

from typing import Dict, Any, List

from src.templates.types import ResponseTier, TemplateContext


class TemplateRenderer:
    """Renders the final markdown response from selected sections and content"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the template renderer.
        
        Args:
            config: Template configuration dictionary
        """
        self.config = config
        self.section_emojis = config.get("section_emojis", {})
        self.components = config.get("components", {})
    
    def render(
        self,
        tier: ResponseTier,
        sections: List[str],
        content: Dict[str, str],
        context: TemplateContext
    ) -> str:
        """
        Render the complete response.
        
        Args:
            tier: Selected response tier
            sections: List of section IDs to include
            content: Section content keyed by section ID
            context: Template context
        
        Returns:
            Formatted markdown response
        """
        # Handle TIER 1 (INSTANT) - just return direct answer
        if tier == ResponseTier.INSTANT:
            return content.get("response", "")
        
        # Handle success template
        if context.all_work_complete and context.no_errors and context.no_user_action_required:
            return self.render_success(content, context)
        
        # Build standard response
        parts = []
        
        # Add header
        header = self._render_header(context.operation)
        parts.append(header)
        
        # Add separator for TIER 3 and TIER 4
        if tier in [ResponseTier.STRUCTURED, ResponseTier.COMPREHENSIVE]:
            parts.append("\n---\n")
        
        # Add sections
        for section_id in sections:
            section_content = content.get(section_id, "")
            if section_content:
                section_text = self._render_section(section_id, section_content)
                parts.append(section_text)
        
        return "\n\n".join(parts)
    
    def render_success(self, content: Dict[str, str], context: TemplateContext) -> str:
        """
        Render a success/completion response (v4.0 format).
        
        Args:
            content: Section content
            context: Template context
        
        Returns:
            Formatted success response
        """
        parts = []
        
        # Celebration header
        parts.append("# 🎉 CONGRATULATIONS\n")
        
        # Standard header
        header = self._render_header(context.operation)
        parts.append(header)
        
        # Separator
        parts.append("\n---\n")
        
        # v4.0 Success sections (simplified)
        success_sections = [
            ("context", "🎯", "Understanding & Scope"),
            ("approach", "⚡", "Approach & Considerations"),
            ("response", "💬", "Response"),
            ("changes", "📊", "Impact & Changes"),
            ("next_steps", "🔍", "Next Steps")
        ]
        
        for section_id, emoji, title in success_sections:
            section_content = content.get(section_id, "")
            if section_content:
                parts.append(f"### {emoji} {title}\n{section_content}")
        
        return "\n\n".join(parts)
    
    def _render_header(self, operation: str) -> str:
        """Render the response header"""
        return (
            f"## 🧠 CORTEX {operation}\n"
            "**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX"
        )
    
    def _render_section(self, section_id: str, content: str) -> str:
        """Render a single section with emoji and title"""
        # Get emoji for this section
        emoji = self.section_emojis.get(section_id.split("_")[0], "📝")
        
        # Get section name
        section_name = self._get_section_name(section_id)
        
        # Build section
        return f"### {emoji} {section_name}\n{content}"
    
    def _get_section_name(self, section_id: str) -> str:
        """Convert section ID to display name (v4.0 adaptive format)"""
        # Map common section IDs to display names
        name_map = {
            "context": "Context",
            "analysis": "Analysis",
            "response": "Response",
            "changes": "Changes",
            "next_steps": "Next Steps",
            "architecture": "Architecture",
            "technical_details": "Technical Details",
            "risks_mitigations": "Risks & Mitigations"
        }
        
        return name_map.get(section_id, section_id.replace("_", " ").title())
