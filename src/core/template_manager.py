"""
Template Manager for CORTEX 4.0

Main interface for response template system v4.0.
Coordinates tier selection, section composition, and rendering.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from src.core.response_tier_selector import ResponseTierSelector, ResponseTier
from src.core.section_selector import SectionSelector, Section


@dataclass
class ResponseMetadata:
    """Metadata about generated response."""
    tier: ResponseTier
    sections: List[Section]
    estimated_tokens: int
    has_header: bool
    has_branding: bool


class TemplateManager:
    """
    Template Manager v4.0 - Adaptive Minimalist Response System
    
    Orchestrates tier selection, section composition, and response rendering
    using dynamic composition instead of static templates.
    
    Features:
    - Intelligent tier selection (INSTANT/FOCUSED/STRUCTURED/COMPREHENSIVE)
    - Dynamic section composition based on context
    - 97% reduction from v3.0 (15,851 → 486 lines)
    - Token-efficient responses
    
    Usage:
        manager = TemplateManager("cortex-brain/response-templates-v4.yaml")
        
        # Render response
        response = manager.render(
            request="implement feature X",
            content={
                "understanding": "Implementing feature X with validation",
                "approach": "No significant challenges",
                "response": "Feature implemented successfully",
                "changes": "Created src/feature_x.py (150 LOC)",
                "next_steps": "1. Test in staging\\n2. Deploy"
            },
            context={
                "has_technical_challenge": False,
                "files_modified": True,
                "user_action_required": True
            }
        )
    """
    
    def __init__(self, templates_path: str):
        """
        Initialize template manager.
        
        Args:
            templates_path: Path to response-templates-v4.yaml
        """
        self.templates_path = Path(templates_path)
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize selectors
        self.tier_selector = ResponseTierSelector()
        self.section_selector = SectionSelector()
        
        self.logger.info(f"Template Manager v4.0 initialized: {templates_path}")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load template configuration from YAML.
        
        Returns:
            Configuration dictionary
        """
        if not self.templates_path.exists():
            self.logger.error(f"Templates file not found: {self.templates_path}")
            return self._get_default_config()
        
        try:
            with open(self.templates_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self.logger.info(
                    f"Loaded v{config.get('schema_version')} templates "
                    f"({self.templates_path.stat().st_size} bytes)"
                )
                return config
        except Exception as e:
            self.logger.error(f"Failed to load templates: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get minimal default configuration."""
        return {
            "schema_version": "4.0",
            "architecture": "adaptive_minimalism"
        }
    
    def render(
        self,
        request: str,
        content: Dict[str, str],
        context: Optional[Dict] = None,
        title: Optional[str] = None
    ) -> str:
        """
        Render response using adaptive tier system.
        
        Args:
            request: User's original request
            content: Section content dictionary (keys match section types)
            context: Context flags for section selection
            title: Optional title (default: extract from request)
        
        Returns:
            Formatted markdown response
        """
        context = context or {}
        
        # Select tier
        tier = self.tier_selector.select_tier(request, context)
        
        # Handle TIER1 (instant) - no formatting
        if tier == ResponseTier.TIER1_INSTANT:
            return content.get("response", "")
        
        # Select sections
        sections = self.section_selector.select_sections(tier.value, context)
        
        # Build response
        response_parts = []
        
        # Add header
        response_parts.append(self._render_header(title or self._extract_title(request)))
        
        # Add separator for TIER3+
        if tier in [ResponseTier.TIER3_STRUCTURED, ResponseTier.TIER4_COMPREHENSIVE]:
            response_parts.append("\n---\n")
        
        # Add sections
        for section in sections:
            section_key = section.type.value
            if section_key in content:
                response_parts.append(
                    self._render_section(section, content[section_key])
                )
        
        return "\n".join(response_parts)
    
    def render_success(
        self,
        operation: str,
        content: Dict[str, str]
    ) -> str:
        """
        Render success completion response.
        
        Args:
            operation: Operation name
            content: Section content (understanding, response, changes)
        
        Returns:
            Formatted success response with 🎉 header
        """
        parts = [
            "# 🎉 CONGRATULATIONS",
            "",
            f"## 🧠 CORTEX {operation}",
            "**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX",
            "",
            "---",
            "",
            "### 🎯 Understanding & Scope",
            content.get("understanding", ""),
            "",
            "### ⚡ Approach & Considerations",
            "No Challenge - All work completed successfully",
            "",
            "### 💬 Response",
            content.get("response", ""),
            "",
            "### 📊 Impact & Changes",
            content.get("changes", ""),
            "",
            "### 🔍 Next Steps",
            "✅ **Work Complete!** No further action required.",
            ""
        ]
        
        # Add optional next actions
        if "next_actions" in content:
            parts.append(content["next_actions"])
        
        return "\n".join(parts)
    
    def render_error(
        self,
        error_message: str,
        solutions: Optional[List[str]] = None
    ) -> str:
        """
        Render error response.
        
        Args:
            error_message: Error description
            solutions: Optional list of possible solutions
        
        Returns:
            Formatted error response
        """
        parts = [
            "## 🧠 CORTEX Error",
            "**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX",
            "",
            "---",
            "",
            "### ⚠️ Error",
            error_message,
            ""
        ]
        
        if solutions:
            parts.append("### 🔍 Possible Solutions")
            for i, solution in enumerate(solutions, 1):
                parts.append(f"{i}. {solution}")
            parts.append("")
        
        return "\n".join(parts)
    
    def _render_header(self, title: str) -> str:
        """Render response header with branding."""
        return (
            f"## 🧠 CORTEX {title}\n"
            "**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX"
        )
    
    def _render_section(self, section: Section, content: str) -> str:
        """Render individual section."""
        return f"\n### {section.emoji} {section.title}\n\n{content}\n"
    
    def _extract_title(self, request: str) -> str:
        """
        Extract title from request.
        
        Args:
            request: User's request
        
        Returns:
            Capitalized title (max 60 chars)
        """
        # Clean request
        title = request.strip()
        
        # Remove question marks
        title = title.rstrip("?")
        
        # Capitalize first letter
        if title:
            title = title[0].upper() + title[1:]
        
        # Truncate if too long
        if len(title) > 60:
            title = title[:57] + "..."
        
        return title or "Response"
    
    def get_metadata(
        self,
        request: str,
        context: Optional[Dict] = None
    ) -> ResponseMetadata:
        """
        Get response metadata without rendering.
        
        Useful for token estimation and testing.
        
        Args:
            request: User's request
            context: Optional context dictionary
        
        Returns:
            ResponseMetadata with tier, sections, token estimate
        """
        context = context or {}
        
        # Select tier
        tier = self.tier_selector.select_tier(request, context)
        
        # Select sections
        sections = []
        if tier != ResponseTier.TIER1_INSTANT:
            sections = self.section_selector.select_sections(tier.value, context)
        
        # Estimate tokens (rough approximation)
        estimated_tokens = self._estimate_response_tokens(tier, sections)
        
        return ResponseMetadata(
            tier=tier,
            sections=sections,
            estimated_tokens=estimated_tokens,
            has_header=tier != ResponseTier.TIER1_INSTANT,
            has_branding=tier != ResponseTier.TIER1_INSTANT
        )
    
    def _estimate_response_tokens(
        self,
        tier: ResponseTier,
        sections: List[Section]
    ) -> int:
        """
        Estimate response token count.
        
        Rough approximation:
        - Header: ~30 tokens
        - Each section: ~50-150 tokens
        """
        if tier == ResponseTier.TIER1_INSTANT:
            return 10  # Direct answer
        
        # Header + branding
        tokens = 30
        
        # Sections (average 100 tokens each)
        tokens += len(sections) * 100
        
        return tokens
    
    def validate_config(self) -> bool:
        """
        Validate template configuration.
        
        Returns:
            True if valid
        """
        required_keys = ["schema_version", "routing", "sections", "components"]
        
        for key in required_keys:
            if key not in self.config:
                self.logger.error(f"Missing required key: {key}")
                return False
        
        # Validate schema version
        if self.config.get("schema_version") != "4.0":
            self.logger.warning(
                f"Unexpected schema version: {self.config.get('schema_version')}"
            )
        
        return True
