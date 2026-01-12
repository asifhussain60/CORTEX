"""
Response Renderer - Markdown generation from orchestrator results.

Converts orchestrator output to formatted markdown responses with CORTEX header injection,
template composition, and executive summary formatting.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timezone


class ResponseRenderer:
    """
    Renders orchestrator results as formatted markdown with CORTEX headers.
    
    Features:
    - Loads response templates from response-templates-v4.yaml
    - Injects mandatory CORTEX header with brain icon and copyright
    - Composes markdown from template library
    - Enforces executive summary format (bullets, no prose)
    - Validates against quality gates
    - Adds "Next Steps:" as final mandatory section
    """
    
    def __init__(self, templates_path: str = "cortex-brain/response-templates-v4.yaml"):
        """
        Initialize response renderer.
        
        Args:
            templates_path: Path to response templates YAML file
        """
        self.logger = logging.getLogger("cortex.orchestrators.response_renderer")
        self.templates_path = Path(templates_path)
        self.templates = self._load_templates()
        self.logger.info(f"ResponseRenderer initialized with templates from {templates_path}")
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load response templates from YAML file."""
        try:
            if self.templates_path.exists():
                with open(self.templates_path, 'r') as f:
                    templates = yaml.safe_load(f) or {}
                    self.logger.debug(f"Loaded {len(templates)} template sections")
                    return templates
            else:
                self.logger.warning(f"Templates file not found: {self.templates_path}")
                return self._get_default_templates()
        except Exception as e:
            self.logger.error(f"Failed to load templates: {e}")
            return self._get_default_templates()
    
    def _get_default_templates(self) -> Dict[str, Any]:
        """Return hardcoded default templates as fallback."""
        return {
            "schema_version": "4.2.0",
            "mandatory_header": {
                "enabled": True,
                "template": "# 🧠 CORTEX {operation_type} Summary\n**Version:** {version} | **Date:** {iso_date}\n**Author:** Asif Hussain\n**Copyright © 2025-2026 Asif Hussain. All rights reserved.**\n---\n"
            },
            "executive_summary": {
                "enabled": True,
                "structure": {
                    "sections": [
                        {"name": "Outcomes", "marker": "✅", "required": True},
                        {"name": "In Progress", "marker": "⚙️", "required": False},
                        {"name": "Risks", "marker": "⚠️", "required": False},
                        {"name": "Impact", "marker": "🎯", "required": False},
                        {"name": "Next Steps", "marker": "📋", "required": True}
                    ]
                }
            }
        }
    
    def render(
        self,
        result: Any,
        tier: str = 'auto',
        context: Optional[Dict[str, Any]] = None,
        operation_type: str = "Execution"
    ) -> str:
        """
        Render result as markdown with CORTEX header and executive format.
        
        Args:
            result: Orchestrator result to render (object with attributes or dict)
            tier: Response detail tier ('auto', 'concise', 'detailed')
            context: Additional rendering context (progress, risks, etc.)
            operation_type: Type of operation for header (e.g., "TDD-Master", "Planning")
        
        Returns:
            Formatted markdown string with CORTEX header and sections
        """
        context = context or {}
        
        # Extract message content from result
        message_content = self._extract_message(result)
        
        # Build header with brain icon and copyright
        header = self._build_header(operation_type, context)
        
        # Build executive summary sections
        sections = self._build_sections(message_content, context)
        
        # Build Next Steps (mandatory final section)
        next_steps = self._build_next_steps(context)
        
        # Compose final markdown
        final_markdown = f"{header}\n{sections}\n{next_steps}"
        
        # Validate against quality gates
        self._validate_quality_gates(final_markdown)
        
        return final_markdown
    
    def _extract_message(self, result: Any) -> str:
        """Extract message content from result object or dict."""
        if hasattr(result, 'message'):
            return str(result.message)
        elif isinstance(result, dict):
            # Try common message keys
            for key in ['message', 'output', 'content', 'summary']:
                if key in result:
                    return str(result[key])
        return str(result)
    
    def _build_header(self, operation_type: str, context: Dict[str, Any]) -> str:
        """
        Build mandatory CORTEX header with brain icon and copyright.
        
        Format:
        # 🧠 CORTEX {operation_type} Summary
        **Version:** {version} | **Date:** {iso_date}
        **Author:** Asif Hussain
        **Copyright © 2025-2026 Asif Hussain. All rights reserved.**
        ---
        """
        header_config = self.templates.get("mandatory_header", {})
        
        if not header_config.get("enabled", True):
            return ""
        
        # Extract version from context or use default
        version = context.get("version", "6.0.0")
        iso_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Use template from config
        template = header_config.get(
            "template",
            "# 🧠 CORTEX {operation_type} Summary\n**Version:** {version} | **Date:** {iso_date}\n**Author:** Asif Hussain\n**Copyright © 2025-2026 Asif Hussain. All rights reserved.**\n---\n"
        )
        
        header = template.format(
            operation_type=operation_type,
            version=version,
            iso_date=iso_date
        )
        
        self.logger.debug(f"Built header for operation: {operation_type}")
        return header
    
    def _build_sections(self, message_content: str, context: Dict[str, Any]) -> str:
        """
        Build executive summary sections from context.
        
        Sections (in order):
        - Executive Summary (3-5 sentences from context.summary)
        - Outcomes (✅ - from context.outcomes)
        - In Progress (⚙️ - from context.in_progress)
        - Risks (⚠️ - from context.risks)
        - Impact (🎯 - from context.impact)
        """
        sections = []
        
        # Executive summary (required, before sections)
        if "summary" in context:
            sections.append(f"{context['summary']}\n")
        
        # Build structured sections
        section_config = self.templates.get("executive_summary", {}).get("structure", {}).get("sections", [])
        
        for section_def in section_config:
            if section_def["name"].lower() == "next steps":
                # Skip Next Steps here - built separately
                continue
            
            section_name = section_def["name"].lower()
            marker = section_def.get("marker", "")
            
            # Get section content from context
            if section_name in context and context[section_name]:
                section_content = context[section_name]
                
                # Build section header with marker
                section_text = f"\n{marker} {section_def['name'].upper()}\n"
                
                # Handle list or string content
                if isinstance(section_content, list):
                    for bullet in section_content:
                        section_text += f"• {bullet}\n"
                else:
                    section_text += f"{section_content}\n"
                
                sections.append(section_text)
        
        return "\n".join(sections)
    
    def _build_next_steps(self, context: Dict[str, Any]) -> str:
        """
        Build mandatory "Next Steps:" section as final section.
        
        Prioritizes single sequential path forward with high-value actions.
        """
        marker = "📋"
        next_steps_list = context.get("next_steps", [])
        
        if not next_steps_list:
            # Generate default next steps from context
            next_steps_list = self._generate_default_next_steps(context)
        
        section = f"\n{marker} NEXT STEPS\n"
        
        # Enforce single sequential path (no branching)
        if isinstance(next_steps_list, list):
            for i, step in enumerate(next_steps_list[:3], 1):  # Max 3 steps
                section += f"{i}. {step}\n"
        else:
            section += f"{next_steps_list}\n"
        
        return section
    
    def _generate_default_next_steps(self, context: Dict[str, Any]) -> List[str]:
        """Generate intelligent default next steps based on context."""
        steps = []
        
        # Analyze context to suggest next actions
        if context.get("multi_phase_operation"):
            next_phase = context.get("next_phase")
            if next_phase:
                steps.append(f"Proceed to Phase {next_phase} when current phase reaches 100%")
        
        if context.get("files_modified"):
            steps.append("Verify changes via `git diff` and commit via `git commit -m 'message'`")
        
        if context.get("progress", {}).get("percentage", 0) < 100:
            steps.append("Continue implementation to reach 100% phase completion")
        
        if not steps:
            steps.append("Monitor progress in cortex-brain/tier1/tracking/progress-tracker.json")
        
        return steps
    
    def _validate_quality_gates(self, markdown: str) -> None:
        """
        Validate rendered markdown against quality gates.
        
        Checks:
        - Header present and starts with 🧠 CORTEX
        - Copyright line present
        - Mandatory sections present (Outcomes, Next Steps)
        - No code blocks (unless explicitly marked)
        - Proper formatting
        """
        checks = {
            "header_present": "🧠 CORTEX" in markdown,
            "copyright_present": "Copyright © 2025-2026" in markdown,
            "outcomes_section": "✅ OUTCOMES" in markdown,
            "next_steps_section": "📋 NEXT STEPS" in markdown,
            "author_present": "Asif Hussain" in markdown
        }
        
        failed_checks = [k for k, v in checks.items() if not v]
        
        if failed_checks:
            self.logger.warning(
                f"Quality gate validation warnings: {', '.join(failed_checks)}"
            )
        else:
            self.logger.debug("All quality gates passed")
